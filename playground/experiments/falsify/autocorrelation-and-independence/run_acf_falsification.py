#!/usr/bin/env python3
"""
Falsifying "Strong Autocorrelation" in Prime Gaps
Implementation of TECH-SPEC.md
"""

import os
import sys
import json
import time
import argparse
import numpy as np
# import pandas as pd # Removed unused import
import matplotlib.pyplot as plt
# import seaborn as sns # Removed unused import
from pathlib import Path
from datetime import datetime
from scipy import stats
from statsmodels.tsa.stattools import acf, pacf

# Add PR-0003 src to path for prime generation
PR0003_PATH = Path(__file__).parent.parent.parent / "PR-0003_prime_log_gap_optimized"
sys.path.insert(0, str(PR0003_PATH / "src"))

try:
    from prime_generator import generate_primes_to_limit, compute_gaps
except ImportError:
    print("Error: Could not import prime_generator from PR-0003. Ensure the path is correct.")
    sys.exit(1)

def compute_hurst_rs(data, return_plot_data=False):
    """Estimate Hurst exponent using R/S analysis."""
    n = len(data)
    if n < 100:
        if return_plot_data:
            return np.nan, None, None
        return np.nan
    
    max_k = int(np.floor(np.log2(n)))
    rs_values = []
    n_values = []
    
    for k in range(6, max_k):
        m = 2**k
        
        # Divide into blocks
        num_blocks = n // m
        rs_block_values = []
        for i in range(num_blocks):
            block = data[i*m : (i+1)*m]
            mean_adj = block - np.mean(block)
            cum_sum = np.cumsum(mean_adj)
            r = np.max(cum_sum) - np.min(cum_sum)
            s = np.std(block)
            if s > 0:
                rs_block_values.append(r / s)
        
        if rs_block_values:
            rs_values.append(np.mean(rs_block_values))
            n_values.append(m)
    
    if len(rs_values) < 2:
        if return_plot_data:
            return np.nan, None, None
        return np.nan
        
    coeffs = np.polyfit(np.log(n_values), np.log(rs_values), 1)
    hurst = coeffs[0]
    
    if return_plot_data:
        return hurst, n_values, rs_values
    return hurst

def compute_dfa(data, scales=None):
    """Detrended Fluctuation Analysis (DFA)."""
    if scales is None:
        scales = np.logspace(1, np.log10(len(data)//4), num=20, dtype=int)
    
    # Integrate the series
    y = np.cumsum(data - np.mean(data))
    
    fluctuations = []
    for scale in scales:
        n_windows = len(y) // scale
        rms = []
        for i in range(n_windows):
            window = y[i*scale : (i+1)*scale]
            x = np.arange(scale)
            coeff = np.polyfit(x, window, 1)
            trend = np.polyval(coeff, x)
            rms.append(np.sqrt(np.mean((window - trend)**2)))
        fluctuations.append(np.mean(rms))
        
    coeffs = np.polyfit(np.log(scales), np.log(fluctuations), 1)
    return coeffs[0]

def bootstrap_metric(data, metric_func, n_iterations=1000, block_size=100):
    """Generic block bootstrap for any metric."""
    n = len(data)
    n_blocks = n // block_size
    samples = []
    
    for _ in range(n_iterations):
        indices = np.random.randint(0, n - block_size, size=n_blocks)
        bootstrap_sample = np.concatenate([data[idx : idx + block_size] for idx in indices])
        
        try:
            val = metric_func(bootstrap_sample)
            if not np.isnan(val):
                samples.append(val)
        except Exception:
            pass
            
    if not samples:
        return np.nan, np.nan, np.nan, np.nan
        
    return np.mean(samples), np.std(samples), np.percentile(samples, 2.5), np.percentile(samples, 97.5)

def permutation_test_acf(data, lag=1, n_permutations=10000):
    """Compute p-value for ACF(lag) using permutation test."""
    obs_rho = np.corrcoef(data[:-lag], data[lag:])[0, 1]
    
    count = 0
    perm_data = data.copy()
    for _ in range(n_permutations):
        np.random.shuffle(perm_data)
        perm_rho = np.corrcoef(perm_data[:-lag], perm_data[lag:])[0, 1]
        if perm_rho >= obs_rho:
            count += 1
            
    return count / n_permutations

def randomized_sieve_simulation(base_log_gaps, epsilon=0.05, delta=0.05):
    """
    Simulate gaps by starting with independent gaps and adding sieve-like perturbations.
    """
    # Start with independent draws from empirical distribution
    n = len(base_log_gaps)
    # Convert log-gaps to regular gaps for simulation
    gaps = np.exp(np.random.choice(base_log_gaps, size=n, replace=True))
    
    # We use a list for simulation as we change length
    current_gaps = gaps.tolist()
    
    # 1. Merging (removing primes)
    if delta > 0:
        merged_gaps = []
        skip_next = False
        for i in range(len(current_gaps)):
            if skip_next:
                skip_next = False
                continue
            
            # Check if we can merge with next
            if i < len(current_gaps) - 1 and np.random.random() < delta:
                # Merge with next (regular gaps are additive)
                merged_gaps.append(current_gaps[i] + current_gaps[i+1])
                skip_next = True
            else:
                merged_gaps.append(current_gaps[i])
        current_gaps = merged_gaps

    # 2. Splitting (adding pseudo-primes)
    if epsilon > 0:
        split_gaps = []
        for g in current_gaps:
            if np.random.random() < epsilon:
                # Split gap randomly
                u = np.random.uniform(0.1, 0.9)
                split_gaps.append(g * u)
                split_gaps.append(g * (1-u))
            else:
                split_gaps.append(g)
        current_gaps = split_gaps
        
    # Return roughly N gaps, converted back to log-gaps
    result_gaps = np.array(current_gaps[:n])
    # Avoid log(0) if any gap became 0 (shouldn't happen with uniform(0.1, 0.9))
    result_gaps[result_gaps <= 0] = 1e-10 
    return np.log(result_gaps)

def run_falsification(args):
    print(f"Starting falsification protocol with seed {args.seed}...")
    np.random.seed(args.seed)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ranges = []
    for r_str in args.ranges.split(','):
        p_min, p_max = map(float, r_str.split(':'))
        ranges.append((int(p_min), int(p_max)))
        
    all_results = []
    sample_log_gaps = None
    
    for p_min, p_max in ranges:
        range_id = f"{p_min:.0e}_{p_max:.0e}"
        print(f"\nProcessing range: {range_id}")
        
        # 1. Data Preparation
        primes = generate_primes_to_limit(p_max, backend=args.prime_backend)
        mask = (primes >= p_min) & (primes <= p_max)
        range_primes = primes[mask]
        
        if len(range_primes) < 100000:
            print(f"Warning: Too few primes in range {range_id} ({len(range_primes)} < 100,000). Results may be unstable.")
            if len(range_primes) < 1000:
                print("Skipping range due to insufficient data.")
                continue
            
        gaps_data = compute_gaps(range_primes)
        log_gaps = gaps_data["log_gaps"]
        
        if args.detrend:
            print("Detrending log-gaps (linear)...")
            x = np.arange(len(log_gaps))
            coeffs = np.polyfit(x, log_gaps, 1)
            trend = np.polyval(coeffs, x)
            log_gaps = log_gaps - trend
        
        if sample_log_gaps is None:
            sample_log_gaps = log_gaps
        
        n_gaps = len(log_gaps)
        print(f"Extracted {n_gaps:,} log-gaps.")
        
        # 2. ACF / PACF Estimation
        acf_vals = acf(log_gaps, nlags=args.max_lag, fft=True)
        pacf_vals = pacf(log_gaps, nlags=args.max_lag)
        
        # 3. Significance & Robustness
        print("Running permutation test and bootstrap...")
        p_val = permutation_test_acf(log_gaps, lag=1, n_permutations=args.permutations)
        
        # Bootstrap ACF(1)
        acf1_func = lambda d: np.corrcoef(d[:-1], d[1:])[0, 1] if len(d) > 1 else np.nan
        mean_boot, se_boot, ci_low, ci_high = bootstrap_metric(
            log_gaps, acf1_func, n_iterations=args.bootstrap_iterations, block_size=args.block_size
        )
        
        # 4. Long-range dependence
        hurst, h_n, h_rs = compute_hurst_rs(log_gaps, return_plot_data=True)
        
        # Bootstrap Hurst (limit iterations for speed)
        hurst_func = lambda d: compute_hurst_rs(d)
        h_mean_boot, h_se_boot, h_ci_low, h_ci_high = bootstrap_metric(
            log_gaps, hurst_func, n_iterations=min(args.bootstrap_iterations, 100), block_size=args.block_size
        )
        
        dfa_alpha = compute_dfa(log_gaps)
        
        # 5. Windowing analysis
        window_size = args.window_size
        n_windows = (n_gaps - window_size) // (window_size // 2) + 1
        window_acf1s = []
        
        if n_windows > 1:
            for i in range(n_windows):
                start = i * (window_size // 2)
                end = start + window_size
                if end > n_gaps: break
                w_gaps = log_gaps[start:end]
                w_acf1 = np.corrcoef(w_gaps[:-1], w_gaps[1:])[0, 1]
                window_acf1s.append(w_acf1)
        
        range_res = {
            "range_id": range_id,
            "p_min": p_min,
            "p_max": p_max,
            "n_gaps": n_gaps,
            "ACF_1": float(acf_vals[1]),
            "ACF_1_boot_mean": float(mean_boot),
            "ACF_1_SE": float(se_boot),
            "ACF_1_95CI_lower": float(ci_low),
            "ACF_1_95CI_upper": float(ci_high),
            "permutation_p_value": float(p_val),
            "hurst_exponent": float(hurst),
            "hurst_95CI_lower": float(h_ci_low),
            "hurst_95CI_upper": float(h_ci_high),
            "dfa_alpha": float(dfa_alpha),
            "window_acf1_mean": float(np.mean(window_acf1s)) if window_acf1s else float(acf_vals[1]),
            "window_acf1_std": float(np.std(window_acf1s)) if window_acf1s else 0.0,
            "window_acf1s": [float(x) for x in window_acf1s],
            "acf_values": acf_vals.tolist(),
            "pacf_values": pacf_vals.tolist()
        }
        all_results.append(range_res)
        
        # 6. Visualizations for this range
        plot_range_results(range_res, output_dir)
        if h_n is not None:
            plot_hurst(h_n, h_rs, hurst, range_id, output_dir)
        if window_acf1s:
            plot_window_distribution(window_acf1s, range_id, output_dir)

    # 7. Null Model Comparisons
    null_results = run_null_models(all_results, args, sample_log_gaps)
    
    # 8. Cross-range visualizations
    plot_cross_range_comparison(all_results, null_results, output_dir)
    
    # 9. Final Report & Falsification Check
    generate_report(all_results, null_results, output_dir)
    
    # Save machine-readable results
    with open(output_dir / "results.json", "w") as f:
        json.dump({
            "ranges": all_results,
            "null_models": null_results,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "args": vars(args)
            }
        }, f, indent=2)

def run_null_models(range_results, args, sample_data=None):
    null_res = []
    if not range_results: return []
    
    template = range_results[0]
    n_gaps = template["n_gaps"]
    obs_acf1 = template["ACF_1"]
    
    # Cramer Model
    if "cramer" in args.null_models:
        print("Running Cramer null model...")
        cramer_acf1s = []
        for _ in range(100):
            if sample_data is not None:
                # Sample from empirical distribution
                sim = np.random.choice(sample_data, size=n_gaps, replace=True)
            else:
                sim = np.random.normal(0, 1, n_gaps)
            cramer_acf1s.append(np.corrcoef(sim[:-1], sim[1:])[0, 1])
        
        null_res.append({
            "model_type": "cramer",
            "ACF_1_null_mean": float(np.mean(cramer_acf1s)),
            "ACF_1_null_sd": float(np.std(cramer_acf1s)),
            "ACF_1_null_95CI_lower": float(np.percentile(cramer_acf1s, 2.5)),
            "ACF_1_null_95CI_upper": float(np.percentile(cramer_acf1s, 97.5)),
            "can_match_observed": bool(np.percentile(cramer_acf1s, 99) >= obs_acf1),
            "acf1_values": [float(x) for x in cramer_acf1s]
        })

    # AR(1) Model
    if "ar1" in args.null_models:
        print("Running AR(1) null model...")
        phi = obs_acf1
        ar1_acf1s = []
        for _ in range(100):
            sim = np.zeros(n_gaps)
            sim[0] = np.random.normal()
            for i in range(1, n_gaps):
                sim[i] = phi * sim[i-1] + np.random.normal()
            ar1_acf1s.append(np.corrcoef(sim[:-1], sim[1:])[0, 1])
            
        null_res.append({
            "model_type": "ar1",
            "ACF_1_null_mean": float(np.mean(ar1_acf1s)),
            "ACF_1_null_sd": float(np.std(ar1_acf1s)),
            "ACF_1_null_95CI_lower": float(np.percentile(ar1_acf1s, 2.5)),
            "ACF_1_null_95CI_upper": float(np.percentile(ar1_acf1s, 97.5)),
            "can_match_observed": True,
            "acf1_values": [float(x) for x in ar1_acf1s]
        })

    # Sieve Model
    if "sieve" in args.null_models:
        print(f"Running Sieve null model (epsilon={args.sieve_epsilon}, delta={args.sieve_delta})...")
        sieve_acf1s = []
        for _ in range(100):
            if sample_data is not None:
                sim = randomized_sieve_simulation(sample_data, epsilon=args.sieve_epsilon, delta=args.sieve_delta)
            else:
                # Fallback if no sample data (should not happen if ranges exist)
                sim = randomized_sieve_simulation(np.random.exponential(10, n_gaps), epsilon=args.sieve_epsilon, delta=args.sieve_delta)
            
            if len(sim) > 1:
                sieve_acf1s.append(np.corrcoef(sim[:-1], sim[1:])[0, 1])
            else:
                sieve_acf1s.append(0)
            
        null_res.append({
            "model_type": "sieve",
            "ACF_1_null_mean": float(np.mean(sieve_acf1s)),
            "ACF_1_null_sd": float(np.std(sieve_acf1s)),
            "ACF_1_null_95CI_lower": float(np.percentile(sieve_acf1s, 2.5)),
            "ACF_1_null_95CI_upper": float(np.percentile(sieve_acf1s, 97.5)),
            "can_match_observed": bool(np.percentile(sieve_acf1s, 99) >= obs_acf1),
            "acf1_values": [float(x) for x in sieve_acf1s]
        })

    return null_res

def plot_range_results(res, output_dir):
    range_id = res["range_id"]
    
    # ACF Plot
    plt.figure(figsize=(10, 6))
    lags = np.arange(len(res["acf_values"]))
    plt.bar(lags, res["acf_values"], color='skyblue', edgecolor='navy')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title(f"ACF for Range {range_id}\nACF(1) = {res['ACF_1']:.4f}")
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(output_dir / f"acf_{range_id}.png")
    plt.close()

    # PACF Plot
    plt.figure(figsize=(10, 6))
    lags = np.arange(len(res["pacf_values"]))
    plt.bar(lags, res["pacf_values"], color='lightgreen', edgecolor='darkgreen')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title(f"PACF for Range {range_id}")
    plt.xlabel("Lag")
    plt.ylabel("Partial Autocorrelation")
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(output_dir / f"pacf_{range_id}.png")
    plt.close()

def plot_hurst(n_values, rs_values, hurst, range_id, output_dir):
    plt.figure(figsize=(8, 6))
    plt.loglog(n_values, rs_values, 'o', label='R/S')
    
    # Fit line for visualization
    coeffs = np.polyfit(np.log(n_values), np.log(rs_values), 1)
    fit_y = np.exp(coeffs[1]) * np.power(n_values, coeffs[0])
    plt.loglog(n_values, fit_y, '-', label=f'Fit (H={hurst:.3f})')
    
    plt.title(f"Hurst Exponent Analysis (R/S) - Range {range_id}")
    plt.xlabel("n (window size)")
    plt.ylabel("R/S")
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.savefig(output_dir / f"hurst_{range_id}.png")
    plt.close()

def plot_window_distribution(window_acf1s, range_id, output_dir):
    plt.figure(figsize=(10, 6))
    plt.hist(window_acf1s, bins=30, color='purple', alpha=0.7, edgecolor='black')
    plt.title(f"Distribution of ACF(1) across Windows - Range {range_id}")
    plt.xlabel("ACF(1)")
    plt.ylabel("Frequency")
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(output_dir / f"window_dist_{range_id}.png")
    plt.close()

def plot_cross_range_comparison(all_results, null_results, output_dir):
    if not all_results: return
    
    # ACF Comparison
    plt.figure(figsize=(12, 8))
    for res in all_results:
        lags = np.arange(len(res["acf_values"]))
        plt.plot(lags, res["acf_values"], label=f"Range {res['range_id']}")
    
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title("ACF Comparison Across Ranges")
    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(output_dir / "acf_comparison.png")
    plt.close()
    
    # Null Model Comparison Boxplot
    plt.figure(figsize=(12, 8))
    data = []
    labels = []
    
    # Observed
    data.append([r["ACF_1"] for r in all_results])
    labels.append("Observed")
    
    # Null models
    for nr in null_results:
        if "acf1_values" in nr:
            data.append(nr["acf1_values"])
            labels.append(nr["model_type"])
    
    plt.boxplot(data, labels=labels)
    plt.title("ACF(1) Comparison: Observed vs Null Models")
    plt.ylabel("ACF(1)")
    plt.savefig(output_dir / "null_model_comparison.png")
    plt.close()

def generate_report(all_results, null_results, output_dir):
    if not all_results:
        return
        
    acf1s = [r["ACF_1"] for r in all_results]
    mean_acf1 = np.mean(acf1s)
    var_acf1 = np.var(acf1s)
    
    # Falsification Logic
    falsified = False
    reasons = []
    
    # Spec: Mean ACF(1) across ranges: 0.75 <= mean <= 0.85
    if not (0.75 <= mean_acf1 <= 0.85):
        falsified = True
        reasons.append(f"Mean ACF(1) {mean_acf1:.4f} is outside [0.75, 0.85]")
        
    if var_acf1 > 0.05**2:
        falsified = True
        reasons.append(f"Variance of ACF(1) {var_acf1:.6f} exceeds threshold {0.05**2}")
        
    for r in all_results:
        if r["permutation_p_value"] > 0.05:
            falsified = True
            reasons.append(f"Range {r['range_id']} not statistically significant (p={r['permutation_p_value']})")

    # Check Null Models (Cramer and Sieve only for falsification of existence)
    for n in null_results:
        if n['model_type'] in ['cramer', 'sieve'] and n['can_match_observed']:
             falsified = True
             reasons.append(f"Null model '{n['model_type']}' can match observed ACF(1).")

    verdict = "FALSIFIED" if falsified else "CONFIRMED"
    summary_text = "Reasons for falsification:" if falsified else "The claim ACF(1) ≈ 0.8 is robust across tested ranges."
    reasons_text = "\n".join([f"- {r}" for r in reasons]) if reasons else ""

    report = f"""# Falsification Report: Strong Autocorrelation in Prime Gaps

## Summary Verdict
**{verdict}**

{summary_text}
{reasons_text}

## Per-Range Estimates
| Range | ACF(1) | SE | 95% CI (Bootstrap) | p-value | Hurst | Hurst 95% CI | DFA Alpha |
|-------|--------|----|-------------------|---------|-------|--------------|-----------|
"""
    for r in all_results:
        report += f"| {r['range_id']} | {r['ACF_1']:.4f} | {r['ACF_1_SE']:.4f} | [{r['ACF_1_95CI_lower']:.4f}, {r['ACF_1_95CI_upper']:.4f}] | {r['permutation_p_value']:.4f} | {r['hurst_exponent']:.4f} | [{r['hurst_95CI_lower']:.4f}, {r['hurst_95CI_upper']:.4f}] | {r['dfa_alpha']:.4f} |\n"
        
    report += f"""
## Cross-Range Consistency
- **Mean ACF(1)**: {mean_acf1:.4f}
- **Variance ACF(1)**: {var_acf1:.6f}

## Null Model Comparison
"""
    for n in null_results:
        report += f"- **{n['model_type']}**: Mean ACF(1) = {n['ACF_1_null_mean']:.4f}, Match Observed: {n['can_match_observed']}\n"

    with open(output_dir / "report.md", "w") as f:
        f.write(report)
    
    print(f"\nReport generated at {output_dir / 'report.md'}")

def main():
    parser = argparse.ArgumentParser(description="Falsify Strong Autocorrelation in Prime Gaps")
    parser.add_argument("--ranges", type=str, default="1e8:1e9,1e9:1e10,1e10:1e11", help="Prime ranges P_min:P_max")
    parser.add_argument("--window-size", type=int, default=100000, help="Gaps per window")
    parser.add_argument("--max-lag", type=int, default=100, help="Max lag for ACF")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--output", type=str, default="results/", help="Output directory")
    parser.add_argument("--null-models", type=str, default="cramer,ar1,sieve", help="Null models to run")
    parser.add_argument("--permutations", type=int, default=10000, help="Permutation iterations")
    parser.add_argument("--bootstrap-iterations", type=int, default=1000, help="Bootstrap iterations")
    parser.add_argument("--block-size", type=int, default=100, help="Block size for bootstrap")
    parser.add_argument("--prime-backend", type=str, default="auto", help="Prime generation backend")
    parser.add_argument("--sieve-epsilon", type=float, default=0.05, help="Sieve split prob")
    parser.add_argument("--sieve-delta", type=float, default=0.05, help="Sieve merge prob")
    parser.add_argument("--detrend", action="store_true", help="Detrend data before ACF")
    
    args = parser.parse_args()
    run_falsification(args)

if __name__ == "__main__":
    main()
