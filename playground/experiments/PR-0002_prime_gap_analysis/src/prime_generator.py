"""
Prime number generator using segmented Sieve of Eratosthenes.

This module provides efficient prime generation for large limits using a
segmented approach that reduces memory usage compared to a standard sieve.
Results are cached to disk for reuse.

Validation:
- π(10^6) = 78,498
- π(10^7) = 664,579
- π(10^8) = 5,761,455
"""

import numpy as np
from pathlib import Path
from typing import Optional
import math


# Known prime counts for validation
KNOWN_PRIME_COUNTS = {
    10**6: 78498,
    10**7: 664579,
    10**8: 5761455,
}


def _simple_sieve(limit: int) -> np.ndarray:
    """IMPLEMENTED: Generate primes up to limit using simple sieve.
    
    This is used for finding small primes up to sqrt(overall_limit) in the
    segmented sieve. Uses a standard Sieve of Eratosthenes implementation.
    
    Args:
        limit: Upper bound for prime generation (inclusive)
        
    Returns:
        np.ndarray: Array of all primes <= limit as uint64
        
    Raises:
        ValueError: If limit < 2
    """
    if limit < 2:
        raise ValueError("limit must be >= 2")
    
    # Create boolean array, True means "potentially prime"
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    
    # Sieve of Eratosthenes
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            # Mark all multiples of i as composite
            is_prime[i*i::i] = False
    
    # Extract prime numbers
    primes = np.nonzero(is_prime)[0].astype(np.uint64)
    return primes


def _get_cache_path(limit: int) -> Path:
    """Get the cache file path for primes up to limit.
    
    Args:
        limit: Upper bound for prime generation
        
    Returns:
        Path object pointing to cache file
    """
    # Get data directory relative to this file
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / f"primes_{limit}.npy"


def _load_cached_primes(limit: int) -> Optional[np.ndarray]:
    """Load cached primes from disk if available.
    
    Args:
        limit: Upper bound for prime generation
        
    Returns:
        Array of primes if cache exists and is valid, None otherwise
    """
    cache_path = _get_cache_path(limit)
    if not cache_path.exists():
        return None
    
    try:
        primes = np.load(cache_path)
        # Validate loaded data
        if primes.dtype != np.uint64:
            return None
        if len(primes) > 0 and np.max(primes) > limit:
            return None
        return primes
    except Exception:
        return None


def _save_cached_primes(primes: np.ndarray, limit: int) -> None:
    """Save generated primes to disk cache.
    
    Args:
        primes: Array of prime numbers to cache
        limit: Upper bound used to generate these primes
    """
    cache_path = _get_cache_path(limit)
    try:
        np.save(cache_path, primes)
    except Exception as e:
        # Don't fail if caching doesn't work, just warn
        print(f"Warning: Failed to cache primes: {e}")


def _validate_prime_count(primes: np.ndarray, limit: int) -> None:
    """Validate generated prime count against known values.
    
    Args:
        primes: Array of generated primes
        limit: Upper bound used for generation
        
    Raises:
        AssertionError: If count doesn't match expected value
    """
    if limit in KNOWN_PRIME_COUNTS:
        expected = KNOWN_PRIME_COUNTS[limit]
        actual = len(primes)
        assert actual == expected, \
            f"Prime count mismatch at {limit:,}: expected {expected:,}, got {actual:,}"


def segmented_sieve(limit: int, segment_size: int = 10**6) -> np.ndarray:
    """Generate primes using segmented Sieve of Eratosthenes.
    
    Args:
        limit: Upper bound for prime generation
        segment_size: Size of each segment (default 10^6)
        
    Returns:
        Array of all primes <= limit as uint64
        
    Raises:
        ValueError: If limit < 2 or segment_size <= 0
    """
    if limit < 2:
        raise ValueError("limit must be >= 2")
    if segment_size <= 0:
        raise ValueError("segment_size must be > 0")
    
    # Step 1: Get small primes up to sqrt(limit)
    sqrt_limit = int(math.sqrt(limit))
    small_primes = _simple_sieve(sqrt_limit)
    
    # If limit is small, just return the simple sieve result
    if limit <= sqrt_limit:
        return small_primes[small_primes <= limit]
    
    # Step 2: Initialize result with small primes
    result = list(small_primes)
    
    # Step 3: Process segments from sqrt_limit+1 to limit
    for low in range(sqrt_limit + 1, limit + 1, segment_size):
        high = min(low + segment_size - 1, limit)
        
        # Create boolean array for this segment
        segment = np.ones(high - low + 1, dtype=bool)
        
        # Mark composites using small primes
        for p in small_primes:
            # Find first multiple of p in segment
            # It's either p^2 (if p^2 is in segment) or the first multiple >= low
            if p * p > high:
                break
            
            start = max(p * p, ((low + p - 1) // p) * p)
            
            # Mark all multiples in this segment as composite
            for multiple in range(start, high + 1, p):
                segment[multiple - low] = False
        
        # Extract primes from this segment
        segment_primes = [low + i for i in range(len(segment)) if segment[i]]
        result.extend(segment_primes)
    
    return np.array(result, dtype=np.uint64)


def generate_primes(limit: int) -> np.ndarray:
    """Generate primes up to limit with caching.
    
    This is the main entry point for prime generation. It attempts to load
    cached primes from disk, and generates them if not cached.
    
    Args:
        limit: Upper bound for prime generation (inclusive)
        
    Returns:
        Array of all primes <= limit as uint64
        
    Raises:
        ValueError: If limit < 2
        AssertionError: If generated count doesn't match known values
    """
    if limit < 2:
        raise ValueError("limit must be >= 2")
    
    # Try to load from cache
    cached = _load_cached_primes(limit)
    if cached is not None:
        print(f"Loaded {len(cached):,} primes from cache")
        _validate_prime_count(cached, limit)
        return cached
    
    # Generate primes
    print(f"Generating primes up to {limit:,}...")
    primes = segmented_sieve(limit)
    
    # Validate and cache
    _validate_prime_count(primes, limit)
    _save_cached_primes(primes, limit)
    
    print(f"Generated {len(primes):,} primes")
    return primes


# Example usage and validation
if __name__ == "__main__":
    # Test with known values
    for test_limit in [10**6, 10**7]:
        print(f"\nGenerating primes up to {test_limit:,}...")
        primes = generate_primes(test_limit)
        expected = KNOWN_PRIME_COUNTS.get(test_limit)
        print(f"Found {len(primes):,} primes")
        if expected:
            print(f"Expected {expected:,} primes")
            assert len(primes) == expected, f"Validation failed!"
        print(f"First 10: {primes[:10]}")
        print(f"Last 10: {primes[-10:]}")
