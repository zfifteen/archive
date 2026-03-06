#!/usr/bin/env python3
"""
PNT Inversion Script for Z5D Test Plan
=====================================

Implements robust inversion of the Prime Number Theorem to convert bit lengths
to k values for Z5D prime prediction. Used by crypto-friendly prime test scripts.

Usage:
    python -m scripts.invert_pnt --m 256 --output k_values.txt
    python -m scripts.invert_pnt --m-list 128,192,224,255,256,384,521
"""

import sys
import os
import argparse
import numpy as np
import json
from typing import List, Dict, Any

# Add framework paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from discrete.crypto_prime_generator import z5d_prime
except ImportError:
    # Fallback Z5D implementation
    def z5d_prime(k):
        if k < 6:
            primes = [2, 3, 5, 7, 11, 13]
            return primes[k-1] if k <= len(primes) else 13
        
        log_k = np.log(float(k))
        log_log_k = np.log(log_k) if log_k > 1 else 1
        pnt = k * (log_k + log_log_k - 1.0 + (log_log_k - 2.0)/log_k)
        
        # Z5D correction terms
        c = -0.00247
        k_star = 0.04449  
        d_term = c * pnt
        e_term = k_star * np.exp(log_k / np.e**2) * pnt
        
        return int(pnt + d_term + e_term)

def k_for_bitlength(m: int, tolerance: float = 1e-6, max_iterations: int = 20) -> int:
    """
    Invert PNT to find k such that the k-th prime ≈ 2^m
    
    Uses Newton's method with robust convergence handling.
    
    Parameters:
    -----------
    m : int
        Target bit length
    tolerance : float
        Convergence tolerance (relative error)
    max_iterations : int
        Maximum Newton iterations
        
    Returns:
    --------
    k : int
        Estimated k value such that p_k ≈ 2^m
    """
    target = 2**m
    
    # Initial guess using enhanced PNT
    log_target = np.log(float(target))
    log_log_target = np.log(log_target) if log_target > 1 else 1
    
    # PNT inverse approximation
    k = target / (log_target - 1 + (log_log_target - 2)/log_target)
    
    print(f"Inverting PNT for m={m} (target=2^{m}={target:,})")
    print(f"Initial k estimate: {k:,.0f}")
    
    # Newton's method refinement
    for iteration in range(max_iterations):
        k_int = max(1, int(k))
        pred = z5d_prime(k_int)
        error = pred - target
        rel_error = abs(error) / target
        
        print(f"  Iteration {iteration+1}: k={k_int:,}, pred={pred:,}, error={error:,}, rel_err={rel_error:.6f}")
        
        if rel_error < tolerance:
            print(f"  Converged in {iteration+1} iterations")
            return k_int
            
        # Numerical derivative using finite difference
        k_delta = max(1, int(k * 0.001))
        pred_delta = z5d_prime(k_int + k_delta)
        derivative = (pred_delta - pred) / k_delta
        
        if derivative <= 0:
            print(f"  Warning: Non-positive derivative {derivative}, using fallback")
            # Fallback: binary search approach
            if error > 0:
                k = k * 0.95  # Reduce k if prediction too high
            else:
                k = k * 1.05  # Increase k if prediction too low
        else:
            # Standard Newton update
            k_new = k - error / derivative
            
            # Ensure k doesn't become negative or change too drastically
            if k_new <= 0 or abs(k_new - k) > k * 0.5:
                print(f"  Large step detected, using dampened update")
                step = -error / derivative
                k = k + 0.5 * step  # Dampen the step
            else:
                k = k_new
                
        k = max(1, k)  # Ensure k stays positive
    
    print(f"  Warning: Did not converge in {max_iterations} iterations")
    return max(1, int(k))

def invert_multiple_bitlengths(m_list: List[int]) -> Dict[int, Dict[str, Any]]:
    """
    Invert PNT for multiple bit lengths and return comprehensive results.
    
    Parameters:
    -----------
    m_list : List[int]
        List of bit lengths to invert
        
    Returns:
    --------
    Dict mapping bit length to results including k, target, prediction, error
    """
    results = {}
    
    for m in m_list:
        print(f"\n{'='*60}")
        print(f"Processing bit length m = {m}")
        print(f"{'='*60}")
        
        target = 2**m
        k = k_for_bitlength(m)
        prediction = z5d_prime(k)
        error = prediction - target
        rel_error = abs(error) / target
        
        results[m] = {
            'k': k,
            'target': target,
            'prediction': prediction,
            'absolute_error': error,
            'relative_error': rel_error,
            'log_target': np.log(float(target)),
            'log_k': np.log(float(k))
        }
        
        print(f"\nFinal Results for m={m}:")
        print(f"  k = {k:,}")
        print(f"  Target (2^{m}) = {target:,}")
        print(f"  Z5D prediction = {prediction:,}")
        print(f"  Absolute error = {error:,}")
        print(f"  Relative error = {rel_error:.6f} ({rel_error*100:.4f}%)")
    
    return results

def save_results(results: Dict[int, Dict[str, Any]], output_file: str):
    """Save inversion results to JSON file"""
    # Convert numpy types to Python native types for JSON serialization
    json_results = {}
    for m, data in results.items():
        json_results[str(m)] = {
            k: int(v) if isinstance(v, (np.integer, np.int64)) else float(v)
            for k, v in data.items()
        }
    
    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="PNT inversion for crypto-friendly prime bit lengths",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single bit length
    python -m scripts.invert_pnt --m 256
    
    # Multiple bit lengths  
    python -m scripts.invert_pnt --m-list 128,192,224,255,256,384,521
    
    # Save results to file
    python -m scripts.invert_pnt --m-list 128,256,521 --output k_values.json
        """
    )
    
    parser.add_argument(
        '--m', 
        type=int,
        help='Single bit length to invert'
    )
    
    parser.add_argument(
        '--m-list',
        type=str,
        help='Comma-separated list of bit lengths (e.g., "128,192,256,384,521")'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        help='Output file for results (JSON format)'
    )
    
    parser.add_argument(
        '--tolerance',
        type=float,
        default=1e-6,
        help='Convergence tolerance (default: 1e-6)'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int, 
        default=20,
        help='Maximum Newton iterations (default: 20)'
    )
    
    args = parser.parse_args()
    
    # Determine bit lengths to process
    if args.m_list:
        try:
            m_values = [int(x.strip()) for x in args.m_list.split(',')]
        except ValueError:
            print("Error: Invalid m-list format. Use comma-separated integers.")
            return 1
    elif args.m:
        m_values = [args.m]
    else:
        # Default crypto-friendly bit lengths from test plan
        m_values = [128, 192, 224, 255, 256, 384, 521]
        print("Using default crypto bit lengths:", m_values)
    
    # Validate bit lengths
    for m in m_values:
        if m < 8 or m > 4096:
            print(f"Warning: Bit length {m} may be outside reasonable range")
    
    # Run PNT inversion
    try:
        results = invert_multiple_bitlengths(m_values)
        
        # Save results if output file specified
        if args.output:
            save_results(results, args.output)
        
        # Print summary table
        print(f"\n{'='*80}")
        print("SUMMARY TABLE")
        print(f"{'='*80}")
        print(f"{'Bit Length':<12} {'k Value':<15} {'Target':<15} {'Prediction':<15} {'Rel Error':<12}")
        print(f"{'-'*12} {'-'*15} {'-'*15} {'-'*15} {'-'*12}")
        
        for m in sorted(m_values):
            data = results[m]
            print(f"{m:<12} {data['k']:<15,} {data['target']:<15,} {data['prediction']:<15,} {data['relative_error']:<12.6f}")
        
        return 0
        
    except Exception as e:
        print(f"Error during PNT inversion: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())