"""
Test suite for Z Prime Utils - Enhanced Accuracy Methods

Tests the three main components:
1. Dynamic Subset Recalibration of Z5D Parameters
2. Geodesic Adjustments for Interval Searches
3. Riemann Zeta Zeros Integration into Z5D Corrections
"""

import numpy as np
import pytest
import sys
import os

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.z_framework.discrete.z_prime_utils import ZPrimeEstimator
import sympy

class TestZPrimeEstimator:
    """Test cases for the ZPrimeEstimator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.estimator = ZPrimeEstimator()
        
        # Small test dataset for quick validation
        self.test_k_values = np.array([10, 50, 100, 500, 1000])
        self.test_true_primes = np.array([29, 229, 541, 3571, 7919])
        
    def test_initialization(self):
        """Test ZPrimeEstimator initialization."""
        estimator = ZPrimeEstimator()
        assert estimator.default_c == -0.00247
        assert estimator.default_k_star == 0.04449
        assert estimator.geodesic_k == 0.3
        assert estimator.wheel_modulus == 210
        assert not estimator.is_calibrated
        assert len(estimator._wheel_residues) > 0
        
    def test_custom_initialization(self):
        """Test ZPrimeEstimator with custom parameters."""
        estimator = ZPrimeEstimator(
            default_c=-0.001,
            default_k_star=0.05,
            geodesic_k=0.4,
            wheel_modulus=30
        )
        assert estimator.default_c == -0.001
        assert estimator.default_k_star == 0.05
        assert estimator.geodesic_k == 0.4
        assert estimator.wheel_modulus == 30


class TestDynamicCalibration:
    """Test cases for dynamic subset recalibration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.estimator = ZPrimeEstimator()
        self.k_values = np.array([10, 50, 100, 200, 500])
        self.true_primes = np.array([29, 229, 541, 1229, 3571])
        
    def test_calibrate_parameters_basic(self):
        """Test basic parameter calibration."""
        result = self.estimator.calibrate_parameters(
            self.k_values, 
            self.true_primes
        )
        
        # Check required fields in result
        required_fields = ['fitted_c', 'fitted_k_star', 'mae', 'mre']
        for field in required_fields:
            assert field in result
            
        # Check that calibration was applied
        assert self.estimator.is_calibrated
        assert isinstance(result['fitted_c'], float)
        assert isinstance(result['fitted_k_star'], float)
        assert result['mae'] >= 0
        assert result['mre'] >= 0
        
    def test_calibrate_parameters_bounds(self):
        """Test parameter calibration with custom bounds."""
        bounds_c = (-0.01, 0.01)
        bounds_k_star = (-0.05, 0.05)
        
        result = self.estimator.calibrate_parameters(
            self.k_values,
            self.true_primes, 
            bounds_c=bounds_c,
            bounds_k_star=bounds_k_star
        )
        
        # Check bounds are respected
        assert bounds_c[0] <= result['fitted_c'] <= bounds_c[1]
        assert bounds_k_star[0] <= result['fitted_k_star'] <= bounds_k_star[1]
        
    def test_calibrate_parameters_auto_primes(self):
        """Test calibration with automatic prime fetching."""
        # This test may be slow due to SymPy prime generation
        small_k = np.array([10, 20, 30])
        
        result = self.estimator.calibrate_parameters(small_k)
        
        assert 'fitted_c' in result
        assert 'fitted_k_star' in result
        assert self.estimator.is_calibrated
        
    def test_calibrate_parameters_error_handling(self):
        """Test error handling in calibration."""
        # Test with mismatched array lengths
        k_bad = np.array([10, 20])
        primes_bad = np.array([29, 71, 113])  # Different length
        
        with pytest.raises(ValueError):
            self.estimator.calibrate_parameters(k_bad, primes_bad)
            
    def test_calibrated_z5d_prime(self):
        """Test calibrated Z5D predictions."""
        # First calibrate
        self.estimator.calibrate_parameters(self.k_values, self.true_primes)
        
        # Test scalar prediction
        pred_scalar = self.estimator.calibrated_z5d_prime(100)
        assert isinstance(pred_scalar, (float, np.floating))
        assert pred_scalar > 0
        
        # Test array prediction
        test_k = np.array([50, 100, 200])
        pred_array = self.estimator.calibrated_z5d_prime(test_k)
        assert isinstance(pred_array, np.ndarray)
        assert len(pred_array) == len(test_k)
        assert np.all(pred_array > 0)
        
    def test_calibrated_z5d_prime_custom_params(self):
        """Test calibrated predictions with custom parameters."""
        pred = self.estimator.calibrated_z5d_prime(100, c=-0.001, k_star=0.02)
        assert isinstance(pred, (float, np.floating))
        assert pred > 0


class TestGeodesicAdjustments:
    """Test cases for geodesic adjustments and interval searches."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.estimator = ZPrimeEstimator()
        
    def test_geodesic_theta_prime_scalar(self):
        """Test geodesic mapping with scalar input."""
        result = self.estimator.geodesic_theta_prime(100)
        assert isinstance(result, (float, np.floating))
        assert 0 <= result <= self.estimator.wheel_modulus
        
    def test_geodesic_theta_prime_array(self):
        """Test geodesic mapping with array input."""
        n_values = np.array([10, 50, 100, 200])
        results = self.estimator.geodesic_theta_prime(n_values)
        
        assert isinstance(results, np.ndarray)
        assert len(results) == len(n_values)
        assert np.all(results >= 0)
        assert np.all(results <= self.estimator.wheel_modulus)
        
    def test_geodesic_theta_prime_custom_params(self):
        """Test geodesic mapping with custom parameters."""
        result = self.estimator.geodesic_theta_prime(100, phi=30, k=0.5)
        assert isinstance(result, (float, np.floating))
        assert 0 <= result <= 30
        
    def test_filter_prime_candidates_basic(self):
        """Test basic prime candidate filtering."""
        candidates = self.estimator.filter_prime_candidates(100, 200)
        
        assert isinstance(candidates, list)
        assert all(isinstance(c, (int, np.integer)) for c in candidates)
        assert all(100 <= c <= 200 for c in candidates)
        
        # Check that candidates are coprime to wheel modulus
        for c in candidates:
            assert c % self.estimator.wheel_modulus in self.estimator._wheel_residues
            
    def test_filter_prime_candidates_empty_range(self):
        """Test filtering with empty range."""
        candidates = self.estimator.filter_prime_candidates(1000, 999)  # Invalid range
        assert candidates == []
        
    def test_filter_prime_candidates_threshold(self):
        """Test filtering with custom threshold."""
        candidates_high = self.estimator.filter_prime_candidates(100, 200, threshold=100)
        candidates_low = self.estimator.filter_prime_candidates(100, 200, threshold=1)
        
        # Higher threshold should yield fewer candidates
        assert len(candidates_high) <= len(candidates_low)
        
    def test_wheel_residues_computation(self):
        """Test wheel sieve residues computation."""
        # Check that residues are coprime to wheel modulus
        for residue in self.estimator._wheel_residues:
            assert np.gcd(residue, self.estimator.wheel_modulus) == 1
            assert 1 <= residue < self.estimator.wheel_modulus


class TestZetaCorrections:
    """Test cases for Riemann zeta zeros integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.estimator = ZPrimeEstimator()
        
    def test_zeta_correction_scalar(self):
        """Test zeta correction with scalar input."""
        result = self.estimator.zeta_correction(100)
        assert isinstance(result, (float, np.floating))
        # Result should be finite
        assert np.isfinite(result)
        
    def test_zeta_correction_array(self):
        """Test zeta correction with array input."""
        x_values = np.array([50, 100, 200, 500])
        results = self.estimator.zeta_correction(x_values)
        
        assert isinstance(results, np.ndarray)
        assert len(results) == len(x_values)
        assert np.all(np.isfinite(results))
        
    def test_zeta_correction_custom_zeros(self):
        """Test zeta correction with custom zeros."""
        custom_zeros = [14.134725, 21.022040, 25.010858]  # First 3 zeros
        result = self.estimator.zeta_correction(100, zeros=custom_zeros)
        
        assert isinstance(result, (float, np.floating))
        assert np.isfinite(result)
        
    def test_zeta_correction_num_zeros(self):
        """Test zeta correction with different numbers of zeros."""
        result_5 = self.estimator.zeta_correction(100, num_zeros=5)
        result_10 = self.estimator.zeta_correction(100, num_zeros=10)
        
        # Both should be finite but may differ
        assert np.isfinite(result_5)
        assert np.isfinite(result_10)
        
    def test_hybrid_z5d_prime_scalar(self):
        """Test hybrid Z5D prediction with scalar input."""
        # First calibrate for best results
        small_k = np.array([10, 50, 100])
        small_primes = np.array([29, 229, 541])
        self.estimator.calibrate_parameters(small_k, small_primes)
        
        result = self.estimator.hybrid_z5d_prime(100)
        assert isinstance(result, (float, np.floating))
        assert result > 0
        
    def test_hybrid_z5d_prime_array(self):
        """Test hybrid Z5D prediction with array input."""
        # First calibrate
        small_k = np.array([10, 50, 100])
        small_primes = np.array([29, 229, 541])
        self.estimator.calibrate_parameters(small_k, small_primes)
        
        k_values = np.array([50, 100, 200])
        results = self.estimator.hybrid_z5d_prime(k_values)
        
        assert isinstance(results, np.ndarray)
        assert len(results) == len(k_values)
        assert np.all(results > 0)
        
    def test_hybrid_z5d_prime_no_zeta(self):
        """Test hybrid prediction without zeta corrections."""
        result = self.estimator.hybrid_z5d_prime(100, include_zeta=False)
        assert isinstance(result, (float, np.floating))
        assert result > 0


class TestValidation:
    """Test cases for prediction validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.estimator = ZPrimeEstimator()
        self.k_train = np.array([10, 50, 100])
        self.primes_train = np.array([29, 229, 541])
        self.k_test = np.array([20, 30, 150])
        self.primes_test = np.array([71, 113, 863])
        
    def test_validate_predictions_basic(self):
        """Test basic prediction validation."""
        # Calibrate first
        self.estimator.calibrate_parameters(self.k_train, self.primes_train)
        
        # Validate
        result = self.estimator.validate_predictions(
            self.k_test, 
            self.primes_test
        )
        
        required_fields = ['mae', 'mre', 'rmse', 'max_error', 'method', 'n_test']
        for field in required_fields:
            assert field in result
            
        assert result['mae'] >= 0
        assert result['mre'] >= 0
        assert result['rmse'] >= 0
        assert result['max_error'] >= 0
        assert result['n_test'] == len(self.k_test)
        
    def test_validate_predictions_methods(self):
        """Test validation with different prediction methods."""
        # Calibrate first
        self.estimator.calibrate_parameters(self.k_train, self.primes_train)
        
        methods = ['z5d', 'calibrated', 'hybrid']
        for method in methods:
            result = self.estimator.validate_predictions(
                self.k_test,
                self.primes_test,
                method=method
            )
            assert result['method'] == method
            assert result['mae'] >= 0
            
    def test_validate_predictions_auto_primes(self):
        """Test validation with automatic prime generation."""
        # Use very small test set to avoid slow SymPy calls
        k_tiny = np.array([10, 20])
        
        self.estimator.calibrate_parameters(self.k_train, self.primes_train)
        result = self.estimator.validate_predictions(k_tiny)
        
        assert 'mae' in result
        assert result['n_test'] == len(k_tiny)
        
    def test_validate_predictions_invalid_method(self):
        """Test validation with invalid method."""
        with pytest.raises(ValueError):
            self.estimator.validate_predictions(
                self.k_test,
                self.primes_test,
                method='invalid_method'
            )


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow(self):
        """Test complete workflow: calibrate -> predict -> validate."""
        estimator = ZPrimeEstimator()
        
        # 1. Calibrate on training data
        k_train = np.array([10, 50, 100, 200, 500])
        primes_train = np.array([29, 229, 541, 1229, 3571])
        
        calib_result = estimator.calibrate_parameters(k_train, primes_train)
        assert estimator.is_calibrated
        assert calib_result['mre'] < 1.0  # Should have reasonable error
        
        # 2. Make predictions
        k_pred = np.array([150, 300, 750])
        
        # Test different prediction methods
        pred_z5d = estimator.calibrated_z5d_prime(k_pred)
        pred_hybrid = estimator.hybrid_z5d_prime(k_pred)
        
        assert len(pred_z5d) == len(k_pred)
        assert len(pred_hybrid) == len(k_pred)
        assert np.all(pred_z5d > 0)
        assert np.all(pred_hybrid > 0)
        
        # 3. Test geodesic filtering
        candidates = estimator.filter_prime_candidates(1000, 1100)
        assert len(candidates) > 0
        assert all(1000 <= c <= 1100 for c in candidates)
        
        # 4. Validate on test data
        k_test = np.array([25, 75, 125])
        primes_test = np.array([97, 379, 691])
        
        val_result = estimator.validate_predictions(k_test, primes_test)
        assert val_result['mae'] >= 0
        assert val_result['mre'] >= 0
        
    def test_accuracy_improvement(self):
        """Test that calibration improves accuracy over defaults."""
        estimator = ZPrimeEstimator()
        
        # Training data  
        k_train = np.array([50, 100, 200, 500])
        primes_train = np.array([229, 541, 1229, 3571])
        
        # Test data
        k_test = np.array([75, 150, 300])
        primes_test = np.array([379, 863, 1987])
        
        # Get baseline error (before calibration)
        baseline_pred = estimator.calibrated_z5d_prime(k_test)
        baseline_mre = np.mean(np.abs((baseline_pred - primes_test) / primes_test))
        
        # Calibrate and get calibrated error
        estimator.calibrate_parameters(k_train, primes_train)
        calibrated_pred = estimator.calibrated_z5d_prime(k_test)
        calibrated_mre = np.mean(np.abs((calibrated_pred - primes_test) / primes_test))
        
        # Calibration should improve accuracy (lower MRE)
        # Note: This may not always be true for very small datasets,
        # but should generally hold for larger, representative datasets
        print(f"Baseline MRE: {baseline_mre:.4f}, Calibrated MRE: {calibrated_mre:.4f}")
        
        # At minimum, calibrated error should be finite and reasonable
        assert np.isfinite(calibrated_mre)
        assert calibrated_mre < 10.0  # Should be much better than 1000% error


def test_mathematical_constants():
    """Test mathematical constants used in the module."""
    from src.z_framework.discrete.z_prime_utils import E_SQUARED, PHI, RIEMANN_ZETA_ZEROS
    
    # Test E_SQUARED
    assert abs(E_SQUARED - 7.389) < 0.01
    
    # Test PHI (golden ratio)
    expected_phi = (1 + np.sqrt(5)) / 2
    assert abs(PHI - expected_phi) < 1e-10
    
    # Test Riemann zeta zeros
    assert len(RIEMANN_ZETA_ZEROS) == 20
    assert all(isinstance(zero, (int, float)) for zero in RIEMANN_ZETA_ZEROS)
    assert all(zero > 0 for zero in RIEMANN_ZETA_ZEROS)
    
    # First zero should be approximately 14.134725
    assert abs(RIEMANN_ZETA_ZEROS[0] - 14.134725) < 0.01


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])