#!/usr/bin/env python3
"""
Nth Prime Comparators Implementation

Implements the comprehensive nth prime comparison as specified in issue #445.
This includes Z5D, li^-1, 4-term asymptotic, and Dusart upper bound comparators.

Ground truth: data/nth_primes.csv
Pinned constants: kappa_star = 0.04449, c_cal = -0.00247 (from src/core/params.py)
"""

import os
import sys
import csv
import numpy as np
import mpmath as mp
from multiprocessing import Pool
import time

# Add src to path to import params
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from core.params import KAPPA_STAR_DEFAULT, Z5D_C_CALIBRATED

# Set precision
mp.mp.dps = 50

# Pinned constants (no refitting)
KAPPA_STAR = KAPPA_STAR_DEFAULT  # 0.04449
C_CAL = Z5D_C_CALIBRATED  # -0.00247

def load_zeta_zeros(path='data/zeta.txt', max_zeros=None):
    """Load zeta zeros from file."""
    zeros = []
    with open(path) as f:
        for i, line in enumerate(f):
            if line.startswith('#'):
                continue
            if max_zeros and len(zeros) >= max_zeros:
                break
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    zeros.append(mp.mpf(parts[1]))
                except ValueError:
                    continue
    return zeros

def load_ground_truth(path='data/nth_primes.csv'):
    """Load ground truth nth primes."""
    truth = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            k = int(row['k'])
            true_prime = int(row['true'])
            truth[k] = true_prime
    return truth

def z5d_pi(x, zeros):
    """Z5D estimate of pi(x) with zeta correction."""
    if x < 2:
        return mp.mpf(0)
    
    li_x = mp.li(x)
    sqrt_x = mp.sqrt(x)
    li_sqrt = mp.li(sqrt_x) / 2
    
    correction = mp.mpf(0)
    for t in zeros:
        rho = mp.mpc(0.5, t)
        conj_rho = mp.conj(rho)
        correction += mp.re(mp.li(x ** rho) / rho + mp.li(x ** conj_rho) / conj_rho) / 2
    
    return li_x - correction - li_sqrt

def z5d_pk(k, zeros, tol=mp.mpf('1e-6')):
    """Z5D prediction of k-th prime using binary search with zeta correction."""
    if k < 2:
        return mp.mpf(0)
    
    # Initial bounds using asymptotic estimates with calibration
    ln_k = mp.log(k)
    base = mp.mpf(k) * ln_k
    
    # Apply calibration to improve initial bounds
    calibration_factor = 1 + C_CAL * (mp.mpf(k) ** KAPPA_STAR)
    
    low = base * calibration_factor * mp.mpf(0.95)
    high = base * calibration_factor * mp.mpf(1.15)
    
    iteration_count = 0
    max_iterations = 30
    
    while high - low > tol and iteration_count < max_iterations:
        mid = (low + high) / 2
        if z5d_pi(mid, zeros) < k:
            low = mid
        else:
            high = mid
        iteration_count += 1
    
    return (low + high) / 2

def li_inverse_pk(k):
    """Logarithmic integral inverse approximation for k-th prime."""
    if k < 2:
        return mp.mpf(0)
    
    # Standard li^-1 series expansion
    ln_k = mp.log(k)
    ln_ln_k = mp.log(ln_k) if ln_k > 1 else mp.mpf(0)
    
    # Series approximation: k * (ln(k) + ln(ln(k)) - 1) + correction
    base = mp.mpf(k) * (ln_k + ln_ln_k - 1)
    
    if ln_k > 1:
        # Additional terms for better accuracy
        a = mp.mpf(1.8)  # Fixed constant as documented
        correction = mp.mpf(k) * (ln_ln_k - a) / ln_k
        return base + correction
    else:
        return base

def asymp4_pk(k):
    """4-term asymptotic expansion for k-th prime."""
    if k < 2:
        return mp.mpf(0)
    
    ln_k = mp.log(k)
    ln_ln_k = mp.log(ln_k) if ln_k > 1 else mp.mpf(0)
    ln_ln_ln_k = mp.log(ln_ln_k) if ln_ln_k > 1 else mp.mpf(0)
    
    # Conventional PNT expansion with 4 terms
    term1 = mp.mpf(k) * ln_k
    term2 = mp.mpf(k) * ln_ln_k
    term3 = mp.mpf(k) * ln_ln_k * ln_ln_k / ln_k
    term4 = mp.mpf(k) * ln_ln_k * (ln_ln_ln_k - 1) / ln_k
    
    return term1 + term2 - term3 + term4

def dusart_upper_bound_pk(k):
    """Dusart upper bound for k-th prime (conservative)."""
    if k < 2:
        return mp.mpf(0)
    
    ln_k = mp.log(k)
    ln_ln_k = mp.log(ln_k) if ln_k > 1 else mp.mpf(0)
    
    # Conservative Dusart upper bound
    if k >= 6:
        return mp.mpf(k) * (ln_k + ln_ln_k - 1 + mp.mpf(1.8) / ln_k)
    else:
        # Handle small k values
        known_primes = [2, 3, 5, 7, 11, 13]
        if k <= len(known_primes):
            return mp.mpf(known_primes[k-1])
        else:
            return mp.mpf(k) * ln_k * mp.mpf(1.2)

def compute_comparators(k, true_prime, zeros):
    """Compute all comparators for a given k."""
    # Z5D prediction
    z5d_pred = float(z5d_pk(k, zeros))
    z5d_err = abs(z5d_pred - true_prime) / true_prime * 100
    z5d_signed_err = (z5d_pred - true_prime) / true_prime * 100
    
    # li^-1 prediction
    li_pred = float(li_inverse_pk(k))
    li_err = abs(li_pred - true_prime) / true_prime * 100
    
    # 4-term asymptotic prediction
    asymp4_pred = float(asymp4_pk(k))
    asymp4_err = abs(asymp4_pred - true_prime) / true_prime * 100
    
    # Dusart upper bound prediction
    dusart_pred = float(dusart_upper_bound_pk(k))
    dusart_err = abs(dusart_pred - true_prime) / true_prime * 100
    
    return {
        'k': k,
        'true': true_prime,
        'z5d': z5d_pred,
        'err_z5d': z5d_err,
        'signed_err_z5d': z5d_signed_err,
        'li_inv': li_pred,
        'err_li': li_err,
        'asymp4': asymp4_pred,
        'err_asymp4': asymp4_err,
        'dusart_ub': dusart_pred,
        'err_dusart_ub': dusart_err
    }

def generate_comparison_results():
    """Generate comprehensive comparison results."""
    print("Loading data...")
    
    # Load zeta zeros and ground truth
    zeros = load_zeta_zeros()
    truth = load_ground_truth()
    
    print(f"Loaded {len(zeros)} zeta zeros and {len(truth)} ground truth primes")
    
    # Generate results for each k
    results = []
    for k in sorted(truth.keys()):
        print(f"Computing comparators for k={k}...")
        true_prime = truth[k]
        result = compute_comparators(k, true_prime, zeros)
        results.append(result)
        
        # Print summary for this k
        print(f"  Z5D: {result['z5d']:.2f} (err: {result['err_z5d']:.4f}%)")
        print(f"  li^-1: {result['li_inv']:.2f} (err: {result['err_li']:.4f}%)")
        print(f"  4-term: {result['asymp4']:.2f} (err: {result['err_asymp4']:.4f}%)")
        print(f"  Dusart UB: {result['dusart_ub']:.2f} (err: {result['err_dusart_ub']:.4f}%)")
    
    # Save results to CSV
    output_path = 'results/comparators_nth_prime.csv'
    os.makedirs('results', exist_ok=True)
    
    with open(output_path, 'w', newline='') as f:
        fieldnames = ['k', 'true', 'z5d', 'err_z5d', 'signed_err_z5d', 
                     'li_inv', 'err_li', 'asymp4', 'err_asymp4', 
                     'dusart_ub', 'err_dusart_ub']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults saved to: {output_path}")
    
    # Print summary statistics
    print("\nSUMMARY STATISTICS:")
    print("-" * 50)
    
    z5d_errors = [r['err_z5d'] for r in results]
    li_errors = [r['err_li'] for r in results]
    asymp4_errors = [r['err_asymp4'] for r in results]
    dusart_errors = [r['err_dusart_ub'] for r in results]
    
    def median(arr):
        return float(np.median(arr))
    
    def p95(arr):
        return float(np.percentile(arr, 95))
    
    print(f"Z5D:       median={median(z5d_errors):.6f}%  p95={p95(z5d_errors):.6f}%")
    print(f"li^-1:     median={median(li_errors):.6f}%  p95={p95(li_errors):.6f}%")
    print(f"asymp4:    median={median(asymp4_errors):.6f}%  p95={p95(asymp4_errors):.6f}%")
    print(f"Dusart_UB: median={median(dusart_errors):.6f}%  p95={p95(dusart_errors):.6f}%")
    
    return results

if __name__ == "__main__":
    results = generate_comparison_results()