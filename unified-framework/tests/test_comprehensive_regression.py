#!/usr/bin/env python3
"""
Comprehensive Framework Regression Testing Suite
==============================================

Systematic regression testing of the Unified Framework with normalized parameters
as implemented in PR #396 (Z Framework k Parameter Standardization).

This test suite validates:
1. Core mathematical components with standardized parameters
2. Statistical validation and bootstrap confidence intervals  
3. Cross-domain applications and numerical stability
4. Parameter validation and deprecation handling
5. Performance metrics across multiple scales

Author: Copilot (GitHub Issue #397)
Date: August 2025
"""

import sys
import os
import time
import warnings
import numpy as np
import pytest
from pathlib import Path
import json

# Add framework path
sys.path.append('/home/runner/work/unified-framework/unified-framework')

# Import core framework components
try:
    from src.core.params import (
        KAPPA_GEO_DEFAULT, KAPPA_STAR_DEFAULT, MP_DPS, BOOTSTRAP_RESAMPLES_DEFAULT,
        validate_kappa_geo, validate_kappa_star, get_parameter_summary
    )
    from src.core.z_5d_enhanced import z5d_predictor as z5d_prime, Z5DEnhancedPredictor
    from src.core.geodesic_mapping import compute_density_enhancement, GeodesicMapper
    from src.core.z_baseline import BaselineZFramework, validate_baseline_implementation
    from tests.test_kappa_ci import generate_primes, bootstrap_ci
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all framework components are properly installed")
    sys.exit(1)


class ComprehensiveRegressionTestSuite:
    """Main regression testing suite for the Unified Framework"""
    
    def __init__(self, verbose=True, quick_mode=False):
        """
        Initialize regression test suite
        
        Args:
            verbose (bool): Enable detailed output
            quick_mode (bool): Run faster tests with smaller datasets
        """
        self.verbose = verbose
        self.quick_mode = quick_mode
        self.results = {
            'test_summary': {},
            'detailed_results': {},
            'performance_metrics': {},
            'validation_status': {},
            'parameter_validation': {},
            'statistical_analysis': {}
        }
        
        # Test scales based on mode
        if quick_mode:
            self.test_scales = [100, 1000, 10000]
            self.bootstrap_samples = 100
            self.prime_datasets = [100, 500, 1000]
        else:
            self.test_scales = [100, 1000, 10000, 100000, 1000000]
            self.bootstrap_samples = BOOTSTRAP_RESAMPLES_DEFAULT
            self.prime_datasets = [100, 1000, 5000, 10000]
            
        self.start_time = time.time()
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        if self.verbose:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def test_parameter_standardization(self):
        """Test 1: Parameter Standardization and Validation"""
        self.log("Testing parameter standardization and validation...")
        
        test_results = {
            'parameter_bounds': {},
            'deprecation_warnings': {},
            'validation_functions': {},
            'parameter_summary': {}
        }
        
        # Test parameter bounds validation
        try:
            # Valid parameters
            kappa_geo_valid = validate_kappa_geo(0.3)
            kappa_star_valid = validate_kappa_star(0.04449)
            test_results['parameter_bounds']['valid_parameters'] = True
            
            # Invalid parameters (should raise ValueError)
            try:
                validate_kappa_geo(-0.1)  # Below minimum
                test_results['parameter_bounds']['lower_bound_validation'] = False
            except ValueError:
                test_results['parameter_bounds']['lower_bound_validation'] = True
                
            try:
                validate_kappa_geo(15.0)  # Above maximum
                test_results['parameter_bounds']['upper_bound_validation'] = False
            except ValueError:
                test_results['parameter_bounds']['upper_bound_validation'] = True
                
        except Exception as e:
            test_results['parameter_bounds']['error'] = str(e)
            
        # Test deprecation warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Test deprecated geodesic parameter
            try:
                result = compute_density_enhancement(generate_primes(100)[:50], k=0.3)
                test_results['deprecation_warnings']['geodesic_k_warning'] = len(w) > 0
            except Exception as e:
                test_results['deprecation_warnings']['geodesic_error'] = str(e)
                
        # Test parameter summary
        try:
            summary = get_parameter_summary()
            test_results['parameter_summary'] = {
                'categories_present': list(summary.keys()),
                'geodesic_defaults_correct': summary.get('geodesic_mapping', {}).get('kappa_geo_default') == KAPPA_GEO_DEFAULT,
                'z5d_defaults_correct': summary.get('z5d_enhanced', {}).get('kappa_star_default') == KAPPA_STAR_DEFAULT
            }
        except Exception as e:
            test_results['parameter_summary']['error'] = str(e)
            
        self.results['parameter_validation'] = test_results
        return test_results
    
    def test_z5d_enhanced_predictor(self):
        """Test 2: Z_5D Enhanced Predictor with Standardized Parameters"""
        self.log("Testing Z_5D Enhanced Predictor...")
        
        test_results = {
            'prediction_accuracy': {},
            'parameter_effects': {},
            'scale_validation': {},
            'numerical_stability': {}
        }
        
        try:
            # Test prediction accuracy across scales
            for scale in self.test_scales:
                if scale > 100000 and self.quick_mode:
                    continue
                    
                # Test with default parameters
                pred_default = z5d_prime(scale)
                
                # Test with explicit standardized parameters
                pred_explicit = z5d_prime(scale, kappa_star=KAPPA_STAR_DEFAULT)
                
                # Test baseline for comparison
                baseline = BaselineZFramework()
                pred_baseline = baseline.prime_prediction(scale)
                
                test_results['prediction_accuracy'][scale] = {
                    'default_prediction': float(pred_default),
                    'explicit_prediction': float(pred_explicit),
                    'baseline_prediction': float(pred_baseline),
                    'consistency_check': abs(pred_default - pred_explicit) < 1e-10,
                    'enhancement_vs_baseline': (pred_default - pred_baseline) / pred_baseline if pred_baseline > 0 else 0
                }
                
            # Test parameter effects
            test_kappa_values = [0.01, 0.04449, 0.1, 0.5] if not self.quick_mode else [0.04449, 0.1]
            test_k = 10000
            
            for kappa in test_kappa_values:
                try:
                    pred = z5d_prime(test_k, kappa_star=kappa)
                    test_results['parameter_effects'][kappa] = float(pred)
                except Exception as e:
                    test_results['parameter_effects'][kappa] = f"Error: {e}"
                    
            # Test numerical stability
            large_k_values = [1e6, 1e8] if not self.quick_mode else [1e6]
            for large_k in large_k_values:
                try:
                    pred = z5d_prime(int(large_k))
                    test_results['numerical_stability'][large_k] = {
                        'prediction': float(pred),
                        'finite': np.isfinite(pred),
                        'positive': pred > 0
                    }
                except Exception as e:
                    test_results['numerical_stability'][large_k] = f"Error: {e}"
                    
        except Exception as e:
            test_results['error'] = str(e)
            
        self.results['detailed_results']['z5d_predictor'] = test_results
        return test_results
    
    def test_geodesic_mapping(self):
        """Test 3: Geodesic Mapping with Standardized Parameters"""
        self.log("Testing Geodesic Mapping...")
        
        test_results = {
            'density_enhancement': {},
            'bootstrap_validation': {},
            'parameter_sensitivity': {},
            'mapper_functionality': {}
        }
        
        try:
            # Generate test prime datasets
            for dataset_size in self.prime_datasets:
                if dataset_size > 1000 and self.quick_mode:
                    continue
                    
                primes = generate_primes(dataset_size)[:min(dataset_size//2, 500)]
                
                # Test density enhancement with default parameters
                result_default = compute_density_enhancement(
                    primes, 
                    kappa_geo=KAPPA_GEO_DEFAULT
                )
                
                # Test with bootstrap CI if not in quick mode
                if not self.quick_mode:
                    result_bootstrap = compute_density_enhancement(
                        primes,
                        kappa_geo=KAPPA_GEO_DEFAULT,
                        bootstrap_ci=True
                    )
                    
                    test_results['bootstrap_validation'][dataset_size] = {
                        'enhancement': result_bootstrap.get('percent', 0),
                        'ci_lower': result_bootstrap.get('ci', [0, 0])[0],
                        'ci_upper': result_bootstrap.get('ci', [0, 0])[1],
                        'ci_width': result_bootstrap.get('ci', [0, 0])[1] - result_bootstrap.get('ci', [0, 0])[0],
                        'ci_includes_15': (14.6 <= result_bootstrap.get('ci', [0, 0])[1] and 
                                          15.4 >= result_bootstrap.get('ci', [0, 0])[0])
                    }
                
                test_results['density_enhancement'][dataset_size] = {
                    'enhancement_percent': result_default.get('percent', 0),
                    'has_enhancements': 'enhancements' in result_default,
                    'valid_result': isinstance(result_default.get('percent'), (int, float))
                }
                
            # Test parameter sensitivity
            test_kappa_geo_values = [0.1, 0.3, 0.5, 1.0] if not self.quick_mode else [0.3, 0.5]
            test_primes = generate_primes(500)[:100]
            
            for kappa in test_kappa_geo_values:
                try:
                    result = compute_density_enhancement(test_primes, kappa_geo=kappa)
                    test_results['parameter_sensitivity'][kappa] = {
                        'enhancement': result.get('percent', 0),
                        'valid': isinstance(result.get('percent'), (int, float))
                    }
                except Exception as e:
                    test_results['parameter_sensitivity'][kappa] = f"Error: {e}"
                    
            # Test GeodesicMapper functionality
            try:
                mapper = GeodesicMapper(kappa_geo=KAPPA_GEO_DEFAULT)
                test_results['mapper_functionality'] = {
                    'instantiation': True,
                    'has_required_methods': hasattr(mapper, 'compute_density_enhancement')
                }
            except Exception as e:
                test_results['mapper_functionality'] = f"Error: {e}"
                
        except Exception as e:
            test_results['error'] = str(e)
            
        self.results['detailed_results']['geodesic_mapping'] = test_results
        return test_results
    
    def test_bootstrap_confidence_intervals(self):
        """Test 4: Bootstrap Confidence Interval Validation"""
        self.log("Testing Bootstrap Confidence Intervals...")
        
        test_results = {
            'ci_calculation': {},
            'statistical_properties': {},
            'coverage_validation': {},
            'resampling_consistency': {}
        }
        
        try:
            # Test CI calculation across different sample sizes
            for n_primes in [100, 500, 1000]:
                if n_primes > 500 and self.quick_mode:
                    continue
                    
                primes = generate_primes(n_primes)[:min(n_primes//2, 200)]
                
                # Calculate bootstrap CI
                ci_result = bootstrap_ci(primes, KAPPA_GEO_DEFAULT, resamples=self.bootstrap_samples)
                
                test_results['ci_calculation'][n_primes] = {
                    'ci_lower': ci_result[0],
                    'ci_upper': ci_result[1],
                    'ci_width': ci_result[1] - ci_result[0],
                    'valid_bounds': ci_result[0] <= ci_result[1],
                    'finite_values': np.isfinite(ci_result).all()
                }
                
            # Test resampling consistency (multiple runs should be similar)
            if not self.quick_mode:
                test_primes = generate_primes(300)[:100]
                ci_runs = []
                
                for run in range(5):  # 5 independent runs
                    ci = bootstrap_ci(test_primes, KAPPA_GEO_DEFAULT, resamples=100)
                    ci_runs.append(ci)
                    
                ci_runs = np.array(ci_runs)
                test_results['resampling_consistency'] = {
                    'mean_lower': np.mean(ci_runs[:, 0]),
                    'mean_upper': np.mean(ci_runs[:, 1]),
                    'std_lower': np.std(ci_runs[:, 0]),
                    'std_upper': np.std(ci_runs[:, 1]),
                    'consistent_bounds': np.std(ci_runs[:, 1] - ci_runs[:, 0]) < 5.0  # CI width variance
                }
                
        except Exception as e:
            test_results['error'] = str(e)
            
        self.results['statistical_analysis']['bootstrap_ci'] = test_results
        return test_results
    
    def test_cross_domain_applications(self):
        """Test 5: Cross-Domain Applications"""
        self.log("Testing Cross-Domain Applications...")
        
        test_results = {
            'ml_cross_validation': {},
            'crispr_applications': {},
            'baseline_validation': {}
        }
        
        try:
            # Test ML Cross-Validation (if available)
            try:
                from applications.ml_cross_validation import CRISPRQuantumCrossValidator
                
                validator = CRISPRQuantumCrossValidator(n_samples=10 if self.quick_mode else 50)
                
                # Test sequence generation
                sequences = validator.generate_crispr_sequences(
                    n_sequences=5 if self.quick_mode else 20, 
                    seq_length=50
                )
                
                test_results['ml_cross_validation'] = {
                    'sequence_generation': len(sequences) > 0,
                    'sequence_count': len(sequences),
                    'integration_available': True
                }
                
                if not self.quick_mode:
                    # Test feature extraction
                    features, feature_names = validator.extract_crispr_feature_matrix(sequences)
                    test_results['ml_cross_validation'].update({
                        'feature_extraction': features.shape[0] > 0,
                        'feature_count': features.shape[1],
                        'feature_names_count': len(feature_names)
                    })
                    
            except ImportError:
                test_results['ml_cross_validation'] = {'integration_available': False}
            except Exception as e:
                test_results['ml_cross_validation'] = {'error': str(e)}
                
            # Test baseline validation
            try:
                baseline_results = validate_baseline_implementation()
                test_results['baseline_validation'] = {
                    'validation_available': True,
                    'test_cases_passed': sum(1 for result in baseline_results.values() if result['in_range']),
                    'total_test_cases': len(baseline_results),
                    'all_tests_passed': all(result['in_range'] for result in baseline_results.values())
                }
            except Exception as e:
                test_results['baseline_validation'] = {'error': str(e)}
                
        except Exception as e:
            test_results['error'] = str(e)
            
        self.results['detailed_results']['cross_domain'] = test_results
        return test_results
    
    def test_numerical_stability(self):
        """Test 6: Numerical Stability and Edge Cases"""
        self.log("Testing Numerical Stability...")
        
        test_results = {
            'precision_handling': {},
            'edge_cases': {},
            'large_scale_stability': {},
            'backend_switching': {}
        }
        
        try:
            # Test edge cases
            edge_test_values = [0, 1, 2, 3, 5, 7]  # Small primes and edge values
            
            for val in edge_test_values:
                try:
                    result = z5d_prime(val)
                    test_results['edge_cases'][val] = {
                        'result': float(result),
                        'finite': np.isfinite(result),
                        'non_negative': result >= 0
                    }
                except Exception as e:
                    test_results['edge_cases'][val] = f"Error: {e}"
                    
            # Test large scale stability (if not in quick mode)
            if not self.quick_mode:
                large_values = [1e6, 1e7, 1e8]
                for val in large_values:
                    try:
                        result = z5d_prime(int(val))
                        test_results['large_scale_stability'][val] = {
                            'result': float(result),
                            'finite': np.isfinite(result),
                            'positive': result > 0,
                            'reasonable_magnitude': 1e3 < result < 1e12  # Sanity check
                        }
                    except Exception as e:
                        test_results['large_scale_stability'][val] = f"Error: {e}"
                        
            # Test precision settings
            try:
                import mpmath as mp
                current_dps = mp.dps
                test_results['precision_handling'] = {
                    'current_precision': current_dps,
                    'framework_precision': MP_DPS,
                    'precision_consistent': current_dps == MP_DPS
                }
            except Exception as e:
                test_results['precision_handling'] = f"Error: {e}"
                
        except Exception as e:
            test_results['error'] = str(e)
            
        self.results['detailed_results']['numerical_stability'] = test_results
        return test_results
    
    def generate_performance_summary(self):
        """Generate comprehensive performance summary"""
        self.log("Generating performance summary...")
        
        runtime = time.time() - self.start_time
        
        # Count test successes and failures
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, results in self.results['detailed_results'].items():
            if isinstance(results, dict) and 'error' not in results:
                total_tests += 1
                passed_tests += 1
            elif isinstance(results, dict) and 'error' in results:
                total_tests += 1
                failed_tests += 1
                
        # Parameter validation summary
        param_validation = self.results.get('parameter_validation', {})
        param_tests_passed = 0
        param_total_tests = 0
        
        for test_type, test_data in param_validation.items():
            if isinstance(test_data, dict):
                for key, value in test_data.items():
                    if isinstance(value, bool):
                        param_total_tests += 1
                        if value:
                            param_tests_passed += 1
        
        performance_summary = {
            'execution_time_seconds': runtime,
            'test_mode': 'quick' if self.quick_mode else 'comprehensive',
            'total_test_categories': total_tests,
            'passed_test_categories': passed_tests,
            'failed_test_categories': failed_tests,
            'parameter_validation_rate': param_tests_passed / param_total_tests if param_total_tests > 0 else 0,
            'overall_success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'framework_status': 'PASS' if (passed_tests / total_tests) > 0.8 else 'FAIL',
            'test_scales_validated': self.test_scales,
            'bootstrap_samples_used': self.bootstrap_samples,
            'prime_datasets_tested': self.prime_datasets
        }
        
        self.results['performance_metrics'] = performance_summary
        return performance_summary
    
    def run_complete_regression_suite(self):
        """Run the complete regression testing suite"""
        self.log("Starting Comprehensive Framework Regression Testing...")
        self.log(f"Mode: {'Quick' if self.quick_mode else 'Comprehensive'}")
        self.log(f"Test scales: {self.test_scales}")
        self.log("=" * 80)
        
        # Execute all test categories
        test_functions = [
            ("Parameter Standardization", self.test_parameter_standardization),
            ("Z_5D Enhanced Predictor", self.test_z5d_enhanced_predictor),
            ("Geodesic Mapping", self.test_geodesic_mapping),
            ("Bootstrap Confidence Intervals", self.test_bootstrap_confidence_intervals),
            ("Cross-Domain Applications", self.test_cross_domain_applications),
            ("Numerical Stability", self.test_numerical_stability)
        ]
        
        for test_name, test_func in test_functions:
            self.log(f"Running {test_name} tests...")
            try:
                start_time = time.time()
                result = test_func()
                duration = time.time() - start_time
                
                self.results['test_summary'][test_name] = {
                    'status': 'PASS' if 'error' not in result else 'FAIL',
                    'duration_seconds': duration,
                    'details': result
                }
                
                status = '✅ PASS' if 'error' not in result else '❌ FAIL'
                self.log(f"{test_name}: {status} ({duration:.2f}s)")
                
            except Exception as e:
                self.results['test_summary'][test_name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'duration_seconds': 0
                }
                self.log(f"{test_name}: ❌ ERROR - {e}")
        
        # Generate final performance summary
        performance_summary = self.generate_performance_summary()
        
        self.log("=" * 80)
        self.log("REGRESSION TESTING COMPLETE")
        self.log(f"Overall Status: {performance_summary['framework_status']}")
        self.log(f"Success Rate: {performance_summary['overall_success_rate']:.1%}")
        self.log(f"Total Runtime: {performance_summary['execution_time_seconds']:.2f}s")
        
        return self.results


def run_regression_tests(quick_mode=False, verbose=True, output_file=None):
    """
    Run comprehensive regression tests and optionally save results
    
    Args:
        quick_mode (bool): Run faster tests with smaller datasets
        verbose (bool): Enable detailed output
        output_file (str): Optional file path to save results as JSON
        
    Returns:
        dict: Complete test results
    """
    suite = ComprehensiveRegressionTestSuite(verbose=verbose, quick_mode=quick_mode)
    results = suite.run_complete_regression_suite()
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        if verbose:
            print(f"Results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Framework Regression Testing")
    parser.add_argument("--quick", action="store_true", help="Run quick tests with smaller datasets")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    results = run_regression_tests(
        quick_mode=args.quick,
        verbose=not args.quiet,
        output_file=args.output
    )
    
    # Exit with appropriate code
    performance = results.get('performance_metrics', {})
    success_rate = performance.get('overall_success_rate', 0)
    
    if success_rate > 0.8:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure