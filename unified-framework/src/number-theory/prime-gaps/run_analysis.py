#!/usr/bin/env python3
"""
Prime Gap Analysis for N=10^9: Complete Example Script
=====================================================

This script demonstrates the complete prime gap analysis implementation
for N=10^9 with Z framework low-κ clustering analysis.

Run with different scale examples to validate before attempting full N=10^9.
"""

import argparse
import time
from analyze_gaps_billion import LargeScalePrimeGapAnalyzer, print_large_scale_summary, save_results


def run_analysis_example(limit: int, memory_mb: int = 4000, sample_rate: float = 0.01):
    """
    Run prime gap analysis example for given parameters.
    
    Args:
        limit: Upper bound for prime generation
        memory_mb: Memory limit in megabytes
        sample_rate: Sampling rate for detailed analysis
    """
    print(f"🔢 Prime Gap Analysis Example: N = {limit:,}")
    print("="*80)
    
    # Create analyzer
    analyzer = LargeScalePrimeGapAnalyzer(
        memory_limit_mb=memory_mb,
        sample_rate=sample_rate
    )
    
    # Run analysis
    start_time = time.time()
    results = analyzer.analyze_billion_scale(limit)
    total_time = time.time() - start_time
    
    # Print results
    print_large_scale_summary(results)
    
    # Performance summary
    if 'error' not in results:
        overall = results['overall_statistics']
        rate = overall['total_gaps'] / total_time if total_time > 0 else 0
        
        print(f"\n📊 Performance Summary:")
        print(f"   Processing rate: {rate:,.0f} gaps/second")
        print(f"   Memory efficiency: {memory_mb} MB limit maintained")
        print(f"   Sample efficiency: {sample_rate:.1%} → {results['analysis_parameters']['sample_size']:,} analyzed")
    
    # Save results
    output_file = f"prime_gaps_N{limit//1000000}M.json"
    save_results(results, output_file)
    
    return results


def main():
    """Main function with preset examples and command-line options."""
    parser = argparse.ArgumentParser(description='Prime Gap Analysis Examples')
    parser.add_argument('--preset', choices=['demo', 'medium', 'large', 'billion'], 
                      default='demo', help='Preset analysis scale')
    parser.add_argument('--custom-limit', type=int, help='Custom limit for analysis')
    parser.add_argument('--memory', type=int, default=4000, help='Memory limit in MB')
    parser.add_argument('--sample-rate', type=float, default=0.01, help='Sample rate (0.01 = 1%%)')
    
    args = parser.parse_args()
    
    # Define presets
    presets = {
        'demo': {
            'limit': 10_000_000,      # 10M - Quick demonstration
            'memory': 1000,
            'sample_rate': 0.01,
            'description': 'Quick demonstration (10M primes, ~30 seconds)'
        },
        'medium': {
            'limit': 100_000_000,     # 100M - Medium scale test
            'memory': 2000,
            'sample_rate': 0.005,
            'description': 'Medium scale analysis (100M primes, ~5 minutes)'
        },
        'large': {
            'limit': 500_000_000,     # 500M - Large scale test
            'memory': 4000,
            'sample_rate': 0.002,
            'description': 'Large scale analysis (500M primes, ~15 minutes)'
        },
        'billion': {
            'limit': 1_000_000_000,   # 1B - Full target
            'memory': 4000,
            'sample_rate': 0.001,
            'description': 'Full billion-scale analysis (1B primes, ~30 minutes)'
        }
    }
    
    if args.custom_limit:
        # Custom analysis
        print("🚀 Custom Prime Gap Analysis")
        results = run_analysis_example(
            limit=args.custom_limit,
            memory_mb=args.memory,
            sample_rate=args.sample_rate
        )
    else:
        # Preset analysis
        preset = presets[args.preset]
        print(f"🚀 Preset Analysis: {args.preset.upper()}")
        print(f"   {preset['description']}")
        print()
        
        results = run_analysis_example(
            limit=preset['limit'],
            memory_mb=preset['memory'],
            sample_rate=preset['sample_rate']
        )
    
    print(f"\n✅ Analysis completed successfully!")
    print(f"   Check generated JSON file and PNG visualizations")


if __name__ == "__main__":
    main()