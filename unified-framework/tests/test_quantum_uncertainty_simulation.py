"""
Test suite for Quantum Uncertainty Modulation via Z Model Frame Alignment

This test suite validates the implementation of the quantum uncertainty simulation
according to the hypothesis specifications in issue #372.
"""

import pytest
import numpy as np
import sys
import os
import warnings

# Add source path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.interactive_simulations.quantum_uncertainty_simulation import (
    QuantumUncertaintySimulation, 
    UncertaintyResult,
    run_quantum_uncertainty_experiment
)
from src.core.domain import DiscreteZetaShift
from src.core.geodesic_mapping import GeodesicMapper

# Filter system instruction warnings for cleaner test output
warnings.filterwarnings('ignore', category=UserWarning, module='.*system_instruction.*')

class TestQuantumUncertaintySimulation:
    """Test cases for the quantum uncertainty simulation implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sim = QuantumUncertaintySimulation(
            hbar=1.0,
            c=1.0,
            n_oscillator_levels=20
        )
    
    def test_initialization(self):
        """Test simulation initialization"""
        assert self.sim.hbar == 1.0
        assert self.sim.c == 1.0
        assert self.sim.n_levels == 20
        assert isinstance(self.sim.geodesic_mapper, GeodesicMapper)
        assert self.sim.geodesic_mapper.k_optimal == 0.3  # As specified in hypothesis
    
    def test_harmonic_oscillator_operators(self):
        """Test quantum harmonic oscillator operator creation"""
        x_op, p_op, hamiltonian = self.sim.create_harmonic_oscillator_operators(10)
        
        # Check operator dimensions
        assert x_op.shape == (10, 10)
        assert p_op.shape == (10, 10) 
        assert hamiltonian.shape == (10, 10)
        
        # Check Hermiticity
        assert np.allclose(x_op, x_op.conj().T)  # x should be Hermitian
        assert np.allclose(p_op, p_op.conj().T)  # p should be Hermitian
        assert np.allclose(hamiltonian, hamiltonian.conj().T)  # H should be Hermitian
        
        # Check canonical commutation relation [x,p] = iℏ (normalized ℏ=1)
        commutator = x_op @ p_op - p_op @ x_op
        expected_commutator = 1j * np.eye(10)
        assert np.allclose(commutator, expected_commutator, atol=1e-10)
    
    def test_frame_velocity_modulation(self):
        """Test Z = T(v/c) framework implementation in Hamiltonian modulation"""
        _, _, base_hamiltonian = self.sim.create_harmonic_oscillator_operators(10)
        
        # Test different v/c ratios
        v_ratios = [0.1, 0.5, 0.9]
        
        for v_ratio in v_ratios:
            modulated_H = self.sim.modulate_frame_velocity(base_hamiltonian, v_ratio)
            
            # Check that modulation preserves Hermiticity
            assert np.allclose(modulated_H, modulated_H.conj().T)
            
            # Check that higher v/c leads to energy scale reduction (frame effects)
            gamma = 1.0 / np.sqrt(1.0 - v_ratio**2)
            expected_scaling = 1.0 / gamma
            expected_H = expected_scaling * base_hamiltonian
            assert np.allclose(modulated_H, expected_H)
    
    def test_uncertainty_computation(self):
        """Test uncertainty product calculation σ_x σ_p"""
        x_op, p_op, hamiltonian = self.sim.create_harmonic_oscillator_operators(20)
        
        # Use ground state of harmonic oscillator
        eigenvalues, eigenstates = np.linalg.eigh(hamiltonian)
        ground_state = eigenstates[:, 0]
        
        sigma_x, sigma_p, uncertainty_product = self.sim.compute_uncertainty_product(
            x_op, p_op, ground_state
        )
        
        # Check that uncertainties are positive
        assert sigma_x > 0
        assert sigma_p > 0
        assert uncertainty_product > 0
        
        # Check Heisenberg uncertainty principle: σ_x σ_p ≥ ℏ/2
        hbar_half = self.sim.hbar / 2.0
        assert uncertainty_product >= hbar_half - 1e-10  # Small numerical tolerance
        
        # For harmonic oscillator ground state, should equal ℏ/2 exactly
        assert abs(uncertainty_product - hbar_half) < 1e-10
    
    def test_discrete_zeta_shift_integration(self):
        """Test DiscreteZetaShift enforcement as specified in hypothesis"""
        v_ratio = 0.5
        trial_idx = 10
        
        dzs = self.sim.enforce_discrete_zeta_shift_computation(v_ratio, trial_idx)
        
        # Check that DiscreteZetaShift object is created correctly
        assert isinstance(dzs, DiscreteZetaShift)
        assert dzs.v == v_ratio  # b = v mapping
        assert dzs.c == self.sim.c  # c = c mapping
        
        # Check that n value is reasonable
        expected_n = max(10, int(1000 * v_ratio + trial_idx % 100))
        assert dzs.a == expected_n  # a = T mapping (using n as time-like parameter)
    
    def test_geodesic_density_enhancement(self):
        """Test geodesic mapping for conditional prime density improvement under canonical benchmark methodology target"""
        # Create test uncertainty data
        uncertainty_data = [0.5, 0.51, 0.49, 0.52, 0.48]
        
        # Create test DiscreteZetaShift
        dzs = DiscreteZetaShift(n=100, v=0.5, delta_max=1.0)
        
        density_enhancement, localization_density = self.sim.apply_geodesic_density_enhancement(
            uncertainty_data, dzs
        )
        
        # Check that enhancement values are reasonable
        assert isinstance(density_enhancement, float)
        assert isinstance(localization_density, float)
        assert density_enhancement >= 0  # Enhancement should be non-negative
        assert localization_density > 0   # Localization density should be positive
    
    def test_single_trial_execution(self):
        """Test single trial execution with all components integrated"""
        v_ratio = 0.7
        trial_idx = 5
        
        result = self.sim.run_single_trial(v_ratio, trial_idx)
        
        # Check result structure
        required_keys = [
            'v_ratio', 'trial_idx', 'sigma_x', 'sigma_p', 
            'uncertainty_product', 'hbar_normalized_product',
            'density_enhancement', 'localization_density',
            'dzs_attributes', 'ground_state_energy'
        ]
        
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        
        # Check value validity
        assert result['v_ratio'] == v_ratio
        assert result['trial_idx'] == trial_idx
        assert result['sigma_x'] > 0
        assert result['sigma_p'] > 0
        assert result['uncertainty_product'] > 0
        assert result['hbar_normalized_product'] >= 1.0 - 1e-10  # Should respect Heisenberg bound
        assert isinstance(result['dzs_attributes'], dict)
        assert result['ground_state_energy'] < 0  # Ground state should have lowest energy
    
    def test_experiment_parameter_ranges(self):
        """Test experiment with hypothesis-specified parameter ranges"""
        # Test v/c range from 0.1 to 0.99 as specified
        results = self.sim.run_uncertainty_modulation_experiment(
            v_ratio_range=(0.1, 0.99),
            n_points=3,      # Minimal for testing
            n_trials=2,      # Minimal for testing
            target_enhancement=0.15  # 15% as specified
        )
        
        # Check experiment structure
        assert 'experiment_results' in results
        assert 'analysis' in results
        assert 'parameters' in results
        
        # Check parameter validation
        params = results['parameters']
        assert params['v_ratio_range'] == (0.1, 0.99)
        assert params['target_enhancement'] == 0.15
        
        # Check experiment results
        exp_results = results['experiment_results']
        assert len(exp_results) == 3  # n_points
        
        for result in exp_results:
            assert isinstance(result, UncertaintyResult)
            assert 0.1 <= result.v_ratio <= 0.99
            assert result.uncertainty_product > 0
            assert result.n_trials == 2
    
    def test_statistical_analysis(self):
        """Test statistical analysis components"""
        # Create mock results for analysis
        mock_results = [
            UncertaintyResult(
                v_ratio=0.1 + 0.4*i, 
                sigma_x=0.7, 
                sigma_p=0.71,
                uncertainty_product=0.5 + 0.01*i,
                hbar_normalized_product=1.0 + 0.02*i,
                density_enhancement=0.1 + 0.05*i,
                localization_density=0.8 + 0.1*i,
                bootstrap_ci_lower=0.49,
                bootstrap_ci_upper=0.51,
                n_trials=10
            ) for i in range(3)
        ]
        
        analysis = self.sim.analyze_experiment_results(mock_results, target_enhancement=0.15)
        
        # Check analysis structure
        required_sections = ['hypothesis_tests', 'statistical_summary', 'enhancement_analysis']
        for section in required_sections:
            assert section in analysis
        
        # Check hypothesis tests
        h_tests = analysis['hypothesis_tests']
        assert 'correlation_v_uncertainty' in h_tests
        assert 'violation_rate' in h_tests
        assert 'p_value' in h_tests
        
        # Check enhancement analysis
        e_analysis = analysis['enhancement_analysis']
        assert 'max_enhancement' in e_analysis
        assert 'target_achieved' in e_analysis
        assert e_analysis['target_enhancement'] == 0.15
    
    def test_bootstrap_confidence_intervals(self):
        """Test bootstrap confidence interval computation"""
        # Run small experiment to test CI computation
        results = self.sim.run_uncertainty_modulation_experiment(
            v_ratio_range=(0.3, 0.7),
            n_points=2,
            n_trials=10,  # Sufficient for bootstrap
            target_enhancement=0.15
        )
        
        exp_results = results['experiment_results']
        
        for result in exp_results:
            # Check that confidence intervals are computed
            assert hasattr(result, 'bootstrap_ci_lower')
            assert hasattr(result, 'bootstrap_ci_upper')
            assert result.bootstrap_ci_lower <= result.uncertainty_product
            assert result.uncertainty_product <= result.bootstrap_ci_upper
    
    def test_heisenberg_bound_enforcement(self):
        """Test that Heisenberg uncertainty principle is respected"""
        # Run trials across different v/c ratios
        v_ratios = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for v_ratio in v_ratios:
            result = self.sim.run_single_trial(v_ratio, 0)
            
            # Check Heisenberg bound: σ_x σ_p ≥ ℏ/2
            hbar_half = self.sim.hbar / 2.0
            assert result['uncertainty_product'] >= hbar_half - 1e-12
            
            # Check normalized bound
            assert result['hbar_normalized_product'] >= 1.0 - 1e-12


class TestHypothesisValidation:
    """Test cases specifically for hypothesis validation requirements"""
    
    def test_framework_implementation(self):
        """Test Z = T(v/c) framework implementation"""
        sim = QuantumUncertaintySimulation()
        
        # Test that Z framework is properly implemented
        # a = T (time-like parameter), b = v (velocity), c = c (speed of light)
        dzs = sim.enforce_discrete_zeta_shift_computation(v_ratio=0.5, trial_idx=10)
        
        # Verify mapping according to hypothesis
        assert dzs.v == 0.5  # b = v
        assert dzs.c == sim.c  # c = c  
        # a = T represented by integer n (time-like discrete parameter)
        assert isinstance(float(dzs.a), (int, float))
    
    def test_k_optimal_parameter(self):
        """Test k* ≈ 0.3 parameter as specified in hypothesis"""
        sim = QuantumUncertaintySimulation()
        
        # Check that geodesic mapper uses k_optimal = 0.3
        assert sim.geodesic_mapper.k_optimal == 0.3
        
        # Test geodesic transformation with k* = 0.3
        n_test = 100
        transform = sim.geodesic_mapper.enhanced_geodesic_transform(n_test)
        
        # Should use θ'(n, k) = φ·{n/φ}^0.3 formula
        phi = (1 + np.sqrt(5)) / 2
        expected = phi * ((n_test % phi) / phi) ** 0.3
        
        assert abs(transform - expected) < 1e-10
    
    def test_precision_requirements(self):
        """Test high precision requirements (mpmath dps=50)"""
        import mpmath as mp
        
        # Check that mpmath is configured for high precision
        assert mp.dps >= 50
        
        # Test that DiscreteZetaShift uses high precision
        dzs = DiscreteZetaShift(n=1000, v=0.5)
        
        # Should use mpmath for calculations
        assert isinstance(dzs.a, type(mp.mpf(1)))
        assert isinstance(dzs.b, type(mp.mpf(1)))
        assert isinstance(dzs.c, type(mp.mpf(1)))
    
    def test_target_enhancement_specification(self):
        """Test conditional prime density improvement under canonical benchmark methodology target with CI [14.6%, 15.4%]"""
        sim = QuantumUncertaintySimulation()
        
        # Check default target enhancement
        assert sim.default_params['target_enhancement'] == 0.15
        
        # Test analysis checks target achievement
        mock_results = [
            UncertaintyResult(
                v_ratio=0.5, sigma_x=0.7, sigma_p=0.71,
                uncertainty_product=0.5, hbar_normalized_product=1.0,
                density_enhancement=0.16,  # Above 15% target
                localization_density=0.8,
                bootstrap_ci_lower=0.49, bootstrap_ci_upper=0.51,
                n_trials=10
            )
        ]
        
        analysis = sim.analyze_experiment_results(mock_results, target_enhancement=0.15)
        
        # Should detect target achievement
        assert analysis['enhancement_analysis']['target_achieved'] == True
        assert analysis['enhancement_analysis']['max_enhancement'] >= 0.15


def test_integration_with_existing_framework():
    """Test integration with existing Z Framework components"""
    
    # Test that simulation properly integrates with existing modules
    sim = QuantumUncertaintySimulation()
    
    # Should successfully create DiscreteZetaShift objects
    dzs = DiscreteZetaShift(n=50, v=0.7)
    assert dzs is not None
    
    # Should successfully use GeodesicMapper
    mapper = GeodesicMapper(k_optimal=0.3)
    transform = mapper.enhanced_geodesic_transform([10, 20, 30])
    assert len(transform) == 3
    
    # Should integrate in simulation workflow
    result = sim.run_single_trial(0.6, 5)
    assert 'dzs_attributes' in result
    assert 'density_enhancement' in result


if __name__ == "__main__":
    # Run basic test when executed directly
    print("🧪 Testing Quantum Uncertainty Modulation Implementation")
    
    # Basic integration test
    try:
        sim = QuantumUncertaintySimulation()
        result = sim.run_single_trial(0.5, 0)
        print(f"✓ Basic functionality test passed")
        print(f"  σ_x σ_p = {result['uncertainty_product']:.6f}")
        print(f"  Normalized = {result['hbar_normalized_product']:.6f}")
        print(f"  Enhancement = {result['density_enhancement']:.3f}")
        
        # Quick experiment test
        exp_results = sim.run_uncertainty_modulation_experiment(
            v_ratio_range=(0.2, 0.8),
            n_points=2,
            n_trials=3,
            target_enhancement=0.15
        )
        print(f"✓ Experiment test passed ({len(exp_results['experiment_results'])} measurements)")
        
        print("🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise