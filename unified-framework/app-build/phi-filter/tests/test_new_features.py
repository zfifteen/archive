import pytest
import numpy as np
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add project root to path so 'src' is a package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.main import app, default_limiter
from src.api.redis_client import redis_manager
from src.core.filter import GeometricTradingFilter
from src.core.models import FilterConfig

client = TestClient(app)

# Mock API Key for tests
API_KEY = "test_key_12345"

@pytest.fixture(autouse=True)
def override_limiter():
    app.dependency_overrides[default_limiter] = lambda: API_KEY
    yield
    app.dependency_overrides = {}

class TestNewFeatures:
    def test_vectorized_batch_core(self):
        """Test the new vectorized filter_batch method in core"""
        trading_filter = GeometricTradingFilter()
        
        n = 10
        prices = np.array([150.0] * n)
        supports = np.array([140.0] * n)
        resistances = np.array([160.0] * n)
        atrs = np.array([2.0] * n)
        
        results = trading_filter.filter_batch(prices, supports, resistances, atrs)
        
        assert len(results) == n
        for res in results:
            assert res.passed is True
            assert res.rejection_reason is None
            assert 0.0 <= res.confidence <= 1.0

    def test_filter_harmonic_endpoint(self):
        """Test the new /filter/harmonic endpoint"""
        # Increase ATR so that levels -1 and 1 pass the 4.0 multiplier check
        # base_price = 100.0, ratio = 1.618
        # -1 level = 61.80. Distance = 38.2.
        # 1 level = 161.80. Distance = 61.8.
        # ATR = 40.0, multiplier = 2.0 -> band = 80.0.
        payload = {
            "base_price": 100.0,
            "atr": 40.0, 
            "harmonic_ratio": 1.618,
            "k_min": -1,
            "k_max": 1
        }
        
        response = client.post(
            "/filter/harmonic",
            json=payload,
            headers={"X-API-KEY": API_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "0" in data
        assert "-1" in data
        assert "1" in data

    @patch("src.api.redis_client.redis_manager.get_redis")
    def test_webhook_subscription(self, mock_get_redis):
        """Test webhook registration and listing"""
        # Mock redis
        mock_redis_conn = AsyncMock()
        mock_redis_conn.hset.return_value = 1
        mock_redis_conn.sadd.return_value = 1
        mock_redis_conn.smembers.return_value = ["mock_webhook_id_123"]
        mock_get_redis.return_value = mock_redis_conn

        # 1. Subscribe
        sub_payload = {
            "url": "https://example.com/webhook",
            "events": ["signal.accepted"],
            "secret": "supersecret"
        }
        
        response = client.post(
            "/webhooks/subscribe",
            json=sub_payload,
            headers={"X-API-KEY": API_KEY}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "webhook_id" in data
        
        # 2. List
        response = client.get(
            "/webhooks",
            headers={"X-API-KEY": API_KEY}
        )
        
        assert response.status_code == 200
        webhooks = response.json()
        assert any(w["webhook_id"] == "mock_webhook_id_123" for w in webhooks)

    def test_custom_fibonacci_ratios(self):
        """Test Fibonacci filtering with custom ratio in config"""
        # We'll use a specific ratio and check if it appears in results
        # Since we use the global trading_filter in main.py, we can't easily change its config per request 
        # unless we add it to the request schema.
        # But wait, filter_fibonacci doesn't take custom ratios in its schema yet.
        # Let's check if my previous change to filter_fibonacci_levels works.
        
        trading_filter = GeometricTradingFilter(FilterConfig(harmonic_ratio=1.414)) # Square root of 2
        
        results = trading_filter.filter_fibonacci_levels(
            high=200.0,
            low=100.0,
            current_price=150.0,
            atr=5.0
        )
        
        # 1.414 - 1.0 = 0.414. So level 141.4 should be there as "Custom(1.414)"
        assert any("Custom(1.414)" in name for name in results.keys())
