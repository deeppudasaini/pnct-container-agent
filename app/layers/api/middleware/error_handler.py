import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


class GlobalExceptionMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except Exception as exc:
            logger.error(
                "Unhandled server error",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(exc),
                    "trace": traceback.format_exc()
                }
            )

            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Internal server error",
                    "details": str(exc)
                }
            )
