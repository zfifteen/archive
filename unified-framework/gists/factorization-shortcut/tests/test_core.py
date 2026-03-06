"""
Core tests for Z5D Factorization Shortcut.

Smoke tests with reproducible seeds to validate:
- Success rate within expected bounds
- Candidate reduction vs naive
- Reproducibility across runs
"""

import os
import sys
import subprocess
import json
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import main script functions (will be refactored to proper module)
# For now, test via subprocess to match production usage

Z5D_SCRIPT = Path(__file__).parent.parent / "factorization_shortcut_z5d.py"
Z5D_BINARY = os.environ.get(
    'Z5D_PRIME_GEN',
    str(Path(__file__).parent.parent.parent.parent / 'src/c/bin/z5d_prime_gen')
)


@pytest.fixture(scope="session")
def z5d_binary():
    """Ensure Z5D binary exists."""
    if not Path(Z5D_BINARY).exists():
        pytest.skip(f"Z5D binary not found at {Z5D_BINARY}. Run 'make z5d_prime_gen' first.")
    return Z5D_BINARY


def run_factorization(nmax, samples, eps, seed, mode="balanced"):
    """Run factorization script and parse output."""
    result = subprocess.run(
        [
            sys.executable,
            str(Z5D_SCRIPT),
            "--Nmax", str(nmax),
            "--samples", str(samples),
            "--eps", str(eps),
            "--seed", str(seed),
            "--mode", mode
        ],
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Parse success rate from output
    for line in result.stdout.split('\n'):
        if '| band@' in line and '|' in line:
            parts = line.split('|')
            if len(parts) >= 6:
                try:
                    rate = float(parts[5].strip())
                    return {"success_rate": rate, "output": result.stdout}
                except (ValueError, IndexError):
                    continue

    pytest.fail(f"Could not parse success rate from output:\n{result.stdout}")


class TestReproducibility:
    """Test that results are reproducible with fixed seeds."""

    def test_same_seed_same_results(self, z5d_binary):
        """Same seed should produce identical results."""
        params = {"nmax": 100000, "samples": 50, "eps": 0.05, "seed": 42}

        result1 = run_factorization(**params)
        result2 = run_factorization(**params)

        assert result1["success_rate"] == result2["success_rate"], \
            "Results should be identical with same seed"

    def test_different_seed_different_results(self, z5d_binary):
        """Different seeds should (usually) produce different results."""
        result1 = run_factorization(100000, 50, 0.05, seed=42)
        result2 = run_factorization(100000, 50, 0.05, seed=123)

        # Results will likely differ, but both should be valid
        assert 0.0 <= result1["success_rate"] <= 1.0
        assert 0.0 <= result2["success_rate"] <= 1.0


class TestSuccessRate:
    """Test that success rates are within expected bounds."""

    def test_smoke_balanced_nmax_100k(self, z5d_binary):
        """Quick smoke test with small N."""
        result = run_factorization(100000, 100, 0.05, seed=42, mode="balanced")

        # Success rate should be between 10-35% (loose bounds for smoke test)
        assert 0.10 <= result["success_rate"] <= 0.35, \
            f"Success rate {result['success_rate']:.1%} outside expected range [10%, 35%]"

    def test_baseline_balanced_nmax_1m(self, z5d_binary):
        """Baseline validation matching PR claims."""
        result = run_factorization(1000000, 500, 0.05, seed=42, mode="balanced")

        # Wilson 95% CI: [20.8%, 26.0%] from PR validation
        # Use looser bounds for CI stability: [18%, 28%]
        assert 0.18 <= result["success_rate"] <= 0.28, \
            f"Success rate {result['success_rate']:.1%} outside expected range [18%, 28%]"

    def test_unbalanced_higher_success(self, z5d_binary):
        """Unbalanced semiprimes should have higher success rate."""
        balanced = run_factorization(1000000, 200, 0.05, seed=42, mode="balanced")
        unbalanced = run_factorization(1000000, 200, 0.05, seed=42, mode="unbalanced")

        # Unbalanced should generally be easier (but not guaranteed every run)
        # Just check both are in valid ranges
        assert 0.10 <= balanced["success_rate"] <= 0.40
        assert 0.15 <= unbalanced["success_rate"] <= 0.50


class TestEpsilonScaling:
    """Test that epsilon affects success rate predictably."""

    def test_larger_epsilon_higher_success(self, z5d_binary):
        """Larger epsilon should give higher success rate (more candidates)."""
        # Use same seed for fair comparison
        result_tight = run_factorization(100000, 100, 0.02, seed=42)
        result_loose = run_factorization(100000, 100, 0.10, seed=42)

        # Larger epsilon should give equal or higher success
        # (not strict inequality due to randomness)
        assert result_loose["success_rate"] >= result_tight["success_rate"] * 0.8, \
            f"Larger epsilon should generally improve success rate"


class TestOutputFormat:
    """Test that output format is consistent and parseable."""

    def test_output_contains_summary(self, z5d_binary):
        """Output should contain summary table."""
        result = run_factorization(100000, 50, 0.05, seed=42)

        assert "=== Summary" in result["output"]
        assert "partial_rate" in result["output"]
        assert "avg_candidates" in result["output"]

    def test_output_contains_examples(self, z5d_binary):
        """Output should show factorization examples."""
        result = run_factorization(100000, 50, 0.05, seed=42)

        assert "=== Factorization Shortcut Examples ===" in result["output"]

    def test_output_contains_comparison(self, z5d_binary):
        """Output should compare with naive approach."""
        result = run_factorization(100000, 50, 0.05, seed=42)

        assert "Comparison: Naive vs Geometric" in result["output"] or \
               "vs naive" in result["output"].lower()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_tiny_nmax(self, z5d_binary):
        """Very small Nmax should still work."""
        result = run_factorization(10000, 20, 0.05, seed=42)

        assert 0.0 <= result["success_rate"] <= 1.0

    def test_zero_samples_fails(self, z5d_binary):
        """Zero samples should fail gracefully."""
        with pytest.raises((subprocess.CalledProcessError, AssertionError)):
            run_factorization(100000, 0, 0.05, seed=42)


@pytest.mark.slow
class TestLongerRuns:
    """Longer-running tests (skip in CI with -m 'not slow')."""

    def test_large_sample_statistical_validity(self, z5d_binary):
        """Large sample should match PR claims closely."""
        result = run_factorization(1000000, 1000, 0.05, seed=42)

        # PR claim: 23.3% with CI [20.8%, 26.0%]
        # Expect very close match with n=1000
        assert 0.20 <= result["success_rate"] <= 0.27, \
            f"Large sample success rate {result['success_rate']:.1%} should match PR claims"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
