#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
κ-Biased Stadlmann Integration Demo
====================================

Demonstration of κ-biased Stadlmann distribution integration in Z_5D predictor.
This script shows the hypothesized 2-8% accuracy lift (ppm error reduction) on
large n by prioritizing low-curvature primes using divisor density weighting.

Reference: κ-Biased Stadlmann Integration in Unified-Framework
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mpmath as mp
import numpy as np
from scipy.stats import bootstrap

# Set high precision
mp.dps = 50

from src.core.z_5d_enhanced import z5d_predictor_with_dist_level
from src.core.divisor_density import kappa


def baseline_z5d_predictor(n, dist_level=0.525):
    """Baseline Stadlmann z5d predictor without κ-bias"""
    return z5d_predictor_with_dist_level(n, dist_level=dist_level, with_kappa_bias=False)


def kappa_biased_predictor(n, dist_level=0.525):
    """κ-biased Stadlmann z5d predictor"""
    return z5d_predictor_with_dist_level(n, dist_level=dist_level, with_kappa_bias=True)


def compute_ppm_error(prediction, true_value):
    """Compute error in parts per million (ppm)"""
    return abs(float(prediction) - float(true_value)) / float(true_value) * 1e6


def run_demo(n_test=100000, replicates=10, verbose=True):
    """
    Run κ-biased Stadlmann demonstration.
    
    Args:
        n_test: Test value for prime index (default: 100000)
        replicates: Number of replicates for bootstrap CI (default: 10, use 100+ for production)
        verbose: Print detailed output
        
    Returns:
        dict: Results with error metrics and deltas
    """
    # Known values for validation
    # From z_5d_enhanced.py KNOWN dict
    known_primes = {
        100000: 1299709,
        1000000: 15485863,
        10000000: 179424673,
        100000000: 2038074743,
        1000000000: 22801763489,
    }
    
    if n_test not in known_primes:
        if verbose:
            print(f"Warning: No known prime for n={n_test}, using n=100000 instead")
        n_test = 100000
    
    true_prime = known_primes[n_test]
    
    if verbose:
        print("=" * 70)
        print("κ-Biased Stadlmann Integration Demo")
        print("=" * 70)
        print(f"\nTest Configuration:")
        print(f"  n = {n_test}")
        print(f"  True p_n = {true_prime}")
        print(f"  Replicates = {replicates}")
        print(f"  Distribution level (θ) = 0.525 (Stadlmann)")
        print()
    
    # Compute baseline predictions
    if verbose:
        print("Computing baseline (Stadlmann without κ-bias)...")
    base_errors = []
    for i in range(replicates):
        pred = baseline_z5d_predictor(n_test)
        error_ppm = compute_ppm_error(pred, true_prime)
        base_errors.append(error_ppm)
        if verbose and i < 3:
            print(f"  Replicate {i+1}: pred={float(pred):.1f}, error={error_ppm:.2f} ppm")
    
    # Compute κ-biased predictions
    if verbose:
        print(f"\nComputing κ-biased predictions...")
        print(f"  κ({n_test}) = {float(kappa(n_test)):.4f}")
    kappa_errors = []
    for i in range(replicates):
        pred = kappa_biased_predictor(n_test)
        error_ppm = compute_ppm_error(pred, true_prime)
        kappa_errors.append(error_ppm)
        if verbose and i < 3:
            print(f"  Replicate {i+1}: pred={float(pred):.1f}, error={error_ppm:.2f} ppm")
    
    # Compute statistics
    mean_base = np.mean(base_errors)
    mean_kappa = np.mean(kappa_errors)
    std_base = np.std(base_errors)
    std_kappa = np.std(kappa_errors)
    
    # Compute delta percentage
    delta_pct = (mean_kappa - mean_base) / mean_base * 100
    
    # Bootstrap confidence interval for κ-biased errors
    if replicates >= 10:
        try:
            ci_result = bootstrap(
                (np.array(kappa_errors),),
                np.mean,
                n_resamples=min(replicates * 10, 1000),
                confidence_level=0.95,
                method='percentile'
            )
            ci_lower = ci_result.confidence_interval.low
            ci_upper = ci_result.confidence_interval.high
        except Exception as e:
            if verbose:
                print(f"Warning: Bootstrap CI failed: {e}")
            ci_lower = ci_upper = mean_kappa
    else:
        ci_lower = ci_upper = mean_kappa
    
    # Print results
    if verbose:
        print("\n" + "=" * 70)
        print("Results Summary")
        print("=" * 70)
        print(f"\nBaseline (Stadlmann without κ-bias):")
        print(f"  Mean error:  {mean_base:.2f} ppm")
        print(f"  Std error:   {std_base:.2f} ppm")
        
        print(f"\nκ-Biased (Stadlmann with κ-bias):")
        print(f"  Mean error:  {mean_kappa:.2f} ppm")
        print(f"  Std error:   {std_kappa:.2f} ppm")
        print(f"  95% CI:      [{ci_lower:.2f}, {ci_upper:.2f}] ppm")
        
        print(f"\nΔ% error: {delta_pct:+.2f}%")
        if delta_pct < 0:
            print(f"  → {abs(delta_pct):.2f}% improvement (error reduction)")
        else:
            print(f"  → {delta_pct:.2f}% degradation (error increase)")
        
        print("\nNote: Current κ-bias formula is pred / (κ(n) + ε) as specified in problem statement.")
        print("      For n~10^5, κ(n)~50-70, causing significant prediction scaling.")
        print("      The hypothesized 2-8% improvement may require:")
        print("        - Parameter tuning (different ε or scaling factor)")
        print("        - Alternative formulas (log-scaled or normalized bias)")
        print("        - Application at a different stage of the prediction pipeline")
        print("      This implementation provides the foundation for such explorations.")
        print("=" * 70)
    
    # Prepare results dictionary
    results = {
        'n_test': n_test,
        'true_prime': true_prime,
        'replicates': replicates,
        'baseline': {
            'mean_error_ppm': mean_base,
            'std_error_ppm': std_base,
            'errors': base_errors
        },
        'kappa_biased': {
            'mean_error_ppm': mean_kappa,
            'std_error_ppm': std_kappa,
            'errors': kappa_errors,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper
        },
        'delta_pct': delta_pct,
        'improvement': delta_pct < 0
    }
    
    return results


def save_results_csv(results, filename='stadlmann_results.csv'):
    """Save results to CSV file"""
    base_errors = results['baseline']['errors']
    kappa_errors = results['kappa_biased']['errors']
    
    # Pad shorter list if needed
    max_len = max(len(base_errors), len(kappa_errors))
    base_errors = base_errors + [np.nan] * (max_len - len(base_errors))
    kappa_errors = kappa_errors + [np.nan] * (max_len - len(kappa_errors))
    
    data = np.array([base_errors, kappa_errors]).T
    np.savetxt(
        filename,
        data,
        delimiter=',',
        header='baseline_error_ppm,kappa_biased_error_ppm',
        comments=''
    )
    print(f"\nResults saved to {filename}")


def main():
    """Main demo function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='κ-Biased Stadlmann Integration Demo'
    )
    parser.add_argument(
        '--n',
        type=int,
        default=100000,
        help='Prime index to test (default: 100000)'
    )
    parser.add_argument(
        '--replicates',
        type=int,
        default=10,
        help='Number of replicates (default: 10, use 100+ for production)'
    )
    parser.add_argument(
        '--out',
        type=str,
        default='stadlmann_results.csv',
        help='Output CSV file (default: stadlmann_results.csv)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed output'
    )
    
    args = parser.parse_args()
    
    # Run demo
    results = run_demo(
        n_test=args.n,
        replicates=args.replicates,
        verbose=not args.quiet
    )
    
    # Save results
    save_results_csv(results, args.out)
    
    # Print summary
    if not args.quiet:
        print("\nQuick Summary:")
        print(f"  Δ% error: {results['delta_pct']:+.2f}%")
        print(f"  Improvement: {'YES' if results['improvement'] else 'NO'}")


if __name__ == "__main__":
    main()
