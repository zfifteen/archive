#!/usr/bin/env python3
"""
Simplified Zeta Zero Cycling Test

This script tests the specific hypothesis mentioned in the issue more directly,
focusing on the interpretation that "cycle 1-5" means cycling through zeros 1-5
while "alt 2-4" means alternating between zeros 2 and 4.
"""

import mpmath as mp
mp.mp.dps = 50
import numpy as np
from scipy import stats
import csv

def load_zeta_zeros():
    """Load first 10 zeta zeros from CSV."""
    zeros = []
    try:
        with open("tests/zeta_zeros.csv", 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if i >= 10:  # Only need first 10
                    break
                zeros.append(mp.mpf(row[0]))
    except:
        # Fallback to hardcoded
        zeros = [
            mp.mpf('14.134725141734695'),
            mp.mpf('21.022039638771556'), 
            mp.mpf('25.01085758014569'),
            mp.mpf('30.424876125859512'),
            mp.mpf('32.93506158773919'),
            mp.mpf('37.586178158825675'),
            mp.mpf('40.9187190121475'),
            mp.mpf('43.327073280915'),
            mp.mpf('48.00515088116716'),
            mp.mpf('49.7738324776723')
        ]
    return zeros

def z5d_pi_with_selected_zeros(x, selected_zeros):
    """Calculate π(x) using only the selected zeta zeros."""
    x_mp = mp.mpf(x)
    
    # Base Li function 
    base = mp.li(x_mp)
    
    # Zeta zero corrections
    correction = mp.mpf('0')
    for gamma in selected_zeros:
        omega = gamma * mp.log(x_mp) / (2 * mp.pi)
        amplitude = mp.sqrt(x_mp) / (mp.pi * gamma)
        oscillation = amplitude * mp.cos(omega)
        correction += oscillation
    
    result = base - correction - mp.log(2)
    return float(result)

def cycle_1_5_strategy(zeros):
    """
    Cycle 1-5 strategy: Uses zeros 1, 2, 3, 4, 5 in a cycling pattern.
    This leverages phase dithering across multiple zeros.
    """
    return zeros[:5]  # Use first 5 zeros

def alt_2_4_strategy(zeros):
    """
    Alt 2-4 strategy: Alternates between zeros 2 and 4 only.
    More limited oscillatory pattern.
    """
    return [zeros[1], zeros[3]]  # Use 2nd and 4th zeros only

def inverse_pi_newton(target_k, selected_zeros, max_iter=10):
    """
    Find x such that π(x) ≈ target_k using Newton's method.
    """
    # Initial guess using inverse PNT approximation
    k_mp = mp.mpf(target_k)
    x = k_mp * mp.log(k_mp)
    
    for i in range(max_iter):
        pi_x = z5d_pi_with_selected_zeros(x, selected_zeros)
        error = pi_x - float(k_mp)
        
        if abs(error) < 1:
            break
            
        # Derivative approximation: dπ/dx ≈ 1/ln(x)
        derivative = 1.0 / float(mp.log(x))
        x_new = x - error / derivative
        
        # Ensure x stays positive and reasonable
        if x_new <= 0:
            x_new = x * 0.9
        x = x_new
        
    return float(x)

def test_hypothesis_at_k_values(zeros, k_values):
    """Test the cycling hypothesis at various k values."""
    print("Testing Zeta Zero Cycling Strategies")
    print("="*45)
    print(f"Available zeros: {len(zeros)}")
    print(f"First 5 zeros: {[float(z) for z in zeros[:5]]}")
    print()
    
    results = []
    
    print(f"{'k':>10} {'True π(k)':>12} {'Cycle 1-5':>12} {'Alt 2-4':>12} {'Err1-5%':>10} {'Err2-4%':>10} {'Reduction%':>12}")
    print("-" * 90)
    
    for k in k_values:
        # True values (approximate)
        true_pi_k = {
            1000: 168,
            10000: 1229,
            100000: 9592,
            1000000: 78498,
            1500000: 120566,
            2000000: 148933,
            3000000: 216816,
            5000000: 348513,
            10000000: 664579
        }.get(k, k // 15)  # Rough approximation if not in table
        
        # Strategy implementations
        cycle_zeros = cycle_1_5_strategy(zeros)
        alt_zeros = alt_2_4_strategy(zeros)
        
        # Calculate predictions (inverse π function)
        pred_cycle = inverse_pi_newton(true_pi_k, cycle_zeros)
        pred_alt = inverse_pi_newton(true_pi_k, alt_zeros)
        
        # Calculate errors
        err_cycle = abs(pred_cycle - k) / k * 100
        err_alt = abs(pred_alt - k) / k * 100
        
        # Error reduction
        reduction = (err_alt - err_cycle) / err_alt * 100 if err_alt > 0 else 0
        
        results.append({
            'k': k,
            'true_pi_k': true_pi_k,
            'pred_cycle': pred_cycle,
            'pred_alt': pred_alt,
            'err_cycle': err_cycle,
            'err_alt': err_alt,
            'reduction': reduction
        })
        
        print(f"{k:>10} {true_pi_k:>12} {pred_cycle:>12.0f} {pred_alt:>12.0f} {err_cycle:>10.4f} {err_alt:>10.4f} {reduction:>12.4f}")
    
    return results

def main():
    """Main test function."""
    zeros = load_zeta_zeros()
    
    # Test at various k values including k > 10^6
    k_values = [1000, 10000, 100000, 1000000, 1500000, 2000000, 3000000, 5000000, 10000000]
    
    results = test_hypothesis_at_k_values(zeros, k_values)
    
    # Focus on k > 10^6 results
    large_k_results = [r for r in results if r['k'] > 1000000]
    
    if large_k_results:
        print("\n" + "="*45)
        print("ANALYSIS FOR k > 10^6")
        print("="*45)
        
        reductions = [r['reduction'] for r in large_k_results]
        mean_reduction = np.mean(reductions)
        
        print(f"Number of k > 10^6 tests: {len(large_k_results)}")
        print(f"Mean error reduction: {mean_reduction:.4f}%")
        print(f"Min reduction: {min(reductions):.4f}%")
        print(f"Max reduction: {max(reductions):.4f}%")
        
        # Simple confidence interval using t-distribution
        if len(reductions) > 1:
            std_err = np.std(reductions) / np.sqrt(len(reductions))
            t_val = stats.t.ppf(0.975, len(reductions) - 1)  # 95% CI
            margin = t_val * std_err
            ci_lower = mean_reduction - margin
            ci_upper = mean_reduction + margin
            print(f"95% CI: [{ci_lower:.4f}%, {ci_upper:.4f}%]")
            
            # Test hypothesis
            hypothesis_met = mean_reduction > 3.0
            expected_ci = (2.5, 3.8)
            ci_overlap = ci_lower <= expected_ci[1] and ci_upper >= expected_ci[0]
            
            print(f"\nHypothesis Test:")
            print(f"Required: >3% reduction: {'✓' if hypothesis_met else '✗'}")
            print(f"Expected CI [2.5%, 3.8%]: {'✓' if ci_overlap else '✗'}")
            
            if hypothesis_met and ci_overlap:
                print("🎯 HYPOTHESIS CONFIRMED")
            else:
                print("❌ HYPOTHESIS NOT CONFIRMED")
        else:
            print("Insufficient data for statistical analysis")
    
    return results

if __name__ == "__main__":
    results = main()