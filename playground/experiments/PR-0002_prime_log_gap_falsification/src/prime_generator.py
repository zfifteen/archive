"""
Prime Generator Module

This module generates prime numbers, which are numbers greater than 1 that have no positive divisors other than 1 and themselves (e.g., 2, 3, 5, 7, 11).
In this experiment, primes are the foundation for studying "prime gaps" – the differences between consecutive primes.
We use efficient algorithms to handle large ranges (up to 10^8 primes) without using too much memory.

Imagine primes as evenly spaced "dots" on a number line, but the gaps between them grow larger on average.
This module creates those dots so we can measure the spaces.
"""

import numpy as np
import math
from typing import List, Generator


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """
    Basic Sieve of Eratosthenes: An ancient method to find all primes up to a limit.

    How it works (like a game of elimination):
    1. Make a list of numbers from 0 to limit, marking them as "potentially prime" (True).
    2. Mark 0 and 1 as not prime (they're special cases).
    3. For each number starting from 2, if it's still marked prime, cross out all its multiples (like 2 eliminates 4, 6, 8, etc.).
    4. What's left unmarked are primes.

    This is efficient for smaller limits but uses a lot of memory for big numbers, so we only use it for small primes here.
    In our experiment, this helps generate "small primes" used to sieve larger ranges.
    """
    if limit < 2:
        return []  # No primes below 2
    sieve = [True] * (limit + 1)  # Boolean array: True means "might be prime"
    sieve[0] = sieve[1] = False  # 0 and 1 are not primes
    for i in range(
        2, int(math.sqrt(limit)) + 1
    ):  # Only check up to square root (optimization)
        if sieve[i]:  # If i is still prime
            for j in range(i * i, limit + 1, i):  # Mark multiples of i as not prime
                sieve[j] = False
    return [i for i in range(2, limit + 1) if sieve[i]]  # Collect the primes


def segmented_sieve(
    limit: int, segment_size: int = 10**6
) -> Generator[int, None, None]:
    """
    Segmented Sieve of Eratosthenes: A smarter version for large limits.

    Why segmented? The basic sieve needs a huge array for big limits (e.g., 10^8 numbers take 100MB+).
    Instead, we break the range into smaller "segments" (chunks of 1 million numbers) and sieve each one separately.
    This saves memory but takes a bit more time – a good trade-off for our experiment.

    Steps:
    1. First, use the basic sieve to get small primes up to sqrt(limit). These are our "tools" for sieving larger numbers.
    2. Divide the big range into segments.
    3. For each segment, mark non-primes using the small primes as filters.
    4. Collect the remaining primes in that segment.

    This is like cleaning a room in sections instead of the whole house at once.
    In the prime gap experiment, this lets us generate millions of primes efficiently for gap analysis.
    """
    if limit < 2:
        return  # No work to do

    # Step 1: Get small primes for sieving (these are quick to compute)
    sqrt_limit = int(math.sqrt(limit)) + 1  # Square root is a key optimization point
    small_primes = sieve_of_eratosthenes(sqrt_limit)
    yield from small_primes  # Output the small primes first

    # Step 2: Now handle the large range in segments
    low_start = (
        max(sqrt_limit, small_primes[-1] + 1) if small_primes else 2
    )  # Start after small primes
    for low in range(
        low_start, limit + 1, segment_size
    ):  # Each segment starts at 'low'
        high = min(low + segment_size, limit + 1)  # End of segment
        sieve = [True] * (high - low)  # Fresh sieve for this segment
        for p in small_primes:  # Use each small prime as a filter
            if p * p > high:  # No need to check primes larger than sqrt(high)
                break
            # Calculate where in this segment p's multiples start
            start = max(
                p * p, ((low + p - 1) // p) * p
            )  # Ensures we start at the right multiple
            for j in range(start, high, p):  # Mark multiples of p as not prime
                sieve[j - low] = False
        # Now collect the primes from this segment
        for i in range(high - low):
            if sieve[i]:  # If still True, it's prime
                yield low + i  # Output the actual number


def generate_primes_up_to(limit: int) -> np.ndarray:
    """
    Collect all primes up to the limit into a NumPy array for easy use.

    NumPy arrays are like super-efficient lists for math operations.
    We use uint64 (unsigned 64-bit integers) because primes can be up to 10^8, which fits.
    This array becomes the input for calculating prime gaps in our experiment.
    """
    primes = list(segmented_sieve(limit))  # Convert generator to list
    return np.array(primes, dtype=np.uint64)  # Pack into NumPy array


def count_primes_up_to(limit: int) -> int:
    """
    Just count the primes without storing them – useful for validation.

    Sometimes we only need the number of primes (like checking against known counts)
    without wasting memory on the list. This uses the generator directly.
    In the experiment, we verify counts like π(10^6) = 78,498 to ensure our sieve is correct.
    """
    return sum(1 for _ in segmented_sieve(limit))  # Count by iterating the generator


# Known values of π(x) (prime counting function) for validation
KNOWN_PI_VALUES = {
    10**6: 78498,
    10**7: 664579,
    10**8: 5761455,
}


def generate_primes_to_limit(limit: int, validate: bool = True) -> np.ndarray:
    """
    Generate primes up to limit with optional validation.
    
    This is a wrapper around generate_primes_up_to that adds validation
    against known prime counts for extra confidence.
    
    Args:
        limit: Upper bound for prime generation
        validate: Whether to validate count against known values (default: True)
        
    Returns:
        NumPy array of primes up to limit
        
    Raises:
        ValueError: If validation fails
    """
    primes = generate_primes_up_to(limit)
    
    if validate and limit in KNOWN_PI_VALUES:
        expected = KNOWN_PI_VALUES[limit]
        actual = len(primes)
        if actual != expected:
            raise ValueError(f"Prime count mismatch at {limit}: expected {expected}, got {actual}")
    
    return primes


def compute_log_gaps(primes: np.ndarray) -> dict:
    """
    Compute log-gaps from primes.
    
    This is a compatibility wrapper that returns both the log-gaps array
    and additional metadata expected by run_experiment.py.
    
    Args:
        primes: Array of prime numbers
        
    Returns:
        Dictionary with 'log_gaps' and 'regular_gaps' keys
    """
    log_primes = np.log(primes.astype(np.float64))
    log_gaps = np.diff(log_primes)
    regular_gaps = np.diff(primes)
    
    return {
        'log_gaps': log_gaps,
        'regular_gaps': regular_gaps
    }


if __name__ == "__main__":
    # Quick test to make sure everything works
    print("Testing prime generation...")
    primes = generate_primes_up_to(100)  # Generate primes up to 100
    print(f"Primes up to 100: {primes}")  # Show the list
    print(f"Count: {len(primes)}")  # Should be 25
