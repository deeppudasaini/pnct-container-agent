"""Health check endpoint"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from app.shared.database.session import get_db
from app.shared.schemas.response_schema import HealthResponse
from app.shared.utils.logger import get_logger
from app.shared.utils.cache import CacheManager

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    services = {}
    try:
        await db.execute(text("SELECT 1"))
        services["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services["database"] = "unhealthy"

    try:
        cache = CacheManager()
        await cache.connect()
        services["cache"] = "healthy"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        services["cache"] = "unhealthy"

    return HealthResponse(
        status="healthy" if all(v == "healthy" for v in services.values()) else "degraded",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        services=services
    )

