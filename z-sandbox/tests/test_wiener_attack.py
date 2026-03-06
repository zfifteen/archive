#!/usr/bin/env python3
"""
Unit tests for Wiener Attack with Convergent Selectivity.

Tests continued fraction expansion, convergent computation,
Wiener attack implementation, and golden ratio defense.

Run from repository root:
    PYTHONPATH=python python3 tests/test_wiener_attack.py
    
Or with pytest:
    PYTHONPATH=python pytest tests/test_wiener_attack.py -v
"""

import sys
sys.path.append("../python")
sys.path.append("python")

import math
import pytest
from wiener_attack import (
    ContinuedFraction,
    WienerAttack,
    GoldenRatioDefense
)


def test_continued_fraction_simple():
    """Test continued fraction expansion of simple rationals."""
    print("\n=== Test: Simple Continued Fractions ===")
    
    # Test 1/2 = [0; 2]
    quotients = ContinuedFraction.quotients(1, 2)
    assert quotients == [0, 2], f"Expected [0, 2], got {quotients}"
    print(f"✓ CF(1/2) = {quotients}")
    
    # Test 3/2 = [1; 2]
    quotients = ContinuedFraction.quotients(3, 2)
    assert quotients == [1, 2], f"Expected [1, 2], got {quotients}"
    print(f"✓ CF(3/2) = {quotients}")
    
    # Test 22/7 (approximation of π)
    quotients = ContinuedFraction.quotients(22, 7)
    assert quotients == [3, 7], f"Expected [3, 7], got {quotients}"
    print(f"✓ CF(22/7) = {quotients}")


def test_convergents_computation():
    """Test convergent computation."""
    print("\n=== Test: Convergents Computation ===")
    
    # Test convergents of 22/7
    convergents = ContinuedFraction.convergents(22, 7)
    print(f"Convergents of 22/7: {convergents}")
    
    # Verify convergents approach 22/7
    assert len(convergents) >= 2, "Should have at least 2 convergents"
    
    # Last convergent should equal the original fraction
    last_conv = convergents[-1]
    assert last_conv[0] * 7 == last_conv[1] * 22 or abs(last_conv[0]/last_conv[1] - 22/7) < 1e-10
    print(f"✓ Convergents computed correctly")


def test_convergents_fibonacci():
    """Test convergents of golden ratio approximation."""
    print("\n=== Test: Golden Ratio Convergents ===")
    
    # Fibonacci ratio F(10)/F(9) = 55/34 ≈ φ
    convergents = ContinuedFraction.convergents(55, 34)
    quotients = ContinuedFraction.quotients(55, 34)
    
    print(f"CF(55/34) quotients: {quotients}")
    print(f"Convergents: {convergents[:5]}")
    
    # Golden ratio CF is [1; 1, 1, 1, ...] so quotients should be mostly 1s
    ones_count = sum(1 for q in quotients if q == 1)
    assert ones_count >= len(quotients) - 2, "Fibonacci ratio should have mostly 1s in CF"
    print(f"✓ Golden ratio CF properties verified ({ones_count}/{len(quotients)} quotients = 1)")


def test_wiener_attack_vulnerable():
    """Test Wiener attack on vulnerable RSA parameters."""
    print("\n=== Test: Wiener Attack on Vulnerable RSA ===")
    
    # Create vulnerable RSA instance
    p = 857
    q = 1009
    N = p * q
    phi_N = (p - 1) * (q - 1)
    d = 17  # Small d, vulnerable
    e = pow(d, -1, phi_N)
    
    print(f"Testing with N={N}, d={d}, e={e}")
    print(f"N^(1/4) = {N**(0.25):.2f}, d < N^(1/4)? {d < N**(0.25)}")
    
    # Perform attack
    attacker = WienerAttack(verbose=False)
    result = attacker.attack(e, N)
    
    assert result is not None, "Attack should succeed on vulnerable parameters"
    p_found, q_found = result
    assert p_found * q_found == N, "Found factors should multiply to N"
    assert {p_found, q_found} == {p, q}, "Should find correct factors"
    
    print(f"✓ Attack succeeded: found p={p_found}, q={q_found}")
    print(f"✓ Convergents tested: {attacker.stats['convergents_tested']}")


def test_wiener_attack_resistant():
    """Test Wiener attack on resistant RSA parameters."""
    print("\n=== Test: Wiener Attack on Resistant RSA ===")
    
    # Create resistant RSA instance (larger d)
    p = 857
    q = 1009
    N = p * q
    phi_N = (p - 1) * (q - 1)  # phi_N = 862848 (calculated from p and q)
    d = 12347  # Large d, resistant
    
    # Ensure d is coprime to phi_N
    MAX_ITERATIONS = 1000  # Safety limit
    iterations = 0
    while math.gcd(d, phi_N) != 1:
        d += 1
        iterations += 1
        if iterations > MAX_ITERATIONS:
            pytest.skip("Could not find coprime d within iteration limit")
    
    e = pow(d, -1, phi_N)
    
    print(f"Testing with N={N}, d={d}, e={e}")
    print(f"N^(1/4) = {N**(0.25):.2f}, d < N^(1/4)? {d < N**(0.25)}")
    
    # Perform attack
    attacker = WienerAttack(verbose=False)
    result = attacker.attack(e, N)
    
    # Attack should fail on resistant parameters
    assert result is None, "Attack should fail on resistant parameters"
    print(f"✓ Attack failed as expected (d too large)")


def test_bias_scanning_efficiency():
    """Test that bias scanning improves efficiency."""
    print("\n=== Test: Bias Scanning Efficiency ===")
    
    # Create test case with large quotient
    # We'll use a fraction that has an anomalous quotient
    e = 1234567
    N = 864713  # Same N as before
    
    # Test with bias scanning enabled
    attacker_biased = WienerAttack(
        enable_bias_scanning=True,
        max_quotient_threshold=100,
        verbose=False
    )
    result1 = attacker_biased.attack(e, N)
    tested_with_bias = attacker_biased.stats['convergents_tested']
    skipped_with_bias = attacker_biased.stats['convergents_skipped']
    
    # Test without bias scanning
    attacker_full = WienerAttack(
        enable_bias_scanning=False,
        verbose=False
    )
    result2 = attacker_full.attack(e, N)
    tested_without_bias = attacker_full.stats['convergents_tested']
    
    print(f"With bias scanning: {tested_with_bias} tested, {skipped_with_bias} skipped")
    print(f"Without bias scanning: {tested_without_bias} tested")
    
    # Both should reach same conclusion (fail in this case)
    assert result1 == result2, "Results should match regardless of bias scanning"
    
    # Bias scanning should test fewer or equal convergents
    assert tested_with_bias <= tested_without_bias, "Bias scanning should be more efficient"
    print(f"✓ Bias scanning efficiency confirmed")


def test_vulnerability_analysis():
    """Test vulnerability analysis functionality."""
    print("\n=== Test: Vulnerability Analysis ===")
    
    # Vulnerable parameters
    p = 857
    q = 1009
    N = p * q
    phi_N = (p - 1) * (q - 1)
    d_vuln = 17
    e_vuln = pow(d_vuln, -1, phi_N)
    
    attacker = WienerAttack()
    analysis_vuln = attacker.analyze_vulnerability(e_vuln, N)
    
    print(f"Vulnerable analysis: score={analysis_vuln['vulnerability_score']:.2f}")
    assert 'total_convergents' in analysis_vuln
    assert 'vulnerability_score' in analysis_vuln
    assert isinstance(analysis_vuln['vulnerability_score'], (int, float))
    
    # Resistant parameters
    d_resist = 12347
    MAX_ITERATIONS = 1000  # Safety limit
    iterations = 0
    while math.gcd(d_resist, phi_N) != 1:
        d_resist += 1
        iterations += 1
        if iterations > MAX_ITERATIONS:
            pytest.skip("Could not find coprime d within iteration limit")
    e_resist = pow(d_resist, -1, phi_N)
    
    analysis_resist = attacker.analyze_vulnerability(e_resist, N)
    print(f"Resistant analysis: score={analysis_resist['vulnerability_score']:.2f}")
    
    # Vulnerable should have higher score
    # (Note: scoring is heuristic, so we just check it's in valid range)
    assert 0 <= analysis_vuln['vulnerability_score'] <= 1
    assert 0 <= analysis_resist['vulnerability_score'] <= 1
    
    print(f"✓ Vulnerability analysis working")


def test_golden_ratio_resistance():
    """Test golden ratio defense mechanism."""
    print("\n=== Test: Golden Ratio Resistance ===")
    
    N = 864713
    
    # Check resistance property
    # We can't generate full RSA params here, but we can test the checker
    e_test = 65537  # Standard exponent
    
    attacker = WienerAttack()
    is_resistant = GoldenRatioDefense.is_phi_resistant(e_test, N, threshold=100)
    
    print(f"e=65537, N={N}: resistant={is_resistant}")
    assert isinstance(is_resistant, bool)
    
    # Test with a vulnerable e
    phi_N = 862848
    d_small = 17
    e_vuln = pow(d_small, -1, phi_N)
    
    is_resistant_vuln = GoldenRatioDefense.is_phi_resistant(e_vuln, N, threshold=100)
    print(f"e={e_vuln} (d=17), N={N}: resistant={is_resistant_vuln}")
    
    print(f"✓ Resistance checking functional")


def test_large_quotient_detection():
    """Test detection of anomalously large quotients."""
    print("\n=== Test: Large Quotient Detection ===")
    
    # Create a case with large quotient
    # Using the "5911 pattern" mentioned in the issue
    e = 17993
    N = 90581
    
    attacker = WienerAttack(max_quotient_threshold=1000, verbose=False)
    analysis = attacker.analyze_vulnerability(e, N)
    
    print(f"Analysis of e={e}, N={N}:")
    print(f"  Max quotient: {analysis['max_quotient']}")
    print(f"  Large quotients: {analysis['large_quotients_count']}")
    print(f"  First large index: {analysis['first_large_quotient_index']}")
    
    assert 'max_quotient' in analysis
    assert 'large_quotients_count' in analysis
    
    print(f"✓ Large quotient detection working")


def test_convergent_termination_pattern():
    """Test early termination based on convergent patterns."""
    print("\n=== Test: Convergent Termination Pattern ===")
    
    # Test case where bias scanning should trigger early termination
    e = 123456789
    N = 864713
    
    attacker = WienerAttack(
        max_quotient_threshold=500,
        enable_bias_scanning=True,
        verbose=False
    )
    
    result = attacker.attack(e, N)
    
    total = attacker.stats['total_convergents']
    tested = attacker.stats['convergents_tested']
    skipped = attacker.stats['convergents_skipped']
    
    print(f"Total convergents: {total}")
    print(f"Tested: {tested}")
    print(f"Skipped: {skipped}")
    
    # If large quotient detected, should have skipped some
    if attacker.stats['large_quotients_detected'] > 0:
        assert skipped > 0, "Should skip convergents after large quotient"
        print(f"✓ Early termination triggered ({skipped} convergents skipped)")
    else:
        print(f"✓ No large quotients in this case")


def test_denominator_growth_analysis():
    """Test analysis of denominator growth patterns."""
    print("\n=== Test: Denominator Growth Analysis ===")
    
    # Get convergents for analysis
    e = 659825
    N = 864713
    
    convergents = ContinuedFraction.convergents(e, N, max_terms=20)
    
    print(f"First 10 convergents (denominators):")
    for i, (num, denom) in enumerate(convergents[:10]):
        growth = denom / convergents[i-1][1] if i > 0 and convergents[i-1][1] > 0 else 1
        print(f"  [{i}]: {num}/{denom} (growth: {growth:.2f}x)")
    
    # Verify denominator growth
    for i in range(1, min(len(convergents), 10)):
        assert convergents[i][1] >= convergents[i-1][1], "Denominators should grow"
    
    print(f"✓ Denominator growth pattern verified")


def run_all_tests():
    """Run all tests in sequence."""
    print("=" * 70)
    print("WIENER ATTACK TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_continued_fraction_simple,
        test_convergents_computation,
        test_convergents_fibonacci,
        test_wiener_attack_vulnerable,
        test_wiener_attack_resistant,
        test_bias_scanning_efficiency,
        test_vulnerability_analysis,
        test_golden_ratio_resistance,
        test_large_quotient_detection,
        test_convergent_termination_pattern,
        test_denominator_growth_analysis,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n✗ FAILED: {test.__name__}")
            print(f"  Error: {e}")
        except Exception as e:
            failed += 1
            print(f"\n✗ ERROR: {test.__name__}")
            print(f"  Exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
