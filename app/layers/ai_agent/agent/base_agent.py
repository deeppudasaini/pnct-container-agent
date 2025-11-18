from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator

from app.layers.ai_agent.schemas.output_schema import ContainerParseSchema


class BaseAgent(ABC):

    @abstractmethod
    async def parse_query(self, query: str) -> ContainerParseSchema:
        pass


    # It can be used to generte sse response if needed
    @abstractmethod
    async def generate_response(self, data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_agent(self):
        pass

    @abstractmethod
    async def setup_agent(self):
        pass

