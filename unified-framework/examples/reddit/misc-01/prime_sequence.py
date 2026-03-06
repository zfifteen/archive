#!/usr/bin/env python3
"""
Prime Sequence Algorithm Implementation
=====================================

Implementation of the algorithm from misc_01.md to reproduce the sequence S
that maps to primes sequentially via f(s) = next_prime(s - 1).

Based on PLAN.md implementation plan.
"""

import math
import time
from typing import List, Set

def is_prime(n: int) -> bool:
    """Check if n is prime using trial division (optimized)"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Check divisibility up to sqrt(n)
    for i in range(5, int(math.sqrt(n)) + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False

    return True

def next_prime(n: int) -> int:
    """Return smallest prime >= n"""
    if n <= 2:
        return 2

    # Make n odd if even
    if n % 2 == 0:
        n += 1

    while not is_prime(n):
        n += 2

    return n

def f(s: int) -> int:
    """f(s) = next_prime(s - 1)"""
    return next_prime(s - 1)

def generate_primes_list(N: int) -> List[int]:
    """Generate first N primes"""
    if N < 1:
        return []

    primes = [2]  # First prime
    candidate = 3

    while len(primes) < N:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 2  # Skip even numbers

    return primes

def generate_S_corrected(N: int = 133) -> List[int]:
    """
    Generate sequence S where f(s_n) = n-th prime

    Corrected algorithm to handle the special case of s_2 = 2
    """
    if N < 1:
        return []

    # Precompute primes
    primes = generate_primes_list(N)

    S = [1]  # s_1 = 1, f(1) = next_prime(0) = 2 = p_1
    used_primes: Set[int] = set([2])  # Track used primes to avoid duplicates

    for n in range(1, N):
        target_prime = primes[n]
        s = S[-1]

        while True:
            s += 1
            candidate_prime = f(s)

            # Special case for n=1 (getting to p_2 = 3): allow s=2 even if f(2)=2 repeats
            if candidate_prime == target_prime and (candidate_prime not in used_primes or n == 1):
                S.append(s)
                if n != 1:  # Don't add to used for the special case
                    used_primes.add(candidate_prime)
                break

    return S

def validate_sequence(S: List[int], primes: List[int]) -> bool:
    """Validate that f(s_n) = p_n for all n"""
    if len(S) != len(primes):
        return False

    for i, (s, expected_prime) in enumerate(zip(S, primes)):
        actual_prime = f(s)
        if actual_prime != expected_prime:
            print(f"Validation failed at n={i+1}: s={s}, f(s)={actual_prime}, expected p_{i+1}={expected_prime}")
            return False

    return True

def compute_gaps(S: List[int]) -> List[int]:
    """Compute gaps g_k = s_{k+1} - s_k"""
    return [S[i+1] - S[i] for i in range(len(S) - 1)]

def z_analysis(gaps: List[int]) -> List[float]:
    """Compute Z values for gaps: Z_k = g_k × (Δg_k / max_gap)"""
    if not gaps:
        return []

    max_gap = max(gaps)
    Z_values = []

    for i in range(len(gaps)):
        g_k = gaps[i]
        if i < len(gaps) - 1:
            delta_g = gaps[i+1] - gaps[i]
        else:
            delta_g = 0  # Last element

        Z_k = g_k * (delta_g / max_gap) if max_gap != 0 else 0
        Z_values.append(Z_k)

    return Z_values

def main():
    """Main execution"""

    # Configuration
    N = 133  # Full sequence
    expected_S = [1, 2, 3, 5, 6, 8, 9, 11, 14, 15, 18, 20, 21, 23, 26, 29, 30, 33, 35, 36, 39, 41, 44, 48, 50, 51, 53, 54, 56, 63, 65, 68, 69, 74, 75, 78, 81, 83, 86, 89, 90, 95, 96, 98, 99, 105, 111, 113, 114, 116, 119, 120, 125, 128, 131, 134, 135, 138, 140, 141, 146, 153, 155, 156, 158, 165, 168, 173, 174, 176, 179, 183, 186, 189, 191, 194, 198, 200, 204, 209, 210, 215, 216, 219, 221, 224, 228, 230, 231, 233, 239, 243, 245, 249, 251, 254, 260, 261, 270, 273, 278, 281, 284, 285, 288, 293, 296, 299, 300, 303, 306, 308, 309, 315, 320, 321, 323, 326, 329, 330, 336, 338, 341, 345, 350, 354, 359, 363, 366, 369, 371, 375, 378, 380, 384, 386, 393, 398, 404, 405, 410, 411, 413, 414, 419, 426, 428, 429, 431, 438, 440, 441, 443, 453, 455, 459, 464, 468, 470, 473, 476, 483, 485, 488, 491, 495, 498]

    # Phase 1: Generate sequence
    print(f"Generating sequence for N={N}...")
    start_time = time.time()

    generated_S = generate_S_corrected(N)
    primes = generate_primes_list(N)

    generation_time = time.time() - start_time

    # Phase 2: Validation
    is_valid = validate_sequence(generated_S, primes)
    print(f"Sequence validation: {'PASS' if is_valid else 'FAIL'}")

    # Compare with expected
    if generated_S == expected_S:
    else:
        print(f"Generated length: {len(generated_S)}")
        print(f"Expected length: {len(expected_S)}")
        if len(generated_S) >= 10 and len(expected_S) >= 10:
            print(f"First 10 generated: {generated_S[:10]}")
            print(f"First 10 expected:  {expected_S[:10]}")

    # Phase 3: Analysis

    # Gaps and Z-analysis
    gaps = compute_gaps(generated_S)
    Z_values = z_analysis(gaps)

    print(f"Sequence length: {len(generated_S)}")
    print(f"Gaps range: {min(gaps)} - {max(gaps)}")
    print(f"Mean gap: {sum(gaps)/len(gaps):.2f}")
    print(f"Z values < 1: {sum(1 for z in Z_values if abs(z) < 1)}/{len(Z_values)} ({100*sum(1 for z in Z_values if abs(z) < 1)/len(Z_values):.1f}%)")

    # Sample Z values
    print(f"Sample Z values: {Z_values[:10]}...")

    # Phase 4: Function verification
    for i in range(min(10, len(generated_S))):
        s = generated_S[i]
        f_s = f(s)
        p_n = primes[i]
        status = "✅" if f_s == p_n else "❌"

if __name__ == "__main__":
    main()