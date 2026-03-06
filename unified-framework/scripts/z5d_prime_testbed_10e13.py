#!/usr/bin/env python3
"""
Z Framework Z5D Prime Prediction Test Bed for n = 10^13

This script provides empirical validation of the Z Framework's z5d_prime prediction 
model against the published value of the 10^13th prime number.

The Z5D prime prediction formula implemented:
  base_pnt_prime(n) = n * (ln n + ln ln n - 1 + (ln ln n - 2)/ln n)
  d_term(n) = (ln(base_pnt_prime(n)) / e^4)^2  
  e_term(n) = base_pnt_prime(n)^{-1/3}
  z5d_prime(n) = base_pnt_prime(n) + c * d_term(n) * base_pnt_prime(n) + k_star * e_term(n) * base_pnt_prime(n)

Calibration parameters:
  c = -0.00247 (dilation calibration)
  k_star = 0.04449 (curvature calibration)

Published reference value (10^13th prime): 323,780,508,946,331

This test validates the predictive power of the Z Framework's prime estimation 
approach at extreme scale (n = 10^13).

References:
- Z Framework discrete domain normalization and geodesic refinement for prime prediction
- Published prime tables (OEIS A006988)
- Prior successful tests for n = 10^12

Author: Z Framework Team
License: MIT
"""

import sys
import os
import time
import warnings
from math import log

# Add src directory to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

try:
    from z_framework.discrete.z5d_predictor import (
        base_pnt_prime, 
        d_term, 
        e_term, 
        z5d_prime
    )
    import mpmath
    MPMATH_AVAILABLE = True
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you have installed the requirements: pip install -r requirements.txt")
    sys.exit(1)


def format_number(num):
    """Format large numbers with comma separators for readability."""
    if isinstance(num, float):
        return f"{num:,.0f}"
    else:
        return f"{num:,}"


def print_header():
    """Print formatted header for the test bed."""
    print("=" * 80)
    print("Z FRAMEWORK Z5D PRIME PREDICTION TEST BED")
    print("Empirical Validation for n = 10^13")
    print("=" * 80)
    print()


def print_formula_details():
    """Print the Z5D formula and parameters being used."""
    print("Z5D PRIME PREDICTION FORMULA:")
    print("-" * 40)
    print("base_pnt_prime(n) = n * (ln n + ln ln n - 1 + (ln ln n - 2)/ln n)")
    print("d_term(n) = (ln(base_pnt_prime(n)) / e^4)^2")
    print("e_term(n) = base_pnt_prime(n)^{-1/3}")
    print("z5d_prime(n) = base_pnt_prime(n) + c * d_term(n) * base_pnt_prime(n) + k_star * e_term(n) * base_pnt_prime(n)")
    print()
    print("CALIBRATION PARAMETERS:")
    print(f"c = -0.00247 (dilation calibration)")
    print(f"k_star = 0.04449 (curvature calibration)")
    print()


def run_z5d_prediction_test():
    """
    Run the empirical test of Z5D prime prediction for n = 10^13.
    
    Returns:
        dict: Results containing prediction, errors, and timing information
    """
    # Test parameters
    n = int(1e13)  # 10^13
    published_value = 323_780_508_946_331  # Published 10^13th prime
    
    # Z5D calibration parameters (as specified in requirements)
    c = -0.00247
    k_star = 0.04449
    
    print("TEST PARAMETERS:")
    print(f"Target n: {format_number(n)}")
    print(f"Published 10^13th prime: {format_number(published_value)}")
    print(f"Dilation parameter (c): {c}")
    print(f"Curvature parameter (k_star): {k_star}")
    print()
    
    # Set high precision for mpmath
    if MPMATH_AVAILABLE:
        mpmath.mp.dps = 50  # 50 decimal places precision
        print("High-precision arithmetic enabled (mpmath, 50 decimal places)")
    else:
        print("Warning: mpmath not available, using standard precision")
    print()
    
    print("COMPUTATION IN PROGRESS...")
    print("-" * 40)
    
    # Record start time
    start_time = time.time()
    
    # Suppress expected precision warnings for cleaner output
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        
        # Step 1: Compute base PNT estimate
        print("Step 1: Computing base Prime Number Theorem estimate...")
        base_pnt_value = base_pnt_prime(n)
        print(f"  base_pnt_prime({format_number(n)}) = {format_number(base_pnt_value)}")
        
        # Step 2: Compute dilation term
        print("Step 2: Computing dilation correction term...")
        d_value = d_term(n)
        print(f"  d_term({format_number(n)}) = {d_value:.10f}")
        
        # Step 3: Compute curvature term  
        print("Step 3: Computing curvature correction term...")
        e_value = e_term(n)
        print(f"  e_term({format_number(n)}) = {e_value:.10f}")
        
        # Step 4: Apply Z5D formula
        print("Step 4: Applying Z5D enhancement formula...")
        z5d_prediction = z5d_prime(n, c=c, k_star=k_star, auto_calibrate=False)
        
    # Record end time
    end_time = time.time()
    computation_time = end_time - start_time
    
    print(f"  z5d_prime({format_number(n)}) = {format_number(z5d_prediction)}")
    print()
    
    # Calculate errors
    absolute_error = abs(z5d_prediction - published_value)
    relative_error = absolute_error / published_value
    
    # Compile results
    results = {
        'n': n,
        'published_value': published_value,
        'base_pnt_prediction': base_pnt_value,
        'd_term_value': d_value,
        'e_term_value': e_value,
        'z5d_prediction': z5d_prediction,
        'absolute_error': absolute_error,
        'relative_error': relative_error,
        'computation_time': computation_time,
        'calibration_params': {'c': c, 'k_star': k_star}
    }
    
    return results


def print_results(results):
    """Print formatted results of the Z5D prediction test."""
    print("EMPIRICAL VALIDATION RESULTS:")
    print("=" * 50)
    
    # Core results
    print(f"Estimated 10^13th prime:     {format_number(results['z5d_prediction'])}")
    print(f"Published 10^13th prime:     {format_number(results['published_value'])}")
    print()
    
    # Error analysis
    print("ERROR ANALYSIS:")
    print("-" * 30)
    print(f"Absolute error:              {format_number(results['absolute_error'])}")
    print(f"Relative error:              {results['relative_error']:.8f} ({results['relative_error']*100:.6f}%)")
    print()
    
    # Component breakdown
    print("COMPONENT BREAKDOWN:")
    print("-" * 30)
    print(f"Base PNT estimate:           {format_number(results['base_pnt_prediction'])}")
    print(f"Dilation term d(n):          {results['d_term_value']:.10f}")
    print(f"Curvature term e(n):         {results['e_term_value']:.10f}")
    print()
    
    # Performance metrics
    print("PERFORMANCE METRICS:")
    print("-" * 30)
    print(f"Computation time:            {results['computation_time']:.3f} seconds")
    print(f"Parameters used:             c = {results['calibration_params']['c']}, k* = {results['calibration_params']['k_star']}")
    print()
    
    # Validation assessment
    if results['relative_error'] < 0.001:  # < 0.1%
        status = "EXCELLENT"
    elif results['relative_error'] < 0.01:  # < 1%
        status = "GOOD"
    elif results['relative_error'] < 0.1:   # < 10%
        status = "ACCEPTABLE"
    else:
        status = "POOR"
    
    print(f"VALIDATION STATUS:           {status}")
    print()


def print_technical_notes():
    """Print technical notes about the computation."""
    print("TECHNICAL NOTES:")
    print("-" * 20)
    print("• This computation uses high-precision arithmetic (mpmath) for numerical stability")
    print("• The Z5D formula extends PNT with dilation and curvature geodesics")
    print("• Calibration parameters optimized for k ≥ 10^6 based on empirical validation")
    print("• Expected sub-0.01% relative error for k ≥ 10^6 in optimal conditions")
    print("• Published value source: OEIS A006988 (prime enumeration tables)")
    print()


def main():
    """Main execution function for the Z5D test bed."""
    try:
        print_header()
        print_formula_details()
        
        # Run the prediction test
        results = run_z5d_prediction_test()
        
        # Print comprehensive results
        print_results(results)
        print_technical_notes()
        
        print("=" * 80)
        print("Z5D PRIME PREDICTION TEST BED COMPLETED SUCCESSFULLY")
        print("Results available for scientific reproducibility and validation")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Test bed execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())