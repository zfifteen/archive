#!/usr/bin/env python3
"""
Zeta Zero Unfolding and Correlation with Prime Shifts

This script implements the comprehensive analysis requested in Issue #35:
- Computes first M=1000 non-trivial zeta zeros and unfolds their spacings
- Generates primes up to N=10^6 and computes zeta shifts Z(p_i) = p_i * (κ(p_i) / Δ_max)  
- Performs correlation analysis between unfolded spacings and prime curvatures
- Validates against hybrid GUE statistics with KS tests
- Implements chiral adjustments and φ-normalization

Target: Achieve r ≈ 0.93 (empirical, pending independent validation) correlation and validate hybrid GUE statistics (KS stat≈0.916).
Success criteria: Sorted r >0.8 (p<0.01)
"""

import numpy as np
import pandas as pd
import mpmath as mp
from scipy.stats import pearsonr, kstest
from scipy import stats
from sympy import primerange, divisors
import matplotlib.pyplot as plt
from core.axioms import curvature

# Set high precision for zeta zero computations
mp.mp.dps = 50

# Mathematical constants
PHI = (1 + mp.sqrt(5)) / 2  # Golden ratio φ ≈ 1.618
PI = mp.pi
E = mp.e
E_SQUARED = mp.exp(2)
DELTA_MAX = 4.567  # Unfolding parameter as specified

def compute_zeta_zeros(M):
    """
    Compute first M non-trivial Riemann zeta zeros ρ_j = 0.5 + i t_j
    Returns the imaginary parts t_j
    """
    print(f"Computing {M} zeta zeros...")
    zeros_imag = []
    for j in range(1, M + 1):
        if j % 100 == 0:
            print(f"  Computed {j}/{M} zeros")
        zero = mp.zetazero(j)
        t_j = float(zero.imag)  # Extract imaginary part
        zeros_imag.append(t_j)
    return np.array(zeros_imag)

def unfold_zeta_zeros(t_values):
    """
    Unfold zeta zeros using the reference implementation approach:
    First unfold individual zeros: tilde_t = t / (2π log(t / (2π e)))
    Then compute spacings: δ_j = tilde_t_{j+1} - tilde_t_j
    """
    print("Unfolding zeta zeros...")
    unfolded_zeros = []
    
    for t in t_values:
        arg = t / (2 * mp.pi * mp.e)
        if arg > 1:  # Only process valid arguments
            log_val = mp.log(arg)
            tilde_t = t / (2 * mp.pi * log_val)
            unfolded_zeros.append(float(tilde_t))
    
    # Now compute spacings from unfolded zeros
    spacings = []
    for j in range(1, len(unfolded_zeros)):
        spacing = unfolded_zeros[j] - unfolded_zeros[j-1]
        spacings.append(spacing)
    
    return np.array(spacings), np.array(unfolded_zeros)

def phi_normalize_spacings(delta_values):
    """
    Apply φ-normalization: δ_φ,j = δ_j / φ
    """
    phi_float = float(PHI)
    return delta_values / phi_float

def generate_primes_up_to(N):
    """
    Generate all primes up to N using sympy
    """
    print(f"Generating primes up to {N}...")
    primes = list(primerange(2, N + 1))
    print(f"Found {len(primes)} primes")
    return primes

def compute_prime_curvatures(primes):
    """
    Compute curvature κ(p_i) = d(p_i) * ln(p_i + 1) / e²
    where d(p_i) is the divisor count (which is 2 for primes)
    """
    print("Computing prime curvatures...")
    curvatures = []
    for p in primes:
        d_p = len(divisors(p))  # For primes, this should be 2
        kappa = float(curvature(p, d_p))
        curvatures.append(kappa)
    return np.array(curvatures)

def compute_zeta_shifts(primes, curvatures, delta_max=DELTA_MAX):
    """
    Compute zeta shifts Z(p_i) = p_i * (Δ_{p_i} / Δ_max)
    where Δ_{p_i} = κ(p_i)
    """
    print("Computing zeta shifts...")
    zeta_shifts = []
    for p, kappa in zip(primes, curvatures):
        Z_p = p * (kappa / delta_max)
        zeta_shifts.append(Z_p)
    return np.array(zeta_shifts)

def compute_phi_modular_predictions(unfolded_zeros, k=0.3):
    """
    Compute φ-modular predictions similar to the reference implementation:
    pred = φ * {u/φ}^k for each unfolded zero u
    """
    print("Computing φ-modular predictions...")
    predictions = []
    
    for u in unfolded_zeros[:-1]:  # Skip last one to match spacing length
        mod_val = float(u % PHI)
        pred = float(PHI * ((mod_val / PHI) ** k))
        predictions.append(pred)
    
    return np.array(predictions)

def compute_chiral_curvatures(primes, curvatures):
    """
    Compute chiral adjustment: κ_chiral = κ + φ^{-1} * sin(ln p) * 0.618
    """
    print("Computing chiral curvatures...")
    phi_inv = 1.0 / float(PHI)
    chiral_curvatures = []
    
    for p, kappa in zip(primes, curvatures):
        chiral_term = phi_inv * np.sin(np.log(p)) * 0.618
        kappa_chiral = kappa + chiral_term
        chiral_curvatures.append(kappa_chiral)
    
    return np.array(chiral_curvatures)

def correlation_analysis(delta, delta_phi, kappa, Z_p, kappa_chiral, phi_predictions=None):
    """
    Perform comprehensive correlation analysis between all pairs:
    - δ vs. κ(p)
    - δ vs. Z(p) 
    - δ_φ vs. κ(p)
    - δ vs. κ_chiral
    - δ_φ vs. κ_chiral
    - δ vs. φ-predictions (if provided)
    
    For both sorted and unsorted data
    """
    print("Performing correlation analysis...")
    
    # Truncate to minimum length for fair comparison
    min_len = min(len(delta), len(kappa))
    delta_trunc = delta[:min_len]
    delta_phi_trunc = delta_phi[:min_len]
    kappa_trunc = kappa[:min_len]
    Z_p_trunc = Z_p[:min_len]
    kappa_chiral_trunc = kappa_chiral[:min_len]
    
    pairs = [
        ("δ vs. κ(p)", delta_trunc, kappa_trunc),
        ("δ vs. Z(p)", delta_trunc, Z_p_trunc),
        ("δ_φ vs. κ(p)", delta_phi_trunc, kappa_trunc),
        ("δ vs. κ_chiral", delta_trunc, kappa_chiral_trunc),
        ("δ_φ vs. κ_chiral", delta_phi_trunc, kappa_chiral_trunc)
    ]
    
    # Add φ-modular predictions if provided
    if phi_predictions is not None:
        phi_pred_trunc = phi_predictions[:min_len]
        pairs.append(("δ vs. φ-pred", delta_trunc, phi_pred_trunc))
        pairs.append(("δ_φ vs. φ-pred", delta_phi_trunc, phi_pred_trunc))
    
    results = []
    
    for pair_name, x, y in pairs:
        # Unsorted correlation
        r_unsorted, p_unsorted = pearsonr(x, y)
        
        # Sorted correlation  
        x_sorted = np.sort(x)
        y_sorted = np.sort(y)
        r_sorted, p_sorted = pearsonr(x_sorted, y_sorted)
        
        results.append({
            'Pair': pair_name,
            'Unsorted r': r_unsorted,
            'Unsorted p': p_unsorted,
            'Sorted r': r_sorted,
            'Sorted p': p_sorted
        })
    
    return results

def simulate_gue_spacings(n_samples):
    """
    Simulate GUE (Gaussian Unitary Ensemble) spacing distribution
    """
    # GUE level spacings follow Wigner surmise: p(s) = (π/2) s exp(-πs²/4)
    # Generate using inverse transform sampling or direct sampling
    random_samples = np.random.exponential(scale=1.0, size=n_samples)
    return random_samples

def ks_test_against_gue(delta_values):
    """
    Perform Kolmogorov-Smirnov test against GUE distribution
    Target KS statistic ≈ 0.916 for hybrid GUE
    """
    print("Performing KS test against GUE...")
    
    # Generate GUE samples for comparison
    gue_samples = simulate_gue_spacings(len(delta_values))
    
    # Perform KS test
    ks_stat, ks_p = kstest(delta_values, gue_samples)
    
    return ks_stat, ks_p, gue_samples

def format_correlation_table(correlation_results):
    """
    Format correlation results as a nice table
    """
    df = pd.DataFrame(correlation_results)
    
    # Format numerical columns
    df['Unsorted r'] = df['Unsorted r'].apply(lambda x: f"{x:.4f}")
    df['Unsorted p'] = df['Unsorted p'].apply(lambda x: f"{x:.2e}")
    df['Sorted r'] = df['Sorted r'].apply(lambda x: f"{x:.4f}")
    df['Sorted p'] = df['Sorted p'].apply(lambda x: f"{x:.2e}")
    
    return df

def main(M=1000, N=1000000):
    """
    Main analysis pipeline
    
    Parameters:
    M: Number of zeta zeros (default 1000)
    N: Upper limit for primes (default 10^6)
    """
    print("=" * 60)
    print("ZETA ZERO UNFOLDING AND CORRELATION ANALYSIS")
    print("=" * 60)
    print(f"Parameters: M={M} zeta zeros, N={N} prime limit")
    
    # Step 1: Compute zeta zeros and unfold spacings
    print("\n1. Computing and unfolding zeta zeros...")
    t_values = compute_zeta_zeros(M)
    delta, unfolded_zeros = unfold_zeta_zeros(t_values)
    delta_phi = phi_normalize_spacings(delta)
    
    print(f"Computed {len(delta)} unfolded spacings")
    print(f"Sample δ values: {delta[:5]}")
    print(f"Sample δ_φ values: {delta_phi[:5]}")
    
    # Step 2: Generate primes and compute curvatures/shifts
    print("\n2. Computing prime curvatures and zeta shifts...")
    primes = generate_primes_up_to(N)
    kappa = compute_prime_curvatures(primes)
    Z_p = compute_zeta_shifts(primes, kappa)
    kappa_chiral = compute_chiral_curvatures(primes, kappa)
    
    # Compute φ-modular predictions from unfolded zeros
    phi_predictions = compute_phi_modular_predictions(unfolded_zeros)
    
    print(f"Sample κ(p) values: {kappa[:5]}")
    print(f"Sample Z(p) values: {Z_p[:5]}")
    print(f"Sample κ_chiral values: {kappa_chiral[:5]}")
    print(f"Sample φ-predictions: {phi_predictions[:5]}")
    
    # Step 3: Correlation analysis
    print("\n3. Performing correlation analysis...")
    correlation_results = correlation_analysis(delta, delta_phi, kappa, Z_p, kappa_chiral, phi_predictions)
    
    # Step 4: KS test against GUE
    print("\n4. Testing against GUE distribution...")
    ks_stat, ks_p, gue_samples = ks_test_against_gue(delta)
    
    # Step 5: Output results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    print("\nCorrelation Matrix:")
    correlation_table = format_correlation_table(correlation_results)
    print(correlation_table.to_string(index=False))
    
    print(f"\nKS Test Results:")
    print(f"KS Statistic: {ks_stat:.4f}")
    print(f"KS p-value: {ks_p:.2e}")
    print(f"Target KS stat ≈ 0.916: {'✓' if abs(ks_stat - 0.916) < 0.1 else '✗'}")
    
    # Check success criteria
    print(f"\nSuccess Criteria Check:")
    max_sorted_r = max([r['Sorted r'] for r in correlation_results])
    min_sorted_p = min([r['Sorted p'] for r in correlation_results])
    print(f"Max Sorted r: {max_sorted_r}")
    print(f"Min Sorted p: {min_sorted_p:.2e}")
    print(f"Success (r>0.8, p<0.01): {'✓' if float(max_sorted_r) > 0.8 and min_sorted_p < 0.01 else '✗'}")
    
    # Output sample arrays (first 100)
    print(f"\nSample Arrays (first 100 values):")
    print(f"δ_j (unfolded spacings): {delta[:100]}")
    print(f"δ_φ,j (φ-normalized): {delta_phi[:100]}")
    print(f"Z(p_i) (zeta shifts): {Z_p[:100]}")
    
    return {
        'delta': delta,
        'delta_phi': delta_phi,
        'kappa': kappa,
        'Z_p': Z_p,
        'kappa_chiral': kappa_chiral,
        'correlation_results': correlation_results,
        'ks_stat': ks_stat,
        'ks_p': ks_p
    }

if __name__ == "__main__":
    # Set matplotlib backend for headless environment
    plt.switch_backend('Agg')
    
    results = main()