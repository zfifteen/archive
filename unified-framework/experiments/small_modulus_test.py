#!/usr/bin/env python3
"""
Test Small Modulus Semi-Prime Factorization
===========================================

Quick test for small N semi-primes to verify 100% success claim.
"""

import math
import numpy as np

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def generate_small_semiprimes(max_n=1000):
    semiprimes = []
    primes = [p for p in range(2, max_n) if is_prime(p)]
    for i in range(len(primes)):
        for j in range(i, len(primes)):
            n = primes[i] * primes[j]
            if n < max_n:
                semiprimes.append((n, primes[i], primes[j]))
    return semiprimes

def geometric_factorize(n, epsilon=0.1):
    sqrt_n = math.sqrt(n)
    search_range = int(sqrt_n * epsilon)
    start = max(2, int(sqrt_n - search_range))
    end = int(sqrt_n + search_range)
    
    for candidate in range(start, end):
        if n % candidate == 0:
            factor = candidate
            cofactor = n // candidate
            if factor > 1 and cofactor > 1:
                return factor, cofactor
    return None, None

def test_small_modulus():
    semiprimes = generate_small_semiprimes(1000)
    print(f"Testing {len(semiprimes)} small semi-primes (N < 1000)")
    
    successes = 0
    for n, p, q in semiprimes:
        found_p, found_q = geometric_factorize(n, epsilon=0.1)
        if found_p and found_q:
            if {found_p, found_q} == {p, q}:
                successes += 1
            else:
                print(f"Wrong factors for {n}: found {found_p},{found_q} instead of {p},{q}")
        else:
            print(f"Failed to factor {n}")
    
    success_rate = successes / len(semiprimes) if semiprimes else 0
    print(f"Success rate: {success_rate:.3f} ({successes}/{len(semiprimes)})")
    
    return success_rate == 1.0

if __name__ == "__main__":
    is_100_percent = test_small_modulus()
    print(f"100% success: {is_100_percent}")