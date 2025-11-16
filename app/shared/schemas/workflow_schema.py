"""Workflow schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.shared.config.constants.app_constants import StepStatus, WorkflowStatus


class WorkflowInput(BaseModel):
    container_id: str
    operation: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkflowStep(BaseModel):
    name: str
    status: StepStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowResult(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    data: Optional[Dict[str, Any]] = None
    steps: List[WorkflowStep] = Field(default_factory=list)
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    current_step: Optional[str] = None
    progress_percentage: int = Field(ge=0, le=100)
    steps: List[WorkflowStep] = Field(default_factory=list)
    message: Optional[str] = None
