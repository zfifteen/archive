#!/usr/bin/env python3
"""
Red Team Verification: EXACT_PRIMES Validation
==============================================

This script validates all EXACT_PRIMES entries in the Z5D prime predictor
against known prime values computed with sympy. It ensures reproducibility
and empirical validation as required by the red team review.

Metrics computed:
1. ppm (parts per million): |predicted - actual| / actual * 10^6
   - Shows relative error against prime magnitude
   - Can be deceptively small for large primes
   
2. gap-units: |predicted - actual| / log(actual)
   - Shows error in terms of average prime gaps
   - More honest metric for "prime prediction" accuracy
   - Average gap near x is ~log(x), so this normalizes by natural scale

Requirements:
- sympy >= 1.14.0
- mpmath >= 1.3.0 (for high-precision validation)

Usage:
    python verify_exact_primes.py
"""

import sys
import time
import math
from typing import Dict, List, Tuple

try:
    import sympy
    import mpmath as mp
except ImportError as e:
    print(f"Error: Missing required library: {e}")
    print("Install with: pip install sympy mpmath")
    sys.exit(1)

# Set high precision for validation (as required by red team: dps >= 50)
mp.mp.dps = 60

# EXACT_PRIMES from z5d_prime_predictor_gist.py
# These are claimed to be the exact nth prime for n = 10^k, k=1..18
EXACT_PRIMES = {
    10**1: 29,
    10**2: 541,
    10**3: 7919,
    10**4: 104729,
    10**5: 1299709,
    10**6: 15485863,
    10**7: 179424673,
    10**8: 2038074743,
    10**9: 22801763489,
    10**10: 252097800623,
    10**11: 2760727302517,
    10**12: 29996224275833,
    10**13: 323780508946331,
    10**14: 3475385758524527,
    10**15: 37124508045065437,
    10**16: 394906913903735329,
    10**17: 4185296581467695669,
    10**18: 44211790234832169331,
}


def compute_error_metrics(predicted: int, actual: int) -> Dict[str, float]:
    """
    Compute both ppm and gap-units metrics for error analysis.
    
    Args:
        predicted: Predicted prime value
        actual: Actual prime value
        
    Returns:
        Dictionary with 'error', 'ppm', 'gap_units', 'log_actual'
    """
    error = abs(predicted - actual)
    
    if actual == 0:
        return {'error': error, 'ppm': float('inf'), 'gap_units': float('inf'), 'log_actual': 0}
    
    # ppm story: relative error normalized by prime size
    ppm = (error / actual) * 1e6
    
    # gap-units story: error normalized by average gap (≈ log(actual))
    log_actual = math.log(actual)
    gap_units = error / log_actual if log_actual > 0 else float('inf')
    
    return {
        'error': error,
        'ppm': ppm,
        'gap_units': gap_units,
        'log_actual': log_actual
    }


def verify_prime(n: int, expected: int) -> Tuple[bool, int, float]:
    """
    Verify that the nth prime equals the expected value using sympy.
    
    Args:
        n: Index of the prime (e.g., 1000000 for millionth prime)
        expected: Expected value of the nth prime
    
    Returns:
        Tuple of (is_correct, actual_value, computation_time_seconds)
    """
    print(f"  Verifying n={n:,} (p_{n:,})...", end=" ", flush=True)
    
    t0 = time.perf_counter()
    try:
        # Use sympy.prime(n) to get the nth prime
        # Note: sympy is 1-indexed, so prime(1) = 2, prime(10) = 29, etc.
        actual = sympy.prime(n)
        t1 = time.perf_counter()
        elapsed = t1 - t0
        
        is_correct = (actual == expected)
        
        if is_correct:
            print(f"✓ VERIFIED in {elapsed:.3f}s")
        else:
            print(f"✗ MISMATCH in {elapsed:.3f}s")
            print(f"    Expected: {expected:,}")
            print(f"    Actual:   {actual:,}")
            print(f"    Error:    {abs(actual - expected):,}")
        
        return is_correct, actual, elapsed
        
    except Exception as e:
        t1 = time.perf_counter()
        elapsed = t1 - t0
        print(f"✗ ERROR: {e}")
        return False, -1, elapsed


def verify_all_exact_primes() -> Dict[str, any]:
    """
    Verify all entries in EXACT_PRIMES dictionary.
    
    Returns:
        Dictionary with verification results
    """
    print("=" * 80)
    print("RED TEAM VERIFICATION: EXACT_PRIMES Validation")
    print("=" * 80)
    print(f"\nSympy version: {sympy.__version__}")
    print(f"Mpmath version: {mp.__version__}")
    print(f"Mpmath precision: {mp.mp.dps} decimal places")
    print(f"\nVerifying {len(EXACT_PRIMES)} entries...")
    print("-" * 80)
    
    results = {
        'total': len(EXACT_PRIMES),
        'verified': 0,
        'failed': 0,
        'errors': 0,
        'details': [],
        'total_time': 0.0
    }
    
    for n in sorted(EXACT_PRIMES.keys()):
        expected = EXACT_PRIMES[n]
        is_correct, actual, elapsed = verify_prime(n, expected)
        
        results['total_time'] += elapsed
        
        if is_correct:
            results['verified'] += 1
        elif actual == -1:
            results['errors'] += 1
        else:
            results['failed'] += 1
        
        results['details'].append({
            'n': n,
            'expected': expected,
            'actual': actual,
            'is_correct': is_correct,
            'elapsed': elapsed
        })
    
    return results


def print_summary(results: Dict[str, any]) -> None:
    """Print verification summary."""
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"\nTotal entries:     {results['total']}")
    print(f"Verified (✓):      {results['verified']}")
    print(f"Failed (✗):        {results['failed']}")
    print(f"Errors:            {results['errors']}")
    print(f"Total time:        {results['total_time']:.2f} seconds")
    if results['total'] > 0:
        print(f"Average time:      {results['total_time'] / results['total']:.3f} seconds per entry")
    
    if results['failed'] > 0:
        print("\n" + "-" * 80)
        print("FAILED ENTRIES (claimed actuals do not match computed values):")
        print("-" * 80)
        for detail in results['details']:
            if not detail['is_correct'] and detail['actual'] != -1:
                n = detail['n']
                exp = detail['expected']
                act = detail['actual']
                err = abs(act - exp)
                print(f"  n={n:,}: expected {exp:,}, got {act:,}, error={err:,}")
    
    if results['errors'] > 0:
        print("\n" + "-" * 80)
        print("ERRORS (computation failures):")
        print("-" * 80)
        for detail in results['details']:
            if detail['actual'] == -1:
                print(f"  n={detail['n']:,}: computation failed")
    
    print("\n" + "=" * 80)
    if results['verified'] == results['total']:
        print("✓ CONCLUSION: All EXACT_PRIMES entries are VERIFIED and reproducible")
        print("  Empirical validation PASSED with code execution (sympy)")
        print("  All claimed 'actual' values are backed by reproducible computation")
    else:
        print("✗ CONCLUSION: Some EXACT_PRIMES entries FAILED verification")
        print("  UNVERIFIED claims detected - requires correction")
    print("=" * 80)


def verify_specific_claim(n: int = 10**6, expected: int = 15485863) -> None:
    """
    Verify a specific claim from the red team issue.
    
    The issue specifically mentions: "p_1000000=15485863"
    """
    print("\n" + "=" * 80)
    print(f"SPECIFIC CLAIM VERIFICATION: p_{n:,} = {expected:,}")
    print("=" * 80)
    print("(As called out in issue: verify p_1000000=15485863)")
    print()
    
    is_correct, actual, elapsed = verify_prime(n, expected)
    
    print()
    if is_correct:
        print(f"✓ CLAIM VERIFIED: p_{n:,} = {expected:,}")
        print(f"  Computation time: {elapsed:.3f} seconds")
        print(f"  Source: sympy.prime({n:,})")
        print(f"  Precision: mpmath dps={mp.mp.dps}")
    else:
        print(f"✗ CLAIM FAILED: p_{n:,} ≠ {expected:,}")
        print(f"  Expected: {expected:,}")
        print(f"  Actual:   {actual:,}")
        if actual != -1:
            error = abs(actual - expected)
            print(f"  Error:    {error:,}")
    print("=" * 80)


def main():
    """Main entry point."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " RED TEAM GROK 4.1 HEAVY: Empirical Validation".center(78) + "║")
    print("║" + " Axiom: All claims require reproducible code".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # First, verify the specific claim mentioned in the issue
    verify_specific_claim(n=10**6, expected=15485863)
    
    # Then verify all EXACT_PRIMES entries
    results = verify_all_exact_primes()
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if results['verified'] == results['total']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
