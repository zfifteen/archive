#!/usr/bin/env python3
"""
Test PRP (Probable Prime) Gate Determinism

This test suite ensures that the Miller-Rabin primality test is:
1. Deterministic (same input → same output)
2. Reproducible across runs
3. Uses fixed witness bases (not random)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from rsa260_repro import miller_rabin_deterministic


def test_deterministic_on_primes():
    """Test that deterministic Miller-Rabin correctly identifies known primes."""
    known_primes = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
        97, 127, 257, 65537,  # Fermat primes
        2147483647,  # Mersenne prime (2^31 - 1)
        # Large primes
        1000000007,
        10000000019,
        100000000003,
    ]
    
    for p in known_primes:
        assert miller_rabin_deterministic(p, rounds=32), \
            f"Failed to identify known prime: {p}"


def test_deterministic_on_composites():
    """Test that deterministic Miller-Rabin correctly identifies known composites."""
    known_composites = [
        4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28,
        # Carmichael numbers (pseudoprimes to many bases)
        561, 1105, 1729, 2465, 2821, 6601, 8911,
        # Large composites
        1000000008,  # 2^3 * 125000001
        10000000020,  # 4 * 2500000005
        # RSA-like products
        1000000007 * 1000000009,  # product of two large primes
    ]
    
    for n in known_composites:
        assert not miller_rabin_deterministic(n, rounds=32), \
            f"Failed to identify known composite: {n}"


def test_reproducibility():
    """Test that the same input always produces the same output."""
    test_numbers = [
        2, 3, 97, 561, 1729, 1000000007, 1000000008,
        1000000007 * 1000000009
    ]
    
    for n in test_numbers:
        # Run test multiple times
        results = [miller_rabin_deterministic(n, rounds=32) for _ in range(10)]
        
        # All results should be identical
        assert all(r == results[0] for r in results), \
            f"Non-deterministic result for {n}: {results}"


def test_different_round_counts():
    """Test that different round counts still give deterministic results."""
    n = 1000000007  # Known prime
    
    # Test with different round counts
    for rounds in [8, 16, 32]:
        results = [miller_rabin_deterministic(n, rounds=rounds) for _ in range(5)]
        
        # All results for same round count should be identical
        assert all(r == results[0] for r in results), \
            f"Non-deterministic with rounds={rounds}: {results}"


def test_edge_cases():
    """Test edge cases for Miller-Rabin."""
    # Small numbers
    assert not miller_rabin_deterministic(0, rounds=32)
    assert not miller_rabin_deterministic(1, rounds=32)
    assert miller_rabin_deterministic(2, rounds=32)
    assert miller_rabin_deterministic(3, rounds=32)
    
    # Even numbers (except 2)
    for n in [4, 6, 8, 10, 100, 1000, 10000]:
        assert not miller_rabin_deterministic(n, rounds=32), \
            f"Even number {n} incorrectly marked as prime"


def test_witness_bases_are_fixed():
    """Test that we use fixed witness bases (first 32 primes)."""
    # The implementation should use: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, ...
    # We can't directly test the witnesses, but we can verify behavior
    
    # Test with a number that would fail with random witnesses sometimes
    # but should always fail with fixed witnesses
    n = 561  # Carmichael number (pseudoprime to base 2)
    
    # Should consistently identify as composite
    for _ in range(20):
        assert not miller_rabin_deterministic(n, rounds=32), \
            "Carmichael number incorrectly passed with deterministic witnesses"


def test_large_primes():
    """Test on large primes (cryptographic scale)."""
    # These are large known primes
    large_primes = [
        # ~40 bits
        1099511627791,  # 2^40 - 17
        # ~50 bits
        1125899906842597,  # 2^50 - 27
    ]
    
    for p in large_primes:
        result = miller_rabin_deterministic(p, rounds=32)
        assert result, f"Failed to identify large prime: {p}"


def test_large_composites():
    """Test on large composites."""
    # Product of large primes
    p1 = 1000000007
    p2 = 1000000009
    n = p1 * p2
    
    assert not miller_rabin_deterministic(n, rounds=32), \
        f"Failed to identify large composite: {n}"


def test_consistency_with_different_inputs():
    """Test that function is consistent across different input types."""
    # Test the same number as different types
    n_int = 1000000007
    
    # Should all give same result
    result1 = miller_rabin_deterministic(n_int, rounds=32)
    result2 = miller_rabin_deterministic(int(n_int), rounds=32)
    
    assert result1 == result2, \
        f"Inconsistent results for different input types: {result1} vs {result2}"


def test_no_randomness_in_deterministic_mode():
    """Test that there's no randomness in deterministic mode."""
    # Run same test many times
    n = 123456789012345678901234567890  # Large number
    
    results = set()
    for _ in range(100):
        result = miller_rabin_deterministic(n, rounds=32)
        results.add(result)
    
    # Should have only one unique result (fully deterministic)
    assert len(results) == 1, \
        f"Non-deterministic behavior detected: {results}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
