#!/usr/bin/env python3
"""
Python Prime Generator — Ported from prime_generator.c

Enhanced GMP-powered prime scanner with optimizations.
Build: python python_prime_generator.py (requires gmpy2)
Usage: python python_prime_generator.py --start 10^18 --count 1000 --csv
"""

import argparse
import sys
import time
import math

try:
    import gmpy2

    GMPY2_AVAILABLE = True
except ImportError:
    GMPY2_AVAILABLE = False
    print(
        "Error: gmpy2 required for GMP speed. Install with: pip install gmpy2",
        file=sys.stderr,
    )
    sys.exit(1)

# Z5D predictor integration (stub: directory not found, fallback sequential)
Z5D_ENHANCED = False  # Set to True if ../z5d-predictor-c exists
ZF_KAPPA_STAR_DEFAULT = 0.2615  # Stub values
ZF_KAPPA_GEO_DEFAULT = 1.0

# Bootstrap for CI (stub)
BOOTSTRAP_ENABLED = True
ZF_BOOTSTRAP_RESAMPLES_DEFAULT = 1000


class PythonPrimeGenerator:
    """Ported prime generator class."""

    def __init__(self, verbose=False, stats=False):
        self.verbose = verbose
        self.stats = stats
        self.wheel_residues = [1, 11, 13, 17, 19, 23, 29, 31]
        self.wheel_gaps = [10, 2, 4, 2, 4, 6, 2, 6]
        self.small_primes = [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    def parse_bigint(self, s: str) -> int:
        """Parse strings like '10^1234' or plain decimal."""
        if not s:
            raise ValueError("Empty string")
        caret = s.find("^")
        if caret == -1:
            return int(s)
        base_str = s[:caret]
        exp_str = s[caret + 1 :]
        base = int(base_str)
        exp = int(exp_str)
        if exp > 100000:
            raise ValueError(f"Exponent {exp} too large (max 100000)")
        return base**exp

    def adaptive_reps(self, bits: int) -> int:
        """Adaptive Miller-Rabin reps based on bit size."""
        if bits <= 64:
            return 10
        elif bits <= 512:
            return 25
        elif bits <= 4096:
            return 40
        else:
            return 64

    def lucas_prefilter(self, n: int) -> bool:
        """Lucas pre-filter: reject if divisible by small primes."""
        for p in self.small_primes:
            if n % p == 0:
                return n == p  # True only if n IS the prime itself
        return True

    def is_prime_mr(self, n: int) -> bool:
        """Miller-Rabin using gmpy2."""
        if n < 2:
            return False
        if n in (2, 3, 5):
            return True
        if n % 2 == 0 or n % 3 == 0 or n % 5 == 0:
            return False
        bits = n.bit_length()
        reps = self.adaptive_reps(bits)
        return bool(gmpy2.is_prime(n, reps))

    def is_mersenne_prime_ll(self, p: int) -> bool:
        """Lucas-Lehmer for M_p = 2^p - 1."""
        if p == 2:
            return True
        if p < 2:
            return False
        Mp = (1 << p) - 1  # 2^p - 1
        s = 4
        for _ in range(p - 2):
            s = (s * s - 2) % Mp
        return s == 0

    def detect_mersenne_and_test(self, n: int) -> bool:
        """Check if n is Mersenne prime."""
        if n < 3:
            return False
        t = n + 1
        # Check if power of two: bit_count == 1
        if bin(t).count("1") != 1:
            return False
        p = t.bit_length() - 1
        return self.is_mersenne_prime_ll(p)

    def align_wheel30_candidate(self, candidate: int) -> int:
        """Align to nearest wheel-30 residue at or above candidate."""
        mod = candidate % 30
        for r in self.wheel_residues:
            if mod == r:
                return candidate  # Already aligned
            elif mod < r:
                return candidate + (r - mod)
        # Wrap to next 30-block + first residue
        return candidate + (30 - mod + self.wheel_residues[0])

    def next_wheel30_candidate(self, candidate: int) -> int:
        """Move to next wheel-30 candidate."""
        mod = candidate % 30
        for i, r in enumerate(self.wheel_residues):
            if mod == r:
                return candidate + self.wheel_gaps[i]
        # Find next
        for i, r in enumerate(self.wheel_residues):
            if mod < r:
                return candidate + (r - mod)
        return candidate + (30 - mod + 1)

    def next_prime_from(self, start: int) -> tuple[int, bool]:
        """Find next prime >= start, return (prime, is_mersenne)."""
        candidate = self.align_wheel30_candidate(max(start, 3))

        candidates_tested = 0
        wheel_filtered = 0
        lucas_filtered = 0
        mr_calls = 0

        while True:
            candidates_tested += 1
            wheel_filtered += 1  # All are wheel candidates

            if not self.lucas_prefilter(candidate):
                lucas_filtered += 1
                candidate = self.next_wheel30_candidate(candidate)
                continue

            mr_calls += 1
            if self.is_prime_mr(candidate):
                is_mers = self.detect_mersenne_and_test(candidate)
                if self.verbose:
                    print(
                        f"Found prime: {candidate}, is_mersenne: {is_mers}",
                        file=sys.stderr,
                    )
                if self.stats:
                    reduction_pct = (
                        100.0 * (1.0 - (mr_calls / candidates_tested))
                        if candidates_tested > 0
                        else 0.0
                    )
                    print(
                        f"LIS-Corrector stats: Candidates {candidates_tested}, Wheel filtered {wheel_filtered}, Lucas filtered {lucas_filtered}, MR calls {mr_calls}, Reduction {reduction_pct:.2f}%",
                        file=sys.stderr,
                    )
                return candidate, is_mers

            candidate = self.next_wheel30_candidate(candidate)

    def generate_primes(self, start_str: str, count: int, csv: bool = False):
        """Generate count primes starting from start_str."""
        start = self.parse_bigint(start_str)
        primes = []
        current = start
        for i in range(1, count + 1):
            start_time = time.perf_counter()
            prime, is_mers = self.next_prime_from(current)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            primes.append(prime)
            if csv:
                print(f"{i},{prime},{1 if is_mers else 0},{elapsed_ms:.3f}")
            else:
                print(f"{i}) prime={prime}*  ({elapsed_ms:.3f} ms)")
                if is_mers:
                    print("  [Mersenne detected]")
            current = prime + 2  # Prepare for next
        return primes


def main():
    parser = argparse.ArgumentParser(
        description="Python Prime Generator (ported from C)"
    )
    parser.add_argument(
        "--start", required=True, help="Starting candidate (e.g., 10^18)"
    )
    parser.add_argument(
        "--count", type=int, required=True, help="Number of primes to output"
    )
    parser.add_argument("--csv", action="store_true", help="CSV output")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--stats", action="store_true", help="Show stats")

    args = parser.parse_args()
    gen = PythonPrimeGenerator(verbose=args.verbose, stats=args.stats)
    if args.csv:
        print("n,prime,is_mersenne,ms")
    gen.generate_primes(args.start, args.count, csv=args.csv)


if __name__ == "__main__":
    main()
