"""
Distribution Analysis Module
===========================

SciPy-based distribution fitting and analysis for prime number sequences
and geometric transformations in the Z Framework.
"""

import numpy as np
import scipy.stats as stats
from scipy.optimize import minimize
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import warnings

def analyze_prime_distribution(prime_sequence, test_distributions=None, significance_level=0.05):
    """
    Analyze the statistical distribution of prime-related sequences.
    
    Tests various probability distributions to find the best fit for
    prime gap sequences, prime densities, or transformed prime values.
    
    Args:
        prime_sequence: Array of prime-related values to analyze
        test_distributions: List of scipy.stats distributions to test
        significance_level: Significance level for goodness-of-fit tests
        
    Returns:
        dict: Distribution analysis results
    """
    if test_distributions is None:
        test_distributions = [
            stats.norm,      # Normal distribution
            stats.gamma,     # Gamma distribution
            stats.lognorm,   # Log-normal distribution
            stats.expon,     # Exponential distribution
            stats.weibull_min, # Weibull distribution
            stats.beta,      # Beta distribution (for bounded data)
            stats.pareto,    # Pareto distribution
            stats.uniform    # Uniform distribution
        ]
    
    prime_sequence = np.array(prime_sequence)
    
    # Basic descriptive statistics
    descriptive_stats = {
        'count': len(prime_sequence),
        'mean': np.mean(prime_sequence),
        'std': np.std(prime_sequence),
        'var': np.var(prime_sequence),
        'median': np.median(prime_sequence),
        'mode': stats.mode(prime_sequence, keepdims=True)[0][0] if len(stats.mode(prime_sequence, keepdims=True)[0]) > 0 else None,
        'skewness': stats.skew(prime_sequence),
        'kurtosis': stats.kurtosis(prime_sequence),
        'min': np.min(prime_sequence),
        'max': np.max(prime_sequence),
        'range': np.max(prime_sequence) - np.min(prime_sequence),
        'q25': np.percentile(prime_sequence, 25),
        'q75': np.percentile(prime_sequence, 75),
        'iqr': np.percentile(prime_sequence, 75) - np.percentile(prime_sequence, 25)
    }
    
    # Test normality
    if len(prime_sequence) <= 5000:
        shapiro_stat, shapiro_pvalue = stats.shapiro(prime_sequence)
    else:
        # Use Anderson-Darling for larger samples
        ad_result = stats.anderson(prime_sequence, dist='norm')
        shapiro_stat, shapiro_pvalue = ad_result.statistic, None
    
    # Jarque-Bera test for normality
    jb_stat, jb_pvalue = stats.jarque_bera(prime_sequence)
    
    # D'Agostino's normality test
    k2_stat, k2_pvalue = stats.normaltest(prime_sequence)
    
    normality_tests = {
        'shapiro_wilk': {'statistic': shapiro_stat, 'p_value': shapiro_pvalue},
        'jarque_bera': {'statistic': jb_stat, 'p_value': jb_pvalue},
        'dagostino': {'statistic': k2_stat, 'p_value': k2_pvalue},
        'is_normal': jb_pvalue > significance_level if jb_pvalue else False
    }
    
    # Distribution fitting
    distribution_fits = {}
    
    for dist in test_distributions:
        try:
            # Fit distribution parameters
            if dist.name == 'beta':
                # Beta distribution requires data in [0,1]
                if np.min(prime_sequence) >= 0 and np.max(prime_sequence) <= 1:
                    params = dist.fit(prime_sequence)
                else:
                    # Normalize to [0,1] for beta fitting
                    normalized_data = (prime_sequence - np.min(prime_sequence)) / (np.max(prime_sequence) - np.min(prime_sequence))
                    params = dist.fit(normalized_data)
            else:
                params = dist.fit(prime_sequence)
            
            # Kolmogorov-Smirnov test
            ks_stat, ks_pvalue = stats.kstest(prime_sequence, 
                                            lambda x: dist.cdf(x, *params))
            
            # Anderson-Darling test (if available)
            try:
                ad_result = stats.anderson(prime_sequence, dist=dist.name)
                ad_stat = ad_result.statistic
                ad_critical = ad_result.critical_values
            except:
                ad_stat, ad_critical = None, None
            
            # Log-likelihood
            log_likelihood = np.sum(dist.logpdf(prime_sequence, *params))
            
            # AIC and BIC
            k = len(params)  # Number of parameters
            n = len(prime_sequence)
            aic = 2 * k - 2 * log_likelihood
            bic = k * np.log(n) - 2 * log_likelihood
            
            distribution_fits[dist.name] = {
                'distribution': dist,
                'parameters': params,
                'ks_statistic': ks_stat,
                'ks_p_value': ks_pvalue,
                'ad_statistic': ad_stat,
                'ad_critical_values': ad_critical,
                'log_likelihood': log_likelihood,
                'aic': aic,
                'bic': bic,
                'fit_quality': 'good' if ks_pvalue > significance_level else 'poor'
            }
            
        except Exception as e:
            distribution_fits[dist.name] = {
                'error': str(e),
                'fit_quality': 'failed'
            }
    
    # Find best distribution based on AIC
    successful_fits = {k: v for k, v in distribution_fits.items() 
                      if 'aic' in v and np.isfinite(v['aic'])}
    
    if successful_fits:
        best_distribution = min(successful_fits.keys(), 
                              key=lambda k: successful_fits[k]['aic'])
        best_fit = successful_fits[best_distribution]
    else:
        best_distribution = None
        best_fit = None
    
    # Quantile-Quantile plot data (for visualization)
    if best_fit:
        theoretical_quantiles = best_fit['distribution'].ppf(
            np.linspace(0.01, 0.99, len(prime_sequence)),
            *best_fit['parameters']
        )
        sample_quantiles = np.sort(prime_sequence)
        qq_data = {
            'theoretical': theoretical_quantiles,
            'sample': sample_quantiles,
            'distribution': best_distribution
        }
    else:
        qq_data = None
    
    return {
        'descriptive_statistics': descriptive_stats,
        'normality_tests': normality_tests,
        'distribution_fits': distribution_fits,
        'best_distribution': {
            'name': best_distribution,
            'parameters': best_fit['parameters'] if best_fit else None,
            'aic': best_fit['aic'] if best_fit else None,
            'bic': best_fit['bic'] if best_fit else None,
            'fit_quality': best_fit['fit_quality'] if best_fit else None
        },
        'qq_plot_data': qq_data,
        'analysis_summary': {
            'sample_size': len(prime_sequence),
            'likely_normal': normality_tests['is_normal'],
            'best_fit_available': best_distribution is not None,
            'distributions_tested': len(test_distributions)
        }
    }

def fit_distribution_models(data, model_type='gmm', n_components=None, **kwargs):
    """
    Fit advanced distribution models to data using various approaches.
    
    Args:
        data: Input data array
        model_type: Type of model ('gmm', 'kde', 'histogram')
        n_components: Number of components (for mixture models)
        **kwargs: Additional model parameters
        
    Returns:
        dict: Fitted model results and analysis
    """
    data = np.array(data).reshape(-1, 1)
    
    if model_type == 'gmm':
        # Gaussian Mixture Model
        if n_components is None:
            # Use BIC to select optimal number of components
            bic_scores = []
            aic_scores = []
            component_range = range(1, min(11, len(data)//10 + 1))
            
            for n in component_range:
                gmm = GaussianMixture(n_components=n, **kwargs)
                gmm.fit(data)
                bic_scores.append(gmm.bic(data))
                aic_scores.append(gmm.aic(data))
            
            optimal_components_bic = component_range[np.argmin(bic_scores)]
            optimal_components_aic = component_range[np.argmin(aic_scores)]
            
            # Use BIC-optimal for final model
            n_components = optimal_components_bic
        else:
            bic_scores = None
            aic_scores = None
            component_range = None
            optimal_components_bic = n_components
            optimal_components_aic = n_components
        
        # Fit final GMM
        gmm = GaussianMixture(n_components=n_components, **kwargs)
        gmm.fit(data)
        
        # Extract parameters
        means = gmm.means_.flatten()
        covariances = gmm.covariances_.flatten()
        weights = gmm.weights_
        
        # Compute component statistics
        component_stats = []
        for i in range(n_components):
            component_stats.append({
                'mean': means[i],
                'std': np.sqrt(covariances[i]),
                'weight': weights[i],
                'variance': covariances[i]
            })
        
        # Model evaluation
        log_likelihood = gmm.score(data)
        aic = gmm.aic(data)
        bic = gmm.bic(data)
        
        # Predict cluster assignments
        cluster_assignments = gmm.predict(data)
        cluster_probabilities = gmm.predict_proba(data)
        
        result = {
            'model_type': 'gaussian_mixture',
            'model': gmm,
            'n_components': n_components,
            'component_statistics': component_stats,
            'model_scores': {
                'log_likelihood': log_likelihood,
                'aic': aic,
                'bic': bic
            },
            'cluster_assignments': cluster_assignments,
            'cluster_probabilities': cluster_probabilities,
            'selection_process': {
                'component_range': component_range,
                'bic_scores': bic_scores,
                'aic_scores': aic_scores,
                'optimal_components_bic': optimal_components_bic,
                'optimal_components_aic': optimal_components_aic
            }
        }
        
    elif model_type == 'kde':
        # Kernel Density Estimation
        from scipy.stats import gaussian_kde
        
        bandwidth = kwargs.get('bandwidth', 'scott')
        kde = gaussian_kde(data.flatten(), bw_method=bandwidth)
        
        # Evaluate KDE on a grid
        x_grid = np.linspace(np.min(data), np.max(data), 1000)
        density = kde(x_grid)
        
        # Find peaks (modes)
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(density, height=0.01 * np.max(density))
        peak_locations = x_grid[peaks]
        peak_densities = density[peaks]
        
        result = {
            'model_type': 'kernel_density',
            'kde_model': kde,
            'bandwidth': kde.factor,
            'x_grid': x_grid,
            'density': density,
            'peaks': {
                'locations': peak_locations,
                'densities': peak_densities,
                'count': len(peak_locations)
            }
        }
        
    elif model_type == 'histogram':
        # Histogram-based distribution
        n_bins = kwargs.get('n_bins', 'auto')
        
        if n_bins == 'auto':
            # Use Freedman-Diaconis rule
            iqr = np.percentile(data, 75) - np.percentile(data, 25)
            bin_width = 2 * iqr / (len(data) ** (1/3))
            n_bins = int((np.max(data) - np.min(data)) / bin_width)
            n_bins = max(1, min(n_bins, 100))  # Reasonable bounds
        
        counts, bin_edges = np.histogram(data, bins=n_bins, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Find peaks in histogram
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(counts, height=0.01 * np.max(counts))
        peak_locations = bin_centers[peaks]
        peak_heights = counts[peaks]
        
        result = {
            'model_type': 'histogram',
            'n_bins': n_bins,
            'counts': counts,
            'bin_edges': bin_edges,
            'bin_centers': bin_centers,
            'peaks': {
                'locations': peak_locations,
                'heights': peak_heights,
                'count': len(peak_locations)
            }
        }
    
    else:
        raise ValueError(f"Unknown model_type: {model_type}")
    
    # Add common statistics
    result['data_statistics'] = {
        'sample_size': len(data),
        'mean': np.mean(data),
        'std': np.std(data),
        'min': np.min(data),
        'max': np.max(data)
    }
    
    return result

def test_normality_assumptions(data, tests=None, significance_level=0.05):
    """
    Comprehensive testing of normality assumptions for statistical tests.
    
    Args:
        data: Input data array
        tests: List of normality tests to perform
        significance_level: Significance threshold
        
    Returns:
        dict: Normality test results and recommendations
    """
    if tests is None:
        tests = ['shapiro', 'jarque_bera', 'dagostino', 'anderson', 'lilliefors']
    
    data = np.array(data)
    
    # Remove infinite and NaN values
    data_clean = data[np.isfinite(data)]
    
    if len(data_clean) == 0:
        return {
            'error': 'No finite data points available',
            'original_size': len(data),
            'clean_size': 0
        }
    
    results = {}
    
    # Shapiro-Wilk test (best for small samples)
    if 'shapiro' in tests and len(data_clean) <= 5000:
        try:
            shapiro_stat, shapiro_pvalue = stats.shapiro(data_clean)
            results['shapiro_wilk'] = {
                'statistic': shapiro_stat,
                'p_value': shapiro_pvalue,
                'is_normal': shapiro_pvalue > significance_level,
                'interpretation': 'Normal' if shapiro_pvalue > significance_level else 'Non-normal'
            }
        except Exception as e:
            results['shapiro_wilk'] = {'error': str(e)}
    
    # Jarque-Bera test
    if 'jarque_bera' in tests:
        try:
            jb_stat, jb_pvalue = stats.jarque_bera(data_clean)
            results['jarque_bera'] = {
                'statistic': jb_stat,
                'p_value': jb_pvalue,
                'is_normal': jb_pvalue > significance_level,
                'interpretation': 'Normal' if jb_pvalue > significance_level else 'Non-normal'
            }
        except Exception as e:
            results['jarque_bera'] = {'error': str(e)}
    
    # D'Agostino's normality test
    if 'dagostino' in tests:
        try:
            k2_stat, k2_pvalue = stats.normaltest(data_clean)
            results['dagostino'] = {
                'statistic': k2_stat,
                'p_value': k2_pvalue,
                'is_normal': k2_pvalue > significance_level,
                'interpretation': 'Normal' if k2_pvalue > significance_level else 'Non-normal'
            }
        except Exception as e:
            results['dagostino'] = {'error': str(e)}
    
    # Anderson-Darling test
    if 'anderson' in tests:
        try:
            ad_result = stats.anderson(data_clean, dist='norm')
            # Check against 5% significance level (index 2)
            critical_value = ad_result.critical_values[2]
            is_normal_ad = ad_result.statistic < critical_value
            
            results['anderson_darling'] = {
                'statistic': ad_result.statistic,
                'critical_values': ad_result.critical_values,
                'significance_levels': ad_result.significance_level,
                'is_normal': is_normal_ad,
                'interpretation': 'Normal' if is_normal_ad else 'Non-normal'
            }
        except Exception as e:
            results['anderson_darling'] = {'error': str(e)}
    
    # Lilliefors test (if available)
    if 'lilliefors' in tests:
        try:
            # Lilliefors test using KS test with estimated parameters
            data_standardized = (data_clean - np.mean(data_clean)) / np.std(data_clean)
            ks_stat, ks_pvalue = stats.kstest(data_standardized, 'norm')
            
            results['lilliefors'] = {
                'statistic': ks_stat,
                'p_value': ks_pvalue,
                'is_normal': ks_pvalue > significance_level,
                'interpretation': 'Normal' if ks_pvalue > significance_level else 'Non-normal',
                'note': 'Approximated using KS test with standardized data'
            }
        except Exception as e:
            results['lilliefors'] = {'error': str(e)}
    
    # Summary statistics
    successful_tests = [test for test in results.keys() 
                       if 'error' not in results[test]]
    
    normal_votes = sum(1 for test in successful_tests 
                      if results[test].get('is_normal', False))
    
    total_tests = len(successful_tests)
    normality_consensus = normal_votes / total_tests if total_tests > 0 else 0
    
    # Overall recommendation
    if normality_consensus >= 0.6:
        overall_recommendation = 'normal'
        statistical_approach = 'parametric'
    elif normality_consensus <= 0.4:
        overall_recommendation = 'non_normal'
        statistical_approach = 'non_parametric'
    else:
        overall_recommendation = 'uncertain'
        statistical_approach = 'robust_methods'
    
    return {
        'test_results': results,
        'summary': {
            'total_tests': total_tests,
            'successful_tests': len(successful_tests),
            'normal_votes': normal_votes,
            'normality_consensus': normality_consensus,
            'overall_recommendation': overall_recommendation,
            'recommended_approach': statistical_approach
        },
        'data_info': {
            'original_size': len(data),
            'clean_size': len(data_clean),
            'removed_values': len(data) - len(data_clean),
            'mean': np.mean(data_clean),
            'std': np.std(data_clean),
            'skewness': stats.skew(data_clean),
            'kurtosis': stats.kurtosis(data_clean)
        },
        'recommendations': [
            f"Data appears to be {overall_recommendation}",
            f"Recommend {statistical_approach} statistical methods",
            f"Consensus: {normality_consensus:.1%} of tests suggest normality",
            "Consider transformation if normality is required" if overall_recommendation == 'non_normal' else "Normality assumptions likely satisfied"
        ]
    }

def distribution_comparison_test(data1, data2, test_type='auto', significance_level=0.05):
    """
    Compare distributions between two datasets.
    
    Args:
        data1, data2: Arrays of data to compare
        test_type: Type of comparison test ('auto', 'ks', 'mw', 'permutation')
        significance_level: Statistical significance threshold
        
    Returns:
        dict: Distribution comparison results
    """
    data1 = np.array(data1)
    data2 = np.array(data2)
    
    # Remove infinite and NaN values
    data1_clean = data1[np.isfinite(data1)]
    data2_clean = data2[np.isfinite(data2)]
    
    if len(data1_clean) == 0 or len(data2_clean) == 0:
        return {
            'error': 'Insufficient finite data for comparison',
            'data1_size': len(data1_clean),
            'data2_size': len(data2_clean)
        }
    
    # Descriptive statistics comparison
    stats_comparison = {
        'data1': {
            'count': len(data1_clean),
            'mean': np.mean(data1_clean),
            'std': np.std(data1_clean),
            'median': np.median(data1_clean),
            'min': np.min(data1_clean),
            'max': np.max(data1_clean)
        },
        'data2': {
            'count': len(data2_clean),
            'mean': np.mean(data2_clean),
            'std': np.std(data2_clean),
            'median': np.median(data2_clean),
            'min': np.min(data2_clean),
            'max': np.max(data2_clean)
        }
    }
    
    # Statistical tests
    test_results = {}
    
    # Kolmogorov-Smirnov test
    if test_type in ['auto', 'ks']:
        ks_stat, ks_pvalue = stats.ks_2samp(data1_clean, data2_clean)
        test_results['kolmogorov_smirnov'] = {
            'statistic': ks_stat,
            'p_value': ks_pvalue,
            'significant': ks_pvalue < significance_level,
            'interpretation': 'Different distributions' if ks_pvalue < significance_level else 'Same distribution'
        }
    
    # Mann-Whitney U test (for location differences)
    if test_type in ['auto', 'mw']:
        mw_stat, mw_pvalue = stats.mannwhitneyu(data1_clean, data2_clean, 
                                               alternative='two-sided')
        test_results['mann_whitney'] = {
            'statistic': mw_stat,
            'p_value': mw_pvalue,
            'significant': mw_pvalue < significance_level,
            'interpretation': 'Different locations' if mw_pvalue < significance_level else 'Same location'
        }
    
    # Welch's t-test (assuming unequal variances)
    if test_type in ['auto']:
        t_stat, t_pvalue = stats.ttest_ind(data1_clean, data2_clean, equal_var=False)
        test_results['welch_t_test'] = {
            'statistic': t_stat,
            'p_value': t_pvalue,
            'significant': t_pvalue < significance_level,
            'interpretation': 'Different means' if t_pvalue < significance_level else 'Same mean'
        }
    
    # Levene's test for equal variances
    if test_type in ['auto']:
        levene_stat, levene_pvalue = stats.levene(data1_clean, data2_clean)
        test_results['levene_variance'] = {
            'statistic': levene_stat,
            'p_value': levene_pvalue,
            'significant': levene_pvalue < significance_level,
            'interpretation': 'Different variances' if levene_pvalue < significance_level else 'Equal variances'
        }
    
    # Permutation test (if requested)
    if test_type == 'permutation':
        from scipy.stats import permutation_test
        
        def statistic(x, y):
            return np.mean(x) - np.mean(y)
        
        perm_result = permutation_test((data1_clean, data2_clean), 
                                     statistic, 
                                     n_resamples=1000,
                                     alternative='two-sided')
        
        test_results['permutation_test'] = {
            'statistic': perm_result.statistic,
            'p_value': perm_result.pvalue,
            'significant': perm_result.pvalue < significance_level,
            'interpretation': 'Significant difference' if perm_result.pvalue < significance_level else 'No significant difference'
        }
    
    # Effect size calculation
    pooled_std = np.sqrt(((len(data1_clean) - 1) * np.var(data1_clean) + 
                         (len(data2_clean) - 1) * np.var(data2_clean)) / 
                        (len(data1_clean) + len(data2_clean) - 2))
    
    cohens_d = (np.mean(data1_clean) - np.mean(data2_clean)) / pooled_std if pooled_std > 0 else 0
    
    # Overall assessment
    significant_tests = sum(1 for test in test_results.values() 
                           if test.get('significant', False))
    total_tests = len(test_results)
    
    overall_different = significant_tests / total_tests > 0.5 if total_tests > 0 else False
    
    return {
        'descriptive_comparison': stats_comparison,
        'statistical_tests': test_results,
        'effect_size': {
            'cohens_d': cohens_d,
            'interpretation': (
                'Large' if abs(cohens_d) > 0.8 else
                'Medium' if abs(cohens_d) > 0.5 else
                'Small' if abs(cohens_d) > 0.2 else
                'Negligible'
            )
        },
        'overall_assessment': {
            'distributions_different': overall_different,
            'significant_tests': significant_tests,
            'total_tests': total_tests,
            'consensus_level': significant_tests / total_tests if total_tests > 0 else 0
        },
        'recommendations': [
            f"Distributions are {'likely different' if overall_different else 'likely similar'}",
            f"Effect size: {abs(cohens_d):.3f} ({('Large' if abs(cohens_d) > 0.8 else 'Medium' if abs(cohens_d) > 0.5 else 'Small' if abs(cohens_d) > 0.2 else 'Negligible')})",
            f"Consensus: {significant_tests}/{total_tests} tests show significant differences"
        ]
    }