from typing import Dict, Any
from dataclasses import dataclass
import uuid

from temporalio.client import Client
from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger

from app.layers.scraper.temporal.workflows.container_workflow import (
    ContainerScraperWorkflow
)
settings = get_settings()
logger = get_logger(__name__)


@dataclass
class WorkflowResult:
    workflow_id: str
    data: Dict[str, Any]
    status: str


class WorkflowClient:


    def __init__(self):
        self._client = None

    async def _get_client(self) -> Client:
        if not self._client:
            self._client = await Client.connect(
                f"{settings.TEMPORAL_HOST}:{settings.TEMPORAL_PORT}",
                namespace=settings.TEMPORAL_NAMESPACE,
            )
            logger.info("Connected to Temporal")

        return self._client

    async def start_workflow(
            self,
            workflow_name: str,
            workflow_input: Dict[str, Any]
    ) -> WorkflowResult:

        workflow_id = f"workflow-{uuid.uuid4()}"

        logger.info(
            "Starting workflow",
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            input=workflow_input
        )

        client = await self._get_client()


        handle = await client.start_workflow(
            ContainerScraperWorkflow.run,
            id=workflow_id,
            task_queue=settings.TEMPORAL_TASK_QUEUE,
            args=[
                workflow_input["container_id"],
                workflow_input["operation"]
            ]
        )

        result = await handle.result()

        logger.info(
            "Workflow completed",
            workflow_id=workflow_id,
            status=result.get("status")
        )

        return WorkflowResult(
            workflow_id=workflow_id,
            data=result.get("data", {}),
            status=result.get("status", "completed")
        )

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        client = await self._get_client()

        try:
            handle = client.get_workflow_handle(workflow_id)
            result = await handle.describe()

            return {
                "workflow_id": workflow_id,
                "status": result.status.name,
                "start_time": result.start_time,
            }
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                "workflow_id": workflow_id,
                "status": "unknown",
                "error": str(e)
            }
