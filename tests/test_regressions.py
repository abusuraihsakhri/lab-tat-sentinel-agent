"""Regression checks for security, packaging-facing CLI, and API."""
import csv
from pathlib import Path

from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail
from agents.models import SystemTaskPayload
from cli import main


def test_audit_verification_recomputes_hmac():
    trail = AuditTrail(secret_key="unit-test-only")
    trail.log("actor", "tier", "event", {"seq": 1})
    trail.log("actor", "tier", "event", {"seq": 2})
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "altered"
    assert not trail.verify_integrity()


def test_audit_verification_detects_forged_last_entry():
    trail = AuditTrail(secret_key="unit-test-only")
    trail.log("actor", "tier", "event", {"seq": 1})
    trail.logs[-1]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_audit_log_snapshot_does_not_modify_internal_chain():
    trail = AuditTrail(secret_key="unit-test-only")
    trail.log("actor", "tier", "event", {"seq": 1})
    trail.get_trail()[0]["actor"] = "outsider"
    assert trail.verify_integrity()


def test_metrics_are_prometheus_text_and_increment():
    client = TestClient(app)
    before = client.get("/metrics")
    assert before.status_code == 200
    assert "system_tasks_total" in before.text
    assert "text/plain" in before.headers["content-type"]
    result = client.post("/api/audit", json={
        "task_id": "T-01", "target_identifier": "SPECIMEN-1",
        "primary_metric": 30, "secondary_metric": 13,
        "status_descriptor": "NOMINAL", "is_critical_flag": False,
    })
    assert result.status_code == 200
    assert result.json()["overall_urgency"] == "ELEVATED_RISK"
    assert client.get("/metrics").status_code == 200


def test_api_rejects_nonfinite_metrics():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T-01", "target_identifier": "SPECIMEN-1",
        "primary_metric": "NaN",
    })
    assert response.status_code == 422


def test_api_blocks_identifier_pattern_without_exposing_value():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T-01", "target_identifier": "MRN-1234567",
        "primary_metric": 10,
    })
    assert response.status_code == 422
    assert "1234567" not in response.text


def test_sample_csv_legacy_schema(tmp_path):
    path = Path(__file__).parent.parent / "sample.csv"
    dest = tmp_path / "evaluated.csv"
    assert main(["batch", "-i", str(path), "-o", str(dest)]) == 0
    with dest.open(newline="", encoding="utf-8") as handle:
        results = list(csv.DictReader(handle))
    assert len(results) == 3
    assert results[0]["overall_urgency"] == "CRITICAL_STAT_PANIC"
    assert results[1]["overall_urgency"] == "ROUTINE"
