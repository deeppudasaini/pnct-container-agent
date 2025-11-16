import json
from typing import Any, Optional
import redis.asyncio as redis
from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class CacheManager:

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        if not self._redis:
            self._redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Connected to Redis")

    async def disconnect(self):
        if self._redis:
            await self._redis.close()
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[Any]:
        if not settings.CACHE_ENABLED:
            return None

        try:
            await self.connect()
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        if not settings.CACHE_ENABLED:
            return False

        try:
            await self.connect()
            ttl = ttl or settings.CACHE_TTL
            await self._redis.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.connect()
            await self._redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        try:
            await self.connect()
            keys = await self._redis.keys(pattern)
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0

