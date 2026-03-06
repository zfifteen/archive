#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Z_5D Pascal Filter: Scalar Fast Path Implementation

Overview:
  This module implements a scalar fast-path filter for the Z_5D Pascal-Only Model (Stage -1/0/S).
  The filter identifies structural composites of the form p^m - 1 (p in P0, m >= 2) up to a specified limit.
  Primes are expected to pass the filter, while targeted structural composites are expected to fail.

Performance Metrics:
  - Timings measured in nanoseconds using time.perf_counter_ns().
  - Aggregate statistics: mean, p50, p90, p99.
  - No per-candidate allocations; uses Python set for O(1) amortized lookups.

Configuration:
  - P0: Initial prime set [3, 5, 7, 11, 13, 17, 19, 23, 29]
  - MAX_N_FOR_FORMS: 10^18 (upper limit for structural forms)
  - DEMO_MAX: 220 (demonstration range for evaluation)
"""

from __future__ import annotations

import time
import numpy as np
import sympy as sp
from typing import Iterable, Set, List, Tuple

# ------------------------------
# Configuration
# ------------------------------
MAX_N_FOR_FORMS = 10**18
DEMO_MAX = 10000000
P0 = np.array([3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=np.int64)

# Global structural set (p^m - 1) and overflow bases
_STRUCT_FORMS: Set[int] = set()
_OVERFLOW_PS: List[int] = []


# ------------------------------
# Utility Functions
# ------------------------------
def fmt_ns(ns: int) -> str:
    return f"{ns:8d} ns ({ns/1_000:7.3f} µs)"

def stats_ns(samples: List[int]) -> Tuple[float, float, float, float]:
    if not samples:
        return (0.0, 0.0, 0.0, 0.0)
    arr = np.fromiter(samples, dtype=np.int64, count=len(samples))
    mean = float(arr.mean())
    p50 = float(np.percentile(arr, 50))
    p90 = float(np.percentile(arr, 90))
    p99 = float(np.percentile(arr, 99))
    return (mean, p50, p90, p99)


# ------------------------------
# Structural Forms Construction
# ------------------------------
def build_structural_forms(P: np.ndarray, limit: int) -> Set[int]:
    """
    Constructs the set {p^m - 1 : p in P (>=3), m >= 2} with values <= limit.
    Uses Python integers for arbitrary precision.
    Collects bases that overflow the limit for reporting.
    """
    struct: Set[int] = set()
    overflow_bases: List[int] = []

    for p in map(int, P[P >= 3]):
        pm = p * p  # Start at p^2 (m=2)
        while pm - 1 <= limit:
            struct.add(pm - 1)
            if pm > limit // p:  # Next multiplication would exceed limit
                overflow_bases.append(p)
                break
            pm *= p
        else:
            overflow_bases.append(p)  # Overflow beyond limit without break

    global _OVERFLOW_PS
    _OVERFLOW_PS = sorted(set(overflow_bases))
    return struct


# ------------------------------
# Scalar Filter Function
# ------------------------------
def z5d_pascal_filter_scalar(n: int) -> bool:
    """
    Scalar fast-path filter.
    Returns True if the candidate passes (potential prime), False if it fails (structural composite).
    """
    return n not in _STRUCT_FORMS


# ------------------------------
# Evaluation Setup
# ------------------------------
def setup_evaluation():
    global _STRUCT_FORMS
    _STRUCT_FORMS = build_structural_forms(P0, MAX_N_FOR_FORMS)


# ------------------------------
# Evaluation Procedure
# ------------------------------
def run_evaluation():
    print("Z_5D Pascal Filter: Scalar Fast Path Performance Evaluation")
    print(f"Configuration: P0 = {list(P0)}, MAX_N_FOR_FORMS = {MAX_N_FOR_FORMS:.0e}, DEMO_MAX = {DEMO_MAX}")
    print("Metrics: Per-candidate timings in nanoseconds; aggregate statistics (mean, p50, p90, p99).")
    print("")

    setup_evaluation()
    print(f"Structural forms constructed: {len(_STRUCT_FORMS)} entries.")

    # Prepare evaluation sets
    primes = list(sp.primerange(2, DEMO_MAX))
    structural = sorted(x for x in _STRUCT_FORMS if 4 <= x < DEMO_MAX)

    # Warm-up to minimize measurement artifacts
    _ = z5d_pascal_filter_scalar(2)

    # Evaluate prime candidates
    print("\nPrime Candidate Evaluation Results")
    print("-" * 60)
    print(f"{'Candidate':>10} | {'Expected':^8} | {'Actual':^6} | {'Time':^20}")
    print("-" * 60)
    prime_times_ns: List[int] = []
    all_pass = True
    for n in primes:
        t0 = time.perf_counter_ns()
        result = z5d_pascal_filter_scalar(n)
        dt = time.perf_counter_ns() - t0
        prime_times_ns.append(dt)
        actual = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"{n:>10} | {'PASS':^8} | {actual:^6} | {fmt_ns(dt)}")
    print("-" * 60)

    assert all_pass, "Validation failed: One or more primes were incorrectly filtered."

    # Evaluate structural composites
    print("\nStructural Composite Evaluation Results")
    print("-" * 60)
    print(f"{'Candidate':>10} | {'Expected':^8} | {'Actual':^6} | {'Time':^20}")
    print("-" * 60)
    struct_times_ns: List[int] = []
    all_fail = True
    for n in structural:
        t0 = time.perf_counter_ns()
        result = z5d_pascal_filter_scalar(n)
        dt = time.perf_counter_ns() - t0
        struct_times_ns.append(dt)
        actual = "PASS" if result else "FAIL"
        if result:
            all_fail = False
        print(f"{n:>10} | {'FAIL':^8} | {actual:^6} | {fmt_ns(dt)}")
    print("-" * 60)

    if structural:
        assert all_fail, "Validation failed: One or more structural composites incorrectly passed."

    # Aggregate timing statistics
    pm, p50, p90, p99 = stats_ns(prime_times_ns)
    sm, s50, s90, s99 = stats_ns(struct_times_ns)

    print("\nAggregate Timing Statistics (ns)")
    print("-" * 60)
    print(f"{'Category':<15} | {'N':>5} | {'Mean':>9} | {'P50':>9} | {'P90':>9} | {'P99':>9}")
    print("-" * 60)
    print(f"{'Primes':<15} | {len(prime_times_ns):>5} | {pm:>9.1f} | {p50:>9.1f} | {p90:>9.1f} | {p99:>9.1f}")
    print(f"{'Struct. Comp.':<15} | {len(struct_times_ns):>5} | {sm:>9.1f} | {s50:>9.1f} | {s90:>9.1f} | {s99:>9.1f}")
    print("-" * 60)

    # Overflow report
    if _OVERFLOW_PS:
        print("\nOverflow Report")
        print("-" * 60)
        print("Bases where p^m - 1 exceeded the construction limit:")
        print(", ".join(str(p) for p in _OVERFLOW_PS))
        print(f"Limit: {MAX_N_FOR_FORMS:.0e}")
        print("-" * 60)


def main():
    run_evaluation()


if __name__ == "__main__":
    main()