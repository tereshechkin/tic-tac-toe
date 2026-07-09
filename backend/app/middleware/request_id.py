from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import request_id_var
import uuid


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to inject and propagate request_id."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Try to get from header, else generate
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Set context var
        token = request_id_var.set(request_id)

        # Add to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        # Reset context var
        request_id_var.reset(token)

        return response
