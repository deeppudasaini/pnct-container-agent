from typing import Optional
from app.layers.mcp.tools.base_tool import BaseTool
from app.layers.mcp.tools.container_tools import (
    GetContainerInfoTool,
    CheckAvailabilityTool,
    GetLocationTool,
    CheckHoldsTool,
    GetLastFreeDayTool
)


class ToolFactory:


    _tool_classes = {
        "get_container_info": GetContainerInfoTool,
        "check_container_availability": CheckAvailabilityTool,
        "get_container_location": GetLocationTool,
        "check_container_holds": CheckHoldsTool,
        "get_last_free_day": GetLastFreeDayTool,
    }

    @classmethod
    def create_tool(cls, tool_name: str) -> Optional[BaseTool]:

        tool_class = cls._tool_classes.get(tool_name)

        if not tool_class:
            return None

        return tool_class()

    @classmethod
    def register_tool_class(cls, name: str, tool_class: type):
        cls._tool_classes[name] = tool_class

    @classmethod
    def list_available_tools(cls) -> list:
        return list(cls._tool_classes.keys())
