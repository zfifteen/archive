#!/usr/bin/env python3
"""
Test suite for SHA-256 Constant Predictability PoC

This test validates that the PoC correctly:
1. Reconstructs SHA-256 IV constants
2. Computes fractional parts accurately
3. Handles various inputs correctly
"""

import sys
from pathlib import Path

# Add hash-bounds directory to path
hash_bounds_dir = Path(__file__).parent.parent / "experiments" / "hash-bounds"
sys.path.insert(0, str(hash_bounds_dir))

import poc


def test_sha256_iv_constants():
    """Test that SHA-256 IV constants are correctly defined."""
    expected_iv = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]
    assert poc.SHA256_IV == expected_iv, "SHA-256 IV constants mismatch"


def test_nth_prime():
    """Test prime computation for small indices."""
    expected = {
        1: 2, 2: 3, 3: 5, 4: 7, 5: 11,
        6: 13, 7: 17, 8: 19, 10: 29,
    }
    
    for n, expected_prime in expected.items():
        actual = poc.nth_prime(n)
        assert actual == expected_prime, f"nth_prime({n}) = {actual}, expected {expected_prime}"


def test_fractional_sqrt():
    """Test fractional square root computation."""
    # Test with known values
    test_cases = [
        (2, 0.41421356),   # sqrt(2) - 1
        (3, 0.73205081),   # sqrt(3) - 1
        (5, 0.23606798),   # sqrt(5) - 2
        (7, 0.64575131),   # sqrt(7) - 2
    ]
    
    for x, expected_frac in test_cases:
        frac = poc.fractional_sqrt(x)
        assert abs(frac - expected_frac) < 1e-6, \
            f"fractional_sqrt({x}) = {frac}, expected {expected_frac}"


def test_sha256_frac_to_u32_hex():
    """Test conversion from fractional part to SHA-256 32-bit word."""
    # Test first SHA-256 IV value: sqrt(2)
    frac = poc.fractional_sqrt(2)
    word = poc.sha256_frac_to_u32_hex(frac)
    expected = "0x6a09e667"
    assert word == expected, f"sha256_frac_to_u32_hex({frac}) = {word}, expected {expected}"
    
    # Test second SHA-256 IV value: sqrt(3)
    frac = poc.fractional_sqrt(3)
    word = poc.sha256_frac_to_u32_hex(frac)
    expected = "0xbb67ae85"
    assert word == expected, f"sha256_frac_to_u32_hex({frac}) = {word}, expected {expected}"


def test_iv_reconstruction():
    """Test that we can perfectly reconstruct SHA-256 IV from first 8 primes."""
    reconstructed = []
    
    for i in range(1, 9):
        p = poc.nth_prime(i)
        frac = poc.fractional_sqrt(p)
        word_hex = poc.sha256_frac_to_u32_hex(frac)
        word_int = int(word_hex, 16)
        reconstructed.append(word_int)
    
    assert reconstructed == poc.SHA256_IV, \
        "Reconstructed IV does not match official SHA-256 IV"


def test_predict_prime_smooth():
    """Test smooth prime approximation."""
    # For m=10, m*log(m) should give a reasonable approximation
    pred = poc.predict_prime_smooth(10)
    
    # Should be positive and somewhat close to true value (29)
    assert pred > 0, "Predicted prime should be positive"
    assert 15 < pred < 40, f"Predicted prime {pred} out of reasonable range for m=10"


def test_geometric_bound():
    """Test geometric bound computation."""
    m = 10
    frac_pred = 0.5
    
    lower, upper = poc.compute_geometric_bound(m, frac_pred)
    
    # Bounds should be reasonable
    assert lower < frac_pred < upper, "Predicted frac should be within bounds"
    assert 0 <= lower < 1, f"Lower bound {lower} out of range [0, 1)"
    assert 0 <= upper < 2, f"Upper bound {upper} too large"
    
    # Width should be positive
    width = upper - lower
    assert width > 0, "Bound width should be positive"


def test_demonstrate_predictability():
    """Test that demonstrate_predictability runs without error."""
    # This is more of an integration test
    try:
        # Capture output but don't display it
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            poc.demonstrate_predictability(m=5, use_z5d=False, show_bounds=True)
        
        output = f.getvalue()
        assert "Geometric Fractional-Part Demo" in output
        assert "Prime index (m): 5" in output
        
    except Exception as e:
        raise AssertionError(f"demonstrate_predictability raised exception: {e}")


def test_show_sha256_iv():
    """Test that show_sha256_iv runs without error."""
    try:
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            poc.show_sha256_iv()
        
        output = f.getvalue()
        assert "SHA-256 Initial Vector" in output
        assert "Perfect match" in output
        
    except Exception as e:
        raise AssertionError(f"show_sha256_iv raised exception: {e}")


def run_tests():
    """Run all tests."""
    tests = [
        ("SHA-256 IV constants", test_sha256_iv_constants),
        ("nth_prime", test_nth_prime),
        ("fractional_sqrt", test_fractional_sqrt),
        ("sha256_frac_to_u32_hex", test_sha256_frac_to_u32_hex),
        ("IV reconstruction", test_iv_reconstruction),
        ("predict_prime_smooth", test_predict_prime_smooth),
        ("geometric_bound", test_geometric_bound),
        ("demonstrate_predictability", test_demonstrate_predictability),
        ("show_sha256_iv", test_show_sha256_iv),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}: Unexpected error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
