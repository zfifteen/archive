from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import os
from .key_manager import key_manager

API_KEY_NAME = "X-API-KEY"
# In production, this would be loaded from a database or secure secret manager
# For now, we use an environment variable or a default for development
DEFAULT_API_KEY = "phi-filter-dev-key-2026"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    # First check if it's the default key
    if api_key_header == os.getenv("API_KEY", DEFAULT_API_KEY):
        return api_key_header

    # Then check if it's a managed key
    key_obj = await key_manager.validate_key(api_key_header)
    if key_obj:
        # Return the user_id for rate limiting and tracking
        return key_obj.user_id

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API Key"
    )
