"""
Test module for the Efficiency Through Symmetry experiment.

This module provides unit tests for the experimental framework to ensure
reliable and reproducible results.
"""

import pytest
import numpy as np
import sys
import os

# Add path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'experiments'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from experiments.efficiency_through_symmetry import (
    EfficiencyThroughSymmetryExperiment,
    ExperimentResult,
    StatisticalSummary
)


class TestEfficiencyThroughSymmetryExperiment:
    """Test class for the efficiency through symmetry experiment."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use smaller parameters for testing
        self.experiment = EfficiencyThroughSymmetryExperiment(max_zeros=100, precision_dps=20)
        self.experiment.test_k_values = [1000, 10000]  # Smaller test set
        
    def test_experiment_initialization(self):
        """Test experiment initialization."""
        assert self.experiment.max_zeros == 100
        assert self.experiment.precision_dps == 20
        assert len(self.experiment.test_k_values) == 2
        
    def test_compute_true_primes(self):
        """Test computation of true prime values."""
        true_primes = self.experiment.compute_true_primes()
        
        # Should have values for all test k values
        assert len(true_primes) == len(self.experiment.test_k_values)
        
        # Check specific known values
        assert 1000 in true_primes
        assert true_primes[1000] > 7000  # 1000th prime is 7919
        
    def test_li_inverse(self):
        """Test logarithmic integral inverse computation."""
        # Test with known value
        result = self.experiment.li_inverse(1000)
        
        # Should be reasonable approximation
        assert 7000 < result < 9000
        
    def test_baseline_prediction(self):
        """Test baseline Z5D prediction."""
        prediction = self.experiment.baseline_z5d_prediction(1000)
        
        # Should be reasonable
        assert 5000 < prediction < 10000
        
    def test_zeta_zero_generation(self):
        """Test zeta zero generation."""
        zeros = self.experiment.generate_zeta_zeros(10)
        
        # Should have requested number of zeros
        assert len(zeros) == 10
        
        # All should be complex numbers
        for zero in zeros:
            assert isinstance(zero, complex)
            
        # Real parts should be approximately 0.5 (RH assumption)
        for zero in zeros:
            assert abs(zero.real - 0.5) < 0.1
            
    def test_bootstrap_analysis(self):
        """Test bootstrap confidence interval computation."""
        # Sample data
        errors = [0.01, 0.02, 0.015, 0.025, 0.018]
        
        ci_lower, ci_upper = self.experiment.bootstrap_analysis(errors, n_bootstrap=100)
        
        # CI should be reasonable
        assert ci_lower < ci_upper
        assert 0 < ci_lower < 0.1
        assert 0 < ci_upper < 0.1
        
    def test_statistical_significance_test(self):
        """Test statistical significance testing."""
        errors1 = [0.01, 0.02, 0.015, 0.025, 0.018]
        errors2 = [0.005, 0.010, 0.008, 0.012, 0.009]  # Smaller errors
        
        p_value = self.experiment.statistical_significance_test(errors1, errors2)
        
        # Should be a valid p-value
        assert 0 <= p_value <= 1
        
    def test_experiment_result_creation(self):
        """Test creation of experiment result objects."""
        result = ExperimentResult(
            method="test",
            k_value=1000,
            true_value=7919.0,
            prediction=7920.0,
            error_absolute=1.0,
            error_relative=0.000126,
            computation_time=0.1,
            num_zeros_used=10
        )
        
        assert result.method == "test"
        assert result.k_value == 1000
        assert result.error_relative < 0.001
        
    def test_statistical_summary_creation(self):
        """Test creation of statistical summary objects."""
        summary = StatisticalSummary(
            method="test",
            num_zeros=10,
            mean_error=0.001,
            median_error=0.0009,
            std_error=0.0002,
            max_error=0.0015,
            min_error=0.0008,
            bootstrap_ci_lower=0.0008,
            bootstrap_ci_upper=0.0012
        )
        
        assert summary.method == "test"
        assert summary.num_zeros == 10
        assert summary.bootstrap_ci_lower < summary.bootstrap_ci_upper
        
    def test_pi_corrected_computation(self):
        """Test corrected prime counting function."""
        # Generate small number of zeros for testing
        zeros = self.experiment.generate_zeta_zeros(5)
        
        # Test computation
        result = self.experiment.pi_corrected(1000, zeros, 5)
        
        # Should be reasonable approximation to number of primes up to 1000
        assert 150 < result < 200  # pi(1000) = 168
        
    def test_enhanced_prediction(self):
        """Test enhanced Z5D prediction with zeta zeros."""
        # Generate small number of zeros for testing
        zeros = self.experiment.generate_zeta_zeros(5)
        
        # Test prediction
        prediction = self.experiment.z5d_prime_enhanced(100, zeros, 5)
        
        # Should be reasonable for 100th prime
        assert 400 < prediction < 600  # 100th prime is 541
        
    @pytest.mark.slow
    def test_small_experiment_run(self):
        """Test running a small version of the experiment."""
        # Override test values for quick test
        self.experiment.test_k_values = [100, 1000]
        
        # Compute true primes
        self.experiment.compute_true_primes()
        
        # Run single experiment
        result = self.experiment.run_single_experiment(100, 'baseline')
        
        # Check result structure
        assert isinstance(result, ExperimentResult)
        assert result.method == 'baseline'
        assert result.k_value == 100
        assert result.true_value > 0
        assert result.prediction > 0
        assert result.computation_time > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])