
# CRITICAL FIX: The threshold WAS being applied in runSearchToCompletion but we're checking at loop level
# Let me rewrite to apply threshold INSIDE the loop properly

class DomainCellFixed:
    """Fixed version with proper threshold handling."""

    def __init__(self, semiprime: int, discovered_factor: Optional[int] = None, parent_id: Optional[str] = None):
        self.target_semiprime = semiprime
        self.target_bit_length = semiprime.bit_length()
        self.cell_id = id(self)
        self.creation_time = time.time()

        if discovered_factor is not None:
            self.target_semiprime = semiprime // discovered_factor
            self.current_role = CellRole.QUOTIENT_SOLVER
            self.complementary_factor_from_parent = discovered_factor
            self.parent_id = parent_id
            self.stagnation_threshold = 2000
        else:
            self.current_role = CellRole.FACTOR_HUNTER
            self.complementary_factor_from_parent = None
            self.parent_id = None
            # CRITICAL: Set initial threshold based on bit length
            if self.target_bit_length > 300:
                self.stagnation_threshold = 500000
            elif self.target_bit_length > 200:
                self.stagnation_threshold = 200000
            elif self.target_bit_length > 100:
                self.stagnation_threshold = 50000
            else:
                self.stagnation_threshold = 5000

        self.slow_walker_position = 0
        self.fast_walker_position = 0
        self.polynomial_offset = 0
        self.iteration_count = 0
        self.walker_separation = 0
        self.last_separation_change_iteration = 0

        self.current_candidate_factor = 1
        self.iteration_of_last_factor_discovery = 0
        self.is_factor_verified = False
        self.is_factor_prime = False

        self.iterations_since_last_progress = 0
        self.restart_attempt_count = 0
        self.cell_status = CellStatus.SEARCHING

        self.initialize_walk_state()

    def initialize_walk_state(self):
        if self.target_semiprime <= 1:
            return
        self.slow_walker_position = random.randint(1, self.target_semiprime - 1)
        self.fast_walker_position = self.slow_walker_position
        self.polynomial_offset = random.randint(1, self.target_semiprime - 1)
        self.iteration_count = 0
        self.walker_separation = 0
        self.last_separation_change_iteration = 0

    def is_prime(self, n: int, k: int = 20) -> bool:
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
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
        return (position * position + self.polynomial_offset) % self.target_semiprime

    def verify_and_probe_factor(self):
        remainder = self.target_semiprime % self.current_candidate_factor
        self.is_factor_verified = (remainder == 0)
        if self.is_factor_verified:
            self.is_factor_prime = self.is_prime(self.current_candidate_factor)

    def detect_stagnation(self):
        # NO AUTOMATIC FREEZING - stagnation just marks status, doesn't halt
        if self.iterations_since_last_progress > self.stagnation_threshold:
            self.cell_status = CellStatus.STAGNANT

    def trigger_restart_eligibility(self):
        self.restart_attempt_count += 1
        if self.restart_attempt_count <= 5:  # Allow more restarts
            self.initialize_walk_state()
            self.cell_status = CellStatus.SEARCHING
        else:
            self.cell_status = CellStatus.FROZEN

    def advance_pollard_rho_by_one_step(self):
        if self.cell_status == CellStatus.FROZEN:
            return False  # Return whether we made progress

        if self.target_semiprime <= 1:
            self.cell_status = CellStatus.FROZEN
            return False

        if self.is_prime(self.target_semiprime):
            self.current_candidate_factor = self.target_semiprime
            self.is_factor_verified = True
            self.is_factor_prime = True
            self.current_role = CellRole.TERMINAL_PRIME
            self.cell_status = CellStatus.FROZEN
            return True

        self.slow_walker_position = self.evaluate_polynomial_step(self.slow_walker_position)
        self.fast_walker_position = self.evaluate_polynomial_step(self.fast_walker_position)
        self.fast_walker_position = self.evaluate_polynomial_step(self.fast_walker_position)

        new_separation = abs(self.slow_walker_position - self.fast_walker_position)

        if new_separation != self.walker_separation:
            self.last_separation_change_iteration = self.iteration_count
            self.walker_separation = new_separation

        gcd = math.gcd(self.walker_separation, self.target_semiprime)

        if 1 < gcd < self.target_semiprime:
            if gcd != self.current_candidate_factor:
                self.current_candidate_factor = gcd
                self.iteration_of_last_factor_discovery = self.iteration_count
                self.iterations_since_last_progress = 0
                self.verify_and_probe_factor()
                return True  # Found a factor!

        self.iteration_count += 1
        self.iterations_since_last_progress += 1

        self.detect_stagnation()

        if gcd == self.target_semiprime:
            self.trigger_restart_eligibility()

        return False

    def run_search_to_completion(self, max_total_iterations: int = 1000000) -> int:
        """Runs until factor found or max iterations exceeded."""
        total_iterations = 0

        while self.cell_status != CellStatus.FROZEN and total_iterations < max_total_iterations:
            self.advance_pollard_rho_by_one_step()
            total_iterations += 1

        if self.is_factor_verified and self.current_candidate_factor > 1:
            return self.current_candidate_factor
        return self.target_semiprime

    def get_statistics(self) -> PollardRhoStatistics:
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

print("=" * 120)
print("POLLARD RHO FACTORIZATION - FIXED VERSION WITH AGGRESSIVE THRESHOLDS")
print("=" * 120)
print()

# Test 1: Small semiprimes (sanity check)
print("TEST 1: Small Semiprimes (Sanity Check)")
print("-" * 120)

test_cases_small = [
    (143, "11 × 13"),
    (187, "11 × 17"),
    (10007 * 10009, "10007 × 10009"),
]

for n, factorization in test_cases_small:
    cell = DomainCellFixed(n)
    start = time.time()
    result = cell.run_search_to_completion()
    elapsed = time.time() - start
    stats = cell.get_statistics()
    quotient = n // result if result != n else "FAILED"
    print(f"N = {n:>15} ({factorization:>30}) | Factor: {result:>15} | "
          f"Iterations: {stats.iteration_count:>10,} | Restarts: {stats.restart_attempt_count} | Time: {elapsed:.4f}s")

print()

# Test 2: RSA-100 with progress reporting
print("TEST 2: RSA-100 Challenge Number (330-bit semiprime)")
print("-" * 120)

rsa_100 = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139

cell = DomainCellFixed(rsa_100)
print(f"Target bit-length: {cell.target_bit_length}")
print(f"Stagnation threshold: {cell.stagnation_threshold:,}")
print()

start = time.time()
iteration_checkpoint = 0

while cell.cell_status != CellStatus.FROZEN:
    cell.advance_pollard_rho_by_one_step()
    iteration_checkpoint += 1
    
    if iteration_checkpoint % 50000 == 0:
        elapsed = time.time() - start
        stats = cell.get_statistics()
        print(f"  Checkpoint: {stats.iteration_count:>10,} iterations | "
              f"Separation: {stats.walker_separation:>20,} | "
              f"Candidate: {stats.current_candidate_factor if stats.current_candidate_factor > 1 else 'none':>20} | "
              f"Restarts: {stats.restart_attempt_count} | Time: {elapsed:>8.2f}s")
    
    if iteration_checkpoint > 1000000:
        print(f"  >> Exceeded max iterations, stopping")
        break

elapsed = time.time() - start
stats = cell.get_statistics()

print()
print("FINAL RESULT:")
print(f"  Status: {cell.cell_status.value}")
print(f"  Total iterations: {stats.iteration_count:,}")
print(f"  Total time: {elapsed:.4f}s")
print(f"  Iterations/second: {stats.iteration_count / elapsed:,.0f}")
print(f"  Found factor: {stats.current_candidate_factor}")
print(f"  Factor verified: {stats.is_factor_verified}")
print(f"  Factor is prime: {stats.is_factor_prime}")
print(f"  Restart attempts: {stats.restart_attempt_count}")
print(f"  Final walker separation: {stats.walker_separation:,}")
print()

if stats.is_factor_verified:
    quotient = rsa_100 // stats.current_candidate_factor
    print(f"✓ FACTORIZATION SUCCESS:")
    print(f"  {stats.current_candidate_factor}")
    print(f"  ×")
    print(f"  {quotient}")
else:
    print(f"✗ FACTORIZATION FAILED - Hit max iterations")

print()
print("=" * 120)
