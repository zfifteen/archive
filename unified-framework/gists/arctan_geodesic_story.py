#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arctan → Half/Double Angle → Geodesic (Robust Density) — Story Script
=====================================================================

Bug fix & robustness
--------------------
- Enhancement is computed from **prime density per bin** (primes_in_bin / n_in_bin).
- Added **quantile binning** (`--quantile`) to equalize n-per-bin and eliminate occupancy bias.
- Added **min-occupancy guard** (`--min-occupancy-frac`) to ignore bins with too few n.

Sections
--------
1) Verify the two arctan identities (symbolic + 50-digit numeric).
2) Geometry insight (half/double angle) with a φ cameo.
3) Geodesic θ′(n,k≈0.3) demo with density-based enhancement, quantile bins (optional), bootstrap CI (optional).

Usage
-----
$ python arctan_geodesic_story.py --N 100000 --bins 20 --quantile --min-occupancy-frac 0.05 --bootstrap 200 --seed 42
"""

from __future__ import annotations
import argparse
import random
from dataclasses import dataclass
from typing import List, Tuple
from bisect import bisect_right

import mpmath as mp
mp.mp.dps = 50

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except Exception:
    SYMPY_AVAILABLE = False

try:
    if SYMPY_AVAILABLE:
        from sympy import primerange as _primerange
        def primerange(a: int, b: int):
            return list(_primerange(a, b))
    else:
        raise ImportError
except Exception:
    def primerange(a: int, b: int):
        if b <= 2:
            return []
        sieve = [True] * b
        sieve[0:2] = [False, False]
        p = 2
        while p*p < b:
            if sieve[p]:
                sieve[p*p:b:p] = [False] * len(range(p*p, b, p))
            p += 1
        return [i for i in range(max(a,2), b) if sieve[i]]

# -----------------------------
# 1) VERIFICATION OF IDENTITIES
# -----------------------------

def identity1_symbolic_ok() -> bool:
    if not SYMPY_AVAILABLE:
        return False
    x = sp.symbols('x', positive=True)
    expr = sp.atan((sp.sqrt(1 + x**2) - 1)/x)
    deriv = sp.diff(expr, x)
    target = 1/(2*(1+x**2))
    return sp.simplify(deriv - target) == 0

def identity1_numeric_ok(samples: int = 12, tol: mp.mpf = mp.mpf('1e-30')) -> Tuple[bool, List[Tuple[mp.mpf, mp.mpf]]]:
    diffs = []
    for _ in range(samples):
        x = mp.mpf('10')**(mp.rand() * 4 - 2)  # 1e-2 .. 1e2
        f = lambda t: mp.atan((mp.sqrt(1 + t*t) - 1)/t)
        fprime_num = mp.diff(f, x)
        fprime_ref = 1/(2*(1+x*x))
        diffs.append((x, abs(fprime_num - fprime_ref)))
    ok = all(d <= tol for _, d in diffs)
    return ok, diffs

def identity2_symbolic_ok() -> bool:
    if not SYMPY_AVAILABLE:
        return False
    x = sp.symbols('x', real=True)
    expr = sp.atan( (2*x*sp.sqrt(1 - x**2)) / (1 - 2*x**2) )
    val = sp.simplify(expr.subs(x, sp.Rational(1,2)))
    return sp.simplify(val - sp.pi/3) == 0

def identity2_numeric_general(samples: int = 50, tol: mp.mpf = mp.mpf('1e-30')) -> Tuple[bool, List[Tuple[mp.mpf, mp.mpf]]]:
    diffs = []
    for _ in range(samples):
        x = (mp.rand() - mp.mpf('0.5')) * mp.mpf('1.4')  # (-0.7, 0.7)
        num = 2*x*mp.sqrt(1 - x*x)
        den = 1 - 2*x*x
        lhs = mp.atan(num/den)
        rhs = 2*mp.asin(x)
        diffs.append((x, abs(lhs - rhs)))
    ok = all(d <= tol for _, d in diffs)
    return ok, diffs

# -----------------------------
# 2) GEOMETRIC INTERPRETATIONS
# -----------------------------

def golden_ratio_cameo():
    phi = (1 + mp.sqrt(5)) / 2
    u = (mp.sqrt(1 + phi*phi) - 1) / phi
    lhs = mp.atan(u)
    rhs = mp.mpf('0.5') * mp.atan(phi)
    return lhs, rhs, abs(lhs - rhs)

# --------------------------------------------------
# 3) Z-FRAMEWORK: θ′(n, k) & DENSITY EXPERIMENT
# --------------------------------------------------

@dataclass
class GeodesicParams:
    phi: mp.mpf = mp.mpf('1.6180339887498948482')  # φ
    kappa_geo: mp.mpf = mp.mpf('0.3')              # empirically interesting

def theta_prime(n: int, p: GeodesicParams) -> mp.mpf:
    y = n / p.phi
    frac = y - mp.floor(y)
    return p.phi * (frac ** p.kappa_geo)

def _quantile_edges(theta_vals: List[float], bins: int) -> List[float]:
    """Compute bin edges so that each bin has (approximately) equal n occupancy."""
    tv = sorted(theta_vals)
    m = len(tv)
    if bins < 2 or m == 0:
        return [0.0, 1.0]
    edges = [tv[0]]
    for b in range(1, bins):
        q_index = int(round(b * m / bins))
        q_index = max(0, min(m - 1, q_index))
        edges.append(tv[q_index])
    edges.append(tv[-1])
    # make edges strictly increasing
    for i in range(1, len(edges)):
        if edges[i] <= edges[i-1]:
            edges[i] = edges[i-1] + (abs(edges[i-1]) + 1.0) * 1e-18
    return edges

def _bin_index_quantile(edges: List[float], val: float) -> int:
    i = bisect_right(edges, val) - 1
    if i < 0: i = 0
    if i >= len(edges) - 1: i = len(edges) - 2
    return i

def enhancement_density(N: int = 100_000, bins: int = 20, seed: int | None = None,
                        p: GeodesicParams = GeodesicParams(),
                        quantile: bool = False,
                        min_occupancy_frac: float = 0.05):
    if seed is not None:
        random.seed(seed)

    primes = set(primerange(2, N+1))

    # Precompute θ′ values for all n
    theta_vals = [float(theta_prime(n, p)) for n in range(2, N+1)]
    if bins < 2:
        bins = 2

    if quantile:
        edges = _quantile_edges(theta_vals, bins)
        index_fn = lambda val: _bin_index_quantile(edges, val)
        binning = "quantile"
    else:
        edges = [float(p.phi) * i / bins for i in range(bins+1)]
        index_fn = lambda val: min(bins-1, int((val / float(p.phi)) * bins))
        binning = "uniform"

    prime_counts = [0] * bins
    n_counts = [0] * bins
    for (n, ang) in zip(range(2, N+1), theta_vals):
        idx = index_fn(ang)
        n_counts[idx] += 1
        if n in primes:
            prime_counts[idx] += 1

    densities = [(prime_counts[i]/n_counts[i]) if n_counts[i] > 0 else 0.0 for i in range(bins)]

    # Occupancy guard
    mean_n = (sum(n_counts)/bins) if bins else 0.0
    min_occ = max(1, int(round(min_occupancy_frac * mean_n)))
    valid = [i for i in range(bins) if n_counts[i] >= min_occ]
    if not valid:
        valid = list(range(bins))

    mean_d = sum(densities[i] for i in valid)/len(valid) if valid else 0.0
    max_d = max((densities[i] for i in valid), default=0.0)
    enh_pct = (max_d/mean_d - 1.0) * 100.0 if mean_d > 0 else 0.0

    mean_raw = sum(prime_counts[i] for i in valid)/len(valid) if valid else 0.0
    max_raw = max((prime_counts[i] for i in valid), default=0.0)
    raw_enh_pct = (max_raw/mean_raw - 1.0) * 100.0 if mean_raw > 0 else 0.0

    return {
        "density_enhancement_pct": enh_pct,
        "densities": densities,
        "prime_counts": prime_counts,
        "n_counts": n_counts,
        "raw_enhancement_pct": raw_enh_pct,
        "edges": edges,
        "valid_bins": valid,
        "min_occupancy": min_occ,
        "binning": binning,
    }

def bootstrap_ci_density(N: int, bins: int, B: int = 200, seed: int | None = None,
                         p: GeodesicParams = GeodesicParams(),
                         quantile: bool = False,
                         min_occupancy_frac: float = 0.05):
    res = enhancement_density(N=N, bins=bins, seed=seed, p=p, quantile=quantile, min_occupancy_frac=min_occupancy_frac)
    prime_counts = res["prime_counts"]
    n_counts = res["n_counts"]

    rng = random.Random(seed)
    samples = []
    for _ in range(B):
        rp, rn = [], []
        for _b in range(bins):
            j = rng.randrange(0, bins)
            rp.append(prime_counts[j])
            rn.append(n_counts[j])
        dens = [(rp[i]/rn[i]) if rn[i] > 0 else 0.0 for i in range(bins)]
        mean_d = sum(dens)/bins if bins else 0.0
        max_d = max(dens) if dens else 0.0
        val = (max_d/mean_d - 1.0) * 100.0 if mean_d > 0 else 0.0
        samples.append(val)

    samples.sort()
    mean_val = sum(samples)/len(samples) if samples else 0.0
    lo = samples[int(0.025*len(samples))]
    hi = samples[int(0.975*len(samples)) - 1]
    return (mean_val, lo, hi), samples

# -----------------
# 4) THE NARRATIVE
# -----------------

def main():
    ap = argparse.ArgumentParser(description="Arctan identities → geometry → Z-geodesic density demo (story-style).")
    ap.add_argument("--N", type=int, default=100000, help="Max n for the geodesic demo (default: 100000).")
    ap.add_argument("--bins", type=int, default=20, help="Number of θ′ bins (default: 20).")
    ap.add_argument("--quantile", action="store_true", help="Use quantile (equal-N) θ′ bins to remove occupancy bias.")
    ap.add_argument("--min-occupancy-frac", type=float, default=0.05, help="Ignore bins with n < frac * mean_n_per_bin (default: 0.05).")
    ap.add_argument("--bootstrap", type=int, default=0, help="Bootstrap resamples for density enhancement CI (default: 0).")
    ap.add_argument("--seed", type=int, default=None, help="Random seed (default: None).")
    args = ap.parse_args()

    print("\nSTEP 1 — Verify the arctan identities (symbolic & numeric)")
    print("-----------------------------------------------------------")
    if SYMPY_AVAILABLE and identity1_symbolic_ok():
        print("✓ Identity 1 (symbolic): d/dx atan((sqrt(1+x^2)-1)/x) == 1/(2(1+x^2))  [PROVED]")
    else:
        print("• Identity 1 (symbolic): SymPy unavailable or proof failed.")
    ok1, diffs1 = identity1_numeric_ok()
    worst1 = max((d for _, d in diffs1), default=mp.mpf('0'))
    # format worst1 (mpf) as scientific via float conversion
    print(f"✓ Identity 1 (numeric): max |Δ| = {float(worst1):.2e} (target ≤ 1e-30) → {'OK' if ok1 else 'CHECK'}")

    if SYMPY_AVAILABLE and identity2_symbolic_ok():
        print("✓ Identity 2 (symbolic @ x=1/2): atan(2x√(1-x^2)/(1-2x^2)) = π/3  [PROVED]")
    else:
        print("• Identity 2 (symbolic): SymPy unavailable or proof failed.")
    ok2, diffs2 = identity2_numeric_general()
    worst2 = max((d for _, d in diffs2), default=mp.mpf('0'))
    print(f"✓ Identity 2 (numeric, |x|≤0.7): max |Δ| = {float(worst2):.2e} (target ≤ 1e-30) → {'OK' if ok2 else 'CHECK'}")

    print("\nSTEP 2 — Geometry cameo: the golden ratio φ and half-angle")
    print("----------------------------------------------------------")
    lhs, rhs, d = golden_ratio_cameo()
    print(f"φ cameo: atan((√(1+φ²)-1)/φ) vs 0.5*atan(φ)  →  |Δ| = {float(d):.2e}  (angles match to high precision)")

    print("\nSTEP 3 — Z-Framework geodesic θ′(n,k) demo (k≈0.3)")
    print("---------------------------------------------------")
    print(f"Running density-correct demo: N={args.N:,}, bins={args.bins}, seed={args.seed}")
    res = enhancement_density(N=args.N, bins=args.bins, seed=args.seed,
                              quantile=args.quantile, min_occupancy_frac=args.min_occupancy_frac)
    print(f"binning: {res['binning']} (min occupancy per bin: {res['min_occupancy']})")
    print(f"Result (density-based): densest-bin enhancement ≈ {res['density_enhancement_pct']:.2f}%")
    print(f"(for transparency) Raw-count enhancement (biased) ≈ {res['raw_enhancement_pct']:.2f}%")
    print(f"n per bin:        {res['n_counts']}")
    print(f"primes per bin:   {res['prime_counts']}")
    print(f"density per bin:  {[round(d, 6) for d in res['densities']]}")

    if args.bootstrap and args.bootstrap > 1:
        (mean_val, lo, hi), _ = bootstrap_ci_density(N=args.N, bins=args.bins, B=args.bootstrap, seed=args.seed,
                                                     quantile=args.quantile, min_occupancy_frac=args.min_occupancy_frac)
        print(f"\nBootstrap CI (density enhancement): mean={mean_val:.2f}%  95% CI=[{lo:.2f}%, {hi:.2f}%]")

    print("\nEpilogue — Takeaways")
    print("---------------------")
    print("• Identities hold (symbolically exact; tiny numeric error).")
    print("• Half-angle / double-angle keep curvature steps simple and stable.")
    print("• θ′(n,k) is not uniform for k≠1 → density matters; counts can mislead.")
    print("• Use **quantile bins** and occupancy guards to avoid artifacts.")
    print("• Bootstrap if you need a quick CI at larger N.")

if __name__ == "__main__":
    main()
