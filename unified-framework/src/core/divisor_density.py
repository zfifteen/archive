#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Divisor Density Module for κ-Biased Stadlmann Integration
===========================================================

This module implements the κ(n) curvature function based on divisor density,
used to bias Stadlmann distribution predictions toward low-curvature primes.

Key function:
- kappa(n): Computes κ(n) = d(n) · ln(n+1) / e²
  where d(n) is the number of divisors of n

The κ-biased approach prioritizes predictions with lower curvature,
hypothesized to yield 2-8% accuracy lift (ppm error reduction) on large n (10^18).

Reference: Issue #TODO - κ-Biased Stadlmann Integration
"""

import mpmath as mp
from functools import lru_cache

# Module constants (avoid global precision mutation)
E_SQUARED = mp.exp(mp.mpf('2'))  # e² ≈ 7.389, computed once
KAPPA_EXACT_MAX_N = 10_000_000  # Switch to approximate τ(n) above this threshold


@lru_cache(maxsize=100000)
def kappa(n, approx_if_large=True):
    """
    Compute κ(n) curvature based on divisor density.
    
    This function calculates the divisor-based curvature metric:
        κ(n) = d(n) · ln(n+1) / e²
    
    where d(n) is the number of divisors of n (tau function).
    
    Args:
        n (int or mpmath.mpf): Integer value for which to compute κ
        approx_if_large (bool): Use fast approximation for n > KAPPA_EXACT_MAX_N
                               to avoid intractable factorization cost (default: True)
        
    Returns:
        mpmath.mpf: Curvature value κ(n)
        
    Notes:
        - For n ≤ 10^7: Uses exact divisor counting (sympy or trial division)
        - For n > 10^7: Uses normal-order heuristic τ(n) ≈ ln(n) for O(1) performance
        - Higher κ(n) indicates higher curvature (more complex factorization)
        - Lower κ(n) suggests lower curvature (simpler prime structure)
        
    Example:
        >>> kappa(12)  # 12 has divisors {1,2,3,4,6,12}, so d(12)=6
        mpf('5.0...')  # Approximately 6 * ln(13) / e²
    """
    # Convert to integer for divisor calculation
    n_int = int(n)
    
    # Compute number of divisors d(n)
    if approx_if_large and n_int > KAPPA_EXACT_MAX_N:
        # Normal-order heuristic for τ(n): O(1) approximation
        # Conservative ln(n); can upgrade to ln(n) * ln(ln(n)) if validated
        ln_n = mp.log(mp.mpf(n_int))
        d_n = ln_n
    else:
        try:
            from sympy import divisors
            d_n = mp.mpf(len(divisors(n_int)))
        except ImportError:
            # Fallback: manual divisor counting
            d_n = mp.mpf(count_divisors(n_int))
    
    # Compute κ(n) = d(n) · ln(n+1) / e²
    n_mp = mp.mpf(n)
    log_term = mp.log(n_mp + mp.mpf('1'))
    
    kappa_val = mp.mpf(d_n) * log_term / E_SQUARED
    
    return kappa_val


@lru_cache(maxsize=10000)
def count_divisors(n):
    """
    Count the number of divisors of n (tau function).
    
    Fallback implementation when sympy is not available.
    Uses trial division up to sqrt(n).
    
    Args:
        n (int): Positive integer
        
    Returns:
        int: Number of divisors of n
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    
    count = 0
    i = 1
    while i * i <= n:
        if n % i == 0:
            count += 1
            if i * i != n:
                count += 1
        i += 1
    
    return count


def kappa_bias(pred, n, epsilon=1e-6):
    """
    DEPRECATED: Apply κ-bias by dividing prediction.
    
    .. deprecated::
        This function applies κ-bias by dividing the prediction by κ(n),
        which causes O(10-100×) scaling for typical n. Use `kappa_bias_factor()`
        with ppm-scale modulation instead.
    
    Formula:
        biased_pred = pred / (κ(n) + ε)
    
    Args:
        pred (mpmath.mpf or float): Base prediction value
        n (int): Index or value for which to compute bias
        epsilon (float): Smoothing factor for numerical stability (default: 1e-6)
        
    Returns:
        mpmath.mpf: κ-biased prediction (likely over-scaled)
        
    Notes:
        - For n in [10^5, 10^6], κ(n) ranges from ~50-70, causing ~50-70× scaling
        - This function is kept for backward compatibility only
        - Prefer using `kappa_bias_factor()` with ppm-scale adjustment:
          `pred * (1 + scale * kappa_bias_factor(n))` where scale ~ 10^-6
        
    See Also:
        kappa_bias_factor: Returns 1/(κ(n)+ε) for ppm-scale modulation
    """
    pred_mp = mp.mpf(pred)
    kappa_val = kappa(n)
    
    # Apply bias: pred / (κ(n) + ε)
    bias_factor = kappa_val + mp.mpf(epsilon)
    biased_pred = pred_mp / bias_factor
    
    return biased_pred


def kappa_bias_factor(n, epsilon=1e-6):
    """
    Compute the bias factor 1 / (κ(n) + ε) for a given n.
    
    This is the multiplicative factor that gets applied to predictions
    to implement κ-biasing.
    
    Args:
        n (int): Index or value for which to compute bias factor
        epsilon (float): Smoothing factor (default: 1e-6)
        
    Returns:
        mpmath.mpf: Bias factor to multiply with predictions
    """
    kappa_val = kappa(n)
    bias_factor = mp.mpf('1') / (kappa_val + mp.mpf(epsilon))
    return bias_factor


def validate_kappa_properties(n_max=1000):
    """
    Validate mathematical properties of the κ function.
    
    Checks:
    1. κ(n) > 0 for all n > 0
    2. κ(n) increases with n on average
    3. κ(prime) < κ(composite) on average (primes have d(p)=2)
    
    Args:
        n_max (int): Maximum n to validate
        
    Returns:
        dict: Validation results with pass/fail status
    """
    results = {
        'positivity_pass': True,
        'monotonicity_violations': 0,
        'prime_vs_composite_pass': None,
        'sample_kappa_values': []
    }
    
    # Check positivity
    for n in range(1, min(100, n_max + 1)):
        k = kappa(n)
        if k <= 0:
            results['positivity_pass'] = False
            break
        if n <= 10:
            results['sample_kappa_values'].append((n, float(k)))
    
    # Check monotonicity (average increase)
    prev_k = kappa(1)
    for n in range(2, min(100, n_max + 1)):
        k = kappa(n)
        if k < prev_k - 0.1:  # Allow small decreases
            results['monotonicity_violations'] += 1
        prev_k = k
    
    # Check prime vs composite
    try:
        from sympy import isprime
        prime_kappas = []
        composite_kappas = []
        
        for n in range(2, min(100, n_max + 1)):
            k = float(kappa(n))
            if isprime(n):
                prime_kappas.append(k)
            else:
                composite_kappas.append(k)
        
        if prime_kappas and composite_kappas:
            avg_prime = sum(prime_kappas) / len(prime_kappas)
            avg_composite = sum(composite_kappas) / len(composite_kappas)
            results['prime_vs_composite_pass'] = avg_prime < avg_composite
            results['avg_prime_kappa'] = avg_prime
            results['avg_composite_kappa'] = avg_composite
    except ImportError:
        results['prime_vs_composite_pass'] = None
    
    return results


if __name__ == "__main__":
    # Demo and validation
    print("κ-Biased Stadlmann Integration - Divisor Density Module")
    print("=" * 60)
    print()
    
    # Test basic kappa values
    test_values = [1, 2, 6, 12, 100, 1000, 10000]
    print("Sample κ(n) values:")
    for n in test_values:
        k = kappa(n)
        print(f"  κ({n:5d}) = {mp.nstr(k, 6)}")
    print()
    
    # Test bias factor
    print("Sample κ-bias factors (1 / (κ(n) + ε)):")
    for n in [100, 1000, 10000]:
        factor = kappa_bias_factor(n)
        print(f"  n={n:5d}: bias_factor = {mp.nstr(factor, 6)}")
    print()
    
    # Validate properties
    print("Validating κ function properties...")
    validation = validate_kappa_properties(n_max=1000)
    print(f"  Positivity check: {'PASS' if validation['positivity_pass'] else 'FAIL'}")
    print(f"  Monotonicity violations: {validation['monotonicity_violations']}")
    if validation['prime_vs_composite_pass'] is not None:
        print(f"  Prime vs Composite: {'PASS' if validation['prime_vs_composite_pass'] else 'FAIL'}")
        print(f"    Avg κ(prime) = {validation.get('avg_prime_kappa', 0):.4f}")
        print(f"    Avg κ(composite) = {validation.get('avg_composite_kappa', 0):.4f}")
    print()
    
    # Demo kappa_bias_factor application
    print("Demo: κ-bias factor for ppm-scale modulation")
    mock_pred = mp.mpf('1299709')  # p_100000
    n_test = 100000
    factor = kappa_bias_factor(n_test)
    KAPPA_BIAS_SCALE = mp.mpf('1e-6')
    adj = mp.mpf('1') + KAPPA_BIAS_SCALE * factor
    modulated = mock_pred * adj
    print(f"  Base prediction: {mp.nstr(mock_pred, 10)}")
    print(f"  κ({n_test}) = {mp.nstr(kappa(n_test), 6)}")
    print(f"  Bias factor (1/κ): {mp.nstr(factor, 6)}")
    print(f"  Adjustment (1 + 10^-6 * factor): {mp.nstr(adj, 10)}")
    print(f"  Modulated prediction: {mp.nstr(modulated, 10)}")
    print(f"  Relative change: {float((modulated - mock_pred) / mock_pred * 100):.6f}%")
