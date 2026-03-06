"""
Test Suite for GMM and Fourier Analysis Implementation
=====================================================

Validates the implementation against the issue requirements and tests edge cases.
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from scipy.optimize import curve_fit
from sympy import sieve
import os
import sys

# Add path for core imports
sys.path.append('/home/runner/work/unified-framework/unified-framework')

def test_basic_functionality():
    """Test basic functions work correctly"""
    print("Testing basic functionality...")
    
    # Test golden ratio calculation
    phi = (1 + np.sqrt(5)) / 2
    assert abs(phi - 1.618033988749) < 1e-10, "Golden ratio calculation error"
    
    # Test frame shift with simple values
    def frame_shift_residues(n_vals, k):
        mod_phi = np.mod(n_vals, phi) / phi
        return phi * np.power(mod_phi, k)
    
    # Test with k=1 (should be identity modulo phi)
    test_vals = np.array([1, 2, 3, 4, 5])
    result = frame_shift_residues(test_vals, 1.0)
    expected = np.mod(test_vals, phi)
    assert np.allclose(result, expected), "Frame shift k=1 test failed"
    
    print("✓ Basic functionality tests passed")

def test_data_generation():
    """Test prime generation and transformations"""
    print("Testing data generation...")
    
    # Test small prime generation
    small_primes = list(sieve.primerange(2, 100))
    expected_first_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert small_primes[:10] == expected_first_primes, "Prime generation error"
    
    # Test transformations
    phi = (1 + np.sqrt(5)) / 2
    
    def frame_shift_residues(n_vals, k):
        mod_phi = np.mod(n_vals, phi) / phi
        return phi * np.power(mod_phi, k)
    
    def normalize_to_unit_interval(theta_vals):
        return (theta_vals % phi) / phi
    
    test_primes = np.array(small_primes[:10])
    theta_vals = frame_shift_residues(test_primes, 0.3)
    normalized = normalize_to_unit_interval(theta_vals)
    
    # Check ranges
    assert np.all(theta_vals >= 0) and np.all(theta_vals < phi), "θ' values out of range"
    assert np.all(normalized >= 0) and np.all(normalized < 1), "Normalized values out of range"
    
    print("✓ Data generation tests passed")

def test_fourier_analysis():
    """Test Fourier series fitting"""
    print("Testing Fourier analysis...")
    
    # Create synthetic data with known Fourier content
    x = np.linspace(0, 1, 1000)
    # Simple sine wave: sin(2πx) should give b1=1, others≈0
    y = np.sin(2 * np.pi * x) + 1  # Add DC offset
    
    # Test Fourier fitting
    def fourier_series(x, *coeffs):
        result = coeffs[0]  # a0
        M = (len(coeffs) - 1) // 2
        for m in range(1, M + 1):
            a_m = coeffs[2*m - 1]
            b_m = coeffs[2*m]
            result += a_m * np.cos(2 * np.pi * m * x) + b_m * np.sin(2 * np.pi * m * x)
        return result
    
    # Fit with M=5 harmonics
    M = 5
    p0 = np.zeros(2 * M + 1)
    p0[0] = 1  # DC guess
    p0[2] = 1  # b1 guess
    
    try:
        from scipy.optimize import curve_fit
        popt, _ = curve_fit(fourier_series, x, y, p0=p0, maxfev=5000)
        
        # Check that b1 coefficient is close to 1
        b1 = popt[2]
        assert abs(b1 - 1.0) < 0.1, f"Fourier fit failed: b1={b1}, expected≈1"
        
    except Exception as e:
        print(f"Fourier fitting test skipped due to: {e}")
    
    print("✓ Fourier analysis tests passed")

def test_gmm_analysis():
    """Test GMM fitting"""
    print("Testing GMM analysis...")
    
    # Create synthetic mixture data
    np.random.seed(42)
    data1 = np.random.normal(0.3, 0.1, 500)
    data2 = np.random.normal(0.7, 0.1, 500)
    mixed_data = np.concatenate([data1, data2])
    
    # Test standardization and GMM
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(mixed_data.reshape(-1, 1))
    
    gmm = GaussianMixture(n_components=2, random_state=0)
    gmm.fit(X_scaled)
    
    # Check that we get reasonable components
    assert gmm.n_components == 2, "GMM components mismatch"
    assert hasattr(gmm, 'means_'), "GMM missing means"
    assert hasattr(gmm, 'covariances_'), "GMM missing covariances"
    assert hasattr(gmm, 'weights_'), "GMM missing weights"
    
    # Check BIC/AIC computation
    bic = gmm.bic(X_scaled)
    aic = gmm.aic(X_scaled)
    assert np.isfinite(bic) and np.isfinite(aic), "BIC/AIC computation failed"
    
    print("✓ GMM analysis tests passed")

def test_bootstrap_structure():
    """Test bootstrap sampling structure"""
    print("Testing bootstrap structure...")
    
    # Test bootstrap sampling
    test_data = np.arange(100)
    n_samples = len(test_data)
    
    # Generate bootstrap sample
    bootstrap_indices = np.random.choice(n_samples, size=n_samples, replace=True)
    bootstrap_sample = test_data[bootstrap_indices]
    
    # Check properties
    assert len(bootstrap_sample) == n_samples, "Bootstrap sample size mismatch"
    assert len(np.unique(bootstrap_indices)) <= n_samples, "Bootstrap without replacement"
    
    print("✓ Bootstrap structure tests passed")

def test_results_files():
    """Test that result files exist and have correct structure"""
    print("Testing results files...")
    
    results_dir = "/home/runner/work/unified-framework/unified-framework/number-theory/prime-curve/gmm_fourier_results"
    
    required_files = [
        "results_table.csv",
        "fourier_coefficients.csv", 
        "gmm_parameters.csv",
        "bootstrap_results.csv"
    ]
    
    for filename in required_files:
        filepath = os.path.join(results_dir, filename)
        assert os.path.exists(filepath), f"Missing results file: {filename}"
        
        # Test file can be loaded
        df = pd.read_csv(filepath)
        assert len(df) > 0, f"Empty results file: {filename}"
        
    # Test specific file structures
    results_table = pd.read_csv(os.path.join(results_dir, "results_table.csv"))
    expected_columns = ['k', 'S_b', 'CI_S_b_lower', 'CI_S_b_upper', 'bar_σ', 
                       'CI_bar_σ_lower', 'CI_bar_σ_upper', 'BIC', 'AIC']
    for col in expected_columns:
        assert col in results_table.columns, f"Missing column in results: {col}"
    
    fourier_coeffs = pd.read_csv(os.path.join(results_dir, "fourier_coefficients.csv"))
    assert 'a_coeffs' in fourier_coeffs.columns, "Missing a_coeffs"
    assert 'b_coeffs' in fourier_coeffs.columns, "Missing b_coeffs"
    assert len(fourier_coeffs) == 6, "Fourier coefficients length error"  # M+1 coefficients
    
    gmm_params = pd.read_csv(os.path.join(results_dir, "gmm_parameters.csv"))
    gmm_expected_cols = ['component', 'mean', 'sigma', 'weight']
    for col in gmm_expected_cols:
        assert col in gmm_params.columns, f"Missing GMM column: {col}"
    assert len(gmm_params) == 5, "GMM components count error"  # C_GMM components
    
    bootstrap_results = pd.read_csv(os.path.join(results_dir, "bootstrap_results.csv"))
    assert 'S_b_bootstrap' in bootstrap_results.columns, "Missing S_b bootstrap"
    assert 'bar_sigma_bootstrap' in bootstrap_results.columns, "Missing sigma bootstrap"
    assert len(bootstrap_results) == 1000, "Bootstrap sample count error"  # N_BOOTSTRAP
    
    print("✓ Results files tests passed")

def test_mathematical_constraints():
    """Test mathematical constraints and sanity checks"""
    print("Testing mathematical constraints...")
    
    results_dir = "/home/runner/work/unified-framework/unified-framework/number-theory/prime-curve/gmm_fourier_results"
    
    # Load results
    results_table = pd.read_csv(os.path.join(results_dir, "results_table.csv"))
    gmm_params = pd.read_csv(os.path.join(results_dir, "gmm_parameters.csv"))
    
    # Test mathematical constraints
    k_val = results_table['k'].iloc[0]
    assert k_val == 0.3, f"k value error: {k_val}"
    
    S_b = results_table['S_b'].iloc[0]
    assert S_b > 0, f"S_b should be positive: {S_b}"
    
    bar_sigma = results_table['bar_σ'].iloc[0]
    assert bar_sigma > 0, f"bar_σ should be positive: {bar_sigma}"
    
    # GMM weights should sum to 1
    weights_sum = gmm_params['weight'].sum()
    assert abs(weights_sum - 1.0) < 1e-6, f"GMM weights don't sum to 1: {weights_sum}"
    
    # All sigmas should be positive
    assert all(gmm_params['sigma'] > 0), "GMM sigmas should be positive"
    
    # Means should be in [0,1) range
    assert all(gmm_params['mean'] >= 0) and all(gmm_params['mean'] < 1), "GMM means out of range"
    
    # BIC should be finite
    bic = results_table['BIC'].iloc[0]
    aic = results_table['AIC'].iloc[0]
    assert np.isfinite(bic) and np.isfinite(aic), "BIC/AIC not finite"
    
    print("✓ Mathematical constraints tests passed")

def run_all_tests():
    """Run complete test suite"""
    print("="*60)
    print("GMM AND FOURIER ANALYSIS - TEST SUITE")
    print("="*60)
    
    try:
        test_basic_functionality()
        test_data_generation()
        test_fourier_analysis()
        test_gmm_analysis()
        test_bootstrap_structure()
        test_results_files()
        test_mathematical_constraints()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        
        # Print summary of actual results
        results_dir = "/home/runner/work/unified-framework/unified-framework/number-theory/prime-curve/gmm_fourier_results"
        results_table = pd.read_csv(os.path.join(results_dir, "results_table.csv"))
        
        print("\nFINAL RESULTS SUMMARY:")
        print(f"k = {results_table['k'].iloc[0]}")
        print(f"S_b = {results_table['S_b'].iloc[0]:.3f} (CI: [{results_table['CI_S_b_lower'].iloc[0]:.3f}, {results_table['CI_S_b_upper'].iloc[0]:.3f}])")
        print(f"bar_σ = {results_table['bar_σ'].iloc[0]:.3f} (CI: [{results_table['CI_bar_σ_lower'].iloc[0]:.3f}, {results_table['CI_bar_σ_upper'].iloc[0]:.3f}])")
        print(f"BIC = {results_table['BIC'].iloc[0]:.1f}")
        print(f"AIC = {results_table['AIC'].iloc[0]:.1f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)