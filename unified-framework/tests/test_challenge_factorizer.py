#!/usr/bin/env python3
"""
Integration tests for challenge factorizer.

Tests the ChallengeFactor class and 127-bit factorization with smaller
test cases to ensure correctness before running the full challenge.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from z5d.challenge_factorizer import (
    ChallengeFactor,
    FactorizationConfig,
    FactorizationResult,
)


class TestFactorizationConfig:
    """Test FactorizationConfig class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = FactorizationConfig()
        assert config.shell_delta == 2500
        assert config.shell_count == 36
        assert config.use_shell_exclusion is True
    
    def test_challenge_127bit_config(self):
        """Test challenge 127-bit configuration."""
        config = FactorizationConfig.challenge_127bit()
        assert config.use_shell_exclusion is True
        assert config.shell_delta == 2500
        assert config.shell_count == 36
        assert config.qmc_point_count_phase2 == 24000
        assert config.qmc_point_count_phase3 == 48000


class TestChallengeFactor:
    """Test ChallengeFactor class."""
    
    def test_small_semiprime_with_shell_exclusion(self):
        """Test factorization of small semiprime with shell exclusion."""
        config = FactorizationConfig(
            shell_delta=10,
            shell_count=10,
            shell_tau=0.15,
            shell_k_samples=3,
            max_iters=10000,
            use_shell_exclusion=True,
        )
        
        factorizer = ChallengeFactor(config)
        
        # 101 × 103 = 10403
        n = 10403
        result = factorizer.factor(n)
        
        assert result.success is True
        assert result.p == 101
        assert result.q == 103
        assert result.p * result.q == n
        assert result.shell_exclusion_used is True
        assert result.elapsed_seconds > 0
    
    def test_small_semiprime_without_shell_exclusion(self):
        """Test factorization of small semiprime without shell exclusion."""
        config = FactorizationConfig(
            max_iters=10000,
            use_shell_exclusion=False,
        )
        
        factorizer = ChallengeFactor(config)
        
        # 101 × 103 = 10403
        n = 10403
        result = factorizer.factor(n)
        
        assert result.success is True
        assert result.p == 101
        assert result.q == 103
        assert result.p * result.q == n
        assert result.shell_exclusion_used is False
        assert result.excluded_ranges_count == 0
    
    def test_perfect_square(self):
        """Test handling of perfect square."""
        config = FactorizationConfig()
        factorizer = ChallengeFactor(config)
        
        # 121 = 11²
        n = 121
        result = factorizer.factor(n)
        
        assert result.success is True
        assert result.p == 11
        assert result.q == 11
        assert result.method == "perfect_square"
    
    def test_multiple_small_semiprimes(self):
        """Test factorization of multiple small semiprimes."""
        test_cases = [
            (15, 3, 5),
            (77, 7, 11),
            (143, 11, 13),
            (323, 17, 19),
            (667, 23, 29),
        ]
        
        config = FactorizationConfig(
            shell_delta=10,
            shell_count=10,
            max_iters=10000,
            use_shell_exclusion=True,
        )
        
        factorizer = ChallengeFactor(config)
        
        for n, expected_p, expected_q in test_cases:
            result = factorizer.factor(n)
            assert result.success is True, f"Failed to factor {n}"
            assert {result.p, result.q} == {expected_p, expected_q}, (
                f"Wrong factors for {n}: got {result.p} × {result.q}, "
                f"expected {expected_p} × {expected_q}"
            )
    
    def test_medium_semiprime(self):
        """Test factorization of medium-sized semiprime."""
        config = FactorizationConfig(
            shell_delta=100,
            shell_count=20,
            shell_tau=0.15,
            shell_k_samples=5,
            max_iters=100000,
            use_shell_exclusion=True,
        )
        
        factorizer = ChallengeFactor(config)
        
        # 1009 × 1013 = 1022117
        n = 1022117
        result = factorizer.factor(n)
        
        assert result.success is True
        assert result.p == 1009
        assert result.q == 1013
        assert result.shell_exclusion_used is True
    
    def test_result_string_representation(self):
        """Test string representation of results."""
        # Success result
        result = FactorizationResult(
            success=True,
            p=101,
            q=103,
            elapsed_seconds=1.23,
            iterations=1000,
            method="fermat_shell_exclusion",
            shell_exclusion_used=True,
            excluded_ranges_count=5,
            excluded_width=1000,
        )
        
        result_str = str(result)
        assert "SUCCESS" in result_str
        assert "101" in result_str
        assert "103" in result_str
        assert "1.23" in result_str
        
        # Failure result
        result = FactorizationResult(
            success=False,
            p=None,
            q=None,
            elapsed_seconds=5.0,
            iterations=10000,
            method="fermat_baseline",
            shell_exclusion_used=False,
            excluded_ranges_count=0,
            excluded_width=0,
        )
        
        result_str = str(result)
        assert "FAILED" in result_str
        assert "5.0" in result_str


def test_factorization_comparison():
    """
    Compare factorization with and without shell exclusion.
    
    This test verifies that shell exclusion doesn't affect correctness,
    only performance (speed).
    """
    # 1009 × 1013 = 1022117
    n = 1022117
    
    # Config with shell exclusion
    config_with = FactorizationConfig(
        shell_delta=100,
        shell_count=20,
        max_iters=100000,
        use_shell_exclusion=True,
    )
    
    # Config without shell exclusion
    config_without = FactorizationConfig(
        max_iters=100000,
        use_shell_exclusion=False,
    )
    
    factorizer_with = ChallengeFactor(config_with)
    factorizer_without = ChallengeFactor(config_without)
    
    result_with = factorizer_with.factor(n)
    result_without = factorizer_without.factor(n)
    
    # Both should succeed
    assert result_with.success is True
    assert result_without.success is True
    
    # Both should find same factors
    assert {result_with.p, result_with.q} == {result_without.p, result_without.q}
    
    # Shell exclusion should report usage correctly
    assert result_with.shell_exclusion_used is True
    assert result_without.shell_exclusion_used is False


def test_no_false_exclusions():
    """
    Critical test: Ensure shell exclusion never causes false negatives.
    
    This test runs factorization on multiple semiprimes with shell exclusion
    enabled and verifies that all succeed (no false exclusions).
    """
    test_cases = [
        (15, 3, 5),
        (77, 7, 11),
        (143, 11, 13),
        (323, 17, 19),
        (667, 23, 29),
        (1147, 31, 37),
        (1763, 41, 43),
        (2491, 47, 53),
    ]
    
    config = FactorizationConfig(
        shell_delta=20,
        shell_count=15,
        shell_tau=0.15,
        shell_k_samples=5,
        max_iters=50000,
        use_shell_exclusion=True,
    )
    
    factorizer = ChallengeFactor(config)
    
    for n, expected_p, expected_q in test_cases:
        result = factorizer.factor(n)
        
        assert result.success is True, (
            f"Shell exclusion caused false negative for {n} = {expected_p} × {expected_q}"
        )
        
        assert {result.p, result.q} == {expected_p, expected_q}, (
            f"Wrong factors for {n}: got {result.p} × {result.q}, "
            f"expected {expected_p} × {expected_q}"
        )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
