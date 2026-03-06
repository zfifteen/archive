#!/usr/bin/env python3
"""
Parameter Sweep for GVA Scaling
Sweeps k (curvature), dims (torus dimensions), and epsilon (threshold) for 128-150 bit semiprimes.
Based on GitHub discussion #18 recommendations for resolving scaling contradictions.
Optimized per code review: Use heap to limit memory usage for large candidate sets.
"""

import sympy as sp
import math
import random
import mpmath as mp
import csv
import heapq
from datetime import datetime

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

def gva_factorize(N, dims=11, k=None, epsilon=0.004, search_range=50000, max_candidates=128):  # Reduced for efficiency
    theta_N = embed(N, dims, k)
    sqrtN = int(math.sqrt(N))
    candidates = range(max(2, sqrtN - search_range), sqrtN + search_range + 1)
    
    # Use heap to keep only top max_candidates to save memory
    top_candidates = []
    for c in candidates:
        dist = riemann_dist(embed(c, dims, k), theta_N, N)
        if len(top_candidates) < max_candidates:
            heapq.heappush(top_candidates, (-dist, c))  # Max heap for smallest dist (negative for max heap)
        elif -top_candidates[0][0] > dist:
            heapq.heapreplace(top_candidates, (-dist, c))
    
    # Sort the top candidates by actual dist
    top_list = [(dist, c) for dist, c in [(-neg_dist, c) for neg_dist, c in top_candidates]]
    top_list.sort(key=lambda x: x[0])
    
    for dist, cand in top_list:
        if dist <= epsilon and N % cand == 0 and sp.isprime(cand):
            return cand, dist
    return None, None

def parameter_sweep(bits=128, num_trials=10, output_csv="parameter_sweep_results.csv"):
    k_values = [0.04, 0.06, 0.08]  # Sweeping k around base 0.06
    dims_values = [11, 13, 15]      # Based on discussion for higher dims
    epsilon_values = [0.004, 0.006, 0.008]  # Threshold sweep
    
    results = []
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['k', 'dims', 'epsilon', 'success_rate', 'avg_time', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for k in k_values:
            for dims in dims_values:
                for epsilon in epsilon_values:
                    successes = 0
                    total_time = 0
                    for trial in range(num_trials):
                        N, p, q = generate_semiprime(bits, seed=12345 + trial)
                        import time
                        start = time.time()
                        factor, dist = gva_factorize(N, dims, k, epsilon)
                        elapsed = time.time() - start
                        total_time += elapsed
                        if factor:
                            successes += 1
                    
                    success_rate = (successes / num_trials) * 100
                    avg_time = total_time / num_trials
                    result = {
                        'k': k, 'dims': dims, 'epsilon': epsilon,
                        'success_rate': success_rate, 'avg_time': avg_time,
                        'timestamp': datetime.now().isoformat()
                    }
                    results.append(result)
                    writer.writerow(result)
                    print(f"k={k}, dims={dims}, eps={epsilon}: {success_rate:.1f}% success, {avg_time:.3f}s avg")
    
    return results

if __name__ == "__main__":
    print("Running optimized parameter sweep for 128-bit semiprimes (10 trials per config)...")
    results = parameter_sweep(128, 10)
    print("Sweep complete. Results in parameter_sweep_results.csv")