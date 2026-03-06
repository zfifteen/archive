import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
from .redis_client import redis_manager


@dataclass
class APIKey:
    """Represents a managed API key"""

    key_hash: str  # SHA-256 hash of the key
    key_prefix: str  # First 8 characters for identification
    created_at: datetime
    expires_at: Optional[datetime]
    user_id: str
    rate_limit: int  # requests per hour
    is_active: bool = True
    description: str = ""

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @classmethod
    def generate_key(cls) -> tuple[str, str]:
        """Generate a new API key and its hash"""
        key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash

    def to_dict(self) -> Dict:
        """Convert to dictionary for Redis storage"""
        return {
            "key_hash": self.key_hash,
            "key_prefix": self.key_prefix,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "user_id": self.user_id,
            "rate_limit": self.rate_limit,
            "is_active": self.is_active,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "APIKey":
        """Create from Redis dictionary"""
        return cls(
            key_hash=data["key_hash"],
            key_prefix=data["key_prefix"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
            user_id=data["user_id"],
            rate_limit=int(data["rate_limit"]),
            is_active=data.get("is_active", True),
            description=data.get("description", ""),
        )


class APIKeyManager:
    """Manages API keys using Redis"""

    def __init__(self):
        self.redis_key_prefix = "api_key:"
        self.user_keys_prefix = "user_keys:"

    async def create_key(
        self,
        user_id: str,
        description: str = "",
        expires_days: int = 365,
        rate_limit: int = 1000,
    ) -> str:
        """
        Create a new API key for a user

        Args:
            user_id: Unique identifier for the user
            description: Optional description
            expires_days: Days until expiration (0 for no expiration)
            rate_limit: Requests per hour

        Returns:
            The API key (only returned once)
        """
        redis = await redis_manager.get_redis()

        # Generate key
        key, key_hash = APIKey.generate_key()
        key_prefix = key[:8]

        # Calculate expiration
        expires_at = None
        if expires_days > 0:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)

        # Create APIKey object
        api_key = APIKey(
            key_hash=key_hash,
            key_prefix=key_prefix,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            user_id=user_id,
            rate_limit=rate_limit,
            description=description,
        )

        # Store in Redis
        key_data = api_key.to_dict()
        redis_key = f"{self.redis_key_prefix}{key_hash}"

        # Store key data
        await redis.hset(redis_key, mapping=key_data)

        # Set expiration if specified
        if expires_at:
            ttl_seconds = int((expires_at - datetime.utcnow()).total_seconds())
            await redis.expire(redis_key, ttl_seconds)

        # Add to user's key list
        user_keys_key = f"{self.user_keys_prefix}{user_id}"
        await redis.sadd(user_keys_key, key_hash)

        return key

    async def validate_key(self, api_key: str) -> Optional[APIKey]:
        """
        Validate an API key and return key info if valid

        Args:
            api_key: The API key to validate

        Returns:
            APIKey object if valid, None otherwise
        """
        redis = await redis_manager.get_redis()

        # Hash the key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        redis_key = f"{self.redis_key_prefix}{key_hash}"

        # Get key data
        key_data = await redis.hgetall(redis_key)
        if not key_data:
            return None

        # Parse into APIKey
        api_key_obj = APIKey.from_dict(key_data)

        # Check if active and not expired
        if not api_key_obj.is_active or api_key_obj.is_expired:
            return None

        return api_key_obj

    async def revoke_key(self, user_id: str, key_hash: str) -> bool:
        """
        Revoke an API key

        Args:
            user_id: User who owns the key
            key_hash: Hash of the key to revoke

        Returns:
            True if revoked, False if not found or not owned by user
        """
        redis = await redis_manager.get_redis()

        # Verify ownership
        user_keys_key = f"{self.user_keys_prefix}{user_id}"
        if not await redis.sismember(user_keys_key, key_hash):
            return False

        # Mark as inactive
        redis_key = f"{self.redis_key_prefix}{key_hash}"
        await redis.hset(redis_key, "is_active", False)

        return True

    async def list_user_keys(self, user_id: str) -> List[APIKey]:
        """
        List all API keys for a user

        Args:
            user_id: User ID

        Returns:
            List of APIKey objects
        """
        redis = await redis_manager.get_redis()

        user_keys_key = f"{self.user_keys_prefix}{user_id}"
        key_hashes = await redis.smembers(user_keys_key)

        keys = []
        for key_hash in key_hashes:
            redis_key = f"{self.redis_key_prefix}{key_hash}"
            key_data = await redis.hgetall(redis_key)
            if key_data:
                api_key = APIKey.from_dict(key_data)
                keys.append(api_key)

        return keys

    async def update_key_limits(
        self, user_id: str, key_hash: str, new_rate_limit: int
    ) -> bool:
        """
        Update rate limit for a key

        Args:
            user_id: User who owns the key
            key_hash: Hash of the key
            new_rate_limit: New rate limit

        Returns:
            True if updated, False otherwise
        """
        redis = await redis_manager.get_redis()

        # Verify ownership
        user_keys_key = f"{self.user_keys_prefix}{user_id}"
        if not await redis.sismember(user_keys_key, key_hash):
            return False

        # Update rate limit
        redis_key = f"{self.redis_key_prefix}{key_hash}"
        await redis.hset(redis_key, "rate_limit", new_rate_limit)

        return True

    async def cleanup_expired_keys(self) -> int:
        """
        Clean up expired keys (called periodically)

        Returns:
            Number of keys cleaned up
        """
        redis = await redis_manager.get_redis()

        # Get all key hashes (this is a simplified approach)
        # In production, you'd want a more efficient method
        cleaned = 0

        # Scan for expired keys - this is expensive, so call sparingly
        async for key in redis.scan_iter(f"{self.redis_key_prefix}*"):
            key_data = await redis.hgetall(key)
            if key_data:
                api_key = APIKey.from_dict(key_data)
                if api_key.is_expired:
                    # Remove from user's set
                    user_keys_key = f"{self.user_keys_prefix}{api_key.user_id}"
                    key_hash = key.replace(self.redis_key_prefix, "")
                    await redis.srem(user_keys_key, key_hash)
                    await redis.delete(key)
                    cleaned += 1

        return cleaned


# Global instance
key_manager = APIKeyManager()
