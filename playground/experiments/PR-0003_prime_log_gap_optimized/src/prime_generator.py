"""
Prime Generator Module with Disk Caching

Generates primes up to 10^9 using segmented sieve and caches results to disk.
Enables rerunning analysis without regenerating primes.
"""

import numpy as np
import math
import os
from pathlib import Path
from typing import Optional, Tuple

# Backend constants for prime generation
BACKEND_SEGMENTED = "segmented"
BACKEND_Z5D = "z5d"
BACKEND_AUTO = "auto"


# Known prime counts for validation
KNOWN_PI_VALUES = {
    10**6: 78498,
    10**7: 664579,
    10**8: 5761455,
    10**9: 50847534,
}


def _generate_primes_z5d(limit: int) -> np.ndarray:
    """
    Generate primes using Z5D predictor by computing nth primes sequentially.

    Args:
        limit: Upper bound for primes (inclusive)

    Returns:
        Sorted numpy array of primes <= limit
    """
    import sys

    sys.path.insert(
        0, str(Path(__file__).parent.parent / "z5d-prime-predictor" / "src" / "python")
    )
    from z5d_predictor.predictor import predict_nth_prime

    # Use binary search to find approximate π(limit)
    # Then generate primes until we exceed limit
    primes = []
    n = 1

    # Estimate π(limit) using n * ln(n) approximation
    import math

    if limit > 10:
        estimated_pi = int(limit / math.log(limit) * 1.5)  # overestimate
    else:
        estimated_pi = limit

    # Generate primes up to limit
    while True:
        result = predict_nth_prime(n)
        if result.prime > limit:
            break
        primes.append(result.prime)
        n += 1

        # Progress indicator for large runs
        if n % 10000 == 0:
            print(f"Generated {n:,} primes (current: {result.prime:,})")

    # Decide dtype based on magnitude
    if limit <= (1 << 63) - 1:
        return np.array(primes, dtype=np.uint64)
    else:
        return np.array(primes, dtype=object)


def sieve_of_eratosthenes(limit: int) -> np.ndarray:
    """
    IMPLEMENTED: Basic Sieve of Eratosthenes for small primes.

    Generates all primes up to limit using the classic sieve algorithm.
    Used to generate small primes needed for segmented sieving.

    Args:
        limit: Upper bound for prime generation (inclusive)

    Returns:
        NumPy array of primes up to limit

    Algorithm:
        1. Create boolean array of size limit+1, all True
        2. Mark 0, 1 as not prime
        3. For each i from 2 to sqrt(limit):
            - If i is prime, mark all multiples as composite
        4. Return indices where array is True
    """
    if limit < 2:
        return np.array([], dtype=np.uint64)

    sieve = np.ones(limit + 1, dtype=bool)
    sieve[0] = sieve[1] = False

    for i in range(2, int(math.sqrt(limit)) + 1):
        if sieve[i]:
            sieve[i * i : limit + 1 : i] = False

    return np.where(sieve)[0].astype(np.uint64)


def segmented_sieve(limit: int, segment_size: int = 10**6) -> np.ndarray:
    """
    Generate primes up to limit using memory-efficient segmented sieve.

    Args:
        limit: Maximum value for prime generation
        segment_size: Size of each segment (default 10^6)

    Returns:
        NumPy array of all primes up to limit
    """
    if limit < 2:
        return np.array([], dtype=np.uint64)

    # Step 1: Get small primes up to sqrt(limit)
    sqrt_limit = int(math.sqrt(limit)) + 1
    small_primes = sieve_of_eratosthenes(sqrt_limit)

    # Step 2: Initialize result with small primes
    result = list(small_primes)

    # Step 3: Process segments from sqrt(limit) to limit
    low_start = int(
        sqrt_limit if sqrt_limit > small_primes[-1] else small_primes[-1] + 1
    )

    for low in range(low_start, limit + 1, segment_size):
        high = min(low + segment_size, limit + 1)
        segment = np.ones(high - low, dtype=bool)

        # Mark composites using small primes
        for p in small_primes:
            if p * p > high:
                break

            # Find first multiple of p in segment
            start = int(max(p * p, ((low + p - 1) // p) * p))

            # Mark all multiples as composite
            for j in range(int(start), high, int(p)):
                segment[j - low] = False

        # Extract primes from segment
        segment_primes = [low + i for i in range(len(segment)) if segment[i]]
        result.extend(segment_primes)

    return np.array(result, dtype=np.uint64)


def _generate_primes_backend(limit: int, backend: str) -> np.ndarray:
    """
    Internal router to select prime generation backend.

    Args:
        limit: Upper bound for primes
        backend: One of BACKEND_SEGMENTED, BACKEND_Z5D, BACKEND_AUTO

    Returns:
        Numpy array of primes
    """
    if backend == BACKEND_AUTO:
        # Use segmented up to 10^9, Z5D beyond
        if limit <= 10**9:
            backend = BACKEND_SEGMENTED
        else:
            backend = BACKEND_Z5D

    if backend == BACKEND_SEGMENTED:
        return segmented_sieve(limit)
    elif backend == BACKEND_Z5D:
        return _generate_primes_z5d(limit)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def generate_primes_to_limit(
    limit: int,
    cache_dir: Optional[str] = None,
    validate: bool = True,
    backend: str = BACKEND_AUTO,
) -> np.ndarray:
    """
    Generate or load primes up to limit with optional disk caching.

    Args:
        limit: Maximum value for prime generation
        cache_dir: Directory for caching primes (default: ../data)
        validate: Whether to validate count against KNOWN_PI_VALUES
        backend: Prime generation backend ('segmented', 'z5d', 'auto')

    Returns:
        NumPy array of primes up to limit
    """
    # Determine cache directory
    if cache_dir is None:
        script_dir = Path(__file__).parent.parent
        cache_dir = script_dir / "data"
    else:
        cache_dir = Path(cache_dir)

    cache_file = cache_dir / f"primes_{limit}.npy"

    # Try to load from cache
    if cache_file.exists():
        primes = np.load(cache_file)
        print(f"Loaded {len(primes):,} primes from cache")
    else:
        # Generate primes
        print(f"Generating primes up to {limit:,} using backend='{backend}'...")
        primes = _generate_primes_backend(limit, backend)

        # Cache to disk
        cache_dir.mkdir(parents=True, exist_ok=True)
        np.save(cache_file, primes, allow_pickle=True)  # allow_pickle for object dtype
        print(f"Generated and cached {len(primes):,} primes")

    # Validate if requested: only when using segmented backend and limit is in KNOWN_PI_VALUES
    if validate and backend == BACKEND_SEGMENTED and limit in KNOWN_PI_VALUES:
        expected = KNOWN_PI_VALUES[limit]
        actual = len(primes)
        if actual != expected:
            raise ValueError(
                f"Prime count mismatch at {limit}: expected {expected}, got {actual}"
            )
        print(f"Validation passed: π({limit:,}) = {actual:,}")

    return primes


def compute_gaps(
    primes: np.ndarray, cache_dir: Optional[str] = None, limit: Optional[int] = None
) -> dict:
    """
    Compute regular and log-gaps with optional disk caching.

    Args:
        primes: Array of prime numbers
        cache_dir: Directory for caching gaps
        limit: Max prime value (used for cache filename)

    Returns:
        Dictionary with 'primes', 'regular_gaps', 'log_gaps', 'log_primes'
    """
    # Determine cache directory and file
    if cache_dir is None and limit is not None:
        script_dir = Path(__file__).parent.parent
        cache_dir = script_dir / "data"

    if cache_dir is not None and limit is not None:
        cache_dir = Path(cache_dir)
        cache_file = cache_dir / f"gaps_{limit}.npz"

        # Try to load from cache
        if cache_file.exists():
            data = np.load(cache_file)
            result = {
                "primes": primes,
                "regular_gaps": data["regular_gaps"],
                "log_gaps": data["log_gaps"],
                "log_primes": data["log_primes"],
            }
            print(f"Loaded gaps from cache")
            return result

    # Compute gaps
    print(f"Computing gaps...")
    # Handle object dtype for very large primes
    if primes.dtype == object:
        # Convert to float64 for log (will overflow beyond ~10^308)
        primes_float = np.array([float(p) for p in primes], dtype=np.float64)
    else:
        primes_float = primes.astype(np.float64)

    log_primes = np.log(primes_float)
    log_gaps = np.diff(log_primes)
    regular_gaps = np.diff(primes.astype(np.int64))  # may overflow for huge primes

    # Cache if requested
    if cache_dir is not None and limit is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        np.savez(
            cache_file,
            regular_gaps=regular_gaps,
            log_gaps=log_gaps,
            log_primes=log_primes,
        )
        print(f"Computed and cached gaps")

    return {
        "primes": primes,
        "regular_gaps": regular_gaps,
        "log_gaps": log_gaps,
        "log_primes": log_primes,
    }
