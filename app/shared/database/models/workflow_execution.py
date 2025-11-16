"""Workflow execution database model"""
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.sql import func
from app.shared.database.base import Base


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(100), unique=True, nullable=False, index=True)
    container_number = Column(String(11), index=True)
    operation = Column(String(50))
    status = Column(String(20), default="pending")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "container_number": self.container_number,
            "operation": self.operation,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }
