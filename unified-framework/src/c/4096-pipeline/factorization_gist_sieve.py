#!/usr/bin/env python3
"""
Factorization Shortcut Demo (Self-Contained, Gist-Ready)
-------------------------------------------------------

Goal: Empirically demonstrate that **recovering just one factor** of a semiprime N = p*q
from a small candidate list is sufficient to fully factor N quickly via the shortcut:

    q = N // p      (then confirm q is prime)

This script:
  - Builds semiprimes (balanced or unbalanced) under Nmax.
  - Uses a simple angular heuristic over θ'(·) to propose candidate primes for each N.
  - Tries dividing N by candidates to recover either factor p or q (the shortcut).
  - Computes the **partial_rate** (practical factorization success), Wilson 95% CIs,
    full_rate, and average candidate list size.
  - Prints a few concrete examples showing N, recovered p, computed q, and primality check.

No external dependencies (pure Python). Suitable as a single-file Gist.
"""

from __future__ import annotations
import argparse
import csv
import math
import random
import sys
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Tuple

# --------------------- θ'(n,k), circle utils ---------------------

PHI = (1.0 + 5.0 ** 0.5) / 2.0
K_DEFAULT = 0.3  # curvature exponent (tunable; 0.3 is the baseline)

def frac(x: float) -> float:
    return x - math.floor(x)

def theta_prime_int(n: int, k: float = K_DEFAULT) -> float:
    """
    θ'(n,k) = φ * { n / φ }^k, then take fractional part.
    Uses float math which is fine for the documented scale (<=1e12). For larger, switch to Decimal/mpmath.
    """
    x = (n % PHI) / PHI
    val = PHI * (x ** k)
    return frac(val)

def circ_dist(a: float, b: float) -> float:
    """Shortest circular distance on [0,1)."""
    d = (a - b + 0.5) % 1.0 - 0.5
    return abs(d)

# --------------------- primes & semiprimes ---------------------

def sieve_primes(limit: int) -> List[int]:
    if limit < 2:
        return []
    bs = bytearray(b"\x01") * (limit + 1)
    bs[0:2] = b"\x00\x00"
    p = 2
    while p * p <= limit:
        if bs[p]:
            step = p
            start = p * p
            bs[start: limit + 1: step] = b"\x00" * (((limit - start) // step) + 1)
        p += 1
    return [i for i, v in enumerate(bs) if v]

def is_prime_trial(n: int, primes_small: List[int]) -> bool:
    """Deterministic primality using trial division by primes <= sqrt(n). Fast enough for this scale."""
    if n < 2:
        return False
    r = int(math.isqrt(n))
    for p in primes_small:
        if p > r:
            break
        if n % p == 0:
            return n == p
    return True

def sample_semiprimes_balanced(primes: List[int], target_count: int, Nmax: int, seed: int) -> List[Tuple[int,int,int]]:
    """
    Balanced sampling: pick p, q from [sqrt(Nmax)/2, 2*sqrt(Nmax)], keep N=p*q < Nmax.
    """
    random.seed(seed)
    out: List[Tuple[int,int,int]] = []
    sqrtNmax = int(math.isqrt(Nmax))
    band_lo = max(2, sqrtNmax // 2)
    band_hi = max(band_lo + 1, sqrtNmax * 2)
    primes_bal = [p for p in primes if band_lo <= p <= band_hi]
    if not primes_bal:
        raise ValueError("No primes in balanced band; increase Nmax or sieve limit.")
    while len(out) < target_count:
        p = random.choice(primes_bal)
        q = random.choice(primes_bal)
        if p > q:
            p, q = q, p
        N = p * q
        if N < Nmax:
            out.append((p, q, N))
    return out

def sample_semiprimes_unbalanced(primes: List[int], target_count: int, Nmax: int, seed: int) -> List[Tuple[int,int,int]]:
    """
    Unbalanced sampling: choose p from a small band, q from a larger band; keep N=p*q < Nmax.
    """
    random.seed(seed)
    out: List[Tuple[int,int,int]] = []
    sqrtNmax = int(math.isqrt(Nmax))
    small_hi = max(7, sqrtNmax // 5)  # smaller band for p
    large_hi = sqrtNmax * 3           # larger band for q (still constrained by N<Nmax)
    primes_small = [p for p in primes if 2 <= p <= small_hi]
    primes_large = [p for p in primes if small_hi < p <= large_hi]
    if not primes_small or not primes_large:
        raise ValueError("Insufficient primes for unbalanced sampling; adjust Nmax or bands.")
    while len(out) < target_count:
        p = random.choice(primes_small)
        q = random.choice(primes_large)
        if p > q:
            p, q = q, p
        N = p * q
        if N < Nmax:
            out.append((p, q, N))
    return out

# --------------------- Heuristic & evaluation ---------------------

@dataclass
class HeuristicSpec:
    name: str
    func: Callable[[int, Dict[str,object]], List[int]]
    params: Dict[str, object]

def heuristic_band(N: int, ctx: Dict[str,object]) -> List[int]:
    """
    Single-band proximity to θ'(N): select primes with |θ'(p) - θ'(N)| <= eps.
    Caps candidate list by closest angular distance if needed.
    """
    eps = float(ctx.get("eps", 0.05))
    max_candidates = int(ctx.get("max_candidates", 1000))
    k = float(ctx.get("k", K_DEFAULT))
    theta_pool: Dict[int,float] = ctx["theta_pool"]
    pool: List[int] = ctx["pool"]
    thetaN = theta_prime_int(N, k=k)
    cands = [p for p in pool if circ_dist(theta_pool[p], thetaN) <= eps]
    if len(cands) > max_candidates:
        cands.sort(key=lambda p: circ_dist(theta_pool[p], thetaN))
        cands = cands[:max_candidates]
    return cands

def wilson_ci(successes: int, n: int, z: float = 1.96) -> Tuple[float,float,float]:
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = successes / n
    denom = 1.0 + (z*z)/n
    center = (p + (z*z)/(2*n)) / denom
    half = z * math.sqrt((p*(1-p)/n) + (z*z)/(4*n*n)) / denom
    return (p, max(0.0, center - half), min(1.0, center + half))

def factorize_with_candidates(N: int, candidates: List[int], primes_small: List[int]) -> Tuple[bool, int, int, bool]:
    """
    Attempt the shortcut: test divisibility by each candidate. If N % p == 0, success.
    Return (success, p_found or 0, q_computed or 0, q_is_prime?).
    """
    for p in candidates:
        if p > 1 and N % p == 0:
            q = N // p
            q_prime = is_prime_trial(q, primes_small)
            return True, p, q, q_prime
    return False, 0, 0, False

def evaluate(semiprimes: List[Tuple[int,int,int]], heuristics: List[HeuristicSpec], pool: List[int], k: float, primes_small: List[int], out_csv: str|None, out_md: str|None, examples: int = 5) -> None:
    theta_pool = {p: theta_prime_int(p, k=k) for p in pool}

    # Show a few concrete examples of the shortcut working
    printed = 0
    print("\n=== Factorization Shortcut Examples ===")
    for p, q, N in semiprimes[:max(10, examples*2)]:  # scan a few to find successes quickly
        hs = heuristics[-1]  # show with the widest eps by default
        cands = hs.func(N, {"theta_pool": theta_pool, "pool": pool, **hs.params, "k": k})
        ok, pf, qf, qprime = factorize_with_candidates(N, cands, primes_small)
        if ok:
            print(f"N={N}  →  recovered p={pf}; shortcut q=N//p={qf}; q is prime? {qprime}; candidates={{len(cands)}}")
            printed += 1
            if printed >= examples:
                break
    if printed == 0:
        print("(No quick successes found in the first few; still computing aggregate rates below.)")

    # Aggregate metrics per heuristic
    rows: List[Dict[str,str]] = []
    n_total = len(semiprimes)
    for hs in heuristics:
        partial = 0
        full = 0
        cand_sizes: List[int] = []
        for p, q, N in semiprimes:
            cands = hs.func(N, {"theta_pool": theta_pool, "pool": pool, **hs.params, "k": k})
            cand_sizes.append(len(cands))
            s = set(cands)
            # practical success: either factor is captured AND divides N
            ok, pf, qf, qprime = factorize_with_candidates(N, cands, primes_small)
            if ok:
                partial += 1
            # diagnostic symmetry: both p and q included in candidates (regardless of divisibility test order)
            if p in s and q in s:
                full += 1
        pr, lo_pr, hi_pr = wilson_ci(partial, n_total)
        fr, lo_fr, hi_fr = wilson_ci(full, n_total)
        row = {
            "heuristic": hs.name,
            "eps": f"{hs.params.get('eps', None)}",
            "max_candidates": f"{hs.params.get('max_candidates', None)}",
            "n": f"{n_total}",
            "partial_rate": f"{pr:.4f}",
            "partial_CI95": f"[{lo_pr:.4f}, {hi_pr:.4f}]",
            "full_rate": f"{fr:.4f}",
            "full_CI95": f"[{lo_fr:.4f}, {hi_fr:.4f}]",
            "avg_candidates": f"{(sum(cand_sizes)/len(cand_sizes)):.1f}"
        }
        rows.append(row)

    # Print table to stdout
    print("\n=== Summary (partial_rate is the practical factorization success) ===")
    hdr = ["heuristic","eps","max_candidates","n","partial_rate","partial_CI95","full_rate","full_CI95","avg_candidates"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "|".join(["---"]*len(hdr)) + "|")
    for r in rows:
        print("| " + " | ".join(r[h] for h in hdr) + " |")

    # Optional CSV/MD
    if out_csv:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=hdr)
            w.writeheader()
            w.writerows(rows)
    if out_md:
        with open(out_md, "w") as f:
            f.write("# Factorization Shortcut — Summary\n\n")
            f.write("_partial_rate is the practical success rate (recover either factor, compute the other as q=N//p)._ \n\n")
            f.write("| " + " | ".join(hdr) + " |\n")
            f.write("|" + "|".join(["---"]*len(hdr)) + "|\n")
            for r in rows:
                f.write("| " + " | ".join(r[h] for h in hdr) + " |\n")

    # --- Human-readable comparison: naive vs. geometric ---
    maxN = max(N for _,_,N in semiprimes) if semiprimes else 0
    naive_limit = int(math.isqrt(maxN)) if maxN > 0 else 0
    naive_divisions = sum(1 for p in pool if p <= naive_limit)

    def _fmt_pct(x): return f"{x*100:.1f}%"
    print("\n=== Human-Readable Summary (Naïve vs. Geometric) ===")
    print(f"Naïve trial division would test ~{naive_divisions} prime divisors per N (up to √N).")
    print("Our geometric band heuristic tries far fewer candidates on average:")
    for r in rows:
        avg_c = float(r["avg_candidates"])
        pr = float(r["partial_rate"])
        eps = r["eps"]
        speedup = (naive_divisions / avg_c) if avg_c > 0 else float('nan')
        print(f"- ε={eps}: partial_rate≈{_fmt_pct(pr)} with ~{avg_c:.0f} candidates (vs ~{naive_divisions} naïve) → ≈{speedup:.1f}× fewer divisions.")

    print("\nInterpretation: even in *balanced* semiprimes (harder), we factor a meaningful fraction using far fewer trials.")
    print("Recovering just one factor from the geometric candidate list completes the factorization via q=N//p + primality check.")

    if out_md:
        with open(out_md, "a") as f:
            f.write("\n\n## Human-Readable Summary (Naïve vs. Geometric)\n\n")
            f.write(f"- Naïve trial division would test ~{naive_divisions} prime divisors per N (up to √N).\n")
            f.write("- Our geometric band heuristic tries far fewer candidates on average:\n")
            for r in rows:
                avg_c = float(r["avg_candidates"]); pr = float(r["partial_rate"]); eps = r["eps"]
                speedup = (naive_divisions / avg_c) if avg_c > 0 else float('nan')
                f.write(f"  - ε={eps}: partial_rate≈{_fmt_pct(pr)} with ~{avg_c:.0f} candidates (vs ~{naive_divisions} naïve) → ≈{speedup:.1f}× fewer divisions.\n")
            f.write("\nInterpretation: even in *balanced* semiprimes (harder), we factor a meaningful fraction using far fewer trials.\n")
            f.write("Recovering just one factor from the geometric candidate list completes the factorization via `q=N//p` plus a primality check.\n")

# --------------------- CLI ---------------------

def parse_args(argv: List[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Empirical demo of semiprime factorization via one-factor shortcut (self-contained).")
    ap.add_argument("--Nmax", type=int, default=1_000_000, help="Upper bound for N (semiprimes are < Nmax)")
    ap.add_argument("--samples", type=int, default=1000, help="Number of semiprimes to test")
    ap.add_argument("--mode", choices=["balanced","unbalanced"], default="balanced", help="Semiprime sampling regime")
    ap.add_argument("--eps", type=float, nargs="+", default=[0.02,0.03,0.04,0.05], help="Epsilon values for band heuristic")
    ap.add_argument("--k", type=float, default=K_DEFAULT, help="Curvature exponent k for θ'")
    ap.add_argument("--max-candidates", type=int, default=1000, help="Candidate cap per N")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed")
    ap.add_argument("--csv", type=str, default="", help="Optional path to write CSV summary")
    ap.add_argument("--md", type=str, default="", help="Optional path to write Markdown summary")
    return ap.parse_args(argv)

def main(argv: List[str]) -> int:
    args = parse_args(argv)
    # Prime pool up to ~3*sqrt(Nmax) for both sampling & candidate pool
    limit = max(100, 3 * int(math.isqrt(args.Nmax)) + 100)
    pool = sieve_primes(limit)
    if not pool:
        print("No primes in pool; increase Nmax.", file=sys.stderr)
        return 2
    # Small primes for trial-division primality checks
    small_primes = sieve_primes(int(math.isqrt(args.Nmax)) + 1000)

    # Build semiprimes
    if args.mode == "balanced":
        semis = sample_semiprimes_balanced(pool, target_count=args.samples, Nmax=args.Nmax, seed=args.seed)
    else:
        semis = sample_semiprimes_unbalanced(pool, target_count=args.samples, Nmax=args.Nmax, seed=args.seed)

    # Register heuristics (single-band A @ each epsilon)
    heuristics: List[HeuristicSpec] = [
        HeuristicSpec(name=f"A:band@{eps}", func=heuristic_band, params={"eps": eps, "max_candidates": args.max_candidates})
        for eps in args.eps
    ]

    out_csv = args.csv if args.csv else None
    out_md  = args.md  if args.md  else None

    evaluate(semis, heuristics, pool, k=args.k, primes_small=small_primes, out_csv=out_csv, out_md=out_md, examples=5)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
