"""
API Request Models for Phi-Harmonic Trading Filter
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SignalFilterRequest(BaseModel):
    """Request model for single signal filtering"""

    price: float = Field(..., description="Signal price level", gt=0)
    support: float = Field(..., description="Support level (lower bound)", gt=0)
    resistance: float = Field(..., description="Resistance level (upper bound)", gt=0)
    volatility: float = Field(
        ..., description="Volatility measure (ATR, std dev)", ge=0
    )

    class Config:
        schema_extra = {
            "example": {
                "price": 102.50,
                "support": 98.00,
                "resistance": 108.00,
                "volatility": 2.0,
            }
        }


class BatchSignalFilterRequest(BaseModel):
    """Request model for batch signal filtering"""

    signals: List[SignalFilterRequest] = Field(
        ..., description="List of signals to filter"
    )

    class Config:
        schema_extra = {
            "example": {
                "signals": [
                    {
                        "price": 102.50,
                        "support": 98.00,
                        "resistance": 108.00,
                        "volatility": 2.0,
                    },
                    {
                        "price": 105.75,
                        "support": 101.00,
                        "resistance": 110.00,
                        "volatility": 1.5,
                    },
                ]
            }
        }


class FibonacciFilterRequest(BaseModel):
    """Request model for Fibonacci level filtering"""

    high: float = Field(..., description="Recent high price", gt=0)
    low: float = Field(..., description="Recent low price", gt=0)
    volatility: float = Field(..., description="Volatility measure", ge=0)

    class Config:
        schema_extra = {
            "example": {
                "high": 110.0,
                "low": 90.0,
                "volatility": 2.5,
            }
        }
