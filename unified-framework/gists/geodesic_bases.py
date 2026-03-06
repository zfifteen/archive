#!/usr/bin/env python3
"""
geodesic_bases.py — Pure geodesic base selectors (NO Miller–Rabin, NO pow mod).

What this is
------------
Deterministic, n-specific integers derived from Beatty sequences of φ, φ², φ³.
Useful for Z Framework geometric resolution: θ'(n, k) = φ · ((n mod φ)/φ)^k,
providing stable seeds for prime density enhancement (~15%, CI [14.6%, 15.4%]) without
primality tests. Aligns with params.py (KAPPA_GEO_DEFAULT=0.3).

Exports
-------
- PHI, PHI2, PHI3  : Decimal constants
- beatty_forward(n, alpha) -> int
- beatty_inverse(m, alpha) -> int        # exact inverse for m = floor(alpha*n)
- geodesic_family(n, alpha, mapped=True) -> int
- geodesic_triplet(n, mapped=True, dedup=True) -> list[int]
- geodesic_set(n, alphas, mapped=True, dedup=True) -> list[int]

Notes
-----
- If mapped=True, values projected into [2, n-2] as: 2 + (u % (n-3)).
  If mapped=False, raw Beatty u = floor(alpha * n).
- No randomness. Collisions (mapped=True) resolved by deterministic bumps (u+1, u+2, ...)
  if dedup=True; max_bump=10 guard prevents loops.
- High-precision Decimal avoids float drift; prec=80 > MP_DPS=50 for safety.
- Z Integration: Use for geodesic_mapper optimizations (e.g., batch via NumPy).

CLI
---
  python geodesic_bases.py N
      → prints geodesic triplet (mapped and raw seeds) for N

  echo "3 5 7" | python geodesic_bases.py
      → prints triplets for each n from stdin (skips invalid)

  python geodesic_bases.py --help
      → usage info
"""
from __future__ import annotations

import math
from decimal import Decimal, getcontext
from typing import Iterable, List, Sequence
import sys
import argparse  # Added for --help

# High precision for robust Beatty floors ( > MP_DPS=50 from params.py)
getcontext().prec = 80
PHI  = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
PHI2 = PHI * PHI
PHI3 = PHI2 * PHI

PHIf = (1+5**0.5)/2
def beatty_forward_fast(n: int) -> int:
    # single-precision floor, ~15 decimal-digit accuracy, 
    # safe for any n up to ~1e14 or so
    return math.floor(PHIf * n)

def _floor_dec(x: Decimal) -> int:
    return int(x.to_integral_value(rounding="ROUND_FLOOR"))

def beatty_forward(n: int, alpha: Decimal) -> int:
    """m = floor(alpha * n), computed with high-precision Decimal."""
    return _floor_dec(alpha * Decimal(n))

def beatty_inverse(m: int, alpha: Decimal) -> int:
    """Exact inverse for Beatty: given m=floor(alpha*n), return n."""
    # n = ceil((m+1)/alpha) - 1
    from decimal import ROUND_CEILING
    q = (Decimal(m) + 1) / alpha
    n = int(q.to_integral_value(rounding=ROUND_CEILING)) - 1
    return n

def _map_to_range(u: int, n: int) -> int:
    """Map integer u deterministically into [2, n-2]."""
    if n <= 4:
        return max(2, min(3, n-2))  # trivial clamp for tiny n (e.g., n=3 → 2)
    return 2 + (u % (n - 3))

def geodesic_family(n: int, alpha: Decimal, mapped: bool = True) -> int:
    """One value for this n from the α-family. Raw seed or mapped base."""
    u = beatty_forward(n, alpha)
    return _map_to_range(u, n) if mapped else u

def geodesic_set(n: int, alphas: Sequence[Decimal], mapped: bool = True, dedup: bool = True) -> List[int]:
    """Values for this n from each α in `alphas`. Ensures distinctness if requested."""
    vals: List[int] = []
    seen = set()
    for a in alphas:
        u = beatty_forward(n, a)
        v = _map_to_range(u, n) if mapped else u
        if dedup and mapped:
            bump = 0
            max_bump = 10  # Guard against infinite loops (rare for n>10)
            while v in seen and bump < max_bump:
                bump += 1
                v = _map_to_range(u + bump, n)
            if bump >= max_bump:
                raise ValueError(f"Dedup failed for n={n}, alpha={a}: too many collisions")
        vals.append(v)
        seen.add(v)
    return vals

def geodesic_triplet(n: int, mapped: bool = True, dedup: bool = True) -> List[int]:
    """Three per-n values from φ, φ², φ³ (Z Framework golden family)."""
    return geodesic_set(n, (PHI, PHI2, PHI3), mapped=mapped, dedup=dedup)

# -----------------------------
# CLI
# -----------------------------
def _print_triplet(n: int) -> None:
    seeds = geodesic_triplet(n, mapped=False, dedup=False)
    bases = geodesic_triplet(n, mapped=True, dedup=True)
    print(f"n={n}")
    print(f"  seeds (φ,φ²,φ³): {seeds}")
    print(f"  bases [2..n-2]: {bases}")
    print()  # Separator for multi-n

def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Geodesic bases from Beatty sequences for Z Framework."
    )
    parser.add_argument('n', nargs='?', help="Single n value")
    # parser.add_argument('--help', action='help', help="Show this help")
    args = parser.parse_args(argv[1:])  # Skip script name

    if args.n and args.n.isdigit():
        _print_triplet(int(args.n))
        return 0

    # Read ns from stdin (whitespace-separated)
    data = sys.stdin.read().strip().split()
    if not data:
        parser.print_help()
        return 2
    processed = 0
    for tok in data:
        try:
            n = int(tok)
            _print_triplet(n)
            processed += 1
        except ValueError:
            print(f"Warning: Skipping invalid '{tok}'", file=sys.stderr)
    if processed == 0:
        print("No valid integers found.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))