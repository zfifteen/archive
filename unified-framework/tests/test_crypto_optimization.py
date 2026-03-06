#!/usr/bin/env python3
"""
Test script for Z5D cryptographic scale optimization.

This script validates the implementation of cryptographic scale optimization
for the Z5D predictor, demonstrating reductions in relative error at RSA scales.
"""

import sys
import os
import numpy as np
import time
import warnings

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from z_framework.discrete.z5d_predictor import (
        z5d_prime,
        z5d_prime_crypto_optimized,
        benchmark_cryptographic_accuracy
    )
    from z_framework.discrete.z5d_rsa_opt import (
        run_rsa_optimization_demo,
        validate_cryptographic_accuracy
    )
    print("✓ Successfully imported Z5D cryptographic optimization modules")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    raise

def test_basic_optimization():
    """Test basic optimization functionality."""
    print("\n=== Testing Basic RSA Optimization ===")
    
    try:
        # Run RSA-1024 scale optimization
        result = run_rsa_optimization_demo('rsa_1024', num_samples=10)
        
        print(f"Test preset: {result['preset']}")
        print(f"K range: {result['k_range']}")
        print(f"Number of samples: {result['num_samples']}")
        
        # Check optimization results
        opt = result['optimization']
        print(f"Optimization success: {opt['optimization_success']}")
        print(f"Mean relative error: {opt['mean_relative_error']:.6f}")
        print(f"Max relative error: {opt['max_relative_error']:.6f}")
        
        # Check validation results
        val = result['validation']
        print(f"Validation pass rate: {val['pass_rate']:.2%}")
        print(f"Meets threshold: {val['meets_threshold']}")
        
        return opt['mean_relative_error'] < 0.01  # Sub-1% error target
        
    except Exception as e:
        print(f"✗ Basic optimization test failed: {e}")
        return False

def test_crypto_optimized_function():
    """Test the crypto-optimized Z5D function."""
    print("\n=== Testing Crypto-Optimized Z5D Function ===")
    
    try:
        # Test single value prediction
        k_test = 5000
        result_standard = z5d_prime(k_test, auto_calibrate=True)
        result_crypto = z5d_prime_crypto_optimized(k_test, 'rsa_1024', auto_optimize=False)
        
        print(f"k = {k_test}")
        print(f"Standard Z5D: {result_standard:.2f}")
        print(f"Crypto Z5D: {result_crypto:.2f}")
        print(f"Difference: {abs(result_crypto - result_standard):.2f}")
        
        # Test array prediction
        k_array = np.linspace(1000, 10000, 5)
        results_array = z5d_prime_crypto_optimized(k_array, 'rsa_1024', auto_optimize=False)
        
        print(f"Array test - k values: {k_array}")
        print(f"Array results: {results_array}")
        
        return len(results_array) == len(k_array) and all(r > 0 for r in results_array)
        
    except Exception as e:
        print(f"✗ Crypto-optimized function test failed: {e}")
        return False

def test_benchmark_comparison():
    """Test benchmarking against multiple methods."""
    print("\n=== Testing Benchmark Comparison ===")
    
    try:
        # Run comprehensive benchmark
        benchmark = benchmark_cryptographic_accuracy(
            'rsa_1024', 
            num_samples=15,
            comparison_methods=['standard_z5d', 'optimized_z5d']
        )
        
        print(f"Benchmark preset: {benchmark['test_preset']}")
        print(f"K range: {benchmark['k_range']}")
        
        for method, results in benchmark['methods'].items():
            print(f"\n{method.upper()}:")
            print(f"  Description: {results['description']}")
            print(f"  Mean error: {results['mean_relative_error']:.6f}")
            print(f"  Sub-1% rate: {results['sub_1_percent_rate']:.2%}")
            print(f"  Sub-0.1% rate: {results['sub_0_1_percent_rate']:.2%}")
        
        # Check if optimized method performs better
        standard_error = benchmark['methods']['standard_z5d']['mean_relative_error']
        optimized_error = benchmark['methods']['optimized_z5d']['mean_relative_error']
        improvement = (standard_error - optimized_error) / standard_error
        
        print(f"\nImprovement: {improvement:.2%}")
        
        return improvement > 0  # Optimized should be better
        
    except Exception as e:
        print(f"✗ Benchmark comparison test failed: {e}")
        return False

def test_parameter_optimization():
    """Test parameter optimization accuracy."""
    print("\n=== Testing Parameter Optimization ===")
    
    try:
        from z_framework.discrete.z5d_rsa_opt import (
            generate_rsa_test_data,
            optimize_z5d_parameters
        )
        
        # Generate test data
        k_values, true_primes = generate_rsa_test_data(1000, 5000, 10)
        
        # Optimize parameters
        opt_result = optimize_z5d_parameters(k_values, true_primes)
        
        print(f"Optimization success: {opt_result['optimization_success']}")
        print(f"Optimal parameters:")
        print(f"  c = {opt_result['c']:.6f}")
        print(f"  k_star = {opt_result['k_star']:.6f}")
        print(f"  kappa_geo = {opt_result['kappa_geo']:.6f}")
        print(f"  beta = {opt_result['beta']:.6f}")
        print(f"Mean relative error: {opt_result['mean_relative_error']:.6f}")
        
        return opt_result['optimization_success'] and opt_result['mean_relative_error'] < 0.05
        
    except Exception as e:
        print(f"✗ Parameter optimization test failed: {e}")
        return False

def performance_timing_test():
    """Test performance timing for cryptographic scales."""
    print("\n=== Performance Timing Test ===")
    
    try:
        k_test = 10000
        
        # Time standard Z5D
        start_time = time.time()
        for _ in range(10):
            result_standard = z5d_prime(k_test, auto_calibrate=True)
        standard_time = (time.time() - start_time) / 10
        
        # Time crypto Z5D  
        start_time = time.time()
        for _ in range(10):
            result_crypto = z5d_prime_crypto_optimized(k_test, 'rsa_1024', auto_optimize=False)
        crypto_time = (time.time() - start_time) / 10
        
        print(f"Standard Z5D average time: {standard_time:.4f}s")
        print(f"Crypto Z5D average time: {crypto_time:.4f}s")
        print(f"Performance ratio: {crypto_time/standard_time:.2f}x")
        
        return True
        
    except Exception as e:
        print(f"✗ Performance timing test failed: {e}")
        return False

def main():
    """Run all tests and report results."""
    print("Z5D Cryptographic Scale Optimization Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Optimization", test_basic_optimization),
        ("Crypto-Optimized Function", test_crypto_optimized_function),
        ("Benchmark Comparison", test_benchmark_comparison),
        ("Parameter Optimization", test_parameter_optimization),
        ("Performance Timing", performance_timing_test),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Cryptographic optimization is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)