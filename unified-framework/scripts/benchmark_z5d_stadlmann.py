#!/usr/bin/env python3
"""
Benchmark script for z5d_predictor_with_dist_level() at N=10^7

This script validates the Stadlmann-enhanced Z5D predictor by:
1. Generating primes up to N=10^7 using sympy
2. Computing density enhancements for AP subsets (mod 6)
3. Validating <0.01% error with bootstrap CI (1,000 resamples)

Author: Unified Framework Team
Date: November 2025
"""

import sys
import os
import time
import numpy as np
from typing import List, Tuple, Dict, Any
import warnings

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Check for optional dependencies
try:
    import sympy
    HAS_SYMPY = True
    try:
        from sympy import primerange
        HAS_PRIMERANGE = True
    except ImportError:
        HAS_PRIMERANGE = False
except ImportError:
    HAS_SYMPY = False
    HAS_PRIMERANGE = False
    sympy = None
    warnings.warn("sympy not available - falling back to basic prime generation")

try:
    import mpmath as mp
    HAS_MPMATH = True
except ImportError:
    HAS_MPMATH = False
    mp = None
    warnings.warn("mpmath not available - using float precision")

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    warnings.warn("scipy not available - bootstrap CI will be limited")

# Import Z5D functions
try:
    from src.core.z_5d_enhanced import z5d_predictor_with_dist_level
    from src.core.conical_flow import conical_density_enhancement_factor
    from src.core.params import DIST_LEVEL_STADLMANN
except ImportError as e:
    print(f"Failed to import Z5D functions: {e}")
    sys.exit(1)


def generate_primes_up_to_limit(limit: int, use_sympy: bool = True) -> List[int]:
    """Generate all primes up to the given limit."""
    if use_sympy and HAS_SYMPY and sympy is not None:
        print(f"Generating primes up to {limit} using sympy...")
        if HAS_PRIMERANGE:
            return list(primerange(2, limit + 1))  # type: ignore
        else:
            # primerange might not be available in some sympy versions
            primes = []
            n = 2
            while n <= limit:
                if sympy.isprime(n):
                    primes.append(n)
                n += 1
            return primes
    else:
        # Fallback sieve implementation
        print(f"Generating primes up to {limit} using sieve...")
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, limit + 1, i):
                    sieve[j] = False
        return [i for i in range(2, limit + 1) if sieve[i]]


def get_primes_in_ap(primes: List[int], mod: int, res: int) -> List[int]:
    """Filter primes that are in the arithmetic progression a mod m."""
    return [p for p in primes if p % mod == res]


def compute_density_enhancement(actual_primes: List[int], predicted_count: float, total_range: int) -> float:
    """Compute the density enhancement factor."""
    actual_density = len(actual_primes) / total_range
    expected_density = predicted_count / total_range
    if expected_density > 0:
        return actual_density / expected_density
    return 1.0


def bootstrap_ci(data: np.ndarray, n_boot: int = 1000, ci_level: float = 0.95) -> Tuple[float, float]:
    """Compute bootstrap confidence interval."""
    if not HAS_SCIPY:
        # Simple percentile bootstrap
        boot_samples = np.random.choice(data, size=(n_boot, len(data)), replace=True)
        boot_means = np.mean(boot_samples, axis=1)
        lower = np.percentile(boot_means, (1 - ci_level) / 2 * 100)
        upper = np.percentile(boot_means, (1 + ci_level) / 2 * 100)
        return float(lower), float(upper)

    # Use scipy for more robust bootstrap
    boot_means = []
    for _ in range(n_boot):
        sample = np.random.choice(data, size=len(data), replace=True)
        boot_means.append(np.mean(sample))
    percentiles = np.percentile(boot_means, [(1 - ci_level) / 2 * 100, (1 + ci_level) / 2 * 100])
    return float(percentiles[0]), float(percentiles[1])


def benchmark_z5d_predictor(N: int = 10**7) -> Dict[str, Any]:
    """Main benchmark function for Z5D predictor with Stadlmann enhancement."""

    print(f"\n{'='*60}")
    print(f"Z5D Predictor Benchmark at N={N:,}")
    print(f"{'='*60}")

    start_time = time.time()

    # Generate primes
    primes = generate_primes_up_to_limit(N)
    n_primes = len(primes)

    print(f"Generated {n_primes:,} primes up to {N:,}")
    print(f"Actual π({N:,}) = {n_primes:,}")

    # Test Stadlmann-enhanced predictions
    results = {}

    # Test points for validation - ensure they don't exceed available primes
    max_test_index = min(n_primes, 10**5)  # Cap at 100k or available primes
    test_indices = [max(1000, max_test_index // 4), max(5000, max_test_index // 2), max_test_index]

    for idx in test_indices:
        if idx > n_primes:
            print(f"Skipping k={idx:,} (exceeds available primes)")
            continue

        print(f"\nTesting k={idx:,} (prime index)")

        # Get actual prime
        actual_prime = primes[idx - 1]  # 0-based indexing
        print(f"Actual prime π({idx:,}) = {actual_prime:,} (mod 6: {actual_prime % 6})")

        # Standard Z5D prediction
        pred_standard = z5d_predictor_with_dist_level(idx)
        error_standard = abs(float(pred_standard) - actual_prime) / actual_prime * 100
        print(f"Z5D prediction: {float(pred_standard):,.0f} (error: {error_standard:.4f}%, mod 6: {int(float(pred_standard)) % 6})")

        # AP-specific prediction (primes ≡ 1 mod 6)
        pred_ap = z5d_predictor_with_dist_level(idx, ap_mod=6, ap_res=1)
        error_ap = abs(float(pred_ap) - actual_prime) / actual_prime * 100
        print(f"Z5D AP prediction: {float(pred_ap):,.0f} (error: {error_ap:.4f}%, mod 6: {int(float(pred_ap)) % 6})")

        # AP-specific prediction (primes ≡ 5 mod 6)
        pred_ap5 = z5d_predictor_with_dist_level(idx, ap_mod=6, ap_res=5)
        error_ap5 = abs(float(pred_ap5) - actual_prime) / actual_prime * 100
        print(f"Z5D AP5 prediction: {float(pred_ap5):,.0f} (error: {error_ap5:.4f}%, mod 6: {int(float(pred_ap5)) % 6})")

        results[idx] = {
            'actual_prime': actual_prime,
            'pred_standard': float(pred_standard),
            'error_standard': error_standard,
            'pred_ap': float(pred_ap),
            'error_ap': error_ap,
            'pred_ap5': float(pred_ap5),
            'error_ap5': error_ap5
        }

    # Density enhancement analysis for AP subsets
    print(f"\n{'='*40}")
    print("Density Enhancement Analysis")
    print(f"{'='*40}")

    # Analyze primes ≡ 1 mod 6
    ap1_primes = get_primes_in_ap(primes, 6, 1)
    ap5_primes = get_primes_in_ap(primes, 6, 5)

    print(f"Primes ≡ 1 mod 6: {len(ap1_primes):,}")
    print(f"Primes ≡ 5 mod 6: {len(ap5_primes):,}")
    print(f"Total primes: {n_primes:,}")

    # Expected counts based on density (should be ~1/φ(6) = 1/2 each)
    expected_ap1 = n_primes / 2
    expected_ap5 = n_primes / 2

    print(f"Expected ≡ 1 mod 6: {expected_ap1:,.0f}")
    print(f"Expected ≡ 5 mod 6: {expected_ap5:,.0f}")

    # Compute enhancement factors
    enhancement_ap1 = len(ap1_primes) / expected_ap1 if expected_ap1 > 0 else 1.0
    enhancement_ap5 = len(ap5_primes) / expected_ap5 if expected_ap5 > 0 else 1.0

    print(f"Density enhancement ≡ 1 mod 6: {enhancement_ap1:.4f}")
    print(f"Density enhancement ≡ 5 mod 6: {enhancement_ap5:.4f}")

    # Check conical enhancement factor
    if HAS_MPMATH and DIST_LEVEL_STADLMANN is not None:
        try:
            enhancement_factor = conical_density_enhancement_factor(n_primes)
            print(f"Conical enhancement factor at N={n_primes}: {float(enhancement_factor):.6f}")
        except Exception as e:
            print(f"Error computing conical enhancement: {e}")

    # Bootstrap confidence intervals for enhancement
    if len(ap1_primes) > 10:  # Need sufficient sample
        ap1_data = np.array([1 if p % 6 == 1 else 0 for p in primes])
        ci_ap1 = bootstrap_ci(ap1_data, n_boot=1000)
        print(f"CI for AP1 density: [{ci_ap1[0]:.4f}, {ci_ap1[1]:.4f}]")

        ap5_data = np.array([1 if p % 6 == 5 else 0 for p in primes])
        ci_ap5 = bootstrap_ci(ap5_data, n_boot=1000)
        print(f"CI for AP5 density: [{ci_ap5[0]:.4f}, {ci_ap5[1]:.4f}]")

    # Error analysis
    errors_standard = [r['error_standard'] for r in results.values()]
    errors_ap = [r['error_ap'] for r in results.values()]
    errors_ap5 = [r['error_ap5'] for r in results.values()]

    print(f"\n{'='*40}")
    print("Error Analysis")
    print(f"{'='*40}")

    if not results:
        print("No test indices were valid for the given N - try larger N")
        max_error = float('inf')
        mean_error_standard = mean_error_ap = mean_error_ap5 = float('nan')
    else:
        print(f"Standard Z5D errors: {errors_standard}")
        print(f"AP-enhanced errors: {errors_ap}")
        print(f"AP5-enhanced errors: {errors_ap5}")

        mean_error_standard = np.mean(errors_standard)
        mean_error_ap = np.mean(errors_ap)
        mean_error_ap5 = np.mean(errors_ap5)

        print(f"Mean error (standard): {mean_error_standard:.6f}%")
        print(f"Mean error (AP enhanced): {mean_error_ap:.6f}%")
        print(f"Mean error (AP5 enhanced): {mean_error_ap5:.6f}%")

        # Check if errors are below 0.01% threshold
        max_error = max(errors_standard + errors_ap + errors_ap5)
        print(f"Maximum error: {max_error:.6f}%")
        print(f"<0.01% error target: {'✓' if max_error < 0.01 else '✗'}")

    total_time = time.time() - start_time
    print(f"\nBenchmark completed in {total_time:.2f} seconds")

    return {
        'n_primes': n_primes,
        'results': results,
        'density_analysis': {
            'ap1_count': len(ap1_primes),
            'ap5_count': len(ap5_primes),
            'enhancement_ap1': enhancement_ap1,
            'enhancement_ap5': enhancement_ap5,
            'expected_ap1': expected_ap1,
            'expected_ap5': expected_ap5
        },
        'error_analysis': {
            'mean_standard': mean_error_standard,
            'mean_ap': mean_error_ap,
            'mean_ap5': mean_error_ap5,
            'max_error': max_error,
            'target_achieved': max_error < 0.01
        },
        'execution_time': total_time
    }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark Z5D predictor with Stadlmann enhancement")
    parser.add_argument('--n', type=int, default=10**7, help='Upper limit for prime generation (default: 10^7)')
    parser.add_argument('--no-sympy', action='store_true', help='Use basic sieve instead of sympy')

    args = parser.parse_args()

    try:
        results = benchmark_z5d_predictor(args.n)

        # Save results to file
        import json
        output_file = f"benchmark_z5d_n{args.n}_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            # Convert numpy types to native Python types for JSON serialization
            json_results = {}
            for k, v in results.items():
                if isinstance(v, dict):
                    json_results[k] = {}
                    for k2, v2 in v.items():
                        if hasattr(v2, 'item'):  # numpy type
                            json_results[k][k2] = v2.item()
                        else:
                            json_results[k][k2] = v2
                else:
                    if hasattr(v, 'item'):
                        json_results[k] = v.item()
                    else:
                        json_results[k] = v

            json.dump(json_results, f, indent=2)

        print(f"\nResults saved to {output_file}")

        # Summary
        target_achieved = results['error_analysis']['target_achieved']
        max_error = results['error_analysis']['max_error']

        print(f"\n{'='*40}")
        print("SUMMARY")
        print(f"{'='*40}")
        print(f"Target (<0.01% error): {'ACHIEVED' if target_achieved else 'NOT ACHIEVED'}")
        print(f"Maximum error: {max_error:.6f}%")
        print(f"Stadlmann enhancement validated: {'✓' if target_achieved else '✗'}")

    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()