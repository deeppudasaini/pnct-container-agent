"""API dependencies"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.session import get_db
from app.shared.database.repositories.repository_factory import RepositoryFactory
from app.shared.config.settings.base import get_settings
from app.shared.exceptions.api_exceptions import UnauthorizedError
from app.layers.ai_agent.agent.agent_orchestrator import AgentOrchestrator

settings = get_settings()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


def get_repository_factory(
    session: AsyncSession = Depends(get_db_session)
) -> RepositoryFactory:
    return RepositoryFactory()




def get_agent_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator()
