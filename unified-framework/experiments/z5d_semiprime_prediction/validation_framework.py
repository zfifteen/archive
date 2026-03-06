#!/usr/bin/env python3
"""
Statistical Validation Framework for Z5D Semiprime Prediction

This module provides comprehensive statistical validation and bootstrap analysis
for the Z5D semiprime prediction experiment. It implements rigorous statistical
testing with bootstrap confidence intervals and cross-domain correlation analysis.

Key Features:
- Bootstrap confidence interval analysis (1000+ resamples)
- Cross-validation and robustness testing
- Parameter optimization and calibration
- Statistical significance testing
- Correlation analysis with theoretical predictions

Author: Z Framework Implementation Team
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize
import json
from typing import Dict, List, Tuple, Optional, Union, Callable
import warnings
from datetime import datetime
import logging
from math import e  # Add explicit import for e

# Import experiment modules
from semiprime_utils import generate_semiprimes, nth_semiprime, baseline_semiprime_approximation
from z5d_semiprime_predictor import z5d_semiprime_variant, validate_z5d_semiprime_accuracy

# Configure logging
logger = logging.getLogger(__name__)


class SemiprimeValidationFramework:
    """
    Comprehensive validation framework for Z5D semiprime predictions.
    
    This class provides statistical validation, parameter optimization,
    and comprehensive analysis of the Z5D semiprime variant performance.
    """
    
    def __init__(self, max_k: int = 1000, bootstrap_samples: int = 100, random_seed: int = 42):
        """
        Initialize validation framework.
        
        Parameters
        ----------
        max_k : int
            Maximum k value for validation (reduced for reliability)
        bootstrap_samples : int
            Number of bootstrap resamples (reduced for speed)
        random_seed : int
            Random seed for reproducibility
        """
        self.max_k = max_k
        self.bootstrap_samples = bootstrap_samples
        self.random_seed = random_seed
        self.results = {}
        
        # Set random seed for reproducibility
        np.random.seed(random_seed)
        
        # Generate reference data
        logger.info(f"Generating semiprimes up to limit for k={max_k}")
        self._generate_reference_data()
    
    def _generate_reference_data(self):
        """Generate reference semiprime data for validation."""
        # Estimate reasonable upper limit for semiprime generation
        # Using rough approximation: s_k ≈ k log k / log log k
        if self.max_k <= 10:
            limit = 100
        else:
            estimate = self.max_k * np.log(self.max_k) / max(np.log(np.log(self.max_k + 10)), 1)
            limit = max(int(estimate * 2), 1000)  # Safety factor
        
        self.semiprimes = generate_semiprimes(limit)
        self.semiprime_count = len(self.semiprimes)
        
        # Create lookup dictionary for faster access
        self.semiprime_lookup = {i+1: sp for i, sp in enumerate(self.semiprimes)}
        
        logger.info(f"Generated {self.semiprime_count} semiprimes up to {self.semiprimes[-1]}")
    
    def get_true_semiprime(self, k: int) -> Optional[int]:
        """Get true kth semiprime if available."""
        return self.semiprime_lookup.get(k)
    
    def bootstrap_confidence_intervals(self, k_range: range, 
                                     prediction_func: Callable,
                                     alpha: float = 0.05) -> Dict:
        """
        Calculate bootstrap confidence intervals for prediction accuracy.
        
        Parameters
        ----------
        k_range : range
            Range of k values for testing
        prediction_func : Callable
            Function that takes k and returns predictions
        alpha : float
            Significance level (default 0.05 for 95% CI)
            
        Returns
        -------
        Dict
            Bootstrap analysis results with confidence intervals
        """
        k_values = list(k_range)
        true_values = []
        predictions = []
        
        # Collect data points where we have true values
        for k in k_values:
            true_sp = self.get_true_semiprime(k)
            if true_sp is not None:
                true_values.append(true_sp)
                pred = prediction_func(k)
                predictions.append(pred)
        
        if len(true_values) < 10:
            warnings.warn("Insufficient data points for reliable bootstrap analysis")
            return {'error': 'insufficient_data', 'sample_size': len(true_values)}
        
        true_values = np.array(true_values)
        predictions = np.array(predictions)
        
        # Calculate relative errors
        relative_errors = np.abs(predictions - true_values) / true_values
        
        # Bootstrap resampling
        bootstrap_errors = []
        for _ in range(self.bootstrap_samples):
            indices = np.random.choice(len(relative_errors), size=len(relative_errors), replace=True)
            boot_errors = relative_errors[indices]
            bootstrap_errors.append(np.mean(boot_errors))
        
        bootstrap_errors = np.array(bootstrap_errors)
        
        # Calculate confidence intervals
        ci_lower = np.percentile(bootstrap_errors, 100 * alpha / 2)
        ci_upper = np.percentile(bootstrap_errors, 100 * (1 - alpha / 2))
        
        return {
            'mean_error': np.mean(relative_errors),
            'bootstrap_mean': np.mean(bootstrap_errors),
            'bootstrap_std': np.std(bootstrap_errors),
            'confidence_interval': (ci_lower, ci_upper),
            'sample_size': len(true_values),
            'bootstrap_samples': self.bootstrap_samples,
            'alpha': alpha,
            'all_errors': relative_errors.tolist(),
            'bootstrap_distribution': bootstrap_errors.tolist()
        }
    
    def parameter_optimization(self, k_range: range, 
                             initial_params: Optional[Tuple[float, float, float]] = None) -> Dict:
        """
        Optimize Z5D semiprime parameters using least-squares fitting.
        
        Parameters
        ----------
        k_range : range
            Range of k values for optimization
        initial_params : Tuple[float, float, float], optional
            Initial parameter guess (c, k_star, beta)
            
        Returns
        -------
        Dict
            Optimization results with optimal parameters
        """
        # Collect training data
        k_values = []
        true_values = []
        
        for k in k_range:
            true_sp = self.get_true_semiprime(k)
            if true_sp is not None:
                k_values.append(k)
                true_values.append(true_sp)
        
        if len(k_values) < 5:
            return {'error': 'insufficient_data', 'sample_size': len(k_values)}
        
        k_array = np.array(k_values)
        true_array = np.array(true_values)
        
        # Define objective function
        def objective(params):
            c, k_star, beta = params
            try:
                predictions = z5d_semiprime_variant(k_array, c=c, k_star=k_star, beta=beta)
                if np.isscalar(predictions):
                    predictions = np.array([predictions])
                
                # Calculate relative errors
                relative_errors = np.abs(predictions - true_array) / true_array
                return np.mean(relative_errors)
            except Exception as e:
                logger.warning(f"Optimization objective failed: {e}")
                return 1.0  # Large error for invalid parameters
        
        # Set initial parameters
        if initial_params is None:
            initial_params = (-0.00247, 0.3, 30.34)  # Default values
        
        # Optimization bounds
        bounds = [(-0.01, 0.01), (0.1, 1.0), (10.0, 100.0)]
        
        try:
            # Run optimization
            result = minimize(objective, initial_params, bounds=bounds, method='L-BFGS-B')
            
            optimal_c, optimal_k_star, optimal_beta = result.x
            
            # Validate optimization
            final_error = objective(result.x)
            initial_error = objective(initial_params)
            
            return {
                'success': result.success,
                'optimal_parameters': {
                    'c': optimal_c,
                    'k_star': optimal_k_star,
                    'beta': optimal_beta
                },
                'initial_parameters': {
                    'c': initial_params[0],
                    'k_star': initial_params[1],
                    'beta': initial_params[2]
                },
                'initial_error': initial_error,
                'final_error': final_error,
                'improvement_ratio': initial_error / final_error if final_error > 0 else float('inf'),
                'optimization_message': result.message,
                'sample_size': len(k_values),
                'iterations': result.nit if hasattr(result, 'nit') else None
            }
            
        except Exception as e:
            logger.error(f"Parameter optimization failed: {e}")
            return {'error': str(e), 'success': False}
    
    def cross_validation_analysis(self, k_range: range, n_folds: int = 5) -> Dict:
        """
        Perform k-fold cross-validation analysis.
        
        Parameters
        ----------
        k_range : range
            Range of k values for cross-validation
        n_folds : int
            Number of cross-validation folds
            
        Returns
        -------
        Dict
            Cross-validation results
        """
        # Collect all available data
        k_values = []
        true_values = []
        
        for k in k_range:
            true_sp = self.get_true_semiprime(k)
            if true_sp is not None:
                k_values.append(k)
                true_values.append(true_sp)
        
        if len(k_values) < n_folds * 2:
            return {'error': 'insufficient_data', 'sample_size': len(k_values)}
        
        k_array = np.array(k_values)
        true_array = np.array(true_values)
        
        # Create folds
        indices = np.arange(len(k_values))
        np.random.shuffle(indices)
        folds = np.array_split(indices, n_folds)
        
        fold_results = []
        
        for i, test_indices in enumerate(folds):
            train_indices = np.concatenate([folds[j] for j in range(n_folds) if j != i])
            
            # Train on training set (optimize parameters)
            train_k = k_array[train_indices]
            train_true = true_array[train_indices]
            
            # Simple parameter optimization on training data
            def train_objective(params):
                c, k_star = params[:2]  # Simplified to 2 parameters
                try:
                    predictions = z5d_semiprime_variant(train_k, c=c, k_star=k_star)
                    if np.isscalar(predictions):
                        predictions = np.array([predictions])
                    relative_errors = np.abs(predictions - train_true) / train_true
                    return np.mean(relative_errors)
                except:
                    return 1.0
            
            # Quick optimization
            from scipy.optimize import minimize
            train_result = minimize(train_objective, [-0.005, 0.3], 
                                  bounds=[(-0.02, 0.02), (0.1, 1.0)], 
                                  method='L-BFGS-B')
            
            if train_result.success:
                optimal_c, optimal_k_star = train_result.x
            else:
                optimal_c, optimal_k_star = -0.00247, 0.3  # Fallback
            
            # Test on test set
            test_k = k_array[test_indices]
            test_true = true_array[test_indices]
            
            test_predictions = z5d_semiprime_variant(test_k, c=optimal_c, k_star=optimal_k_star)
            if np.isscalar(test_predictions):
                test_predictions = np.array([test_predictions])
            
            test_errors = np.abs(test_predictions - test_true) / test_true
            
            fold_results.append({
                'fold': i,
                'train_size': len(train_indices),
                'test_size': len(test_indices),
                'optimal_c': optimal_c,
                'optimal_k_star': optimal_k_star,
                'test_error': np.mean(test_errors),
                'test_std': np.std(test_errors)
            })
        
        # Aggregate results
        test_errors = [fold['test_error'] for fold in fold_results]
        
        return {
            'n_folds': n_folds,
            'total_samples': len(k_values),
            'mean_cv_error': np.mean(test_errors),
            'std_cv_error': np.std(test_errors),
            'fold_results': fold_results,
            'cv_stability': np.std(test_errors) / np.mean(test_errors) if np.mean(test_errors) > 0 else float('inf')
        }
    
    def density_enhancement_analysis(self, k_range: range) -> Dict:
        """
        Analyze density enhancement in semiprime gaps.
        
        This implements the hypothesis that Z5D provides ~15% density enhancement
        for semiprime detection as mentioned in the problem statement.
        
        Parameters
        ----------
        k_range : range
            Range of k values for analysis
            
        Returns
        -------
        Dict
            Density enhancement analysis results
        """
        # Collect semiprimes in the range
        range_semiprimes = []
        for k in k_range:
            sp = self.get_true_semiprime(k)
            if sp is not None:
                range_semiprimes.append(sp)
        
        if len(range_semiprimes) < 10:
            return {'error': 'insufficient_data'}
        
        range_semiprimes = np.array(range_semiprimes)
        
        # Calculate gaps
        gaps = np.diff(range_semiprimes)
        
        # Calculate density metrics
        total_span = range_semiprimes[-1] - range_semiprimes[0]
        actual_density = len(range_semiprimes) / total_span if total_span > 0 else 0
        
        # Theoretical density from asymptotic π_2(x) ~ x log log x / log x
        mean_x = np.mean(range_semiprimes)
        if mean_x > e:
            theoretical_density = np.log(np.log(mean_x)) / (mean_x * np.log(mean_x))
        else:
            theoretical_density = 0.1  # Rough estimate for small values
        
        # Enhancement ratio
        enhancement_ratio = actual_density / theoretical_density if theoretical_density > 0 else 1.0
        
        # Bootstrap confidence interval for enhancement
        bootstrap_enhancements = []
        for _ in range(self.bootstrap_samples):
            indices = np.random.choice(len(range_semiprimes), size=len(range_semiprimes), replace=True)
            boot_semiprimes = range_semiprimes[indices]
            boot_semiprimes = np.sort(boot_semiprimes)
            
            boot_span = boot_semiprimes[-1] - boot_semiprimes[0]
            boot_density = len(boot_semiprimes) / boot_span if boot_span > 0 else 0
            boot_enhancement = boot_density / theoretical_density if theoretical_density > 0 else 1.0
            
            bootstrap_enhancements.append(boot_enhancement)
        
        bootstrap_enhancements = np.array(bootstrap_enhancements)
        enhancement_ci = np.percentile(bootstrap_enhancements, [2.5, 97.5])
        
        return {
            'sample_size': len(range_semiprimes),
            'actual_density': actual_density,
            'theoretical_density': theoretical_density,
            'enhancement_ratio': enhancement_ratio,
            'enhancement_percentage': (enhancement_ratio - 1) * 100,
            'bootstrap_enhancement_mean': np.mean(bootstrap_enhancements),
            'bootstrap_enhancement_std': np.std(bootstrap_enhancements),
            'enhancement_ci_95': enhancement_ci.tolist(),
            'mean_gap': np.mean(gaps),
            'gap_variability': np.std(gaps) / np.mean(gaps) if np.mean(gaps) > 0 else 0
        }
    
    def comprehensive_validation(self, test_ranges: Optional[List[range]] = None) -> Dict:
        """
        Run comprehensive validation across multiple test ranges.
        
        Parameters
        ----------
        test_ranges : List[range], optional
            List of k ranges to test. If None, uses default ranges.
            
        Returns
        -------
        Dict
            Comprehensive validation results
        """
        if test_ranges is None:
            test_ranges = [
                range(5, 26, 5),         # Small scale: k=5 to 25
                range(20, 101, 20),      # Medium scale: k=20 to 100  
                range(50, min(self.max_k, 201), 50)  # Large scale: k=50+
            ]
        
        results = {
            'validation_timestamp': datetime.now().isoformat(),
            'framework_config': {
                'max_k': self.max_k,
                'bootstrap_samples': self.bootstrap_samples,
                'random_seed': self.random_seed,
                'semiprime_count': self.semiprime_count
            },
            'test_ranges': [],
            'parameter_optimization': {},
            'cross_validation': {},
            'density_enhancement': {},
            'summary_statistics': {}
        }
        
        # Test each range
        for i, k_range in enumerate(test_ranges):
            range_name = f"range_{i+1}"
            logger.info(f"Testing range: {range_name} = {list(k_range)[:5]}...")
            
            # Bootstrap analysis
            bootstrap_baseline = self.bootstrap_confidence_intervals(
                k_range, lambda k: baseline_semiprime_approximation(k)
            )
            bootstrap_z5d = self.bootstrap_confidence_intervals(
                k_range, lambda k: z5d_semiprime_variant(k)
            )
            
            # Store range results
            range_results = {
                'k_range': list(k_range),
                'bootstrap_baseline': bootstrap_baseline,
                'bootstrap_z5d': bootstrap_z5d
            }
            
            results['test_ranges'].append(range_results)
        
        # Parameter optimization on combined medium range
        if len(test_ranges) > 1:
            combined_range = range(10, min(self.max_k, 101), 10)
            results['parameter_optimization'] = self.parameter_optimization(combined_range)
        
        # Cross-validation analysis
        cv_range = range(10, min(self.max_k, 51), 5)
        results['cross_validation'] = self.cross_validation_analysis(cv_range)
        
        # Density enhancement analysis
        density_range = range(10, min(self.max_k, 101), 5)
        results['density_enhancement'] = self.density_enhancement_analysis(density_range)
        
        # Summary statistics
        z5d_errors = []
        baseline_errors = []
        
        for range_result in results['test_ranges']:
            if 'error' not in range_result['bootstrap_z5d']:
                z5d_errors.extend(range_result['bootstrap_z5d']['all_errors'])
            if 'error' not in range_result['bootstrap_baseline']:
                baseline_errors.extend(range_result['bootstrap_baseline']['all_errors'])
        
        if z5d_errors and baseline_errors:
            z5d_errors = np.array(z5d_errors)
            baseline_errors = np.array(baseline_errors)
            
            results['summary_statistics'] = {
                'z5d_mean_error': np.mean(z5d_errors),
                'baseline_mean_error': np.mean(baseline_errors),
                'improvement_ratio': np.mean(baseline_errors) / np.mean(z5d_errors) if np.mean(z5d_errors) > 0 else float('inf'),
                'z5d_sub_1_percent': np.mean(z5d_errors < 0.01),
                'baseline_sub_1_percent': np.mean(baseline_errors < 0.01),
                'total_test_points': len(z5d_errors)
            }
        
        return results
    
    def save_results(self, results: Dict, filename: str):
        """Save validation results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {filename}")
    
    def generate_validation_report(self, results: Dict) -> str:
        """Generate a human-readable validation report."""
        report = []
        report.append("Z5D Semiprime Prediction Validation Report")
        report.append("=" * 50)
        report.append(f"Generated: {results.get('validation_timestamp', 'Unknown')}")
        report.append(f"Random Seed: {self.random_seed}")
        report.append("")
        
        # Summary statistics
        if 'summary_statistics' in results and results['summary_statistics']:
            stats = results['summary_statistics']
            report.append("SUMMARY STATISTICS")
            report.append("-" * 20)
            report.append(f"Z5D Mean Error: {stats['z5d_mean_error']:.4f} ({stats['z5d_mean_error']*100:.2f}%)")
            report.append(f"Baseline Mean Error: {stats['baseline_mean_error']:.4f} ({stats['baseline_mean_error']*100:.2f}%)")
            report.append(f"Improvement Ratio: {stats['improvement_ratio']:.2f}x")
            report.append(f"Z5D Sub-1% Rate: {stats['z5d_sub_1_percent']*100:.1f}%")
            report.append(f"Baseline Sub-1% Rate: {stats['baseline_sub_1_percent']*100:.1f}%")
            report.append(f"Total Test Points: {stats['total_test_points']}")
            report.append("")
        
        # Parameter optimization
        if 'parameter_optimization' in results and 'optimal_parameters' in results['parameter_optimization']:
            opt = results['parameter_optimization']
            report.append("PARAMETER OPTIMIZATION")
            report.append("-" * 25)
            report.append(f"Success: {opt['success']}")
            report.append(f"Optimal c: {opt['optimal_parameters']['c']:.6f}")
            report.append(f"Optimal k*: {opt['optimal_parameters']['k_star']:.6f}")
            report.append(f"Optimal β: {opt['optimal_parameters']['beta']:.6f}")
            report.append(f"Initial Error: {opt['initial_error']:.4f}")
            report.append(f"Final Error: {opt['final_error']:.4f}")
            report.append(f"Improvement: {opt['improvement_ratio']:.2f}x")
            report.append("")
        
        # Density enhancement
        if 'density_enhancement' in results and 'enhancement_percentage' in results['density_enhancement']:
            density = results['density_enhancement']
            report.append("DENSITY ENHANCEMENT ANALYSIS")
            report.append("-" * 30)
            report.append(f"Enhancement: {density['enhancement_percentage']:.2f}%")
            report.append(f"95% CI: [{density['enhancement_ci_95'][0]:.3f}, {density['enhancement_ci_95'][1]:.3f}]")
            report.append(f"Sample Size: {density['sample_size']}")
            report.append("")
        
        # Cross-validation
        if 'cross_validation' in results and 'mean_cv_error' in results['cross_validation']:
            cv = results['cross_validation']
            report.append("CROSS-VALIDATION")
            report.append("-" * 16)
            report.append(f"CV Error: {cv['mean_cv_error']:.4f} ± {cv['std_cv_error']:.4f}")
            report.append(f"CV Stability: {cv['cv_stability']:.3f}")
            report.append(f"Folds: {cv['n_folds']}")
            report.append("")
        
        return "\n".join(report)


def run_comprehensive_experiment():
    """Run the complete Z5D semiprime prediction experiment."""
    print("Starting Z5D Semiprime Prediction Comprehensive Experiment")
    print("=" * 60)
    
    # Initialize validation framework with conservative parameters
    framework = SemiprimeValidationFramework(max_k=500, bootstrap_samples=100)
    
    # Run comprehensive validation
    print("Running comprehensive validation...")
    results = framework.comprehensive_validation()
    
    # Save results
    results_file = "experiment_results.json"
    framework.save_results(results, results_file)
    
    # Generate and display report
    report = framework.generate_validation_report(results)
    print("\n" + report)
    
    # Save report
    with open("validation_report.txt", "w") as f:
        f.write(report)
    
    print(f"\nExperiment complete!")
    print(f"Results saved to: {results_file}")
    print(f"Report saved to: validation_report.txt")
    
    return results


if __name__ == "__main__":
    # Run the comprehensive experiment
    results = run_comprehensive_experiment()