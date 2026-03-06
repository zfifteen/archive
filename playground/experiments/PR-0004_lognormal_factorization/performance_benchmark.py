#!/usr/bin/env python3
"""Performance benchmark for lognormal factorization pipeline on fitted bands."""

import time
import random
from typing import List
from src.pipeline import factor_with_lognormal_prefilter, factor_classical
from src.model import ModelStore, Band
from src.config import SearchPolicyConfig


def segmented_sieve(limit: int, segment_size: int = 10**6) -> List[int]:
    """Generate primes up to limit using memory-efficient segmented sieve."""
    if limit < 2:
        return []

    # Step 1: Get small primes up to sqrt(limit)
    sqrt_limit = int(limit**0.5) + 1
    small_primes = sieve_of_eratosthenes(sqrt_limit)

    # Step 2: Initialize result with small primes
    result = list(small_primes)

    # Step 3: Process segments from sqrt(limit) to limit
    low_start = int(
        sqrt_limit if sqrt_limit > small_primes[-1] else small_primes[-1] + 1
    )

    for low in range(low_start, limit + 1, segment_size):
        high = min(low + segment_size, limit + 1)
        segment = [True] * (high - low)

        # Mark composites using small primes
        for p in small_primes:
            if p * p > high:
                break

            # Find first multiple of p in segment
            start = ((low + p - 1) // p) * p

            # Mark all multiples as composite
            for j in range(max(start, low), high, p):
                segment[j - low] = False

        # Extract primes from segment
        segment_primes = [low + i for i in range(len(segment)) if segment[i]]
        result.extend(segment_primes)

    return [p for p in result if p <= limit]


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """Basic Sieve of Eratosthenes for small primes."""
    if limit < 2:
        return []

    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False

    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False

    return [i for i in range(2, limit + 1) if sieve[i]]


def generate_primes_in_range(min_p: int, max_p: int, count: int) -> List[int]:
    """Generate primes in [min_p, max_p) using segmented sieve."""
    all_primes = segmented_sieve(max_p - 1)
    primes_in_range = [p for p in all_primes if min_p <= p < max_p]
    return primes_in_range[:count]


def generate_test_semiprimes(band: Band, count: int) -> List[int]:
    """Generate semiprimes with p,q in band's range."""
    min_p = band.p_min
    max_p = band.p_max
    primes = generate_primes_in_range(min_p, max_p, count * 2)
    semiprimes = []
    for i in range(0, len(primes) - 1, 2):
        p = primes[i]
        q = primes[i + 1]
        semiprimes.append(p * q)
        if len(semiprimes) >= count:
            break
    return semiprimes


def performance_benchmark():
    """Benchmark on semiprimes in fitted bands."""
    model = ModelStore()
    cfg = SearchPolicyConfig(
        max_steps=10000, radius_scale=1.0, direction_mode="ALTERNATE"
    )

    results = []

    for band_idx, band in enumerate(model.bands):
        print(f"Benchmarking band {band_idx + 1}: {band.p_min}-{band.p_max}")
        test_ns = generate_test_semiprimes(
            band, 1
        )  # 1 semiprime per band for timing stats

        for N in test_ns:
            # Set seed for reproducibility
            cfg.seed = random.randint(0, 1000000)
            cfg.__post_init__()  # Re-init rng

            # Pipeline
            start = time.time()
            pipeline_factor = factor_with_lognormal_prefilter(N, model, cfg)
            pipeline_time = time.time() - start

            # Classical
            start = time.time()
            classical_factor = factor_classical(N)
            classical_time = time.time() - start

            # Verify
            if pipeline_factor and classical_factor:
                factors = {pipeline_factor, N // pipeline_factor}
                classical_factors = {classical_factor, N // classical_factor}
                success = factors == classical_factors
            else:
                success = False

            results.append(
                {
                    "band": band_idx + 1,
                    "N": N,
                    "pipeline_time": pipeline_time,
                    "classical_time": classical_time,
                    "success": success,
                    "speedup": classical_time / pipeline_time
                    if pipeline_time > 0
                    else 0,
                }
            )

    # Summary per band
    for band_idx in range(1, len(model.bands) + 1):
        band_results = [r for r in results if r["band"] == band_idx]
        if band_results:
            avg_pipeline = sum(r["pipeline_time"] for r in band_results) / len(
                band_results
            )
            avg_classical = sum(r["classical_time"] for r in band_results) / len(
                band_results
            )
            avg_speedup = sum(r["speedup"] for r in band_results) / len(band_results)
            success_rate = sum(1 for r in band_results if r["success"]) / len(
                band_results
            )
            print(
                f"Band {band_idx}: Avg pipeline {avg_pipeline:.4f}s, classical {avg_classical:.4f}s, speedup {avg_speedup:.2f}x, success {success_rate:.0%}"
            )


if __name__ == "__main__":
    performance_benchmark()
