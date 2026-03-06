"""
Prime Gap Analysis with Z Framework Low-κ Clustering
===================================================

This module implements efficient prime gap generation and analysis for N=10^9,
with special focus on low-κ clustering patterns using the Z framework models.

Features:
- Memory-efficient prime gap generation using segmented sieves
- Low-κ clustering analysis based on Z framework curvature measures
- Statistical analysis and visualization of gap distributions
- Integration with golden ratio transformations and frame shifts

Z Framework References:
- Curvature measure: κ(n) = d(n)·ln(n+1)/e²
- Frame shift: θ'(n,k) = φ·{n/φ}^k where φ = golden ratio
- Universal form: Z = A(B/c) where c is invariant (speed of light)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environment
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Iterator, List, Tuple, Dict, Optional
import time
import gc
from collections import Counter
import scipy.stats as stats
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import warnings

# Import our optimized sieves
from optimized_sieves import OptimizedSieves

warnings.filterwarnings("ignore")

# Z Framework constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
E_SQUARED = np.exp(2)       # e² normalization factor


class PrimeGapAnalyzer:
    """
    Prime gap analysis with Z framework low-κ clustering.
    """
    
    def __init__(self, memory_limit_mb: int = 2000):
        """
        Initialize the prime gap analyzer.
        
        Args:
            memory_limit_mb: Memory limit for sieve operations
        """
        self.memory_limit_mb = memory_limit_mb
        self.sieves = OptimizedSieves(memory_limit_mb=memory_limit_mb)
        self.phi = PHI
        self.e_squared = E_SQUARED
        
    def generate_prime_gaps_streaming(self, limit: int) -> Iterator[Tuple[int, int, int]]:
        """
        Generate prime gaps in a memory-efficient streaming fashion.
        
        Args:
            limit: Upper bound for prime generation
            
        Yields:
            Tuples of (prime_p, prime_q, gap) where gap = q - p
        """
        prev_prime = None
        
        for segment in self.sieves.sieve_of_eratosthenes_segmented(limit):
            for prime in segment:
                if prev_prime is not None:
                    gap = prime - prev_prime
                    yield (prev_prime, prime, gap)
                prev_prime = prime
    
    def compute_curvature_simple(self, n: int) -> float:
        """
        Compute simplified curvature κ(n) = d(n)·ln(n+1)/e² for efficiency.
        
        For large-scale analysis, we use a simplified divisor count estimation.
        
        Args:
            n: Integer to compute curvature for
            
        Returns:
            Curvature value κ(n)
        """
        # Simplified divisor count for efficiency
        if n <= 1:
            return 0.0
        
        # Fast divisor counting for small numbers
        if n <= 1000:
            divisor_count = sum(1 for i in range(1, int(np.sqrt(n)) + 1) 
                              if n % i == 0) * 2
            if int(np.sqrt(n))**2 == n:
                divisor_count -= 1  # Perfect square correction
        else:
            # Use approximation for large numbers: d(n) ≈ log(n)^log(2)
            divisor_count = np.log(n) ** np.log(2)
        
        return divisor_count * np.log(n + 1) / self.e_squared
    
    def compute_frame_shift(self, n: int, k: float = 0.2) -> float:
        """
        Compute frame shift θ'(n,k) = φ·{n/φ}^k.
        
        Args:
            n: Integer position
            k: Curvature exponent (default from proof.py optimal k* = 0.2)
            
        Returns:
            Frame shift value
        """
        mod_phi = (n % self.phi) / self.phi
        return self.phi * (mod_phi ** k)
    
    def analyze_gap_clustering(self, gaps: List[int], gap_positions: List[int], 
                             max_gaps: int = 100000) -> Dict:
        """
        Analyze low-κ clustering in prime gaps using Z framework models.
        
        Args:
            gaps: List of prime gaps
            gap_positions: List of positions where gaps occur
            max_gaps: Maximum number of gaps to analyze for efficiency
            
        Returns:
            Dictionary with clustering analysis results
        """
        # Sample gaps if too many
        if len(gaps) > max_gaps:
            indices = np.random.choice(len(gaps), max_gaps, replace=False)
            gaps = [gaps[i] for i in sorted(indices)]
            gap_positions = [gap_positions[i] for i in sorted(indices)]
        
        gaps = np.array(gaps)
        gap_positions = np.array(gap_positions)
        
        # Compute curvatures for gap positions
        print("Computing curvatures...")
        curvatures = np.array([self.compute_curvature_simple(pos) for pos in gap_positions])
        
        # Compute frame shifts
        print("Computing frame shifts...")
        frame_shifts = np.array([self.compute_frame_shift(pos) for pos in gap_positions])
        
        # Low-κ clustering analysis
        print("Analyzing low-κ clustering...")
        
        # Define low-κ threshold (bottom 25% of curvature values)
        kappa_threshold = np.percentile(curvatures, 25)
        low_kappa_mask = curvatures <= kappa_threshold
        
        low_kappa_gaps = gaps[low_kappa_mask]
        low_kappa_positions = gap_positions[low_kappa_mask]
        low_kappa_curvatures = curvatures[low_kappa_mask]
        low_kappa_frame_shifts = frame_shifts[low_kappa_mask]
        
        # Statistical analysis
        results = {
            'total_gaps': len(gaps),
            'low_kappa_count': len(low_kappa_gaps),
            'low_kappa_fraction': len(low_kappa_gaps) / len(gaps),
            'kappa_threshold': kappa_threshold,
            
            # Gap statistics
            'gap_stats': {
                'all_gaps': {
                    'mean': np.mean(gaps),
                    'std': np.std(gaps),
                    'median': np.median(gaps),
                    'max': np.max(gaps),
                    'min': np.min(gaps)
                },
                'low_kappa_gaps': {
                    'mean': np.mean(low_kappa_gaps),
                    'std': np.std(low_kappa_gaps),
                    'median': np.median(low_kappa_gaps),
                    'max': np.max(low_kappa_gaps) if len(low_kappa_gaps) > 0 else 0,
                    'min': np.min(low_kappa_gaps) if len(low_kappa_gaps) > 0 else 0
                }
            },
            
            # Curvature statistics
            'curvature_stats': {
                'all_curvatures': {
                    'mean': np.mean(curvatures),
                    'std': np.std(curvatures),
                    'median': np.median(curvatures)
                },
                'low_kappa_curvatures': {
                    'mean': np.mean(low_kappa_curvatures),
                    'std': np.std(low_kappa_curvatures),
                    'median': np.median(low_kappa_curvatures)
                }
            },
            
            # Frame shift statistics
            'frame_shift_stats': {
                'all_frame_shifts': {
                    'mean': np.mean(frame_shifts),
                    'std': np.std(frame_shifts),
                    'median': np.median(frame_shifts)
                },
                'low_kappa_frame_shifts': {
                    'mean': np.mean(low_kappa_frame_shifts),
                    'std': np.std(low_kappa_frame_shifts),
                    'median': np.median(low_kappa_frame_shifts)
                }
            }
        }
        
        # Clustering analysis with KMeans
        if len(low_kappa_gaps) > 10:
            print("Performing clustering analysis...")
            
            # Prepare feature matrix: [gap, curvature, frame_shift]
            features = np.column_stack([
                low_kappa_gaps / np.max(low_kappa_gaps),  # Normalized gap
                low_kappa_curvatures / np.max(low_kappa_curvatures),  # Normalized curvature
                low_kappa_frame_shifts / np.max(low_kappa_frame_shifts)  # Normalized frame shift
            ])
            
            # K-means clustering
            n_clusters = min(5, len(low_kappa_gaps) // 10)  # Adaptive cluster count
            if n_clusters >= 2:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(features)
                
                results['clustering'] = {
                    'n_clusters': n_clusters,
                    'cluster_labels': cluster_labels,
                    'cluster_centers': kmeans.cluster_centers_,
                    'inertia': kmeans.inertia_
                }
                
                # Cluster statistics
                cluster_stats = {}
                for i in range(n_clusters):
                    cluster_mask = cluster_labels == i
                    cluster_gaps = low_kappa_gaps[cluster_mask]
                    cluster_curvatures = low_kappa_curvatures[cluster_mask]
                    
                    cluster_stats[f'cluster_{i}'] = {
                        'size': np.sum(cluster_mask),
                        'gap_mean': np.mean(cluster_gaps),
                        'gap_std': np.std(cluster_gaps),
                        'curvature_mean': np.mean(cluster_curvatures),
                        'curvature_std': np.std(cluster_curvatures)
                    }
                
                results['clustering']['cluster_stats'] = cluster_stats
        
        return results
    
    def create_visualizations(self, gaps: List[int], gap_positions: List[int], 
                            analysis_results: Dict, output_prefix: str = "prime_gaps") -> List[str]:
        """
        Create empirical plots for prime gap analysis.
        
        Args:
            gaps: List of prime gaps
            gap_positions: List of positions where gaps occur
            analysis_results: Results from analyze_gap_clustering
            output_prefix: Prefix for output filenames
            
        Returns:
            List of generated plot filenames
        """
        plot_files = []
        
        # Limit data for visualization if too large
        max_viz_points = 10000
        if len(gaps) > max_viz_points:
            indices = np.random.choice(len(gaps), max_viz_points, replace=False)
            gaps_viz = [gaps[i] for i in sorted(indices)]
            positions_viz = [gap_positions[i] for i in sorted(indices)]
        else:
            gaps_viz = gaps
            positions_viz = gap_positions
        
        # Set up matplotlib parameters
        plt.style.use('default')
        fig_size = (12, 8)
        
        # Plot 1: Prime gap distribution
        plt.figure(figsize=fig_size)
        plt.hist(gaps_viz, bins=50, alpha=0.7, edgecolor='black')
        plt.xlabel('Prime Gap Size')
        plt.ylabel('Frequency')
        plt.title('Distribution of Prime Gaps')
        plt.grid(True, alpha=0.3)
        
        # Add statistics text
        stats_text = f"Mean: {analysis_results['gap_stats']['all_gaps']['mean']:.2f}\n"
        stats_text += f"Std: {analysis_results['gap_stats']['all_gaps']['std']:.2f}\n"
        stats_text += f"Median: {analysis_results['gap_stats']['all_gaps']['median']:.2f}"
        plt.text(0.7, 0.8, stats_text, transform=plt.gca().transAxes, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        filename = f"{output_prefix}_distribution.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        plot_files.append(filename)
        
        # Plot 2: Gap size vs position
        plt.figure(figsize=fig_size)
        plt.scatter(positions_viz, gaps_viz, alpha=0.6, s=1)
        plt.xlabel('Prime Position')
        plt.ylabel('Gap to Next Prime')
        plt.title('Prime Gap Size vs Position')
        plt.grid(True, alpha=0.3)
        
        filename = f"{output_prefix}_vs_position.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        plot_files.append(filename)
        
        # Plot 3: Low-κ clustering visualization
        if 'low_kappa_count' in analysis_results and analysis_results['low_kappa_count'] > 0:
            # Compute curvatures for visualization subset
            curvatures_viz = [self.compute_curvature_simple(pos) for pos in positions_viz]
            kappa_threshold = analysis_results['kappa_threshold']
            
            plt.figure(figsize=fig_size)
            
            # Plot all points
            mask_high = np.array(curvatures_viz) > kappa_threshold
            mask_low = np.array(curvatures_viz) <= kappa_threshold
            
            plt.scatter(np.array(positions_viz)[mask_high], np.array(gaps_viz)[mask_high], 
                       alpha=0.6, s=1, color='blue', label='High κ')
            plt.scatter(np.array(positions_viz)[mask_low], np.array(gaps_viz)[mask_low], 
                       alpha=0.8, s=2, color='red', label='Low κ')
            
            plt.xlabel('Prime Position')
            plt.ylabel('Gap to Next Prime')
            plt.title(f'Low-κ Clustering (κ ≤ {kappa_threshold:.3f})')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Add clustering statistics
            stats_text = f"Low-κ fraction: {analysis_results['low_kappa_fraction']:.3f}\n"
            stats_text += f"Low-κ count: {analysis_results['low_kappa_count']}"
            plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                    bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7),
                    verticalalignment='top')
            
            filename = f"{output_prefix}_low_kappa_clustering.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            plot_files.append(filename)
        
        # Plot 4: Curvature distribution
        curvatures_viz = [self.compute_curvature_simple(pos) for pos in positions_viz]
        
        plt.figure(figsize=fig_size)
        plt.hist(curvatures_viz, bins=50, alpha=0.7, edgecolor='black')
        plt.xlabel('Curvature κ(n)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Curvature Values')
        plt.axvline(analysis_results['kappa_threshold'], color='red', linestyle='--', 
                   label=f'Low-κ threshold: {analysis_results["kappa_threshold"]:.3f}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        filename = f"{output_prefix}_curvature_distribution.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        plot_files.append(filename)
        
        return plot_files
    
    def analyze_prime_gaps(self, limit: int, output_prefix: str = "prime_gaps_analysis") -> Dict:
        """
        Complete prime gap analysis for given limit.
        
        Args:
            limit: Upper bound for prime generation
            output_prefix: Prefix for output files
            
        Returns:
            Complete analysis results
        """
        print(f"=== Prime Gap Analysis for N = {limit:,} ===")
        start_time = time.time()
        
        # Generate gaps
        print("Generating prime gaps...")
        gaps = []
        gap_positions = []
        
        gap_count = 0
        for prev_prime, next_prime, gap in self.generate_prime_gaps_streaming(limit):
            gaps.append(gap)
            gap_positions.append(prev_prime)
            gap_count += 1
            
            if gap_count % 100000 == 0:
                print(f"  Processed {gap_count:,} gaps")
        
        print(f"Generated {len(gaps):,} prime gaps")
        
        # Analyze clustering
        print("Analyzing low-κ clustering...")
        analysis_results = self.analyze_gap_clustering(gaps, gap_positions)
        
        # Create visualizations
        print("Creating visualizations...")
        plot_files = self.create_visualizations(gaps, gap_positions, analysis_results, output_prefix)
        
        # Add summary information
        analysis_results['summary'] = {
            'limit': limit,
            'total_gaps_generated': len(gaps),
            'analysis_time_seconds': time.time() - start_time,
            'plot_files': plot_files
        }
        
        return analysis_results


def print_analysis_summary(results: Dict):
    """
    Print a formatted summary of the analysis results.
    
    Args:
        results: Analysis results dictionary
    """
    print("\n" + "="*60)
    print("PRIME GAP ANALYSIS SUMMARY")
    print("="*60)
    
    summary = results['summary']
    print(f"Analysis limit: N = {summary['limit']:,}")
    print(f"Total gaps analyzed: {summary['total_gaps_generated']:,}")
    print(f"Analysis time: {summary['analysis_time_seconds']:.2f} seconds")
    print(f"Generated plots: {len(summary['plot_files'])}")
    
    print(f"\nLow-κ Clustering Results:")
    print(f"  κ threshold: {results['kappa_threshold']:.6f}")
    print(f"  Low-κ gaps: {results['low_kappa_count']:,} ({results['low_kappa_fraction']:.1%})")
    
    print(f"\nGap Statistics:")
    all_gaps = results['gap_stats']['all_gaps']
    low_gaps = results['gap_stats']['low_kappa_gaps']
    print(f"  All gaps   - Mean: {all_gaps['mean']:.2f}, Std: {all_gaps['std']:.2f}, Max: {all_gaps['max']}")
    print(f"  Low-κ gaps - Mean: {low_gaps['mean']:.2f}, Std: {low_gaps['std']:.2f}, Max: {low_gaps['max']}")
    
    if 'clustering' in results:
        clustering = results['clustering']
        print(f"\nClustering Analysis:")
        print(f"  Number of clusters: {clustering['n_clusters']}")
        print(f"  Clustering inertia: {clustering['inertia']:.2f}")
        
        for cluster_name, stats in clustering['cluster_stats'].items():
            print(f"  {cluster_name}: {stats['size']} gaps, "
                  f"gap mean: {stats['gap_mean']:.2f}, "
                  f"κ mean: {stats['curvature_mean']:.6f}")
    
    print(f"\nGenerated visualizations:")
    for plot_file in summary['plot_files']:
        print(f"  - {plot_file}")


if __name__ == "__main__":
    print("=== Prime Gap Analysis with Z Framework Low-κ Clustering ===")
    
    # Test with smaller limits first
    analyzer = PrimeGapAnalyzer(memory_limit_mb=1000)
    
    # Test with N=10^6 first
    print("\n--- Testing with N=10^6 ---")
    results_1m = analyzer.analyze_prime_gaps(1000000, "gaps_1M")
    print_analysis_summary(results_1m)
    
    # Test with N=10^7 
    print("\n--- Testing with N=10^7 ---")
    results_10m = analyzer.analyze_prime_gaps(10000000, "gaps_10M")
    print_analysis_summary(results_10m)