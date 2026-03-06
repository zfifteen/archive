#!/usr/bin/env python3
"""
Test script for Z5D RSA Solver performance validation.
"""

import time
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from core.z_5d_rsa_solver import Z5DRSASolver

def test_solver():
    """Test the Z5D RSA solver on small semiprimes."""

    # Test cases: small semiprimes
    test_cases = [
        (15, (3, 5)),
        (21, (3, 7)),
        (35, (5, 7)),
        (91, (7, 13)),
        (143, (11, 13)),
        (323, (17, 19)),
    ]

    solver = Z5DRSASolver(max_workers=4)

    print("Z5D RSA Solver Performance Validation")
    print("=" * 40)

    total_time = 0
    successful = 0

    for n, expected_factors in test_cases:
        print(f"\nTesting n = {n} (expected: {expected_factors[0]} × {expected_factors[1]})")

        start_time = time.time()
        factors = solver.factor_rsa_modulus(n, search_radius=100)
        elapsed = time.time() - start_time

        total_time += elapsed

        if factors:
            p, q = sorted(factors)
            expected_p, expected_q = sorted(expected_factors)

            if p == expected_p and q == expected_q:
                print(f"✅ SUCCESS: Found {p} × {q} in {elapsed:.3f}s")
                successful += 1
            else:
                print(f"❌ WRONG: Found {p} × {q}, expected {expected_p} × {expected_q}")
        else:
            print(f"❌ FAILED: No factors found in {elapsed:.3f}s")

    print("\nSummary:")
    print(f"  Tests run: {len(test_cases)}")
    print(f"  Successful: {successful}")
    print(f"  Success rate: {successful/len(test_cases)*100:.1f}%")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Average time: {total_time/len(test_cases):.3f}s")

    # Show solver stats
    stats = solver.get_performance_stats()
    print("\nSolver Statistics:")
    print(f"  Total attempts: {stats['total_attempts']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Average time: {stats['average_time']:.3f}s")
    print(f"  AMX enabled: {stats['amx_enabled']}")
    print(f"  Workers: {stats['max_workers']}")

if __name__ == "__main__":
    test_solver()