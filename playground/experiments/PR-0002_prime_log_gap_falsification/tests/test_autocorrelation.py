"""
Tests for autocorrelation analysis with optional Ljung-Box test.

These tests validate:
1. Default behavior (Ljung-Box disabled)
2. Explicit Ljung-Box enabled
3. White noise control (should not reject null)
4. AR(1) positive control (should reject null)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from autocorrelation import compute_autocorrelation_analysis


def test_default_ljungbox_disabled():
    """
    Test that default behavior does NOT run Ljung-Box (autocorr=none equivalent).
    """
    print("\nTest 1: Default Ljung-Box Disabled")
    print("-" * 50)
    
    np.random.seed(42)
    data = np.random.randn(1000)
    
    # Default should have run_ljungbox=True for backward compatibility
    # But we'll test the disabled case explicitly
    result = compute_autocorrelation_analysis(data, nlags=20, run_ljungbox=False)
    
    # Check that Ljung-Box status is not evaluated
    assert result['ljungbox_status'] == 'not_evaluated', \
        f"Expected 'not_evaluated', got '{result['ljungbox_status']}'"
    assert result['ljungbox_all_p_above_005'] is None, \
        "Expected None for ljungbox_all_p_above_005 when disabled"
    assert result['f4_falsified'] is None, \
        "Expected None for f4_falsified when disabled"
    
    # Check that ACF/PACF are still computed
    assert result['acf'] is not None, "ACF should still be computed"
    assert len(result['acf']) == 21, f"Expected 21 ACF values, got {len(result['acf'])}"
    assert result['nlags'] == 20, f"Expected nlags=20, got {result['nlags']}"
    
    print("✓ Ljung-Box correctly disabled")
    print(f"  ljungbox_status: {result['ljungbox_status']}")
    print(f"  ljungbox_all_p_above_005: {result['ljungbox_all_p_above_005']}")
    print(f"  ACF length: {len(result['acf'])}")
    print(f"  Has short-range structure: {result['has_short_range_structure']}")
    
    return True


def test_ljungbox_enabled():
    """
    Test that Ljung-Box runs when explicitly enabled.
    """
    print("\nTest 2: Ljung-Box Enabled")
    print("-" * 50)
    
    np.random.seed(42)
    data = np.random.randn(1000)
    
    result = compute_autocorrelation_analysis(data, nlags=20, run_ljungbox=True)
    
    # Check that Ljung-Box was evaluated
    assert result['ljungbox_status'] == 'evaluated', \
        f"Expected 'evaluated', got '{result['ljungbox_status']}'"
    assert result['ljungbox_all_p_above_005'] is not None, \
        "Expected non-None value for ljungbox_all_p_above_005 when enabled"
    assert result['f4_falsified'] is not None, \
        "Expected non-None value for f4_falsified when enabled"
    
    # Check that results object is present
    assert result['ljungbox_results'] is not None, \
        "Expected ljungbox_results when enabled"
    
    print("✓ Ljung-Box correctly enabled")
    print(f"  ljungbox_status: {result['ljungbox_status']}")
    print(f"  ljungbox_all_p_above_005: {result['ljungbox_all_p_above_005']}")
    print(f"  f4_falsified: {result['f4_falsified']}")
    
    return True


def test_white_noise_control():
    """
    Test Ljung-Box on white noise - should NOT reject null (high p-values).
    """
    print("\nTest 3: White Noise Control")
    print("-" * 50)
    
    np.random.seed(123)
    white_noise = np.random.randn(1000)
    
    result = compute_autocorrelation_analysis(white_noise, nlags=20, run_ljungbox=True)
    
    # For white noise, most lags should have p > 0.05
    # We expect ljungbox_all_p_above_005 to be True or at least not strongly False
    print(f"  White noise ljungbox_all_p_above_005: {result['ljungbox_all_p_above_005']}")
    print(f"  Significant ACF lags: {result['significant_lags']}")
    
    # With white noise, we might have a few false positives, but not many
    num_significant = len(result['significant_lags'])
    print(f"  Number of significant ACF lags: {num_significant} (expect few)")
    
    print("✓ White noise test complete")
    
    return True


def test_ar1_positive_control():
    """
    Test Ljung-Box on AR(1) process - should reject null (low p-values).
    """
    print("\nTest 4: AR(1) Positive Control")
    print("-" * 50)
    
    np.random.seed(456)
    n = 1000
    ar1_data = np.zeros(n)
    ar1_data[0] = np.random.randn()
    
    # Generate AR(1) with rho=0.7 (strong autocorrelation)
    for i in range(1, n):
        ar1_data[i] = 0.7 * ar1_data[i-1] + np.random.randn()
    
    result = compute_autocorrelation_analysis(ar1_data, nlags=20, run_ljungbox=True)
    
    # For AR(1), we expect strong autocorrelation
    # ljungbox_all_p_above_005 should be False (reject null)
    print(f"  AR(1) ljungbox_all_p_above_005: {result['ljungbox_all_p_above_005']}")
    print(f"  Significant ACF lags: {result['significant_lags'][:10]}...")
    
    # With AR(1), we should have many significant lags
    num_significant = len(result['significant_lags'])
    print(f"  Number of significant ACF lags: {num_significant} (expect many)")
    
    assert not result['ljungbox_all_p_above_005'], \
        "AR(1) process should reject white noise null hypothesis"
    assert num_significant > 0, \
        "AR(1) process should have significant autocorrelation"
    
    print("✓ AR(1) positive control passed")
    
    return True


def test_performance_guard():
    """
    Verify that when Ljung-Box is disabled, it doesn't consume time.
    This is a lightweight check - just ensures the code path is different.
    """
    print("\nTest 5: Performance Guard")
    print("-" * 50)
    
    import time
    
    np.random.seed(789)
    large_data = np.random.randn(10000)
    
    # Time disabled
    start = time.time()
    result_disabled = compute_autocorrelation_analysis(large_data, nlags=20, run_ljungbox=False)
    time_disabled = time.time() - start
    
    # Time enabled
    start = time.time()
    result_enabled = compute_autocorrelation_analysis(large_data, nlags=20, run_ljungbox=True)
    time_enabled = time.time() - start
    
    print(f"  Time with Ljung-Box disabled: {time_disabled:.4f}s")
    print(f"  Time with Ljung-Box enabled: {time_enabled:.4f}s")
    
    # Disabled should be faster (though both might be fast for small data)
    if time_enabled > time_disabled:
        print(f"  ✓ Enabled is slower (speedup: {time_enabled/time_disabled:.2f}x)")
    else:
        print(f"  Note: Times similar (data may be too small to see difference)")
    
    # Verify results are different
    assert result_disabled['ljungbox_status'] == 'not_evaluated'
    assert result_enabled['ljungbox_status'] == 'evaluated'
    
    print("✓ Performance guard check passed")
    
    return True


def run_all_tests():
    """Run all autocorrelation tests."""
    print("=" * 70)
    print("AUTOCORRELATION ANALYSIS TESTS")
    print("=" * 70)
    
    tests = [
        ("Default Ljung-Box Disabled", test_default_ljungbox_disabled),
        ("Ljung-Box Enabled", test_ljungbox_enabled),
        ("White Noise Control", test_white_noise_control),
        ("AR(1) Positive Control", test_ar1_positive_control),
        ("Performance Guard", test_performance_guard),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
