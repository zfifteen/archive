"""
Comprehensive Test Suite for Cornerstone Invariant Framework

Tests the fundamental invariant principle Z = A(B/c) across all domains:
1. Physical domain (relativity)
2. Discrete mathematical domain (prime densities)
3. Number-theoretic domain (geodesic transformations)
4. Cross-domain validation
"""

import pytest
import sys
import os
from math import e, sqrt

# Direct path manipulation to ensure imports work in test environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from cornerstone_invariant import (
    CornerstoneInvariant,
    PhysicalInvariant,
    DiscreteInvariant,
    NumberTheoreticInvariant,
    demonstrate_invariant_universality,
    validate_cornerstone_principle
)


class TestCornerstoneInvariant:
    """Test base CornerstoneInvariant class."""
    
    def test_initialization(self):
        """Test invariant initialization."""
        inv = CornerstoneInvariant(c=100.0, domain="test")
        assert float(inv.c) == 100.0
        assert inv.domain == "test"
    
    def test_initialization_negative_c(self):
        """Test that negative c raises ValueError."""
        with pytest.raises(ValueError, match="Invariant c must be positive"):
            CornerstoneInvariant(c=-100.0)
    
    def test_initialization_zero_c(self):
        """Test that zero c raises ValueError."""
        with pytest.raises(ValueError, match="Invariant c must be positive"):
            CornerstoneInvariant(c=0.0)
    
    def test_compute_z_scalar(self):
        """Test Z computation with scalar A."""
        inv = CornerstoneInvariant(c=100.0)
        result = inv.compute_z(A=10.0, B=50.0)
        expected = 10.0 * (50.0 / 100.0)
        assert abs(float(result) - expected) < 1e-10
    
    def test_compute_z_function(self):
        """Test Z computation with callable A."""
        inv = CornerstoneInvariant(c=100.0)
        
        def square_func(x):
            return x ** 2
        
        result = inv.compute_z(A=square_func, B=50.0)
        ratio = 50.0 / 100.0
        expected = ratio ** 2
        assert abs(float(result) - expected) < 1e-10
    
    def test_get_invariant_properties(self):
        """Test getting invariant properties."""
        inv = CornerstoneInvariant(c=100.0, domain="test")
        props = inv.get_invariant_properties()
        
        assert props['domain'] == "test"
        assert props['invariant_c'] == 100.0
        assert 'universality' in props
        assert 'symmetry' in props
        assert 'reproducibility' in props


class TestPhysicalInvariant:
    """Test PhysicalInvariant for relativistic transformations."""
    
    def test_initialization(self):
        """Test physical invariant initialization."""
        phys = PhysicalInvariant()
        assert float(phys.c) == 299792458.0
        assert phys.domain == "physical"
    
    def test_time_dilation_zero_velocity(self):
        """Test time dilation at zero velocity."""
        phys = PhysicalInvariant()
        result = phys.time_dilation(1.0, 0.0)
        # At v=0, time dilation should be 1 (no dilation)
        assert abs(float(result) - 1.0) < 1e-10
    
    def test_time_dilation_half_c(self):
        """Test time dilation at v = 0.5c."""
        phys = PhysicalInvariant()
        result = phys.time_dilation(1.0, 0.5 * phys.c)
        # γ = 1/√(1-0.5²) = 1/√0.75 ≈ 1.1547
        expected = 1.0 / sqrt(1 - 0.5**2)
        assert abs(float(result) - expected) < 1e-6
    
    def test_time_dilation_causality_violation(self):
        """Test that v >= c raises ValueError."""
        phys = PhysicalInvariant()
        with pytest.raises(ValueError, match="Causality violation"):
            phys.time_dilation(1.0, phys.c)
        
        with pytest.raises(ValueError, match="Causality violation"):
            phys.time_dilation(1.0, 1.5 * phys.c)
    
    def test_length_contraction_zero_velocity(self):
        """Test length contraction at zero velocity."""
        phys = PhysicalInvariant()
        result = phys.length_contraction(10.0, 0.0)
        # At v=0, no contraction
        assert abs(float(result) - 10.0) < 1e-10
    
    def test_length_contraction_high_velocity(self):
        """Test length contraction at v = 0.8c."""
        phys = PhysicalInvariant()
        result = phys.length_contraction(10.0, 0.8 * phys.c)
        # L = L₀√(1-0.8²) = 10√0.36 = 6.0
        expected = 10.0 * sqrt(1 - 0.8**2)
        assert abs(float(result) - expected) < 1e-6
    
    def test_length_contraction_causality_violation(self):
        """Test that v >= c raises ValueError."""
        phys = PhysicalInvariant()
        with pytest.raises(ValueError, match="Causality violation"):
            phys.length_contraction(10.0, phys.c)
    
    def test_relativistic_momentum(self):
        """Test relativistic momentum calculation."""
        phys = PhysicalInvariant()
        mass = 1.0  # kg
        velocity = 0.6 * phys.c
        
        result = phys.relativistic_momentum(mass, velocity)
        
        # p = γmv, where γ = 1/√(1-0.6²) = 1.25
        gamma = 1.0 / sqrt(1 - 0.6**2)
        expected = mass * velocity * gamma
        
        assert abs(float(result) - expected) < 1e-6


class TestDiscreteInvariant:
    """Test DiscreteInvariant for discrete mathematical domain."""
    
    def test_initialization_default(self):
        """Test discrete invariant with default e²."""
        discrete = DiscreteInvariant()
        assert abs(float(discrete.c) - e**2) < 1e-10
        assert discrete.domain == "discrete"
    
    def test_initialization_custom(self):
        """Test discrete invariant with custom delta_max."""
        discrete = DiscreteInvariant(delta_max=10.0)
        assert float(discrete.c) == 10.0
    
    def test_compute_normalized_density(self):
        """Test normalized density computation."""
        discrete = DiscreteInvariant()
        result = discrete.compute_normalized_density(n=1000, delta_n=0.5)
        
        # Z = n * (delta_n / c)
        expected = 1000 * (0.5 / (e**2))
        assert abs(float(result) - expected) < 1e-10
    
    def test_compute_divisor_scaling(self):
        """Test divisor-based scaling computation."""
        discrete = DiscreteInvariant()
        result = discrete.compute_divisor_scaling(n=100)
        
        # Should return a positive value
        assert float(result) > 0
        
        # Larger n should give larger result
        result_larger = discrete.compute_divisor_scaling(n=1000)
        assert float(result_larger) > float(result)
    
    def test_compute_divisor_scaling_edge_cases(self):
        """Test divisor scaling edge cases."""
        discrete = DiscreteInvariant()
        
        # n = 1 should work
        result = discrete.compute_divisor_scaling(n=1)
        assert float(result) >= 0
        
        # n = 0 should return 0
        result_zero = discrete.compute_divisor_scaling(n=0)
        assert float(result_zero) == 0


class TestNumberTheoreticInvariant:
    """Test NumberTheoreticInvariant for number-theoretic domain."""
    
    def test_initialization_default(self):
        """Test number-theoretic invariant with golden ratio."""
        nt = NumberTheoreticInvariant()
        golden_ratio = (1 + sqrt(5)) / 2
        assert abs(float(nt.c) - golden_ratio) < 1e-10
        assert nt.domain == "number_theoretic"
    
    def test_initialization_custom(self):
        """Test number-theoretic invariant with custom constant."""
        nt = NumberTheoreticInvariant(invariant_constant=2.0)
        assert float(nt.c) == 2.0
    
    def test_compute_geodesic_transform(self):
        """Test geodesic transformation computation."""
        nt = NumberTheoreticInvariant()
        result = nt.compute_geodesic_transform(n=100, k=0.3)
        
        # θ'(n,k) = φ·{n/φ}^k
        golden = float(nt.c)
        ratio = 100 / golden
        expected = golden * (ratio ** 0.3)
        
        assert abs(float(result) - expected) < 1e-6
    
    def test_geodesic_transform_scaling(self):
        """Test that geodesic transform scales appropriately."""
        nt = NumberTheoreticInvariant()
        
        # Larger n should give larger result (for k > 0)
        result_small = nt.compute_geodesic_transform(n=10, k=0.3)
        result_large = nt.compute_geodesic_transform(n=100, k=0.3)
        
        assert float(result_large) > float(result_small)
        
        # Larger k should affect scaling
        result_k_small = nt.compute_geodesic_transform(n=100, k=0.1)
        result_k_large = nt.compute_geodesic_transform(n=100, k=0.9)
        
        # Both should be positive and finite
        assert float(result_k_small) > 0
        assert float(result_k_large) > 0


class TestCrossDomainValidation:
    """Test cross-domain consistency and validation."""
    
    def test_demonstrate_universality(self):
        """Test universality demonstration function."""
        results = demonstrate_invariant_universality()
        
        # Should have results for all three domains
        assert 'physical' in results
        assert 'discrete' in results
        assert 'number_theoretic' in results
        
        # Each should have required fields
        for domain in ['physical', 'discrete', 'number_theoretic']:
            assert 'domain' in results[domain]
            assert 'invariant' in results[domain]
            assert 'example' in results[domain]
            assert 'result' in results[domain]
            
            # Result should be a finite number
            assert isinstance(results[domain]['result'], float)
            assert not (results[domain]['result'] == float('inf'))
    
    def test_validate_cornerstone_principle(self):
        """Test cornerstone principle validation."""
        validation = validate_cornerstone_principle()
        
        # Should have all required checks
        required_checks = [
            'universality_check',
            'consistency_check',
            'reproducibility_check',
            'symmetry_check',
            'precision_check',
            'overall_pass'
        ]
        
        for check in required_checks:
            assert check in validation
            assert isinstance(validation[check], bool)
    
    def test_cross_domain_equation_consistency(self):
        """Test that Z = A(B/c) is consistent across domains."""
        # Create instances
        phys = PhysicalInvariant()
        discrete = DiscreteInvariant()
        nt = NumberTheoreticInvariant()
        
        # Test with same A and B (scaled appropriately)
        A = 10.0
        B = 50.0
        
        # All should compute without error
        result_phys = phys.compute_z(A=A, B=B, validate_precision=False)
        result_discrete = discrete.compute_z(A=A, B=B, validate_precision=False)
        result_nt = nt.compute_z(A=A, B=B, validate_precision=False)
        
        # All should be finite
        assert float(result_phys) != float('inf')
        assert float(result_discrete) != float('inf')
        assert float(result_nt) != float('inf')
        
        # When scaled by their invariants, should follow expected relationship
        # Z_i = A * (B / c_i)
        assert abs(float(result_phys) - A * (B / float(phys.c))) < 1e-6
        assert abs(float(result_discrete) - A * (B / float(discrete.c))) < 1e-6
        assert abs(float(result_nt) - A * (B / float(nt.c))) < 1e-6


class TestNumericalPrecision:
    """Test numerical precision and stability."""
    
    def test_high_precision_maintained(self):
        """Test that high precision is maintained in computations."""
        inv = CornerstoneInvariant(c=100.0, precision_threshold=1e-16)
        
        # Should not raise with normal computation
        result = inv.compute_z(A=10.0, B=50.0, validate_precision=True)
        assert float(result) > 0
    
    def test_precision_validation_function(self):
        """Test precision validation through public interface."""
        inv = CornerstoneInvariant(c=100.0, precision_threshold=1e-16)
        
        # Normal result with validation enabled should pass
        result = inv.compute_z(A=10.0, B=50.0, validate_precision=True)
        # If no exception raised, precision validation passed
        assert float(result) > 0
    
    def test_reproducibility(self):
        """Test that same inputs always give same outputs."""
        discrete = DiscreteInvariant()
        
        # Compute same value multiple times
        results = [discrete.compute_divisor_scaling(n=500) for _ in range(10)]
        
        # All should be identical (within floating point precision)
        for i in range(1, len(results)):
            assert abs(float(results[i]) - float(results[0])) < 1e-15


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_velocity_physical(self):
        """Test physical domain at zero velocity."""
        phys = PhysicalInvariant()
        
        # Time dilation at v=0 should be 1
        t = phys.time_dilation(5.0, 0.0)
        assert abs(float(t) - 5.0) < 1e-10
        
        # Length contraction at v=0 should be rest length
        l = phys.length_contraction(10.0, 0.0)
        assert abs(float(l) - 10.0) < 1e-10
    
    def test_small_n_discrete(self):
        """Test discrete domain with small n."""
        discrete = DiscreteInvariant()
        
        # Should handle n=1
        result = discrete.compute_normalized_density(n=1, delta_n=0.1)
        assert float(result) >= 0
        
        # Should handle n=2
        result = discrete.compute_normalized_density(n=2, delta_n=0.1)
        assert float(result) > 0
    
    def test_large_k_geodesic(self):
        """Test geodesic with large k values."""
        nt = NumberTheoreticInvariant()
        
        # Should handle k=1.0
        result = nt.compute_geodesic_transform(n=100, k=1.0)
        assert float(result) > 0
        
        # Should handle k=2.0
        result = nt.compute_geodesic_transform(n=100, k=2.0)
        assert float(result) > 0


class TestIntegration:
    """Integration tests with framework."""
    
    def test_invariant_properties_all_domains(self):
        """Test getting properties from all domain invariants."""
        domains = [
            PhysicalInvariant(),
            DiscreteInvariant(),
            NumberTheoreticInvariant(),
            CornerstoneInvariant(c=100.0, domain="custom")
        ]
        
        for inv in domains:
            props = inv.get_invariant_properties()
            
            # All should have required properties
            assert 'domain' in props
            assert 'invariant_c' in props
            assert 'precision_threshold' in props
            assert 'universality' in props
            assert 'symmetry' in props
            assert 'reproducibility' in props
            
            # Invariant should be positive
            assert props['invariant_c'] > 0
    
    def test_computation_across_all_domains(self):
        """Test that computation works across all domain types."""
        test_cases = [
            (PhysicalInvariant(), 1.0, 1.0e8),
            (DiscreteInvariant(), 100, 0.5),
            (NumberTheoreticInvariant(), 50, 10.0),
            (CornerstoneInvariant(c=10.0), 5.0, 2.0)
        ]
        
        for inv, A, B in test_cases:
            result = inv.compute_z(A=A, B=B, validate_precision=False)
            
            # Should be finite and positive (for positive A and B)
            assert float(result) > 0
            assert float(result) != float('inf')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
