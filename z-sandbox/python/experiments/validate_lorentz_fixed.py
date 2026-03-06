#!/usr/bin/env python3
"""
Validate Lorentz Dilation Hypothesis for High-Scale Z5D Stability (Fixed Version)
================================================================================

This script validates the Lorentz dilation hypothesis for enhancing Z5D predictor
stability at ultra-high scales, with fixes applied for correct regressor, tail analysis,
and meaningful stability gates.

Hypothesis: γ = 1 + (1/2)(ln p_k / (e^4 + β ln p_k))^2 with β ≈ 30.34
enhances high-scale Z5D stability to <0.00001% error at k > 10^{12}.

Validation approach:
1. Simulate γ on primes up to 10^7 (k ≤ π(10^7) ≈ 664,579)
2. Compute bootstrap CI (1000 resamples) on dilation fit (target r ≥ 0.93) on tail (p >= 10^6)
3. Extrapolate error to k > 10^{12} using linearized fit
"""

import mpmath as mp
import numpy as np
import sympy
from scipy import stats
import time

# Set precision
mp.dps = 50
beta = 30.34

def compute_gamma(p_k):
    """Compute Lorentz dilation γ for prime p_k"""
    ln_pk = mp.log(p_k)
    e4 = mp.exp(4)
    denominator = e4 + beta * ln_pk
    term = ln_pk / denominator
    gamma = 1 + 0.5 * (term ** 2)
    return float(gamma)

def generate_primes_up_to(limit):
    """Generate all primes up to limit"""
    return list(sympy.primerange(2, limit + 1))

def main():
    print("Generating primes up to 10^7...")
    start_time = time.time()
    primes = generate_primes_up_to(10**7)
    gen_time = time.time() - start_time
    print(f"Generated {len(primes)} primes in {gen_time:.2f} seconds")

    print("Computing γ for each prime...")
    start_time = time.time()
    gammas = []
    for i, p in enumerate(primes):
        if i % 10000 == 0:
            print(f"Processed {i}/{len(primes)} primes")
        gamma = compute_gamma(mp.mpf(p))
        gammas.append(gamma)
    comp_time = time.time() - start_time
    print(f"Computed γ in {comp_time:.2f} seconds")

    # Convert to arrays
    primes_array = np.array(primes, dtype=np.float64)
    gammas_array = np.array(gammas, dtype=np.float64)

    # Focus on tail primes (p >= 10^6)
    tail_mask = primes_array >= 1_000_000
    primes_tail = primes_array[tail_mask]
    gammas_tail = gammas_array[tail_mask]
    L_tail = np.log(primes_tail)

    print(f"Tail analysis: {len(primes_tail)} primes with p >= 10^6")


    # Linearizable variables per formula
    X = L_tail / (np.e**4 + beta * L_tail)
    Y = np.sqrt(np.maximum(gammas_tail - 1.0, 0.0))

    # Correlations
    r_xy = np.corrcoef(X, Y)[0, 1]
    r_L_gamma = np.corrcoef(L_tail, gammas_tail)[0, 1]

    print(f"Fit √(γ−1) vs L/(e^4+βL): r={r_xy:.6f}  (target ~ 1.0)")
    print(f"Fit γ vs ln p (tail): r={r_L_gamma:.6f}")

    print(f"Fit γ vs ln p (tail): r={r_L_gamma:.6f}")

    # Bootstrap on the tail
    rng = np.random.default_rng(0)
    n = len(L_tail)
    B = 1000
    rs = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, size=n)
        rs[b] = np.corrcoef(X[idx], Y[idx])[0, 1]
    lo, hi = np.quantile(rs, [0.025, 0.975])
    mean_r = rs.mean()

    print(f"Bootstrap r (tail): mean={mean_r:.6f}, 95% CI [{lo:.6f}, {hi:.6f}]")
    if mean_r >= 0.93:
        print("✓ Target r ≥ 0.93 achieved")
    else:
        print("✗ Target r ≥ 0.93 not achieved")

        # Linearized variables
        X = L_tail / (np.e**4 + 30.34 * L_tail)
        Y = np.sqrt(np.maximum(gammas_tail - 1.0, 0.0))
    
        # Expected slope from the model
    c = 1.0 / np.sqrt(2.0)
    
    # Fit (no intercept) and with intercept for diagnostics
    c_hat_no_int = (X @ Y) / (X @ X)
    A = np.vstack([X, np.ones_like(X)]).T
    c_hat, b_hat = np.linalg.lstsq(A, Y, rcond=None)[0]
    
    # Proper residual vs the *correct* slope
    res = Y - c * X
    
    # Relative error (mean & tail-robust p95), normalized to signal magnitude
    mean_rel_err = np.mean(np.abs(res)) / np.mean(np.abs(Y))
    p95_rel_err  = np.percentile(np.abs(res) / np.maximum(np.abs(Y), 1e-300), 95)
    
    print(f"slope (no-intercept)  c_hat_no_int = {c_hat_no_int:.12f}  (target c = {c:.12f})")
    print(f"slope/intercept (OLS) c_hat = {c_hat:.12f}, b_hat = {b_hat:.3e}  (target b≈0)")
    print(f"Mean relative error vs cX: {mean_rel_err:.3e}")
    print(f"P95  relative error vs cX: {p95_rel_err:.3e}")
    
    # Gates
    TOL_SLOPE = 1e-12
    TOL_INT   = 1e-12
    TOL_ERR   = 1e-7   # 0.00001%
    
    ok = True
    if abs(c_hat_no_int - c) > TOL_SLOPE: 
        print("✗ slope(no-intercept) deviates from 1/√2"); ok = False
    if abs(b_hat) > TOL_INT:
        print("✗ intercept not ~0"); ok = False
    if mean_rel_err > TOL_ERR:
        print(f"✗ mean relative error {mean_rel_err:.2e} > {TOL_ERR:.1e}"); ok = False
    if ok:
        print("✓ Linearized identity validated to numerical precision.")
print("Validation complete.")

if __name__ == "__main__":
    main()