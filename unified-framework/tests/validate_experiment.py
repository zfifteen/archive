#!/usr/bin/env python3
"""
Validation Test for Riemann vs Z5D Experiment

This script validates the experimental implementation by checking:
1. Numerical consistency
2. Statistical validity
3. Reproducibility
4. Mathematical correctness
"""

import numpy as np
import json
import os
from riemann_z5d_symmetry_experiment import RiemannZ5DExperiment

def test_basic_functionality():
    """Test basic functionality of the experiment framework."""
    print("Testing basic functionality...")
    
    experiment = RiemannZ5DExperiment(precision_dps=25)  # Lower precision for faster testing
    
    # Test small scale
    results = experiment.run_symmetry_analysis(k_min=100, k_max=1000, num_points=5)
    
    # Validate results structure
    assert 'correlation' in results
    assert 'p_value' in results
    assert len(results['k_values']) == 5
    assert len(results['z5d_predictions']) == 5
    assert len(results['riemann_predictions']) == 5
    
    print("✓ Basic functionality test passed")

def test_mathematical_consistency():
    """Test mathematical consistency of predictions."""
    print("Testing mathematical consistency...")
    
    experiment = RiemannZ5DExperiment(precision_dps=25)
    
    # Test that predictions are monotonically increasing
    k_values = [100, 200, 500, 1000, 2000]
    
    z5d_preds = [experiment.z5d_prime_original(k) for k in k_values]
    riemann_preds = [experiment.riemann_prime_inverse(k, experiment.load_zeta_zeros(max_zeros=10)) for k in k_values]
    
    # Check monotonicity
    assert all(z5d_preds[i] < z5d_preds[i+1] for i in range(len(z5d_preds)-1)), "Z5D predictions not monotonic"
    assert all(riemann_preds[i] < riemann_preds[i+1] for i in range(len(riemann_preds)-1)), "Riemann predictions not monotonic"
    
    # Check reasonable magnitude
    for i, k in enumerate(k_values):
        assert z5d_preds[i] > k, f"Z5D prediction {z5d_preds[i]} should be > k={k}"
        assert riemann_preds[i] > k, f"Riemann prediction {riemann_preds[i]} should be > k={k}"
    
    print("✓ Mathematical consistency test passed")

def test_reproducibility():
    """Test reproducibility of results."""
    print("Testing reproducibility...")
    
    experiment1 = RiemannZ5DExperiment(precision_dps=25)
    experiment2 = RiemannZ5DExperiment(precision_dps=25)
    
    # Run same experiment twice
    results1 = experiment1.run_symmetry_analysis(k_min=100, k_max=1000, num_points=3)
    results2 = experiment2.run_symmetry_analysis(k_min=100, k_max=1000, num_points=3)
    
    # Check predictions are identical
    assert np.allclose(results1['z5d_predictions'], results2['z5d_predictions'], rtol=1e-10)
    assert np.allclose(results1['riemann_predictions'], results2['riemann_predictions'], rtol=1e-10)
    assert abs(results1['correlation'] - results2['correlation']) < 1e-10
    
    print("✓ Reproducibility test passed")

def test_statistical_validity():
    """Test statistical validity of results."""
    print("Testing statistical validity...")
    
    experiment = RiemannZ5DExperiment(precision_dps=25)
    results = experiment.run_symmetry_analysis(k_min=100, k_max=10000, num_points=10)
    
    # Check correlation is within valid range
    assert -1 <= results['correlation'] <= 1, f"Correlation {results['correlation']} outside valid range"
    
    # Check p-value is valid
    assert 0 <= results['p_value'] <= 1, f"P-value {results['p_value']} outside valid range"
    
    # Check for reasonable differences
    differences = np.array(results['differences'])
    assert not np.any(np.isnan(differences)), "NaN values in differences"
    assert not np.any(np.isinf(differences)), "Infinite values in differences"
    
    print("✓ Statistical validity test passed")

def test_hypothesis_claims():
    """Test specific hypothesis claims from the problem statement."""
    print("Testing hypothesis claims...")
    
    experiment = RiemannZ5DExperiment(precision_dps=50)
    results = experiment.run_symmetry_analysis(k_min=1000, k_max=1000000, num_points=20)
    
    # Test correlation hypothesis (r ≥ 0.93, p < 10^-10)
    correlation_supported = results['correlation'] >= 0.93 and results['p_value'] < 1e-10
    print(f"  Correlation hypothesis: {'SUPPORTED' if correlation_supported else 'NOT SUPPORTED'}")
    print(f"    r = {results['correlation']:.6f} (target: ≥ 0.93)")
    print(f"    p = {results['p_value']:.2e} (target: < 10^-10)")
    
    # Test performance claims
    z5d_time = results['mean_z5d_time']
    riemann_time = results['mean_riemann_time']
    print(f"  Performance: Z5D {z5d_time:.3f}ms, Riemann {riemann_time:.3f}ms")
    
    # Test systematic bias
    mean_diff = np.mean(results['differences'])
    print(f"  Systematic bias: {'Z5D overestimates' if mean_diff > 0 else 'Z5D underestimates'} (mean diff: {mean_diff:.2f})")
    
    print("✓ Hypothesis testing completed")

def validate_file_outputs():
    """Validate that all expected files were generated."""
    print("Validating file outputs...")
    
    expected_files = [
        'riemann_z5d_experiment_results.json',
        'riemann_z5d_experiment_report.txt',
        'WHITE_PAPER_RIEMANN_Z5D_SYMMETRY_FALSIFICATION.md',
        'plots/pred_vs_logk.png',
        'plots/diff_vs_logk.png',
        'plots/norm_diff_vs_logk.png',
        'plots/symmetry_analysis_comprehensive.png'
    ]
    
    for filename in expected_files:
        assert os.path.exists(filename), f"Missing expected file: {filename}"
        print(f"  ✓ {filename}")
    
    # Validate JSON file structure
    with open('riemann_z5d_experiment_results.json', 'r') as f:
        data = json.load(f)
        
    required_keys = ['k_values', 'z5d_predictions', 'riemann_predictions', 
                     'correlation', 'p_value', 'statistics']
    for key in required_keys:
        assert key in data, f"Missing key in results: {key}"
    
    print("✓ File validation passed")

def main():
    """Run all validation tests."""
    print("=== RIEMANN vs Z5D EXPERIMENT VALIDATION ===")
    
    try:
        test_basic_functionality()
        test_mathematical_consistency()
        test_reproducibility()
        test_statistical_validity()
        test_hypothesis_claims()
        validate_file_outputs()
        
        print("\n=== ALL VALIDATION TESTS PASSED ===")
        print("The experimental implementation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        raise

if __name__ == "__main__":
    main()