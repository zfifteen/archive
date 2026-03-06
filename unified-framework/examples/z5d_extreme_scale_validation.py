#!/usr/bin/env python3
"""
Z5D Prime Predictor - Extreme Scale Validation

Tests performance and accuracy from 10^18 to 10^1233 in batches.
This validates the predictor's behavior at scales far beyond standard testing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from z5d import predict_prime, benchmark_prediction
import time


def test_extreme_scale_batch(start_exp, end_exp, batch_size=10):
    """
    Test predictor at extreme scales in batches.
    
    Args:
        start_exp: Starting exponent (e.g., 18 for 10^18)
        end_exp: Ending exponent (e.g., 1233 for 10^1233)
        batch_size: Number of exponents to test per batch
    """
    print("\n" + "="*80)
    print(" Z5D PRIME PREDICTOR - EXTREME SCALE VALIDATION")
    print(f" Testing from 10^{start_exp} to 10^{end_exp}")
    print("="*80)
    
    results = []
    
    for batch_start in range(start_exp, end_exp + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, end_exp)
        print(f"\n[BATCH] Testing 10^{batch_start} to 10^{batch_end}")
        print("-"*80)
        
        batch_results = []
        for exp in range(batch_start, batch_end + 1):
            n = 10**exp
            
            try:
                # Time the prediction
                t0 = time.perf_counter_ns()
                result = predict_prime(n)
                t1 = time.perf_counter_ns()
                runtime_ms = (t1 - t0) / 1e6
                
                # Calculate result characteristics
                result_digits = len(str(result))
                
                batch_results.append({
                    'exponent': exp,
                    'n': n,
                    'result': result,
                    'result_digits': result_digits,
                    'runtime_ms': runtime_ms,
                    'status': 'SUCCESS'
                })
                
                print(f"  10^{exp:<4}: {result_digits} digits, {runtime_ms:.3f}ms - SUCCESS")
                
            except Exception as e:
                batch_results.append({
                    'exponent': exp,
                    'n': n,
                    'result': None,
                    'result_digits': None,
                    'runtime_ms': None,
                    'status': f'FAILED: {str(e)[:50]}'
                })
                print(f"  10^{exp:<4}: FAILED - {str(e)[:50]}")
        
        # Batch summary
        successes = sum(1 for r in batch_results if r['status'] == 'SUCCESS')
        failures = len(batch_results) - successes
        
        if successes > 0:
            avg_runtime = sum(r['runtime_ms'] for r in batch_results if r['runtime_ms']) / successes
            avg_digits = sum(r['result_digits'] for r in batch_results if r['result_digits']) / successes
            print(f"\n  Batch Summary: {successes} SUCCESS, {failures} FAILED")
            print(f"  Avg Runtime: {avg_runtime:.3f}ms")
            print(f"  Avg Result Digits: {avg_digits:.1f}")
        else:
            print(f"\n  Batch Summary: All {failures} predictions FAILED")
        
        results.extend(batch_results)
    
    return results


def generate_summary_report(results, start_exp, end_exp):
    """Generate a summary report of the validation."""
    print("\n" + "="*80)
    print(" SUMMARY REPORT")
    print("="*80)
    
    successes = [r for r in results if r['status'] == 'SUCCESS']
    failures = [r for r in results if r['status'] != 'SUCCESS']
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Successful: {len(successes)}")
    print(f"Failed: {len(failures)}")
    
    if successes:
        print(f"\nPerformance Statistics:")
        runtimes = [r['runtime_ms'] for r in successes]
        print(f"  Min Runtime: {min(runtimes):.3f}ms")
        print(f"  Max Runtime: {max(runtimes):.3f}ms")
        print(f"  Avg Runtime: {sum(runtimes)/len(runtimes):.3f}ms")
        
        print(f"\nResult Statistics:")
        digits = [r['result_digits'] for r in successes]
        print(f"  Min Digits: {min(digits)}")
        print(f"  Max Digits: {max(digits)}")
        print(f"  Avg Digits: {sum(digits)/len(digits):.1f}")
        
        # Show range of successful exponents
        exp_success = [r['exponent'] for r in successes]
        print(f"\nSuccessful Range: 10^{min(exp_success)} to 10^{max(exp_success)}")
    
    if failures:
        print(f"\nFirst 5 Failures:")
        for r in failures[:5]:
            print(f"  10^{r['exponent']}: {r['status']}")


def save_detailed_results(results, filename="extreme_scale_validation_results.txt"):
    """Save detailed results to a file."""
    filepath = os.path.join(os.path.dirname(__file__), '..', filename)
    
    with open(filepath, 'w') as f:
        f.write("Z5D Prime Predictor - Extreme Scale Validation Results\n")
        f.write("="*80 + "\n\n")
        
        for r in results:
            f.write(f"Exponent: 10^{r['exponent']}\n")
            f.write(f"Status: {r['status']}\n")
            if r['result']:
                f.write(f"Result: {r['result']}\n")
                f.write(f"Result Digits: {r['result_digits']}\n")
                f.write(f"Runtime: {r['runtime_ms']:.3f}ms\n")
            f.write("-"*80 + "\n")
    
    print(f"\nDetailed results saved to: {filepath}")


def main():
    """Main entry point."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        start_exp = int(sys.argv[1])
    else:
        start_exp = 18
    
    if len(sys.argv) > 2:
        end_exp = int(sys.argv[2])
    else:
        end_exp = 100  # Default to 10^100 for reasonable testing
    
    if len(sys.argv) > 3:
        batch_size = int(sys.argv[3])
    else:
        batch_size = 10
    
    print(f"\nStarting validation from 10^{start_exp} to 10^{end_exp}")
    print(f"Batch size: {batch_size}")
    print(f"\nNote: Testing up to 10^1233 may take significant time and memory.")
    print(f"Consider starting with smaller ranges (e.g., 10^18 to 10^100)")
    
    # Run validation
    results = test_extreme_scale_batch(start_exp, end_exp, batch_size)
    
    # Generate summary
    generate_summary_report(results, start_exp, end_exp)
    
    # Save detailed results
    save_detailed_results(results)
    
    print("\n" + "="*80)
    print(" VALIDATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
