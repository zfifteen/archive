#!/usr/bin/env python3
"""
Optimized RSA Factorization using Tuned Z5D Predictor with Newton-like Adjustment
Scales by optimizing k to find where pred_p is an integer dividing n.
"""

import sys
import time
import mpmath

# Set precision
mpmath.mp.dps = 100

# Tuned parameters from RSA-100 (extendable)
phi = (1 + mpmath.sqrt(5)) / 2
c = -4.670305e30
kstar = 0.04449

# RSA Numbers
RSA_NUMBERS = {
    'RSA-100': '1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139',
    'RSA-129': '114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541',
    'RSA-155': '109080464142283928548631143003683792850987318979060772906350992238586989932759896165779734318111705648648364327956946574806842938968862636688997953060833928920493090697778516698072398062547866627715061122001330946065071089048300273323808756851651236255969431644054445266862593310426442079633635533092095824027'
}

def tuned_z5d_prime(k):
    mp_k = mpmath.mpf(k)
    ln_k = mpmath.log(mp_k)
    li_k = mpmath.ei(ln_k)
    mod_phi = mpmath.fmod(mp_k, phi)
    geo = phi * (mod_phi / phi) ** 0.3
    correction = c * (mp_k ** kstar) * geo
    pred_p = li_k + correction
    return pred_p

def compute_k_est(n_str):
    n = mpmath.mpf(n_str)
    sqrt_n = mpmath.sqrt(n)
    ln_sqrt_n = mpmath.log(sqrt_n)
    return float(sqrt_n * ln_sqrt_n)  # Note: This may be approximate; adjust if needed

def optimize_k_for_factor(n, k_start, max_iter=100, tolerance=1e-10):
    """Optimize k using Newton-like adjustment to find where pred_p is an integer dividing n."""
    k = mpmath.mpf(k_start)
    for i in range(max_iter):
        pred_p = tuned_z5d_prime(k)
        cand_p = mpmath.nint(pred_p)
        diff = pred_p - cand_p
        
        # Check if divides
        if diff < tolerance and diff > -tolerance:
            if int(cand_p) > 1 and n % int(cand_p) == 0:
                return float(k), int(cand_p)
        
        # Approximate derivative: d pred_p / dk ≈ 1 / ln(k)
        ln_k = mpmath.log(k)
        d_pred_dk = 1 / ln_k if ln_k != 0 else 1
        
        # Adjust k
        k -= diff / d_pred_dk
        
        if k <= 0:
            break
    
    return None, None

def factorize_rsa_optimized(n_str, name, max_iter=1000, timeout_minutes=10):
    print(f"\n{'='*60}")
    print(f"Factorizing {name} (Optimized)")
    print(f"{'='*60}")
    print(f"Digits: {len(n_str)}")
    
    n = int(n_str)
    k_est = compute_k_est(n_str)
    print(f"k_est: {k_est:.2e}")
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    # Try optimizing from k_est
    k_found, factor = optimize_k_for_factor(n, k_est, max_iter, tolerance=1e-5)  # Relax tolerance for large n
    
    if time.time() - start_time > timeout_seconds:
        print("⏰ Timeout")
        return None
    
    if factor:
        other = n // factor
        print(f"✅ SUCCESS: Found factor {factor}")
        print(f"k: {k_found:.2e}")
        return factor
    else:
        print("❌ No factor found")
        return None

def main():
    print("Optimized RSA Factorization using Tuned Z5D Predictor")
    print("Testing RSA-100, RSA-129, RSA-155")
    
    results = {}
    for name, n_str in RSA_NUMBERS.items():
        factor = factorize_rsa_optimized(n_str, name)
        results[name] = factor
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, factor in results.items():
        status = "SUCCESS" if factor else "FAILED"
        print(f"{name}: {status}")

if __name__ == "__main__":
    main()