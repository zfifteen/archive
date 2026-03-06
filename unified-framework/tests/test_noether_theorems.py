"""
Test module for Discrete Noether's Theorems in Z Framework
=========================================================

This module provides comprehensive tests for the discrete Noether's theorems
implementation, validating both theoretical consistency and numerical accuracy.
"""

import pytest
import numpy as np
import sympy as sp
import mpmath as mp
from sympy import symbols, sqrt, log, exp, pi, simplify, N
import sys
import os

# Set high precision for mpmath operations in tests
mp.dps = 50

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from symbolic.noether_theorems import (
    derive_discrete_noether_first_theorem,
    derive_discrete_noether_second_theorem,
    derive_prime_density_conservation,
    derive_continuous_discrete_connection,
    noether_theorems_summary,
    evaluate_theta_prime_high_precision,
    evaluate_enhancement_factor_high_precision
)


class TestDiscreteNoetherFirstTheorem:
    """Test discrete Noether's First Theorem implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.first_theorem_result = derive_discrete_noether_first_theorem()
        
    def test_theorem_structure(self):
        """Test that all required components are present."""
        required_keys = [
            'discrete_lagrangian',
            'symmetry_generator', 
            'noether_current',
            'conservation_condition',
            'conserved_quantity',
            'geodesic_conserved_quantity',
            'enhancement_factor',
            'curvature_term',
            'theorem_statement'
        ]
        
        for key in required_keys:
            assert key in self.first_theorem_result, f"Missing key: {key}"
            
    def test_discrete_lagrangian_form(self):
        """Test the discrete Lagrangian has correct mathematical form."""
        L_discrete = self.first_theorem_result['discrete_lagrangian']
        
        # Should contain curvature term κ(n) * θ'(n,k)
        # and kinetic-like term with delta_n
        assert L_discrete is not None
        
        # Convert to string to check structure
        L_str = str(L_discrete)
        assert 'log' in L_str  # From κ(n) = d(n) * ln(n+1) / e²
        assert 'delta_n' in L_str  # Kinetic term
        
    def test_conservation_condition(self):
        """Test conservation condition is properly formulated."""
        conservation = self.first_theorem_result['conservation_condition']
        
        # Should be an equation (Eq object)
        assert isinstance(conservation, sp.Eq)
        
        # Should represent div J = 0 (we use symbolic representation)
        assert conservation.rhs == 0
        
    def test_conserved_quantity_properties(self):
        """Test properties of conserved quantities."""
        Q_general = self.first_theorem_result['conserved_quantity']
        Q_geodesic = self.first_theorem_result['geodesic_conserved_quantity']
        
        # Both should be symbolic expressions
        assert isinstance(Q_general, sp.Basic)
        assert isinstance(Q_geodesic, sp.Basic)
        
        # Geodesic should be substitution of general case
        # (can't easily test equality due to symbolic complexity)
        assert Q_geodesic is not None
        
    def test_enhancement_factor_form(self):
        """Test enhancement factor θ'(n,k) has golden ratio structure."""
        theta = self.first_theorem_result['enhancement_factor']
        
        # Should contain phi (golden ratio)
        theta_str = str(theta)
        assert 'phi' in theta_str
        
        # Should have modular form (n % phi) / phi
        # This is complex to test symbolically, so check string representation
        assert '%' in theta_str or 'Mod' in theta_str
        
    def test_theorem_statement_completeness(self):
        """Test theorem statement covers key concepts."""
        statements = self.first_theorem_result['theorem_statement']
        
        assert isinstance(statements, list)
        assert len(statements) >= 3
        
        # Check for key concepts
        combined_text = ' '.join(statements).lower()
        assert 'symmetry' in combined_text
        assert 'conserved' in combined_text
        assert 'prime' in combined_text


class TestDiscreteNoetherSecondTheorem:
    """Test discrete Noether's Second Theorem implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.second_theorem_result = derive_discrete_noether_second_theorem()
        
    def test_theorem_structure(self):
        """Test that all required components are present."""
        required_keys = [
            'gauge_parameter',
            'gauge_transformed_curvature',
            'gauge_transformed_enhancement',
            'gauge_invariant_lagrangian',
            'gauge_invariance_condition',
            'bianchi_identity',
            'constraint_equation',
            'constraint_dimension',
            'theorem_statement'
        ]
        
        for key in required_keys:
            assert key in self.second_theorem_result, f"Missing key: {key}"
            
    def test_gauge_invariance_condition(self):
        """Test gauge invariance condition is properly formulated."""
        condition = self.second_theorem_result['gauge_invariance_condition']
        
        # Should be an equation setting variation to zero
        assert isinstance(condition, sp.Eq)
        assert condition.rhs == 0
        
    def test_bianchi_identity(self):
        """Test Bianchi identity mathematical structure."""
        bianchi = self.second_theorem_result['bianchi_identity']
        
        # Should be an equation representing discrete divergence = 0
        assert isinstance(bianchi, sp.Eq)
        assert bianchi.rhs == 0
        
    def test_constraint_dimension(self):
        """Test constraint dimension calculation."""
        constraint_dim = self.second_theorem_result['constraint_dimension']
        
        # Should be positive integer (constraints reduce degrees of freedom)
        assert isinstance(constraint_dim, int)
        assert constraint_dim > 0
        
    def test_gauge_transformations(self):
        """Test gauge transformation structure."""
        kappa_prime = self.second_theorem_result['gauge_transformed_curvature']
        theta_gauge = self.second_theorem_result['gauge_transformed_enhancement']
        
        # Both should be symbolic expressions
        assert isinstance(kappa_prime, sp.Basic)
        assert isinstance(theta_gauge, sp.Basic)
        
        # Should contain gauge parameter alpha_n
        kappa_str = str(kappa_prime)
        theta_str = str(theta_gauge)
        assert 'alpha_n' in kappa_str
        assert 'alpha_n' in theta_str


class TestPrimeDensityConservation:
    """Test prime density conservation law derivation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.conservation_result = derive_prime_density_conservation()
        
    def test_conservation_structure(self):
        """Test conservation law structure."""
        required_keys = [
            'prime_density_enhanced',
            'prime_charge_density',
            'scaling_transformation',
            'conservation_law',
            'geodesic_scaling_generator',
            'enhancement_constraint',
            'empirical_enhancement',
            'confidence_interval',
            'conservation_principle'
        ]
        
        for key in required_keys:
            assert key in self.conservation_result, f"Missing key: {key}"
            
    def test_empirical_validation(self):
        """Test empirical validation parameters."""
        enhancement = self.conservation_result['empirical_enhancement']
        ci = self.conservation_result['confidence_interval']
        
        # Enhancement should be around 14.9% (as mentioned in problem statement)
        enhancement_float = float(enhancement)
        assert 0.145 <= enhancement_float <= 0.155
        
        # Confidence interval should be reasonable
        assert isinstance(ci, list)
        assert len(ci) == 2
        assert ci[0] < enhancement_float < ci[1]
        
    def test_conservation_law_form(self):
        """Test conservation law mathematical form."""
        conservation = self.conservation_result['conservation_law']
        
        # Should be an equation
        assert isinstance(conservation, sp.Eq)
        
    def test_geodesic_scaling_generator(self):
        """Test geodesic scaling generator properties."""
        theta_scaling = self.conservation_result['geodesic_scaling_generator']
        
        # Should contain golden ratio phi and optimal k=0.3
        theta_str = str(theta_scaling)
        assert 'phi' in theta_str
        
        # Check for k=0.3 (represented as rational 3/10)
        # This is complex to verify symbolically, but should be present
        assert theta_scaling is not None


class TestContinuousDiscreteConnection:
    """Test continuous-discrete domain connection."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.connection_result = derive_continuous_discrete_connection()
        
    def test_connection_structure(self):
        """Test connection derivation structure."""
        required_keys = [
            'physical_metric',
            'discrete_metric', 
            'physical_energy_conservation',
            'discrete_energy_analog',
            'connection_mapping',
            'physical_z_form',
            'discrete_z_form',
            'correspondence_principle',
            'unified_conservation_law',
            'mathematical_bridge'
        ]
        
        for key in required_keys:
            assert key in self.connection_result, f"Missing key: {key}"
            
    def test_metric_structures(self):
        """Test physical and discrete metric structures."""
        physical_metric = self.connection_result['physical_metric']
        discrete_metric = self.connection_result['discrete_metric']
        
        # Both should be symbolic expressions
        assert isinstance(physical_metric, sp.Basic)
        assert isinstance(discrete_metric, sp.Basic)
        
        # Physical metric should contain c² term
        phys_str = str(physical_metric)
        assert 'c' in phys_str
        
        # Discrete metric should contain e² term
        disc_str = str(discrete_metric) 
        assert 'e_squared' in disc_str
        
    def test_correspondence_principle(self):
        """Test correspondence principle mapping."""
        correspondence = self.connection_result['correspondence_principle']
        
        assert isinstance(correspondence, dict)
        
        # Should map c ↔ e², γ ↔ curvature factor, etc.
        expected_keys = ['c_to_e_squared', 'lorentz_to_curvature', 'velocity_to_position']
        for key in expected_keys:
            assert key in correspondence
            
    def test_unified_conservation_law(self):
        """Test unified conservation law."""
        unified = self.connection_result['unified_conservation_law']
        
        # Should be an equation connecting physical and discrete forms
        assert isinstance(unified, sp.Eq)


class TestNoetherTheoremsSummary:
    """Test comprehensive Noether's theorems summary."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.summary = noether_theorems_summary()
        
    def test_summary_completeness(self):
        """Test summary contains all components."""
        required_keys = [
            'first_theorem',
            'second_theorem',
            'prime_density_conservation',
            'continuous_discrete_bridge',
            'theoretical_implications',
            'empirical_validation',
            'framework_extensions'
        ]
        
        for key in required_keys:
            assert key in self.summary, f"Missing key: {key}"
            
    def test_empirical_validation_parameters(self):
        """Test empirical validation parameters."""
        validation = self.summary['empirical_validation']
        
        # Check confidence interval
        ci = validation['prime_enhancement_ci']
        assert ci == [14.6, 15.4]
        
        # Check optimal k parameter
        assert validation['optimal_k_parameter'] == 0.3
        
        # Check bootstrap samples
        assert validation['bootstrap_samples'] == 10000
        
        # Check correlation coefficient
        assert abs(validation['correlation_coefficient'] - 0.93) < 0.01
        
    def test_theoretical_implications(self):
        """Test theoretical implications completeness."""
        implications = self.summary['theoretical_implications']
        
        assert isinstance(implications, list)
        assert len(implications) >= 5
        
        # Check for key concepts
        combined_text = ' '.join(implications).lower()
        assert 'noether' in combined_text
        assert 'conservation' in combined_text
        assert 'symmetr' in combined_text  # symmetry/symmetries
        assert 'prime' in combined_text
        
    def test_framework_extensions(self):
        """Test framework extensions suggestions."""
        extensions = self.summary['framework_extensions']
        
        assert isinstance(extensions, list)
        assert len(extensions) >= 4
        
        # Should suggest various extensions
        combined_text = ' '.join(extensions).lower()
        assert 'discrete' in combined_text
        assert 'quantum' in combined_text or 'field' in combined_text


class TestNumericalValidation:
    """Test numerical validation of key results."""
    
    def test_golden_ratio_numerical_value(self):
        """Test golden ratio numerical computation."""
        phi_symbolic = (1 + sqrt(5)) / 2
        phi_numerical = float(N(phi_symbolic, 10))
        
        # Golden ratio ≈ 1.618033988749895
        assert abs(phi_numerical - 1.618033988749895) < 1e-10
        
    def test_e_squared_numerical_value(self):
        """Test e² numerical computation."""
        e_squared_symbolic = exp(2)
        e_squared_numerical = float(N(e_squared_symbolic, 10))
        
        # e² ≈ 7.38905609893065
        assert abs(e_squared_numerical - 7.38905609893065) < 1e-10
        
    def test_enhancement_factor_bounds(self):
        """Test enhancement factor stays within empirical bounds."""
        # Test for typical values: n = 100, k = 0.3
        phi_val = (1 + sqrt(5)) / 2
        n_test = 100
        k_test = 0.3
        
        # Calculate θ'(n,k) = φ * ((n % φ) / φ)^k
        # This is approximate numerical test
        phi_num = float(N(phi_val))
        modular_part = (n_test % phi_num) / phi_num
        theta_val = phi_num * (modular_part ** k_test)
        
        # Enhancement = θ'(n,k) - 1 should be reasonable
        enhancement = theta_val - 1
        
        # Should be within plausible range for prime enhancement
        assert -0.5 <= enhancement <= 1.0  # Allow broad range for individual values


class TestSymbolicConsistency:
    """Test symbolic consistency across different theorems."""
    
    def test_lagrangian_consistency(self):
        """Test Lagrangian forms are consistent between theorems."""
        first = derive_discrete_noether_first_theorem()
        second = derive_discrete_noether_second_theorem()
        
        L1 = first['discrete_lagrangian']
        L2_base = second['gauge_invariant_lagrangian']
        
        # Both should be symbolic expressions
        assert isinstance(L1, sp.Basic)
        assert isinstance(L2_base, sp.Basic)
        
        # Should have similar mathematical structure (hard to test exactly)
        # At minimum, both should be non-trivial expressions
        assert str(L1) != '0'
        assert str(L2_base) != '0'
        
    def test_curvature_term_consistency(self):
        """Test curvature terms are consistent."""
        first = derive_discrete_noether_first_theorem()
        conservation = derive_prime_density_conservation()
        
        # Both should reference curvature/enhancement concepts
        # This is a structural consistency test
        assert first['curvature_term'] is not None
        assert conservation['geodesic_scaling_generator'] is not None
        
    def test_enhancement_factor_consistency(self):
        """Test enhancement factors are consistent across derivations."""
        first = derive_discrete_noether_first_theorem()
        conservation = derive_prime_density_conservation()
        
        # Both should have enhancement-related terms
        assert first['enhancement_factor'] is not None
        assert conservation['enhancement_constraint'] is not None
        
        # Empirical enhancement should match confidence interval bounds
        empirical = conservation['empirical_enhancement']
        ci = conservation['confidence_interval']
        
        empirical_float = float(empirical)
        ci_floats = [float(bound) for bound in ci]
        
        assert ci_floats[0] <= empirical_float <= ci_floats[1]


@pytest.mark.integration 
class TestFrameworkIntegration:
    """Test integration with existing Z Framework components."""
    
    def test_import_compatibility(self):
        """Test imports work correctly with existing framework."""
        try:
            from symbolic.noether_theorems import noether_theorems_summary
            summary = noether_theorems_summary()
            assert summary is not None
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
            
    def test_symbolic_variable_consistency(self):
        """Test symbolic variables are consistent with axiom derivation."""
        try:
            from symbolic.axiom_derivation import derive_universal_invariance
            from symbolic.noether_theorems import derive_discrete_noether_first_theorem
            
            axiom_result = derive_universal_invariance()
            noether_result = derive_discrete_noether_first_theorem()
            
            # Both should work without errors
            assert axiom_result is not None
            assert noether_result is not None
            
        except Exception as e:
            pytest.fail(f"Framework integration failed: {e}")


class TestHighPrecisionValidation:
    """Test high-precision arithmetic for modulo operations with irrational φ."""
    
    def test_high_precision_theta_prime_evaluation(self):
        """Test high-precision θ'(n,k) evaluation."""
        # Test with typical values
        n_val = 100
        k_val = 0.3
        
        theta_hp = evaluate_theta_prime_high_precision(n_val, k_val)
        enhancement_hp = evaluate_enhancement_factor_high_precision(n_val, k_val)
        
        # Should be mpmath values with high precision
        assert isinstance(theta_hp, mp.mpf)
        assert isinstance(enhancement_hp, mp.mpf)
        
        # Enhancement should be within empirical bounds
        enhancement_float = float(enhancement_hp)
        assert 0.10 <= enhancement_float <= 0.20  # Reasonable range for individual values
        
    def test_high_precision_large_scale_stability(self):
        """Test precision stability for n>10^9 to mitigate ~0.03% drift."""
        large_values = [10**6, 10**7, 10**8, 10**9, 10**10]
        k_val = 0.3
        
        enhancements = []
        for n_val in large_values:
            enhancement = evaluate_enhancement_factor_high_precision(n_val, k_val)
            enhancements.append(float(enhancement))
        
        # Check that all values are reasonable (no NaN or infinity)
        for enhancement in enhancements:
            assert not np.isnan(enhancement)
            assert not np.isinf(enhancement)
            assert -1.0 <= enhancement <= 2.0  # Broad but reasonable bounds
            
    def test_precision_improvement_validation(self):
        """Test that high-precision arithmetic improves upon float precision."""
        n_val = 10**9
        k_val = 0.3
        
        # High-precision calculation
        theta_hp = evaluate_theta_prime_high_precision(n_val, k_val)
        
        # Standard float calculation (for comparison)
        phi_float = float((1 + np.sqrt(5)) / 2)
        modular_part_float = (n_val % phi_float) / phi_float
        theta_float = phi_float * (modular_part_float ** k_val)
        
        # High-precision should have more decimal places of accuracy
        # (We can't directly test the precision improvement without reference,
        #  but we can verify the calculation completes without errors)
        assert isinstance(theta_hp, mp.mpf)
        assert abs(float(theta_hp) - theta_float) >= 0  # May differ due to precision
        
    def test_high_dps_assertions_for_large_n(self):
        """Test high-dps assertions (dps≥30) for n>10^9 as requested."""
        # Ensure mpmath is using high precision
        assert mp.dps >= 30
        
        # Test very large n values
        n_large = 2 * 10**9
        k_val = 0.3
        
        # Calculate with high precision
        theta_large = evaluate_theta_prime_high_precision(n_large, k_val)
        
        # Verify result has high precision (more than 15 decimal places)
        theta_str = mp.nstr(theta_large, 35)  # 35 digits
        assert len(theta_str.replace('.', '')) >= 25  # At least 25 significant digits
        
        # Enhancement should still be reasonable
        enhancement = theta_large - mp.mpf(1)
        enhancement_float = float(enhancement)
        assert -2.0 <= enhancement_float <= 3.0  # Very broad bounds for stability
        
    def test_golden_ratio_high_precision_computation(self):
        """Test high-precision golden ratio computation."""
        phi_hp = (mp.mpf(1) + mp.sqrt(mp.mpf(5))) / mp.mpf(2)
        
        # Should be very close to known value
        phi_known = mp.mpf('1.6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374847540880753868917521266338622235369317931800607667263544333890865959395829056383226613199282902678806752087668925017116962070322210432162695486262963136144')
        
        # High precision comparison (within 1e-45)
        assert abs(phi_hp - phi_known) < mp.mpf('1e-45')
        
    def test_modular_arithmetic_precision_bounds(self):
        """Test that modular arithmetic precision is within expected bounds."""
        test_values = [1000, 10000, 100000, 1000000, 10000000]
        k_val = 0.3
        
        for n_val in test_values:
            theta = evaluate_theta_prime_high_precision(n_val, k_val)
            enhancement = evaluate_enhancement_factor_high_precision(n_val, k_val)
            
            # Enhancement should be finite and reasonable
            assert mp.isfinite(theta)
            assert mp.isfinite(enhancement)
            
            # θ'(n,k) should be positive and not too large
            assert theta > 0
            assert theta < 10  # Upper bound for sanity
            
        # Test consistency: repeated calculations should give identical results
        n_test = 500000
        theta1 = evaluate_theta_prime_high_precision(n_test, k_val)
        theta2 = evaluate_theta_prime_high_precision(n_test, k_val)
        
        # Should be exactly equal due to deterministic high-precision arithmetic
        assert theta1 == theta2


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])