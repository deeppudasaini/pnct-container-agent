from typing import Dict, Any
from dataclasses import dataclass

from app.layers.mcp.registry.tool_registry import ToolRegistry
from app.layers.mcp.clients.workflow_client import WorkflowClient
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ToolResult:
    data: Dict[str, Any]
    workflow_id: str
    status: str
    tool_name: str


class ToolExecutor:
    def __init__(self):
        self.registry = ToolRegistry()
        self.workflow_client = WorkflowClient()

    async def execute_tool(
            self,
            tool_name: str,
            parameters: Dict[str, Any]
    ) -> ToolResult:
        logger.info(
            "Executing tool",
            tool=tool_name,
            parameters=parameters
        )

        tool = self.registry.get_tool(tool_name)

        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        result = await tool.execute(parameters, self.workflow_client)

        return ToolResult(
            data=result["data"],
            workflow_id=result["workflow_id"],
            status=result["status"],
            tool_name=tool_name
        )

    def list_tools(self) -> list:
        return self.registry.list_tools()
