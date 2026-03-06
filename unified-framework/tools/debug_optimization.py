#!/usr/bin/env python3
"""
Debug script to understand optimization issues.
"""
import sys
import os
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from z_framework.discrete.z5d_predictor import z5d_prime
from z_framework.discrete.z5d_rsa_opt import (
    generate_rsa_test_data,
    optimize_z5d_parameters,
    z5d_prime_optimized,
    CRYPTO_SCALE_PRESETS
)

def debug_optimization():
    """Debug the optimization process step by step."""
    print("=== Debugging Z5D Optimization ===")
    
    # Generate small test dataset
    k_values, true_primes = generate_rsa_test_data(10000, 50000, 5)
    print(f"Test k values: {k_values}")
    print(f"True primes: {true_primes}")
    
    # Test standard Z5D predictions
    standard_predictions = [z5d_prime(k, auto_calibrate=True) for k in k_values]
    print(f"Standard Z5D predictions: {standard_predictions}")
    
    # Calculate standard errors
    standard_errors = [abs(pred - true) / true for pred, true in zip(standard_predictions, true_primes)]
    print(f"Standard Z5D errors: {standard_errors}")
    print(f"Standard Z5D mean error: {np.mean(standard_errors):.6f}")
    
    # Test optimization with default parameters
    default_params = [-0.00247, 0.04449, 1.0, 0.1]
    print(f"\nTesting with default parameters: {default_params}")
    
    default_predictions = [z5d_prime_optimized(k, default_params) for k in k_values]
    print(f"Default optimized predictions: {default_predictions}")
    
    default_opt_errors = [abs(pred - true) / true for pred, true in zip(default_predictions, true_primes)]
    print(f"Default optimized errors: {default_opt_errors}")
    print(f"Default optimized mean error: {np.mean(default_opt_errors):.6f}")
    
    # Run actual optimization
    print(f"\n=== Running Parameter Optimization ===")
    opt_result = optimize_z5d_parameters(k_values, true_primes)
    print(f"Optimization success: {opt_result['optimization_success']}")
    print(f"Optimal parameters: {opt_result['optimal_params']}")
    print(f"Optimized mean error: {opt_result['mean_relative_error']:.6f}")
    
    # Compare errors
    print(f"\n=== Error Comparison ===")
    print(f"Standard Z5D mean error: {np.mean(standard_errors):.6f}")
    print(f"Default params mean error: {np.mean(default_opt_errors):.6f}")
    print(f"Optimized params mean error: {opt_result['mean_relative_error']:.6f}")
    
    improvement_vs_standard = (np.mean(standard_errors) - opt_result['mean_relative_error']) / np.mean(standard_errors)
    print(f"Improvement vs standard: {improvement_vs_standard:.2%}")

if __name__ == "__main__":
    debug_optimization()