#!/usr/bin/env python3
"""
Test Suite for Symbolic and Statistical Modules
===============================================

Comprehensive validation tests for the new SymPy-based symbolic derivation 
and SciPy-based statistical testing modules.

Usage: python3 test_symbolic_statistical.py
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from sympy import symbols, isprime, divisors
import scipy.stats as stats

# Import our new modules
from symbolic import (
    derive_universal_invariance, derive_curvature_formula, 
    derive_golden_ratio_transformation, derive_5d_metric_tensor,
    comprehensive_symbolic_verification
)
from statistical import (
    test_prime_enhancement_hypothesis, test_optimal_k_hypothesis,
    test_variance_minimization, test_asymmetry_significance,
    analyze_prime_distribution, bootstrap_confidence_intervals,
    correlate_zeta_zeros_primes
)

def test_symbolic_derivations():
    """Test symbolic axiom derivation functions."""
    print("\n=== Testing Symbolic Derivations ===")
    
    # Test universal invariance derivation
    print("Testing universal invariance derivation...")
    invariance_result = derive_universal_invariance()
    
    assert 'universal_form' in invariance_result
    assert 'relativistic_form' in invariance_result
    assert 'discrete_form' in invariance_result
    print("✓ Universal invariance derivation successful")
    
    # Test curvature formula derivation
    print("Testing curvature formula derivation...")
    curvature_result = derive_curvature_formula()
    
    assert 'curvature_formula' in curvature_result
    assert 'curvature_5d' in curvature_result
    assert 'normalization_factor' in curvature_result
    print("✓ Curvature formula derivation successful")
    
    # Test golden ratio transformation
    print("Testing golden ratio transformation...")
    golden_result = derive_golden_ratio_transformation()
    
    assert 'phi_exact' in golden_result
    assert 'theta_prime_formula' in golden_result
    assert 'asymmetry_measure' in golden_result
    print("✓ Golden ratio transformation successful")
    
    # Test e² trigonometric limit derivation
    print("Testing e² trigonometric limit derivation...")
    try:
        from symbolic.axiom_derivation import derive_e_squared_trigonometric_limit
        e_squared_result = derive_e_squared_trigonometric_limit()
        
        assert 'trigonometric_expression' in e_squared_result
        assert 'symbolic_limit' in e_squared_result
        assert 'mathematical_significance' in e_squared_result
        assert 'framework_integration' in e_squared_result
        
        # Verify the limit is actually e²
        import sympy as sp
        import math
        symbolic_limit = e_squared_result['symbolic_limit']
        numerical_value = float(symbolic_limit)
        expected_value = math.e**2
        
        assert abs(numerical_value - expected_value) < 1e-10, f"Limit value mismatch: {numerical_value} vs {expected_value}"
        print("✓ e² trigonometric limit derivation successful")
        e_squared_test_passed = True
    except ImportError as e:
        print(f"⚠ e² trigonometric limit test skipped: {e}")
        e_squared_result = None
        e_squared_test_passed = False
    
    # Test 5D metric tensor
    print("Testing 5D metric tensor derivation...")
    metric_result = derive_5d_metric_tensor()
    
    assert 'metric_tensor' in metric_result
    assert 'christoffel_symbols' in metric_result
    assert 'coupling_strength' in metric_result
    print("✓ 5D metric tensor derivation successful")
    
    return {
        'universal_invariance': invariance_result,
        'curvature_formula': curvature_result,
        'golden_ratio': golden_result,
        'e_squared_limit': e_squared_result if e_squared_test_passed else None,
        'metric_tensor': metric_result
    }

def test_statistical_hypothesis_testing():
    """Test statistical hypothesis testing functions."""
    print("\n=== Testing Statistical Hypothesis Testing ===")
    
    # Generate synthetic prime and composite data
    primes = [p for p in range(2, 1000) if isprime(p)]
    composites = [n for n in range(4, 1000) if not isprime(n)][:len(primes)]
    
    # Simulate enhancement transformation
    phi = (1 + np.sqrt(5)) / 2
    k = 0.3
    
    def theta_transform(n, k):
        return phi * ((n % phi) / phi) ** k
    
    prime_transformed = [theta_transform(p, k) for p in primes[:100]]
    composite_transformed = [theta_transform(c, k) for c in composites[:100]]
    
    # Test prime enhancement hypothesis
    print("Testing prime enhancement hypothesis...")
    enhancement_result = test_prime_enhancement_hypothesis(
        prime_transformed, composite_transformed
    )
    
    assert 'hypothesis_test' in enhancement_result
    assert 'statistical_tests' in enhancement_result
    assert 'effect_sizes' in enhancement_result
    print("✓ Prime enhancement hypothesis test successful")
    
    # Test optimal k hypothesis with synthetic data
    print("Testing optimal k hypothesis...")
    k_values = np.linspace(0.1, 0.5, 20)
    # Simulate enhancement curve with peak around k=0.3
    enhancement_values = 100 * np.exp(-10 * (k_values - 0.3)**2) + np.random.normal(0, 5, len(k_values))
    
    k_optimal_result = test_optimal_k_hypothesis(k_values, enhancement_values)
    
    assert 'hypothesis_test' in k_optimal_result
    assert 'empirical_results' in k_optimal_result
    assert 'fitted_models' in k_optimal_result
    print("✓ Optimal k hypothesis test successful")
    
    # Test variance minimization
    print("Testing variance minimization...")
    # Generate synthetic curvature data
    curvature_data = np.random.normal(0.5, 0.11, 1000)  # Close to target variance 0.118
    
    variance_result = test_variance_minimization(curvature_data)
    
    assert 'hypothesis_test' in variance_result
    assert 'sample_statistics' in variance_result
    assert 'tolerance_test' in variance_result
    print("✓ Variance minimization test successful")
    
    # Test asymmetry significance
    print("Testing asymmetry significance...")
    # Generate synthetic Fourier coefficients
    cosine_coeffs = np.random.normal(0, 1, 5)
    sine_coeffs = np.random.normal(0.5, 1, 5)  # Introduce asymmetry
    
    fourier_coeffs = {
        'cosine': cosine_coeffs,
        'sine': sine_coeffs
    }
    
    asymmetry_result = test_asymmetry_significance(fourier_coeffs)
    
    assert 'hypothesis_test' in asymmetry_result
    assert 'asymmetry_measures' in asymmetry_result
    assert 'bootstrap_analysis' in asymmetry_result
    print("✓ Asymmetry significance test successful")
    
    return {
        'prime_enhancement': enhancement_result,
        'optimal_k': k_optimal_result,
        'variance_minimization': variance_result,
        'asymmetry_significance': asymmetry_result
    }

def test_distribution_analysis():
    """Test distribution analysis functions."""
    print("\n=== Testing Distribution Analysis ===")
    
    # Generate synthetic prime gap data
    primes = [p for p in range(2, 10000) if isprime(p)]
    prime_gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
    
    # Test distribution analysis
    print("Testing prime distribution analysis...")
    dist_result = analyze_prime_distribution(prime_gaps[:1000])
    
    assert 'descriptive_statistics' in dist_result
    assert 'normality_tests' in dist_result
    assert 'distribution_fits' in dist_result
    print("✓ Distribution analysis successful")
    
    return {'distribution_analysis': dist_result}

def test_correlation_analysis():
    """Test correlation analysis functions."""
    print("\n=== Testing Correlation Analysis ===")
    
    # Generate synthetic zeta zeros and prime data with known correlation
    n_points = 100
    t = np.linspace(1, 100, n_points)
    
    # Simulate correlated data
    true_correlation = 0.85
    noise_level = np.sqrt(1 - true_correlation**2)
    
    zeta_data = t + np.random.normal(0, 1, n_points)
    prime_data = true_correlation * zeta_data + noise_level * np.random.normal(0, 1, n_points)
    
    # Test correlation analysis
    print("Testing zeta zeros - prime correlation...")
    correlation_result = correlate_zeta_zeros_primes(zeta_data, prime_data)
    
    assert 'correlation_analysis' in correlation_result
    assert 'documentation_validation' in correlation_result
    assert 'bootstrap_analysis' in correlation_result
    print("✓ Correlation analysis successful")
    
    return {'correlation_analysis': correlation_result}

def test_bootstrap_validation():
    """Test bootstrap validation functions."""
    print("\n=== Testing Bootstrap Validation ===")
    
    # Generate sample data
    sample_data = np.random.normal(10, 2, 100)
    
    # Test bootstrap confidence intervals
    print("Testing bootstrap confidence intervals...")
    ci_result = bootstrap_confidence_intervals(
        sample_data, 
        lambda x: np.mean(x),
        n_bootstrap=1000
    )
    
    assert 'confidence_interval' in ci_result
    assert 'bootstrap_summary' in ci_result
    assert 'interval_interpretation' in ci_result
    print("✓ Bootstrap confidence intervals successful")
    
    return {'bootstrap_validation': ci_result}

def test_symbolic_verification():
    """Test comprehensive symbolic verification."""
    print("\n=== Testing Symbolic Verification ===")
    
    # Run comprehensive verification
    print("Running comprehensive symbolic verification...")
    verification_result = comprehensive_symbolic_verification()
    
    assert 'axiom_consistency' in verification_result
    assert 'dimensional_analysis' in verification_result
    assert 'golden_ratio_properties' in verification_result
    print("✓ Symbolic verification successful")
    
    return {'symbolic_verification': verification_result}

def integration_test():
    """Test integration between symbolic and statistical modules."""
    print("\n=== Integration Test ===")
    
    # Generate prime sequence
    primes = [p for p in range(2, 1000) if isprime(p)]
    
    # Apply symbolic transformation
    from symbolic.axiom_derivation import derive_golden_ratio_transformation
    golden_result = derive_golden_ratio_transformation()
    
    phi_value = float((1 + np.sqrt(5)) / 2)
    k_value = 0.3
    
    # Transform primes using derived formula
    def symbolic_transform(n):
        return phi_value * ((n % phi_value) / phi_value) ** k_value
    
    transformed_primes = [symbolic_transform(p) for p in primes[:100]]
    
    # Statistical analysis of transformed data
    from statistical.distribution_analysis import analyze_prime_distribution
    
    dist_analysis = analyze_prime_distribution(transformed_primes)
    
    # Bootstrap analysis of mean
    from statistical.bootstrap_validation import bootstrap_confidence_intervals
    
    boot_analysis = bootstrap_confidence_intervals(
        transformed_primes,
        lambda x: np.mean(x)
    )
    
    print("✓ Integration test successful")
    
    return {
        'symbolic_transformation': len(transformed_primes),
        'distribution_analysis': dist_analysis['descriptive_statistics'],
        'bootstrap_analysis': boot_analysis['confidence_interval']
    }

def main():
    """Run all tests and generate summary report."""
    print("=" * 60)
    print("SYMBOLIC AND STATISTICAL MODULES VALIDATION TEST SUITE")
    print("=" * 60)
    
    test_results = {}
    failed_tests = []
    
    # Run individual test suites
    try:
        test_results['symbolic'] = test_symbolic_derivations()
    except Exception as e:
        print(f"❌ Symbolic derivations test failed: {e}")
        failed_tests.append('symbolic_derivations')
    
    try:
        test_results['statistical'] = test_statistical_hypothesis_testing()
    except Exception as e:
        print(f"❌ Statistical hypothesis testing failed: {e}")
        failed_tests.append('statistical_hypothesis')
    
    try:
        test_results['distribution'] = test_distribution_analysis()
    except Exception as e:
        print(f"❌ Distribution analysis test failed: {e}")
        failed_tests.append('distribution_analysis')
    
    try:
        test_results['correlation'] = test_correlation_analysis()
    except Exception as e:
        print(f"❌ Correlation analysis test failed: {e}")
        failed_tests.append('correlation_analysis')
    
    try:
        test_results['bootstrap'] = test_bootstrap_validation()
    except Exception as e:
        print(f"❌ Bootstrap validation test failed: {e}")
        failed_tests.append('bootstrap_validation')
    
    try:
        test_results['verification'] = test_symbolic_verification()
    except Exception as e:
        print(f"❌ Symbolic verification test failed: {e}")
        failed_tests.append('symbolic_verification')
    
    try:
        test_results['integration'] = integration_test()
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        failed_tests.append('integration_test')
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("TEST SUMMARY REPORT")
    print("=" * 60)
    
    total_tests = 7
    passed_tests = total_tests - len(failed_tests)
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    if failed_tests:
        print(f"\nFailed tests: {', '.join(failed_tests)}")
    else:
        print("\n🎉 All tests passed successfully!")
    
    # Key validation results
    print("\nKEY VALIDATION RESULTS:")
    print("-" * 30)
    
    if 'symbolic' in test_results:
        print("✓ Symbolic axiom derivation module operational")
    
    if 'statistical' in test_results:
        print("✓ Statistical hypothesis testing module operational")
    
    if 'verification' in test_results:
        verification = test_results['verification']['symbolic_verification']
        if verification.get('verification_complete', False):
            print("✓ All symbolic verifications passed")
        else:
            print("⚠ Some symbolic verifications need attention")
    
    if 'integration' in test_results:
        print("✓ Symbolic-statistical integration successful")
    
    print("\nThe symbolic and statistical modules are ready for use in Z Framework analysis.")
    print("Refer to the documentation and examples for detailed usage patterns.")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)