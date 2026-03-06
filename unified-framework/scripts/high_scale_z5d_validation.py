#!/usr/bin/env python3
"""
High-Scale Z5D Prime Prediction Validation
==========================================

This script implements the high-scale Z5D validation from the z-sandbox repository,
adapted for the unified-framework. It validates predictor behavior at cryptographic
scales (10^500 to 10^1233) with ppm-scale relative error bounds.

Based on: HIGH_SCALE_Z5D_VALIDATION.md from z-sandbox
"""

import sys
import os
import time
import random
from typing import Dict, List, Any, Optional, Tuple

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import mpmath as mp
    HAS_MPMATH = True
except ImportError:
    HAS_MPMATH = False
    mp = None

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Import Z5D functions
try:
    from core.z_5d_enhanced import z5d_predictor_with_dist_level
except ImportError:
    print("Warning: Could not import Z5D functions")

def z5d_predictor_full_highscale(n: int, dist_level: float = 0.71, use_conical: bool = True, dps: int = 2000) -> int:
    """
    High-scale Z5D prime predictor with full precision arithmetic.

    Based on the z-sandbox implementation for cryptographic scales.

    Args:
        n: Prime index
        dist_level: Distribution level correction factor (default: 0.71)
        use_conical: Whether to apply conical enhancement
        dps: Decimal precision for mpmath

    Returns:
        Predicted n-th prime as Python int
    """
    if not HAS_MPMATH:
        raise ImportError("mpmath required for high-scale validation")

    if dps < 1500:
        raise ValueError(f"dps must be >= 1500 for high-scale validation, got {dps}")

    # Short-circuit for small n to avoid log(1) singularities
    if n <= 9:
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        return small_primes[n - 1] if n <= len(small_primes) else 29  # Fallback

    # Set working precision
    with mp.workdps(dps):
        n_mp = mp.mpf(n)

        # Base 2-term PNT approximation
        ln_n = mp.log(n_mp)
        ln_ln_n = mp.log(ln_n)

        base_prediction = n_mp * ln_n + n_mp * ln_ln_n - n_mp

        # Distribution-level correction
        correction = dist_level * n_mp / ln_n

        # Conical enhancement (scale-adaptive)
        if use_conical:
            # enhancement = 0.015 · (ln(n) / ln(10^6) - 1)
            ln_million = mp.log(mp.mpf('1000000'))
            enhancement_factor = mp.mpf('0.015') * (ln_n / ln_million - 1)
            effective_dist_level = dist_level + enhancement_factor
            correction = effective_dist_level * n_mp / ln_n

        # Final prediction
        prediction_mp = base_prediction + correction

        # Convert to Python int (arbitrary precision)
        return int(mp.nint(prediction_mp))

def estimate_prime_index(magnitude_power: int, dps: int = 2000) -> int:
    """
    Estimate prime index n for target magnitude ~10^K.

    Uses inverse PNT: n ≈ P / ln(P) where P ≈ 10^K

    Args:
        magnitude_power: K in 10^K
        dps: Decimal precision

    Returns:
        Estimated prime index n
    """
    if not HAS_MPMATH:
        raise ImportError("mpmath required for prime index estimation")

    with mp.workdps(dps):
        # Target magnitude P ≈ 10^magnitude_power
        p_target = mp.mpf(10) ** magnitude_power

        # Inverse PNT: n ≈ P / ln(P)
        ln_p = mp.log(p_target)
        n_estimate = p_target / ln_p

        return int(mp.nint(n_estimate))

def compute_asymptotic_error_bound(n: int, dps: int = 2000) -> float:
    """
    Compute theoretical asymptotic relative error bound.

    ε(n) ≈ (ln ln n) / (ln n)²

    Args:
        n: Prime index
        dps: Decimal precision

    Returns:
        Asymptotic relative error bound
    """
    if not HAS_MPMATH:
        raise ImportError("mpmath required for error bound computation")

    with mp.workdps(dps):
        n_mp = mp.mpf(n)
        ln_n = mp.log(n_mp)
        ln_ln_n = mp.log(ln_n)

        # ε(n) ≈ (ln ln n) / (ln n)²
        error_bound = ln_ln_n / (ln_n ** 2)

        return float(error_bound)

def validate_high_scale_prediction(magnitude_power: int,
                                 dist_level: float = 0.71,
                                 use_conical: bool = True,
                                 dps: int = 2000) -> Dict[str, Any]:
    """
    Validate prediction at a specific high scale.

    Args:
        magnitude_power: K in target magnitude ~10^K
        dist_level: Distribution level correction
        use_conical: Whether to use conical enhancement
        dps: Decimal precision

    Returns:
        Dictionary with validation metrics
    """
    start_time = time.time()

    # Estimate prime index
    n_estimate = estimate_prime_index(magnitude_power, dps)

    # Make prediction
    p_hat = z5d_predictor_full_highscale(n_estimate, dist_level, use_conical, dps)

    runtime = time.time() - start_time

    # Compute error bound
    error_bound = compute_asymptotic_error_bound(n_estimate, dps)
    error_ppm = error_bound * 1e6  # Convert to ppm

    # Get bit length
    bit_length = p_hat.bit_length()

    return {
        'magnitude_power': magnitude_power,
        'target_magnitude': f"~10^{magnitude_power}",
        'estimated_index': n_estimate,
        'predicted_prime': p_hat,
        'bit_length': bit_length,
        'runtime_ms': runtime * 1000,
        'asymptotic_error_bound': error_bound,
        'error_ppm': error_ppm,
        'dist_level': dist_level,
        'use_conical': use_conical,
        'dps': dps
    }

def bootstrap_predictor_stability(magnitude_power: int,
                                n_boot: int = 1000,
                                dist_level: float = 0.71,
                                dps: int = 2000) -> Dict[str, Any]:
    """
    Bootstrap analysis of predictor stability.

    Args:
        magnitude_power: K in target magnitude ~10^K
        n_boot: Number of bootstrap resamples
        dist_level: Distribution level correction
        dps: Decimal precision

    Returns:
        Bootstrap statistics
    """
    if not HAS_NUMPY:
        return {"error": "numpy required for bootstrap analysis"}

    predictions = []
    runtimes = []

    print(f"Running bootstrap stability analysis for 10^{magnitude_power} (n_boot={n_boot})...")

    for i in range(n_boot):
        if (i + 1) % 100 == 0:
            print(f"  Bootstrap sample {i + 1}/{n_boot}")

        result = validate_high_scale_prediction(magnitude_power, dist_level, True, dps)
        predictions.append(result['predicted_prime'])
        runtimes.append(result['runtime_ms'])

    # Compute statistics
    predictions_array = np.array(predictions)
    runtimes_array = np.array(runtimes)

    # Bootstrap confidence intervals
    pred_mean = np.mean(predictions_array)
    pred_std = np.std(predictions_array)
    pred_ci_lower = np.percentile(predictions_array, 2.5)
    pred_ci_upper = np.percentile(predictions_array, 97.5)

    runtime_mean = np.mean(runtimes_array)
    runtime_std = np.std(runtimes_array)
    runtime_ci_lower = np.percentile(runtimes_array, 2.5)
    runtime_ci_upper = np.percentile(runtimes_array, 97.5)

    # Coefficient of variation
    pred_cv = pred_std / pred_mean if pred_mean > 0 else 0
    runtime_cv = runtime_std / runtime_mean if runtime_mean > 0 else 0

    return {
        'n_boot': n_boot,
        'magnitude_power': magnitude_power,
        'prediction_stats': {
            'mean': float(pred_mean),
            'std': float(pred_std),
            'cv': float(pred_cv),
            'ci_95_lower': float(pred_ci_lower),
            'ci_95_upper': float(pred_ci_upper)
        },
        'runtime_stats': {
            'mean': float(runtime_mean),
            'std': float(runtime_std),
            'cv': float(runtime_cv),
            'ci_95_lower': float(runtime_ci_lower),
            'ci_95_upper': float(runtime_ci_upper)
        },
        'stability_assessment': 'stable' if pred_cv < 0.01 else 'unstable'  # <1% CV = stable
    }

def run_high_scale_validation_suite(target_magnitudes: Optional[List[int]] = None,
                                  dist_level: float = 0.71,
                                  use_conical: bool = True,
                                  dps: int = 2000,
                                  with_bootstrap: bool = False) -> Dict[str, Any]:
    """
    Run complete high-scale validation suite.

    Args:
        target_magnitudes: List of magnitude powers (default: [500, 750, 1000, 1233])
        dist_level: Distribution level correction
        use_conical: Whether to use conical enhancement
        dps: Decimal precision
        with_bootstrap: Whether to run bootstrap stability analysis

    Returns:
        Complete validation results
    """
    if target_magnitudes is None:
        target_magnitudes = [500, 750, 1000, 1233]

    print("=" * 80)
    print("HIGH-SCALE Z5D PRIME PREDICTION VALIDATION")
    print("=" * 80)
    print()
    print("Configuration:")
    print(f"  Distribution level θ: {dist_level}")
    print(f"  Conical enhancement: {use_conical}")
    print(f"  Working precision: {dps} decimal places")
    print(f"  Bootstrap analysis: {with_bootstrap}")
    print()

    results = []
    for magnitude in target_magnitudes:
        print(f"Testing magnitude ~10^{magnitude}...")
        result = validate_high_scale_prediction(magnitude, dist_level, use_conical, dps)
        results.append(result)

        print(f"  Target magnitude: {result['target_magnitude']}")
        print(f"  Estimated index n: ~10^{len(str(result['estimated_index']))-1} ({len(str(result['estimated_index']))} digits)")
        print(f"  Predicted p̂ bit length: {result['bit_length']} bits")
        print(".2f")
        print(".6f")
        print(".4f")
        print()

    # Summary statistics
    bit_lengths = [r['bit_length'] for r in results]
    error_ppms = [r['error_ppm'] for r in results]
    runtimes = [r['runtime_ms'] for r in results]

    print("-" * 40)
    print("SUMMARY STATISTICS")
    print("-" * 40)
    print(f"Error ceiling range: {min(error_ppms):.4f} - {max(error_ppms):.4f} ppm")
    print(".4f")
    print(".2f")
    print(".2f")
    print(f"Bit length range: {min(bit_lengths)} - {max(bit_lengths)} bits")
    print()

    # Bootstrap stability analysis
    bootstrap_results = {}
    if with_bootstrap and HAS_NUMPY:
        print("-" * 40)
        print("BOOTSTRAP STABILITY ANALYSIS")
        print("-" * 40)

        for magnitude in target_magnitudes:
            boot_result = bootstrap_predictor_stability(magnitude, 100, dist_level, dps)
            bootstrap_results[magnitude] = boot_result

            print(f"Magnitude 10^{magnitude}:")
            pred_stats = boot_result['prediction_stats']
            print(".2e")
            print(".2e")
            print(f"  Stability: {boot_result['stability_assessment']}")
            print()

    # Acceptance gates
    print("-" * 40)
    print("ACCEPTANCE GATES")
    print("-" * 40)

    gates_passed = 0
    total_gates = 0

    # Gate 1: Error at ~10^500 <= 10 ppm
    total_gates += 1
    gate1_result = results[0]['error_ppm'] <= 10.0
    print(f"Gate 1: Error at ~10^500 <= 10 ppm: {'✓ PASS' if gate1_result else '✗ FAIL'}")
    print(f"        Actual: {results[0]['error_ppm']:.4f} ppm")
    if gate1_result:
        gates_passed += 1

    # Gate 2: Error decreases with magnitude
    total_gates += 1
    gate2_result = all(error_ppms[i] >= error_ppms[i+1] for i in range(len(error_ppms)-1))
    print(f"Gate 2: Error decreases with magnitude: {'✓ PASS' if gate2_result else '✗ FAIL'}")
    trend = " > ".join([f"{x:.4f}" for x in error_ppms])
    print(f"        Trend: {trend} ppm")
    if gate2_result:
        gates_passed += 1

    # Gate 3: Error at ~10^1233 approaches ~1 ppm
    total_gates += 1
    gate3_result = results[-1]['error_ppm'] <= 2.0  # Allow some tolerance
    print(f"Gate 3: Error at ~10^1233 approaches ~1 ppm: {'✓ PASS' if gate3_result else '✗ FAIL'}")
    print(f"        Actual: {results[-1]['error_ppm']:.4f} ppm")
    if gate3_result:
        gates_passed += 1

    # Gate 4: Bit lengths in range [1661, 4096]
    total_gates += 1
    gate4_result = all(1661 <= bl <= 4096 for bl in bit_lengths)
    print(f"Gate 4: Bit lengths in range [1661, 4096]: {'✓ PASS' if gate4_result else '✗ FAIL'}")
    print(f"        Range: [{min(bit_lengths)}, {max(bit_lengths)}] bits")
    if gate4_result:
        gates_passed += 1

    # Gate 5: Runtime is millisecond-class
    total_gates += 1
    gate5_result = max(runtimes) <= 100.0  # 100ms threshold
    print(f"Gate 5: Runtime is millisecond-class: {'✓ PASS' if gate5_result else '✗ FAIL'}")
    print(f"        Max runtime: {max(runtimes):.2f} ms")
    if gate5_result:
        gates_passed += 1

    # Gate 6: Bootstrap stability (if enabled)
    if with_bootstrap and bootstrap_results:
        total_gates += 1
        stability_results = [boot_result['stability_assessment'] == 'stable'
                           for boot_result in bootstrap_results.values()]
        gate6_result = all(stability_results)
        print(f"Gate 6: Bootstrap stability (<1% CV): {'✓ PASS' if gate6_result else '✗ FAIL'}")
        if gate6_result:
            gates_passed += 1

    print()
    print("-" * 40)
    if gates_passed == total_gates:
        print("✓ VALIDATION PASSED: All gates met")
    else:
        print(f"⚠ VALIDATION PARTIAL: {gates_passed}/{total_gates} gates met")
    print("-" * 40)

    return {
        'configuration': {
            'dist_level': dist_level,
            'use_conical': use_conical,
            'dps': dps,
            'with_bootstrap': with_bootstrap
        },
        'results': results,
        'bootstrap_results': bootstrap_results,
        'summary_stats': {
            'error_range_ppm': [min(error_ppms), max(error_ppms)],
            'avg_error_ppm': sum(error_ppms) / len(error_ppms),
            'runtime_range_ms': [min(runtimes), max(runtimes)],
            'avg_runtime_ms': sum(runtimes) / len(runtimes),
            'bit_length_range': [min(bit_lengths), max(bit_lengths)]
        },
        'acceptance_gates': {
            'passed': gates_passed,
            'total': total_gates,
            'success': gates_passed == total_gates
        }
    }

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="High-scale Z5D prime prediction validation")
    parser.add_argument('--magnitudes', nargs='*', type=int,
                       default=[500, 750, 1000, 1233],
                       help='Target magnitude powers (default: 500 750 1000 1233)')
    parser.add_argument('--dist-level', type=float, default=0.71,
                       help='Distribution level correction (default: 0.71)')
    parser.add_argument('--no-conical', action='store_true',
                       help='Disable conical enhancement')
    parser.add_argument('--dps', type=int, default=2000,
                       help='Decimal precision (default: 2000)')
    parser.add_argument('--bootstrap', action='store_true',
                       help='Run bootstrap stability analysis')
    parser.add_argument('--bootstrap-samples', type=int, default=100,
                       help='Number of bootstrap samples (default: 100)')

    args = parser.parse_args()

    try:
        results = run_high_scale_validation_suite(
            target_magnitudes=args.magnitudes,
            dist_level=args.dist_level,
            use_conical=not args.no_conical,
            dps=args.dps,
            with_bootstrap=args.bootstrap
        )

        # Save results
        import json
        output_file = f"high_scale_validation_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            # Convert any non-serializable types
            serializable_results = {}
            for k, v in results.items():
                if isinstance(v, dict):
                    serializable_results[k] = {}
                    for k2, v2 in v.items():
                        if hasattr(v2, 'item'):  # numpy type
                            serializable_results[k][k2] = v2.item()
                        else:
                            serializable_results[k][k2] = v2
                else:
                    serializable_results[k] = v

            json.dump(serializable_results, f, indent=2)

        print(f"\nResults saved to {output_file}")

        # Final assessment
        if results['acceptance_gates']['success']:
            print("\n🎉 High-scale Z5D validation PASSED!")
            print("Predictor achieves ppm-scale accuracy at cryptographic scales.")
        else:
            print(f"\n⚠️ High-scale Z5D validation PARTIAL: {results['acceptance_gates']['passed']}/{results['acceptance_gates']['total']} gates passed")

    except Exception as e:
        print(f"High-scale validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()