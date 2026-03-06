"""
Redis Client for Phi-Harmonic Trading Filter API
"""

import redis
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper with connection management and error handling"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self._client: Optional[redis.Redis] = None

    def connect(self) -> redis.Redis:
        """Establish Redis connection with retry logic"""
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                # Test connection
                self._client.ping()
                logger.info(f"Connected to Redis at {self.host}:{self.port}")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return self._client

    @property
    def client(self) -> redis.Redis:
        """Get Redis client, connecting if necessary"""
        return self.connect()

    def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration"""
        try:
            return bool(self.client.set(key, value, ex=ex))
        except redis.RedisError as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    def delete(self, key: str) -> int:
        """Delete key from Redis"""
        try:
            return self.client.delete(key)
        except redis.RedisError as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    def incr(self, key: str) -> Optional[int]:
        """Increment counter in Redis"""
        try:
            return self.client.incr(key)
        except redis.RedisError as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return None

    def expire(self, key: str, time: int) -> bool:
        """Set expiration time for key"""
        try:
            return bool(self.client.expire(key, time))
        except redis.RedisError as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    def close(self):
        """Close Redis connection"""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("Redis connection closed")
