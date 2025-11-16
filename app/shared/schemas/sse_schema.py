"""Server-Sent Events schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.shared.config.constants.app_constants import StepStatus, ProcessingStep


class SSEStepUpdate(BaseModel):
    step: ProcessingStep
    status: StepStatus
    message: Optional[str] = None
    progress: int = Field(ge=0, le=100)
    data: Optional[Dict[str, Any]] = None
    timestamp: str


class SSEErrorUpdate(BaseModel):
    step: ProcessingStep
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


class SSECompleteUpdate(BaseModel):
    status: str = "completed"
    data: Dict[str, Any]
    total_time_ms: int
    timestamp: str