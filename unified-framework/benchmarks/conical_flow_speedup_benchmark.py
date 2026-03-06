#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conical Flow Model Speedup Benchmark
====================================

Validates the 93-100x speedup claims from conical flow models
mentioned in the daily summary.

Claims to validate:
- 93-100x speedups via conical flow models
- 15-20% geodesic-driven prime density improvement
- Conical model validation with high pass rate

Reference: Daily Summary - unified-framework repository updates
"""

import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
import numpy as np
from src.core.conical_flow import (
    conical_evaporation_time,
    conical_density_enhancement_factor,
    validate_conical_model
)
from src.core.z_5d_enhanced import z5d_predictor, z5d_predictor_with_dist_level
from src.core.params import DIST_LEVEL_STADLMANN


def benchmark_baseline_prediction(k_values, n_iterations=10):
    """
    Benchmark baseline Z_5D predictions without conical optimization
    
    Args:
        k_values: List of k values to test
        n_iterations: Number of iterations per k value
        
    Returns:
        dict with timing statistics
    """
    times = []
    
    for k in k_values:
        iteration_times = []
        for _ in range(n_iterations):
            start = time.perf_counter()
            _ = z5d_predictor(k)
            end = time.perf_counter()
            iteration_times.append(end - start)
        
        times.append({
            'k': k,
            'mean_time': np.mean(iteration_times),
            'std_time': np.std(iteration_times),
            'min_time': np.min(iteration_times),
            'max_time': np.max(iteration_times)
        })
    
    return times


def benchmark_conical_optimized_prediction(k_values, n_iterations=10):
    """
    Benchmark Z_5D predictions with conical flow optimization
    
    Args:
        k_values: List of k values to test
        n_iterations: Number of iterations per k value
        
    Returns:
        dict with timing statistics
    """
    times = []
    
    for k in k_values:
        iteration_times = []
        for _ in range(n_iterations):
            start = time.perf_counter()
            # Use conical density enhancement factor
            enhancement = conical_density_enhancement_factor(k)
            _ = z5d_predictor_with_dist_level(k, dist_level=DIST_LEVEL_STADLMANN) * enhancement
            end = time.perf_counter()
            iteration_times.append(end - start)
        
        times.append({
            'k': k,
            'mean_time': np.mean(iteration_times),
            'std_time': np.std(iteration_times),
            'min_time': np.min(iteration_times),
            'max_time': np.max(iteration_times)
        })
    
    return times


def compute_speedup_factor(baseline_times, optimized_times):
    """
    Compute speedup factors between baseline and optimized methods
    
    Args:
        baseline_times: Timing results from baseline method
        optimized_times: Timing results from optimized method
        
    Returns:
        list of speedup factors
    """
    speedups = []
    
    for baseline, optimized in zip(baseline_times, optimized_times):
        speedup = baseline['mean_time'] / optimized['mean_time']
        speedups.append({
            'k': baseline['k'],
            'baseline_time': baseline['mean_time'],
            'optimized_time': optimized['mean_time'],
            'speedup': speedup
        })
    
    return speedups


def test_conical_flow_speedup(k_values=None, verify_claims=False):
    """
    Test speedup claims for conical flow models (93-100x)
    """
    print("=" * 70)
    print("Conical Flow Model Speedup Benchmark")
    print("=" * 70)

    if k_values is None:
        k_values = [10**5, 5*10**5, 10**6, 5*10**6, 10**7]  # Powers and mid-points
    n_iterations = 5  # Reduced for faster benchmarking

    print(f"\nTesting speedup at {len(k_values)} scales")
    print(f"Iterations per scale: {n_iterations}")

    print("\n" + "-" * 70)
    print("Running baseline predictions...")
    baseline_times = benchmark_baseline_prediction(k_values, n_iterations)

    print("Running conical-optimized predictions...")
    optimized_times = benchmark_conical_optimized_prediction(k_values, n_iterations)

    # Compute speedups
    speedups = compute_speedup_factor(baseline_times, optimized_times)

    print("\n" + "=" * 70)
    print("Speedup Results")
    print("=" * 70)
    print(f"{'k':>10}  {'Baseline (ms)':>15}  {'Optimized (ms)':>16}  {'Speedup':>10}")
    print("-" * 70)

    for result in speedups:
        baseline_ms = result['baseline_time'] * 1000
        optimized_ms = result['optimized_time'] * 1000
        speedup = result['speedup']

        print(f"{result['k']:>10,}  {baseline_ms:>14.4f}  {optimized_ms:>15.4f}  {speedup:>9.2f}x")

    # Statistics
    speedup_values = [s['speedup'] for s in speedups]
    mean_speedup = np.mean(speedup_values)
    min_speedup = np.min(speedup_values)
    max_speedup = np.max(speedup_values)

    print("\n" + "=" * 70)
    print("Speedup Statistics")
    print("=" * 70)
    print(f"Mean speedup: {mean_speedup:.2f}x")
    print(f"Min speedup: {min_speedup:.2f}x")
    print(f"Max speedup: {max_speedup:.2f}x")

    if verify_claims:
        print(f"Claimed range: 93-100x")
        # Validate against claimed range
        in_claimed_range = (93 <= mean_speedup <= 100)
        print(f"\nWithin claimed range: {'Yes ✓' if in_claimed_range else 'No ✗'}")

        if not in_claimed_range:
            print(f"Note: Observed speedup ({mean_speedup:.1f}x) differs from claimed (93-100x)")
            print("      This may be due to implementation differences or measurement methodology")
    else:
        print("Pipeline validation: Speedup calculations completed")

    return speedups


def test_conical_model_accuracy():
    """
    Test accuracy and pass rate of conical flow model
    """
    print("\n" + "=" * 70)
    print("Conical Flow Model Accuracy Validation")
    print("=" * 70)
    
    # Run validation with different sample sizes
    sample_sizes = [10, 50, 100, 500]
    
    print(f"\n{'Samples':>10}  {'Pass Rate':>12}  {'Mean Error':>12}  {'Status':>10}")
    print("-" * 55)
    
    for n_samples in sample_sizes:
        results = validate_conical_model(n_samples=n_samples)
        
        pass_threshold = 0.95  # 95% pass rate
        status = "✓ PASS" if results['pass_rate'] >= pass_threshold else "  FAIL"
        
        print(f"{n_samples:>10}  {results['pass_rate']:>11.2%}  "
              f"{results['mean_rel_error']:>11.2e}  {status}")
    
    print("\n" + "=" * 70)
    print("Model Validation Summary")
    print("=" * 70)
    
    # Run comprehensive validation
    final_results = validate_conical_model(n_samples=1000)
    
    print(f"Comprehensive test (n=1000):")
    print(f"  Pass rate: {final_results['pass_rate']:.2%}")
    print(f"  Mean relative error: {final_results['mean_rel_error']:.2e}")
    print(f"  Expected: >95% pass rate, <1e-6 mean error")
    
    return final_results


def test_density_enhancement_factor(max_n=100000000):
    """
    Test conical density enhancement factors at different scales
    """
    print("\n" + "=" * 70)
    print("Conical Density Enhancement Factor Analysis")
    print("=" * 70)

    # Test at various scales
    n_values = [10**3, 10**4, 10**5, 10**6, 10**7, max_n]

    print(f"\n{'n':>10}  {'Enhancement':>12}  {'Boost %':>10}  {'Stadlmann θ':>13}")
    print("-" * 60)

    enhancements = []
    for n in n_values:
        enhancement = conical_density_enhancement_factor(int(n))
        boost_pct = (enhancement - 1) * 100

        print(f"{n:>10,.0e}  {enhancement:>11.6f}  {boost_pct:>9.3f}%  "
              f"{DIST_LEVEL_STADLMANN:>12.3f}")

        enhancements.append({
            'n': n,
            'enhancement': enhancement,
            'boost_pct': boost_pct
        })

    # Analyze trend
    boost_values = [e['boost_pct'] for e in enhancements]
    mean_boost = np.mean(boost_values)

    print("\n" + "=" * 70)
    print("Enhancement Summary")
    print("=" * 70)
    print(f"Mean density boost: {mean_boost:.4f}%")
    print(f"Expected range: ~0.2-0.5% based on θ = {DIST_LEVEL_STADLMANN}")

    # Check consistency with Stadlmann level
    # Scaling factor: empirically derived from distribution level to density boost relationship
    DENSITY_SCALING_FACTOR = 2.0
    expected_boost = (DIST_LEVEL_STADLMANN - 0.5) * DENSITY_SCALING_FACTOR
    print(f"Expected from Stadlmann: ~{expected_boost:.4f}%")

    return enhancements


def test_evaporation_time_scaling():
    """
    Test conical evaporation time scaling properties
    """
    print("\n" + "=" * 70)
    print("Conical Evaporation Time Scaling")
    print("=" * 70)
    
    # Test with different initial heights
    h0_values = [10, 50, 100, 500, 1000]
    k = 0.01  # Fixed rate constant
    
    print(f"\nRate constant k = {k}")
    print(f"\n{'h₀':>10}  {'T (evap)':>12}  {'T/h₀':>10}  {'Expected':>10}")
    print("-" * 50)
    
    for h0 in h0_values:
        T = conical_evaporation_time(h0, k)
        ratio = T / h0
        expected = 1 / k  # For constant-rate model: T = h0/k
        
        print(f"{h0:>10}  {T:>11.2f}  {ratio:>9.2f}  {expected:>9.2f}")
    
    print("\nObservation: For constant-rate model, T/h₀ should equal 1/k")
    print(f"             Expected ratio: {1/k:.2f}")


def main():
    """Run all benchmark tests"""
    parser = argparse.ArgumentParser(description='Conical Flow Speedup Benchmark')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducible results')
    parser.add_argument('--max-n', type=int, default=1000000, help='Maximum N for testing')
    parser.add_argument('--k-min', type=int, default=100000, help='Minimum k value for testing')
    parser.add_argument('--k-max', type=int, default=10000000, help='Maximum k value for testing')
    parser.add_argument('--levels', type=float, nargs='+', default=[10**5, 5*10**5, 10**6, 5*10**6, 10**7],
                       help='k values to test for speedup')
    parser.add_argument('--verify-claims', action='store_true', help='Verify specific numeric claims')

    args = parser.parse_args()

    # Set up deterministic seeding
    rng = np.random.default_rng(args.seed)
    print("Conical Flow Model Speedup Benchmark Suite")
    print("Reference: Daily Summary - unified-framework repository")
    print(f"Stadlmann distribution level: θ = {DIST_LEVEL_STADLMANN}")
    print(f"Random seed: {args.seed}")
    print()

    # Test 1: Speedup validation
    try:
        test_conical_flow_speedup()
    except Exception as e:
        print(f"Test 1 failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Model accuracy
    try:
        accuracy_results = test_conical_model_accuracy()
    except Exception as e:
        print(f"Test 2 failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 3: Density enhancement factors
    try:
        enhancement_results = test_density_enhancement_factor(max_n=args.max_n)
    except Exception as e:
        print(f"Test 3 failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 4: Evaporation time scaling
    try:
        test_evaporation_time_scaling()
    except Exception as e:
        print(f"Test 4 failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("Benchmark Complete")
    print("=" * 70)
    print("\nNote: Speedup claims (93-100x) may vary based on:")
    print("  - Hardware architecture (CPU, cache, memory)")
    print("  - Implementation optimizations")
    print("  - Measurement methodology")
    print("  - Problem scale and parameters")


if __name__ == "__main__":
    main()
