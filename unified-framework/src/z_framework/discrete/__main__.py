#!/usr/bin/env python3
"""
Z Prime Utils CLI - Command Line Interface for Z Framework Accuracy Enhancement

This CLI provides access to the three accuracy enhancement methods:
1. Dynamic subset recalibration
2. Geodesic filtering  
3. Hybrid predictions with zeta corrections

Usage examples:
  python -m z_prime_utils calibrate --ks 1000,10000,100000
  python -m z_prime_utils predict --k 50000 --method hybrid
  python -m z_prime_utils filter --start 1000 --end 2000 --threshold auto
"""

import sys
import os
import argparse
import json
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.z_framework.discrete.z_prime_utils import ZPrimeEstimator
import sympy


def parse_k_values(k_string):
    """Parse comma-separated k values."""
    try:
        return np.array([int(k.strip()) for k in k_string.split(',')])
    except:
        raise ValueError(f"Invalid k values format: {k_string}")


def calibrate_command(args):
    """Handle calibration command."""
    print("Z PRIME UTILS - DYNAMIC CALIBRATION")
    print("="*50)
    
    # Parse k values
    k_values = parse_k_values(args.ks)
    print(f"Calibration set: {k_values}")
    
    # Generate or load true primes
    if args.primes:
        true_primes = parse_k_values(args.primes)
        if len(true_primes) != len(k_values):
            print("ERROR: Number of primes must match number of k values")
            return 1
    else:
        print("Generating true primes (this may take time for large k)...")
        true_primes = np.array([sympy.ntheory.prime(int(k)) for k in k_values])
    
    # Create estimator and calibrate
    estimator = ZPrimeEstimator()
    
    bounds_c = (args.min_c, args.max_c)
    bounds_k_star = (args.min_k_star, args.max_k_star)
    
    result = estimator.calibrate_parameters(
        k_values, 
        true_primes,
        bounds_c=bounds_c,
        bounds_k_star=bounds_k_star
    )
    
    # Display results
    print(f"\nCalibration Results:")
    print(f"  Fitted c:     {result['fitted_c']:.8f} ± {result.get('c_error', 0):.8f}")
    print(f"  Fitted k*:    {result['fitted_k_star']:.8f} ± {result.get('k_star_error', 0):.8f}")
    print(f"  Training MAE: {result['mae']:.2f}")
    print(f"  Training MRE: {100*result['mre']:.4f}%")
    print(f"  Bounds c:     {bounds_c}")
    print(f"  Bounds k*:    {bounds_k_star}")
    print(f"  Data points:  {result['n_points']}")
    
    # Save results if requested
    if args.output:
        output_data = {
            'fitted_c': float(result['fitted_c']),
            'fitted_k_star': float(result['fitted_k_star']),
            'mae': float(result['mae']),
            'mre': float(result['mre']),
            'k_values': k_values.tolist(),
            'true_primes': true_primes.tolist(),
            'bounds_c': bounds_c,
            'bounds_k_star': bounds_k_star
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    return 0


def predict_command(args):
    """Handle prediction command."""
    print("Z PRIME UTILS - PRIME PREDICTION")
    print("="*50)
    
    # Parse k values
    if ',' in args.k:
        k_values = parse_k_values(args.k)
        is_array = True
    else:
        k_values = int(args.k)
        is_array = False
        
    print(f"Predicting prime(s) for k = {k_values}")
    
    # Create estimator
    estimator = ZPrimeEstimator()
    
    # Load calibration if provided
    if args.calibration:
        try:
            with open(args.calibration, 'r') as f:
                calib_data = json.load(f)
            
            estimator.calibrated_c = calib_data['fitted_c']
            estimator.calibrated_k_star = calib_data['fitted_k_star']
            estimator.is_calibrated = True
            print(f"Loaded calibration: c={calib_data['fitted_c']:.6f}, k*={calib_data['fitted_k_star']:.6f}")
        except Exception as e:
            print(f"WARNING: Failed to load calibration: {e}")
    
    # Make predictions
    print(f"\nMethod: {args.method}")
    
    if args.method == 'z5d':
        from src.z_framework.discrete.z5d_predictor import z5d_prime
        predictions = z5d_prime(k_values)
    elif args.method == 'calibrated':
        predictions = estimator.calibrated_z5d_prime(k_values)
    elif args.method == 'hybrid':
        predictions = estimator.hybrid_z5d_prime(k_values, num_zeros=args.num_zeros)
    else:
        print(f"ERROR: Unknown method: {args.method}")
        return 1
    
    # Display results
    if is_array:
        print(f"\nPredictions:")
        for i, (k, pred) in enumerate(zip(k_values, predictions)):
            print(f"  p_{k} ≈ {pred:.2f}")
    else:
        print(f"\nPrediction: p_{k_values} ≈ {predictions:.2f}")
        
        # Optionally show true value for comparison
        if args.show_true:
            true_prime = sympy.ntheory.prime(k_values)
            error = abs(predictions - true_prime) / true_prime
            print(f"True value: p_{k_values} = {true_prime}")
            print(f"Relative error: {100*error:.4f}%")
    
    return 0


def filter_command(args):
    """Handle filtering command."""
    print("Z PRIME UTILS - GEODESIC FILTERING")
    print("="*50)
    
    print(f"Filtering candidates in range [{args.start}, {args.end}]")
    
    # Create estimator
    estimator = ZPrimeEstimator(geodesic_k=args.geodesic_k, wheel_modulus=args.wheel_modulus)
    
    # Determine threshold
    if args.threshold == 'auto':
        threshold = None  # Will use median
        print("Using automatic threshold (median)")
    else:
        threshold = float(args.threshold)
        print(f"Using threshold: {threshold}")
    
    # Apply filtering
    candidates = estimator.filter_prime_candidates(
        args.start, 
        args.end, 
        threshold=threshold
    )
    
    print(f"\nFiltering Results:")
    print(f"  Candidates found: {len(candidates)}")
    print(f"  Geodesic k:       {args.geodesic_k}")
    print(f"  Wheel modulus:    {args.wheel_modulus}")
    
    # Show first few candidates
    if candidates:
        show_count = min(10, len(candidates))
        print(f"  First {show_count}: {candidates[:show_count]}")
        
        if args.check_primes:
            print(f"\nPrimality check:")
            primes = [c for c in candidates if sympy.ntheory.isprime(c)]
            print(f"  Actual primes: {len(primes)}")
            print(f"  Prime density: {100*len(primes)/len(candidates):.2f}%")
    
    # Save results if requested
    if args.output:
        output_data = {
            'candidates': candidates,
            'range': [args.start, args.end],
            'threshold': threshold,
            'geodesic_k': args.geodesic_k,
            'wheel_modulus': args.wheel_modulus,
            'count': len(candidates)
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    return 0


def validate_command(args):
    """Handle validation command."""
    print("Z PRIME UTILS - VALIDATION")
    print("="*50)
    
    # Parse test k values
    k_test = parse_k_values(args.k_test)
    print(f"Test set: {k_test}")
    
    # Generate true primes
    print("Generating true primes for validation...")
    true_primes = np.array([sympy.ntheory.prime(int(k)) for k in k_test])
    
    # Create estimator
    estimator = ZPrimeEstimator()
    
    # Load calibration if provided
    if args.calibration:
        try:
            with open(args.calibration, 'r') as f:
                calib_data = json.load(f)
            
            estimator.calibrated_c = calib_data['fitted_c']
            estimator.calibrated_k_star = calib_data['fitted_k_star']
            estimator.is_calibrated = True
            print(f"Loaded calibration: c={calib_data['fitted_c']:.6f}, k*={calib_data['fitted_k_star']:.6f}")
        except Exception as e:
            print(f"WARNING: Using default parameters: {e}")
    
    # Validate each method
    methods = ['z5d', 'calibrated', 'hybrid']
    results = {}
    
    for method in methods:
        result = estimator.validate_predictions(
            k_test, 
            true_primes, 
            method=method
        )
        results[method] = result
        
        print(f"\n{method.upper()} Method:")
        print(f"  MAE:  {result['mae']:.2f}")
        print(f"  MRE:  {100*result['mre']:.4f}%")
        print(f"  RMSE: {result['rmse']:.2f}")
        print(f"  Max Error: {100*result['max_error']:.4f}%")
    
    # Compare methods
    print(f"\nMethod Comparison:")
    baseline_mre = results['z5d']['mre']
    for method in ['calibrated', 'hybrid']:
        if results[method]['mre'] > 0:
            improvement = baseline_mre / results[method]['mre']
            print(f"  {method} vs z5d: {improvement:.2f}x improvement")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Z Prime Utils CLI - Enhanced accuracy methods for prime prediction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m z_prime_utils calibrate --ks 1000,10000,100000
  python -m z_prime_utils predict --k 50000 --method hybrid --show-true
  python -m z_prime_utils filter --start 1000 --end 2000 --check-primes
  python -m z_prime_utils validate --k-test 5000,15000,25000 --calibration calib.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Calibrate command
    calib_parser = subparsers.add_parser('calibrate', help='Calibrate Z5D parameters')
    calib_parser.add_argument('--ks', required=True, help='Comma-separated k values for training')
    calib_parser.add_argument('--primes', help='Comma-separated true primes (if not provided, will compute)')
    calib_parser.add_argument('--min-c', type=float, default=-0.02, help='Minimum bound for c parameter')
    calib_parser.add_argument('--max-c', type=float, default=0, help='Maximum bound for c parameter')
    calib_parser.add_argument('--min-k-star', type=float, default=-0.1, help='Minimum bound for k* parameter')
    calib_parser.add_argument('--max-k-star', type=float, default=0.1, help='Maximum bound for k* parameter')
    calib_parser.add_argument('--output', help='Save calibration results to JSON file')
    
    # Predict command
    pred_parser = subparsers.add_parser('predict', help='Make prime predictions')
    pred_parser.add_argument('--k', required=True, help='k value(s) for prediction (single or comma-separated)')
    pred_parser.add_argument('--method', choices=['z5d', 'calibrated', 'hybrid'], default='calibrated', 
                           help='Prediction method')
    pred_parser.add_argument('--calibration', help='Load calibration from JSON file')
    pred_parser.add_argument('--num-zeros', type=int, default=10, help='Number of zeta zeros for hybrid method')
    pred_parser.add_argument('--show-true', action='store_true', help='Show true value and error (single k only)')
    
    # Filter command  
    filter_parser = subparsers.add_parser('filter', help='Apply geodesic filtering')
    filter_parser.add_argument('--start', type=int, required=True, help='Start of range')
    filter_parser.add_argument('--end', type=int, required=True, help='End of range')
    filter_parser.add_argument('--threshold', default='auto', help='Geodesic threshold (or "auto" for median)')
    filter_parser.add_argument('--geodesic-k', type=float, default=0.3, help='Geodesic curvature parameter')
    filter_parser.add_argument('--wheel-modulus', type=int, default=210, help='Wheel sieve modulus')
    filter_parser.add_argument('--check-primes', action='store_true', help='Check primality of candidates')
    filter_parser.add_argument('--output', help='Save candidates to JSON file')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate predictions')
    val_parser.add_argument('--k-test', required=True, help='Comma-separated k values for testing')
    val_parser.add_argument('--calibration', help='Load calibration from JSON file')
    
    args = parser.parse_args()
    
    if args.command == 'calibrate':
        return calibrate_command(args)
    elif args.command == 'predict':
        return predict_command(args)
    elif args.command == 'filter':
        return filter_command(args)
    elif args.command == 'validate':
        return validate_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())