from typing import Dict, Optional, List, Any


from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class ToolRegistry:

    _instance = None
    _tools: Dict[str, Any] = {}
    _tool_metadata: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._tools = {}
            self._tool_metadata = {}
            self._initialized = True

    def initialize_with_workflow_client(self, workflow_client):
        from app.layers.mcp.tools.container_tools import ContainerTools

        container_tools = ContainerTools(workflow_client)

        self._register_tool_method(
            name="get_container_info",
            method=container_tools.get_container_info,
            description="Retrieve complete container information from PNCT",
            parameters={"container_id": "Container number (4 letters + 7 digits)"}
        )

        self._register_tool_method(
            name="check_container_availability",
            method=container_tools.check_container_availability,
            description="Check if container is available for pickup",
            parameters={"container_id": "Container number"}
        )

        self._register_tool_method(
            name="get_container_location",
            method=container_tools.get_container_location,
            description="Get container yard location",
            parameters={"container_id": "Container number"}
        )

        self._register_tool_method(
            name="check_container_holds",
            method=container_tools.check_container_holds,
            description="Check for holds or restrictions on container",
            parameters={"container_id": "Container number"}
        )

        self._register_tool_method(
            name="get_last_free_day",
            method=container_tools.get_last_free_day,
            description="Get last free day for container",
            parameters={"container_id": "Container number"}
        )

        logger.info(f"Registered {len(self._tools)} container tools")

    def _register_tool_method(
            self,
            name: str,
            method: Any,
            description: str,
            parameters: Dict[str, str]
    ):
        self._tools[name] = method
        self._tool_metadata[name] = {
            "name": name,
            "description": description,
            "parameters": parameters
        }
        logger.debug(f"Registered tool: {name}")

    def get_all_tools(self) -> List[Any]:
        return list(self._tools.values())

    def list_tool_names(self) -> List[str]:
        return list(self._tools.keys())

    def get_tool_metadata(self, name: str) -> Optional[Dict]:
        return self._tool_metadata.get(name)

    def get_all_metadata(self) -> Dict[str, Dict]:
        return self._tool_metadata.copy()