#!/usr/bin/env python3
"""Benchmark script for lognormal factorization pipeline."""

import time
import random
from typing import List
from src.pipeline import factor_with_lognormal_prefilter, factor_classical
from src.model import ModelStore
from src.config import SearchPolicyConfig


def generate_test_semiprimes(count: int = 100) -> List[int]:
    """Generate small semiprimes for testing."""
    # Simple sieve for primes up to 10^4
    primes = []
    is_prime = [True] * 10001
    is_prime[0] = is_prime[1] = False
    for i in range(2, 10001):
        if is_prime[i]:
            primes.append(i)
            for j in range(i * i, 10001, i):
                is_prime[j] = False

    semiprimes = []
    for _ in range(count):
        p = random.choice(primes[100:])  # Avoid very small primes
        q = random.choice(primes[100:])
        semiprimes.append(p * q)
    return semiprimes


def benchmark():
    """Run benchmark comparing pipeline vs classical."""
    model = ModelStore()
    cfg = SearchPolicyConfig(
        max_steps=1000, radius_scale=1.0, direction_mode="ALTERNATE"
    )

    test_ns = generate_test_semiprimes(50)
    results = []

    for N in test_ns:
        # Pipeline
        start = time.time()
        cfg.seed = 42  # Set seed on config for reproducibility
        pipeline_factor = factor_with_lognormal_prefilter(N, model, cfg)
        pipeline_time = time.time() - start

        # Classical
        start = time.time()
        classical_factor = factor_classical(N)
        classical_time = time.time() - start

        # Verify
        if pipeline_factor and classical_factor:
            success = set([pipeline_factor, N // pipeline_factor]) == set(
                [classical_factor, N // classical_factor]
            )
        else:
            success = False

        results.append(
            {
                "N": N,
                "pipeline_time": pipeline_time,
                "classical_time": classical_time,
                "success": success,
            }
        )

    # Summary
    pipeline_total = sum(r["pipeline_time"] for r in results)
    classical_total = sum(r["classical_time"] for r in results)
    success_rate = sum(1 for r in results if r["success"]) / len(results)

    print(f"Total pipeline time: {pipeline_total:.4f}s")
    print(f"Total classical time: {classical_total:.4f}s")
    print(f"Speedup: {classical_total / pipeline_total:.2f}x")
    print(f"Success rate: {success_rate:.2%}")


if __name__ == "__main__":
    benchmark()
