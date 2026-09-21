import logging
from fastapi import FastAPI, BackgroundTasks, status
from src.schemas import AlertmanagerWebhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("podwarden")

app = FastAPI(
    title="PodWarden",
    description="Autonomous Kubernetes Incident Triage Agent",
    version="0.1.0"
)


def process_alert_pipeline(payload: AlertmanagerWebhook):
    """Background task to enrich context, run dual-pass diagnosis, and dispatch actions."""
    logger.info(f"Received alert batch with status '{payload.status}' via receiver '{payload.receiver}'")
    
    for alert in payload.alerts:
        alertname = alert.labels.get("alertname", "UnknownAlert")
        namespace = alert.labels.get("namespace", "default")
        pod_name = alert.labels.get("pod", alert.labels.get("pod_name", "N/A"))
        severity = alert.labels.get("severity", "unknown")

        logger.info(
            f"⚡ [INGRESS] Alert: '{alertname}' | Severity: {severity} | "
            f"Target: {namespace}/{pod_name}"
        )
        # Day 2: Telemetry enrichment (k8s.py) and LLM diagnosis (triage.py) will connect here.


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "service": "podwarden", "version": "0.1.0"}


@app.post("/alerts", status_code=status.HTTP_202_ACCEPTED)
async def ingest_alert(payload: AlertmanagerWebhook, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_alert_pipeline, payload)
    return {
        "status": "accepted",
        "message": f"Queued {len(payload.alerts)} alert(s) for automated triage"
    }