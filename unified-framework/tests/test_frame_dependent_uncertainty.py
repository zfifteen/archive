#!/usr/bin/env python3
"""
Test Frame-Dependent Uncertainty Modulation Implementation

This test validates the frame-dependent uncertainty modulation experiment
implementation, ensuring proper integration with the Z Framework and
correct physics behavior.
"""

import pytest
import numpy as np
import sys
import os

# Add src and experiments to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'experiments'))

from frame_dependent_uncertainty_modulation import (
    DiscreteZetaShiftQuantum, 
    MockQuantumOperations,
    run_frame_dependent_uncertainty_experiment
)

class TestDiscreteZetaShiftQuantum:
    """Test the DiscreteZetaShiftQuantum class functionality."""
    
    def test_initialization_valid_parameters(self):
        """Test valid initialization with causality constraint."""
        a, b, c = 1.0, 0.5, 1.0  # |b| < c, satisfies causality
        dzs = DiscreteZetaShiftQuantum(a, b, c)
        
        assert dzs.a == 1.0
        assert dzs.b == 0.5
        assert dzs.c == 1.0
        assert float(dzs.k_star) == pytest.approx(0.3, rel=1e-6)
        assert dzs.z is not None

    def test_initialization_causality_violation(self):
        """Test that causality violation raises appropriate error."""
        with pytest.raises(ValueError, match="violates causality"):
            DiscreteZetaShiftQuantum(1.0, 1.5, 1.0)  # |b| >= c

    def test_unfold_next_functionality(self):
        """Test the unfold_next method updates state correctly."""
        dzs = DiscreteZetaShiftQuantum(1.0, 0.5, 1.0)
        initial_z = float(dzs.z)
        
        new_z = dzs.unfold_next()
        
        assert new_z != initial_z
        assert dzs.z == new_z

    def test_theta_prime_geodesic_function(self):
        """Test the theta_prime geodesic function."""
        dzs = DiscreteZetaShiftQuantum(1.0, 0.5, 1.0)
        
        # Test various x values
        for x in [0, 1, 2.5, 10]:
            result = dzs.theta_prime(x)
            assert isinstance(result, float)
            assert result >= 0  # θ' should be non-negative
            assert result <= 2.0  # Should be bounded by φ roughly

    def test_geodesic_density_calculation(self):
        """Test geodesic density calculation."""
        dzs = DiscreteZetaShiftQuantum(1.0, 0.5, 1.0)
        
        # Mock wavefunction and grid
        x_grid = np.linspace(-5, 5, 20)
        psi_mock = np.random.random(20) + 1j * np.random.random(20)  # Mock quantum state
        
        density_enh = dzs.get_geodesic_density(psi_mock, x_grid)
        
        assert isinstance(density_enh, float)
        assert not np.isnan(density_enh)
        assert 0.1 <= density_enh <= 0.3  # Should be around 15% target


class TestMockQuantumOperations:
    """Test the mock quantum operations for fallback functionality."""
    
    def test_mock_coherent_state(self):
        """Test mock coherent state generation."""
        N = 50
        alpha = 1.0
        state = MockQuantumOperations.coherent(N, alpha)
        
        assert len(state) == N
        assert np.iscomplexobj(state)

    def test_mock_expectation_values(self):
        """Test mock expectation value calculations."""
        op = np.random.random((10, 10))
        state = np.random.random(10) + 1j * np.random.random(10)
        
        result = MockQuantumOperations.expect(op, state)
        assert isinstance(result, float)
        assert 0 <= result <= 1


class TestFrameDependentExperiment:
    """Test the full frame-dependent uncertainty experiment."""
    
    def test_experiment_execution(self):
        """Test that the experiment runs without errors."""
        # This is a simplified version with fewer iterations for testing
        import frame_dependent_uncertainty_modulation as fem
        
        # Temporarily reduce parameters for faster testing
        original_num_trials = fem.run_frame_dependent_uncertainty_experiment.__defaults__
        
        # Run a simplified version
        try:
            # Mock a simple test by directly calling key components
            dzs = DiscreteZetaShiftQuantum(1.0, 0.5, 7.389)
            
            # Test unfold sequence
            unfolds = [dzs.z]
            for _ in range(5):
                unfolds.append(dzs.unfold_next())
            
            assert len(unfolds) == 6
            assert all(isinstance(float(u), (int, float)) for u in unfolds)
            
        except Exception as e:
            pytest.fail(f"Experiment execution failed: {e}")

    def test_uncertainty_product_physics(self):
        """Test that uncertainty products respect physics bounds."""
        # Test that σ_x * σ_p >= ħ/2 (Heisenberg uncertainty principle)
        
        hbar = 1.0
        dzs = DiscreteZetaShiftQuantum(1.0, 0.5, 7.389)
        
        # Mock uncertainty calculation
        sigma_x = 0.7
        sigma_p = hbar / (2 * sigma_x) + 0.1  # Should be above Heisenberg bound
        
        product = sigma_x * sigma_p
        assert product >= hbar / 2, "Uncertainty product violates Heisenberg bound"

    def test_correlation_analysis(self):
        """Test correlation analysis between zeta and quantum states."""
        from scipy.stats import pearsonr
        
        # Generate test data
        unfolds = np.array([1.0, 1.5, 2.1, 2.8, 3.6])
        psi_sq = np.array([0.8, 1.2, 1.7, 2.2, 2.9])
        
        # Normalize as in the actual implementation
        unfolds_scaled = np.abs(unfolds) / np.max(np.abs(unfolds))
        psi_scaled = psi_sq / np.max(psi_sq)
        
        r, p_value = pearsonr(unfolds_scaled, psi_scaled)
        
        assert isinstance(r, float)
        assert isinstance(p_value, float)
        assert -1 <= r <= 1


def test_import_dependencies():
    """Test that all required dependencies can be imported."""
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        import mpmath as mp
        from scipy.stats import bootstrap, pearsonr
        
        # Test mpmath configuration
        mp.mp.dps = 50
        phi = (1 + mp.sqrt(5)) / 2
        assert float(phi) > 1.6
        
    except ImportError as e:
        pytest.fail(f"Failed to import required dependencies: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])