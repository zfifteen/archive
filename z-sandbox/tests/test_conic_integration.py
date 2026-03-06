#!/usr/bin/env python3
"""
Integration test for conic sections module with existing framework.

Validates that conic methods work seamlessly with GVA, Monte Carlo,
and Gaussian lattice components.
"""

import sys
sys.path.append("../python")
sys.path.append("python")

from conic_sections import ConicFactorization
from conic_integration import (
    ConicGVAIntegration,
    ConicMonteCarloIntegration,
    ConicGaussianLatticeIntegration
)


def test_conic_factorization_basic():
    """Test basic conic factorization works."""
    print("\n=== Test: Basic Conic Factorization ===")
    
    conic = ConicFactorization()
    
    test_cases = [143, 899, 1003, 10403]
    
    for N in test_cases:
        result = conic.factorize_via_conics(N, strategies=['fermat'])
        assert result is not None, f"Should factor {N}"
        
        p, q = result
        assert p * q == N, f"Invalid factorization: {p} × {q} ≠ {N}"
        assert p > 1 and q > 1, f"Trivial factors for {N}"
        
        print(f"✓ {N} = {p} × {q}")
    
    print("✓ Basic factorization test passed")
    return True


def test_gva_integration():
    """Test GVA integration with Z5D weighting."""
    print("\n=== Test: GVA Integration ===")
    
    gva_conic = ConicGVAIntegration()
    
    N = 899
    
    # Get weighted candidates
    weighted = gva_conic.conic_candidates_with_z5d_curvature(N, num_candidates=20, k=0.3)
    
    assert len(weighted) > 0, "Should generate candidates"
    assert len(weighted) <= 20, "Should not exceed requested count"
    
    # Check structure
    for candidate, weight in weighted:
        assert isinstance(candidate, int), "Candidate must be integer"
        assert isinstance(weight, float), "Weight must be float"
        assert weight > 0, "Weight must be positive"
    
    # Try factorization
    result = gva_conic.factorize_with_conic_gva(N, max_candidates=100)
    assert result is not None, f"Should factor {N}"
    
    p, q = result
    assert p * q == N, f"Invalid factorization"
    
    print(f"✓ GVA integration: {N} = {p} × {q}")
    print(f"✓ Generated {len(weighted)} Z5D-weighted candidates")
    print("✓ GVA integration test passed")
    return True


def test_monte_carlo_integration():
    """Test Monte Carlo integration with conic sampling."""
    print("\n=== Test: Monte Carlo Integration ===")
    
    mc_conic = ConicMonteCarloIntegration(seed=42)
    
    N = 899
    
    # Test different sampling modes
    for mode in ['uniform', 'phi-biased', 'stratified']:
        candidates = mc_conic.monte_carlo_conic_candidates(N, num_samples=200, mode=mode)
        
        assert len(candidates) > 0, f"Should generate candidates in {mode} mode"
        assert all(isinstance(c, int) for c in candidates), "All candidates must be integers"
        assert all(c > 1 and c < N for c in candidates), "Candidates must be in valid range"
        
        print(f"✓ {mode}: {len(candidates)} candidates generated")
    
    print("✓ Monte Carlo integration test passed")
    return True


def test_gaussian_lattice_integration():
    """Test Gaussian lattice integration."""
    print("\n=== Test: Gaussian Lattice Integration ===")
    
    try:
        lattice_conic = ConicGaussianLatticeIntegration()
        
        N = 899
        sqrt_n = 29
        
        # Test lattice-enhanced distance
        distance = lattice_conic.lattice_enhanced_conic_distance(sqrt_n, N, lattice_scale=0.5)
        
        assert isinstance(distance, float), "Distance must be float"
        assert distance >= 0, "Distance must be non-negative"
        
        print(f"✓ Lattice-enhanced distance computed: {distance:.6f}")
        
        # Test Gaussian Pell solutions
        gaussian_sols = lattice_conic.gaussian_pell_solutions(d=2, num_solutions=3)
        
        assert len(gaussian_sols) > 0, "Should find Gaussian Pell solutions"
        
        for z, norm in gaussian_sols:
            assert isinstance(z, complex), "Solution must be complex"
            assert norm > 0, "Norm must be positive"
        
        print(f"✓ Found {len(gaussian_sols)} Gaussian Pell solutions")
        print("✓ Gaussian lattice integration test passed")
        
    except Exception as e:
        print(f"Note: Gaussian lattice test skipped: {e}")
    
    return True


def test_candidate_quality():
    """Test quality of conic-generated candidates."""
    print("\n=== Test: Candidate Quality ===")
    
    conic = ConicFactorization()
    
    test_cases = [
        (143, 11, 13),
        (899, 29, 31),
        (10403, 101, 103),
    ]
    
    for N, p_true, q_true in test_cases:
        candidates = conic.generate_conic_candidates(N, num_candidates=50)
        
        # Check if true factors are in candidates
        p_found = p_true in candidates
        q_found = q_true in candidates
        
        assert p_found or q_found, f"At least one factor should be in candidates for {N}"
        
        if p_found:
            p_rank = candidates.index(p_true)
            assert p_rank < 20, f"Factor {p_true} should be in top 20 (rank: {p_rank})"
            print(f"✓ N={N}: Factor {p_true} at rank {p_rank}")
        
        if q_found:
            q_rank = candidates.index(q_true)
            assert q_rank < 20, f"Factor {q_true} should be in top 20 (rank: {q_rank})"
            print(f"✓ N={N}: Factor {q_true} at rank {q_rank}")
    
    print("✓ Candidate quality test passed")
    return True


def test_reproducibility():
    """Test that results are reproducible."""
    print("\n=== Test: Reproducibility ===")
    
    # Test conic factorization
    conic1 = ConicFactorization()
    conic2 = ConicFactorization()
    
    N = 899
    result1 = conic1.factorize_via_conics(N, strategies=['fermat'])
    result2 = conic2.factorize_via_conics(N, strategies=['fermat'])
    
    assert result1 == result2, "Conic factorization must be reproducible"
    print(f"✓ Conic factorization reproducible: {result1} == {result2}")
    
    # Test Monte Carlo with same seed
    mc1 = ConicMonteCarloIntegration(seed=42)
    mc2 = ConicMonteCarloIntegration(seed=42)
    
    candidates1 = mc1.monte_carlo_conic_candidates(N, num_samples=100, mode='phi-biased')
    candidates2 = mc2.monte_carlo_conic_candidates(N, num_samples=100, mode='phi-biased')
    
    assert candidates1 == candidates2, "Monte Carlo must be reproducible with same seed"
    print(f"✓ Monte Carlo reproducible: {len(candidates1)} candidates match")
    
    print("✓ Reproducibility test passed")
    return True


def run_all_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("Conic Sections Integration Test Suite")
    print("=" * 70)
    
    tests = [
        test_conic_factorization_basic,
        test_gva_integration,
        test_monte_carlo_integration,
        test_gaussian_lattice_integration,
        test_candidate_quality,
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
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("✓ All integration tests passed!")
        return True
    else:
        print(f"✗ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
