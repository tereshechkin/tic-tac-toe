import contextlib
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.cache import cache
from app.core.exceptions import AppException
from app.middleware import LoggingMiddleware, RequestIDMiddleware, RateLimitMiddleware
from app.utils.logger import configure_logging, get_logger
from app.api.v1 import router as v1_router
from app.api import websocket as websocket_router
from app.db.connection import engine
from sqlalchemy import text

logger = get_logger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: connect to Redis and shutdown gracefully."""
    # Startup
    configure_logging(level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)
    logger.info("Starting application")

    # Connect to Redis
    await cache.connect()
    logger.info("Redis connected")

    yield

    # Shutdown
    logger.info("Shutting down application")
    await cache.close()
    await engine.dispose()
    logger.info("Resources released")


app = FastAPI(
    title="Tic-Tac-Toe Backend API",
    version="1.0.0",
    description="Backend for Tic-Tac-Toe game with LLM opponents",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)

# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(
        f"AppException occurred: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"},
    )

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint verifying database and Redis connectivity."""
    health_status = {
        "status": "healthy",
        "services": {},
    }
    overall = True

    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        overall = False

    # Check Redis
    try:
        await cache.ping()
        health_status["services"]["redis"] = "ok"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        overall = False

    if not overall:
        health_status["status"] = "unhealthy"
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_status)

    return health_status

# Include API routers
app.include_router(v1_router)
app.include_router(websocket_router.router)
