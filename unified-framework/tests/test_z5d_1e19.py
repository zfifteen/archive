#!/usr/bin/env python3
"""
Z5D Grid Factorization Test for 10^19
=====================================

Test the Z5D θ' Shortcut method on N=10^19 = 2^19 × 5^19
"""

import time
import mpmath as mp
import sympy

mp.dps = 50

# Z Framework constants
phi = mp.phi  # golden ratio

def theta_prime(n, k):
    """Compute θ'(n, k) = φ · ((n mod φ) / φ)^k"""
    n_mod_phi = mp.fmod(n, phi)
    ratio = n_mod_phi / phi
    return phi * mp.power(ratio, k)

def factorize_with_z5d_grid(N, sieve_limit=10**7, bin_width=0.4, k=0.1):
    """
    Factorize N using Z5D Grid method.

    - Generate primes up to sieve_limit
    - Compute θ'(p, k) for each prime p
    - Bin the θ' values
    - Compute θ'(N, k)
    - Find bin containing θ'(N)
    - Check primes in that bin for divisibility
    """
    print(f"Starting Z5D Grid factorization of {N}")
    print(f"Sieve limit: {sieve_limit}")
    print(f"Bin width: {bin_width}")
    print(f"k parameter: {k}")

    start_time = time.time()

    # Generate primes up to sieve_limit
    print("Generating primes...")
    primes = list(sympy.primerange(2, sieve_limit + 1))
    print(f"Generated {len(primes)} primes")

    # Compute θ'(N, k)
    theta_N = theta_prime(N, k)
    print(f"θ'(N, k): {theta_N}")

    # Compute θ' for each prime and bin them
    print("Computing θ' for primes and binning...")
    bins = {}
    for p in primes:
        theta_p = theta_prime(p, k)
        bin_key = int(mp.floor(theta_p / bin_width))
        if bin_key not in bins:
            bins[bin_key] = []
        bins[bin_key].append((p, theta_p))

    # Find the bin for θ'(N)
    target_bin = int(mp.floor(theta_N / bin_width))
    print(f"Target bin: {target_bin}")

    if target_bin not in bins:
        print("Target bin not found in prime bins")
        return [], time.time() - start_time

    candidates = bins[target_bin]
    print(f"Candidates in target bin: {len(candidates)}")

    # Check candidates for divisibility
    factors = []
    remaining = N
    for p, theta_p in candidates:
        if remaining % p == 0:
            # Count multiplicity
            count = 0
            while remaining % p == 0:
                remaining //= p
                count += 1
            factors.extend([p] * count)
            print(f"Found factor {p} with multiplicity {count}")

    if remaining > 1:
        print(f"Remaining unfactored: {remaining}")
    else:
        print("Full factorization achieved")

    runtime = time.time() - start_time
    print(".3f")

    return factors, runtime

def main():
    N = 10**19
    print(f"Testing Z5D Grid on N = {N} = 2^19 × 5^19")

    factors, runtime = factorize_with_z5d_grid(N)

    print("\nResults:")
    print(f"Factors: {factors}")
    print(f"Count: {len(factors)}")
    print(".3f")

    # Verification
    product = 1
    for f in factors:
        product *= f
    print(f"Product verification: {product == N}")

    # Expected factors
    expected = [2]*19 + [5]*19
    print(f"Expected: {expected}")
    print(f"Match: {factors == expected}")

if __name__ == "__main__":
    main()