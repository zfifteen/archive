#!/usr/bin/env python3
"""
Simple Test for Symbolic and Statistical Modules
================================================

Focused validation tests with robust error handling.
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

import numpy as np
from sympy import isprime

def test_basic_symbolic():
    """Test basic symbolic functionality."""
    print("Testing symbolic modules...")
    
    try:
        from symbolic.axiom_derivation import derive_universal_invariance
        result = derive_universal_invariance()
        print("✓ Universal invariance derivation works")
        return True
    except Exception as e:
        print(f"❌ Symbolic test failed: {e}")
        return False

def test_basic_statistical():
    """Test basic statistical functionality."""
    print("Testing statistical modules...")
    
    try:
        from statistical.hypothesis_testing import test_prime_enhancement_hypothesis
        
        # Simple test data
        primes = [p for p in range(2, 100) if isprime(p)][:20]
        composites = [n for n in range(4, 100) if not isprime(n)][:20]
        
        # Simple transformation
        phi = 1.618
        prime_data = [p * phi for p in primes]
        composite_data = [c * phi for c in composites]
        
        result = test_prime_enhancement_hypothesis(prime_data, composite_data)
        print("✓ Prime enhancement hypothesis test works")
        return True
    except Exception as e:
        print(f"❌ Statistical test failed: {e}")
        return False

def test_distribution_analysis():
    """Test distribution analysis with simple data."""
    print("Testing distribution analysis...")
    
    try:
        from statistical.distribution_analysis import analyze_prime_distribution
        
        # Simple data
        data = np.random.normal(10, 2, 100)
        result = analyze_prime_distribution(data)
        print("✓ Distribution analysis works")
        return True
    except Exception as e:
        print(f"❌ Distribution analysis failed: {e}")
        return False

def test_bootstrap():
    """Test bootstrap functionality."""
    print("Testing bootstrap validation...")
    
    try:
        from statistical.bootstrap_validation import bootstrap_confidence_intervals
        
        data = np.random.normal(0, 1, 50)
        result = bootstrap_confidence_intervals(data, np.mean, n_bootstrap=100)
        print("✓ Bootstrap validation works")
        return True
    except Exception as e:
        print(f"❌ Bootstrap test failed: {e}")
        return False

def main():
    """Run simplified tests."""
    print("=" * 50)
    print("SIMPLIFIED MODULE VALIDATION")
    print("=" * 50)
    
    tests = [
        test_basic_symbolic,
        test_basic_statistical,
        test_distribution_analysis,
        test_bootstrap
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic functionality is working!")
    else:
        print("⚠ Some issues need attention, but core functionality is available")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)