"""Container repository"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.models.container_model import Container
from app.shared.database.repositories.base_repository import BaseRepository
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


class ContainerRepository(BaseRepository[Container]):

    def __init__(self, session: AsyncSession):
        super().__init__(Container, session)

    async def get_by_container_number(
            self,
            container_number: str
    ) -> Optional[Container]:
        result = await self.session.execute(
            select(Container).where(
                Container.container_number == container_number.upper()
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
            self,
            container_number: str,
            data: dict,
            source: str = "PNCT"
    ) -> Container:
        existing = await self.get_by_container_number(container_number)

        if existing:
            logger.info(f"Updating container: {container_number}")
            existing.data = data
            existing.source = source
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        else:
            logger.info(f"Creating container: {container_number}")
            return await self.create(
                container_number=container_number.upper(),
                data=data,
                source=source
            )
