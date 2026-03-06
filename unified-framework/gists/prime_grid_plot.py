#!/usr/bin/env python3
"""
Prime Grid Plotter — arbitrary scales (e.g., "10^6", up to ~10^1234)

This script plots points (x, y) where N = x * 10^m + y is prime, for a given base 10^m.
It supports extremely large m using arbitrary-precision integers and probabilistic
primality tests (gmpy2 if available, otherwise Miller–Rabin with configurable rounds).
It is designed to *sample* the y-range for huge scales so plots remain feasible.

Key features
------------
- Scale via --scale "10^m" (e.g., "10^6") or --m 6
- Arbitrary-precision ints for N = x*10^m + y
- gmpy2.is_prime if available; else Miller–Rabin (configurable --mr-rounds)
- Two y traversal modes:
  * stepped: iterate y from y-start to y-end by y-step
  * random probes: pick --probes random y in [y-start, y-end]
- Optional composite overlay (to visualize "corridors" vs "deserts"):
  --composites none|sample|all  (default: none)
  --composite-sample N          (how many random composite points to draw if sampling)
- Saves both image and (optional) CSV
- Integer-only axis ticks for clean presentation

Examples
--------
# Dense sample at moderate scale
python prime_grid_plot.py --scale "10^6" --x-start 1 --x-end 5 \
    --y-start 0 --y-end 20000 --y-step 1 \
    --out-img grid_1e6.png --out-csv grid_1e6.csv

# Larger scale with random probes
python prime_grid_plot.py --scale "10^9" --x-start 1 --x-end 3 \
    --y-start 0 --y-end 1000000 --probes 20000 \
    --out-img grid_1e9.png

# Ultra extreme (plot will be sparse; keep probes modest)
python prime_grid_plot.py --scale "10^1234" --x-start 1 --x-end 2 \
    --y-start 0 --y-end 1000000000000 --probes 5000 \
    --mr-rounds 24 --out-img grid_1e1234.png
"""

import argparse
import math
import os
import random
from typing import Iterable, Tuple, List, Optional

try:
    import gmpy2
    HAVE_GMPY2 = True
except Exception:
    HAVE_GMPY2 = False

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import csv

# -----------------------------
# Utilities
# -----------------------------

def parse_scale(scale: Optional[str], m: Optional[int]) -> int:
    """
    Parse a scale like "10^6" or accept --m directly.
    Returns m (the exponent).
    """
    if m is not None:
        if m < 0:
            raise ValueError("--m must be non-negative")
        return m
    if not scale:
        raise ValueError("Provide --scale like '10^6' or --m <int>")
    s = scale.strip().lower().replace(" ", "")
    if s.startswith("10^"):
        try:
            return int(s[3:])
        except Exception:
            raise ValueError(f"Could not parse exponent from scale='{scale}'")
    # Accept raw integer like "6"
    try:
        return int(s)
    except Exception:
        raise ValueError(f"Unrecognized scale format: {scale}. Use '10^6' or provide --m.")

# -----------------------------
# Primality
# -----------------------------

def mr_is_probable_prime(n: int, rounds: int = 16, rng: Optional[random.Random] = None) -> bool:
    """
    Miller–Rabin probabilistic primality test for arbitrary-size n.
    Returns True if n is probably prime.
    """
    if n < 2:
        return False
    # small primes quick check
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # write n-1 as d * 2^s with d odd
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    if rng is None:
        rng = random

    # Random bases in [2, n-2]
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        skip = False
        for _r in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                skip = True
                break
        if skip:
            continue
        return False
    return True

def is_probable_prime(n: int, mr_rounds: int, rng: Optional[random.Random]) -> bool:
    if HAVE_GMPY2:
        # gmpy2.is_prime: 0=composite, 1=probably prime, 2=definitely prime (for small n)
        return gmpy2.is_prime(n) > 0
    return mr_is_probable_prime(n, rounds=mr_rounds, rng=rng)

# -----------------------------
# Traversal over (x, y)
# -----------------------------

def y_iterators(y_start: int, y_end: int, y_step: int, probes: int, rng: random.Random):
    """
    Yield y candidates by either stepped iteration or random sampling.
    - If probes > 0: return 'probes' uniformly random y in [y_start, y_end], unique.
    - Else: stepped from y_start to y_end inclusive by y_step.
    """
    if probes and probes > 0:
        span = y_end - y_start + 1
        if probes >= span:
            # Degenerate: just return full stepped range
            for y in range(y_start, y_end + 1, max(1, y_step)):
                yield y
        else:
            # Sample without replacement for stable visuals
            ys = rng.sample(range(y_start, y_end + 1), probes)
            ys.sort()
            for y in ys:
                yield y
    else:
        for y in range(y_start, y_end + 1, max(1, y_step)):
            yield y

# -----------------------------
# Composite overlay helpers
# -----------------------------

def choose_composite_points(all_points: List[Tuple[int,int,bool]], mode: str, sample_n: int, rng: random.Random) -> List[Tuple[int,int]]:
    """
    From the scanned points, pick composite positions to overlay.
    mode: 'none'|'sample'|'all'
    """
    if mode == "none":
        return []
    comps = [(x,y) for (x,y,is_p) in all_points if not is_p]
    if mode == "all":
        return comps
    # sample
    if len(comps) <= sample_n:
        return comps
    return rng.sample(comps, sample_n)

# -----------------------------
# Main plotting
# -----------------------------

def run_plot(m: int,
             x_start: int, x_end: int,
             y_start: int, y_end: int,
             y_step: int, probes: int,
             mr_rounds: int, seed: Optional[int],
             out_img: str, out_csv: Optional[str],
             composites: str, composite_sample: int):
    assert x_start <= x_end, "x-start must be <= x-end"
    assert y_start <= y_end, "y-start must be <= y-end"
    assert composites in ("none", "sample", "all"), "--composites must be none|sample|all"

    rng = random.Random(seed) if seed is not None else random

    # Collect results: (x, y, is_prime)
    results: List[Tuple[int,int,bool]] = []

    pow10m = pow(10, m)  # arbitrary-precision
    for x in range(x_start, x_end + 1):
        base = x * pow10m
        for y in y_iterators(y_start, y_end, y_step, probes, rng):
            N = base + y
            is_p = is_probable_prime(N, mr_rounds=mr_rounds, rng=rng if not HAVE_GMPY2 else None)
            results.append((x, y, is_p))

    # CSV (optional)
    if out_csv:
        with open(out_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["x", "y", "N", "is_prime"])
            for (x,y,is_p) in results:
                # Save N exactly; for enormous N, this is still fine as text
                N = x * pow10m + y
                w.writerow([x, y, str(N), int(is_p)])

    # Split for plotting
    primes_xy = [(x,y) for (x,y,is_p) in results if is_p]
    comp_xy = choose_composite_points(results, composites, composite_sample, rng)

    # Plot
    import numpy as np
    P = np.array(primes_xy) if primes_xy else np.empty((0,2))
    C = np.array(comp_xy) if comp_xy else np.empty((0,2))

    fig, ax = plt.subplots(figsize=(8, 6))
    if len(C) > 0:
        ax.scatter(C[:,0], C[:,1], s=2, alpha=0.08)
    if len(P) > 0:
        ax.scatter(P[:,0], P[:,1], s=6)
    ax.set_title(f"Prime Grid — base 10^{m}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    # Force integer-only ticks
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.tight_layout()
    fig.savefig(out_img, dpi=170)
    plt.close(fig)

    # Return quick stats
    return {
        "points_scanned": len(results),
        "primes_found": len(primes_xy),
        "composites_plotted": len(comp_xy),
        "out_img": out_img,
        "out_csv": out_csv,
        "gmpy2": HAVE_GMPY2,
    }

# -----------------------------
# CLI
# -----------------------------

def main():
    ap = argparse.ArgumentParser(description="Plot (x,y) where N = x*10^m + y is prime, at arbitrary scale.")
    ap.add_argument("--scale", type=str, default=None, help="Scale like '10^6' or raw exponent '6'.")
    ap.add_argument("--m", type=int, default=None, help="Exponent m (alternative to --scale).")
    ap.add_argument("--x-start", type=int, required=True, help="Start x (inclusive).")
    ap.add_argument("--x-end", type=int, required=True, help="End x (inclusive).")
    ap.add_argument("--y-start", type=int, required=True, help="Start y (inclusive).")
    ap.add_argument("--y-end", type=int, required=True, help="End y (inclusive).")
    ap.add_argument("--y-step", type=int, default=1, help="Step for y traversal (ignored if --probes > 0).")
    ap.add_argument("--probes", type=int, default=0, help="Random probes in [y-start, y-end] (0 = disabled).")
    ap.add_argument("--mr-rounds", type=int, default=16, help="MR rounds if gmpy2 not available.")
    ap.add_argument("--seed", type=int, default=None, help="Random seed (reproducible probes).")
    ap.add_argument("--out-img", type=str, required=True, help="Output image path (PNG).")
    ap.add_argument("--out-csv", type=str, default=None, help="Optional CSV path (stores x,y,N,is_prime).")
    ap.add_argument("--composites", type=str, default="none", choices=["none","sample","all"],
                    help="Composite overlay mode.")
    ap.add_argument("--composite-sample", type=int, default=10000,
                    help="How many composite points to draw when --composites=sample.")

    args = ap.parse_args()
    m = parse_scale(args.scale, args.m)

    stats = run_plot(
        m=m,
        x_start=args.x_start, x_end=args.x_end,
        y_start=args.y_start, y_end=args.y_end,
        y_step=args.y_step, probes=args.probes,
        mr_rounds=args.mr_rounds, seed=args.seed,
        out_img=args.out_img, out_csv=args.out_csv,
        composites=args.composites, composite_sample=args.composite_sample
    )

    print("Done.")
    for k,v in stats.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
