"""
Rate Limiting for Phi-Harmonic Trading Filter API
"""

from typing import Optional, Tuple
import time
import logging
from .redis_client import RedisClient

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-backed rate limiter using sliding window algorithm"""

    def __init__(self, redis_client: RedisClient, window_seconds: int = 60):
        self.redis = redis_client
        self.window_seconds = window_seconds

    def check_rate_limit(self, key: str, limit: int) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit

        Returns:
            (allowed: bool, current_count: int, reset_seconds: int)
        """
        if limit <= 0:
            return False, 0, 0

        window_key = f"ratelimit:{key}:{int(time.time() / self.window_seconds)}"
        current_count = self.redis.incr(window_key)

        if current_count == 1:
            # First request in this window, set expiration
            self.redis.expire(window_key, self.window_seconds)

        allowed = current_count <= limit
        reset_seconds = self.window_seconds - (int(time.time()) % self.window_seconds)

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for key {key}: {current_count}/{limit}"
            )

        return allowed, current_count, reset_seconds

    def get_remaining_requests(self, key: str, limit: int) -> int:
        """Get remaining requests in current window"""
        window_key = f"ratelimit:{key}:{int(time.time() / self.window_seconds)}"
        current_count = self.redis.get(window_key)
        if current_count is None:
            return limit
        try:
            count = int(current_count)
            return max(0, limit - count)
        except (ValueError, TypeError):
            return limit

    def reset_rate_limit(self, key: str):
        """Reset rate limit for a key (admin function)"""
        pattern = f"ratelimit:{key}:*"
        # Note: Redis doesn't have direct pattern delete, would need SCAN in production
        # For simplicity, just delete current window
        window_key = f"ratelimit:{key}:{int(time.time() / self.window_seconds)}"
        self.redis.delete(window_key)
