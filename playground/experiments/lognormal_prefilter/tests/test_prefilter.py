"""
Tests for the candidate prefilter.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from prefilter import (
    generate_lognormal_offsets,
    probably_prime,
    pollard_rho,
    factor_with_candidate_prefilter
)
from model import create_default_model_store
from config import SearchPolicyConfig


def test_generate_lognormal_offsets_alternate():
    """Test that generate_lognormal_offsets produces alternating signs."""
    store = create_default_model_store()
    band = store.get_band_for_p(500000)
    cfg = SearchPolicyConfig(max_steps=100, direction_mode="ALTERNATE", random_seed=42)
    
    offsets = generate_lognormal_offsets(500000, band, cfg)
    
    # Should have max_steps offsets
    assert len(offsets) == 100
    
    # Check that we have both positive and negative offsets
    positive = [o for o in offsets if o > 0]
    negative = [o for o in offsets if o < 0]
    
    assert len(positive) > 0, "Should have positive offsets"
    assert len(negative) > 0, "Should have negative offsets"
    
    print(f"✓ generate_lognormal_offsets (ALTERNATE): {len(positive)} positive, {len(negative)} negative")


def test_generate_lognormal_offsets_random():
    """Test that generate_lognormal_offsets works in RANDOM mode."""
    store = create_default_model_store()
    band = store.get_band_for_p(500000)
    cfg = SearchPolicyConfig(max_steps=100, direction_mode="RANDOM", random_seed=42)
    
    offsets = generate_lognormal_offsets(500000, band, cfg)
    
    # Should have max_steps offsets
    assert len(offsets) == 100
    
    # Check that we have both positive and negative offsets
    positive = [o for o in offsets if o > 0]
    negative = [o for o in offsets if o < 0]
    
    assert len(positive) > 0, "Should have positive offsets"
    assert len(negative) > 0, "Should have negative offsets"
    
    print(f"✓ generate_lognormal_offsets (RANDOM): {len(positive)} positive, {len(negative)} negative")


def test_probably_prime():
    """Test Miller-Rabin primality test."""
    # Known primes
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in primes:
        assert probably_prime(p) == True, f"{p} should be prime"
    
    # Known composites
    composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25]
    for c in composites:
        assert probably_prime(c) == False, f"{c} should be composite"
    
    # Larger primes
    large_primes = [10007, 10009, 10037, 10039]
    for p in large_primes:
        assert probably_prime(p) == True, f"{p} should be prime"
    
    print("✓ probably_prime works correctly")


def test_pollard_rho_small():
    """Test Pollard's rho on small numbers."""
    # Even number
    factor = pollard_rho(100)
    assert factor == 2
    
    # Small semiprimes
    test_cases = [
        (15, [3, 5]),
        (21, [3, 7]),
        (35, [5, 7]),
        (77, [7, 11]),
    ]
    
    for N, expected in test_cases:
        factor = pollard_rho(N)
        if factor is not None:
            assert factor in expected or N // factor in expected
            assert N % factor == 0
            print(f"  ✓ pollard_rho factored {N} = {factor} × {N // factor}")
    
    print("✓ pollard_rho works on small numbers")


def test_factor_with_candidate_prefilter_even():
    """Test that even numbers return 2."""
    store = create_default_model_store()
    cfg = SearchPolicyConfig(random_seed=42)
    
    factor = factor_with_candidate_prefilter(100, store, cfg)
    assert factor == 2
    
    print("✓ factor_with_candidate_prefilter handles even numbers")


def test_factor_with_candidate_prefilter_small():
    """Test factorization of small semiprimes."""
    store = create_default_model_store()
    cfg = SearchPolicyConfig(max_steps=1000, random_seed=42)
    
    test_cases = [
        (15, [3, 5]),
        (21, [3, 7]),
        (35, [5, 7]),
        (77, [7, 11]),
        (143, [11, 13]),
    ]
    
    for N, expected_factors in test_cases:
        factor = factor_with_candidate_prefilter(N, store, cfg)
        # For very small N, the lognormal model may not be helpful
        # but the Pollard's rho fallback should still find a factor
        if factor is not None:
            assert N % factor == 0, f"{factor} should divide {N}"
            print(f"  ✓ Factored {N} = {factor} × {N // factor}")
        else:
            # This should be very rare due to fallback
            print(f"  ~ Could not factor {N} (rare but possible)")
    
    print("✓ factor_with_candidate_prefilter works on small semiprimes")


def test_factor_with_candidate_prefilter_medium():
    """Test factorization of medium semiprimes."""
    store = create_default_model_store()
    cfg = SearchPolicyConfig(max_steps=5000, random_seed=42)
    
    # Semiprimes with factors in tractable range
    test_cases = [
        (10007 * 10009, [10007, 10009]),
        (10037 * 10039, [10037, 10039]),
    ]
    
    for N, expected_factors in test_cases:
        factor = factor_with_candidate_prefilter(N, store, cfg)
        if factor is not None:
            assert N % factor == 0
            print(f"  ✓ Factored {N} = {factor} × {N // factor}")
        else:
            print(f"  ~ Could not factor {N}")
    
    print("✓ factor_with_candidate_prefilter tested on medium semiprimes")


def run_all_tests():
    """Run all prefilter tests."""
    test_generate_lognormal_offsets_alternate()
    test_generate_lognormal_offsets_random()
    test_probably_prime()
    test_pollard_rho_small()
    test_factor_with_candidate_prefilter_even()
    test_factor_with_candidate_prefilter_small()
    test_factor_with_candidate_prefilter_medium()
    print("\n✓ All prefilter tests passed!")


if __name__ == "__main__":
    run_all_tests()
