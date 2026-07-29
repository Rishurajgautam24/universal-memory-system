from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, api_key: str | None = None):
        super().__init__(app)
        self._api_key = api_key

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "ok": False,
                    "error": "unauthorized",
                    "message": "Invalid or missing API key",
                    "meta": {},
                },
            )
        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return JSONResponse(
                status_code=401,
                content={
                    "ok": False,
                    "error": "unauthorized",
                    "message": "Invalid or missing API key",
                    "meta": {},
                },
            )
        if self._api_key and token != self._api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "ok": False,
                    "error": "unauthorized",
                    "message": "Invalid or missing API key",
                    "meta": {},
                },
            )
        request.state.user_id = "default"
        return await call_next(request)
