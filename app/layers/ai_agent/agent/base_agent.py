from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator


class BaseAgent(ABC):

    @abstractmethod
    async def parse_query(self, query: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_response(self, data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_agent(self):
        pass

    @abstractmethod
    async def setup_agent(self):
        pass

