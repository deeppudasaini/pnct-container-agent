from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
import os


class Settings(BaseSettings):

    APP_NAME: str = "PNCT Container Query System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql://pnct_user:pnct_pass@localhost:5432/pnct_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300
    CACHE_ENABLED: bool = True

    TEMPORAL_HOST: str = "localhost"
    TEMPORAL_PORT: int = 7233
    TEMPORAL_NAMESPACE: str = "default"
    TEMPORAL_TASK_QUEUE: str = "pnct-container-tasks"
    TEMPORAL_WORKFLOW_TIMEOUT: int = 600
    TEMPORAL_ACTIVITY_TIMEOUT: int = 60

    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL: str = "gemini-1.5-pro"
    GOOGLE_TEMPERATURE: float = 0.1
    GOOGLE_MAX_TOKENS: int = 2048

    SECRET_KEY: str = "change-in-production-min-32-chars"
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: List[str] = ["dev-key-123", "test-key-456"]
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000

    PNCT_BASE_URL: str = "https://pnct.net"
    PNCT_SEARCH_URL: str = "https://pnct.net/container-search"
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_RETRY_DELAY: int = 2
    SCRAPER_HEADLESS: bool = True

    BROWSER_HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30000
    BROWSER_VIEWPORT_WIDTH: int = 1920
    BROWSER_VIEWPORT_HEIGHT: int = 1080

    class Config:
        env_file = ".env.local"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
