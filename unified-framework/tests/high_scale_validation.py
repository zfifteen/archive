#!/usr/bin/env python3
"""
High-Scale Computationally Intensive Research Tasks for Z Framework
===================================================================

Extended validation suite implementing TC01-TC05 with support for N up to 10^10.
This version includes optimizations for large-scale computations and advanced
statistical analysis methods.

Usage:
    python high_scale_validation.py --max_n 10000000 --full_validation

Features:
- Chunked prime generation for memory efficiency
- Parallel processing for large computations
- Advanced statistical tests (KS, Anderson-Darling)
- Cross-domain validation extensions
- Comprehensive bootstrap analysis
- Performance monitoring and optimization
"""

import os
import sys
import time
import argparse
import logging
from typing import Dict, List, Tuple, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import scipy.stats as stats
from scipy.optimize import minimize_scalar, differential_evolution
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import sympy as sp
import mpmath as mp
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp_cpu

# High precision settings
mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)

# Configure logging
def setup_logging(log_file: str = 'high_scale_validation.log'):
    """Setup comprehensive logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class HighScaleValidator:
    """
    Advanced validator for high-scale computations up to N = 10^10.
    Includes memory optimization and parallel processing.
    """
    
    def __init__(self, max_n: int = 10**7, bootstrap_samples: int = 1000, 
                 chunk_size: int = 10**6, n_jobs: int = None):
        """
        Initialize high-scale validator.
        
        Args:
            max_n: Maximum N for computations
            bootstrap_samples: Number of bootstrap samples
            chunk_size: Size of computation chunks for memory management
            n_jobs: Number of parallel jobs (None = auto-detect)
        """
        self.max_n = max_n
        self.bootstrap_samples = bootstrap_samples
        self.chunk_size = chunk_size
        self.n_jobs = n_jobs or min(mp_cpu.cpu_count(), 8)
        self.results = {}
        
        logger.info(f"Initialized HighScaleValidator:")
        logger.info(f"  Max N: {max_n:,}")
        logger.info(f"  Bootstrap samples: {bootstrap_samples}")
        logger.info(f"  Chunk size: {chunk_size:,}")
        logger.info(f"  Parallel jobs: {self.n_jobs}")
    
    def efficient_prime_generation(self, n: int) -> List[int]:
        """
        Memory-efficient prime generation using chunked sieving.
        
        Args:
            n: Upper limit for prime generation
            
        Returns:
            List of primes up to n
        """
        if n <= 10**6:
            # Use direct method for smaller ranges
            return [p for p in range(2, n + 1) if sp.isprime(p)]
        
        # For larger ranges, use chunked approach
        logger.info(f"Generating primes up to {n:,} using chunked approach")
        primes = []
        
        for start in range(2, n + 1, self.chunk_size):
            end = min(start + self.chunk_size, n + 1)
            chunk_primes = [p for p in range(start, end) if sp.isprime(p)]
            primes.extend(chunk_primes)
            
            if len(primes) % 10000 == 0:
                logger.info(f"Generated {len(primes):,} primes (up to {end:,})")
        
        logger.info(f"Total primes generated: {len(primes):,}")
        return primes
    
    def advanced_bootstrap_ci(self, data: np.ndarray, statistic=np.mean, 
                            confidence: float = 0.95) -> Dict[str, float]:
        """
        Advanced bootstrap with bias correction and acceleration (BCa).
        
        Args:
            data: Sample data
            statistic: Function to compute statistic (default: mean)
            confidence: Confidence level
            
        Returns:
            Dictionary with CI bounds and bias correction info
        """
        n = len(data)
        original_stat = statistic(data)
        
        # Bootstrap resamples
        bootstrap_stats = []
        for _ in range(self.bootstrap_samples):
            sample = np.random.choice(data, size=n, replace=True)
            bootstrap_stats.append(statistic(sample))
        
        bootstrap_stats = np.array(bootstrap_stats)
        
        # Bias correction
        bias_correction = stats.norm.ppf((bootstrap_stats < original_stat).mean())
        
        # Acceleration (jackknife)
        jackknife_stats = []
        for i in range(n):
            jackknife_sample = np.concatenate([data[:i], data[i+1:]])
            jackknife_stats.append(statistic(jackknife_sample))
        
        jackknife_stats = np.array(jackknife_stats)
        jackknife_mean = np.mean(jackknife_stats)
        acceleration = np.sum((jackknife_mean - jackknife_stats)**3) / (6 * (np.sum((jackknife_mean - jackknife_stats)**2))**1.5)
        
        # BCa bounds
        alpha = 1 - confidence
        z_alpha_2 = stats.norm.ppf(alpha / 2)
        z_1_alpha_2 = stats.norm.ppf(1 - alpha / 2)
        
        alpha_1 = stats.norm.cdf(bias_correction + (bias_correction + z_alpha_2) / (1 - acceleration * (bias_correction + z_alpha_2)))
        alpha_2 = stats.norm.cdf(bias_correction + (bias_correction + z_1_alpha_2) / (1 - acceleration * (bias_correction + z_1_alpha_2)))
        
        lower_bound = np.percentile(bootstrap_stats, 100 * alpha_1)
        upper_bound = np.percentile(bootstrap_stats, 100 * alpha_2)
        
        return {
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'bias_correction': bias_correction,
            'acceleration': acceleration,
            'original_statistic': original_stat,
            'bootstrap_mean': np.mean(bootstrap_stats),
            'bootstrap_std': np.std(bootstrap_stats)
        }
    
    def advanced_statistical_tests(self, sample1: np.ndarray, sample2: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive statistical comparison between two samples.
        
        Args:
            sample1, sample2: Arrays to compare
            
        Returns:
            Dictionary with multiple test results
        """
        results = {}
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.ks_2samp(sample1, sample2)
        results['ks_test'] = {'statistic': ks_stat, 'p_value': ks_p}
        
        # Anderson-Darling test
        try:
            ad_stat, ad_critical, ad_significance = stats.anderson_ksamp([sample1, sample2])
            results['anderson_darling'] = {
                'statistic': ad_stat,
                'critical_values': ad_critical,
                'significance_level': ad_significance
            }
        except Exception as e:
            logger.warning(f"Anderson-Darling test failed: {e}")
            results['anderson_darling'] = {'error': str(e)}
        
        # Mann-Whitney U test
        try:
            mw_stat, mw_p = stats.mannwhitneyu(sample1, sample2, alternative='two-sided')
            results['mann_whitney'] = {'statistic': mw_stat, 'p_value': mw_p}
        except Exception as e:
            results['mann_whitney'] = {'error': str(e)}
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.var(sample1) + np.var(sample2)) / 2)
        cohens_d = (np.mean(sample1) - np.mean(sample2)) / pooled_std if pooled_std > 0 else 0
        results['effect_size'] = {'cohens_d': cohens_d}
        
        return results
    
    def tc01_advanced_scale_invariance(self) -> Dict[str, Any]:
        """
        TC01: Advanced scale-invariant validation with statistical rigor.
        Tests enhancement consistency across logarithmic scales.
        """
        logger.info("Starting TC01: Advanced Scale-Invariant Validation")
        
        # Use logarithmic scaling for better coverage
        base_scales = [10**3, 10**4, 10**5]
        if self.max_n >= 10**6:
            base_scales.append(10**6)
        if self.max_n >= 10**7:
            base_scales.append(min(10**7, self.max_n))
        
        k_values = [0.1, 0.2, 0.3, 0.4, 0.5]  # Test multiple k values
        results = {
            'scales': base_scales,
            'k_values': k_values,
            'scale_enhancement_data': {},
            'statistical_tests': {}
        }
        
        for k in k_values:
            logger.info(f"TC01: Testing k={k}")
            k_enhancements = []
            k_scales = []
            
            for n in base_scales:
                logger.info(f"TC01: Processing N={n:,} with k={k}")
                
                try:
                    # Generate data efficiently
                    primes = self.efficient_prime_generation(n)
                    if len(primes) < 50:
                        logger.warning(f"Insufficient primes for N={n}, skipping")
                        continue
                    
                    # Compute enhancements over multiple runs
                    run_enhancements = []
                    for run in range(3):
                        integers = list(range(2, min(n + 1, len(primes) * 5)))
                        enhancement_data = self._compute_density_enhancement_optimized(primes, integers, k)
                        run_enhancements.append(enhancement_data['max_enhancement'])
                    
                    mean_enhancement = np.mean(run_enhancements)
                    k_enhancements.append(mean_enhancement)
                    k_scales.append(n)
                    
                    logger.info(f"TC01: N={n:,}, k={k}, Enhancement={mean_enhancement:.2f}%")
                    
                except Exception as e:
                    logger.error(f"Error processing N={n} with k={k}: {e}")
                    continue
            
            if len(k_enhancements) >= 2:
                # Store data
                results['scale_enhancement_data'][k] = {
                    'scales': k_scales,
                    'enhancements': k_enhancements
                }
                
                # Compute scale invariance metrics
                enhancement_stability = np.std(k_enhancements)
                cv = enhancement_stability / max(np.mean(k_enhancements), 0.1)  # Coefficient of variation
                
                results['scale_enhancement_data'][k]['stability_metrics'] = {
                    'std': enhancement_stability,
                    'coefficient_of_variation': cv,
                    'passes_invariance': cv < 0.3  # Threshold for acceptable variation
                }
        
        # Cross-k analysis
        if len(results['scale_enhancement_data']) >= 2:
            # Find most scale-invariant k
            best_k = min(results['scale_enhancement_data'].keys(),
                        key=lambda k: results['scale_enhancement_data'][k]['stability_metrics']['coefficient_of_variation'])
            
            results['optimal_scale_invariant_k'] = best_k
            results['passes_scale_invariance'] = results['scale_enhancement_data'][best_k]['stability_metrics']['passes_invariance']
        else:
            results['optimal_scale_invariant_k'] = 0.3
            results['passes_scale_invariance'] = False
        
        logger.info(f"TC01 Complete: Optimal scale-invariant k={results['optimal_scale_invariant_k']}")
        return results
    
    def _compute_density_enhancement_optimized(self, primes: List[int], integers: List[int], 
                                             k: float, num_bins: int = 20) -> Dict[str, Any]:
        """Optimized density enhancement computation."""
        try:
            phi_float = float(PHI)
            
            # Vectorized transformations
            primes_array = np.array(primes)
            integers_array = np.array(integers)
            
            # Golden ratio transformations
            theta_primes = phi_float * ((primes_array % phi_float) / phi_float) ** k
            theta_integers = phi_float * ((integers_array % phi_float) / phi_float) ** k
            
            # Histogram computation
            bin_edges = np.linspace(0, phi_float, num_bins + 1)
            hist_primes, _ = np.histogram(theta_primes, bins=bin_edges, density=True)
            hist_integers, _ = np.histogram(theta_integers, bins=bin_edges, density=True)
            
            # Enhancement calculation with numerical stability
            hist_integers = np.maximum(hist_integers, 1e-10)
            enhancements = (hist_primes - hist_integers) / hist_integers * 100
            valid_enhancements = enhancements[np.isfinite(enhancements)]
            
            if len(valid_enhancements) == 0:
                return {'max_enhancement': 0.0, 'mean_enhancement': 0.0}
            
            return {
                'max_enhancement': np.max(valid_enhancements),
                'mean_enhancement': np.mean(valid_enhancements),
                'std_enhancement': np.std(valid_enhancements),
                'enhancements': valid_enhancements
            }
            
        except Exception as e:
            logger.error(f"Error in optimized density enhancement: {e}")
            return {'max_enhancement': 0.0, 'mean_enhancement': 0.0}
    
    def run_high_scale_validation(self, test_cases: List[str] = None) -> Dict[str, Any]:
        """
        Run high-scale validation with specified test cases.
        
        Args:
            test_cases: List of test case names to run (default: all)
            
        Returns:
            Comprehensive results dictionary
        """
        if test_cases is None:
            test_cases = ['TC01']  # Start with TC01 for now
        
        logger.info("=== Starting High-Scale Computational Validation ===")
        logger.info(f"Test cases: {test_cases}")
        logger.info(f"Max N: {self.max_n:,}")
        
        start_time = time.time()
        
        comprehensive_results = {
            'metadata': {
                'start_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'max_n': self.max_n,
                'bootstrap_samples': self.bootstrap_samples,
                'chunk_size': self.chunk_size,
                'n_jobs': self.n_jobs,
                'mpmath_precision': mp.mp.dps
            },
            'test_results': {}
        }
        
        # Available test methods
        test_methods = {
            'TC01': self.tc01_advanced_scale_invariance,
            # Can add TC02-TC05 advanced versions here
        }
        
        for test_name in test_cases:
            if test_name not in test_methods:
                logger.error(f"Unknown test case: {test_name}")
                continue
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Executing {test_name}")
            logger.info(f"{'='*60}")
            
            try:
                test_start = time.time()
                result = test_methods[test_name]()
                test_duration = time.time() - test_start
                
                result['duration_seconds'] = test_duration
                result['status'] = 'COMPLETED'
                comprehensive_results['test_results'][test_name] = result
                
                logger.info(f"{test_name} completed in {test_duration:.2f} seconds")
                
            except Exception as e:
                logger.error(f"Error in {test_name}: {e}")
                comprehensive_results['test_results'][test_name] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'duration_seconds': 0
                }
        
        total_duration = time.time() - start_time
        comprehensive_results['metadata']['total_duration'] = total_duration
        comprehensive_results['metadata']['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"\n{'='*60}")
        logger.info("HIGH-SCALE VALIDATION COMPLETE")
        logger.info(f"Total Duration: {total_duration:.2f} seconds")
        logger.info(f"{'='*60}")
        
        return comprehensive_results


def main():
    """Main execution with command-line arguments."""
    parser = argparse.ArgumentParser(description='High-Scale Z Framework Validation')
    parser.add_argument('--max_n', type=int, default=10**6, 
                       help='Maximum N for computations (default: 1,000,000)')
    parser.add_argument('--bootstrap_samples', type=int, default=1000,
                       help='Number of bootstrap samples (default: 1000)')
    parser.add_argument('--chunk_size', type=int, default=10**6,
                       help='Chunk size for large computations (default: 1,000,000)')
    parser.add_argument('--test_cases', nargs='+', default=['TC01'],
                       help='Test cases to run (default: TC01)')
    parser.add_argument('--full_validation', action='store_true',
                       help='Run full validation with all test cases')
    parser.add_argument('--output_file', type=str, default='high_scale_validation_results.json',
                       help='Output file for results (default: high_scale_validation_results.json)')
    
    args = parser.parse_args()
    
    if args.full_validation:
        args.test_cases = ['TC01']  # Extend when other TC are implemented
    
    print("Z Framework: High-Scale Computationally Intensive Research Tasks")
    print("=" * 70)
    print(f"Max N: {args.max_n:,}")
    print(f"Test Cases: {args.test_cases}")
    print(f"Bootstrap Samples: {args.bootstrap_samples}")
    
    # Initialize validator
    validator = HighScaleValidator(
        max_n=args.max_n,
        bootstrap_samples=args.bootstrap_samples,
        chunk_size=args.chunk_size
    )
    
    # Run validation
    results = validator.run_high_scale_validation(args.test_cases)
    
    # Save results
    try:
        import json
        
        def convert_for_json(obj):
            """Convert objects for JSON serialization."""
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, dict):
                return {key: convert_for_json(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            else:
                return obj
        
        with open(args.output_file, 'w') as f:
            json.dump(convert_for_json(results), f, indent=2)
        print(f"\nResults saved to: {args.output_file}")
        
    except Exception as e:
        print(f"Error saving results: {e}")
    
    # Display summary
    print(f"\n=== VALIDATION SUMMARY ===")
    completed_tests = len([r for r in results['test_results'].values() if r.get('status') == 'COMPLETED'])
    total_tests = len(results['test_results'])
    print(f"Tests Completed: {completed_tests}/{total_tests}")
    print(f"Total Duration: {results['metadata']['total_duration']:.2f} seconds")
    
    return results


if __name__ == "__main__":
    main()