"""
Utilities for sampling from lognormal distributions.
"""
import random
import math
from typing import Optional

try:
    from .model import Band
except ImportError:
    from model import Band


def sample_lognormal(shape: float, scale: float, rng: Optional[random.Random] = None) -> float:
    """
    Sample a value from a lognormal distribution.
    
    The lognormal distribution has parameters:
    - shape (sigma): standard deviation of the underlying normal
    - scale: exp(mu) where mu is the mean of the underlying normal
    - loc is assumed to be 0
    
    Args:
        shape: Lognormal shape parameter (sigma)
        scale: Lognormal scale parameter (exp(mu))
        rng: Optional random number generator for reproducibility
        
    Returns:
        A sample from the lognormal distribution
    """
    if rng is None:
        rng = random
    
    # Lognormal: if X ~ Normal(mu, sigma^2), then exp(X) ~ LogNormal
    # With scale = exp(mu) and shape = sigma:
    # We need to compute mu = log(scale)
    mu = math.log(scale)
    sigma = shape
    
    # Sample from standard normal using Box-Muller transform
    u1 = rng.random()
    u2 = rng.random()
    
    # Guard against u1 = 0.0 to prevent log domain error
    u1 = max(u1, 1e-10)
    
    # Box-Muller: z = sqrt(-2 * ln(u1)) * cos(2*pi*u2)
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    
    # Transform to N(mu, sigma^2)
    normal_sample = mu + sigma * z
    
    # Transform to lognormal
    lognormal_sample = math.exp(normal_sample)
    
    return lognormal_sample


def clamp_gap(gap: float, band: Band) -> float:
    """
    Clamp a gap value to the valid range for a band.
    
    If the band has min_gap and max_gap defined, clamps to those values.
    Otherwise, uses a generic range based on the scale parameter.
    
    Args:
        gap: The gap value to clamp
        band: The band containing clamping parameters
        
    Returns:
        Clamped gap value
    """
    # Determine clamping bounds
    if band.min_gap is not None and band.max_gap is not None:
        min_val = band.min_gap
        max_val = band.max_gap
    else:
        # Generic fallback: [1, 10 * scale]
        min_val = 1.0
        max_val = 10.0 * band.scale
    
    # Clamp the value
    return max(min_val, min(gap, max_val))
