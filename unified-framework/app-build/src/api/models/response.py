"""
API Response Models for Phi-Harmonic Trading Filter
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class SignalFilterResponse(BaseModel):
    """Response model for single signal filtering"""

    passed: bool = Field(..., description="Whether signal passed geometric filter")
    rejection_reason: Optional[str] = Field(
        None, description="Reason for rejection if failed"
    )
    confidence: float = Field(..., description="Confidence score (0-1)", ge=0, le=1)
    filter_time_us: float = Field(
        ..., description="Filter execution time in microseconds", ge=0
    )

    class Config:
        schema_extra = {
            "example": {
                "passed": True,
                "rejection_reason": None,
                "confidence": 0.85,
                "filter_time_us": 0.3,
            }
        }


class BatchSignalFilterResponse(BaseModel):
    """Response model for batch signal filtering"""

    results: List[SignalFilterResponse] = Field(
        ..., description="Filtered results for each signal"
    )
    summary: Dict = Field(..., description="Batch processing summary")

    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "passed": True,
                        "rejection_reason": None,
                        "confidence": 0.85,
                        "filter_time_us": 0.3,
                    },
                    {
                        "passed": False,
                        "rejection_reason": "price_above_geometric_bound",
                        "confidence": 0.0,
                        "filter_time_us": 0.25,
                    },
                ],
                "summary": {
                    "total_signals": 2,
                    "passed": 1,
                    "rejected": 1,
                    "rejection_rate": 0.5,
                    "avg_time_us": 0.275,
                },
            }
        }


class FibonacciLevel(BaseModel):
    """Individual Fibonacci level"""

    name: str = Field(..., description="Fibonacci level name (e.g., '61.8%')")
    price: float = Field(..., description="Calculated price level", gt=0)
    confidence: float = Field(..., description="Filter confidence (0-1)", ge=0, le=1)


class FibonacciFilterResponse(BaseModel):
    """Response model for Fibonacci level filtering"""

    valid_levels: List[FibonacciLevel] = Field(
        ..., description="Geometrically valid Fibonacci levels"
    )
    total_levels: int = Field(..., description="Total Fibonacci levels evaluated")
    rejection_rate: float = Field(
        ..., description="Proportion of levels rejected", ge=0, le=1
    )
    filter_time_us: float = Field(..., description="Total filter execution time", ge=0)

    class Config:
        schema_extra = {
            "example": {
                "valid_levels": [
                    {"name": "38.2%", "price": 96.36, "confidence": 0.92},
                    {"name": "61.8%", "price": 103.64, "confidence": 0.78},
                ],
                "total_levels": 7,
                "rejection_rate": 0.71,
                "filter_time_us": 1.5,
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict] = Field(None, description="Additional error details")

    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid input parameters",
                "code": "VALIDATION_ERROR",
                "details": {"price": "must be greater than 0"},
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-02-08T12:00:00Z",
            }
        }
