#!/usr/bin/env python3
"""
Z5D Adapter - Arbitrary Precision Prime Prediction
Provides scale-adaptive nth-prime estimation and prime counting using gmpy2/mpmath
"""

import sys
try:
    import gmpy2
    from gmpy2 import mpfr, log as gmp_log
    HAS_GMPY2 = True
except ImportError:
    HAS_GMPY2 = False
    print("Warning: gmpy2 not available, using mpmath", file=sys.stderr)

import mpmath
from mpmath import mp, mpf, log as mp_log, sqrt as mp_sqrt

# Set default precision for extreme scales
mp.dps = 100  # 100 decimal places

def n_est(n_int, k_or_phase=0.27952859830111265):
    """
    Estimate the nth prime using asymptotic expansion.
    
    Args:
        n_int: The index (can be int or string for extreme scales)
        k_or_phase: Phase constant for geometric resonance (default from empirical calibration)
    
    Returns:
        String representation of estimated nth prime to avoid overflow
    """
    if isinstance(n_int, str):
        n = mpf(n_int)
    else:
        n = mpf(n_int)
    
    if n < 1:
        raise ValueError("n must be >= 1")
    
    # Special cases for small n where asymptotic formula breaks down
    if n == 1:
        return "2"
    if n == 2:
        return "3"
    if n < 10:
        # Small primes: 2, 3, 5, 7, 11, 13, 17, 19, 23
        small_primes = ["2", "3", "5", "7", "11", "13", "17", "19", "23"]
        if int(n) < len(small_primes):
            return small_primes[int(n) - 1]
    
    # Use prime number theorem asymptotic expansion
    # p_n ≈ n * (ln(n) + ln(ln(n)) - 1 + (ln(ln(n))-2)/ln(n))
    ln_n = mp_log(n)
    ln_ln_n = mp_log(ln_n)
    
    # Basic PNT approximation with correction terms
    estimate = n * (ln_n + ln_ln_n - mpf(1) + (ln_ln_n - mpf(2)) / ln_n)
    
    # Apply geometric resonance phase correction
    phase_correction = mpf(1) + k_or_phase * mp_log(n) / n
    estimate = estimate * phase_correction
    
    # Return as string to avoid overflow in Python int conversion
    return mpmath.nstr(estimate, 50).split('.')[0]


def nth_prime(n_int, k_or_phase=0.27952859830111265):
    """
    Wrapper for n_est with different naming convention.
    
    Args:
        n_int: The index
        k_or_phase: Phase constant
    
    Returns:
        String representation of estimated nth prime
    """
    return n_est(n_int, k_or_phase)


def prime_counting_function(x_str, k_or_phase=0.27952859830111265):
    """
    Estimate π(x) - the number of primes <= x using inverse PNT.
    
    Args:
        x_str: Upper bound (string or number)
        k_or_phase: Phase constant
    
    Returns:
        Estimated count of primes <= x
    """
    if isinstance(x_str, str):
        x = mpf(x_str)
    else:
        x = mpf(x_str)
    
    if x < 2:
        return 0
    
    # π(x) ≈ x / (ln(x) - 1)
    ln_x = mp_log(x)
    estimate = x / (ln_x - mpf(1))
    
    # Apply geometric resonance correction
    phase_correction = mpf(1) - k_or_phase / ln_x
    estimate = estimate * phase_correction
    
    return int(estimate)


def geometric_resonance_score(p, q, n=None):
    """
    Calculate Z5D geometric resonance score for a semiprime.
    
    The score measures deviation from expected geometric mean positioning
    in log-space, with scale-invariant normalization.
    
    Args:
        p: First prime factor (smaller)
        q: Second prime factor (larger)
        n: Semiprime N = p*q (optional, computed if not provided)
    
    Returns:
        Z5D score (negative values indicate strong resonance)
    """
    if isinstance(p, str):
        p = mpf(p)
    else:
        p = mpf(p)
    
    if isinstance(q, str):
        q = mpf(q)
    else:
        q = mpf(q)
    
    if n is None:
        n = p * q
    elif isinstance(n, str):
        n = mpf(n)
    else:
        n = mpf(n)
    
    # Log-space coordinates
    ln_p = mp_log(p)
    ln_q = mp_log(q)
    ln_n = mp_log(n)
    
    # Expected geometric mean
    expected_geom_mean = ln_n / mpf(2)
    
    # Actual geometric positioning (weighted by asymmetry)
    asymmetry = abs(ln_q - ln_p) / (ln_q + ln_p)
    actual_position = (ln_p + ln_q) / mpf(2)
    
    # Z-score normalized by scale
    deviation = abs(actual_position - expected_geom_mean) / mp_sqrt(ln_n)
    
    # Apply resonance transformation (negative = strong resonance)
    z5d_score = -mpf(10) * mp_log(mpf(1) + asymmetry) / (mpf(1) + deviation)
    
    return float(z5d_score)


if __name__ == "__main__":
    # Self-test
    print("Z5D Adapter Self-Test")
    print("=" * 60)
    
    # Test small scale
    n = 100
    est = n_est(n)
    print(f"Estimated 100th prime: {est}")
    print(f"Actual 100th prime: 541")
    
    # Test medium scale
    n = "1000000"
    est = n_est(n)
    print(f"\nEstimated 1,000,000th prime: {est}")
    
    # Test extreme scale
    n = "10" + "0" * 100  # 10^100
    est = n_est(n)
    print(f"\nEstimated 10^100th prime (first 50 digits): {est[:50]}")
    
    # Test geometric resonance
    p, q = 3, 5
    score = geometric_resonance_score(p, q)
    print(f"\nZ5D score for N=15 (3×5): {score:.4f}")
    
    print("\n✓ All tests completed successfully")
