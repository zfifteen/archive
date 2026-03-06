from fastapi import HTTPException, status, Depends
from .redis_client import redis_manager
from .auth import get_api_key
from .key_manager import key_manager
import time


class RateLimiter:
    def __init__(self, requests_limit: int = 100, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds

    async def __call__(self, api_key_or_user: str = Depends(get_api_key)):
        r = await redis_manager.get_redis()

        # Determine if this is a managed key (user_id) or default key
        key_obj = await key_manager.validate_key(api_key_or_user)
        if key_obj:
            # Managed key - use per-key limits
            limit_key = f"rate_limit:key:{key_obj.key_hash}"
            requests_limit = key_obj.rate_limit
            tracking_key = f"usage_stats:key:{key_obj.key_hash}"
            return_value = key_obj.user_id
        else:
            # Default key - use global limits
            limit_key = f"rate_limit:default:{api_key_or_user}"
            requests_limit = self.requests_limit
            tracking_key = f"usage_stats:default:{api_key_or_user}"
            return_value = api_key_or_user

        # Rate Limiting
        current_usage = await r.get(limit_key)

        if current_usage and int(current_usage) >= requests_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Upgrade to Pro for higher limits.",
            )

        # Increment usage and set expiration if new
        pipe = r.pipeline()
        pipe.incr(limit_key)
        if not current_usage:
            pipe.expire(limit_key, self.window_seconds)

        # Usage Tracking (Total requests per key)
        pipe.hincrby(tracking_key, "total_requests", 1)
        pipe.hset(tracking_key, "last_request_time", int(time.time()))

        await pipe.execute()
        return return_value


# Default limiter: 100 requests per minute
default_limiter = RateLimiter(requests_limit=100, window_seconds=60)
