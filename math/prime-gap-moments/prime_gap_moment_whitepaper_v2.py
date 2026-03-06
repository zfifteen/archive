#!/usr/bin/env python3
"""
WHITE PAPER SCRIPT
==================
Prime Gap Moment Deviations — Reversal, Cancellation, and Shape Metrics

Date: 2026-03-02

What this script does
---------------------
This script re-analyzes the (n, μ1..μ4) moment data reported by Joel E. Cohen (2024),
arXiv:2405.16019, for the first n prime gaps.

It distinguishes two different kinds of deviation:

  (1) Cohen-normalized deviations (mean + shape mixed together)
      A_k(n) = μ'_{k,n}/(k! (log n)^k) - 1

  (2) Shape-only deviations at fixed empirical mean (removes mean mismatch)
      B_k(n) = μ'_{k,n}/(k! μ_1(n)^k) - 1     (and B_1 := 0)

Key identity (exact, algebraic)
-------------------------------
Let μ_1 be the empirical mean for the same dataset used to compute μ_k.

Then:

      1 + A_k(n)  =  (1 + A_1(n))^k  ·  (1 + B_k(n))

So a small |A_k| for k>=2 can arise from *cancellation* between:
  • a mean mismatch term (A_1 > 0 when μ_1 exceeds log n), and
  • a shape term (B_k < 0 when the standardized moments are sub-exponential).

This script demonstrates:
  • the apparent "reversed hierarchy" in |A_k| for the largest Cohen table scales,
  • why that reversal is largely a cancellation artifact,
  • what the shape-only deviations B_k do instead,
  • how a better mean proxy (log n + log log n - 1) removes the A_1 bias, and
  • simple control/toy models showing what mean drift alone can and cannot explain.

Plots
-----
If matplotlib is available, the script writes PNG plots into an output directory.
No seaborn is used; no explicit colors are set (matplotlib defaults only).

Optional raw-gap analysis
-------------------------
If you have a file of actual gap values (one per line or whitespace-separated),
you can pass:

  --gaps-file path/to/gaps.txt

The script will compute global and windowed metrics (last 10%, last 1%)
to reduce “history mixing”.

Disclaimer
----------
This script is a diagnostics / reproducibility “white paper” runner. It does not
prove any asymptotic statements. Interpret “convergence” cautiously: several
curves cross zero, so |·| plots can be misleading.
"""

from __future__ import annotations

import argparse
import math
import os
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ============================================================================
# 0) DATA SOURCE: Cohen (2024) Table-1 moment values (as used in the original script)
# ============================================================================
#
# Each row: (n, μ1, μ2, μ3, μ4)
#
# Here n is the number of prime gaps used; μk is the empirical k-th raw moment of the gaps
# over the first n gaps (as tabulated).
#
# NOTE: This script treats these as authoritative inputs and focuses on derived metrics.
#
COHEN_TABLE: List[Tuple[float, float, float, float, float]] = [
    (3510, 9.3293, 136.2017, 2781.8, 74292.0),
    (22998, 11.3982, 210.7095, 5506.0, 185460.0),
    (155609, 13.4770, 304.1124, 9891.4, 425030.0),
    (1077869, 15.5652, 412.7866, 15776.0, 788630.0),
    (7603551, 17.6520, 539.4491, 23885.0, 1386400.0),
    (54400026, 19.7379, 683.2373, 34423.0, 2280600.0),
    (393615804, 21.8231, 844.1273, 47670.0, 3544000.0),
    (2.8744e9, 23.9074, 1022.2, 63972.0, 5277300.0),
    (2.1152e10, 25.9908, 1217.3, 83638.0, 7581900.0),
    (1.5666e11, 28.0736, 1429.6, 106990.0, 10574000.0),
    (1.1667e12, 30.1560, 1659.0, 134350.0, 14377000.0),
    (8.7312e12, 32.2379, 1905.6, 166030.0, 19127000.0),
]


# ============================================================================
# 1) SMALL UTILITIES
# ============================================================================

def safe_log(x: float) -> float:
    if x <= 0:
        raise ValueError(f"log domain error: x={x}")
    return math.log(x)

def safe_loglog(x: float) -> float:
    lx = safe_log(x)
    if lx <= 0:
        raise ValueError(f"loglog domain error: log(x)={lx} for x={x}")
    return math.log(lx)

def fmt(x: float, digits: int = 6) -> str:
    # compact but readable numeric formatting
    if x == 0:
        return "0"
    ax = abs(x)
    if ax < 1e-4 or ax >= 1e4:
        return f"{x:.{digits}e}"
    return f"{x:.{digits}f}"

def monotone_reversed_abs(values_by_k: Dict[int, float]) -> bool:
    """True if |k=4| < |k=3| < |k=2| < |k=1|."""
    return (abs(values_by_k[4]) < abs(values_by_k[3]) < abs(values_by_k[2]) < abs(values_by_k[1]))

def monotone_normal_abs(values_by_k: Dict[int, float]) -> bool:
    """True if |k=4| > |k=3| > |k=2| > |k=1|."""
    return (abs(values_by_k[4]) > abs(values_by_k[3]) > abs(values_by_k[2]) > abs(values_by_k[1]))

def sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0

def find_sign_changes(xs: Sequence[float], ys: Sequence[float]) -> List[Tuple[float, float]]:
    """Return intervals [x_i, x_{i+1}] where y changes sign or hits zero."""
    out = []
    for i in range(len(xs) - 1):
        y0, y1 = ys[i], ys[i + 1]
        if y0 == 0 or y1 == 0 or (y0 > 0) != (y1 > 0):
            out.append((xs[i], xs[i + 1]))
    return out


# ============================================================================
# 2) METRIC DEFINITIONS: A_k, B_k, and alternative mean proxy
# ============================================================================

@dataclass(frozen=True)
class MomentRow:
    n: float
    mu: Dict[int, float]     # raw moments mu[k], k=1..4
    logn: float
    loglogn: float

@dataclass(frozen=True)
class MetricsRow:
    n: float
    logn: float
    loglogn: float
    mu: Dict[int, float]
    A: Dict[int, float]       # Cohen normalization
    B: Dict[int, float]       # mean-standardized (shape-only)
    A_meanonly: Dict[int, float]  # predicted if B_k ≡ 0 (pure mean mismatch)
    A_altmean: Dict[int, float]   # using L(n)=log n + log log n - 1 as mean proxy
    A1_pnt_correction: float      # (log log n - 1)/log n
    cancellation_residual: Dict[int, float]  # sanity check: reconstructed vs direct

def mean_proxy_loglog(n: float) -> float:
    """
    A common next-order proxy for the average prime gap among the first n gaps:
      L(n) = log n + log log n - 1
    This is motivated by the refinement p_n ~ n (log n + log log n - 1 + ...),
    so average gap ~ p_n/n ≈ log n + log log n - 1.

    We use it here as an *illustrative* alternative normalization, not a theorem.
    """
    ln = safe_log(n)
    return ln + math.log(ln) - 1.0

def compute_metrics_from_cohen_table(table: Sequence[Tuple[float, float, float, float, float]]) -> List[MetricsRow]:
    rows: List[MetricsRow] = []
    for (n, mu1, mu2, mu3, mu4) in table:
        n = float(n)
        mu = {1: float(mu1), 2: float(mu2), 3: float(mu3), 4: float(mu4)}
        ln = safe_log(n)
        lln = safe_loglog(n)

        # Cohen normalization A_k
        A: Dict[int, float] = {}
        for k in range(1, 5):
            denom = math.factorial(k) * (ln ** k)
            A[k] = (mu[k] / denom) - 1.0

        # Shape-only deviations B_k (mean-standardized)
        B: Dict[int, float] = {1: 0.0}
        for k in range(2, 5):
            denom = math.factorial(k) * (mu[1] ** k)
            B[k] = (mu[k] / denom) - 1.0

        # Mean-only prediction for A_k if the shape were exactly exponential at mean μ1 (i.e. B_k ≡ 0)
        A_meanonly: Dict[int, float] = {1: A[1]}
        for k in range(2, 5):
            A_meanonly[k] = (1.0 + A[1]) ** k - 1.0

        # Alternative mean normalization using L(n)=log n + log log n - 1
        L = mean_proxy_loglog(n)
        A_altmean: Dict[int, float] = {}
        for k in range(1, 5):
            denom = math.factorial(k) * (L ** k)
            A_altmean[k] = (mu[k] / denom) - 1.0

        # PNT-style leading correction for A1 if μ1 ≈ log n + log log n - 1
        A1_corr = (lln - 1.0) / ln

        # Sanity: reconstruct A_k from A1 and B_k using the identity.
        cancellation_residual: Dict[int, float] = {}
        for k in range(1, 5):
            if k == 1:
                recon = A[1]
            else:
                recon = ((1.0 + A[1]) ** k) * (1.0 + B[k]) - 1.0
            cancellation_residual[k] = recon - A[k]

        rows.append(
            MetricsRow(
                n=n,
                logn=ln,
                loglogn=lln,
                mu=mu,
                A=A,
                B=B,
                A_meanonly=A_meanonly,
                A_altmean=A_altmean,
                A1_pnt_correction=A1_corr,
                cancellation_residual=cancellation_residual,
            )
        )
    return rows


# ============================================================================
# 3) REPORT GENERATION (console + optional markdown)
# ============================================================================

class Report:
    def __init__(self) -> None:
        self.lines: List[str] = []

    def add(self, s: str = "") -> None:
        self.lines.append(s)

    def extend(self, ss: Iterable[str]) -> None:
        self.lines.extend(ss)

    def text(self) -> str:
        return "\n".join(self.lines)

    def write_to(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.text(), encoding="utf-8")

def build_whitepaper_report(rows: Sequence[MetricsRow]) -> Report:
    r = Report()

    r.add("=" * 90)
    r.add("PRIME GAP MOMENT DEVIATIONS — REVERSAL, CANCELLATION, AND SHAPE METRICS")
    r.add("=" * 90)
    r.add("")
    r.add("Data: Cohen (2024) Table moment values for the first n prime gaps (μ1..μ4).")
    r.add("Goal: Diagnose what the apparent 'reversed convergence hierarchy' in |A_k| is really measuring.")
    r.add("")

    r.add("Definitions")
    r.add("-" * 90)
    r.add("A_k(n) = μ_k / (k! (log n)^k) - 1            (Cohen normalization; mixes mean + shape)")
    r.add("B_k(n) = μ_k / (k! μ_1^k) - 1               (shape-only deviation at fixed empirical mean)")
    r.add("")
    r.add("Identity (exact):  1 + A_k = (1 + A_1)^k · (1 + B_k)")
    r.add("Interpretation:")
    r.add("  • A_1 captures how μ_1 compares to log n (mean mismatch).")
    r.add("  • B_k captures whether standardized moments are exponential-like once the mean is matched.")
    r.add("  • Small |A_k| for k>=2 can be cancellation between (1+A_1)^k (>1) and (1+B_k) (<1).")
    r.add("")

    # Main table
    r.add("Cohen table-derived metrics (signed)")
    r.add("-" * 90)
    header = (
        f"{'idx':>3} {'n':>12} {'loglog n':>9} "
        f"{'A1':>10} {'A2':>10} {'A3':>10} {'A4':>10} "
        f"{'B2':>10} {'B3':>10} {'B4':>10}"
    )
    r.add(header)
    r.add("-" * len(header))

    for i, row in enumerate(rows):
        r.add(
            f"{i:>3d} {row.n:>12.3e} {row.loglogn:>9.4f} "
            f"{row.A[1]:>10.6f} {row.A[2]:>10.6f} {row.A[3]:>10.6f} {row.A[4]:>10.6f} "
            f"{row.B[2]:>10.6f} {row.B[3]:>10.6f} {row.B[4]:>10.6f}"
        )

    r.add("")
    r.add("Absolute-value 'hierarchies' and why |·| can mislead")
    r.add("-" * 90)

    reversed_A = 0
    normal_B = 0
    for row in rows:
        if monotone_reversed_abs(row.A):
            reversed_A += 1
        if monotone_normal_abs({1: 0.0, 2: row.B[2], 3: row.B[3], 4: row.B[4]}):
            normal_B += 1

    r.add(f"Rows with reversed hierarchy in |A_k| (|A4|<|A3|<|A2|<|A1|): {reversed_A}/{len(rows)}")
    r.add(f"Rows with normal hierarchy in |B_k| (|B4|>|B3|>|B2|):         {normal_B}/{len(rows)}")
    r.add("")
    r.add("Important: |A_k| can look 'small' due to a zero crossing. Always inspect signed A_k.")
    r.add("")

    # Show largest-scale decomposition explicitly
    last = rows[-1]
    r.add("Largest scale decomposition (cancellation check)")
    r.add("-" * 90)
    r.add(f"n = {last.n:.4e}")
    r.add(f"A1 = {last.A[1]:.6f}  => mean factor (1+A1) = {1+last.A[1]:.6f}")
    for k in (2, 3, 4):
        mean_factor = (1.0 + last.A[1]) ** k
        shape_factor = 1.0 + last.B[k]
        total = 1.0 + last.A[k]
        r.add(
            f"k={k}: 1+A{k}={total:.6f}  "
            f"(1+A1)^k={mean_factor:.6f}  "
            f"(1+B{k})={shape_factor:.6f}  "
            f"product={mean_factor*shape_factor:.6f}"
        )
    r.add("")
    r.add("Takeaway: if A1>0 and Bk<0, higher k can have *more* cancellation, yielding smaller |A_k|.")
    r.add("          That is a normalization artifact, not necessarily 'faster convergence' of tails.")
    r.add("")

    # A1 correction check
    r.add("A1 vs a simple next-order correction")
    r.add("-" * 90)
    r.add("If μ1 ≈ log n + log log n - 1, then")
    r.add("  A1(n) ≈ (log log n - 1)/log n")
    r.add("")
    r.add(f"{'n':>12} {'A1 observed':>12} {'(loglog n - 1)/log n':>24} {'diff':>12}")
    r.add("-" * 65)
    for row in rows:
        diff = row.A[1] - row.A1_pnt_correction
        r.add(f"{row.n:>12.3e} {row.A[1]:>12.6f} {row.A1_pnt_correction:>24.6f} {diff:>12.6f}")
    r.add("")
    r.add("This explains why A1 is 'stubborn': it's dominated by the next-order mean correction,")
    r.add("not by tail effects.")
    r.add("")

    # Alternative mean normalization
    r.add("Alternative mean proxy normalization: L(n) = log n + log log n - 1")
    r.add("-" * 90)
    r.add("Define Ã_k(n) = μ_k/(k! L(n)^k) - 1. This removes most of A1.")
    r.add("Observe that Ã_k for k>=2 aligns closely with B_k (shape-only deviation).")
    r.add("")
    r.add(f"{'n':>12} {'Ã1':>10} {'Ã2':>10} {'Ã3':>10} {'Ã4':>10}")
    r.add("-" * 55)
    for row in rows:
        r.add(
            f"{row.n:>12.3e} "
            f"{row.A_altmean[1]:>10.6f} {row.A_altmean[2]:>10.6f} {row.A_altmean[3]:>10.6f} {row.A_altmean[4]:>10.6f}"
        )
    r.add("")
    r.add("Interpretation: once you normalize by a better mean proxy, the 'reversal' disappears;")
    r.add("you see sub-exponential standardized moments (negative deviations) instead.")
    r.add("")

    # Sign change diagnostics
    r.add("Sign-change diagnostics (where |·| plots are most misleading)")
    r.add("-" * 90)
    xs = [row.loglogn for row in rows]
    for k in (1, 2, 3, 4):
        ys = [row.A[k] for row in rows]
        intervals = find_sign_changes(xs, ys)
        if intervals:
            r.add(f"A{k} sign changes / zero touches in loglog(n) intervals: {intervals}")
        else:
            r.add(f"A{k} sign changes / zero touches: none in the Cohen table scales.")
    r.add("")
    r.add("If A_k crosses zero, |A_k| can appear to 'converge rapidly' even when A_k itself")
    r.add("is not monotonically shrinking.")
    r.add("")

    # Control models summary (printed, details in plots/extra output)
    r.add("Control-model sanity checks (conceptual)")
    r.add("-" * 90)
    r.add("Mean drift alone (a mixture of exponentials with varying means) implies B_k >= 0 for k>=2")
    r.add("by Jensen (x^k convex). Therefore, the observed B_k < 0 cannot be explained by mean drift alone.")
    r.add("")
    r.add("A simple way to get B_k < 0 is a sub-exponential shape (e.g., Gamma with shape r>1),")
    r.add("which has smaller standardized moments than Exp at the same mean. Combined with A1>0,")
    r.add("this can produce small |A_k| via cancellation.")
    r.add("")

    # Sanity: cancellation residual should be ~0
    r.add("Numerical sanity: identity residuals (reconstructed A_k - direct A_k)")
    r.add("-" * 90)
    r.add(f"{'n':>12} {'resid A1':>10} {'resid A2':>10} {'resid A3':>10} {'resid A4':>10}")
    r.add("-" * 60)
    for row in rows:
        r.add(
            f"{row.n:>12.3e} "
            f"{fmt(row.cancellation_residual[1], 3):>10} {fmt(row.cancellation_residual[2], 3):>10} "
            f"{fmt(row.cancellation_residual[3], 3):>10} {fmt(row.cancellation_residual[4], 3):>10}"
        )
    r.add("")
    r.add("Residuals should be ~0 up to floating error; this confirms the algebraic decomposition.")
    r.add("")

    r.add("Actionable recommendations for future empirical work")
    r.add("-" * 90)
    r.add("1) Always report A_k *and* B_k. A_k mixes mean mismatch and shape; B_k isolates shape.")
    r.add("2) Plot signed A_k (not only |A_k|). Zero crossings can fake 'fast convergence'.")
    r.add("3) Use windowed moments (e.g., last 10%, last 1%) to reduce history mixing.")
    r.add("4) For tail claims, add tail diagnostics: exceedance rates and conditional tail moments.")
    r.add("5) Test control models: drift-only mixtures cannot produce B_k<0; if primes show B_k<0 robustly,")
    r.add("   that is evidence of additional arithmetic regularity beyond nonstationary means.")
    r.add("")

    r.add("=" * 90)
    r.add("END OF WHITE PAPER SCRIPT OUTPUT")
    r.add("=" * 90)

    return r


# ============================================================================
# 4) OPTIONAL: RAW GAP FILE ANALYSIS + WINDOWED MOMENTS
# ============================================================================

def load_gaps(path: Path) -> List[float]:
    txt = path.read_text(encoding="utf-8").strip()
    if not txt:
        raise ValueError(f"No data in gaps file: {path}")
    parts = txt.replace(",", " ").split()
    gaps: List[float] = []
    for p in parts:
        try:
            gaps.append(float(p))
        except ValueError as e:
            raise ValueError(f"Failed to parse value {p!r} in {path}") from e
    if len(gaps) < 10:
        raise ValueError(f"Too few gap values ({len(gaps)}) in {path}")
    return gaps

def raw_moments(xs: Sequence[float], max_k: int = 4) -> Dict[int, float]:
    out: Dict[int, float] = {}
    n = len(xs)
    mean1 = sum(xs) / n
    out[1] = mean1
    for k in range(2, max_k + 1):
        out[k] = sum((x ** k) for x in xs) / n
    return out

def compute_A_B_for_gap_sample(gaps: Sequence[float], denom_log_n: Optional[float] = None, max_k: int = 4) -> Tuple[Dict[int, float], Dict[int, float], float]:
    """
    Compute A_k and B_k from a raw sample of gaps.
      denom_log_n: if None uses log(len(gaps)) as in Cohen; otherwise use provided scalar.
    Returns (A, B, L_used)
    """
    n = len(gaps)
    mu = raw_moments(gaps, max_k=max_k)
    L = safe_log(n) if denom_log_n is None else float(denom_log_n)

    A: Dict[int, float] = {}
    for k in range(1, max_k + 1):
        A[k] = mu[k] / (math.factorial(k) * (L ** k)) - 1.0

    B: Dict[int, float] = {1: 0.0}
    for k in range(2, max_k + 1):
        B[k] = mu[k] / (math.factorial(k) * (mu[1] ** k)) - 1.0

    return A, B, L

def windowed(xs: Sequence[float], keep_last_fraction: float) -> List[float]:
    if not (0 < keep_last_fraction <= 1.0):
        raise ValueError("keep_last_fraction must be in (0,1].")
    n = len(xs)
    start = int(math.floor(n * (1.0 - keep_last_fraction)))
    start = max(0, min(start, n-1))
    return list(xs[start:])

def tail_exceedance(xs: Sequence[float], multiples: Sequence[float]) -> Dict[float, float]:
    """
    Simple tail diagnostic: P(X >= m * mean(X)) for various multiples m.
    """
    mu = sum(xs) / len(xs)
    out: Dict[float, float] = {}
    for m in multiples:
        thr = m * mu
        out[m] = sum(1 for x in xs if x >= thr) / len(xs)
    return out


# ============================================================================
# 5) TOY / CONTROL MODELS
# ============================================================================

def gamma_ratio(shape_r: float, k: int) -> float:
    """
    Ratio R(r,k) := E[X^k] / (k! mean(X)^k) for Gamma(shape=r, scale=mean/r).
    For r=1 this is 1 (exponential). For r>1, this is <1.
    """
    # E[X^k] = (m/r)^k * Gamma(r+k)/Gamma(r).
    # Divide by k! m^k -> Gamma(r+k)/(Gamma(r)*r^k*k!)
    return math.gamma(shape_r + k) / (math.gamma(shape_r) * (shape_r ** k) * math.factorial(k))

def mean_profile(j: float) -> float:
    """
    A simple increasing proxy for 'local mean gap' as a function of index j.

    Chosen for demonstration:
        m(j) = log j + log log j

    This produces a mean mismatch vs log n of size ~ (log log n - 1)/log n,
    similar to what is observed in A1 from the Cohen table.

    Domain: j>e. We enforce j>=3 by construction.
    """
    lj = math.log(j)
    return lj + math.log(lj)

def approx_index_averages(n: int, kmax: int, grid: int = 20000) -> Dict[int, float]:
    """
    Approximate averages of m(j)^k over j=3..n using a uniform grid (deterministic).
      avg_k = (1/(n-2)) Σ_{j=3}^n m(j)^k  ≈ average over grid points.

    Returns dict {k: E[m^k]} for k=1..kmax.
    """
    if n < 3:
        raise ValueError("n must be >=3")
    g = max(200, int(grid))
    # deterministic grid over [3, n]
    acc = {k: 0.0 for k in range(1, kmax + 1)}
    for i in range(g):
        j = 3.0 + (n - 3.0) * ((i + 0.5) / g)
        m = mean_profile(j)
        p = m
        acc[1] += p
        for k in range(2, kmax + 1):
            p *= m
            acc[k] += p
    for k in acc:
        acc[k] /= g
    return acc

def toy_expected_metrics(n: int, shape_r: float, kmax: int = 4) -> Tuple[Dict[int, float], Dict[int, float]]:
    """
    Compute expected A_k and B_k for a toy model where:
      conditional on index j, gap ~ Gamma(shape=shape_r, mean=m(j))
    and we pool all j in {3..n} uniformly.

    This is not meant to be a faithful prime model; it is a sanity check.
    """
    av = approx_index_averages(n, kmax=kmax)
    mu1 = av[1]  # because mean(X|j)=m(j)
    A: Dict[int, float] = {}
    B: Dict[int, float] = {1: 0.0}
    ln = math.log(n)

    for k in range(1, kmax + 1):
        if k == 1:
            mu_k = mu1
        else:
            # E[X^k] pooled = k! * R(r,k) * E[m^k]
            mu_k = math.factorial(k) * gamma_ratio(shape_r, k) * av[k]
        A[k] = mu_k / (math.factorial(k) * (ln ** k)) - 1.0

    for k in range(2, kmax + 1):
        # pooled standardized deviation vs exponential at same pooled mean:
        # B_k = mu_k / (k! mu1^k) - 1
        if k == 1:
            continue
        mu_k = math.factorial(k) * gamma_ratio(shape_r, k) * av[k]
        B[k] = mu_k / (math.factorial(k) * (mu1 ** k)) - 1.0

    return A, B


# ============================================================================
# 6) PLOTTING (optional)
# ============================================================================

def maybe_import_matplotlib(cache_dir: Optional[Path] = None):
    """
    Import matplotlib in a way that works in restricted environments.
    """
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ["MPLCONFIGDIR"] = str(cache_dir / "mplconfig")
        os.environ["XDG_CACHE_HOME"] = str(cache_dir / "xdg-cache")
    try:
        import matplotlib  # type: ignore
        matplotlib.use("Agg", force=True)  # Headless backend for batch plot generation.
        import matplotlib.pyplot as plt  # type: ignore
    except Exception as e:
        print(f"[plots] matplotlib import failed: {e}")
        print("[plots] Install deps with: python3 -m pip install -r prime-gap-moments/requirements.txt")
        return None
    return plt

def save_plot(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    fig.clf()

def plot_series(rows: Sequence[MetricsRow], outdir: Path, show: bool = False) -> None:
    plt = maybe_import_matplotlib(cache_dir=outdir / ".plot_cache")
    if plt is None:
        print("[plots] matplotlib not available; skipping plots.")
        return

    xs = [row.loglogn for row in rows]

    # Plot 1: signed A_k
    fig = plt.figure()
    for k in (1, 2, 3, 4):
        ys = [row.A[k] for row in rows]
        plt.plot(xs, ys, marker="o", label=f"A{k}")
    plt.axhline(0.0)
    plt.xlabel("log log n")
    plt.ylabel("A_k (signed)")
    plt.title("Cohen-normalized deviations A_k(n) (signed)")
    plt.legend()
    save_plot(fig, outdir / "A_signed.png")

    # Plot 2: abs(A_k)
    fig = plt.figure()
    for k in (1, 2, 3, 4):
        ys = [abs(row.A[k]) for row in rows]
        plt.plot(xs, ys, marker="o", label=f"|A{k}|")
    plt.xlabel("log log n")
    plt.ylabel("|A_k|")
    plt.title("Apparent 'hierarchy' in |A_k(n)| (note: sensitive to zero crossings)")
    plt.legend()
    save_plot(fig, outdir / "A_abs.png")

    # Plot 3: shape-only B_k
    fig = plt.figure()
    for k in (2, 3, 4):
        ys = [row.B[k] for row in rows]
        plt.plot(xs, ys, marker="o", label=f"B{k}")
    plt.axhline(0.0)
    plt.xlabel("log log n")
    plt.ylabel("B_k (signed)")
    plt.title("Shape-only deviations B_k(n) (mean-standardized)")
    plt.legend()
    save_plot(fig, outdir / "B_signed.png")

    # Plot 4: compare A_k to mean-only prediction (cancellation illustration)
    fig = plt.figure()
    k = 4
    ys_A = [row.A[k] for row in rows]
    ys_mean = [row.A_meanonly[k] for row in rows]
    plt.plot(xs, ys_A, marker="o", label=f"A{k} (observed)")
    plt.plot(xs, ys_mean, marker="o", label=f"A{k} if B{k}=0 (mean-only)")
    plt.axhline(0.0)
    plt.xlabel("log log n")
    plt.ylabel("value")
    plt.title(f"Cancellation demo: observed A{k} vs mean-only prediction")
    plt.legend()
    save_plot(fig, outdir / f"A{k}_vs_mean_only.png")

    # Plot 5: log-space decomposition for k=4
    fig = plt.figure()
    k = 4
    ys_total = [math.log1p(row.A[k]) for row in rows]
    ys_mean_term = [k * math.log1p(row.A[1]) for row in rows]
    ys_shape_term = [math.log1p(row.B[k]) for row in rows]
    plt.plot(xs, ys_total, marker="o", label="log(1 + A4)")
    plt.plot(xs, ys_mean_term, marker="o", label="4·log(1 + A1)")
    plt.plot(xs, ys_shape_term, marker="o", label="log(1 + B4)")
    plt.axhline(0.0)
    plt.xlabel("log log n")
    plt.ylabel("log-factor")
    plt.title("Multiplicative decomposition in log space (k=4)")
    plt.legend()
    save_plot(fig, outdir / "decomposition_log_k4.png")

    # Plot 6: A1 vs correction
    fig = plt.figure()
    ys_A1 = [row.A[1] for row in rows]
    ys_corr = [row.A1_pnt_correction for row in rows]
    plt.plot(xs, ys_A1, marker="o", label="A1 observed")
    plt.plot(xs, ys_corr, marker="o", label="(loglog n - 1)/log n")
    plt.xlabel("log log n")
    plt.ylabel("value")
    plt.title("A1 explained by a next-order mean correction")
    plt.legend()
    save_plot(fig, outdir / "A1_vs_correction.png")

    # Plot 7: alternative mean proxy normalization (Ã_k)
    fig = plt.figure()
    for k in (1, 2, 3, 4):
        ys = [row.A_altmean[k] for row in rows]
        plt.plot(xs, ys, marker="o", label=f"Ã{k}")
    plt.axhline(0.0)
    plt.xlabel("log log n")
    plt.ylabel("Ã_k (signed)")
    plt.title("Alternative normalization using L(n)=log n + log log n - 1")
    plt.legend()
    save_plot(fig, outdir / "A_tilde_altmean.png")

    if show:
        # If user requests interactive display.
        plt.show()


def plot_toy_models(outdir: Path, show: bool = False) -> None:
    """
    Plot toy expected metrics for two models:
      r=1  (Exponential, drift-only)  => should give B_k >= 0
      r=2  (Gamma shape=2, drift+subexp shape) => can give B_k < 0
    """
    plt = maybe_import_matplotlib(cache_dir=outdir / ".plot_cache")
    if plt is None:
        print("[plots] matplotlib not available; skipping toy-model plots.")
        return

    # Use modest n range for fast deterministic evaluation
    ns = [int(10 ** x) for x in [3, 3.5, 4, 4.5, 5, 5.5, 6]]
    xs = [safe_loglog(n) for n in ns]

    series = {}
    for rshape in (1.0, 2.0):
        A_list = []
        B_list = []
        for n in ns:
            A, B = toy_expected_metrics(n=n, shape_r=rshape, kmax=4)
            A_list.append(A)
            B_list.append(B)
        series[rshape] = (A_list, B_list)

    # Toy plot: B_k signs
    fig = plt.figure()
    for rshape, (_, Bs) in series.items():
        for k in (2, 3, 4):
            ys = [b[k] for b in Bs]
            plt.plot(xs, ys, marker="o", label=f"shape r={rshape:g}, B{k}")
    plt.axhline(0.0)
    plt.xlabel("log log n")
    plt.ylabel("B_k (expected, toy)")
    plt.title("Toy sanity: drift-only (r=1) implies B_k ≥ 0; subexp (r>1) can yield B_k < 0")
    plt.legend()
    save_plot(fig, outdir / "toy_Bk_signs.png")

    # Toy plot: |A_k| reversal check
    fig = plt.figure()
    for rshape, (As, _) in series.items():
        k = 4
        ys = [abs(a[k]) for a in As]
        plt.plot(xs, ys, marker="o", label=f"shape r={rshape:g}, |A4|")
    plt.xlabel("log log n")
    plt.ylabel("|A4| (expected, toy)")
    plt.title("Toy: |A4| scale under drift-only vs sub-exponential shape")
    plt.legend()
    save_plot(fig, outdir / "toy_absA4.png")

    if show:
        plt.show()


# ============================================================================
# 7) MAIN
# ============================================================================

def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Prime gap moment 'white paper' diagnostics (A_k vs B_k).")
    ap.add_argument("--outdir", type=str, default="whitepaper_out", help="Output directory for plots / markdown report.")
    ap.add_argument("--no-plots", action="store_true", help="Do not generate plots.")
    ap.add_argument("--show", action="store_true", help="Display plots interactively (if supported).")
    ap.add_argument("--gaps-file", type=str, default="", help="Optional path to a file of raw gap values.")
    args = ap.parse_args(list(argv) if argv is not None else None)

    outdir = Path(args.outdir)

    # Cohen-table analysis
    rows = compute_metrics_from_cohen_table(COHEN_TABLE)
    report = build_whitepaper_report(rows)
    print(report.text())

    # Write markdown report and a simple CSV of derived metrics
    report_path = outdir / "whitepaper_report.md"
    report.write_to(report_path)

    csv_path = outdir / "cohen_derived_metrics.csv"
    csv_lines = [
        "n,logn,loglogn,A1,A2,A3,A4,B2,B3,B4,A1_corr,Atilde1,Atilde2,Atilde3,Atilde4",
    ]
    for row in rows:
        csv_lines.append(
            ",".join(
                [
                    fmt(row.n, 8),
                    fmt(row.logn, 10),
                    fmt(row.loglogn, 10),
                    fmt(row.A[1], 10),
                    fmt(row.A[2], 10),
                    fmt(row.A[3], 10),
                    fmt(row.A[4], 10),
                    fmt(row.B[2], 10),
                    fmt(row.B[3], 10),
                    fmt(row.B[4], 10),
                    fmt(row.A1_pnt_correction, 10),
                    fmt(row.A_altmean[1], 10),
                    fmt(row.A_altmean[2], 10),
                    fmt(row.A_altmean[3], 10),
                    fmt(row.A_altmean[4], 10),
                ]
            )
        )
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    # Optional: raw gaps file analysis
    if args.gaps_file.strip():
        gaps_path = Path(args.gaps_file).expanduser()
        gaps = load_gaps(gaps_path)

        print("\n" + "=" * 90)
        print("RAW GAP FILE ANALYSIS")
        print("=" * 90)
        print(f"Loaded {len(gaps)} gaps from: {gaps_path}")

        fractions = [1.0, 0.10, 0.01]
        multiples = [2.0, 3.0, 4.0, 5.0]
        for frac in fractions:
            w = windowed(gaps, keep_last_fraction=frac)
            A, B, L = compute_A_B_for_gap_sample(w, denom_log_n=None, max_k=4)
            print("\n" + "-" * 90)
            print(f"Window: last {frac*100:.2f}%  (m={len(w)} samples), denom log(m)={L:.6f}")
            print(f"A1..A4: {', '.join(f'A{k}={A[k]:+.6f}' for k in range(1,5))}")
            print(f"B2..B4: {', '.join(f'B{k}={B[k]:+.6f}' for k in range(2,5))}")
            tail = tail_exceedance(w, multiples=multiples)
            print("Tail exceedance P(X >= m·mean): " + ", ".join(f"m={m:g}:{tail[m]:.6f}" for m in multiples))

    # Plots
    if not args.no_plots:
        plot_series(rows, outdir=outdir, show=args.show)
        plot_toy_models(outdir=outdir, show=args.show)
        print(f"\n[plots] Wrote plots and report to: {outdir.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
