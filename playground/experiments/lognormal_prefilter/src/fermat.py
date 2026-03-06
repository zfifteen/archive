"""
Lognormal-guided Fermat factorization stage.
"""
import math
import random
from typing import Optional

try:
    from .model import ModelStore
    from .config import SearchPolicyConfig
    from .sampling import sample_lognormal, clamp_gap
except ImportError:
    from model import ModelStore
    from config import SearchPolicyConfig
    from sampling import sample_lognormal, clamp_gap


def isqrt(n: int) -> int:
    """
    Compute the integer square root of n.
    
    Returns floor(sqrt(n)).
    
    Args:
        n: Non-negative integer
        
    Returns:
        Integer square root of n
    """
    if n < 0:
        raise ValueError("isqrt requires non-negative input")
    if n == 0:
        return 0
    
    # Use Python's built-in if available (Python 3.8+)
    if hasattr(math, 'isqrt'):
        return math.isqrt(n)
    
    # Newton's method fallback
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def is_perfect_square(n: int) -> bool:
    """
    Check if n is a perfect square.
    
    Args:
        n: Non-negative integer
        
    Returns:
        True if n is a perfect square, False otherwise
    """
    if n < 0:
        return False
    if n == 0:
        return True
    
    root = isqrt(n)
    return root * root == n


def lognormal_fermat_stage(
    N: int,
    model_store: ModelStore,
    cfg: SearchPolicyConfig
) -> Optional[int]:
    """
    Try to factor N using a Fermat-style search where candidate x values
    near floor(sqrt(N)) are chosen using a lognormal prime-gap model.
    
    Args:
        N: Number to factor (should be a semiprime)
        model_store: ModelStore containing lognormal band parameters
        cfg: Search policy configuration
        
    Returns:
        A non-trivial factor of N on success, or None on failure
    """
    # Handle trivial case
    if N % 2 == 0:
        return 2
    
    if N < 2:
        return None
    
    # Compute p0 = floor(sqrt(N))
    p0 = isqrt(N)
    
    # Get the appropriate band for p0
    band = model_store.get_closest_band(p0)
    
    # Initialize RNG if seed is provided
    rng = random.Random(cfg.random_seed) if cfg.random_seed is not None else random
    
    # Maintain cumulative offset and direction
    cumulative_offset = 0.0
    direction = 1
    
    # Try max_steps candidates
    for step in range(cfg.max_steps):
        # Sample gap from lognormal distribution
        g = sample_lognormal(band.shape, band.scale, rng)
        
        # Clamp the gap
        g = clamp_gap(g, band)
        
        # Update cumulative offset
        cumulative_offset += g * cfg.radius_scale
        
        # Update direction based on mode
        if cfg.direction_mode == "ALTERNATE":
            direction = -direction
        elif cfg.direction_mode == "RANDOM":
            direction = rng.choice([-1, 1])
        
        # Compute candidate x value
        x_candidate = p0 + direction * round(cumulative_offset)
        
        # Skip if x_candidate is invalid
        if x_candidate <= 0:
            continue
        
        # Compute y^2 = x^2 - N
        y2 = x_candidate * x_candidate - N
        
        # Skip if y^2 is negative
        if y2 < 0:
            continue
        
        # Check if y^2 is a perfect square
        if is_perfect_square(y2):
            y = isqrt(y2)
            
            # Compute candidate factors
            a = x_candidate - y
            b = x_candidate + y
            
            # Check if we found a non-trivial factor
            if a > 1 and N % a == 0:
                return a
            if b > 1 and b < N and N % b == 0:
                return b
    
    # No factor found
    return None
