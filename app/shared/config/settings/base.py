from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
import os


class Settings(BaseSettings):

    APP_NAME: str = "agents"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    REQUEST_TOKEN_LIMIT:int=100

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql://portpro_db:portpro_db@localhost:5433/portpro_db"
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

    GOOGLE_API_KEY: str = "AIzaSyBZMqgn2YDmyOnwM9NB9nU19329meJZ4_c"

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100

    PNCT_SEARCH_URL: str = "https://pnct.net"

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
