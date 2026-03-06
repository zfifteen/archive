#!/usr/bin/env python3
"""
Wave-Knob Invariant Prime Scanner - Core Python Implementation
==============================================================

This module implements the Wave-Knob Invariant Prime Scanner system described in PR #713.
It provides adaptive (window, step) scanning to find R* where prime_count = 1.

Key Features:
- High-precision arithmetic using mpmath for ultra-scale k values
- Wave-ratio scanning with R = window/step invariant
- Self-tuning algorithm to lock onto resonance valleys
- Wheel-based coprime offset scanning for efficiency
- Cross-validation with Z5D enhanced predictor

Usage:
    python wave_knob_scanner.py --k 1000 --auto-tune
    python wave_knob_scanner.py --k 1e100 --window 66 --step 2 --precision 50
"""

import argparse
import time
import json
from typing import List, Tuple, Dict, Optional, Any
import numpy as np
from mpmath import mp, mpf, log, sqrt, isint, floor
from sympy import isprime, primerange, prime
# Add unified-framework root to Python path for src imports
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
unified_framework_root = os.path.join(script_dir, '..', '..')
unified_framework_root = os.path.abspath(unified_framework_root)
if unified_framework_root not in sys.path:
    sys.path.insert(0, unified_framework_root)

import src.core.z_5d_enhanced


# Set default precision
mp.dps = 50

class WaveKnobScanner:
    """
    Wave-Knob Invariant Prime Scanner implementation.
    
    This class implements the core scanning algorithm with wave-like interference
    patterns in the R = window/step parameter space.
    """
    
    def __init__(self, precision: int = 50, wheel_modulus: int = 30):
        """
        Initialize the wave-knob scanner.
        
        Args:
            precision: mpmath decimal precision
            wheel_modulus: Coprime wheel modulus (30 or 210)
        """
        mp.dps = precision
        self.precision = precision
        self.wheel_modulus = wheel_modulus
        self.wheel_offsets = self._get_wheel_offsets(wheel_modulus)
        self.total_primality_tests = 0
        
    def _get_wheel_offsets(self, modulus: int) -> List[int]:
        """Get coprime residue classes for wheel optimization."""
        if modulus == 30:
            return [1, 7, 11, 13, 17, 19, 23, 29]
        elif modulus == 210:
            return [1, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
                   71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 121, 127, 131, 
                   137, 139, 143, 149, 151, 157, 163, 167, 169, 173, 179, 181, 187, 
                   191, 193, 197, 199, 209]
        else:
            return list(range(1, modulus))  # Fallback: all residues
    
    def z5d_prediction(self, k: mpf) -> mpf:
        """
        Get Z5D prime prediction for index k.
        
        Args:
            k: Prime index
            
        Returns:
            Predicted k-th prime
        """
        if src.core.z_5d_enhanced.z5d_predictor is not None:
            return src.core.z_5d_enhanced.z5d_predictor(int(k))
        else:
            # Fallback: Enhanced PNT approximation
            k_val = mpf(k)
            ln_k = log(k_val)
            ln_ln_k = log(ln_k)
            return k_val * (ln_k + ln_ln_k - mpf('1') + (ln_ln_k - mpf('2')) / ln_k)
    
    def miller_rabin_test(self, n: int, rounds: int = 50) -> bool:
        """
        Miller-Rabin primality test.
        
        Args:
            n: Number to test
            rounds: Number of test rounds
            
        Returns:
            True if probably prime
        """
        self.total_primality_tests += 1
        return isprime(n)
    
    def scan_prime_count(self, prediction: mpf, window: int, step: int, 
                        wheel_offset_index: int = 0) -> Tuple[int, List[int]]:
        """
        Scan for primes around prediction with given window and step.
        
        Args:
            prediction: Central prediction point
            window: Search window size
            step: Step size between candidates
            wheel_offset_index: Index into wheel offsets array
            
        Returns:
            Tuple of (prime_count, list_of_primes_found)
        """
        center = int(prediction)
        primes_found = []
        
        # Use wheel offset for coprime scanning
        wheel_offset = self.wheel_offsets[wheel_offset_index % len(self.wheel_offsets)]
        
        # Adjust center to be congruent to wheel offset
        remainder = center % self.wheel_modulus
        if remainder != wheel_offset:
            adjust = wheel_offset - remainder
            if adjust < 0:
                adjust += self.wheel_modulus
            center += adjust
        
        # Search in window around adjusted center
        for offset in range(0, window + 1, step):
            # Forward direction
            if offset == 0:
                candidate = center
            else:
                candidate = center + offset * self.wheel_modulus
            
            if candidate > 2 and self.miller_rabin_test(candidate):
                primes_found.append(candidate)
            
            # Backward direction (if offset > 0)
            if offset > 0:
                candidate = center - offset * self.wheel_modulus
                if candidate > 2 and self.miller_rabin_test(candidate):
                    primes_found.append(candidate)
        
        return len(primes_found), primes_found
    
    def auto_tune_scan(self, k: mpf, target_count: int = 1, max_iterations: int = 100,
                      initial_window: int = 64, initial_step: int = 2) -> Dict[str, Any]:
        """
        Auto-tune scanning parameters to find R* where prime_count = target_count.
        
        Args:
            k: Prime index to scan around
            target_count: Target number of primes to find
            max_iterations: Maximum tuning iterations
            initial_window: Starting window size
            initial_step: Starting step size
            
        Returns:
            Dictionary with tuning results
        """
        start_time = time.time()
        prediction = self.z5d_prediction(k)
        
        window = initial_window
        step = initial_step
        found_target = False
        wheel_index = 0
        
        results = {
            'k': float(k),
            'z5d_prediction': float(prediction),
            'target_count': target_count,
            'iterations': 0,
            'locked': False,
            'final_window': window,
            'final_step': step,
            'final_R': 0.0,
            'prime_count': 0,
            'primes_found': [],
            'convergence_history': [],
            'total_primality_tests': 0,
            'elapsed_time': 0.0
        }
        
        for iteration in range(max_iterations):
            # Cycle through wheel offsets for uniform sampling
            count, primes = self.scan_prime_count(prediction, window, step, wheel_index)
            wheel_index = (wheel_index + 1) % len(self.wheel_offsets)
            
            R = window / step if step > 0 else float('inf')
            
            # Record iteration history
            results['convergence_history'].append({
                'iteration': iteration + 1,
                'window': window,
                'step': step,
                'R': R,
                'prime_count': count,
                'adjustment': 'none'
            })
            
            if count == target_count:
                # Found target - lock in
                found_target = True
                results['prime_count'] = count
                results['primes_found'] = primes
                break
            elif count == 0:
                # No primes found - increase R (expand search)
                if window < 10000:
                    window = int(window * 1.5)  # Grow window by 50%
                    results['convergence_history'][-1]['adjustment'] = 'expand_window'
                else:
                    step = max(1, step - 1)  # Reduce step if large window
                    results['convergence_history'][-1]['adjustment'] = 'reduce_step'
            elif count > target_count:
                # Too many primes - decrease R (narrow search)
                if window > step * 2:
                    window = max(step * 2, int(window * 0.67))  # Shrink window by 33%
                    results['convergence_history'][-1]['adjustment'] = 'shrink_window'
                else:
                    step += 1  # Increase step
                    results['convergence_history'][-1]['adjustment'] = 'increase_step'
            else:
                # Count < target but > 0 - fine-tune
                if count < target_count:
                    if window < 1000:
                        window = int(window * 1.2)  # Modest window increase
                        results['convergence_history'][-1]['adjustment'] = 'fine_expand'
                    else:
                        step = max(1, step - 1)
                        results['convergence_history'][-1]['adjustment'] = 'fine_reduce_step'
        
        # Record final state
        results['iterations'] = min(iteration + 1, max_iterations)
        results['locked'] = found_target
        results['final_window'] = window
        results['final_step'] = step
        results['final_R'] = window / step if step > 0 else float('inf')
        results['total_primality_tests'] = self.total_primality_tests
        results['elapsed_time'] = time.time() - start_time
        
        return results
    
    def r_sweep_experiment(self, k: mpf, window_range: Tuple[int, int, int],
                          step_range: Tuple[int, int, int]) -> List[Dict[str, Any]]:
        """
        Perform R-sweep experiment over window/step parameter grid.
        
        Args:
            k: Prime index to scan around
            window_range: (start, stop, step) for window values
            step_range: (start, stop, step) for step values
            
        Returns:
            List of scan results for each (window, step) combination
        """
        prediction = self.z5d_prediction(k)
        results = []
        
        windows = range(*window_range)
        steps = range(*step_range)
        
        wheel_index = 0
        for window in windows:
            for step in steps:
                if step == 0:  # Avoid division by zero
                    continue
                
                count, primes = self.scan_prime_count(prediction, window, step, wheel_index)
                wheel_index = (wheel_index + 1) % len(self.wheel_offsets)
                
                result = {
                    'k': float(k),
                    'z5d_prediction': float(prediction),
                    'window': window,
                    'step': step,
                    'R': window / step,
                    'prime_count': count,
                    'primes_found': primes[:5] if len(primes) <= 5 else primes[:5],  # Limit output
                    'is_resonance_valley': count == 1
                }
                results.append(result)
        
        return results


def main():
    """Main CLI interface for wave-knob scanner."""
    parser = argparse.ArgumentParser(description='Wave-Knob Invariant Prime Scanner')
    
    # Core arguments
    parser.add_argument('--k', type=str, required=True, help='Prime index (supports scientific notation)')
    parser.add_argument('--precision', type=int, default=50, help='mpmath decimal precision')
    parser.add_argument('--wheel', type=int, default=30, choices=[30, 210], help='Wheel modulus')
    
    # Scanning mode
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--auto-tune', action='store_true', help='Auto-tune mode')
    group.add_argument('--r-sweep', action='store_true', help='R-sweep mode')
    group.add_argument('--manual', action='store_true', help='Manual scan mode')
    
    # Auto-tune parameters
    parser.add_argument('--target', type=int, default=1, help='Target prime count for auto-tune')
    parser.add_argument('--max-iterations', type=int, default=100, help='Max auto-tune iterations')
    parser.add_argument('--initial-window', type=int, default=64, help='Initial window size')
    parser.add_argument('--initial-step', type=int, default=2, help='Initial step size')
    
    # Manual scan parameters
    parser.add_argument('--window', type=int, default=10, help='Manual scan window')
    parser.add_argument('--step', type=int, default=2, help='Manual scan step')
    
    # R-sweep parameters
    parser.add_argument('--window-range', type=str, default='2,50,5', 
                       help='Window range: start,stop,step')
    parser.add_argument('--step-range', type=str, default='1,10,1',
                       help='Step range: start,stop,step')
    
    # Output options
    parser.add_argument('--output', type=str, help='Output JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Parse k value
    try:
        k = mpf(args.k)
        if k < 2:
            print(f"Error: k must be >= 2, got {k}")
            return 1
    except:
        print(f"Error: Invalid k value '{args.k}'")
        return 1
    
    # Initialize scanner
    scanner = WaveKnobScanner(precision=args.precision, wheel_modulus=args.wheel)
    
    if args.verbose:
        print(f"Wave-Knob Scanner initialized")
        print(f"Precision: {args.precision} decimal places")
        print(f"Wheel modulus: {args.wheel}")
        print(f"Target k: {k}")
    
    # Determine mode
    if args.auto_tune or (not args.r_sweep and not args.manual):
        # Auto-tune mode (default)
        if args.verbose:
            print(f"Running auto-tune scan (target count: {args.target})")
        
        result = scanner.auto_tune_scan(
            k, 
            target_count=args.target,
            max_iterations=args.max_iterations,
            initial_window=args.initial_window,
            initial_step=args.initial_step
        )
        
        if args.verbose:
            print(f"Auto-tune completed:")
            print(f"  Locked: {result['locked']}")
            print(f"  Iterations: {result['iterations']}")
            print(f"  Final R*: {result['final_R']:.6f}")
            print(f"  Prime count: {result['prime_count']}")
            print(f"  Primality tests: {result['total_primality_tests']}")
            print(f"  Elapsed time: {result['elapsed_time']:.3f}s")
        
        output_data = result
        
    elif args.r_sweep:
        # R-sweep mode
        try:
            window_range = tuple(map(int, args.window_range.split(',')))
            step_range = tuple(map(int, args.step_range.split(',')))
        except ValueError:
            print("Error: Invalid range format. Use: start,stop,step")
            return 1
        
        if args.verbose:
            print(f"Running R-sweep experiment")
            print(f"Window range: {window_range}")
            print(f"Step range: {step_range}")
        
        results = scanner.r_sweep_experiment(k, window_range, step_range)
        
        if args.verbose:
            print(f"R-sweep completed: {len(results)} scans")
            resonance_valleys = [r for r in results if r['is_resonance_valley']]
            print(f"Resonance valleys found: {len(resonance_valleys)}")
            if resonance_valleys:
                min_r = min(r['R'] for r in resonance_valleys)
                print(f"Minimum R* in valleys: {min_r:.6f}")
        
        output_data = {
            'scan_type': 'r_sweep',
            'k': float(k),
            'window_range': window_range,
            'step_range': step_range,
            'total_scans': len(results),
            'resonance_valleys': len([r for r in results if r['is_resonance_valley']]),
            'results': results
        }
        
    else:
        # Manual scan mode
        if args.verbose:
            print(f"Running manual scan (window={args.window}, step={args.step})")
        
        prediction = scanner.z5d_prediction(k)
        count, primes = scanner.scan_prime_count(prediction, args.window, args.step)
        
        result = {
            'scan_type': 'manual',
            'k': float(k),
            'z5d_prediction': float(prediction),
            'window': args.window,
            'step': args.step,
            'R': args.window / args.step,
            'prime_count': count,
            'primes_found': primes,
            'total_primality_tests': scanner.total_primality_tests
        }
        
        if args.verbose:
            print(f"Manual scan completed:")
            print(f"  R ratio: {result['R']:.6f}")
            print(f"  Prime count: {result['prime_count']}")
            print(f"  Primes found: {result['primes_found'][:5] if len(result['primes_found']) <= 5 else result['primes_found'][:5]}")
        
        output_data = result
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        if args.verbose:
            print(f"Results saved to {args.output}")
    else:
        print(json.dumps(output_data, indent=2))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())