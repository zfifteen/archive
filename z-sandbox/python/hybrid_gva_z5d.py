#!/usr/bin/env python3
"""
Hybrid GVA-Z5D Factorization Prototype
Uses Z5D to generate initial candidates, then GVA for geometric ranking.
Based on insights from GitHub discussion #18 for scaling beyond 128 bits.
Fixed per code review: Proper Z5D usage for prime prediction around sqrtN.
"""

import sympy as sp
import math
import random
import mpmath as mp
from z5d_predictor import z5d_predict  # Assuming z5d_predictor.py is available

mp.mp.dps = 50

def generate_semiprime(bits, seed=None):
    if seed:
        random.seed(seed)
    half_bits = bits // 2
    base = 2**half_bits
    offset = random.randint(0, 10**(half_bits//10))
    p = sp.nextprime(base + offset)
    q = sp.nextprime(base + offset + random.randint(1, 10**(half_bits//20)))
    N = int(p) * int(q)
    return N, int(p), int(q)

def embed(n, dims=11, k=None, z_norm=20.48):
    phi = mp.mpf((1 + mp.sqrt(5)) / 2)
    c = mp.exp(2)
    if k is None:
        k = mp.mpf('0.3') / mp.log(mp.log(float(n) + 1), 2)
    x = mp.mpf(n) / c
    coords = []
    for _ in range(dims):
        x = phi * mp.power(mp.frac(x / phi), k)
        coords.append(mp.frac(x))
    normalized_coords = [coord * (z_norm / dims) for coord in coords]
    return normalized_coords

def riemann_dist(c1, c2, N, z_norm=20.48):
    kappa = 4 * mp.log(N + 1) / mp.exp(2)
    deltas = [mp.mpf(min(abs(a - b), 1 - abs(a - b))) for a, b in zip(c1, c2)]
    dist_sq = sum((delta * (1 + kappa * delta))**2 for delta in deltas)
    dist = mp.sqrt(dist_sq)
    return dist / z_norm

def estimate_k_for_prime(n):
    """Estimate k for prime around n using PNT approximation."""
    return int(n / math.log(n))

def hybrid_gva_z5d(N, dims=11, num_candidates=100, search_range=10000):
    sqrtN = int(math.sqrt(N))
    k_est = estimate_k_for_prime(sqrtN)
    
    # Use Z5D to predict primes around k_est
    predicted_primes = []
    for dk in range(-num_candidates//2, num_candidates//2):
        k = max(1, k_est + dk)
        pred_prime = z5d_predict(k)
        if pred_prime:
            predicted_primes.append(int(pred_prime))
    
    # Filter primes within search_range of sqrtN and sort
    candidates = [p for p in set(predicted_primes) if abs(p - sqrtN) <= search_range]
    candidates = sorted(candidates)
    
    # GVA ranking
    theta_N = embed(N, dims)
    ranked = sorted(candidates, key=lambda c: riemann_dist(embed(c), theta_N, N))
    
    # Test top ranked for factors
    for cand in ranked:
        if N % cand == 0 and sp.isprime(cand):
            return cand
    return None

# Test
if __name__ == "__main__":
    N, p, q = generate_semiprime(150, seed=12345)
    print(f"Testing hybrid on N={N} ({N.bit_length()} bits)")
    factor = hybrid_gva_z5d(N)
    if factor:
        print(f"Found factor: {factor}")
    else:
        print("No factor found")