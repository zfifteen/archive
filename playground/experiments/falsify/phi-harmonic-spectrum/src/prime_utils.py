import numpy as np
from math import sqrt, log


def sieve_of_eratosthenes(limit):
    """Simple sieve for primes up to limit. For testing small ranges."""
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i, is_prime in enumerate(sieve) if is_prime]


def segmented_sieve(low, high):
    """Segmented sieve for primes in range [low, high]. Efficient for large ranges."""
    if low < 2:
        low = 2
    if low > high:
        return []

    # Find primes up to sqrt(high) using simple sieve
    limit = int(sqrt(high)) + 1
    primes_small = sieve_of_eratosthenes(limit)

    # Initialize sieve for the segment
    sieve = [True] * (high - low + 1)

    # Mark multiples of small primes
    for prime in primes_small:
        if prime * prime > high:
            break
        # Find smallest multiple >= low
        start = max(prime * prime, (low + prime - 1) // prime * prime)
        for j in range(start, high + 1, prime):
            if j != prime:  # Don't mark the prime itself
                sieve[j - low] = False

    # Collect primes
    primes = [i for i in range(max(low, 2), high + 1) if sieve[i - low]]
    return primes


def load_prime_gaps(prime_range):
    """
    Load prime gaps for a given range [low, high].
    Returns list of log-gaps Δ_n = ln(p_{n+1} / p_n)
    """
    low, high = prime_range
    primes = segmented_sieve(low, high)
    if len(primes) < 2:
        return []
    gaps = [primes[i + 1] - primes[i] for i in range(len(primes) - 1)]
    log_gaps = [log(gap) for gap in gaps]
    return log_gaps
