#!/usr/bin/env python3
"""
Adaptive Windowing Adversarial Test
Tests asymmetric distance-dependent enrichment in factor detection
"""

import sys
import math
from typing import Tuple, List, Dict
import statistics

try:
    import gmpy2
    from gmpy2 import is_prime as gmpy_is_prime
    HAS_GMPY2 = True
except ImportError:
    HAS_GMPY2 = False

from z5d_adapter import n_est, geometric_resonance_score, prime_counting_function


def is_prime_simple(n):
    """Simple primality test for small numbers."""
    if HAS_GMPY2:
        return gmpy_is_prime(n)
    
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Trial division
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def find_next_prime(n):
    """Find the next prime >= n."""
    if n < 2:
        return 2
    if n == 2:
        return 2
    
    # Make odd
    if n % 2 == 0:
        n += 1
    
    while not is_prime_simple(n):
        n += 2
        if n > 10**15:  # Safety limit for simple test
            raise ValueError("Prime search exceeded safety limit")
    
    return n


def find_prev_prime(n):
    """Find the previous prime <= n."""
    if n <= 2:
        return 2
    if n == 3:
        return 3
    
    # Make odd
    if n % 2 == 0:
        n -= 1
    
    while n >= 3:
        if is_prime_simple(n):
            return n
        n -= 2
    
    return 2


def factorize_semiprime(N, max_attempts=1000000):
    """
    Simple trial division factorization.
    Only works for small semiprimes in test cases.
    """
    if N < 4:
        return None, None
    
    # Try small factors first
    for p in range(2, min(int(math.sqrt(N)) + 1, max_attempts)):
        if N % p == 0:
            q = N // p
            if is_prime_simple(p) and is_prime_simple(q):
                return (p, q) if p <= q else (q, p)
    
    return None, None


def adaptive_window_search(N, base_offset_pct=0.1, max_offset_pct=0.5, 
                           k_or_phase=0.27952859830111265):
    """
    Adaptive windowing search for semiprime factors.
    
    Tests asymmetric enrichment at increasing distances from sqrt(N).
    
    Args:
        N: Semiprime to factor
        base_offset_pct: Starting offset percentage from sqrt(N)
        max_offset_pct: Maximum offset to test
        k_or_phase: Geometric resonance phase constant
    
    Returns:
        Dict with search results and enrichment metrics
    """
    sqrt_n = math.sqrt(N)
    ln_n = math.log(N)
    
    results = {
        'N': N,
        'sqrt_N': sqrt_n,
        'searches': [],
        'factors_found': None,
        'enrichment_detected': False
    }
    
    # Adaptive window sizing: radius = offset * 1.2
    offset_pct = base_offset_pct
    
    while offset_pct <= max_offset_pct:
        offset = sqrt_n * offset_pct
        radius = offset * 1.2  # Adaptive radius
        
        # Search below sqrt(N) for p
        p_center = sqrt_n - offset
        p_candidates = []
        
        # Sample primes in window
        p_low = max(2, int(p_center - radius))
        p_high = int(p_center + radius)
        
        for candidate in range(p_low, p_high, 2 if p_low > 2 else 1):
            if is_prime_simple(candidate):
                # Check if it divides N
                if N % candidate == 0:
                    q = N // candidate
                    if is_prime_simple(q):
                        results['factors_found'] = (candidate, q)
                        results['enrichment_detected'] = True
                        results['detection_offset_pct'] = offset_pct
                        break
                
                p_candidates.append(candidate)
            
            if len(p_candidates) >= 100:  # Limit candidates per window
                break
        
        if results['factors_found']:
            break
        
        # Search above sqrt(N) for q
        q_center = sqrt_n + offset
        q_candidates = []
        
        q_low = int(q_center - radius)
        q_high = int(q_center + radius)
        
        for candidate in range(q_low, q_high, 2 if q_low > 2 else 1):
            if is_prime_simple(candidate):
                if N % candidate == 0:
                    p = N // candidate
                    if is_prime_simple(p):
                        results['factors_found'] = (p, candidate)
                        results['enrichment_detected'] = True
                        results['detection_offset_pct'] = offset_pct
                        break
                
                q_candidates.append(candidate)
            
            if len(q_candidates) >= 100:
                break
        
        if results['factors_found']:
            break
        
        # Calculate enrichment ratio
        p_enrichment = len(p_candidates) / (radius * 2) if radius > 0 else 0
        q_enrichment = len(q_candidates) / (radius * 2) if radius > 0 else 0
        
        search_result = {
            'offset_pct': offset_pct,
            'radius': radius,
            'p_candidates': len(p_candidates),
            'q_candidates': len(q_candidates),
            'p_enrichment': p_enrichment,
            'q_enrichment': q_enrichment,
            'enrichment_ratio': q_enrichment / p_enrichment if p_enrichment > 0 else 0
        }
        
        results['searches'].append(search_result)
        
        # Increase offset
        offset_pct += 0.05
    
    return results


def analyze_asymmetric_enrichment(semiprimes: List[int], 
                                   k_or_phase=0.27952859830111265):
    """
    Analyze asymmetric enrichment patterns across multiple semiprimes.
    
    Tests hypothesis that q (larger factor) shows preferential enrichment
    at distances farther from sqrt(N).
    
    Args:
        semiprimes: List of semiprimes to analyze
        k_or_phase: Phase constant
    
    Returns:
        Analysis results with statistical metrics
    """
    all_results = []
    
    for N in semiprimes:
        result = adaptive_window_search(N, k_or_phase=k_or_phase)
        all_results.append(result)
    
    # Aggregate statistics
    p_enrichments = []
    q_enrichments = []
    enrichment_ratios = []
    
    for result in all_results:
        for search in result['searches']:
            if search['p_enrichment'] > 0:
                p_enrichments.append(search['p_enrichment'])
            if search['q_enrichment'] > 0:
                q_enrichments.append(search['q_enrichment'])
            if search['enrichment_ratio'] > 0:
                enrichment_ratios.append(search['enrichment_ratio'])
    
    analysis = {
        'total_semiprimes': len(semiprimes),
        'total_searches': sum(len(r['searches']) for r in all_results),
        'factors_found': sum(1 for r in all_results if r['factors_found']),
        'p_enrichment_mean': statistics.mean(p_enrichments) if p_enrichments else 0,
        'q_enrichment_mean': statistics.mean(q_enrichments) if q_enrichments else 0,
        'enrichment_ratio_mean': statistics.mean(enrichment_ratios) if enrichment_ratios else 0,
        'enrichment_ratio_median': statistics.median(enrichment_ratios) if enrichment_ratios else 0,
        'results': all_results
    }
    
    # Test for asymmetry: is q_enrichment significantly > p_enrichment?
    if p_enrichments and q_enrichments:
        analysis['asymmetry_detected'] = analysis['q_enrichment_mean'] > analysis['p_enrichment_mean'] * 1.5
    else:
        analysis['asymmetry_detected'] = False
    
    return analysis


def test_rsa_challenges():
    """
    Test on known RSA challenge numbers (small ones for validation).
    """
    # Small test semiprimes that we can actually factor
    test_cases = [
        ('N=15', 15, (3, 5)),
        ('N=21', 21, (3, 7)),
        ('N=35', 35, (5, 7)),
        ('N=77', 77, (7, 11)),
        ('N=143', 143, (11, 13)),
        ('N=323', 323, (17, 19)),
        ('N=899', 899, (29, 31)),
    ]
    
    print("RSA Challenge Test (Small Semiprimes)")
    print("=" * 60)
    
    results = []
    
    for name, N, expected in test_cases:
        print(f"\nTesting {name}:")
        result = adaptive_window_search(N)
        
        if result['factors_found']:
            p, q = result['factors_found']
            print(f"  ✓ Factors found: {p} × {q}")
            print(f"  Detection at offset: {result.get('detection_offset_pct', 0)*100:.1f}%")
            
            # Calculate asymmetry
            ln_p = math.log(p)
            ln_q = math.log(q)
            asymmetry = abs(ln_q - ln_p) / (ln_q + ln_p) * 100
            print(f"  Asymmetry: {asymmetry:.2f}%")
            
            # Z5D score
            score = geometric_resonance_score(p, q, N)
            print(f"  Z5D score: {score:.4f}")
        else:
            print(f"  ✗ Factors not found in adaptive search")
        
        results.append(result)
    
    return results


def test_unbalanced_semiprimes():
    """
    Test on deliberately unbalanced semiprimes.
    """
    print("\n\nUnbalanced Semiprime Test")
    print("=" * 60)
    
    # Create unbalanced semiprimes
    test_cases = [
        (3, 97),   # Very unbalanced
        (7, 89),
        (11, 83),
        (13, 79),
        (17, 73),
    ]
    
    semiprimes = [p * q for p, q in test_cases]
    analysis = analyze_asymmetric_enrichment(semiprimes)
    
    print(f"\nTotal semiprimes tested: {analysis['total_semiprimes']}")
    print(f"Factors found: {analysis['factors_found']}/{analysis['total_semiprimes']}")
    print(f"Mean p-enrichment: {analysis['p_enrichment_mean']:.6f}")
    print(f"Mean q-enrichment: {analysis['q_enrichment_mean']:.6f}")
    print(f"Mean enrichment ratio (q/p): {analysis['enrichment_ratio_mean']:.2f}")
    print(f"Asymmetry detected: {analysis['asymmetry_detected']}")
    
    return analysis


if __name__ == "__main__":
    print("Adaptive Windowing Adversarial Test")
    print("=" * 60)
    print()
    
    # Run tests
    rsa_results = test_rsa_challenges()
    unbalanced_results = test_unbalanced_semiprimes()
    
    print("\n" + "=" * 60)
    print("✓ Adversarial testing complete")
