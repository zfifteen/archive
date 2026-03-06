#!/usr/bin/env python3
"""
Test case for Z5D Prime Prediction Test Bed at n = 10^14

This test case validates the z5d_prime_testbed_10e14.py script functionality
and ensures the Z Framework maintains accuracy and numerical stability at
ultra-large scales (n = 10^14).

Integration test for the test bed implementation corresponding to issue #277.
"""

import sys
import os
import subprocess
import pytest
import warnings
from math import log

# Add src directory to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

try:
    from z_framework.discrete.z5d_predictor import (
        z5d_prime, 
        base_pnt_prime,
        d_term,
        e_term,
        _get_optimal_calibration,
        MPMATH_AVAILABLE
    )
    import mpmath
except ImportError as e:
    pytest.skip(f"Required modules not available: {e}", allow_module_level=True)


class TestZ5DTestbed10e14:
    """Test class for n = 10^14 test bed functionality."""
    
    def setup_method(self):
        """Setup test parameters."""
        self.n = int(1e14)
        self.published_value = 3_475_385_758_524_527  # OEIS A006988
        self.expected_relative_error_threshold = 0.01  # 1% maximum acceptable error
        self.excellent_threshold = 0.001  # 0.1% for excellent rating
        
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^14 tests")
    def test_z5d_prediction_accuracy_10e14(self):
        """Test Z5D prediction accuracy for n = 10^14."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Get Z5D prediction with auto-calibration
            prediction = z5d_prime(self.n, auto_calibrate=True, force_backend='mpmath')
            
            # Calculate relative error
            absolute_error = abs(prediction - self.published_value)
            relative_error = absolute_error / self.published_value
            
            # Assertions for accuracy
            assert prediction > 0, "Prediction should be positive"
            assert prediction > self.n, "Prime should be larger than its index"
            assert relative_error < self.expected_relative_error_threshold, \
                f"Relative error {relative_error:.6f} exceeds threshold {self.expected_relative_error_threshold}"
            assert relative_error < self.excellent_threshold, \
                f"Expected excellent accuracy (<{self.excellent_threshold}), got {relative_error:.6f}"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^14 tests")
    def test_ultra_large_scale_calibration_parameters(self):
        """Test that ultra-large scale calibration parameters are used for n = 10^14."""
        # Get optimal calibration parameters for n = 10^14
        c_optimal, k_star_optimal = _get_optimal_calibration(self.n)
        
        # Expected ultra-large scale parameters
        expected_c = -0.0001
        expected_k_star = -0.15
        
        assert c_optimal == expected_c, f"Expected c={expected_c}, got {c_optimal}"
        assert k_star_optimal == expected_k_star, f"Expected k_star={expected_k_star}, got {k_star_optimal}"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^14 tests")
    def test_component_terms_numerical_stability(self):
        """Test that component terms (base_pnt, d_term, e_term) are numerically stable for n = 10^14."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Test base PNT term
            base_pnt = base_pnt_prime(self.n)
            assert base_pnt > 0, "Base PNT should be positive"
            assert abs(base_pnt - self.published_value) / self.published_value < 0.1, \
                "Base PNT should be within 10% of published value"
            
            # Test dilation term
            d_val = d_term(self.n)
            assert d_val > 0, "Dilation term should be positive"
            assert d_val < 1, "Dilation term should be less than 1"
            assert 0.1 < d_val < 0.8, f"Dilation term {d_val} outside expected range [0.1, 0.8]"
            
            # Test curvature term
            e_val = e_term(self.n)
            assert e_val > 0, "Curvature term should be positive"
            assert e_val < 1, "Curvature term should be less than 1"
            assert 1e-6 < e_val < 1e-4, f"Curvature term {e_val} outside expected range [1e-6, 1e-4]"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^14 tests") 
    def test_improvement_over_base_pnt(self):
        """Test that Z5D prediction improves upon base PNT for n = 10^14."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Get base PNT prediction
            base_pnt_pred = base_pnt_prime(self.n)
            base_pnt_error = abs(base_pnt_pred - self.published_value) / self.published_value
            
            # Get Z5D prediction
            z5d_pred = z5d_prime(self.n, auto_calibrate=True, force_backend='mpmath')
            z5d_error = abs(z5d_pred - self.published_value) / self.published_value
            
            # Z5D should be more accurate than base PNT
            improvement_factor = base_pnt_error / z5d_error if z5d_error > 0 else float('inf')
            
            assert z5d_error < base_pnt_error, \
                f"Z5D error {z5d_error:.8f} should be less than base PNT error {base_pnt_error:.8f}"
            assert improvement_factor > 1.5, \
                f"Expected significant improvement (>1.5x), got {improvement_factor:.2f}x"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^14 tests")
    def test_high_precision_enforcement(self):
        """Test that high-precision arithmetic is enforced for n = 10^14."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Test that mpmath backend is automatically selected
            prediction_auto = z5d_prime(self.n, auto_calibrate=True)  # Should auto-select mpmath
            prediction_forced = z5d_prime(self.n, auto_calibrate=True, force_backend='mpmath')
            
            # Results should be identical (confirming mpmath was used automatically)
            assert abs(prediction_auto - prediction_forced) < 1e-6, \
                "Auto-selected backend should match forced mpmath backend"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^14 tests")
    def test_computation_performance(self):
        """Test that computation completes within reasonable time for n = 10^14."""
        import time
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            start_time = time.time()
            prediction = z5d_prime(self.n, auto_calibrate=True, force_backend='mpmath')
            end_time = time.time()
            
            computation_time = end_time - start_time
            
            assert prediction > 0, "Computation should produce valid result"
            assert computation_time < 30, f"Computation took {computation_time:.3f}s, should be under 30s"
    
    def test_testbed_script_execution(self):
        """Test that the test bed script executes successfully."""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'scripts', 
            'z5d_prime_testbed_10e14.py'
        )
        
        if not os.path.exists(script_path):
            pytest.skip("Test bed script not found")
        
        try:
            # Run the script and capture output
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            # Check that script executed successfully
            assert result.returncode == 0, f"Script failed with return code {result.returncode}"
            assert "COMPLETED SUCCESSFULLY" in result.stdout, \
                "Script should complete with success message"
            assert "EXCEPTIONAL" in result.stdout or "EXCELLENT" in result.stdout, \
                "Script should report excellent validation status"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Test bed script execution timed out")
        except Exception as e:
            pytest.fail(f"Failed to execute test bed script: {e}")


class TestZ5DScaleProgression:
    """Test scale progression from 10^13 to 10^14."""
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for scale progression tests")
    def test_scale_progression_consistency(self):
        """Test that accuracy remains excellent across scales."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Test n = 10^13 (reference from existing test bed)
            n_13 = int(1e13)
            published_13 = 323_780_508_946_331
            pred_13 = z5d_prime(n_13, auto_calibrate=True, force_backend='mpmath')
            error_13 = abs(pred_13 - published_13) / published_13
            
            # Test n = 10^14 (this test bed)
            n_14 = int(1e14)
            published_14 = 3_475_385_758_524_527
            pred_14 = z5d_prime(n_14, auto_calibrate=True, force_backend='mpmath')
            error_14 = abs(pred_14 - published_14) / published_14
            
            # Both should have excellent accuracy (sub-1% error)
            assert error_13 < 0.01, f"n=10^13 error {error_13:.8f} should be < 1%"
            assert error_14 < 0.01, f"n=10^14 error {error_14:.8f} should be < 1%"
            
            # Both should achieve sub-0.1% accuracy for excellent validation
            assert error_13 < 0.001, f"n=10^13 should achieve sub-0.1% accuracy, got {error_13*100:.6f}%"
            assert error_14 < 0.001, f"n=10^14 should achieve sub-0.1% accuracy, got {error_14*100:.6f}%"
            
            # Verify both are in the excellent range (different scales may have different optimal points)
            assert error_13 < 0.0001 or error_14 < 0.01, "At least one scale should show exceptional accuracy"


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])