#!/usr/bin/env python3
"""
64-Bit Balanced Semiprime Factorization via TRUE Geometric-Guided Search

This demonstrates geometry-guided factorization where torus embeddings and 
geodesic distances PRIORITIZE candidates BEFORE divisibility testing.

Key difference from gva_factorize.py:
- gva_factorize.py: sqrt(N) ± d → N % p → primality → THEN geometry (validation)
- This file: sqrt(N) ± d → compute ALL embeddings → sort by geodesic distance → 
  test N % p in geometry-ordered sequence (guided search)

Only after this can we honestly claim "geometry guides the factor search."
"""
import math
import multiprocessing
from mpmath import *
from sympy.ntheory import isprime
from functools import partial
import heapq

def is_prime_robust(n):
    """Robust primality check: sympy + miller_rabin fallback."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    try:
        return isprime(n)
    except:
        return miller_rabin(n)

def miller_rabin(n, k=20):
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37][:k]
    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True
    for w in witnesses:
        if w >= n:
            continue
        if check_composite(w):
            return False
    return True

# High precision for 64-bit
mp.dps = 300
phi = (1 + sqrt(5)) / 2
k_default = mpf('0.04')

def embed_torus_geodesic(n, c=exp(2), k=k_default, dims=7):
    """
    Torus geodesic embedding for GVA.
    Z = A(B / c) with c = e², iterative θ'(n, k)
    """
    x = mpf(n) / c
    coords = []
    for _ in range(dims):
        x = phi * power(frac(x / phi), k)
        coords.append(frac(x))
    return tuple(coords)

def riemannian_distance(coords1, coords2, N):
    """
    Riemannian distance on torus with domain-specific curvature.
    κ(n) = 4 · ln(n+1) / e²
    """
    kappa = mpf(4) * log(mpf(N) + 1) / exp(2)
    total = mpf(0)
    for c1, c2 in zip(coords1, coords2):
        d = min(abs(c1 - c2), 1 - abs(c1 - c2))
        total += (d * (1 + kappa * d))**2
    return sqrt(total)

def adaptive_threshold(N):
    """Adaptive ε = 0.12 / (1 + κ) *10"""
    kappa = 4 * math.log(N + 1) / math.exp(2)
    return 0.12 / (1 + kappa) * 10

def check_balance(p, q):
    """Check if |log2(p/q)| ≤ 1"""
    if p == 0 or q == 0:
        return False
    ratio = abs(math.log2(p / q))
    return ratio <= 1

def compute_candidate_with_distance(d, N, sqrtN, emb_N):
    """
    Compute candidate and its geodesic distance.
    Returns (distance, d, p) or None if invalid candidate.
    """
    p = sqrtN + d
    if p <= 1 or p >= N:
        return None
    emb_p = embed_torus_geodesic(p)
    dist = float(riemannian_distance(emb_N, emb_p, N))
    return (dist, d, p)

def gva_factorize_geometric_guided(N, R=10000000, top_k=1000):
    """
    TRUE geometric-guided factorization for 64-bit balanced semiprimes.
    
    Search order (GEOMETRY-GUIDED):
    1. Generate all candidate values p = sqrt(N) + d for d in [-R, R]
    2. Compute torus embeddings and geodesic distances for ALL candidates
    3. Sort candidates by geodesic distance (ascending = most geometrically plausible)
    4. Test candidates in geometry-ordered sequence: N % p, primality, balance
    
    This demonstrates geometry guiding the search, not just validating after the fact.
    
    Args:
        N: Semiprime to factor
        R: Search radius around sqrt(N)
        top_k: Number of top geometric candidates to test (optimization)
    
    Returns:
        (p, q, dist, candidates_tried) if successful, (None, None, None, 0) otherwise
    """
    if N >= 2**64:
        raise ValueError("N must be < 2^64")
    if is_prime_robust(N):
        return None, None, None, 0
    
    print(f"GEOMETRIC-GUIDED GVA: N = {N} ({N.bit_length()} bits)")
    print(f"Computing embeddings for {2*R+1} candidates...")
    
    sqrtN = int(sqrt(mpf(N)))
    emb_N = embed_torus_geodesic(N)
    
    # Phase 1: Compute distances for ALL candidates (geometry-first)
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        compute_func = partial(compute_candidate_with_distance, N=N, sqrtN=sqrtN, emb_N=emb_N)
        results = pool.map(compute_func, range(-R, R + 1))
    
    # Filter out invalid candidates
    valid_results = [r for r in results if r is not None]
    print(f"Valid candidates: {len(valid_results)}")
    
    # Phase 2: Sort by geodesic distance (geometry guides the order)
    valid_results.sort(key=lambda x: x[0])  # Sort by distance (ascending)
    print(f"Testing top {top_k} geometric candidates in distance-ordered sequence...")
    
    # Phase 3: Test in geometry-ordered sequence (not linear scan order)
    candidates_tried = 0
    for dist, d, p in valid_results[:top_k]:
        candidates_tried += 1
        
        # Now test divisibility in geometry-ordered sequence
        if N % p != 0:
            continue
        
        q = N // p
        if not is_prime_robust(p) or not is_prime_robust(q):
            continue
        
        if not check_balance(p, q):
            continue
        
        # Found it!
        print(f"GEOMETRIC VICTORY after {candidates_tried} candidates!")
        print(f"True factor found at geometry rank {candidates_tried}/{len(valid_results)}")
        return p, q, dist, candidates_tried
    
    print(f"No factor found in top {candidates_tried} geometric candidates")
    return None, None, None, candidates_tried

# Sample 64-bit test
if __name__ == "__main__":
    # Sample: N=18446736050711510819 = 4294966297 × 4294966427
    p, q = 4294966297, 4294966427
    N = p * q
    print(f"Sample 64-bit N = {N} ({N.bit_length()} bits)")
    import time
    start = time.time()
    
    # Test with smaller R and top_k for demonstration
    result = gva_factorize_geometric_guided(N, R=100000, top_k=5000)
    
    end = time.time()
    if result[0]:
        p_found, q_found, dist, tried = result
        print(f"SUCCESS: {p_found} × {q_found} = {N}")
        print(f"Distance: {dist:.4f}")
        print(f"Candidates tested: {tried}")
        print(f"Geometry placed true factor in top {tried} of {2*100000+1} candidates")
    else:
        print(f"No victory found (tested {result[3]} candidates)")
    print(f"Time: {end - start:.2f}s")
