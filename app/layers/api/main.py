from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.layers.api.middleware.error_handler import GlobalExceptionMiddleware
from app.shared.config.settings.base import get_settings
from app.shared.database.session import init_db, close_db
from app.shared.utils.logger import get_logger
from app.layers.api.routes.v1 import query, health
from app.layers.api.middleware.logging import LoggingMiddleware
from app.layers.api.middleware.rate_limit import RateLimitMiddleware

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting PNCT Container Query System (Layer 2: API)")

    await init_db()

    yield

    await close_db()
    logger.info("👋 Shutting down PNCT Container Query System")


app = FastAPI(
    title="PNCT Container Query System",
    description="AI-powered container information retrieval with layered architecture",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)


if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)


app.add_middleware(GlobalExceptionMiddleware)

app.include_router(health.router, prefix=settings.API_PREFIX, tags=["Health"])
app.include_router(query.router, prefix=settings.API_PREFIX, tags=["Query"])


@app.get("/")
async def root():
    return {
        "service": "PNCT Container Query System",
        "version": "1.0.0",
        "architecture": "Layered (5 layers)",
        "docs": f"{settings.API_PREFIX}/docs"
    }
