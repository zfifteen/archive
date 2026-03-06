from abc import ABC, abstractmethod
import math

class ZetaShift(ABC):
    """
    Abstract base for ZetaShift, embodying Z = A(B/C) across domains.
    """
    def __init__(self, observed_quantity: float, rate: float):
        self.observed_quantity = observed_quantity
        self.rate = rate
        self.INVARIANT = 299792458.0  # C: speed of light in m/s

    @abstractmethod
    def compute_z(self) -> float:
        """Compute domain-specific Z."""
        pass

    @staticmethod
    def is_prime(num: int) -> bool:
        """Utility to check primality for flagging or adjustments."""
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0 or num % 3 == 0:
            return False
        i = 5
        while i * i <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False
            i += 6
        return True

class NumberLineZetaShift(ZetaShift):
    """
    ZetaShift for the number line: Z = n (v_earth / c), with v_earth fixed to CMB velocity.
    Optional prime gap adjustment amplifies Z for prime resonance.
    """
    EARTH_CMB_VELOCITY = 369820.0  # B: Earth's velocity wrt CMB in m/s

    def __init__(self, n: float, use_prime_gap_adjustment: bool = False):
        super().__init__(n, self.EARTH_CMB_VELOCITY)
        self.use_prime_gap_adjustment = use_prime_gap_adjustment

    def compute_z(self) -> float:
        base_z = self.observed_quantity * (self.rate / self.INVARIANT)  # Z = n (v_earth / c) ≈ n * 0.0012336
        if self.use_prime_gap_adjustment:
            gap = self._compute_prime_gap(int(self.observed_quantity))
            base_z *= (1 + gap / self.observed_quantity if self.observed_quantity != 0 else 1)  # Amplify with gap ratio
        return base_z

    def _compute_prime_gap(self, n: int) -> float:
        """Compute gap to next prime (0 if not prime)."""
        if not self.is_prime(n):
            return 0.0
        next_prime = n + 1
        while not self.is_prime(next_prime):
            next_prime += 1
        return next_prime - n

    def compute_z_across_range(self, start: int, end: int, resonance_threshold: float,
                               use_prime_gap_adjustment: bool = False) -> list[float]:
        """Apply Z across range, flagging primes where Z > threshold."""
        z_values = []
        flagged_primes = []
        for i in range(start, end + 1):
            shift = NumberLineZetaShift(i, use_prime_gap_adjustment)
            z = shift.compute_z()
            z_values.append(z)
            if z > resonance_threshold and self.is_prime(i):
                flagged_primes.append(i)
        print("Flagged primes via Z resonance:", flagged_primes)
        return z_values

# Demo: Navigate a small range
if __name__ == "__main__":
    navigator = NumberLineZetaShift(13)  # Example for prime 13
    print(f"Z for n=13 (no adjustment): {navigator.compute_z():.6f}")

    range_z = navigator.compute_z_across_range(1, 20, 0.01, use_prime_gap_adjustment=True)
    print("Z values for 1-20:", [f"{z:.6f}" for z in range_z])