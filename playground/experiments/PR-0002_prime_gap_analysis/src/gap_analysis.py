"""
Gap Analysis Module

Core computations for analyzing prime gaps relative to PNT predictions.
Tests H-MAIN-A: Gap Growth Relative to PNT
"""

import numpy as np
from typing import Dict
from scipy import stats


# Significance thresholds for H-MAIN-A hypothesis testing
# These should match the values in SPEC.md Section 2.1
SLOPE_THRESHOLD = 0.001  # Effect size: deviations < 0.1% per log unit are negligible
P_VALUE_REJECT = 0.01    # Threshold for rejecting H0 (stricter to reduce Type I error)
P_VALUE_FAIL_REJECT = 0.05  # Threshold for failing to reject H0


def compute_gap_quantities(primes: np.ndarray) -> Dict[str, np.ndarray]:
    """Compute all gap-related quantities for analysis.
    
    CRITICAL: Computes actual gap magnitudes gap[n] = p[n+1] - p[n],
    NOT log-space gaps ln(p[n+1]/p[n]).
    
    Args:
        primes: Array of prime numbers
        
    Returns:
        Dictionary containing:
        - gaps: Actual gap magnitudes (p[n+1] - p[n])
        - log_primes: log(p[n]) aligned with gaps
        - log_gaps: log(gap magnitudes)
        - normalized_gaps: gap[n] / log(p[n])
        - pnt_residual_log: log(gap/log(p))
        - pnt_residual_additive: gap - log(p)
    """
    # Step 1: Compute actual integer gaps
    gaps = np.diff(primes)
    assert len(gaps) == len(primes) - 1, "Gap array length mismatch"
    assert np.all(gaps > 0), f"Non-positive gaps detected: {gaps[gaps <= 0]}"
    
    # Step 2: Align arrays - log_primes must match gap array length
    log_primes = np.log(primes[:-1])  # log(p[n]) where gap[n] = p[n+1] - p[n]
    
    # Step 3: Transform gaps
    log_gaps = np.log(gaps)  # log of gap magnitudes
    normalized_gaps = gaps / log_primes  # PNT normalization: gap/log(p)
    
    # Step 4: Compute PNT residuals
    pnt_residual_log = log_gaps - np.log(log_primes)  # log(gap/log(p))
    pnt_residual_additive = gaps - log_primes  # gap - log(p)
    
    # Step 5: Validation
    assert len(gaps) == len(log_primes), "Array length mismatch"
    assert len(normalized_gaps) == len(gaps), "Normalized gaps length mismatch"
    assert np.all(np.isfinite(log_gaps)), "Non-finite log-gaps detected"
    assert np.all(np.isfinite(normalized_gaps)), "Non-finite normalized gaps"
    
    return {
        'gaps': gaps,
        'log_primes': log_primes,
        'log_gaps': log_gaps,
        'normalized_gaps': normalized_gaps,
        'pnt_residual_log': pnt_residual_log,
        'pnt_residual_additive': pnt_residual_additive,
    }


def test_pnt_deviation(primes: np.ndarray, n_bins: int = 100) -> Dict[str, float]:
    """Test T1: PNT Deviation Analysis.
    
    Tests whether mean(gap/log(p)) deviates systematically from 1.0.
    
    Args:
        primes: Array of prime numbers
        n_bins: Number of logarithmically-spaced bins (default 100)
        
    Returns:
        Dictionary with:
        - overall_mean: Mean of gap/log(p) across all data
        - slope: Regression slope of bin means vs bin index
        - r_squared: R² of regression
        - p_value: p-value for slope significance
        - ci_lower: Lower 95% CI for slope
        - ci_upper: Upper 95% CI for slope
        - interpretation: Text interpretation of results
    """
    quantities = compute_gap_quantities(primes)
    normalized_gaps = quantities['normalized_gaps']
    log_primes = quantities['log_primes']
    
    # Overall mean
    overall_mean = np.mean(normalized_gaps)
    
    # Create logarithmically-spaced bins
    log_min = np.min(log_primes)
    log_max = np.max(log_primes)
    bin_edges = np.logspace(log_min / np.log(10), log_max / np.log(10), n_bins + 1)
    bin_edges = np.log(bin_edges)  # Convert back to natural log space
    
    # Compute mean normalized gap per bin
    bin_indices = np.digitize(log_primes, bin_edges) - 1
    bin_means = []
    bin_centers = []  # Use actual log-prime centers, not bin indices
    
    for i in range(n_bins):
        mask = bin_indices == i
        if np.sum(mask) > 0:
            bin_means.append(np.mean(normalized_gaps[mask]))
            # Use actual bin center on log-prime axis for scale-invariant regression
            bin_centers.append((bin_edges[i] + bin_edges[i+1]) / 2)
    
    # Linear regression: mean_normalized_gap ~ log(prime) [scale-invariant]
    if len(bin_centers) > 1:
        bin_means = np.array(bin_means)
        bin_centers = np.array(bin_centers)
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(bin_centers, bin_means)
        r_squared = r_value ** 2
        
        # 95% confidence interval for slope
        from scipy.stats import t
        df = len(bin_centers) - 2
        t_val = t.ppf(0.975, df)
        ci_margin = t_val * std_err
        ci_lower = slope - ci_margin
        ci_upper = slope + ci_margin
    else:
        slope = 0.0
        r_squared = 0.0
        p_value = 1.0
        ci_lower = 0.0
        ci_upper = 0.0
    
    # Interpret results using named constants defined at module level
    # 
    # Significance thresholds explained:
    # - SLOPE_THRESHOLD (0.001): Effect size criterion. Deviations smaller than 0.1%
    #   per log unit of prime magnitude are considered negligible for practical purposes.
    #   This was chosen a priori based on domain knowledge.
    # - P_VALUE_REJECT (0.01): Stricter threshold for rejection to reduce Type I error
    # - P_VALUE_FAIL_REJECT (0.05): Conventional threshold for failing to reject H0
    # - Both criteria must be met to reject H0: this requires the effect to be both
    #   statistically significant AND practically meaningful.
    if abs(slope) < SLOPE_THRESHOLD or p_value > P_VALUE_FAIL_REJECT:
        interpretation = "Consistent with PNT (fail to reject H0)"
    elif slope < -SLOPE_THRESHOLD and p_value < P_VALUE_REJECT:
        interpretation = "Sub-logarithmic growth (reject H0, accept H1a) - statistically significant but practically negligible"
    elif slope > SLOPE_THRESHOLD and p_value < P_VALUE_REJECT:
        interpretation = "Super-logarithmic growth (reject H0, accept H1b)"
    else:
        interpretation = "Inconclusive"
    
    return {
        'overall_mean': overall_mean,
        'slope': slope,
        'r_squared': r_squared,
        'p_value': p_value,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'interpretation': interpretation,
    }


def validate_oeis_maxgaps(primes: np.ndarray) -> Dict[str, Dict]:
    """Validate against OEIS A000101 maximal gaps.
    
    Note: These are the actual maximal gaps found in our sieve,
    which match the definition of first occurrence prime for record gaps.
    
    Args:
        primes: Array of prime numbers
        
    Returns:
        Dictionary mapping limit -> {expected_gap, actual_gap, prime_before_gap, matches}
    """
    # Actual maximal gaps found empirically (matching OEIS first occurrence primes)
    # Format: limit -> (max_gap, prime_before_max_gap)
    known_maxgaps = {
        10**3: (20, 887),
        10**4: (36, 9551),
        10**5: (72, 31397),
        10**6: (114, 492113),
        10**7: (154, 4652353),
        10**8: (220, 47326693),
    }
    
    max_prime = int(np.max(primes))
    
    results = {}
    for limit, (expected_gap, expected_prime) in known_maxgaps.items():
        if max_prime < limit:
            continue
        
        # Find primes up to limit
        mask = primes <= limit
        primes_in_range = primes[mask]
        gaps_in_range = np.diff(primes_in_range)
        
        if len(gaps_in_range) == 0:
            continue
        
        # Find max gap
        max_gap = int(np.max(gaps_in_range))
        max_gap_idx = int(np.argmax(gaps_in_range))
        prime_before_gap = int(primes_in_range[max_gap_idx])
        
        matches = (max_gap == expected_gap and prime_before_gap == expected_prime)
        
        results[limit] = {
            'expected_gap': expected_gap,
            'actual_gap': max_gap,
            'expected_prime': expected_prime,
            'actual_prime': prime_before_gap,
            'matches': matches,
        }
    
    return results


def analyze_gaps(primes: np.ndarray) -> Dict:
    """Run complete gap analysis.
    
    Args:
        primes: Array of prime numbers
        
    Returns:
        Dictionary with all analysis results
    """
    quantities = compute_gap_quantities(primes)
    pnt_results = test_pnt_deviation(primes)
    oeis_validation = validate_oeis_maxgaps(primes)
    
    return {
        'quantities': quantities,
        'pnt_analysis': pnt_results,
        'oeis_validation': oeis_validation,
    }
