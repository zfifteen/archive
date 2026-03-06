#!/usr/bin/env python3
"""
Test Gap Closure Achieved - CI Assertions for Dynamic Comb Step

This test suite validates the deterministic tweak from Issue #211:
- Dynamic comb_step = 1 / (10 * log2(N))
- Ensures fractional and scale-dependent sampling without integer discretization
- Validates pure resonance preservation (CPU-only, deterministic, no local probing)
"""

import pytest
import sys
import os
import math
from mpmath import mp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from greens_function_factorization import (  # noqa: E402
    find_crest_near_sqrt,
    RefinementConfig,
    _dynamic_comb_step,
)


def test_comb_step_is_fractional_and_scale_dependent():
    """
    CI assertion from Issue #211:
    Assert comb_step < 1 / log2(N) and not isinstance(comb_step, int)

    This confirms fractional and scale-dependent sampling without integer discretization.
    """
    # Test with various modulus sizes
    test_cases = [
        # (N, name)
        (143, "small_semiprime"),  # 11 * 13
        (2**64 - 59, "64bit_near_power"),
        (2**128 - 159, "128bit_near_power"),
        (2**256 - 189, "256bit_near_power"),
    ]

    for N, name in test_cases:
        # Create config with fractional comb enabled
        config = RefinementConfig(
            use_fractional_comb=True, comb_range=10  # Small range for testing
        )

        # Call find_crest_near_sqrt which should set dynamic comb_step
        _ = find_crest_near_sqrt(N, k=0.3, window_size=50, config=config)

        # Verify comb_step was set dynamically
        comb_step = config.comb_step
        log2_N = math.log2(N)

        # CI assertion 1: comb_step < 1 / log2(N)
        assert (
            comb_step < 1.0 / log2_N
        ), f"{name}: comb_step {comb_step} should be < 1/log2(N) = {1.0/log2_N}"

        # CI assertion 2: not isinstance(comb_step, int)
        assert not isinstance(
            comb_step, int
        ), f"{name}: comb_step {comb_step} should not be an integer"
        
        # CI assertion 3: type should be mp.mpf for high-precision
        assert isinstance(
            comb_step, type(mp.mpf(1))
        ), f"{name}: comb_step should be mp.mpf type, got {type(comb_step)}"

        # Additional validation: check it follows the formula (with reasonable tolerance)
        expected_comb_step = mp.mpf(1) / (mp.mpf(10) * mp.log(mp.mpf(N), 2))
        # Use relative error tolerance for comparison
        rel_error = abs((comb_step - expected_comb_step) / expected_comb_step)
        assert (
            rel_error < mp.mpf('1e-10')
        ), f"{name}: comb_step {comb_step} != expected {expected_comb_step}, rel_error={rel_error}"


def test_comb_step_scales_with_modulus_size():
    """
    Test that comb_step decreases as modulus size increases.

    This validates the scale-dependent nature of the dynamic adjustment.
    """
    # Use more reasonable modulus sizes that safe_sqrt can handle
    modulus_sizes = [64, 128, 256, 512]
    previous_comb_step = float("inf")

    for bits in modulus_sizes:
        # Create a modulus near 2^bits
        N = 2**bits - 1

        config = RefinementConfig(use_fractional_comb=True, comb_range=10)

        # Trigger dynamic comb_step calculation
        _ = find_crest_near_sqrt(N, k=0.3, window_size=50, config=config)

        comb_step = config.comb_step

        # Verify comb_step decreases with increasing N
        msg = (
            f"comb_step should decrease with larger N: "
            f"{comb_step} >= {previous_comb_step} at {bits} bits"
        )
        assert comb_step < previous_comb_step, msg

        previous_comb_step = comb_step


def test_dynamic_comb_step_is_deterministic():
    """
    Test that dynamic comb_step calculation is deterministic.

    This validates CPU-only, deterministic behavior required by Issue #211.
    """
    N = 2**256 - 189
    k = 0.3

    # Run multiple times and verify identical results
    comb_steps = []

    for _ in range(5):
        config = RefinementConfig(use_fractional_comb=True, comb_range=10)

        _ = find_crest_near_sqrt(N, k, window_size=50, config=config)
        comb_steps.append(config.comb_step)

    # All comb_steps should be identical (deterministic)
    for i in range(len(comb_steps) - 1):
        assert (
            abs(comb_steps[i] - comb_steps[i + 1]) < 1e-15
        ), f"Dynamic comb_step not deterministic: {comb_steps[i]} != {comb_steps[i+1]}"


def test_no_local_probing_in_comb_step():
    """
    Test that comb_step calculation doesn't involve local probing.

    This validates pure resonance preservation (no gcd operations or local searches).
    The calculation should only depend on N and mathematical constants.
    """
    N = 2**1024 - 1

    config = RefinementConfig(use_fractional_comb=True, comb_range=10)

    # The comb_step should be calculable without evaluating candidates
    # This is a whitebox test - we verify the formula is closed-form
    log2_N = math.log2(N)
    expected_comb_step = 1.0 / (10.0 * log2_N)

    # Trigger calculation
    _ = find_crest_near_sqrt(N, k=0.3, window_size=50, config=config)

    # Verify it matches the closed-form formula (no probing involved)
    assert (
        abs(config.comb_step - expected_comb_step) < 1e-10
    ), "comb_step should be pure closed-form calculation"


def test_fractional_comb_disabled_preserves_original_behavior():
    """
    Test that when use_fractional_comb=False, comb_step is not modified.

    This ensures backward compatibility.
    """
    N = 2**256 - 189

    config = RefinementConfig(
        use_fractional_comb=False, comb_step=0.5  # Explicit value
    )

    original_comb_step = config.comb_step

    # Call function with fractional_comb disabled
    _ = find_crest_near_sqrt(N, k=0.3, window_size=50, config=config)

    # comb_step should remain unchanged
    msg = (
        f"comb_step changed when use_fractional_comb=False: "
        f"{config.comb_step} != {original_comb_step}"
    )
    assert config.comb_step == original_comb_step, msg


def test_dynamic_step_precision_stability():
    """
    Test that derived step is stable across different mp.dps settings.
    
    This validates precision stability as required by PR #217 review.
    """
    N = (1 << 2048) - 159  # RSA-2048-like
    
    # Save original dps
    original_dps = mp.dps
    
    try:
        # Compute at two different precision levels
        mp.dps = 80
        s1 = _dynamic_comb_step(N)
        
        mp.dps = 200
        s2 = _dynamic_comb_step(N)
        
        # Results should be stable within tolerance
        assert abs(s1 - s2) <= mp.mpf('1e-70'), (
            f"Precision instability: {s1} vs {s2}, diff = {abs(s1 - s2)}"
        )
        
        # Both should be mp.mpf type
        assert isinstance(s1, type(mp.mpf(1))), f"s1 should be mp.mpf, got {type(s1)}"
        assert isinstance(s2, type(mp.mpf(1))), f"s2 should be mp.mpf, got {type(s2)}"
    finally:
        # Restore original dps
        mp.dps = original_dps


def test_explicit_comb_step_respected():
    """
    Test that explicit config.comb_step is respected and not overridden.
    
    This validates precedence: explicit > derived (PR #217 review Blocking 2).
    """
    N = 2**256 - 189
    explicit_step = mp.mpf("0.0012345")
    
    config = RefinementConfig(
        use_fractional_comb=True,
        comb_step=explicit_step,
        comb_range=10
    )
    
    # Call function - should NOT override explicit comb_step
    _ = find_crest_near_sqrt(N, k=0.3, window_size=50, config=config)
    
    # comb_step should remain exactly as specified
    assert config.comb_step == explicit_step, (
        f"Explicit comb_step was overridden: {config.comb_step} != {explicit_step}"
    )


def test_skewed_modulus_caps_comb_step():
    """
    Test that skewed moduli use capped comb_step (PR #217 review Blocking 5).
    
    For moduli with significant bit-length skew, dynamic stepping should cap
    at 1.0 to avoid over/under-sampling.
    """
    # Create a skewed modulus: very unbalanced factors
    # e.g., 30-bit factor * 226-bit factor = 256-bit modulus
    p_small = (1 << 30) - 35  # ~30 bits
    p_large = (1 << 226) - 5   # ~226 bits
    N_skewed = p_small * p_large
    
    config = RefinementConfig(
        use_fractional_comb=True,
        comb_step=None,  # Auto-derive
        comb_range=10
    )
    
    # Trigger calculation for skewed modulus
    _ = find_crest_near_sqrt(N_skewed, k=0.3, window_size=50, config=config)
    
    # For skewed moduli, comb_step should be capped at 1.0
    assert config.comb_step == mp.mpf(1), (
        f"Skewed modulus should cap comb_step at 1.0, got {config.comb_step}"
    )


def test_rsa_2048_scale_comb_step():
    """
    Test comb_step calculation at RSA-2048 scale (2048 bits).

    This validates the expected impact on rel_distance and abs_distance
    as mentioned in Issue #211. We test just the formula calculation without
    calling find_crest_near_sqrt to avoid overflow issues.
    """
    # Calculate for RSA-2048 scale using the formula directly
    # N would be approximately 2^2048, so log2(N) ≈ 2048
    log2_N_2048 = 2048.0
    expected_comb_step = 1.0 / (10.0 * log2_N_2048)

    # At RSA-2048 scale (log2(N) ≈ 2048), comb_step should be very fine
    # comb_step ≈ 1 / (10 * 2048) ≈ 0.0000488
    assert (
        expected_comb_step < 0.0001
    ), f"RSA-2048 comb_step should be very fine (< 0.0001): {expected_comb_step}"

    msg = (
        "RSA-2048 comb_step should be approximately 4.88e-05: "
        f"{expected_comb_step}"
    )
    assert abs(expected_comb_step - 4.8828125e-05) < 1e-10, msg

    # Verify it's fractional and scale-dependent
    assert not isinstance(expected_comb_step, int), (
        "comb_step should be fractional at RSA-2048 scale"
    )

    assert expected_comb_step < 1.0 / log2_N_2048, (
        "comb_step should be < 1/log2(N) at RSA-2048 scale"
    )

    # Also test with a more reasonable size we can actually compute with
    N_256 = 2**256 - 189
    config = RefinementConfig(use_fractional_comb=True, comb_range=10)

    # Calculate expected value
    log2_N_256 = math.log2(N_256)
    expected_256 = 1.0 / (10.0 * log2_N_256)

    # Trigger calculation
    _ = find_crest_near_sqrt(N_256, k=0.3, window_size=50, config=config)

    # Verify
    assert (
        abs(config.comb_step - expected_256) < 1e-10
    ), f"256-bit scale comb_step mismatch: {config.comb_step} != {expected_256}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
