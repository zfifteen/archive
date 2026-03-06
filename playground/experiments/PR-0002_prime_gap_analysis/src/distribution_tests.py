"""
Distribution Testing Module

Tests H-MAIN-B: Lognormal Gap Distribution
Fits various distributions to log(gap) within magnitude bands.
"""

import numpy as np
from typing import Dict, Tuple
from scipy import stats


# Study-wide constants for Bonferroni correction
# These should match the study design in SPEC.md
N_DISTRIBUTIONS = 4  # normal_on_log, exponential, gamma, weibull
N_BANDS = 3  # [10^5, 10^6), [10^6, 10^7), [10^7, 10^8)
EFFECT_SIZE_THRESHOLD = 1.5  # KS ratio threshold for practical significance (SPEC 2.2)
# NOTE: This threshold is heuristic-based as defined in the technical specification.
# It effectively requires the preferred distribution to have a KS statistic
# at least 1.5x smaller (better) than the alternative. Use with caution as it
# is not calibrated to a specific statistical power level.


def compute_effect_size_ratio(ks_stat1: float, ks_stat2: float) -> float:
    """Compute effect size ratio for comparing two distribution fits.
    
    For goodness-of-fit comparisons, we use the KS statistic ratio rather than
    Cohen's d (which is designed for comparing means). The ratio directly shows
    how much better one distribution fits compared to another.
    
    Args:
        ks_stat1: KS statistic for first distribution (e.g., lognormal)
        ks_stat2: KS statistic for second distribution (e.g., exponential)
        
    Returns:
        Effect size ratio (ks_stat2 / ks_stat1). Interpretation:
        - ratio > 1.5: ks_stat1 distribution fits substantially better
        - ratio < 0.67: ks_stat2 distribution fits substantially better
        - ratio between 0.67 and 1.5: similar fit quality
    """
    if ks_stat1 < 1e-10:
        return float('inf') if ks_stat2 > 1e-10 else 1.0
    return ks_stat2 / ks_stat1


def compute_practical_significance(ratio: float, threshold: float = 1.5) -> dict:
    """Determine if the effect size ratio indicates practical significance.
    
    Args:
        ratio: KS statistic ratio from compute_effect_size_ratio (exp_ks / lognormal_ks)
        threshold: Ratio threshold for practical significance (default 1.5)
        
    Returns:
        Dictionary with:
        - 'significant': True if ratio indicates practically significant difference
        - 'favors_lognormal': True if ratio > threshold (lognormal fits better)
        - 'favors_exponential': True if ratio < 1/threshold (exponential fits better)
    """
    favors_lognormal = ratio > threshold
    favors_exponential = ratio < (1.0 / threshold)
    
    # Sanity check: Flags must be mutually exclusive
    # Mathematically guaranteed if threshold > 1.0, but enforced for safety
    if favors_lognormal and favors_exponential:
        # This implies ratio > threshold AND ratio < 1/threshold
        # Impossible for threshold > 1.0
        raise ValueError(
            f"Contradictory significance detected: ratio={ratio:.4f}, "
            f"threshold={threshold}. Check if threshold <= 1.0."
        )

    return {
        'significant': favors_lognormal or favors_exponential,
        'favors_lognormal': favors_lognormal,
        'favors_exponential': favors_exponential,
    }


def test_distributions_in_band(gaps: np.ndarray, band_name: str, 
                                n_distributions: int = N_DISTRIBUTIONS,
                                n_bands: int = N_BANDS) -> Dict:
    """Test distribution fits for gaps within a magnitude band.
    
    Tests whether log(gap) fits normal distribution (lognormal hypothesis)
    vs exponential, gamma, and Weibull alternatives.
    
    Args:
        gaps: Array of gap values within the band
        band_name: Name of the band for reporting
        n_distributions: Total number of candidate distributions considered
            in the study (default is N_DISTRIBUTIONS). This is used for
            multiple-comparison reasoning such as Bonferroni correction.
        n_bands: Total number of magnitude bands in the study design
            (default is N_BANDS). This is used for multiple-comparison
            reasoning across bands.
        
    Returns:
        Dictionary with fit statistics for each distribution
    """
    if len(gaps) < 10:
        return {'error': 'Insufficient data'}
    
    log_gaps = np.log(gaps)
    
    results = {}
    
    # Test 1: Normal fit to log(gaps) - implies lognormal for gaps
    try:
        # Shapiro-Wilk test for normality
        shapiro_stat, shapiro_p = stats.shapiro(log_gaps)
        
        # KS test against fitted normal
        mu, sigma = np.mean(log_gaps), np.std(log_gaps)
        ks_normal, ks_normal_p = stats.kstest(log_gaps, 
                                               stats.norm(mu, sigma).cdf)
        
        results['normal_on_log'] = {
            'shapiro_stat': shapiro_stat,
            'shapiro_p': shapiro_p,
            'ks_stat': ks_normal,
            'ks_p': ks_normal_p,
            'mu': mu,
            'sigma': sigma,
        }
    except Exception as e:
        results['normal_on_log'] = {'error': str(e)}
    
    # Test 2: Exponential fit to raw gaps
    try:
        # MLE for exponential
        lambda_exp = 1.0 / np.mean(gaps)
        ks_exp, ks_exp_p = stats.kstest(gaps, 
                                        stats.expon(scale=1/lambda_exp).cdf)
        
        results['exponential'] = {
            'ks_stat': ks_exp,
            'ks_p': ks_exp_p,
            'lambda': lambda_exp,
        }
    except Exception as e:
        results['exponential'] = {'error': str(e)}
    
    # Test 3: Gamma fit to raw gaps
    try:
        # MLE for gamma
        shape, loc, scale = stats.gamma.fit(gaps)
        ks_gamma, ks_gamma_p = stats.kstest(gaps, 
                                            stats.gamma(shape, loc, scale).cdf)
        
        results['gamma'] = {
            'ks_stat': ks_gamma,
            'ks_p': ks_gamma_p,
            'shape': shape,
            'scale': scale,
        }
    except Exception as e:
        results['gamma'] = {'error': str(e)}
    
    # Test 4: Weibull fit to raw gaps
    try:
        # MLE for Weibull
        c, loc, scale = stats.weibull_min.fit(gaps)
        ks_weibull, ks_weibull_p = stats.kstest(gaps, 
                                                stats.weibull_min(c, loc, scale).cdf)
        
        results['weibull'] = {
            'ks_stat': ks_weibull,
            'ks_p': ks_weibull_p,
            'shape': c,
            'scale': scale,
        }
    except Exception as e:
        results['weibull'] = {'error': str(e)}
    
    # Determine best fit by lowest KS statistic
    ks_stats = {}
    for dist_name, dist_result in results.items():
        if 'error' not in dist_result and 'ks_stat' in dist_result:
            ks_stats[dist_name] = dist_result['ks_stat']
    
    if ks_stats:
        best_fit = min(ks_stats, key=ks_stats.get)
        results['best_fit'] = best_fit
        
        # Apply Bonferroni correction for multiple testing
        # Use study-wide correction using constants defined at module level
        total_tests = n_distributions * n_bands
        bonferroni_alpha = 0.05 / total_tests
        results['bonferroni_alpha'] = bonferroni_alpha
        results['n_distributions_tested'] = len(ks_stats)
        results['total_study_tests'] = total_tests
        
        # Check if lognormal (normal on log) is best and compute effect size
        if 'normal_on_log' in ks_stats and 'exponential' in ks_stats:
            # Use KS ratio as effect size measure (appropriate for distribution comparisons)
            ks_ratio = compute_effect_size_ratio(
                ks_stats['normal_on_log'], 
                ks_stats['exponential']
            )
            results['ks_ratio_exp_to_lognormal'] = ks_ratio
            
            # Practical significance with directional tracking
            # ratio > EFFECT_SIZE_THRESHOLD means lognormal fits substantially better
            # ratio < 1/EFFECT_SIZE_THRESHOLD means exponential fits substantially better
            practical_sig = compute_practical_significance(
                ks_ratio, EFFECT_SIZE_THRESHOLD
            )
            results['practical_significance'] = practical_sig['significant']
            results['practical_sig_favors_lognormal'] = practical_sig['favors_lognormal']
            results['practical_sig_favors_exponential'] = practical_sig['favors_exponential']
    
    results['band_name'] = band_name
    results['n_samples'] = len(gaps)
    
    return results


def test_distributions(primes: np.ndarray) -> Dict:
    """Test T2: Distribution Fitting Within Magnitude Bands.
    
    Tests distribution of gaps within magnitude bands:
    - [10^5, 10^6)
    - [10^6, 10^7)
    - [10^7, 10^8)
    
    Args:
        primes: Array of prime numbers
        
    Returns:
        Dictionary with results for each band and overall interpretation
    """
    gaps = np.diff(primes)
    
    # Define magnitude bands
    bands = {
        '1e5_1e6': (10**5, 10**6),
        '1e6_1e7': (10**6, 10**7),
        '1e7_1e8': (10**7, 10**8),
    }
    
    band_results = {}
    
    for band_name, (lower, upper) in bands.items():
        # Find gaps in this band
        mask = (primes[:-1] >= lower) & (primes[:-1] < upper)
        band_gaps = gaps[mask]
        
        if len(band_gaps) > 0:
            band_results[band_name] = test_distributions_in_band(band_gaps, band_name)
    
    # Cross-band analysis with family-wise error rate correction
    # Track directional practical significance separately to avoid
    # conflating lognormal-favoring and exponential-favoring effects
    best_fits = []
    distribution_counts = {}
    ks_ratios = []
    practical_sig_lognormal_count = 0
    practical_sig_exponential_count = 0
    
    # Bonferroni-corrected alpha for cross-band decision
    n_bands_tested = len(band_results)
    cross_band_alpha = 0.05 / n_bands_tested if n_bands_tested > 0 else 0.05
    
    for band_name, results in band_results.items():
        if 'best_fit' in results:
            bf = results['best_fit']
            best_fits.append(bf)
            distribution_counts[bf] = distribution_counts.get(bf, 0) + 1
        
        # Collect KS ratio values and directional practical significance
        if 'ks_ratio_exp_to_lognormal' in results:
            ks_ratios.append(results['ks_ratio_exp_to_lognormal'])
            if results.get('practical_sig_favors_lognormal', False):
                practical_sig_lognormal_count += 1
            if results.get('practical_sig_favors_exponential', False):
                practical_sig_exponential_count += 1

    # Primary evidence: Identify majority winner in best-fit (>= 2 bands)
    majority_winner = None
    for dist, count in distribution_counts.items():
        if count >= 2:
            majority_winner = dist
            break

    # Interpretation logic based on majority best-fit and practical significance
    if majority_winner == 'normal_on_log':
        if practical_sig_lognormal_count >= 1:
            interpretation = "Lognormal structure detected (reject H0 for H-MAIN-B)"
        else:
            interpretation = "Lognormal detected but practical significance not established"
    elif majority_winner == 'exponential':
        if practical_sig_exponential_count >= 1:
            interpretation = "Exponential structure detected with practical significance (fail to reject H0)"
        else:
            interpretation = "Exponential structure detected (fail to reject H0)"
    elif majority_winner:
        # Gamma, Weibull, etc. won the majority
        interpretation = f"{majority_winner.replace('_on_log', '').capitalize()} structure detected (contradicts H-MAIN-B)"
    else:
        # No majority in best-fit (e.g., 1 Lognormal, 1 Exponential, 1 Gamma)
        # Fall back to practical significance if it's overwhelming (>= 2 bands)
        if practical_sig_lognormal_count >= 2:
            interpretation = "Lognormal favored over exponential (marginal best-fit evidence)"
        elif practical_sig_exponential_count >= 2:
            interpretation = "Exponential favored over lognormal (marginal best-fit evidence)"
        else:
            interpretation = "Inconsistent across scales"
    
    return {
        'band_results': band_results,
        'best_fits': best_fits,
        'lognormal_count': distribution_counts.get('normal_on_log', 0),
        'exponential_count': distribution_counts.get('exponential', 0),
        'practical_sig_lognormal_count': practical_sig_lognormal_count,
        'practical_sig_exponential_count': practical_sig_exponential_count,
        'ks_ratios': ks_ratios,
        'cross_band_alpha': cross_band_alpha,
        'n_bands_tested': n_bands_tested,
        'interpretation': interpretation,
    }


def compute_qq_data(gaps: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute Q-Q plot data for normal quantiles vs log(gap).
    
    Args:
        gaps: Array of gap values
        
    Returns:
        Tuple of (theoretical_quantiles, sample_quantiles)
    """
    log_gaps = np.log(gaps)
    log_gaps_sorted = np.sort(log_gaps)
    
    # Theoretical normal quantiles
    n = len(log_gaps)
    theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, n))
    
    # Standardize sample quantiles
    mu = np.mean(log_gaps)
    sigma = np.std(log_gaps)
    sample_quantiles = (log_gaps_sorted - mu) / sigma
    
    return theoretical_quantiles, sample_quantiles
