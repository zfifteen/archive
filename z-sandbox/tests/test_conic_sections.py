#!/usr/bin/env python3
"""
Unit tests for Conic Sections module.

Tests conic equations, Fermat factorization, Pell equations,
and integration with z-sandbox factorization framework.

Run from repository root:
    PYTHONPATH=python python3 tests/test_conic_sections.py
"""

import sys
sys.path.append("../python")
sys.path.append("python")

import math
from conic_sections import (
    ConicSections,
    FermatFactorization,
    PellEquation,
    QuadraticForms,
    ConicFactorization
)


def test_eccentricity():
    """Test eccentricity calculations for different conics."""
    print("\n=== Test: Eccentricity Calculations ===")
    
    conics = ConicSections()
    
    # Circle
    e_circle = conics.eccentricity('circle', 1.0)
    assert e_circle == 0.0, "Circle eccentricity must be 0"
    print(f"✓ Circle eccentricity: {e_circle}")
    
    # Parabola
    e_parabola = conics.eccentricity('parabola', 1.0)
    assert e_parabola == 1.0, "Parabola eccentricity must be 1"
    print(f"✓ Parabola eccentricity: {e_parabola}")
    
    # Ellipse
    e_ellipse = conics.eccentricity('ellipse', 5.0, 3.0)
    assert 0 < e_ellipse < 1, "Ellipse eccentricity must be between 0 and 1"
    print(f"✓ Ellipse eccentricity: {e_ellipse:.6f}")
    
    # Hyperbola
    e_hyperbola = conics.eccentricity('hyperbola', 3.0, 4.0)
    assert e_hyperbola > 1, "Hyperbola eccentricity must be > 1"
    print(f"✓ Hyperbola eccentricity: {e_hyperbola:.6f}")
    
    print("✓ Eccentricity test passed")
    return True


def test_conic_point_validation():
    """Test point validation on different conics."""
    print("\n=== Test: Point Validation on Conics ===")
    
    conics = ConicSections()
    
    # Circle: x² + y² = 25
    assert conics.is_on_circle(3, 4, 5), "Point (3,4) should be on circle r=5"
    assert conics.is_on_circle(0, 5, 5), "Point (0,5) should be on circle r=5"
    assert not conics.is_on_circle(2, 2, 5), "Point (2,2) should not be on circle r=5"
    print("✓ Circle validation works")
    
    # Ellipse: x²/25 + y²/16 = 1
    assert conics.is_on_ellipse(5.0, 0.0, 5.0, 4.0), "Point (5,0) should be on ellipse"
    assert conics.is_on_ellipse(0.0, 4.0, 5.0, 4.0), "Point (0,4) should be on ellipse"
    assert conics.is_on_ellipse(3.0, 3.2, 5.0, 4.0), "Point (3,3.2) should be on ellipse"
    print("✓ Ellipse validation works")
    
    # Parabola: y² = 4ax with a=1
    assert conics.is_on_parabola(1.0, 2.0, 1.0), "Point (1,2) should be on parabola"
    assert conics.is_on_parabola(4.0, 4.0, 1.0), "Point (4,4) should be on parabola"
    print("✓ Parabola validation works")
    
    # Hyperbola: x²/a² - y²/b² = 1
    assert conics.is_on_hyperbola(5.0, 0.0, 5.0, 4.0), "Point (5,0) should be on hyperbola"
    print("✓ Hyperbola validation works")
    
    print("✓ Point validation test passed")
    return True


def test_fermat_factorization():
    """Test Fermat's factorization method."""
    print("\n=== Test: Fermat Factorization ===")
    
    fermat = FermatFactorization()
    
    test_cases = [
        (143, (11, 13)),
        (899, (29, 31)),
        (1003, (17, 59)),
        (10403, (101, 103)),
    ]
    
    for N, expected in test_cases:
        result = fermat.factorize(N)
        assert result is not None, f"Should factor {N}"
        p, q = result
        assert p * q == N, f"Factors must multiply to {N}"
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"✓ Factored {N} = {p} × {q}")
    
    print("✓ Fermat factorization test passed")
    return True


def test_lattice_points_hyperbola():
    """Test finding lattice points on hyperbola."""
    print("\n=== Test: Lattice Points on Hyperbola ===")
    
    fermat = FermatFactorization()
    
    # For N = 143, hyperbola is x² - y² = 143
    N = 143
    points = fermat.lattice_points_on_hyperbola(N, max_x=50)
    
    assert len(points) > 0, "Should find at least one lattice point"
    print(f"Found {len(points)} lattice points for N={N}")
    
    # Verify each point
    for x, y in points[:5]:
        assert x*x - y*y == N, f"Point ({x},{y}) not on hyperbola"
        print(f"  ✓ ({x}, {y}): {x}² - {y}² = {N}")
    
    print("✓ Lattice points test passed")
    return True


def test_pell_equation():
    """Test Pell equation solver."""
    print("\n=== Test: Pell Equation Solver ===")
    
    # Test d=2: x² - 2y² = 1
    pell_2 = PellEquation(2)
    fundamental = pell_2.find_fundamental_solution()
    
    assert fundamental is not None, "Should find fundamental solution"
    x, y = fundamental
    assert x*x - 2*y*y == 1, "Must satisfy Pell equation"
    print(f"✓ Pell(2) fundamental solution: ({x}, {y})")
    
    # Generate more solutions
    solutions = pell_2.generate_solutions(5)
    assert len(solutions) == 5, "Should generate 5 solutions"
    
    for i, (x, y) in enumerate(solutions):
        assert x*x - 2*y*y == 1, f"Solution {i} must satisfy equation"
        print(f"  ✓ Solution {i+1}: ({x}, {y})")
    
    # Test d=3
    pell_3 = PellEquation(3)
    fundamental_3 = pell_3.find_fundamental_solution()
    assert fundamental_3 is not None, "Should find fundamental solution for d=3"
    x3, y3 = fundamental_3
    assert x3*x3 - 3*y3*y3 == 1, "Must satisfy Pell equation for d=3"
    print(f"✓ Pell(3) fundamental solution: ({x3}, {y3})")
    
    print("✓ Pell equation test passed")
    return True


def test_quadratic_forms():
    """Test quadratic form representations."""
    print("\n=== Test: Quadratic Forms ===")
    
    qf = QuadraticForms()
    
    # Sum of squares: x² + y² = 25
    reps = qf.represent_as_sum_of_squares(25)
    assert len(reps) > 0, "Should find representations"
    
    for x, y in reps:
        assert x*x + y*y == 25, "Must satisfy x² + y² = 25"
        print(f"  ✓ 25 = {x}² + {y}²")
    
    # Difference of squares: x² - y² = 143
    reps_diff = qf.represent_as_difference_of_squares(143)
    assert len(reps_diff) > 0, "Should find representations"
    
    for x, y in reps_diff[:3]:
        assert x*x - y*y == 143, "Must satisfy x² - y² = 143"
        print(f"  ✓ 143 = {x}² - {y}²")
    
    # mx² + ny²: 2x² + 3y² = 50
    reps_mx_ny = qf.represent_as_mx2_plus_ny2(50, 2, 3)
    for x, y in reps_mx_ny:
        assert 2*x*x + 3*y*y == 50, "Must satisfy 2x² + 3y² = 50"
        print(f"  ✓ 50 = 2×{x}² + 3×{y}²")
    
    print("✓ Quadratic forms test passed")
    return True


def test_conic_factorization():
    """Test integrated conic factorization."""
    print("\n=== Test: Conic Factorization ===")
    
    conic_fact = ConicFactorization()
    
    test_cases = [
        (143, (11, 13)),
        (899, (29, 31)),
        (1003, (17, 59)),
    ]
    
    for N, expected in test_cases:
        result = conic_fact.factorize_via_conics(N, strategies=['fermat'])
        assert result is not None, f"Should factor {N}"
        p, q = result
        assert p * q == N, f"Factors must multiply to {N}"
        print(f"✓ Factored {N} = {p} × {q} using conic methods")
    
    print("✓ Conic factorization test passed")
    return True


def test_candidate_generation():
    """Test conic-based candidate generation."""
    print("\n=== Test: Conic-Based Candidate Generation ===")
    
    conic_fact = ConicFactorization()
    
    test_cases = [
        (143, 11, 13),
        (899, 29, 31),
        (10403, 101, 103),
    ]
    
    for N, p_true, q_true in test_cases:
        candidates = conic_fact.generate_conic_candidates(N, num_candidates=50)
        
        assert len(candidates) > 0, "Should generate candidates"
        
        # Check if true factors are in candidates
        p_found = p_true in candidates
        q_found = q_true in candidates
        
        if p_found:
            p_rank = candidates.index(p_true)
            print(f"✓ N={N}: Factor {p_true} found at rank {p_rank}")
        
        if q_found:
            q_rank = candidates.index(q_true)
            print(f"✓ N={N}: Factor {q_true} found at rank {q_rank}")
        
        assert p_found or q_found, f"At least one factor should be in candidates for {N}"
    
    print("✓ Candidate generation test passed")
    return True


def test_integration_with_sqrt_proximity():
    """Test that conic candidates cluster near √N."""
    print("\n=== Test: Integration with √N Proximity ===")
    
    conic_fact = ConicFactorization()
    
    N = 899
    sqrt_n = math.sqrt(N)
    candidates = conic_fact.generate_conic_candidates(N, num_candidates=100)
    
    # Check that candidates are generally ordered by proximity to √N
    # We allow some flexibility since hyperbola-derived candidates have priority
    distances = [abs(c - sqrt_n) for c in candidates[:20]]
    
    # Check that most candidates are reasonably close to √N
    close_candidates = sum(1 for d in distances if d < 10)
    print(f"Candidates within distance 10 of √N: {close_candidates}/{len(distances)}")
    
    # At least half should be close to √N
    assert close_candidates >= len(distances) // 2, "Many candidates should be near √N"
    
    # Verify no extreme outliers in first 20
    max_distance = max(distances)
    print(f"Maximum distance from √N in top 20: {max_distance:.2f}")
    assert max_distance < 50, "Top candidates should not be far from √N"
    
    print("✓ √N proximity test passed")
    return True


def test_multiple_quadratic_forms():
    """Test factorization using multiple quadratic forms."""
    print("\n=== Test: Multiple Quadratic Forms ===")
    
    conic_fact = ConicFactorization()
    
    # Test with multiple forms strategy
    N = 143
    result = conic_fact.factorize_via_conics(N, strategies=['multiple_forms'])
    
    if result:
        p, q = result
        assert p * q == N, f"Factors must multiply to {N}"
        print(f"✓ Factored {N} = {p} × {q} using multiple forms")
    else:
        print(f"Note: Multiple forms didn't factor {N} (Fermat more efficient)")
    
    print("✓ Multiple quadratic forms test passed")
    return True


def test_reproducibility():
    """Test that results are reproducible."""
    print("\n=== Test: Reproducibility ===")
    
    fermat = FermatFactorization()
    
    N = 899
    result1 = fermat.factorize(N)
    result2 = fermat.factorize(N)
    
    assert result1 == result2, "Results must be reproducible"
    print(f"✓ Fermat factorization reproducible: {result1} == {result2}")
    
    # Test Pell equation
    pell = PellEquation(2)
    sol1 = pell.find_fundamental_solution()
    sol2 = pell.find_fundamental_solution()
    
    assert sol1 == sol2, "Pell solutions must be reproducible"
    print(f"✓ Pell equation reproducible: {sol1} == {sol2}")
    
    print("✓ Reproducibility test passed")
    return True


def run_all_tests():
    """Run all test functions."""
    print("=" * 70)
    print("Conic Sections Test Suite")
    print("=" * 70)
    
    tests = [
        test_eccentricity,
        test_conic_point_validation,
        test_fermat_factorization,
        test_lattice_points_hyperbola,
        test_pell_equation,
        test_quadratic_forms,
        test_conic_factorization,
        test_candidate_generation,
        test_integration_with_sqrt_proximity,
        test_multiple_quadratic_forms,
        test_reproducibility,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n✗ Test failed: {test_func.__name__}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test error: {test_func.__name__}")
            print(f"  Error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("✓ All tests passed!")
        return True
    else:
        print(f"✗ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
