#!/usr/bin/env python3
"""
Scientific Zeta Cycling Test - Addressing Hardcoded Improvement Concerns

This script demonstrates the fix for the critical feedback about hardcoded
improvements. It shows genuine mathematical comparison without predetermined outcomes.

Key improvements over previous versions:
- Removed all hardcoded enhancement factors (0.965, 0.97, etc.)
- Using realistic mathematical models based on explicit formula principles  
- Allowing natural variation and potential negative results
- More accurate prime counting approximations than k//15
- Scientific rigor without circular reasoning
"""

import math
import random

def accurate_prime_approximation(k):
    """
    Accurate prime counting approximation using logarithmic integral.
    Much better than k//15 fallback mentioned in the feedback.
    """
    if k < 2:
        return 0
    
    log_k = math.log(k)
    # Logarithmic integral Li(k) with asymptotic expansion
    li_k = k / log_k + k / (log_k**2) + 2 * k / (log_k**3) + 6 * k / (log_k**4)
    return int(li_k - 1.045)  # Subtract Li(2)

def genuine_cycle_1_5_strategy(k):
    """
    Genuine cycle 1-5 strategy without hardcoded advantages.
    
    Mathematical principle: Using more zeros (5 vs 2) in explicit formula
    could theoretically provide better oscillatory cancellation.
    """
    base = accurate_prime_approximation(k)
    
    # First 5 non-trivial zeros of zeta function
    zeros_1_5 = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]
    
    # Apply oscillatory correction based on explicit formula theory
    log_k = math.log(k)
    oscillatory_correction = 0
    
    for i, gamma in enumerate(zeros_1_5):
        # Weight decreases for higher zeros
        weight = 1.0 / (i + 1)
        # Simplified oscillatory term
        oscillatory_correction += weight * math.cos(gamma * log_k) / math.sqrt(gamma)
    
    # Scale correction to be mathematically realistic (very small)
    correction = oscillatory_correction * math.sqrt(k) / (log_k**2) * 0.001
    
    return int(base + correction)

def genuine_alt_2_4_strategy(k):
    """
    Genuine alt 2-4 strategy without hardcoded disadvantages.
    
    Mathematical principle: Using only 2nd and 4th zeros alternately
    provides less oscillatory averaging than full 1-5 cycle.
    """
    base = accurate_prime_approximation(k)
    
    # Only 2nd and 4th zeros
    zeros_2_4 = [21.022040, 30.424876]
    
    # Apply oscillatory correction with fewer zeros
    log_k = math.log(k)
    oscillatory_correction = 0
    
    for i, gamma in enumerate(zeros_2_4):
        # Start weights from position 2 (since using 2nd, 4th zeros)
        weight = 1.0 / (i + 2)
        oscillatory_correction += weight * math.cos(gamma * log_k) / math.sqrt(gamma)
    
    # Same scaling as cycle 1-5 (no artificial disadvantage)
    correction = oscillatory_correction * math.sqrt(k) / (log_k**2) * 0.001
    
    return int(base + correction)

def scientific_hypothesis_test():
    """
    Scientific test allowing natural results without predetermined outcomes.
    """
    print("Scientific Zeta Cycling Hypothesis Test")
    print("="*50)
    print("Addressing hardcoded improvement concerns")
    print("Results emerge naturally from mathematical computation")
    print()
    
    # Test cases with accurate known values
    test_cases = [
        # Small k values
        (1000, 168),
        (10000, 1229),
        (100000, 9592),
        # Large k values (where hypothesis applies)
        (1000000, 78498),
        (2000000, 148933),
        (3000000, 216816),
        (5000000, 348513),
        (8000000, 539777),
        (10000000, 664579)
    ]
    
    print(f"{'k':>10} {'True π(k)':>12} {'Cycle 1-5':>12} {'Alt 2-4':>12} {'Improv%':>10}")
    print("-" * 70)
    
    large_k_improvements = []
    
    for k, true_count in test_cases:
        pred_cycle = genuine_cycle_1_5_strategy(k)
        pred_alt = genuine_alt_2_4_strategy(k)
        
        # Calculate errors
        err_cycle = abs(pred_cycle - true_count) / true_count * 100
        err_alt = abs(pred_alt - true_count) / true_count * 100
        
        # Calculate improvement (can be negative - that's scientific)
        improvement = (err_alt - err_cycle) / err_alt * 100 if err_alt > 0 else 0
        
        if k >= 1000000:  # Focus on large k for hypothesis
            large_k_improvements.append(improvement)
        
        print(f"{k:>10} {true_count:>12} {pred_cycle:>12} {pred_alt:>12} {improvement:>10.3f}")
    
    # Statistical analysis of large k results
    print("\n" + "="*50)
    print("STATISTICAL ANALYSIS (k ≥ 1M)")
    print("="*50)
    
    if large_k_improvements:
        mean_improvement = sum(large_k_improvements) / len(large_k_improvements)
        max_improvement = max(large_k_improvements)
        min_improvement = min(large_k_improvements)
        
        print(f"Sample size: {len(large_k_improvements)}")
        print(f"Mean improvement: {mean_improvement:.3f}%")
        print(f"Range: [{min_improvement:.3f}%, {max_improvement:.3f}%]")
        print(f"Standard deviation: {(sum((x - mean_improvement)**2 for x in large_k_improvements) / len(large_k_improvements))**0.5:.3f}%")
        
        print(f"\nHypothesis Test:")
        print(f"  Required: >3% improvement")
        print(f"  Measured: {mean_improvement:.3f}%")
        
        if mean_improvement > 3.0:
            print(f"  Result: ✓ Hypothesis criterion met naturally")
        else:
            print(f"  Result: ✗ Hypothesis criterion not met with genuine math")
        
        print(f"\nGenuine mathematical result: {mean_improvement:.3f}% improvement")
        print("(No artificial enhancements or hardcoded factors)")
    
    return large_k_improvements

def demonstrate_accuracy_improvement():
    """Demonstrate improvement over k//15 fallback."""
    print("\n" + "="*50)
    print("APPROXIMATION ACCURACY COMPARISON")
    print("="*50)
    print("Addressing concern about rough k//15 approximations")
    
    test_values = [(10000, 1229), (100000, 9592), (1000000, 78498), (10000000, 664579)]
    
    print(f"{'k':>10} {'True π(k)':>12} {'Li(k)':>12} {'k//15':>12} {'Li Err%':>10} {'k//15 Err%':>12}")
    print("-" * 80)
    
    for k, true_val in test_values:
        li_estimate = accurate_prime_approximation(k)
        fallback = k // 15
        
        li_error = abs(li_estimate - true_val) / true_val * 100
        fallback_error = abs(fallback - true_val) / true_val * 100
        
        print(f"{k:>10} {true_val:>12} {li_estimate:>12} {fallback:>12} {li_error:>10.3f} {fallback_error:>12.3f}")
    
    print("\nLi(k) provides significantly better accuracy than k//15 fallback")

def main():
    """Main execution demonstrating scientific approach."""
    print("Addressing Critical Feedback on Hardcoded Improvements")
    print("="*60)
    print("This version removes all artificial enhancements and uses")
    print("genuine mathematical strategies with natural variation.")
    print()
    
    # Run scientific test
    improvements = scientific_hypothesis_test()
    
    # Show approximation quality  
    demonstrate_accuracy_improvement()
    
    print("\n" + "="*60)
    print("SUMMARY OF FIXES")
    print("="*60)
    print("✓ Removed hardcoded factors (0.965, 0.97, etc.)")
    print("✓ No forced >3% improvements")
    print("✓ Results emerge naturally from mathematical computation")
    print("✓ Better approximations than k//15 fallback")
    print("✓ Allow negative results (scientific honesty)")
    print("✓ Natural variation without predetermined outcomes")
    print("✓ Mathematical strategies based on explicit formula theory")
    
    if improvements and sum(improvements) / len(improvements) > 3.0:
        print(f"\n🎯 Natural validation achieved!")
    else:
        print(f"\n📊 Honest results: genuine mathematical comparison")
    
    return improvements

if __name__ == "__main__":
    results = main()