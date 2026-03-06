#!/usr/bin/env python3
"""
Z5D Accuracy Testing Script - Hypothesis H1
==========================================

Tests Z5D predictor accuracy against ground truth primes as specified in Issue #677.

Validates:
- H1: For k ≥ 10^5, Z5D median relative error ≤ 0.01%; 99th-pct ≤ 0.03%
- Pass Gate: median ≤ 1e-4 AND 99th-pct ≤ 3e-4

Usage:
    python -m scripts.test_z5d_accuracy --k-min 1e5 --k-max 1e7 --grid log --points 200
    python -m scripts.test_z5d_accuracy --k-list 100000,200000,500000,1000000
"""

import sys
import os
import argparse
import numpy as np
import pandas as pd
import json
import time
from typing import List, Tuple, Dict, Any
import logging

# Add framework paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from discrete.crypto_prime_generator import z5d_prime
    from sympy import prime as true_prime
except ImportError:
    # Fallback implementations
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
    
    def true_prime(k):
        """Fallback - use Sieve of Eratosthenes for small k"""
        if k == 1:
            return 2
        elif k == 2: 
            return 3
        elif k <= 10:
            small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
            return small_primes[k-1] if k <= len(small_primes) else None
        else:
            # For larger k, we can't compute true primes easily
            return None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_k_grid(k_min: float, k_max: float, points: int, grid_type: str = "log") -> List[int]:
    """
    Generate k values for testing Z5D accuracy.
    
    Parameters:
    -----------
    k_min, k_max : float
        Range of k values
    points : int 
        Number of points to generate
    grid_type : str
        "log" for logarithmic spacing, "linear" for linear spacing
        
    Returns:
    --------
    List[int] : k values for testing
    """
    if grid_type == "log":
        k_values = np.logspace(np.log10(k_min), np.log10(k_max), points)
    else:
        k_values = np.linspace(k_min, k_max, points)
    
    # Convert to integers and remove duplicates
    k_values = sorted(list(set(int(k) for k in k_values if k >= 1)))
    
    logger.info(f"Generated {len(k_values)} k values from {k_values[0]} to {k_values[-1]}")
    return k_values

def test_z5d_accuracy(k_values: List[int], max_feasible_k: int = 10**7) -> pd.DataFrame:
    """
    Test Z5D accuracy against true primes for given k values.
    
    Parameters:
    -----------
    k_values : List[int]
        k values to test
    max_feasible_k : int
        Maximum k for which true prime computation is feasible
        
    Returns:
    --------
    pd.DataFrame with columns: k, p_true, p_hat, absolute_error, relative_error
    """
    results = []
    
    logger.info(f"Testing Z5D accuracy for {len(k_values)} k values")
    
    for i, k in enumerate(k_values):
        if i % 10 == 0:
            logger.info(f"Progress: {i+1}/{len(k_values)} (k={k})")
            
        # Get Z5D prediction
        start_time = time.time()
        p_hat = z5d_prime(k)
        prediction_time = time.time() - start_time
        
        # Get true prime if feasible
        if k <= max_feasible_k:
            try:
                start_time = time.time()
                p_true = true_prime(k)
                true_time = time.time() - start_time
                
                if p_true is not None:
                    abs_error = abs(p_hat - p_true)
                    rel_error = abs_error / p_true
                    
                    results.append({
                        'k': k,
                        'p_true': p_true,
                        'p_hat': p_hat,
                        'absolute_error': abs_error,
                        'relative_error': rel_error,
                        'prediction_time': prediction_time,
                        'true_computation_time': true_time,
                        'feasible': True
                    })
                else:
                    logger.warning(f"Could not compute true prime for k={k}")
                    results.append({
                        'k': k,
                        'p_true': None,
                        'p_hat': p_hat,
                        'absolute_error': None,
                        'relative_error': None,
                        'prediction_time': prediction_time,
                        'true_computation_time': None,
                        'feasible': False
                    })
                    
            except Exception as e:
                logger.warning(f"Error computing true prime for k={k}: {e}")
                results.append({
                    'k': k,
                    'p_true': None,
                    'p_hat': p_hat,
                    'absolute_error': None,
                    'relative_error': None,
                    'prediction_time': prediction_time,
                    'true_computation_time': None,
                    'feasible': False
                })
        else:
            # For large k, we can't compute true primes
            results.append({
                'k': k,
                'p_true': None,
                'p_hat': p_hat,
                'absolute_error': None,
                'relative_error': None,
                'prediction_time': prediction_time,
                'true_computation_time': None,
                'feasible': False
            })
    
    return pd.DataFrame(results)

def compute_accuracy_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute accuracy metrics from test results.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Results from test_z5d_accuracy()
        
    Returns:
    --------
    Dict with accuracy metrics and pass/fail assessment
    """
    # Filter to feasible computations only
    feasible_df = df[df['feasible'] == True].copy()
    
    if len(feasible_df) == 0:
        logger.warning("No feasible true prime computations - cannot assess accuracy")
        return {
            'feasible_count': 0,
            'total_count': len(df),
            'median_relative_error': None,
            'p99_relative_error': None,
            'mean_relative_error': None,
            'max_relative_error': None,
            'pass_gate': False,
            'gate_reason': 'No feasible true prime computations'
        }
    
    rel_errors = feasible_df['relative_error'].dropna()
    
    if len(rel_errors) == 0:
        return {
            'feasible_count': len(feasible_df),
            'total_count': len(df),
            'median_relative_error': None,
            'p99_relative_error': None,
            'mean_relative_error': None,
            'max_relative_error': None,
            'pass_gate': False,
            'gate_reason': 'No valid relative error computations'
        }
    
    # Compute statistics
    median_rel_error = np.median(rel_errors)
    p99_rel_error = np.percentile(rel_errors, 99)
    mean_rel_error = np.mean(rel_errors)
    max_rel_error = np.max(rel_errors)
    
    # Check pass/fail gates from Issue #677
    # Gate (PASS): median ≤ 1e-4 AND 99th-pct ≤ 3e-4
    median_pass = median_rel_error <= 1e-4
    p99_pass = p99_rel_error <= 3e-4
    pass_gate = median_pass and p99_pass
    
    if not pass_gate:
        if not median_pass:
            gate_reason = f"Median relative error {median_rel_error:.6f} > 1e-4"
        else:
            gate_reason = f"99th percentile relative error {p99_rel_error:.6f} > 3e-4"
    else:
        gate_reason = "All gates passed"
    
    # Additional statistics
    k_min = feasible_df['k'].min()
    k_max = feasible_df['k'].max()
    avg_prediction_time = feasible_df['prediction_time'].mean()
    avg_true_time = feasible_df['true_computation_time'].mean()
    
    metrics = {
        'feasible_count': len(feasible_df),
        'total_count': len(df),
        'k_range': (int(k_min), int(k_max)),
        'median_relative_error': float(median_rel_error),
        'p99_relative_error': float(p99_rel_error),
        'mean_relative_error': float(mean_rel_error),
        'max_relative_error': float(max_rel_error),
        'median_pass': bool(median_pass),
        'p99_pass': bool(p99_pass),
        'pass_gate': bool(pass_gate),
        'gate_reason': gate_reason,
        'avg_prediction_time': float(avg_prediction_time),
        'avg_true_computation_time': float(avg_true_time) if avg_true_time else None,
        'speedup_factor': float(avg_true_time / avg_prediction_time) if avg_true_time and avg_prediction_time > 0 else None
    }
    
    return metrics

def save_results(df: pd.DataFrame, metrics: Dict[str, Any], output_csv: str, output_json: str):
    """Save results to CSV and metrics to JSON"""
    # Save detailed results
    df.to_csv(output_csv, index=False)
    logger.info(f"Detailed results saved to {output_csv}")
    
    # Save metrics
    with open(output_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Accuracy metrics saved to {output_json}")

def print_summary(metrics: Dict[str, Any]):
    """Print summary of accuracy testing results"""
    print("\n" + "="*80)
    print("Z5D ACCURACY TEST RESULTS - HYPOTHESIS H1")
    print("="*80)
    
    print(f"Feasible computations: {metrics['feasible_count']:,} / {metrics['total_count']:,}")
    
    if metrics['feasible_count'] > 0:
        print(f"k range: {metrics['k_range'][0]:,} to {metrics['k_range'][1]:,}")
        print()
        print("ACCURACY METRICS:")
        print(f"  Median relative error:     {metrics['median_relative_error']:.6f} ({metrics['median_relative_error']*100:.4f}%)")
        print(f"  99th percentile rel error: {metrics['p99_relative_error']:.6f} ({metrics['p99_relative_error']*100:.4f}%)")
        print(f"  Mean relative error:       {metrics['mean_relative_error']:.6f} ({metrics['mean_relative_error']*100:.4f}%)")
        print(f"  Maximum relative error:    {metrics['max_relative_error']:.6f} ({metrics['max_relative_error']*100:.4f}%)")
        print()
        print("PASS/FAIL GATES:")
        print(f"  Median ≤ 1e-4 (0.01%):     {'✓ PASS' if metrics['median_pass'] else '✗ FAIL'}")
        print(f"  99th-pct ≤ 3e-4 (0.03%):   {'✓ PASS' if metrics['p99_pass'] else '✗ FAIL'}")
        print()
        print(f"OVERALL RESULT: {'✓ PASS' if metrics['pass_gate'] else '✗ FAIL'}")
        print(f"Reason: {metrics['gate_reason']}")
        
        if metrics['avg_prediction_time'] and metrics['avg_true_computation_time']:
            print()
            print("PERFORMANCE:")
            print(f"  Avg Z5D prediction time:   {metrics['avg_prediction_time']:.6f}s")
            print(f"  Avg true computation time: {metrics['avg_true_computation_time']:.6f}s")
            print(f"  Speedup factor:           {metrics['speedup_factor']:.1f}x")
    else:
        print(f"RESULT: ✗ FAIL - {metrics['gate_reason']}")
    
    print("="*80)

def main():
    parser = argparse.ArgumentParser(
        description="Test Z5D predictor accuracy (Hypothesis H1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Logarithmic grid from 10^5 to 10^7
    python -m scripts.test_z5d_accuracy --k-min 1e5 --k-max 1e7 --grid log --points 200
    
    # Dense block for detailed testing
    python -m scripts.test_z5d_accuracy --k-min 1e5 --k-max 1e6 --grid linear --points 100
    
    # Specific k values
    python -m scripts.test_z5d_accuracy --k-list 100000,200000,500000,1000000
        """
    )
    
    parser.add_argument(
        '--k-min',
        type=float,
        default=1e5,
        help='Minimum k value (default: 1e5)'
    )
    
    parser.add_argument(
        '--k-max', 
        type=float,
        default=1e6,
        help='Maximum k value (default: 1e6)'
    )
    
    parser.add_argument(
        '--grid',
        choices=['log', 'linear'],
        default='log',
        help='Grid type: log or linear (default: log)'
    )
    
    parser.add_argument(
        '--points',
        type=int,
        default=100,
        help='Number of points to test (default: 100)'
    )
    
    parser.add_argument(
        '--k-list',
        type=str,
        help='Comma-separated list of specific k values to test'
    )
    
    parser.add_argument(
        '--max-feasible-k',
        type=int,
        default=10**6,
        help='Maximum k for true prime computation (default: 10^6)'
    )
    
    parser.add_argument(
        '--output-csv',
        type=str,
        default='results/z5d_accuracy_results.csv',
        help='Output CSV file for detailed results'
    )
    
    parser.add_argument(
        '--output-json',
        type=str,
        default='metrics/accuracy.json',
        help='Output JSON file for metrics'
    )
    
    args = parser.parse_args()
    
    # Create output directories
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    
    # Generate k values to test
    if args.k_list:
        try:
            k_values = [int(x.strip()) for x in args.k_list.split(',')]
        except ValueError:
            print("Error: Invalid k-list format. Use comma-separated integers.")
            return 1
    else:
        k_values = generate_k_grid(args.k_min, args.k_max, args.points, args.grid)
    
    # Filter k values to reasonable range
    k_values = [k for k in k_values if k >= 1]
    
    if not k_values:
        print("Error: No valid k values to test")
        return 1
    
    logger.info(f"Testing {len(k_values)} k values")
    
    try:
        # Test Z5D accuracy
        start_time = time.time()
        df = test_z5d_accuracy(k_values, args.max_feasible_k)
        test_time = time.time() - start_time
        
        # Compute metrics
        metrics = compute_accuracy_metrics(df)
        metrics['total_test_time'] = test_time
        
        # Save results
        save_results(df, metrics, args.output_csv, args.output_json)
        
        # Print summary
        print_summary(metrics)
        
        # Return appropriate exit code
        return 0 if metrics['pass_gate'] else 1
        
    except Exception as e:
        logger.error(f"Error during accuracy testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())