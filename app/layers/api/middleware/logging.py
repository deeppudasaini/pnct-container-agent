import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None
        )

        response = await call_next(request)

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )

        response.headers["X-Process-Time"] = str(duration_ms)

        return response
