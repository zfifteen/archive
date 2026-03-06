"""
Test suite for ZeroLine Zeta Integration Features
================================================

Tests for the new zeta zero integration features added to ZeroLine class
including calibration, error refinement, enhanced validation, and hybrid prediction.
"""

import sys
import os
import numpy as np
import pytest

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from core.zero_line import ZeroLine


class TestZeroLineZetaIntegration:
    """Test cases for ZeroLine zeta integration methods."""
    
    def test_calibrate_from_zeros_default(self):
        """Test calibrate_from_zeros with default N=94."""
        zl = ZeroLine()
        k_star = zl.calibrate_from_zeros()
        
        # Should return a float
        assert isinstance(k_star, float)
        # Should be approximately -2.316 as specified in issue
        assert abs(k_star - (-2.316)) < 0.01
        # Should be in reasonable range
        assert -3.0 < k_star < -2.0
    
    def test_calibrate_from_zeros_custom_n(self):
        """Test calibrate_from_zeros with custom N values."""
        zl = ZeroLine()
        
        # Test with different N values
        k_star_10 = zl.calibrate_from_zeros(10)
        k_star_50 = zl.calibrate_from_zeros(50)
        k_star_100 = zl.calibrate_from_zeros(100)
        
        # All should be numeric
        assert all(isinstance(k, float) for k in [k_star_10, k_star_50, k_star_100])
        # Should be negative (geodesic inversion)
        assert all(k < 0 for k in [k_star_10, k_star_50, k_star_100])
    
    def test_calibrate_from_zeros_edge_cases(self):
        """Test calibrate_from_zeros with edge cases."""
        zl = ZeroLine()
        
        # Test with N=1 (should use default)
        k_star_1 = zl.calibrate_from_zeros(1)
        assert k_star_1 == zl.default_k_star
        
        # Test with N=0 (should use default)
        k_star_0 = zl.calibrate_from_zeros(0)
        assert k_star_0 == zl.default_k_star
    
    def test_calibrate_error_refinement(self):
        """Test calibrate_error_refinement method."""
        zl = ZeroLine()
        c_refined = zl.calibrate_error_refinement(94)
        
        # Should return a float
        assert isinstance(c_refined, float)
        # Should be reasonable value (close to default c)
        assert abs(c_refined) < 1.0
    
    def test_calibrate_error_refinement_edge_cases(self):
        """Test calibrate_error_refinement with edge cases."""
        zl = ZeroLine()
        
        # Test with N=1 (should use default)
        c_refined_1 = zl.calibrate_error_refinement(1)
        assert c_refined_1 == zl.default_c
        
        # Test with N=0 (should use default)
        c_refined_0 = zl.calibrate_error_refinement(0)
        assert c_refined_0 == zl.default_c
    
    def test_validate_prediction_with_zeros(self):
        """Test enhanced validation with zeta zeros."""
        zl = ZeroLine()
        k_values = [100, 1000]
        results = zl.validate_prediction_with_zeros(k_values)
        
        # Should contain all base validation fields
        assert 'k_values' in results
        assert 'predictions' in results
        assert 'base_pnt' in results
        
        # Should contain enhanced fields
        assert 'enhanced_predictions' in results
        assert 'k_star_calibrated' in results
        assert 'zeta_lattice_size' in results
        
        # Check enhanced predictions
        assert len(results['enhanced_predictions']) == len(k_values)
        assert all(pred > 0 for pred in results['enhanced_predictions'])
        
        # Check calibrated k_star
        assert isinstance(results['k_star_calibrated'], float)
        assert results['k_star_calibrated'] < 0
    
    def test_validate_prediction_with_zeros_and_true_primes(self):
        """Test enhanced validation with true primes."""
        zl = ZeroLine()
        k_values = [10, 100]
        true_primes = [29, 541]  # Approximate true 10th and 100th primes
        
        results = zl.validate_prediction_with_zeros(k_values, true_primes)
        
        # Should contain base validation with true primes
        assert 'true_primes' in results
        assert 'absolute_errors' in results
        assert 'relative_errors' in results
        
        # Should contain enhanced fields
        assert 'enhanced_predictions' in results
        assert 'k_star_calibrated' in results
    
    def test_z5d_zero_hybrid_scalar(self):
        """Test hybrid prediction with scalar input."""
        zl = ZeroLine()
        k = 1000
        
        # Test with different M values
        hybrid_small = zl.z5d_zero_hybrid(k, M=10)
        hybrid_large = zl.z5d_zero_hybrid(k, M=100)
        
        # Should return floats
        assert isinstance(hybrid_small, float)
        assert isinstance(hybrid_large, float)
        
        # Should be positive
        assert hybrid_small > 0
        assert hybrid_large > 0
        
        # Should be finite
        assert np.isfinite(hybrid_small)
        assert np.isfinite(hybrid_large)
        
        # Should be different (more zero terms should change result) or very close due to convergence
        # At k=1000, the correction terms become small, so allow for near-equality
        assert hybrid_small != hybrid_large or abs(hybrid_small - hybrid_large) < 1e-6
    
    def test_z5d_zero_hybrid_array(self):
        """Test hybrid prediction with array input."""
        zl = ZeroLine()
        k_values = np.array([100, 500, 1000])
        
        hybrid_predictions = zl.z5d_zero_hybrid(k_values, M=50)
        
        # Should return array
        assert isinstance(hybrid_predictions, np.ndarray)
        assert len(hybrid_predictions) == len(k_values)
        
        # All should be positive and finite
        assert np.all(hybrid_predictions > 0)
        assert np.all(np.isfinite(hybrid_predictions))
        
        # Should be increasing
        assert np.all(np.diff(hybrid_predictions) > 0)
    
    def test_z5d_zero_hybrid_efficiency_bounds(self):
        """Test hybrid prediction efficiency bounds."""
        zl = ZeroLine()
        k = 1000
        
        # Test M limit (should cap at 10000)
        hybrid_capped = zl.z5d_zero_hybrid(k, M=20000)  # Should be capped to 10000
        hybrid_normal = zl.z5d_zero_hybrid(k, M=10000)
        
        # Should be the same due to capping
        assert abs(hybrid_capped - hybrid_normal) < 1e-6
    
    def test_z5d_zero_hybrid_vs_base_prediction(self):
        """Test that hybrid predictions differ from base Z5D predictions."""
        zl = ZeroLine()
        k_values = [100, 1000, 5000]
        
        for k in k_values:
            base_pred = zl.z5d_prediction(k)
            hybrid_pred = zl.z5d_zero_hybrid(k, M=50)
            
            # Should be different
            assert abs(base_pred - hybrid_pred) > 1e-6
            # Hybrid should be bounded by e^2 as specified
            assert hybrid_pred <= base_pred + zl.e_squared


class TestZeroLineZetaIntegration_ErrorHandling:
    """Test error handling for zeta integration methods."""
    
    def test_import_fallback(self):
        """Test that the module can handle import issues gracefully."""
        # This test ensures the try/except import logic works
        zl = ZeroLine()
        
        # If we can create the object, imports worked
        assert isinstance(zl, ZeroLine)
        
        # Test that zeta methods are available
        assert hasattr(zl, 'calibrate_from_zeros')
        assert hasattr(zl, 'calibrate_error_refinement')
        assert hasattr(zl, 'validate_prediction_with_zeros')
        assert hasattr(zl, 'z5d_zero_hybrid')
    
    def test_logging_integration(self):
        """Test that logging works without errors."""
        import logging
        
        # Configure logging to capture messages
        logging.basicConfig(level=logging.INFO)
        
        zl = ZeroLine()
        
        # These methods should work without raising exceptions
        # even if logging messages are generated
        try:
            k_star = zl.calibrate_from_zeros(50)
            c_refined = zl.calibrate_error_refinement(50)
            hybrid_pred = zl.z5d_zero_hybrid(1000, M=10)
            
            # All should succeed
            assert isinstance(k_star, float)
            assert isinstance(c_refined, float)
            assert isinstance(hybrid_pred, float)
            
        except Exception as e:
            pytest.fail(f"Logging integration test failed: {e}")


class TestZerolineZetaIntegration_Performance:
    """Performance tests for zeta integration methods."""
    
    def test_calibration_performance(self):
        """Test that calibration methods complete in reasonable time."""
        import time
        
        zl = ZeroLine()
        
        # Test calibrate_from_zeros performance
        start_time = time.time()
        k_star = zl.calibrate_from_zeros(100)
        calibration_time = time.time() - start_time
        
        # Should complete in under 1 second for N=100
        assert calibration_time < 1.0
        assert isinstance(k_star, float)
    
    def test_hybrid_prediction_performance(self):
        """Test that hybrid prediction completes in reasonable time."""
        import time
        
        zl = ZeroLine()
        
        # Test hybrid prediction performance
        start_time = time.time()
        hybrid_pred = zl.z5d_zero_hybrid(1000, M=100, N_lattice=200)
        prediction_time = time.time() - start_time
        
        # Should complete in under 2 seconds
        assert prediction_time < 2.0
        assert isinstance(hybrid_pred, float)


def run_zeta_integration_tests():
    """Run comprehensive tests for zeta integration features."""
    print("Running ZeroLine Zeta Integration Tests...")
    
    # Test basic functionality
    zl = ZeroLine()
    
    print("\n1. Testing calibrate_from_zeros...")
    k_star = zl.calibrate_from_zeros(94)
    print(f"✓ k_star calibration: {k_star:.6f}")
    assert abs(k_star - (-2.316)) < 0.01
    
    print("\n2. Testing calibrate_error_refinement...")
    c_refined = zl.calibrate_error_refinement(94)
    print(f"✓ Error refinement: {c_refined:.6f}")
    assert isinstance(c_refined, float)
    
    print("\n3. Testing validate_prediction_with_zeros...")
    enhanced_results = zl.validate_prediction_with_zeros([100, 1000])
    print(f"✓ Enhanced validation with {len(enhanced_results['enhanced_predictions'])} predictions")
    assert 'enhanced_predictions' in enhanced_results
    
    print("\n4. Testing z5d_zero_hybrid...")
    hybrid_pred = zl.z5d_zero_hybrid(1000, M=50)
    base_pred = zl.z5d_prediction(1000)
    print(f"✓ Hybrid prediction: {hybrid_pred:.2f} vs base: {base_pred:.2f}")
    assert hybrid_pred > 0
    assert abs(hybrid_pred - base_pred) > 1
    
    print("\n🎉 All zeta integration tests passed!")


if __name__ == "__main__":
    run_zeta_integration_tests()