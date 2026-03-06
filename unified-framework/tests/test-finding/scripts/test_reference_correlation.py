#!/usr/bin/env python3
"""
Direct implementation of the reference zeta zero correlation analysis
Focus on the specific correlation that achieves r ≈ 0.93 (empirical, pending independent validation)
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

import numpy as np
import mpmath as mp
from scipy.stats import pearsonr, kstest
from sympy import primerange

# Set high precision
mp.mp.dps = 50

def compute_unfolded_zeros(M):
    """Reference implementation unfolding"""
    phi = mp.phi
    pi = mp.pi
    e = mp.e
    unfolded = []
    for k in range(1, M + 1):
        if k % 50 == 0:
            print(f"  Computing zero {k}/{M}")
        t = mp.zetazero(k).imag
        arg = t / (2 * pi * e)
        if arg > 1:
            log_val = mp.log(arg)
            tilde_t = t / (2 * pi * log_val)
            unfolded.append(tilde_t)
    return unfolded

def compute_spacings(unfolded):
    """Reference implementation spacing computation"""
    return [float(unfolded[j] - unfolded[j-1]) for j in range(1, len(unfolded))]

def phi_modular_predictions(unfolded, k=0.3):
    """Reference implementation φ-modular predictions"""
    phi = mp.phi
    preds = []
    for u in unfolded[:-1]:
        mod = u % phi
        pred = float(phi * ((mod / phi) ** k))
        preds.append(pred)
    return preds

def main_reference_test(M=100):
    """Test the specific correlation from reference implementation"""
    print(f"Testing reference implementation correlation with M={M} zeros...")
    
    # Compute unfolded zeros
    print("1. Computing unfolded zeros...")
    unfolded = compute_unfolded_zeros(M)
    print(f"Got {len(unfolded)} unfolded zeros")
    
    # Compute spacings
    print("2. Computing spacings...")
    spacings = compute_spacings(unfolded)
    print(f"Got {len(spacings)} spacings")
    print(f"Sample spacings: {spacings[:5]}")
    
    # Compute φ-modular predictions
    print("3. Computing φ-modular predictions...")
    preds = phi_modular_predictions(unfolded, k=0.3)
    print(f"Got {len(preds)} predictions")
    print(f"Sample predictions: {preds[:5]}")
    
    # Compute correlation (this should be the r ≈ 0.93 (empirical, pending independent validation))
    print("4. Computing correlation...")
    corr, p_val = pearsonr(spacings, preds)
    print(f"Pearson correlation: {corr:.4f}")
    print(f"p-value: {p_val:.2e}")
    
    # Test if this meets the target
    if abs(corr) >= 0.9:
        print("✓ Target correlation achieved!")
    else:
        print("✗ Target correlation not achieved")
    
    return corr, p_val, spacings, preds

if __name__ == "__main__":
    # Test with different sizes
    for M in [50, 100, 200]:
        print("="*60)
        try:
            corr, p_val, spacings, preds = main_reference_test(M)
            print(f"Result for M={M}: r={corr:.4f}, p={p_val:.2e}")
        except Exception as e:
            print(f"Error for M={M}: {e}")
        print("="*60)