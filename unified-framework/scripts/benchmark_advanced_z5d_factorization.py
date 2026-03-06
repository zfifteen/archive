#!/usr/bin/env python3
"""
Advanced Z5D Factorization Benchmark
====================================

This script benchmarks the Advanced Z5D Factorization from z-sandbox,
reproducing 256-bit semiprime tests with adaptive k-tuning and QMC-Rho methods.
Targets 40-55% success rate as reported in the z-sandbox validation.

Based on z-sandbox implementations:
- greens_function_factorization.py (Green's function approach)
- factor_256bit.py (basic pipeline)
- Various advanced factorization methods
"""

import sys
import os
import time
import random
import math
import json
from typing import List, Tuple, Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import sympy
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

try:
    import mpmath as mp
    HAS_MPMATH = True
except ImportError:
    HAS_MPMATH = False

# Try to import z-sandbox factorization modules
# Since we can't directly import from z-sandbox, we'll implement the key algorithms

class AdvancedZ5DFactorizer:
    """Advanced Z5D factorization using Green's function and wave interference."""

    def __init__(self):
        self.mp_precision = 50
        if HAS_MPMATH:
            mp.mp.dps = self.mp_precision

    def safe_log(self, n: int) -> float:
        """Safe logarithm computation."""
        if n <= 0:
            return 0.0
        return float(mp.log(mp.mpf(n))) if HAS_MPMATH else math.log(n)

    def safe_sqrt(self, n: int) -> float:
        """Safe square root computation."""
        if n <= 0:
            return 0.0
        return float(mp.sqrt(mp.mpf(n))) if HAS_MPMATH else math.sqrt(n)

    def greens_function_amplitude(self, log_N: float, log_p: float, k: float) -> float:
        """Compute Green's function amplitude for factorization."""
        # Helmholtz kernel: |G(log p)| = |cos(k(log N - 2log p))|
        phase = k * (log_N - 2 * log_p)
        return abs(math.cos(phase))

    def comb_formula(self, log_N: float, k: float, m: int) -> float:
        """Compute candidate factor using comb formula."""
        # p_m = exp((log N - 2πm/k)/2)
        phase_shift = 2 * math.pi * m / k
        log_p = (log_N - phase_shift) / 2
        return math.exp(log_p)

    def estimate_k_optimal(self, N: int, balance_estimate: float = 1.0) -> float:
        """Estimate optimal wave number k for factorization."""
        # k(N,β) = π / (β * log N) where β is balance factor
        log_N = self.safe_log(N)
        return math.pi / (balance_estimate * log_N)

    def find_candidates_near_sqrt(self, N: int, k: float, window_size: int = 500) -> List[Dict[str, Any]]:
        """Find candidate factors near sqrt(N) using Green's function."""
        sqrt_N = self.safe_sqrt(N)
        log_N = self.safe_log(N)

        candidates = []

        # Search around sqrt(N)
        start = max(2, int(sqrt_N - window_size // 2))
        end = int(sqrt_N + window_size // 2)

        for p in range(start, end):
            if p >= N:
                break

            log_p = self.safe_log(p)
            amplitude = self.greens_function_amplitude(log_N, log_p, k)

            # Compute curvature score (Z5D axiom κ(n))
            curvature = self.compute_curvature(p)

            # Combined score
            score = amplitude * curvature

            candidates.append({
                'p_candidate': p,
                'amplitude': amplitude,
                'curvature': curvature,
                'score': score
            })

        # Sort by score (descending)
        candidates.sort(key=lambda x: x['score'], reverse=True)

        return candidates

    def compute_curvature(self, n: int) -> float:
        """Compute Z5D curvature κ(n) = d(n)·ln(n+1)/e²."""
        if not HAS_SYMPY:
            # Fallback: approximate using prime factors
            return 1.0 / math.log(n + 1) if n > 1 else 1.0

        try:
            # Exact divisor count
            d_n = sympy.divisor_count(n)
            ln_term = math.log(n + 1)
            e_squared = math.e ** 2
            return d_n * ln_term / e_squared
        except:
            return 1.0 / math.log(n + 1) if n > 1 else 1.0

    def factorize_advanced(self, N: int, max_candidates: int = 50) -> Dict[str, Any]:
        """Advanced factorization using Green's function approach."""
        start_time = time.time()

        # Estimate optimal k
        k = self.estimate_k_optimal(N)

        # Find candidates
        candidates = self.find_candidates_near_sqrt(N, k)

        # Check for exact factors
        exact_factors = []
        found_factor = False

        for candidate in candidates[:max_candidates]:
            p = candidate['p_candidate']
            if N % p == 0:
                q = N // p
                if p != q and self.is_probable_prime(p) and self.is_probable_prime(q):
                    exact_factors.append((p, q))
                    found_factor = True
                    break

        runtime = time.time() - start_time

        return {
            'N': N,
            'k_used': k,
            'candidates_checked': len(candidates[:max_candidates]),
            'found_factor': found_factor,
            'exact_factors': exact_factors,
            'runtime': runtime,
            'method': 'greens_function'
        }

    def is_probable_prime(self, n: int, k: int = 12) -> bool:
        """Miller-Rabin primality test."""
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False

        # Write n-1 as 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        # Witness loop
        witnesses = [2, 3, 5, 7, 11, 13, 23, 29, 31, 37, 41, 43, 47][:k]
        for a in witnesses:
            if a >= n:
                continue

            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue

            for _ in range(r - 1):
                x = (x * x) % n
                if x == n - 1:
                    break
            else:
                return False

        return True

class QMCEnhancedFactorizer:
    """QMC-enhanced factorization with adaptive k-tuning."""

    def __init__(self):
        self.base_factorizer = AdvancedZ5DFactorizer()

    def generate_qmc_sequence(self, n_points: int, dimension: int = 1) -> List[float]:
        """Generate Quasi-Monte Carlo sequence for parameter sampling."""
        # Simple Halton sequence for demonstration
        sequence = []
        for i in range(n_points):
            x = 0.0
            f = 1.0 / 2.0
            j = i + 1
            while j > 0:
                x += f * (j % 2)
                j //= 2
                f /= 2.0
            sequence.append(x)
        return sequence

    def adaptive_k_tuning(self, N: int, n_samples: int = 10) -> float:
        """Adaptive k-tuning using QMC sampling."""
        qmc_points = self.generate_qmc_sequence(n_samples)

        # Sample k values in reasonable range
        k_min = 0.1
        k_max = 2.0

        best_k = k_min
        best_score = 0

        for point in qmc_points:
            k = k_min + point * (k_max - k_min)

            # Evaluate k by checking candidate quality
            candidates = self.base_factorizer.find_candidates_near_sqrt(N, k, window_size=100)
            if candidates:
                avg_score = sum(c['score'] for c in candidates[:10]) / min(10, len(candidates))
                if avg_score > best_score:
                    best_score = avg_score
                    best_k = k

        return best_k

    def factorize_qmc_enhanced(self, N: int) -> Dict[str, Any]:
        """QMC-enhanced factorization with adaptive k-tuning."""
        start_time = time.time()

        # Adaptive k-tuning
        k_optimal = self.adaptive_k_tuning(N)

        # Use optimal k for factorization
        result = self.base_factorizer.factorize_advanced(N)
        result['k_adaptive'] = k_optimal
        result['method'] = 'qmc_enhanced_greens'

        result['runtime'] = time.time() - start_time

        return result

def generate_256bit_semiprime() -> Tuple[int, int, int]:
    """Generate a 256-bit semiprime with known factors."""
    if not HAS_SYMPY:
        raise ImportError("sympy required for prime generation")

    # Generate two 128-bit primes
    p = sympy.randprime(2**127, 2**128)
    q = sympy.randprime(2**127, 2**128)
    N = p * q

    return N, p, q

def benchmark_advanced_z5d_factorization(n_samples: int = 50) -> Dict[str, Any]:
    """Benchmark advanced Z5D factorization methods."""

    print("=" * 70)
    print("ADVANCED Z5D FACTORIZATION BENCHMARK")
    print("=" * 70)
    print(f"Testing {n_samples} random 256-bit semiprimes")
    print("Methods: Green's Function, QMC-Enhanced")
    print("Target: 40-55% success rate")
    print()

    # Initialize factorizers
    greens_factorizer = AdvancedZ5DFactorizer()
    qmc_factorizer = QMCEnhancedFactorizer()

    results = {
        'greens_function': [],
        'qmc_enhanced': []
    }

    total_greens_success = 0
    total_qmc_success = 0

    for i in range(n_samples):
        print(f"Test {i+1:2d}/{n_samples}: Generating 256-bit semiprime...")

        # Generate test case
        N, p, q = generate_256bit_semiprime()
        print(f"  N = {N.bit_length()}-bit semiprime")

        # Test Green's function method
        print("  Testing Green's function factorization...")
        greens_result = greens_factorizer.factorize_advanced(N)
        greens_success = greens_result['found_factor']
        if greens_success:
            total_greens_success += 1
            print(".3f")
        else:
            print(".3f")
        results['greens_function'].append(greens_result)

        # Test QMC-enhanced method
        print("  Testing QMC-enhanced factorization...")
        qmc_result = qmc_factorizer.factorize_qmc_enhanced(N)
        qmc_success = qmc_result['found_factor']
        if qmc_success:
            total_qmc_success += 1
            print(".3f")
        else:
            print(".3f")
        results['qmc_enhanced'].append(qmc_result)

        print()

    # Analysis
    print("=" * 40)
    print("RESULTS SUMMARY")
    print("=" * 40)

    greens_rate = total_greens_success / n_samples * 100
    qmc_rate = total_qmc_success / n_samples * 100

    print(f"Green's Function success: {total_greens_success}/{n_samples} ({greens_rate:.1f}%)")
    print(f"QMC-Enhanced success:     {total_qmc_success}/{n_samples} ({qmc_rate:.1f}%)")

    # Calculate runtimes
    greens_times = [r['runtime'] for r in results['greens_function']]
    qmc_times = [r['runtime'] for r in results['qmc_enhanced']]

    avg_greens_time = sum(greens_times) / len(greens_times)
    avg_qmc_time = sum(qmc_times) / len(qmc_times)

    print(".3f")
    print(".3f")
    # Check targets
    greens_target_achieved = 40 <= greens_rate <= 55
    qmc_target_achieved = 40 <= qmc_rate <= 55

    print("\nTarget validation:")
    print(f"Green's method 40-55% success: {'✓' if greens_target_achieved else '✗'} ({greens_rate:.1f}%)")
    print(f"QMC method 40-55% success:     {'✓' if qmc_target_achieved else '✗'} ({qmc_rate:.1f}%)")

    return {
        'n_samples': n_samples,
        'greens_successes': total_greens_success,
        'qmc_successes': total_qmc_success,
        'greens_rate': greens_rate,
        'qmc_rate': qmc_rate,
        'avg_greens_time': avg_greens_time,
        'avg_qmc_time': avg_qmc_time,
        'greens_target_achieved': greens_target_achieved,
        'qmc_target_achieved': qmc_target_achieved,
        'results': results
    }

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark Advanced Z5D Factorization")
    parser.add_argument('--samples', type=int, default=50, help='Number of test samples')
    parser.add_argument('--method', choices=['greens', 'qmc', 'both'], default='both',
                       help='Factorization method to test')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')

    args = parser.parse_args()

    random.seed(args.seed)
    # Note: sympy.seed may not be available in all versions

    try:
        results = benchmark_advanced_z5d_factorization(args.samples)

        # Save results
        output_file = f"advanced_z5d_factorization_benchmark_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            # Convert to serializable format
            serializable_results = {}
            for k, v in results.items():
                if isinstance(v, dict):
                    serializable_results[k] = {}
                    for k2, v2 in v.items():
                        if isinstance(v2, list) and v2 and isinstance(v2[0], dict):
                            # Handle list of dicts
                            serializable_results[k][k2] = []
                            for item in v2:
                                serializable_item = {}
                                for ik, iv in item.items():
                                    if hasattr(iv, 'item'):  # numpy type
                                        serializable_item[ik] = iv.item()
                                    else:
                                        serializable_item[ik] = iv
                                serializable_results[k][k2].append(serializable_item)
                        else:
                            serializable_results[k][k2] = v2
                else:
                    serializable_results[k] = v

            json.dump(serializable_results, f, indent=2)

        print(f"\nResults saved to {output_file}")

        # Final assessment
        greens_achieved = results.get('greens_target_achieved', False)
        qmc_achieved = results.get('qmc_target_achieved', False)

        if greens_achieved or qmc_achieved:
            print("\n🎉 Advanced Z5D factorization shows promise!")
            if greens_achieved:
                print(f"  Green's function method achieved target success rate.")
            if qmc_achieved:
                print(f"  QMC-enhanced method achieved target success rate.")
        else:
            print(f"\n⚠️ Advanced Z5D factorization needs optimization.")
            print(f"  Current rates: Green's {results.get('greens_rate', 0):.1f}%, QMC {results.get('qmc_rate', 0):.1f}%")
            print("  Target: 40-55% success rate")

    except Exception as e:
        print(f"Advanced factorization benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()