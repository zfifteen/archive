#!/usr/bin/env python3
"""
Test script for cross-linking 5D embeddings to quantum chaos analysis
Validates the implementation and correlation computations
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

from cross_link_5d_quantum_analysis import CrossLink5DQuantumAnalysis
import numpy as np

def test_basic_functionality():
    """Test basic functionality with minimal parameters"""
    print("Testing basic functionality...")
    
    analyzer = CrossLink5DQuantumAnalysis(M=50, N_primes=100, N_seq=100)
    
    # Test individual components
    zeros = analyzer.compute_zeta_zeros_and_spacings()
    assert len(zeros) > 0, "Zero spacings should be computed"
    
    curvatures = analyzer.compute_prime_curvatures_and_shifts()
    assert len(curvatures) > 0, "Prime curvatures should be computed"
    
    embeddings = analyzer.generate_5d_embeddings()
    assert 'x' in embeddings, "5D embeddings should contain x coordinate"
    assert len(embeddings['x']) > 0, "5D embeddings should not be empty"
    
    deviations, ks_stat = analyzer.compute_gue_deviations()
    assert len(deviations) > 0, "GUE deviations should be computed"
    assert 0 <= ks_stat <= 1, "KS statistic should be between 0 and 1"
    
    correlations = analyzer.compute_cross_correlations()
    assert 'reference_correlation' in correlations, "Reference correlation should be computed"
    assert 'gue_vs_5d_curvatures' in correlations, "GUE-5D correlation should be computed"
    
    print("✓ Basic functionality test passed")
    return True

def test_correlation_structure():
    """Test that correlations are properly structured"""
    print("Testing correlation structure...")
    
    analyzer = CrossLink5DQuantumAnalysis(M=30, N_primes=50, N_seq=50)
    
    # Run analysis
    analyzer.compute_zeta_zeros_and_spacings()
    analyzer.compute_prime_curvatures_and_shifts()
    analyzer.generate_5d_embeddings()
    analyzer.compute_gue_deviations()
    correlations = analyzer.compute_cross_correlations()
    
    # Check correlation structure
    for key, result in correlations.items():
        if 'correlation' in result:
            r = result['correlation']
            p = result['p_value']
            assert -1 <= r <= 1, f"Correlation {key} should be between -1 and 1, got {r}"
            assert 0 <= p <= 1, f"P-value for {key} should be between 0 and 1, got {p}"
            assert 'description' in result, f"Result {key} should have description"
    
    print("✓ Correlation structure test passed")
    return True

def test_5d_embedding_coordinates():
    """Test 5D embedding coordinate generation"""
    print("Testing 5D embedding coordinates...")
    
    analyzer = CrossLink5DQuantumAnalysis(M=20, N_primes=30, N_seq=30)
    embeddings = analyzer.generate_5d_embeddings()
    
    # Check all coordinates exist
    required_coords = ['x', 'y', 'z', 'w', 'u']
    for coord in required_coords:
        assert coord in embeddings, f"Missing coordinate {coord}"
        assert len(embeddings[coord]) > 0, f"Empty coordinate {coord}"
    
    # Check coordinate properties
    x, y = embeddings['x'], embeddings['y']
    assert np.all(np.isfinite(x)), "X coordinates should be finite"
    assert np.all(np.isfinite(y)), "Y coordinates should be finite"
    
    # Check that coordinates are in reasonable ranges (helical structure)
    assert np.all(np.abs(x) <= 2), "X coordinates should be bounded"
    assert np.all(np.abs(y) <= 2), "Y coordinates should be bounded"
    
    print("✓ 5D embedding coordinates test passed")
    return True

def test_gue_analysis():
    """Test GUE analysis and deviations"""
    print("Testing GUE analysis...")
    
    analyzer = CrossLink5DQuantumAnalysis(M=40, N_primes=50, N_seq=50)
    analyzer.compute_zeta_zeros_and_spacings()
    deviations, ks_stat = analyzer.compute_gue_deviations()
    
    # Check GUE analysis properties
    assert 0 <= ks_stat <= 1, f"KS statistic should be in [0,1], got {ks_stat}"
    assert len(deviations) > 0, "GUE deviations should not be empty"
    assert np.all(np.isfinite(deviations)), "All GUE deviations should be finite"
    
    # Check that deviations are reasonable
    assert np.abs(np.mean(deviations)) < 1, "Mean deviation should be reasonable"
    assert np.std(deviations) > 0, "Deviations should have non-zero variance"
    
    print("✓ GUE analysis test passed")
    return True

def test_cross_linkage_achievement():
    """Test if cross-linkage is established"""
    print("Testing cross-linkage achievement...")
    
    analyzer = CrossLink5DQuantumAnalysis(M=60, N_primes=200, N_seq=200)
    
    # Run full analysis
    analyzer.compute_zeta_zeros_and_spacings()
    analyzer.compute_prime_curvatures_and_shifts()
    analyzer.generate_5d_embeddings()
    analyzer.compute_gue_deviations()
    analyzer.compute_cross_correlations()
    
    summary = analyzer.generate_summary_report()
    
    # Check that some cross-linkage is established
    gue_corr = summary.get('gue_correlation', 0)
    cascade_corr = summary.get('cascade_correlation', 0)
    
    # At least one strong correlation should exist
    strong_correlation_exists = (abs(gue_corr) > 0.1 or abs(cascade_corr) > 0.1)
    assert strong_correlation_exists, "At least one strong cross-domain correlation should exist"
    
    # Variance ratio should show discrimination
    var_ratio = summary.get('variance_ratio', 1)
    assert var_ratio != 1, "Variance ratio should show prime/composite discrimination"
    
    print("✓ Cross-linkage achievement test passed")
    return True

def run_all_tests():
    """Run all test functions"""
    print("Running Cross-Link 5D Quantum Analysis Tests")
    print("=" * 50)
    
    tests = [
        test_basic_functionality,
        test_correlation_structure,
        test_5d_embedding_coordinates,
        test_gue_analysis,
        test_cross_linkage_achievement
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test_func.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test_func.__name__} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All tests passed successfully!")
    else:
        print("✗ Some tests failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)