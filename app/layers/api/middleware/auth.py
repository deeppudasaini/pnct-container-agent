"""Authentication middleware"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.shared.config.settings.base import get_settings

settings = get_settings()


class AuthenticationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # it can be used to validate request from users. Permissions or api keys

        return await call_next(request)
