#!/usr/bin/env python3
"""
Candidate Filter Cascade for Semiprime Factorization

This module implements a cascade of mathematical filters that reject impossible
factor candidates before expensive operations (primality testing, trial division).

The filters exploit mathematical properties that true factors MUST satisfy:
1. Terminal Digit Compatibility - last digit multiplication rules
2. Digital Root Compatibility - mod-9 multiplication rules
3. Small Factor Exclusion - GCD structure inheritance
4. Primality Verification - factors must be prime
5. Quadratic Residue Test - Legendre symbol divisibility

CRITICAL PROPERTY: True factors NEVER fail these filters. They only reject
candidates that are mathematically impossible as factors.

Filter ordering is by computational cost (cheapest first) to maximize
rejection before expensive operations.

Reference: docs/Z5D_Candidate_Filter_System.md
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import gmpy2


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class FilterStats:
    """Statistics tracking for filter cascade performance."""
    total_candidates: int = 0
    rejected_terminal_digit: int = 0
    rejected_digital_root: int = 0
    rejected_small_factor: int = 0
    rejected_primality: int = 0
    rejected_quadratic_residue: int = 0
    accepted: int = 0

    def rejection_rate(self, filter_name: str) -> float:
        """
        IMPLEMENTED: Calculate rejection rate for a specific filter.
        """
        # STEP[4]: Handle edge case where total_candidates is 0
        if self.total_candidates == 0:
            return 0.0

        # STEP[1] & [2]: Get rejection count for specified filter
        filter_counts = {
            'terminal_digit': self.rejected_terminal_digit,
            'digital_root': self.rejected_digital_root,
            'small_factor': self.rejected_small_factor,
            'primality': self.rejected_primality,
            'quadratic_residue': self.rejected_quadratic_residue,
        }

        if filter_name not in filter_counts:
            raise ValueError(f"Unknown filter: {filter_name}. Valid: {list(filter_counts.keys())}")

        rejections = filter_counts[filter_name]

        # STEP[3]: Calculate percentage
        return (rejections / self.total_candidates) * 100

    def summary(self) -> Dict[str, Any]:
        """
        IMPLEMENTED: Return summary dictionary of all statistics.
        """
        # STEP[1]: Calculate overall acceptance rate
        if self.total_candidates == 0:
            acceptance_rate = 0.0
        else:
            acceptance_rate = (self.accepted / self.total_candidates) * 100

        # STEP[2]: Calculate rejection rate for each filter stage
        filter_names = ['terminal_digit', 'digital_root', 'small_factor',
                        'primality', 'quadratic_residue']
        per_filter_rates = {name: self.rejection_rate(name) for name in filter_names}

        # STEP[3]: Calculate cumulative rejection
        total_rejected = (self.rejected_terminal_digit + self.rejected_digital_root +
                          self.rejected_small_factor + self.rejected_primality +
                          self.rejected_quadratic_residue)
        if self.total_candidates == 0:
            cumulative_rejection_rate = 0.0
        else:
            cumulative_rejection_rate = (total_rejected / self.total_candidates) * 100

        # STEP[4]: Package all metrics into a dictionary
        return {
            'total_candidates': self.total_candidates,
            'accepted': self.accepted,
            'acceptance_rate': acceptance_rate,
            'per_filter_rejections': {
                'terminal_digit': self.rejected_terminal_digit,
                'digital_root': self.rejected_digital_root,
                'small_factor': self.rejected_small_factor,
                'primality': self.rejected_primality,
                'quadratic_residue': self.rejected_quadratic_residue,
            },
            'per_filter_rates': per_filter_rates,
            'cumulative_rejection_rate': cumulative_rejection_rate,
        }


@dataclass
class FilterConfig:
    """Configuration for the filter cascade."""
    # Set of valid terminal digits for factor candidates (derived from N's terminal digit)
    valid_terminal_digits: Set[int] = field(default_factory=set)

    # Set of valid digital roots for factor candidates (derived from N's digital root)
    valid_digital_roots: Set[int] = field(default_factory=set)

    # Product of small primes for GCD check: 2 * 3 * 5 * 7 * 11 * 13 * 17 * 19 * 23
    small_primes_product: int = 223092870

    # Number of Miller-Rabin rounds for primality testing
    miller_rabin_rounds: int = 25  # gmpy2 default, extremely reliable

    # Whether N has small prime factors (determined during initialization)
    n_has_small_factors: bool = False


@dataclass
class CandidateFilterResult:
    """Result of filtering a single candidate."""
    candidate: gmpy2.mpz
    passed: bool
    rejected_by: Optional[str] = None  # Name of filter that rejected, if any
    legendre_symbol: Optional[int] = None  # 0, 1, or -1 if quadratic residue check ran


# =============================================================================
# Filter Cascade Class
# =============================================================================

class CandidateFilterCascade:
    """
    Applies a cascade of mathematical filters to factor candidates.

    Filters are applied in order of computational cost:
    1. Terminal digit (~1 nanosecond)
    2. Digital root (~1 nanosecond)
    3. Small factor GCD (~100 nanoseconds)
    4. Primality test (~1-20 milliseconds)
    5. Quadratic residue (~1 microsecond)

    Usage:
        cascade = CandidateFilterCascade(N)
        result = cascade.filter(candidate)
        if result.passed:
            # candidate is a plausible factor, verify with trial division
    """

    def __init__(self, N: gmpy2.mpz):
        """
        IMPLEMENTED: Initialize filter cascade for semiprime N.

        Precomputes all N-dependent filter parameters during initialization
        so that per-candidate filtering is as fast as possible.
        """
        # STEP[1]: Store N as instance attribute
        self.N = N

        # STEP[2]: Compute and store N's terminal digit (N mod 10)
        self._n_terminal_digit = int(N % 10)

        # STEP[3]: Compute and store N's digital root using _compute_digital_root()
        self._n_digital_root = self._compute_digital_root(N)

        # STEP[4]: Build valid terminal digit set using _build_terminal_digit_map()
        terminal_map = self._build_terminal_digit_map()
        valid_terminals = terminal_map.get(self._n_terminal_digit, set())

        # STEP[5]: Build valid digital root set using _build_digital_root_map()
        dr_map = self._build_digital_root_map()
        valid_drs = dr_map.get(self._n_digital_root, set())

        # STEP[6]: Check if N has small prime factors using GCD with small_primes_product
        small_primes_product = 223092870  # 2 * 3 * 5 * 7 * 11 * 13 * 17 * 19 * 23
        n_has_small_factors = gmpy2.gcd(N, small_primes_product) > 1

        # STEP[7]: Initialize FilterConfig with all precomputed values
        self.config = FilterConfig(
            valid_terminal_digits=valid_terminals,
            valid_digital_roots=valid_drs,
            small_primes_product=small_primes_product,
            miller_rabin_rounds=25,
            n_has_small_factors=n_has_small_factors,
        )

        # STEP[8]: Initialize FilterStats for tracking
        self.stats = FilterStats()

    # =========================================================================
    # Public API
    # =========================================================================

    def filter(self, candidate: gmpy2.mpz) -> CandidateFilterResult:
        """
        IMPLEMENTED: Apply full filter cascade to a candidate.

        Filters are applied in order of computational cost:
        1. Terminal digit (~1ns)
        2. Digital root (~1ns)
        3. Small factor GCD (~100ns)
        4. Primality (~1-20ms)
        5. Quadratic residue (~1us)

        Returns result indicating whether candidate passed all filters,
        and if not, which filter rejected it.
        """
        # STEP[1]: Increment stats.total_candidates
        self.stats.total_candidates += 1

        # STEP[2]: Apply terminal digit filter
        if not self.check_terminal_digit(candidate):
            self.stats.rejected_terminal_digit += 1
            return CandidateFilterResult(
                candidate=candidate,
                passed=False,
                rejected_by="terminal_digit"
            )

        # STEP[3]: Apply digital root filter
        if not self.check_digital_root(candidate):
            self.stats.rejected_digital_root += 1
            return CandidateFilterResult(
                candidate=candidate,
                passed=False,
                rejected_by="digital_root"
            )

        # STEP[4]: Apply small factor filter
        if not self.check_small_factor(candidate):
            self.stats.rejected_small_factor += 1
            return CandidateFilterResult(
                candidate=candidate,
                passed=False,
                rejected_by="small_factor"
            )

        # STEP[5]: Apply primality filter
        if not self.check_primality(candidate):
            self.stats.rejected_primality += 1
            return CandidateFilterResult(
                candidate=candidate,
                passed=False,
                rejected_by="primality"
            )

        # STEP[6]: Apply quadratic residue filter
        passed_qr, legendre = self.check_quadratic_residue(candidate)
        if not passed_qr:
            self.stats.rejected_quadratic_residue += 1
            return CandidateFilterResult(
                candidate=candidate,
                passed=False,
                rejected_by="quadratic_residue",
                legendre_symbol=legendre
            )

        # STEP[7]: Increment stats.accepted
        self.stats.accepted += 1

        # STEP[8]: Return passed result with Legendre symbol
        return CandidateFilterResult(
            candidate=candidate,
            passed=True,
            rejected_by=None,
            legendre_symbol=legendre
        )

    def filter_batch(self, candidates: List[gmpy2.mpz]) -> List[CandidateFilterResult]:
        """
        IMPLEMENTED: Filter a batch of candidates, returning results for each.
        """
        # STEP[1], [2], [3]: Apply filter to each candidate and collect results
        return [self.filter(c) for c in candidates]

    def get_stats(self) -> FilterStats:
        """
        IMPLEMENTED: Return current filter statistics.
        """
        # STEP[1]: Return self.stats (mutable reference for efficiency)
        return self.stats

    # =========================================================================
    # Individual Filter Checks
    # =========================================================================

    def check_terminal_digit(self, candidate: gmpy2.mpz) -> bool:
        """
        IMPLEMENTED: Check if candidate's terminal digit is compatible with N.

        Cost: ~1 nanosecond (single modulo + set lookup)
        """
        # STEP[1]: Compute candidate's terminal digit (candidate mod 10)
        candidate_terminal = int(candidate % 10)

        # STEP[2] & [3]: Check if result is in valid set and return
        return candidate_terminal in self.config.valid_terminal_digits

    def check_digital_root(self, candidate: gmpy2.mpz) -> bool:
        """
        IMPLEMENTED: Check if candidate's digital root is compatible with N.

        Cost: ~1 nanosecond (single modulo + set lookup)
        """
        # STEP[1]: Compute candidate's digital root
        candidate_dr = self._compute_digital_root(candidate)

        # STEP[2] & [3]: Check if result is in valid set and return
        return candidate_dr in self.config.valid_digital_roots

    def check_small_factor(self, candidate: gmpy2.mpz) -> bool:
        """
        IMPLEMENTED: Check if candidate shares small factors appropriately with N.

        If N has no small prime factors (2, 3, 5, 7, 11, 13, 17, 19, 23),
        then neither can its factors. This filter rejects candidates that
        are divisible by small primes when N is not.

        Cost: ~100 nanoseconds (GCD computation)
        """
        # STEP[1]: If N has small factors, skip this filter (can't reject anything)
        if self.config.n_has_small_factors:
            return True

        # STEP[2]: Compute GCD of candidate with small_primes_product
        gcd = gmpy2.gcd(candidate, self.config.small_primes_product)

        # STEP[3] & [4]: If GCD > 1, candidate has small factors but N doesn't - reject
        return gcd == 1

    def check_primality(self, candidate: gmpy2.mpz) -> bool:
        """
        IMPLEMENTED: Check if candidate is a probable prime.

        Uses gmpy2's is_prime() which performs Miller-Rabin testing.
        Returns 0 for definitely composite, 1 for probably prime,
        2 for definitely prime.

        Cost: ~1-20 milliseconds depending on candidate size
        """
        # STEP[1]: Call gmpy2.is_prime() with configured number of rounds
        # gmpy2.is_prime returns: 0 = composite, 1 = probably prime, 2 = definitely prime
        result = gmpy2.is_prime(candidate, self.config.miller_rabin_rounds)

        # STEP[2]: Return True if probably prime (result > 0), False if composite
        return result > 0

    def check_quadratic_residue(self, candidate: gmpy2.mpz) -> Tuple[bool, int]:
        """
        IMPLEMENTED: Check quadratic residue (Legendre symbol) of N with respect to candidate.

        The Legendre symbol (N|p) for prime p tells us:
        - 0: p divides N (found a factor!)
        - 1: N is a quadratic residue mod p (might be a factor)
        - -1: N is a quadratic non-residue mod p (provably NOT a factor)

        This is a powerful filter: it rejects ~50% of prime candidates.

        Cost: ~1 microsecond (modular exponentiation)
        """
        # STEP[1]: Compute Legendre symbol (N | candidate) using gmpy2.legendre()
        legendre = gmpy2.legendre(self.N, candidate)

        # STEP[2]: If result == -1, candidate provably doesn't divide N
        if legendre == -1:
            return (False, -1)

        # STEP[3]: If result == 0, candidate divides N - jackpot!
        if legendre == 0:
            return (True, 0)

        # STEP[4]: If result == 1, candidate might divide N
        return (True, 1)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    @staticmethod
    def _compute_digital_root(n: gmpy2.mpz) -> int:
        """
        IMPLEMENTED: Compute digital root of n (iterative digit sum until single digit).

        The digital root is the single digit obtained by repeatedly summing
        the digits of a number until only one digit remains.

        Example: 9875 -> 9+8+7+5 = 29 -> 2+9 = 11 -> 1+1 = 2

        Mathematically, this is equivalent to n mod 9, with the special case
        that multiples of 9 have digital root 9 (not 0).

        This property is useful because digital roots are multiplicative:
        DR(a * b) = DR(DR(a) * DR(b))

        So if we know N's digital root, we can constrain which digital roots
        the factors p and q can have.
        """
        # STEP[1]: Compute n mod 9
        # Using gmpy2's modulo which handles arbitrary precision
        remainder = int(n % 9)

        # STEP[2]: If result is 0 and n > 0, return 9 (special case for multiples of 9)
        # Multiples of 9 have digital root 9, not 0
        # Example: 18 -> 1+8 = 9, and 18 % 9 = 0
        if remainder == 0 and n > 0:
            return 9

        # STEP[3]: Otherwise return the mod 9 result
        # For n = 0, we return 0 (edge case, shouldn't occur for factor candidates)
        return remainder

    @staticmethod
    def _build_terminal_digit_map() -> Dict[int, Set[int]]:
        """
        IMPLEMENTED: Build mapping of N terminal digit -> valid factor terminal digits.

        For odd primes > 5, terminal digits are 1, 3, 7, 9.
        The prime 5 is a special case - it only appears in semiprimes ending in 5.

        This method computes which terminal digit pairs produce each possible
        product terminal digit.

        Mathematical basis: When two numbers multiply, the last digit of the
        product depends only on the last digits of the multiplicands.

        Example: If N ends in 1, valid pairs are (1,1), (3,7), (7,3), (9,9).
                 So valid factor terminal digits are {1, 3, 7, 9}.

        Example: If N ends in 5, valid pairs are (5,1), (5,3), (5,7), (5,9).
                 So valid factor terminal digits are {1, 3, 5, 7, 9}.

        Note: For semiprimes, N can end in 1, 3, 5, 7, or 9.
        N ends in 5 only if one factor is exactly 5.
        """
        # STEP[1]: Define valid prime terminal digits
        # For primes > 5: {1, 3, 7, 9}
        # The prime 5 itself ends in 5
        valid_prime_terminals_gt5 = {1, 3, 7, 9}
        all_odd_prime_terminals = {1, 3, 5, 7, 9}  # Including 5

        # Initialize mapping for all possible N terminal digits
        terminal_map: Dict[int, Set[int]] = {d: set() for d in range(10)}

        # STEP[2]: Handle products of primes > 5
        # For each pair (a, b) from {1,3,7,9}, compute product terminal
        for a in valid_prime_terminals_gt5:
            for b in valid_prime_terminals_gt5:
                product_terminal = (a * b) % 10
                terminal_map[product_terminal].add(a)
                terminal_map[product_terminal].add(b)

        # STEP[3]: Handle products involving the prime 5
        # 5 * {1,3,7,9} = {5, 15, 35, 45} -> terminals {5, 5, 5, 5} = {5}
        # So if N ends in 5, one factor is 5 and the other ends in {1,3,7,9}
        for other in valid_prime_terminals_gt5:
            product_terminal = (5 * other) % 10  # Always 5
            terminal_map[product_terminal].add(5)
            terminal_map[product_terminal].add(other)

        # STEP[4]: Return the complete mapping
        return terminal_map

    @staticmethod
    def _build_digital_root_map() -> Dict[int, Set[int]]:
        """
        IMPLEMENTED: Build mapping of N digital root -> valid factor digital roots.

        Digital roots multiply: DR(p*q) = DR(DR(p) * DR(q)).

        For each possible N digital root (1-9), this computes which factor
        digital roots are valid. A factor digital root 'a' is valid for N
        digital root 'd' if there exists some 'b' in 1-9 such that
        DR(a * b) = d.
        """
        # STEP[1]: Initialize mapping for all possible digital roots (1-9)
        dr_map: Dict[int, Set[int]] = {d: set() for d in range(1, 10)}

        # STEP[2] & [3]: For each pair (a, b), compute product DR and record valid factors
        for a in range(1, 10):
            for b in range(1, 10):
                # Compute digital root of product
                # Since a, b are single digits, a*b <= 81
                product = a * b
                # DR of product: use mod 9 with 0->9 mapping
                product_dr = product % 9
                if product_dr == 0:
                    product_dr = 9

                # Both a and b are valid factor digital roots for this product DR
                dr_map[product_dr].add(a)
                dr_map[product_dr].add(b)

        # STEP[4]: Return the complete mapping
        return dr_map


# =============================================================================
# Convenience Functions
# =============================================================================

def create_filter_cascade(N: Union[int, str, gmpy2.mpz]) -> CandidateFilterCascade:
    """
    IMPLEMENTED: Create a filter cascade for the given semiprime N.
    """
    # STEP[1]: Convert N to gmpy2.mpz if not already
    if isinstance(N, str):
        n_mpz = gmpy2.mpz(N)
    elif isinstance(N, int):
        n_mpz = gmpy2.mpz(N)
    else:
        n_mpz = N

    # STEP[2]: Validate N > 3 and N is odd
    if n_mpz <= 3:
        raise ValueError(f"N must be greater than 3, got {n_mpz}")
    if n_mpz % 2 == 0:
        raise ValueError(f"N must be odd (even numbers have trivial factor 2), got {n_mpz}")

    # STEP[3]: Create and return CandidateFilterCascade instance
    return CandidateFilterCascade(n_mpz)


def quick_filter_check(N: Union[int, str, gmpy2.mpz], candidate: Union[int, str, gmpy2.mpz]) -> bool:
    """
    IMPLEMENTED: Quick one-off check if a candidate could be a factor of N.

    For repeated checks on the same N, use CandidateFilterCascade instead
    (avoids recreating the cascade for each check).
    """
    # STEP[1]: Create temporary CandidateFilterCascade for N
    cascade = create_filter_cascade(N)

    # STEP[2]: Convert candidate to gmpy2.mpz
    if isinstance(candidate, str):
        c_mpz = gmpy2.mpz(candidate)
    elif isinstance(candidate, int):
        c_mpz = gmpy2.mpz(candidate)
    else:
        c_mpz = candidate

    # STEP[3]: Call cascade.filter(candidate) and return result.passed
    result = cascade.filter(c_mpz)
    return result.passed
