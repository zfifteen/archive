#!/usr/bin/env python3
"""
Simple validation script for Hybrid Prime Identification Function
================================================================

This script provides a quick validation of the hybrid prime identification
implementation with known test cases.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.hybrid_prime_identification import hybrid_prime_identification


def main():
    """Run simple validation tests."""
    print("Hybrid Prime Identification - Simple Validation")
    print("=" * 60)
    
    # Test cases with known k-th primes
    test_cases = [
        (10, 29, "10th prime"),
        (25, 97, "25th prime"),
        (50, 229, "50th prime"),
        (100, 541, "100th prime"),
        (1000, 7919, "1000th prime"),
    ]
    
    results = []
    total_time = 0
    
    for k, expected_prime, description in test_cases:
        print(f"\nTesting {description} (k={k}):")
        print(f"Expected prime: {expected_prime}")
        
        start_time = time.time()
        try:
            result = hybrid_prime_identification(k, error_rate=0.01)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            predicted = result['predicted_prime']
            if predicted:
                deviation = abs(predicted - expected_prime) / expected_prime
                success = deviation < 0.2  # 20% tolerance
                
                print(f"Predicted prime: {predicted}")
                print(f"Deviation: {deviation:.3%}")
                print(f"Filter rate: {result['metrics']['filter_rate']:.1%}")
                print(f"Time: {elapsed:.3f}s")
                print(f"Status: {'✅ PASS' if success else '❌ FAIL'}")
                
                results.append({
                    'k': k,
                    'expected': expected_prime,
                    'predicted': predicted,
                    'deviation': deviation,
                    'success': success,
                    'time': elapsed
                })
            else:
                print("❌ FAIL: No prime found")
                results.append({
                    'k': k,
                    'expected': expected_prime,
                    'predicted': None,
                    'deviation': float('inf'),
                    'success': False,
                    'time': elapsed
                })
                
        except Exception as e:
            elapsed = time.time() - start_time
            total_time += elapsed
            print(f"❌ ERROR: {e}")
            results.append({
                'k': k,
                'expected': expected_prime,
                'predicted': None,
                'deviation': float('inf'),
                'success': False,
                'time': elapsed,
                'error': str(e)
            })
    
    # Summary
    print(f"\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    total_tests = len(results)
    success_rate = successful / total_tests if total_tests > 0 else 0
    
    print(f"Tests passed: {successful}/{total_tests}")
    print(f"Success rate: {success_rate:.1%}")
    print(f"Total time: {total_time:.3f}s")
    print(f"Average time per test: {total_time/total_tests:.3f}s")
    
    # Detailed results
    print(f"\nDetailed Results:")
    print(f"{'k':>6} {'Expected':>8} {'Predicted':>9} {'Deviation':>10} {'Status'}")
    print("-" * 50)
    
    for r in results:
        pred_str = str(r['predicted']) if r['predicted'] else "None"
        dev_str = f"{r['deviation']:.2%}" if r['deviation'] != float('inf') else "N/A"
        status = "PASS" if r['success'] else "FAIL"
        print(f"{r['k']:>6} {r['expected']:>8} {pred_str:>9} {dev_str:>10} {status}")
    
    if success_rate >= 0.6:  # 60% success threshold
        print(f"\n🎉 OVERALL: VALIDATION PASSED ({success_rate:.1%} success rate)")
        return 0
    else:
        print(f"\n❌ OVERALL: VALIDATION FAILED ({success_rate:.1%} success rate)")
        return 1


if __name__ == "__main__":
    sys.exit(main())