from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.models.container_scrape_result import ContainerScrapeResult
from app.shared.database.repositories.base_repository import BaseRepository


class ContainerScrapeResultRepository(BaseRepository[ContainerScrapeResult]):

    def __init__(self, session: AsyncSession):
        super().__init__(ContainerScrapeResult, session)

    async def get_latest(
        self,
        container_number: str,
        operation: str
    ) -> Optional[ContainerScrapeResult]:
        result = await self.session.execute(
            select(ContainerScrapeResult)
            .where(ContainerScrapeResult.container_number == container_number)
            .where(ContainerScrapeResult.operation == operation)
            .order_by(desc(ContainerScrapeResult.scraped_at))
            .limit(1)
        )
        return result.scalars().first()

    async def get_all_for_container(
        self,
        container_number: str
    ) -> List[ContainerScrapeResult]:
        result = await self.session.execute(
            select(ContainerScrapeResult)
            .where(ContainerScrapeResult.container_number == container_number)
            .order_by(desc(ContainerScrapeResult.scraped_at))
        )
        return result.scalars().all()

    async def upsert(
        self,
        container_number: str,
        operation: str,
        raw_html: Optional[str],
        parsed_json: Optional[dict],
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> ContainerScrapeResult:
        existing = await self.get_latest(container_number, operation)

        if existing:
            existing.raw_html = raw_html
            existing.parsed_json = parsed_json
            existing.status = status
            existing.error_message = error_message
            await self.session.flush()
            return existing

        new_entry = ContainerScrapeResult(
            container_number=container_number,
            operation=operation,
            raw_html=raw_html,
            parsed_json=parsed_json,
            status=status,
            error_message=error_message
        )

        self.session.add(new_entry)
        await self.session.flush()
        return new_entry

    async def get_by_container_id(self,id:str) -> Optional[ContainerScrapeResult]:
        result = await self.session.execute(
            select(ContainerScrapeResult)
            .where(ContainerScrapeResult.container_number == id)
        )
        return result.scalars().first()



