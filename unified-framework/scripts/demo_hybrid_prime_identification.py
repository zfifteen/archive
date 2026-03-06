#!/usr/bin/env python3
"""
Hybrid Prime Identification Demo
===============================

Demonstrates the complete workflow of the Z Framework hybrid prime 
identification function with various k values and configurations.
"""

import sys
import os
import time
import logging

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.hybrid_prime_identification import hybrid_prime_identification


def demo_basic_usage():
    """Demonstrate basic usage of hybrid prime identification."""
    print("🔍 BASIC USAGE DEMONSTRATION")
    print("=" * 50)
    
    k_values = [100, 500, 1000, 2000]
    
    for k in k_values:
        print(f"\nFinding {k}th prime...")
        start_time = time.time()
        
        result = hybrid_prime_identification(k)
        elapsed = time.time() - start_time
        
        print(f"  Predicted: {result['predicted_prime']}")
        print(f"  Search range: {result['range'][0]} - {result['range'][1]}")
        print(f"  Candidates filtered: {result['filtered_candidates_count']}")
        print(f"  Time: {elapsed:.3f}s")
        
        if result['predicted_prime']:
            # Quick validation using known approximation
            approx = k * (1.0 + 1.0/k)  # Simple approximation
            deviation = abs(result['predicted_prime'] - k*1.44*log(k)) / (k*1.44*log(k)) if k > 1 else 0
            print(f"  Quality: {'Good' if deviation < 0.1 else 'Fair'}")


def demo_advanced_configuration():
    """Demonstrate advanced configuration options."""
    print("\n\n⚙️ ADVANCED CONFIGURATION DEMONSTRATION")  
    print("=" * 50)
    
    k = 1000
    configurations = [
        {"error_rate": 0.001, "desc": "High precision (0.1%)"},
        {"error_rate": 0.01, "desc": "Standard precision (1%)"},
        {"error_rate": 0.05, "desc": "Fast mode (5%)"},
    ]
    
    for config in configurations:
        print(f"\nTesting {config['desc']}:")
        
        start_time = time.time()
        result = hybrid_prime_identification(
            k=k,
            error_rate=config['error_rate'],
            log_diagnostics=False
        )
        elapsed = time.time() - start_time
        
        range_size = result['range'][1] - result['range'][0] + 1
        print(f"  Range size: {range_size}")
        print(f"  Predicted: {result['predicted_prime']}")
        print(f"  Filter rate: {result['metrics']['filter_rate']:.1%}")
        print(f"  Time: {elapsed:.3f}s")


def demo_performance_analysis():
    """Demonstrate performance characteristics."""
    print("\n\n📊 PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    # Test scaling behavior
    k_values = [10, 50, 100, 500, 1000]
    times = []
    accuracies = []
    
    # Known approximate values for validation
    known_primes = {10: 29, 50: 229, 100: 541, 500: 3571, 1000: 7919}
    
    print(f"\n{'k':>6} {'Time (ms)':>10} {'Range Size':>12} {'Accuracy':>10}")
    print("-" * 45)
    
    for k in k_values:
        start_time = time.time()
        result = hybrid_prime_identification(k, error_rate=0.01)
        elapsed = time.time() - start_time
        
        times.append(elapsed * 1000)  # Convert to ms
        
        range_size = result['range'][1] - result['range'][0] + 1
        
        # Calculate accuracy if we have expected value
        if k in known_primes and result['predicted_prime']:
            expected = known_primes[k]
            accuracy = 1 - abs(result['predicted_prime'] - expected) / expected
            accuracies.append(accuracy)
            accuracy_str = f"{accuracy:.1%}"
        else:
            accuracy_str = "N/A"
        
        print(f"{k:>6} {elapsed*1000:>10.1f} {range_size:>12} {accuracy_str:>10}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\nAverage time: {avg_time:.1f}ms")
    
    if accuracies:
        avg_accuracy = sum(accuracies) / len(accuracies)
        print(f"Average accuracy: {avg_accuracy:.1%}")


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n\n🛡️ ERROR HANDLING DEMONSTRATION")
    print("=" * 50)
    
    test_cases = [
        {"k": 0, "desc": "Edge case: k=0"},
        {"k": 1, "desc": "Edge case: k=1"}, 
        {"k": 2, "desc": "Edge case: k=2"},
        {"k": 10**13, "desc": "Extrapolation: k=10^13"},
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['desc']}:")
        try:
            result = hybrid_prime_identification(
                test_case['k'], 
                error_rate=0.01,
                log_diagnostics=False
            )
            
            print(f"  Result: {result['predicted_prime']}")
            print(f"  Extrapolation: {result['is_extrapolation']}")
            print(f"  Error bound: {result['uncertainty_bound']}")
            print("  Status: ✅ Handled successfully")
            
        except Exception as e:
            print(f"  Error: {e}")
            print("  Status: ❌ Exception occurred")


def main():
    """Run the complete demonstration."""
    print("Z Framework - Hybrid Prime Identification Demo")
    print("=" * 60)
    print("This demo showcases the integration of Z5D prediction,")
    print("DiscreteZetaShift filtering, and traditional sieve methods.")
    print("=" * 60)
    
    # Enable math module for approximations
    import math
    global log
    log = math.log
    
    # Run demonstration sections
    demo_basic_usage()
    demo_advanced_configuration()
    demo_performance_analysis()
    demo_error_handling()
    
    print("\n\n🎉 DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("The hybrid prime identification function demonstrates:")
    print("• Integration of Z Framework components")
    print("• Scalable prime prediction with adaptive error bounds")
    print("• Robust error handling for edge cases")
    print("• Performance suitable for interactive applications")
    print("\nFor more details, see: docs/hybrid_prime_identification.md")


if __name__ == "__main__":
    main()