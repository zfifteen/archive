#!/usr/bin/env python3
"""
gbmr3_geodesic.py — Geodesic Miller–Rabin with three per‑n base families.

Design
------
For each n, choose exactly one Miller–Rabin base from each of three
geodesic families derived from powers of the golden ratio:

  A: α₁ = φ
  B: α₂ = φ²
  C: α₃ = φ³

Compute u = floor(α * n) in high precision (Decimal) to avoid drift,
then map deterministically into [2, n-2] via  a = 2 + (u mod (n-3)).
Ensure the three bases are distinct with a tiny deterministic bump.

This is a pure “geodesic-only” selector: no random choices, no S64 set.

CLI
---
  python gbmr3_geodesic.py check N
      → prints the three bases and primality decision for N.

  python gbmr3_geodesic.py find-break [LIMIT]
      → scans Carmichael<=1e6 first, then odd numbers up to LIMIT (default 1e6)
        and prints the first mismatch vs sympy.isprime, if any.

  python gbmr3_geodesic.py demo
      → demonstrates that n=1_024_651 (19*199*271) is correctly rejected here.

Requirements
------------
  - Python 3.9+
  - sympy (for ground truth in check/find-break modes)
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from typing import List, Optional, Tuple, Dict, Any
import sys

# Ground truth only used in CLI modes
try:
    import sympy as sp
except Exception:
    sp = None  # allow import without sympy if used as a library

# High precision for robust Beatty floors
getcontext().prec = 80
PHI  = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
PHI2 = PHI * PHI
PHI3 = PHI2 * PHI

# -----------------------------
# Miller–Rabin core
# -----------------------------
def mr_core(n: int, bases: List[int]) -> bool:
    """Return True if n is probably prime under the provided bases."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    # write n-1 = 2^r * d with d odd
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in bases:
        if a <= 1 or a >= n:
            a = (a % (n - 2)) + 2  # clamp into [2, n-2]
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False  # composite
    return True  # probably prime

# -----------------------------
# Three-set geodesic witnesses (per-n)
# -----------------------------
def _floor_dec(x: Decimal) -> int:
    return int(x.to_integral_value(rounding="ROUND_FLOOR"))

def _map_to_base(u: int, n: int) -> int:
    # Map integer u deterministically into MR base range [2, n-2]
    if n <= 4:
        return max(2, min(3, n-2))  # trivial smalls
    return 2 + (u % (n - 3))

def geodesic_triplet(n: int) -> List[int]:
    """
    Compute three distinct MR bases for n from φ, φ², φ³ families.
    Each base is derived from u = floor(alpha * n) and mapped to [2, n-2].
    If collisions occur, bump u deterministically until distinct.
    """
    if n <= 4:
        return [2, 3, 5][:max(0, n-2)]

    alphas = (PHI, PHI2, PHI3)
    seen = set()
    bases: List[int] = []
    for i, alpha in enumerate(alphas):
        u = _floor_dec(alpha * Decimal(n))
        a = _map_to_base(u, n)
        # ensure distinct bases (at most a couple of bumps)
        bump = 0
        while a in seen:
            bump += 1
            a = _map_to_base(u + bump, n)
        seen.add(a)
        bases.append(a)
    return bases

def gbmr3(n: int) -> bool:
    """Geodesic-BMR with exactly three per-n bases (φ, φ², φ³)."""
    return mr_core(n, geodesic_triplet(n))

# -----------------------------
# Search utilities (CLI)
# -----------------------------

CARMICHAEL_LE_1E6 = [
    561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341, 41041, 46657,
    52633, 62745, 63973, 75361, 101101, 115921, 126217, 162401, 172081, 188461,
    252601, 278545, 294409, 314821, 334153, 340561, 399001, 410041, 449065, 488881,
    512461, 530881, 552721, 656601, 658801, 670033, 748657, 825265, 838201, 852841,
    997633
]

def find_first_break(limit_scan: int = 1_000_000) -> Optional[Dict[str, Any]]:
    """Return the first mismatch vs sympy.isprime, or None if none found."""
    if sp is None:
        raise RuntimeError("sympy is required for find_first_break (ground truth).")

    # 1) Carmichael set first (classic MR traps)
    for n in CARMICHAEL_LE_1E6:
        pred = gbmr3(n)
        if pred:  # claimed prime but actually composite
            return {
                "source": "carmichael<=1e6",
                "n": n,
                "true_isprime": False,
                "gbmr3_isprime": True,
                "bases": geodesic_triplet(n),
            }

    # 2) Incremental odd scan
    for n in range(3, limit_scan + 1, 2):
        truth = sp.isprime(n)
        pred = gbmr3(n)
        if bool(truth) != bool(pred):
            return {
                "source": f"odd_scan_up_to_{limit_scan}",
                "n": n,
                "true_isprime": bool(truth),
                "gbmr3_isprime": bool(pred),
                "bases": geodesic_triplet(n),
            }
    return None

# -----------------------------
# CLI entry
# -----------------------------
def _usage() -> None:
    print(
        "Usage:\n"
        "  python gbmr3_geodesic.py check N\n"
        "  python gbmr3_geodesic.py find-break [LIMIT]\n"
        "  python gbmr3_geodesic.py demo\n"
    )

def main(argv: List[str]) -> int:
    if len(argv) < 2:
        _usage()
        return 0

    cmd = argv[1]
    if cmd == "check":
        if len(argv) < 3:
            print("check requires N")
            return 2
        n = int(argv[2])
        bases = geodesic_triplet(n)
        print(f"n={n}")
        print(f"geodesic bases: {bases}")
        print(f"gbmr3 decision: {'prime' if gbmr3(n) else 'composite'}")
        return 0

    if cmd == "find-break":
        limit = int(argv[2]) if len(argv) >= 3 else 1_000_000
        res = find_first_break(limit)
        print(res)
        return 0

    if cmd == "demo":
        n = 1_024_651  # 19*199*271, was a 3-base FP in older scheme
        print(f"n={n}")
        print(f"geodesic bases: {geodesic_triplet(n)}")
        print(f"gbmr3 decision: {'prime' if gbmr3(n) else 'composite'}")
        return 0

    _usage()
    return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
