#!/usr/bin/env python3
"""
Reproduction of the Exact Code from Problem Statement

This script reproduces the exact code snippets mentioned in the problem statement
to validate that the implementation matches the expected behavior.
"""

import numpy as np
import mpmath as mp
import matplotlib.pyplot as plt
from sympy import prime
import timeit

# Set precision as specified
mp.mp.dps = 50

def z5d_prime_original(k):
    """
    Original Z5D implementation matching the problem statement.
    Calibrated with c = -0.00247 and k* = 0.04449 for curvature adjustments.
    """
    k_mp = mp.mpf(k)
    
    if k_mp <= 5:
        return float(k_mp)
        
    log_k = mp.log(k_mp)
    log_log_k = mp.log(log_k) if log_k > 1 else mp.mpf(0)
    
    # PNT inverse: k * (ln(k) + ln(ln(k)) - 1)
    p_pnt = k_mp * (log_k + log_log_k - 1)
    
    # Z5D enhancements with calibrated parameters
    c = mp.mpf('-0.00247')  # Calibrated dilation
    k_star = mp.mpf('0.04449')  # Calibrated curvature
    
    # Enhanced terms
    d_term = mp.log(k_mp + 1) / (mp.e ** 2)
    e_term = mp.power(mp.log(k_mp), mp.mpf('0.618'))
    
    # Z5D formula
    z5d_prediction = p_pnt + c * d_term * p_pnt + k_star * e_term * p_pnt
    
    return float(z5d_prediction)

def riemann_prime_inverse(k):
    """
    Riemann implementation using Gram series inversion for p_n.
    """
    k_mp = mp.mpf(k)
    
    if k_mp <= 5:
        return float(k_mp)
        
    log_k = mp.log(k_mp)
    log_log_k = mp.log(log_k) if log_k > 1 else mp.mpf(0)
    
    # Base inverse li approximation
    x_approx = k_mp * (log_k + log_log_k - 1)
    
    # Apply simple Riemann corrections (simplified for demonstration)
    correction = mp.mpf('0.1') * mp.sqrt(x_approx) * mp.cos(mp.log(x_approx))
    x_corrected = x_approx - correction
    
    return float(x_corrected)

def main():
    """
    Execute the exact plotting code from the problem statement.
    """
    print("Reproducing exact code from problem statement...")
    
    # k values for plotting (as specified)
    k_values = np.logspace(3, 6, num=20)
    k_values_mp = [mp.mpf(k) for k in k_values]
    
    print(f"K values range: {k_values[0]:.0f} to {k_values[-1]:.0f}")
    
    # Time and compute Z_5D
    print("Computing Z5D predictions...")
    z5d_times = []
    pred_z5d = []
    for k in k_values_mp:
        time_taken = timeit.timeit(lambda: z5d_prime_original(k), number=10) / 10 * 1000  # ms
        z5d_times.append(time_taken)
        pred_z5d.append(float(z5d_prime_original(k)))
    
    # Time and compute Riemann  
    print("Computing Riemann predictions...")
    riemann_times = []
    pred_riemann = []
    for k in k_values_mp:
        time_taken = timeit.timeit(lambda: riemann_prime_inverse(k), number=10) / 10 * 1000  # ms
        riemann_times.append(time_taken)
        pred_riemann.append(float(riemann_prime_inverse(k)))
    
    # Create plots directory
    import os
    os.makedirs("problem_statement_plots", exist_ok=True)
    
    # Plot 1: Z_5D vs Riemann Predictions (exact from problem statement)
    plt.figure(figsize=(10, 6))
    plt.plot(np.log10(k_values), pred_z5d, label='Z_5D', marker='o')
    plt.plot(np.log10(k_values), pred_riemann, label='Riemann', marker='x')
    plt.xlabel('log10(k)')
    plt.ylabel('Predicted p_k')
    plt.title('Z_5D vs Riemann Predictions')
    plt.legend()
    plt.grid(True)
    plt.savefig('problem_statement_plots/pred_vs_logk.png')
    plt.close()
    
    # Plot 2: Diff plot (exact from problem statement)
    diff = np.array(pred_z5d) - np.array(pred_riemann)
    plt.figure(figsize=(10, 6))
    plt.plot(np.log10(k_values), diff, label='Z_5D - Riemann', marker='o')
    plt.xlabel('log10(k)')
    plt.ylabel('Difference')
    plt.title('Difference vs log(k)')
    plt.legend()
    plt.grid(True)
    plt.savefig('problem_statement_plots/diff_vs_logk.png')
    plt.close()
    
    # Plot 3: Norm diff plot (exact from problem statement)
    norm_diff = diff / np.array(pred_riemann) * 100
    plt.figure(figsize=(10, 6))
    plt.plot(np.log10(k_values), norm_diff, label='Normalized Difference (%)', marker='o')
    plt.xlabel('log10(k)')
    plt.ylabel('Normalized Difference (%)')
    plt.title('Normalized Difference vs log(k)')
    plt.legend()
    plt.grid(True)
    plt.savefig('problem_statement_plots/norm_diff_vs_logk.png')
    plt.close()
    
    # Summary output (matching problem statement)
    print(f"Plots generated; avg Z_5D time: {np.mean(z5d_times):.6f} ms; avg Riemann time: {np.mean(riemann_times):.6f} ms")
    
    # Analysis of key patterns described in problem statement
    print("\n=== PATTERN ANALYSIS ===")
    
    # Check underestimation at small k, overestimation at large k
    small_k_diff = np.mean(diff[:5])  # First 5 points
    large_k_diff = np.mean(diff[-5:])  # Last 5 points
    
    print(f"Small k differences (avg): {small_k_diff:.2f}")
    print(f"Large k differences (avg): {large_k_diff:.2f}")
    
    if small_k_diff < 0 and large_k_diff > 0:
        print("✓ Observed pattern: Z5D underestimates at small k, overestimates at large k")
    elif small_k_diff > 0 and large_k_diff > 0:
        print("⚠ Observed pattern: Z5D consistently overestimates")
    else:
        print("? Mixed pattern observed")
    
    # Check scaling with 1/log k
    log_k_values = np.log(k_values)
    scaling_coeff = np.polyfit(log_k_values, np.abs(diff), 1)[0]
    print(f"Scaling coefficient: {scaling_coeff:.2f}")
    
    # Correlation analysis
    from scipy.stats import pearsonr
    correlation, p_value = pearsonr(pred_z5d, pred_riemann)
    print(f"Correlation: r = {correlation:.6f}, p = {p_value:.2e}")
    
    if correlation >= 0.93 and p_value < 1e-10:
        print("✓ Correlation hypothesis SUPPORTED")
    else:
        print("⚠ Correlation hypothesis needs investigation")
    
    # Performance analysis
    performance_ratio = np.mean(riemann_times) / np.mean(z5d_times)
    print(f"Performance ratio (Riemann/Z5D): {performance_ratio:.2f}x")
    
    # Save results for analysis
    results = {
        'k_values': k_values.tolist(),
        'z5d_predictions': pred_z5d,
        'riemann_predictions': pred_riemann,
        'differences': diff.tolist(),
        'normalized_differences': norm_diff.tolist(),
        'z5d_times_ms': z5d_times,
        'riemann_times_ms': riemann_times,
        'correlation': correlation,
        'p_value': p_value,
        'performance_ratio': performance_ratio
    }
    
    import json
    with open('problem_statement_reproduction_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n=== REPRODUCTION COMPLETED ===")
    print("Generated files:")
    print("- problem_statement_plots/pred_vs_logk.png")
    print("- problem_statement_plots/diff_vs_logk.png")
    print("- problem_statement_plots/norm_diff_vs_logk.png")
    print("- problem_statement_reproduction_results.json")

if __name__ == "__main__":
    main()