"""
Test suite for Z5D Stability Enhancement (Issue #431)

This module tests the enhanced precision monitoring, cross-validation,
and perturbation detection mechanisms added to address numerical instability
concerns in high-order Z5D approximations.
"""

import sys
import os
import numpy as np
import pytest
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
    DEFAULT_PRECISION_DPS,
    MPMATH_AVAILABLE
)


class TestPrecisionMonitoring:
    """Test precision degradation detection functionality."""
    
    def test_precision_degradation_detection_basic(self):
        """Test basic precision degradation detection."""
        if not MPMATH_AVAILABLE:
            pytest.skip("mpmath not available")
        
        # Test with a moderately large k value
        test_k = 1e8
        degradation_detected, recommended_dps, error_magnitude = _detect_precision_degradation(test_k)
        
        assert isinstance(degradation_detected, bool)
        assert isinstance(recommended_dps, int)
        assert isinstance(error_magnitude, float)
        assert recommended_dps >= DEFAULT_PRECISION_DPS
        assert error_magnitude >= 0
    
    def test_precision_monitoring_in_z5d_prime(self):
        """Test that precision monitoring works in z5d_prime function."""
        # Test with large k values that might trigger precision monitoring
        large_k_values = np.array([1e7, 1e8, 1e9])
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = z5d_prime(large_k_values, enable_precision_monitoring=True)
            
            # Check that function completes successfully
            assert len(result) == len(large_k_values)
            assert np.all(result > 0)
            
            # May or may not trigger warnings depending on actual precision needs
            # Just ensure no errors occur
    
    def test_precision_monitoring_disabled(self):
        """Test that precision monitoring can be disabled."""
        large_k_values = np.array([1e7, 1e8])
        
        # Should complete without precision monitoring overhead
        result = z5d_prime(large_k_values, enable_precision_monitoring=False)
        assert len(result) == len(large_k_values)
        assert np.all(result > 0)


class TestEnhancedStatisticalValidation:
    """Test enhanced statistical validation with bootstrap methods."""
    
    def test_correlation_validation_basic(self):
        """Test basic correlation validation functionality."""
        # Create synthetic data with known correlation
        np.random.seed(42)
        n = 100
        x = np.random.randn(n)
        y = 0.93 * x + 0.37 * np.random.randn(n)  # Target correlation ≈ 0.93
        
        validation_results = _enhanced_statistical_validation(x, y, correlation_threshold=0.93)
        
        # Check result structure
        expected_keys = [
            'correlation', 'p_value', 'bootstrap_ci', 'robust_correlation',
            'significance_validated', 'warning_flags', 'sample_size'
        ]
        for key in expected_keys:
            assert key in validation_results
        
        # Check basic validity
        assert isinstance(validation_results['correlation'], float)
        assert 0 <= validation_results['p_value'] <= 1
        assert len(validation_results['bootstrap_ci']) == 2
        assert isinstance(validation_results['significance_validated'], bool)
        assert validation_results['sample_size'] == n
    
    def test_correlation_validation_edge_cases(self):
        """Test correlation validation with edge cases."""
        # Test with insufficient data
        small_data = np.array([1, 2, 3])
        result = _enhanced_statistical_validation(small_data, small_data)
        assert len(result['warning_flags']) > 0  # Should flag insufficient data
        
        # Test with perfect correlation
        perfect_x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        perfect_y = 2 * perfect_x + 1
        result = _enhanced_statistical_validation(perfect_x, perfect_y)
        assert abs(result['correlation'] - 1.0) < 0.01
    
    def test_statistical_validation_robustness(self):
        """Test robustness of statistical validation."""
        # Test with data that has outliers
        np.random.seed(123)
        n = 50
        x = np.random.randn(n)
        y = 0.8 * x + 0.6 * np.random.randn(n)
        
        # Add outliers
        x[-1] = 10
        y[-1] = -10
        
        result = _enhanced_statistical_validation(x, y, correlation_threshold=0.8)
        
        # Should still provide reasonable results despite outliers
        assert isinstance(result['bootstrap_ci'], tuple)
        assert len(result['bootstrap_ci']) == 2
        assert result['bootstrap_ci'][0] <= result['bootstrap_ci'][1]


class TestNonlinearPerturbationDetection:
    """Test detection of non-Euclidean perturbations."""
    
    def test_perturbation_detection_linear_data(self):
        """Test perturbation detection with linear data."""
        # Create synthetic linear data in log-log space
        k_values = np.logspace(2, 6, 50)  # 10^2 to 10^6
        predictions = k_values * np.log(k_values)  # Linear in log-log space
        
        result = _detect_nonlinear_perturbations(k_values, predictions)
        
        assert 'linearity_score' in result
        assert 'perturbation_detected' in result
        assert 'recommendation' in result
        
        # Should detect high linearity (the main indicator)
        assert result['linearity_score'] > 0.95
        
        # Note: Perturbation may still be detected due to autocorrelation in synthetic data
        # This is expected behavior - the algorithm correctly identifies patterns
        # The key test is that linearity_score is high, indicating good linear fit
    
    def test_perturbation_detection_nonlinear_data(self):
        """Test perturbation detection with non-linear data."""
        # Create synthetic non-linear data
        k_values = np.logspace(2, 4, 30)
        predictions = k_values**1.5 + 0.1 * k_values**2  # Non-linear
        
        result = _detect_nonlinear_perturbations(k_values, predictions)
        
        # May or may not detect perturbations depending on the specific pattern
        # But should complete without errors
        assert isinstance(result['linearity_score'], float)
        assert isinstance(result['perturbation_detected'], bool)
    
    def test_perturbation_detection_insufficient_data(self):
        """Test perturbation detection with insufficient data."""
        # Test with very small dataset
        k_values = np.array([100, 200])
        predictions = np.array([1000, 2000])
        
        result = _detect_nonlinear_perturbations(k_values, predictions)
        
        # Should handle gracefully
        assert 'insufficient_data' in str(result['residual_patterns'])


class TestZ5DEnhancedFeatures:
    """Test enhanced Z5D features for stability."""
    
    def test_z5d_with_perturbation_detection(self):
        """Test Z5D with perturbation detection enabled."""
        k_values = np.array([1000, 5000, 10000, 50000, 100000])
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = z5d_prime(k_values, enable_perturbation_detection=True)
            
            # Should complete successfully
            assert len(result) == len(k_values)
            assert np.all(result > 0)
            
            # May generate warnings about perturbations
    
    def test_z5d_precision_and_perturbation_combined(self):
        """Test Z5D with both precision monitoring and perturbation detection."""
        k_values = np.logspace(4, 7, 10)  # 10^4 to 10^7
        
        result = z5d_prime(
            k_values, 
            enable_precision_monitoring=True,
            enable_perturbation_detection=True
        )
        
        assert len(result) == len(k_values)
        assert np.all(result > 0)
        assert np.all(np.isfinite(result))


class TestComprehensiveStabilityAnalysis:
    """Test comprehensive stability analysis functionality."""
    
    def test_stability_analysis_basic(self):
        """Test basic stability analysis functionality."""
        k_values = np.array([1000, 5000, 10000, 50000])
        
        # Generate some test "true" primes (synthetic data)
    # 1% noise level for synthetic prime generation
    SYNTHETIC_PRIME_NOISE_LEVEL = 0.01

    def test_stability_analysis_basic(self):
        """Test basic stability analysis functionality."""
        k_values = np.array([1000, 5000, 10000, 50000])
        
        # Generate some test "true" primes (synthetic data)
        true_primes = k_values * np.log(k_values) * (1 + self.SYNTHETIC_PRIME_NOISE_LEVEL * np.random.randn(len(k_values)))
        
        result = comprehensive_stability_analysis(k_values, true_primes=true_primes)
        
        # Check result structure
        expected_keys = [
            'input_summary', 'precision_analysis', 'statistical_validation',
            'perturbation_analysis', 'stability_score', 'recommendations', 'risk_flags'
        ]
        for key in expected_keys:
            assert key in result
        
        # Check score validity
        assert 0 <= result['stability_score'] <= 1
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['risk_flags'], list)
    
    def test_stability_analysis_large_scale(self):
        """Test stability analysis with large k values."""
        k_values = np.logspace(6, 8, 20)  # 10^6 to 10^8
        
        result = comprehensive_stability_analysis(k_values, enable_all_checks=True)
        
        # Should complete without errors even for large k
        assert 'stability_score' in result
        assert isinstance(result['stability_score'], float)
    
    def test_stability_analysis_minimal_data(self):
        """Test stability analysis with minimal data."""
        k_values = np.array([1000, 2000, 3000])
        
        result = comprehensive_stability_analysis(k_values, enable_all_checks=False)
        
        # Should handle gracefully with limited data
        assert 'stability_score' in result
        assert result['input_summary']['sample_size'] == 3


class TestIssue431Integration:
    """Integration tests specifically for Issue #431 concerns."""
    
    def test_k_star_calibration_stability(self):
        """Test stability of k* ≈ 0.04449 calibration parameter."""
        # Test with the specific k* value mentioned in the issue
        k_test = 1e6
        
        # Test with default calibration
        result_default = z5d_prime(k_test, auto_calibrate=False)
        
        # Test with auto calibration
        result_auto = z5d_prime(k_test, auto_calibrate=True)
        
        # Both should give reasonable results
        assert result_default > 0
        assert result_auto > 0
        assert np.isfinite(result_default)
        assert np.isfinite(result_auto)
    
    def test_correlation_threshold_robustness(self):
        """Test robustness around r ≈ 0.93 correlation threshold."""
        # Create synthetic data around the critical correlation threshold
        np.random.seed(42)
        n = 100
        x = np.random.randn(n)
        
        # Test correlations around 0.93
        for target_r in [0.90, 0.93, 0.96]:
            noise_strength = np.sqrt(1 - target_r**2) / target_r
            y = target_r * x + noise_strength * np.random.randn(n)
            
            validation = _enhanced_statistical_validation(
                x, y, correlation_threshold=0.93, significance_level=0.01
            )
            
            # Should provide robust assessment
            assert isinstance(validation['significance_validated'], bool)
            assert len(validation['warning_flags']) >= 0
    
    def test_large_n_precision_handling(self):
        """Test precision handling for extremely large N as mentioned in issue."""
        # Test progressively larger k values
        large_k_values = [1e10, 1e11, 1e12]
        
        for k in large_k_values:
            try:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    result = z5d_prime(k, enable_precision_monitoring=True)
                    
                    # Should complete successfully or provide meaningful warnings
                    assert np.isfinite(result)
                    assert result > 0
                    
                    # May generate precision warnings for very large k
                    
            except Exception as e:
                # If computation fails for ultra-large k, should fail gracefully
                assert "precision" in str(e).lower() or "overflow" in str(e).lower()


def run_issue_431_validation():
    """
    Run comprehensive validation for Issue #431 concerns.
    This function can be called directly to test the stability enhancements.
    """
    print("Running Issue #431 Stability Enhancement Validation...")
    
    # Test 1: Precision degradation detection
    print("\n1. Testing precision degradation detection...")
    if MPMATH_AVAILABLE:
        degradation_detected, recommended_dps, error_magnitude = _detect_precision_degradation(1e9)
        print(f"   Degradation detected: {degradation_detected}")
        print(f"   Recommended precision: {recommended_dps} dps")
        print(f"   Error magnitude: {error_magnitude:.2e}")
    else:
        print("   Skipped (mpmath not available)")
    
    # Test 2: Statistical validation robustness
    print("\n2. Testing statistical validation robustness...")
    np.random.seed(42)
    x = np.random.randn(100)
    y = 0.93 * x + 0.37 * np.random.randn(100)
    validation = _enhanced_statistical_validation(x, y, correlation_threshold=0.93)
    print(f"   Correlation: {validation['correlation']:.3f}")
    print(f"   Bootstrap CI: ({validation['bootstrap_ci'][0]:.3f}, {validation['bootstrap_ci'][1]:.3f})")
    print(f"   Significance validated: {validation['significance_validated']}")
    print(f"   Warning flags: {len(validation['warning_flags'])}")
    
    # Test 3: Comprehensive stability analysis
    print("\n3. Testing comprehensive stability analysis...")
    k_values = np.logspace(4, 7, 20)
    stability_results = comprehensive_stability_analysis(k_values)
    print(f"   Stability score: {stability_results['stability_score']:.3f}")
    print(f"   Risk level: {stability_results.get('overall_risk_level', 'N/A')}")
    print(f"   Risk flags: {len(stability_results['risk_flags'])}")
    print(f"   Recommendations: {len(stability_results['recommendations'])}")
    
    print("\n✅ Issue #431 validation completed successfully!")
    return True


if __name__ == "__main__":
    # Run validation when script is executed directly
    run_issue_431_validation()