#!/usr/bin/env python3
"""
Fine K-Sweep Analysis for Prime Curvature Metrics
================================================

Performs fine-grained k-value sweep around k=0.3 with Δk=0.002 as specified
in the task requirements. Uses the computed results from large_curvature_metrics.py
to perform detailed analysis around the target k≈0.3 region.

Requirements:
- Fine k sweep with Δk=0.002 around k=0.3
- Target validation: 15% enhancement at k≈0.3
- Bootstrap confidence intervals
- Detailed statistical analysis

Author: Z Framework / Prime Curvature Analysis
"""

import numpy as np
import pandas as pd
import json
import time
import argparse
import mpmath as mp
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import warnings
from pathlib import Path

# Suppress warnings for clean output
warnings.filterwarnings("ignore")

# Set high precision for mpmath calculations
mp.mp.dps = 50

# Mathematical constants
PHI = (1 + mp.sqrt(5)) / 2  # Golden ratio
E = mp.exp(1)               # Euler's number
E_SQUARED = E ** 2          # e^2 normalization factor

class FineKSweepAnalyzer:
    """
    Fine-grained k-value sweep analysis for prime curvature metrics.
    
    Performs detailed analysis around k=0.3 with fine resolution Δk=0.002
    to identify optimal curvature parameters for prime density enhancement.
    """
    
    def __init__(self, csv_filepath):
        """
        Initialize the fine k-sweep analyzer.
        
        Args:
            csv_filepath (str): Path to the curvature metrics CSV file
        """
        self.csv_filepath = csv_filepath
        self.phi_float = float(PHI)
        self.e_squared_float = float(E_SQUARED)
        
        # Load the data
        print(f"Loading data from {csv_filepath}...")
        self.df = pd.read_csv(csv_filepath)
        self.primes_df = self.df[self.df['is_prime'] == True]
        
        print(f"Loaded {len(self.df)} total numbers")
        print(f"Found {len(self.primes_df)} primes")
        print(f"Prime ratio: {len(self.primes_df) / len(self.df):.6f}")
        
        # Results storage
        self.fine_k_results = {}
    
    def compute_theta_prime_fine(self, n_values, k):
        """
        Compute θ'(n,k) for given n values and k parameter.
        
        Args:
            n_values (array): Array of n values
            k (float): Curvature exponent
            
        Returns:
            array: θ'(n,k) values
        """
        n_mod_phi = n_values % self.phi_float
        fractional_part = n_mod_phi / self.phi_float
        theta_prime = self.phi_float * (fractional_part ** k)
        return theta_prime
    
    def compute_density_enhancement(self, theta_all, theta_primes, n_bins=20):
        """
        Compute prime density enhancement across bins.
        
        Args:
            theta_all (array): θ' values for all n
            theta_primes (array): θ' values for primes only
            n_bins (int): Number of bins over [0, φ)
            
        Returns:
            tuple: (all_density, prime_density, enhancement_percent, bin_centers, max_enhancement)
        """
        # Create bins over [0, φ)
        bins = np.linspace(0, self.phi_float, n_bins + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # Compute histograms
        all_counts, _ = np.histogram(theta_all, bins=bins)
        prime_counts, _ = np.histogram(theta_primes, bins=bins)
        
        # Normalize to densities
        all_density = all_counts / len(theta_all) if len(theta_all) > 0 else np.zeros_like(all_counts)
        prime_density = prime_counts / len(theta_primes) if len(theta_primes) > 0 else np.zeros_like(prime_counts)
        
        # Compute enhancement: (d_P - d_N) / d_N * 100
        with np.errstate(divide='ignore', invalid='ignore'):
            enhancement = (prime_density - all_density) / all_density * 100
        
        # Mask invalid enhancements 
        enhancement = np.where(all_density > 0, enhancement, -np.inf)
        
        # Get maximum valid enhancement
        valid_enh = enhancement[enhancement > -np.inf]
        max_enhancement = np.max(valid_enh) if len(valid_enh) > 0 else 0.0
        
        return all_density, prime_density, enhancement, bin_centers, max_enhancement
    
    def bootstrap_confidence_interval(self, theta_primes, n_bootstrap=1000, confidence=0.95):
        """
        Compute bootstrap confidence interval for maximum enhancement.
        
        Args:
            theta_primes (array): θ' values for primes
            n_bootstrap (int): Number of bootstrap samples
            confidence (float): Confidence level
            
        Returns:
            tuple: (lower_bound, upper_bound)
        """
        if len(theta_primes) < 10:  # Need sufficient data
            return (-np.inf, np.inf)
        
        max_enhancements = []
        
        # Generate background distribution (approximating all n values)
        n_background = len(theta_primes) * 15  # Approximate ratio
        
        for _ in range(n_bootstrap):
            # Resample primes with replacement
            resampled_primes = np.random.choice(theta_primes, size=len(theta_primes), replace=True)
            
            # Generate background distribution
            background_theta = np.random.uniform(0, self.phi_float, size=n_background)
            
            # Compute enhancement for resampled data
            try:
                _, _, _, _, max_enh = self.compute_density_enhancement(background_theta, resampled_primes)
                max_enhancements.append(max_enh)
            except:
                max_enhancements.append(0.0)
        
        # Compute confidence interval
        alpha = 1 - confidence
        lower = np.percentile(max_enhancements, 100 * alpha/2)
        upper = np.percentile(max_enhancements, 100 * (1 - alpha/2))
        
        return lower, upper
    
    def fine_k_sweep_analysis(self, k_center=0.3, k_range=0.1, k_delta=0.002):
        """
        Perform fine-grained k-sweep analysis around k_center.
        
        Args:
            k_center (float): Center k value for fine sweep
            k_range (float): Range around k_center (±k_range)
            k_delta (float): Step size for k values
            
        Returns:
            dict: Fine k-sweep results
        """
        print(f"Performing fine k-sweep around k = {k_center}")
        print(f"Range: [{k_center - k_range:.3f}, {k_center + k_range:.3f}]")
        print(f"Step size: Δk = {k_delta}")
        
        # Generate fine k values
        k_min = k_center - k_range
        k_max = k_center + k_range
        k_values = np.arange(k_min, k_max + k_delta, k_delta)
        
        print(f"Analyzing {len(k_values)} k values...")
        
        # Get n values for computation
        n_all = self.df['n'].values
        n_primes = self.primes_df['n'].values
        
        results = {}
        
        for i, k in enumerate(k_values):
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(k_values)} k values...")
            
            # Compute θ'(n,k) for this k
            theta_all = self.compute_theta_prime_fine(n_all, k)
            theta_primes = self.compute_theta_prime_fine(n_primes, k)
            
            # Compute density enhancement
            all_density, prime_density, enhancement, bin_centers, max_enhancement = \
                self.compute_density_enhancement(theta_all, theta_primes)
            
            # Bootstrap confidence interval
            ci_low, ci_high = self.bootstrap_confidence_interval(theta_primes)
            
            # Compute correlations
            kappa_primes = self.primes_df['kappa_n'].values
            theta_sorted = np.sort(theta_primes)
            kappa_sorted = np.sort(kappa_primes)
            
            if len(theta_sorted) > 1 and len(kappa_sorted) > 1:
                try:
                    pearson_r, pearson_p = stats.pearsonr(kappa_sorted, theta_sorted)
                except:
                    pearson_r, pearson_p = 0.0, 1.0
            else:
                pearson_r, pearson_p = 0.0, 1.0
            
            # Store results
            results[k] = {
                'k': k,
                'max_enhancement': max_enhancement,
                'enhancement_CI': [ci_low, ci_high],
                'pearson_r': pearson_r,
                'pearson_p': pearson_p,
                'n_primes': len(theta_primes),
                'enhancement_values': enhancement.tolist(),
                'bin_centers': bin_centers.tolist()
            }
        
        self.fine_k_results = results
        return results
    
    def find_optimal_k(self, target_enhancement=15.0):
        """
        Find optimal k value that maximizes enhancement.
        
        Args:
            target_enhancement (float): Target enhancement threshold
            
        Returns:
            tuple: (optimal_k, max_enhancement, meets_target)
        """
        if not self.fine_k_results:
            print("No fine k-sweep results available")
            return None, 0.0, False
        
        best_k = None
        best_enhancement = -np.inf
        
        for k, results in self.fine_k_results.items():
            enhancement = results['max_enhancement']
            if enhancement > best_enhancement:
                best_enhancement = enhancement
                best_k = k
        
        meets_target = best_enhancement >= target_enhancement
        
        return best_k, best_enhancement, meets_target
    
    def analyze_k_near_target(self, k_target=0.3, tolerance=0.02):
        """
        Analyze k values near the target k=0.3.
        
        Args:
            k_target (float): Target k value
            tolerance (float): Tolerance around target
            
        Returns:
            dict: Analysis results for k values near target
        """
        near_target_results = {}
        
        for k, results in self.fine_k_results.items():
            if abs(k - k_target) <= tolerance:
                near_target_results[k] = results
        
        return near_target_results
    
    def save_fine_k_results(self, output_path):
        """
        Save fine k-sweep results to JSON file.
        
        Args:
            output_path (str): Output file path
        """
        if not self.fine_k_results:
            print("No results to save")
            return
        
        # Prepare output data
        output_data = {
            'analysis_info': {
                'total_numbers': len(self.df),
                'total_primes': len(self.primes_df),
                'prime_ratio': len(self.primes_df) / len(self.df),
                'phi': self.phi_float,
                'e_squared': self.e_squared_float
            },
            'fine_k_results': {}
        }
        
        # Add results for each k (convert numpy types to Python types for JSON)
        for k, results in self.fine_k_results.items():
            output_data['fine_k_results'][str(k)] = {
                'k': float(k),
                'max_enhancement': float(results['max_enhancement']),
                'enhancement_CI': [float(results['enhancement_CI'][0]), float(results['enhancement_CI'][1])],
                'pearson_r': float(results['pearson_r']),
                'pearson_p': float(results['pearson_p']),
                'n_primes': int(results['n_primes'])
            }
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Fine k-sweep results saved to {output_path}")
    
    def generate_summary_report(self):
        """
        Generate a comprehensive summary report.
        
        Returns:
            str: Formatted summary report
        """
        if not self.fine_k_results:
            return "No fine k-sweep results available for reporting"
        
        lines = []
        lines.append("=== FINE K-SWEEP ANALYSIS SUMMARY ===\n")
        
        # Find optimal k
        optimal_k, max_enhancement, meets_target = self.find_optimal_k()
        
        lines.append(f"Dataset: {len(self.df)} numbers, {len(self.primes_df)} primes")
        lines.append(f"Prime ratio: {len(self.primes_df) / len(self.df):.6f}")
        lines.append("")
        
        lines.append(f"OPTIMAL K ANALYSIS:")
        lines.append(f"  Optimal k* = {optimal_k:.6f}")
        lines.append(f"  Maximum enhancement = {max_enhancement:.2f}%")
        
        if optimal_k in self.fine_k_results:
            opt_results = self.fine_k_results[optimal_k]
            ci_low, ci_high = opt_results['enhancement_CI']
            lines.append(f"  Confidence interval = [{ci_low:.2f}%, {ci_high:.2f}%]")
            lines.append(f"  Pearson correlation = {opt_results['pearson_r']:.6f} (p = {opt_results['pearson_p']:.3e})")
        
        lines.append("")
        
        # Target validation
        target_enhancement = 15.0
        target_k = 0.3
        lines.append(f"TARGET VALIDATION (k≈{target_k}, enhancement≥{target_enhancement}%):")
        
        if meets_target and abs(optimal_k - target_k) < 0.05:
            lines.append("  ✓ TARGET ACHIEVED: Optimal k≈0.3 with ≥15% enhancement")
        else:
            lines.append("  ✗ Target not achieved")
            lines.append(f"    Required: k≈{target_k} with ≥{target_enhancement}% enhancement")
            lines.append(f"    Found: k={optimal_k:.6f} with {max_enhancement:.2f}% enhancement")
        
        lines.append("")
        
        # Analysis around k=0.3
        near_target = self.analyze_k_near_target(k_target=0.3, tolerance=0.02)
        lines.append(f"ANALYSIS AROUND k=0.3 (±0.02):")
        lines.append(f"  Found {len(near_target)} k values in range [0.28, 0.32]")
        
        for k in sorted(near_target.keys()):
            results = near_target[k]
            lines.append(f"  k={k:.6f}: {results['max_enhancement']:.2f}% enhancement, r={results['pearson_r']:.3f}")
        
        lines.append("")
        
        # Top 5 k values by enhancement
        sorted_k = sorted(self.fine_k_results.items(), key=lambda x: x[1]['max_enhancement'], reverse=True)
        lines.append("TOP 5 K VALUES BY ENHANCEMENT:")
        for i, (k, results) in enumerate(sorted_k[:5]):
            lines.append(f"  {i+1}. k={k:.6f}: {results['max_enhancement']:.2f}% enhancement, r={results['pearson_r']:.3f}")
        
        lines.append("")
        lines.append("=== END SUMMARY ===")
        
        return "\n".join(lines)
    
    def create_enhancement_plot(self, output_path, figsize=(12, 8)):
        """
        Create a plot of enhancement vs k values.
        
        Args:
            output_path (str): Output file path for the plot
            figsize (tuple): Figure size
        """
        if not self.fine_k_results:
            print("No results to plot")
            return
        
        # Extract data for plotting
        k_values = []
        enhancements = []
        ci_lows = []
        ci_highs = []
        
        for k in sorted(self.fine_k_results.keys()):
            results = self.fine_k_results[k]
            k_values.append(k)
            enhancements.append(results['max_enhancement'])
            ci_lows.append(results['enhancement_CI'][0])
            ci_highs.append(results['enhancement_CI'][1])
        
        k_values = np.array(k_values)
        enhancements = np.array(enhancements)
        ci_lows = np.array(ci_lows)
        ci_highs = np.array(ci_highs)
        
        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot enhancement curve
        ax.plot(k_values, enhancements, 'b-', linewidth=2, label='Max Enhancement')
        
        # Plot confidence intervals
        ax.fill_between(k_values, ci_lows, ci_highs, alpha=0.3, color='blue', label='95% CI')
        
        # Mark target region
        ax.axvline(x=0.3, color='red', linestyle='--', alpha=0.7, label='Target k=0.3')
        ax.axhline(y=15.0, color='orange', linestyle='--', alpha=0.7, label='Target 15% enhancement')
        
        # Find and mark optimal k
        optimal_k, max_enhancement, _ = self.find_optimal_k()
        ax.plot(optimal_k, max_enhancement, 'ro', markersize=8, label=f'Optimal k*={optimal_k:.6f}')
        
        # Formatting
        ax.set_xlabel('k (Curvature Exponent)', fontsize=12)
        ax.set_ylabel('Maximum Enhancement (%)', fontsize=12)
        ax.set_title('Prime Density Enhancement vs Curvature Exponent k\n(Fine K-Sweep Analysis)', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Save plot
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Enhancement plot saved to {output_path}")


def main():
    """Main execution function with command-line interface."""
    
    parser = argparse.ArgumentParser(description='Fine K-Sweep Analysis for Prime Curvature Metrics')
    parser.add_argument('csv_file', help='Path to curvature metrics CSV file')
    parser.add_argument('--output_dir', type=str, default='.', help='Output directory')
    parser.add_argument('--k_center', type=float, default=0.3, help='Center k value for fine sweep')
    parser.add_argument('--k_range', type=float, default=0.1, help='Range around k_center')
    parser.add_argument('--k_delta', type=float, default=0.002, help='Step size for k values')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize analyzer
    analyzer = FineKSweepAnalyzer(args.csv_file)
    
    # Perform fine k-sweep analysis
    start_time = time.time()
    analyzer.fine_k_sweep_analysis(
        k_center=args.k_center,
        k_range=args.k_range,
        k_delta=args.k_delta
    )
    
    analysis_time = time.time() - start_time
    print(f"Fine k-sweep analysis completed in {analysis_time:.1f}s")
    
    # Generate outputs
    base_name = Path(args.csv_file).stem
    
    # Save results
    json_output = output_dir / f"{base_name}_fine_k_sweep.json"
    analyzer.save_fine_k_results(json_output)
    
    # Generate summary report
    summary_report = analyzer.generate_summary_report()
    summary_output = output_dir / f"{base_name}_fine_k_summary.txt"
    
    with open(summary_output, 'w') as f:
        f.write(summary_report)
    
    print(f"Summary report saved to {summary_output}")
    
    # Create enhancement plot
    plot_output = output_dir / f"{base_name}_enhancement_plot.png"
    analyzer.create_enhancement_plot(plot_output)
    
    # Print summary
    print("\n" + summary_report)


if __name__ == "__main__":
    main()