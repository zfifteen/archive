#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
python bruhtus43s_theorem.py --N 1000000 --bins 20 --k 0.3

"Bruhtus43's Theorem" (satire): If you ignore the κ exponent and/or use equal-width bins
after applying y = x^κ with κ<1, you will 'discover' density where none exists; the spike
is an artifact of your bin choice, not signal. Remedy: use quantile bins or weight by
the Jacobian so the null is flat for any κ.

Run:
    python bruhtus43s_theorem.py --N 1000000 --bins 20 --k 0.3

Outputs a few lines that (a) reproduce the last-bin spike with equal-width bins,
(b) show it on both deterministic U = {n/φ} and random U ~ Uniform(0,1),
and (c) make it disappear with quantile bins (κ-invariant test).
"""

import numpy as np

def enhancement_equal_bins(u, k, m, side='right'):
    """Return (ratio_vs_uniform, counts) for equal-width bins in v = u**k."""
    v = u**k
    counts, _ = np.histogram(v, bins=m, range=(0.0, 1.0))
    bin_idx = (m - 1) if side == 'right' else 0
    ratio = counts[bin_idx] / (len(v) / m)
    return float(ratio), counts

def theoretical_ratio(m, k, side='right'):
    """Closed-form expected ratio for the edge bin under the null (U ~ Uniform[0,1])."""
    if side == 'right':
        # Rightmost bin [1-1/m, 1]; for k<1 this is the inflated bin.
        return float(m * (1 - (1 - 1/m)**(1/k)))
    else:
        # Leftmost bin [0, 1/m]; for k>1 this is the inflated bin.
        return float(m * (1/m)**(1/k))

def quantile_edges(k, m):
    """Quantile-bin edges that make the null flat for ANY k: q_j = (j/m)**k."""
    j = np.arange(m + 1, dtype=float)
    return (j / m) ** k

def counts_in_bins(v, edges):
    counts, _ = np.histogram(v, bins=edges)
    return counts

def main(N=1_000_000, m=20, k=0.3, seed=123):
    rng = np.random.default_rng(seed)
    # Golden ratio φ
    phi = (1 + 5**0.5) / 2

    # Deterministic sequence U = frac(n / φ)
    n = np.arange(1, N + 1, dtype=np.float64)
    u_det = np.modf(n / phi)[0]

    # Random uniform for comparison
    u_rand = rng.random(N)

    print("@bruhtus43\n")
    print("Thanks for the feedback! The “fundamental mistake” you cite isn’t a mistake—it’s the point.")
    print(f"k<1 is a deliberate contrast filter. We never assume θ′ is uniform.\n")
    print(f"Parameters: N={N:,}, bins={m}, k={k}\n")

    print("--- Bruhtus43's Theorem (tongue-in-cheek) ---")
    print("If you drop κ or keep κ<1 but use equal-width bins on y=x^κ,")
    print("you will 'discover' a density spike at the edge that your binning created.\n")

    # Equal-width bins: artifact appears (rightmost bin for k<1)
    for label, u in [("deterministic U = {n/φ}", u_det), ("random U ~ Uniform(0,1)", u_rand)]:
        ratio, _ = enhancement_equal_bins(u, k, m, side='right')
        theo = theoretical_ratio(m, k, side='right')
        print(f"[Equal-width bins] {label}: last-bin ratio vs uniform = {ratio:.3f} (theory ≈ {theo:.3f})")

    # Quantile bins: null is flat for any k (κ-invariant)
    qe = quantile_edges(k, m)
    for label, u in [("deterministic U = {n/φ}", u_det), ("random U ~ Uniform(0,1)", u_rand)]:
        v = u**k
        qc = counts_in_bins(v, qe)
        deviation = (qc - (len(v) / m)) / (len(v) / m)
        print(f"[Quantile bins]    {label}: max relative deviation from flat = {np.max(np.abs(deviation)):.4f}")

    # Mirror artifact for large k>1: first bin spikes (purely binning again)
    k_big = 100.0
    ratio_left, _ = enhancement_equal_bins(u_det, k_big, m, side='left')
    theo_left = theoretical_ratio(m, k_big, side='left')
    print(f"\n[Equal-width bins] k={k_big:.0f}: FIRST-bin ratio vs uniform (deterministic) = {ratio_left:.3f} (theory ≈ {theo_left:.3f})")
    print("Moral: equal-width bin spikes flip sides when κ flips regime—because it's the bins, not a signal.\n")

    print("QED (with jokes): The spike is a binning artifact. Use quantile bins or Jacobian weighting to test real structure.\n")
    print("P.S. If you want to compare primes vs composites, do it here—AFTER the κ-invariant step—so κ can't fake wins.")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Demonstrate the κ<1 equal-width bin artifact and the κ-invariant fix.")
    ap.add_argument("--N", type=int, default=1_000_000, help="number of points")
    ap.add_argument("--bins", type=int, default=20, help="number of bins")
    ap.add_argument("--k", type=float, default=0.3, help="contrast exponent κ")
    ap.add_argument("--seed", type=int, default=123, help="random seed")
    args = ap.parse_args()
    main(args.N, args.bins, args.k, args.seed)
