from abc import ABC, abstractmethod
from typing import Optional
import uuid


class BaseScraper(ABC):

    def __init__(self):
        self.session_id = str(uuid.uuid4())

    @abstractmethod
    async def initialize(self):
        pass

    @abstractmethod
    async def search_container(self, container_id: str) -> str:
        pass

    @abstractmethod
    async def close(self):
        pass

    def get_session_id(self) -> str:
        return self.session_id
