"""Query log repository"""
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.models.query_log import QueryLog
from app.shared.database.repositories.base_repository import BaseRepository


class QueryLogRepository(BaseRepository[QueryLog]):

    def __init__(self, session: AsyncSession):
        super().__init__(QueryLog, session)

    async def get_recent_queries(
            self,
            limit: int = 50
    ) -> List[QueryLog]:
        result = await self.session.execute(
            select(QueryLog)
            .order_by(desc(QueryLog.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_container(
            self,
            container_number: str
    ) -> List[QueryLog]:
        result = await self.session.execute(
            select(QueryLog)
            .where(QueryLog.extracted_container == container_number)
            .order_by(desc(QueryLog.created_at))
        )
        return result.scalars().all()