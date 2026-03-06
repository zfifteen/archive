#!/usr/bin/env python3
"""
RSA Challenge Factorization Script
=================================

This script implements systematic factorization attempts for all RSA challenge numbers
using the enhanced Z5D predictor algorithms with error growth compensation.

Usage:
    python run_rsa_factorization.py [--quick] [--subset N]
    
Options:
    --quick     Use reduced trials and timeouts for faster execution
    --subset N  Only process first N RSA numbers (sorted by size)
"""

import sys
import time
import json
from src.applications.rsa_probe_validation import (
    RSA_CHALLENGE_NUMBERS, rsa_systematic_factorization, 
    probe_semiprime_with_timeout, compensated_k_estimation
)

def quick_factorization_test(max_numbers=5):
    """Run a quick factorization test on the smallest RSA numbers."""
    print("QUICK RSA FACTORIZATION TEST")
    print("=" * 50)
    print(f"Testing first {max_numbers} RSA challenge numbers with reduced parameters")
    print("Goal: Demonstrate the systematic factorization approach")
    print("=" * 50)
    
    # Sort by size and take first max_numbers
    sorted_rsa = sorted(RSA_CHALLENGE_NUMBERS.items(), key=lambda x: len(x[1]))[:max_numbers]
    
    results = {}
    
    for idx, (name, n_str) in enumerate(sorted_rsa, 1):
        print(f"\n[{idx}/{len(sorted_rsa)}] Testing {name} ({len(n_str)} digits)")
        print("-" * 40)
        
        # Quick parameters for demonstration
        trials = 30
        timeout_sec = 15
        
        print(f"  Parameters: trials={trials}, timeout={timeout_sec}s")
        
        start_time = time.time()
        try:
            factor = probe_semiprime_with_timeout(
                n_str, trials=trials, timeout_seconds=timeout_sec, enable_error_compensation=True
            )
        except TimeoutError:
            factor = None
            print(f"  TIMEOUT: Exceeded {timeout_sec}s")
        except Exception as e:
            factor = None
            print(f"  ERROR: {e}")
        
        end_time = time.time()
        runtime = end_time - start_time
        
        # Calculate k_est
        try:
            k_est = compensated_k_estimation(n_str, error_compensation=True)
            k_est_str = f"{k_est:.2e}"
        except:
            k_est = 0
            k_est_str = "Failed"
        
        results[name] = {
            'digits': len(n_str),
            'factor_found': factor,
            'runtime_seconds': runtime,
            'k_est': k_est_str,
            'trials': trials,
            'status': 'SUCCESS - Factor found' if factor else 'No factor detected'
        }
        
        print(f"  Runtime: {runtime:.3f}s")
        print(f"  k_est: {k_est_str}")
        print(f"  Factor found: {factor}")
        
        if factor:
            print(f"  🎉 BREAKTHROUGH: Factor discovered for {name}!")
            try:
                n = int(n_str)
                if n % factor == 0:
                    other_factor = n // factor
                    print(f"  ✓ VERIFIED FACTORS:")
                    print(f"    {factor} × {other_factor} = {name}")
                else:
                    print(f"  ⚠️ Factor verification failed")
            except Exception as e:
                print(f"  ⚠️ Verification error: {e}")
        else:
            print(f"  Status: No factor detected (as expected for RSA challenges)")
    
    # Summary
    print("\n" + "=" * 50)
    print("QUICK TEST SUMMARY")
    print("=" * 50)
    
    factors_found = sum(1 for r in results.values() if r['factor_found'])
    total_time = sum(r['runtime_seconds'] for r in results.values())
    
    if factors_found > 0:
        print(f"🎉 BREAKTHROUGH: {factors_found} factor(s) discovered!")
        for name, result in results.items():
            if result['factor_found']:
                print(f"  {name}: Factor = {result['factor_found']}")
    else:
        print("No factors discovered (expected result for RSA challenge numbers)")
    
    print(f"Numbers tested: {len(results)}")
    print(f"Total runtime: {total_time:.1f}s")
    print(f"Average time per number: {total_time/len(results):.1f}s")
    
    # Algorithm demonstration
    print("\nAlgorithm Demonstration:")
    print("• Enhanced Z5D predictor with error growth compensation")
    print("• Advanced k estimation using logarithmic integral")
    print("• Scale-adaptive precision and calibration")
    print("• Systematic search with timeout protection")
    
    return results

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='RSA Challenge Factorization')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick test on smallest numbers')
    parser.add_argument('--subset', type=int, metavar='N',
                       help='Only process first N numbers (sorted by size)')
    parser.add_argument('--full', action='store_true',
                       help='Run full systematic factorization')
    
    args = parser.parse_args()
    
    if args.quick:
        subset_size = args.subset if args.subset else 5
        results = quick_factorization_test(max_numbers=subset_size)
        
        # Save results
        with open('rsa_quick_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to rsa_quick_test_results.json")
        
    elif args.full:
        print("Running FULL systematic factorization on all RSA challenge numbers...")
        print("This may take several hours. Consider using --quick for testing.")
        
        confirm = input("Continue? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            results = rsa_systematic_factorization()
            print("Full factorization complete!")
        else:
            print("Cancelled.")
            return
            
    else:
        # Default: Show available numbers and usage
        print("RSA Challenge Factorization Tool")
        print("=" * 40)
        print(f"Available RSA challenge numbers: {len(RSA_CHALLENGE_NUMBERS)}")
        
        sorted_rsa = sorted(RSA_CHALLENGE_NUMBERS.items(), key=lambda x: len(x[1]))
        for name, n_str in sorted_rsa[:10]:  # Show first 10
            print(f"  {name}: {len(n_str)} digits")
        
        if len(sorted_rsa) > 10:
            print(f"  ... and {len(sorted_rsa) - 10} more")
        
        print("\nUsage:")
        print("  python run_rsa_factorization.py --quick          # Quick test (5 numbers)")
        print("  python run_rsa_factorization.py --quick --subset 3  # Quick test (3 numbers)")
        print("  python run_rsa_factorization.py --full           # Full systematic test")

if __name__ == "__main__":
    main()