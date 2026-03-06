#!/usr/bin/env python3
"""
Medium-scale test for correlation analysis functionality
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

from zeta_zero_correlation_analysis import *

def test_correlation_analysis():
    """
    Test correlation analysis with medium-sized data
    """
    print("Testing correlation analysis with medium parameters...")
    
    # Medium test parameters
    M_test = 50  # 50 zeta zeros  
    N_test = 1000  # Primes up to 1000
    
    print("1. Computing zeta zeros and unfolding...")
    t_values = compute_zeta_zeros(M_test)
    delta = unfold_zeta_spacings(t_values)
    delta_phi = phi_normalize_spacings(delta)
    
    print("2. Computing primes and curvatures...")
    primes = generate_primes_up_to(N_test)
    kappa = compute_prime_curvatures(primes)
    Z_p = compute_zeta_shifts(primes, kappa)
    kappa_chiral = compute_chiral_curvatures(primes, kappa)
    
    print("3. Testing correlation analysis...")
    correlation_results = correlation_analysis(delta, delta_phi, kappa, Z_p, kappa_chiral)
    
    print("4. Testing KS test...")
    ks_stat, ks_p, gue_samples = ks_test_against_gue(delta)
    
    print("5. Formatting results...")
    correlation_table = format_correlation_table(correlation_results)
    print("\nCorrelation Table:")
    print(correlation_table.to_string(index=False))
    
    print(f"\nKS Test Results:")
    print(f"KS Statistic: {ks_stat:.4f}")
    print(f"KS p-value: {ks_p:.2e}")
    
    print("\nMedium-scale test completed successfully!")
    return True

if __name__ == "__main__":
    test_correlation_analysis()