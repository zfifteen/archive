import math
from typing import Iterator

class SegmentedSkipTracker:
    """
    Segmented Skip Tracker Prime Generator.

    Splits [2..limit] into chunks of size `segment_size`, marks composites by:
      1. Even numbers ≥ 4
      2. Perfect squares ≥ 4
      3. Products i*j (i<j), optimized to only mark odd composites
    Yields primes one by one.
    """
    def __init__(self, limit: int, segment_size: int = 1_000_000):
        self.limit = limit
        self.segment_size = segment_size

    def find_primes(self) -> Iterator[int]:
        if self.limit < 2:
            return

        sqrt_limit = int(math.isqrt(self.limit))

        prime_count = 0

        # Iterate over segments [low, high]
        for low in range(2, self.limit + 1, self.segment_size):
            high = min(self.limit, low + self.segment_size - 1)
            size = high - low + 1

            # False = unclaimed (potential prime), True = composite
            segment = bytearray(size)

            # 1. Mark evens in this segment, skipping 2
            start_even = low if (low & 1) == 0 else low + 1
            if start_even == 2:
                start_even = 4
            for n in range(start_even, high + 1, 2):
                segment[n - low] = 1

            # 2. Mark perfect squares in this segment
            k = int(math.isqrt(low))
            if k * k < low:
                k += 1
            while k * k <= high:
                segment[k*k - low] = 1
                k += 1

            # 3. Mark odd composites via products i*j, skipping even factors
            for i in range(3, sqrt_limit + 1, 2):
                # Compute first j so that i*j >= low, j > i
                j_start = max(i + 1, (low + i - 1) // i)
                # Ensure j_start is odd (skip even j → marks already-covered evens)
                if (j_start & 1) == 0:
                    j_start += 1
                pos = i * j_start
                step = 2 * i  # jump j by 2 each time → pos += 2i

                # Advance pos to the first multiple ≥ low
                for m in range(pos, high + 1, step):
                    segment[m - low] = 1

            # Emit unclaimed numbers as primes
            for offset, is_composite in enumerate(segment):
                if not is_composite:
                    prime = low + offset
                    yield prime
                    prime_count += 1
                    if prime_count % 1000 == 0:
                        print(f"Prime {prime_count} found, value: {prime}")


# Example usage
if __name__ == "__main__":
    LIMIT = 5_000_000_000      # e.g., five billion
    SEGMENT = 5_000_000        # five-million-wide chunks

    counter = 0
    for prime in SegmentedSkipTracker(LIMIT, SEGMENT).find_primes():
        counter += 1
        # e.g., print(prime)  # comment out to avoid flooding stdout
    print(f"Total primes up to {LIMIT:,}: {counter:,}")