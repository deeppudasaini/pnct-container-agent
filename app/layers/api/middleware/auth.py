"""Authentication middleware"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.shared.config.settings.base import get_settings

settings = get_settings()


class AuthenticationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        if request.url.path.endswith("/health"):
            return await call_next(request)

        api_key = request.headers.get(settings.API_KEY_HEADER)

        if not api_key or api_key not in settings.API_KEYS:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )

        return await call_next(request)
