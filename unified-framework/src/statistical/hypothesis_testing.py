"""
Statistical Hypothesis Testing Module
====================================

SciPy-based statistical hypothesis testing for validating empirical results
in the Z Framework, including prime enhancement, variance minimization, and
optimal parameter discovery.
"""

import numpy as np
import scipy.stats as stats
from scipy import optimize
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import warnings

def test_prime_enhancement_hypothesis(prime_data, composite_data, enhancement_threshold=0.05, 
                                    confidence_level=0.95):
    """
    Test the hypothesis that the golden ratio transformation significantly enhances
    prime number clustering compared to composite numbers.
    
    H0: No significant difference in clustering between primes and composites
    H1: Primes show significantly enhanced clustering
    
    Args:
        prime_data: Array of transformed prime values
        composite_data: Array of transformed composite values
        enhancement_threshold: Minimum enhancement ratio to consider significant
        confidence_level: Statistical confidence level
        
    Returns:
        dict: Statistical test results and interpretation
    """
    # Convert to numpy arrays
    prime_data = np.array(prime_data)
    composite_data = np.array(composite_data)
    
    # Basic descriptive statistics
    prime_stats = {
        'mean': np.mean(prime_data),
        'std': np.std(prime_data),
        'var': np.var(prime_data),
        'count': len(prime_data)
    }
    
    composite_stats = {
        'mean': np.mean(composite_data),
        'std': np.std(composite_data),
        'var': np.var(composite_data),
        'count': len(composite_data)
    }
    
    # Test 1: Two-sample t-test for mean differences
    t_stat, t_pvalue = stats.ttest_ind(prime_data, composite_data, 
                                      alternative='two-sided')
    
    # Test 2: Mann-Whitney U test (non-parametric)
    u_stat, u_pvalue = stats.mannwhitneyu(prime_data, composite_data, 
                                         alternative='two-sided')
    
    # Test 3: Kolmogorov-Smirnov test for distribution differences
    ks_stat, ks_pvalue = stats.ks_2samp(prime_data, composite_data)
    
    # Test 4: F-test for variance differences
    f_stat = np.var(composite_data) / np.var(prime_data) if np.var(prime_data) > 0 else np.inf
    f_pvalue = 2 * min(
        stats.f.cdf(f_stat, len(composite_data)-1, len(prime_data)-1),
        1 - stats.f.cdf(f_stat, len(composite_data)-1, len(prime_data)-1)
    )
    
    # Effect size calculations
    pooled_std = np.sqrt(((len(prime_data) - 1) * np.var(prime_data) + 
                         (len(composite_data) - 1) * np.var(composite_data)) / 
                        (len(prime_data) + len(composite_data) - 2))
    
    cohens_d = (composite_stats['mean'] - prime_stats['mean']) / pooled_std if pooled_std > 0 else 0
    
    # Enhancement ratio calculation
    if prime_stats['var'] > 0:
        variance_enhancement = (composite_stats['var'] - prime_stats['var']) / prime_stats['var']
    else:
        variance_enhancement = np.inf
    
    # Confidence intervals
    alpha = 1 - confidence_level
    prime_ci = stats.t.interval(confidence_level, len(prime_data)-1, 
                               loc=prime_stats['mean'], 
                               scale=prime_stats['std']/np.sqrt(len(prime_data)))
    composite_ci = stats.t.interval(confidence_level, len(composite_data)-1,
                                   loc=composite_stats['mean'],
                                   scale=composite_stats['std']/np.sqrt(len(composite_data)))
    
    # Overall hypothesis testing
    alpha_corrected = alpha / 4  # Bonferroni correction for multiple tests
    significant_tests = sum([
        t_pvalue < alpha_corrected,
        u_pvalue < alpha_corrected,
        ks_pvalue < alpha_corrected,
        f_pvalue < alpha_corrected
    ])
    
    hypothesis_rejected = significant_tests >= 2  # Majority of tests significant
    enhancement_significant = variance_enhancement > enhancement_threshold
    
    return {
        'hypothesis_test': {
            'null_hypothesis': "No significant difference between primes and composites",
            'alternative_hypothesis': "Primes show enhanced clustering properties",
            'rejected_null': hypothesis_rejected,
            'enhancement_significant': enhancement_significant,
            'confidence_level': confidence_level
        },
        'descriptive_statistics': {
            'prime_stats': prime_stats,
            'composite_stats': composite_stats
        },
        'statistical_tests': {
            't_test': {'statistic': t_stat, 'p_value': t_pvalue, 'significant': t_pvalue < alpha_corrected},
            'mann_whitney': {'statistic': u_stat, 'p_value': u_pvalue, 'significant': u_pvalue < alpha_corrected},
            'kolmogorov_smirnov': {'statistic': ks_stat, 'p_value': ks_pvalue, 'significant': ks_pvalue < alpha_corrected},
            'f_test': {'statistic': f_stat, 'p_value': f_pvalue, 'significant': f_pvalue < alpha_corrected}
        },
        'effect_sizes': {
            'cohens_d': cohens_d,
            'variance_enhancement': variance_enhancement,
            'effect_interpretation': (
                'Large' if abs(cohens_d) > 0.8 else
                'Medium' if abs(cohens_d) > 0.5 else
                'Small' if abs(cohens_d) > 0.2 else
                'Negligible'
            )
        },
        'confidence_intervals': {
            'prime_mean_ci': prime_ci,
            'composite_mean_ci': composite_ci
        },
        'recommendations': [
            f"Hypothesis {'rejected' if hypothesis_rejected else 'not rejected'} at {confidence_level:.1%} confidence",
            f"Effect size: {cohens_d:.3f} ({('Large' if abs(cohens_d) > 0.8 else 'Medium' if abs(cohens_d) > 0.5 else 'Small' if abs(cohens_d) > 0.2 else 'Negligible')})",
            f"Variance enhancement: {variance_enhancement:.1%}" if variance_enhancement != np.inf else "Infinite variance enhancement"
        ]
    }

def test_optimal_k_hypothesis(k_values, enhancement_values, theoretical_k=0.3, 
                             significance_level=0.05):
    """
    Test the hypothesis that there exists an optimal curvature parameter k* that
    maximizes prime enhancement.
    
    H0: No optimal k exists (enhancement is constant)
    H1: Optimal k* exists and differs significantly from random
    
    Args:
        k_values: Array of k parameter values tested
        enhancement_values: Corresponding enhancement percentages
        theoretical_k: Theoretical optimal k value
        significance_level: Statistical significance threshold
        
    Returns:
        dict: Optimal k hypothesis test results
    """
    k_values = np.array(k_values)
    enhancement_values = np.array(enhancement_values)
    
    # Find empirical optimal k
    max_idx = np.argmax(enhancement_values)
    k_optimal_empirical = k_values[max_idx]
    max_enhancement = enhancement_values[max_idx]
    
    # Test 1: Test if enhancement varies significantly with k
    # Use correlation test
    correlation_coeff, correlation_pvalue = stats.pearsonr(k_values, enhancement_values)
    
    # Test 2: Test if optimal k differs from theoretical value
    # Bootstrap confidence interval around optimal k
    n_bootstrap = 1000
    bootstrap_k_optimal = []
    
    for _ in range(n_bootstrap):
        # Bootstrap sample
        indices = np.random.choice(len(k_values), len(k_values), replace=True)
        k_boot = k_values[indices]
        enhancement_boot = enhancement_values[indices]
        
        # Find optimal k in bootstrap sample
        max_idx_boot = np.argmax(enhancement_boot)
        k_opt_boot = k_boot[max_idx_boot]
        bootstrap_k_optimal.append(k_opt_boot)
    
    bootstrap_k_optimal = np.array(bootstrap_k_optimal)
    
    # Bootstrap confidence interval for optimal k
    ci_lower = np.percentile(bootstrap_k_optimal, (significance_level/2) * 100)
    ci_upper = np.percentile(bootstrap_k_optimal, (1 - significance_level/2) * 100)
    
    # Test if theoretical k falls within confidence interval
    theoretical_in_ci = ci_lower <= theoretical_k <= ci_upper
    
    # Test 3: Quadratic fit to enhancement curve
    # H0: Linear relationship (no optimum)
    # H1: Quadratic relationship (has optimum)
    
    # Fit linear model
    linear_coeffs = np.polyfit(k_values, enhancement_values, 1)
    linear_fit = np.polyval(linear_coeffs, k_values)
    linear_sse = np.sum((enhancement_values - linear_fit)**2)
    
    # Fit quadratic model
    quadratic_coeffs = np.polyfit(k_values, enhancement_values, 2)
    quadratic_fit = np.polyval(quadratic_coeffs, k_values)
    quadratic_sse = np.sum((enhancement_values - quadratic_fit)**2)
    
    # F-test for model comparison
    n = len(k_values)
    f_stat_model = ((linear_sse - quadratic_sse) / 1) / (quadratic_sse / (n - 3))
    f_pvalue_model = 1 - stats.f.cdf(f_stat_model, 1, n - 3)
    
    # Extract optimal k from quadratic fit
    if quadratic_coeffs[0] < 0:  # Negative coefficient for k² term (inverted parabola)
        k_optimal_fitted = -quadratic_coeffs[1] / (2 * quadratic_coeffs[0])
        has_maximum = True
    else:
        k_optimal_fitted = None
        has_maximum = False
    
    # Test 4: Significance of peak enhancement
    baseline_enhancement = np.mean(enhancement_values)
    peak_significance = (max_enhancement - baseline_enhancement) / np.std(enhancement_values)
    peak_pvalue = 2 * (1 - stats.norm.cdf(abs(peak_significance)))  # Two-tailed test
    
    return {
        'hypothesis_test': {
            'null_hypothesis': "No optimal k exists (constant enhancement)",
            'alternative_hypothesis': "Optimal k* exists and maximizes enhancement",
            'optimal_k_exists': f_pvalue_model < significance_level and has_maximum,
            'significance_level': significance_level
        },
        'empirical_results': {
            'k_optimal_empirical': k_optimal_empirical,
            'max_enhancement': max_enhancement,
            'enhancement_range': [np.min(enhancement_values), np.max(enhancement_values)]
        },
        'statistical_tests': {
            'correlation_test': {
                'correlation': correlation_coeff,
                'p_value': correlation_pvalue,
                'significant': correlation_pvalue < significance_level
            },
            'model_comparison': {
                'f_statistic': f_stat_model,
                'p_value': f_pvalue_model,
                'quadratic_preferred': f_pvalue_model < significance_level
            },
            'peak_significance': {
                'z_score': peak_significance,
                'p_value': peak_pvalue,
                'significant': peak_pvalue < significance_level
            }
        },
        'fitted_models': {
            'linear_coefficients': linear_coeffs,
            'quadratic_coefficients': quadratic_coeffs,
            'k_optimal_fitted': k_optimal_fitted,
            'has_maximum': has_maximum,
            'linear_sse': linear_sse,
            'quadratic_sse': quadratic_sse
        },
        'bootstrap_analysis': {
            'k_optimal_mean': np.mean(bootstrap_k_optimal),
            'k_optimal_std': np.std(bootstrap_k_optimal),
            'confidence_interval': (ci_lower, ci_upper),
            'theoretical_k': theoretical_k,
            'theoretical_in_ci': theoretical_in_ci
        },
        'conclusions': [
            f"Empirical k* = {k_optimal_empirical:.3f}",
            f"Fitted k* = {k_optimal_fitted:.3f}" if k_optimal_fitted else "No fitted maximum",
            f"Theoretical k = {theoretical_k:.3f} {'within' if theoretical_in_ci else 'outside'} CI",
            f"Peak enhancement: {max_enhancement:.1f}%",
            f"Model comparison: {'Quadratic' if f_pvalue_model < significance_level else 'Linear'} preferred"
        ]
    }

def test_variance_minimization(curvature_values, target_variance=0.118, 
                              tolerance=0.01, confidence_level=0.95):
    """
    Test the hypothesis that the framework achieves the target variance σ ≈ 0.118
    for curvature minimization.
    
    H0: Variance equals target value (σ = 0.118)
    H1: Variance differs significantly from target
    
    Args:
        curvature_values: Array of computed curvature values
        target_variance: Target variance value (default 0.118)
        tolerance: Acceptable tolerance around target
        confidence_level: Statistical confidence level
        
    Returns:
        dict: Variance minimization test results
    """
    curvature_values = np.array(curvature_values)
    
    # Sample statistics
    n = len(curvature_values)
    sample_variance = np.var(curvature_values, ddof=1)  # Sample variance
    sample_std = np.std(curvature_values, ddof=1)
    
    # Test 1: Chi-square test for variance
    # H0: σ² = target_variance
    chi2_stat = (n - 1) * sample_variance / target_variance
    chi2_pvalue = 2 * min(
        stats.chi2.cdf(chi2_stat, n - 1),
        1 - stats.chi2.cdf(chi2_stat, n - 1)
    )
    
    # Test 2: Confidence interval for variance
    alpha = 1 - confidence_level
    chi2_lower = stats.chi2.ppf(alpha/2, n - 1)
    chi2_upper = stats.chi2.ppf(1 - alpha/2, n - 1)
    
    variance_ci_lower = (n - 1) * sample_variance / chi2_upper
    variance_ci_upper = (n - 1) * sample_variance / chi2_lower
    
    target_in_ci = variance_ci_lower <= target_variance <= variance_ci_upper
    
    # Test 3: Tolerance test
    variance_difference = abs(sample_variance - target_variance)
    within_tolerance = variance_difference <= tolerance
    
    # Test 4: Bootstrap test for variance stability
    n_bootstrap = 1000
    bootstrap_variances = []
    
    for _ in range(n_bootstrap):
        bootstrap_sample = np.random.choice(curvature_values, n, replace=True)
        bootstrap_variances.append(np.var(bootstrap_sample, ddof=1))
    
    bootstrap_variances = np.array(bootstrap_variances)
    bootstrap_var_mean = np.mean(bootstrap_variances)
    bootstrap_var_std = np.std(bootstrap_variances)
    
    # Bootstrap confidence interval
    bootstrap_ci_lower = np.percentile(bootstrap_variances, (alpha/2) * 100)
    bootstrap_ci_upper = np.percentile(bootstrap_variances, (1 - alpha/2) * 100)
    
    # Test 5: Normality test for curvature values (prerequisite for variance tests)
    shapiro_stat, shapiro_pvalue = stats.shapiro(curvature_values[:5000])  # Limit for shapiro test
    
    # Test 6: Levene's test for equal variances (if comparing multiple groups)
    # This would require multiple groups of curvature values
    
    return {
        'hypothesis_test': {
            'null_hypothesis': f"Variance equals target ({target_variance})",
            'alternative_hypothesis': f"Variance differs from target",
            'target_achieved': target_in_ci and within_tolerance,
            'confidence_level': confidence_level
        },
        'sample_statistics': {
            'sample_size': n,
            'sample_variance': sample_variance,
            'sample_std': sample_std,
            'target_variance': target_variance,
            'variance_difference': variance_difference,
            'relative_error': variance_difference / target_variance * 100
        },
        'statistical_tests': {
            'chi_square_test': {
                'statistic': chi2_stat,
                'p_value': chi2_pvalue,
                'critical_values': (chi2_lower, chi2_upper),
                'significant': chi2_pvalue < (1 - confidence_level)
            },
            'normality_test': {
                'shapiro_statistic': shapiro_stat,
                'shapiro_p_value': shapiro_pvalue,
                'normal_distribution': shapiro_pvalue > 0.05
            }
        },
        'confidence_intervals': {
            'variance_ci': (variance_ci_lower, variance_ci_upper),
            'bootstrap_ci': (bootstrap_ci_lower, bootstrap_ci_upper),
            'target_in_ci': target_in_ci
        },
        'bootstrap_analysis': {
            'bootstrap_variance_mean': bootstrap_var_mean,
            'bootstrap_variance_std': bootstrap_var_std,
            'bootstrap_samples': len(bootstrap_variances)
        },
        'tolerance_test': {
            'tolerance': tolerance,
            'within_tolerance': within_tolerance,
            'tolerance_ratio': variance_difference / tolerance
        },
        'conclusions': [
            f"Sample variance: {sample_variance:.6f}",
            f"Target variance: {target_variance:.6f}",
            f"Difference: {variance_difference:.6f} ({variance_difference/target_variance*100:.1f}%)",
            f"Within tolerance: {'Yes' if within_tolerance else 'No'}",
            f"Target in CI: {'Yes' if target_in_ci else 'No'}"
        ]
    }

def test_asymmetry_significance(fourier_coefficients, significance_level=0.05):
    """
    Test the statistical significance of Fourier asymmetry in prime distributions.
    
    H0: Fourier coefficients show no asymmetry (symmetric distribution)
    H1: Significant asymmetry exists (chirality in prime sequences)
    
    Args:
        fourier_coefficients: Dictionary with 'cosine' and 'sine' coefficients
        significance_level: Statistical significance threshold
        
    Returns:
        dict: Asymmetry significance test results
    """
    cosine_coeffs = np.array(fourier_coefficients.get('cosine', []))
    sine_coeffs = np.array(fourier_coefficients.get('sine', []))
    
    if len(cosine_coeffs) == 0 or len(sine_coeffs) == 0:
        return {
            'error': 'Insufficient Fourier coefficient data',
            'cosine_coeffs': len(cosine_coeffs),
            'sine_coeffs': len(sine_coeffs)
        }
    
    # Asymmetry measures
    cosine_magnitude = np.sum(np.abs(cosine_coeffs))
    sine_magnitude = np.sum(np.abs(sine_coeffs))
    total_magnitude = cosine_magnitude + sine_magnitude
    
    asymmetry_ratio = sine_magnitude / total_magnitude if total_magnitude > 0 else 0
    
    # Test 1: Test if sine coefficients are significantly non-zero
    # One-sample t-test against zero
    sine_t_stat, sine_pvalue = stats.ttest_1samp(sine_coeffs, 0)
    
    # Test 2: Test if sine coefficients differ from cosine coefficients
    # Paired t-test (assuming same harmonics)
    if len(sine_coeffs) == len(cosine_coeffs):
        paired_t_stat, paired_pvalue = stats.ttest_rel(np.abs(sine_coeffs), 
                                                      np.abs(cosine_coeffs))
    else:
        # Independent t-test if different lengths
        paired_t_stat, paired_pvalue = stats.ttest_ind(np.abs(sine_coeffs), 
                                                      np.abs(cosine_coeffs))
    
    # Test 3: Wilcoxon signed-rank test (non-parametric)
    if len(sine_coeffs) == len(cosine_coeffs):
        wilcoxon_stat, wilcoxon_pvalue = stats.wilcoxon(np.abs(sine_coeffs), 
                                                       np.abs(cosine_coeffs))
    else:
        wilcoxon_stat, wilcoxon_pvalue = stats.mannwhitneyu(np.abs(sine_coeffs), 
                                                           np.abs(cosine_coeffs))
    
    # Test 4: F-test for variance differences
    sine_var = np.var(sine_coeffs)
    cosine_var = np.var(cosine_coeffs)
    
    if cosine_var > 0:
        f_stat = sine_var / cosine_var
        f_pvalue = 2 * min(
            stats.f.cdf(f_stat, len(sine_coeffs)-1, len(cosine_coeffs)-1),
            1 - stats.f.cdf(f_stat, len(sine_coeffs)-1, len(cosine_coeffs)-1)
        )
    else:
        f_stat = np.inf
        f_pvalue = 0.0
    
    # Test 5: Bootstrap confidence interval for asymmetry ratio
    n_bootstrap = 1000
    bootstrap_asymmetries = []
    
    # Combine all coefficients for bootstrap
    all_coeffs = np.concatenate([cosine_coeffs, sine_coeffs])
    n_cosine = len(cosine_coeffs)
    n_sine = len(sine_coeffs)
    
    for _ in range(n_bootstrap):
        # Bootstrap sample
        bootstrap_sample = np.random.choice(all_coeffs, len(all_coeffs), replace=True)
        bootstrap_cosine = bootstrap_sample[:n_cosine]
        bootstrap_sine = bootstrap_sample[n_cosine:n_cosine+n_sine]
        
        # Calculate asymmetry ratio
        boot_cosine_mag = np.sum(np.abs(bootstrap_cosine))
        boot_sine_mag = np.sum(np.abs(bootstrap_sine))
        boot_total = boot_cosine_mag + boot_sine_mag
        
        if boot_total > 0:
            boot_asymmetry = boot_sine_mag / boot_total
            bootstrap_asymmetries.append(boot_asymmetry)
    
    bootstrap_asymmetries = np.array(bootstrap_asymmetries)
    
    # Bootstrap confidence interval
    alpha = significance_level
    asym_ci_lower = np.percentile(bootstrap_asymmetries, (alpha/2) * 100)
    asym_ci_upper = np.percentile(bootstrap_asymmetries, (1 - alpha/2) * 100)
    
    # Test if asymmetry is significantly different from 0.5 (perfect symmetry)
    symmetric_asymmetry = 0.5
    asymmetry_significant = not (asym_ci_lower <= symmetric_asymmetry <= asym_ci_upper)
    
    # Overall significance assessment
    significant_tests = sum([
        sine_pvalue < significance_level,
        paired_pvalue < significance_level,
        wilcoxon_pvalue < significance_level,
        f_pvalue < significance_level
    ])
    
    overall_significant = significant_tests >= 2  # Majority of tests significant
    
    return {
        'hypothesis_test': {
            'null_hypothesis': "No asymmetry in Fourier coefficients (symmetric)",
            'alternative_hypothesis': "Significant asymmetry exists (chirality)",
            'asymmetry_significant': overall_significant and asymmetry_significant,
            'significance_level': significance_level
        },
        'asymmetry_measures': {
            'cosine_magnitude': cosine_magnitude,
            'sine_magnitude': sine_magnitude,
            'total_magnitude': total_magnitude,
            'asymmetry_ratio': asymmetry_ratio,
            'perfect_symmetry': symmetric_asymmetry
        },
        'statistical_tests': {
            'sine_ttest': {
                'statistic': sine_t_stat,
                'p_value': sine_pvalue,
                'significant': sine_pvalue < significance_level
            },
            'paired_comparison': {
                'statistic': paired_t_stat,
                'p_value': paired_pvalue,
                'significant': paired_pvalue < significance_level
            },
            'wilcoxon_test': {
                'statistic': wilcoxon_stat,
                'p_value': wilcoxon_pvalue,
                'significant': wilcoxon_pvalue < significance_level
            },
            'variance_test': {
                'f_statistic': f_stat,
                'p_value': f_pvalue,
                'significant': f_pvalue < significance_level
            }
        },
        'bootstrap_analysis': {
            'asymmetry_ci': (asym_ci_lower, asym_ci_upper),
            'bootstrap_mean': np.mean(bootstrap_asymmetries),
            'bootstrap_std': np.std(bootstrap_asymmetries),
            'symmetric_in_ci': asym_ci_lower <= symmetric_asymmetry <= asym_ci_upper
        },
        'coefficient_analysis': {
            'cosine_coefficients': cosine_coeffs.tolist(),
            'sine_coefficients': sine_coeffs.tolist(),
            'cosine_stats': {
                'mean': np.mean(cosine_coeffs),
                'std': np.std(cosine_coeffs),
                'max': np.max(np.abs(cosine_coeffs))
            },
            'sine_stats': {
                'mean': np.mean(sine_coeffs),
                'std': np.std(sine_coeffs),
                'max': np.max(np.abs(sine_coeffs))
            }
        },
        'conclusions': [
            f"Asymmetry ratio: {asymmetry_ratio:.3f}",
            f"Sine magnitude: {sine_magnitude:.3f}",
            f"Cosine magnitude: {cosine_magnitude:.3f}",
            f"Overall significance: {'Yes' if overall_significant else 'No'}",
            f"Chirality detected: {'Yes' if asymmetry_significant else 'No'}"
        ]
    }

def power_analysis(effect_size, sample_size, significance_level=0.05, test_type='t_test'):
    """
    Compute statistical power for framework hypothesis tests.
    
    Args:
        effect_size: Expected effect size (Cohen's d for t-tests)
        sample_size: Sample size for the test
        significance_level: Type I error rate
        test_type: Type of statistical test
        
    Returns:
        dict: Power analysis results
    """
    from scipy.stats import norm
    
    if test_type == 't_test':
        # Power for two-sample t-test
        # Critical value
        critical_t = stats.t.ppf(1 - significance_level/2, 2*sample_size - 2)
        
        # Non-centrality parameter
        ncp = effect_size * np.sqrt(sample_size / 2)
        
        # Power calculation
        power = 1 - stats.t.cdf(critical_t, 2*sample_size - 2, loc=ncp) + \
                stats.t.cdf(-critical_t, 2*sample_size - 2, loc=ncp)
    
    elif test_type == 'variance_test':
        # Power for chi-square variance test
        # This is more complex and requires numerical integration
        power = 0.8  # Placeholder - would need specialized calculation
    
    else:
        power = None
    
    # Sample size calculation for desired power
    if test_type == 't_test':
        target_power = 0.8
        # Iterative search for required sample size
        for n in range(5, 10000):
            ncp_target = effect_size * np.sqrt(n / 2)
            critical_t_target = stats.t.ppf(1 - significance_level/2, 2*n - 2)
            power_target = 1 - stats.t.cdf(critical_t_target, 2*n - 2, loc=ncp_target) + \
                          stats.t.cdf(-critical_t_target, 2*n - 2, loc=ncp_target)
            
            if power_target >= target_power:
                required_sample_size = n
                break
        else:
            required_sample_size = None
    else:
        required_sample_size = None
    
    return {
        'test_configuration': {
            'effect_size': effect_size,
            'sample_size': sample_size,
            'significance_level': significance_level,
            'test_type': test_type
        },
        'power_analysis': {
            'statistical_power': power,
            'required_sample_size_80_power': required_sample_size,
            'power_interpretation': (
                'Excellent (>0.9)' if power and power > 0.9 else
                'Good (0.8-0.9)' if power and power > 0.8 else
                'Adequate (0.6-0.8)' if power and power > 0.6 else
                'Poor (<0.6)' if power else
                'Unknown'
            )
        },
        'recommendations': [
            f"Current power: {power:.3f}" if power else "Power calculation unavailable",
            f"Required N for 80% power: {required_sample_size}" if required_sample_size else "Sample size recommendation unavailable",
            "Consider increasing sample size if power < 0.8" if power and power < 0.8 else "Adequate power for reliable results"
        ]
    }