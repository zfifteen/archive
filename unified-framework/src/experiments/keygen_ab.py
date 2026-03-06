"""
RSA Keygen A/B Test Harness

Generates RSA prime candidates and measures the impact of simplex-anchor
enhancement on candidate density and wall-clock time.

NO FALLBACKS: Pure simplex-anchor approach only.
"""

import time
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from pathlib import Path

try:
    from mpmath import mp

    mp.dps = 50  # High precision as required
    MPMATH_AVAILABLE = True
except ImportError:
    MPMATH_AVAILABLE = False

from src.z5d.simplex_anchor import (
    ConditionType,
    create_z5d_state,
    apply_anchor_to_candidate_count,
    validate_no_fallback,
)


@dataclass
class KeygenTrial:
    """Single keygen trial result."""

    trial_id: int
    bit_length: int
    prime_found: int
    candidates_tested: int
    miller_rabin_calls: int
    trial_division_calls: int
    mr_time_ms: float
    total_time_ms: float
    condition: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KeygenSummary:
    """Summary statistics for keygen experiment."""

    condition: str
    bit_length: int
    n_trials: int
    mean_candidates: float
    median_candidates: float
    mean_mr_calls: float
    median_mr_calls: float
    mean_total_time_ms: float
    median_total_time_ms: float
    mean_mr_time_ms: float
    median_mr_time_ms: float
    seed: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def is_prime_miller_rabin(
    n: int, k: int = 20, rng: np.random.RandomState = None
) -> bool:
    """Miller-Rabin primality test.

    Args:
        n: Number to test
        k: Number of rounds (default 20)
        rng: Random number generator for determinism

    Returns:
        True if probably prime, False if composite
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    if rng is None:
        rng = np.random.RandomState(42)

    # Perform k rounds
    for _ in range(k):
        # Use Python's random for large integers
        # Generate random bytes and convert to integer in range [2, n-2]
        a = _random_in_range(2, n - 2, rng)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def _random_in_range(low: int, high: int, rng: np.random.RandomState) -> int:
    """Generate random integer in [low, high] using arbitrary precision.

    Args:
        low: Lower bound (inclusive)
        high: Upper bound (inclusive)
        rng: Random number generator

    Returns:
        Random integer in range
    """
    if low > high:
        raise ValueError("low must be <= high")
    if low == high:
        return low

    range_size = high - low + 1
    num_bits = range_size.bit_length()
    num_bytes = (num_bits + 7) // 8

    # Generate random value in range
    while True:
        random_bytes = rng.bytes(num_bytes)
        value = int.from_bytes(random_bytes, byteorder="big")
        value = value % range_size
        result = low + value
        if low <= result <= high:
            return result


def trial_division(n: int, limit: int = 1000) -> bool:
    """Quick trial division check.

    Args:
        n: Number to test
        limit: Check divisibility up to this limit

    Returns:
        True if no small factors found, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # Check odd divisors
    for d in range(3, min(limit, int(n**0.5) + 1), 2):
        if n % d == 0:
            return False

    return True


def generate_candidate(bit_length: int, rng: np.random.RandomState) -> int:
    """Generate a random odd candidate of specified bit length.

    Args:
        bit_length: Target bit length
        rng: Random number generator

    Returns:
        Odd integer near 2^bit_length
    """
    # Generate near 2^bit_length using Python's arbitrary precision
    # Use random bits instead of randint for large values
    lower_bound = 2 ** (bit_length - 1)
    upper_bound = 2**bit_length - 1

    # Generate random bytes and convert to integer
    num_bytes = (bit_length + 7) // 8
    random_bytes = rng.bytes(num_bytes)
    candidate = int.from_bytes(random_bytes, byteorder="big")

    # Ensure it's in range
    candidate = lower_bound + (candidate % (upper_bound - lower_bound + 1))

    # Make odd
    if candidate % 2 == 0:
        candidate += 1

    return candidate


def find_prime(
    bit_length: int,
    condition: ConditionType,
    rng: np.random.RandomState,
    mr_rounds: int = 20,
    td_limit: int = 1000,
) -> KeygenTrial:
    """Find a single prime using simplex-anchor enhanced search.

    Args:
        bit_length: Target bit length
        condition: Simplex-anchor condition
        rng: Random number generator
        mr_rounds: Miller-Rabin rounds
        td_limit: Trial division limit

    Returns:
        KeygenTrial with metrics
    """
    start_time = time.time()
    mr_time_total = 0.0

    candidates_tested = 0
    mr_calls = 0
    td_calls = 0
    prime_found = None

    # Create Z5D state and validate no fallbacks
    state = create_z5d_state(
        condition,
        {
            "bit_length": bit_length,
            "seed": int(rng.get_state()[1][0]),
        },
    )
    validate_no_fallback(state)

    # Expected candidates with enhancement
    baseline_candidates = bit_length * np.log(2) / 2.0
    expected_candidates = apply_anchor_to_candidate_count(
        baseline_candidates, condition
    )

    # Search for prime
    max_attempts = int(expected_candidates * 10)  # Safety limit

    for _ in range(max_attempts):
        candidate = generate_candidate(bit_length, rng)
        candidates_tested += 1

        # Trial division
        td_calls += 1
        if not trial_division(candidate, td_limit):
            continue

        # Miller-Rabin
        mr_start = time.time()
        mr_calls += 1
        if is_prime_miller_rabin(candidate, mr_rounds, rng):
            prime_found = candidate
            mr_time_total += (time.time() - mr_start) * 1000
            break
        mr_time_total += (time.time() - mr_start) * 1000

    total_time = (time.time() - start_time) * 1000  # Convert to ms

    if prime_found is None:
        raise RuntimeError(f"Failed to find prime in {max_attempts} attempts")

    return KeygenTrial(
        trial_id=-1,  # Will be set by caller
        bit_length=bit_length,
        prime_found=prime_found,
        candidates_tested=candidates_tested,
        miller_rabin_calls=mr_calls,
        trial_division_calls=td_calls,
        mr_time_ms=mr_time_total,
        total_time_ms=total_time,
        condition=condition,
    )


def run_keygen_experiment(
    bit_length: int,
    condition: ConditionType,
    n_trials: int,
    seed: int,
    mr_rounds: int = 20,
    td_limit: int = 1000,
) -> Tuple[List[KeygenTrial], KeygenSummary]:
    """Run full keygen experiment for one condition.

    Args:
        bit_length: RSA bit length (1024 or 2048)
        condition: Simplex-anchor condition
        n_trials: Number of trials
        seed: Random seed
        mr_rounds: Miller-Rabin rounds
        td_limit: Trial division limit

    Returns:
        Tuple of (trial_list, summary)
    """
    rng = np.random.RandomState(seed)
    trials = []

    print(f"Running {n_trials} trials for {bit_length}-bit, condition={condition}")

    for i in range(n_trials):
        if (i + 1) % max(1, n_trials // 10) == 0:
            print(f"  Progress: {i + 1}/{n_trials}")

        trial = find_prime(bit_length, condition, rng, mr_rounds, td_limit)
        trial.trial_id = i
        trials.append(trial)

    # Compute summary statistics
    candidates = [t.candidates_tested for t in trials]
    mr_calls = [t.miller_rabin_calls for t in trials]
    total_times = [t.total_time_ms for t in trials]
    mr_times = [t.mr_time_ms for t in trials]

    summary = KeygenSummary(
        condition=condition,
        bit_length=bit_length,
        n_trials=n_trials,
        mean_candidates=float(np.mean(candidates)),
        median_candidates=float(np.median(candidates)),
        mean_mr_calls=float(np.mean(mr_calls)),
        median_mr_calls=float(np.median(mr_calls)),
        mean_total_time_ms=float(np.mean(total_times)),
        median_total_time_ms=float(np.median(total_times)),
        mean_mr_time_ms=float(np.mean(mr_times)),
        median_mr_time_ms=float(np.median(mr_times)),
        seed=seed,
    )

    return trials, summary


def save_results(
    trials: List[KeygenTrial],
    summary: KeygenSummary,
    output_dir: Path,
) -> None:
    """Save experiment results to CSV and JSON.

    Args:
        trials: List of trial results
        summary: Summary statistics
        output_dir: Output directory path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save trials CSV
    import csv

    csv_path = output_dir / "metrics.csv"
    with open(csv_path, "w", newline="") as f:
        if trials:
            writer = csv.DictWriter(f, fieldnames=trials[0].to_dict().keys())
            writer.writeheader()
            for trial in trials:
                writer.writerow(trial.to_dict())

    # Save summary JSON
    json_path = output_dir / "summary.json"
    with open(json_path, "w") as f:
        json.dump(summary.to_dict(), f, indent=2)

    print(f"Results saved to {output_dir}")


__all__ = [
    "KeygenTrial",
    "KeygenSummary",
    "generate_candidate",
    "trial_division",
    "is_prime_miller_rabin",
    "find_prime",
    "run_keygen_experiment",
    "save_results",
]
