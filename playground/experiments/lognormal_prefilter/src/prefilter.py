"""
Lognormal candidate-list pre-filter and classical factorization fallbacks.
"""
import random
import math
from typing import Optional

try:
    from .model import ModelStore, Band
    from .config import SearchPolicyConfig
    from .sampling import sample_lognormal, clamp_gap
    from .fermat import isqrt
except ImportError:
    from model import ModelStore, Band
    from config import SearchPolicyConfig
    from sampling import sample_lognormal, clamp_gap
    from fermat import isqrt


def generate_lognormal_offsets(
    p0: int,
    band: Band,
    cfg: SearchPolicyConfig
) -> list[int]:
    """
    Generate a list of integer offsets around p0 based on the lognormal prime-gap model.
    
    Offsets are signed (±) according to cfg.direction_mode.
    
    Args:
        p0: Base value (typically floor(sqrt(N)))
        band: Band containing lognormal parameters
        cfg: Search policy configuration
        
    Returns:
        List of signed integer offsets
    """
    # Initialize RNG if seed is provided
    rng = random.Random(cfg.random_seed) if cfg.random_seed is not None else random
    
    offsets = []
    cumulative_offset = 0.0
    direction = 1
    
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
        
        # Compute signed offset
        offset = direction * round(cumulative_offset)
        offsets.append(offset)
    
    return offsets


def probably_prime(n: int, k: int = 5, rng: Optional[random.Random] = None) -> bool:
    """
    Miller-Rabin primality test.
    
    A simple probabilistic primality test. Returns False if n is definitely
    composite, True if n is probably prime.
    
    Args:
        n: Number to test
        k: Number of rounds (higher = more accurate)
        rng: Optional random number generator for reproducibility
        
    Returns:
        True if n is probably prime, False if definitely composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    if rng is None:
        rng = random
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop
    for _ in range(k):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


def pollard_rho(N: int, max_iterations: int = 100000, rng: Optional[random.Random] = None) -> Optional[int]:
    """
    Pollard's rho algorithm for factorization.
    
    A simple classical factorization algorithm used as a fallback.
    
    Args:
        N: Number to factor
        max_iterations: Maximum number of iterations
        rng: Optional random number generator for reproducibility
        
    Returns:
        A non-trivial factor of N, or None if not found
    """
    if N % 2 == 0:
        return 2
    
    if N < 2:
        return None
    
    if rng is None:
        rng = random
    
    # Try multiple times with different starting values
    for attempt in range(5):
        # Choose random starting values
        x = rng.randint(2, N - 1)
        y = x
        c = rng.randint(1, N - 1)
        d = 1
        
        iterations = 0
        while d == 1 and iterations < max_iterations:
            # Pollard's rho function: f(x) = (x^2 + c) mod N
            x = (x * x + c) % N
            y = (y * y + c) % N
            y = (y * y + c) % N
            
            d = math.gcd(abs(x - y), N)
            iterations += 1
        
        if d != N and d > 1:
            return d
    
    return None


def factor_with_candidate_prefilter(
    N: int,
    model_store: ModelStore,
    cfg: SearchPolicyConfig
) -> Optional[int]:
    """
    Use the lognormal model to generate candidate offsets near sqrt(N),
    test those candidates as possible factors, then fall back to a classical method.
    
    Args:
        N: Number to factor
        model_store: ModelStore containing lognormal band parameters
        cfg: Search policy configuration
        
    Returns:
        A non-trivial factor of N, or None if not found
    """
    # Handle trivial case
    if N % 2 == 0:
        return 2
    
    if N < 2:
        return None
    
    # Compute p0 = floor(sqrt(N))
    p0 = isqrt(N)
    
    # Get the appropriate band
    band = model_store.get_closest_band(p0)
    
    # Generate candidate offsets
    offsets = generate_lognormal_offsets(p0, band, cfg)
    
    # Initialize RNG if seed is provided
    rng = random.Random(cfg.random_seed) if cfg.random_seed is not None else random
    
    # Test each candidate
    for offset in offsets:
        q_candidate = p0 + offset
        
        # Skip invalid candidates
        if q_candidate <= 1 or q_candidate >= N:
            continue
        
        # Optional: fast primality check to skip obvious composites
        # (Skip this for now to keep it simple and fast)
        
        # Test if it's a factor
        if N % q_candidate == 0:
            return q_candidate
    
    # Fall back to classical method
    return pollard_rho(N, rng=rng)
