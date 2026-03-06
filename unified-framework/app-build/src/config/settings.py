"""
Application Configuration Settings
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Settings:
    """Application settings"""

    # API Settings
    app_name: str = "Phi-Harmonic Trading Filter API"
    version: str = "1.0.0"
    description: str = (
        "High-performance geometric signal filtering for algorithmic trading"
    )

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Security Settings
    api_key_header: str = "X-API-Key"
    api_keys: Optional[List[str]] = None

    # Rate Limiting (requests per minute per user)
    rate_limit_default: int = 1000
    rate_limit_premium: int = 10000

    # Redis Settings (for caching and rate limiting)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_enabled: bool = True  # Enable Redis for production features

    # Filter Settings
    default_band_multiplier: float = 2.0
    max_batch_size: int = 1000

    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = ["demo-key-123", "test-key-456"]


# Global settings instance
settings = Settings()
