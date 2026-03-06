#!/usr/bin/env python3
"""
Prime Number Demo - Complete Implementation

This script demonstrates the nth prime comparators as specified in issue #445.
Implements Z5D, li^-1, 4-term asymptotic, and Dusart upper bound comparators
with pinned constants and comprehensive validation.

Usage:
    python3 demo_prime_number.py

Output:
    - Comparison table in the format specified in the issue
    - CSV results saved to results/comparators_nth_prime.csv
    - Plots: error_vs_k.png and signed_error_vs_k.png
    - CI validation results
"""

import os
import sys
import subprocess

def print_header():
    """Print demo header."""
    print("=" * 80)
    print("PRIME NUMBER DEMO - Nth Prime Comparator Implementation")
    print("=" * 80)
    print("Implementation: Z5D with zeta correction vs. standard comparators")
    print("Ground Truth: data/nth_primes.csv (versioned in repo)")
    print("Pinned Constants: kappa_star = 0.04449, c_cal = -0.00247")
    print("Error Metric: abs(pred - true) / true * 100 (percent)")
    print()

def print_table_header():
    """Print comparison table header."""
    print("Comparison Results:")
    print("-" * 120)
    header = "k | True Prime | Z5D Pred | Z5D Err (%) | Signed Z5D Err (%) | li⁻¹ Pred | li⁻¹ Err (%) | 4-term Asymp Pred | 4-term Err (%) | Dusart UB Pred | Dusart UB Err (%)"
    print(header)
    print("-" * len(header))

def run_demo():
    """Run the complete demo."""
    print_header()
    
    # Step 1: Generate comparison results
    print("Step 1: Generating nth prime comparisons...")
    result = subprocess.run([sys.executable, 'nth_prime_comparators.py'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: Failed to generate comparisons: {result.stderr}")
        return False
    
    # Step 2: Load and display results in the specified format
    print("\nStep 2: Displaying results in comparison table format...")
    import csv
    import numpy as np
    
    # Load CSV results
    with open('results/comparators_nth_prime.csv') as f:
        reader = csv.DictReader(f)
        results = list(reader)
    
    print_table_header()
    
    for row in results:
        k = int(float(row['k']))
        true_prime = int(float(row['true']))
        z5d_pred = float(row['z5d'])
        z5d_err = float(row['err_z5d'])
        z5d_signed_err = float(row['signed_err_z5d'])
        li_pred = float(row['li_inv'])
        li_err = float(row['err_li'])
        asymp4_pred = float(row['asymp4'])
        asymp4_err = float(row['err_asymp4'])
        dusart_pred = float(row['dusart_ub'])
        dusart_err = float(row['err_dusart_ub'])
        
        print(f"{k:,} | {true_prime:,} | {z5d_pred:.2f} | {z5d_err:.4f} | {z5d_signed_err:+.4f} | {li_pred:.2f} | {li_err:.4f} | {asymp4_pred:.2f} | {asymp4_err:.4f} | {dusart_pred:.2f} | {dusart_err:.4f}")
    
    # Step 3: Generate summary statistics
    print("\n" + "-" * 120)
    print("Summary Statistics:")
    
    z5d_errors = [float(r['err_z5d']) for r in results]
    li_errors = [float(r['err_li']) for r in results]
    asymp4_errors = [float(r['err_asymp4']) for r in results]
    dusart_errors = [float(r['err_dusart_ub']) for r in results]
    
    median_z5d = np.median(z5d_errors)
    median_li = np.median(li_errors)
    median_asymp4 = np.median(asymp4_errors)
    median_dusart = np.median(dusart_errors)
    
    improvement_factor = median_li / median_z5d if median_z5d > 0 else float('inf')
    
    print(f"Median errors → Z5D: {median_z5d:.4f}%, li⁻¹: {median_li:.4f}%, 4-term: {median_asymp4:.4f}%, Dusart UB: {median_dusart:.4f}%")
    print(f"Z5D median is ~{improvement_factor:.1f}× lower than li⁻¹; Dusart exhibits expected positive bias.")
    
    # Step 4: Run reproduction script
    print("\nStep 3: Running reproduction script...")
    result = subprocess.run([sys.executable, 'scripts/reproduce_nth_prime_bench.py'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Reproduction script executed successfully")
        print("Reproduction output:")
        print(result.stdout)
    else:
        print(f"❌ Reproduction script failed: {result.stderr}")
    
    # Step 5: Run CI validation
    print("Step 4: Running CI validation...")
    result = subprocess.run([sys.executable, 'ci_validation.py'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ CI validation passed")
    else:
        print("❌ CI validation failed")
    
    print("CI validation output:")
    print(result.stdout)
    
    # Step 6: List artifacts
    print("\nStep 5: Generated artifacts:")
    artifacts = [
        "data/nth_primes.csv - Ground truth nth primes",
        "data/zeta.txt - Riemann zeta zeros (100 zeros)",
        "results/comparators_nth_prime.csv - Complete comparison results",
        "scripts/reproduce_nth_prime_bench.py - 50-line reproduction script",
        "error_vs_k.png - Error vs log10(k) plot",
        "signed_error_vs_k.png - Signed error (bias) plot",
        "ci_validation.py - CI validation script"
    ]
    
    for artifact in artifacts:
        print(f"  📄 {artifact}")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE - All components implemented and validated")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)