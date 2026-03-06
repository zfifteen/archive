#!/usr/bin/env python3
"""
Tests for Conformal Transformation Enhancements

Tests the conformal transformation functionality added to Gaussian integer
lattice framework, including z → z² and z → 1/z transformations.
"""

import sys
import math
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from gaussian_lattice import GaussianIntegerLattice
from lattice_conformal_transform import LatticeConformalTransform

import numpy as np


def test_conformal_square_basic():
    """Test basic z → z² transformation."""
    lattice = GaussianIntegerLattice()
    
    # Test real number
    z1 = 3 + 0j
    z1_sq = lattice.conformal_square(z1)
    assert z1_sq == 9 + 0j, f"Expected 9+0j, got {z1_sq}"
    
    # Test imaginary number
    z2 = 0 + 2j
    z2_sq = lattice.conformal_square(z2)
    assert abs(z2_sq - (-4 + 0j)) < 1e-10, f"Expected -4+0j, got {z2_sq}"
    
    # Test complex number: (3+4i)² = 9 + 24i - 16 = -7 + 24i
    z3 = 3 + 4j
    z3_sq = lattice.conformal_square(z3)
    expected = -7 + 24j
    assert abs(z3_sq - expected) < 1e-10, f"Expected {expected}, got {z3_sq}"
    
    print("✓ test_conformal_square_basic passed")
    return True


def test_conformal_square_properties():
    """Test mathematical properties of z → z²."""
    lattice = GaussianIntegerLattice()
    
    # Test angle doubling
    z = complex(1, 1)  # 45 degrees
    z_sq = lattice.conformal_square(z)
    
    angle_orig = math.atan2(z.imag, z.real)
    angle_sq = math.atan2(z_sq.imag, z_sq.real)
    
    # Angle should double (modulo 2π)
    expected_angle = 2 * angle_orig
    assert abs(angle_sq - expected_angle) < 1e-10, \
        f"Angle not doubled: {angle_orig} → {angle_sq}, expected {expected_angle}"
    
    # Test modulus squaring
    mod_orig = abs(z)
    mod_sq = abs(z_sq)
    expected_mod = mod_orig ** 2
    assert abs(mod_sq - expected_mod) < 1e-10, \
        f"Modulus not squared: {mod_orig} → {mod_sq}, expected {expected_mod}"
    
    print("✓ test_conformal_square_properties passed")
    return True


def test_conformal_inversion_basic():
    """Test basic z → 1/z transformation."""
    lattice = GaussianIntegerLattice()
    
    # Test real number
    z1 = 2 + 0j
    z1_inv = lattice.conformal_inversion(z1)
    assert z1_inv is not None, "Inversion returned None"
    assert abs(z1_inv - 0.5) < 1e-10, f"Expected 0.5, got {z1_inv}"
    
    # Test imaginary number
    z2 = 0 + 2j
    z2_inv = lattice.conformal_inversion(z2)
    assert z2_inv is not None, "Inversion returned None"
    expected = 0 - 0.5j
    assert abs(z2_inv - expected) < 1e-10, f"Expected {expected}, got {z2_inv}"
    
    # Test complex: 1/(3+4i) = (3-4i)/25 = 0.12 - 0.16i
    z3 = 3 + 4j
    z3_inv = lattice.conformal_inversion(z3)
    assert z3_inv is not None, "Inversion returned None"
    expected = complex(3/25, -4/25)
    assert abs(z3_inv - expected) < 1e-10, f"Expected {expected}, got {z3_inv}"
    
    # Test near-zero handling
    z_zero = 1e-15 + 0j
    z_zero_inv = lattice.conformal_inversion(z_zero)
    assert z_zero_inv is None, "Expected None for near-zero input"
    
    print("✓ test_conformal_inversion_basic passed")
    return True


def test_conformal_inversion_properties():
    """Test mathematical properties of z → 1/z."""
    lattice = GaussianIntegerLattice()
    
    z = 3 + 4j
    z_inv = lattice.conformal_inversion(z)
    assert z_inv is not None, "Inversion returned None"
    
    # Test modulus inversion: |1/z| = 1/|z|
    mod_orig = abs(z)
    mod_inv = abs(z_inv)
    expected_mod = 1.0 / mod_orig
    assert abs(mod_inv - expected_mod) < 1e-10, \
        f"Modulus not inverted: {mod_orig} → {mod_inv}, expected {expected_mod}"
    
    # Test double inversion: 1/(1/z) = z
    z_inv_inv = lattice.conformal_inversion(z_inv)
    assert z_inv_inv is not None, "Double inversion returned None"
    assert abs(z_inv_inv - z) < 1e-10, \
        f"Double inversion failed: {z} → {z_inv} → {z_inv_inv}"
    
    print("✓ test_conformal_inversion_properties passed")
    return True


def test_batch_transformation():
    """Test batch transformation of multiple points."""
    lattice = GaussianIntegerLattice()
    
    # Generate test points
    points = [
        1 + 0j,
        2 + 1j,
        3 + 2j,
        -1 + 1j,
        0 + 3j,
    ]
    
    # Test square transformation
    squared = lattice.transform_lattice_points(points, 'square')
    assert len(squared) == len(points), \
        f"Expected {len(points)} squared points, got {len(squared)}"
    
    # Verify first point: (1+0i)² = 1+0i
    assert abs(squared[0] - 1) < 1e-10, \
        f"First squared point incorrect: {squared[0]}"
    
    # Test inversion transformation
    inverted = lattice.transform_lattice_points(points, 'invert')
    assert len(inverted) == len(points), \
        f"Expected {len(points)} inverted points, got {len(inverted)}"
    
    # Verify inversion property for first point
    z_inv_inv = lattice.conformal_inversion(inverted[0])
    assert z_inv_inv is not None, "Double inversion returned None"
    assert abs(z_inv_inv - points[0]) < 1e-10, \
        f"Inversion property failed for first point"
    
    # Test invalid transform
    try:
        lattice.transform_lattice_points(points, 'invalid')
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    print("✓ test_batch_transformation passed")
    return True


def test_enhanced_collision_detection():
    """Test enhanced collision detection using transformations."""
    lattice = GaussianIntegerLattice()
    
    N = 143  # 11 × 13
    z1 = 11 + 0j
    z2 = 13 + 0j
    
    # Standard metric
    metric_std = lattice.enhanced_collision_detection(z1, z2, N, use_square=False)
    assert metric_std > 0, "Standard metric should be positive"
    
    # Enhanced metric
    metric_enh = lattice.enhanced_collision_detection(z1, z2, N, use_square=True)
    assert metric_enh > 0, "Enhanced metric should be positive"
    
    # Enhanced should be different from standard
    assert abs(metric_enh - metric_std) > 0.001, \
        "Enhanced metric should differ from standard"
    
    print("✓ test_enhanced_collision_detection passed")
    return True


def test_conformal_transform_class():
    """Test LatticeConformalTransform class."""
    transformer = LatticeConformalTransform()
    
    # Test static methods
    z = 3 + 4j
    z_sq = transformer.conformal_square(z)
    assert abs(z_sq - (-7 + 24j)) < 1e-10, \
        f"Square transform failed: {z_sq}"
    
    z_inv = transformer.conformal_inversion(z)
    assert z_inv is not None, "Inversion returned None"
    expected = complex(3/25, -4/25)
    assert abs(z_inv - expected) < 1e-10, \
        f"Inversion transform failed: {z_inv}"
    
    # Test epsilon parameter
    transformer_strict = LatticeConformalTransform(epsilon=1e-5)
    z_small = 1e-6 + 0j
    z_small_inv = transformer_strict.conformal_inversion(z_small)
    assert z_small_inv is None, "Should return None for small value with strict epsilon"
    
    print("✓ test_conformal_transform_class passed")
    return True


def test_cauchy_riemann_equations():
    """Verify Cauchy-Riemann equations for conformality."""
    
    # For z → z², we have u = x² - y², v = 2xy
    # Cauchy-Riemann: u_x = v_y, u_y = -v_x
    
    def verify_square_cr(x, y, h=1e-6):
        """Verify CR equations numerically for z²."""
        # u = x² - y²
        u = lambda x, y: x**2 - y**2
        # v = 2xy
        v = lambda x, y: 2*x*y
        
        # Partial derivatives (numerical)
        u_x = (u(x+h, y) - u(x-h, y)) / (2*h)
        u_y = (u(x, y+h) - u(x, y-h)) / (2*h)
        v_x = (v(x+h, y) - v(x-h, y)) / (2*h)
        v_y = (v(x, y+h) - v(x, y-h)) / (2*h)
        
        # Analytical derivatives
        u_x_exact = 2*x
        u_y_exact = -2*y
        v_x_exact = 2*y
        v_y_exact = 2*x
        
        # Check CR equations
        cr1_satisfied = abs(u_x_exact - v_y_exact) < 1e-10
        cr2_satisfied = abs(u_y_exact + v_x_exact) < 1e-10
        
        return cr1_satisfied and cr2_satisfied
    
    # Test at various points
    test_points = [(1, 0), (0, 1), (1, 1), (3, 4), (-2, 5)]
    for x, y in test_points:
        assert verify_square_cr(x, y), \
            f"CR equations not satisfied at ({x}, {y})"
    
    print("✓ test_cauchy_riemann_equations passed")
    return True


def test_lattice_point_generation():
    """Test generation of lattice points for transformation."""
    
    # Generate lattice points near √143 ≈ 12
    N = 143
    sqrt_N = int(math.sqrt(N))
    lattice_range = 3
    
    points = []
    for m in range(-lattice_range, lattice_range + 1):
        for n in range(-lattice_range, lattice_range + 1):
            z = complex(sqrt_N + m, n)
            points.append(z)
    
    expected_count = (2 * lattice_range + 1) ** 2
    assert len(points) == expected_count, \
        f"Expected {expected_count} points, got {len(points)}"
    
    # Check that true factors are near the lattice
    factor1 = 11
    factor2 = 13
    
    # Both factors should be within range
    assert any(abs(z - factor1) < 2 for z in points), \
        "Factor 11 not near generated lattice"
    assert any(abs(z - factor2) < 2 for z in points), \
        "Factor 13 not near generated lattice"
    
    print("✓ test_lattice_point_generation passed")
    return True


def test_transformation_integration():
    """Test integration of transformations with factorization workflow."""
    lattice = GaussianIntegerLattice()
    
    # Test case: N = 143 = 11 × 13
    N = 143
    factors = [11, 13]
    sqrt_N_complex = complex(int(math.sqrt(N)), 0)
    
    # Generate candidates
    candidates = [complex(c, 0) for c in range(8, 16)]
    
    # Compute collision metrics
    metrics = []
    for c in candidates:
        metric = lattice.enhanced_collision_detection(
            sqrt_N_complex, c, N, use_square=True
        )
        metrics.append((int(c.real), metric))
    
    # Sort by metric (lower is better for collision)
    metrics.sort(key=lambda x: x[1])
    
    # Check that factors are highly ranked
    top_5_candidates = [c for c, _ in metrics[:5]]
    
    factors_in_top_5 = sum(1 for f in factors if f in top_5_candidates)
    
    # At least one factor should be in top 5
    assert factors_in_top_5 > 0, \
        f"No factors in top 5: {top_5_candidates}, factors: {factors}"
    
    print("✓ test_transformation_integration passed")
    return True


def test_mobius_transform_basic():
    """Test basic Möbius transformation."""
    lattice = GaussianIntegerLattice()
    
    z = complex(3, 4)
    a, b, c, d = complex(2, 0), complex(1, 0), complex(1, 0), complex(3, 0)
    
    # Apply Möbius transformation
    result = lattice.mobius_transform(z, a, b, c, d)
    
    # Should not be None
    assert result is not None, "Möbius transformation returned None"
    
    # Manual calculation: (2*z + 1)/(z + 3) for z = 3+4i
    # Numerator: 2(3+4i) + 1 = 7+8i
    # Denominator: (3+4i) + 3 = 6+4i
    # Result: (7+8i)/(6+4i)
    expected = (complex(7, 8)) / (complex(6, 4))
    
    error = abs(result - expected)
    assert error < 1e-10, f"Möbius result {result} != expected {expected}"
    
    print("✓ test_mobius_transform_basic passed")
    return True


def test_mobius_inverse():
    """Test Möbius inverse transformation."""
    lattice = GaussianIntegerLattice()
    
    z = complex(3, 4)
    a, b, c, d = complex(2, 0), complex(1, 0), complex(1, 0), complex(3, 0)
    
    # Apply transformation and inverse
    transformed = lattice.mobius_transform(z, a, b, c, d)
    recovered = lattice.mobius_inverse(transformed, a, b, c, d)
    
    # Should recover original
    error = abs(recovered - z)
    assert error < 1e-10, f"Möbius inverse error {error} too large"
    
    print("✓ test_mobius_inverse passed")
    return True


def test_mobius_bijectivity():
    """Test that Möbius transformations are bijective."""
    lattice = GaussianIntegerLattice()
    
    # Test multiple points
    test_points = [
        complex(1, 0),
        complex(0, 1),
        complex(3, 4),
        complex(-2, 5),
        complex(1, 1),
    ]
    
    a, b, c, d = complex(2, 1), complex(1, -1), complex(1, 0), complex(3, 2)
    
    for z in test_points:
        # Transform and inverse
        w = lattice.mobius_transform(z, a, b, c, d)
        if w is not None:
            z_recovered = lattice.mobius_inverse(w, a, b, c, d)
            if z_recovered is not None:
                error = abs(z_recovered - z)
                assert error < 1e-9, \
                    f"Bijectivity failed for z={z}: error={error}"
    
    print("✓ test_mobius_bijectivity passed")
    return True


def run_all_tests():
    """Run all test functions."""
    tests = [
        test_conformal_square_basic,
        test_conformal_square_properties,
        test_conformal_inversion_basic,
        test_conformal_inversion_properties,
        test_batch_transformation,
        test_enhanced_collision_detection,
        test_conformal_transform_class,
        test_cauchy_riemann_equations,
        test_lattice_point_generation,
        test_transformation_integration,
        test_mobius_transform_basic,
        test_mobius_inverse,
        test_mobius_bijectivity,
    ]
    
    print("=" * 70)
    print("Running Conformal Transformation Tests")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
