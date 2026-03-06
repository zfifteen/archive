
import math
import random
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum
import time

class CellRole(Enum):
    """Specialized roles a cell can play in factorization."""
    FACTOR_HUNTER = "FACTOR_HUNTER"
    FACTOR_VERIFIER = "FACTOR_VERIFIER"
    QUOTIENT_SOLVER = "QUOTIENT_SOLVER"
    RESTART_DELEGATE = "RESTART_DELEGATE"
    ACCELERATION_SPECIALIST = "ACCELERATION_SPECIALIST"
    CHECKPOINT_HOLDER = "CHECKPOINT_HOLDER"
    TERMINAL_PRIME = "TERMINAL_PRIME"

class CellStatus(Enum):
    """Status of a cell's search."""
    SEARCHING = "SEARCHING"
    STAGNANT = "STAGNANT"
    FROZEN = "FROZEN"
    DORMANT = "DORMANT"

@dataclass
class PollardRhoStatistics:
    """Rich statistics about a cell's Pollard Rho walk."""
    iteration_count: int = 0
    iterations_since_progress: int = 0
    walker_separation: int = 0
    current_candidate_factor: int = 1
    is_factor_verified: bool = False
    is_factor_prime: bool = False
    polynomial_offset: int = 0
    slow_walker_position: int = 0
    fast_walker_position: int = 0
    restart_attempt_count: int = 0
    last_factor_discovery_iteration: int = 0

    def __str__(self):
        return (
            f"Iterations: {self.iteration_count:,} | "
            f"Since Progress: {self.iterations_since_progress:,} | "
            f"Walker Sep: {self.walker_separation:,} | "
            f"Candidate: {self.current_candidate_factor} | "
            f"Verified: {self.is_factor_verified} | "
            f"Restart Attempts: {self.restart_attempt_count}"
        )

class DomainCell:
    """
    A computational agent that factors semiprimes via Pollard Rho.
    Exposes fine-grained state for work division and emergent clustering.
    """

    def __init__(self, semiprime: int, discovered_factor: Optional[int] = None, parent_id: Optional[str] = None):
        self.target_semiprime = semiprime
        self.target_bit_length = semiprime.bit_length()
        self.cell_id = id(self)  # Unique ID for this cell
        self.creation_time = time.time()

        # Determine target based on role
        if discovered_factor is not None:
            # Quotient solver: reduce the problem
            self.target_semiprime = semiprime // discovered_factor
            self.current_role = CellRole.QUOTIENT_SOLVER
            self.complementary_factor_from_parent = discovered_factor
            self.parent_id = parent_id
            self.stagnation_threshold = 2000
        else:
            # Factor hunter: solve the full problem
            self.current_role = CellRole.FACTOR_HUNTER
            self.complementary_factor_from_parent = None
            self.parent_id = None
            self.stagnation_threshold = 5000

        # Initialize walk state
        self.slow_walker_position = 0
        self.fast_walker_position = 0
        self.polynomial_offset = 0
        self.iteration_count = 0
        self.walker_separation = 0
        self.last_separation_change_iteration = 0

        # Initialize factor state
        self.current_candidate_factor = 1
        self.iteration_of_last_factor_discovery = 0
        self.is_factor_verified = False
        self.is_factor_prime = False

        # Health signals
        self.iterations_since_last_progress = 0
        self.restart_attempt_count = 0
        self.cell_status = CellStatus.SEARCHING

        self.initialize_walk_state()

    def initialize_walk_state(self):
        """Initialize Pollard Rho walk with fresh random parameters."""
        if self.target_semiprime <= 1:
            return

        # Random initial position
        self.slow_walker_position = random.randint(1, self.target_semiprime - 1)
        self.fast_walker_position = self.slow_walker_position

        # Random polynomial offset
        self.polynomial_offset = random.randint(1, self.target_semiprime - 1)

        self.iteration_count = 0
        self.walker_separation = 0
        self.last_separation_change_iteration = 0

    def is_prime(self, n: int, k: int = 20) -> bool:
        """Miller-Rabin primality test."""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False

        # Write n-1 as 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        # Witness loop
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)

            if x == 1 or x == n - 1:
                continue

            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False

        return True

    def evaluate_polynomial_step(self, position: int) -> int:
        """Applies f(x) = x^2 + c (mod n)."""
        return (position * position + self.polynomial_offset) % self.target_semiprime

    def verify_and_probe_factor(self):
        """Verifies candidate factor and probes its properties."""
        remainder = self.target_semiprime % self.current_candidate_factor
        self.is_factor_verified = (remainder == 0)

        if self.is_factor_verified:
            self.is_factor_prime = self.is_prime(self.current_candidate_factor)

    def detect_stagnation(self):
        """Detects if walk is stalled."""
        if self.iterations_since_last_progress > self.stagnation_threshold:
            self.cell_status = CellStatus.STAGNANT

    def trigger_restart_eligibility(self):
        """Handles restart when cycle is fully exhausted."""
        self.restart_attempt_count += 1
        if self.restart_attempt_count <= 3:
            self.initialize_walk_state()
            self.cell_status = CellStatus.SEARCHING
        else:
            self.cell_status = CellStatus.FROZEN

    def advance_pollard_rho_by_one_step(self):
        """Advances walk by one iteration, updating exposed state."""
        if self.cell_status in [CellStatus.FROZEN, CellStatus.DORMANT]:
            return

        if self.target_semiprime <= 1:
            self.cell_status = CellStatus.FROZEN
            return

        # Early termination: target is prime
        if self.is_prime(self.target_semiprime):
            self.current_candidate_factor = self.target_semiprime
            self.is_factor_verified = True
            self.is_factor_prime = True
            self.current_role = CellRole.TERMINAL_PRIME
            self.cell_status = CellStatus.FROZEN
            return

        # Advance slow walker by 1 step
        self.slow_walker_position = self.evaluate_polynomial_step(self.slow_walker_position)

        # Advance fast walker by 2 steps
        self.fast_walker_position = self.evaluate_polynomial_step(self.fast_walker_position)
        self.fast_walker_position = self.evaluate_polynomial_step(self.fast_walker_position)

        # Compute separation
        new_separation = abs(self.slow_walker_position - self.fast_walker_position)

        if new_separation != self.walker_separation:
            self.last_separation_change_iteration = self.iteration_count
            self.walker_separation = new_separation

        # Compute GCD
        gcd = math.gcd(self.walker_separation, self.target_semiprime)

        # Record factor if non-trivial
        if 1 < gcd < self.target_semiprime:
            if gcd != self.current_candidate_factor:
                self.current_candidate_factor = gcd
                self.iteration_of_last_factor_discovery = self.iteration_count
                self.iterations_since_last_progress = 0
                self.verify_and_probe_factor()

        # Increment counters
        self.iteration_count += 1
        self.iterations_since_last_progress += 1

        self.detect_stagnation()

        # Detect if walk cycled completely
        if gcd == self.target_semiprime:
            self.cell_status = CellStatus.STAGNANT
            self.trigger_restart_eligibility()

    def run_search_to_completion(self) -> int:
        """Runs search until factor found or stagnant."""
        # Adaptive threshold for large numbers
        original_threshold = self.stagnation_threshold
        if self.target_bit_length > 100:
            self.stagnation_threshold = 50000
        if self.target_bit_length > 200:
            self.stagnation_threshold = 100000
        if self.target_bit_length > 300:
            self.stagnation_threshold = 200000

        while self.cell_status == CellStatus.SEARCHING:
            self.advance_pollard_rho_by_one_step()

        self.stagnation_threshold = original_threshold

        if self.is_factor_verified and self.current_candidate_factor > 1:
            return self.current_candidate_factor

        return self.target_semiprime

    def get_statistics(self) -> PollardRhoStatistics:
        """Returns rich statistics about current state."""
        return PollardRhoStatistics(
            iteration_count=self.iteration_count,
            iterations_since_progress=self.iterations_since_last_progress,
            walker_separation=self.walker_separation,
            current_candidate_factor=self.current_candidate_factor,
            is_factor_verified=self.is_factor_verified,
            is_factor_prime=self.is_factor_prime,
            polynomial_offset=self.polynomial_offset,
            slow_walker_position=self.slow_walker_position,
            fast_walker_position=self.fast_walker_position,
            restart_attempt_count=self.restart_attempt_count,
            last_factor_discovery_iteration=self.iteration_of_last_factor_discovery
        )

# Test suite
print("=" * 100)
print("POLLARD RHO FACTORIZATION - COMPREHENSIVE TESTS")
print("=" * 100)
print()

# Test 1: Small semiprimes
print("TEST 1: Small Semiprimes (Quick Convergence)")
print("-" * 100)

test_cases_small = [
    (143, "11 × 13"),
    (187, "11 × 17"),
    (221, "13 × 17"),
    (323, "17 × 19"),
    (391, "17 × 23"),
]

for n, factorization in test_cases_small:
    cell = DomainCell(n)
    start = time.time()
    result = cell.run_search_to_completion()
    elapsed = time.time() - start

    stats = cell.get_statistics()
    print(f"N = {n:>6} ({factorization:>15}) | Result: {result:>6} | "
          f"Iterations: {stats.iteration_count:>8,} | Time: {elapsed:.4f}s")

print()

# Test 2: Medium semiprimes
print("TEST 2: Medium Semiprimes (Moderate Difficulty)")
print("-" * 100)

test_cases_medium = [
    (1927, "41 × 47"),
    (3233, "53 × 61"),
    (6557, "79 × 83"),
    (9973, "97 × 103"),
]

for n, factorization in test_cases_medium:
    cell = DomainCell(n)
    start = time.time()
    result = cell.run_search_to_completion()
    elapsed = time.time() - start

    stats = cell.get_statistics()
    quotient = n // result if result != n else "N/A"
    print(f"N = {n:>6} ({factorization:>15}) | Factor: {result:>6} | Quotient: {quotient:>6} | "
          f"Iterations: {stats.iteration_count:>8,} | Time: {elapsed:.4f}s")

print()

# Test 3: Larger semiprimes (500-1000 bits worth of factorization difficulty)
print("TEST 3: Large Semiprimes (100-200 bit range)")
print("-" * 100)

test_cases_large = [
    (10007 * 10009, "10007 × 10009"),
    (100019 * 100043, "100019 × 100043"),
]

for n, factorization in test_cases_large:
    cell = DomainCell(n)
    start = time.time()
    result = cell.run_search_to_completion()
    elapsed = time.time() - start

    stats = cell.get_statistics()
    quotient = n // result if result != n else "N/A"
    print(f"N = {n:>15} ({factorization:>30}) | Factor: {result:>15} | "
          f"Iterations: {stats.iteration_count:>10,} | Time: {elapsed:.4f}s")

print()

# Test 4: RSA Challenge Numbers (real tests)
print("TEST 4: RSA Challenge Numbers (330-bit, the actual test case)")
print("-" * 100)

rsa_100 = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
# RSA-100 = 3932380965235924914333389668342420684974786564569494856176035326322058077805659331026192708460314150258592864177116725943603718461857357598351152301588859...
# Factorization: 39685999459223046528074264268928497375778309043164899778044697208566919478829464690427784822052594148545260346543612726403772662651878727272331425373475303227479636280769

cell = DomainCell(rsa_100)
start = time.time()

# Run with progress reporting
while cell.cell_status == CellStatus.SEARCHING:
    cell.advance_pollard_rho_by_one_step()
    
    if cell.iteration_count % 10000 == 0:
        stats = cell.get_statistics()
        elapsed = time.time() - start
        print(f"  Progress: {stats.iteration_count:>10,} iterations | "
              f"Separation: {stats.walker_separation:>15,} | "
              f"Time elapsed: {elapsed:>8.2f}s | "
              f"Status: {cell.cell_status.value}")

elapsed = time.time() - start

stats = cell.get_statistics()
quotient = rsa_100 // cell.current_candidate_factor if cell.current_candidate_factor != rsa_100 else "N/A"

print()
print(f"RESULT:")
print(f"  N = {rsa_100}")
print(f"  Found factor: {cell.current_candidate_factor}")
print(f"  Quotient: {quotient if quotient != 'N/A' else 'FAILED'}")
print(f"  Total time: {elapsed:.4f}s")
print(f"  Iterations: {stats.iteration_count:,}")
print(f"  Verified: {stats.is_factor_verified}")
print(f"  Restart attempts: {stats.restart_attempt_count}")
print(f"  Role: {cell.current_role.value}")
print(f"  Status: {cell.cell_status.value}")

print()
print("=" * 100)
