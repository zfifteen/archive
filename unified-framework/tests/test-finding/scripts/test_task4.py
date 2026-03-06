"""
Test Suite for Task 4: Statistical Discrimination and GMM Fitting
===============================================================

Tests the implementation against requirements and validates functionality.
"""

import numpy as np
import pandas as pd
import json
import os
import sys
import tempfile
import shutil

# Add path for imports
sys.path.append('/home/runner/work/unified-framework/unified-framework')

def test_theta_prime_computation():
    """Test θ' computation functionality"""
    print("Testing θ' computation...")
    
    from task4_statistical_discrimination import compute_theta_prime_values, PHI, K_TARGET
    
    # Test with small dataset
    theta_primes, theta_composites, all_theta, is_prime = compute_theta_prime_values(100, K_TARGET)
    
    # Basic sanity checks
    assert len(theta_primes) > 0, "No primes found"
    assert len(theta_composites) > 0, "No composites found"
    assert len(all_theta) == len(is_prime), "Length mismatch"
    assert len(theta_primes) + len(theta_composites) == len(all_theta), "Count mismatch"
    
    # Check value ranges
    assert np.all(theta_primes >= 0), "Negative θ' values for primes"
    assert np.all(theta_composites >= 0), "Negative θ' values for composites"
    assert np.all(theta_primes < PHI * 10), "θ' values too large for primes"  # Reasonable upper bound
    
    print("✓ θ' computation tests passed")

def test_cohens_d_computation():
    """Test Cohen's d calculation"""
    print("Testing Cohen's d computation...")
    
    from task4_statistical_discrimination import compute_cohens_d
    
    # Test with known data
    # Two well-separated distributions
    group1 = np.random.normal(0, 1, 1000)
    group2 = np.random.normal(3, 1, 1000)  # d should be around 3
    
    cohens_d = compute_cohens_d(group1, group2)
    assert cohens_d > 2.5, f"Cohen's d too small: {cohens_d}"
    assert cohens_d < 3.5, f"Cohen's d too large: {cohens_d}"
    
    # Test with identical distributions
    group3 = np.random.normal(0, 1, 1000)
    group4 = np.random.normal(0, 1, 1000)
    
    cohens_d_small = compute_cohens_d(group3, group4)
    assert cohens_d_small < 0.3, f"Cohen's d should be small: {cohens_d_small}"
    
    print("✓ Cohen's d computation tests passed")

def test_kl_divergence_computation():
    """Test KL divergence calculation"""
    print("Testing KL divergence computation...")
    
    from task4_statistical_discrimination import compute_kl_divergence
    
    # Test with different distributions
    dist1 = np.random.normal(0, 1, 1000)
    dist2 = np.random.normal(2, 1, 1000)
    
    kl_div = compute_kl_divergence(dist1, dist2)
    assert kl_div > 0, f"KL divergence should be positive: {kl_div}"
    assert np.isfinite(kl_div), f"KL divergence should be finite: {kl_div}"
    
    # Test with similar distributions
    dist3 = np.random.normal(0, 1, 1000)
    dist4 = np.random.normal(0.1, 1, 1000)
    
    kl_div_small = compute_kl_divergence(dist3, dist4)
    assert kl_div_small < kl_div, "KL divergence should be smaller for similar distributions"
    
    print("✓ KL divergence computation tests passed")

def test_gmm_fitting():
    """Test GMM fitting functionality"""
    print("Testing GMM fitting...")
    
    from task4_statistical_discrimination import fit_gmm_and_compute_statistics, C_GMM
    
    # Create test data with known structure
    np.random.seed(42)
    data1 = np.random.normal(0.3, 0.1, 500)
    data2 = np.random.normal(0.7, 0.1, 500)
    
    results = fit_gmm_and_compute_statistics(data1, data2)
    
    # Check structure
    assert 'gmm' in results, "Missing GMM object"
    assert 'sigma_bar' in results, "Missing sigma_bar"
    assert 'bic' in results, "Missing BIC"
    assert 'aic' in results, "Missing AIC"
    
    # Check values
    assert results['sigma_bar'] > 0, "sigma_bar should be positive"
    assert np.isfinite(results['bic']), "BIC should be finite"
    assert np.isfinite(results['aic']), "AIC should be finite"
    assert len(results['means']) == C_GMM, f"Should have {C_GMM} means"
    assert len(results['sigmas']) == C_GMM, f"Should have {C_GMM} sigmas"
    assert len(results['weights']) == C_GMM, f"Should have {C_GMM} weights"
    
    # Weights should sum to 1
    assert abs(np.sum(results['weights']) - 1.0) < 1e-6, "Weights should sum to 1"
    
    print("✓ GMM fitting tests passed")

def test_json_output_format():
    """Test JSON output format"""
    print("Testing JSON output format...")
    
    # Create temporary results
    test_results = {
        "k": 0.3,
        "cohens_d": 1.5,
        "KL": 0.5,
        "sigma_bar": 0.12,
        "BIC": 1000.0,
        "AIC": 950.0
    }
    
    # Test JSON serialization
    json_str = json.dumps(test_results)
    parsed_results = json.loads(json_str)
    
    # Check required fields
    required_fields = ["cohens_d", "KL", "sigma_bar"]
    for field in required_fields:
        assert field in parsed_results, f"Missing required field: {field}"
        assert isinstance(parsed_results[field], (int, float)), f"Field {field} should be numeric"
    
    print("✓ JSON output format tests passed")

def test_validation_logic():
    """Test validation against success criteria"""
    print("Testing validation logic...")
    
    from task4_statistical_discrimination import validate_results
    
    # Test valid case
    valid_result = validate_results(1.5, 0.5, 0.12)
    assert valid_result == True, "Should validate as passed"
    
    # Test invalid cases
    invalid_d = validate_results(0.8, 0.5, 0.12)  # Cohen's d too low
    assert invalid_d == False, "Should validate as failed (low Cohen's d)"
    
    invalid_kl = validate_results(1.5, 0.8, 0.12)  # KL too high
    assert invalid_kl == False, "Should validate as failed (high KL)"
    
    invalid_sigma = validate_results(1.5, 0.5, 0.30)  # sigma_bar too high
    assert invalid_sigma == False, "Should validate as failed (high sigma_bar)"
    
    print("✓ Validation logic tests passed")

def test_bootstrap_structure():
    """Test bootstrap sampling structure"""
    print("Testing bootstrap structure...")
    
    from task4_statistical_discrimination import bootstrap_analysis
    
    # Create small test data
    np.random.seed(42)
    test_primes = np.random.normal(0.3, 0.1, 100)
    test_composites = np.random.normal(0.7, 0.1, 100)
    
    # Run with small number of bootstrap iterations
    results = bootstrap_analysis(test_primes, test_composites, n_bootstrap=10)
    
    # Check structure
    assert 'cohens_d_values' in results, "Missing Cohen's d bootstrap values"
    assert 'kl_values' in results, "Missing KL bootstrap values"
    assert 'sigma_bar_values' in results, "Missing sigma_bar bootstrap values"
    assert 'cohens_d_ci' in results, "Missing Cohen's d CI"
    assert 'kl_ci' in results, "Missing KL CI"
    assert 'sigma_bar_ci' in results, "Missing sigma_bar CI"
    
    # Check lengths
    assert len(results['cohens_d_values']) == 10, "Wrong number of bootstrap samples"
    assert len(results['kl_values']) == 10, "Wrong number of bootstrap samples"
    assert len(results['sigma_bar_values']) == 10, "Wrong number of bootstrap samples"
    
    # Check CI structure
    assert len(results['cohens_d_ci']) == 2, "CI should have 2 values"
    assert results['cohens_d_ci'][0] <= results['cohens_d_ci'][1], "CI should be ordered"
    
    print("✓ Bootstrap structure tests passed")

def test_integration():
    """Test full integration with small dataset"""
    print("Testing full integration...")
    
    # Import and modify parameters for quick test
    import task4_statistical_discrimination as task4
    
    # Temporarily modify constants for faster testing
    original_n_max = task4.N_MAX
    original_n_bootstrap = task4.N_BOOTSTRAP
    
    task4.N_MAX = 1000  # Small dataset
    task4.N_BOOTSTRAP = 10  # Few bootstrap iterations
    
    try:
        # Run main analysis
        results, is_valid = task4.main()
        
        # Check results structure
        assert isinstance(results, dict), "Results should be a dictionary"
        assert 'cohens_d' in results, "Missing cohens_d in results"
        assert 'KL' in results, "Missing KL in results"
        assert 'sigma_bar' in results, "Missing sigma_bar in results"
        assert 'BIC' in results, "Missing BIC in results"
        assert 'AIC' in results, "Missing AIC in results"
        
        # Check output files exist
        output_dir = "/home/runner/work/unified-framework/unified-framework/task4_results"
        assert os.path.exists(output_dir), "Output directory not created"
        
        json_path = os.path.join(output_dir, "task4_results.json")
        detailed_path = os.path.join(output_dir, "task4_detailed_results.json")
        
        assert os.path.exists(json_path), "JSON results file not created"
        assert os.path.exists(detailed_path), "Detailed results file not created"
        
        # Load and validate JSON
        with open(json_path, 'r') as f:
            loaded_results = json.load(f)
        
        assert loaded_results['k'] == 0.3, "Wrong k value in JSON"
        assert isinstance(loaded_results['cohens_d'], (int, float)), "cohens_d not numeric"
        assert isinstance(loaded_results['KL'], (int, float)), "KL not numeric"
        assert isinstance(loaded_results['sigma_bar'], (int, float)), "sigma_bar not numeric"
        
        print("✓ Full integration tests passed")
        
    finally:
        # Restore original parameters
        task4.N_MAX = original_n_max
        task4.N_BOOTSTRAP = original_n_bootstrap

def run_all_tests():
    """Run complete test suite"""
    print("="*80)
    print("TASK 4 STATISTICAL DISCRIMINATION - TEST SUITE")
    print("="*80)
    
    try:
        test_theta_prime_computation()
        test_cohens_d_computation()
        test_kl_divergence_computation()
        test_gmm_fitting()
        test_json_output_format()
        test_validation_logic()
        test_bootstrap_structure()
        test_integration()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)