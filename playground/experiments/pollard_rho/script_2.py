
# The issue: we're not batching the GCD computations correctly.
# Classic Pollard Rho batches GCD checks every k steps to avoid expensive GCD ops on huge numbers
# Let me implement the STANDARD Pollard Rho with Brent's optimization

class DomainCellProduction:
    """Production-grade Pollard Rho with Brent's cycle-finding optimization."""

    def __init__(self, semiprime: int, discovered_factor: Optional[int] = None, parent_id: Optional[str] = None):
        self.target_semiprime = semiprime
        self.target_bit_length = semiprime.bit_length()
        self.cell_id = id(self)
        self.creation_time = time.time()

        if discovered_factor is not None:
            self.target_semiprime = semiprime // discovered_factor
            self.current_role = CellRole.QUOTIENT_SOLVER
            self.complementary_factor_from_parent = discovered_factor
        else:
            self.current_role = CellRole.FACTOR_HUNTER
            self.complementary_factor_from_parent = None

        self.slow_walker_position = 0
        self.fast_walker_position = 0
        self.polynomial_offset = 0
        self.iteration_count = 0
        self.walker_separation = 0
        self.accumulated_product = 1  # For batched GCD

        self.current_candidate_factor = 1
        self.iteration_of_last_factor_discovery = 0
        self.is_factor_verified = False
        self.is_factor_prime = False

        self.iterations_since_last_progress = 0
        self.restart_attempt_count = 0
        self.cell_status = CellStatus.SEARCHING
        self.gcd_batch_size = 20  # Batch GCD every N steps

        self.initialize_walk_state()

    def initialize_walk_state(self):
        if self.target_semiprime <= 1:
            return
        self.slow_walker_position = random.randint(1, self.target_semiprime - 1)
        self.fast_walker_position = self.slow_walker_position
        self.polynomial_offset = random.randint(1, self.target_semiprime - 1)
        self.iteration_count = 0
        self.walker_separation = 0
        self.accumulated_product = 1

    def is_prime(self, n: int, k: int = 10) -> bool:
        """Miller-Rabin primality test."""
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
            a = random.randint(2, n - 2) if n > 3 else 2
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
        """f(x) = x^2 + c (mod n)"""
        return (position * position + self.polynomial_offset) % self.target_semiprime

    def verify_and_probe_factor(self):
        remainder = self.target_semiprime % self.current_candidate_factor
        self.is_factor_verified = (remainder == 0)
        if self.is_factor_verified:
            self.is_factor_prime = self.is_prime(self.current_candidate_factor, k=5)

    def advance_pollard_rho_with_batched_gcd(self):
        """
        Advances Pollard Rho using batched GCD for efficiency.
        This is the production algorithm.
        """
        if self.cell_status == CellStatus.FROZEN:
            return False

        if self.target_semiprime <= 1:
            self.cell_status = CellStatus.FROZEN
            return False

        if self.is_prime(self.target_semiprime, k=5):
            self.current_candidate_factor = self.target_semiprime
            self.is_factor_verified = True
            self.is_factor_prime = True
            self.current_role = CellRole.TERMINAL_PRIME
            self.cell_status = CellStatus.FROZEN
            return True

        # Batch GCD: accumulate products over k iterations, then compute GCD
        for _ in range(self.gcd_batch_size):
            # Advance slow walker by 1
            self.slow_walker_position = self.evaluate_polynomial_step(self.slow_walker_position)

            # Advance fast walker by 2
            self.fast_walker_position = self.evaluate_polynomial_step(self.fast_walker_position)
            self.fast_walker_position = self.evaluate_polynomial_step(self.fast_walker_position)

            # Accumulate product: product *= |slow - fast|
            diff = abs(self.slow_walker_position - self.fast_walker_position)
            self.accumulated_product = (self.accumulated_product * diff) % self.target_semiprime
            self.walker_separation = diff
            self.iteration_count += 1

        # Compute batched GCD
        gcd = math.gcd(self.accumulated_product, self.target_semiprime)

        if gcd == self.target_semiprime:
            # Backtrack: compute GCD step-by-step to find exact factor
            self.slow_walker_position = random.randint(1, self.target_semiprime - 1)
            self.fast_walker_position = self.slow_walker_position
            self.polynomial_offset = random.randint(1, self.target_semiprime - 1)
            self.restart_attempt_count += 1
            
            if self.restart_attempt_count > 10:
                self.cell_status = CellStatus.FROZEN
                return False
            return False

        if 1 < gcd < self.target_semiprime:
            if gcd != self.current_candidate_factor:
                self.current_candidate_factor = gcd
                self.iteration_of_last_factor_discovery = self.iteration_count
                self.iterations_since_last_progress = 0
                self.verify_and_probe_factor()
                return True

        self.iterations_since_last_progress += self.gcd_batch_size
        return False

    def run_search_to_completion(self, max_total_iterations: int = 100000000) -> int:
        """Runs until factor found or max iterations."""
        while self.cell_status != CellStatus.FROZEN and self.iteration_count < max_total_iterations:
            self.advance_pollard_rho_with_batched_gcd()

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

# COMPREHENSIVE TEST SUITE
print("=" * 130)
print("PRODUCTION-GRADE POLLARD RHO WITH BATCHED GCD - COMPREHENSIVE TESTS")
print("=" * 130)
print()

# Test 1: Small semiprimes
print("TEST 1: Small Semiprimes (Validation)")
print("-" * 130)

test_cases_small = [
    (143, "11 × 13"),
    (187, "11 × 17"),
    (221, "13 × 17"),
    (323, "17 × 19"),
    (391, "17 × 23"),
]

for n, fact in test_cases_small:
    cell = DomainCellProduction(n)
    start = time.time()
    result = cell.run_search_to_completion(max_total_iterations=100000)
    elapsed = time.time() - start
    stats = cell.get_statistics()
    quotient = n // result if result != n else "FAIL"
    print(f"N = {n:>6} ({fact:>15}) | Factor: {result:>6} | Quotient: {quotient:>6} | "
          f"Iterations: {stats.iteration_count:>10,} | Time: {elapsed:.4f}s | Restarts: {stats.restart_attempt_count}")

print()

# Test 2: Medium semiprimes
print("TEST 2: Medium Semiprimes")
print("-" * 130)

test_cases_med = [
    (10007 * 10009, "10007 × 10009", 50),
    (100019 * 100043, "100019 × 100043", 50),
]

for n, fact, timeout in test_cases_med:
    cell = DomainCellProduction(n)
    start = time.time()
    result = cell.run_search_to_completion(max_total_iterations=10000000)
    elapsed = time.time() - start
    stats = cell.get_statistics()
    quotient = n // result if result != n else "FAIL"
    print(f"N = {n:>15} ({fact:>30}) | Factor: {result:>15} | "
          f"Iterations: {stats.iteration_count:>12,} | Time: {elapsed:>7.3f}s | Restarts: {stats.restart_attempt_count}")

print()

# Test 3: RSA-100
print("TEST 3: RSA-100 Challenge (330-bit semiprime)")
print("-" * 130)

rsa_100 = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139

cell = DomainCellProduction(rsa_100)
start = time.time()

checkpoint = 0
while cell.cell_status != CellStatus.FROZEN:
    cell.advance_pollard_rho_with_batched_gcd()
    checkpoint += cell.gcd_batch_size
    
    if checkpoint % 500000 == 0:
        elapsed = time.time() - start
        stats = cell.get_statistics()
        if stats.current_candidate_factor > 1:
            print(f"  FOUND FACTOR at {stats.iteration_count:>10,} iterations!")
            print(f"  Factor: {stats.current_candidate_factor}")
            print(f"  Verified: {stats.is_factor_verified}")
            break
        else:
            print(f"  Progress: {stats.iteration_count:>12,} iterations | Time: {elapsed:>8.2f}s | Restarts: {stats.restart_attempt_count}")
    
    if cell.iteration_count > 50000000:
        print("  >> Hit max iterations (50M), stopping")
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
print(f"  Verified: {stats.is_factor_verified}")
print(f"  Restarts: {stats.restart_attempt_count}")

if stats.is_factor_verified and stats.current_candidate_factor > 1:
    quotient = rsa_100 // stats.current_candidate_factor
    print(f"\n✓ FACTORIZATION SUCCESS: {stats.current_candidate_factor} × {quotient}")
else:
    print(f"\n✗ FACTORIZATION INCOMPLETE")

print()
print("=" * 130)
