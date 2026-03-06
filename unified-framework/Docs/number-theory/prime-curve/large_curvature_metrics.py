#!/usr/bin/env python3
"""
Large-Scale Prime Curvature Metrics Computation
==============================================

Objective: Validate κ(n), θ'(n,k), and prime density enhancement for N up to 10^6, 
extending to 10^9 if feasible. Test geodesic replacement of ratios, targeting 15% 
enhancement at k≈0.3.

Requirements:
- N_start = 900001, N_end = 10^6 (scale to 10^9 in batches)
- k_values = [0.2, 0.24, 0.28, 0.3, 0.32, 0.36, 0.4] (sweep with Δk=0.002)
- φ = (1 + mpmath.sqrt(5))/2; e = mpmath.exp(1)
- Use sympy.ntheory.primetest.isprime for prime checks
- Use sympy.ntheory.divisors for d(n)

Output:
- CSV: columns [n, is_prime, κ_n, θ_prime_n_0.3, ...]
- Metrics JSON: {"k": k_values, "e_max": [...], "e_max_CI": [[low, high], ...]}
- Histogram analysis descriptions

Author: Z Framework / Prime Curvature Analysis
"""

import numpy as np
import pandas as pd
import json
import time
import argparse
import mpmath as mp
from sympy.ntheory import isprime, divisors
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

class LargeCurvatureMetrics:
    """
    Large-scale computation of prime curvature metrics using the Z framework.
    
    Computes κ(n) curvature and θ'(n,k) transformations for extensive ranges,
    with memory-efficient batching and statistical analysis.
    """
    
    def __init__(self, n_start=900001, n_end=1000000, batch_size=10000):
        """
        Initialize the large curvature metrics computation.
        
        Args:
            n_start (int): Starting value for n range
            n_end (int): Ending value for n range  
            batch_size (int): Batch size for memory management
        """
        self.n_start = n_start
        self.n_end = n_end
        self.batch_size = batch_size
        self.phi_float = float(PHI)
        self.e_squared_float = float(E_SQUARED)
        
        # Results storage
        self.results = []
        self.k_sweep_results = {}
        
        print(f"Initialized LargeCurvatureMetrics for range [{n_start}, {n_end}]")
        print(f"Batch size: {batch_size}")
        print(f"φ = {self.phi_float:.10f}")
        print(f"e² = {self.e_squared_float:.10f}")
    
    def compute_curvature_kappa(self, n):
        """
        Compute the frame-normalized curvature κ(n) for integer n.
        
        κ(n) = d(n) * ln(n+1) / e²
        
        Args:
            n (int): Input integer
            
        Returns:
            float: Curvature value κ(n)
        """
        try:
            d_n = len(divisors(n))  # Divisor count
            ln_n_plus_1 = mp.log(n + 1)
            kappa = d_n * ln_n_plus_1 / E_SQUARED
            return float(kappa)
        except Exception as e:
            print(f"Error computing κ({n}): {e}")
            return 0.0
    
    def compute_theta_prime(self, n, k):
        """
        Compute θ'(n,k) = φ * ((n % φ)/φ)^k transformation.
        
        Args:
            n (int): Input integer
            k (float): Curvature exponent
            
        Returns:
            float: Transformed value θ'(n,k)
        """
        try:
            n_mod_phi = n % self.phi_float
            fractional_part = n_mod_phi / self.phi_float
            theta_prime = self.phi_float * (fractional_part ** k)
            return theta_prime
        except Exception as e:
            print(f"Error computing θ'({n},{k}): {e}")
            return 0.0
    
    def compute_batch_metrics(self, n_batch, k_values):
        """
        Compute metrics for a batch of n values.
        
        Args:
            n_batch (list): List of n values to process
            k_values (list): List of k exponents to test
            
        Returns:
            list: Batch results with metrics per n
        """
        batch_results = []
        
        for n in n_batch:
            # Check if n is prime
            is_prime_n = isprime(n)
            
            # Compute curvature κ(n)
            kappa_n = self.compute_curvature_kappa(n)
            
            # Compute θ'(n,k) for each k value
            theta_primes = {}
            for k in k_values:
                theta_primes[f'theta_prime_k_{k:.3f}'] = self.compute_theta_prime(n, k)
            
            # Store result
            result = {
                'n': n,
                'is_prime': is_prime_n,
                'kappa_n': kappa_n,
                **theta_primes
            }
            batch_results.append(result)
        
        return batch_results
    
    def compute_density_enhancement(self, theta_all, theta_primes, n_bins=20):
        """
        Compute prime density enhancement across bins.
        
        Args:
            theta_all (array): θ' values for all n
            theta_primes (array): θ' values for primes only
            n_bins (int): Number of bins over [0, φ)
            
        Returns:
            tuple: (all_density, prime_density, enhancement_percent, bin_centers)
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
        
        return all_density, prime_density, enhancement, bin_centers
    
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
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            resampled = np.random.choice(theta_primes, size=len(theta_primes), replace=True)
            
            # Compute enhancement for resampled data
            try:
                all_theta = np.random.uniform(0, self.phi_float, size=len(theta_primes) * 10)  # Approximate all distribution
                _, _, enhancement, _ = self.compute_density_enhancement(all_theta, resampled)
                
                # Get maximum valid enhancement
                valid_enh = enhancement[enhancement > -np.inf]
                if len(valid_enh) > 0:
                    max_enhancements.append(np.max(valid_enh))
                else:
                    max_enhancements.append(0.0)
            except:
                max_enhancements.append(0.0)
        
        # Compute confidence interval
        alpha = 1 - confidence
        lower = np.percentile(max_enhancements, 100 * alpha/2)
        upper = np.percentile(max_enhancements, 100 * (1 - alpha/2))
        
        return lower, upper
    
    def analyze_k_sweep(self, k_values, fine_k_delta=0.002):
        """
        Perform detailed k-value sweep analysis.
        
        Args:
            k_values (list): Coarse k values to analyze
            fine_k_delta (float): Fine-tuning delta for k sweep
            
        Returns:
            dict: K-sweep results with enhancements and statistics
        """
        print(f"Analyzing k-sweep for {len(k_values)} coarse values...")
        
        # Convert results to DataFrame for analysis
        df = pd.DataFrame(self.results)
        
        if len(df) == 0:
            print("No results available for k-sweep analysis")
            return {}
        
        primes_df = df[df['is_prime'] == True]
        
        k_sweep_results = {}
        
        for k in k_values:
            print(f"  Analyzing k = {k:.3f}...")
            
            col_name = f'theta_prime_k_{k:.3f}'
            if col_name not in df.columns:
                print(f"    Column {col_name} not found, skipping...")
                continue
            
            # Get θ' values for all n and primes
            theta_all = df[col_name].values
            theta_primes = primes_df[col_name].values
            
            if len(theta_primes) == 0:
                print(f"    No primes found for k = {k:.3f}, skipping...")
                continue
            
            # Compute density enhancement
            all_density, prime_density, enhancement, bin_centers = \
                self.compute_density_enhancement(theta_all, theta_primes)
            
            # Get maximum enhancement
            valid_enh = enhancement[enhancement > -np.inf]
            e_max = np.max(valid_enh) if len(valid_enh) > 0 else 0.0
            
            # Bootstrap confidence interval
            ci_low, ci_high = self.bootstrap_confidence_interval(theta_primes)
            
            # Compute additional statistics
            mean_kappa_primes = primes_df['kappa_n'].mean()
            mean_kappa_composites = df[df['is_prime'] == False]['kappa_n'].mean()
            
            # Pearson correlation between κ and sorted θ'
            theta_sorted = np.sort(theta_primes)
            kappa_sorted = np.sort(primes_df['kappa_n'].values)
            
            if len(theta_sorted) > 1 and len(kappa_sorted) > 1:
                try:
                    pearson_r, pearson_p = stats.pearsonr(kappa_sorted, theta_sorted)
                except:
                    pearson_r, pearson_p = 0.0, 1.0
            else:
                pearson_r, pearson_p = 0.0, 1.0
            
            k_sweep_results[k] = {
                'e_max': e_max,
                'e_max_CI': [ci_low, ci_high],
                'mean_kappa_primes': mean_kappa_primes,
                'mean_kappa_composites': mean_kappa_composites,
                'pearson_r': pearson_r,
                'pearson_p': pearson_p,
                'n_primes': len(theta_primes),
                'enhancement_values': enhancement.tolist(),
                'bin_centers': bin_centers.tolist()
            }
            
            print(f"    e_max = {e_max:.1f}%, CI = [{ci_low:.1f}, {ci_high:.1f}]")
            print(f"    Pearson r = {pearson_r:.3f} (p = {pearson_p:.3e})")
        
        return k_sweep_results
    
    def run_computation(self, k_values):
        """
        Run the complete large-scale curvature metrics computation.
        
        Args:
            k_values (list): List of k exponents to analyze
        """
        print(f"Starting computation for range [{self.n_start}, {self.n_end}]")
        print(f"K values: {k_values}")
        
        total_n = self.n_end - self.n_start + 1
        n_batches = (total_n + self.batch_size - 1) // self.batch_size
        
        print(f"Total n values: {total_n}")
        print(f"Number of batches: {n_batches}")
        
        start_time = time.time()
        
        # Process in batches
        for batch_idx in range(n_batches):
            batch_start = self.n_start + batch_idx * self.batch_size
            batch_end = min(batch_start + self.batch_size - 1, self.n_end)
            
            print(f"Processing batch {batch_idx + 1}/{n_batches}: [{batch_start}, {batch_end}]")
            
            # Create batch of n values
            n_batch = list(range(batch_start, batch_end + 1))
            
            # Compute metrics for batch
            batch_results = self.compute_batch_metrics(n_batch, k_values)
            
            # Add to results
            self.results.extend(batch_results)
            
            # Progress update
            elapsed = time.time() - start_time
            progress = (batch_idx + 1) / n_batches
            estimated_total = elapsed / progress if progress > 0 else 0
            remaining = estimated_total - elapsed
            
            print(f"  Batch completed in {elapsed:.1f}s, estimated remaining: {remaining:.1f}s")
        
        total_time = time.time() - start_time
        print(f"Computation completed in {total_time:.1f}s")
        print(f"Computed metrics for {len(self.results)} values")
        
        # Analyze k-sweep
        print("Starting k-sweep analysis...")
        self.k_sweep_results = self.analyze_k_sweep(k_values)
    
    def save_csv_results(self, filename):
        """
        Save detailed results to CSV.
        
        Args:
            filename (str): Output CSV filename
        """
        if not self.results:
            print("No results to save")
            return
        
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} results to {filename}")
        
        # Print sample statistics
        primes_count = df['is_prime'].sum()
        total_count = len(df)
        prime_ratio = primes_count / total_count if total_count > 0 else 0
        
        print(f"Statistics: {primes_count} primes out of {total_count} numbers ({prime_ratio:.4f} ratio)")
    
    def save_json_metrics(self, filename):
        """
        Save k-sweep metrics to JSON.
        
        Args:
            filename (str): Output JSON filename
        """
        if not self.k_sweep_results:
            print("No k-sweep results to save")
            return
        
        # Prepare summary metrics
        summary = {
            'computation_info': {
                'n_start': self.n_start,
                'n_end': self.n_end,
                'total_computed': len(self.results),
                'phi': self.phi_float,
                'e_squared': self.e_squared_float
            },
            'k_sweep_results': {}
        }
        
        # Add k-sweep results
        for k, metrics in self.k_sweep_results.items():
            summary['k_sweep_results'][str(k)] = {
                'k': k,
                'e_max': metrics['e_max'],
                'e_max_CI': metrics['e_max_CI'],
                'mean_kappa_primes': metrics['mean_kappa_primes'],
                'mean_kappa_composites': metrics['mean_kappa_composites'],
                'pearson_r': metrics['pearson_r'],
                'pearson_p': metrics['pearson_p'],
                'n_primes': metrics['n_primes']
            }
        
        # Save to JSON
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Saved k-sweep metrics to {filename}")
    
    def generate_histogram_descriptions(self):
        """
        Generate text descriptions of histogram analysis.
        
        Returns:
            str: Formatted histogram analysis description
        """
        if not self.k_sweep_results:
            return "No k-sweep results available for histogram analysis"
        
        descriptions = []
        descriptions.append("=== Histogram Analysis Descriptions ===\n")
        
        for k, metrics in self.k_sweep_results.items():
            descriptions.append(f"K = {k:.3f}:")
            descriptions.append(f"  Maximum enhancement: {metrics['e_max']:.1f}%")
            descriptions.append(f"  Confidence interval: [{metrics['e_max_CI'][0]:.1f}%, {metrics['e_max_CI'][1]:.1f}%]")
            descriptions.append(f"  Primes analyzed: {metrics['n_primes']}")
            descriptions.append(f"  Pearson correlation: r = {metrics['pearson_r']:.3f} (p = {metrics['pearson_p']:.3e})")
            
            # Find best enhancement bin
            enhancements = np.array(metrics['enhancement_values'])
            valid_enh = enhancements[enhancements > -np.inf]
            
            if len(valid_enh) > 0:
                best_bin_idx = np.argmax(enhancements)
                best_enhancement = enhancements[best_bin_idx]
                bin_center = metrics['bin_centers'][best_bin_idx]
                
                descriptions.append(f"  Best bin: bin {best_bin_idx} (center θ' = {bin_center:.3f}) shows {best_enhancement:.1f}% enhancement")
            
            descriptions.append("")
        
        return "\n".join(descriptions)


def main():
    """Main execution function with command-line interface."""
    
    parser = argparse.ArgumentParser(description='Large-Scale Prime Curvature Metrics Computation')
    parser.add_argument('--n_start', type=int, default=900001, help='Starting n value')
    parser.add_argument('--n_end', type=int, default=1000000, help='Ending n value')
    parser.add_argument('--batch_size', type=int, default=10000, help='Batch size for processing')
    parser.add_argument('--output_dir', type=str, default='.', help='Output directory')
    parser.add_argument('--test_run', action='store_true', help='Run on smaller test range')
    
    args = parser.parse_args()
    
    # Test run on smaller range for validation
    if args.test_run:
        args.n_start = 1000
        args.n_end = 2000
        args.batch_size = 500
        print("TEST RUN MODE: Using smaller range for validation")
    
    # K values to analyze
    k_values = [0.2, 0.24, 0.28, 0.3, 0.32, 0.36, 0.4]
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize and run computation
    lcm = LargeCurvatureMetrics(
        n_start=args.n_start,
        n_end=args.n_end,
        batch_size=args.batch_size
    )
    
    # Run computation
    lcm.run_computation(k_values)
    
    # Generate output filenames
    n_suffix = f"N{args.n_end}"
    csv_filename = output_dir / f"curvature_metrics_{n_suffix}.csv"
    json_filename = output_dir / f"curvature_metrics_{n_suffix}.json"
    
    # Save results
    lcm.save_csv_results(csv_filename)
    lcm.save_json_metrics(json_filename)
    
    # Generate and save histogram descriptions
    hist_descriptions = lcm.generate_histogram_descriptions()
    hist_filename = output_dir / f"histogram_analysis_{n_suffix}.txt"
    
    with open(hist_filename, 'w') as f:
        f.write(hist_descriptions)
    
    print(f"Histogram analysis saved to {hist_filename}")
    print("\n" + hist_descriptions)
    
    # Summary of key findings
    print("\n=== SUMMARY OF KEY FINDINGS ===")
    
    best_k = None
    best_enhancement = -np.inf
    
    for k, metrics in lcm.k_sweep_results.items():
        if metrics['e_max'] > best_enhancement:
            best_enhancement = metrics['e_max']
            best_k = k
    
    if best_k is not None:
        print(f"Optimal k* = {best_k:.3f}")
        print(f"Maximum enhancement = {best_enhancement:.1f}%")
        
        metrics = lcm.k_sweep_results[best_k]
        print(f"Confidence interval = [{metrics['e_max_CI'][0]:.1f}%, {metrics['e_max_CI'][1]:.1f}%]")
        print(f"Pearson correlation = {metrics['pearson_r']:.3f} (p = {metrics['pearson_p']:.3e})")
        
        # Check target validation
        if abs(best_k - 0.3) < 0.05 and best_enhancement >= 15.0:
            print("✓ TARGET VALIDATION PASSED: k≈0.3 with ≥15% enhancement")
        else:
            print("✗ Target validation: Expected k≈0.3 with ≥15% enhancement")
    
    print("\nComputation completed successfully!")


if __name__ == "__main__":
    main()