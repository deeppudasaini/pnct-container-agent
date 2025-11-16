from typing import Dict, Optional, List
from app.layers.mcp.tools.base_tool import BaseTool
from app.layers.mcp.tools.container_tools import (
    GetContainerInfoTool,
    CheckAvailabilityTool,
    GetLocationTool,
    CheckHoldsTool,
    GetLastFreeDayTool
)
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:

    _instance = None
    _tools: Dict[str, BaseTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_tools()
        return cls._instance

    def _initialize_tools(self):
        tools = [
            GetContainerInfoTool(),
            CheckAvailabilityTool(),
            GetLocationTool(),
            CheckHoldsTool(),
            GetLastFreeDayTool(),
        ]

        for tool in tools:
            self.register_tool(tool)

        logger.info(f"Registered {len(self._tools)} tools")

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        tool = self._tools.get(name)

        if not tool:
            logger.warning(f"Tool not found: {name}")

        return tool

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_tool_metadata(self, name: str) -> Optional[dict]:
        tool = self.get_tool(name)

        if tool:
            return tool.get_metadata().__dict__

        return None
