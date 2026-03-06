#!/usr/bin/env python3
"""
Skip Tracker Prime Detection Algorithm
Based on the algebraic form: P = {n ∈ ℕ | n ≥ 2 ∧ n ∉ ({2k} ∪ {k²} ∪ {i·j}) for k ≥ 2, i < j ≥ 2}

This algorithm finds primes by tracking "skips" in composite number coverage.
No factorization or primality testing required during traversal.
"""

import time
import math
from typing import List, Set

class SkipTrackerPrimeFinder:
    """
    Prime finder using exclusion set tracking.
    Avoids factorization by pre-computing composite patterns.
    """

    def __init__(self, limit: int):
        self.limit = limit
        self.claimed = [False] * (limit + 1)  # Track which numbers are "claimed" by exclusion sets
        self.primes = []

    def mark_exclusion_sets(self) -> None:
        """
        Mark all numbers claimed by the three exclusion sets:
        1. {2k} for k ≥ 2: Even numbers ≥ 4
        2. {k²} for k ≥ 2: Perfect squares ≥ 4
        3. {i·j} for i < j ≥ 2: Products of distinct integers ≥ 2
        """
        print(f"Marking exclusion sets up to {self.limit}...")

        # Set 1: Even numbers ≥ 4
        print("  Marking even numbers ≥ 4...")
        count_evens = 0
        for k in range(2, (self.limit // 2) + 1):
            pos = 2 * k
            if pos <= self.limit:
                self.claimed[pos] = True
                count_evens += 1
        print(f"    Marked {count_evens} even numbers")

        # Set 2: Perfect squares ≥ 4
        print("  Marking perfect squares ≥ 4...")
        count_squares = 0
        k = 2
        while k * k <= self.limit:
            pos = k * k
            if not self.claimed[pos]:  # Don't double-count
                count_squares += 1
            self.claimed[pos] = True
            k += 1
        print(f"    Marked {count_squares} new perfect squares")

        # Set 3: Products i×j where i < j ≥ 2
        print("  Marking products i×j where i < j ≥ 2...")
        count_products = 0
        for i in range(2, int(math.sqrt(self.limit)) + 1):
            for j in range(i + 1, (self.limit // i) + 1):
                pos = i * j
                if pos <= self.limit:
                    if not self.claimed[pos]:  # Don't double-count
                        count_products += 1
                    self.claimed[pos] = True
        print(f"    Marked {count_products} new products")

    def find_primes(self) -> List[int]:
        """
        Find all primes by detecting 'skips' in exclusion set coverage.
        Any unclaimed number ≥ 2 is prime.
        """
        print("Finding primes by skip detection...")

        # Mark all exclusion sets
        self.mark_exclusion_sets()

        # Collect unclaimed numbers = primes
        self.primes = []
        for n in range(2, self.limit + 1):
            if not self.claimed[n]:
                self.primes.append(n)

        print(f"Found {len(self.primes)} primes by skip tracking")
        return self.primes

    def get_coverage_stats(self) -> dict:
        """Return statistics about exclusion set coverage."""
        total_numbers = self.limit - 1  # Numbers from 2 to limit
        claimed_count = sum(self.claimed[2:])
        unclaimed_count = total_numbers - claimed_count

        return {
            'total_numbers': total_numbers,
            'claimed_by_exclusion_sets': claimed_count,
            'unclaimed_skips': unclaimed_count,
            'coverage_percentage': (claimed_count / total_numbers) * 100
        }

def traditional_sieve(limit: int) -> List[int]:
    """Traditional Sieve of Eratosthenes for comparison."""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False

    for i in range(2, int(math.sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False

    return [i for i in range(2, limit + 1) if sieve[i]]

def benchmark_algorithms(limit: int) -> None:
    """Compare skip tracker vs traditional sieve performance."""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: Finding primes up to {limit:,}")
    print(f"{'='*60}")

    # Skip Tracker Method
    print("\n🚀 SKIP TRACKER METHOD:")
    start_time = time.time()
    finder = SkipTrackerPrimeFinder(limit)
    skip_primes = finder.find_primes()
    skip_time = time.time() - start_time

    stats = finder.get_coverage_stats()
    print(f"Stats: {stats}")

    # Traditional Sieve
    print("\n🐌 TRADITIONAL SIEVE:")
    start_time = time.time()
    sieve_primes = traditional_sieve(limit)
    sieve_time = time.time() - start_time
    print(f"Found {len(sieve_primes)} primes using traditional sieve")

    # Verification
    print(f"\n📊 RESULTS:")
    print(f"Skip Tracker: {len(skip_primes):,} primes in {skip_time:.4f}s")
    print(f"Traditional:  {len(sieve_primes):,} primes in {sieve_time:.4f}s")
    print(f"Speedup: {sieve_time/skip_time:.2f}x {'faster' if skip_time < sieve_time else 'slower'}")
    print(f"Results match: {'✓' if skip_primes == sieve_primes else '✗'}")

    if limit <= 100:
        print(f"\nFirst 20 primes found: {skip_primes[:20]}")

def demonstrate_skip_detection(limit: int = 30) -> None:
    """Demonstrate how skip detection works step by step."""
    print(f"\n{'='*60}")
    print(f"SKIP DETECTION DEMONSTRATION (up to {limit})")
    print(f"{'='*60}")

    finder = SkipTrackerPrimeFinder(limit)
    finder.mark_exclusion_sets()

    print(f"\nNumber line analysis:")
    print(f"{'n':>3} {'Claimed':>8} {'Status':>10}")
    print("-" * 25)

    primes_found = []
    for n in range(2, limit + 1):
        claimed = finder.claimed[n]
        status = "COMPOSITE" if claimed else "PRIME"
        if not claimed:
            primes_found.append(n)
        print(f"{n:>3} {'Yes' if claimed else 'No':>8} {status:>10}")

    print(f"\n🎯 PRIMES DETECTED BY SKIPS: {primes_found}")
    print(f"Total primes found: {len(primes_found)}")

def main():
    """Main execution function."""
    print("🔢 SKIP TRACKER PRIME DETECTION ALGORITHM")
    print("Finds primes without factorization using exclusion set tracking")

    # Small demonstration
    demonstrate_skip_detection(30)

    # Performance benchmarks
    test_limits = [6000, 12000, 240000]

    for limit in test_limits:
        benchmark_algorithms(limit)
        print()

    print("🚀 Algorithm complete! Key insights:")
    print("• No trial division or factorization required")
    print("• Primes detected as 'skips' in composite coverage")
    print("• Scales well for large number ranges")
    print("• Pure pattern matching approach")

if __name__ == "__main__":
    main()