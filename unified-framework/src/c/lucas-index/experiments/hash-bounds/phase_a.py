#!/usr/bin/env python3
"""
LIS Phase A — Micro‑Efficiency Validation (Proof of Concept)

Runs LIS Corrector (Z5D seed + LIS + MR) over log‑spaced bands of n to
estimate the MR‑call reduction vs a wheel‑210 baseline. Outputs per‑band
means with 95% bootstrap CIs and a pooled headline.

Default settings follow the Phase A plan (10k per band). You can reduce
samples via CLI flags for quick dry‑runs.
"""
from __future__ import annotations

import argparse
import random
import statistics as stats
import time
from typing import Iterable, List, Tuple

# Try local import first; fall back to adding script dir to sys.path
try:
    from lis_corrector import lis_correct_nth_prime  # type: ignore
except Exception:
    import os, sys
    _HERE = os.path.dirname(os.path.abspath(__file__))
    # Also try repo-level experiments/hash-bounds alongside this nested copy
    _ALT = os.path.abspath(os.path.join(_HERE, '..', '..', '..', '..', '..', 'experiments', 'hash-bounds'))
    for p in (_HERE, _ALT):
        if p not in sys.path:
            sys.path.insert(0, p)
    from lis_corrector import lis_correct_nth_prime  # type: ignore


Band = Tuple[int, int, str]  # (start_inclusive, end_inclusive, label)


def bands_default() -> List[Band]:
    return [
        (10**3, 10**4, "small"),
        (10**4, 10**5, "medium-1"),
        (10**5, 10**6, "medium-2"),
        (10**6, 10**7, "large-1"),
        (10**7, 10**8, "large-2"),
    ]


def bootstrap_ci_mean(values: List[float], resamples: int = 5000, alpha: float = 0.05) -> Tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    n = len(values)
    means: List[float] = []
    for _ in range(resamples):
        sample = [values[random.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lower = means[int((alpha / 2) * resamples)]
    upper = means[int((1 - alpha / 2) * resamples) - 1]
    return lower, upper


def _auto_window_for_band(start: int, end: int) -> int:
    if start == 10**3 and end == 10**4:
        return 5_000
    if start == 10**4 and end == 10**5:
        return 5_000
    if start == 10**5 and end == 10**6:
        return 10_000
    if start == 10**6 and end == 10**7:
        return 100_000
    if start == 10**7 and end == 10**8:
        return 1_000_000
    raise RuntimeError(f"No fixed window configured for band [{start}, {end}].")


def run_band(start: int, end: int, samples: int, window: int, seed: int | None = None) -> Tuple[List[float], int]:
    if seed is not None:
        random.seed(seed)
    reductions: List[float] = []
    failures = 0
    for _ in range(samples):
        n = random.randint(start, end)
        try:
            use_win = window if window > 0 else _auto_window_for_band(start, end)
            _p, mr, base = lis_correct_nth_prime(n, window=use_win)
            if base <= 0:
                continue
            red = 1.0 - (mr / base)
            reductions.append(red)
        except Exception:
            failures += 1
            continue
    return reductions, failures


def format_pct(x: float) -> str:
    return f"{x*100:.2f}%"


def main() -> int:
    ap = argparse.ArgumentParser(description="LIS Phase A — Micro‑Efficiency Validation (PoC)")
    ap.add_argument("--samples-per-band", type=int, default=10000, help="number of n per band (default: 10000)")
    ap.add_argument("--window", type=int, default=0, help="fixed correction window; 0 = use fixed per-band windows (no fallback)")
    ap.add_argument("--resamples", type=int, default=5000, help="bootstrap resamples for 95% CI (default: 5000)")
    ap.add_argument("--seed", type=int, default=12345, help="random seed (default: 12345)")
    args = ap.parse_args()

    bands = bands_default()
    overall: List[float] = []
    t0 = time.time()

    print("LIS Phase A — Proof of Concept")
    print(f"Samples per band: {args.samples_per_band}")
    print(f"Window: {args.window}")
    print(f"Bootstrap resamples: {args.resamples}")
    print("")

    for (bstart, bend, label) in bands:
        print(f"Band: {label} [{bstart}, {bend}]")
        bt0 = time.time()
        reds, fails = run_band(bstart, bend, args.samples_per_band, args.window, seed=args.seed)
        bt1 = time.time()
        if not reds:
            print("  No usable samples (all failures)")
            print("")
            continue
        mean_red = sum(reds) / len(reds)
        ci_lo, ci_hi = bootstrap_ci_mean(reds, resamples=args.resamples)
        overall.extend(reds)
        dur = bt1 - bt0
        print(f"  Samples: {len(reds)} (failures: {fails})")
        print(f"  Mean MR-call reduction vs baseline: {format_pct(mean_red)} (95% CI {format_pct(ci_lo)}..{format_pct(ci_hi)})")
        print(f"  Time: {dur:.2f}s  ({len(reds)/dur:.1f} n/sec)")
        print("")

    if overall:
        mean_all = sum(overall) / len(overall)
        lo_all, hi_all = bootstrap_ci_mean(overall, resamples=args.resamples)
        print("Pooled")
        print(f"  Mean MR-call reduction vs baseline: {format_pct(mean_all)} (95% CI {format_pct(lo_all)}..{format_pct(hi_all)})")
    t1 = time.time()
    print("")
    print(f"Completed Phase A in {t1 - t0:.2f}s  ({len(overall)/(t1 - t0):.1f} n/sec pooled)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
