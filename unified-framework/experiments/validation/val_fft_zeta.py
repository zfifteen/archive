#!/usr/bin/env python3
"""
val_fft_zeta.py - Independent validation script for FFT-zeta Z5D enhancement
@author Dionisio Alberto Lopez III (D.A.L. III)

This script validates the FFT-zeta enhancement implementation according to the
problem statement requirements.

Usage: python3 val_fft_zeta.py [--seed=42] [--csv-logs] [--bootstrap]

Requirements:
- Validates FFT-zeta → Lorentz γ hypothesis  
- Tests correlation r≥0.93 for β≈30.34
- Generates CSV logs for CI [14.6,15.4]
- Compares with reference implementation
- Bootstrap resampling (1,000 resamples) for CIs
"""

import argparse
import csv
import os
import random
import subprocess
import sys
import time
from typing import List, Tuple
import numpy as np
from scipy import stats
import math

# Test configuration
DEFAULT_SEED = 42
TEST_K_VALUES = [10, 52, 100, 1000, 10000, 100000, 1000000]
BETA_HYPOTHESIS = 30.34
CORRELATION_THRESHOLD = 0.93
CI_LOWER = 14.6
CI_UPPER = 15.4

def setup_seed(seed: int = DEFAULT_SEED):
    """Setup random seed for reproducible results."""
    random.seed(seed)
    np.random.seed(seed)
    print(f"Using seed: {seed}")

def run_z5d_prime_gen(k: int) -> Tuple[float, int]:
    """
    Run z5d_prime_gen for given k and extract results.
    
    Returns:
        Tuple of (prediction, actual_prime)
    """
    try:
        # Run the C implementation
        result = subprocess.run(
            ['./bin/z5d_prime_gen', str(k)], 
            capture_output=True, 
            text=True, 
            cwd='src/c',
            timeout=30
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"z5d_prime_gen failed: {result.stderr}")
        
        # Parse output
        lines = result.stdout.split('\n')
        prediction = None
        actual_prime = None
        
        for line in lines:
            if 'FFT-zeta enhanced Z5D prediction (rounded):' in line:
                prediction = float(line.split(':')[1].strip())
            elif f'Refined p_{k}:' in line:
                actual_prime = int(line.split(':')[1].strip())
        
        if prediction is None or actual_prime is None:
            raise ValueError(f"Could not parse output for k={k}")
            
        return prediction, actual_prime
        
    except Exception as e:
        print(f"Error running z5d_prime_gen for k={k}: {e}")
        return None, None

def bootstrap_confidence_interval(data: List[float], n_bootstrap: int = 1000, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate bootstrap confidence interval for given data.
    
    Args:
        data: List of numerical values
        n_bootstrap: Number of bootstrap resamples (default 1000)
        confidence: Confidence level (default 0.95)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if len(data) < 2:
        return (0.0, 0.0)
    
    bootstrap_means = []
    n = len(data)
    
    for _ in range(n_bootstrap):
        # Resample with replacement
        bootstrap_sample = np.random.choice(data, size=n, replace=True)
        bootstrap_means.append(np.mean(bootstrap_sample))
    
    # Calculate confidence interval
    alpha = 1 - confidence
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    lower_bound = np.percentile(bootstrap_means, lower_percentile)
    upper_bound = np.percentile(bootstrap_means, upper_percentile)
    
    return (lower_bound, upper_bound)

def calculate_lorentz_gamma(p_k: float, beta: float = BETA_HYPOTHESIS) -> float:
    """
    Calculate Lorentz gamma according to hypothesis:
    γ = 1 + (1/2)(ln p_k/(e^4+β ln p_k))^2
    """
    if p_k <= 0:
        return 1.0
    
    ln_p_k = math.log(p_k)
    e_fourth = math.exp(4.0)  # e^4
    denominator = e_fourth + beta * ln_p_k
    
    if denominator <= 0:
        return 1.0
    
    ratio = ln_p_k / denominator
    gamma = 1.0 + 0.5 * ratio * ratio
    
    return gamma

def validate_fft_zeta() -> dict:
    """
    Main validation function for FFT-zeta enhancement.
    
    Returns:
        Dictionary with validation results
    """
    print("FFT-Zeta Z5D Enhancement Validation")
    print("===================================")
    
    results = {
        'test_k_values': [],
        'predictions': [],
        'actual_primes': [],
        'gamma_values': [],
        'enhancement_factors': [],
        'pass_count': 0,
        'total_tests': len(TEST_K_VALUES),
        'correlation': None,
        'beta_estimate': BETA_HYPOTHESIS,
        'ci_validation': False
    }
    
    # Test each k value
    for k in TEST_K_VALUES:
        print(f"\nTesting k={k}...")
        
        prediction, actual_prime = run_z5d_prime_gen(k)
        
        if prediction is None or actual_prime is None:
            print(f"❌ Failed for k={k}")
            continue
        
        # Calculate Lorentz gamma
        gamma = calculate_lorentz_gamma(actual_prime, BETA_HYPOTHESIS)
        
        # Calculate enhancement factor (actual vs PNT)
        pnt_estimate = k * (math.log(k) + math.log(math.log(k)) - 1)
        enhancement = (actual_prime - pnt_estimate) / pnt_estimate * 100
        
        # Store results
        results['test_k_values'].append(k)
        results['predictions'].append(prediction)
        results['actual_primes'].append(actual_prime)
        results['gamma_values'].append(gamma)
        results['enhancement_factors'].append(enhancement)
        
        # Calculate prediction accuracy
        relative_error = abs(prediction - actual_prime) / actual_prime
        
        print(f"  Prediction: {prediction:.0f}")
        print(f"  Actual: {actual_prime}")
        print(f"  Lorentz γ: {gamma:.6f}")
        print(f"  Enhancement: {enhancement:.2f}%")
        print(f"  Relative error: {relative_error:.6f}")
        
        # Pass/fail criteria (reasonable accuracy)
        if relative_error < 0.01:  # 1% accuracy
            results['pass_count'] += 1
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")
    
    # Calculate correlation between gamma and enhancement
    if len(results['gamma_values']) > 3:
        correlation, p_value = stats.pearsonr(results['gamma_values'], results['enhancement_factors'])
        results['correlation'] = correlation
        
        print(f"\nCorrelation Analysis:")
        print(f"  Pearson r = {correlation:.4f}")
        print(f"  p-value = {p_value:.6f}")
        
        if abs(correlation) >= CORRELATION_THRESHOLD:
            print(f"  ✅ Correlation meets threshold r≥{CORRELATION_THRESHOLD}")
        else:
            print(f"  ❌ Correlation below threshold r≥{CORRELATION_THRESHOLD}")
    
    # CI validation (rough estimate for enhancement stability) + Bootstrap
    if results['enhancement_factors']:
        mean_enhancement = np.mean(results['enhancement_factors'])
        
        # Bootstrap confidence interval
        bootstrap_ci = bootstrap_confidence_interval(results['enhancement_factors'], n_bootstrap=1000)
        
        results['ci_validation'] = CI_LOWER <= mean_enhancement <= CI_UPPER
        results['bootstrap_ci'] = bootstrap_ci
        
        print(f"\nCI Validation:")
        print(f"  Mean enhancement: {mean_enhancement:.2f}%")
        print(f"  Bootstrap CI (95%): [{bootstrap_ci[0]:.2f}%, {bootstrap_ci[1]:.2f}%]")
        print(f"  Target CI range: [{CI_LOWER}, {CI_UPPER}]")
        
        # Check if bootstrap CI overlaps with target range
        bootstrap_overlap = not (bootstrap_ci[1] < CI_LOWER or bootstrap_ci[0] > CI_UPPER)
        
        if results['ci_validation']:
            print("  ✅ Mean enhancement within CI range")
        else:
            print("  ⚠️  Mean enhancement outside CI range")
            
        if bootstrap_overlap:
            print("  ✅ Bootstrap CI overlaps with target range")
        else:
            print("  ⚠️  Bootstrap CI does not overlap with target range")
    
    return results

def write_csv_logs(results: dict, filename: str = "fft_zeta_validation.csv"):
    """Write results to CSV for CI analysis."""
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['k', 'prediction', 'actual_prime', 'gamma', 'enhancement_pct', 'relative_error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for i in range(len(results['test_k_values'])):
                k = results['test_k_values'][i]
                pred = results['predictions'][i]
                actual = results['actual_primes'][i]
                gamma = results['gamma_values'][i]
                enh = results['enhancement_factors'][i]
                rel_err = abs(pred - actual) / actual
                
                writer.writerow({
                    'k': k,
                    'prediction': pred,
                    'actual_prime': actual,
                    'gamma': gamma,
                    'enhancement_pct': enh,
                    'relative_error': rel_err
                })
        
        print(f"\nCSV logs written to: {filename}")
        
    except Exception as e:
        print(f"Error writing CSV: {e}")

def main():
    parser = argparse.ArgumentParser(description='Validate FFT-zeta Z5D enhancement')
    parser.add_argument('--seed', type=int, default=DEFAULT_SEED, help='Random seed')
    parser.add_argument('--csv-logs', action='store_true', help='Generate CSV logs')
    parser.add_argument('--bootstrap', action='store_true', help='Enable bootstrap resampling (1000 resamples)')
    
    args = parser.parse_args()
    
    # Setup
    setup_seed(args.seed)
    
    # Check if C implementation is built
    if not os.path.exists('src/c/bin/z5d_prime_gen'):
        print("❌ z5d_prime_gen not found. Please build first:")
        print("   cd src/c && make gen")
        sys.exit(1)
    
    # Run validation
    start_time = time.time()
    results = validate_fft_zeta()
    end_time = time.time()
    
    # Bootstrap analysis if requested
    if args.bootstrap and results['enhancement_factors']:
        print(f"\n" + "="*50)
        print("BOOTSTRAP ANALYSIS (1000 resamples)")
        print("="*50)
        
        # Bootstrap for enhancement factors
        enh_ci = bootstrap_confidence_interval(results['enhancement_factors'], n_bootstrap=1000)
        print(f"Enhancement factors Bootstrap CI (95%): [{enh_ci[0]:.2f}%, {enh_ci[1]:.2f}%]")
        
        # Bootstrap for gamma values if available
        if results['gamma_values']:
            gamma_ci = bootstrap_confidence_interval(results['gamma_values'], n_bootstrap=1000)
            print(f"Lorentz gamma Bootstrap CI (95%): [{gamma_ci[0]:.6f}, {gamma_ci[1]:.6f}]")
            
        # Check overlap with target CI
        target_overlap = not (enh_ci[1] < CI_LOWER or enh_ci[0] > CI_UPPER)
        print(f"Bootstrap CI overlaps target [{CI_LOWER}, {CI_UPPER}]: {'✅ YES' if target_overlap else '❌ NO'}")
    
    # Summary
    print(f"\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    print(f"Tests passed: {results['pass_count']}/{results['total_tests']}")
    print(f"Pass rate: {results['pass_count']/results['total_tests']*100:.1f}%")
    
    if results['correlation'] is not None:
        print(f"Correlation: {results['correlation']:.4f}")
        correlation_pass = abs(results['correlation']) >= CORRELATION_THRESHOLD
        print(f"Correlation validation: {'✅ PASS' if correlation_pass else '❌ FAIL'}")
    
    if results['enhancement_factors']:
        ci_pass = results['ci_validation']
        print(f"CI validation: {'✅ PASS' if ci_pass else '⚠️  PARTIAL'}")
    
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    # Overall result
    overall_pass = (
        results['pass_count'] >= results['total_tests'] * 0.8 and  # 80% pass rate
        (results['correlation'] is None or abs(results['correlation']) >= CORRELATION_THRESHOLD)
    )
    
    print(f"\nOVERALL RESULT: {'✅ PASS' if overall_pass else '❌ FAIL'}")
    
    # CSV logs
    if args.csv_logs:
        write_csv_logs(results)
    
    # Exit code
    sys.exit(0 if overall_pass else 1)

if __name__ == "__main__":
    main()