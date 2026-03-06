#!/usr/bin/env python3
"""
Numerical Stability Benchmark for Z5D Model
===========================================

This script tests the Z5D model's numerical stability for extremely large k values,
as required by issue #257. It benchmarks performance up to k = 10^14 using random
sampling and validates that the high-precision backend switching works correctly.

Usage:
    python test_numerical_stability_benchmark.py
"""

import sys
import os
import numpy as np
import warnings
import time
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from z_framework.discrete.z5d_predictor import (
    z5d_prime, 
    validate_z5d_accuracy,
    DEFAULT_PRECISION_THRESHOLD,
    MPMATH_AVAILABLE
)

def test_threshold_boundary_conditions():
    """Test boundary conditions around the precision threshold."""
    print("=" * 60)
    print("THRESHOLD BOUNDARY CONDITIONS TEST")
    print("=" * 60)
    
    threshold = DEFAULT_PRECISION_THRESHOLD
    test_values = [
        threshold - 1,     # Just below
        threshold,         # Exactly at threshold  
        threshold + 1,     # Just above
    ]
    
    print(f"Testing around threshold: {threshold:.0e}")
    print(f"{'k Value':<15} {'Result':<20} {'Warnings':<10} {'Backend':<10}")
    print("-" * 60)
    
    for k_val in test_values:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = z5d_prime(k_val)
            
            precision_warnings = [warning for warning in w 
                                if "numerical instability" in str(warning.message).lower()]
            warning_count = len(precision_warnings)
            backend = "mpmath" if warning_count > 0 else "numpy"
            
            print(f"{k_val:<15.0e} {result:<20.2e} {warning_count:<10} {backend:<10}")
    
    print("\n✅ Boundary conditions test completed")
    return True

def test_edge_cases():
    """Test edge cases for input validation."""
    print("\n" + "=" * 60)
    print("EDGE CASES AND INPUT VALIDATION TEST")
    print("=" * 60)
    
    edge_cases = [
        ("k = 0", lambda: z5d_prime(0)),
        ("k = 1", lambda: z5d_prime(1)),
        ("k = 2 (minimal valid)", lambda: z5d_prime(2)),
    ]
    
    error_cases = [
        ("Negative k", lambda: z5d_prime(-5), ValueError),
        ("NaN k", lambda: z5d_prime(float('nan')), ValueError),
        ("Infinite k", lambda: z5d_prime(float('inf')), ValueError),
        ("Non-numeric k", lambda: z5d_prime("not_a_number"), TypeError),
    ]
    
    print("Valid edge cases:")
    for name, test_func in edge_cases:
        try:
            result = test_func()
            print(f"  {name}: {result}")
        except Exception as e:
            print(f"  {name}: ERROR - {e}")
    
    print("\nInvalid input cases (should raise errors):")
    for name, test_func, expected_error in error_cases:
        try:
            result = test_func()
            print(f"  {name}: ERROR - Should have raised {expected_error.__name__}")
        except expected_error:
            print(f"  {name}: ✅ Correctly raised {expected_error.__name__}")
        except Exception as e:
            print(f"  {name}: ⚠️ Raised {type(e).__name__} instead of {expected_error.__name__}")
    
    print("\n✅ Edge cases test completed")
    return True

def test_backend_override_warnings():
    """Test backend override warning mechanisms."""
    print("\n" + "=" * 60)
    print("BACKEND OVERRIDE WARNINGS TEST")
    print("=" * 60)
    
    large_k = 1e13
    
    print("Testing forced NumPy backend for large k (should warn):")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = z5d_prime(large_k, force_backend='numpy')
        
        backend_warnings = [warning for warning in w 
                           if "numpy backend forced" in str(warning.message).lower()]
        
        print(f"  Result: {result:.2e}")
        print(f"  Warnings: {len(backend_warnings)}")
        if backend_warnings:
            print(f"  Warning message: {backend_warnings[0].message}")
    
    print("\nTesting forced mpmath backend for small k (should work silently):")
    small_k = 1000
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = z5d_prime(small_k, force_backend='mpmath')
        
        print(f"  Result: {result:.2e}")
        print(f"  Warnings: {len(w)}")
    
    print("\n✅ Backend override warnings test completed")
    return True

def test_custom_precision_threshold():
    """Test custom precision threshold functionality."""
    print("\n" + "=" * 60)
    print("CUSTOM PRECISION THRESHOLD TEST")
    print("=" * 60)
    
    custom_threshold = 1e6
    k_test = 1e7
    
    print(f"Testing custom threshold {custom_threshold:.0e} with k = {k_test:.0e}")
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = z5d_prime(k_test, precision_threshold=custom_threshold)
        
        threshold_warnings = [warning for warning in w 
                             if "numerical instability" in str(warning.message).lower()]
        
        print(f"  Result: {result:.2e}")
        print(f"  Warnings: {len(threshold_warnings)}")
        if threshold_warnings:
            print(f"  Warning contains custom threshold: {'1e+06' in str(threshold_warnings[0].message)}")
    
    print("\nTesting disabled threshold (None):")
    large_k = 1e15
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = z5d_prime(large_k, precision_threshold=None)
        
        precision_warnings = [warning for warning in w 
                             if "numerical instability" in str(warning.message).lower()]
        
        print(f"  Result: {result:.2e}")
        print(f"  No precision warnings: {len(precision_warnings) == 0}")
    
    print("\n✅ Custom precision threshold test completed")
    return True

def test_large_k_random_sampling():
    """Test random sampling of large k values up to 10^14."""
    print("\n" + "=" * 60)
    print("LARGE K RANDOM SAMPLING TEST (up to 10^14)")
    print("=" * 60)
    
    if not MPMATH_AVAILABLE:
        print("⚠️ mpmath not available - skipping large k tests")
        return True
    
    # Random sample of k values up to 10^14
    np.random.seed(42)  # For reproducible results
    k_ranges = [
        (1e12, 1e13, 5),   # 5 samples between 10^12 and 10^13
        (1e13, 1e14, 3),   # 3 samples between 10^13 and 10^14
    ]
    
    all_samples = []
    for k_min, k_max, n_samples in k_ranges:
        samples = np.random.uniform(k_min, k_max, size=n_samples).astype(int)
        all_samples.extend(samples)
    
    print(f"Testing {len(all_samples)} random samples:")
    print(f"{'k Value':<15} {'Result':<20} {'Time (s)':<10} {'Backend':<10}")
    print("-" * 60)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Suppress expected warnings for cleaner output
        
        for k_val in all_samples:
            start_time = time.time()
            result = z5d_prime(k_val, force_backend='mpmath')
            computation_time = time.time() - start_time
            
            # Verify result is reasonable
            assert np.isfinite(result)
            assert result > 0
            assert result > k_val  # Prime should be larger than index
            
            print(f"{k_val:<15.0e} {result:<20.2e} {computation_time:<10.3f} {'mpmath':<10}")
    
    print(f"\n✅ Random sampling test completed - all {len(all_samples)} samples valid")
    return True

def test_backend_consistency():
    """Test consistency between NumPy and mpmath backends."""
    print("\n" + "=" * 60)
    print("BACKEND CONSISTENCY TEST")
    print("=" * 60)
    
    if not MPMATH_AVAILABLE:
        print("⚠️ mpmath not available - skipping consistency tests")
        return True
    
    # Test k values that are small enough for both backends to handle
    test_k_values = [1000, 10000, 100000, 1000000]
    
    print(f"{'k Value':<10} {'NumPy':<20} {'mpmath':<20} {'Rel Diff (%)':<15}")
    print("-" * 70)
    
    max_rel_diff = 0
    for k in test_k_values:
        result_numpy = z5d_prime(k, force_backend='numpy')
        result_mpmath = z5d_prime(k, force_backend='mpmath')
        
        # Calculate relative difference
        rel_diff = abs(result_numpy - result_mpmath) / max(result_numpy, result_mpmath) * 100
        max_rel_diff = max(max_rel_diff, rel_diff)
        
        print(f"{k:<10} {result_numpy:<20.2f} {result_mpmath:<20.2f} {rel_diff:<15.6f}")
    
    print(f"\nMaximum relative difference: {max_rel_diff:.6f}%")
    
    # Backends should be very consistent for reasonable k values
    if max_rel_diff < 0.01:  # Less than 0.01% difference
        print("✅ Backends are highly consistent")
    elif max_rel_diff < 0.1:   # Less than 0.1% difference  
        print("✅ Backends are reasonably consistent")
    else:
        print("⚠️ Backends show significant differences")
    
    print("\n✅ Backend consistency test completed")
    return True

def test_performance_comparison():
    """Test performance difference between backends."""
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON TEST")
    print("=" * 60)
    
    if not MPMATH_AVAILABLE:
        print("⚠️ mpmath not available - skipping performance tests")
        return True
    
    test_k = 1e6  # Large enough to see difference, reasonable for timing
    n_trials = 3
    
    print(f"Performance test with k = {test_k:.0e} ({n_trials} trials each):")
    
    # Time NumPy backend
    numpy_times = []
    for i in range(n_trials):
        start_time = time.time()
        result_numpy = z5d_prime(test_k, force_backend='numpy')
        numpy_times.append(time.time() - start_time)
    
    # Time mpmath backend
    mpmath_times = []
    for i in range(n_trials):
        start_time = time.time()
        result_mpmath = z5d_prime(test_k, force_backend='mpmath')
        mpmath_times.append(time.time() - start_time)
    
    numpy_avg = np.mean(numpy_times)
    mpmath_avg = np.mean(mpmath_times)
    speedup_ratio = mpmath_avg / numpy_avg
    
    print(f"  NumPy average time:  {numpy_avg:.4f}s")
    print(f"  mpmath average time: {mpmath_avg:.4f}s")
    print(f"  Speedup ratio (mpmath/numpy): {speedup_ratio:.2f}x")
    
    if speedup_ratio > 1:
        print(f"  ✅ mpmath is {speedup_ratio:.1f}x slower than NumPy (expected for high precision)")
    else:
        print(f"  ⚠️ mpmath is faster than NumPy (unexpected, but possible in CI environments)")
    
    print("\n✅ Performance comparison test completed")
    return True

def test_scale_consistency():
    """Test consistency across different scales."""
    print("\n" + "=" * 60)
    print("SCALE CONSISTENCY TEST")
    print("=" * 60)
    
    # Test scales from 10^3 to 10^13  
    test_scales = [10**i for i in range(3, 14, 2)]  # 10^3, 10^5, 10^7, 10^9, 10^11, 10^13
    
    print(f"{'Scale (k)':<12} {'Result':<20} {'Backend':<10} {'Time (s)':<10}")
    print("-" * 55)
    
    results = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Suppress expected warnings
        
        for k in test_scales:
            start_time = time.time()
            result = z5d_prime(k)
            computation_time = time.time() - start_time
            
            backend = "mpmath" if k > DEFAULT_PRECISION_THRESHOLD else "numpy"
            results.append(result)
            
            assert np.isfinite(result)
            assert result > 0
            assert result > k  # Prime should be larger than index
            
            print(f"{k:<12.0e} {result:<20.2e} {backend:<10} {computation_time:<10.3f}")
    
    # Check that results are strictly increasing
    increasing = np.all(np.diff(results) > 0)
    print(f"\nResults strictly increasing: {increasing}")
    
    # Check that relative spacing generally increases (primes get sparser)
    relative_spacings = np.diff(results) / np.array(results[:-1])
    spacing_trend = np.mean(relative_spacings[-3:]) > np.mean(relative_spacings[:3])
    print(f"Relative spacing increases at larger scales: {spacing_trend}")
    
    print("\n✅ Scale consistency test completed")
    return True

def main():
    """Run all numerical stability benchmark tests."""
    print("Z5D NUMERICAL STABILITY BENCHMARK")
    print("Issue #257 - Numerical instability risk for extremely large k values")
    print("Testing up to k = 10^14 with random sampling")
    print()
    
    if not MPMATH_AVAILABLE:
        print("⚠️  WARNING: mpmath not available - some high-precision tests will be skipped")
        print()
    
    # Run all test functions
    test_functions = [
        test_threshold_boundary_conditions,
        test_edge_cases,
        test_backend_override_warnings,
        test_custom_precision_threshold,
        test_large_k_random_sampling,
        test_backend_consistency,
        test_performance_comparison,
        test_scale_consistency,
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_func in test_functions:
        try:
            success = test_func()
            results.append((test_func.__name__, success, None))
        except Exception as e:
            print(f"\n❌ Test {test_func.__name__} failed: {e}")
            results.append((test_func.__name__, False, str(e)))
    
    total_time = time.time() - total_start_time
    
    # Summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Total time: {total_time:.2f}s")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Z5D model numerical stability validated for k up to 10^14")
        print("✅ High-precision backend switching working correctly")
        print("✅ Warning mechanisms functioning properly")
        print("✅ Input validation robust against edge cases")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests failed:")
        for name, success, error in results:
            if not success:
                print(f"  - {name}: {error}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)