#!/usr/bin/env python3
"""
Wiener Attack Demonstration - Convergent Selectivity in Practice

This example demonstrates:
1. Successful attack on vulnerable RSA (small d)
2. Failed attack on resistant RSA (large d)
3. Fractional bias scanning efficiency
4. Convergent termination patterns
5. Golden ratio defense

Educational/Research Purpose Only

Run from repository root:
    PYTHONPATH=python python3 python/examples/wiener_attack_demo.py
"""

import sys
sys.path.append("../")
sys.path.append(".")

import math
from wiener_attack import (
    ContinuedFraction,
    WienerAttack,
    GoldenRatioDefense
)


def to_int(value):
    """Convert sympy or other objects to int safely."""
    if hasattr(value, '__int__'):
        return int(value)
    return value


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def demo_vulnerable_rsa():
    """Demonstrate successful Wiener attack on vulnerable RSA."""
    print_section("Demo 1: Wiener Attack on Vulnerable RSA")
    
    # Generate vulnerable RSA parameters
    p = 857
    q = 1009
    N = p * q
    phi_N = (p - 1) * (q - 1)
    
    # Small d - vulnerable to Wiener attack
    d = 17
    e = pow(d, -1, phi_N)
    
    print(f"\nRSA Parameters:")
    print(f"  p = {p}")
    print(f"  q = {q}")
    print(f"  N = p·q = {N}")
    print(f"  φ(N) = (p-1)(q-1) = {phi_N}")
    print(f"  d = {d} (private exponent)")
    print(f"  e = {e} (public exponent)")
    
    # Check Wiener condition
    threshold = (1/3) * (N ** 0.25)
    print(f"\nWiener Attack Condition:")
    print(f"  N^(1/4) = {N**0.25:.2f}")
    print(f"  (1/3)·N^(1/4) = {threshold:.2f}")
    print(f"  d = {d}")
    print(f"  d < (1/3)·N^(1/4)? {d < threshold} {'✓ VULNERABLE' if d < threshold else '✗ SAFE'}")
    
    # Perform attack
    print(f"\nPerforming Wiener Attack...")
    attacker = WienerAttack(verbose=False, enable_bias_scanning=True)
    result = attacker.attack(e, N)
    
    if result:
        p_found, q_found = result
        print(f"\n✓ ATTACK SUCCESSFUL!")
        print(f"  Recovered: p = {p_found}, q = {q_found}")
        print(f"  Verification: {p_found} × {q_found} = {p_found * q_found}")
        print(f"  Match: {p_found * q_found == N}")
        print(f"  Convergents tested: {attacker.stats['convergents_tested']}")
        print(f"  Attack efficiency: Found in first {attacker.stats['convergents_tested']} convergents")
    else:
        print(f"\n✗ Attack failed")


def demo_resistant_rsa():
    """Demonstrate failed attack on resistant RSA."""
    print_section("Demo 2: Wiener Attack on Resistant RSA")
    
    # Generate resistant RSA parameters
    p = 857
    q = 1009
    N = p * q
    phi_N = (p - 1) * (q - 1)
    
    # Large d - resistant to Wiener attack
    d = 123457
    MAX_ITERATIONS = 1000
    iterations = 0
    while math.gcd(d, phi_N) != 1:
        d += 2
        iterations += 1
        if iterations > MAX_ITERATIONS:
            print(f"\n⚠️ Could not find coprime d, skipping test")
            return
    e = pow(d, -1, phi_N)
    
    print(f"\nRSA Parameters:")
    print(f"  N = {N}")
    print(f"  d = {d} (private exponent)")
    print(f"  e = {e} (public exponent)")
    
    # Check Wiener condition
    threshold = (1/3) * (N ** 0.25)
    print(f"\nWiener Attack Condition:")
    print(f"  (1/3)·N^(1/4) = {threshold:.2f}")
    print(f"  d = {d}")
    print(f"  d < (1/3)·N^(1/4)? {d < threshold} {'✓ VULNERABLE' if d < threshold else '✗ SAFE'}")
    
    # Perform attack
    print(f"\nPerforming Wiener Attack...")
    attacker = WienerAttack(verbose=False)
    result = attacker.attack(e, N)
    
    if result:
        print(f"\n✓ Attack succeeded (unexpected!)")
    else:
        print(f"\n✗ ATTACK FAILED (as expected)")
        print(f"  Convergents tested: {attacker.stats['convergents_tested']}")
        print(f"  Reason: d too large for Wiener attack")


def demo_bias_scanning():
    """Demonstrate fractional bias scanning efficiency."""
    print_section("Demo 3: Fractional Bias Scanning Efficiency")
    
    # Use parameters that will trigger bias scanning
    p = 857
    q = 1009
    N = p * q
    phi_N = (p - 1) * (q - 1)
    
    # Use a value that creates interesting quotient patterns
    d = 17
    e = pow(d, -1, phi_N)
    
    print(f"\nTesting e = {e}, N = {N}")
    
    # Get continued fraction for analysis
    quotients = ContinuedFraction.quotients(e, N, max_terms=20)
    print(f"\nContinued Fraction Quotients (first 15):")
    print(f"  {quotients[:15]}")
    
    # Test with different thresholds
    thresholds = [10, 50, 100, 500, 1000]
    
    print(f"\nBias Scanning with Different Thresholds:")
    print(f"  {'Threshold':<12} {'Tested':<10} {'Skipped':<10} {'Efficiency':<12}")
    print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*12}")
    
    for threshold in thresholds:
        attacker = WienerAttack(
            max_quotient_threshold=threshold,
            enable_bias_scanning=True,
            verbose=False
        )
        result = attacker.attack(e, N)
        
        tested = attacker.stats['convergents_tested']
        skipped = attacker.stats['convergents_skipped']
        total = tested + skipped
        efficiency = f"{(skipped/total*100):.1f}%" if total > 0 else "N/A"
        
        print(f"  {threshold:<12} {tested:<10} {skipped:<10} {efficiency:<12}")
    
    # Compare bias scanning vs full search
    print(f"\nComparison: Bias Scanning ON vs OFF")
    
    attacker_on = WienerAttack(enable_bias_scanning=True, verbose=False)
    attacker_on.attack(e, N)
    
    attacker_off = WienerAttack(enable_bias_scanning=False, verbose=False)
    attacker_off.attack(e, N)
    
    print(f"  Bias scanning ON:  {attacker_on.stats['convergents_tested']} convergents tested")
    print(f"  Bias scanning OFF: {attacker_off.stats['convergents_tested']} convergents tested")
    
    if attacker_off.stats['convergents_tested'] > 0:
        speedup = attacker_off.stats['convergents_tested'] / max(1, attacker_on.stats['convergents_tested'])
        print(f"  Speedup: {speedup:.2f}x")


def demo_convergent_patterns():
    """Demonstrate convergent termination patterns."""
    print_section("Demo 4: Convergent Termination Patterns")
    
    # Create example with interesting quotient pattern
    e = 659825
    N = 864713
    
    print(f"\nAnalyzing e/N = {e}/{N}")
    
    # Get continued fraction
    quotients = ContinuedFraction.quotients(e, N, max_terms=20)
    convergents = ContinuedFraction.convergents(e, N, max_terms=20)
    
    print(f"\nContinued Fraction Expansion:")
    print(f"  Quotients: {quotients[:12]}")
    
    # Analyze convergents
    print(f"\nConvergent Analysis (first 10):")
    print(f"  {'Index':<8} {'k/d':<20} {'Quotient':<12} {'Denom Growth':<15}")
    print(f"  {'-'*8} {'-'*20} {'-'*12} {'-'*15}")
    
    for i in range(min(10, len(convergents))):
        k, d = convergents[i]
        # Convert to int to avoid sympy formatting issues
        k = to_int(k)
        d = to_int(d)
        quotient = quotients[i] if i < len(quotients) else 'N/A'
        quotient = to_int(quotient) if quotient != 'N/A' else quotient
        
        if i > 0 and convergents[i-1][1] > 0:
            growth = d / to_int(convergents[i-1][1])
            growth_str = f"{growth:.2f}x"
        else:
            growth_str = "---"
        
        # Highlight large quotients
        quotient_str = str(quotient)
        if isinstance(quotient, int) and quotient > 100:
            quotient_str = f"{quotient} ⚠️"
        
        print(f"  {i:<8} {k}/{d:<18} {quotient_str:<12} {growth_str:<15}")
    
    # Demonstrate the "5911 pattern" concept
    print(f"\nThe '5911 Pattern' Concept:")
    print(f"  In practice, convergents before anomalously large quotients")
    print(f"  are the most efficient candidates for testing.")
    print(f"  Example from literature: [0;2,1,9,6,54,5911,...]")
    print(f"  Practitioners stop before 5911 - too large to be efficient.")


def demo_vulnerability_analysis():
    """Demonstrate vulnerability analysis."""
    print_section("Demo 5: Vulnerability Analysis")
    
    # Test multiple parameter sets
    test_cases = [
        ("Vulnerable", 857, 1009, 17),
        ("Borderline", 857, 1009, 29),
        ("Resistant", 857, 1009, 123457),
    ]
    
    print(f"\n{'Case':<15} {'d':<10} {'N^(1/4)':<10} {'Vuln Score':<12} {'Status':<15}")
    print(f"{'-'*15} {'-'*10} {'-'*10} {'-'*12} {'-'*15}")
    
    attacker = WienerAttack()
    
    for case_name, p, q, d in test_cases:
        N = p * q
        phi_N = (p - 1) * (q - 1)
        
        # Ensure d is coprime to phi_N (with safety limit)
        MAX_ITERATIONS = 1000
        iterations = 0
        while math.gcd(d, phi_N) != 1:
            d += 1
            iterations += 1
            if iterations > MAX_ITERATIONS:
                print(f"  Skipping {case_name}: could not find coprime d")
                continue
        
        e = pow(d, -1, phi_N)
        
        analysis = attacker.analyze_vulnerability(e, N)
        score = analysis['vulnerability_score']
        n_fourth = N ** 0.25
        
        # Determine status
        if d < n_fourth / 3:
            status = "VULNERABLE ⚠️"
        elif d < n_fourth:
            status = "BORDERLINE ⚡"
        else:
            status = "SAFE ✓"
        
        print(f"{case_name:<15} {d:<10} {n_fourth:<10.2f} {score:<12.2f} {status:<15}")
    
    # Detailed analysis for one case
    print(f"\nDetailed Analysis for Vulnerable Case:")
    p, q, d = 857, 1009, 17
    N = p * q
    phi_N = (p - 1) * (q - 1)
    e = pow(d, -1, phi_N)
    
    analysis = attacker.analyze_vulnerability(e, N)
    
    for key, value in analysis.items():
        print(f"  {key}: {value}")


def demo_golden_ratio_defense():
    """Demonstrate golden ratio-based defense."""
    print_section("Demo 6: Golden Ratio Defense")
    
    print("\nGolden Ratio φ Properties:")
    print(f"  φ = (1 + √5)/2 ≈ {(1 + math.sqrt(5))/2:.10f}")
    print(f"  Continued fraction: [1; 1, 1, 1, 1, ...]")
    print(f"  All quotients = 1 (maximally poor approximations)")
    
    # Demonstrate Fibonacci convergents approaching φ
    print(f"\nFibonacci Ratios (convergents of φ):")
    fib = [1, 1]
    for _ in range(8):
        fib.append(fib[-1] + fib[-2])
    
    print(f"  {'F(n+1)/F(n)':<15} {'Value':<12} {'Error from φ':<15}")
    print(f"  {'-'*15} {'-'*12} {'-'*15}")
    
    phi = (1 + math.sqrt(5)) / 2
    for i in range(1, min(8, len(fib)-1)):
        ratio = fib[i+1] / fib[i]
        error = abs(ratio - phi)
        print(f"  F({i+1})/F({i}):{'':<6} {ratio:<12.8f} {error:<15.10f}")
    
    # Test resistance checking
    print(f"\nTesting Resistance Properties:")
    
    N = 864713
    phi_N = 862848
    
    # Generate φ-resistant exponent
    e_phi = GoldenRatioDefense.generate_phi_resistant_exponent(N, min_bits=16)
    print(f"  Generated φ-resistant e: {e_phi}")
    
    # Compare different exponents
    test_exponents = [
        ("Standard (65537)", 65537),
        ("φ-resistant", e_phi),
        ("Small (vulnerable)", 659825),  # From earlier vulnerable example
    ]
    
    print(f"\n  {'Type':<25} {'Resistant?':<15}")
    print(f"  {'-'*25} {'-'*15}")
    
    for name, e in test_exponents:
        if math.gcd(e, N) == 1:  # Valid exponent
            is_resistant = GoldenRatioDefense.is_phi_resistant(e, N, threshold=1000)
            status = "✓ Yes" if is_resistant else "✗ No"
            print(f"  {name:<25} {status:<15}")
        else:
            print(f"  {name:<25} {'N/A (invalid)':<15}")


def main():
    """Run all demonstrations."""
    print("=" * 70)
    print("WIENER ATTACK DEMONSTRATION")
    print("Convergent Selectivity in Continued Fraction Cryptanalysis")
    print("Educational/Research Purpose Only")
    print("=" * 70)
    
    demos = [
        demo_vulnerable_rsa,
        demo_resistant_rsa,
        demo_bias_scanning,
        demo_convergent_patterns,
        demo_vulnerability_analysis,
        demo_golden_ratio_defense,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n✗ Error in {demo.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Wiener attack works when d < (1/3)·N^(1/4)")
    print("  2. Fractional bias scanning improves efficiency")
    print("  3. Large quotients signal early termination opportunities")
    print("  4. Golden ratio φ provides cryptographic resistance")
    print("  5. Modern RSA uses large d - inherently resistant")
    print("\nFor more info: docs/methods/other/WIENER_ATTACK.md")


if __name__ == "__main__":
    main()
