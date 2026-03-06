from fastapi import FastAPI, HTTPException, Depends, Security, Request, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import Header
from typing import List, Optional, Dict
import time
import os
import logging
import uuid
import numpy as np

from ..core.filter import GeometricTradingFilter
from ..core.models import FilterConfig, SignalResult
from ..core.backtester import HistoricalBacktester
from ..core.dispatcher import dispatcher
from .auth import get_api_key
from .limiter import default_limiter
from .redis_client import redis_manager
from .key_manager import key_manager
from .schemas import (
    SignalRequest,
    SignalResponse,
    BatchSignalRequest,
    BatchSignalResponse,
    FibonacciRequest,
    HarmonicLatticeRequest,
    UsageResponse,
    WebhookRegistration,
    WebhookResponse,
    BacktestFibonacciRequest,
    BacktestCustomRequest,
    BacktestResponse,
    BacktestSignal,
    CreateAPIKeyRequest,
    APIKeyResponse,
    APIKeyInfo,
    ListAPIKeysResponse,
    RevokeAPIKeyRequest,
    UpdateAPIKeyLimitsRequest,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Phi-Harmonic Trading Filter API",
    description="""
    High-performance geometric signal filtering for algorithmic trading.
    
    This API provides endpoints to filter trading signals based on phi-harmonic lattice constraints 
    and volatility-adjusted geometric bands. It helps in rejecting geometrically infeasible signals 
    before they reach expensive downstream execution or ML systems.

    <div class="mermaid">
    graph TD
        S[Incoming Signal] --> P{Phi-Filter}
        P -->|In-Bounds| Pass[Valid Signal]
        P -->|Out-of-Bounds| Reject[Noise Rejected]
        
        subgraph Geometric Lattice
            B1[Volatility Band]
            B2[Phi-Harmonic Levels]
        end
        P --- Geometric Lattice
    </div>
    """,
    version="0.1.2",
    contact={
        "name": "Z15 Support",
        "url": "https://github.com/zfifteen/unified-framework",
    },
    license_info={
        "name": "MIT",
    },
    docs_url=None,
    redoc_url=None,
)


@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection and start background tasks"""
    redis = await redis_manager.get_redis()
    logger.info("Redis connection established")

    # Clean up expired keys on startup
    cleaned = await key_manager.cleanup_expired_keys()
    if cleaned > 0:
        logger.info(f"Cleaned up {cleaned} expired API keys")


@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis connection"""
    await redis_manager.close()
    logger.info("Redis connection closed")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with Mermaid.js support for geometric visualizations."""
    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

    mermaid_script = """
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true });
        
        // Re-run mermaid when the DOM changes (e.g., when Swagger UI renders sections)
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                if (mutation.addedNodes.length) {
                    mermaid.run();
                }
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    </script>
    <style>
        .mermaid { background-color: white; padding: 10px; border-radius: 4px; margin: 10px 0; }
    </style>
    """

    content = response.body.decode().replace("</body>", f"{mermaid_script}</body>")
    return HTMLResponse(content=content)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error. Please check logs or contact support."
        },
    )


# Initialize the filter
trading_filter = GeometricTradingFilter()
backtester = HistoricalBacktester(trading_filter)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint to verify service operational status."""
    return {
        "message": "Phi-Harmonic Trading Filter API is operational",
        "version": "0.1.1",
        "timestamp": time.time(),
    }


@app.post("/filter", response_model=SignalResponse, tags=["Filtering"])
async def filter_signal(
    req: SignalRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(default_limiter),
):
    """
    Apply geometric filtering to a standard trading signal.
    Rejects signals that fall outside the expected volatility-adjusted geometric bands.
    """
    try:
        result = trading_filter.filter_signal(
            price=req.price, support=req.support, resistance=req.resistance, atr=req.atr
        )

        # Dispatch to webhooks in background
        event_type = "signal.accepted" if result.passed else "signal.rejected"
        background_tasks.add_task(
            dispatcher.dispatch, api_key, event_type, req.model_dump(), result
        )

        return SignalResponse(
            passed=result.passed,
            rejection_reason=result.rejection_reason,
            confidence=result.confidence,
            filter_time_ns=result.filter_time_ns,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in filter_signal: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing signal filter.")


@app.post("/filter/batch", response_model=BatchSignalResponse, tags=["Filtering"])
async def filter_batch(
    req: BatchSignalRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(default_limiter),
):
    """
    Process multiple signals in a single request for improved efficiency.
    Uses vectorized geometric calculations for sub-microsecond batch processing.
    """
    try:
        if not req.signals:
            return BatchSignalResponse(results=[])

        # Extract fields for vectorized processing
        prices = np.array([s.price for s in req.signals])
        supports = np.array([s.support for s in req.signals])
        resistances = np.array([s.resistance for s in req.signals])
        atrs = np.array([s.atr for s in req.signals])

        results = trading_filter.filter_batch(
            prices=prices, supports=supports, resistances=resistances, atrs=atrs
        )

        # Dispatch individual signals in background
        for i, res in enumerate(results):
            event_type = "signal.accepted" if res.passed else "signal.rejected"
            background_tasks.add_task(
                dispatcher.dispatch,
                api_key,
                event_type,
                req.signals[i].model_dump(),
                res,
            )

        return BatchSignalResponse(
            results=[
                SignalResponse(
                    passed=res.passed,
                    rejection_reason=res.rejection_reason,
                    confidence=res.confidence,
                    filter_time_ns=res.filter_time_ns,
                )
                for res in results
            ]
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in filter_batch: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing batch signals.")


@app.post("/filter/fibonacci", tags=["Filtering"])
async def filter_fibonacci(
    req: FibonacciRequest, api_key: str = Depends(default_limiter)
):
    """
    Filter Fibonacci retracement/extension levels based on current geometric market regime.
    """
    try:
        # We can pass custom configurations if needed, but for now using default
        valid_levels = trading_filter.filter_fibonacci_levels(
            high=req.high, low=req.low, current_price=req.current_price, atr=req.atr
        )
        return valid_levels
    except Exception as e:
        logger.error(f"Error in filter_fibonacci: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error processing Fibonacci levels."
        )


@app.post("/filter/harmonic", tags=["Filtering"])
async def filter_harmonic(
    req: HarmonicLatticeRequest, api_key: str = Depends(default_limiter)
):
    """
    Generate and filter a harmonic lattice around a base price.
    Useful for discovering geometrically significant support/resistance levels.
    """
    try:
        # Temporary config override for this request
        original_config = trading_filter.config
        temp_config = FilterConfig(
            band_multiplier=original_config.band_multiplier,
            harmonic_ratio=req.harmonic_ratio or original_config.harmonic_ratio,
            lattice_k_min=req.k_min
            if req.k_min is not None
            else original_config.lattice_k_min,
            lattice_k_max=req.k_max
            if req.k_max is not None
            else original_config.lattice_k_max,
        )

        trading_filter.config = temp_config
        valid_levels = trading_filter.filter_harmonic_levels(
            base_price=req.base_price, atr=req.atr
        )
        # Restore original config
        trading_filter.config = original_config

        return valid_levels
    except Exception as e:
        logger.error(f"Error in filter_harmonic: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error processing harmonic lattice."
        )


@app.get("/usage", response_model=UsageResponse, tags=["Monitoring"])
async def get_usage(api_key_or_user: str = Depends(default_limiter)):
    """
    Retrieve current API usage statistics and rate limit status for the authenticated key.
    """
    r = await redis_manager.get_redis()

    # Check if this is a managed key
    key_obj = await key_manager.validate_key(api_key_or_user)
    if key_obj:
        # Managed key
        tracking_key = f"usage_stats:key:{key_obj.key_hash}"
        limit_key = f"rate_limit:key:{key_obj.key_hash}"
        rate_limit = key_obj.rate_limit
        api_key_display = f"{key_obj.key_prefix}..."
    else:
        # Default key
        tracking_key = f"usage_stats:default:{api_key_or_user}"
        limit_key = f"rate_limit:default:{api_key_or_user}"
        rate_limit = default_limiter.requests_limit
        api_key_display = f"{api_key_or_user[:8]}...{api_key_or_user[-4:]}"

    stats = await r.hgetall(tracking_key)
    current_usage = await r.get(limit_key)

    total_requests = int(stats.get("total_requests", 0))
    last_request_time = stats.get("last_request_time")
    if last_request_time:
        last_request_time = int(last_request_time)

    limit_remaining = rate_limit - int(current_usage or 0)

    return UsageResponse(
        api_key=api_key_display,
        total_requests=total_requests,
        last_request_time=last_request_time,
        rate_limit_remaining=max(0, limit_remaining),
    )


@app.get("/stats", tags=["Monitoring"])
async def get_stats(api_key: str = Depends(default_limiter)):
    """

    Get global filter performance statistics (rejection rates, latency averages).

    """

    return trading_filter.report()


@app.post("/webhooks/subscribe", response_model=WebhookResponse, tags=["Webhooks"])
async def subscribe_webhook(
    req: WebhookRegistration, api_key: str = Depends(default_limiter)
):
    """

    Register a webhook URL to receive real-time signal alerts.

    Signals that pass the geometric filter will be POSTed to this URL.

    """

    try:
        webhook_id = str(uuid.uuid4())

        r = await redis_manager.get_redis()

        webhook_data = {
            "url": req.url,
            "events": ",".join(req.events),
            "secret": req.secret or "",
            "created_at": int(time.time()),
            "api_key": api_key,
        }

        # Store metadata in Redis

        await r.hset(f"webhook:{webhook_id}", mapping=webhook_data)

        await r.sadd(f"user_webhooks:{api_key}", webhook_id)

        logger.info(
            f"New webhook registered: {webhook_id} for API key {api_key[:8]}..."
        )

        return WebhookResponse(webhook_id=webhook_id)

    except Exception as e:
        logger.error(f"Error registering webhook: {str(e)}")

        raise HTTPException(status_code=500, detail="Error registering webhook.")


@app.get("/webhooks", response_model=List[WebhookResponse], tags=["Webhooks"])
async def list_webhooks(api_key: str = Depends(default_limiter)):
    """

    List all active webhook registrations for the authenticated API key.

    """

    try:
        r = await redis_manager.get_redis()

        webhook_ids = await r.smembers(f"user_webhooks:{api_key}")

        return [WebhookResponse(webhook_id=wid) for wid in webhook_ids]

    except Exception as e:
        logger.error(f"Error listing webhooks: {str(e)}")

        raise HTTPException(status_code=500, detail="Error retrieving webhooks.")


@app.post("/backtest/fibonacci", response_model=BacktestResponse, tags=["Backtesting"])
async def backtest_fibonacci(
    req: BacktestFibonacciRequest, api_key: str = Depends(default_limiter)
):
    """
    Run a historical backtest of Fibonacci signals over provided price arrays.
    Scans for points in history where geometric feasibility and price levels aligned.
    """
    try:
        results = backtester.scan_fibonacci_signals(
            highs=np.array(req.highs),
            lows=np.array(req.lows),
            prices=np.array(req.prices),
            atrs=np.array(req.atrs),
        )
        return BacktestResponse(**results)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in backtest_fibonacci: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error processing Fibonacci backtest."
        )


@app.post("/backtest/custom", response_model=BacktestResponse, tags=["Backtesting"])
async def backtest_custom(
    req: BacktestCustomRequest, api_key: str = Depends(default_limiter)
):
    """
    Run a historical backtest using custom signal data (price, support, resistance, ATR).
    Evaluates which signals in history would have passed the geometric filter.
    """
    try:
        results = backtester.scan_custom_signals(
            prices=np.array(req.prices),
            supports=np.array(req.supports),
            resistances=np.array(req.resistances),
            atrs=np.array(req.atrs),
        )
        return BacktestResponse(**results)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in backtest_custom: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing custom backtest.")


# API Key Management Endpoints
@app.post("/keys", response_model=APIKeyResponse, tags=["API Key Management"])
async def create_api_key(
    req: CreateAPIKeyRequest, user_id: str = Header(..., alias="X-User-ID")
):
    """
    Create a new API key for the authenticated user.

    **Note:** The full API key is only returned once. Store it securely.
    """
    try:
        key = await key_manager.create_key(
            user_id=user_id,
            description=req.description,
            expires_days=req.expires_days,
            rate_limit=req.rate_limit,
        )

        # Get key info for response
        key_obj = await key_manager.validate_key(key)
        if not key_obj:
            raise HTTPException(status_code=500, detail="Failed to create key")

        return APIKeyResponse(
            key=key,
            key_prefix=key_obj.key_prefix,
            created_at=key_obj.created_at,
            expires_at=key_obj.expires_at,
            rate_limit=key_obj.rate_limit,
        )
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create API key")


@app.get("/keys", response_model=ListAPIKeysResponse, tags=["API Key Management"])
async def list_api_keys(user_id: str = Header(..., alias="X-User-ID")):
    """
    List all API keys for the authenticated user.
    """
    try:
        keys = await key_manager.list_user_keys(user_id)
        key_infos = [
            APIKeyInfo(
                key_prefix=key.key_prefix,
                created_at=key.created_at,
                expires_at=key.expires_at,
                rate_limit=key.rate_limit,
                is_active=key.is_active,
                description=key.description,
            )
            for key in keys
        ]
        return ListAPIKeysResponse(keys=key_infos)
    except Exception as e:
        logger.error(f"Error listing API keys: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@app.delete("/keys", tags=["API Key Management"])
async def revoke_api_key(
    req: RevokeAPIKeyRequest, user_id: str = Header(..., alias="X-User-ID")
):
    """
    Revoke an API key by its prefix.
    """
    try:
        # Find the key hash by prefix
        keys = await key_manager.list_user_keys(user_id)
        key_hash = None
        for key in keys:
            if key.key_prefix == req.key_prefix:
                key_hash = key.key_hash
                break

        if not key_hash:
            raise HTTPException(status_code=404, detail="API key not found")

        success = await key_manager.revoke_key(user_id, key_hash)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to revoke key")

        return {"message": "API key revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to revoke API key")


@app.put("/keys/limits", tags=["API Key Management"])
async def update_api_key_limits(
    req: UpdateAPIKeyLimitsRequest, user_id: str = Header(..., alias="X-User-ID")
):
    """
    Update the rate limit for an API key.
    """
    try:
        # Find the key hash by prefix
        keys = await key_manager.list_user_keys(user_id)
        key_hash = None
        for key in keys:
            if key.key_prefix == req.key_prefix:
                key_hash = key.key_hash
                break

        if not key_hash:
            raise HTTPException(status_code=404, detail="API key not found")

        success = await key_manager.update_key_limits(
            user_id, key_hash, req.new_rate_limit
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update key limits")

        return {"message": "API key limits updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating API key limits: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update API key limits")


# Admin Endpoints (require admin privileges)
@app.get("/admin/stats", tags=["Admin"])
async def admin_stats(admin_key: str = Header(..., alias="X-Admin-Key")):
    """
    Admin endpoint to get system-wide statistics.
    Requires X-Admin-Key header.
    """
    try:
        # Simple admin check - in production, verify admin_key properly
        if admin_key != os.getenv("ADMIN_KEY", "admin-phi-2026"):
            raise HTTPException(status_code=403, detail="Admin access required")

        r = await redis_manager.get_redis()

        # Get total keys
        total_keys = await r.scard("user_keys:*")  # This won't work, need to scan

        # Get active keys count (simplified)
        active_keys = 0
        async for key in r.scan_iter("api_key:*"):
            key_data = await r.hgetall(key)
            if key_data and key_data.get("is_active", "True") == "True":
                active_keys += 1

        # Get total requests (simplified)
        total_requests = 0
        async for key in r.scan_iter("usage_stats:*"):
            stats = await r.hgetall(key)
            total_requests += int(stats.get("total_requests", 0))

        return {
            "total_managed_keys": active_keys,
            "total_api_requests": total_requests,
            "system_status": "operational",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get admin stats")
