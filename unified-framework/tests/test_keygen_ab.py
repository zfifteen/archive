"""
Tests for keygen A/B experiment harness.

Validates determinism and correctness with small trials.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from src.experiments.keygen_ab import (
    generate_candidate,
    trial_division,
    is_prime_miller_rabin,
    find_prime,
    run_keygen_experiment,
    save_results,
)


class TestCandidateGeneration:
    """Test candidate generation."""

    def test_generate_candidate_odd(self):
        """Candidates should be odd."""
        rng = np.random.RandomState(42)
        for bit_length in [256, 512, 1024]:
            candidate = generate_candidate(bit_length, rng)
            assert candidate % 2 == 1

    def test_generate_candidate_range(self):
        """Candidates should be in correct bit range."""
        rng = np.random.RandomState(42)
        bit_length = 256
        candidate = generate_candidate(bit_length, rng)

        lower = 2 ** (bit_length - 1)
        upper = 2**bit_length - 1

        assert lower <= candidate <= upper

    def test_generate_candidate_determinism(self):
        """Same seed should produce same candidates."""
        rng1 = np.random.RandomState(42)
        rng2 = np.random.RandomState(42)

        c1 = generate_candidate(256, rng1)
        c2 = generate_candidate(256, rng2)

        assert c1 == c2


class TestTrialDivision:
    """Test trial division primality check."""

    def test_small_primes(self):
        """Small primes should pass."""
        assert trial_division(2)
        assert trial_division(3)
        assert trial_division(5)
        assert trial_division(7)
        assert trial_division(11)
        assert trial_division(97)

    def test_small_composites(self):
        """Small composites should fail."""
        assert not trial_division(4)
        assert not trial_division(6)
        assert not trial_division(8)
        assert not trial_division(9)
        assert not trial_division(15)
        assert not trial_division(100)

    def test_edge_cases(self):
        """Edge cases."""
        assert not trial_division(0)
        assert not trial_division(1)


class TestMillerRabin:
    """Test Miller-Rabin primality test."""

    def test_known_primes(self):
        """Known primes should pass."""
        rng = np.random.RandomState(42)
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 97, 101]
        for p in primes:
            assert is_prime_miller_rabin(p, k=5, rng=rng)

    def test_known_composites(self):
        """Known composites should fail."""
        rng = np.random.RandomState(42)
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 100]
        for c in composites:
            assert not is_prime_miller_rabin(c, k=5, rng=rng)

    def test_large_prime(self):
        """Large known prime."""
        rng = np.random.RandomState(42)
        # First prime > 2^20
        p = 1048583
        assert is_prime_miller_rabin(p, k=20, rng=rng)


class TestFindPrime:
    """Test prime finding with simplex-anchor."""

    def test_find_prime_baseline(self):
        """Should find prime in baseline condition."""
        rng = np.random.RandomState(42)
        trial = find_prime(256, "baseline", rng, mr_rounds=5, td_limit=100)

        assert trial.prime_found is not None
        assert trial.candidates_tested > 0
        assert trial.miller_rabin_calls > 0

        # Verify it's actually prime (quick check)
        rng_verify = np.random.RandomState(999)
        assert is_prime_miller_rabin(trial.prime_found, k=10, rng=rng_verify)

    def test_find_prime_simplex(self):
        """Should find prime in simplex condition."""
        rng = np.random.RandomState(42)
        trial = find_prime(256, "simplex", rng, mr_rounds=5, td_limit=100)

        assert trial.prime_found is not None
        assert trial.candidates_tested > 0

        # Verify prime
        rng_verify = np.random.RandomState(999)
        assert is_prime_miller_rabin(trial.prime_found, k=10, rng=rng_verify)

    def test_find_prime_metrics(self):
        """Metrics should be recorded."""
        rng = np.random.RandomState(42)
        trial = find_prime(256, "baseline", rng, mr_rounds=5, td_limit=100)

        assert trial.bit_length == 256
        assert trial.condition == "baseline"
        assert trial.total_time_ms >= trial.mr_time_ms
        assert trial.trial_division_calls >= trial.miller_rabin_calls


class TestKeygenExperiment:
    """Test full keygen experiment."""

    def test_run_small_experiment(self):
        """Run small experiment with determinism."""
        trials, summary = run_keygen_experiment(
            bit_length=256,
            condition="baseline",
            n_trials=3,
            seed=42,
            mr_rounds=5,
            td_limit=100,
        )

        assert len(trials) == 3
        assert summary.n_trials == 3
        assert summary.bit_length == 256
        assert summary.condition == "baseline"
        assert summary.mean_candidates > 0
        assert summary.median_total_time_ms > 0

    def test_experiment_determinism(self):
        """Same seed should give same results."""
        trials1, summary1 = run_keygen_experiment(
            bit_length=256,
            condition="baseline",
            n_trials=2,
            seed=1337,
            mr_rounds=5,
            td_limit=100,
        )

        trials2, summary2 = run_keygen_experiment(
            bit_length=256,
            condition="baseline",
            n_trials=2,
            seed=1337,
            mr_rounds=5,
            td_limit=100,
        )

        # Same candidates found
        assert trials1[0].prime_found == trials2[0].prime_found
        assert trials1[1].prime_found == trials2[1].prime_found

        # Same summary stats
        assert abs(summary1.mean_candidates - summary2.mean_candidates) < 0.01


class TestResultsSaving:
    """Test results saving."""

    def test_save_and_load(self):
        """Save and verify results."""
        trials, summary = run_keygen_experiment(
            bit_length=256,
            condition="baseline",
            n_trials=2,
            seed=42,
            mr_rounds=5,
            td_limit=100,
        )

        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "test_results"
            save_results(trials, summary, output_dir)

            # Verify files exist
            assert (output_dir / "metrics.csv").exists()
            assert (output_dir / "summary.json").exists()

            # Load and verify JSON
            import json

            with open(output_dir / "summary.json") as f:
                loaded = json.load(f)

            assert loaded["condition"] == "baseline"
            assert loaded["n_trials"] == 2
            assert loaded["bit_length"] == 256


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
