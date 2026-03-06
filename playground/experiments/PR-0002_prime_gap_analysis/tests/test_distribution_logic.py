
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from distribution_tests import test_distributions, compute_practical_significance

def test_cross_band_logic_fix():
    """Verify that lognormal detection works even if another dist wins best-fit,
    as long as lognormal significantly beats exponential (binary comparison).
    """
    import distribution_tests
    original_fn = distribution_tests.test_distributions_in_band
    
    # Scenario:
    # Band 1: Gamma best fit, but Lognormal > Exponential (sig)
    # Band 2: Gamma best fit, but Lognormal > Exponential (sig)
    # Band 3: Exponential best fit
    
    call_count = 0
    def mock_test_in_band(gaps, band_name):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return {
                'best_fit': 'gamma',
                'practical_sig_favors_lognormal': True,
                'ks_ratio_exp_to_lognormal': 2.0
            }
        else:
            return {
                'best_fit': 'exponential',
                'practical_sig_favors_lognormal': False,
                'ks_ratio_exp_to_lognormal': 0.5
            }
            
    distribution_tests.test_distributions_in_band = mock_test_in_band
    
    try:
        primes = np.array([10**5 + 1, 10**5 + 2, 10**6 + 1, 10**6 + 2, 10**7 + 1, 10**7 + 2])
        results = test_distributions(primes)
        
        print(f"Interpretation: {results['interpretation']}")
        print(f"Lognormal count: {results['lognormal_count']}")
        print(f"Prac sig lognormal count: {results['practical_sig_lognormal_count']}")
        
        # Expectation: 
        # lognormal_count = 0 (Gamma won 2, Exp won 1)
        # practical_sig_lognormal_count = 2 (Bands 1 & 2)
        # Result should be Gamma wins
        
        assert "Gamma structure detected" in results['interpretation']
        assert results['lognormal_count'] == 0
        assert results['practical_sig_lognormal_count'] == 2
        
        print("✓ test_cross_band_logic_fix (Gamma dominance) passed")
        
    finally:
        distribution_tests.test_distributions_in_band = original_fn

def test_lognormal_detection_success():
    """Verify lognormal detection works when bands align perfectly."""
    import distribution_tests
    original_fn = distribution_tests.test_distributions_in_band
    
    call_count = 0
    def mock_test_in_band(gaps, band_name):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return {
                'best_fit': 'normal_on_log',
                'practical_sig_favors_lognormal': True,
                'ks_ratio_exp_to_lognormal': 2.0
            }
        else:
            return {
                'best_fit': 'exponential',
                'practical_sig_favors_lognormal': False,
                'ks_ratio_exp_to_lognormal': 0.5
            }
            
    distribution_tests.test_distributions_in_band = mock_test_in_band
    
    try:
        primes = np.array([10**5 + 1, 10**5 + 2, 10**6 + 1, 10**6 + 2, 10**7 + 1, 10**7 + 2])
        results = test_distributions(primes)
        
        print(f"Interpretation: {results['interpretation']}")
        assert "Lognormal structure detected" in results['interpretation']
        assert results['practical_sig_lognormal_count'] == 2
        assert results['lognormal_count'] == 2
        
        print("✓ test_lognormal_detection_success passed")
        
    finally:
        distribution_tests.test_distributions_in_band = original_fn

def test_no_majority_winner():
    """Verify fallback logic when no distribution has a majority (1-1-1)."""
    import distribution_tests
    original_fn = distribution_tests.test_distributions_in_band
    
    call_count = 0
    def mock_test_in_band(gaps, band_name):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return {'best_fit': 'normal_on_log', 'practical_sig_favors_lognormal': True, 'ks_ratio_exp_to_lognormal': 2.0}
        elif call_count == 2:
            return {'best_fit': 'exponential', 'practical_sig_favors_lognormal': True, 'ks_ratio_exp_to_lognormal': 2.0}
        else:
            return {'best_fit': 'gamma', 'practical_sig_favors_lognormal': False, 'ks_ratio_exp_to_lognormal': 1.0}
            
    distribution_tests.test_distributions_in_band = mock_test_in_band
    
    try:
        primes = np.array([10**5 + 1, 10**5 + 2, 10**6 + 1, 10**6 + 2, 10**7 + 1, 10**7 + 2])
        results = test_distributions(primes)
        
        print(f"Interpretation: {results['interpretation']}")
        # 1 lognormal, 1 exponential, 1 gamma -> No majority.
        # But 2 bands have practical_sig_favors_lognormal
        assert "Lognormal favored over exponential (marginal best-fit evidence)" in results['interpretation']
        
        print("✓ test_no_majority_winner passed")
        
    finally:
        distribution_tests.test_distributions_in_band = original_fn

def test_practical_significance_safety():
    """Verify compute_practical_significance raises error on invalid threshold."""
    
    res = compute_practical_significance(2.0, threshold=1.5)
    assert res['favors_lognormal'] is True
    assert res['favors_exponential'] is False
    
    try:
        compute_practical_significance(1.0, threshold=0.5)
        print("FAIL: Should have raised ValueError for threshold=0.5")
        assert False, "Did not raise ValueError for contradictory threshold"
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")

if __name__ == "__main__":
    test_cross_band_logic_fix()
    test_lognormal_detection_success()
    test_no_majority_winner()
    test_practical_significance_safety()
