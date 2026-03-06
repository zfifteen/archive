#!/usr/bin/env python3
"""
RSA-260 Setup Validation Script

This script validates that the RSA-260 factorization setup meets all requirements:
1. Center is fixed at log(N)/2
2. High precision (dps≥1000)
3. Fractional m sampling
4. Distance-based ranking
5. Deterministic PRP
"""

import sys
import os
from mpmath import mp, mpf, log as mplog

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python.rsa260_repro import (
    RSA_260,
    miller_rabin_deterministic,
    comb_formula,
    generate_fractional_candidates,
    rank_by_distance
)
from python.geom.m0_estimator import estimate_m0_balanced, get_resonance_metadata


def validate_rsa260_constant():
    """Validate RSA-260 constant."""
    print("=" * 80)
    print("1. RSA-260 Constant Validation")
    print("=" * 80)
    
    expected_bits = 862
    expected_digits = 260
    
    actual_bits = RSA_260.bit_length()
    actual_digits = len(str(RSA_260))
    
    print(f"Bits: {actual_bits} (expected: {expected_bits})")
    print(f"Digits: {actual_digits} (expected: {expected_digits})")
    
    assert actual_bits == expected_bits, f"Bit count mismatch"
    assert actual_digits == expected_digits, f"Digit count mismatch"
    
    print("✓ RSA-260 constant validated")
    print()


def validate_center_fixed():
    """Validate that center is fixed at log(N)/2."""
    print("=" * 80)
    print("2. Fixed Center Validation")
    print("=" * 80)
    
    dps = 1000
    mp.dps = dps
    
    log_N = mplog(RSA_260)
    center = log_N / 2
    
    print(f"log(N) = {float(log_N):.10f}")
    print(f"center = {float(center):.10f}")
    print(f"center = log(N)/2: {abs(float(center) - float(log_N)/2) < 1e-10}")
    
    # Test with different k values - center should never change
    print("\nTesting center stability with different k values:")
    for k in [0.29, 0.3, 0.31, 0.5, 1.0]:
        metadata = get_resonance_metadata(RSA_260, k, dps)
        center_k = metadata['center']
        deviation = abs(center_k - float(center))
        print(f"  k={k:.2f}: center={center_k:.10f}, deviation={deviation:.2e}")
        assert deviation < 1e-10, f"Center shifted with k={k}"
    
    print("✓ Center is fixed at log(N)/2")
    print()


def validate_high_precision():
    """Validate high precision calculations."""
    print("=" * 80)
    print("3. High Precision Validation")
    print("=" * 80)
    
    dps = 1000
    mp.dps = dps
    
    log_N = mplog(RSA_260)
    log_N_str = str(log_N)
    
    # Count significant digits
    digits = log_N_str.replace('.', '').replace('-', '')
    
    print(f"Precision: {dps} dps")
    print(f"log(N) has {len(digits)} digits")
    print(f"log(N) = {log_N_str[:50]}...")
    
    assert len(digits) > 100, "Insufficient precision"
    
    print("✓ High precision validated (>100 digits)")
    print()


def validate_fractional_m_sampling():
    """Validate fractional m sampling."""
    print("=" * 80)
    print("4. Fractional M Sampling Validation")
    print("=" * 80)
    
    dps = 1000
    k = 0.3
    m0 = 0.0
    window = 0.01
    step = 0.001
    
    candidates = generate_fractional_candidates(RSA_260, k, m0, window, step, dps)
    
    print(f"Parameters: k={k}, m0={m0}, window=±{window}, step={step}")
    print(f"Generated: {len(candidates)} candidates")
    
    # Check for fractional m values
    m_values = [m for m, p in candidates]
    non_integer = sum(1 for m in m_values if abs(m - round(m)) > 1e-6)
    
    print(f"Non-integer m values: {non_integer}/{len(m_values)} ({100*non_integer/len(m_values):.1f}%)")
    
    assert non_integer > len(m_values) * 0.8, "Not enough fractional m values"
    
    print("✓ Fractional m sampling validated")
    print()


def validate_distance_ranking():
    """Validate distance-based ranking."""
    print("=" * 80)
    print("5. Distance-Based Ranking Validation")
    print("=" * 80)
    
    dps = 1000
    k = 0.3
    m0 = 0.0
    window = 0.01
    step = 0.001
    
    candidates = generate_fractional_candidates(RSA_260, k, m0, window, step, dps)
    ranked = rank_by_distance(candidates, RSA_260, dps)
    
    print(f"Ranked {len(ranked)} candidates by distance")
    print("\nTop 5 candidates:")
    for i, (m, p, dist) in enumerate(ranked[:5]):
        print(f"  {i+1}. m={m:.6f}, distance={dist:.6e}")
    
    # Verify sorting
    distances = [dist for m, p, dist in ranked]
    sorted_correctly = all(distances[i] <= distances[i+1] for i in range(len(distances)-1))
    
    print(f"\nSorted correctly: {sorted_correctly}")
    assert sorted_correctly, "Distances not sorted"
    
    print("✓ Distance-based ranking validated")
    print()


def validate_deterministic_prp():
    """Validate deterministic PRP test."""
    print("=" * 80)
    print("6. Deterministic PRP Validation")
    print("=" * 80)
    
    # Test with known primes
    known_primes = [2, 3, 97, 1000000007]
    print("Testing known primes:")
    for p in known_primes:
        is_prime = miller_rabin_deterministic(p, rounds=32)
        print(f"  {p}: {is_prime}")
        assert is_prime, f"Failed to identify prime {p}"
    
    # Test with known composites
    known_composites = [4, 561, 1729]  # 561 and 1729 are Carmichael numbers
    print("\nTesting known composites:")
    for n in known_composites:
        is_prime = miller_rabin_deterministic(n, rounds=32)
        print(f"  {n}: {is_prime}")
        assert not is_prime, f"Failed to identify composite {n}"
    
    # Test reproducibility
    print("\nTesting reproducibility:")
    n = 1000000007
    results = [miller_rabin_deterministic(n, rounds=32) for _ in range(10)]
    print(f"  10 runs on {n}: all {results[0]}")
    assert all(r == results[0] for r in results), "Not deterministic"
    
    print("✓ Deterministic PRP validated")
    print()


def validate_comb_formula():
    """Validate comb formula precision."""
    print("=" * 80)
    print("7. Comb Formula Precision Validation")
    print("=" * 80)
    
    dps = 1000
    k = 0.3
    
    test_m_values = [0.0, 0.001, -0.001, 0.01]
    
    print(f"Testing comb formula at k={k}, dps={dps}:")
    for m in test_m_values:
        p = comb_formula(RSA_260, k, m, dps)
        print(f"  m={m:+.3f}: p has {len(str(p))} digits")
        assert isinstance(p, int), "Not an integer"
        assert 0 < p < RSA_260, "Out of range"
    
    print("✓ Comb formula validated")
    print()


def main():
    """Run all validations."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "RSA-260 Setup Validation" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    try:
        validate_rsa260_constant()
        validate_center_fixed()
        validate_high_precision()
        validate_fractional_m_sampling()
        validate_distance_ranking()
        validate_deterministic_prp()
        validate_comb_formula()
        
        print("=" * 80)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 80)
        print()
        print("The RSA-260 factorization setup meets all requirements:")
        print("  1. ✓ RSA-260 constant (260 digits, 862 bits)")
        print("  2. ✓ Center fixed at log(N)/2")
        print("  3. ✓ High precision (dps≥1000)")
        print("  4. ✓ Fractional m sampling")
        print("  5. ✓ Distance-based ranking")
        print("  6. ✓ Deterministic PRP")
        print("  7. ✓ Comb formula precision")
        print()
        print("Ready to run: python3 python/rsa260_repro.py")
        print()
        
        return 0
        
    except AssertionError as e:
        print()
        print("=" * 80)
        print("VALIDATION FAILED ✗")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
