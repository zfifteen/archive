#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geodesic Density Enhancement Benchmark
======================================

Validates the geodesic-informed prime density enhancement claims from
the daily summary:
- 15-20% geodesic-driven prime density improvement
- CI [14.6%, 15.4%] for the enhancement
- k* ≈ 0.3 in θ'(n, k) = φ · ((n mod φ)/φ)^k

Reference: Daily Summary "Validated Findings" section
"""

import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.core.params import KAPPA_GEO_DEFAULT, BOOTSTRAP_RESAMPLES_DEFAULT

try:
    from sympy import primerange
    from scipy import stats
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False
    print("Warning: Required libraries not available")


def compute_phi_residue_density(primes, kappa=0.3):
    """
    Compute φ-residue based density using θ'(n, k) = φ · ((n mod φ)/φ)^k
    
    Args:
        primes: List of prime numbers
        kappa: Exponent parameter (k*)
        
    Returns:
        Array of density enhancement factors
    """
    phi = (1 + np.sqrt(5)) / 2
    primes_array = np.array(primes, dtype=float)
    
    # Compute φ-residue
    residues = np.mod(primes_array, phi) / phi
    
    # Apply geodesic transformation
    density_factors = phi * (residues ** kappa)
    
    return density_factors


def bootstrap_geodesic_enhancement(primes, kappa=0.3, n_bootstrap=1000, rng=None):
    """
    Compute bootstrap confidence interval for geodesic enhancement

    Args:
        primes: List of prime numbers
        kappa: Geodesic exponent parameter
        n_bootstrap: Number of bootstrap resamples
        rng: Random number generator for reproducibility

    Returns:
        dict with enhancement statistics and confidence intervals
    """
    if rng is None:
        rng = np.random.default_rng()

    n_primes = len(primes)
    enhancements = []

    for _ in range(n_bootstrap):
        # Bootstrap resample
        indices = rng.choice(n_primes, size=n_primes, replace=True)
        sample_primes = [primes[i] for i in indices]

        # Compute density factors
        density_factors = compute_phi_residue_density(sample_primes, kappa)

        # Baseline (uniform density)
        baseline_density = 1.0

        # Enhanced density (mean of geodesic factors)
        enhanced_density = np.mean(density_factors)

        # Compute enhancement percentage
        enhancement_pct = (enhanced_density - baseline_density) / baseline_density * 100
        enhancements.append(enhancement_pct)

    enhancements = np.array(enhancements)

    return {
        'mean_enhancement': np.mean(enhancements),
        'ci_lower': np.percentile(enhancements, 2.5),
        'ci_upper': np.percentile(enhancements, 97.5),
        'std': np.std(enhancements)
    }


def test_claimed_enhancement_range(max_n=1000000, rng=None, verify_claims=False):
    """
    Test if geodesic enhancement falls within claimed 15-20% range
    with CI [14.6%, 15.4%]
    """
    print("=" * 70)
    print("Geodesic Density Enhancement Validation")
    print("=" * 70)

    if not LIBS_AVAILABLE:
        print("\nError: Required libraries not available")
        return

    # Generate test primes
    print(f"\nGenerating primes up to N = {max_n:,}...")
    primes = list(primerange(2, max_n))
    n_primes = len(primes)
    print(f"Generated {n_primes:,} primes")

    # Test with k* = 0.3 (claimed optimal)
    kappa_optimal = 0.3
    print(f"\nTesting with k* = {kappa_optimal} (claimed optimal)")
    print(f"Bootstrap resamples: {BOOTSTRAP_RESAMPLES_DEFAULT:,}")

    # Use subset for faster computation
    test_primes = primes[:10000]
    result = bootstrap_geodesic_enhancement(
        test_primes,
        kappa=kappa_optimal,
        n_bootstrap=BOOTSTRAP_RESAMPLES_DEFAULT,
        rng=rng
    )

    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)
    print(f"Mean enhancement: {result['mean_enhancement']:>10.4f}%")
    print(f"95% CI: [{result['ci_lower']:.4f}%, {result['ci_upper']:.4f}%]")
    print(f"Standard deviation: {result['std']:.4f}%")

    if verify_claims:
        # Check against claimed range
        claimed_range = [14.6, 15.4]
        claimed_broad_range = [15.0, 20.0]

        print("\n" + "=" * 70)
        print("Validation Against Claims")
        print("=" * 70)

        # Check if CI overlaps with claimed CI [14.6%, 15.4%]
        ci_overlap = (result['ci_lower'] <= claimed_range[1] and
                      result['ci_upper'] >= claimed_range[0])

        print(f"Claimed CI: [{claimed_range[0]}%, {claimed_range[1]}%]")
        print(f"Observed CI: [{result['ci_lower']:.4f}%, {result['ci_upper']:.4f}%]")
        print(f"CI overlap: {'Yes ✓' if ci_overlap else 'No ✗'}")

        # Check if mean is in broad range [15%, 20%]
        in_broad_range = (claimed_broad_range[0] <= result['mean_enhancement'] <=
                          claimed_broad_range[1])

        print(f"\nClaimed broad range: [{claimed_broad_range[0]}%, {claimed_broad_range[1]}%]")
        print(f"Mean in range: {'Yes ✓' if in_broad_range else 'No ✗'}")
    else:
        print("\nPipeline validation: Statistics computed successfully")

    return result


def test_kappa_optimization(kappa_values=None, rng=None):
    """
    Test geodesic enhancement across different kappa values
    to validate k* ≈ 0.3 claim
    """
    print("\n" + "=" * 70)
    print("Kappa (k*) Optimization Analysis")
    print("=" * 70)

    if not LIBS_AVAILABLE:
        print("\nError: Required libraries not available")
        return

    if kappa_values is None:
        kappa_values = np.linspace(0.1, 0.5, 9)

    # Generate test primes - efficiently get only needed count
    from itertools import islice
    max_n = 500000
    primes = list(islice(primerange(2, max_n), 5000))  # Use smaller subset

    print(f"\nTesting {len(kappa_values)} kappa values...")
    print(f"\n{'k*':>6}  {'Enhancement':>12}  {'CI Lower':>10}  {'CI Upper':>10}")
    print("-" * 50)

    results = []
    for kappa in kappa_values:
        result = bootstrap_geodesic_enhancement(
            primes,
            kappa=kappa,
            n_bootstrap=100,  # Reduced for speed
            rng=rng
        )

        marker = " ← Claimed optimal" if abs(kappa - 0.3) < 0.01 else ""
        print(f"{kappa:>6.2f}  {result['mean_enhancement']:>11.4f}%  "
              f"{result['ci_lower']:>9.4f}%  {result['ci_upper']:.4f}%{marker}")

        results.append({
            'kappa': kappa,
            **result
        })

    # Find optimal kappa (maximum enhancement)
    optimal_idx = np.argmax([r['mean_enhancement'] for r in results])
    optimal_kappa = results[optimal_idx]['kappa']
    optimal_enhancement = results[optimal_idx]['mean_enhancement']

    print("\n" + "=" * 70)
    print("Optimization Results")
    print("=" * 70)
    print(f"Optimal k* (observed): {optimal_kappa:.2f}")
    print(f"Enhancement at optimal: {optimal_enhancement:.4f}%")
    print(f"Claimed optimal k*: 0.30")
    print(f"Difference: {abs(optimal_kappa - 0.30):.2f}")

    return results


def test_scale_dependence(k_min=10000, k_max=1000000, rng=None):
    """
    Test how geodesic enhancement scales with sample size
    """
    print("\n" + "=" * 70)
    print("Scale Dependence Analysis")
    print("=" * 70)

    if not LIBS_AVAILABLE:
        print("\nError: Required libraries not available")
        return

    # Test at different scales
    scales = [k_min, k_min*10, k_max] if k_max > k_min else [k_min]
    kappa = KAPPA_GEO_DEFAULT

    print(f"\nTesting geodesic enhancement at different scales")
    print(f"Using k* = {kappa}")
    print(f"\n{'N':>10}  {'Primes':>10}  {'Enhancement':>12}  {'CI Lower':>10}  {'CI Upper':>10}")
    print("-" * 65)

    for max_n in scales:
        primes = list(primerange(2, max_n))

        # Use subset for faster computation
        test_primes = primes[:min(5000, len(primes))]

        result = bootstrap_geodesic_enhancement(
            test_primes,
            kappa=kappa,
            n_bootstrap=100,  # Reduced for speed
            rng=rng
        )

        print(f"{max_n:>10,}  {len(primes):>10,}  {result['mean_enhancement']:>11.4f}%  "
              f"{result['ci_lower']:>9.4f}%  {result['ci_upper']:>9.4f}%")

    print("\nObservation: Enhancement should be relatively stable across scales")

    return None


def test_kolmogorov_smirnov_asymmetry(max_n=100000):
    """
    Test for asymmetry in prime clustering using KS test
    Claims: KS p ≈ 0 for asymmetry in clustering
    """
    print("\n" + "=" * 70)
    print("Kolmogorov-Smirnov Asymmetry Test")
    print("=" * 70)

    if not LIBS_AVAILABLE:
        print("\nError: Required libraries not available")
        return

    # Generate primes
    primes = list(primerange(2, max_n))

    # Compute φ-residues using vectorized operations for better performance
    phi = (1 + np.sqrt(5)) / 2
    primes_array = np.array(primes, dtype=float)
    residues = (primes_array % phi) / phi

    # Test against uniform distribution
    ks_statistic, p_value = stats.kstest(residues, 'uniform')

    print(f"\nSample size: {len(primes):,} primes")
    print(f"φ-residue distribution vs uniform")
    print(f"\nKS statistic: {ks_statistic:.6f}")
    print(f"p-value: {p_value:.2e}")

    # Interpret results
    significant = p_value < 0.001
    print(f"\nSignificant asymmetry (p < 0.001): {'Yes ✓' if significant else 'No ✗'}")

    if significant:
        print("Result: Primes show non-uniform φ-residue distribution")
        print("        Consistent with geodesic clustering effects")
    else:
        print("Result: No significant deviation from uniform distribution")

    return {
        'ks_statistic': ks_statistic,
        'p_value': p_value,
        'significant': significant
    }


def main():
    """Run all benchmark tests"""
    parser = argparse.ArgumentParser(description='Geodesic Density Enhancement Benchmark')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducible results')
    parser.add_argument('--max-n', type=int, default=1000000, help='Maximum N for prime generation')
    parser.add_argument('--k-min', type=int, default=10000, help='Minimum k value for testing')
    parser.add_argument('--k-max', type=int, default=1000000, help='Maximum k value for testing')
    parser.add_argument('--levels', type=float, nargs='+', default=[0.1, 0.2, 0.3, 0.4, 0.5],
                       help='Kappa values to test')
    parser.add_argument('--verify-claims', action='store_true', help='Verify specific numeric claims')

    args = parser.parse_args()

    # Set up deterministic seeding
    rng = np.random.default_rng(args.seed)
    print("Geodesic Density Enhancement Benchmark Suite")
    print("Reference: Daily Summary 'Validated Findings'")
    print(f"Default kappa (k*): {KAPPA_GEO_DEFAULT}")
    print(f"Random seed: {args.seed}")
    print()

    # Test 1: Validate claimed 15-20% enhancement with CI [14.6%, 15.4%]
    try:
        enhancement_result = test_claimed_enhancement_range(max_n=args.max_n, rng=rng, verify_claims=args.verify_claims)
    except Exception as e:
        print(f"Test 1 failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Validate k* ≈ 0.3 as optimal
    try:
        kappa_results = test_kappa_optimization(kappa_values=args.levels, rng=rng)
    except Exception as e:
        print(f"Test 2 failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 3: Scale dependence
    try:
        test_scale_dependence(k_min=args.k_min, k_max=args.k_max, rng=rng)
    except Exception as e:
        print(f"Test 3 failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 4: KS test for asymmetry
    try:
        ks_result = test_kolmogorov_smirnov_asymmetry(max_n=args.max_n)
    except Exception as e:
        print(f"Test 4 failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("Benchmark Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
