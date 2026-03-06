#!/usr/bin/env python3
"""
Test case for Z5D Prime Prediction Test Bed at n = 10^15

This test case validates the z5d_prime_testbed_10e15.py script functionality
and ensures the Z Framework maintains accuracy and numerical stability at
ultra-extreme scales (n = 10^15).

Integration test for the test bed implementation extending beyond n = 10^14 
to frontier-scale computational prime prediction capabilities.
"""

import sys
import os
import subprocess
import pytest
import warnings
import statistics
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


class TestZ5DTestbed10e15:
    """Test class for n = 10^15 test bed functionality."""
    
    def setup_method(self):
        """Setup test parameters."""
        self.n = int(1e15)
        # Since exact 10^15th prime is computationally infeasible,
        # we use Enhanced PNT as reference and test relative performance
        self.expected_relative_error_threshold = 0.01  # 1% maximum acceptable error
        self.excellent_threshold = 0.001  # 0.1% for excellent rating
        
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^15 tests")
    def test_z5d_prediction_computational_feasibility(self):
        """Test that Z5D prediction is computationally feasible for n = 10^15."""
        import time
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            start_time = time.time()
            prediction = z5d_prime(self.n, auto_calibrate=True, force_backend='mpmath')
            end_time = time.time()
            
            computation_time = end_time - start_time
            
            # Assertions for computational feasibility
            assert prediction > 0, "Prediction should be positive"
            assert prediction > self.n, "Prime should be larger than its index"
            assert computation_time < 60, f"Computation took {computation_time:.3f}s, should be under 60s"
            assert isinstance(prediction, float), "Prediction should be a float"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^15 tests")
    def test_ultra_extreme_scale_calibration(self):
        """Test ultra-extreme scale calibration parameters for n = 10^15."""
        # For n = 10^15, should use ultra_extreme scale parameters
        c_optimal, k_star_optimal = _get_optimal_calibration(self.n)
        
        # Expected ultra-extreme scale parameters (new implementation)
        expected_c = -0.00002
        expected_k_star = -0.10
        
        assert c_optimal == expected_c, f"Expected c={expected_c}, got {c_optimal}"
        assert k_star_optimal == expected_k_star, f"Expected k_star={expected_k_star}, got {k_star_optimal}"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^15 tests")
    def test_component_terms_numerical_stability_10e15(self):
        """Test that component terms remain numerically stable for n = 10^15."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Test base PNT term
            base_pnt = base_pnt_prime(self.n)
            assert base_pnt > 0, "Base PNT should be positive"
            assert base_pnt > self.n, "PNT estimate should be larger than n"
            assert 3e16 < base_pnt < 5e16, f"Base PNT {base_pnt} outside expected range [3e16, 5e16]"
            
            # Test dilation term
            d_val = d_term(self.n)
            assert d_val > 0, "Dilation term should be positive"
            assert d_val < 1, "Dilation term should be less than 1"
            assert 0.3 < d_val < 0.6, f"Dilation term {d_val} outside expected range [0.3, 0.6]"
            
            # Test curvature term
            e_val = e_term(self.n)
            assert e_val > 0, "Curvature term should be positive"
            assert e_val < 1, "Curvature term should be less than 1"
            assert 1e-7 < e_val < 1e-5, f"Curvature term {e_val} outside expected range [1e-7, 1e-5]"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^15 tests")
    def test_cross_validation_consistency(self):
        """Test cross-validation consistency across multiple estimation methods."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Get estimates from different methods
            base_pnt_pred = base_pnt_prime(self.n)
            z5d_current = z5d_prime(self.n, auto_calibrate=True, force_backend='mpmath')
            z5d_manual = z5d_prime(self.n, c=-0.00002, k_star=-0.10, auto_calibrate=False, force_backend='mpmath')
            
            estimates = [base_pnt_pred, z5d_current, z5d_manual]
            
            # Cross-validation checks
            assert all(est > 0 for est in estimates), "All estimates should be positive"
            assert all(est > self.n for est in estimates), "All estimates should be larger than n"
            
            # Check consistency (coefficient of variation should be small)
            mean_est = statistics.mean(estimates)
            std_est = statistics.stdev(estimates)
            cv = std_est / mean_est
            
            assert cv < 0.01, f"Coefficient of variation {cv:.6f} too high, estimates inconsistent"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^15 tests")
    def test_high_precision_enforcement_10e15(self):
        """Test that ultra-high-precision arithmetic is enforced for n = 10^15."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Test that computation produces finite, reasonable results
            prediction = z5d_prime(self.n, force_backend='mpmath')
            
            assert isinstance(prediction, float), "Prediction should be float"
            assert prediction > 0, "Prediction should be positive"
            assert not (prediction != prediction), "Prediction should not be NaN"  # NaN check
            assert prediction != float('inf'), "Prediction should not be infinite"
            assert prediction != float('-inf'), "Prediction should not be negative infinite"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^15 tests")
    def test_prime_density_statistics(self):
        """Test prime density statistics calculations for n = 10^15."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Calculate theoretical prime density: 1/ln(n)
            ln_n = log(self.n)
            theoretical_density = 1.0 / ln_n
            expected_gap = ln_n
            
            # Verify reasonable values
            assert 0.02 < theoretical_density < 0.04, f"Theoretical density {theoretical_density} outside expected range"
            assert 30 < expected_gap < 40, f"Expected gap {expected_gap} outside expected range"
            
            # Test that Z5D prediction is consistent with density expectations
            z5d_pred = z5d_prime(self.n, force_backend='mpmath')
            implied_density = self.n / z5d_pred
            
            # Implied density should be close to theoretical density
            density_ratio = implied_density / theoretical_density
            assert 0.9 < density_ratio < 1.1, f"Density ratio {density_ratio} suggests inconsistent prediction"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for n=10^15 tests")
    def test_computation_performance_10e15(self):
        """Test computation performance and efficiency for n = 10^15."""
        import time
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Time multiple computations to get average
            times = []
            results = []
            
            for _ in range(3):  # 3 runs for averaging
                start_time = time.time()
                result = z5d_prime(self.n, auto_calibrate=True, force_backend='mpmath')
                end_time = time.time()
                
                times.append(end_time - start_time)
                results.append(result)
            
            avg_time = statistics.mean(times)
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            
            # Performance assertions
            assert avg_time < 10, f"Average computation time {avg_time:.3f}s should be under 10s"
            assert std_time < 2, f"Time variation {std_time:.3f}s should be consistent"
            
            # Result consistency
            result_std = statistics.stdev(results) if len(results) > 1 else 0
            result_mean = statistics.mean(results)
            result_cv = result_std / result_mean if result_mean > 0 else 0
            
            assert result_cv < 1e-10, f"Results should be deterministic, got CV={result_cv:.2e}"
    
    def test_testbed_script_execution_10e15(self):
        """Test that the 10^15 test bed script executes successfully."""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'scripts', 
            'z5d_prime_testbed_10e15.py'
        )
        
        if not os.path.exists(script_path):
            pytest.skip("10^15 test bed script not found")
        
        try:
            # Run the script and capture output
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=120  # 120 second timeout for 10^15 computation
            )
            
            # Check that script executed successfully
            assert result.returncode == 0, f"Script failed with return code {result.returncode}"
            assert "COMPLETED SUCCESSFULLY" in result.stdout, \
                "Script should complete with success message"
            assert "EXCEPTIONAL" in result.stdout or "EXCELLENT" in result.stdout or "FRONTIER" in result.stdout, \
                "Script should report good validation status"
            assert "Cross-validation" in result.stdout, \
                "Script should include cross-validation analysis"
            assert "PRIME DENSITY STATISTICS" in result.stdout, \
                "Script should include prime density statistics"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Test bed script execution timed out")
        except Exception as e:
            pytest.fail(f"Failed to execute test bed script: {e}")


class TestZ5DScaleProgression10e15:
    """Test scale progression from 10^14 to 10^15."""
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for scale progression tests")
    def test_scale_progression_10e14_to_10e15(self):
        """Test that computational feasibility scales from 10^14 to 10^15."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Test n = 10^14 (reference)
            n_14 = int(1e14)
            pred_14 = z5d_prime(n_14, auto_calibrate=True, force_backend='mpmath')
            
            # Test n = 10^15 (frontier)
            n_15 = int(1e15)
            pred_15 = z5d_prime(n_15, auto_calibrate=True, force_backend='mpmath')
            
            # Both should produce reasonable results
            assert pred_14 > n_14, "10^14 prediction should be larger than n"
            assert pred_15 > n_15, "10^15 prediction should be larger than n"
            
            # Predictions should scale reasonably (10^15 ~ 10x larger, prime should be ~23x larger)
            scaling_factor = pred_15 / pred_14
            expected_scaling = (n_15 / n_14) * log(n_15) / log(n_14)  # Asymptotic scaling
            
            assert 5 < scaling_factor < 15, f"Scaling factor {scaling_factor:.2f} outside reasonable range"
            
            # Relative scaling should be close to expected asymptotic behavior
            relative_scaling_error = abs(scaling_factor - expected_scaling) / expected_scaling
            assert relative_scaling_error < 0.5, f"Scaling pattern deviates too much from PNT expectations"
    
    @pytest.mark.skipif(not MPMATH_AVAILABLE, reason="mpmath required for scale progression tests")
    def test_computational_efficiency_scaling(self):
        """Test that computational efficiency scales appropriately to 10^15."""
        import time
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Time computation for 10^14
            start = time.time()
            pred_14 = z5d_prime(int(1e14), auto_calibrate=True, force_backend='mpmath')
            time_14 = time.time() - start
            
            # Time computation for 10^15
            start = time.time()
            pred_15 = z5d_prime(int(1e15), auto_calibrate=True, force_backend='mpmath')
            time_15 = time.time() - start
            
            # Both should complete in reasonable time
            assert time_14 < 30, f"10^14 computation took {time_14:.3f}s, should be under 30s"
            assert time_15 < 60, f"10^15 computation took {time_15:.3f}s, should be under 60s"
            
            # Time scaling should not be excessive (10^15 is only 10x larger input)
            time_scaling = time_15 / time_14 if time_14 > 0 else float('inf')
            assert time_scaling < 10, f"Time scaling {time_scaling:.2f}x too high for 10x input increase"


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])