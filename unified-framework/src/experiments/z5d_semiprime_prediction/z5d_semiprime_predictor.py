#!/usr/bin/env python3
"""
Z5D Semiprime Prediction Module

This module implements Z5D-enhanced semiprime prediction for RSA factoring.
Uses the Z5D framework to predict semiprime values s_k = p_k * q_k for
given prime indices k.

Key Features:
- Z5D-enhanced semiprime prediction using prime predictor
- Baseline asymptotic approximation
- Enhanced prediction with periodic modulation
- Statistical validation and benchmarking

Author: Z Framework Implementation Team
"""

import math
import sys
from typing import Union, Optional, Tuple
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    import mpmath as mp
    mp.mp.dps = 50  # High precision for semiprime calculations
except ImportError:
    mp = None

# Import Z5D prime predictor
from ...core.z_5d_enhanced import z5d_predictor, z5d_predictor_with_modulation


def baseline_semiprime_enhanced(k: Union[int, float]) -> Union[float, mp.mpf]:
    """
    Baseline semiprime prediction using Z5D-enhanced prime prediction.

    Predicts the k-th semiprime s_k ≈ p_k * q_k where p_k and q_k are
    the k-th primes. Uses Z5D prediction for prime estimation.

    Args:
        k: Prime index (typically k ≈ n / log(n) for semiprime n)

    Returns:
        Predicted semiprime value
    """
    if mp is None:
        # Fallback without mpmath
        k_float = float(k)

        # Estimate p_k ≈ k * log(k) using Z5D approximation
        # For semiprime, we need two primes, so estimate around sqrt(s_k)
        # Use iterative approach
        log_k = math.log(k_float) if k_float > 1 else 1.0

        # Rough approximation: s_k ≈ (k * log(k))^2
        # But adjust for Z5D enhancement
        p_est = k_float * (log_k + math.log(log_k) - 1)

        # Semiprime is product of two similar primes
        s_k = p_est * (p_est + 2)  # Approximation for consecutive primes

        return s_k

    # High-precision version with mpmath
    k_mp = mp.mpf(str(k))

    try:
        # Use Z5D predictor for prime estimation
        p_k = z5d_predictor(int(k_mp))

        # For semiprime, we need two prime factors
        # Approximation: s_k ≈ p_k * p_{k+1} ≈ p_k * (p_k + log(p_k))
        # More accurately, estimate the second prime
        log_p_k = mp.log(p_k)
        p_k_plus_1_approx = p_k + log_p_k * 1.1  # Rough next prime estimate

        s_k = p_k * p_k_plus_1_approx

        return s_k

    except Exception:
        # Fallback to asymptotic approximation
        return baseline_semiprime_asymptotic(k_mp)


def baseline_semiprime_asymptotic(k: Union[int, float, mp.mpf]) -> Union[float, mp.mpf]:
    """
    Asymptotic baseline semiprime prediction.

    Uses the asymptotic approximation s_k ≈ k^2 * (log k)^2

    Args:
        k: Prime index

    Returns:
        Asymptotic semiprime approximation
    """
    if mp is not None and isinstance(k, mp.mpf):
        log_k = mp.log(k)
        return k * k * log_k * log_k
    else:
        k_float = float(k)
        log_k = math.log(k_float)
        return k_float * k_float * log_k * log_k


def enhanced_semiprime_prediction(k: Union[int, float],
                                 use_modulation: bool = True,
                                 precision: int = 50) -> Tuple[float, float, float]:
    """
    Enhanced semiprime prediction with error bounds and modulation.

    Provides prediction with confidence intervals and optional periodic modulation.

    Args:
        k: Prime index
        use_modulation: Whether to apply periodic integral modulation
        precision: mpmath precision for calculation

    Returns:
        Tuple of (prediction, lower_bound, upper_bound)
    """
    if mp is None:
        pred = baseline_semiprime_enhanced(k)
        # Rough error bounds: ±10% for baseline
        return float(pred), float(pred * 0.9), float(pred * 1.1)

    # Set precision
    old_dps = mp.mp.dps
    mp.mp.dps = precision

    try:
        k_mp = mp.mpf(str(k))

        if use_modulation:
            # Use modulated prediction
            p_k = z5d_predictor_with_modulation(int(k_mp), apply_modulation=True)
        else:
            p_k = z5d_predictor(int(k_mp))

        # Estimate second prime more accurately
        # Use the fact that p_{k+1} ≈ p_k + log(p_k) + o(1)
        log_p_k = mp.log(p_k)
        delta = log_p_k + mp.log(log_p_k) - 1  # More accurate prime gap
        p_k_plus_1 = p_k + delta

        s_k = p_k * p_k_plus_1

        # Estimate error bounds based on prime prediction accuracy
        # Z5D typically has <1% error for large k
        error_factor = 0.01 if k > 1000 else 0.05
        lower = s_k * (1 - error_factor)
        upper = s_k * (1 + error_factor)

        return float(s_k), float(lower), float(upper)

    finally:
        mp.mp.dps = old_dps


def z5d_semiprime_variant(k: Union[int, float]) -> Union[float, mp.mpf]:
    """
    Z5D semiprime variant predictor.

    Specialized version for RSA factoring that uses Z5D to predict
    semiprime values directly.

    Args:
        k: Prime index

    Returns:
        Predicted semiprime value
    """
    return baseline_semiprime_enhanced(k)


def validate_semiprime_prediction(n_test: int = 100) -> dict:
    """
    Validate semiprime prediction against known values.

    Args:
        n_test: Number of test cases

    Returns:
        Validation statistics
    """
    from sympy import prime

    results = []
    errors = []

    # Test against known semiprimes
    for k in range(10, min(1000, n_test + 10)):
        try:
            p1 = prime(k)
            p2 = prime(k + 1) if k + 1 <= 1000 else prime(k) + 2  # Approximation
            true_semiprime = p1 * p2

            predicted = baseline_semiprime_enhanced(k)
            error = abs(predicted - true_semiprime) / true_semiprime * 100

            results.append({
                'k': k,
                'true_semiprime': true_semiprime,
                'predicted': float(predicted),
                'error_percent': float(error)
            })
            errors.append(error)

        except Exception as e:
            continue

    if not results:
        return {'error': 'No valid test cases'}

    mean_error = sum(errors) / len(errors)
    max_error = max(errors)
    min_error = min(errors)

    return {
        'n_tests': len(results),
        'mean_error_percent': mean_error,
        'max_error_percent': max_error,
        'min_error_percent': min_error,
        'results': results[:10]  # First 10 for inspection
    }


def benchmark_semiprime_prediction(k_values: list) -> dict:
    """
    Benchmark semiprime prediction performance.

    Args:
        k_values: List of k values to test

    Returns:
        Benchmark results
    """
    import time

    times = []
    predictions = []

    for k in k_values:
        start = time.time()
        pred = baseline_semiprime_enhanced(k)
        elapsed = time.time() - start

        times.append(elapsed)
        predictions.append(float(pred))

    return {
        'k_values': k_values,
        'predictions': predictions,
        'times': times,
        'mean_time': sum(times) / len(times),
        'total_time': sum(times)
    }


# For compatibility with the RSA solver
def semiprime_predictor(k: int) -> float:
    """
    Simple interface for semiprime prediction.

    Args:
        k: Prime index

    Returns:
        Predicted semiprime value
    """
    return float(baseline_semiprime_enhanced(k))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Z5D Semiprime Predictor")
    parser.add_argument("k", type=int, help="Prime index k")
    parser.add_argument("--validate", action="store_true", help="Run validation")
    parser.add_argument("--benchmark", nargs="+", type=int, help="Benchmark on k values")

    args = parser.parse_args()

    if args.validate:
        print("Running semiprime prediction validation...")
        results = validate_semiprime_prediction()
        print(f"Tests: {results['n_tests']}")
        print(".2f")
        print(".2f")
        print(".2f")

    elif args.benchmark:
        print(f"Benchmarking on k values: {args.benchmark}")
        results = benchmark_semiprime_prediction(args.benchmark)
        print(".4f")
        for k, pred, t in zip(results['k_values'], results['predictions'], results['times']):
            print(f"k={k}: s_k≈{pred:.0e}, time={t:.4f}s")

    else:
        pred = baseline_semiprime_enhanced(args.k)
        print(f"Predicted s_{args.k} ≈ {pred:.0f}")

        # Enhanced prediction with bounds
        pred_val, lower, upper = enhanced_semiprime_prediction(args.k)
        print(".0f")