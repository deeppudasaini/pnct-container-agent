import time
import json
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis

from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.window = 60
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        redis_key = f"rate:{client_ip}"

        current_count = await self.redis.get(redis_key)
        current_count = int(current_count) if current_count else 0

        if current_count >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # increment with TTL
        await self.redis.incr(redis_key)
        await self.redis.expire(redis_key, self.window)

        # validate request body token size
        body = await request.body()
        try:
            parsed = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON request"
            )

        token_count = self._count_tokens(parsed)
        if token_count > settings.REQUEST_TOKEN_LIMIT:
            logger.warning(
                f"Request token limit exceeded for {client_ip}. "
                f"Tokens: {token_count}"
            )
            raise HTTPException(
                status_code=413,
                detail="Request body is too large"
            )

        return await call_next(request)

    def _count_tokens(self, obj):
        if isinstance(obj, dict):
            return sum(self._count_tokens(v) for v in obj.values())
        if isinstance(obj, list):
            return sum(self._count_tokens(i) for i in obj)
        if isinstance(obj, str):
            return len(obj.split())
        return 1
