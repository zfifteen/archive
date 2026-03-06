#!/usr/bin/env python3
"""
Z_5D Integration Example

This script demonstrates how the Z_5D Prime Enumeration Predictor integrates
with existing prime generation pipelines and geodesic mapping functionality.
"""

import sys
import os
import numpy as np
from sympy import ntheory

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from z_framework.discrete.z5d_predictor import z5d_prime, validate_z5d_accuracy


def demo_basic_usage():
    """Demonstrate basic Z_5D usage."""
    print("=== Basic Z_5D Usage ===")
    
    # Single prediction
    k = 100000
    prediction = z5d_prime(k)
    true_prime = ntheory.prime(k)
    error = abs(prediction - true_prime) / true_prime * 100
    
    print(f"k = {k:,}")
    print(f"Z_5D prediction: {prediction:,.1f}")
    print(f"Actual prime: {true_prime:,}")
    print(f"Relative error: {error:.4f}%")
    
    # Array predictions
    print(f"\nBatch predictions:")
    k_values = [1000, 10000, 100000]
    predictions = z5d_prime(k_values)
    
    for k, pred in zip(k_values, predictions):
        true_p = ntheory.prime(k)
        err = abs(pred - true_p) / true_p * 100
        print(f"  k={k:>6,}: pred={pred:>10,.1f}, true={true_p:>8,}, error={err:>6.3f}%")


def demo_sieve_integration():
    """Demonstrate integration with sieve bounds."""
    print("\n=== Sieve Integration Example ===")
    
    # Use Z_5D to estimate bounds for sieving
    k_target = 10000
    upper_bound_estimate = z5d_prime(k_target)
    
    # Add safety margin (Z_5D tends to underestimate slightly)
    safety_margin = 1.02  # 2% margin
    sieve_upper = int(upper_bound_estimate * safety_margin)
    
    print(f"Target: {k_target}th prime")
    print(f"Z_5D estimate: {upper_bound_estimate:.1f}")
    print(f"Sieve upper bound: {sieve_upper:,}")
    
    # Count primes up to sieve bound to verify
    primes_count = int(ntheory.primepi(sieve_upper))
    actual_kth_prime = ntheory.prime(k_target)
    
    print(f"Primes ≤ {sieve_upper:,}: {primes_count:,}")
    print(f"Actual {k_target}th prime: {actual_kth_prime:,}")
    print(f"Bound efficiency: {'✓' if primes_count >= k_target else '❌'}")


def demo_geodesic_hybrid():
    """Demonstrate hybrid Z_5D with geodesic filtering."""
    print("\n=== Geodesic Hybrid Example ===")
    
    # Generate candidate range around Z_5D estimate
    k = 1000
    z5d_estimate = z5d_prime(k)
    
    # Create search window
    window_size = int(z5d_estimate * 0.05)  # 5% window
    lower = max(2, int(z5d_estimate - window_size))
    upper = int(z5d_estimate + window_size)
    
    print(f"Z_5D estimate for {k}th prime: {z5d_estimate:.1f}")
    print(f"Search window: [{lower:,}, {upper:,}]")
    
    # Simple geodesic filter example (φ-based)
    phi = 1.6180339887498948  # Golden ratio
    e_squared = np.e**2
    
    candidates = []
    for n in range(lower, upper + 1):
        if ntheory.isprime(n):
            # Simple geodesic test: |Δ_n| ≤ e^2
            delta_n = (n % phi / phi) * e_squared
            if abs(delta_n) <= e_squared:
                candidates.append(n)
    
    actual_prime = int(ntheory.prime(k))
    
    print(f"Prime candidates in window: {len(candidates)}")
    print(f"Actual {k}th prime: {actual_prime}")
    print(f"Found actual prime: {'✓' if actual_prime in candidates else '❌'}")
    if candidates:
        closest = min(candidates, key=lambda x: abs(x - actual_prime))
        print(f"Closest candidate: {closest} (error: {abs(closest - actual_prime)})")


def demo_calibration():
    """Demonstrate parameter calibration."""
    print("\n=== Calibration Example ===")
    
    # Test default parameters vs actual primes
    test_k = [100, 500, 1000, 5000, 10000]
    true_primes = [int(ntheory.prime(k)) for k in test_k]
    
    # Default calibration
    results = validate_z5d_accuracy(test_k, true_primes)
    
    print(f"Default calibration (c=-0.00247, k*=0.04449):")
    print(f"  Mean relative error: {results['mean_relative_error']*100:.4f}%")
    print(f"  Max relative error: {results['max_relative_error']*100:.4f}%")
    
    # Custom calibration example
    results_custom = validate_z5d_accuracy(test_k, true_primes, c=-0.003, k_star=0.05)
    
    print(f"Custom calibration (c=-0.003, k*=0.05):")
    print(f"  Mean relative error: {results_custom['mean_relative_error']*100:.4f}%")
    print(f"  Max relative error: {results_custom['max_relative_error']*100:.4f}%")


def demo_performance():
    """Demonstrate performance characteristics."""
    print("\n=== Performance Demonstration ===")
    
    import time
    
    # Test various array sizes
    sizes = [100, 1000, 10000]
    
    for size in sizes:
        k_values = np.arange(100, 100 + size)  # Start from 100 for better accuracy
        
        start_time = time.time()
        predictions = z5d_prime(k_values)
        end_time = time.time()
        
        duration = end_time - start_time
        per_prediction = duration / size * 1000  # milliseconds
        
        print(f"Size {size:>5,}: {duration:.4f}s total, {per_prediction:.4f}ms per prediction")


def main():
    """Run all demonstration examples."""
    print("Z_5D Prime Enumeration Predictor - Integration Examples")
    print("=" * 60)
    
    try:
        demo_basic_usage()
        demo_sieve_integration()
        demo_geodesic_hybrid()
        demo_calibration()
        demo_performance()
        
        print("\n" + "=" * 60)
        print("🎉 All integration examples completed successfully!")
        print("\nThe Z_5D predictor is ready for integration into your")
        print("prime generation and optimization pipelines.")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)