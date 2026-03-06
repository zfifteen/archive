#!/usr/bin/env python3
"""
Minimal smoke test for the Z5D prime estimator.

Replicates the whitepaper formula in pure Python and compares predictions
against the exact k-th prime for a few small indices. The goal is to get
a quick sanity check on the mathematics before investing in heavier tests.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List


# Calibration constants from the whitepaper / C reference implementation
DEFAULT_C = -0.00247
DEFAULT_K_STAR = 0.04449
E_FOURTH = math.e ** 4


@dataclass
class SmokeResult:
    index: int
    predicted: float
    actual: int

    @property
    def abs_error(self) -> float:
        return abs(self.predicted - self.actual)

    @property
    def rel_error(self) -> float:
        return self.abs_error / self.actual


def z5d_predict(k: int) -> float:
    """Pure-Python reproduction of the Z5D estimate for the k-th prime."""
    if k < 2:
        raise ValueError("k must be >= 2 for prime indexing")

    ln_k = math.log(k)
    ln_ln_k = math.log(ln_k)

    # Base PNT term (same as z5d_base_pnt_prime in C)
    pnt = k * (ln_k + ln_ln_k - 1.0 + (ln_ln_k - 2.0) / ln_k)

    ln_pnt = math.log(pnt)
    d_term = (ln_pnt / E_FOURTH) ** 2 if ln_pnt > 0 else 0.0
    e_term = pnt ** (-1.0 / 3.0)

    return pnt + DEFAULT_C * d_term * pnt + DEFAULT_K_STAR * e_term * pnt


def nth_prime(k: int) -> int:
    """Naive nth-prime calculation; good enough for small smoke tests."""
    if k < 1:
        raise ValueError("k must be >= 1")

    count = 0
    candidate = 1

    while count < k:
        candidate += 1
        if is_prime(candidate):
            count += 1
    return candidate


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    limit = int(math.isqrt(n))
    for factor in range(3, limit + 1, 2):
        if n % factor == 0:
            return False
    return True


def run_smoke(indices: Iterable[int]) -> List[SmokeResult]:
    results = []
    for idx in indices:
        predicted = z5d_predict(idx)
        actual = nth_prime(idx)
        results.append(SmokeResult(idx, predicted, actual))
    return results


def main() -> None:
    indices = [100, 1000, 10000]
    print("Z5D Smoke Test (whitepaper formula vs exact primes)")
    print(f"{'k':>8} {'predicted':>16} {'actual':>10} {'abs_err':>10} {'rel_err':>10}")
    for result in run_smoke(indices):
        print(
            f"{result.index:8d} "
            f"{result.predicted:16.2f} "
            f"{result.actual:10d} "
            f"{result.abs_error:10.2f} "
            f"{result.rel_error:10.4f}"
        )


if __name__ == "__main__":
    main()
