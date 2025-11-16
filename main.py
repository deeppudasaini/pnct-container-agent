import uvicorn
from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PNCT Container AI Agent ")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    logger.info("=" * 60)

    uvicorn.run(
        "app.layers.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower(),
    )
