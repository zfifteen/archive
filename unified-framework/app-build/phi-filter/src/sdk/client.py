import httpx
from typing import List, Optional, Dict, Any


class PhiFilterClient:
    """
    Client SDK for the Phi-Harmonic Trading Filter API.

    Provides both synchronous and asynchronous methods to interact with the API.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        user_id: Optional[str] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self.headers = {"X-API-KEY": api_key}
        if user_id:
            self.headers["X-User-ID"] = user_id

    def filter_signal(
        self, price: float, support: float, resistance: float, atr: float
    ) -> Dict[str, Any]:
        """
        Synchronously filters a single trading signal.
        """
        url = f"{self.base_url}/filter"
        payload = {
            "price": price,
            "support": support,
            "resistance": resistance,
            "atr": atr,
        }
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def filter_signal_async(
        self, price: float, support: float, resistance: float, atr: float
    ) -> Dict[str, Any]:
        """
        Asynchronously filters a single trading signal.
        """
        url = f"{self.base_url}/filter"
        payload = {
            "price": price,
            "support": support,
            "resistance": resistance,
            "atr": atr,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def filter_batch(self, signals: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Synchronously filters multiple trading signals in a single batch request.
        """
        url = f"{self.base_url}/filter/batch"
        payload = {"signals": signals}
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def filter_batch_async(
        self, signals: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Asynchronously filters multiple trading signals in a single batch request.
        """
        url = f"{self.base_url}/filter/batch"
        payload = {"signals": signals}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def get_usage(self) -> Dict[str, Any]:
        """
        Synchronously retrieves current API usage statistics.
        """
        url = f"{self.base_url}/usage"
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_usage_async(self) -> Dict[str, Any]:
        """
        Asynchronously retrieves current API usage statistics.
        """
        url = f"{self.base_url}/usage"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def get_stats(self) -> Dict[str, Any]:
        """
        Synchronously retrieves global filter performance statistics.
        """
        url = f"{self.base_url}/stats"
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_stats_async(self) -> Dict[str, Any]:
        """
        Asynchronously retrieves global filter performance statistics.
        """
        url = f"{self.base_url}/stats"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    # API Key Management Methods
    def create_api_key(
        self, description: str = "", expires_days: int = 365, rate_limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Creates a new API key for the authenticated user.
        """
        if not self.user_id:
            raise ValueError("user_id required for key management operations")
        url = f"{self.base_url}/keys"
        payload = {
            "description": description,
            "expires_days": expires_days,
            "rate_limit": rate_limit,
        }
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def create_api_key_async(
        self, description: str = "", expires_days: int = 365, rate_limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Asynchronously creates a new API key for the authenticated user.
        """
        if not self.user_id:
            raise ValueError("user_id required for key management operations")
        url = f"{self.base_url}/keys"
        payload = {
            "description": description,
            "expires_days": expires_days,
            "rate_limit": rate_limit,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def list_api_keys(self) -> Dict[str, Any]:
        """
        Lists all API keys for the authenticated user.
        """
        if not self.user_id:
            raise ValueError("user_id required for key management operations")
        url = f"{self.base_url}/keys"
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def list_api_keys_async(self) -> Dict[str, Any]:
        """
        Asynchronously lists all API keys for the authenticated user.
        """
        if not self.user_id:
            raise ValueError("user_id required for key management operations")
        url = f"{self.base_url}/keys"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def revoke_api_key(self, key_prefix: str) -> Dict[str, Any]:
        """
        Revokes an API key by its prefix.
        """
        if not self.user_id:
            raise ValueError("user_id required for key management operations")
        url = f"{self.base_url}/keys"
        payload = {"key_prefix": key_prefix}
        with httpx.Client() as client:
            response = client.delete(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def revoke_api_key_async(self, key_prefix: str) -> Dict[str, Any]:
        """
        Asynchronously revokes an API key by its prefix.
        """
        if not self.user_id:
            raise ValueError("user_id required for key management operations")
        url = f"{self.base_url}/keys"
        payload = {"key_prefix": key_prefix}
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def update_key_limits(self, key_prefix: str, new_rate_limit: int) -> Dict[str, Any]:
        """
        Updates the rate limit for an API key.
        """
        if not self.user_id:
            raise ValueError("user_id required for key management operations")
        url = f"{self.base_url}/keys/limits"
        payload = {"key_prefix": key_prefix, "new_rate_limit": new_rate_limit}
        with httpx.Client() as client:
            response = client.put(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def update_key_limits_async(
        self, key_prefix: str, new_rate_limit: int
    ) -> Dict[str, Any]:
        """
        Asynchronously updates the rate limit for an API key.
        """
        if not self.user_id:
            raise ValueError("user_id required for key management operations")
        url = f"{self.base_url}/keys/limits"
        payload = {"key_prefix": key_prefix, "new_rate_limit": new_rate_limit}
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
