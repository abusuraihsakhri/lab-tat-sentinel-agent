"""
Automated Pytest Test Suite for Lab Tat Sentinel Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main, _resolve_safe_path


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


# ---- Security & Edge Case Tests ----

def test_phi_guard_redaction():
    """PHIGuard.redact_phi should mask sensitive patterns."""
    text = "Patient MRN-1234567 has phone 555-123-4567 and email test@example.com"
    redacted = PHIGuard.redact_phi(text)
    assert "MRN-1234567" not in redacted
    assert "555-123-4567" not in redacted
    assert "test@example.com" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_phi_guard_ssn_detection():
    """SSN pattern should be detected."""
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("SSN: 123-45-6789")


def test_audit_trail_with_explicit_key():
    """AuditTrail with explicit key should not warn."""
    trail = AuditTrail(secret_key="test-secret-key-for-unit-tests")
    entry = trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value"})
    assert entry["current_hash"] != ""
    assert entry["prev_hash"] == "GENESIS_BLOCK_0000000000000000"
    assert trail.verify_integrity() is True


def test_audit_trail_chained_integrity():
    """Multiple audit entries should form a valid chain."""
    trail = AuditTrail(secret_key="chain-test-key")
    trail.log("actor1", "tier1", "EVENT_A", {"seq": 1})
    trail.log("actor2", "tier2", "EVENT_B", {"seq": 2})
    trail.log("actor3", "tier3", "EVENT_C", {"seq": 3})
    assert trail.verify_integrity() is True
    assert len(trail.get_trail()) == 3


def test_resolve_safe_path_existing():
    """Existing file path should resolve correctly."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        tmp_path = f.name
    try:
        result = _resolve_safe_path(tmp_path, must_exist=True)
        assert result == Path(tmp_path).resolve()
    finally:
        os.unlink(tmp_path)


def test_resolve_safe_path_nonexistent():
    """Non-existent file with must_exist=True should raise."""
    with pytest.raises(Exception):
        _resolve_safe_path("/nonexistent/path/to/file.csv", must_exist=True)


def test_batch_csv_processing():
    """CLI batch command should process valid CSV."""
    import csv as csv_mod
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        writer = csv_mod.DictWriter(f, fieldnames=["task_id", "primary_metric", "is_critical_flag"])
        writer.writeheader()
        writer.writerow({"task_id": "B1", "primary_metric": "30.0", "is_critical_flag": "True"})
        writer.writerow({"task_id": "B2", "primary_metric": "10.0", "is_critical_flag": "False"})
        input_path = f.name

    output_path = input_path + ".out.csv"
    try:
        ret = main(["batch", "-i", input_path, "-o", output_path])
        assert ret == 0
        assert os.path.exists(output_path)
        with open(output_path) as f:
            reader = csv_mod.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_batch_missing_file():
    """CLI batch should exit with error for missing input file."""
    with pytest.raises(SystemExit) as exc_info:
        main(["batch", "-i", "/nonexistent/input.csv"])
    # argparse exits with code 2 for argument errors
    assert exc_info.value.code == 2


def test_supervisor_critical_escalation():
    """Critical payload should produce CRITICAL_STAT urgency."""
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="CRIT-01",
        target_identifier="TARGET-CRIT",
        primary_metric=50.0,
        secondary_metric=15.0,
        is_critical_flag=True,
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.CRITICAL_STAT
    assert dossier.critical_alerts_count >= 1


def test_empty_query_returns_response():
    """Supervisor chat with empty query should not crash."""
    supervisor = SystemSupervisor(model_provider="mock")
    response = supervisor.query_supervisory_chat("")
    assert isinstance(response, str)
    assert len(response) > 0
