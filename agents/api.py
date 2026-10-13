"""
FastAPI REST API Server for Lab Tat Sentinel Agent.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .metrics import GLOBAL_METRICS
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Lab Tat Sentinel Agent API",
    description="Illustrative threshold-based specimen operations evaluation API; not validated for clinical decisions",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.exception_handler(SecurityException)
def security_violation_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Input rejected by sensitive-identifier screening."},
    )


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "lab-tat-sentinel-agent", "domain": "Clinical & Biomedical AI", "standard": "Illustrative thresholds; not clinically validated", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """Prometheus exposition format; no task or patient identifiers."""
    return PlainTextResponse(
        GLOBAL_METRICS.export_prometheus_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid query.")


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
