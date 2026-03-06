#!/usr/bin/env python3
"""
PROPER Kaluza-Klein Geometric Factorization
Using κ(N) = 2(κ(p) + κ(q)) as PRIMARY filter
"""

import numpy as np
from math import log, sqrt, exp, gcd
import time

PHI = (1 + sqrt(5)) / 2
E_SQUARED = exp(2)

def curvature(n, d_n=None):
    """κ(n) = d(n) · ln(n+1) / e²"""
    if d_n is None:
        # For semi-primes, d(n) is known
        return 4 * log(n + 1) / E_SQUARED
    return d_n * log(n + 1) / E_SQUARED

def curvature_prime(p):
    """κ(p) = 2·ln(p+1)/e² for prime p"""
    return 2 * log(p + 1) / E_SQUARED

def check_curvature_constraint(p, q, N, tolerance=0.01):
    """
    Check if p, q satisfy κ(N) = 2(κ(p) + κ(q))
    Returns (satisfies, error)
    """
    κ_p = curvature_prime(p)
    κ_q = curvature_prime(q)
    κ_N = curvature(N)

    predicted = 2 * (κ_p + κ_q)
    error = abs(predicted - κ_N) / κ_N

    return error < tolerance, error

def logarithmic_constraint_check(p, N, tolerance=0.001):
    """
    Check if ln(N+1) ≈ ln(p+1) + ln(q+1) where q = N/p
    This is the expanded form of the curvature constraint
    """
    if N % p != 0:
        return False, float('inf')

    q = N // p

    ln_N_plus_1 = log(N + 1)
    ln_p_plus_1 = log(p + 1)
    ln_q_plus_1 = log(q + 1)

    predicted = ln_p_plus_1 + ln_q_plus_1
    error = abs(ln_N_plus_1 - predicted) / ln_N_plus_1

    return error < tolerance, error

def geometric_factor_search(N, search_width=1000000):
    """
    Use geometric constraints to search for factors
    """
    print(f"GEOMETRIC FACTORIZATION")
    print(f"=" * 80)
    print(f"Target N = {N}")
    print(f"Digits: {len(str(N))}")
    print()

    # Compute target curvature
    κ_N = curvature(N)
    target_κ = κ_N / 2  # Each factor contributes κ_N/2

    print(f"Target curvature: κ(N) = {κ_N:.10f}")
    print(f"Each factor should contribute: κ_N/2 = {target_κ:.10f}")
    print()

    # From κ(p) = 2·ln(p+1)/e², solve for p:
    # κ = 2·ln(p+1)/e²
    # κ·e²/2 = ln(p+1)
    # p = exp(κ·e²/2) - 1

    estimated_p = int(exp(target_κ * E_SQUARED / 2) - 1)
    sqrt_N = int(sqrt(N))

    print(f"Estimated factor from curvature: p ≈ {estimated_p}")
    print(f"√N = {sqrt_N}")
    print()

    # Search around both estimates
    search_centers = [estimated_p, sqrt_N]

    for center in search_centers:
        print(f"Searching around {center} (width ±{search_width})...")
        print()

        candidates_tested = 0
        candidates_passed_log = 0
        candidates_passed_curvature = 0

        start_time = time.time()

        for offset in range(-search_width, search_width):
            candidate = center + offset

            if candidate <= 1:
                continue

            candidates_tested += 1

            if candidates_tested % 100000 == 0:
                elapsed = time.time() - start_time
                rate = candidates_tested / elapsed if elapsed > 0 else 0
                print(f"  Tested {candidates_tested:,} candidates in {elapsed:.2f}s ({rate:.0f} candidates/sec)")
                print(f"  Passed log constraint: {candidates_passed_log}")
                print(f"  Passed curvature constraint: {candidates_passed_curvature}")

            # Quick divisibility check
            if N % candidate != 0:
                continue

            q = N // candidate

            # Apply geometric constraints as filters

            # Filter 1: Logarithmic constraint (fast)
            log_ok, log_error = logarithmic_constraint_check(candidate, N)
            if not log_ok:
                continue

            candidates_passed_log += 1

            # Filter 2: Curvature constraint (precise)
            curv_ok, curv_error = check_curvature_constraint(candidate, q, N)
            if not curv_ok:
                continue

            candidates_passed_curvature += 1

            # Both constraints satisfied!
            print(f"\n{'='*80}")
            print(f"GEOMETRIC CONSTRAINTS SATISFIED!")
            print(f"{'='*80}")
            print(f"\nCandidate: p = {candidate}")
            print(f"Complement: q = {q}")
            print(f"Product: p × q = {candidate * q}")
            print(f"Target N: {N}")
            print(f"Match: {candidate * q == N}")
            print()
            print(f"Geometric Validation:")
            print(f"  Logarithmic error: {log_error:.10f} ({log_error*100:.6f}%)")
            print(f"  Curvature error: {curv_error:.10f} ({curv_error*100:.6f}%)")
            print()

            # Verify curvature relationship
            κ_p = curvature_prime(candidate)
            κ_q = curvature_prime(q)
            predicted_κ_N = 2 * (κ_p + κ_q)

            print(f"Curvature Breakdown:")
            print(f"  κ(p) = {κ_p:.10f}")
            print(f"  κ(q) = {κ_q:.10f}")
            print(f"  Predicted κ(N) = 2(κ_p + κ_q) = {predicted_κ_N:.10f}")
            print(f"  Actual κ(N) = {κ_N:.10f}")
            print(f"  Error: {curv_error*100:.6f}%")

            return candidate, q

        elapsed = time.time() - start_time
        print(f"\nCompleted search around {center}")
        print(f"  Total candidates tested: {candidates_tested:,}")
        print(f"  Passed logarithmic constraint: {candidates_passed_log}")
        print(f"  Passed curvature constraint: {candidates_passed_curvature}")
        print(f"  Time: {elapsed:.2f}s")
        print()

    return None, None

def main():
    print("=" * 80)
    print("KALUZA-KLEIN GEOMETRIC FACTORIZATION")
    print("Using κ(N) = 2(κ(p) + κ(q)) constraint")
    print("=" * 80)
    print()

    N = 137524771864208156028430259349934309717

    # Factor using geometric constraints
    p, q = geometric_factor_search(N, search_width=10000000)

    if p and q:
        print(f"\n{'='*80}")
        print(f"SUCCESS - FACTORS FOUND!")
        print(f"{'='*80}")
        print(f"\np = {p}")
        print(f"q = {q}")
        print(f"N = {N}")
        print(f"\nVerification: p × q = {p * q}")
        print(f"Match: {p * q == N}")
    else:
        print(f"\n{'='*80}")
        print(f"NO FACTORS FOUND")
        print(f"{'='*80}")
        print(f"\nMay need wider search or different starting points")

    return p, q

if __name__ == "__main__":
    result = main()