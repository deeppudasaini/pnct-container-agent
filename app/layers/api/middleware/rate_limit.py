import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware

from app.shared.config.settings.base import get_settings
from app.shared.utils.logger import get_logger
from fastapi import Request, HTTPException

settings = get_settings()
logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
        self.window = 60

    async def dispatch(self, request: Request, call_next):
        client_id = request.client.host if request.client else "unknown"

        current_time = time.time()
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < self.window
        ]

        if len(self.requests[client_id]) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        self.requests[client_id].append(current_time)

        return await call_next(request)
