from dataclasses import dataclass
from typing import Optional

@dataclass
class FilterConfig:
    """Configuration for geometric filter"""
    band_multiplier: float = 2.0  # ATR multiplier for volatility bands
    min_rejection_rate: float = 0.50  # Minimum expected rejection (50%)
    max_rejection_rate: float = 0.95  # Maximum before over-filtering
    adaptive: bool = True  # Auto-adjust parameters based on market regime
    
    # Advanced Geometric Settings
    harmonic_ratio: float = 1.618033988749895  # Golden Ratio (PHI)
    lattice_k_min: int = -10
    lattice_k_max: int = 10
    custom_ratios: Optional[list[float]] = None  # Explicitly defined ratios

@dataclass
class SignalResult:
    """Result of signal filtering"""
    passed: bool
    rejection_reason: Optional[str]
    confidence: float  # 0-1 scale
    filter_time_ns: int
