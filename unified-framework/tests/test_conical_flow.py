#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Conical Flow Model
==================================

Comprehensive tests for constant-rate conical evaporation model
and Z5D integration.

Attribution: Dionisio Alberto Lopez III (D.A.L. III)
Issue: zfifteen/unified-framework#631
"""

import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.conical_flow import (
    cone_volume,
    cone_surface,
    cone_time,
    height_at_time,
    cone_flow_invariant,
    validate_constant_rate,
    bootstrap_cone_validation,
    symbolic_complexity_reduction,
    z5d_density_with_cone_flow,
    derive_cone_properties,
)


class TestConeGeometry:
    """Test basic cone geometry calculations."""

    def test_cone_volume_at_full_height(self):
        """Volume at full height should match standard cone formula."""
        R, H = 5.0, 10.0
        V = cone_volume(H, R, H)
        expected = (1.0 / 3.0) * np.pi * R**2 * H
        assert abs(V - expected) < 1e-10

    def test_cone_volume_at_half_height(self):
        """Volume scales cubically with height."""
        R, H = 5.0, 10.0
        V_full = cone_volume(H, R, H)
        V_half = cone_volume(H / 2, R, H)
        # At half height, volume should be 1/8 of full
        assert abs(V_half - V_full / 8) < 1e-10

    def test_cone_volume_zero_height(self):
        """Volume should be zero at zero height."""
        assert cone_volume(0, 5.0, 10.0) == 0.0

    def test_cone_surface_at_full_height(self):
        """Surface area at full height."""
        R, H = 5.0, 10.0
        S = cone_surface(H, R, H)
        expected = np.pi * R**2
        assert abs(S - expected) < 1e-10

    def test_cone_surface_scales_quadratically(self):
        """Surface area scales quadratically with height."""
        R, H = 5.0, 10.0
        S_full = cone_surface(H, R, H)
        S_half = cone_surface(H / 2, R, H)
        # At half height, surface should be 1/4 of full
        assert abs(S_half - S_full / 4) < 1e-10


class TestConeTime:
    """Test the core T = H/k formula."""

    def test_cone_time_basic(self):
        """Basic cone time calculation."""
        H, k = 10.0, 0.1
        T = cone_time(H, k)
        assert abs(T - 100.0) < 1e-10

    def test_cone_time_various_parameters(self):
        """Test various parameter combinations."""
        test_cases = [
            (10.0, 0.1, 100.0),
            (50.0, 0.05, 1000.0),
            (100.0, 0.1, 1000.0),
            (5.0, 0.5, 10.0),
        ]
        for H, k, expected_T in test_cases:
            T = cone_time(H, k)
            assert abs(T - expected_T) < 1e-10

    def test_cone_time_zero_height(self):
        """Zero height should give zero time."""
        assert cone_time(0.0, 0.1) == 0.0

    def test_cone_time_invalid_k(self):
        """Negative or zero k should raise ValueError."""
        with pytest.raises(ValueError):
            cone_time(10.0, 0.0)
        with pytest.raises(ValueError):
            cone_time(10.0, -0.1)

    def test_height_at_time(self):
        """Test height evolution over time."""
        H, k = 10.0, 0.1

        # At t=0, height should be H
        assert abs(height_at_time(0, H, k) - H) < 1e-10

        # At t=50, height should be H/2
        assert abs(height_at_time(50, H, k) - 5.0) < 1e-10

        # At t=T, height should be 0
        T = cone_time(H, k)
        assert abs(height_at_time(T, H, k)) < 1e-10

        # After T, height should remain 0
        assert height_at_time(T + 10, H, k) == 0.0


class TestConstantRate:
    """Test validation of constant dh/dt = -k."""

    def test_validate_constant_rate_basic(self):
        """Basic validation of constant rate."""
        H, k = 10.0, 0.1
        is_valid, max_dev = validate_constant_rate(H, k)
        assert is_valid
        assert max_dev < 1e-10

    def test_validate_constant_rate_various_params(self):
        """Test constant rate for various parameters."""
        test_cases = [
            (10.0, 0.1),
            (50.0, 0.05),
            (100.0, 0.1),
        ]
        for H, k in test_cases:
            is_valid, max_dev = validate_constant_rate(H, k, num_samples=100)
            assert is_valid
            assert max_dev < 1e-9


class TestBootstrapValidation:
    """Test bootstrap validation functionality."""

    def test_bootstrap_validation_accuracy(self):
        """Bootstrap should achieve near-perfect accuracy."""
        accuracy, (ci_low, ci_high) = bootstrap_cone_validation(
            num_iterations=100, seed=42
        )
        # Should be very close to 100% accuracy
        assert accuracy > 0.999
        assert ci_low > 0.999
        assert ci_high > 0.999

    def test_bootstrap_validation_consistency(self):
        """Bootstrap with same seed should give same results."""
        acc1, ci1 = bootstrap_cone_validation(num_iterations=50, seed=42)
        acc2, ci2 = bootstrap_cone_validation(num_iterations=50, seed=42)
        assert abs(acc1 - acc2) < 1e-10
        assert abs(ci1[0] - ci2[0]) < 1e-10
        assert abs(ci1[1] - ci2[1]) < 1e-10


class TestSymbolicReduction:
    """Test symbolic operation reduction."""

    def test_symbolic_reduction_15_percent(self):
        """Should reduce operations by ~15%."""
        base_ops = 10000
        optimized = symbolic_complexity_reduction(base_ops, use_cone_invariant=True)
        reduction_pct = 100 * (1 - optimized / base_ops)

        # Should be exactly 15% for this implementation
        assert abs(reduction_pct - 15.0) < 0.1

    def test_symbolic_reduction_disabled(self):
        """With optimization disabled, should return base ops."""
        base_ops = 10000
        no_opt = symbolic_complexity_reduction(base_ops, use_cone_invariant=False)
        assert no_opt == base_ops

    def test_symbolic_reduction_scales(self):
        """Reduction should scale with input."""
        base_cases = [1000, 10000, 100000]
        for base in base_cases:
            optimized = symbolic_complexity_reduction(base, use_cone_invariant=True)
            expected = int(base * 0.85)
            assert optimized == expected


class TestFlowInvariant:
    """Test flow invariant calculations."""

    def test_flow_invariant_bounded(self):
        """Flow invariant should be in [0, 1]."""
        test_values = [10, 100, 1000, 10000, 100000]
        for n in test_values:
            invariant = cone_flow_invariant(n)
            assert 0 <= invariant <= 1

    def test_flow_invariant_caching(self):
        """Flow invariant should cache results."""
        n = 12345
        # Call twice and ensure consistent
        inv1 = cone_flow_invariant(n)
        inv2 = cone_flow_invariant(n)
        assert inv1 == inv2


class TestZ5DIntegration:
    """Test Z5D integration with conical flow."""

    def test_z5d_density_positive(self):
        """Z5D density should be positive."""
        test_values = [10, 100, 1000, 10000]
        for n in test_values:
            density = z5d_density_with_cone_flow(n)
            assert density > 0

    def test_z5d_density_with_k_parameter(self):
        """Z5D density should respect k parameter."""
        n = 1000
        d1 = z5d_density_with_cone_flow(n, k=0.3)
        d2 = z5d_density_with_cone_flow(n, k=0.5)
        # Different k should give different results
        assert abs(d1 - d2) > 1e-10


class TestDerivation:
    """Test derivation properties."""

    def test_derive_cone_properties(self):
        """Derivation should return all steps."""
        derivation = derive_cone_properties()

        # Check all expected keys exist
        assert "step_1_volume" in derivation
        assert "step_2_surface" in derivation
        assert "step_3_evaporation" in derivation
        assert "step_4_constant_rate" in derivation
        assert "step_5_integration" in derivation
        assert "validation" in derivation

        # Check key formulas
        assert derivation["step_4_constant_rate"]["formula"] == "dh/dt = -k"
        assert derivation["step_5_integration"]["result"] == "T = H / k"
        assert derivation["validation"]["accuracy"] == "100%"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_small_k(self):
        """Very small k should still work."""
        H, k = 10.0, 1e-6
        T = cone_time(H, k)
        assert T > 0
        assert abs(T - H / k) < 1e-10

    def test_very_large_h(self):
        """Very large H should still work."""
        H, k = 1e6, 0.1
        T = cone_time(H, k)
        assert T > 0
        assert abs(T - H / k) < 1e-5


if __name__ == "__main__":
    # Run tests with pytest and propagate exit code
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
