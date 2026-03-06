"""
Z5D Prime Predictor: Quick Empirical Validation Summary

This script runs a focused set of empirical validation tests to quickly
assess Z5D predictor performance and generate a summary report.
"""

import sys
import os
import numpy as np
import pandas as pd
import time
from pathlib import Path

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from test_z5d_empirical_validation import Z5DEmpiricalValidator

def run_quick_validation():
    """Run focused empirical validation tests."""
    print("=" * 70)
    print("Z5D PRIME PREDICTOR: QUICK EMPIRICAL VALIDATION")
    print("=" * 70)
    
    # Initialize validator
    validator = Z5DEmpiricalValidator(output_dir="validation_results")
    
    # Test 1: Small scale for basic functionality
    print("\n1. Small Scale Validation (n: 10-1000)")
    print("-" * 40)
    small_results = validator.run_scale_validation('small', save_results=False)
    
    # Test 2: Medium scale for improved accuracy
    print("\n2. Medium Scale Validation (n: 1000-100000)")
    print("-" * 40)
    medium_results = validator.run_scale_validation('medium', save_results=False)
    
    # Test 3: Numerical stability (limited range)
    print("\n3. Numerical Stability Test (n: 10^3 to 10^20)")
    print("-" * 40)
    stability_results = validator.test_numerical_stability(max_exponent=20)
    
    # Test 4: Large scale sample for accuracy claims
    print("\n4. Large Scale Sample (n: 100000-1000000)")
    print("-" * 40)
    large_results = validator.run_scale_validation('large', save_results=False)
    
    # Generate summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    # Small scale summary
    if not small_results.empty and 'relative_error' in small_results.columns:
        small_errors = small_results['relative_error'].dropna()
        if not small_errors.empty:
            print(f"Small Scale (n: 10-1000):")
            print(f"  Points tested: {len(small_errors)}")
            print(f"  Mean Relative Error: {small_errors.mean():.3f}%")
            print(f"  Within bounds rate: {small_results['within_bounds'].mean()*100:.1f}%")
    
    # Medium scale summary
    if not medium_results.empty and 'relative_error' in medium_results.columns:
        medium_errors = medium_results['relative_error'].dropna()
        if not medium_errors.empty:
            print(f"\nMedium Scale (n: 1000-100000):")
            print(f"  Points tested: {len(medium_errors)}")
            print(f"  Mean Relative Error: {medium_errors.mean():.3f}%")
            print(f"  Within bounds rate: {medium_results['within_bounds'].mean()*100:.1f}%")
    
    # Large scale summary
    if not large_results.empty and 'relative_error' in large_results.columns:
        large_errors = large_results['relative_error'].dropna()
        if not large_errors.empty:
            print(f"\nLarge Scale (n: 100000-1000000):")
            print(f"  Points tested: {len(large_errors)}")
            print(f"  Mean Relative Error: {large_errors.mean():.6f}%")
            print(f"  Within bounds rate: {large_results['within_bounds'].mean()*100:.1f}%")
            
            # Check accuracy claim for large scale
            claim_threshold = 0.01  # 0.01% - reasonable threshold for validation
            if large_errors.mean() < claim_threshold:
                print(f"  ✅ High accuracy confirmed (< {claim_threshold}%)")
            else:
                print(f"  ⚠️ Mean error above {claim_threshold}% threshold")
    
    # Numerical stability summary
    if not stability_results.empty:
        successful_tests = stability_results['success'].sum()
        total_tests = len(stability_results)
        max_successful_scale = stability_results[stability_results['success']]['log10_n'].max()
        print(f"\nNumerical Stability:")
        print(f"  Successful tests: {successful_tests}/{total_tests}")
        print(f"  Maximum stable scale: 10^{max_successful_scale}")
        if successful_tests == total_tests:
            print(f"  ✅ Excellent numerical stability")
        elif successful_tests > total_tests * 0.8:
            print(f"  ✅ Good numerical stability")
        else:
            print(f"  ⚠️ Some numerical stability issues")
    
    print(f"\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    
    # Analyze progression of accuracy
    if (not small_results.empty and not medium_results.empty and 
        not large_results.empty):
        
        small_mre = small_results['relative_error'].dropna().mean()
        medium_mre = medium_results['relative_error'].dropna().mean()
        large_mre = large_results['relative_error'].dropna().mean()
        
        print(f"Error Progression:")
        print(f"  Small → Medium → Large: {small_mre:.3f}% → {medium_mre:.3f}% → {large_mre:.6f}%")
        
        if large_mre < medium_mre < small_mre:
            print(f"  ✅ Error decreases with scale (expected behavior)")
        elif large_mre < 0.1:  # Still very good accuracy
            print(f"  ✅ Maintains excellent accuracy at large scales")
        else:
            print(f"  ⚠️ Error behavior needs further investigation")
    
    # Performance analysis
    if not large_results.empty and 'computation_time' in large_results.columns:
        avg_time = large_results['computation_time'].mean()
        print(f"\nPerformance:")
        print(f"  Average prediction time: {avg_time*1000:.2f} ms")
        if avg_time < 0.01:  # < 10ms
            print(f"  ✅ Excellent computational efficiency")
        elif avg_time < 0.1:  # < 100ms
            print(f"  ✅ Good computational efficiency")
        else:
            print(f"  ⚠️ Consider performance optimization")
    
    print(f"\nValidation completed. Detailed results saved in validation_results/")
    
    return {
        'small': small_results,
        'medium': medium_results,
        'large': large_results,
        'stability': stability_results
    }

if __name__ == "__main__":
    results = run_quick_validation()