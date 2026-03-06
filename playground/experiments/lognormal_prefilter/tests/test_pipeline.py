"""
Tests for the top-level pipeline.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pipeline import factor_with_lognormal_prefilter
from model import create_default_model_store
from config import SearchPolicyConfig


def test_pipeline_even():
    """Test that even numbers return 2."""
    store = create_default_model_store()
    cfg = SearchPolicyConfig(random_seed=42)
    
    factor = factor_with_lognormal_prefilter(100, store, cfg)
    assert factor == 2
    
    factor = factor_with_lognormal_prefilter(1234, store, cfg)
    assert factor == 2
    
    print("✓ Pipeline handles even numbers")


def test_pipeline_small_semiprimes():
    """Test factorization of small semiprimes."""
    store = create_default_model_store()
    cfg = SearchPolicyConfig(max_steps=1000, random_seed=42)
    
    test_cases = [
        (15, [3, 5]),
        (21, [3, 7]),
        (35, [5, 7]),
        (77, [7, 11]),
        (143, [11, 13]),
        (323, [17, 19]),
    ]
    
    for N, expected_factors in test_cases:
        factor = factor_with_lognormal_prefilter(N, store, cfg)
        assert factor is not None, f"Should find a factor for {N}"
        assert N % factor == 0, f"{factor} should divide {N}"
        assert factor > 1 and factor < N, f"{factor} should be non-trivial"
        print(f"  ✓ Factored {N} = {factor} × {N // factor}")
    
    print("✓ Pipeline works on small semiprimes")


def test_pipeline_medium_semiprimes():
    """Test factorization of medium semiprimes."""
    store = create_default_model_store()
    cfg = SearchPolicyConfig(max_steps=5000, random_seed=42)
    
    # Semiprimes with factors in tractable range
    test_cases = [
        (10007 * 10009, [10007, 10009]),
        (10037 * 10039, [10037, 10039]),
    ]
    
    for N, expected_factors in test_cases:
        factor = factor_with_lognormal_prefilter(N, store, cfg)
        assert factor is not None, f"Should find a factor for {N}"
        assert N % factor == 0, f"{factor} should divide {N}"
        print(f"  ✓ Factored {N} = {factor} × {N // factor}")
    
    print("✓ Pipeline works on medium semiprimes")


def test_pipeline_correctness():
    """Test that pipeline always finds valid factors."""
    store = create_default_model_store()
    cfg = SearchPolicyConfig(max_steps=2000, random_seed=42)
    
    # Various test cases
    test_numbers = [
        6,      # 2 × 3
        14,     # 2 × 7
        55,     # 5 × 11
        91,     # 7 × 13
        221,    # 13 × 17
        667,    # 23 × 29
        1147,   # 31 × 37
    ]
    
    for N in test_numbers:
        factor = factor_with_lognormal_prefilter(N, store, cfg)
        assert factor is not None, f"Should find a factor for {N}"
        assert N % factor == 0, f"{factor} should divide {N}"
        assert factor > 1, f"{factor} should be > 1"
        assert factor <= N, f"{factor} should be <= {N}"
        
        # Check that it's actually a non-trivial factor
        other_factor = N // factor
        assert other_factor > 1, f"Should find non-trivial factor, got {factor} for {N}"
        
        print(f"  ✓ Factored {N} = {factor} × {other_factor}")
    
    print("✓ Pipeline always finds valid factors")


def test_pipeline_different_configs():
    """Test pipeline with different configurations."""
    store = create_default_model_store()
    
    N = 10007 * 10009
    
    # Test with ALTERNATE mode
    cfg1 = SearchPolicyConfig(max_steps=5000, direction_mode="ALTERNATE", random_seed=42)
    factor1 = factor_with_lognormal_prefilter(N, store, cfg1)
    assert factor1 is not None
    assert N % factor1 == 0
    print(f"  ✓ ALTERNATE mode: {N} = {factor1} × {N // factor1}")
    
    # Test with RANDOM mode
    cfg2 = SearchPolicyConfig(max_steps=5000, direction_mode="RANDOM", random_seed=42)
    factor2 = factor_with_lognormal_prefilter(N, store, cfg2)
    assert factor2 is not None
    assert N % factor2 == 0
    print(f"  ✓ RANDOM mode: {N} = {factor2} × {N // factor2}")
    
    # Test with different radius_scale
    cfg3 = SearchPolicyConfig(max_steps=5000, radius_scale=2.0, random_seed=42)
    factor3 = factor_with_lognormal_prefilter(N, store, cfg3)
    assert factor3 is not None
    assert N % factor3 == 0
    print(f"  ✓ radius_scale=2.0: {N} = {factor3} × {N // factor3}")
    
    print("✓ Pipeline works with different configurations")


def run_all_tests():
    """Run all pipeline tests."""
    test_pipeline_even()
    test_pipeline_small_semiprimes()
    test_pipeline_medium_semiprimes()
    test_pipeline_correctness()
    test_pipeline_different_configs()
    print("\n✓ All pipeline tests passed!")


if __name__ == "__main__":
    run_all_tests()
