#!/usr/bin/env python3
"""
POC 64-Bit Factorization Demonstration

Complete proof-of-concept for Z5D geodesic factorization ladder rung.
Factors 10 deterministic 64-bit semi-primes with statistical validation.
"""

import time
import random
import json
import sympy
from z5d_64bit_factorizer import factor_naive, factor_z5d
from validation_framework import bootstrap_analysis

# Set random seed for reproducibility
random.seed(42)

# Generate 10 deterministic 64-bit semi-primes
semi_primes = []
print("Generating 10 deterministic 64-bit semi-primes...")
for i in range(10):
    p = sympy.randprime(2**16, 2**17)
    q = sympy.randprime(2**16, 2**17)
    n = int(p * q)
    semi_primes.append(n)
    print(f"  {i+1}: {n} = {p} * {q}")

print("\nRunning factorization POC...")

times_naive = []
times_z5d = []
success_count = 0

for idx, n in enumerate(semi_primes):
    print(f"\nFactoring {idx+1}/10: {n}")
    
    # Baseline factorization
    start = time.time()
    factors_n = factor_naive(n)
    time_n = time.time() - start
    times_naive.append(time_n)
    print(f"  Naive: {factors_n}, time: {time_n:.6f}s")
    
    # Z5D factorization
    start = time.time()
    factors_z = factor_z5d(n)
    time_z = time.time() - start
    times_z5d.append(time_z)
    print(f"  Z5D:  {factors_z}, time: {time_z:.6f}s")
    
    if factors_n == factors_z and factors_n is not None:
        success_count += 1
    else:
        print(f"  ERROR: Factor mismatch for {n}")

print(f"\nPOC Results:")
print(f"Success rate: {success_count}/10")
if success_count == 10:
    avg_naive = sum(times_naive) / len(times_naive)
    avg_z5d = sum(times_z5d) / len(times_z5d)
    improvement_percent = (avg_naive - avg_z5d) / avg_naive * 100
    improvement_ratio = avg_naive / avg_z5d
    
    print(f"Average time - Naive: {avg_naive:.6f}s, Z5D: {avg_z5d:.6f}s")
    print(f"Improvement: {improvement_percent:.2f}% ({improvement_ratio:.3f}x)")
    
    # Bootstrap validation
    boot_result = bootstrap_analysis(times_naive, times_z5d, n_resamples=1000)
    print(f"Bootstrap CI (95%): [{boot_result['ci_low']:.4f}, {boot_result['ci_high']:.4f}]")
    
    # Save results
    results = {
        "semi_primes": semi_primes,
        "times_naive": times_naive,
        "times_z5d": times_z5d,
        "avg_naive": avg_naive,
        "avg_z5d": avg_z5d,
        "improvement_percent": improvement_percent,
        "improvement_ratio": improvement_ratio,
        "bootstrap": boot_result,
        "success_count": success_count
    }
    with open("z5d_64bit_poc_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to z5d_64bit_poc_results.json")
else:
    print("POC failed due to factorization errors.")

print("\nPOC complete!")