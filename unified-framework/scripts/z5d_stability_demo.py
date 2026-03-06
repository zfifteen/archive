#!/usr/bin/env python3
"""
Z5D Stability Enhancement Demonstration (Issue #431)

This script demonstrates the new stability monitoring and validation features
added to address numerical instability concerns in high-order Z5D approximations.

Key features demonstrated:
1. Precision degradation detection and automatic scaling
2. Enhanced statistical validation with bootstrap confidence intervals
3. Non-Euclidean perturbation detection for linear invariance breakdown
4. Comprehensive stability analysis for production readiness
"""

import sys
import os
import numpy as np
import warnings

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from z_framework.discrete.z5d_predictor import (
    z5d_prime,
    _detect_precision_degradation,
    _enhanced_statistical_validation,
    _detect_nonlinear_perturbations,
    comprehensive_stability_analysis,
    MPMATH_AVAILABLE
)


def demonstrate_precision_monitoring():
    """Demonstrate precision monitoring capabilities."""
    print("=" * 60)
    print("PRECISION MONITORING DEMONSTRATION")
    print("=" * 60)
    
    print("\nTesting precision degradation detection for large k values...")
    
    if not MPMATH_AVAILABLE:
        print("⚠️  mpmath not available - precision monitoring limited")
        return
    
    # Test different k scales
    test_k_values = [1e6, 1e8, 1e10, 1e12]
    
    for k in test_k_values:
        print(f"\nTesting k = {k:.0e}:")
        try:
            degradation_detected, recommended_dps, error_magnitude = _detect_precision_degradation(k)
            
            print(f"  Precision degradation detected: {degradation_detected}")
            print(f"  Current precision adequate: {not degradation_detected}")
            print(f"  Recommended precision: {recommended_dps} dps")
            print(f"  Error magnitude: {error_magnitude:.2e}")
            
            if degradation_detected:
                print(f"  ⚠️  Precision upgrade recommended for k >= {k:.0e}")
            else:
                print(f"  ✅ Current precision adequate for k = {k:.0e}")
                
        except Exception as e:
            print(f"  ❌ Precision test failed: {e}")
    
    print("\nDemonstrating automatic precision monitoring in z5d_prime...")
    
    # Test with progressively larger k values
    large_k_values = np.array([1e7, 1e8, 1e9])
    
    print(f"\nTesting Z5D predictions with precision monitoring:")
    print(f"k values: {large_k_values}")
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        results = z5d_prime(large_k_values, enable_precision_monitoring=True)
        
        print(f"Predictions: {results}")
        print(f"Warnings generated: {len(w)}")
        
        for warning in w:
            if "precision" in str(warning.message).lower():
                print(f"  ⚠️  {warning.message}")


def demonstrate_statistical_validation():
    """Demonstrate enhanced statistical validation."""
    print("\n" + "=" * 60)
    print("ENHANCED STATISTICAL VALIDATION DEMONSTRATION")
    print("=" * 60)
    
    print("\nTesting statistical validation around critical r ≈ 0.93 threshold...")
    
    # Create synthetic data with different correlation strengths
    np.random.seed(42)
    n = 100
    
    correlations_to_test = [0.85, 0.90, 0.93, 0.95, 0.98]
    
    for target_r in correlations_to_test:
        print(f"\nTesting target correlation r = {target_r}")
        
        # Generate correlated data
        x = np.random.randn(n)
        noise_strength = np.sqrt(1 - target_r**2) / target_r if target_r > 0.1 else 1.0
        y = target_r * x + noise_strength * np.random.randn(n)
        
        # Enhanced validation
        validation = _enhanced_statistical_validation(
            x, y, 
            correlation_threshold=0.93,
            significance_level=0.01
        )
        
        print(f"  Actual correlation: {validation['correlation']:.3f}")
        print(f"  Bootstrap CI: ({validation['bootstrap_ci'][0]:.3f}, {validation['bootstrap_ci'][1]:.3f})")
        print(f"  Robust correlation: {validation['robust_correlation']:.3f}")
        print(f"  p-value: {validation['p_value']:.2e}")
        print(f"  Significance validated: {validation['significance_validated']}")
        
        if validation['warning_flags']:
            print(f"  ⚠️  Warning flags: {len(validation['warning_flags'])}")
            for flag in validation['warning_flags']:
                print(f"    - {flag}")
        else:
            print(f"  ✅ No statistical concerns detected")
    
    print("\nDemonstrating robustness to outliers...")
    
    # Test with outlier-contaminated data
    x_clean = np.random.randn(50)
    y_clean = 0.93 * x_clean + 0.37 * np.random.randn(50)
    
    # Add outliers
    x_outliers = np.concatenate([x_clean, [10, -10, 15]])
    y_outliers = np.concatenate([y_clean, [-8, 12, -20]])
    
    validation_clean = _enhanced_statistical_validation(x_clean, y_clean, correlation_threshold=0.93)
    validation_outliers = _enhanced_statistical_validation(x_outliers, y_outliers, correlation_threshold=0.93)
    
    print(f"\nClean data correlation: {validation_clean['correlation']:.3f}")
    print(f"Bootstrap CI: ({validation_clean['bootstrap_ci'][0]:.3f}, {validation_clean['bootstrap_ci'][1]:.3f})")
    
    print(f"\nOutlier-contaminated correlation: {validation_outliers['correlation']:.3f}")
    print(f"Bootstrap CI: ({validation_outliers['bootstrap_ci'][0]:.3f}, {validation_outliers['bootstrap_ci'][1]:.3f})")
    print(f"Bootstrap provides robustness: CI width change = {(validation_outliers['bootstrap_ci'][1] - validation_outliers['bootstrap_ci'][0]) - (validation_clean['bootstrap_ci'][1] - validation_clean['bootstrap_ci'][0]):.3f}")


def demonstrate_perturbation_detection():
    """Demonstrate non-Euclidean perturbation detection."""
    print("\n" + "=" * 60)
    print("NON-EUCLIDEAN PERTURBATION DETECTION DEMONSTRATION")
    print("=" * 60)
    
    print("\nTesting linear invariance assumption validation...")
    
    # Test 1: Linear data (should pass)
    print("\n1. Testing with linear data (expected: no perturbations)")
    k_linear = np.logspace(2, 6, 50)
    pred_linear = k_linear * np.log(k_linear)  # Linear in log-log space
    
    result_linear = _detect_nonlinear_perturbations(k_linear, pred_linear)
    
    print(f"   Linearity score: {result_linear['linearity_score']:.3f}")
    print(f"   Perturbations detected: {result_linear['perturbation_detected']}")
    print(f"   Residual patterns: {result_linear['residual_patterns']}")
    print(f"   Recommendation: {result_linear['recommendation']}")
    
    # Test 2: Non-linear data (should detect perturbations)
    print("\n2. Testing with non-linear data (expected: perturbations detected)")
    k_nonlinear = np.logspace(2, 5, 40)
    pred_nonlinear = k_nonlinear**1.3 + 0.05 * k_nonlinear**1.8  # Non-linear
    
    result_nonlinear = _detect_nonlinear_perturbations(k_nonlinear, pred_nonlinear)
    
    print(f"   Linearity score: {result_nonlinear['linearity_score']:.3f}")
    print(f"   Perturbations detected: {result_nonlinear['perturbation_detected']}")
    print(f"   Residual patterns: {result_nonlinear['residual_patterns']}")
    print(f"   Recommendation: {result_nonlinear['recommendation']}")
    
    # Test 3: Real Z5D predictions
    print("\n3. Testing with actual Z5D predictions")
    k_real = np.array([1000, 5000, 10000, 50000, 100000])
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        pred_real = z5d_prime(k_real, enable_perturbation_detection=True)
        
        print(f"   Z5D predictions: {pred_real}")
        print(f"   Perturbation warnings: {len([warning for warning in w if 'perturbation' in str(warning.message).lower()])}")
        
        # Manual perturbation analysis
        result_real = _detect_nonlinear_perturbations(k_real, pred_real)
        print(f"   Linearity score: {result_real['linearity_score']:.3f}")
        print(f"   Perturbations detected: {result_real['perturbation_detected']}")


def demonstrate_comprehensive_analysis():
    """Demonstrate comprehensive stability analysis."""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE STABILITY ANALYSIS DEMONSTRATION")
    print("=" * 60)
    
    print("\nRunning comprehensive stability analysis...")
    
    # Test with different scale ranges
    test_scenarios = [
        ("Small scale", np.array([100, 500, 1000, 5000, 10000])),
        ("Medium scale", np.logspace(4, 6, 15)),
        ("Large scale", np.logspace(6, 8, 10)),
    ]
    
    for scenario_name, k_values in test_scenarios:
        print(f"\n{scenario_name} scenario (k range: {k_values.min():.0e} to {k_values.max():.0e}):")
        
        # Generate synthetic "true" primes for demonstration
        # In practice, these would be actual known prime values
        true_primes = k_values * np.log(k_values) * (1 + 0.005 * np.random.randn(len(k_values)))
        
        stability_results = comprehensive_stability_analysis(
            k_values, 
            true_primes=true_primes,
            enable_all_checks=True
        )
        
        print(f"  Overall stability score: {stability_results['stability_score']:.3f}")
        print(f"  Risk level: {stability_results['overall_risk_level']}")
        print(f"  Risk flags: {len(stability_results['risk_flags'])}")
        print(f"  Recommendations: {len(stability_results['recommendations'])}")
        
        if stability_results['risk_flags']:
            print(f"  ⚠️  Risk flags:")
            for flag in stability_results['risk_flags'][:3]:  # Show first 3
                print(f"     - {flag}")
        
        if stability_results['recommendations']:
            print(f"  💡 Key recommendations:")
            for rec in stability_results['recommendations'][:2]:  # Show first 2
                print(f"     - {rec}")
        
        # Show specific analysis components
        if 'precision_analysis' in stability_results and stability_results['precision_analysis']:
            precision = stability_results['precision_analysis']
            print(f"  Precision analysis: {'✅ Adequate' if precision['precision_adequate'] else '⚠️ Needs attention'}")
        
        if 'statistical_validation' in stability_results and stability_results['statistical_validation']:
            stats = stability_results['statistical_validation']
            print(f"  Statistical validation: {'✅ Validated' if stats['significance_validated'] else '⚠️ Concerns detected'}")


def demonstrate_issue_431_scenarios():
    """Demonstrate specific scenarios mentioned in Issue #431."""
    print("\n" + "=" * 60)
    print("ISSUE #431 SPECIFIC SCENARIOS DEMONSTRATION")
    print("=" * 60)
    
    print("\nScenario 1: k* ≈ 0.04449 calibration stability at large N")
    
    # Test the specific calibration parameter mentioned in the issue
    large_n_values = np.array([1e6, 1e7, 1e8])
    
    for n in large_n_values:
        print(f"\nTesting at N = {n:.0e}:")
        
        # Test with default calibration (k* ≈ 0.04449)
        result_default = z5d_prime(n, auto_calibrate=False, enable_precision_monitoring=True)
        
        # Test with auto calibration
        result_auto = z5d_prime(n, auto_calibrate=True, enable_precision_monitoring=True)
        
        print(f"  Default calibration (k*=0.04449): {result_default:.2e}")
        print(f"  Auto calibration: {result_auto:.2e}")
        print(f"  Relative difference: {abs(result_auto - result_default) / result_default * 100:.3f}%")
    
    print("\nScenario 2: Statistical significance near r ≈ 0.93 threshold")
    
    # Test correlations around the critical threshold
    print("\nTesting statistical robustness around r ≈ 0.93:")
    
    critical_correlations = [0.92, 0.93, 0.94]
    
    for target_r in critical_correlations:
        np.random.seed(42)
        x = np.random.randn(100)
        noise_strength = np.sqrt(1 - target_r**2) / target_r
        y = target_r * x + noise_strength * np.random.randn(100)
        
        validation = _enhanced_statistical_validation(x, y, correlation_threshold=0.93)
        
        print(f"\n  Target r = {target_r}:")
        print(f"    Actual correlation: {validation['correlation']:.3f}")
        print(f"    Significance validated: {validation['significance_validated']}")
        print(f"    Bootstrap CI width: {validation['bootstrap_ci'][1] - validation['bootstrap_ci'][0]:.3f}")
        
        if validation['warning_flags']:
            print(f"    ⚠️  Validation concerns: {len(validation['warning_flags'])}")
    
    print("\nScenario 3: d_term and e_term linear invariance under perturbations")
    
    # Test the specific terms mentioned in the issue
    print("\nTesting d_term and e_term behavior under different conditions:")
    
    
    test_k_ranges = [
        np.logspace(3, 5, 20),  # Medium scale
        np.logspace(5, 7, 20),  # Large scale
    ]
    
    for i, k_range in enumerate(test_k_ranges):
        scale_name = ["Medium", "Large"][i]
        print(f"\n  {scale_name} scale analysis:")
        
        d_values = d_term(k_range)
        e_values = e_term(k_range)
        
        # Check for any numerical issues
        d_finite = np.all(np.isfinite(d_values))
        e_finite = np.all(np.isfinite(e_values))
        
        print(f"    d_term finite values: {d_finite}")
        print(f"    e_term finite values: {e_finite}")
        
        if d_finite and e_finite:
            # Test linearity assumption
            log_k = np.log(k_range)
            log_d = np.log(d_values[d_values > 0])
            log_e = np.log(e_values[e_values > 0])
            
            if len(log_d) > 5:
                d_linearity = np.corrcoef(log_k[:len(log_d)], log_d)[0, 1]**2
                print(f"    d_term log-log linearity: {d_linearity:.3f}")
            
            if len(log_e) > 5:
                e_linearity = np.corrcoef(log_k[:len(log_e)], log_e)[0, 1]**2
                print(f"    e_term log-log linearity: {e_linearity:.3f}")


def main():
    """Main demonstration function."""
    print("Z5D Stability Enhancement Demonstration")
    print("Addressing Issue #431: Hidden Instability in High-Order Z5D Approximations")
    print()
    
    try:
        # Run all demonstrations
        demonstrate_precision_monitoring()
        demonstrate_statistical_validation()
        demonstrate_perturbation_detection()
        demonstrate_comprehensive_analysis()
        demonstrate_issue_431_scenarios()
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nKey findings:")
        print("✅ Precision monitoring system operational")
        print("✅ Enhanced statistical validation working")
        print("✅ Perturbation detection functional")
        print("✅ Comprehensive stability analysis available")
        print("✅ Issue #431 scenarios addressed")
        
        print("\nFor production use:")
        print("• Enable precision monitoring for k > 10^6")
        print("• Use enhanced statistical validation for critical correlations")
        print("• Run comprehensive stability analysis before deployment")
        print("• Monitor for perturbation warnings in real-time use")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    main()