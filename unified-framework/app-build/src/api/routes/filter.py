"""
API Routes for Phi-Harmonic Trading Filter
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import time

from ..models.request import (
    SignalFilterRequest,
    BatchSignalFilterRequest,
    FibonacciFilterRequest,
)
from ..models.response import (
    SignalFilterResponse,
    BatchSignalFilterResponse,
    FibonacciFilterResponse,
    FibonacciLevel,
    ErrorResponse,
)
from ...core.filter import PhiHarmonicFilter, FilterConfig
from ...config.settings import settings
from ...auth.dependencies import verify_api_key, check_rate_limit


router = APIRouter()


def get_filter() -> PhiHarmonicFilter:
    """Dependency to get configured filter instance"""
    config = FilterConfig(band_multiplier=settings.default_band_multiplier)
    return PhiHarmonicFilter(config)


@router.post(
    "/signals",
    response_model=SignalFilterResponse,
    summary="Filter Single Trading Signal",
    description="Apply geometric filtering to a single trading signal",
)
async def filter_signal(
    request: SignalFilterRequest,
    user_info: Dict[str, Any] = Depends(verify_api_key),
    rate_limit: None = Depends(check_rate_limit),
    filter: PhiHarmonicFilter = Depends(get_filter),
):
    """Filter a single trading signal using geometric constraints"""
    try:
        result = filter.filter_signal(
            price=request.price,
            support=request.support,
            resistance=request.resistance,
            volatility=request.volatility,
        )

        return SignalFilterResponse(
            passed=result.passed,
            rejection_reason=result.rejection_reason,
            confidence=result.confidence,
            filter_time_us=result.filter_time_ns / 1000,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter error: {str(e)}")


@router.post(
    "/signals/batch",
    response_model=BatchSignalFilterResponse,
    summary="Filter Batch of Trading Signals",
    description="Apply geometric filtering to multiple trading signals in batch",
)
async def filter_signals_batch(
    request: BatchSignalFilterRequest,
    user_info: Dict[str, Any] = Depends(verify_api_key),
    rate_limit: None = Depends(check_rate_limit),
    filter: PhiHarmonicFilter = Depends(get_filter),
):
    """Filter multiple trading signals in batch for high throughput"""
    try:
        if len(request.signals) > settings.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size exceeds maximum ({settings.max_batch_size})",
            )

        start_time = time.time()
        results = filter.filter_batch([signal.dict() for signal in request.signals])
        total_time = time.time() - start_time

        response_results = []
        passed_count = 0

        for result in results:
            response_result = SignalFilterResponse(
                passed=result.passed,
                rejection_reason=result.rejection_reason,
                confidence=result.confidence,
                filter_time_us=result.filter_time_ns / 1000,
            )
            response_results.append(response_result)
            if result.passed:
                passed_count += 1

        summary = {
            "total_signals": len(results),
            "passed": passed_count,
            "rejected": len(results) - passed_count,
            "rejection_rate": (len(results) - passed_count) / len(results)
            if results
            else 0,
            "avg_time_us": (total_time * 1e6) / len(results) if results else 0,
            "total_time_ms": total_time * 1000,
        }

        return BatchSignalFilterResponse(results=response_results, summary=summary)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch filter error: {str(e)}")


@router.post(
    "/fibonacci",
    response_model=FibonacciFilterResponse,
    summary="Filter Fibonacci Retracement Levels",
    description="Apply geometric filtering to Fibonacci retracement levels",
)
async def filter_fibonacci_levels(
    request: FibonacciFilterRequest,
    user_info: Dict[str, Any] = Depends(verify_api_key),
    rate_limit: None = Depends(check_rate_limit),
    filter: PhiHarmonicFilter = Depends(get_filter),
):
    """Filter Fibonacci retracement levels using geometric constraints"""
    try:
        # Calculate Fibonacci levels manually (simplified version)
        price_range = request.high - request.low
        fib_ratios = {
            "0.0%": 0.000,
            "23.6%": 0.236,
            "38.2%": 0.382,
            "50.0%": 0.500,
            "61.8%": 0.618,
            "78.6%": 0.786,
            "100.0%": 1.000,
        }

        valid_levels = []
        start_time = time.time()

        for name, ratio in fib_ratios.items():
            level = request.low + price_range * ratio
            result = filter.filter_signal(
                level, request.low, request.high, request.volatility
            )

            if result.passed:
                valid_levels.append(
                    FibonacciLevel(name=name, price=level, confidence=result.confidence)
                )

        total_time = time.time() - start_time

        return FibonacciFilterResponse(
            valid_levels=valid_levels,
            total_levels=len(fib_ratios),
            rejection_rate=1 - (len(valid_levels) / len(fib_ratios)),
            filter_time_us=total_time * 1e6,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fibonacci filter error: {str(e)}")
