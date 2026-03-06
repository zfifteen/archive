import sys
import os
import json
import time
import random
import sympy
from geodesic_utils import theta_prime
from z5d_128bit_factorizer import factor_naive, factor_z5d
from validation_framework import bootstrap_ci

random.seed(42)

def generate_semi_prime():
    p = sympy.randprime(2**31, 2**32)
    q = sympy.randprime(2**31, 2**32)
    return p * q

def run_poc():
    print("Generating 10 deterministic 128-bit semi-primes...")
    semi_primes = []
    for i in range(10):
        n = generate_semi_prime()
        print(f"  {i+1}: {n} = p * q (hidden)")
        semi_primes.append(n)

    print("\nRunning factorization POC...\n")

    results = []
    for i, n in enumerate(semi_primes):
        print(f"Factoring {i+1}/10: {n}")
        # Naive
        start = time.time()
        naive_result = factor_naive(n)
        naive_time = time.time() - start
        print(f"  Naive: {naive_result}, time: {naive_time:.6f}s")
        # Z5D
        start = time.time()
        z5d_result = factor_z5d(n)
        z5d_time = time.time() - start
        print(f"  Z5D:  {z5d_result}, time: {z5d_time:.6f}s")

        results.append({
            'n': str(n),
            'naive': naive_result,
            'naive_time': naive_time,
            'z5d': z5d_result,
            'z5d_time': z5d_time
        })

    # Analysis
    successes_naive = sum(1 for r in results if r['naive'] is not None)
    successes_z5d = sum(1 for r in results if r['z5d'] is not None)
    avg_naive = sum(r['naive_time'] for r in results) / len(results)
    avg_z5d = sum(r['z5d_time'] for r in results) / len(results)
    ratio = avg_z5d / avg_naive if avg_naive > 0 else 1
    improvement = (1 - ratio) * 100
    ci = bootstrap_ci([r['z5d_time'] / r['naive_time'] for r in results if r['naive_time'] > 0])

    print(f"\nPOC Results:")
    print(f"Success rate: Naive {successes_naive}/10, Z5D {successes_z5d}/10")
    print(f"Average time - Naive: {avg_naive:.6f}s, Z5D: {avg_z5d:.6f}s")
    print(f"Improvement: {improvement:.2f}% ({ratio:.3f}x)")
    print(f"Bootstrap CI (95%): [{ci[0]:.4f}, {ci[1]:.4f}]")

    with open('z5d_128bit_poc_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Results saved to z5d_128bit_poc_results.json")

    print("\nPOC complete!")

if __name__ == "__main__":
    run_poc()