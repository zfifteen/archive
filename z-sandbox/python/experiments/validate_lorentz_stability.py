#!/usr/bin/env python3
import argparse, sys, math, numpy as np
import pandas as pd
from pathlib import Path

def sieve_primes(n):
    n = int(n)
    sieve = np.ones(n+1, dtype=bool)
    sieve[:2] = False
    limit = int(n**0.5) + 1
    for p in range(2, limit):
        if sieve[p]:
            sieve[p*p:n+1:p] = False
    return np.flatnonzero(sieve)

def lorentz_gamma_ln_p(lnp, beta=30.34):
    # γ = 1 + 0.5 * (L / (e^4 + βL))^2
    L = lnp
    denom = (math.e**4) + beta * L
    return 1.0 + 0.5 * (L/denom)**2

def bootstrap_stat(x, rng, fn=np.mean, B=2000):
    n = x.size
    out = np.empty(B, dtype=float)
    for b in range(B):
        idx = rng.integers(0, n, size=n)
        out[b] = fn(np.abs(x[idx]))
    return out

def pearson_r(x, y):
    return np.corrcoef(x, y)[0,1]

def spearman_r(x, y):
    # no external deps; rank via argsort twice
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    return pearson_r(rx.astype(float), ry.astype(float))

def main():
    ap = argparse.ArgumentParser(description="Lorentz dilation stability validation (pre/post-γ).")
    ap.add_argument("--max_n", type=int, default=10_000_000)
    ap.add_argument("--tail_min", type=int, default=1_000_000)
    ap.add_argument("--beta", type=float, default=30.34)
    ap.add_argument("--baseline", type=str, required=True, help="CSV with columns p,k,err_baseline")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--boots", type=int, default=2000)
    ap.add_argument("--report", type=str, default="lorentz_stability_report.csv")
    # Gates (tune as you like)
    ap.add_argument("--gate_impr_mean_pct", type=float, default=0.04, help="Require ≥ this % mean|err| improvement")
    ap.add_argument("--gate_corr_drop", type=float, default=0.00, help="Require ≥ this drop in Pearson corr(|err|, ln p)")
    ap.add_argument("--gate_ci_positive", action="store_true", help="Require 95%% CI of improvement > 0")
    args = ap.parse_args()

    print(f"Generating primes up to {args.max_n:,}...")
    primes = sieve_primes(args.max_n)
    print(f"Generated {primes.size:,} primes.")

    lnp = np.log(primes.astype(np.float64))
    gamma = lorentz_gamma_ln_p(lnp, beta=args.beta)

    # Tail
    tail_mask = primes >= args.tail_min
    primes_t = primes[tail_mask]
    lnp_t    = lnp[tail_mask]
    gamma_t  = gamma[tail_mask]
    print(f"Tail analysis: {primes_t.size:,} primes with p ≥ {args.tail_min:,}.")

    # Load baseline
    df = pd.read_csv(args.baseline)
    cols = set(c.lower() for c in df.columns)
    if not {"p","k","err_baseline"} <= cols:
        print("Baseline CSV must have columns: p,k,err_baseline", file=sys.stderr)
        sys.exit(1)

    # Align by p on tail
    df["p"] = df["p"].astype(np.int64)
    base_tail = pd.DataFrame({"p": primes_t})
    merged = base_tail.merge(df[["p","k","err_baseline"]], on="p", how="inner")

    if merged.empty:
        print("No overlap between baseline CSV and computed tail primes.", file=sys.stderr)
        sys.exit(1)

    # Sort by p to match order
    merged.sort_values("p", inplace=True)
    # Reindex gamma_t to merged.p
    idx = np.searchsorted(primes_t, merged["p"].values)
    gamma_m = gamma_t[idx]
    lnp_m   = np.log(merged["p"].values.astype(np.float64))

    err_base = merged["err_baseline"].to_numpy(dtype=np.float64)
    err_dil  = err_base / gamma_m

    # Stats
    rng = np.random.default_rng(args.seed)
    base_mean = bootstrap_stat(err_base, rng, np.mean, args.boots)
    dil_mean  = bootstrap_stat(err_dil,  rng, np.mean, args.boots)
    base_med  = bootstrap_stat(err_base, rng, np.median, args.boots)
    dil_med   = bootstrap_stat(err_dil,  rng, np.median, args.boots)
    base_p95  = bootstrap_stat(err_base, rng, lambda z: np.percentile(np.abs(z),95), args.boots)
    dil_p95   = bootstrap_stat(err_dil,  rng, lambda z: np.percentile(np.abs(z),95), args.boots)

    impr_mean = 100.0*(base_mean - dil_mean)/base_mean
    impr_med  = 100.0*(base_med  - dil_med )/base_med
    impr_p95  = 100.0*(base_p95  - dil_p95 )/base_p95

    mean_impr_mu = impr_mean.mean()
    mean_impr_lo, mean_impr_hi = np.percentile(impr_mean, [2.5, 97.5])
    med_impr_mu  = impr_med.mean()
    med_impr_lo, med_impr_hi   = np.percentile(impr_med,  [2.5, 97.5])
    p95_impr_mu  = impr_p95.mean()
    p95_impr_lo, p95_impr_hi   = np.percentile(impr_p95,  [2.5, 97.5])

    # Correlation with scale (absolute errors)
    ab = np.abs(err_base)
    ad = np.abs(err_dil)

    rP_base = pearson_r(lnp_m, ab)
    rP_dil  = pearson_r(lnp_m, ad)
    rS_base = spearman_r(lnp_m, ab)
    rS_dil  = spearman_r(lnp_m, ad)

    print("\n=== Stability Results (tail) ===")
    print(f"Mean |err| improvement: {mean_impr_mu:.3f}%  (95% CI [{mean_impr_lo:.3f}%, {mean_impr_hi:.3f}%])")
    print(f"Median |err| improvement: {med_impr_mu:.3f}% (95% CI [{med_impr_lo:.3f}%, {med_impr_hi:.3f}%])")
    print(f"P95 |err| improvement: {p95_impr_mu:.3f}%    (95% CI [{p95_impr_lo:.3f}%, {p95_impr_hi:.3f}%])")

    print(f"\nPearson corr(|err|, ln p): before={rP_base:.4f}, after={rP_dil:.4f}, Δ={rP_base-rP_dil:.4f}")
    print(f"Spearman corr(|err|, ln p): before={rS_base:.4f}, after={rS_dil:.4f}, Δ={rS_base-rS_dil:.4f}")

    # Gates
    ok = True
    if mean_impr_mu < args.gate_impr_mean_pct:
        print(f"✗ Mean improvement {mean_impr_mu:.2f}% < gate {args.gate_impr_mean_pct:.2f}%"); ok = False
    if (rP_base - rP_dil) < args.gate_corr_drop:
        print(f"✗ Corr drop {rP_base - rP_dil:.3f} < gate {args.gate_corr_drop:.3f} (Pearson)"); ok = False
    if args.gate_ci_positive and mean_impr_lo <= 0:
        print("✗ 95% CI for mean improvement includes 0"); ok = False

    if ok:
        print("✓ Stability gates PASSED.")
    else:
        print("✗ Stability gates FAILED.")

    # Save report
    rep = {
        "tail_min": args.tail_min,
        "beta": args.beta,
        "n_tail_overlap": int(merged.shape[0]),
        "mean_impr_mu_pct": mean_impr_mu,
        "mean_impr_lo_pct": mean_impr_lo,
        "mean_impr_hi_pct": mean_impr_hi,
        "median_impr_mu_pct": med_impr_mu,
        "median_impr_lo_pct": med_impr_lo,
        "median_impr_hi_pct": med_impr_hi,
        "p95_impr_mu_pct": p95_impr_mu,
        "p95_impr_lo_pct": p95_impr_lo,
        "p95_impr_hi_pct": p95_impr_hi,
        "pearson_before": rP_base,
        "pearson_after": rP_dil,
        "pearson_delta": rP_base - rP_dil,
        "spearman_before": rS_base,
        "spearman_after": rS_dil,
        "spearman_delta": rS_base - rS_dil,
        "gate_impr_mean_pct": args.gate_impr_mean_pct,
        "gate_corr_drop": args.gate_corr_drop,
        "gate_ci_positive": bool(args.gate_ci_positive),
        "gates_passed": bool(ok),
    }
    pd.DataFrame([rep]).to_csv(args.report, index=False)
    print(f"\nWrote report → {args.report}")

if __name__ == "__main__":
    main()