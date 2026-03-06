"""
Phi-Harmonic Trading Signal Filter SDK

A Python SDK for the Phi-Harmonic Trading Signal Filter SaaS API.
Provides easy-to-use methods for filtering trading signals using geometric constraints.
"""

from .client import PhiHarmonicClient
from .models import (
    Signal,
    BatchSignalRequest,
    BatchSignalResponse,
    FibonacciSignalRequest,
    FibonacciSignalResponse,
    FilterResult,
)

__version__ = "1.0.0"
__all__ = [
    "PhiHarmonicClient",
    "Signal",
    "BatchSignalRequest",
    "BatchSignalResponse",
    "FibonacciSignalRequest",
    "FibonacciSignalResponse",
    "FilterResult",
]
