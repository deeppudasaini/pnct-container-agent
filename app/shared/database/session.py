"""Database session management"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.base import async_session_maker, engine
from app.shared.utils.logger import get_logger
from app.shared.database.models import container_model, query_log, workflow_execution
from app.shared.database.base import Base

logger = get_logger(__name__)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized")


async def close_db():
    await engine.dispose()
    logger.info("Database connections closed")
