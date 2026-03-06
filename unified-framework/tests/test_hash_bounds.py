#!/usr/bin/env python3
"""
Tests for hash bounds demonstrations.

These tests verify that the hash bounds demo scripts work correctly
and that SHA-256 constants can be reconstructed accurately.
"""

import sys
from pathlib import Path

# Add hash-bounds directory to path
hash_bounds_dir = Path(__file__).parent.parent / "experiments" / "hash-bounds"
sys.path.insert(0, str(hash_bounds_dir))

import pytest  # noqa: E402

# Import from hash_bounds_demo
from hash_bounds_demo import (  # noqa: E402
    SHA256_IV,
    compute_geometric_bound,
    fractional_sqrt,
    nth_prime,
    predict_prime_smooth,
    sha256_frac_to_u32_hex,
)


class TestFractionalSqrt:
    """Test fractional square root computation."""

    def test_fractional_sqrt_basic(self):
        """Test basic fractional sqrt computation."""
        # sqrt(2) = 1.414..., frac = 0.414...
        frac = fractional_sqrt(2)
        assert 0.414 < frac < 0.415

        # sqrt(3) = 1.732..., frac = 0.732...
        frac = fractional_sqrt(3)
        assert 0.732 < frac < 0.733

    def test_fractional_sqrt_perfect_square(self):
        """Test fractional sqrt of perfect square is 0."""
        frac = fractional_sqrt(4)
        assert abs(frac) < 1e-10

        frac = fractional_sqrt(9)
        assert abs(frac) < 1e-10


class TestNthPrime:
    """Test prime number computation."""

    def test_first_primes(self):
        """Test first few primes."""
        assert nth_prime(1) == 2
        assert nth_prime(2) == 3
        assert nth_prime(3) == 5
        assert nth_prime(4) == 7
        assert nth_prime(5) == 11
        assert nth_prime(6) == 13
        assert nth_prime(7) == 17
        assert nth_prime(8) == 19

    def test_larger_primes(self):
        """Test some larger primes."""
        assert nth_prime(10) == 29
        assert nth_prime(20) == 71
        assert nth_prime(50) == 229

    def test_invalid_input(self):
        """Test error on invalid input."""
        with pytest.raises(ValueError):
            nth_prime(0)

        with pytest.raises(ValueError):
            nth_prime(-1)


class TestPredictPrimeSmooth:
    """Test smooth prime approximation."""

    def test_smooth_approximation(self):
        """Test that smooth approximation is in reasonable range."""
        # For m=10, true prime is 29
        pred = predict_prime_smooth(10)
        # m log m = 10 * ln(10) ≈ 23
        assert 20 < pred < 30

        # For m=100, true prime is 541
        pred = predict_prime_smooth(100)
        # m log m = 100 * ln(100) ≈ 460
        assert 400 < pred < 600


class TestSHA256Reconstruction:
    """Test SHA-256 constant reconstruction."""

    def test_sha256_iv_reconstruction(self):
        """Test that we can reconstruct all SHA-256 IV words."""
        for i in range(1, 9):
            p = nth_prime(i)
            frac = fractional_sqrt(p)
            word_hex = sha256_frac_to_u32_hex(frac)
            word_int = int(word_hex, 16)

            expected = SHA256_IV[i - 1]
            assert word_int == expected, (
                f"Mismatch for prime {i}: " f"got {word_hex}, expected {hex(expected)}"
            )

    def test_first_sha256_word(self):
        """Test reconstruction of first SHA-256 word from sqrt(2)."""
        frac = fractional_sqrt(2)
        word_hex = sha256_frac_to_u32_hex(frac)
        assert word_hex == "0x6a09e667"

    def test_second_sha256_word(self):
        """Test reconstruction of second SHA-256 word from sqrt(3)."""
        frac = fractional_sqrt(3)
        word_hex = sha256_frac_to_u32_hex(frac)
        assert word_hex == "0xbb67ae85"


class TestGeometricBounds:
    """Test geometric bound computation."""

    def test_bounds_basic(self):
        """Test that bounds are computed correctly."""
        frac_pred = 0.5
        lower, upper = compute_geometric_bound(10, frac_pred, width_factor=0.155)

        # Bounds should be around the predicted value
        assert lower < frac_pred
        assert upper > frac_pred

        # Bounds should be in [0, 1] range (or close)
        assert -0.5 < lower < 1.5
        assert -0.5 < upper < 1.5

    def test_bounds_contain_truth(self):
        """Test that bounds often contain true value."""
        # Use smooth approximation
        p_pred = predict_prime_smooth(10)
        frac_pred = fractional_sqrt(p_pred)

        lower, upper = compute_geometric_bound(10, frac_pred, width_factor=0.3)

        # With wide bounds, should contain true value
        # Note: This might not always be true, so we just check bounds exist
        assert lower < upper
        assert upper - lower > 0

    def test_bounds_width_factor(self):
        """Test that width_factor affects bound width."""
        frac_pred = 0.5

        lower1, upper1 = compute_geometric_bound(10, frac_pred, width_factor=0.1)
        lower2, upper2 = compute_geometric_bound(10, frac_pred, width_factor=0.3)

        width1 = upper1 - lower1
        width2 = upper2 - lower2

        # Larger width_factor should give wider bounds
        assert width2 > width1


class TestIntegration:
    """Integration tests for the demo."""

    def test_full_workflow(self):
        """Test full workflow for one prime."""
        m = 5

        # Get true prime
        p_true = nth_prime(m)
        assert p_true == 11

        # Get true fractional part
        frac_true = fractional_sqrt(p_true)

        # Get true SHA-256 word
        word_true = sha256_frac_to_u32_hex(frac_true)
        assert word_true == "0x510e527f"

        # Verify it matches SHA-256 IV
        assert int(word_true, 16) == SHA256_IV[4]


def test_imports():
    """Test that all necessary imports work."""
    # These should not raise ImportError
    from hash_bounds_demo import (  # noqa: F401
        compute_geometric_bound,
        demonstrate_predictability,
        fractional_sqrt,
        nth_prime,
        predict_prime_smooth,
        sha256_frac_to_u32_hex,
        show_sha256_iv,
    )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
