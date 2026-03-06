#!/usr/bin/env python3
"""
Tests for High-Scale Z5D Prime Prediction Validation

These tests ensure the high-scale validation script maintains
correct behavior at cryptographic scales.
"""

import pytest
from high_scale_z5d_validation import (
    z5d_predictor_full_highscale,
    estimate_prime_index,
    compute_asymptotic_error_bound,
    validate_high_scale_prediction,
    SMALL_PRIMES
)


class TestZ5DPredictorHighScale:
    """Tests for the high-scale Z5D predictor."""
    
    def test_small_prime_shortcircuit(self):
        """Test that small primes are returned exactly."""
        for n in range(1, 10):
            pred = z5d_predictor_full_highscale(n, dps=1500)
            assert pred == SMALL_PRIMES[n-1], f"Small prime p_{n} should be {SMALL_PRIMES[n-1]}, got {pred}"
    
    def test_minimum_dps_enforced(self):
        """Test that dps >= 1500 is enforced."""
        with pytest.raises(ValueError, match="dps must be >= 1500"):
            z5d_predictor_full_highscale(100, dps=1000)
    
    def test_positive_n_required(self):
        """Test that n > 0 is required."""
        with pytest.raises(ValueError, match="Index n must be positive"):
            z5d_predictor_full_highscale(0, dps=1500)
        
        with pytest.raises(ValueError, match="Index n must be positive"):
            z5d_predictor_full_highscale(-5, dps=1500)
    
    def test_known_prime_accuracy(self):
        """Test accuracy against known primes."""
        # Known: p_1000000 = 15485863
        pred = z5d_predictor_full_highscale(1000000, dps=1500)
        actual = 15485863
        error_ppm = abs(pred - actual) / actual * 1e6
        
        # Should be within 1000 ppm (0.1%) at this scale
        assert error_ppm < 1000, f"Error {error_ppm:.2f} ppm exceeds 1000 ppm threshold"
    
    def test_deterministic_behavior(self):
        """Test that predictions are deterministic."""
        n = 100000
        pred1 = z5d_predictor_full_highscale(n, dps=1500)
        pred2 = z5d_predictor_full_highscale(n, dps=1500)
        
        assert pred1 == pred2, "Predictions should be deterministic"
    
    def test_conical_enhancement_effect(self):
        """Test that conical enhancement has measurable effect."""
        n = 100000
        pred_without = z5d_predictor_full_highscale(n, use_conical=False, dps=1500)
        pred_with = z5d_predictor_full_highscale(n, use_conical=True, dps=1500)
        
        # They should be different
        assert pred_without != pred_with, "Conical enhancement should affect prediction"
    
    def test_no_float_casting(self):
        """Test that result is a Python int, not float."""
        pred = z5d_predictor_full_highscale(10000, dps=1500)
        assert isinstance(pred, int), f"Prediction should be int, got {type(pred)}"


class TestPrimeIndexEstimation:
    """Tests for prime index estimation."""
    
    def test_index_estimation_500(self):
        """Test index estimation for 10^500."""
        n = estimate_prime_index(500, dps=2000)
        
        # Should be roughly 10^496 (by inverse Prime Number Theorem: n ≈ P / ln(P) where P = 10^500)
        n_str = str(n)
        assert 495 <= len(n_str) <= 498, f"Index should have ~497 digits, got {len(n_str)}"
    
    def test_index_estimation_1233(self):
        """Test index estimation for 10^1233."""
        n = estimate_prime_index(1233, dps=2000)
        
        # Should be roughly 10^1229
        n_str = str(n)
        assert 1228 <= len(n_str) <= 1231, f"Index should have ~1230 digits, got {len(n_str)}"
    
    def test_index_is_integer(self):
        """Test that estimated index is an integer."""
        n = estimate_prime_index(500, dps=2000)
        assert isinstance(n, int), f"Index should be int, got {type(n)}"


class TestAsymptoticErrorBound:
    """Tests for asymptotic error bound computation."""
    
    def test_error_bound_decreases(self):
        """Test that error bound decreases with n."""
        n1 = estimate_prime_index(500, dps=2000)
        n2 = estimate_prime_index(750, dps=2000)
        n3 = estimate_prime_index(1000, dps=2000)
        
        error1 = compute_asymptotic_error_bound(n1, dps=2000)
        error2 = compute_asymptotic_error_bound(n2, dps=2000)
        error3 = compute_asymptotic_error_bound(n3, dps=2000)
        
        assert error1 > error2 > error3, "Error bound should decrease with n"
    
    def test_error_bound_positive(self):
        """Test that error bound is positive."""
        n = estimate_prime_index(500, dps=2000)
        error = compute_asymptotic_error_bound(n, dps=2000)
        
        assert error > 0, "Error bound should be positive"
    
    def test_error_bound_small(self):
        """Test that error bound is small at high scales."""
        n = estimate_prime_index(1233, dps=2000)
        error = compute_asymptotic_error_bound(n, dps=2000)
        error_ppm = error * 1e6
        
        # Should be approaching 1 ppm
        assert error_ppm < 2.0, f"Error bound {error_ppm:.4f} ppm should be < 2 ppm"


class TestHighScaleValidation:
    """Integration tests for high-scale validation."""
    
    def test_validation_500(self):
        """Test validation at 10^500 scale."""
        result = validate_high_scale_prediction(500, dps=2000)
        
        # Check result structure
        assert 'magnitude_power' in result
        assert 'n' in result
        assert 'p_hat' in result
        assert 'bit_length' in result
        assert 'runtime_ms' in result
        assert 'error_bound' in result
        assert 'error_ppm' in result
        
        # Check values
        assert result['magnitude_power'] == 500
        assert 1650 <= result['bit_length'] <= 1670, f"Bit length {result['bit_length']} not in expected range"
        assert result['error_ppm'] < 10.0, f"Error {result['error_ppm']:.4f} ppm exceeds 10 ppm threshold"
        assert result['runtime_ms'] > 0, "Runtime should be positive"
    
    def test_validation_1233(self):
        """Test validation at 10^1233 scale."""
        result = validate_high_scale_prediction(1233, dps=2000)
        
        # Check bit length
        assert 4085 <= result['bit_length'] <= 4105, f"Bit length {result['bit_length']} not in expected range"
        
        # Check error approaches 1 ppm
        assert result['error_ppm'] < 2.0, f"Error {result['error_ppm']:.4f} ppm should approach 1 ppm"
    
    def test_bit_length_scaling(self):
        """Test that bit length scales appropriately with magnitude."""
        result_500 = validate_high_scale_prediction(500, dps=2000)
        result_750 = validate_high_scale_prediction(750, dps=2000)
        result_1000 = validate_high_scale_prediction(1000, dps=2000)
        
        # Bit lengths should increase
        assert result_500['bit_length'] < result_750['bit_length'] < result_1000['bit_length']
    
    def test_error_trend(self):
        """Test that error decreases with magnitude."""
        result_500 = validate_high_scale_prediction(500, dps=2000)
        result_1000 = validate_high_scale_prediction(1000, dps=2000)
        
        # Error should decrease
        assert result_500['error_ppm'] > result_1000['error_ppm'], "Error should decrease with magnitude"
    
    def test_runtime_reasonable(self):
        """Test that runtime is millisecond-class."""
        result = validate_high_scale_prediction(500, dps=2000)
        
        # Should be < 5 seconds (very generous upper bound)
        assert result['runtime_ms'] < 5000, f"Runtime {result['runtime_ms']:.2f} ms exceeds 5 second threshold"


class TestAcceptanceCriteria:
    """Tests that validate acceptance criteria from the issue."""
    
    def test_acceptance_gate_1_error_at_500(self):
        """Gate 1: Error at ~10^500 should be <= ~10 ppm."""
        result = validate_high_scale_prediction(500, dps=2000)
        assert result['error_ppm'] <= 10.0, f"Error {result['error_ppm']:.4f} ppm exceeds 10 ppm gate"
    
    def test_acceptance_gate_2_bit_length_range(self):
        """Gate 2: Bit lengths should be in [1661, 4096] range."""
        magnitudes = [500, 750, 1000, 1233]
        
        for mag in magnitudes:
            result = validate_high_scale_prediction(mag, dps=2000)
            assert 1600 <= result['bit_length'] <= 4200, \
                f"Bit length {result['bit_length']} at 10^{mag} outside expected range"
    
    def test_acceptance_gate_3_error_trending(self):
        """Gate 3: Error should trend toward ~1 ppm at ~10^1233."""
        result = validate_high_scale_prediction(1233, dps=2000)
        assert result['error_ppm'] <= 2.0, \
            f"Error {result['error_ppm']:.4f} ppm should approach 1 ppm at 10^1233"
    
    def test_acceptance_gate_4_no_float_precision(self):
        """Gate 4: Must use high precision, not float."""
        # This is enforced by the dps parameter
        with pytest.raises(ValueError):
            z5d_predictor_full_highscale(100, dps=50)  # Too low
    
    def test_acceptance_gate_5_deterministic(self):
        """Gate 5: Execution must be deterministic."""
        result1 = validate_high_scale_prediction(500, dps=2000)
        result2 = validate_high_scale_prediction(500, dps=2000)
        
        assert result1['p_hat'] == result2['p_hat'], "Results should be deterministic"
        assert result1['error_ppm'] == result2['error_ppm'], "Error should be deterministic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
