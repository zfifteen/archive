#!/usr/bin/env python3
"""
Demonstration Script for Progressive Validation Ladder
======================================================

This script provides easy access to the Progressive Validation Ladder
for different use cases and configurations.

Usage examples:
    python demo_progressive_validation.py                    # Full validation
    python demo_progressive_validation.py --quick           # Quick test
    python demo_progressive_validation.py --baseline-only   # RSA-768 only
    python demo_progressive_validation.py --no-precision    # Disable high precision
"""

import sys
import os
import argparse
from datetime import datetime

# Add application path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'applications'))
from progressive_validation_ladder import ProgressiveValidationLadder

def quick_validation():
    """Run a quick validation with reduced parameters."""
    print("QUICK PROGRESSIVE VALIDATION")
    print("=" * 50)
    
    ladder = ProgressiveValidationLadder(enable_high_precision=True)
    
    # Override with quick parameters
    ladder.validation_levels = [
        {
            'name': 'RSA-512-Quick',
            'bits': 512,
            'known_factors': None,
            'description': 'Quick RSA-512 validation',
            'trials': 10,
            'max_iterations': 100,
            'tolerance': 1e-3
        },
        {
            'name': 'RSA-768-Quick',
            'bits': 768,
            'known_factors': ladder.RSA_768_FACTORS,
            'description': 'Quick RSA-768 baseline',
            'trials': 5,
            'max_iterations': 50,
            'tolerance': 1e-3
        }
    ]
    
    return ladder.run_progressive_validation()

def baseline_only_validation():
    """Run validation only on RSA-768 baseline."""
    print("BASELINE-ONLY VALIDATION (RSA-768)")
    print("=" * 50)
    
    ladder = ProgressiveValidationLadder(enable_high_precision=True)
    
    # Only RSA-768 known factorization
    ladder.validation_levels = [
        {
            'name': 'RSA-768-Baseline',
            'bits': 768,
            'known_factors': ladder.RSA_768_FACTORS,
            'description': 'RSA-768 baseline validation with known factors',
            'trials': 100,
            'max_iterations': 1000,
            'tolerance': 1e-6
        }
    ]
    
    return ladder.run_progressive_validation()

def custom_validation(max_bits=2048, enable_precision=True):
    """Run custom validation up to specified bit length."""
    print(f"CUSTOM VALIDATION (up to RSA-{max_bits})")
    print("=" * 50)
    
    ladder = ProgressiveValidationLadder(enable_high_precision=enable_precision)
    
    # Filter levels based on max_bits
    filtered_levels = []
    for level in ladder.validation_levels:
        if level['bits'] <= max_bits:
            filtered_levels.append(level)
    
    ladder.validation_levels = filtered_levels
    
    return ladder.run_progressive_validation()

def benchmark_mode():
    """Run in benchmark mode with detailed timing."""
    print("BENCHMARK MODE")
    print("=" * 50)
    
    results = {}
    
    # Test different precision modes
    for precision_mode in [False, True]:
        mode_name = "high_precision" if precision_mode else "standard_precision"
        print(f"\nTesting {mode_name} mode...")
        
        ladder = ProgressiveValidationLadder(enable_high_precision=precision_mode)
        
        # Use smaller test for benchmarking
        ladder.validation_levels = [
            {
                'name': 'RSA-512-Benchmark',
                'bits': 512,
                'known_factors': None,
                'description': f'Benchmark test - {mode_name}',
                'trials': 20,
                'max_iterations': 200,
                'tolerance': 1e-4
            }
        ]
        
        validation_results = ladder.run_progressive_validation()
        results[mode_name] = validation_results
        
        # Print timing comparison
        if len(validation_results.validation_results) > 0:
            time_taken = validation_results.validation_results[0].execution_time
            accuracy = validation_results.validation_results[0].accuracy_percentage
            print(f"  Time: {time_taken:.3f}s, Accuracy: {accuracy:.2f}%")
    
    # Compare results
    print(f"\nBENCHMARK COMPARISON:")
    print("-" * 30)
    if 'standard_precision' in results and 'high_precision' in results:
        std_time = results['standard_precision'].validation_results[0].execution_time
        hp_time = results['high_precision'].validation_results[0].execution_time
        speedup = hp_time / std_time if std_time > 0 else float('inf')
        print(f"High precision overhead: {speedup:.2f}x")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Progressive Validation Ladder Demo')
    parser.add_argument('--quick', action='store_true',
                        help='Run quick validation with reduced parameters')
    parser.add_argument('--baseline-only', action='store_true',
                        help='Run only RSA-768 baseline validation')
    parser.add_argument('--benchmark', action='store_true',
                        help='Run benchmark mode comparing precision settings')
    parser.add_argument('--max-bits', type=int, choices=[512, 768, 1024, 2048, 4096],
                        help='Maximum RSA bit length to test')
    parser.add_argument('--no-precision', action='store_true',
                        help='Disable high precision mode')
    parser.add_argument('--output', '-o', type=str,
                        help='Output filename for results')
    
    args = parser.parse_args()
    
    # Determine which validation to run
    if args.quick:
        results = quick_validation()
    elif args.baseline_only:
        results = baseline_only_validation()
    elif args.benchmark:
        results = benchmark_mode()
    elif args.max_bits:
        results = custom_validation(args.max_bits, not args.no_precision)
    else:
        # Full validation
        print("FULL PROGRESSIVE VALIDATION")
        print("=" * 50)
        ladder = ProgressiveValidationLadder(enable_high_precision=not args.no_precision)
        results = ladder.run_progressive_validation()
    
    # Save results if requested
    if args.output and hasattr(results, 'save_results'):
        ladder = ProgressiveValidationLadder()
        ladder.save_results(results, args.output)
    elif args.output:
        print(f"Warning: Cannot save results in benchmark mode")
    
    # Final summary
    if hasattr(results, 'overall_success'):
        print(f"\nFINAL RESULT: {'SUCCESS' if results.overall_success else 'FAILED'}")
        if hasattr(results, 'successful_levels') and hasattr(results, 'total_levels'):
            print(f"Success Rate: {results.successful_levels}/{results.total_levels}")
    
    print(f"\nDemo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()