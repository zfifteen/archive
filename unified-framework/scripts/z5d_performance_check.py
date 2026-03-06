#!/usr/bin/env python3
"""
Empirical check of the Z5D prediction offset versus exact indexed primes.

The whitepaper claims the predicted value is typically within ±100 integers
of the true prime even at extreme indices. This script evaluates that claim
for moderate scales that are practical to verify locally.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Tuple

try:
    from sympy import prime as nth_prime
except ImportError as exc:
    raise SystemExit(
        "sympy is required for this script (pip install sympy)"
    ) from exc


SCALE_CALIBRATIONS: List[Tuple[float, float, float]] = [
    (1e6, -0.00247, 0.04449),
    (1e12, -0.00037, -0.11446),
    (1e18, -0.0001, -0.15),
    (float("inf"), -0.00002, -0.10),
]

E_FOURTH = math.e ** 4


@dataclass
class OffsetResult:
    index: int
    predicted: float
    actual: int

    @property
    def abs_value_offset(self) -> float:
        return abs(self.predicted - self.actual)

    @property
    def abs_rounded_offset(self) -> int:
        return abs(int(round(self.predicted)) - self.actual)

    @property
    def relative_error(self) -> float:
        return self.abs_value_offset / self.actual


def z5d_predict(k: int) -> float:
    """Reproduce the whitepaper Z5D estimate with scale-auto-calibration."""
    if k < 2:
        raise ValueError("k must be >= 2")

    c, k_star = _get_calibration(k)

    ln_k = math.log(k)
    ln_ln_k = math.log(ln_k)
    base_pnt = k * (ln_k + ln_ln_k - 1.0 + (ln_ln_k - 2.0) / ln_k)

    ln_base = math.log(base_pnt)
    d_term = (ln_base / E_FOURTH) ** 2 if ln_base > 0 else 0.0
    e_term = base_pnt ** (-1.0 / 3.0)

    return base_pnt + c * d_term * base_pnt + k_star * e_term * base_pnt


def _get_calibration(k: int) -> Tuple[float, float]:
    for limit, c, k_star in SCALE_CALIBRATIONS:
        if k <= limit:
            return c, k_star
    return SCALE_CALIBRATIONS[-1][1:]  # Fallback (should never hit)


def check_indices(indices: Iterable[int]) -> List[OffsetResult]:
    results: List[OffsetResult] = []
    for k in indices:
        predicted = z5d_predict(k)
        actual = int(nth_prime(k))
        results.append(OffsetResult(k, predicted, actual))
    return results


def main(args: Iterable[str] | None = None) -> None:
    if args:
        indices = [int(float(arg)) for arg in args]
    else:
        indices = [10**3, 10**4, 10**5, 10**6]
    print("Index | Predicted       | Actual          | |Δ| (value) | |Δ| (rounded) | RelErr")
    print("------|-----------------|-----------------|------------|---------------|--------")
    for result in check_indices(indices):
        print(
            f"{result.index:6d} | "
            f"{result.predicted:15.2f} | "
            f"{result.actual:15d} | "
            f"{result.abs_value_offset:10.2f} | "
            f"{result.abs_rounded_offset:13d} | "
            f"{result.relative_error:0.6f}"
        )


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
