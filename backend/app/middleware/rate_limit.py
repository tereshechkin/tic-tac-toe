from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.rate_limiter import RateLimiter
from app.core.exceptions import RateLimitException
from app.utils.logger import get_logger

logger = get_logger(__name__)

RATE_LIMITS = {
    "/api/v1/auth/register": (5, 3600),  # 5 per hour
    "/api/v1/auth/login": (10, 60),      # 10 per minute
    "/api/v1/auth/resend-code": (5, 3600), # optionally
}

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limiter = RateLimiter()

    async def dispatch(self, request: Request, call_next):
        # Determine client IP
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        # Find matching rate limit (exact match or prefix?)
        limit_config = None
        for route, (limit, period) in RATE_LIMITS.items():
            if path.startswith(route):
                limit_config = (limit, period)
                break
        if limit_config is None:
            return await call_next(request)
        limit, period = limit_config
        key = f"{client_ip}:{path}"
        allowed, remaining = await self.rate_limiter.check(key, limit, period)
        if not allowed:
            logger.warning("Rate limit exceeded", extra={"ip": client_ip, "path": path})
            raise RateLimitException(details={"limit": limit, "period": period, "remaining": remaining})
        response = await call_next(request)
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
