#!/usr/bin/env python3
"""
Simple test script for enhanced hybrid prime identification.
"""

import sys
import os
sys.path.append('.')

from src.core.hybrid_prime_identification import (
    hybrid_prime_identification, 
    miller_rabin_deterministic,
    compute_rigorous_bounds,
    is_prime_optimized
)

def test_basic_components():
    """Test basic components of the enhanced system."""
    print("Testing Basic Components")
    print("=" * 30)
    
    # Test Miller-Rabin
    print("1. Testing Miller-Rabin primality testing:")
    test_numbers = [17, 15, 1009, 1013, 1021, 1024]
    for n in test_numbers:
        is_prime_mr = miller_rabin_deterministic(n)
        is_prime_opt = is_prime_optimized(n)
        print(f"   {n}: MR={is_prime_mr}, Opt={is_prime_opt}, Match={is_prime_mr == is_prime_opt}")
    
    # Test bounds
    print("\n2. Testing rigorous bounds:")
    test_k_values = [100, 1000, 10000]
    for k in test_k_values:
        lower, upper = compute_rigorous_bounds(k, "auto")
        width = upper - lower
        print(f"   k={k}: bounds=[{lower}, {upper}], width={width}")

def test_hybrid_function():
    """Test the hybrid function with small examples."""
    print("\nTesting Enhanced Hybrid Function")
    print("=" * 35)
    
    # Test cases with known results
    test_cases = [
        {'k': 100, 'expected': 541},  # 100th prime
        {'k': 500, 'expected': 3571}, # 500th prime
    ]
    
    for case in test_cases:
        k = case['k']
        expected = case['expected']
        
        print(f"\nTesting k={k} (expected: {expected})")
        
        try:
            # Test with rigorous bounds and Miller-Rabin
            result = hybrid_prime_identification(
                k, 
                use_rigorous_bounds=True,
                bounds_type="auto",
                sieve_method="miller_rabin",
                log_diagnostics=False,
                max_range_size=10000  # Smaller range for testing
            )
            
            predicted = result['predicted_prime']
            success = (predicted == expected)
            
            print(f"   Predicted: {predicted}")
            print(f"   Expected:  {expected}")
            print(f"   Success:   {'✅' if success else '❌'}")
            print(f"   Time:      {result['metrics']['total_time']:.3f}s")
            print(f"   Method:    {result['sieve_method']} + {result['bounds_type']} bounds")
            print(f"   Primes found: {result['metrics']['primes_found']}")
            print(f"   Filter rate:  {result['metrics']['filter_rate']:.1%}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

def test_performance_comparison():
    """Compare old vs new methods."""
    print("\nPerformance Comparison")
    print("=" * 22)
    
    k = 1000
    print(f"Testing k={k}")
    
    try:
        # Test new method
        print("\n1. Enhanced method (rigorous bounds + Miller-Rabin):")
        result_new = hybrid_prime_identification(
            k, 
            use_rigorous_bounds=True,
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=5000
        )
        
        print(f"   Result: {result_new['predicted_prime']}")
        print(f"   Time: {result_new['metrics']['total_time']:.3f}s")
        print(f"   Candidates: {result_new['metrics']['candidates_count']}")
        print(f"   Primes found: {result_new['metrics']['primes_found']}")
        
        # Test fallback method
        print("\n2. Fallback method (prediction-based + Miller-Rabin):")
        result_old = hybrid_prime_identification(
            k, 
            use_rigorous_bounds=False,
            sieve_method="miller_rabin",
            log_diagnostics=False,
            max_range_size=5000
        )
        
        print(f"   Result: {result_old['predicted_prime']}")
        print(f"   Time: {result_old['metrics']['total_time']:.3f}s")
        print(f"   Candidates: {result_old['metrics']['candidates_count']}")
        print(f"   Primes found: {result_old['metrics']['primes_found']}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    test_basic_components()
    test_hybrid_function() 
    test_performance_comparison()
    
    print("\n" + "=" * 50)
    print("Enhanced Hybrid Prime Identification Test Complete")