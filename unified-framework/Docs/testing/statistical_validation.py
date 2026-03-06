#!/usr/bin/env python3
"""
Statistical Validation Framework for Z Framework Claims

This module provides comprehensive statistical testing and validation
protocols for all empirical claims made in the Z Framework.
"""

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any
import warnings

class StatisticalValidator:
    """Statistical validation framework for Z Framework claims."""
    
    def __init__(self, significance_level: float = 0.05):
        """
        Initialize statistical validator.
        
        Args:
            significance_level: Alpha level for statistical tests (default: 0.05)
        """
        self.alpha = significance_level
        self.results = {}
    
    def bootstrap_confidence_interval(self, 
                                    data: List[float], 
                                    statistic_func: callable,
                                    n_bootstrap: int = 1000,
                                    confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Compute bootstrap confidence interval for any statistic.
        
        Args:
            data: Input data array
            statistic_func: Function to compute statistic (e.g., np.mean)
            n_bootstrap: Number of bootstrap samples
            confidence_level: Confidence level (e.g., 0.95 for 95% CI)
            
        Returns:
            Dictionary with CI bounds and bootstrap distribution
        """
        bootstrap_stats = []
        n = len(data)
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            bootstrap_sample = np.random.choice(data, size=n, replace=True)
            bootstrap_stat = statistic_func(bootstrap_sample)
            bootstrap_stats.append(bootstrap_stat)
        
        # Compute confidence interval
        alpha = 1 - confidence_level
        ci_lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
        ci_upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))
        
        return {
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'bootstrap_mean': np.mean(bootstrap_stats),
            'bootstrap_std': np.std(bootstrap_stats),
            'bootstrap_samples': bootstrap_stats,
            'confidence_level': confidence_level
        }
    
    def validate_enhancement_claim(self, 
                                 prime_enhancements: List[float],
                                 expected_enhancement: float = 15.0) -> Dict[str, Any]:
        """
        Validate the conditional prime density improvement under canonical benchmark methodology claim.
        
        Args:
            prime_enhancements: List of observed enhancement percentages
            expected_enhancement: Expected enhancement percentage (15.0)
            
        Returns:
            Validation results with statistical tests
        """
        # One-sample t-test against expected enhancement
        t_stat, p_value = stats.ttest_1samp(prime_enhancements, expected_enhancement)
        
        # Bootstrap confidence interval
        ci_result = self.bootstrap_confidence_interval(
            prime_enhancements, np.mean, n_bootstrap=1000
        )
        
        # Effect size (Cohen's d)
        effect_size = (np.mean(prime_enhancements) - expected_enhancement) / np.std(prime_enhancements)
        
        # Validate that CI contains expected value
        ci_contains_expected = (ci_result['ci_lower'] <= expected_enhancement <= ci_result['ci_upper'])
        
        result = {
            'observed_mean': np.mean(prime_enhancements),
            'expected': expected_enhancement,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'effect_size': effect_size,
            'ci_lower': ci_result['ci_lower'],
            'ci_upper': ci_result['ci_upper'],
            'ci_contains_expected': ci_contains_expected,
            'validation_status': 'VALIDATED' if ci_contains_expected and p_value < self.alpha else 'FAILED'
        }
        
        self.results['enhancement_validation'] = result
        return result
    
    def validate_correlation_claim(self, 
                                 array_a: List[float], 
                                 array_b: List[float],
                                 expected_correlation: float = 0.93) -> Dict[str, Any]:
        """
        Validate correlation claims (e.g., r ≈ 0.93 (empirical, pending independent validation) with zeta zeros).
        
        Args:
            array_a: First data array
            array_b: Second data array  
            expected_correlation: Expected correlation coefficient
            
        Returns:
            Correlation validation results
        """
        # Compute Pearson correlation
        correlation, p_value = stats.pearsonr(array_a, array_b)
        
        # Bootstrap confidence interval for correlation
        def correlation_func(indices):
            return stats.pearsonr(np.array(array_a)[indices], np.array(array_b)[indices])[0]
        
        # Bootstrap correlation coefficients
        bootstrap_correlations = []
        n = len(array_a)
        for _ in range(1000):
            indices = np.random.randint(0, n, n)
            boot_corr = correlation_func(indices)
            bootstrap_correlations.append(boot_corr)
        
        ci_lower = np.percentile(bootstrap_correlations, 2.5)
        ci_upper = np.percentile(bootstrap_correlations, 97.5)
        
        # Validate correlation
        ci_contains_expected = (ci_lower <= expected_correlation <= ci_upper)
        
        result = {
            'observed_correlation': correlation,
            'expected_correlation': expected_correlation,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'ci_contains_expected': ci_contains_expected,
            'n_samples': len(array_a),
            'validation_status': 'VALIDATED' if ci_contains_expected and p_value < self.alpha else 'FAILED'
        }
        
        self.results['correlation_validation'] = result
        return result
    
    def multiple_testing_correction(self, p_values: List[float], method: str = 'bonferroni') -> Dict[str, Any]:
        """
        Apply multiple testing correction to p-values.
        
        Args:
            p_values: List of p-values to correct
            method: Correction method ('bonferroni' or 'fdr')
            
        Returns:
            Corrected p-values and significance results
        """
        if method == 'bonferroni':
            corrected_alpha = self.alpha / len(p_values)
            significant = np.array(p_values) < corrected_alpha
            corrected_p_values = np.array(p_values) * len(p_values)
            # Clip to 1.0 maximum
            corrected_p_values = np.minimum(corrected_p_values, 1.0)
            
        elif method == 'fdr':
            # Benjamini-Hochberg FDR correction
            from statsmodels.stats.multitest import fdrcorrection
            significant, corrected_p_values = fdrcorrection(p_values, alpha=self.alpha)
        else:
            raise ValueError(f"Unknown correction method: {method}")
        
        result = {
            'original_p_values': p_values,
            'corrected_p_values': corrected_p_values.tolist(),
            'significant_tests': significant.tolist(),
            'n_significant': np.sum(significant),
            'family_wise_error_rate': self.alpha,
            'correction_method': method
        }
        
        self.results['multiple_testing'] = result
        return result
    
    def validate_parameter_optimization(self, 
                                      k_values: List[float],
                                      enhancements: List[float],
                                      expected_optimal_k: float = 0.3) -> Dict[str, Any]:
        """
        Validate optimal parameter k* ≈ 0.3 claim.
        
        Args:
            k_values: Array of k parameter values tested
            enhancements: Corresponding enhancement percentages
            expected_optimal_k: Expected optimal k value
            
        Returns:
            Parameter optimization validation results
        """
        # Find empirical optimal k
        optimal_idx = np.argmax(enhancements)
        observed_optimal_k = k_values[optimal_idx]
        max_enhancement = enhancements[optimal_idx]
        
        # Test if observed k* is close to expected
        k_difference = abs(observed_optimal_k - expected_optimal_k)
        tolerance = 0.05  # Allow 5% tolerance
        
        # Bootstrap confidence interval for optimal k
        bootstrap_optimal_k = []
        for _ in range(1000):
            # Resample enhancement curve with noise
            noise = np.random.normal(0, np.std(enhancements) * 0.1, len(enhancements))
            noisy_enhancements = np.array(enhancements) + noise
            boot_optimal_idx = np.argmax(noisy_enhancements)
            bootstrap_optimal_k.append(k_values[boot_optimal_idx])
        
        ci_lower = np.percentile(bootstrap_optimal_k, 2.5)
        ci_upper = np.percentile(bootstrap_optimal_k, 97.5)
        ci_contains_expected = (ci_lower <= expected_optimal_k <= ci_upper)
        
        result = {
            'observed_optimal_k': observed_optimal_k,
            'expected_optimal_k': expected_optimal_k,
            'max_enhancement': max_enhancement,
            'k_difference': k_difference,
            'within_tolerance': k_difference < tolerance,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'ci_contains_expected': ci_contains_expected,
            'validation_status': 'VALIDATED' if ci_contains_expected and k_difference < tolerance else 'FAILED'
        }
        
        self.results['parameter_optimization'] = result
        return result
    
    def generate_validation_report(self) -> str:
        """
        Generate comprehensive validation report.
        
        Returns:
            Formatted validation report string
        """
        report = ["=" * 60]
        report.append("Z FRAMEWORK STATISTICAL VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        for test_name, result in self.results.items():
            report.append(f"## {test_name.upper().replace('_', ' ')}")
            report.append("-" * 40)
            
            if 'validation_status' in result:
                status = result['validation_status']
                report.append(f"Status: {status}")
                
            for key, value in result.items():
                if key != 'validation_status' and not key.endswith('_samples'):
                    if isinstance(value, float):
                        report.append(f"{key}: {value:.6f}")
                    else:
                        report.append(f"{key}: {value}")
            
            report.append("")
        
        # Summary
        validated_tests = sum(1 for r in self.results.values() 
                            if r.get('validation_status') == 'VALIDATED')
        total_tests = len(self.results)
        
        report.append("## SUMMARY")
        report.append("-" * 40)
        report.append(f"Validated Tests: {validated_tests}/{total_tests}")
        report.append(f"Success Rate: {validated_tests/total_tests*100:.1f}%")
        
        overall_status = "PASSED" if validated_tests == total_tests else "FAILED"
        report.append(f"Overall Status: {overall_status}")
        
        return "\n".join(report)

# Example usage and demonstration
if __name__ == "__main__":
    # Initialize validator
    validator = StatisticalValidator()
    
    # Example data for demonstration
    np.random.seed(42)  # For reproducible results
    
    # Simulate enhancement data around 15%
    enhancement_data = np.random.normal(15.0, 1.5, 100)
    
    # Simulate correlation data  
    n_points = 1000
    array_a = np.random.randn(n_points)
    array_b = 0.93 * array_a + 0.1 * np.random.randn(n_points)  # Correlation ≈ 0.93
    
    # Simulate k optimization data
    k_range = np.linspace(0.1, 0.5, 40)
    # Peak at k=0.3 with some noise
    enhancements_k = 15 * np.exp(-50 * (k_range - 0.3)**2) + np.random.normal(0, 0.5, len(k_range))
    
    # Run validations
    print("Running Z Framework Statistical Validation...")
    print()
    
    # Test 1: Enhancement claim
    result1 = validator.validate_enhancement_claim(enhancement_data)
    print(f"Enhancement Validation: {result1['validation_status']}")
    
    # Test 2: Correlation claim
    result2 = validator.validate_correlation_claim(array_a, array_b)
    print(f"Correlation Validation: {result2['validation_status']}")
    
    # Test 3: Parameter optimization
    result3 = validator.validate_parameter_optimization(k_range, enhancements_k)
    print(f"Parameter Optimization: {result3['validation_status']}")
    
    # Test 4: Multiple testing correction
    p_values = [result1['p_value'], result2['p_value'], 0.001]
    result4 = validator.multiple_testing_correction(p_values)
    print(f"Multiple Testing: {result4['n_significant']}/{len(p_values)} significant after correction")
    
    print()
    print("=" * 60)
    print("FULL VALIDATION REPORT")
    print("=" * 60)
    print(validator.generate_validation_report())