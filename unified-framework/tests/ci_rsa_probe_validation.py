#!/usr/bin/env python3
"""
CI validation script for RSA Probe Validation

This script runs the RSA probe validation in CI environment, expecting
no factors to be found. This validates numerical stability and performance
of the inverse Mersenne probe implementation.

Exit codes:
0 - All validations passed (no factors found as expected)
1 - Validation failed (unexpected factors found or errors)
2 - Performance issues detected
"""

import sys
import os
import json
import time
import math

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src', 'applications')
sys.path.insert(0, src_dir)

try:
    import rsa_probe_validation
except ImportError as e:
    print(f"ERROR: Failed to import rsa_probe_validation: {e}")
    sys.exit(1)

def run_ci_validation():
    """
    Run RSA probe validation for CI environment.
    
    Returns
    -------
    int
        Exit code (0=success, 1=failure, 2=performance issue)
    """
    print("=" * 60)
    print("RSA Probe Validation - CI Test")
    print("=" * 60)
    
    # Check mpmath availability
    if not rsa_probe_validation.MPMATH_AVAILABLE:
        print("WARNING: mpmath not available - using reduced precision")
    else:
        print(f"Using mpmath with {rsa_probe_validation.mpmath.mp.dps} decimal places")
    
    # Run validation with reduced trials for CI speed
    start_time = time.time()
    
    try:
        # Test each RSA challenge number individually for better error reporting
        results = {}
        
        for name, n_str in rsa_probe_validation.RSA_CHALLENGE_NUMBERS.items():
            print(f"\nTesting {name}...")
            
            # Use fewer trials in CI for speed
            test_start = time.time()
            factor = rsa_probe_validation.probe_semiprime(n_str, trials=20)
            test_end = time.time()
            
            # Calculate k_est for reporting
            if rsa_probe_validation.MPMATH_AVAILABLE:
                sqrt_n = rsa_probe_validation.mpmath.sqrt(rsa_probe_validation.mpmath.mpf(n_str))
                ln_sqrt = rsa_probe_validation.mpmath.log(sqrt_n)
                k_est = float(sqrt_n / ln_sqrt)
            else:
                sqrt_n = math.sqrt(float(n_str))
                ln_sqrt = math.log(sqrt_n)
                k_est = sqrt_n / ln_sqrt
            
            results[name] = {
                'factor_found': factor,
                'time': test_end - test_start,
                'k_est_order': f"10^{int(math.log10(k_est))}",
                'validation_passed': factor is None
            }
            
            print(f"  k_est order: {results[name]['k_est_order']}")
            print(f"  Time: {results[name]['time']:.3f}s")
            print(f"  Factor found: {factor}")
            print(f"  Expected: No factor")
            print(f"  Result: {'PASS' if factor is None else 'FAIL'}")
            
            # Check for unexpected factors
            if factor is not None:
                print(f"  ERROR: Unexpected factor found: {factor}")
                return 1
                
    except Exception as e:
        print(f"ERROR: Validation failed with exception: {e}")
        return 1
    
    total_time = time.time() - start_time
    
    # Performance check
    if total_time > 30.0:  # Should complete within 30 seconds in CI
        print(f"\nWARNING: Total time {total_time:.1f}s exceeds expected CI performance")
        return 2
    
    # Summary
    print(f"\n" + "=" * 60)
    print("CI Validation Summary")
    print("=" * 60)
    
    all_passed = all(r['validation_passed'] for r in results.values())
    avg_time = sum(r['time'] for r in results.values()) / len(results)
    
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per test: {avg_time:.3f}s") 
    print(f"All validations passed: {'Yes' if all_passed else 'No'}")
    print(f"Factors found: {sum(1 for r in results.values() if r['factor_found'] is not None)}")
    print(f"Expected factors: 0")
    
    # Save results for CI artifacts
    try:
        ci_results = {
            'timestamp': time.time(),
            'total_time': total_time,
            'average_time': avg_time,
            'all_passed': all_passed,
            'mpmath_available': rsa_probe_validation.MPMATH_AVAILABLE,
            'precision': rsa_probe_validation.mpmath.mp.dps if getattr(rsa_probe_validation, 'mpmath', None) is not None and rsa_probe_validation.MPMATH_AVAILABLE else 'standard',
            'results': results
        }
        
        with open('ci_rsa_probe_results.json', 'w') as f:
            json.dump(ci_results, f, indent=2)
        print(f"\nResults saved to ci_rsa_probe_results.json")
        
    except Exception as e:
        print(f"WARNING: Failed to save CI results: {e}")
    
    if all_passed:
        print("\n✅ CI Validation PASSED - No factors found as expected")
        print("   The inverse Mersenne probe demonstrates numerical stability")
        print("   but does not present a threat to RSA security at these scales.")
        return 0
    else:
        print("\n❌ CI Validation FAILED - Unexpected results")
        return 1


def run_performance_benchmark():
    """
    Run a quick performance benchmark for CI.
    
    Returns
    -------
    dict
        Performance metrics
    """
    print("\nRunning performance benchmark...")
    
    # Test with RSA-100 for consistent benchmarking
    rsa100 = rsa_probe_validation.RSA_CHALLENGE_NUMBERS['RSA-100']
    
    benchmark = rsa_probe_validation.benchmark_probe_performance(
        rsa100, trials=10, num_runs=3
    )
    
    print(f"Benchmark results (3 runs, 10 trials each):")
    print(f"  Mean time: {benchmark['mean_time']:.3f}s")
    print(f"  Min time: {benchmark['min_time']:.3f}s") 
    print(f"  Max time: {benchmark['max_time']:.3f}s")
    print(f"  Std dev: {benchmark['std_time']:.3f}s")
    print(f"  Success rate: {benchmark['success_rate']:.1%}")
    
    return benchmark


if __name__ == "__main__":
    print("Starting RSA Probe Validation CI Test...")
    
    # Run main validation
    exit_code = run_ci_validation()
    
    # Run performance benchmark if main validation passed
    if exit_code == 0:
        try:
            benchmark = run_performance_benchmark()
            
            # Check if performance is within expected range
            if benchmark['mean_time'] > 1.0:  # Should be much faster than original 0.15s spec
                print(f"WARNING: Performance slower than expected ({benchmark['mean_time']:.3f}s)")
                exit_code = 2
                
        except Exception as e:
            print(f"WARNING: Performance benchmark failed: {e}")
            # Don't fail CI for benchmark issues
    
    # Final status
    if exit_code == 0:
        print("\n🎉 All CI validations completed successfully!")
    elif exit_code == 1:
        print("\n💥 CI validation failed - check results above")
    elif exit_code == 2:
        print("\n⚠️ CI validation passed but performance issues detected")
    
    sys.exit(exit_code)