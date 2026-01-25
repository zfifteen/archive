#!/usr/bin/env python3
"""
ArctanGeodesic Demo: Showcase stable atan identities and geodesic mappings.

Usage: python atan_geodesic_demo.py --N 100 --k 1 --type integers
"""

import argparse
import time
import matplotlib.pyplot as plt
from mpmath import mp, mpf, atan, tan, pi, sqrt, fabs, fmod
import sympy

# Set high precision
mp.dps = 120
phi = (1 + sqrt(5)) / 2

def theta_prime(n, k):
    r = fmod(mpf(n), phi)
    return phi * (r / phi) ** k

def validate_identities():
    print("Validating Arctan Identities:")
    # Addition: atan(a) + atan(b) = atan((a+b)/(1-a*b))
    a, b = mpf('0.5'), mpf('0.3')
    lhs = atan(a) + atan(b)
    rhs = atan((a + b) / (1 - a * b))
    res = fabs(lhs - rhs)
    print(f"  Addition residual: {res}")

    # Double-angle: tan(2α) = 2*tan(α)/(1-tan²(α))
    alpha = mpf('0.785')
    lhs = tan(2 * alpha)
    rhs = 2 * tan(alpha) / (1 - tan(alpha)**2)
    res = fabs(lhs - rhs)
    print(f"  Double-angle residual: {res}")

    # Machin's formula: π/4 = atan(1/5) - atan(1/239)
    lhs = pi / 4
    rhs = atan(mpf(1)/5) - atan(mpf(1)/239)
    res = fabs(lhs - rhs)
    print(f"  Machin's π/4 residual: {res}")

def benchmark_efficiency(x=mpf('0.9'), terms=100):
    print(f"\nBenchmarking Arctan Efficiency at x={x}:")

    # Taylor series: sum_{k=0}^∞ (-1)^k * x^{2k+1} / (2k+1)
    start = time.time()
    taylor_sum = mpf(0)
    for k in range(terms):
        taylor_sum += (-1)**k * x**(2*k + 1) / (2*k + 1)
    taylor_time = time.time() - start
    print(f"  Taylor series ({terms} terms): {taylor_time:.4f}s, result: {taylor_sum}")

    # Using mpmath's atan (identity-based internally)
    start = time.time()
    identity_result = atan(x)
    identity_time = time.time() - start
    print(f"  Identity-based (mpmath): {identity_time:.4f}s, result: {identity_result}")

    speedup = taylor_time / identity_time if identity_time > 0 else float('inf')
    print(f"  Speedup: {speedup:.1f}x")

def plot_mapping(values, labels, title, filename):
    plt.figure(figsize=(10, 6))
    for val, lab in zip(values, labels):
        plt.scatter(range(len(val)), val, label=lab, alpha=0.7)
    plt.xlabel('Index')
    plt.ylabel('θ\'(n,k)')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()
    print(f"Plot saved: {filename}")

def main():
    parser = argparse.ArgumentParser(description="ArctanGeodesic Demo")
    parser.add_argument('--N', type=int, default=100, help='Sequence length')
    parser.add_argument('--k', type=int, default=1, help='Exponent for mapping')
    parser.add_argument('--type', choices=['integers', 'primes'], default='integers', help='Input type')
    args = parser.parse_args()

    print("ArctanGeodesic Demo: Stable Identities and Geodesic Mappings")
    print(f"φ ≈ {float(phi):.10f}\n")

    # Validate identities
    validate_identities()

    # Benchmark efficiency
    benchmark_efficiency()

    # Generate sequence
    if args.type == 'integers':
        seq = list(range(1, args.N + 1))
        title = f"Geodesic Mapping θ'(n,{args.k}) for Integers n=1 to {args.N}"
    else:
        seq = list(sympy.primerange(1, args.N + 1))[:args.N]
        title = f"Geodesic Mapping θ'(p,{args.k}) for First {len(seq)} Primes"

    # Compute mappings
    theta_k1 = [theta_prime(n, 1) for n in seq]
    theta_k = [theta_prime(n, args.k) for n in seq]

    # Check invariants
    in_range = all(0 <= t < phi for t in theta_k)
    print(f"\nMapping Invariants: All in [0, φ)? {in_range}")

    # Plot
    plot_mapping([theta_k1, theta_k], [f'k=1', f'k={args.k}'], title, 'mapping_demo.png')

    print("\nNovelty: Enables stable, efficient computations for geometric-number theoretic explorations.")

if __name__ == '__main__':
    main()