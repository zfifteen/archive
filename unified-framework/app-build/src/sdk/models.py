"""
Data models for Phi-Harmonic Trading Signal Filter SDK
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Signal(BaseModel):
    """A single trading signal to be filtered"""

    price: float = Field(..., description="Current price of the asset")
    support: float = Field(..., description="Support level")
    resistance: float = Field(..., description="Resistance level")
    volatility: float = Field(..., gt=0, description="Price volatility measure")
    band_multiplier: Optional[float] = Field(
        2.0, description="Band multiplier for filter width"
    )


class FilterResult(BaseModel):
    """Result of filtering a single signal"""

    accepted: bool = Field(
        ..., description="Whether the signal was accepted by the filter"
    )
    confidence: float = Field(
        ..., ge=0, le=1, description="Confidence score of the filtering decision"
    )
    rejection_reason: Optional[str] = Field(
        None, description="Reason for rejection if applicable"
    )


class BatchSignalRequest(BaseModel):
    """Request for batch signal filtering"""

    signals: List[Signal] = Field(..., description="List of signals to filter")
    return_rejected: Optional[bool] = Field(
        False, description="Whether to include rejected signals in response"
    )


class BatchSignalResponse(BaseModel):
    """Response from batch signal filtering"""

    filtered_signals: List[Dict[str, Any]] = Field(
        ..., description="Filtered signals with results"
    )
    summary: Dict[str, int] = Field(
        ..., description="Summary of accepted/rejected counts"
    )
    processing_time_ms: float = Field(
        ..., description="Total processing time in milliseconds"
    )


class FibonacciSignalRequest(BaseModel):
    """Request for Fibonacci level signal filtering"""

    price: float = Field(..., description="Current price")
    support: float = Field(..., description="Support level")
    resistance: float = Field(..., description="Resistance level")
    volatility: float = Field(..., ge=0, description="Volatility measure")
    fib_levels: Optional[List[float]] = Field(
        None, description="Custom Fibonacci levels (default: standard levels)"
    )


class FibonacciSignalResponse(BaseModel):
    """Response from Fibonacci level filtering"""

    accepted: bool = Field(..., description="Whether signal passed Fibonacci filtering")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    nearest_fib_level: Optional[float] = Field(
        None, description="Nearest Fibonacci level if rejected"
    )
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")
