"""
Prime Gap Analysis for N=10^9 with Z Framework Low-κ Clustering
===============================================================

This script performs large-scale prime gap analysis for N=10^9, specifically
designed to analyze low-κ clustering patterns using the Z framework models.

Key Features:
- Memory-efficient segmented prime generation for N=10^9
- Streaming gap analysis to minimize memory footprint
- Z framework low-κ clustering analysis with statistical modeling
- Empirical visualization and comprehensive reporting

Optimizations for N=10^9:
- Segmented sieve processing to stay within memory limits
- Sampling-based analysis for computational efficiency  
- Progressive reporting and checkpointing
- Adaptive memory management

Usage:
    python3 analyze_gaps_billion.py --limit 1000000000 --memory-limit 4000
"""

import argparse
import json
import time
import gc
import numpy as np
from typing import Dict, List, Tuple
import os
import sys
import traceback

# Import our analysis modules
from prime_gap_analyzer import PrimeGapAnalyzer, print_analysis_summary


class LargeScalePrimeGapAnalyzer:
    """
    Specialized analyzer for very large N with memory and performance optimizations.
    """
    
    def __init__(self, memory_limit_mb: int = 4000, sample_rate: float = 0.1):
        """
        Initialize large-scale analyzer.
        
        Args:
            memory_limit_mb: Memory limit in megabytes
            sample_rate: Fraction of gaps to sample for detailed analysis
        """
        self.memory_limit_mb = memory_limit_mb
        self.sample_rate = sample_rate
        self.analyzer = PrimeGapAnalyzer(memory_limit_mb=memory_limit_mb)
        self.checkpoint_interval = 10000000  # Checkpoint every 10M primes
        
    def analyze_billion_scale(self, limit: int = 1000000000) -> Dict:
        """
        Perform prime gap analysis optimized for N=10^9 scale.
        
        Args:
            limit: Upper bound for prime generation (default 10^9)
            
        Returns:
            Analysis results dictionary
        """
        print(f"=== Large-Scale Prime Gap Analysis for N = {limit:,} ===")
        print(f"Memory limit: {self.memory_limit_mb} MB")
        print(f"Sample rate: {self.sample_rate:.1%}")
        
        start_time = time.time()
        
        # Initialize collectors
        all_gaps = []
        all_positions = []
        gap_count = 0
        
        # Statistics collectors
        gap_sum = 0
        gap_sum_squares = 0
        max_gap = 0
        min_gap = float('inf')
        
        # Low-κ analysis setup
        kappa_samples = []
        frame_shift_samples = []
        
        print("\nGenerating and analyzing prime gaps...")
        
        try:
            checkpoint_counter = 0
            
            for prev_prime, next_prime, gap in self.analyzer.generate_prime_gaps_streaming(limit):
                gap_count += 1
                
                # Update statistics
                gap_sum += gap
                gap_sum_squares += gap * gap
                max_gap = max(max_gap, gap)
                min_gap = min(min_gap, gap)
                
                # Sample for detailed analysis
                if np.random.random() < self.sample_rate:
                    all_gaps.append(gap)
                    all_positions.append(prev_prime)
                    
                    # Compute curvature and frame shift for sampled points
                    kappa = self.analyzer.compute_curvature_simple(prev_prime)
                    frame_shift = self.analyzer.compute_frame_shift(prev_prime)
                    
                    kappa_samples.append(kappa)
                    frame_shift_samples.append(frame_shift)
                
                # Progress reporting
                if gap_count % 1000000 == 0:
                    elapsed = time.time() - start_time
                    rate = gap_count / elapsed if elapsed > 0 else 0
                    print(f"  Processed {gap_count:,} gaps ({rate:.0f} gaps/sec), "
                          f"current gap: {gap}, at position: {prev_prime:,}")
                
                # Memory management
                if gap_count % self.checkpoint_interval == 0:
                    checkpoint_counter += 1
                    print(f"  Checkpoint {checkpoint_counter}: {gap_count:,} gaps processed")
                    
                    # Force garbage collection
                    gc.collect()
                    
                    # Check if we need to reduce sample size
                    if len(all_gaps) > 1000000:  # Keep sample size reasonable
                        # Keep recent samples and some random older ones
                        keep_recent = int(0.7 * len(all_gaps))
                        keep_random = int(0.3 * len(all_gaps))
                        
                        indices = list(range(-keep_recent, 0))  # Recent
                        indices.extend(np.random.choice(len(all_gaps) - keep_recent, 
                                                      keep_random, replace=False))
                        
                        all_gaps = [all_gaps[i] for i in indices]
                        all_positions = [all_positions[i] for i in indices]
                        kappa_samples = [kappa_samples[i] for i in indices]
                        frame_shift_samples = [frame_shift_samples[i] for i in indices]
                        
                        print(f"    Reduced sample size to {len(all_gaps):,} for memory efficiency")
        
        except KeyboardInterrupt:
            print(f"\n⚠️ Analysis interrupted by user at {gap_count:,} gaps")
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            traceback.print_exc()
        
        print(f"\nCompleted gap generation: {gap_count:,} total gaps processed")
        print(f"Sample size for detailed analysis: {len(all_gaps):,}")
        
        # Compute overall statistics
        gap_mean = gap_sum / gap_count if gap_count > 0 else 0
        gap_variance = (gap_sum_squares / gap_count - gap_mean**2) if gap_count > 0 else 0
        gap_std = np.sqrt(gap_variance) if gap_variance > 0 else 0
        
        # Analyze sampled data for low-κ clustering
        print("\nAnalyzing low-κ clustering on sampled data...")
        
        if len(all_gaps) > 0:
            # Convert to numpy arrays
            all_gaps = np.array(all_gaps)
            all_positions = np.array(all_positions)
            kappa_samples = np.array(kappa_samples)
            frame_shift_samples = np.array(frame_shift_samples)
            
            # Low-κ threshold analysis
            kappa_threshold = np.percentile(kappa_samples, 25)
            low_kappa_mask = kappa_samples <= kappa_threshold
            
            low_kappa_gaps = all_gaps[low_kappa_mask]
            low_kappa_count = len(low_kappa_gaps)
            low_kappa_fraction = low_kappa_count / len(all_gaps)
            
            # Compile results
            results = {
                'analysis_parameters': {
                    'limit': limit,
                    'memory_limit_mb': self.memory_limit_mb,
                    'sample_rate': self.sample_rate,
                    'total_gaps_processed': gap_count,
                    'sample_size': len(all_gaps),
                    'analysis_time_seconds': time.time() - start_time
                },
                
                'overall_statistics': {
                    'total_gaps': gap_count,
                    'gap_mean': gap_mean,
                    'gap_std': gap_std,
                    'gap_min': min_gap if min_gap != float('inf') else 0,
                    'gap_max': max_gap
                },
                
                'sampled_statistics': {
                    'sample_size': len(all_gaps),
                    'sample_gap_mean': np.mean(all_gaps),
                    'sample_gap_std': np.std(all_gaps),
                    'sample_gap_median': np.median(all_gaps),
                    'sample_gap_min': np.min(all_gaps),
                    'sample_gap_max': np.max(all_gaps)
                },
                
                'low_kappa_analysis': {
                    'kappa_threshold': kappa_threshold,
                    'low_kappa_count': low_kappa_count,
                    'low_kappa_fraction': low_kappa_fraction,
                    'low_kappa_gap_mean': np.mean(low_kappa_gaps) if len(low_kappa_gaps) > 0 else 0,
                    'low_kappa_gap_std': np.std(low_kappa_gaps) if len(low_kappa_gaps) > 0 else 0,
                    'curvature_stats': {
                        'mean': np.mean(kappa_samples),
                        'std': np.std(kappa_samples),
                        'median': np.median(kappa_samples)
                    },
                    'frame_shift_stats': {
                        'mean': np.mean(frame_shift_samples),
                        'std': np.std(frame_shift_samples),
                        'median': np.median(frame_shift_samples)
                    }
                }
            }
            
            # Create visualizations for sampled data
            print("Creating visualizations for sampled data...")
            try:
                # Create a minimal analysis results dict for visualization
                viz_results = {
                    'kappa_threshold': kappa_threshold, 
                    'low_kappa_count': low_kappa_count,
                    'low_kappa_fraction': low_kappa_fraction,
                    'gap_stats': {
                        'all_gaps': {
                            'mean': np.mean(all_gaps),
                            'std': np.std(all_gaps),
                            'median': np.median(all_gaps)
                        }
                    }
                }
                
                plot_files = self.analyzer.create_visualizations(
                    all_gaps.tolist(), all_positions.tolist(), 
                    viz_results, 
                    f"billion_analysis_{limit//1000000}M"
                )
                results['plot_files'] = plot_files
            except Exception as e:
                print(f"⚠️ Warning: Could not create all visualizations: {e}")
                results['plot_files'] = []
        
        else:
            print("⚠️ No gaps collected for analysis")
            results = {
                'analysis_parameters': {
                    'limit': limit,
                    'total_gaps_processed': gap_count,
                    'analysis_time_seconds': time.time() - start_time
                },
                'error': 'No gaps collected for analysis'
            }
        
        return results


def save_results(results: Dict, filename: str):
    """Save analysis results to JSON file."""
    try:
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            else:
                return obj
        
        results_serializable = convert_numpy(results)
        
        with open(filename, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"⚠️ Could not save results to {filename}: {e}")


def print_large_scale_summary(results: Dict):
    """Print summary for large-scale analysis."""
    print("\n" + "="*80)
    print("LARGE-SCALE PRIME GAP ANALYSIS SUMMARY")
    print("="*80)
    
    if 'error' in results:
        print(f"❌ Analysis failed: {results['error']}")
        return
    
    params = results['analysis_parameters']
    overall = results['overall_statistics']
    sampled = results['sampled_statistics']
    low_kappa = results['low_kappa_analysis']
    
    print(f"Analysis Parameters:")
    print(f"  Target limit: N = {params['limit']:,}")
    print(f"  Memory limit: {params['memory_limit_mb']} MB")
    print(f"  Sample rate: {params['sample_rate']:.1%}")
    print(f"  Analysis time: {params['analysis_time_seconds']:.1f} seconds")
    
    print(f"\nOverall Statistics (all {overall['total_gaps']:,} gaps):")
    print(f"  Mean gap: {overall['gap_mean']:.2f}")
    print(f"  Std gap: {overall['gap_std']:.2f}")
    print(f"  Min gap: {overall['gap_min']}")
    print(f"  Max gap: {overall['gap_max']}")
    
    print(f"\nSampled Statistics ({sampled['sample_size']:,} gaps):")
    print(f"  Mean gap: {sampled['sample_gap_mean']:.2f}")
    print(f"  Std gap: {sampled['sample_gap_std']:.2f}")
    print(f"  Median gap: {sampled['sample_gap_median']:.2f}")
    print(f"  Range: [{sampled['sample_gap_min']}, {sampled['sample_gap_max']}]")
    
    print(f"\nLow-κ Clustering Analysis:")
    print(f"  κ threshold: {low_kappa['kappa_threshold']:.6f}")
    print(f"  Low-κ gaps: {low_kappa['low_kappa_count']:,} ({low_kappa['low_kappa_fraction']:.1%})")
    print(f"  Low-κ gap mean: {low_kappa['low_kappa_gap_mean']:.2f}")
    print(f"  Low-κ gap std: {low_kappa['low_kappa_gap_std']:.2f}")
    
    curvature_stats = low_kappa['curvature_stats']
    frame_stats = low_kappa['frame_shift_stats']
    print(f"  Curvature - Mean: {curvature_stats['mean']:.6f}, Std: {curvature_stats['std']:.6f}")
    print(f"  Frame shift - Mean: {frame_stats['mean']:.6f}, Std: {frame_stats['std']:.6f}")
    
    if 'plot_files' in results:
        print(f"\nGenerated {len(results['plot_files'])} visualization files:")
        for plot_file in results['plot_files']:
            print(f"  - {plot_file}")


def main():
    """Main function for command-line execution."""
    parser = argparse.ArgumentParser(description='Prime Gap Analysis for N=10^9')
    parser.add_argument('--limit', type=int, default=1000000000,
                      help='Upper limit for prime generation (default: 10^9)')
    parser.add_argument('--memory-limit', type=int, default=4000,
                      help='Memory limit in MB (default: 4000)')
    parser.add_argument('--sample-rate', type=float, default=0.01,
                      help='Sampling rate for detailed analysis (default: 0.01 = 1%%)')
    parser.add_argument('--output', type=str, default='billion_gap_analysis.json',
                      help='Output file for results (default: billion_gap_analysis.json)')
    
    args = parser.parse_args()
    
    print("🔢 Prime Gap Analysis for N=10^9 with Z Framework Low-κ Clustering")
    print("="*80)
    
    # Create analyzer
    analyzer = LargeScalePrimeGapAnalyzer(
        memory_limit_mb=args.memory_limit,
        sample_rate=args.sample_rate
    )
    
    try:
        # Run analysis
        results = analyzer.analyze_billion_scale(limit=args.limit)
        
        # Print summary
        print_large_scale_summary(results)
        
        # Save results
        save_results(results, args.output)
        
        print(f"\n✅ Analysis completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()