"""
Correlation Analysis Module
==========================

Statistical correlation and regression analysis for validating relationships
between prime distributions, zeta zeros, and geometric transformations.
"""

import numpy as np
import scipy.stats as stats
from scipy.optimize import curve_fit
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import cross_val_score
import warnings

def correlate_zeta_zeros_primes(zeta_zeros, prime_data, correlation_types=None):
    """
    Analyze correlation between Riemann zeta zeros and prime-related sequences.
    
    Tests the claimed convergence between prime analysis and zeta zero analysis
    with reported Pearson correlation r = 0.93.
    
    Args:
        zeta_zeros: Array of zeta zero positions or related values
        prime_data: Array of prime-related measurements
        correlation_types: List of correlation methods to use
        
    Returns:
        dict: Comprehensive correlation analysis results
    """
    if correlation_types is None:
        correlation_types = ['pearson', 'spearman', 'kendall']
    
    zeta_zeros = np.array(zeta_zeros)
    prime_data = np.array(prime_data)
    
    # Ensure equal lengths by truncating to minimum
    min_length = min(len(zeta_zeros), len(prime_data))
    zeta_zeros = zeta_zeros[:min_length]
    prime_data = prime_data[:min_length]
    
    # Remove pairs with infinite or NaN values
    valid_mask = np.isfinite(zeta_zeros) & np.isfinite(prime_data)
    zeta_clean = zeta_zeros[valid_mask]
    prime_clean = prime_data[valid_mask]
    
    if len(zeta_clean) < 3:
        return {
            'error': 'Insufficient valid data points for correlation analysis',
            'original_length': min_length,
            'valid_points': len(zeta_clean)
        }
    
    correlation_results = {}
    
    # Pearson correlation (linear relationship)
    if 'pearson' in correlation_types:
        pearson_r, pearson_p = stats.pearsonr(zeta_clean, prime_clean)
        correlation_results['pearson'] = {
            'correlation': pearson_r,
            'p_value': pearson_p,
            'significant': pearson_p < 0.05,
            'strength': (
                'Very Strong' if abs(pearson_r) > 0.9 else
                'Strong' if abs(pearson_r) > 0.7 else
                'Moderate' if abs(pearson_r) > 0.5 else
                'Weak' if abs(pearson_r) > 0.3 else
                'Very Weak'
            ),
            'direction': 'Positive' if pearson_r > 0 else 'Negative'
        }
    
    # Spearman correlation (monotonic relationship)
    if 'spearman' in correlation_types:
        spearman_r, spearman_p = stats.spearmanr(zeta_clean, prime_clean)
        correlation_results['spearman'] = {
            'correlation': spearman_r,
            'p_value': spearman_p,
            'significant': spearman_p < 0.05,
            'strength': (
                'Very Strong' if abs(spearman_r) > 0.9 else
                'Strong' if abs(spearman_r) > 0.7 else
                'Moderate' if abs(spearman_r) > 0.5 else
                'Weak' if abs(spearman_r) > 0.3 else
                'Very Weak'
            ),
            'direction': 'Positive' if spearman_r > 0 else 'Negative'
        }
    
    # Kendall's tau (rank correlation)
    if 'kendall' in correlation_types:
        kendall_tau, kendall_p = stats.kendalltau(zeta_clean, prime_clean)
        correlation_results['kendall'] = {
            'correlation': kendall_tau,
            'p_value': kendall_p,
            'significant': kendall_p < 0.05,
            'strength': (
                'Very Strong' if abs(kendall_tau) > 0.7 else
                'Strong' if abs(kendall_tau) > 0.5 else
                'Moderate' if abs(kendall_tau) > 0.3 else
                'Weak' if abs(kendall_tau) > 0.2 else
                'Very Weak'
            ),
            'direction': 'Positive' if kendall_tau > 0 else 'Negative'
        }
    
    # Test against documented claim (r = 0.93)
    documented_correlation = 0.93
    pearson_r = correlation_results.get('pearson', {}).get('correlation', 0)
    
    correlation_validation = {
        'documented_claim': documented_correlation,
        'observed_pearson': pearson_r,
        'difference': abs(pearson_r - documented_correlation),
        'claim_supported': abs(pearson_r - documented_correlation) < 0.05,
        'confidence_interval': None
    }
    
    # Bootstrap confidence interval for Pearson correlation
    n_bootstrap = 1000
    bootstrap_correlations = []
    
    for _ in range(n_bootstrap):
        # Bootstrap sample
        indices = np.random.choice(len(zeta_clean), len(zeta_clean), replace=True)
        zeta_boot = zeta_clean[indices]
        prime_boot = prime_clean[indices]
        
        # Calculate correlation
        boot_r, _ = stats.pearsonr(zeta_boot, prime_boot)
        bootstrap_correlations.append(boot_r)
    
    bootstrap_correlations = np.array(bootstrap_correlations)
    ci_lower = np.percentile(bootstrap_correlations, 2.5)
    ci_upper = np.percentile(bootstrap_correlations, 97.5)
    
    correlation_validation['confidence_interval'] = (ci_lower, ci_upper)
    correlation_validation['claim_in_ci'] = ci_lower <= documented_correlation <= ci_upper
    
    # Partial correlation analysis (removing linear trends)
    detrended_zeta = stats.zscore(zeta_clean)
    detrended_prime = stats.zscore(prime_clean)
    
    # Remove linear trend
    z_trend = np.polyfit(range(len(detrended_zeta)), detrended_zeta, 1)
    p_trend = np.polyfit(range(len(detrended_prime)), detrended_prime, 1)
    
    zeta_detrended = detrended_zeta - np.polyval(z_trend, range(len(detrended_zeta)))
    prime_detrended = detrended_prime - np.polyval(p_trend, range(len(detrended_prime)))
    
    partial_r, partial_p = stats.pearsonr(zeta_detrended, prime_detrended)
    
    # Cross-correlation analysis
    cross_corr = np.correlate(zeta_clean - np.mean(zeta_clean), 
                             prime_clean - np.mean(prime_clean), mode='full')
    lags = np.arange(-len(prime_clean) + 1, len(zeta_clean))
    
    # Find maximum cross-correlation and corresponding lag
    max_corr_idx = np.argmax(np.abs(cross_corr))
    max_correlation = cross_corr[max_corr_idx]
    optimal_lag = lags[max_corr_idx]
    
    # Normalize cross-correlation
    norm_factor = np.sqrt(np.sum((zeta_clean - np.mean(zeta_clean))**2) * 
                         np.sum((prime_clean - np.mean(prime_clean))**2))
    normalized_max_corr = max_correlation / norm_factor if norm_factor > 0 else 0
    
    return {
        'data_summary': {
            'original_lengths': (len(zeta_zeros), len(prime_data)),
            'valid_points': len(zeta_clean),
            'data_quality': len(zeta_clean) / min_length if min_length > 0 else 0
        },
        'correlation_analysis': correlation_results,
        'documentation_validation': correlation_validation,
        'bootstrap_analysis': {
            'bootstrap_correlations': bootstrap_correlations.tolist(),
            'mean_correlation': np.mean(bootstrap_correlations),
            'std_correlation': np.std(bootstrap_correlations),
            'confidence_interval': correlation_validation['confidence_interval']
        },
        'advanced_analysis': {
            'partial_correlation': {
                'correlation': partial_r,
                'p_value': partial_p,
                'significant': partial_p < 0.05
            },
            'cross_correlation': {
                'max_correlation': normalized_max_corr,
                'optimal_lag': optimal_lag,
                'all_correlations': cross_corr.tolist(),
                'lags': lags.tolist()
            }
        },
        'interpretation': {
            'primary_correlation': pearson_r,
            'correlation_strength': correlation_results.get('pearson', {}).get('strength', 'Unknown'),
            'statistical_significance': correlation_results.get('pearson', {}).get('significant', False),
            'documented_claim_validation': correlation_validation['claim_supported'],
            'robust_correlation': correlation_results.get('spearman', {}).get('correlation', 0)
        },
        'recommendations': [
            f"Observed Pearson r = {pearson_r:.3f}",
            f"Documented claim r = 0.93: {'Supported' if correlation_validation['claim_supported'] else 'Not supported'}",
            f"Correlation strength: {correlation_results.get('pearson', {}).get('strength', 'Unknown')}",
            f"Statistical significance: {'Yes' if correlation_results.get('pearson', {}).get('significant', False) else 'No'}",
            f"Bootstrap 95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]"
        ]
    }

def regression_analysis_enhancement(k_values, enhancement_values, model_types=None):
    """
    Perform regression analysis to model the relationship between curvature 
    parameter k and prime enhancement values.
    
    Args:
        k_values: Array of curvature parameter values
        enhancement_values: Corresponding enhancement percentages
        model_types: List of regression models to fit
        
    Returns:
        dict: Comprehensive regression analysis results
    """
    if model_types is None:
        model_types = ['linear', 'quadratic', 'cubic', 'ridge', 'lasso']
    
    k_values = np.array(k_values).reshape(-1, 1)
    enhancement_values = np.array(enhancement_values)
    
    # Remove invalid values
    valid_mask = np.isfinite(k_values.flatten()) & np.isfinite(enhancement_values)
    k_clean = k_values[valid_mask]
    enhancement_clean = enhancement_values[valid_mask]
    
    if len(k_clean) < 3:
        return {
            'error': 'Insufficient valid data points for regression analysis',
            'valid_points': len(k_clean)
        }
    
    regression_results = {}
    
    # Linear regression
    if 'linear' in model_types:
        linear_model = LinearRegression()
        linear_model.fit(k_clean, enhancement_clean)
        
        enhancement_pred = linear_model.predict(k_clean)
        r2_linear = r2_score(enhancement_clean, enhancement_pred)
        mse_linear = mean_squared_error(enhancement_clean, enhancement_pred)
        
        regression_results['linear'] = {
            'model': linear_model,
            'coefficients': {
                'intercept': linear_model.intercept_,
                'slope': linear_model.coef_[0]
            },
            'r_squared': r2_linear,
            'mse': mse_linear,
            'predictions': enhancement_pred,
            'equation': f"enhancement = {linear_model.intercept_:.3f} + {linear_model.coef_[0]:.3f} * k"
        }
    
    # Polynomial regression (quadratic and cubic)
    for degree in [2, 3]:
        if (degree == 2 and 'quadratic' in model_types) or (degree == 3 and 'cubic' in model_types):
            poly_features = PolynomialFeatures(degree=degree)
            k_poly = poly_features.fit_transform(k_clean)
            
            poly_model = LinearRegression()
            poly_model.fit(k_poly, enhancement_clean)
            
            enhancement_pred_poly = poly_model.predict(k_poly)
            r2_poly = r2_score(enhancement_clean, enhancement_pred_poly)
            mse_poly = mean_squared_error(enhancement_clean, enhancement_pred_poly)
            
            # Extract polynomial coefficients
            coeffs = poly_model.coef_
            intercept = poly_model.intercept_
            
            if degree == 2:
                name = 'quadratic'
                equation = f"enhancement = {intercept:.3f} + {coeffs[1]:.3f} * k + {coeffs[2]:.3f} * k²"
                
                # Find optimal k (maximum of parabola)
                if coeffs[2] < 0:  # Negative coefficient for k² term
                    optimal_k = -coeffs[1] / (2 * coeffs[2])
                    max_enhancement = poly_model.predict(poly_features.transform([[optimal_k]]))[0]
                else:
                    optimal_k = None
                    max_enhancement = None
                
            else:  # degree == 3
                name = 'cubic'
                equation = f"enhancement = {intercept:.3f} + {coeffs[1]:.3f} * k + {coeffs[2]:.3f} * k² + {coeffs[3]:.3f} * k³"
                
                # Find critical points for cubic
                # Derivative: coeffs[1] + 2*coeffs[2]*k + 3*coeffs[3]*k²
                if coeffs[3] != 0:
                    discriminant = (2*coeffs[2])**2 - 4*(3*coeffs[3])*coeffs[1]
                    if discriminant >= 0:
                        k1 = (-2*coeffs[2] + np.sqrt(discriminant)) / (2*3*coeffs[3])
                        k2 = (-2*coeffs[2] - np.sqrt(discriminant)) / (2*3*coeffs[3])
                        
                        # Evaluate at critical points
                        if np.min(k_clean) <= k1 <= np.max(k_clean):
                            enhancement1 = poly_model.predict(poly_features.transform([[k1]]))[0]
                        else:
                            k1, enhancement1 = None, None
                            
                        if np.min(k_clean) <= k2 <= np.max(k_clean):
                            enhancement2 = poly_model.predict(poly_features.transform([[k2]]))[0]
                        else:
                            k2, enhancement2 = None, None
                        
                        # Choose the maximum
                        if enhancement1 is not None and enhancement2 is not None:
                            if enhancement1 > enhancement2:
                                optimal_k, max_enhancement = k1, enhancement1
                            else:
                                optimal_k, max_enhancement = k2, enhancement2
                        elif enhancement1 is not None:
                            optimal_k, max_enhancement = k1, enhancement1
                        elif enhancement2 is not None:
                            optimal_k, max_enhancement = k2, enhancement2
                        else:
                            optimal_k, max_enhancement = None, None
                    else:
                        optimal_k, max_enhancement = None, None
                else:
                    optimal_k, max_enhancement = None, None
            
            regression_results[name] = {
                'model': poly_model,
                'poly_features': poly_features,
                'coefficients': {
                    'intercept': intercept,
                    'polynomial_coeffs': coeffs.tolist()
                },
                'r_squared': r2_poly,
                'mse': mse_poly,
                'predictions': enhancement_pred_poly,
                'equation': equation,
                'optimal_k': optimal_k,
                'max_enhancement': max_enhancement
            }
    
    # Regularized regression
    for reg_type in ['ridge', 'lasso']:
        if reg_type in model_types:
            # Use polynomial features for regularized models
            poly_features = PolynomialFeatures(degree=2)
            k_poly = poly_features.fit_transform(k_clean)
            
            if reg_type == 'ridge':
                reg_model = Ridge(alpha=1.0)
            else:  # lasso
                reg_model = Lasso(alpha=0.1)
            
            reg_model.fit(k_poly, enhancement_clean)
            
            enhancement_pred_reg = reg_model.predict(k_poly)
            r2_reg = r2_score(enhancement_clean, enhancement_pred_reg)
            mse_reg = mean_squared_error(enhancement_clean, enhancement_pred_reg)
            
            # Cross-validation score
            cv_scores = cross_val_score(reg_model, k_poly, enhancement_clean, 
                                       cv=min(5, len(k_clean)//2), scoring='r2')
            
            regression_results[reg_type] = {
                'model': reg_model,
                'poly_features': poly_features,
                'coefficients': {
                    'intercept': reg_model.intercept_,
                    'coeffs': reg_model.coef_.tolist()
                },
                'r_squared': r2_reg,
                'mse': mse_reg,
                'cv_score_mean': np.mean(cv_scores),
                'cv_score_std': np.std(cv_scores),
                'predictions': enhancement_pred_reg
            }
    
    # Model comparison
    model_comparison = {}
    for name, result in regression_results.items():
        if 'r_squared' in result:
            model_comparison[name] = {
                'r_squared': result['r_squared'],
                'mse': result['mse'],
                'complexity': 1 if name == 'linear' else 2 if name == 'quadratic' else 3
            }
    
    # Find best model based on R²
    if model_comparison:
        best_model_name = max(model_comparison.keys(), 
                             key=lambda k: model_comparison[k]['r_squared'])
        best_model = regression_results[best_model_name]
    else:
        best_model_name = None
        best_model = None
    
    # Residual analysis for best model
    if best_model:
        residuals = enhancement_clean - best_model['predictions']
        residual_analysis = {
            'residuals': residuals.tolist(),
            'mean_residual': np.mean(residuals),
            'std_residual': np.std(residuals),
            'residual_normality': stats.jarque_bera(residuals)[1] > 0.05,
            'durbin_watson': None  # Would need additional computation
        }
    else:
        residual_analysis = None
    
    return {
        'data_summary': {
            'sample_size': len(k_clean),
            'k_range': (np.min(k_clean), np.max(k_clean)),
            'enhancement_range': (np.min(enhancement_clean), np.max(enhancement_clean))
        },
        'regression_results': regression_results,
        'model_comparison': model_comparison,
        'best_model': {
            'name': best_model_name,
            'details': best_model
        },
        'residual_analysis': residual_analysis,
        'optimal_parameter_analysis': {
            name: result.get('optimal_k') for name, result in regression_results.items()
            if result.get('optimal_k') is not None
        },
        'interpretation': {
            'best_fit_model': best_model_name,
            'best_r_squared': best_model['r_squared'] if best_model else None,
            'optimal_k_estimates': [
                result.get('optimal_k') for result in regression_results.values()
                if result.get('optimal_k') is not None
            ]
        },
        'recommendations': [
            f"Best fitting model: {best_model_name}" if best_model_name else "No successful model fits",
            f"R² = {best_model['r_squared']:.3f}" if best_model else "R² unavailable",
            f"Optimal k estimates: {[result.get('optimal_k') for result in regression_results.values() if result.get('optimal_k') is not None]}"
        ]
    }

def time_series_correlation(sequence1, sequence2, max_lag=10):
    """
    Analyze time series correlation between two sequences with lag analysis.
    
    Args:
        sequence1, sequence2: Time series data arrays
        max_lag: Maximum lag to test
        
    Returns:
        dict: Time series correlation analysis
    """
    sequence1 = np.array(sequence1)
    sequence2 = np.array(sequence2)
    
    # Ensure equal lengths
    min_length = min(len(sequence1), len(sequence2))
    seq1 = sequence1[:min_length]
    seq2 = sequence2[:min_length]
    
    # Remove trend (optional)
    seq1_detrended = seq1 - np.polyval(np.polyfit(range(len(seq1)), seq1, 1), range(len(seq1)))
    seq2_detrended = seq2 - np.polyval(np.polyfit(range(len(seq2)), seq2, 1), range(len(seq2)))
    
    # Cross-correlation analysis
    lags = np.arange(-max_lag, max_lag + 1)
    correlations = []
    
    for lag in lags:
        if lag > 0:
            # seq2 leads seq1
            corr, _ = stats.pearsonr(seq1[lag:], seq2[:-lag])
        elif lag < 0:
            # seq1 leads seq2
            corr, _ = stats.pearsonr(seq1[:lag], seq2[-lag:])
        else:
            # No lag
            corr, _ = stats.pearsonr(seq1, seq2)
        
        correlations.append(corr)
    
    correlations = np.array(correlations)
    
    # Find maximum correlation and corresponding lag
    max_corr_idx = np.argmax(np.abs(correlations))
    max_correlation = correlations[max_corr_idx]
    optimal_lag = lags[max_corr_idx]
    
    # Auto-correlation analysis
    auto_corr_1 = [stats.pearsonr(seq1[:-i] if i > 0 else seq1, 
                                 seq1[i:] if i > 0 else seq1)[0] 
                   for i in range(max_lag + 1)]
    auto_corr_2 = [stats.pearsonr(seq2[:-i] if i > 0 else seq2, 
                                 seq2[i:] if i > 0 else seq2)[0] 
                   for i in range(max_lag + 1)]
    
    return {
        'cross_correlation': {
            'lags': lags.tolist(),
            'correlations': correlations.tolist(),
            'max_correlation': max_correlation,
            'optimal_lag': optimal_lag,
            'lag_interpretation': (
                f"Sequence 2 leads by {optimal_lag} steps" if optimal_lag > 0 else
                f"Sequence 1 leads by {-optimal_lag} steps" if optimal_lag < 0 else
                "No lag relationship"
            )
        },
        'auto_correlation': {
            'sequence_1': auto_corr_1,
            'sequence_2': auto_corr_2,
            'persistence_1': sum(1 for ac in auto_corr_1 if ac > 0.5),
            'persistence_2': sum(1 for ac in auto_corr_2 if ac > 0.5)
        },
        'synchronization_analysis': {
            'zero_lag_correlation': correlations[max_lag],  # lag = 0
            'max_lagged_correlation': max_correlation,
            'synchronization_strength': abs(correlations[max_lag]),
            'lead_lag_strength': abs(max_correlation) - abs(correlations[max_lag])
        }
    }

def spectral_correlation_analysis(data1, data2, sampling_rate=1.0):
    """
    Analyze correlation in the frequency domain using spectral analysis.
    
    Args:
        data1, data2: Input sequences for spectral correlation
        sampling_rate: Sampling rate for frequency calculation
        
    Returns:
        dict: Spectral correlation analysis results
    """
    from scipy.fft import fft, fftfreq
    from scipy.signal import coherence, csd
    
    data1 = np.array(data1)
    data2 = np.array(data2)
    
    # Ensure equal lengths
    min_length = min(len(data1), len(data2))
    data1 = data1[:min_length]
    data2 = data2[:min_length]
    
    # Remove DC component
    data1 = data1 - np.mean(data1)
    data2 = data2 - np.mean(data2)
    
    # Compute FFTs
    fft1 = fft(data1)
    fft2 = fft(data2)
    
    # Frequency array
    freqs = fftfreq(len(data1), 1.0/sampling_rate)
    
    # Cross-power spectral density
    cross_psd = fft1 * np.conj(fft2)
    
    # Magnitude-squared coherence
    f_coh, coherence_vals = coherence(data1, data2, fs=sampling_rate)
    
    # Cross-spectral density
    f_csd, cross_spectral_density = csd(data1, data2, fs=sampling_rate)
    
    # Phase relationship
    phase_diff = np.angle(cross_psd)
    
    # Find dominant frequencies
    power1 = np.abs(fft1)**2
    power2 = np.abs(fft2)**2
    
    # Get positive frequencies only
    pos_freqs = freqs[:len(freqs)//2]
    coherence_pos = coherence_vals[:len(coherence_vals)//2]
    
    # Find peak coherence
    max_coherence_idx = np.argmax(coherence_pos)
    max_coherence = coherence_pos[max_coherence_idx]
    peak_frequency = f_coh[max_coherence_idx]
    
    return {
        'spectral_analysis': {
            'frequencies': pos_freqs.tolist(),
            'coherence': coherence_pos.tolist(),
            'max_coherence': max_coherence,
            'peak_frequency': peak_frequency,
            'mean_coherence': np.mean(coherence_pos)
        },
        'cross_spectral': {
            'frequencies': f_csd.tolist(),
            'cross_psd_magnitude': np.abs(cross_spectral_density).tolist(),
            'cross_psd_phase': np.angle(cross_spectral_density).tolist()
        },
        'phase_analysis': {
            'phase_differences': phase_diff[:len(phase_diff)//2].tolist(),
            'mean_phase_diff': np.mean(phase_diff[:len(phase_diff)//2]),
            'phase_coherence': np.abs(np.mean(np.exp(1j * phase_diff[:len(phase_diff)//2])))
        },
        'interpretation': {
            'spectral_correlation_strength': max_coherence,
            'dominant_frequency': peak_frequency,
            'overall_coherence': np.mean(coherence_pos),
            'phase_relationship': (
                'In-phase' if abs(np.mean(phase_diff[:len(phase_diff)//2])) < np.pi/4 else
                'Out-of-phase' if abs(np.mean(phase_diff[:len(phase_diff)//2])) > 3*np.pi/4 else
                'Quadrature'
            )
        }
    }