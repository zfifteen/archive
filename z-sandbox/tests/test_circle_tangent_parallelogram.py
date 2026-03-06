#!/usr/bin/env python3
"""
Unit tests for Circle-Tangent Parallelogram geometric invariant.

Tests the invariant area property and its integration with Monte Carlo
and Gaussian lattice modules for factorization enhancement.

Run from repository root:
    PYTHONPATH=python python3 tests/test_circle_tangent_parallelogram.py
"""

import sys
sys.path.append("../python")
sys.path.append("python")

import math
from monte_carlo import CircleTangentParallelogramValidator
from gaussian_lattice import TangentBasedLatticeEmbedding


def test_validator_initialization():
    """Test CircleTangentParallelogramValidator initialization."""
    print("\n=== Test: Validator Initialization ===")
    
    validator = CircleTangentParallelogramValidator(
        side_length=5.0,
        target_area=25.0,
        precision_dps=50
    )
    
    print(f"Side length: {float(validator.side_length)}")
    print(f"Target area: {float(validator.target_area)}")
    print(f"Height: {float(validator.height)}")
    print(f"Invariant constant: {float(validator.invariant_constant)}")
    
    # Check derived values
    assert float(validator.side_length) == 5.0, "Side length should be 5.0"
    assert float(validator.target_area) == 25.0, "Target area should be 25.0"
    assert float(validator.height) == 5.0, "Height should be 5.0 (25/5)"
    assert float(validator.invariant_constant) == 25.0, "Invariant should be 25.0"
    
    print("✓ Validator initialization test passed")
    return True


def test_symbolic_area_computation():
    """Test symbolic area computation with sympy."""
    print("\n=== Test: Symbolic Area Computation ===")
    
    validator = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)
    
    try:
        area_symbolic = validator.compute_area_symbolic()
        print(f"Symbolic area: {area_symbolic}")
        
        # Convert to float and check
        if hasattr(area_symbolic, '__float__'):
            area_value = float(area_symbolic)
        else:
            area_value = area_symbolic
        
        print(f"Numeric value: {area_value}")
        assert abs(area_value - 25.0) < 1e-6, f"Symbolic area should be 25.0, got {area_value}"
        print("✓ Symbolic area computation test passed")
    except ImportError:
        print("Note: sympy not available, skipping symbolic test")
    
    return True


def test_scale_invariance():
    """Test that area remains constant across different diameters."""
    print("\n=== Test: Scale Invariance Property ===")
    
    validator = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)
    
    # Test multiple diameters
    test_diameters = [1.0, 5.0, 10.0, 25.0]
    
    results = validator.validate_scale_invariance(
        diameters=test_diameters,
        num_mc_samples=10000,
        seed=42
    )
    
    print(f"Target area: {results['target_area']}")
    print(f"\n{'Diameter':>10} {'Height':>10} {'d×h':>10} {'Area':>12} {'Error':>12}")
    print("-" * 60)
    
    for val in results['validations']:
        print(f"{val['diameter']:>10.2f} {val['height']:>10.4f} {val['d_times_h']:>10.4f} "
              f"{val['area_theory']:>12.6f} {val['area_error']:>12.6e}")
        
        # Check that d*h equals the invariant constant
        assert abs(val['d_times_h'] - results['target_area']) < 1e-6, \
            f"d×h should equal invariant constant: {val['d_times_h']} vs {results['target_area']}"
        
        # Check that area is constant at target_area (within numerical precision)
        assert abs(val['area_theory'] - results['target_area']) < 1e-6, \
            f"Area should be constant: {val['area_theory']} vs {results['target_area']}"
    
    print("\n✓ Scale invariance test passed")
    print("  - Area remains constant at 25.0 across all diameters")
    print("  - d×h = 25.0 (invariant) for all test cases")
    return True


def test_geometric_resonance():
    """Test Z5D geometric resonance factor computation."""
    print("\n=== Test: Geometric Resonance Factor ===")
    
    validator = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)
    
    # Test for known semiprimes
    test_cases = [
        (77, 7, 11),
        (143, 11, 13),
        (221, 13, 17),
    ]
    
    print(f"{'N':>8} {'Factors':>12} {'√N':>8} {'Resonance':>15}")
    print("-" * 50)
    
    for N, p, q in test_cases:
        sqrt_N = int(math.sqrt(N))
        resonance = validator.geometric_resonance_factor(N)
        
        print(f"{N:>8} {f'{p}×{q}':>12} {sqrt_N:>8} {float(resonance):>15.6f}")
        
        # Resonance should be positive
        assert float(resonance) > 0, "Resonance factor must be positive"
    
    print("✓ Geometric resonance test passed")
    return True


def test_tangent_perpendicularity_candidates():
    """Test candidate generation using tangent perpendicularity."""
    print("\n=== Test: Tangent-Perpendicularity Candidate Generation ===")
    
    validator = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)
    
    # Test with small semiprime
    N = 143  # 11 × 13
    candidates = validator.tangent_perpendicularity_candidates(N, num_samples=100, seed=42)
    
    print(f"N = {N} (factors: 11 × 13)")
    print(f"Generated {len(candidates)} candidates")
    print(f"Sample: {candidates[:15]}")
    
    # Check properties
    assert len(candidates) > 0, "Should generate candidates"
    assert all(c > 0 for c in candidates), "All candidates must be positive"
    assert all(c < N for c in candidates), "All candidates must be less than N"
    assert candidates == sorted(set(candidates)), "Candidates should be sorted and unique"
    
    print("✓ Tangent-perpendicularity candidate generation test passed")
    return True


def test_tangent_based_embedding():
    """Test tangent-based lattice embedding."""
    print("\n=== Test: Tangent-Based Lattice Embedding ===")
    
    embedding = TangentBasedLatticeEmbedding(invariant_constant=25.0, precision_dps=50)
    
    # Test enhanced distance
    z1 = 0+0j
    z2 = 5+0j
    
    euclidean = abs(z2 - z1)
    enhanced = embedding.tangent_enhanced_distance(z1, z2, lattice_scale=1.0, tangent_weight=0.5)
    
    print(f"z1: {z1}")
    print(f"z2: {z2}")
    print(f"Euclidean distance: {euclidean:.6f}")
    print(f"Enhanced distance: {float(enhanced):.6f}")
    
    # Enhanced should be >= Euclidean (due to added tangent contribution)
    assert float(enhanced) >= euclidean - 1e-6, "Enhanced distance should be >= Euclidean"
    
    print("✓ Tangent-based embedding test passed")
    return True


def test_candidate_filtering():
    """Test candidate filtering by tangent property."""
    print("\n=== Test: Candidate Filtering by Tangent Property ===")
    
    embedding = TangentBasedLatticeEmbedding(invariant_constant=25.0, precision_dps=50)
    
    N = 143  # 11 × 13
    sqrt_N = int(math.sqrt(N))
    
    # Create candidate list
    candidates = list(range(sqrt_N - 5, sqrt_N + 6))
    
    print(f"N = {N}")
    print(f"Initial candidates: {candidates}")
    
    # Filter
    filtered = embedding.filter_candidates_by_tangent_property(N, candidates, threshold=0.5)
    
    print(f"Filtered candidates: {filtered}")
    print(f"Reduction: {len(candidates)} → {len(filtered)}")
    
    # Check properties
    assert len(filtered) > 0, "Should have some filtered candidates"
    assert len(filtered) <= len(candidates), "Filtered set should not be larger"
    assert all(c in candidates for c in filtered), "Filtered set should be subset of original"
    
    print("✓ Candidate filtering test passed")
    return True


def test_quality_scoring():
    """Test lattice point quality scoring."""
    print("\n=== Test: Lattice Point Quality Scoring ===")
    
    embedding = TangentBasedLatticeEmbedding(invariant_constant=25.0, precision_dps=50)
    
    N = 143
    sqrt_N = int(math.sqrt(N))
    reference = complex(sqrt_N, 0)
    
    # Score candidates
    candidates = [11, 12, 13, 14]
    scores = {}
    
    print(f"Reference point: {reference}")
    print(f"\n{'Candidate':>10} {'Distance':>12} {'Quality':>12}")
    print("-" * 40)
    
    for c in candidates:
        z = complex(c, 0)
        dist = abs(z - reference)
        quality = embedding.lattice_point_quality_score(z, reference)
        scores[c] = float(quality)
        
        marker = " ← factor" if c in [11, 13] else ""
        print(f"{c:>10} {dist:>12.6f} {scores[c]:>12.8f}{marker}")
    
    # All scores should be positive and <= 1
    assert all(0 < s <= 1.0 for s in scores.values()), "Quality scores should be in (0, 1]"
    
    print("✓ Quality scoring test passed")
    return True


def test_reproducibility():
    """Test reproducibility with fixed seed."""
    print("\n=== Test: Reproducibility ===")
    
    seed = 12345
    
    # Test validator
    validator1 = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)
    results1 = validator1.validate_scale_invariance([5.0], num_mc_samples=1000, seed=seed)
    
    validator2 = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)
    results2 = validator2.validate_scale_invariance([5.0], num_mc_samples=1000, seed=seed)
    
    area1 = results1['validations'][0]['area_mc']
    area2 = results2['validations'][0]['area_mc']
    
    print(f"Run 1: area = {area1:.10f}")
    print(f"Run 2: area = {area2:.10f}")
    print(f"Difference: {abs(area1 - area2):.2e}")
    
    # Should be identical with same seed
    assert abs(area1 - area2) < 1e-10, "Results should be reproducible with same seed"
    
    # Test candidates
    candidates1 = validator1.tangent_perpendicularity_candidates(143, num_samples=50, seed=seed)
    candidates2 = validator2.tangent_perpendicularity_candidates(143, num_samples=50, seed=seed)
    
    assert candidates1 == candidates2, "Candidate generation should be reproducible"
    
    print("✓ Reproducibility test passed")
    return True


def test_integration_with_monte_carlo():
    """Test integration with Monte Carlo framework."""
    print("\n=== Test: Integration with Monte Carlo Framework ===")
    
    from monte_carlo import MonteCarloEstimator
    
    # Basic Monte Carlo still works
    estimator = MonteCarloEstimator(seed=42)
    pi_est, _, _ = estimator.estimate_pi(10000)
    
    print(f"Monte Carlo π estimate: {pi_est:.6f}")
    assert abs(pi_est - math.pi) < 0.1, "Monte Carlo should still work"
    
    # Circle-tangent validator works alongside
    validator = CircleTangentParallelogramValidator(side_length=5.0, target_area=25.0)
    results = validator.validate_scale_invariance([5.0], num_mc_samples=1000, seed=42)
    
    area = results['validations'][0]['area_mc']
    print(f"Circle-tangent area: {area:.6f}")
    assert abs(area - 25.0) < 1.0, "Area should be close to 25"
    
    print("✓ Integration test passed")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("Circle-Tangent Parallelogram Test Suite")
    print("=" * 70)
    
    tests = [
        test_validator_initialization,
        test_symbolic_area_computation,
        test_scale_invariance,
        test_geometric_resonance,
        test_tangent_perpendicularity_candidates,
        test_tangent_based_embedding,
        test_candidate_filtering,
        test_quality_scoring,
        test_reproducibility,
        test_integration_with_monte_carlo,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
