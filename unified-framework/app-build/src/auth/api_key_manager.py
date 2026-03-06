"""
API Key Management for Phi-Harmonic Trading Filter API
"""

from typing import Dict, Optional, Any
import logging
from .redis_client import RedisClient

logger = logging.getLogger(__name__)


class ApiKeyManager:
    """Manages API keys and user tiers using Redis"""

    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        # Default API keys with tiers (in production, these would be managed via admin interface)
        self.default_keys = {
            "demo-key-123": {"tier": "free", "rate_limit": 100},
            "test-key-456": {"tier": "premium", "rate_limit": 10000},
        }

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user info"""
        # First check Redis cache
        cached_info = self._get_cached_key_info(api_key)
        if cached_info:
            return cached_info

        # Check default keys
        if api_key in self.default_keys:
            user_info = self.default_keys[api_key].copy()
            user_info["key"] = api_key
            # Cache in Redis for faster lookups
            self._cache_key_info(api_key, user_info)
            return user_info

        # In production, check database here
        return None

    def get_rate_limit(self, api_key: str) -> int:
        """Get rate limit for API key"""
        user_info = self.validate_api_key(api_key)
        if user_info:
            return user_info.get("rate_limit", 100)
        return 0  # Invalid key, no requests allowed

    def _get_cached_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get API key info from Redis cache"""
        key = f"apikey:{api_key}"
        data = self.redis.get(key)
        if data:
            try:
                import json

                return json.loads(data)
            except (ValueError, TypeError):
                logger.warning(f"Invalid cached data for API key {api_key}")
                self.redis.delete(key)
        return None

    def _cache_key_info(self, api_key: str, info: Dict[str, Any], ttl: int = 3600):
        """Cache API key info in Redis"""
        key = f"apikey:{api_key}"
        try:
            import json

            self.redis.set(key, json.dumps(info), ex=ttl)
        except Exception as e:
            logger.error(f"Failed to cache API key info: {e}")

    def invalidate_cache(self, api_key: str):
        """Invalidate cached API key info"""
        key = f"apikey:{api_key}"
        self.redis.delete(key)
