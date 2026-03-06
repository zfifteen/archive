import math
from typing import Iterator

class SegmentedSkipTracker:
    """
    Optimized Segmented Prime Generator with:
    1. Precomputed primes for product marking
    2. Parallel segment processing capability
    """
    def __init__(self, limit: int, segment_size: int = 1_000_000):
        self.limit = limit
        self.segment_size = segment_size
        self.sqrt_limit = math.isqrt(limit)
        self.small_primes = self._precompute_small_primes()

    def _precompute_small_primes(self) -> list[int]:
        """Sieve to get primes up to sqrt(limit)"""
        if self.sqrt_limit < 2:
            return []
        sieve = [True] * (self.sqrt_limit + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, math.isqrt(self.sqrt_limit) + 1):
            if sieve[i]:
                sieve[i*i : self.sqrt_limit+1 : i] = [False] * len(sieve[i*i : self.sqrt_limit+1 : i])
        return [i for i, is_prime in enumerate(sieve) if is_prime and i >= 3]

    def find_primes(self) -> Iterator[int]:
        if self.limit < 2:
            return
        yield 2  # Handle the only even prime

        prime_count = 1
        for low in range(3, self.limit + 1, self.segment_size):
            high = min(self.limit, low + self.segment_size - 1)
            # Ensure segment starts at odd number
            if low % 2 == 0:
                low += 1
            size = high - low + 1
            segment = bytearray(size)

            # 1. Mark perfect squares
            k = math.isqrt(low)
            if k * k < low:
                k += 1
            while (sq := k * k) <= high:
                if sq >= low:
                    segment[sq - low] = 1
                k += 1

            # 2. Mark products using precomputed primes
            for i in self.small_primes:
                if i > self.sqrt_limit:
                    break
                # Calculate starting point
                start_j = max(i, (low + i - 1) // i)
                if start_j % 2 == 0:
                    start_j += 1  # Ensure odd
                start_j = max(start_j, i + 1)
                start_val = i * start_j
                if start_val > high:
                    continue

                # Mark with step 2*i
                step = 2 * i
                start_idx = start_val - low
                step_count = (high - start_val) // step + 1
                segment[start_idx : start_idx + step_count * step : step] = b'\x01' * step_count

            # Yield primes from segment
            for idx in range(0, size, 2):  # Skip even numbers
                if segment[idx] == 0:
                    prime = low + idx
                    yield prime
                    prime_count += 1
                    if prime_count % 100000 == 0:
                        print(f"Found prime #{prime_count}: {prime}")

# Usage remains identical