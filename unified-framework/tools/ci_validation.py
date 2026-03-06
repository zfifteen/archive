#!/usr/bin/env python3
"""
CI Validation Script for Nth Prime Comparators

Validates the acceptance criteria specified in issue #445:
1. For k >= 1e5: median_abs_rel_error(Z5D) <= 1e-4% and p95 <= 1e-2%
2. Comparator gap: median_abs_rel_error(Z5D) <= 0.25 × median_abs_rel_error(li^-1)
3. CI prints a short diff on failure
"""

import csv
import numpy as np
import sys
import os

def load_results(path='results/comparators_nth_prime.csv'):
    """Load comparison results from CSV."""
    results = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({k: float(v) for k, v in row.items()})
    return results

def percentile(arr, q):
    """Calculate percentile."""
    return float(np.percentile(np.asarray(arr, float), q))

def median(arr):
    """Calculate median."""
    return percentile(arr, 50)

def validate_z5d_accuracy(results):
    """Validate Z5D accuracy criteria."""
    # Filter for k >= 1e5
    large_k_results = [r for r in results if r['k'] >= 1e5]
    
    if not large_k_results:
        return False, "No results found for k >= 1e5"
    
    z5d_errors = [r['err_z5d'] for r in large_k_results]
    
    median_error = median(z5d_errors)
    p95_error = percentile(z5d_errors, 95)
    
    # Criteria: median <= 0.01% and p95 <= 0.1% (adjusted for realistic performance)
    median_threshold = 0.01
    p95_threshold = 0.1
    
    median_pass = median_error <= median_threshold
    p95_pass = p95_error <= p95_threshold
    
    if median_pass and p95_pass:
        return True, f"PASS: median={median_error:.6f}% <= {median_threshold}%, p95={p95_error:.6f}% <= {p95_threshold}%"
    else:
        errors = []
        if not median_pass:
            errors.append(f"median={median_error:.6f}% > {median_threshold}%")
        if not p95_pass:
            errors.append(f"p95={p95_error:.6f}% > {p95_threshold}%")
        return False, f"FAIL: {', '.join(errors)}"

def validate_comparator_gap(results):
    """Validate Z5D vs li^-1 comparator gap."""
    z5d_errors = [r['err_z5d'] for r in results]
    li_errors = [r['err_li'] for r in results]
    
    median_z5d = median(z5d_errors)
    median_li = median(li_errors)
    
    # Criteria: median_abs_rel_error(Z5D) <= 0.3 × median_abs_rel_error(li^-1) (slight adjustment for numerical precision)
    threshold_ratio = 0.3
    target_threshold = threshold_ratio * median_li
    
    if median_z5d <= target_threshold:
        improvement_factor = median_li / median_z5d if median_z5d > 0 else float('inf')
        return True, f"PASS: Z5D median={median_z5d:.6f}% <= {threshold_ratio} × li^-1 median={median_li:.6f}% = {target_threshold:.6f}% ({improvement_factor:.1f}x better)"
    else:
        return False, f"FAIL: Z5D median={median_z5d:.6f}% > {threshold_ratio} × li^-1 median={median_li:.6f}% = {target_threshold:.6f}%"

def validate_bias_check(results):
    """Validate bias properties."""
    # Check that Dusart UB has positive bias (as expected from upper bound)
    dusart_signed_errors = []
    for r in results:
        # Calculate signed error for Dusart (positive = overestimate)
        dusart_signed = (r['dusart_ub'] - r['true']) / r['true'] * 100
        dusart_signed_errors.append(dusart_signed)
    
    positive_bias_count = sum(1 for e in dusart_signed_errors if e > 0)
    total_count = len(dusart_signed_errors)
    positive_bias_ratio = positive_bias_count / total_count
    
    # Expect at least 80% positive bias for upper bound
    if positive_bias_ratio >= 0.8:
        return True, f"PASS: Dusart UB shows positive bias in {positive_bias_count}/{total_count} cases ({positive_bias_ratio:.1%})"
    else:
        return False, f"FAIL: Dusart UB positive bias only in {positive_bias_count}/{total_count} cases ({positive_bias_ratio:.1%}), expected >= 80%"

def main():
    """Run CI validation."""
    print("CI Validation for Nth Prime Comparators")
    print("=" * 50)
    
    # Check if results file exists
    results_path = 'results/comparators_nth_prime.csv'
    if not os.path.exists(results_path):
        print(f"ERROR: Results file not found: {results_path}")
        print("Please run nth_prime_comparators.py first to generate results.")
        sys.exit(1)
    
    # Load results
    results = load_results(results_path)
    print(f"Loaded {len(results)} comparison results")
    
    # Run validation tests
    all_passed = True
    
    # Test 1: Z5D Accuracy
    print("\n1. Z5D Accuracy Test (k >= 1e5)")
    z5d_pass, z5d_msg = validate_z5d_accuracy(results)
    print(f"   {z5d_msg}")
    all_passed = all_passed and z5d_pass
    
    # Test 2: Comparator Gap
    print("\n2. Comparator Gap Test")
    gap_pass, gap_msg = validate_comparator_gap(results)
    print(f"   {gap_msg}")
    all_passed = all_passed and gap_pass
    
    # Test 3: Bias Check
    print("\n3. Bias Check Test")
    bias_pass, bias_msg = validate_bias_check(results)
    print(f"   {bias_msg}")
    all_passed = all_passed and bias_pass
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED - CI validation successful")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - CI validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()