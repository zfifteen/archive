import httpx
import logging
import time
import asyncio
import hmac
import hashlib
import json
from typing import List, Dict, Any, Optional
from .models import SignalResult
from ..api.redis_client import redis_manager

logger = logging.getLogger(__name__)

class SignalDispatcher:
    """
    Dispatches filtered signals to registered webhooks.
    """
    
    def __init__(self, timeout: float = 5.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

    async def dispatch(self, api_key: str, event_type: str, signal_data: Dict[str, Any], result: SignalResult):
        """
        Find webhooks for the user and dispatch the signal.
        """
        try:
            r = await redis_manager.get_redis()
            
            # Get all webhook IDs for this user
            # Redis manager returns decoded strings if decode_responses=True
            webhook_ids = await r.smembers(f"user_webhooks:{api_key}")
            if not webhook_ids:
                return

            tasks = []
            for wid in webhook_ids:
                # Get webhook metadata
                webhook_data = await r.hgetall(f"webhook:{wid}")
                if not webhook_data:
                    continue
                
                # Check if subscribed to this event
                subscribed_events = webhook_data.get("events", "").split(",")
                if event_type not in subscribed_events:
                    continue
                    
                payload = {
                    "event": event_type,
                    "timestamp": int(time.time()),
                    "webhook_id": wid,
                    "data": {
                        "signal": signal_data,
                        "result": {
                            "passed": result.passed,
                            "rejection_reason": result.rejection_reason,
                            "confidence": result.confidence,
                            "filter_time_ns": result.filter_time_ns
                        }
                    }
                }
                
                tasks.append(self._send_to_webhook(
                    webhook_data.get("url"), 
                    payload, 
                    webhook_data.get("secret")
                ))
                
            if tasks:
                # We use gather to run them concurrently.
                # In production, this would likely be offloaded to a task queue like Celery or RQ,
                # but for an MVP, asyncio.gather in a BackgroundTask is sufficient.
                await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in dispatch: {str(e)}")

    async def _send_to_webhook(self, url: str, payload: Dict[str, Any], secret: Optional[str]):
        """
        Send a single POST request to a webhook URL with retries and HMAC signing.
        """
        headers = {"Content-Type": "application/json"}
        body = json.dumps(payload)
        
        if secret:
            signature = hmac.new(
                secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Phi-Signature"] = signature
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.post(url, content=body, headers=headers)
                    response.raise_for_status()
                    logger.info(f"Successfully dispatched to {url}")
                    return True
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                    if attempt < self.max_retries - 1:
                        # Non-blocking sleep between retries
                        await asyncio.sleep(2 ** attempt) 
                    else:
                        logger.error(f"Failed to dispatch to {url} after {self.max_retries} attempts")
        return False

# Global instance
dispatcher = SignalDispatcher()
