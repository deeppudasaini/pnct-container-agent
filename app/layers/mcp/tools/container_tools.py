from typing import Dict, Any
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


class ContainerTools:


    def __init__(self, workflow_client):

        self.workflow_client = workflow_client
        logger.info("ContainerTools initialized")

    async def get_container_info(self, container_id: str) -> Dict[str, Any]:

        logger.info(f"Executing get_container_info for {container_id}")

        result = await self.workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": container_id,
                "operation": "get_full_info"
            }
        )
        logger.info("Result from tool calll {result}" +str(result))

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": result.status
        }

    async def check_container_availability(self, container_id: str) -> Dict[str, Any]:

        logger.info(f"Checking availability for {container_id}")

        result = await self.workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": container_id,
                "operation": "check_availability"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": result.status
        }

    async def get_container_location(self, container_id: str) -> Dict[str, Any]:

        logger.info(f"Getting location for {container_id}")

        result = await self.workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": container_id,
                "operation": "get_location"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": result.status
        }

    async def check_container_holds(self, container_id: str) -> Dict[str, Any]:
        logger.info(f"Checking holds for {container_id}")

        result = await self.workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": container_id,
                "operation": "check_holds"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": result.status
        }

    async def get_last_free_day(self, container_id: str) -> Dict[str, Any]:
        logger.info(f"Getting last free day for {container_id}")

        result = await self.workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": container_id,
                "operation": "get_lfd"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": result.status
        }
