from typing import Dict, Any
from app.layers.mcp.tools.base_tool import BaseTool
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


class GetContainerInfoTool(BaseTool):

    name = "get_container_info"
    description = "Retrieve complete container information from PNCT"

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "required": ["container_id"],
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "Container number (4 letters + 7 digits)"
                }
            }
        }

    async def execute(
            self,
            parameters: Dict[str, Any],
            workflow_client
    ) -> Dict[str, Any]:
        self.validate_parameters(parameters)

        container_id = parameters["container_id"]

        logger.info(f"Executing get_container_info for {container_id}")

        result = await workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": container_id,
                "operation": "get_full_info"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": "success"
        }


class CheckAvailabilityTool(BaseTool):
    name = "check_container_availability"
    description = "Check if container is available for pickup"

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "required": ["container_id"],
            "properties": {
                "container_id": {
                    "type": "string",
                    "description": "Container number"
                }
            }
        }

    async def execute(
            self,
            parameters: Dict[str, Any],
            workflow_client
    ) -> Dict[str, Any]:
        self.validate_parameters(parameters)

        container_id = parameters["container_id"]

        logger.info(f"Checking availability for {container_id}")

        result = await workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": container_id,
                "operation": "check_availability"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": "success"
        }


class GetLocationTool(BaseTool):
    name = "get_container_location"
    description = "Get container yard location"

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "required": ["container_id"],
            "properties": {
                "container_id": {"type": "string"}
            }
        }

    async def execute(
            self,
            parameters: Dict[str, Any],
            workflow_client
    ) -> Dict[str, Any]:
        self.validate_parameters(parameters)

        result = await workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": parameters["container_id"],
                "operation": "get_location"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": "success"
        }


class CheckHoldsTool(BaseTool):
    name = "check_container_holds"
    description = "Check for holds or restrictions on container"

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "required": ["container_id"],
            "properties": {
                "container_id": {"type": "string"}
            }
        }

    async def execute(
            self,
            parameters: Dict[str, Any],
            workflow_client
    ) -> Dict[str, Any]:
        self.validate_parameters(parameters)

        result = await workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": parameters["container_id"],
                "operation": "check_holds"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": "success"
        }


class GetLastFreeDayTool(BaseTool):

    name = "get_last_free_day"
    description = "Get last free day for container"

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "required": ["container_id"],
            "properties": {
                "container_id": {"type": "string"}
            }
        }

    async def execute(
            self,
            parameters: Dict[str, Any],
            workflow_client
    ) -> Dict[str, Any]:
        self.validate_parameters(parameters)

        result = await workflow_client.start_workflow(
            workflow_name="container_scraper_workflow",
            workflow_input={
                "container_id": parameters["container_id"],
                "operation": "get_lfd"
            }
        )

        return {
            "data": result.data,
            "workflow_id": result.workflow_id,
            "status": "success"
        }
