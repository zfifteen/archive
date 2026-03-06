#!/usr/bin/env python3
"""
Tests for Golden Ratio Tangent Circles Module

Validates the implementation of symmetric tangent circles scaled by
powers of the golden ratio φ ≈ 1.618.
"""

import sys
import os
import math
import pytest
import numpy as np

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from golden_ratio_tangent_circles import (
    GoldenRatioTangentCircles,
    TangentChainSampler,
    TangentCircle,
    PHI, PHI_INV, PHI_SQ, PHI_CUBE
)


class TestGoldenRatioConstants:
    """Test golden ratio mathematical constants."""
    
    def test_phi_value(self):
        """Test φ = (1 + √5)/2 ≈ 1.618."""
        expected = (1 + math.sqrt(5)) / 2
        assert abs(PHI - expected) < 1e-15
        assert 1.618 < PHI < 1.619
    
    def test_phi_squared(self):
        """Test φ² = φ + 1 (golden ratio identity)."""
        assert abs(PHI_SQ - (PHI + 1)) < 1e-15
        assert abs(PHI * PHI - PHI_SQ) < 1e-15
    
    def test_phi_inverse(self):
        """Test φ⁻¹ = φ - 1."""
        assert abs(PHI_INV - (PHI - 1)) < 1e-15
        assert abs(1 / PHI - PHI_INV) < 1e-15
    
    def test_phi_cube(self):
        """Test φ³ = φ² + φ."""
        assert abs(PHI_CUBE - (PHI_SQ + PHI)) < 1e-15
        assert abs(PHI ** 3 - PHI_CUBE) < 1e-15


class TestGoldenRatioTangentCircles:
    """Test tangent circles arrangement."""
    
    def test_circle_creation(self):
        """Test that circles are created correctly."""
        arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
        circles = arrangement.compute_circle_positions()
        
        assert len(circles) > 0
        assert all(isinstance(c, TangentCircle) for c in circles)
        assert all(c.radius > 0 for c in circles)
    
    def test_circle_count(self):
        """Test that expected number of circles are created."""
        arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
        circles = arrangement.compute_circle_positions()
        
        # Should have central circles + symmetric sides
        # 2 central (green φ², pink φ) + 4 per side (purple, violet, blue, orange)
        assert len(circles) == 10
    
    def test_circle_radii_powers_of_phi(self):
        """Test that circle radii are powers of φ."""
        arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
        circles = arrangement.compute_circle_positions()
        
        # Check that radii match expected φ powers
        radii = sorted(set(c.radius for c in circles))
        
        # Expected radii: φ⁻⁴, φ⁻², φ⁻¹, 1, φ, φ²
        expected_radii = [
            PHI_INV**4,  # φ⁻⁴
            PHI_INV**2,  # φ⁻²
            PHI_INV,     # φ⁻¹
            1.0,         # φ⁰
            PHI,         # φ
            PHI_SQ,      # φ²
        ]
        
        assert len(radii) == len(expected_radii)
        for r, expected in zip(radii, expected_radii):
            assert abs(r - expected) < 1e-10
    
    def test_baseline_tangency(self):
        """Test that all circles are tangent to baseline."""
        arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
        circles = arrangement.compute_circle_positions()
        
        # Each circle should have y_center = baseline_y + radius
        for circle in circles:
            expected_y = arrangement.baseline_y + circle.radius
            assert abs(circle.y - expected_y) < 1e-10
    
    def test_symmetry(self):
        """Test that arrangement is symmetric around center."""
        arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
        circles = arrangement.compute_circle_positions()
        
        # Find circles on left and right (excluding center)
        left_circles = [c for c in circles if c.x < -0.1]
        right_circles = [c for c in circles if c.x > 0.1]
        
        # Should have equal number on each side
        assert len(left_circles) == len(right_circles)
        
        # Radii should match (sorted)
        left_radii = sorted([c.radius for c in left_circles])
        right_radii = sorted([c.radius for c in right_circles])
        
        for lr, rr in zip(left_radii, right_radii):
            assert abs(lr - rr) < 1e-10
    
    def test_arc_computation(self):
        """Test overarching arc computation."""
        arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
        arrangement.compute_circle_positions()
        arc = arrangement.compute_overarching_arc()
        
        assert arc is not None
        assert arc['radius'] == PHI_CUBE
        assert arc['color'] == 'red'
        assert arc['label'] == 'φ³'
    
    def test_circle_data_export(self):
        """Test circle data export functionality."""
        arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
        circle_data = arrangement.get_circle_data()
        
        assert len(circle_data) > 0
        assert all('x' in c for c in circle_data)
        assert all('y' in c for c in circle_data)
        assert all('radius' in c for c in circle_data)
        assert all('area' in c for c in circle_data)
        assert all('power' in c for c in circle_data)


class TestTangentChainSampler:
    """Test tangent chain sampler for low-discrepancy sequences."""
    
    def test_sampler_creation(self):
        """Test that sampler is created correctly."""
        sampler = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
        assert sampler.base_radius == 1.0
        assert sampler.num_scales == 5
        assert sampler.seed == 42
    
    def test_hierarchical_samples_1d(self):
        """Test 1D hierarchical sampling."""
        sampler = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
        samples = sampler.generate_hierarchical_samples(100, dimension=1)
        
        assert samples.shape == (100, 1)
        assert np.all(np.isfinite(samples))
    
    def test_hierarchical_samples_2d(self):
        """Test 2D hierarchical sampling."""
        sampler = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
        samples = sampler.generate_hierarchical_samples(100, dimension=2)
        
        assert samples.shape == (100, 2)
        assert np.all(np.isfinite(samples))
    
    def test_sample_distribution(self):
        """Test that samples are distributed across scales."""
        sampler = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
        samples = sampler.generate_hierarchical_samples(1000, dimension=2)
        
        # Compute radial distribution
        radii = np.sqrt(samples[:, 0]**2 + samples[:, 1]**2)
        
        # Should have samples at multiple scales
        assert np.min(radii) < 1.0  # Smaller than base
        assert np.max(radii) > 1.0  # Larger than base
        
        # Mean should be around base radius
        assert 0.5 < np.mean(radii) < 2.0
    
    def test_annulus_sampling(self):
        """Test annulus sampling."""
        sampler = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
        r_inner, r_outer = 1.0, 2.0
        samples = sampler.generate_annulus_samples(100, r_inner, r_outer)
        
        assert samples.shape == (100, 2)
        
        # All samples should be within annulus
        radii = np.sqrt(samples[:, 0]**2 + samples[:, 1]**2)
        assert np.all(radii >= r_inner * 0.99)  # Allow small tolerance
        assert np.all(radii <= r_outer * 1.01)
    
    def test_reproducibility(self):
        """Test that seeded sampler produces reproducible results."""
        sampler1 = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
        sampler2 = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
        
        samples1 = sampler1.generate_hierarchical_samples(50, dimension=2)
        samples2 = sampler2.generate_hierarchical_samples(50, dimension=2)
        
        assert np.allclose(samples1, samples2)


class TestIntegrationWithLowDiscrepancy:
    """Test integration with low_discrepancy module."""
    
    def test_tangent_chain_sampler_import(self):
        """Test that TangentChainSampler can be imported in low_discrepancy."""
        from low_discrepancy import SamplerType, LowDiscrepancySampler
        
        # Check that TANGENT_CHAIN type exists
        assert hasattr(SamplerType, 'TANGENT_CHAIN')
    
    def test_tangent_chain_generation(self):
        """Test tangent chain sampling through LowDiscrepancySampler."""
        from low_discrepancy import SamplerType, LowDiscrepancySampler
        
        sampler = LowDiscrepancySampler(SamplerType.TANGENT_CHAIN, dimension=2, seed=42)
        samples = sampler.generate(100)
        
        assert samples.shape == (100, 2)
        assert np.all(np.isfinite(samples))
        
        # Should be in [0, 1]² after normalization
        assert np.all(samples >= 0)
        assert np.all(samples <= 1)


class TestMathematicalProperties:
    """Test mathematical properties of golden ratio arrangement."""
    
    def test_fibonacci_approximation(self):
        """Test Binet's formula for Fibonacci numbers using φ."""
        # Binet's formula: F_n = (φⁿ - ψⁿ) / √5, where ψ = (1-√5)/2 = -1/φ
        fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        
        psi = (1 - math.sqrt(5)) / 2  # ψ = -1/φ
        sqrt5 = math.sqrt(5)
        
        for n in range(1, 11):
            # Binet's formula (exact)
            fib_n = round((PHI ** n - psi ** n) / sqrt5)
            assert fib_n == fib[n], f"F_{n} mismatch: {fib_n} != {fib[n]}"
    
    def test_self_similarity(self):
        """Test self-similarity under φ-scaling."""
        arrangement1 = GoldenRatioTangentCircles(baseline_y=0.0)
        circles1 = arrangement1.compute_circle_positions()
        
        arrangement2 = GoldenRatioTangentCircles(baseline_y=0.0)
        circles2 = arrangement2.compute_circle_positions()
        
        # Scale second arrangement by φ
        for circle in circles2:
            circle.x *= PHI
            circle.y *= PHI
            circle.radius *= PHI
        
        # Radii ratios should be preserved
        radii1 = sorted([c.radius for c in circles1])
        radii2 = sorted([c.radius for c in circles2])
        
        for i in range(1, len(radii1)):
            ratio1 = radii1[i] / radii1[i-1]
            ratio2 = radii2[i] / radii2[i-1]
            assert abs(ratio1 - ratio2) < 1e-10


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
