#!/usr/bin/env python3
"""
Test Suite for Linear Curvature Implementation
==============================================

Tests for the kappa_linear module implementing linearized κ_g ≈ Δθ'/Δs
with fixed-point arithmetic using golden ratio transformations.

Author: Z Framework / Small-Angle Curvature Testing
"""

import pytest
import numpy as np
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.kappa_linear import (
    gen_frac_phi, kappa_linear, kappa_linear_sequence, 
    benchmark_linear_vs_traditional, PHI, ALPHA
)


class TestLinearCurvature:
    """Test suite for linear curvature implementation."""
    
    def test_gen_frac_phi_basic(self):
        """Test basic functionality of gen_frac_phi."""
        # Generate first 10 fractional parts
        frac_values = list(gen_frac_phi(10))
        
        assert len(frac_values) == 10
        
        # All values should be in [0, 1)
        for frac in frac_values:
            assert 0 <= frac < 1, f"Fractional part {frac} out of range [0, 1)"
        
        # Values should be different (non-constant sequence)
        assert len(set(frac_values)) > 1, "Fractional parts should vary"
    
    def test_gen_frac_phi_golden_ratio_properties(self):
        """Test that gen_frac_phi respects golden ratio properties."""
        N = 100
        frac_values = list(gen_frac_phi(N))
        
        # Golden ratio property: {n/φ} should have low discrepancy
        # Check that values are well-distributed in [0, 1)
        hist, _ = np.histogram(frac_values, bins=10, range=(0, 1))
        
        # No bin should be completely empty for reasonable N
        non_empty_bins = np.sum(hist > 0)
        assert non_empty_bins >= 5, f"Only {non_empty_bins} bins have values, distribution too sparse"
    
    def test_gen_frac_phi_fixed_point_accuracy(self):
        """Test fixed-point arithmetic accuracy."""
        # Compare different scale_bits
        N = 50
        frac_32 = list(gen_frac_phi(N, scale_bits=32))
        frac_48 = list(gen_frac_phi(N, scale_bits=48))
        
        # Higher precision should be different (more accurate)
        assert frac_32 != frac_48, "Different scale_bits should produce different results"
        
        # But should be reasonably close
        max_diff = max(abs(a - b) for a, b in zip(frac_32, frac_48))
        assert max_diff < 0.01, f"Scale difference too large: {max_diff}"
    
    def test_kappa_linear_basic(self):
        """Test basic kappa_linear computation."""
        # Simple test case
        n = 5
        u_prev = 0.3
        u_curr = 0.7
        k = 0.3
        ds = 1.0
        
        kappa = kappa_linear(n, u_prev, u_curr, k, ds)
        
        # Should return a finite number
        assert np.isfinite(kappa), f"kappa_linear returned {kappa}"
        
        # Should be positive for this case (u_curr > u_prev)
        assert kappa > 0, f"Expected positive curvature, got {kappa}"
    
    def test_kappa_linear_edge_cases(self):
        """Test edge cases for kappa_linear."""
        # ds = 0 should return 0
        kappa_zero_ds = kappa_linear(1, 0.3, 0.7, 0.3, 0.0)
        assert kappa_zero_ds == 0.0
        
        # k = 0 should return 0 (u^0 - u^0 = 0)
        kappa_zero_k = kappa_linear(1, 0.3, 0.7, 0.0, 1.0)
        assert kappa_zero_k == 0.0
        
        # u_prev = u_curr should return 0
        kappa_equal_u = kappa_linear(1, 0.5, 0.5, 0.3, 1.0)
        assert abs(kappa_equal_u) < 1e-10
    
    def test_kappa_linear_monotonicity(self):
        """Test that kappa_linear behaves reasonably with parameter changes."""
        base_case = kappa_linear(1, 0.3, 0.7, 0.3, 1.0)
        
        # Larger k should generally give different result
        larger_k = kappa_linear(1, 0.3, 0.7, 0.5, 1.0)
        assert larger_k != base_case
        
        # Larger ds should give smaller curvature (inverse relationship)
        larger_ds = kappa_linear(1, 0.3, 0.7, 0.3, 2.0)
        assert abs(larger_ds) < abs(base_case)
    
    def test_kappa_linear_sequence(self):
        """Test kappa_linear_sequence function."""
        N = 20
        kappa_seq = kappa_linear_sequence(N, k=0.3, ds=1.0)
        
        assert len(kappa_seq) == N
        
        # All values should be finite
        assert all(np.isfinite(k) for k in kappa_seq)
        
        # Should have some variation
        assert len(set(kappa_seq)) > 1, "Sequence should have variation"
    
    def test_mathematical_constants(self):
        """Test that mathematical constants are correct."""
        # Golden ratio φ = (1 + √5)/2 ≈ 1.618
        assert abs(float(PHI) - 1.618033988749) < 1e-10
        
        # ALPHA = 1/φ ≈ 0.618
        assert abs(float(ALPHA) - 0.618033988749) < 1e-10
        
        # φ * α = 1 (golden ratio property)
        assert abs(float(PHI * ALPHA) - 1.0) < 1e-10
    
    def test_performance_benchmark(self):
        """Test performance benchmark function."""
        # Small benchmark for testing
        results = benchmark_linear_vs_traditional(N=50, k=0.3)
        
        # Check that all expected keys are present
        expected_keys = ['linear_time', 'traditional_time', 'speedup_factor', 
                        'mse', 'correlation', 'linear_values', 'traditional_values']
        for key in expected_keys:
            assert key in results, f"Missing key {key} in benchmark results"
        
        # Times should be positive
        assert results['linear_time'] > 0
        assert results['traditional_time'] > 0
        assert results['speedup_factor'] > 0
        
        # Values arrays should have correct length
        assert len(results['linear_values']) == 50
        assert len(results['traditional_values']) == 50
        
        # MSE and correlation should be finite
        assert np.isfinite(results['mse'])
        assert np.isfinite(results['correlation'])
    
    def test_integration_with_golden_ratio_properties(self):
        """Test integration with golden ratio mathematical properties."""
        # Generate sequence and check Wythoff/Beatty properties
        N = 100
        frac_values = list(gen_frac_phi(N))
        
        # The sequence should approximate the theoretical {n/φ} values
        theoretical_values = [(n / float(PHI)) % 1 for n in range(1, N+1)]
        
        # Compare with theoretical values (should be close but not identical due to fixed-point)
        max_error = max(abs(a - b) for a, b in zip(frac_values, theoretical_values))
        assert max_error < 0.001, f"Fixed-point approximation error too large: {max_error}"
    
    def test_curvature_sequence_properties(self):
        """Test mathematical properties of the curvature sequence."""
        N = 30
        kappa_seq = kappa_linear_sequence(N, k=0.3, ds=1.0)
        
        # Convert to numpy array for analysis
        kappa_array = np.array(kappa_seq)
        
        # Check statistical properties
        mean_kappa = np.mean(kappa_array)
        std_kappa = np.std(kappa_array)
        
        # Values should have reasonable magnitude
        assert abs(mean_kappa) < 10, f"Mean curvature too large: {mean_kappa}"
        assert std_kappa < 10, f"Curvature variance too large: {std_kappa}"
        
        # Should not all be the same value
        assert std_kappa > 1e-10, "Curvature sequence should have variation"


def test_smoke_test():
    """Smoke test to ensure basic functionality works."""
    # Test that we can import and run basic functions
    frac_gen = gen_frac_phi(5)
    frac_values = list(frac_gen)
    assert len(frac_values) == 5
    
    kappa = kappa_linear(1, 0.2, 0.8, 0.3, 1.0)
    assert np.isfinite(kappa)
    
    print("✓ Linear curvature smoke test passed")


def test_performance_comparison():
    """Quick performance comparison test."""
    results = benchmark_linear_vs_traditional(N=100, k=0.3)
    
    print(f"✓ Performance benchmark completed:")
    print(f"  Linear time: {results['linear_time']:.4f}s")
    print(f"  Traditional time: {results['traditional_time']:.4f}s")
    print(f"  Speedup factor: {results['speedup_factor']:.2f}x")
    print(f"  Correlation: {results['correlation']:.4f}")
    print(f"  MSE: {results['mse']:.6f}")


if __name__ == "__main__":
    # Run smoke tests when executed directly
    test_smoke_test()
    test_performance_comparison()
    print("All manual tests passed!")