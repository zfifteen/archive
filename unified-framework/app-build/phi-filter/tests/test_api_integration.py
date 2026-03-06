import unittest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add project root to path so 'src' is a package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.main import app, default_limiter
from src.api.redis_client import redis_manager

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Clear overrides before each test
        app.dependency_overrides = {}

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Phi-Harmonic Trading Filter API is operational", response.json()["message"])

    def test_filter_signal_success(self):
        # Override limiter to bypass Redis
        app.dependency_overrides[default_limiter] = lambda: "test-key"
        
        payload = {
            "price": 100.0,
            "support": 95.0,
            "resistance": 105.0,
            "atr": 2.0
        }
        response = self.client.post("/filter", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["passed"])

    def test_filter_signal_reject(self):
        app.dependency_overrides[default_limiter] = lambda: "test-key"
        
        payload = {
            "price": 110.0,
            "support": 95.0,
            "resistance": 105.0,
            "atr": 2.0
        }
        response = self.client.post("/filter", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["passed"])
        self.assertEqual(response.json()["rejection_reason"], "price_too_high")

    def test_filter_batch_success(self):
        app.dependency_overrides[default_limiter] = lambda: "test-key"
        
        payload = {
            "signals": [
                {
                    "price": 100.0,
                    "support": 95.0,
                    "resistance": 105.0,
                    "atr": 2.0
                },
                {
                    "price": 110.0,
                    "support": 95.0,
                    "resistance": 105.0,
                    "atr": 2.0
                }
            ]
        }
        response = self.client.post("/filter/batch", json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]["passed"])
        self.assertFalse(results[1]["passed"])

    @patch("src.api.redis_client.redis_manager.get_redis")
    def test_usage_endpoint(self, mock_get_redis):
        # Override limiter to bypass Redis for auth
        app.dependency_overrides[default_limiter] = lambda: "test-api-key-string"
        
        # Mock redis response for hgetall and get
        mock_redis_conn = AsyncMock()
        mock_redis_conn.hgetall.return_value = {
            "total_requests": "42",
            "last_request_time": "1675862400"
        }
        mock_redis_conn.get.return_value = "5"
        mock_get_redis.return_value = mock_redis_conn
        
        response = self.client.get("/usage")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_requests"], 42)
        self.assertEqual(data["rate_limit_remaining"], 95)
        self.assertNotIn("test-api-key-string", data["api_key"])
        self.assertTrue(data["api_key"].startswith("test-api"))

    def test_filter_signal_invalid_payload(self):
        # Even with invalid payload, limiter is checked first if not overridden
        app.dependency_overrides[default_limiter] = lambda: "test-key"
        
        # Missing atr
        payload = {
            "price": 100.0,
            "support": 95.0,
            "resistance": 105.0
        }
        response = self.client.post("/filter", json=payload)
        self.assertEqual(response.status_code, 422) # Validation Error

    def test_backtest_fibonacci(self):
        app.dependency_overrides[default_limiter] = lambda: "test-key"
        payload = {
            "highs": [110.0, 110.0, 110.0],
            "lows": [90.0, 90.0, 90.0],
            "prices": [100.0, 102.36, 94.72],
            "atrs": [2.5, 2.5, 2.5]
        }
        response = self.client.post("/backtest/fibonacci", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_intervals"], 3)
        self.assertGreaterEqual(data["valid_signals_found"], 1)

    def test_backtest_custom(self):
        app.dependency_overrides[default_limiter] = lambda: "test-key"
        payload = {
            "prices": [100.0, 120.0, 100.0],
            "supports": [95.0, 95.0, 95.0],
            "resistances": [105.0, 105.0, 105.0],
            "atrs": [5.0, 5.0, 5.0]
        }
        response = self.client.post("/backtest/custom", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_intervals"], 3)
        self.assertEqual(data["valid_signals_found"], 2)

if __name__ == '__main__':
    unittest.main()