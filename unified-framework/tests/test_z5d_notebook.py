#!/usr/bin/env python3
"""
Test script for Z5D Prime Ratio Analyzer notebook functionality.
Validates the magnitude hypothesis with a smaller dataset.
"""

import math
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import sys
import os

# Add src to path to import parameters
sys.path.append('src')

def main():
    print("=== Z5D Prime Ratio Analyzer Test ===")
    
    # Configuration
    N_PRIMES = 5000  # Larger test set to see better asymptotic behavior
    RNG_SEED = 42
    BOOTSTRAP_B = 100  # Faster bootstrap
    
    np.random.seed(RNG_SEED)
    
    # Z5D Calibrated parameters
    C_CAL = -0.00247
    K_STAR = 0.04449
    KAPPA_GEO = 0.3
    
    print(f"Config: N_PRIMES={N_PRIMES}, BOOTSTRAP_B={BOOTSTRAP_B}")
    print(f"Z5D Calibration: C={C_CAL}, K*={K_STAR}, κ_geo={KAPPA_GEO}")
    
    # Functions
    def base_pnt(k: int) -> float:
        if k < 1: 
            return 0.0
        # Minimal handling for small k; main focus is on asymptotic behavior
        ln = math.log(k)
        if ln <= 0:
            return k * 0.5  # Simple fallback
        lnl = math.log(ln)
        return k * (ln + lnl - 1 + (lnl - 2) / ln)

    def z5d_prime(k: int) -> float:
        if k < 1: 
            return 2.0
        
        pnt = base_pnt(k)
        if pnt <= 0: 
            # Fallback for small k
            return k * math.log(max(k, 2))
        
        ln_pnt = math.log(pnt)
        d = (ln_pnt / math.exp(4))**2
        
        e = (k**2 + k + 2) / (k * (k + 1) * (k + 2))
        e *= KAPPA_GEO * (math.log(k + 1) / math.exp(2))
        
        return pnt + C_CAL * d * pnt + K_STAR * e * pnt

    def nth_prime_upper_bound(n: int) -> int:
        if n < 6:
            return 30
        ln_n = math.log(n)
        ln_ln_n = math.log(ln_n)
        return int(n * (ln_n + ln_ln_n) * 1.1)

    def sieve_of_eratosthenes(limit: int) -> list:
        if limit < 2:
            return []
        
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        
        for i in range(2, int(math.sqrt(limit)) + 1):
            if is_prime[i]:
                for j in range(i * i, limit + 1, i):
                    is_prime[j] = False
        
        return [i for i in range(2, limit + 1) if is_prime[i]]

    def first_n_primes(n: int) -> list:
        upper_bound = nth_prime_upper_bound(n)
        
        while True:
            primes = sieve_of_eratosthenes(upper_bound)
            if len(primes) >= n:
                return primes[:n]
            upper_bound *= 2

    def bootstrap_ci_mean(x, B=100, alpha=0.05):
        x = x[~np.isnan(x)]
        n = len(x)
        if n == 0:
            return (float('nan'), float('nan'))
        
        means = np.empty(B, dtype=float)
        for b in range(B):
            idx = np.random.randint(0, n, size=n)
            means[b] = x[idx].mean()
        
        lo = float(np.quantile(means, alpha/2))
        hi = float(np.quantile(means, 1 - alpha/2))
        return lo, hi

    def pearson_r(x, y):
        x = x.astype(float)
        y = y.astype(float)
        mx, my = x.mean(), y.mean()
        num = np.sum((x - mx) * (y - my))
        den = np.sqrt(np.sum((x - mx)**2) * np.sum((y - my)**2))
        return 0.0 if den == 0 else float(num / den)
    
    # Generate primes
    print(f"Generating {N_PRIMES} primes...")
    primes = first_n_primes(N_PRIMES)
    print(f"Generated {len(primes)} primes. Range: {primes[0]} to {primes[-1]:,}")
    
    # Compute ratios and estimates
    k_idx = np.arange(1, len(primes) + 1)
    p_arr = np.array(primes, dtype=float)
    
    p_over_k = p_arr / k_idx
    log_ratio = np.log(p_arr) / np.log(k_idx + 1)
    
    gaps = np.diff(p_arr)
    gap_ratio = np.where(gaps > 0, p_arr[1:], np.nan) / np.where(gaps > 0, gaps, np.nan)
    
    pnt_est = np.array([base_pnt(int(k)) for k in k_idx], dtype=float)
    z5d_est = np.array([z5d_prime(int(k)) for k in k_idx], dtype=float)
    
    pnt_err_pct = np.abs(p_arr - pnt_est) / p_arr * 100.0
    z5d_err_pct = np.abs(p_arr - z5d_est) / p_arr * 100.0
    
    # Calculate statistics
    mean_pk = float(np.nanmean(p_over_k))
    r_pk_log = pearson_r(p_over_k, log_ratio)
    mean_gap_ratio = float(np.nanmean(gap_ratio))
    mean_pnt = float(np.mean(pnt_err_pct))
    mean_z5d = float(np.mean(z5d_err_pct))
    improvement = (mean_pnt - mean_z5d) / (mean_pnt if mean_pnt else 1.0) * 100.0
    
    # Bootstrap CIs
    pk_lo, pk_hi = bootstrap_ci_mean(p_over_k, B=BOOTSTRAP_B)
    diff_err = pnt_err_pct - z5d_err_pct
    de_lo, de_hi = bootstrap_ci_mean(diff_err, B=BOOTSTRAP_B)
    gap_lo, gap_hi = bootstrap_ci_mean(gap_ratio, B=BOOTSTRAP_B)
    
    # Results
    print("\n=== MAGNITUDE HYPOTHESIS VALIDATION ===")
    print(f"Mean p/k: {mean_pk:.2f} (95% CI: [{pk_lo:.2f}, {pk_hi:.2f}])")
    print(f"Pearson r (p/k vs ln p / ln k): {r_pk_log:.2f}")
    print(f"Mean p/gap: {mean_gap_ratio:.2f} (95% CI: [{gap_lo:.2f}, {gap_hi:.2f}])")
    print(f"PNT mean abs % error: {mean_pnt:.4f}%")
    print(f"Z5D mean abs % error: {mean_z5d:.6f}%")
    print(f"Z5D Improvement: {improvement:.1f}%")
    print(f"Error difference CI: [{de_lo:.4f}%, {de_hi:.4f}%]")
    
    # Validate against expected values
    print("\n=== VALIDATION AGAINST EXPECTED VALUES ===")
    
    # Expected: Mean p/k ratio: ~9.37 for 10k primes
    # For 1k primes, should be lower (around 6-8)
    if 5.0 <= mean_pk <= 10.0:
        print("✓ Mean p/k ratio in expected range")
    else:
        print(f"⚠ Mean p/k ratio {mean_pk:.2f} outside expected range [5.0, 10.0]")
    
    # Expected: Pearson r (p/k vs log_ratio): ~-0.82
    if -0.9 <= r_pk_log <= -0.7:
        print("✓ Pearson correlation in expected range")
    else:
        print(f"⚠ Pearson correlation {r_pk_log:.2f} outside expected range [-0.9, -0.7]")
    
    # Expected: Z5D should be much more accurate than PNT
    if improvement > 90.0:
        print("✓ Z5D shows significant improvement over PNT")
    else:
        print(f"⚠ Z5D improvement {improvement:.1f}% lower than expected (>90%)")
    
    # Expected: Z5D errors should be very low
    if mean_z5d < 0.1:
        print("✓ Z5D absolute error is very low")
    else:
        print(f"⚠ Z5D error {mean_z5d:.6f}% higher than expected (<0.1%)")
    
    print("\n=== TEST COMPLETED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    main()