#!/usr/bin/env python3
"""
Z5D Factorization Scaling Analysis
==================================

This script analyzes the scaling behavior of Z5D factorization by testing
on semi-primes of increasing bit sizes (16, 32, 64, 128 bits).

Focus: Understand time complexity, success rates, and opportunities for refinement.
"""

import time
import math
import random
import json
from typing import List, Tuple, Dict
import mpmath as mp

try:
    from sympy import nextprime
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

# Import Z5D factorization
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'applications', 'primes', 'core'))
from rsa_probe_validation import probe_semiprime_with_timeout

mp.dps = 50  # High precision for Z-framework

def generate_semiprime(bits: int) -> Tuple[str, int, int]:
    """
    Generate a semi-prime with close factors (RSA-like).
    """
    prime_bits = bits // 2
    min_val = 2**(prime_bits - 1)
    max_val = 2**prime_bits - 1
    
    if SYMPY_AVAILABLE:
        p = nextprime(min_val + random.randint(0, min_val // 2))
        d = random.randint(2, min(2**(prime_bits//4), 10000))  # Small difference for close factors
        q = nextprime(p + d)
    else:
        # Fallback
        p = generate_prime(min_val, min_val + min_val // 2)
        d = random.randint(2, min(1000, min_val // 100))
        candidate = p + d
        while not is_prime(candidate):
            candidate += 1
        q = candidate
    
    n = p * q
    return str(n), p, q
    """
    Generate a semi-prime of approximately the given bit size.

    Returns:
        str: The semi-prime as string
        int: Factor p
        int: Factor q
    """
    # Generate two primes of roughly equal size
    prime_bits = bits // 2

    if SYMPY_AVAILABLE:
        # Use sympy for faster prime generation
        min_val = 2**(prime_bits - 1) + 1
        p = nextprime(min_val + random.randint(0, 2**(prime_bits//2)))
        q = nextprime(p + random.randint(1, 2**(prime_bits//2)))
    else:
        # Fallback simple method (slower for large bits)
        def is_prime(n):
            if n <= 1:
                return False
            if n <= 3:
                return True
            if n % 2 == 0 or n % 3 == 0:
                return False
            i = 5
            while i * i <= n:
                if n % i == 0 or n % (i + 2) == 0:
                    return False
                i += 6
            return True

        def generate_prime(min_val, max_val):
            for attempt in range(1000):  # Limit attempts
                candidate = random.randint(min_val, max_val)
                if is_prime(candidate):
                    return candidate
            # If no prime found, use a known small prime offset
            return min_val + 3 if is_prime(min_val + 3) else min_val + 1

        min_val = 2**(prime_bits - 1) + 1
        max_val = min(2**prime_bits - 1, min_val + 2**(prime_bits//2))

        p = generate_prime(min_val, max_val)
        q = generate_prime(min_val, max_val)

    n = p * q
    return str(n), p, q

def run_scaling_test() -> Dict:
    """
    Run scaling analysis on Z5D factorization.

    Tests bit sizes: 16, 32, 64, 128
    For each size: generate 2 semi-primes, test factorization, measure time
    """
    bit_sizes = [16, 32, 64, 128]
    results = {}

    print("Z5D Factorization Scaling Analysis")
    print("=" * 50)
    print("Testing bit sizes: 16, 32, 64, 128")
    print("For each size: 2 semi-primes, Z5D factorization with timeout")
    print()

    for bits in bit_sizes:
        print(f"Testing {bits}-bit semi-primes...")
        print("-" * 30)

        size_results = []
        total_time = 0

        for i in range(2):  # Test 2 samples per size for speed
            print(f"  Sample {i+1}/2: Generating {bits}-bit semi-prime...")

            # Generate semi-prime
            n_str, p, q = generate_semiprime(bits)
            actual_bits = len(bin(int(n_str))) - 2  # Actual bit length

            print(f"    Generated {actual_bits}-bit number: {n_str[:20]}...")
            print(f"    Factors: {p} × {q}")

            # Test Z5D factorization
            trials = 1000 * (2 ** ((bits - 16) // 16))  # Adaptive trials based on bit size
            timeout = 15 + 15 * ((bits - 16) // 16)  # Adaptive timeout

            start_time = time.time()
            try:
                factor = probe_semiprime_with_timeout(
                    n_str,
                    trials=trials,
                    timeout_seconds=timeout,
                    enable_error_compensation=True
                )
            except TimeoutError:
                factor = None
                runtime = timeout
            except Exception as e:
                print(f"    Error: {e}")
                factor = None
                runtime = time.time() - start_time
            else:
                runtime = time.time() - start_time

            total_time += runtime

            # Check if correct factor found
            success = factor is not None and (factor == p or factor == q)

            sample_result = {
                'bits': actual_bits,
                'n_str': n_str,
                'factors': (p, q),
                'factor_found': factor,
                'success': success,
                'runtime': runtime,
                'trials': trials,
                'timeout': timeout
            }

            size_results.append(sample_result)

            print(f"    Runtime: {runtime:.3f}s")
            print(f"    Factor found: {factor}")
            print(f"    Success: {'✓' if success else '✗'}")

        # Size summary
        avg_time = total_time / 2
        success_rate = sum(1 for r in size_results if r['success']) / 2

        size_summary = {
            'bits': bits,
            'samples': size_results,
            'avg_runtime': avg_time,
            'success_rate': success_rate,
            'total_time': total_time
        }

        results[f'{bits}bit'] = size_summary

        print(f"  {bits}-bit Summary:")
        print(f"    Average time: {avg_time:.3f}s")
        print(".1%")
        print(f"    Total time: {total_time:.1f}s")
        print()

    return results

def analyze_scaling(results: Dict) -> str:
    """
    Analyze the scaling behavior and suggest refinements.
    """
    analysis = []
    analysis.append("Z5D Factorization Scaling Analysis Report")
    analysis.append("=" * 50)
    analysis.append("")

    # Extract scaling data
    bit_sizes = []
    avg_times = []
    success_rates = []

    for key, size_data in results.items():
        bits = size_data['bits']
        avg_time = size_data['avg_runtime']
        success_rate = size_data['success_rate']

        bit_sizes.append(bits)
        avg_times.append(avg_time)
        success_rates.append(success_rate)

        analysis.append(f"{bits}-bit Results:")
        analysis.append(f"  Average runtime: {avg_time:.3f}s")
        analysis.append(f"  Success rate: {success_rate*100:.1f}%")
        analysis.append("")

    # Scaling analysis
    analysis.append("Scaling Behavior:")
    analysis.append("")

    # Time scaling
    if len(avg_times) >= 2:
        time_ratios = []
        for i in range(1, len(avg_times)):
            ratio = avg_times[i] / avg_times[i-1]
            bit_ratio = bit_sizes[i] / bit_sizes[i-1]
            time_ratios.append((ratio, bit_ratio))

        analysis.append("Time scaling ratios:")
        for i, (time_ratio, bit_ratio) in enumerate(time_ratios):
            analysis.append(f"  {bit_sizes[i]}→{bit_sizes[i+1]} bits: {time_ratio:.2f}x time for {bit_ratio:.1f}x bits")

        # Estimate complexity
        if time_ratios:
            avg_time_ratio = sum(r[0] for r in time_ratios) / len(time_ratios)
            analysis.append(f"  Average time scaling: ~{avg_time_ratio:.2f}x per doubling")

            if avg_time_ratio > 4:
                analysis.append("  → Exponential scaling (O(2^n)) - severe limitation")
            elif avg_time_ratio > 2:
                analysis.append("  → Super-linear scaling (worse than O(n))")
            elif avg_time_ratio > 1.5:
                analysis.append("  → Approximately O(n log n) scaling")
            else:
                analysis.append("  → Near-linear scaling")

    analysis.append("")
    analysis.append("Success Rate Trends:")
    if success_rates:
        analysis.append(f"  16-bit: {success_rates[0]*100:.0f}%")
        analysis.append(f"  32-bit: {success_rates[1]*100:.0f}%")
        analysis.append(f"  64-bit: {success_rates[2]*100:.0f}%")
        analysis.append(f"  128-bit: {success_rates[3]*100:.0f}%")

        if success_rates[3] < 0.5:
            analysis.append("  → Success rate drops significantly at 128-bit scale")

    analysis.append("")
    analysis.append("Z5D Geometric Invariants (Why scaling matters):")
    analysis.append("• Z = A × (B / c) where c = φ (golden ratio)")
    analysis.append("• θ'(n,k) = φ × ((n mod φ)/φ)^k for prime density mapping")
    analysis.append("• κ(n) = d(n) · ln(n+1) / e² curvature constraint")
    analysis.append("• Current implementation: Naive search around k_est")

    analysis.append("")
    analysis.append("Refinement Opportunities (Geometric Priority):")
    analysis.append("")

    analysis.append("1. Curvature-Guided Search:")
    analysis.append("   - Why: κ(n) provides local density information")
    analysis.append("   - How: Use κ(n) to bias search toward high-density regions")
    analysis.append("   - Expected: 5-10x speedup through geometric focusing")

    analysis.append("")
    analysis.append("2. Multi-Scale Resolution:")
    analysis.append("   - Why: θ'(n,k) scales with φ^k - use hierarchical search")
    analysis.append("   - How: Coarse-to-fine search with φ-scaled k increments")
    analysis.append("   - Expected: Logarithmic reduction in search space")

    analysis.append("")
    analysis.append("3. Invariant-Based Bounds:")
    analysis.append("   - Why: Z = A × (B / c) constrains the search space")
    analysis.append("   - How: Derive tighter k bounds from invariant relationships")
    analysis.append("   - Expected: Reduce trials by geometric factors")

    analysis.append("")
    analysis.append("4. Error Growth Compensation:")
    analysis.append("   - Why: O(1/log k) error accumulates at scale")
    analysis.append("   - How: Scale-adaptive calibration with empirical corrections")
    analysis.append("   - Expected: Maintain accuracy at crypto scales")

    analysis.append("")
    analysis.append("5. Parallel Geodesic Exploration:")
    analysis.append("   - Why: Independent k trials can be vectorized")
    analysis.append("   - How: GPU acceleration for simultaneous θ' computations")
    analysis.append("   - Expected: Hardware-accelerated scaling improvements")

    analysis.append("")
    analysis.append("Next Steps for Scaling Up:")
    analysis.append("1. Implement curvature-guided search (κ(n) biasing)")
    analysis.append("2. Add multi-scale resolution with φ-scaled increments")
    analysis.append("3. Validate on 256-bit numbers with refined algorithms")
    analysis.append("4. Integrate with classical methods for hybrid approach")
    analysis.append("5. Explore quantum-resistant geometric optimizations")

    return "\n".join(analysis)

def main():
    """Main execution."""
    # Set random seed for reproducibility
    random.seed(42)

    # Run scaling test
    print("Starting Z5D factorization scaling analysis...")
    results = run_scaling_test()

    # Generate analysis
    analysis = analyze_scaling(results)

    # Print analysis
    print("\n" + analysis)

    # Save results
    with open('z5d_scaling_results.json', 'w') as f:
        # Convert to JSON-serializable
        json_results = {}
        for key, size_data in results.items():
            json_results[key] = {
                'bits': size_data['bits'],
                'avg_runtime': size_data['avg_runtime'],
                'success_rate': size_data['success_rate'],
                'total_time': size_data['total_time'],
                'samples': [
                    {
                        'bits': s['bits'],
                        'n_str': s['n_str'][:50] + "..." if len(s['n_str']) > 50 else s['n_str'],
                        'factors': s['factors'],
                        'factor_found': s['factor_found'],
                        'success': s['success'],
                        'runtime': s['runtime'],
                        'trials': s['trials'],
                        'timeout': s['timeout']
                    } for s in size_data['samples']
                ]
            }
        json.dump(json_results, f, indent=2)

    print("\nResults saved to z5d_scaling_results.json")

if __name__ == "__main__":
    main()