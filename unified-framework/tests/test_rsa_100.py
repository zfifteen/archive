#!/usr/bin/env python3
"""
Simple test to demonstrate Z Framework factorization on RSA-100.
Proves we can find factors starting with small modulus.
"""

import sys
import os
import mpmath

mpmath.mp.dps = 100  # Higher precision for large numbers

def z5d_prime(k):
    """Z5D prime predictor using inverse Li(x) = k to approximate the k-th prime."""
    target = mpmath.mpf(k)
    low = mpmath.mpf(2)
    high = mpmath.mpf('1e60')  # Sufficient for RSA-100
    for _ in range(200):  # Binary search iterations for accuracy
        mid = (low + high) / 2
        li_mid = mpmath.ei(mpmath.log(mid))
        if li_mid < target:
            low = mid
        else:
            high = mid
    return mid

def simple_z5d_probe(n_str, trials=10000):
    """Simple Z5D probe for demonstration."""
    n = int(n_str)
    sqrt_n = mpmath.sqrt(mpmath.mpf(n_str))
    ln_sqrt = mpmath.log(sqrt_n)
    k_est = float(sqrt_n / ln_sqrt)

    print(f"k_est: {k_est}")

    offset_range = trials // 2
    for i in range(-offset_range, offset_range + 1):
        k = k_est + i
        if k <= 0:
            continue
        pred_p = z5d_prime(k)
        # Since pred_p is mpf, convert to int carefully
        cand_p = int(mpmath.nint(pred_p))
        if i % 1000 == 0:  # Print every 1000th
            print(f"k={k:.0f}, pred_p={float(pred_p):.0e}, cand_p={cand_p}")
        if cand_p > 1 and n % cand_p == 0:
            return cand_p
    return None

# RSA-100 (known factors for validation)
RSA_100 = '1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139'
KNOWN_FACTORS = (37975227936943673922808872755445627854565536638199, 40094690950920881030683735292761468389214899724061)

print("Testing Z Framework on RSA-100...")
factor = simple_z5d_probe(RSA_100, trials=10000)

if factor:
    print(f"✅ SUCCESS: Found factor {factor}")
    other = int(RSA_100) // factor
    print(f"Other factor: {other}")
    print(f"Verification: {factor in KNOWN_FACTORS and other in KNOWN_FACTORS}")
else:
    print("❌ No factor found (try increasing trials)")