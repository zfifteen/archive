#!/usr/bin/env python3
"""
Simple test for Z5D RSA Solver basic functionality.
"""

import math
import time
import concurrent.futures
from typing import Optional, Tuple, List, Dict, Any

class SimpleRSASolver:
    """
    Simplified RSA solver for testing parallel trial division.
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

def test_solver():
    """Test the solver on small semiprimes."""

    test_cases = [
        (15, (3, 5)),
        (21, (3, 7)),
        (35, (5, 7)),
        (91, (7, 13)),
        (143, (11, 13)),
        (323, (17, 19)),
        (899, (29, 31)),
    ]

    solver = SimpleRSASolver(max_workers=4)

    print("Simple RSA Solver Performance Validation")
    print("=" * 45)

    total_time = 0
    successful = 0

    for n, expected_factors in test_cases:
        print(f"\nTesting n = {n} (expected: {expected_factors[0]} × {expected_factors[1]})")

        start_time = time.time()
        factors = solver.factor_semiprime(n, search_radius=1000)
        elapsed = time.time() - start_time

        total_time += elapsed

        if factors:
            p, q = sorted(factors)
            expected_p, expected_q = sorted(expected_factors)

            if p == expected_p and q == expected_q:
                print(f"✅ SUCCESS: Found {p} × {q} in {elapsed:.4f}s")
                successful += 1
            else:
                print(f"❌ WRONG: Found {p} × {q}, expected {expected_p} × {expected_q}")
        else:
            print(f"❌ FAILED: No factors found in {elapsed:.4f}s")

    print("\nSummary:")
    print(f"  Tests run: {len(test_cases)}")
    print(f"  Successful: {successful}")
    print(f"  Success rate: {successful/len(test_cases)*100:.1f}%")
    print(f"  Total time: {total_time:.4f}s")
    print(f"  Average time: {total_time/len(test_cases):.4f}s")

if __name__ == "__main__":
    test_solver()