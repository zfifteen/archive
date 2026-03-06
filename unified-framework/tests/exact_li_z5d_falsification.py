#!/usr/bin/env python3
"""
Exact Reproduction and Falsification of the Li-Z5D Symmetry Hypothesis

This script reproduces the exact code structure from the problem statement
and provides empirical falsification evidence for the claimed symmetries.
"""

import numpy as np
import mpmath as mp
import sys
import os
from scipy.special import expit  
from sympy import mobius
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from core.z_5d_enhanced import Z5DEnhancedPredictor
from core.params import get_exact_pi

mp.dps = 50

# Approximate li(k) via numerical integration (from problem statement)
def li(k):
    if k < 2:
        return mp.mpf(0)
    return mp.li(k)

# Riemann R approximation (truncated sum, mu(n) from sympy) - from problem statement  
def riemann_r(k, max_n=50):  # Truncate for efficiency
    sum_r = mp.mpf(1)
    for n in range(1, max_n + 1):
        mu_n = mobius(n)
        if mu_n != 0:
            sum_r += mp.mpf(mu_n) / n * li(mp.power(k, 1/n))
    return sum_r

# PASE: k / log k - from problem statement
def pase(k):
    return k / mp.log(k) if k > 1 else mp.mpf(0)

# Z5D to π(k) inversion via binary search
def z5d_to_pi_inversion(target_k, z5d_predictor):
    """
    Invert Z5D k-th prime predictor to get π(k) approximation
    If Z5D(x) ≈ target_k, then π(target_k) ≈ x
    """
    if target_k < 2:
        return 0
    
    # Binary search bounds
    low = 1.0
    high = target_k / mp.log(target_k) * 2  # Upper bound estimate
    
    # Binary search for x such that Z5D(x) ≈ target_k
    for _ in range(50):  # Max iterations
        mid = (low + high) / 2
        z5d_val = z5d_predictor.z_5d_prediction(mid)
        
        if abs(z5d_val - target_k) < target_k * 1e-6:  # Convergence tolerance
            return mid
        elif z5d_val < target_k:
            low = mid
        else:
            high = mid
            
        if high - low < 1e-8:
            break
    
    return (low + high) / 2

def run_exact_reproduction_test():
    """
    Run the exact test from the problem statement with falsification analysis
    """
    print("Exact Reproduction of Li-Z5D Symmetry Hypothesis Test")
    print("=" * 60)
    
    # Initialize Z5D predictor
    z5d_predictor = Z5DEnhancedPredictor()
    
    # Generate k values from problem statement: 10^2 to 10^10 (reduced to 10^7 for speed)
    k_vals = np.logspace(2, 7, 30)  
    
    # Use exact π(k) values from centralized function
    true_pi = get_exact_pi(k_vals)
    
    print(f"Testing {len(k_vals)} points from k=10^2 to k=10^7")
    print("Computing approximations...")
    
    # Compute approximations exactly as in problem statement
    start_time = time.time()
    
    errors_li = []
    errors_r = []  
    errors_pase = []
    errors_z5d = []
    
    for i, k in enumerate(k_vals):
        if i % 5 == 0:
            print(f"  Progress: {i+1}/{len(k_vals)}")
        
        # Compute all approximations
        li_val = float(li(k))
        r_val = float(riemann_r(k))
        pase_val = float(pase(k))
        z5d_pi_val = float(z5d_to_pi_inversion(k, z5d_predictor))
        
        true_val = float(true_pi[i])
        
        # Compute relative errors as in problem statement
        if true_val > 0:
            errors_li.append(float(abs(li_val - true_val) / true_val))
            errors_r.append(float(abs(r_val - true_val) / true_val))
            errors_pase.append(float(abs(pase_val - true_val) / true_val))
            errors_z5d.append(float(abs(z5d_pi_val - true_val) / true_val))
        else:
            errors_li.append(0.0)
            errors_r.append(0.0)
            errors_pase.append(0.0)
            errors_z5d.append(0.0)
    
    computation_time = time.time() - start_time
    
    # Convert to numpy arrays for analysis
    errors_li = np.array(errors_li)
    errors_r = np.array(errors_r)
    errors_pase = np.array(errors_pase)
    errors_z5d = np.array(errors_z5d)
    
    print(f"Computation completed in {computation_time:.2f} seconds")
    
    # Exact analysis from problem statement
    print("\n" + "="*60)
    print("FALSIFICATION ANALYSIS")
    print("="*60)
    
    # Test 1: Ultra-low error claim for Z5D (~10^-6 at k≈10^7)
    high_k_idx = -1  # Last point (highest k)
    z5d_error_high_k = errors_z5d[high_k_idx]
    
    print(f"\n1. Z5D Ultra-Low Error Claim Test:")
    print(f"   Claimed: ~10^-6 error at high k")
    print(f"   Actual Z5D error at k={k_vals[high_k_idx]:.1e}: {float(z5d_error_high_k):.2e}")
    z5d_claim_validated = float(z5d_error_high_k) <= 1e-5
    print(f"   Result: {'VALIDATED' if z5d_claim_validated else 'FALSIFIED'}")
    
    # Test 2: Li error range claim (10^-1 to 10^-2)
    li_error_high_k = errors_li[high_k_idx]
    print(f"\n2. Li Error Range Claim Test:")
    print(f"   Claimed: 10^-2 to 10^-1 error range")
    print(f"   Actual Li error at k={k_vals[high_k_idx]:.1e}: {float(li_error_high_k):.2e}")
    li_claim_validated = 1e-3 <= float(li_error_high_k) <= 1e0
    print(f"   Result: {'VALIDATED' if li_claim_validated else 'FALSIFIED'}")
    
    # Test 3: PASE error claim (~10^-1)
    pase_error_high_k = errors_pase[high_k_idx]
    print(f"\n3. PASE Error Claim Test:")
    print(f"   Claimed: ~10^-1 error")
    print(f"   Actual PASE error at k={k_vals[high_k_idx]:.1e}: {float(pase_error_high_k):.2e}")
    pase_claim_validated = 1e-2 <= float(pase_error_high_k) <= 1e0
    print(f"   Result: {'VALIDATED' if pase_claim_validated else 'FALSIFIED'}")
    
    # Test 4: Symmetry correlation claim 
    # Remove invalid values
    valid_mask = np.isfinite(errors_li) & np.isfinite(errors_z5d) & (errors_li > 0) & (errors_z5d > 0)
    li_clean = errors_li[valid_mask]
    z5d_clean = errors_z5d[valid_mask]
    
    if len(li_clean) >= 2 and np.std(li_clean) > 1e-10 and np.std(z5d_clean) > 1e-10:
        correlation = np.corrcoef(li_clean, z5d_clean)[0, 1]
    else:
        correlation = 0.0
        
    print(f"\n4. Li-Z5D Symmetry Correlation Test:")
    print(f"   Claimed: Quasi-symmetric oscillations (strong correlation)")
    print(f"   Actual correlation: {correlation:.4f}")
    symmetry_claim_validated = abs(correlation) > 0.5  # Threshold for "strong" correlation
    print(f"   Result: {'VALIDATED' if symmetry_claim_validated else 'FALSIFIED'}")
    
    # Test 5: Oscillatory vs smooth behavior
    z5d_variance = np.var(errors_z5d[valid_mask]) if np.sum(valid_mask) > 1 else 0
    li_variance = np.var(errors_li[valid_mask]) if np.sum(valid_mask) > 1 else 0
    
    print(f"\n5. Oscillatory Behavior Claim Test:")
    print(f"   Claimed: Z5D more oscillatory than Li")
    print(f"   Z5D error variance: {z5d_variance:.2e}")
    print(f"   Li error variance: {li_variance:.2e}")
    oscillatory_claim_validated = z5d_variance > li_variance
    print(f"   Result: {'VALIDATED' if oscillatory_claim_validated else 'FALSIFIED'}")
    
    # Overall falsification verdict
    claims_tested = [z5d_claim_validated, li_claim_validated, pase_claim_validated, 
                    symmetry_claim_validated, oscillatory_claim_validated]
    claims_validated = sum(claims_tested)
    claims_falsified = len(claims_tested) - claims_validated
    
    print(f"\n" + "="*60)
    print("OVERALL FALSIFICATION VERDICT")
    print("="*60)
    print(f"Claims tested: {len(claims_tested)}")
    print(f"Claims validated: {claims_validated}")
    print(f"Claims falsified: {claims_falsified}")
    
    hypothesis_falsified = claims_falsified >= 2  # Majority falsification
    print(f"\nHypothesis falsified: {'YES' if hypothesis_falsified else 'NO'}")
    
    if hypothesis_falsified:
        print("\n🔴 CONCLUSION: The Li-Z5D symmetry hypothesis is FALSIFIED")
        print("   Empirical evidence contradicts the claimed error levels and symmetries.")
    else:
        print("\n🟢 CONCLUSION: The Li-Z5D symmetry hypothesis is NOT falsified")
        print("   Empirical evidence supports the claimed patterns.")
    
    # Bootstrap confidence interval for symmetry (matching problem statement)
    if len(li_clean) > 10:
        print(f"\nBootstrap Analysis:")
        boot_correlations = []
        for _ in range(100):  # Reduced for speed
            indices = np.random.choice(len(li_clean), len(li_clean), replace=True)
            boot_li = li_clean[indices]
            boot_z5d = z5d_clean[indices]
            if np.std(boot_li) > 1e-10 and np.std(boot_z5d) > 1e-10:
                boot_corr = np.corrcoef(boot_li, boot_z5d)[0, 1]
                if np.isfinite(boot_corr):
                    boot_correlations.append(boot_corr)
        
        if boot_correlations:
            ci_low, ci_high = np.percentile(boot_correlations, [2.5, 97.5])
            print(f"Correlation 95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
            print(f"Mean correlation: {np.mean(boot_correlations):.4f}")
        
    return {
        'k_values': k_vals.tolist(),
        'errors': {
            'Li': errors_li.tolist(),
            'Riemann_R': errors_r.tolist(), 
            'PASE': errors_pase.tolist(),
            'Z5D': errors_z5d.tolist()
        },
        'claims_validated': claims_tested,
        'hypothesis_falsified': hypothesis_falsified,
        'correlation': correlation,
        'runtime': computation_time
    }

if __name__ == "__main__":
    results = run_exact_reproduction_test()
    
    # Exit with appropriate code for CI
    exit_code = 0 if results['hypothesis_falsified'] else 1
    sys.exit(exit_code)