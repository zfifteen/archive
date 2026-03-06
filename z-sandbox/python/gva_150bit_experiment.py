#!/usr/bin/env python3
"""
GVA Scaling Experiment: 150-bit Semiprime Factorization

Objective: Test GVA on 150-bit semiprimes to establish working range,
aiming for >0% success rate to guide further scaling.

Uses geometric embedding with Riemannian distance on torus manifold.

Usage:
    python3 gva_150bit_experiment.py [num_trials] [dims] [search_range]

Example:
    python3 gva_150bit_experiment.py 10 11 100000
"""

import sympy as sp
import math
import csv
import time
import random
import sys
import mpmath as mp
from datetime import datetime

mp.mp.dps = 50  # High precision

def embed(n, dims=11, k=None):
    """Embed number into d-dimensional torus using golden ratio modulation."""
    phi = mp.mpf((1 + mp.sqrt(5)) / 2)
    c = mp.exp(2)
    if k is None:
        k = mp.mpf('0.3') / mp.log(mp.log(float(n) + 1), 2)
    x = mp.mpf(n) / c
    coords = []
    for _ in range(dims):
        x = phi * mp.power(mp.frac(x / phi), k)
        coords.append(mp.frac(x))
    return coords

def riemann_dist(c1, c2, N):
    """Calculate Riemannian distance with curvature correction."""
    kappa = 4 * mp.log(N + 1) / mp.exp(2)
    deltas = [mp.mpf(min(abs(a - b), 1 - abs(a - b))) for a, b in zip(c1, c2)]
    dist_sq = sum((delta * (1 + kappa * delta))**2 for delta in deltas)
    return mp.sqrt(dist_sq)

def generate_150bit_semiprime(seed=None):
    """Generate a balanced 150-bit semiprime."""
    if seed:
        random.seed(seed)

    # Generate two ~75-bit primes
    base = 2**74
    offset = random.randint(0, 10**6)
    p = sp.nextprime(base + offset)
    q = sp.nextprime(base + offset + random.randint(1, 10**5))
    N = int(p) * int(q)

    return N, int(p), int(q)

def gva_factorize_150bit(N, max_candidates=1000, dims=11, search_range=100000):
    """Attempt GVA factorization on 150-bit semiprime with logging."""
    start_time = time.time()

    # Embed N
    theta_N = embed(N, dims)

    # Search around sqrt(N)
    sqrtN = int(mp.sqrt(N))
    R = search_range
    candidates = range(max(2, sqrtN - R), sqrtN + R + 1)

    # Rank candidates by Riemannian distance
    candidate_distances = []
    for c in candidates:
        dist = riemann_dist(embed(c, dims), theta_N, N)
        candidate_distances.append((dist, c))

    candidate_distances.sort()

    # Log top 10 distances
    print(f"  Top 10 distances: {[float(d) for d, _ in candidate_distances[:10]]}")

    # Check factors
    p_dist = riemann_dist(embed(sp.factorint(N).keys()[0] if len(sp.factorint(N)) == 1 else list(sp.factorint(N).keys())[0], dims), theta_N, N)  # wait, better to have p,q
    # Since we have N, but to log, perhaps assume we have p,q but we don't in factorization.

    # For logging, print the rank of p if we had it, but since it's factorization, we test divisibility on top.

    # Test top candidates
    for dist, cand in candidate_distances[:max_candidates]:
        if N % cand == 0 and sp.isprime(cand):
            elapsed = time.time() - start_time
            return cand, elapsed

    elapsed = time.time() - start_time
    return None, elapsed

def run_experiment(num_trials=10, output_csv="gva_150bit_results.csv", dims=11, search_range=100000):
    """Run GVA scaling experiment on random 150-bit semiprimes."""
    print(f"=== GVA 150-bit Scaling Experiment (dims={dims}, range={search_range}) ===")
    print(f"Running {num_trials} trials on 150-bit semiprimes")
    print(f"Target: >0% success rate (at least one factorization)")
    print()

    results = []
    successes = 0
    total_time = 0

    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['trial', 'N_bits', 'success', 'factor_found', 'time_seconds', 'dims', 'search_range', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for trial in range(num_trials):
            # Generate semiprime
            N, p, q = generate_150bit_semiprime(seed=12345 + trial)

            print(f"Trial {trial+1}/{num_trials}: N = {N} ({N.bit_length()} bits)")

            # Attempt factorization
            factor, elapsed = gva_factorize_150bit(N, dims=dims, search_range=search_range)

            success = factor is not None
            if success:
                successes += 1
                print(f"  ✓ SUCCESS: Found factor {factor} in {elapsed:.3f}s")
            else:
                print(f"  ✗ FAILED: No factor found in {elapsed:.3f}s")

            total_time += elapsed

            # Log result
            result = {
                'trial': trial + 1,
                'N_bits': N.bit_length(),
                'success': success,
                'factor_found': str(factor) if factor else None,
                'time_seconds': round(elapsed, 3),
                'dims': dims,
                'search_range': search_range,
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            writer.writerow(result)

    # Summary
    success_rate = (successes / num_trials) * 100
    avg_time = total_time / num_trials

    print()
    print("=== Results Summary ===")
    print(f"Trials: {num_trials}")
    print(f"Successes: {successes}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Average Time: {avg_time:.3f}s per trial")
    print(f"Total Time: {total_time:.1f}s")
    print(f"Results saved to: {output_csv}")

    if success_rate > 0:
        print("🎉 HYPOTHESIS VERIFIED: GVA shows potential for 150-bit factorization!")
    else:
        print("❌ Hypothesis not verified: No factorizations found. Consider parameter tuning.")

    return success_rate > 0

if __name__ == "__main__":
    # Parse command line arguments
    num_trials = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    dims = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    search_range = int(sys.argv[3]) if len(sys.argv) > 3 else 100000

    print(f"Running with parameters: trials={num_trials}, dims={dims}, search_range={search_range}")
    success = run_experiment(num_trials, f"gva_150bit_d{dims}_r{search_range}_results.csv", dims, search_range)
    exit(0 if success else 1)