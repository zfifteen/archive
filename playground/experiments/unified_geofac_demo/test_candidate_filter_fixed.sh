#!/bin/bash
#
# Exhaustive test suite for candidate_filter.py
#
# Tests the mathematical filter cascade that rejects impossible factor candidates.
# The critical property: TRUE FACTORS MUST NEVER BE REJECTED.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo "=============================================================================="
    echo -e "${BLUE}$1${NC}"
    echo "=============================================================================="
}

print_subheader() {
    echo ""
    echo -e "${CYAN}--- $1 ---${NC}"
}

# Run the Python test suite
python3 << 'PYTHON_TEST_SUITE'
import sys
import time
import gmpy2
from dataclasses import dataclass
from typing import List, Tuple

# Import the module under test
import candidate_filter as cf

# =============================================================================
# Test Framework
# =============================================================================

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration_ms: float = 0.0

class TestSuite:
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.start_time = time.time()

    def add_result(self, name: str, passed: bool, message: str = "", duration_ms: float = 0.0):
        self.results.append(TestResult(name, passed, message, duration_ms))

    def summary(self) -> Tuple[int, int]:
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        return passed, failed

# Color codes for Python print
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
NC = '\033[0m'

def print_result(name: str, passed: bool, details: str = ""):
    status = f"{GREEN}PASS{NC}" if passed else f"{RED}FAIL{NC}"
    detail_str = f" - {details}" if details else ""
    print(f"  [{status}] {name}{detail_str}")

def print_section(title: str):
    print(f"\n{CYAN}--- {title} ---{NC}")

# =============================================================================
# Test Suites
# =============================================================================

all_suites: List[TestSuite] = []

# -----------------------------------------------------------------------------
# Suite 1: Static Method Tests
# -----------------------------------------------------------------------------
def test_static_methods():
    suite = TestSuite("Static Methods")

    print_section("Digital Root Computation")

    dr = cf.CandidateFilterCascade._compute_digital_root

    test_cases = [
        (gmpy2.mpz(1), 1),
        (gmpy2.mpz(9), 9),
        (gmpy2.mpz(10), 1),
        (gmpy2.mpz(18), 9),
        (gmpy2.mpz(27), 9),
        (gmpy2.mpz(123), 6),
        (gmpy2.mpz(9875), 2),
        (gmpy2.mpz(999999999), 9),
    ]

    all_passed = True
    for n, expected in test_cases:
        result = dr(n)
        passed = result == expected
        all_passed = all_passed and passed
        if not passed:
            print_result(f"DR({n})", passed, f"got {result}, expected {expected}")

    print_result("Digital root computation", all_passed, f"{len(test_cases)} cases")
    suite.add_result("digital_root", all_passed)

    print_section("Digital Root Multiplicative Property")

    pairs = [(123, 456), (17, 19), (1000003, 1000033), (99999, 88888)]
    mult_passed = True
    for a, b in pairs:
        a_mpz, b_mpz = gmpy2.mpz(a), gmpy2.mpz(b)
        dr_product = dr(a_mpz * b_mpz)
        dr_composed = dr(gmpy2.mpz(dr(a_mpz) * dr(b_mpz)))
        if dr_product != dr_composed:
            mult_passed = False
            print_result(f"DR({a}*{b})", False, f"DR(a*b)={dr_product} != DR(DR(a)*DR(b))={dr_composed}")

    print_result("Multiplicative property", mult_passed, f"{len(pairs)} pairs")
    suite.add_result("multiplicative_property", mult_passed)

    print_section("Terminal Digit Map")

    term_map = cf.CandidateFilterCascade._build_terminal_digit_map()

    expected_maps = {
        1: {1, 3, 7, 9},
        3: {1, 3, 7, 9},
        5: {1, 3, 5, 7, 9},
        7: {1, 3, 7, 9},
        9: {1, 3, 7, 9},
    }

    map_passed = True
    for n_term, expected_set in expected_maps.items():
        actual_set = term_map[n_term]
        if actual_set != expected_set:
            map_passed = False
            print_result(f"Terminal {n_term}", False, f"got {actual_set}, expected {expected_set}")

    print_result("Terminal digit map", map_passed, f"{len(expected_maps)} terminals")
    suite.add_result("terminal_map", map_passed)

    print_section("Digital Root Map")

    dr_map = cf.CandidateFilterCascade._build_digital_root_map()

    dr_map_passed = True
    for d in range(1, 10):
        if not dr_map[d]:
            dr_map_passed = False
            print_result(f"DR map for {d}", False, "empty set")

    print_result("Digital root map completeness", dr_map_passed, "all 1-9 have valid sets")
    suite.add_result("dr_map", dr_map_passed)

    return suite

# -----------------------------------------------------------------------------
# Suite 2: True Factor Tests (CRITICAL)
# -----------------------------------------------------------------------------
def test_true_factors():
    suite = TestSuite("True Factor Acceptance (CRITICAL)")

    print_section("True Factors Must Pass All Filters")

    test_semiprimes = [
        (143, 11, 13, "small balanced"),
        (85, 5, 17, "factor 5"),
        (35, 5, 7, "both small primes"),
        (91, 7, 13, "small primes"),
        (10007 * 10009, 10007, 10009, "medium balanced"),
        (104729 * 104743, 104729, 104743, "5-digit primes"),
        (
            gmpy2.mpz("137524771864208156028430259349934309717"),
            gmpy2.mpz("10508623501177419659"),
            gmpy2.mpz("13086849276577416863"),
            "N_127 (127-bit)"
        ),
        (
            gmpy2.mpz("32452843") * gmpy2.mpz("32452867"),
            gmpy2.mpz("32452843"),
            gmpy2.mpz("32452867"),
            "8-digit primes"
        ),
    ]

    all_factors_pass = True
    factors_tested = 0

    for N, p, q, desc in test_semiprimes:
        N = gmpy2.mpz(N)
        p = gmpy2.mpz(p)
        q = gmpy2.mpz(q)

        cascade = cf.CandidateFilterCascade(N)

        result_p = cascade.filter(p)
        result_q = cascade.filter(q)

        p_ok = result_p.passed and result_p.legendre_symbol == 0
        q_ok = result_q.passed and result_q.legendre_symbol == 0

        factors_tested += 2

        if not p_ok or not q_ok:
            all_factors_pass = False
            if not p_ok:
                print_result(f"{desc}: p={p}", False, f"rejected by {result_p.rejected_by}")
            if not q_ok:
                print_result(f"{desc}: q={q}", False, f"rejected by {result_q.rejected_by}")

    print_result("All true factors accepted", all_factors_pass, f"{factors_tested} factors tested")
    suite.add_result("true_factors", all_factors_pass)

    print_section("Legendre Symbol = 0 for True Factors")

    legendre_ok = True
    for N, p, q, desc in test_semiprimes:
        N = gmpy2.mpz(N)
        p = gmpy2.mpz(p)
        q = gmpy2.mpz(q)

        cascade = cf.CandidateFilterCascade(N)
        result_p = cascade.filter(p)
        result_q = cascade.filter(q)

        if result_p.legendre_symbol != 0 or result_q.legendre_symbol != 0:
            legendre_ok = False
            print_result(f"{desc}", False,
                f"p.legendre={result_p.legendre_symbol}, q.legendre={result_q.legendre_symbol}")

    print_result("Legendre symbol = 0 for factors", legendre_ok)
    suite.add_result("legendre_zero", legendre_ok)

    return suite

# -----------------------------------------------------------------------------
# Suite 3: Filter Rejection Tests
# -----------------------------------------------------------------------------
def test_filter_rejections():
    suite = TestSuite("Filter Rejection Behavior")

    N = gmpy2.mpz("137524771864208156028430259349934309717")
    cascade = cf.CandidateFilterCascade(N)

    print_section("Terminal Digit Rejection")

    even_rejected = True
    for terminal in [0, 2, 4, 6, 8]:
        candidate = gmpy2.mpz(10508623501177419650 + terminal)
        result = cascade.filter(candidate)
        if result.passed or result.rejected_by != "terminal_digit":
            even_rejected = False

    print_result("Even numbers rejected by terminal_digit", even_rejected)
    suite.add_result("even_rejection", even_rejected)

    print_section("Primality Rejection")

    composites = [
        gmpy2.mpz(10508623501177419659 + 2),
        gmpy2.mpz(1000003 * 1000033),
        gmpy2.mpz(123456789),
    ]

    cascade = cf.CandidateFilterCascade(N)  # Fresh cascade
    composites_rejected = 0
    for comp in composites:
        if cascade.check_terminal_digit(comp) and cascade.check_digital_root(comp):
            if not cascade.check_primality(comp):
                composites_rejected += 1

    print_result("Composites rejected by primality", composites_rejected > 0,
                 f"{composites_rejected}/{len(composites)} tested")
    suite.add_result("composite_rejection", composites_rejected > 0)

    print_section("Quadratic Residue Rejection")

    cascade = cf.CandidateFilterCascade(N)
    sqrt_n = gmpy2.isqrt(N)
    test_primes = []
    candidate = sqrt_n
    while len(test_primes) < 20:
        candidate = gmpy2.next_prime(candidate)
        if cascade.check_terminal_digit(candidate) and cascade.check_digital_root(candidate):
            test_primes.append(candidate)

    qr_rejections = 0
    for prime in test_primes:
        passed, _ = cascade.check_quadratic_residue(prime)
        if not passed:
            qr_rejections += 1

    qr_rate = qr_rejections / len(test_primes) * 100
    qr_reasonable = 30 <= qr_rate <= 70

    print_result("QR rejection rate reasonable", qr_reasonable,
                 f"{qr_rate:.1f}% (expected ~50%)")
    suite.add_result("qr_rejection_rate", qr_reasonable)

    return suite

# -----------------------------------------------------------------------------
# Suite 4: Edge Cases
# -----------------------------------------------------------------------------
def test_edge_cases():
    suite = TestSuite("Edge Cases")

    print_section("Special Semiprimes")

    N_with_5 = gmpy2.mpz(5 * 1000003)
    cascade = cf.CandidateFilterCascade(N_with_5)
    result = cascade.filter(gmpy2.mpz(5))
    factor5_ok = result.passed and result.legendre_symbol == 0
    print_result("N = 5 * p: factor 5 accepted", factor5_ok)
    suite.add_result("factor_5", factor5_ok)

    N_with_3 = gmpy2.mpz(3 * 1000003)
    cascade = cf.CandidateFilterCascade(N_with_3)
    result = cascade.filter(gmpy2.mpz(3))
    factor3_ok = result.passed and result.legendre_symbol == 0
    print_result("N = 3 * p: factor 3 accepted", factor3_ok)
    suite.add_result("factor_3", factor3_ok)

    N_with_7 = gmpy2.mpz(7 * 1000003)
    cascade = cf.CandidateFilterCascade(N_with_7)
    result = cascade.filter(gmpy2.mpz(7))
    factor7_ok = result.passed and result.legendre_symbol == 0
    print_result("N = 7 * p: factor 7 accepted", factor7_ok)
    suite.add_result("factor_7", factor7_ok)

    print_section("Small Factor Detection")

    N_no_small = gmpy2.mpz("137524771864208156028430259349934309717")
    cascade = cf.CandidateFilterCascade(N_no_small)

    # Create a candidate divisible by 3 that survives terminal/digit checks if possible
    base = gmpy2.mpz("10508623501177419659")  # Near true factor
    candidate_div3 = base
    while candidate_div3 % 3 != 0:
        candidate_div3 += 2  # Keep odd

    result = cascade.filter(candidate_div3)
    # Accept rejection by ANY filter - early rejection is still correct
    small_factor_rejected = not result.passed
    print_result("Candidate with small factor rejected", small_factor_rejected,
                 f"rejected_by={result.rejected_by if not result.passed else 'none'}")
    suite.add_result("small_factor_filter", small_factor_rejected)

    print_section("Input Validation")

    try:
        cf.create_filter_cascade(3)
        validation_ok = False
    except ValueError:
        validation_ok = True
    print_result("N <= 3 rejected", validation_ok)
    suite.add_result("validate_small_n", validation_ok)

    try:
        cf.create_filter_cascade(100)
        validation_ok = False
    except ValueError:
        validation_ok = True
    print_result("Even N rejected", validation_ok)
    suite.add_result("validate_even_n", validation_ok)

    try:
        cascade = cf.create_filter_cascade("143")
        string_ok = cascade.N == 143
    except:
        string_ok = False
    print_result("String input accepted", string_ok)
    suite.add_result("string_input", string_ok)

    return suite

# -----------------------------------------------------------------------------
# Suite 5: Statistics Tracking
# -----------------------------------------------------------------------------
def test_statistics():
    suite = TestSuite("Statistics Tracking")

    print_section("Filter Statistics")

    N = gmpy2.mpz("137524771864208156028430259349934309717")
    cascade = cf.CandidateFilterCascade(N)

    candidates = [
        gmpy2.mpz("10508623501177419659"),
        gmpy2.mpz("13086849276577416863"),
        gmpy2.mpz("10508623501177419660"),
        gmpy2.mpz("10508623501177419662"),
        gmpy2.mpz("10508623501177419661"),
        gmpy2.mpz("10508623501177419663"),
    ]

    for c in candidates:
        cascade.filter(c)

    stats = cascade.get_stats()

    stats_ok = stats.total_candidates == len(candidates)
    print_result("Total candidates tracked", stats_ok,
                 f"{stats.total_candidates} == {len(candidates)}")
    suite.add_result("total_tracked", stats_ok)

    accepted_ok = stats.accepted == 2
    print_result("Accepted count correct", accepted_ok, f"{stats.accepted} == 2")
    suite.add_result("accepted_count", accepted_ok)

    total_rejected = (stats.rejected_terminal_digit + stats.rejected_digital_root +
                      stats.rejected_small_factor + stats.rejected_primality +
                      stats.rejected_quadratic_residue)
    sum_ok = stats.total_candidates == stats.accepted + total_rejected
    print_result("Rejection counts sum correctly", sum_ok,
                 f"{stats.accepted} + {total_rejected} == {stats.total_candidates}")
    suite.add_result("rejection_sum", sum_ok)

    print_section("Summary Statistics")

    summary = stats.summary()

    summary_ok = all([
        'total_candidates' in summary,
        'accepted' in summary,
        'acceptance_rate' in summary,
        'per_filter_rejections' in summary,
        'per_filter_rates' in summary,
        'cumulative_rejection_rate' in summary,
    ])
    print_result("Summary contains all fields", summary_ok)
    suite.add_result("summary_fields", summary_ok)

    expected_rate = (2 / len(candidates)) * 100
    rate_ok = abs(summary['acceptance_rate'] - expected_rate) < 0.01
    print_result("Acceptance rate calculated correctly", rate_ok,
                 f"{summary['acceptance_rate']:.2f}% == {expected_rate:.2f}%")
    suite.add_result("acceptance_rate", rate_ok)

    return suite

# -----------------------------------------------------------------------------
# Suite 6: Performance Sanity Check
# -----------------------------------------------------------------------------
def test_performance():
    suite = TestSuite("Performance")

    print_section("Filter Performance")

    N = gmpy2.mpz("137524771864208156028430259349934309717")
    cascade = cf.CandidateFilterCascade(N)

    sqrt_n = gmpy2.isqrt(N)
    candidates = [sqrt_n + i*2 + 1 for i in range(100)]

    start = time.time()
    results = cascade.filter_batch([gmpy2.mpz(c) for c in candidates])
    elapsed_ms = (time.time() - start) * 1000

    perf_ok = elapsed_ms < 5000
    print_result("100 candidates filtered", perf_ok, f"{elapsed_ms:.1f}ms")
    suite.add_result("batch_performance", perf_ok)

    batch_ok = len(results) == 100
    print_result("Batch results complete", batch_ok, f"{len(results)} results")
    suite.add_result("batch_completeness", batch_ok)

    return suite

# =============================================================================
# Main Test Runner
# =============================================================================

def main():
    print("=" * 78)
    print(f"{CYAN}CANDIDATE FILTER CASCADE - EXHAUSTIVE TEST SUITE{NC}")
    print("=" * 78)
    print(f"Testing: candidate_filter.py")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    suites = [
        test_static_methods(),
        test_true_factors(),
        test_filter_rejections(),
        test_edge_cases(),
        test_statistics(),
        test_performance(),
    ]

    print("\n" + "=" * 78)
    print(f"{CYAN}TEST SUMMARY{NC}")
    print("=" * 78)

    total_passed = 0
    total_failed = 0

    for suite in suites:
        passed, failed = suite.summary()
        total_passed += passed
        total_failed += failed

        status = f"{GREEN}PASS{NC}" if failed == 0 else f"{RED}FAIL{NC}"
        print(f"  [{status}] {suite.name}: {passed} passed, {failed} failed")

    print()
    print(f"Total: {total_passed} passed, {total_failed} failed")
    print(f"Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if total_failed == 0:
        print(f"\n{GREEN}All tests passed!{NC}")
        sys.exit(0)
    else:
        print(f"\n{RED}Some tests failed.{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()

PYTHON_TEST_SUITE

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}Test suite completed successfully.${NC}"
else
    echo -e "${RED}Test suite failed.${NC}"
fi

exit $exit_code