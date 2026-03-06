#!/usr/bin/env python3
"""
Test script for zeta zero correlation analysis with smaller parameters
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

from zeta_zero_correlation_analysis import *

def test_small():
    """
    Test with smaller parameters to verify functionality
    """
    print("Testing with small parameters...")
    
    # Test parameters
    M_test = 10  # 10 zeta zeros
    N_test = 100  # Primes up to 100
    
    # Test individual functions
    print("1. Testing zeta zero computation...")
    t_values = compute_zeta_zeros(M_test)
    print(f"Got {len(t_values)} zeta zeros: {t_values}")
    
    print("\n2. Testing unfolding...")
    delta = unfold_zeta_spacings(t_values)
    print(f"Got {len(delta)} unfolded spacings: {delta}")
    
    print("\n3. Testing φ-normalization...")
    delta_phi = phi_normalize_spacings(delta)
    print(f"φ-normalized spacings: {delta_phi}")
    
    print("\n4. Testing prime generation...")
    primes = generate_primes_up_to(N_test)
    print(f"Got {len(primes)} primes: {primes[:10]}...")
    
    print("\n5. Testing curvature computation...")
    kappa = compute_prime_curvatures(primes)
    print(f"Got {len(kappa)} curvatures: {kappa[:5]}...")
    
    print("\n6. Testing zeta shifts...")
    Z_p = compute_zeta_shifts(primes, kappa)
    print(f"Got {len(Z_p)} zeta shifts: {Z_p[:5]}...")
    
    print("\n7. Testing chiral curvatures...")
    kappa_chiral = compute_chiral_curvatures(primes, kappa)
    print(f"Got {len(kappa_chiral)} chiral curvatures: {kappa_chiral[:5]}...")
    
    print("\nAll tests passed!")
    return True

if __name__ == "__main__":
    test_small()