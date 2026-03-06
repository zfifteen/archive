"""
Phi-Harmonic Trading Filter API - Main Application
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from mangum import Mangum

from .routes.filter import router as filter_router
from ..config.settings import settings
from ..api.models.response import HealthResponse, ErrorResponse
from ..monitoring.logger import setup_logging
from ..monitoring.metrics import setup_metrics
from ..monitoring.health import comprehensive_health_check


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers to responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add rate limit headers if available
        if hasattr(request.state, "rate_limit_info"):
            info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset_seconds"])

        return response


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=settings.description,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup monitoring
setup_logging()
setup_metrics(app)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            code="INTERNAL_ERROR",
            details={"message": str(exc)},
        ).dict(),
    )


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    return comprehensive_health_check()


# Include routers
app.include_router(filter_router, prefix="/api/v1/filter", tags=["filter"])


# AWS Lambda handler
handler = Mangum(app, lifespan="off")


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
