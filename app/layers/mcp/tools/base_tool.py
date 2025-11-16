from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ToolMetadata:
    name: str
    description: str
    parameters: Dict[str, Any]
    version: str = "1.0.0"


class BaseTool(ABC):

    name: str = "base_tool"
    description: str = "Base tool"

    @abstractmethod
    async def execute(
            self,
            parameters: Dict[str, Any],
            workflow_client: Any
    ) -> Dict[str, Any]:

        pass

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=self._get_parameters()
        )

    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        required = self._get_parameters().get("required", [])

        for param in required:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")

        return True
