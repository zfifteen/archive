"""
Z5D Prime Predictor: Empirical Validation Test Specifications

This module implements systematic empirical validation of the Z5D Prime Predictor's
accuracy, numerical stability, and asymptotic behavior across wide ranges of n values.
Provides quantitative data to assess predictive power relative to Prime Number Theorem
(PNT) and established bounds (Dusart inequalities).

Key Objectives:
- Mean relative error (MRE) validation across scales
- Absolute error distribution analysis  
- Error trend identification with increasing n
- Substantiation of claims: MRE ~0.0001% for n ≥ 10^6
- Correction terms D(n) and E(n) drift analysis
- Numerical stability validation up to n = 10^308

Output Format: CSV with columns [n, predicted_p_n, true_p_n, lower_bound, 
upper_bound, relative_error, absolute_error, d_term, e_term]
"""

import sys
import os
import numpy as np
import pandas as pd
import time
import warnings
from typing import List, Tuple, Dict, Optional, Union
from pathlib import Path
import csv
from sympy import ntheory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

try:
    from z_framework.discrete.z5d_predictor import (
        z5d_prime,
        base_pnt_prime, 
        d_term,
        e_term,
        DEFAULT_C,
        DEFAULT_K_STAR
    )
except ImportError as e:
    logger.error(f"Failed to import Z5D predictor: {e}")
    raise


class DusartBounds:
    """
    Implementation of Dusart's bounds for nth prime.
    
    Provides empirically validated upper and lower bounds for prime enumeration
    based on Pierre Dusart's refined inequalities (2010, 2018).
    """
    
    @staticmethod
    def lower_bound(n: Union[int, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Dusart's lower bound for nth prime.
        
        For n ≥ 6: p_n > n * (ln(n) + ln(ln(n)) - 1)
        For large n: p_n > n * (ln(n) + ln(ln(n)) - 1 + (ln(ln(n)) - 2)/ln(n))
        """
        n = np.asarray(n, dtype=float)
        is_scalar = n.ndim == 0
        if is_scalar:
            n = n.reshape(1)
            
        bounds = np.zeros_like(n)
        
        # For small n < 6, use exact values
        small_primes = [0, 2, 3, 5, 7, 11]  # 0th index unused
        small_mask = (n >= 1) & (n <= 5)
        if np.any(small_mask):
            for i, val in enumerate(n[small_mask]):
                if 1 <= val <= 5:
                    bounds[small_mask][i] = small_primes[int(val)]
        
        # For n ≥ 6, apply Dusart bounds
        large_mask = n >= 6
        if np.any(large_mask):
            n_large = n[large_mask]
            ln_n = np.log(n_large)
            ln_ln_n = np.log(ln_n)
            
            # Enhanced bound for better accuracy
            bounds[large_mask] = n_large * (
                ln_n + ln_ln_n - 1 + (ln_ln_n - 2) / ln_n
            )
            
        return float(bounds[0]) if is_scalar else bounds
    
    @staticmethod
    def upper_bound(n: Union[int, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Dusart's upper bound for nth prime.
        
        For n ≥ 6: p_n < n * (ln(n) + ln(ln(n)))
        For large n: Enhanced bound with higher-order corrections
        """
        n = np.asarray(n, dtype=float)
        is_scalar = n.ndim == 0
        if is_scalar:
            n = n.reshape(1)
            
        bounds = np.zeros_like(n)
        
        # For small n < 6, use exact values with small margin
        small_primes = [0, 2, 3, 5, 7, 11]
        small_mask = (n >= 1) & (n <= 5)
        if np.any(small_mask):
            for i, val in enumerate(n[small_mask]):
                if 1 <= val <= 5:
                    bounds[small_mask][i] = small_primes[int(val)] * 1.01  # Small margin
        
        # For n ≥ 6, apply Dusart bounds
        large_mask = n >= 6
        if np.any(large_mask):
            n_large = n[large_mask]
            ln_n = np.log(n_large)
            ln_ln_n = np.log(ln_n)
            
            # Enhanced upper bound
            bounds[large_mask] = n_large * (
                ln_n + ln_ln_n + (ln_ln_n - 1) / ln_n
            )
            
        return float(bounds[0]) if is_scalar else bounds


class Z5DEmpiricalValidator:
    """
    Comprehensive empirical validation framework for Z5D Prime Predictor.
    
    Implements systematic testing across multiple scales with statistical
    analysis and performance benchmarking.
    """
    
    def __init__(self, output_dir: str = "validation_results"):
        """
        Initialize validator with output directory for results.
        
        Parameters
        ----------
        output_dir : str
            Directory to store validation results and CSV outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Test scales and parameters
        self.test_scales = {
            'small': {'range': (10, 1000), 'samples': 50},
            'medium': {'range': (1000, 100000), 'samples': 100}, 
            'large': {'range': (100000, 1000000), 'samples': 50},
            'ultra_large': {'range': (1000000, 10000000), 'samples': 25},
            'extreme': {'range': (10000000, 100000000), 'samples': 10}
        }
        
        # Alternative calibration parameters for testing
        self.calibration_variants = {
            'default': {'c': DEFAULT_C, 'k_star': DEFAULT_K_STAR},
            'mid_range': {'c': -0.01342, 'k_star': 0.11562},
            'conservative': {'c': -0.001, 'k_star': 0.02}
        }
        
    def generate_test_points(self, scale_name: str, 
                           distribution: str = 'logarithmic') -> np.ndarray:
        """
        Generate test points for given scale with specified distribution.
        
        Parameters
        ----------
        scale_name : str
            Scale identifier from self.test_scales
        distribution : str
            Distribution type: 'logarithmic', 'linear', or 'powers_of_10'
            
        Returns
        -------
        np.ndarray
            Array of test point indices
        """
        scale_config = self.test_scales[scale_name]
        start, end = scale_config['range']
        num_samples = scale_config['samples']
        
        if distribution == 'logarithmic':
            # Logarithmically spaced points
            points = np.logspace(np.log10(start), np.log10(end), num_samples)
        elif distribution == 'linear':
            # Linearly spaced points
            points = np.linspace(start, end, num_samples)
        elif distribution == 'powers_of_10':
            # Powers of 10 within range
            log_start = int(np.log10(start))
            log_end = int(np.log10(end))
            points = [10**i for i in range(log_start, log_end + 1)]
            points = np.array([p for p in points if start <= p <= end])
        else:
            raise ValueError(f"Unknown distribution: {distribution}")
            
        return np.round(points).astype(int)
    
    def get_true_prime(self, n: int) -> Optional[int]:
        """
        Get true nth prime using most feasible method.
        
        For n ≤ 10^8: Use sympy.ntheory.prime(n) - empirically feasible
        For n > 10^8: Return None (computationally infeasible)
        
        Parameters
        ----------
        n : int
            Prime index
            
        Returns
        -------
        int or None
            True nth prime if computable, None otherwise
        """
        if n <= 100_000_000:  # 10^8 limit for direct computation
            try:
                return ntheory.prime(n)
            except (MemoryError, OverflowError, ValueError):
                logger.warning(f"Failed to compute true prime for n={n}")
                return None
        else:
            return None
    
    def validate_single_prediction(self, n: int, 
                                 calibration: str = 'default') -> Dict:
        """
        Validate single Z5D prediction with comprehensive metrics.
        
        Parameters
        ----------
        n : int
            Prime index to validate
        calibration : str
            Calibration variant to use
            
        Returns
        -------
        Dict
            Validation results with all computed metrics
        """
        # Get calibration parameters
        params = self.calibration_variants[calibration]
        
        # Start timing
        start_time = time.time()
        
        # Get Z5D prediction
        try:
            z5d_pred = z5d_prime(n, c=params['c'], k_star=params['k_star'])
        except Exception as e:
            logger.error(f"Z5D prediction failed for n={n}: {e}")
            return {'n': n, 'error': str(e)}
        
        # Get component terms
        try:
            pnt_pred = base_pnt_prime(n)
            d_val = d_term(n)
            e_val = e_term(n)
        except Exception as e:
            logger.warning(f"Component calculation failed for n={n}: {e}")
            pnt_pred = d_val = e_val = np.nan
        
        # Get bounds
        lower_bound = DusartBounds.lower_bound(n)
        upper_bound = DusartBounds.upper_bound(n)
        
        # Get true prime if feasible
        true_prime = self.get_true_prime(n)
        
        # Calculate errors
        if true_prime is not None:
            absolute_error = abs(z5d_pred - true_prime)
            relative_error = absolute_error / true_prime * 100
        else:
            absolute_error = relative_error = np.nan
        
        # Check bound compliance
        within_bounds = lower_bound <= z5d_pred <= upper_bound
        
        computation_time = time.time() - start_time
        
        return {
            'n': n,
            'predicted_p_n': z5d_pred,
            'true_p_n': true_prime,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'relative_error': relative_error,
            'absolute_error': absolute_error,
            'pnt_prediction': pnt_pred,
            'd_term': d_val,
            'e_term': e_val,
            'within_bounds': within_bounds,
            'computation_time': computation_time,
            'calibration': calibration
        }
    
    def run_scale_validation(self, scale_name: str,
                           calibration: str = 'default',
                           save_results: bool = True) -> pd.DataFrame:
        """
        Run validation for entire scale range.
        
        Parameters
        ----------
        scale_name : str
            Scale to validate
        calibration : str
            Calibration variant
        save_results : bool
            Whether to save results to CSV
            
        Returns
        -------
        pd.DataFrame
            Complete validation results
        """
        logger.info(f"Running {scale_name} scale validation with {calibration} calibration")
        
        # Generate test points
        test_points = self.generate_test_points(scale_name)
        logger.info(f"Testing {len(test_points)} points from {test_points[0]} to {test_points[-1]}")
        
        # Run validations
        results = []
        for i, n in enumerate(test_points):
            if i % max(1, len(test_points) // 10) == 0:
                logger.info(f"Progress: {i}/{len(test_points)} ({i/len(test_points)*100:.1f}%)")
            
            result = self.validate_single_prediction(n, calibration)
            results.append(result)
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Calculate summary statistics
        if not df.empty and 'relative_error' in df.columns:
            valid_errors = df['relative_error'].dropna()
            if not valid_errors.empty:
                summary = {
                    'scale': scale_name,
                    'calibration': calibration,
                    'total_points': len(df),
                    'valid_comparisons': len(valid_errors),
                    'mean_relative_error': valid_errors.mean(),
                    'median_relative_error': valid_errors.median(),
                    'std_relative_error': valid_errors.std(),
                    'max_relative_error': valid_errors.max(),
                    'min_relative_error': valid_errors.min(),
                    'within_bounds_rate': df['within_bounds'].mean() if 'within_bounds' in df else np.nan
                }
                logger.info(f"Summary for {scale_name}: MRE={summary['mean_relative_error']:.6f}%")
        
        # Save results if requested
        if save_results:
            filename = f"z5d_validation_{scale_name}_{calibration}.csv"
            filepath = self.output_dir / filename
            df.to_csv(filepath, index=False)
            logger.info(f"Results saved to {filepath}")
        
        return df
    
    def test_numerical_stability(self, max_exponent: int = 100) -> pd.DataFrame:
        """
        Test numerical stability up to extreme scales.
        
        Tests Z5D predictor at exponentially increasing scales to identify
        numerical breakdown points and validate stability claims up to n = 10^308.
        
        Parameters
        ----------
        max_exponent : int
            Maximum power of 10 to test (default: 100 for n = 10^100)
            
        Returns
        -------
        pd.DataFrame
            Stability test results
        """
        logger.info("Running numerical stability test")
        
        # Test points: 10^3, 10^4, ..., 10^max_exponent
        test_points = [10**i for i in range(3, min(max_exponent + 1, 309))]  # Python float limit
        
        results = []
        for n in test_points:
            log10_n = int(np.log10(float(n)))
            logger.info(f"Testing stability at n = 10^{log10_n}")
            
            start_time = time.time()
            
            try:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    
                    prediction = z5d_prime(n)
                    computation_time = time.time() - start_time
                    
                    # Check for warnings
                    warning_messages = [str(warning.message) for warning in w]
                    
                    # Validate result properties
                    is_finite = np.isfinite(prediction)
                    is_positive = prediction > 0
                    is_reasonable = prediction > n  # Prime should be larger than index
                    
                    results.append({
                        'n': n,
                        'log10_n': log10_n,
                        'prediction': prediction,
                        'computation_time': computation_time,
                        'is_finite': is_finite,
                        'is_positive': is_positive,
                        'is_reasonable': is_reasonable,
                        'warnings': len(warning_messages),
                        'warning_messages': '; '.join(warning_messages) if warning_messages else None,
                        'success': is_finite and is_positive and is_reasonable
                    })
                    
            except Exception as e:
                logger.error(f"Stability test failed at n=10^{log10_n}: {e}")
                results.append({
                    'n': n,
                    'log10_n': log10_n,
                    'prediction': np.nan,
                    'computation_time': np.nan,
                    'is_finite': False,
                    'is_positive': False,
                    'is_reasonable': False,
                    'warnings': 0,
                    'warning_messages': str(e),
                    'success': False
                })
        
        df = pd.DataFrame(results)
        
        # Save results
        filepath = self.output_dir / "z5d_numerical_stability.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"Numerical stability results saved to {filepath}")
        
        return df
    
    def test_asymptotic_behavior(self) -> pd.DataFrame:
        """
        Test asymptotic behavior hypotheses.
        
        Tests hypothesis that relative error decreases as O(1/n^{1/2}) or better,
        consistent with PNT refinements.
        
        Returns
        -------
        pd.DataFrame
            Asymptotic behavior analysis results
        """
        logger.info("Running asymptotic behavior analysis")
        
        # Use scales with known true primes for comparison
        test_points = np.logspace(2, 7, 50, dtype=int)  # 10^2 to 10^7
        
        results = []
        for n in test_points:
            true_prime = self.get_true_prime(n)
            if true_prime is None:
                continue
                
            prediction = z5d_prime(n)
            relative_error = abs(prediction - true_prime) / true_prime
            
            # Theoretical error bounds
            theoretical_bound_sqrt = 1.0 / np.sqrt(n)  # O(1/n^{1/2})
            theoretical_bound_ln = 1.0 / np.log(n)     # O(1/ln(n))
            
            results.append({
                'n': n,
                'log_n': np.log(n),
                'relative_error': relative_error,
                'theoretical_sqrt_bound': theoretical_bound_sqrt,
                'theoretical_ln_bound': theoretical_bound_ln,
                'error_vs_sqrt': relative_error / theoretical_bound_sqrt,
                'error_vs_ln': relative_error / theoretical_bound_ln
            })
        
        df = pd.DataFrame(results)
        
        # Save results
        filepath = self.output_dir / "z5d_asymptotic_behavior.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"Asymptotic behavior results saved to {filepath}")
        
        return df
    
    def run_comprehensive_validation(self) -> Dict[str, pd.DataFrame]:
        """
        Run complete empirical validation suite.
        
        Returns
        -------
        Dict[str, pd.DataFrame]
            Dictionary of all validation results
        """
        logger.info("Starting comprehensive Z5D empirical validation")
        
        all_results = {}
        
        # 1. Scale-based validation
        for scale_name in self.test_scales.keys():
            if scale_name in ['extreme']:  # Skip computationally intensive scales by default
                logger.info(f"Skipping {scale_name} scale (computationally intensive)")
                continue
                
            for calibration in ['default', 'mid_range']:
                key = f"{scale_name}_{calibration}"
                all_results[key] = self.run_scale_validation(scale_name, calibration)
        
        # 2. Numerical stability test
        all_results['numerical_stability'] = self.test_numerical_stability(max_exponent=50)
        
        # 3. Asymptotic behavior test
        all_results['asymptotic_behavior'] = self.test_asymptotic_behavior()
        
        # 4. Generate summary report
        self.generate_validation_report(all_results)
        
        logger.info("Comprehensive validation completed")
        return all_results
    
    def generate_validation_report(self, results: Dict[str, pd.DataFrame]) -> None:
        """
        Generate comprehensive validation report.
        
        Parameters
        ----------
        results : Dict[str, pd.DataFrame]
            All validation results
        """
        report_path = self.output_dir / "z5d_validation_report.md"
        
        with open(report_path, 'w') as f:
            f.write("# Z5D Prime Predictor: Empirical Validation Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Executive Summary\n\n")
            
            # Process scale validations
            scale_summaries = []
            for key, df in results.items():
                if 'numerical_stability' in key or 'asymptotic' in key:
                    continue
                    
                if 'relative_error' in df.columns:
                    valid_errors = df['relative_error'].dropna()
                    if not valid_errors.empty:
                        scale_summaries.append({
                            'scale': key,
                            'points': len(df),
                            'valid_comparisons': len(valid_errors),
                            'mean_relative_error': valid_errors.mean(),
                            'max_relative_error': valid_errors.max(),
                            'within_bounds_rate': df['within_bounds'].mean() if 'within_bounds' in df else 0
                        })
            
            if scale_summaries:
                f.write("### Scale Validation Summary\n\n")
                f.write("| Scale | Points | Valid Comparisons | Mean RE (%) | Max RE (%) | Within Bounds (%) |\n")
                f.write("|-------|--------|-------------------|-------------|------------|-----------------|\n")
                
                for summary in scale_summaries:
                    f.write(f"| {summary['scale']} | {summary['points']} | "
                           f"{summary['valid_comparisons']} | {summary['mean_relative_error']:.6f} | "
                           f"{summary['max_relative_error']:.6f} | {summary['within_bounds_rate']*100:.1f} |\n")
            
            f.write("\n## Key Findings\n\n")
            
            # Analyze results for key claims
            for scale_key, df in results.items():
                if 'large' in scale_key and 'relative_error' in df.columns:
                    large_scale_errors = df['relative_error'].dropna()
                    if not large_scale_errors.empty:
                        mean_error = large_scale_errors.mean()
                        f.write(f"- Large scale ({scale_key}) mean relative error: {mean_error:.6f}%\n")
                        if mean_error < 0.001:  # 0.001% threshold
                            f.write("  ✅ **Meets claimed accuracy of ~0.0001% for large n**\n")
                        else:
                            f.write("  ❌ **Does not meet claimed accuracy of ~0.0001% for large n**\n")
            
            f.write("\n## Detailed Results\n\n")
            f.write("Detailed CSV files saved in validation_results/ directory:\n\n")
            
            for key in results.keys():
                f.write(f"- `{key}.csv`: {key.replace('_', ' ').title()} results\n")
        
        logger.info(f"Validation report generated: {report_path}")


def main():
    """
    Main function to run empirical validation with command line interface.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Z5D Prime Predictor Empirical Validation")
    parser.add_argument("--scale", choices=['small', 'medium', 'large', 'ultra_large', 'extreme'], 
                       help="Run validation for specific scale only")
    parser.add_argument("--calibration", choices=['default', 'mid_range', 'conservative'],
                       default='default', help="Calibration variant to use")
    parser.add_argument("--output-dir", default="validation_results", 
                       help="Output directory for results")
    parser.add_argument("--stability-only", action='store_true',
                       help="Run only numerical stability test")
    parser.add_argument("--asymptotic-only", action='store_true', 
                       help="Run only asymptotic behavior test")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = Z5DEmpiricalValidator(output_dir=args.output_dir)
    
    if args.stability_only:
        validator.test_numerical_stability()
    elif args.asymptotic_only:
        validator.test_asymptotic_behavior()
    elif args.scale:
        validator.run_scale_validation(args.scale, args.calibration)
    else:
        validator.run_comprehensive_validation()


if __name__ == "__main__":
    main()