#!/usr/bin/env python3
"""
Comprehensive test for Z5D RSA Solver across multiple ranges.
"""

import math
import time
import concurrent.futures
from typing import Optional, Tuple, List, Dict, Any

class ComprehensiveRSASolver:
    """
    Comprehensive RSA solver for testing across ranges.
    """

    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or 4

    def factor_semiprime(self, n: int, search_radius: int = 1000) -> Optional[Tuple[int, int]]:
        """Factor semiprime n = p*q using parallel trial division."""
        if n < 4 or n % 2 == 0:
            return None

        sqrt_n = int(math.sqrt(n))
        p_min = max(2, sqrt_n - search_radius)
        p_max = sqrt_n + search_radius

        # Parallel trial division
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            chunk_size = max(100, (p_max - p_min + 1) // self.max_workers)

            current_min = p_min
            while current_min <= p_max:
                current_max = min(current_min + chunk_size - 1, p_max)
                futures.append(executor.submit(self._trial_division_chunk, n, current_min, current_max))
                current_min = current_max + 1

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    return result

        return None

    def _trial_division_chunk(self, n: int, p_min: int, p_max: int) -> Optional[Tuple[int, int]]:
        """Trial division for a chunk of p values."""
        start_p = p_min if p_min % 2 == 1 else p_min + 1

        for p in range(start_p, p_max + 1, 2):
            if n % p == 0:
                q = n // p
                if self._is_prime(p) and self._is_prime(q):
                    return (p, q)

        return None

    def _is_prime(self, n: int) -> bool:
        """Basic primality test."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False

        sqrt_n = int(math.sqrt(n)) + 1
        for i in range(3, sqrt_n, 2):
            if n % i == 0:
                return False

        return True

def generate_test_cases():
    """Generate test cases across different ranges."""

    # Small semiprimes (n < 100)
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    small_semiprimes = []
    for i in range(len(small_primes)):
        for j in range(i+1, len(small_primes)):
            n = small_primes[i] * small_primes[j]
            if n < 100:
                small_semiprimes.append((n, (small_primes[i], small_primes[j])))

    # Medium semiprimes (100 <= n < 10000)
    medium_primes = [53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
    medium_semiprimes = []
    for i in range(len(medium_primes)):
        for j in range(i+1, len(medium_primes)):
            n = medium_primes[i] * medium_primes[j]
            if 100 <= n < 10000:
                medium_semiprimes.append((n, (medium_primes[i], medium_primes[j])))

    # Large semiprimes (10000 <= n < 100000)
    large_primes = [127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229]
    large_semiprimes = []
    for i in range(len(large_primes)):
        for j in range(i+1, len(large_primes)):
            n = large_primes[i] * large_primes[j]
            if 10000 <= n < 100000:
                large_semiprimes.append((n, (large_primes[i], large_primes[j])))

    return {
        "Small (< 100)": small_semiprimes,
        "Medium (100-9999)": medium_semiprimes,
        "Large (10000-99999)": large_semiprimes
    }

def test_range(solver: ComprehensiveRSASolver, range_name: str, test_cases: List[Tuple[int, Tuple[int, int]]], search_radius: int = 1000):
    """Test a specific range."""

    print(f"\n{range_name} Range Tests")
    print("-" * (len(range_name) + 12))

    total_time = 0
    successful = 0
    times = []

    for n, expected_factors in test_cases:
        start_time = time.time()
        factors = solver.factor_semiprime(n, search_radius=search_radius)
        elapsed = time.time() - start_time

        total_time += elapsed
        times.append(elapsed)

        if factors:
            p, q = sorted(factors)
            expected_p, expected_q = sorted(expected_factors)

            if p == expected_p and q == expected_q:
                print(f"✅ n={n}: {p}×{q} ({elapsed:.4f}s)")
                successful += 1
            else:
                print(f"❌ n={n}: Wrong factors {p}×{q}, expected {expected_p}×{expected_q}")
        else:
            print(f"❌ n={n}: No factors found ({elapsed:.4f}s)")

    avg_time = total_time / len(test_cases) if test_cases else 0
    success_rate = successful / len(test_cases) * 100 if test_cases else 0
    max_time = max(times) if times else 0
    min_time = min(times) if times else 0

    print(f"\nRange Summary ({range_name}):")
    print(f"  Tests: {len(test_cases)}")
    print(f"  Success: {successful} ({success_rate:.1f}%)")
    print(f"  Total time: {total_time:.4f}s")
    print(f"  Avg time: {avg_time:.4f}s")
    print(f"  Min/Max time: {min_time:.4f}s / {max_time:.4f}s")

    return {
        'tests': len(test_cases),
        'successful': successful,
        'success_rate': success_rate,
        'total_time': total_time,
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time
    }

def run_comprehensive_tests():
    """Run comprehensive tests across all ranges."""

    print("Z5D RSA Solver Comprehensive Range Testing")
    print("=" * 50)

    solver = ComprehensiveRSASolver(max_workers=4)
    test_ranges = generate_test_cases()

    overall_stats = {
        'total_tests': 0,
        'total_successful': 0,
        'total_time': 0,
        'ranges': {}
    }

    for range_name, test_cases in test_ranges.items():
        stats = test_range(solver, range_name, test_cases)
        overall_stats['ranges'][range_name] = stats
        overall_stats['total_tests'] += stats['tests']
        overall_stats['total_successful'] += stats['successful']
        overall_stats['total_time'] += stats['total_time']

    print("\n" + "=" * 50)
    print("OVERALL PERFORMANCE SUMMARY")
    print("=" * 50)

    overall_success_rate = overall_stats['total_successful'] / overall_stats['total_tests'] * 100 if overall_stats['total_tests'] else 0
    overall_avg_time = overall_stats['total_time'] / overall_stats['total_tests'] if overall_stats['total_tests'] else 0

    print(f"Total tests run: {overall_stats['total_tests']}")
    print(f"Total successful: {overall_stats['total_successful']}")
    print(f"Overall success rate: {overall_success_rate:.1f}%")
    print(f"Total time: {overall_stats['total_time']:.4f}s")
    print(f"Average time per test: {overall_avg_time:.4f}s")

    print("\nRange Breakdown:")
    for range_name, stats in overall_stats['ranges'].items():
        print(f"  {range_name}: {stats['successful']}/{stats['tests']} ({stats['success_rate']:.1f}%) - avg {stats['avg_time']:.4f}s")

    print("\nSolver Configuration:")
    print(f"  Max workers: {solver.max_workers}")
    print(f"  Search radius: 1000 (for all tests)")

if __name__ == "__main__":
    run_comprehensive_tests()