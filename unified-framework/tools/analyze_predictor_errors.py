#!/usr/bin/env python3
"""
Red Team Analysis: Z5D Predictor Error Analysis with Gap-Units Metric
======================================================================

This script analyzes the Z5D predictor's errors using BOTH metrics:
1. ppm (parts per million) - shows relative error vs prime magnitude
2. gap-units - shows error in terms of average prime gaps (more honest)

The gap-units metric reveals that errors appearing as "0.00 ppm" can 
actually be millions of prime gaps away, providing a more truthful 
assessment of prediction accuracy.

Gap-units formula: |predicted - actual| / log(actual)
  - Average gap near x is ≈ log(x)
  - Measures "how many average gaps away" the prediction is
  - Natural metric for prime prediction quality

Usage:
    python analyze_predictor_errors.py
"""

import sys
import os
import math
import time

# Add gists directory to path
# Note: This is a verification script intended to be run from the repository root.
# For production use, consider proper package installation or PYTHONPATH configuration.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'gists', 'z5d_prime_predictor'))

try:
    from z5d_prime_predictor_gist import predict_prime, EXACT_PRIMES
    import sympy
except ImportError as e:
    print(f"Error: {e}")
    print("Ensure z5d_prime_predictor_gist.py is in gists/z5d_prime_predictor/")
    print("Install sympy with: pip install sympy")
    sys.exit(1)


def compute_error_metrics(predicted: int, actual: int) -> dict:
    """
    Compute both ppm and gap-units metrics for comprehensive error analysis.
    
    Args:
        predicted: Predicted prime value
        actual: Actual prime value
        
    Returns:
        Dictionary with detailed error metrics
    """
    error = abs(predicted - actual)
    
    if actual == 0:
        return {
            'error': error,
            'ppm': float('inf'),
            'gap_units': float('inf'),
            'log_actual': 0,
            'avg_gap': 0
        }
    
    # ppm story: relative error normalized by prime size
    ppm = (error / actual) * 1e6
    
    # gap-units story: error normalized by average gap (≈ log(actual))
    log_actual = math.log(actual)
    avg_gap = log_actual  # Average gap near x is approximately log(x)
    gap_units = error / avg_gap if avg_gap > 0 else float('inf')
    
    return {
        'error': error,
        'ppm': ppm,
        'gap_units': gap_units,
        'log_actual': log_actual,
        'avg_gap': avg_gap
    }


def format_number(num: float, precision: int = 2) -> str:
    """Format number with appropriate precision and units."""
    if num >= 1e9:
        return f"{num/1e9:.{precision}f}B"
    elif num >= 1e6:
        return f"{num/1e6:.{precision}f}M"
    elif num >= 1e3:
        return f"{num/1e3:.{precision}f}K"
    else:
        return f"{num:.{precision}f}"


def analyze_predictor() -> None:
    """
    Comprehensive analysis of Z5D predictor errors using both metrics.
    """
    print("=" * 90)
    print("RED TEAM ANALYSIS: Z5D Predictor Error Analysis with Gap-Units")
    print("=" * 90)
    print("\nTwo stories your error can tell:")
    print("  1. ppm story: |error| / actual × 10⁶  (relative to prime size)")
    print("  2. gap-units: |error| / log(actual)   (in terms of average gaps)")
    print("\nAverage gap near x ≈ log(x), so gap-units shows 'how many gaps away'")
    print("=" * 90)
    
    results = []
    
    print(f"\n{'n':<12} {'Predicted':<20} {'Actual':<20} {'Error':<12} {'ppm':<12} {'Gap-Units':<15}")
    print("-" * 90)
    
    for n in sorted(EXACT_PRIMES.keys()):
        actual = EXACT_PRIMES[n]
        
        # Predict using Z5D
        t0 = time.perf_counter()
        predicted = predict_prime(n)
        t1 = time.perf_counter()
        runtime_ms = (t1 - t0) * 1000
        
        # Compute error metrics
        metrics = compute_error_metrics(predicted, actual)
        
        results.append({
            'n': n,
            'predicted': predicted,
            'actual': actual,
            'runtime_ms': runtime_ms,
            **metrics
        })
        
        # Format for display
        ppm_str = f"{metrics['ppm']:.2f}" if metrics['ppm'] < 1e6 else "INF"
        gap_str = format_number(metrics['gap_units'])
        
        print(f"{n:<12,} {predicted:<20,} {actual:<20,} {metrics['error']:<12,} "
              f"{ppm_str:<12} {gap_str:<15}")
    
    print("-" * 90)
    
    # Summary statistics
    print("\n" + "=" * 90)
    print("SUMMARY STATISTICS")
    print("=" * 90)
    
    ppms = [r['ppm'] for r in results if r['ppm'] < 1e6]
    gaps = [r['gap_units'] for r in results if r['gap_units'] < 1e9]
    
    if ppms:
        print(f"\nppm metrics:")
        print(f"  Mean:      {sum(ppms)/len(ppms):.2f} ppm")
        print(f"  Median:    {sorted(ppms)[len(ppms)//2]:.2f} ppm")
        print(f"  Min:       {min(ppms):.2f} ppm")
        print(f"  Max:       {max(ppms):.2f} ppm")
    
    if gaps:
        print(f"\ngap-units metrics:")
        print(f"  Mean:      {format_number(sum(gaps)/len(gaps))} gaps")
        print(f"  Median:    {format_number(sorted(gaps)[len(gaps)//2])} gaps")
        print(f"  Min:       {format_number(min(gaps))} gaps")
        print(f"  Max:       {format_number(max(gaps))} gaps")
    
    # Detailed examples for key cases
    print("\n" + "=" * 90)
    print("DETAILED EXAMPLES: Same Error, Two Normalizations")
    print("=" * 90)
    
    # Example 1: n = 10^6
    r1 = next(r for r in results if r['n'] == 10**6)
    print(f"\n📊 Example 1: n = 10^6 (millionth prime)")
    print(f"  Predicted: {r1['predicted']:,}")
    print(f"  Actual:    {r1['actual']:,}")
    print(f"  Error:     {r1['error']:,}")
    print(f"  log(p_n):  {r1['log_actual']:.2f}")
    print(f"\n  ppm story:      {r1['ppm']:.2f} ppm (looks modest)")
    print(f"  gap-units:      ~{r1['gap_units']:.1f} average prime gaps away")
    print(f"  → You're {format_number(r1['gap_units'])} prime gaps away")
    
    # Example 2: n = 10^18 (if available in future with predictor)
    if 10**18 in EXACT_PRIMES:
        r2 = next(r for r in results if r['n'] == 10**18)
        print(f"\n📊 Example 2: n = 10^18")
        print(f"  Predicted: {r2['predicted']:,}")
        print(f"  Actual:    {r2['actual']:,}")
        print(f"  Error:     {r2['error']:,}")
        print(f"  log(p_n):  {r2['log_actual']:.2f}")
        print(f"\n  ppm story:      {r2['ppm']:.6f} ppm → rounds to 0.00 ppm")
        print(f"  gap-units:      ~{format_number(r2['gap_units'])} average prime gaps away")
        print(f"  → The 'same' error that shows '0.00 ppm' is {format_number(r2['gap_units'])} gaps!")
    
    # Largest n example
    largest = max(results, key=lambda r: r['n'])
    print(f"\n📊 Example 3: n = {largest['n']:,} (largest tested)")
    print(f"  Predicted: {largest['predicted']:,}")
    print(f"  Actual:    {largest['actual']:,}")
    print(f"  Error:     {largest['error']:,}")
    print(f"  log(p_n):  {largest['log_actual']:.2f}")
    print(f"\n  ppm story:      {largest['ppm']:.6f} ppm")
    print(f"  gap-units:      {format_number(largest['gap_units'])} average prime gaps away")
    
    # Conclusion
    print("\n" + "=" * 90)
    print("CONCLUSION: What This Settles")
    print("=" * 90)
    print("""
Your ppm numbers look breathtaking because:
  • The denominator (p_n) is enormous at large n (e.g., ~10^19)
  • Dividing by that and rounding to 2 decimals almost forces "0.00 ppm"
  • This makes the error appear negligible

In gap-units, the reality is different:
  • The method gives excellent global scale (right order of magnitude)
  • But it's off by hundreds to millions of gaps at large n
  • It doesn't "locate the prime" - it gives a very good approximation

Classical li-inverse + Newton methods ARE EXPECTED to have tiny relative 
error at large n. Your results are fully consistent with that, not beyond it.

The apparent extraordinariness is almost entirely an artifact of:
  1. Using ppm on huge numbers
  2. Rounding to 2 decimal places
  3. Not considering the natural scale (prime gaps)

In a prime-native metric (gap-units), performance is GOOD but not REVOLUTIONARY.
""")
    print("=" * 90)


def main():
    """Main entry point."""
    print("\n")
    print("╔" + "═" * 88 + "╗")
    print("║" + " RED TEAM GROK 4.1 HEAVY: Two Stories Your Error Can Tell".center(88) + "║")
    print("║" + " ppm vs gap-units: Same error, different normalizations".center(88) + "║")
    print("╚" + "═" * 88 + "╝")
    print()
    
    analyze_predictor()


if __name__ == "__main__":
    main()
