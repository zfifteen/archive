import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import json
import time

from src.core.dispatcher import SignalDispatcher
from src.core.models import SignalResult
from src.api.redis_client import redis_manager

class TestSignalDispatcher(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.dispatcher = SignalDispatcher(timeout=0.1, max_retries=1)
        self.api_key = "test_api_key_123"
        self.webhook_id = "test_webhook_id_456"
        self.webhook_url = "http://example.com/webhook"
        self.webhook_secret = "test_secret"

    @patch("src.api.redis_client.redis_manager.get_redis")
    @patch("src.core.dispatcher.httpx.AsyncClient.post")
    async def test_dispatch_success(self, mock_post, mock_get_redis):
        # Mock Redis
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis
        
        mock_redis.smembers.return_value = {self.webhook_id}
        mock_redis.hgetall.return_value = {
            "url": self.webhook_url,
            "events": "signal.accepted,signal.rejected",
            "secret": self.webhook_secret
        }
        
        # Mock HTTP Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        signal_data = {"price": 100.0, "support": 90.0, "resistance": 110.0, "atr": 5.0}
        result = SignalResult(passed=True, rejection_reason=None, confidence=0.8, filter_time_ns=1000)
        
        await self.dispatcher.dispatch(self.api_key, "signal.accepted", signal_data, result)
        
        # Verify Redis calls
        mock_redis.smembers.assert_called_with(f"user_webhooks:{self.api_key}")
        mock_redis.hgetall.assert_called_with(f"webhook:{self.webhook_id}")
        
        # Verify HTTP call
        self.assertTrue(mock_post.called)
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], self.webhook_url)
        
        # Check payload
        payload = json.loads(kwargs["content"])
        self.assertEqual(payload["event"], "signal.accepted")
        self.assertEqual(payload["data"]["signal"]["price"], 100.0)
        self.assertEqual(payload["data"]["result"]["passed"], True)
        
        # Check HMAC header
        self.assertIn("X-Phi-Signature", kwargs["headers"])

    @patch("src.api.redis_client.redis_manager.get_redis")
    async def test_dispatch_no_webhooks(self, mock_get_redis):
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis
        mock_redis.smembers.return_value = set()
        
        signal_data = {"price": 100.0}
        result = SignalResult(passed=True, rejection_reason=None, confidence=0.8, filter_time_ns=1000)
        
        # Should return early without error
        await self.dispatcher.dispatch(self.api_key, "signal.accepted", signal_data, result)
        mock_redis.hgetall.assert_not_called()

    @patch("src.api.redis_client.redis_manager.get_redis")
    @patch("src.core.dispatcher.httpx.AsyncClient.post")
    async def test_dispatch_event_mismatch(self, mock_post, mock_get_redis):
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis
        
        mock_redis.smembers.return_value = {self.webhook_id}
        mock_redis.hgetall.return_value = {
            "url": self.webhook_url,
            "events": "signal.accepted",
            "secret": self.webhook_secret
        }
        
        signal_data = {"price": 100.0}
        result = SignalResult(passed=False, rejection_reason="too_high", confidence=0.0, filter_time_ns=1000)
        
        # Dispatching 'signal.rejected' but webhook only subscribed to 'signal.accepted'
        await self.dispatcher.dispatch(self.api_key, "signal.rejected", signal_data, result)
        
        self.assertFalse(mock_post.called)

if __name__ == "__main__":
    unittest.main()
