#!/usr/bin/env python3
"""
PRNG Bias Investigation: Test different randomness sources for prime generation clustering
"""
import random
import secrets
from math import isqrt
import numpy as np
from scipy import stats

def is_prime(n):
    """Simple primality test for small numbers"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True

def generate_prime_basic_random(min_val, max_val):
    """Generate prime using Python's basic random module (Mersenne Twister)"""
    while True:
        candidate = random.randint(min_val, max_val)
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            return candidate

def generate_prime_crypto_random(min_val, max_val):
    """Generate prime using cryptographically secure randomness"""
    while True:
        candidate = secrets.randbelow(max_val - min_val) + min_val
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            return candidate

def generate_prime_fixed_seed(min_val, max_val, seed=12345):
    """Generate prime using fixed seed (deterministic)"""
    rng = random.Random(seed)
    while True:
        candidate = rng.randint(min_val, max_val)
        if candidate % 2 == 0:
            candidate += 1
        if is_prime(candidate):
            return candidate

def map_prime_to_grid(prime, scale_m=7):
    """Map prime to grid coordinates"""
    base = 10 ** scale_m
    x = prime // base
    y = prime % base
    return x, y

def calculate_clustering_metrics(primes, scale_m=7):
    """Calculate clustering statistics for a set of primes"""
    grid_coords = [map_prime_to_grid(p, scale_m) for p in primes]
    x_coords = [coord[0] for coord in grid_coords]

    unique_x = set(x_coords)
    clustering_ratio = len(primes) / len(unique_x)

    # Count factors per x-coordinate
    x_counts = {}
    for x in x_coords:
        x_counts[x] = x_counts.get(x, 0) + 1

    max_factors = max(x_counts.values())
    void_regions = len(range(min(x_coords), max(x_coords) + 1)) - len(unique_x)

    return {
        'primes': primes,
        'clustering_ratio': clustering_ratio,
        'unique_x_coords': len(unique_x),
        'max_factors_per_x': max_factors,
        'void_regions': void_regions,
        'x_distribution': x_counts,
        'grid_coords': grid_coords
    }

def generate_dataset(method_name, generator_func, count=20, bit_size=50):
    """Generate RSA dataset using specified random method"""
    print(f"\nGenerating {count} RSA keys using {method_name}...")

    prime_min = 2**(bit_size//2 - 2)
    prime_max = 2**(bit_size//2 + 2)

    all_primes = []
    rsa_moduli = []

    for i in range(count):
        if method_name == "Fixed Seed":
            # Use different seeds for p and q to avoid p=q
            p = generate_prime_fixed_seed(prime_min, prime_max, seed=12345+i*2)
            q = generate_prime_fixed_seed(prime_min, prime_max, seed=12345+i*2+1)
        else:
            p = generator_func(prime_min, prime_max)
            q = generator_func(prime_min, prime_max)
            while q == p:  # Ensure p != q
                q = generator_func(prime_min, prime_max)

        n = p * q
        all_primes.extend([p, q])
        rsa_moduli.append((n, p, q))

    return all_primes, rsa_moduli

def chi_square_uniformity_test(x_counts, total_coords_range):
    """Perform chi-square test for uniform distribution"""
    # Calculate expected frequency based on total observations
    total_observed = sum(x_counts.values())
    expected_freq = total_observed / len(x_counts)

    observed = list(x_counts.values())
    expected = [expected_freq] * len(observed)

    try:
        chi2, p_value = stats.chisquare(observed, expected)
        return chi2, p_value
    except ValueError:
        # Fallback calculation if scipy fails
        return 0.0, 1.0

def run_bias_investigation():
    """Run complete PRNG bias investigation"""
    print("PRNG BIAS INVESTIGATION")
    print("=" * 50)

    # Test configurations
    test_configs = [
        ("Cryptographically Secure", generate_prime_crypto_random),
        ("Basic Random (Mersenne)", generate_prime_basic_random),
        ("Fixed Seed", None)  # Special case handled in generate_dataset
    ]

    results = {}

    # Generate datasets for each method
    for method_name, generator_func in test_configs:
        all_primes, rsa_moduli = generate_dataset(method_name, generator_func)
        metrics = calculate_clustering_metrics(all_primes)
        results[method_name] = metrics

    # Analysis and comparison
    print("\n" + "=" * 60)
    print("CLUSTERING ANALYSIS RESULTS")
    print("=" * 60)

    for method_name, metrics in results.items():
        print(f"\n{method_name}:")
        print(f"  Clustering Ratio: {metrics['clustering_ratio']:.3f}")
        print(f"  Unique x-coordinates: {metrics['unique_x_coords']}")
        print(f"  Max factors per x: {metrics['max_factors_per_x']}")
        print(f"  Void regions: {metrics['void_regions']}")

        # Chi-square test
        total_range = max(metrics['x_distribution'].keys()) - min(metrics['x_distribution'].keys()) + 1
        if len(metrics['x_distribution']) > 1:
            chi2, p_val = chi_square_uniformity_test(metrics['x_distribution'], total_range)
            print(f"  Chi-square: {chi2:.3f}, p-value: {p_val:.4f}")

    # Statistical comparison
    print("\n" + "=" * 60)
    print("STATISTICAL COMPARISON")
    print("=" * 60)

    ratios = {name: metrics['clustering_ratio'] for name, metrics in results.items()}

    print(f"Clustering Ratio Comparison:")
    for method, ratio in ratios.items():
        print(f"  {method}: {ratio:.3f}")

    # Determine hypothesis outcome
    crypto_ratio = ratios["Cryptographically Secure"]
    basic_ratio = ratios["Basic Random (Mersenne)"]
    fixed_ratio = ratios["Fixed Seed"]

    print(f"\nHypothesis Testing:")
    print(f"  Secure Random Ratio: {crypto_ratio:.3f}")
    print(f"  Basic Random Ratio: {basic_ratio:.3f}")
    print(f"  Fixed Seed Ratio: {fixed_ratio:.3f}")

    if crypto_ratio < 2.0 and basic_ratio >= 3.0:
        conclusion = "HYPOTHESIS PROVEN: PRNG bias causes clustering"
    elif abs(crypto_ratio - basic_ratio) < 0.5:
        conclusion = "HYPOTHESIS DISPROVEN: Mathematical property, not PRNG bias"
    else:
        conclusion = "INCONCLUSIVE: Mixed evidence"

    print(f"\nCONCLUSION: {conclusion}")

    return results, conclusion

if __name__ == "__main__":
    results, conclusion = run_bias_investigation()

    # Save detailed results
    with open("bias_test_results.txt", "w") as f:
        f.write("PRNG Bias Investigation Results\n")
        f.write("=" * 40 + "\n\n")

        for method_name, metrics in results.items():
            f.write(f"{method_name}:\n")
            f.write(f"  Clustering Ratio: {metrics['clustering_ratio']:.3f}\n")
            f.write(f"  Unique x-coordinates: {metrics['unique_x_coords']}\n")
            f.write(f"  X-distribution: {metrics['x_distribution']}\n")
            f.write(f"  Primes: {sorted(metrics['primes'])}\n\n")

        f.write(f"Conclusion: {conclusion}\n")

    print(f"\nDetailed results saved to bias_test_results.txt")