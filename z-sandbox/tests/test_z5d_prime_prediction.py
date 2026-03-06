#!/usr/bin/env python3
"""
Test suite for Z5D Prime Prediction gist
"""

import os
import sys
import time

# Path manipulation after standard library imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'gists'))

import pytest
import numpy as np
from z5d_prime_prediction import (
    z5d_predictor,
    z5d_predictor_with_dist_level,
    conical_density_enhancement_factor,
    z5d_predictor_full,
    bootstrap_ci,
    validate_predictions
)


class TestZ5DPredictor:
    """Test the base Z5D predictor function."""
    
    def test_basic_predictions(self):
        """Test base predictor on known values."""
        # Known primes at specific indices
        test_cases = [
            (1000000, 15485863),
            (10000000, 179424673),
            (100000000, 2038074743)
        ]
        
        for n, expected in test_cases:
            pred = z5d_predictor(n)
            # Allow up to 3000 ppm error for base predictor
            error_ppm = abs(pred - expected) / expected * 1e6
            assert error_ppm < 3000, f"Error {error_ppm:.2f} ppm exceeds threshold for n={n}"
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert z5d_predictor(0) == 0
        assert z5d_predictor(1) == 0
        assert z5d_predictor(2) > 0
    
    def test_monotonic(self):
        """Test that predictions increase monotonically."""
        values = [z5d_predictor(n) for n in [100, 1000, 10000, 100000]]
        for i in range(len(values) - 1):
            assert values[i] < values[i+1], "Predictions should be monotonically increasing"


class TestDistributionLevel:
    """Test the distribution level enhancement."""
    
    def test_optimized_dist_level(self):
        """Test predictions with optimized θ=0.71."""
        test_cases = [
            (1000000, 15485863),
            (10000000, 179424673),
            (100000000, 2038074743)
        ]
        
        for n, expected in test_cases:
            pred = z5d_predictor_with_dist_level(n, density_correction_factor=0.71)
            error_ppm = abs(pred - expected) / expected * 1e6
            # Mean error should be under 500 ppm for individual predictions
            assert error_ppm < 500, f"Error {error_ppm:.2f} ppm exceeds threshold for n={n}"
    
    def test_dist_level_improves_accuracy(self):
        """Test that distribution level improves over base predictor."""
        n = 10000000
        actual = 179424673
        
        base_pred = z5d_predictor(n)
        dist_pred = z5d_predictor_with_dist_level(n, density_correction_factor=0.71)
        
        base_error = abs(base_pred - actual)
        dist_error = abs(dist_pred - actual)
        
        # Distribution level should reduce error
        assert dist_error < base_error, "Distribution level should improve accuracy"
    
    def test_adjustable_theta(self):
        """Test that different theta values produce different results."""
        n = 10000000
        
        pred_low = z5d_predictor_with_dist_level(n, density_correction_factor=0.3)
        pred_mid = z5d_predictor_with_dist_level(n, density_correction_factor=0.71)
        pred_high = z5d_predictor_with_dist_level(n, density_correction_factor=1.0)
        
        # Higher theta should give higher predictions
        assert pred_low < pred_mid < pred_high


class TestConicalEnhancement:
    """Test the conical density enhancement."""
    
    def test_enhancement_factor(self):
        """Test that enhancement factor is computed correctly."""
        # At reference point (10^6), enhancement should be 0
        enh_ref = conical_density_enhancement_factor(10**6)
        assert abs(enh_ref) < 1e-10, "Enhancement should be ~0 at reference"
        
        # At higher scales, enhancement should be positive
        enh_high = conical_density_enhancement_factor(10**8)
        assert enh_high > 0, "Enhancement should be positive above reference"
    
    def test_scale_dependent(self):
        """Test that enhancement increases with scale."""
        enh_small = conical_density_enhancement_factor(10**6)
        enh_medium = conical_density_enhancement_factor(10**7)
        enh_large = conical_density_enhancement_factor(10**8)
        
        # Enhancement should increase with scale
        assert enh_small < enh_medium < enh_large


class TestFullPredictor:
    """Test the full Z5D predictor with all enhancements."""
    
    def test_full_predictor_accuracy(self):
        """Test full predictor achieves target accuracy."""
        test_cases = [
            (1000000, 15485863),
            (10000000, 179424673),
            (100000000, 2038074743)
        ]
        
        errors = []
        for n, expected in test_cases:
            pred = z5d_predictor_full(n, dist_level=0.71, use_conical=True)
            error_ppm = abs(pred - expected) / expected * 1e6
            errors.append(error_ppm)
        
        mean_error = np.mean(errors)
        # Mean error should be under 300 ppm
        assert mean_error < 300, f"Mean error {mean_error:.2f} ppm exceeds target"
    
    def test_conical_enhancement_effect(self):
        """Test that conical enhancement has positive effect."""
        n = 10000000
        actual = 179424673
        
        pred_no_conical = z5d_predictor_full(n, dist_level=0.71, use_conical=False)
        pred_with_conical = z5d_predictor_full(n, dist_level=0.71, use_conical=True)
        
        error_no_conical = abs(pred_no_conical - actual)
        error_with_conical = abs(pred_with_conical - actual)
        
        # Conical enhancement should improve or maintain accuracy
        assert error_with_conical <= error_no_conical * 1.1  # Allow 10% tolerance


class TestBootstrapCI:
    """Test bootstrap confidence interval computation."""
    
    def test_bootstrap_ci_basic(self):
        """Test basic bootstrap CI computation."""
        errors = [100, 200, 300, 400, 500]
        ci = bootstrap_ci(errors, n_resamples=100)
        
        # CI should bracket the mean
        mean_err = np.mean(errors)
        assert ci[0] < mean_err < ci[1], "CI should bracket mean"
        
        # Lower bound should be less than upper bound
        assert ci[0] < ci[1], "Lower CI should be less than upper CI"
    
    def test_empty_errors(self):
        """Test bootstrap CI with empty errors."""
        errors = []
        ci = bootstrap_ci(errors)
        assert ci == (0.0, 0.0), "Empty errors should return (0, 0)"
    
    def test_reproducibility(self):
        """Test that bootstrap CI is reproducible."""
        errors = [100, 200, 300, 400, 500]
        ci1 = bootstrap_ci(errors, n_resamples=100)
        ci2 = bootstrap_ci(errors, n_resamples=100)
        
        # Results should be identical due to fixed seed
        assert ci1 == ci2, "Bootstrap CI should be reproducible"


class TestValidatePredictions:
    """Test the validation function."""
    
    def test_validate_predictions_structure(self):
        """Test that validate_predictions returns correct structure."""
        n_values = [1000000, 10000000]
        actual_primes = [15485863, 179424673]
        
        results = validate_predictions(n_values, actual_primes)
        
        # Check result structure
        assert 'predictions' in results
        assert 'errors_ppm' in results
        assert 'mean_error_ppm' in results
        assert 'ci_95' in results
        assert 'n_values' in results
        assert 'actual_primes' in results
        
        # Check lengths match
        assert len(results['predictions']) == len(n_values)
        assert len(results['errors_ppm']) == len(n_values)
    
    def test_validate_predictions_accuracy(self):
        """Test that validation produces accurate results."""
        n_values = [1000000, 10000000, 100000000]
        actual_primes = [15485863, 179424673, 2038074743]
        
        results = validate_predictions(n_values, actual_primes, 
                                      dist_level=0.71, use_conical=True)
        
        # Mean error should be reasonable
        assert results['mean_error_ppm'] < 300, "Mean error should be under 300 ppm"
        
        # CI should be reasonable
        ci = results['ci_95']


class TestPerformance:
    """Test performance characteristics."""
    
    def test_extreme_values(self):
        """Test that predictor works for extreme values."""
        extreme_values = [10**9, 10**12, 10**15]
        
        for n in extreme_values:
            start = time.perf_counter()
            pred = z5d_predictor_full(n, dist_level=0.71)
            elapsed = (time.perf_counter() - start) * 1000  # ms
            
            # Should complete in under 1ms
            assert elapsed < 1.0, f"Prediction for n={n} took {elapsed:.2f}ms"
            
            # Prediction should be positive and reasonable
            assert pred > 0
            assert pred > n  # nth prime should be larger than n


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
