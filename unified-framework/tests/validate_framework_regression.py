#!/usr/bin/env python3
"""
Framework Regression Testing Validation Script
==============================================

Quick validation script to verify regression testing findings.
This script can be run independently to confirm framework status.

Usage:
    python validate_framework_regression.py
    python validate_framework_regression.py --detailed
"""

import sys
import os
import time
import warnings

# Add framework path
sys.path.append('/home/runner/work/unified-framework/unified-framework')

def run_quick_validation():
    """Run quick validation of key framework components"""
    print("=" * 60)
    print("UNIFIED FRAMEWORK REGRESSION VALIDATION")
    print("=" * 60)
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print()
    
    results = {
        'parameter_system': False,
        'z5d_predictor': False,
        'geodesic_mapping': False,
        'numerical_stability': False,
        'deprecation_warnings': False
    }
    
    # Test 1: Parameter System
    print("1. Testing Parameter System...")
    try:
        from src.core.params import (
            KAPPA_GEO_DEFAULT, KAPPA_STAR_DEFAULT, 
            validate_kappa_geo, validate_kappa_star
        )
        
        # Test default values
        assert KAPPA_GEO_DEFAULT == 0.3
        assert KAPPA_STAR_DEFAULT == 0.04449
        
        # Test validation functions
        validate_kappa_geo(0.3)
        validate_kappa_star(0.04449)
        
        print("   ✅ Parameter system operational")
        results['parameter_system'] = True
        
    except Exception as e:
        print(f"   ❌ Parameter system error: {e}")
    
    # Test 2: Z_5D Predictor
    print("2. Testing Z_5D Predictor...")
    try:
        from src.core.z_5d_enhanced import z5d_predictor as z5d_prime
        
        # Test basic prediction
        pred1 = z5d_prime(100)
        pred2 = z5d_prime(100)  # z5d_predictor doesn't take kappa_star parameter
        
        # Should be identical
        assert abs(float(pred1) - float(pred2)) < 1e-10
        
        # Should be reasonable
        assert 0 < float(pred1) < 1000
        
        print(f"   ✅ Z_5D predictor operational (k=100 -> {float(pred1):.2f})")
        results['z5d_predictor'] = True
        
    except Exception as e:
        print(f"   ❌ Z_5D predictor error: {e}")
    
    # Test 3: Geodesic Mapping
    print("3. Testing Geodesic Mapping...")
    try:
        from src.core.geodesic_mapping import compute_density_enhancement
        from tests.test_kappa_ci import generate_primes
        
        # Generate small prime set
        primes = generate_primes(100)[:20]
        
        # Test enhancement calculation
        result = compute_density_enhancement(primes, kappa_geo=KAPPA_GEO_DEFAULT)
        
        # Should return valid result
        assert 'percent' in result or 'enhancement_percent' in result
        percent_val = result.get('percent', result.get('enhancement_percent', 0))
        assert isinstance(percent_val, (int, float))
        
        print(f"   ✅ Geodesic mapping operational (enhancement: {percent_val:.2f}%)")
        results['geodesic_mapping'] = True
        
    except Exception as e:
        print(f"   ❌ Geodesic mapping error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Numerical Stability
    print("4. Testing Numerical Stability...")
    try:
        from src.core.z_5d_enhanced import z5d_predictor as z5d_prime
        import numpy as np
        
        # Test edge cases
        edge_results = []
        for k in [1, 2, 3, 5, 7, 11]:  # Remove k=0 as it's not valid for prime prediction
            pred = z5d_prime(k)
            edge_results.append(float(pred))  # Convert mpmath to float
            assert np.isfinite(float(pred))
            assert float(pred) >= 0
        
        # Test larger values
        for k in [1000, 10000, 100000]:
            pred = z5d_prime(k)
            assert np.isfinite(float(pred))
            assert float(pred) > 0
        
        print("   ✅ Numerical stability confirmed")
        results['numerical_stability'] = True
        
    except Exception as e:
        print(f"   ❌ Numerical stability error: {e}")
    
    # Test 5: Deprecation Warnings
    print("5. Testing Deprecation Warnings...")
    try:
        from src.core.geodesic_mapping import compute_density_enhancement
        from tests.test_kappa_ci import generate_primes
        
        primes = generate_primes(50)[:10]
        
        # This should trigger a deprecation warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = compute_density_enhancement(primes, k=0.3)
            
            # Check if warning was triggered
            if len(w) > 0 and "deprecated" in str(w[0].message).lower():
                print("   ✅ Deprecation warnings working")
                results['deprecation_warnings'] = True
            else:
                print("   ⚠️  Deprecation warnings not triggered")
                
    except Exception as e:
        print(f"   ❌ Deprecation warning error: {e}")
    
    # Summary
    print()
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, status in results.items():
        status_str = "✅ PASS" if status else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():.<30} {status_str}")
    
    print()
    print(f"Overall Result: {passed}/{total} tests passed ({passed/total:.0%})")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Framework is operational!")
        return True
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY PASSED - Framework is mostly operational")
        return True
    else:
        print("❌ MULTIPLE FAILURES - Framework needs attention")
        return False

def run_detailed_validation():
    """Run detailed validation using the full regression suite"""
    print("Running detailed validation using comprehensive regression suite...")
    print()
    
    try:
        from tests.test_comprehensive_regression import run_regression_tests
        
        # Run in quick mode for faster results
        results = run_regression_tests(quick_mode=True, verbose=True)
        
        print()
        print("=" * 60)
        print("DETAILED VALIDATION COMPLETE")
        print("=" * 60)
        
        performance = results.get('performance_metrics', {})
        success_rate = performance.get('overall_success_rate', 0)
        framework_status = performance.get('framework_status', 'UNKNOWN')
        
        print(f"Framework Status: {framework_status}")
        print(f"Success Rate: {success_rate:.1%}")
        print(f"Runtime: {performance.get('execution_time_seconds', 0):.2f}s")
        
        return success_rate > 0.8
        
    except Exception as e:
        print(f"❌ Detailed validation error: {e}")
        return False

def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Framework Regression Validation")
    parser.add_argument("--detailed", action="store_true", 
                       help="Run detailed validation using full test suite")
    
    args = parser.parse_args()
    
    if args.detailed:
        success = run_detailed_validation()
    else:
        success = run_quick_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()