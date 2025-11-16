"""Workflow execution repository"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from shared.database.models.workflow_execution import WorkflowExecution
from shared.database.repositories.base_repository import BaseRepository


class WorkflowRepository(BaseRepository[WorkflowExecution]):
    """Repository for workflow execution operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(WorkflowExecution, session)

    async def get_by_workflow_id(
            self,
            workflow_id: str
    ) -> Optional[WorkflowExecution]:
        """Get workflow by workflow ID"""
        result = await self.session.execute(
            select(WorkflowExecution).where(
                WorkflowExecution.workflow_id == workflow_id
            )
        )
        return result.scalar_one_or_none()

    async def update_status(
            self,
            workflow_id: str,
            status: str,
            error_message: Optional[str] = None,
            completed_at: Optional[datetime] = None,
            duration_ms: Optional[int] = None
    ) -> Optional[WorkflowExecution]:
        """Update workflow status"""
        workflow = await self.get_by_workflow_id(workflow_id)
        if not workflow:
            return None

        workflow.status = status
        if error_message:
            workflow.error_message = error_message
        if completed_at:
            workflow.completed_at = completed_at
        if duration_ms:
            workflow.duration_ms = duration_ms

        await self.session.flush()
        await self.session.refresh(workflow)
        return workflow
