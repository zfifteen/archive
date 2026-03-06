#!/usr/bin/env python3
"""
Simple Z5D Prime Prediction Validation for n = 10^13

This script validates that our Z5D implementation matches the exact formula 
specified in the problem statement:

Formula verification:
- base_pnt_prime(n) = n * (ln n + ln ln n - 1 + (ln ln n - 2)/ln n)
- d_term(n) = (ln(base_pnt_prime(n)) / e^4)^2
- e_term(n) = base_pnt_prime(n)^{-1/3}
- z5d_prime(n) = base_pnt_prime(n) + c * d_term(n) * base_pnt_prime(n) + k_star * e_term(n) * base_pnt_prime(n)

Parameters: c = -0.00247, k_star = 0.04449
Target: n = 10^13
Reference: 323,780,508,946,331
"""

import sys
import os
import math

# Add src directory to path
sys.path.insert(0, os.path.join('.', 'src'))

from z_framework.discrete.z5d_predictor import base_pnt_prime, d_term, e_term, z5d_prime

def manual_formula_implementation(n, c, k_star):
    """
    Manual implementation of the exact formula from the problem statement
    to verify our module implementation matches exactly.
    """
    # base_pnt_prime(n) = n * (ln n + ln ln n - 1 + (ln ln n - 2)/ln n)
    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)
    base_pnt = n * (ln_n + ln_ln_n - 1 + (ln_ln_n - 2)/ln_n)
    
    # d_term(n) = (ln(base_pnt_prime(n)) / e^4)^2
    e_fourth = math.e ** 4
    d_val = (math.log(base_pnt) / e_fourth) ** 2
    
    # e_term(n) = base_pnt_prime(n)^{-1/3}
    e_val = base_pnt ** (-1.0/3.0)
    
    # z5d_prime(n) = base_pnt_prime(n) + c * d_term(n) * base_pnt_prime(n) + k_star * e_term(n) * base_pnt_prime(n)
    z5d_val = base_pnt + c * d_val * base_pnt + k_star * e_val * base_pnt
    
    return {
        'base_pnt': base_pnt,
        'd_term': d_val,
        'e_term': e_val,
        'z5d_prime': z5d_val
    }

def main():
    n = int(1e13)
    c = -0.00247
    k_star = 0.04449
    published_value = 323_780_508_946_331
    
    print("Z5D Formula Validation Test")
    print("=" * 40)
    print(f"n = {n:,}")
    print(f"c = {c}")
    print(f"k_star = {k_star}")
    print(f"Published value = {published_value:,}")
    print()
    
    # Manual calculation for validation
    print("Manual formula implementation:")
    manual_result = manual_formula_implementation(n, c, k_star)
    print(f"  base_pnt_prime({n:,}) = {manual_result['base_pnt']:,.0f}")
    print(f"  d_term({n:,}) = {manual_result['d_term']:.10f}")
    print(f"  e_term({n:,}) = {manual_result['e_term']:.10f}")
    print(f"  z5d_prime({n:,}) = {manual_result['z5d_prime']:,.0f}")
    print()
    
    # Module implementation
    print("Module implementation:")
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        base_pnt_val = base_pnt_prime(n)
        d_val = d_term(n) 
        e_val = e_term(n)
        z5d_val = z5d_prime(n, c=c, k_star=k_star, auto_calibrate=False)
    
    print(f"  base_pnt_prime({n:,}) = {base_pnt_val:,.0f}")
    print(f"  d_term({n:,}) = {d_val:.10f}")
    print(f"  e_term({n:,}) = {e_val:.10f}")
    print(f"  z5d_prime({n:,}) = {z5d_val:,.0f}")
    print()
    
    # Compare results
    print("Comparison:")
    print(f"  Manual vs Module base_pnt: {abs(manual_result['base_pnt'] - base_pnt_val):,.0f} difference")
    print(f"  Manual vs Module d_term: {abs(manual_result['d_term'] - d_val):.2e} difference")
    print(f"  Manual vs Module e_term: {abs(manual_result['e_term'] - e_val):.2e} difference")
    print(f"  Manual vs Module z5d: {abs(manual_result['z5d_prime'] - z5d_val):,.0f} difference")
    print()
    
    # Final result vs published
    absolute_error = abs(z5d_val - published_value)
    relative_error = absolute_error / published_value
    
    print("Final Results:")
    print(f"  Estimated 10^13th prime: {z5d_val:,.0f}")
    print(f"  Published 10^13th prime: {published_value:,}")
    print(f"  Absolute error: {absolute_error:,.0f}")
    print(f"  Relative error: {relative_error:.6f} ({relative_error*100:.4f}%)")
    print()
    
    if relative_error < 0.001:
        print("✅ EXCELLENT accuracy (< 0.1% error)")
    elif relative_error < 0.01:
        print("✅ GOOD accuracy (< 1% error)")
    else:
        print("⚠️  Moderate accuracy")

if __name__ == "__main__":
    main()