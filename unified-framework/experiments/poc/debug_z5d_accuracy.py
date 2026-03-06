#!/usr/bin/env python3
"""
Debug Z5D Accuracy Issues
=========================

Test prime estimation accuracy for a known small semiprime.
"""

import mpmath as mp
from refined_z5d_factorizer import RefinedZ5DFactorizer, generate_semiprime_refined

mp.dps = 50

def debug_small_case():
    """Debug with 16-bit semiprime."""
    print("Debugging Z5D accuracy on small semiprime...")

    # Generate small semiprime
    n_str, p, q = generate_semiprime_refined(16, seed=42)
    n = int(n_str)

    print(f"n = {n} = {p} × {q}")

    # Create factorizer
    factorizer = RefinedZ5DFactorizer()

    # Get k_est
    sqrt_n = mp.sqrt(mp.mpf(n_str))
    ln_sqrt = mp.log(sqrt_n)
    k_est = float(sqrt_n / ln_sqrt)

    print(f"k_est ≈ {k_est:.3f}")

    # Test a few k values around k_est
    k_candidates = [k_est + i * 0.1 for i in range(-5, 6)]

    print("Testing k values around k_est:")
    for k in k_candidates:
        pred_p = factorizer.z5d_prime_estimate(k)
        error = abs(pred_p - p) / p
        print(f"k={k:.3f}: pred_p={pred_p:.3f}, error={error:.3f}")

    # Test refined method
    print("\nTesting refined factorization...")
    factor = factorizer.factorize_with_refinements(n_str, trials=50)
    print(f"Factor found: {factor}")
    print(f"Success: {factor == p or factor == q}")

if __name__ == "__main__":
    debug_small_case()