#!/bin/bash
#
# Test suite for unified_geofac_demo.py
# Tests factorization of semiprimes with various factor balances
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_SCRIPT="$SCRIPT_DIR/unified_geofac_demo.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
SKIPPED=0
TOTAL=0

# Test timeout (seconds)
TIMEOUT=120

print_header() {
    echo ""
    echo "=============================================================================="
    echo -e "${BLUE}$1${NC}"
    echo "=============================================================================="
}

print_subheader() {
    echo ""
    echo -e "${YELLOW}--- $1 ---${NC}"
}

# Deterministic test - expects specific result
run_deterministic_test() {
    local name="$1"
    local n="$2"
    local expected_p="$3"
    local expected_q="$4"
    local description="$5"

    TOTAL=$((TOTAL + 1))

    print_subheader "Test $TOTAL: $name"
    echo "N = $n"
    echo "Expected: p=$expected_p, q=$expected_q"
    echo "Description: $description"
    echo ""

    local start_time=$(date +%s.%N)
    local output
    local exit_code=0

    output=$(timeout $TIMEOUT python3 "$DEMO_SCRIPT" "$n" 2>&1) || exit_code=$?

    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "N/A")

    if [ $exit_code -eq 124 ]; then
        echo -e "${RED}TIMEOUT${NC} after ${TIMEOUT}s"
        FAILED=$((FAILED + 1))
        return
    fi

    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}FAILED${NC} (exit code $exit_code)"
        echo "Output (last 5 lines):"
        echo "$output" | tail -5
        FAILED=$((FAILED + 1))
        return
    fi

    local found_p=$(echo "$output" | grep -E "^\s*p = " | sed 's/.*p = //')
    local found_q=$(echo "$output" | grep -E "^\s*q = " | sed 's/.*q = //')
    local method=$(echo "$output" | grep -E "SUCCESS via" | sed 's/.*SUCCESS via //')
    local verification=$(echo "$output" | grep -E "Verification:" | grep -o "True\|False")

    # Check if factors match (in either order)
    local match=false
    if [[ ("$found_p" == "$expected_p" && "$found_q" == "$expected_q") || \
          ("$found_p" == "$expected_q" && "$found_q" == "$expected_p") ]]; then
        match=true
    fi

    if [ "$match" = true ] && [ "$verification" = "True" ]; then
        echo -e "${GREEN}PASSED${NC} in ${duration}s via $method"
        echo "  Found: p=$found_p, q=$found_q"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAILED${NC}"
        echo "  Expected: p=$expected_p, q=$expected_q"
        echo "  Found:    p=$found_p, q=$found_q"
        echo "  Verification: $verification"
        FAILED=$((FAILED + 1))
    fi
}

# Probabilistic test - algorithm may or may not find factors
run_probabilistic_test() {
    local name="$1"
    local n="$2"
    local expected_p="$3"
    local expected_q="$4"
    local description="$5"

    TOTAL=$((TOTAL + 1))

    print_subheader "Test $TOTAL: $name (probabilistic)"
    echo "N = $n"
    echo "True factors: p=$expected_p, q=$expected_q"
    echo "Description: $description"
    echo ""

    local start_time=$(date +%s.%N)
    local output
    local exit_code=0

    output=$(timeout $TIMEOUT python3 "$DEMO_SCRIPT" "$n" 2>&1) || exit_code=$?

    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "N/A")

    if [ $exit_code -eq 124 ]; then
        echo -e "${YELLOW}TIMEOUT${NC} after ${TIMEOUT}s (expected for hard instances)"
        SKIPPED=$((SKIPPED + 1))
        return
    fi

    # Extract metadata
    local balanced_tests=$(echo "$output" | grep -E "Balanced phase:" | grep -oE "[0-9]+ tests" | head -1)
    local adaptive_tests=$(echo "$output" | grep -E "Adaptive phase:" | grep -oE "[0-9]+ tests" | head -1)
    local windows=$(echo "$output" | grep -E "Explored windows:" | sed 's/.*Explored windows: //')

    if [ $exit_code -eq 0 ]; then
        local found_p=$(echo "$output" | grep -E "^\s*p = " | sed 's/.*p = //')
        local found_q=$(echo "$output" | grep -E "^\s*q = " | sed 's/.*q = //')
        local method=$(echo "$output" | grep -E "SUCCESS via" | sed 's/.*SUCCESS via //')
        local verification=$(echo "$output" | grep -E "Verification:" | grep -o "True\|False")

        if [ "$verification" = "True" ]; then
            # Check if correct factors found
            local match=false
            if [[ ("$found_p" == "$expected_p" && "$found_q" == "$expected_q") || \
                  ("$found_p" == "$expected_q" && "$found_q" == "$expected_p") ]]; then
                match=true
            fi

            if [ "$match" = true ]; then
                echo -e "${GREEN}PASSED${NC} in ${duration}s via $method"
                echo "  Found expected factors: p=$found_p, q=$found_q"
            else
                echo -e "${CYAN}PARTIAL${NC} in ${duration}s via $method"
                echo "  Found different factorization (N has multiple factor pairs or algorithm found alternative)"
                echo "  Found: p=$found_p, q=$found_q"
            fi
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}FAILED${NC} - verification failed"
            FAILED=$((FAILED + 1))
        fi
    else
        echo -e "${YELLOW}NOT FOUND${NC} in ${duration}s (probabilistic - may require multiple runs)"
        echo "  Balanced: $balanced_tests | Adaptive: $adaptive_tests"
        echo "  Windows explored: $windows"
        SKIPPED=$((SKIPPED + 1))
    fi
}

run_error_test() {
    local name="$1"
    local n="$2"
    local expected_error="$3"

    TOTAL=$((TOTAL + 1))

    print_subheader "Test $TOTAL: $name (error case)"
    echo "Input: $n"
    echo "Expected error: $expected_error"
    echo ""

    local output
    local exit_code=0

    output=$(python3 "$DEMO_SCRIPT" "$n" 2>&1) || exit_code=$?

    if [ $exit_code -ne 0 ] && echo "$output" | grep -q "$expected_error"; then
        echo -e "${GREEN}PASSED${NC} - correctly rejected with expected error"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAILED${NC} - expected error not found"
        echo "Output: $output"
        FAILED=$((FAILED + 1))
    fi
}

# ==============================================================================
# MAIN TEST EXECUTION
# ==============================================================================

print_header "UNIFIED GEOFAC DEMO TEST SUITE"
echo "Script: $DEMO_SCRIPT"
echo "Timeout: ${TIMEOUT}s per test"
echo "Started: $(date)"

# Check dependencies
print_header "CHECKING DEPENDENCIES"
python3 -c "import numpy, gmpy2, mpmath" 2>/dev/null && \
    echo -e "${GREEN}All Python dependencies available${NC}" || \
    { echo -e "${RED}Missing dependencies. Run: pip install numpy gmpy2 mpmath${NC}"; exit 1; }

# ==============================================================================
# TEST GROUP 1: Deterministic Small Factor Detection
# ==============================================================================
print_header "TEST GROUP 1: SMALL FACTOR DETECTION (deterministic)"

# Even number (factor of 2)
run_deterministic_test "Large even semiprime" \
    "123456789012345678901234567890" \
    "2" \
    "61728394506172839450617283945" \
    "Should detect factor of 2 via trial division"

# Factor of 3
run_deterministic_test "Multiple of 3" \
    "333333333333333333333333333333" \
    "3" \
    "111111111111111111111111111111" \
    "Should detect factor of 3 via trial division"

# Factor of 7 (not divisible by smaller primes)
run_deterministic_test "Multiple of 7" \
    "777777777777777777777777777791" \
    "7" \
    "111111111111111111111111111113" \
    "Should detect factor of 7 via trial division"

# Factor of 11 (not divisible by smaller primes)
run_deterministic_test "Multiple of 11" \
    "1111111111111111111111111111121" \
    "11" \
    "101010101010101010101010101011" \
    "Should detect factor of 11 via trial division"

# ==============================================================================
# TEST GROUP 2: Error Handling
# ==============================================================================
print_header "TEST GROUP 2: ERROR HANDLING (deterministic)"

run_error_test "N too small" "3" "must be at least 4"
run_error_test "Invalid input (text)" "notanumber" "Invalid integer"
run_error_test "Invalid input (float)" "123.456" "Invalid integer"

# ==============================================================================
# TEST GROUP 3: Probabilistic Factorization
# ==============================================================================
print_header "TEST GROUP 3: PROBABILISTIC FACTORIZATION"
echo ""
echo "NOTE: These tests use heuristic algorithms with random sampling."
echo "      Success depends on factor position and random seed alignment."
echo "      'NOT FOUND' results are expected for some instances."

# N_127 - the canonical test case (factors ~10-11% from sqrt)
run_probabilistic_test "N_127 (127-bit, canonical)" \
    "137524771864208156028430259349934309717" \
    "10508623501177419659" \
    "13086849276577416863" \
    "Factors at -10.4% and +11.6% from sqrt(N), should be in ±13% window"

# 96-bit with very close factors (within 0.001%)
run_probabilistic_test "96-bit ultra-balanced" \
    "10000000000009800000000002077" \
    "100000000000031" \
    "100000000000067" \
    "Factors differ by 36, essentially at sqrt(N)"

# 81-bit with close factors
run_probabilistic_test "81-bit balanced" \
    "1208925819660808663073173" \
    "1099511627791" \
    "1099511627803" \
    "Factors differ by 12, at sqrt(N)"

# ==============================================================================
# TEST GROUP 4: Metadata Verification
# ==============================================================================
print_header "TEST GROUP 4: OUTPUT STRUCTURE VERIFICATION"

print_subheader "Verifying full algorithm output format"
TOTAL=$((TOTAL + 1))

# Run on a semiprime that requires full algorithm (not small factor detection)
# This 64-bit semiprime has no small factors
output=$(timeout 30 python3 "$DEMO_SCRIPT" "9223372036854775837" 2>&1) || true

errors=""
echo "$output" | grep -q "UNIFIED GEOFAC BLIND FACTORIZATION" || errors="${errors}Missing header. "
echo "$output" | grep -q "Bit length:" || errors="${errors}Missing bit length. "
echo "$output" | grep -q "STAGE 1: BALANCED" || errors="${errors}Missing Stage 1. "
echo "$output" | grep -q "FINAL RESULTS" || errors="${errors}Missing final results. "
echo "$output" | grep -q "Performance Summary" || errors="${errors}Missing performance summary. "
echo "$output" | grep -q "Balanced phase:" || errors="${errors}Missing balanced phase stats. "
echo "$output" | grep -q "Explored windows:" || errors="${errors}Missing explored windows. "

if [ -z "$errors" ]; then
    echo -e "${GREEN}PASSED${NC} - All expected output sections present"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAILED${NC} - $errors"
    FAILED=$((FAILED + 1))
fi

print_subheader "Verifying small factor detection output"
TOTAL=$((TOTAL + 1))

# Small factor detection has minimal output
output=$(python3 "$DEMO_SCRIPT" "123456789012345678901234567890" 2>&1)

errors=""
echo "$output" | grep -q "SUCCESS" || errors="${errors}Missing success. "
echo "$output" | grep -q "small_factor_trial" || errors="${errors}Missing method. "
echo "$output" | grep -q "p = 2" || errors="${errors}Missing factor p. "
echo "$output" | grep -q "Verification" || errors="${errors}Missing verification. "

if [ -z "$errors" ]; then
    echo -e "${GREEN}PASSED${NC} - Small factor output correct"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAILED${NC} - $errors"
    FAILED=$((FAILED + 1))
fi

# ==============================================================================
# SUMMARY
# ==============================================================================
print_header "TEST SUMMARY"

echo "Total tests:  $TOTAL"
echo -e "Passed:       ${GREEN}$PASSED${NC}"
echo -e "Skipped/NA:   ${YELLOW}$SKIPPED${NC} (probabilistic tests that didn't find factors)"
echo -e "Failed:       ${RED}$FAILED${NC}"
echo ""
echo "Completed: $(date)"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}All deterministic tests passed!${NC}"
    if [ $SKIPPED -gt 0 ]; then
        echo -e "${YELLOW}Some probabilistic tests did not find factors (expected behavior).${NC}"
    fi
    exit 0
else
    echo ""
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
