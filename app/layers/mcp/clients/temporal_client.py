# app/layers/mcp/clients/temporal_client.py
import asyncio
import logging
from typing import Any, Dict, Optional
from temporalio.client import Client, WorkflowHandle
from temporalio.service import TLSConfig

logger = logging.getLogger(__name__)

class TemporalClient:

    def __init__(
        self,
        host: str = "localhost",
        port: int = 7233,
        namespace: str = "default",
        tls_config: Optional[TLSConfig] = None
    ):
        self.host = host
        self.port = port
        self.namespace = namespace
        self.tls_config = tls_config
        self._client = None
        
    async def connect(self):
        if not self._client:
            try:
                self._client = await Client.connect(
                    f"{self.host}:{self.port}",
                    namespace=self.namespace,
                    tls=self.tls_config
                )
                logger.info("Connected to Temporal server")
            except Exception as e:
                logger.error(f"Failed to connect to Temporal server: {str(e)}")
                raise
        return self._client
    
    async def start_workflow(
        self,
        workflow_id: str,
        workflow_name: str,
        input_data: Dict[str, Any],
        task_queue: str = "pnct-queue",
        execution_timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        try:
            client = await self.connect()
            handle: WorkflowHandle = await client.start_workflow(
                workflow=workflow_name,
                args=[input_data],
                id=workflow_id,
                task_queue=task_queue,
                execution_timeout_seconds=execution_timeout_seconds
            )
            
            logger.info(f"Started workflow {workflow_name} with ID: {workflow_id}")
            result = await handle.result()
            
            return {
                "status": "completed",
                "workflow_id": workflow_id,
                "data": result,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except asyncio.TimeoutError:
            error_msg = f"Workflow {workflow_id} timed out after {execution_timeout_seconds} seconds"
            logger.error(error_msg)
            return {
                "status": "timeout",
                "error": error_msg,
                "workflow_id": workflow_id
            }
        except Exception as e:
            error_msg = f"Workflow {workflow_id} failed: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "failed",
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def close(self):
        if self._client:
            self._client = None
            logger.info("Temporal client connection closed")