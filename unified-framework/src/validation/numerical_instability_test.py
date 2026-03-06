"""
Comprehensive Numerical Instability and Prime Density Enhancement Testing Framework

This module implements empirical testing of the Z-model geometric prime distribution 
framework for numerical instability and prime density enhancement under the θ'(n, k) 
modular transform, with focus on finite-precision arithmetic effects at large N.

Key Components:
1. Prime sequence generation up to large N (10^6, 10^8, 10^9)
2. Geometric transform θ'(n, k) = φ · {n/φ}^k implementation
3. Gaussian KDE density analysis and enhancement calculation
4. Bootstrap confidence intervals for statistical validation
5. Precision sensitivity testing (float64 vs mpmath high precision)
6. Discrepancy and equidistribution analysis with Weyl bounds
7. Control experiments with non-primes and alternate irrational moduli
8. Comprehensive documentation and reproducible results

Mathematical Foundation:
- φ = (1+√5)/2 ≈ 1.618034 (golden ratio)
- k* ≈ 0.3 (optimal curvature parameter from existing research)
- Expected enhancement ~15% based on prior validation
- Numerical stability threshold: errors > 10^-6

References:
- Weyl, H. (1916). "Über die Gleichverteilung von Zahlen mod. Eins"
- Hardy & Ramanujan (1917). "The normal number of prime factors of a number n"
- Z-framework documentation in repository README.md
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import gaussian_kde
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import sympy
from sympy import primerange, isprime
import mpmath as mp
import math
import sys
import warnings
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Dict, Union, Optional
import seaborn as sns

# Set high precision for mpmath
mp.mp.dps = 50

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set matplotlib backend for headless environment
plt.switch_backend('Agg')

# Set random seeds for reproducibility
np.random.seed(42)

@dataclass
class TestConfiguration:
    """Configuration parameters for numerical instability testing."""
    N_values: List[int] = None
    k_values: List[float] = None
    num_bootstrap: int = 1000
    confidence_level: float = 0.95
    precision_threshold: float = 1e-6
    num_bins: int = 100
    test_alternate_irrationals: bool = True
    
    def __post_init__(self):
        if self.N_values is None:
            self.N_values = [10**4, 10**5, 10**6]  # Start smaller for testing
        if self.k_values is None:
            self.k_values = [0.25, 0.3, 0.35]  # Around optimal k* ≈ 0.3

@dataclass 
class TestResults:
    """Container for test results and metrics."""
    N: int
    k: float
    precision_mode: str
    primes: np.ndarray
    transformed_primes: np.ndarray
    transformed_all: np.ndarray
    enhancement: float
    enhancement_ci: Tuple[float, float]
    discrepancy: float
    kl_divergence: float
    ks_statistic: float
    ks_p_value: float
    computation_time: float
    numerical_errors: Dict[str, float]

class NumericalInstabilityTester:
    """
    Comprehensive testing framework for Z-model numerical instability 
    and prime density enhancement analysis.
    """
    
    def __init__(self, config: TestConfiguration = None):
        self.config = config or TestConfiguration()
        self.phi = self._compute_phi_high_precision()
        self.phi_float = float(self.phi)
        self.results = []
        
    def _compute_phi_high_precision(self) -> mp.mpf:
        """Compute golden ratio with high precision."""
        return (1 + mp.sqrt(5)) / 2
    
    def generate_primes_efficient(self, N: int) -> np.ndarray:
        """
        Generate all primes up to N using efficient sympy.primerange.
        
        Args:
            N: Upper bound for prime generation
            
        Returns:
            numpy array of primes up to N
        """
        print(f"Generating primes up to N={N:,}...")
        start_time = time.time()
        primes = np.array(list(primerange(2, N + 1)), dtype=int)
        end_time = time.time()
        print(f"Generated {len(primes):,} primes in {end_time - start_time:.2f} seconds")
        return primes
    
    def geometric_transform_float64(self, n: Union[int, np.ndarray], k: float) -> Union[float, np.ndarray]:
        """
        Compute θ'(n, k) = φ · {n/φ}^k using standard float64 precision.
        
        Args:
            n: Integer or array of integers
            k: Curvature parameter
            
        Returns:
            Transformed value(s)
        """
        if isinstance(n, np.ndarray):
            frac = np.mod(n, self.phi_float) / self.phi_float
            return self.phi_float * np.power(frac, k)
        else:
            frac = (n % self.phi_float) / self.phi_float
            return self.phi_float * (frac ** k)
    
    def geometric_transform_high_precision(self, n: Union[int, np.ndarray], k: float) -> Union[mp.mpf, np.ndarray]:
        """
        Compute θ'(n, k) = φ · {n/φ}^k using mpmath high precision.
        
        Args:
            n: Integer or array of integers  
            k: Curvature parameter
            
        Returns:
            High precision transformed value(s)
        """
        k_mp = mp.mpf(k)
        
        if isinstance(n, np.ndarray):
            results = []
            for val in n:
                # Convert numpy int to Python int for mpmath compatibility
                n_mp = mp.mpf(int(val))
                frac = (n_mp % self.phi) / self.phi
                result = self.phi * (frac ** k_mp)
                results.append(float(result))
            return np.array(results)
        else:
            # Convert to Python int if it's a numpy int
            if hasattr(n, 'item'):
                n = n.item()
            n_mp = mp.mpf(n)
            frac = (n_mp % self.phi) / self.phi
            return self.phi * (frac ** k_mp)
    
    def compute_density_enhancement_kde(self, transformed_primes: np.ndarray, 
                                       transformed_all: np.ndarray) -> Tuple[float, np.ndarray, np.ndarray]:
        """
        Compute prime density enhancement using Gaussian KDE.
        
        Args:
            transformed_primes: Transformed prime values
            transformed_all: Transformed values for all integers
            
        Returns:
            Tuple of (max_enhancement, kde_primes, kde_all)
        """
        # Create evaluation points
        x_min = 0
        x_max = self.phi_float
        x_eval = np.linspace(x_min, x_max, 1000)
        
        # Compute KDEs
        kde_primes = gaussian_kde(transformed_primes)
        kde_all = gaussian_kde(transformed_all)
        
        # Evaluate densities
        density_primes = kde_primes(x_eval)
        density_all = kde_all(x_eval)
        
        # Compute enhancement
        with np.errstate(divide='ignore', invalid='ignore'):
            enhancement_ratio = density_primes / density_all
            enhancement_ratio = np.nan_to_num(enhancement_ratio, nan=1.0, posinf=1.0)
        
        max_enhancement = np.max(enhancement_ratio) - 1.0
        
        return max_enhancement, density_primes, density_all
    
    def bootstrap_confidence_interval(self, data: np.ndarray, 
                                    statistic_func, 
                                    alpha: float = 0.05) -> Tuple[float, float]:
        """
        Compute bootstrap confidence intervals for a statistic.
        
        Args:
            data: Input data
            statistic_func: Function to compute statistic on resampled data
            alpha: Significance level (default 0.05 for 95% CI)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        n_samples = len(data)
        bootstrap_stats = []
        
        for _ in range(self.config.num_bootstrap):
            # Bootstrap resample
            indices = np.random.choice(n_samples, n_samples, replace=True)
            bootstrap_sample = data[indices]
            
            # Compute statistic
            stat = statistic_func(bootstrap_sample)
            bootstrap_stats.append(stat)
        
        # Compute percentiles
        lower_percentile = 100 * (alpha / 2)
        upper_percentile = 100 * (1 - alpha / 2)
        
        lower_bound = np.percentile(bootstrap_stats, lower_percentile)
        upper_bound = np.percentile(bootstrap_stats, upper_percentile)
        
        return lower_bound, upper_bound
    
    def compute_discrepancy(self, sequence: np.ndarray) -> float:
        """
        Compute discrepancy D_N of a sequence in [0,1).
        
        The discrepancy measures deviation from uniform distribution.
        For well-distributed sequences, we expect D_N = O(1/√N).
        
        Args:
            sequence: Normalized sequence in [0,1)
            
        Returns:
            Discrepancy value
        """
        N = len(sequence)
        sequence_sorted = np.sort(sequence)
        
        # Compute supremum of |F_N(x) - x| where F_N is empirical CDF
        max_discrepancy = 0.0
        
        for i, x in enumerate(sequence_sorted):
            empirical_cdf = (i + 1) / N
            discrepancy = abs(empirical_cdf - x)
            max_discrepancy = max(max_discrepancy, discrepancy)
        
        return max_discrepancy
    
    def compute_numerical_errors(self, n_values: np.ndarray, k: float) -> Dict[str, float]:
        """
        Compare float64 vs high precision results to detect numerical instability.
        
        Args:
            n_values: Array of integer values to test
            k: Curvature parameter
            
        Returns:
            Dictionary of error metrics
        """
        # Sample subset for performance
        sample_size = min(1000, len(n_values))
        sample_indices = np.random.choice(len(n_values), sample_size, replace=False)
        sample_values = n_values[sample_indices]
        
        # Compute with both precisions
        results_float64 = self.geometric_transform_float64(sample_values, k)
        results_high_prec = self.geometric_transform_high_precision(sample_values, k)
        
        # Convert high precision to float for comparison
        if isinstance(results_high_prec, np.ndarray):
            results_high_prec_float = results_high_prec
        else:
            results_high_prec_float = float(results_high_prec)
        
        # Compute error metrics
        absolute_errors = np.abs(results_float64 - results_high_prec_float)
        relative_errors = np.abs(absolute_errors / (np.abs(results_high_prec_float) + 1e-16))
        
        return {
            'max_absolute_error': np.max(absolute_errors),
            'mean_absolute_error': np.mean(absolute_errors),
            'max_relative_error': np.max(relative_errors),
            'mean_relative_error': np.mean(relative_errors),
            'error_threshold_exceeded': np.sum(absolute_errors > self.config.precision_threshold)
        }
    
    def test_control_irrationals(self, n_values: np.ndarray, k: float) -> Dict[str, float]:
        """
        Test alternate irrational moduli as controls.
        
        Args:
            n_values: Array of integers to transform
            k: Curvature parameter
            
        Returns:
            Dictionary of enhancement results for different irrationals
        """
        controls = {
            'sqrt_2': math.sqrt(2),
            'e': math.e,
            'pi': math.pi
        }
        
        results = {}
        
        for name, irrational in controls.items():
            # Transform with alternate irrational
            frac = np.mod(n_values, irrational) / irrational
            transformed = irrational * np.power(frac, k)
            
            # Compute simple enhancement metric (max/min ratio)
            hist, _ = np.histogram(transformed, bins=50)
            hist = hist + 1  # Avoid division by zero
            enhancement = (np.max(hist) / np.mean(hist)) - 1.0
            results[name] = enhancement
            
        return results
    
    def run_comprehensive_test(self, N: int, k: float, precision_mode: str = 'float64') -> TestResults:
        """
        Run comprehensive numerical instability test for given N and k.
        
        Args:
            N: Upper bound for integer sequence
            k: Curvature parameter
            precision_mode: 'float64' or 'high_precision'
            
        Returns:
            TestResults object containing all metrics
        """
        print(f"\n=== Running test: N={N:,}, k={k}, precision={precision_mode} ===")
        start_time = time.time()
        
        # Generate sequences
        primes = self.generate_primes_efficient(N)
        all_integers = np.arange(1, N + 1)
        
        # Apply geometric transform
        if precision_mode == 'float64':
            transformed_primes = self.geometric_transform_float64(primes, k)
            transformed_all = self.geometric_transform_float64(all_integers, k)
        else:
            transformed_primes = self.geometric_transform_high_precision(primes, k)
            transformed_all = self.geometric_transform_high_precision(all_integers, k)
        
        # Normalize to [0,1) for discrepancy analysis
        normalized_primes = transformed_primes / self.phi_float
        
        # Compute density enhancement
        enhancement, _, _ = self.compute_density_enhancement_kde(transformed_primes, transformed_all)
        
        # Bootstrap confidence interval for enhancement
        def enhancement_statistic(sample):
            # Use a subset of all integers for comparison to avoid memory issues
            sample_size = len(sample)
            if sample_size > 1000:
                all_subset = np.random.choice(all_integers, 1000, replace=False)
            else:
                all_subset = np.random.choice(all_integers, sample_size, replace=False)
            
            if precision_mode == 'float64':
                sample_all = self.geometric_transform_float64(all_subset, k)
            else:
                sample_all = self.geometric_transform_high_precision(all_subset, k)
            
            enh, _, _ = self.compute_density_enhancement_kde(sample, sample_all)
            return enh
        
        enhancement_ci = self.bootstrap_confidence_interval(
            transformed_primes, enhancement_statistic)
        
        # Compute discrepancy
        discrepancy = self.compute_discrepancy(normalized_primes)
        
        # Statistical tests
        ks_stat, ks_p = stats.kstest(normalized_primes, 'uniform')
        
        # KL divergence
        hist_primes, _ = np.histogram(normalized_primes, bins=self.config.num_bins, density=True)
        hist_uniform = np.ones(self.config.num_bins) / self.config.num_bins
        hist_primes = hist_primes / np.sum(hist_primes)
        kl_div = stats.entropy(hist_primes + 1e-10, hist_uniform + 1e-10)
        
        # Numerical error analysis
        numerical_errors = self.compute_numerical_errors(primes, k)
        
        end_time = time.time()
        computation_time = end_time - start_time
        
        print(f"Enhancement: {enhancement:.4f}")
        print(f"Enhancement CI: [{enhancement_ci[0]:.4f}, {enhancement_ci[1]:.4f}]")
        print(f"Discrepancy: {discrepancy:.6f}")
        print(f"Expected Weyl bound O(1/√N): {1/math.sqrt(len(primes)):.6f}")
        print(f"KS test: stat={ks_stat:.6f}, p={ks_p:.6f}")
        print(f"Computation time: {computation_time:.2f} seconds")
        
        return TestResults(
            N=N,
            k=k,
            precision_mode=precision_mode,
            primes=primes,
            transformed_primes=transformed_primes,
            transformed_all=transformed_all,
            enhancement=enhancement,
            enhancement_ci=enhancement_ci,
            discrepancy=discrepancy,
            kl_divergence=kl_div,
            ks_statistic=ks_stat,
            ks_p_value=ks_p,
            computation_time=computation_time,
            numerical_errors=numerical_errors
        )
    
    def run_all_tests(self) -> List[TestResults]:
        """
        Run comprehensive test suite across all configured parameters.
        
        Returns:
            List of TestResults for all parameter combinations
        """
        print("=== Starting Comprehensive Numerical Instability Test Suite ===")
        print(f"Configuration: N_values={self.config.N_values}")
        print(f"              k_values={self.config.k_values}")
        print(f"              Bootstrap samples: {self.config.num_bootstrap}")
        print(f"              Precision threshold: {self.config.precision_threshold}")
        
        all_results = []
        
        for N in self.config.N_values:
            for k in self.config.k_values:
                for precision_mode in ['float64', 'high_precision']:
                    try:
                        result = self.run_comprehensive_test(N, k, precision_mode)
                        all_results.append(result)
                        self.results.append(result)
                    except Exception as e:
                        print(f"Error in test N={N}, k={k}, precision={precision_mode}: {e}")
                        continue
        
        print(f"\n=== Completed {len(all_results)} tests ===")
        return all_results
    
    def generate_comprehensive_report(self, results: List[TestResults]) -> str:
        """
        Generate comprehensive analysis report.
        
        Args:
            results: List of test results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE NUMERICAL INSTABILITY TEST REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        enhancements = [r.enhancement for r in results]
        discrepancies = [r.discrepancy for r in results]
        computation_times = [r.computation_time for r in results]
        
        report.append("SUMMARY STATISTICS:")
        report.append(f"Number of tests: {len(results)}")
        report.append(f"Enhancement range: [{np.min(enhancements):.4f}, {np.max(enhancements):.4f}]")
        report.append(f"Mean enhancement: {np.mean(enhancements):.4f} ± {np.std(enhancements):.4f}")
        report.append(f"Discrepancy range: [{np.min(discrepancies):.6f}, {np.max(discrepancies):.6f}]")
        report.append(f"Total computation time: {np.sum(computation_times):.2f} seconds")
        report.append("")
        
        # Detailed results table
        report.append("DETAILED RESULTS:")
        report.append(f"{'N':>8} {'k':>6} {'Precision':>12} {'Enhancement':>12} {'Discrepancy':>12} {'KS_p':>8} {'Time':>8}")
        report.append("-" * 80)
        
        for r in results:
            report.append(f"{r.N:>8,} {r.k:>6.2f} {r.precision_mode:>12} "
                         f"{r.enhancement:>12.4f} {r.discrepancy:>12.6f} "
                         f"{r.ks_p_value:>8.4f} {r.computation_time:>8.1f}")
        
        report.append("")
        
        # Numerical stability analysis
        report.append("NUMERICAL STABILITY ANALYSIS:")
        float64_results = [r for r in results if r.precision_mode == 'float64']
        high_prec_results = [r for r in results if r.precision_mode == 'high_precision']
        
        if float64_results and high_prec_results:
            # Compare corresponding results
            for f64_r, hp_r in zip(float64_results, high_prec_results):
                if f64_r.N == hp_r.N and f64_r.k == hp_r.k:
                    enhancement_diff = abs(f64_r.enhancement - hp_r.enhancement)
                    discrepancy_diff = abs(f64_r.discrepancy - hp_r.discrepancy)
                    report.append(f"N={f64_r.N:,}, k={f64_r.k}: Enhancement diff={enhancement_diff:.6f}, "
                                 f"Discrepancy diff={discrepancy_diff:.6f}")
        
        report.append("")
        
        # Weyl bound analysis
        report.append("WEYL BOUND ANALYSIS:")
        for r in results:
            expected_weyl = 1 / math.sqrt(len(r.primes))
            weyl_ratio = r.discrepancy / expected_weyl
            report.append(f"N={r.N:,}, k={r.k}: D_N={r.discrepancy:.6f}, "
                         f"O(1/√N)={expected_weyl:.6f}, Ratio={weyl_ratio:.2f}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def create_visualizations(self, results: List[TestResults], output_dir: str = "."):
        """
        Create comprehensive visualizations of test results.
        
        Args:
            results: List of test results
            output_dir: Directory to save plots
        """
        print("Generating visualizations...")
        
        # 1. Enhancement vs N and k
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Enhancement vs N
        N_values = sorted(list(set(r.N for r in results)))
        for k in self.config.k_values:
            k_results = [r for r in results if r.k == k and r.precision_mode == 'float64']
            if k_results:
                Ns = [r.N for r in k_results]
                enhancements = [r.enhancement for r in k_results]
                axes[0,0].plot(Ns, enhancements, 'o-', label=f'k={k}')
        
        axes[0,0].set_xlabel('N')
        axes[0,0].set_ylabel('Enhancement')
        axes[0,0].set_title('Prime Density Enhancement vs N')
        axes[0,0].set_xscale('log')
        axes[0,0].legend()
        axes[0,0].grid(True)
        
        # Discrepancy vs N (with Weyl bound)
        for k in self.config.k_values:
            k_results = [r for r in results if r.k == k and r.precision_mode == 'float64']
            if k_results:
                Ns = [r.N for r in k_results]
                discrepancies = [r.discrepancy for r in k_results]
                axes[0,1].plot(Ns, discrepancies, 'o-', label=f'k={k}')
        
        # Plot theoretical Weyl bound
        Ns_theory = np.logspace(3, 6, 100)
        weyl_bound = 1 / np.sqrt(Ns_theory)
        axes[0,1].plot(Ns_theory, weyl_bound, 'k--', label='O(1/√N)', alpha=0.7)
        
        axes[0,1].set_xlabel('N')
        axes[0,1].set_ylabel('Discrepancy')
        axes[0,1].set_title('Discrepancy vs N (with Weyl Bound)')
        axes[0,1].set_xscale('log')
        axes[0,1].set_yscale('log')
        axes[0,1].legend()
        axes[0,1].grid(True)
        
        # Precision comparison
        float64_results = [r for r in results if r.precision_mode == 'float64']
        high_prec_results = [r for r in results if r.precision_mode == 'high_precision']
        
        if float64_results and high_prec_results:
            f64_enh = [r.enhancement for r in float64_results]
            hp_enh = [r.enhancement for r in high_prec_results]
            axes[1,0].scatter(f64_enh, hp_enh, alpha=0.7)
            axes[1,0].plot([min(f64_enh), max(f64_enh)], [min(f64_enh), max(f64_enh)], 'r--')
            axes[1,0].set_xlabel('Float64 Enhancement')
            axes[1,0].set_ylabel('High Precision Enhancement')
            axes[1,0].set_title('Precision Comparison: Enhancement')
            axes[1,0].grid(True)
        
        # Computation time vs N
        for precision in ['float64', 'high_precision']:
            prec_results = [r for r in results if r.precision_mode == precision]
            if prec_results:
                Ns = [r.N for r in prec_results]
                times = [r.computation_time for r in prec_results]
                axes[1,1].scatter(Ns, times, label=precision, alpha=0.7)
        
        axes[1,1].set_xlabel('N')
        axes[1,1].set_ylabel('Computation Time (seconds)')
        axes[1,1].set_title('Computation Time vs N')
        axes[1,1].set_xscale('log')
        axes[1,1].legend()
        axes[1,1].grid(True)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/numerical_instability_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Distribution visualizations for selected cases
        if results:
            # Pick a representative result
            repr_result = results[0]
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # Transformed prime distribution
            axes[0,0].hist(repr_result.transformed_primes, bins=50, density=True, alpha=0.7, 
                          label='Transformed Primes')
            axes[0,0].axhline(1/self.phi_float, color='r', linestyle='--', label='Uniform')
            axes[0,0].set_xlabel('θ\'(p, k)')
            axes[0,0].set_ylabel('Density')
            axes[0,0].set_title(f'Prime Distribution (N={repr_result.N:,}, k={repr_result.k})')
            axes[0,0].legend()
            axes[0,0].grid(True)
            
            # KDE comparison
            x_eval = np.linspace(0, self.phi_float, 200)
            kde_primes = gaussian_kde(repr_result.transformed_primes)
            kde_all = gaussian_kde(repr_result.transformed_all[:len(repr_result.primes)])
            
            axes[0,1].plot(x_eval, kde_primes(x_eval), label='Primes KDE', linewidth=2)
            axes[0,1].plot(x_eval, kde_all(x_eval), label='All Integers KDE', linewidth=2)
            axes[0,1].set_xlabel('θ\'(n, k)')
            axes[0,1].set_ylabel('Density')
            axes[0,1].set_title('KDE Comparison')
            axes[0,1].legend()
            axes[0,1].grid(True)
            
            # Enhancement ratio
            with np.errstate(divide='ignore', invalid='ignore'):
                enhancement_ratio = kde_primes(x_eval) / kde_all(x_eval)
                enhancement_ratio = np.nan_to_num(enhancement_ratio, nan=1.0, posinf=1.0)
            
            axes[1,0].plot(x_eval, enhancement_ratio, linewidth=2)
            axes[1,0].axhline(1.0, color='r', linestyle='--', alpha=0.7)
            axes[1,0].set_xlabel('θ\'(n, k)')
            axes[1,0].set_ylabel('Enhancement Ratio')
            axes[1,0].set_title('Prime/All Density Ratio')
            axes[1,0].grid(True)
            
            # Normalized sequence (for discrepancy visualization)
            normalized = repr_result.transformed_primes / self.phi_float
            sorted_norm = np.sort(normalized)
            empirical_cdf = np.arange(1, len(sorted_norm) + 1) / len(sorted_norm)
            
            axes[1,1].plot(sorted_norm, empirical_cdf, label='Empirical CDF', linewidth=1)
            axes[1,1].plot([0, 1], [0, 1], 'r--', label='Uniform CDF', alpha=0.7)
            axes[1,1].set_xlabel('Normalized θ\'(p, k)')
            axes[1,1].set_ylabel('CDF')
            axes[1,1].set_title(f'Equidistribution Test (D_N={repr_result.discrepancy:.4f})')
            axes[1,1].legend()
            axes[1,1].grid(True)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/distribution_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Visualizations saved to {output_dir}/")

def main():
    """Main function to run comprehensive numerical instability tests."""
    print("Initializing Numerical Instability Tester...")
    
    # Configure test parameters - start with small test
    config = TestConfiguration(
        N_values=[1000, 5000],  # Very small for initial testing
        k_values=[0.3],  # Just test the optimal value
        num_bootstrap=20,  # Very reduced for speed
        confidence_level=0.95,
        precision_threshold=1e-6,
        num_bins=20
    )
    
    # Initialize tester
    tester = NumericalInstabilityTester(config)
    
    # Run all tests
    results = tester.run_all_tests()
    
    if results:
        # Generate report
        report = tester.generate_comprehensive_report(results)
        print("\n" + report)
        
        # Save report to file
        with open('numerical_instability_report.txt', 'w') as f:
            f.write(report)
        
        # Create visualizations
        tester.create_visualizations(results)
        
        print("\nTest completed successfully!")
        print("Files generated:")
        print("- numerical_instability_report.txt")
        print("- numerical_instability_analysis.png")
        print("- distribution_analysis.png")
    else:
        print("No test results generated. Check for errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()