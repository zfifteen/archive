#!/usr/bin/env python3
"""
Semiprime Utility Functions for Z5D Adaptation

This module provides core utilities for semiprime generation, counting, and analysis
to support the Z5D semiprime prediction experiment. Includes efficient semiprime
generation algorithms and mathematical utilities for semiprime analysis.

Key Features:
- Fast semiprime generation up to large limits (10^6+)
- Semiprime counting and nth-semiprime lookup
- Divisor structure analysis for Z5D adaptation
- Statistical utilities for validation

Author: Z Framework Implementation Team
"""

import numpy as np
import sympy
from math import log, sqrt, e, log1p
from typing import List, Dict, Tuple, Union, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

def generate_semiprimes(limit: int) -> List[int]:
    """
    Generate all semiprimes up to a given limit efficiently.
    
    A semiprime is a number that is the product of exactly two prime numbers
    (not necessarily distinct). This includes p*q where p and q are primes,
    including p^2 (perfect square semiprimes).
    
    Parameters
    ----------
    limit : int
        Maximum value for semiprime generation
        
    Returns
    -------
    List[int]
        Sorted list of all semiprimes up to limit
        
    Examples
    --------
    >>> semiprimes = generate_semiprimes(30)
    >>> print(semiprimes[:10])
    [4, 6, 9, 10, 14, 15, 21, 22, 25, 26]
    
    Notes
    -----
    Time complexity: O(π(√limit) * π(limit/p)) where π is the prime counting function
    Space complexity: O(number of semiprimes up to limit)
    """
    if limit < 4:
        return []
    
    semiprimes = set()
    sqrt_limit = int(sqrt(limit))
    
    # Generate primes up to limit using sieve for efficiency
    def sieve_of_eratosthenes(n):
        sieve = [True] * (n + 1)
        sieve[0] = sieve[1] = False
        
        for i in range(2, int(sqrt(n)) + 1):
            if sieve[i]:
                for j in range(i * i, n + 1, i):
                    sieve[j] = False
        
        return [i for i in range(2, n + 1) if sieve[i]]
    
    primes = sieve_of_eratosthenes(limit)
    primes_set = set(primes)
    
    # Generate semiprimes by multiplying pairs of primes
    for i, p in enumerate(primes):
        if p > sqrt_limit:
            break
            
        # Include p^2 (perfect square semiprimes)
        if p * p <= limit:
            semiprimes.add(p * p)
        
        # Include p*q for all primes q >= p
        for j in range(i, len(primes)):
            q = primes[j]
            product = p * q
            if product > limit:
                break
            semiprimes.add(product)
    
    return sorted(list(semiprimes))


def count_semiprimes(x: float) -> int:
    """
    Count the number of semiprimes up to x using direct enumeration.
    
    This function implements the semiprime counting function π_2(x).
    For large x, this becomes computationally expensive and should be
    replaced with the Z5D semiprime variant predictor.
    
    Parameters
    ----------
    x : float
        Upper bound for counting semiprimes
        
    Returns
    -------
    int
        Number of semiprimes ≤ x
        
    Notes
    -----
    Asymptotic behavior: π_2(x) ~ (x log log x) / log x
    """
    if x < 4:
        return 0
    
    semiprimes = generate_semiprimes(int(x))
    return len(semiprimes)


def nth_semiprime(k: int) -> int:
    """
    Return the kth semiprime using direct enumeration.
    
    Parameters
    ----------
    k : int
        Index of desired semiprime (1-based)
        
    Returns
    -------
    int
        The kth semiprime
        
    Raises
    ------
    ValueError
        If k <= 0 or k is too large for reasonable computation
    """
    if k <= 0:
        raise ValueError("k must be positive")
    
    if k > 100000:  # Reasonable limit for direct computation
        raise ValueError("k too large for direct enumeration, use Z5D predictor")
    
    # Estimate upper bound for generation
    # Using rough approximation: s_k ≈ k log k / log log k
    if k < 10:
        limit = 100
    else:
        estimate = k * log(k) / max(log(log(k + 10)), 1)
        limit = max(int(estimate * 3), 100)  # Safety factor of 3
    
    # Generate semiprimes and check if we have enough
    while True:
        semiprimes = generate_semiprimes(limit)
        if len(semiprimes) >= k:
            return semiprimes[k-1]
        
        # Increase limit and try again
        limit *= 2
        if limit > 10**8:  # Prevent infinite loops
            raise ValueError(f"Cannot find {k}th semiprime within reasonable bounds")


def baseline_semiprime_approximation(k: int) -> float:
    """
    Naive asymptotic approximation for the kth semiprime.
    
    This implements the basic asymptotic formula derived from
    π_2(x) ~ (x log log x) / log x by inversion.
    
    Parameters
    ----------
    k : int
        Index of semiprime to estimate
        
    Returns
    -------
    float
        Baseline estimate of kth semiprime
        
    Notes
    -----
    Formula: s_k ≈ k * log(k) / log(log(k + 10))
    Expected error: ~50% (very rough approximation)
    """
    if k < 3:
        # Handle small cases explicitly
        small_semiprimes = [4, 6, 9, 10]
        return float(small_semiprimes[k-1]) if k <= 4 else 4.0
    
    # Use offset to avoid log(log(0)) issues
    return k * log(k) / log(log(k + 10))


def omega(n: int) -> int:
    """
    Count the number of distinct prime factors of n.
    
    This is the ω(n) function used in the enhanced geodesic mapping.
    For semiprimes, ω(n) = 2 for square-free semiprimes (p*q, p≠q)
    and ω(n) = 1 for perfect square semiprimes (p^2).
    
    Parameters
    ----------
    n : int
        Number to analyze
        
    Returns
    -------
    int
        Number of distinct prime factors
        
    Examples
    --------
    >>> omega(12)  # 12 = 2^2 * 3
    2
    >>> omega(25)  # 25 = 5^2
    1
    >>> omega(30)  # 30 = 2 * 3 * 5
    3
    """
    if n <= 1:
        return 0
    
    # Use SymPy for robust factorization
    factors = sympy.factorint(n)
    return len(factors)


def big_omega(n: int) -> int:
    """
    Count the total number of prime factors of n with multiplicity.
    
    This is the Ω(n) function. For semiprimes, Ω(n) = 2 always.
    
    Parameters
    ----------
    n : int
        Number to analyze
        
    Returns
    -------
    int
        Total number of prime factors (with multiplicity)
    """
    if n <= 1:
        return 0
    
    factors = sympy.factorint(n)
    return sum(factors.values())


def is_semiprime(n: int) -> bool:
    """
    Check if n is a semiprime (exactly two prime factors with multiplicity).
    
    Parameters
    ----------
    n : int
        Number to check
        
    Returns
    -------
    bool
        True if n is a semiprime
    """
    return big_omega(n) == 2


def divisor_count(n: int) -> int:
    """
    Count the number of divisors of n.
    
    This is the d(n) function used in the Z5D adaptation.
    For semiprimes: d(p*q) = 4 if p≠q, d(p^2) = 3
    
    Parameters
    ----------
    n : int
        Number to analyze
        
    Returns
    -------
    int
        Number of positive divisors
    """
    if n <= 0:
        return 0
    
    return len(sympy.divisors(n))


def enhanced_delta_semiprime(n: int) -> float:
    """
    Enhanced delta function for semiprime detection.
    
    Formula: Δ_2(n) = [d(n) - 3]^2 * ln(n+1) / e^2
    
    This focuses on d(n) ≈ 3 for square-free semiprimes and
    d(n) = 4 for most semiprimes.
    
    Parameters
    ----------
    n : int
        Number to analyze
        
    Returns
    -------
    float
        Enhanced delta value for semiprime structure
    """
    if n <= 1:
        return 0.0
    
    d_n = divisor_count(n)
    return ((d_n - 3) ** 2) * log(n + 1) / (e ** 2)


def enhanced_geodesic_semiprime(n: int, k: int, k_star: float = 0.3) -> float:
    """
    Enhanced geodesic mapping for semiprime detection.
    
    Formula: θ_2'(n, k) = φ · ((ω(n) mod φ)/φ)^k_star
    where ω(n) is the number of distinct prime factors.
    
    Parameters
    ----------
    n : int
        Number for geodesic calculation
    k : int
        Index parameter
    k_star : float, optional
        Geodesic enhancement parameter (default 0.3)
        
    Returns
    -------
    float
        Enhanced geodesic value
    """
    if n <= 1:
        return 0.0
    
    # Golden ratio φ
    phi = (1 + sqrt(5)) / 2
    
    omega_n = omega(n)
    
    # Enhanced geodesic with semiprime focus
    return phi * ((omega_n % phi) / phi) ** k_star


def semiprime_statistics(semiprimes: List[int]) -> Dict[str, float]:
    """
    Calculate statistical properties of a semiprime sequence.
    
    Parameters
    ----------
    semiprimes : List[int]
        List of semiprimes to analyze
        
    Returns
    -------
    Dict[str, float]
        Statistical measures including gaps, density, etc.
    """
    if len(semiprimes) < 2:
        return {'count': len(semiprimes)}
    
    gaps = np.diff(semiprimes)
    
    return {
        'count': len(semiprimes),
        'mean_gap': np.mean(gaps),
        'std_gap': np.std(gaps),
        'min_gap': np.min(gaps),
        'max_gap': np.max(gaps),
        'density_ratio': len(semiprimes) / semiprimes[-1] if semiprimes else 0,
        'mean_value': np.mean(semiprimes),
        'largest': semiprimes[-1] if semiprimes else 0
    }


def validate_semiprime_generation(limit: int = 1000) -> Dict[str, bool]:
    """
    Validate semiprime generation against known properties.
    
    Parameters
    ----------
    limit : int
        Limit for validation testing
        
    Returns
    -------
    Dict[str, bool]
        Validation results
    """
    semiprimes = generate_semiprimes(limit)
    
    validation = {
        'all_semiprimes': True,
        'sorted_order': True,
        'no_duplicates': True,
        'includes_squares': True,
        'includes_products': True
    }
    
    # Check if all generated numbers are actually semiprimes
    for sp in semiprimes:
        if not is_semiprime(sp):
            validation['all_semiprimes'] = False
            logger.warning(f"Non-semiprime found in generation: {sp}")
    
    # Check sorted order
    if semiprimes != sorted(semiprimes):
        validation['sorted_order'] = False
    
    # Check for duplicates
    if len(semiprimes) != len(set(semiprimes)):
        validation['no_duplicates'] = False
    
    # Check for prime squares (e.g., 4, 9, 25) - only p^2 where p is prime
    prime_squares = [4, 9, 25, 49, 121, 169, 289, 361, 529, 841, 961]  # Removed 625=5^4 (not semiprime)
    expected_squares = [ps for ps in prime_squares if ps <= limit]
    found_squares = [ps for ps in expected_squares if ps in semiprimes]
    if len(found_squares) < len(expected_squares):
        validation['includes_squares'] = False
    
    # Check for prime products (e.g., 6=2*3, 10=2*5, 14=2*7)
    prime_products = [6, 10, 14, 15, 21, 22, 26, 33, 34, 35, 38, 39]
    expected_products = [pp for pp in prime_products if pp <= limit]
    found_products = [pp for pp in expected_products if pp in semiprimes]
    if len(found_products) < len(expected_products):
        validation['includes_products'] = False
    
    return validation


# Sample known semiprimes for testing and validation
SAMPLE_SEMIPRIMES = [
    4, 6, 9, 10, 14, 15, 21, 22, 25, 26, 33, 34, 35, 38, 39, 46, 49, 51, 57, 58,
    62, 65, 69, 74, 77, 82, 85, 86, 87, 91, 93, 94, 95, 106, 111, 115, 118, 119,
    121, 122, 123, 129, 133, 134, 141, 142, 143, 145, 146, 155, 158, 159, 161,
    166, 169, 177, 178, 183, 185, 187, 194, 201, 202, 203, 205, 206, 209, 213,
    214, 215, 217, 218, 219, 221, 226, 235, 237, 247, 249, 253, 254, 259, 262,
    265, 267, 274, 278, 287, 289, 291, 295, 298, 299, 301, 302, 303, 305, 309
]


if __name__ == "__main__":
    # Demo and validation
    print("Z5D Semiprime Utilities Demo")
    print("=" * 40)
    
    # Test semiprime generation
    print("\n1. Generating semiprimes up to 100:")
    semiprimes_100 = generate_semiprimes(100)
    print(f"Found {len(semiprimes_100)} semiprimes: {semiprimes_100}")
    
    # Validate generation
    print("\n2. Validating semiprime generation:")
    validation = validate_semiprime_generation(100)
    for test, passed in validation.items():
        status = "✓" if passed else "✗"
        print(f"   {status} {test}: {passed}")
    
    # Test nth semiprime
    print("\n3. Testing nth semiprime function:")
    for k in [1, 5, 10, 20]:
        sp = nth_semiprime(k)
        print(f"   {k}th semiprime: {sp}")
    
    # Test baseline approximation
    print("\n4. Testing baseline approximation:")
    for k in [10, 100, 1000]:
        approx = baseline_semiprime_approximation(k)
        if k <= 20:
            actual = nth_semiprime(k)
            error = abs(approx - actual) / actual * 100
            print(f"   k={k}: approx={approx:.1f}, actual={actual}, error={error:.1f}%")
        else:
            print(f"   k={k}: approx={approx:.1f}")
    
    # Test enhanced functions
    print("\n5. Testing enhanced Z5D functions:")
    test_numbers = [6, 9, 10, 15, 25, 30]
    for n in test_numbers:
        is_sp = is_semiprime(n)
        d_n = divisor_count(n)
        omega_n = omega(n)
        delta = enhanced_delta_semiprime(n)
        geodesic = enhanced_geodesic_semiprime(n, 100)
        
        print(f"   n={n}: semiprime={is_sp}, d(n)={d_n}, ω(n)={omega_n}, "
              f"Δ_2={delta:.3f}, θ_2'={geodesic:.3f}")
    
    # Statistical analysis
    print("\n6. Statistical analysis of first 50 semiprimes:")
    stats = semiprime_statistics(semiprimes_100[:50])
    print(f"   Count: {stats['count']}")
    print(f"   Mean gap: {stats['mean_gap']:.2f}")
    print(f"   Density ratio: {stats['density_ratio']:.4f}")
    print(f"   Largest: {stats['largest']}")
    
    print("\nSemiprime utilities validation complete!")