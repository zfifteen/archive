"""
FastAPI Dependencies for Authentication and Rate Limiting
"""

from fastapi import HTTPException, Header, Request, Depends
from typing import Optional, Dict, Any
import logging

from .redis_client import RedisClient
from .api_key_manager import ApiKeyManager
from .rate_limiter import RateLimiter
from ..config.settings import settings

logger = logging.getLogger(__name__)

# Global instances (in production, use dependency injection)
_redis_client: Optional[RedisClient] = None
_api_key_manager: Optional[ApiKeyManager] = None
_rate_limiter: Optional[RateLimiter] = None


def get_redis_client() -> RedisClient:
    """Get Redis client instance"""
    global _redis_client
    if _redis_client is None and settings.redis_enabled:
        _redis_client = RedisClient(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
        )
    return _redis_client


def get_api_key_manager() -> ApiKeyManager:
    """Get API key manager instance"""
    global _api_key_manager
    if _api_key_manager is None:
        redis_client = get_redis_client()
        _api_key_manager = ApiKeyManager(redis_client)
    return _api_key_manager


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        redis_client = get_redis_client()
        _rate_limiter = RateLimiter(redis_client)
    return _rate_limiter


async def verify_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None),
    api_key_manager: ApiKeyManager = Depends(get_api_key_manager),
) -> Dict[str, Any]:
    """Verify API key and return user info"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")

    user_info = api_key_manager.validate_api_key(x_api_key)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Attach user info to request state for rate limiting
    request.state.user_info = user_info
    return user_info


async def check_rate_limit(
    request: Request,
    user_info: Dict[str, Any] = Depends(verify_api_key),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    """Check rate limit for the request"""
    if not settings.redis_enabled:
        # Skip rate limiting if Redis not enabled
        return

    api_key = user_info["key"]
    rate_limit = user_info["rate_limit"]

    allowed, current_count, reset_seconds = rate_limiter.check_rate_limit(
        api_key, rate_limit
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "current_count": current_count,
                "limit": rate_limit,
                "reset_seconds": reset_seconds,
            },
        )

    # Add rate limit headers to response (will be set by middleware)
    request.state.rate_limit_info = {
        "current_count": current_count,
        "limit": rate_limit,
        "reset_seconds": reset_seconds,
        "remaining": rate_limit - current_count,
    }
