#!/usr/bin/env python3
"""
Test suite for Ulam spiral with Z-Framework integration.

Validates core functionality:
1. Coordinate generation correctness
2. Prime detection accuracy
3. Z-Framework metric calculation
4. Statistical analysis
5. Reproducibility (deterministic output)
"""

import sys
import os

# Add repository root to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

import numpy as np
import sympy

# Import directly from file paths
ulam_framework_path = os.path.join(repo_root, 'gists', 'ulam_spiral', 'ulam_spiral_z_framework.py')
ulam_qmc_path = os.path.join(repo_root, 'gists', 'ulam_spiral', 'ulam_spiral_qmc_analysis.py')

import importlib.util

# Load ulam_z_framework module
spec1 = importlib.util.spec_from_file_location("ulam_z_framework", ulam_framework_path)
ulam_z_framework = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(ulam_z_framework)

# Load ulam_qmc module
spec2 = importlib.util.spec_from_file_location("ulam_qmc", ulam_qmc_path)
ulam_qmc = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(ulam_qmc)


def test_ulam_coordinates():
    """Test Ulam spiral coordinate generation for known positions."""
    ulam_coordinates = ulam_z_framework.ulam_coordinates
    
    print("Testing Ulam coordinate generation...")
    
    # Known positions
    test_cases = [
        (1, (0, 0)),     # Origin
        (2, (1, 0)),     # First step east
        (3, (1, 1)),     # North
        (4, (0, 1)),     # West
        (5, (-1, 1)),    # West again
        (6, (-1, 0)),    # South
        (7, (-1, -1)),   # South again
        (8, (0, -1)),    # East
        (9, (1, -1)),    # East again
    ]
    
    for n, expected in test_cases:
        result = ulam_coordinates(n)
        assert result == expected, f"Failed for n={n}: got {result}, expected {expected}"
    
    print("  ✓ All coordinate tests passed")


def test_prime_detection():
    """Test that known primes are correctly identified."""
    generate_ulam_spiral = ulam_z_framework.generate_ulam_spiral
    
    print("Testing prime detection...")
    
    # Generate small spiral
    spiral = generate_ulam_spiral(size=11, seed=42)
    
    # Check specific known primes
    known_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    numbers = spiral['numbers'].flatten()
    is_prime = spiral['is_prime'].flatten()
    
    for p in known_primes:
        idx = np.where(numbers == p)[0]
        if len(idx) > 0:
            assert is_prime[idx[0]], f"Failed to detect prime {p}"
    
    # Check that 1 is not marked as prime
    idx_1 = np.where(numbers == 1)[0]
    if len(idx_1) > 0:
        assert not is_prime[idx_1[0]], "1 incorrectly marked as prime"
    
    # Check that known composites are not marked as prime
    composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21]
    for c in composites:
        idx = np.where(numbers == c)[0]
        if len(idx) > 0:
            assert not is_prime[idx[0]], f"Composite {c} incorrectly marked as prime"
    
    print("  ✓ Prime detection correct")


def test_z_framework_metrics():
    """Test Z-Framework metric calculations."""
    kappa = ulam_z_framework.kappa
    theta_prime = ulam_z_framework.theta_prime
    z_weight = ulam_z_framework.z_weight
    
    print("Testing Z-Framework metrics...")
    
    # Test κ(n) properties
    k1 = kappa(1)
    k10 = kappa(10)
    k100 = kappa(100)
    k1000 = kappa(1000)
    
    # κ(n) should be positive and generally decreasing (but not monotonic due to d(n))
    assert k1 >= 0, "κ(1) should be non-negative"
    assert k1000 > 0, "κ(1000) should be positive"
    
    # Test θ'(n,k) properties
    t1 = theta_prime(1, k=0.3)
    t100 = theta_prime(100, k=0.3)
    
    # θ'(n,k) should be positive
    assert t1 > 0, "θ'(1, 0.3) should be positive"
    assert t100 > 0, "θ'(100, 0.3) should be positive"
    
    # Test z_weight
    z1 = z_weight(1, k=0.3)
    z100 = z_weight(100, k=0.3)
    
    assert z1 >= 0, "z_weight(1) should be non-negative"  # May be 0 for n=1
    assert z100 > 0, "z_weight(100) should be positive"
    
    print("  ✓ Z-Framework metrics valid")


def test_statistical_analysis():
    """Test statistical analysis functions."""
    generate_ulam_spiral = ulam_z_framework.generate_ulam_spiral
    statistical_analysis = ulam_z_framework.statistical_analysis
    
    print("Testing statistical analysis...")
    
    # Generate spiral
    spiral = generate_ulam_spiral(size=51, seed=42)
    
    # Run analysis
    stats = statistical_analysis(spiral)
    
    # Check that all required keys are present
    required_keys = [
        'total_numbers', 'total_primes', 'observed_density', 'expected_density',
        'density_ratio', 'kappa_correlation', 'theta_correlation', 'z_weight_correlation'
    ]
    
    for key in required_keys:
        assert key in stats, f"Missing key in statistics: {key}"
    
    # Sanity checks
    assert stats['total_numbers'] > 0, "Should have counted some numbers"
    assert stats['total_primes'] > 0, "Should have found some primes"
    assert 0 <= stats['observed_density'] <= 1, "Density should be in [0, 1]"
    assert -1 <= stats['kappa_correlation'] <= 1, "Correlation should be in [-1, 1]"
    
    print("  ✓ Statistical analysis correct")


def test_reproducibility():
    """Test that results are deterministic with fixed seed."""
    generate_ulam_spiral = ulam_z_framework.generate_ulam_spiral
    
    print("Testing reproducibility...")
    
    # Generate spiral twice with same seed
    spiral1 = generate_ulam_spiral(size=51, seed=42)
    spiral2 = generate_ulam_spiral(size=51, seed=42)
    
    # Check that results are identical
    assert np.array_equal(spiral1['numbers'], spiral2['numbers']), "Numbers grid not reproducible"
    assert np.array_equal(spiral1['is_prime'], spiral2['is_prime']), "Prime marking not reproducible"
    assert np.allclose(spiral1['kappa'], spiral2['kappa']), "Kappa values not reproducible"
    assert np.allclose(spiral1['theta_prime'], spiral2['theta_prime']), "Theta values not reproducible"
    
    print("  ✓ Reproducibility verified")


def test_qmc_sampler():
    """Test QMC sampler initialization and basic functionality."""
    UlamSpiralQMC = ulam_qmc.UlamSpiralQMC
    
    print("Testing QMC sampler...")
    
    # Initialize sampler
    sampler = UlamSpiralQMC(max_n=10000, seed=42)
    
    # Test position sampling
    positions = sampler.sample_positions(n_samples=100, bias_mode='uniform')
    
    # Check properties
    assert len(positions) <= 100, "Should return at most requested samples"
    assert np.all(positions >= 1), "All positions should be >= 1"
    assert np.all(positions <= 10000), "All positions should be <= max_n"
    
    # Test analysis
    result = sampler.analyze_sample(n_samples=500, bias_mode='uniform')
    
    # Check that analysis returns expected structure
    required_keys = [
        'n_samples', 'n_primes', 'prime_density',
        'kappa_correlation', 'theta_correlation'
    ]
    
    for key in required_keys:
        assert key in result, f"Missing key in QMC result: {key}"
    
    assert result['n_primes'] >= 0, "Should have non-negative prime count"
    
    print("  ✓ QMC sampler functional")


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("Ulam Spiral Test Suite")
    print("=" * 80)
    print()
    
    tests = [
        test_ulam_coordinates,
        test_prime_detection,
        test_z_framework_metrics,
        test_statistical_analysis,
        test_reproducibility,
        test_qmc_sampler,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
