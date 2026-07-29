from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens: float = float(capacity)
        self.last_refill = time.time()

    def consume(self) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def remaining(self) -> float:
        now = time.time()
        elapsed = now - self.last_refill
        return min(self.capacity, self.tokens + elapsed * self.refill_rate)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, limits: dict[str, int]):
        super().__init__(app)
        self._buckets: defaultdict[str, TokenBucket] = defaultdict()
        self._limits = limits

    def _bucket(self, key: str) -> TokenBucket:
        if key not in self._buckets:
            capacity = self._limits.get(key, 100)
            refill_rate = capacity / 3600.0
            self._buckets[key] = TokenBucket(capacity, refill_rate)
        return self._buckets[key]

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)
        user_id = getattr(request.state, "user_id", "default")
        route_key = f"{request.method}:{request.url.path}"
        bucket_key = f"{user_id}:{route_key}"
        bucket = self._bucket(bucket_key)
        if not bucket.consume():
            return JSONResponse(
                status_code=429,
                content={
                    "ok": False,
                    "error": "rate_limited",
                    "message": "Rate limit exceeded",
                    "meta": {},
                },
            )
        response = await call_next(request)
        remaining = int(bucket.remaining())
        cap = self._limits.get(route_key, 100)
        response.headers["X-RateLimit-Limit"] = str(cap)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 3600))
        return response
