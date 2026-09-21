from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# --- Prometheus Alertmanager Webhook Models ---
class AlertItem(BaseModel):
    status: str
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    startsAt: Optional[str] = None
    endsAt: Optional[str] = None
    generatorURL: Optional[str] = None


class AlertmanagerWebhook(BaseModel):
    version: str = "4"
    groupKey: Optional[str] = None
    status: str  # "firing" or "resolved"
    receiver: str
    alerts: List[AlertItem] = Field(default_factory=list)
    commonLabels: Dict[str, str] = Field(default_factory=dict)
    commonAnnotations: Dict[str, str] = Field(default_factory=dict)


# --- Autonomous Triage & Action Models ---
class ActionType(str, Enum):
    RESTART_POD = "restart_pod"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    SCALE_REPLICAS = "scale_replicas"
    CLEAR_PVC_CACHE = "clear_pvc_cache"
    NO_OP_ESCALATE = "no_op_escalate"


class RemediationStep(BaseModel):
    order: int
    action_type: ActionType
    target_resource: str = Field(description="e.g. deployment/auth-service")
    namespace: str
    command_preview: str = Field(description="Exact kubectl command for execution")
    rollback_command: str = Field(description="Exact command to undo this step")


class TriageDiagnosis(BaseModel):
    alert_name: str
    root_cause_summary: str = Field(description="Concise explanation of failure")
    confidence_score: float = Field(ge=0.0, le=1.0)
    blast_radius_risk: str = Field(description="LOW, MEDIUM, HIGH, or CRITICAL")
    suggested_steps: List[RemediationStep] = Field(default_factory=list)
    escalation_reason: Optional[str] = None