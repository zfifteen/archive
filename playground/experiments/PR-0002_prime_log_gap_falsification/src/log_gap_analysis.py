"""
Log Gap Analysis Module

This module transforms prime numbers into "log-gaps," which are the logarithmic differences between consecutive primes.
Why logs? Prime gaps (differences like 3-2=1, 5-3=2) grow larger on average as numbers get bigger.
But logarithms (natural log, ln) compress this growth, making gaps relative rather than absolute.
This is key to our hypothesis: in electrical circuits, we often deal with ratios (like voltage logs), not absolute values.
Log-gaps reveal patterns like decay (gaps shrinking relatively) that might mimic a "damped" system.

We also compute regular gaps for comparison and analyze trends across bins (default: 50 bins for robust statistical proof).
Note: Previous versions used quintiles (5 bins), but 50 bins provides greater statistical robustness.
"""

import numpy as np
from scipy import stats


def compute_log_gaps(primes: np.ndarray) -> np.ndarray:
    """
    Calculate logarithmic prime gaps.

    For each pair of consecutive primes (p_n, p_{n+1}), compute ln(p_{n+1}) - ln(p_n).
    This is the same as ln(p_{n+1} / p_n), the natural log of their ratio.
    Why? Ratios capture multiplicative relationships, like how circuit voltages relate logarithmically.
    Without logs, gaps are additive and dominated by large numbers; logs make them comparable.
    """
    log_primes = np.log(
        primes.astype(np.float64)
    )  # Convert primes to logs (float for precision)
    log_gaps = np.diff(log_primes)  # Difference between consecutive logs
    return log_gaps  # Array of log-gaps


def compute_regular_gaps(primes: np.ndarray) -> np.ndarray:
    """
    Calculate regular (arithmetic) prime gaps for comparison.

    Just p_{n+1} - p_n, the straight difference.
    These show the raw "distances" between primes, which increase over time (Prime Number Theorem).
    We compute them alongside log-gaps to contrast additive vs. multiplicative views.
    In the experiment, log-gaps are the focus, but regular gaps help validate data.
    """
    return np.diff(primes)  # Simple differences


def get_quintile_means(log_gaps: np.ndarray) -> np.ndarray:
    """
    Split log-gaps into 5 equal groups (quintiles) and find the average gap in each.

    Quintiles divide data into fifths: first 20%, second 20%, etc.
    Here, we group the log-gaps by their position (earlier vs. later in the prime list).
    Computing means per group lets us check if gaps change systematically.
    In the hypothesis, we expect averages to decrease (decay) as primes get larger.
    
    Note: For more robust statistical analysis, use get_bin_means() with n_bins=50.
    """
    return get_bin_means(log_gaps, n_bins=5)


def get_decile_means(log_gaps: np.ndarray) -> np.ndarray:
    """
    Split log-gaps into 10 equal groups (deciles) and find the average gap in each.

    Deciles are like quintiles but finer: tenths of the data.
    This gives more detail on trends, useful for checking if decay is consistent.
    Similar to quintiles, we look for decreasing means as a sign of "damping."
    
    Note: For more robust statistical analysis, use get_bin_means() with n_bins=50.
    """
    return get_bin_means(log_gaps, n_bins=10)


def get_bin_means(log_gaps: np.ndarray, n_bins: int = 50) -> np.ndarray:
    """
    Split log-gaps into n_bins equal groups and find the average gap in each.

    This is a generalized version that supports any number of bins.
    Default is 50 bins for robust statistical proof (increased from 5 quintiles).
    More bins provide finer granularity for detecting trends and decay patterns.
    
    Args:
        log_gaps: Array of log-gaps to analyze
        n_bins: Number of bins to divide the data into (default: 50)
        
    Returns:
        Array of mean log-gap values for each bin
    """
    n = len(log_gaps)
    bin_size = n // n_bins
    means = []
    for i in range(n_bins):
        start = i * bin_size
        end = (i + 1) * bin_size if i < n_bins - 1 else n  # Last group takes remainder
        mean = np.mean(log_gaps[start:end])
        means.append(mean)
    return np.array(means)


def regression_analysis(means: np.ndarray):
    """
    Fit a straight line to the means (quintile or decile averages) to check for trends.

    Linear regression finds the best-fit line: y = slope * x + intercept.
    Here, x is the group index (0 for first quintile, 1 for second, etc.), y is the mean gap.
    We want to know if gaps are decreasing (negative slope, like damping).
    Outputs: slope (trend strength), intercept (starting point), r_squared (how well the line fits, 0-1), p_value (probability the trend is random, low means significant).
    """
    x = np.arange(len(means))  # x-values: 0, 1, 2, ... for each group
    result = stats.linregress(x, means)  # SciPy's regression function
    slope = result[0]  # How much y changes per x
    intercept = result[1]  # y when x=0
    r_value = result[2]  # Correlation coefficient
    p_value = result[3]  # Significance
    r_squared = r_value * r_value  # Fraction of variance explained
    return slope, intercept, r_squared, p_value


def analyze_log_gaps(primes: np.ndarray) -> dict:
    """
    Run the complete log-gap analysis pipeline.

    This is the heart of the module: takes a list of primes and outputs everything needed to test the hypothesis.
    It computes gaps, stats, trends, and regressions to see if log-gaps behave like a damped circuit.
    The result dict is used by other modules for plotting and falsification checks.
    
    Primary analysis uses 50 bins for robust statistical proof.
    Quintiles (5 bins) and deciles (10 bins) are retained for backward compatibility.
    """
    log_gaps = compute_log_gaps(primes)  # Get the log-gaps
    regular_gaps = compute_regular_gaps(primes)  # And regular gaps for context

    # Basic statistics: summarize the distribution
    basic_stats = {
        "count": len(log_gaps),  # Number of gaps
        "mean": np.mean(log_gaps),  # Average gap
        "std": np.std(log_gaps),  # Spread around the mean
        "min": np.min(log_gaps),  # Smallest gap
        "max": np.max(log_gaps),  # Largest gap
        "skewness": stats.skew(log_gaps),  # Asymmetry (positive = right-tail heavy)
        "kurtosis": stats.kurtosis(log_gaps),  # Tail heaviness (excess over normal)
        "regular_gap_mean": np.mean(regular_gaps),  # Regular gap average
        "regular_gap_std": np.std(regular_gaps),  # Regular gap spread
        "regular_gap_max": np.max(regular_gaps),  # Biggest regular gap
    }

    # Primary analysis with 50 bins for robust statistical proof
    bin_means_50 = get_bin_means(log_gaps, n_bins=50)  # Averages per bin
    bin_slope_50, bin_intercept_50, bin_r2_50, bin_p_50 = regression_analysis(
        bin_means_50  # Fit line to check decay
    )

    # Backward compatibility: Analyze trends in quintiles (5 groups)
    quintile_means = get_quintile_means(log_gaps)  # Averages per group
    quintile_slope, quintile_intercept, quintile_r2, quintile_p = regression_analysis(
        quintile_means  # Fit line to check decay
    )

    # Backward compatibility: Finer analysis with deciles (10 groups)
    decile_means = get_decile_means(log_gaps)
    decile_slope, decile_intercept, decile_r2, decile_p = regression_analysis(
        decile_means
    )

    # Package everything into a results dictionary
    analysis = {
        "basic_stats": basic_stats,  # Summary numbers
        # Primary 50-bin analysis (most robust)
        "bin_means": bin_means_50,  # 50-bin averages (primary)
        "bin_regression": {  # Trend line for 50 bins
            "slope": bin_slope_50,
            "intercept": bin_intercept_50,
            "r_squared": bin_r2_50,
            "p_value": bin_p_50,
        },
        # Backward compatibility fields
        "quintile_means": quintile_means,  # 5-bin averages (legacy)
        "quintile_regression": {  # Trend line for quintiles
            "slope": quintile_slope,
            "intercept": quintile_intercept,
            "r_squared": quintile_r2,
            "p_value": quintile_p,
        },
        "decile_means": decile_means,  # 10-bin averages (legacy)
        "decile_regression": {  # Trend line for deciles
            "slope": decile_slope,
            "intercept": decile_intercept,
            "r_squared": decile_r2,
            "p_value": decile_p,
        },
        "log_gaps": log_gaps,  # Full array for further use
        "regular_gaps": regular_gaps,
    }

    return analysis


if __name__ == "__main__":
    # Quick test to see the analysis in action
    from prime_generator import generate_primes_up_to

    primes = generate_primes_up_to(100)  # Small set for testing
    analysis = analyze_log_gaps(primes)  # Run full analysis
    print("Basic stats:", analysis["basic_stats"])  # Show summary
    print("50-bin means:", analysis["bin_means"])  # Primary 50-bin averages
    print("50-bin regression:", analysis["bin_regression"])  # Primary trend check
    print("Quintile means (legacy):", analysis["quintile_means"])  # Legacy 5-bin averages
    print("Quintile regression (legacy):", analysis["quintile_regression"])  # Legacy trend


# Compatibility wrappers for run_experiment.py
def compute_descriptive_stats(log_gaps: np.ndarray) -> dict:
    """
    Compute descriptive statistics for log-gaps.
    
    Compatibility wrapper for run_experiment.py.
    """
    return {
        "count": len(log_gaps),
        "mean": np.mean(log_gaps),
        "std": np.std(log_gaps),
        "min": np.min(log_gaps),
        "max": np.max(log_gaps),
        "skewness": stats.skew(log_gaps),
        "kurtosis": stats.kurtosis(log_gaps),
    }


def compute_quintile_analysis(log_gaps: np.ndarray) -> dict:
    """
    Analyze log-gaps using quintiles (5 bins).
    
    Returns quintile analysis with regression and falsification check.
    """
    quintile_means = get_quintile_means(log_gaps)
    slope, intercept, r_squared, p_value = regression_analysis(quintile_means)
    
    # F1 falsification: Check if trend is monotonically decreasing
    is_monotonic_decreasing = all(
        quintile_means[i] >= quintile_means[i+1] for i in range(len(quintile_means)-1)
    )
    f1_falsified = not is_monotonic_decreasing
    
    decay_ratio = quintile_means[0] / quintile_means[-1] if quintile_means[-1] > 0 else float('inf')
    
    return {
        'bin_means': quintile_means,
        'means': quintile_means,  # Alias for compatibility
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'p_value': p_value,
        'decay_ratio': decay_ratio,
        'f1_falsified': f1_falsified,
        'is_monotonic_decreasing': is_monotonic_decreasing
    }


def compute_decile_analysis(log_gaps: np.ndarray) -> dict:
    """
    Analyze log-gaps using deciles (10 bins).
    
    Returns decile analysis with regression.
    """
    decile_means = get_decile_means(log_gaps)
    slope, intercept, r_squared, p_value = regression_analysis(decile_means)
    
    return {
        'bin_means': decile_means,
        'means': decile_means,
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'p_value': p_value
    }


def compute_scale_comparison(all_results: dict) -> dict:
    """
    Compare results across multiple scales.
    
    Args:
        all_results: Dictionary mapping scale to results
        
    Returns:
        Dictionary with comparison metrics
    """
    scales = sorted(all_results.keys())
    
    # Check if all scales show negative slope (decay)
    slopes = [all_results[s]['quintile']['slope'] for s in scales]
    directional_consistent = all(s < 0 for s in slopes)
    decay_consistent = directional_consistent
    
    # F6: Scale-dependent reversals
    f6_falsified = not directional_consistent
    
    return {
        'scales': scales,
        'slopes': slopes,
        'directional_consistent': directional_consistent,
        'decay_consistent': decay_consistent,
        'f6_falsified': f6_falsified
    }


def generate_summary_dataframe(results: dict):
    """
    Generate a summary DataFrame from results.
    
    Creates a pandas DataFrame with key metrics for easy export.
    """
    import pandas as pd
    
    # Extract key metrics
    summary_data = {
        'Scale': [results['scale']],
        'Prime_Count': [results['prime_generation']['count']],
        'Mean_Log_Gap': [results['descriptive']['mean']],
        'Std_Log_Gap': [results['descriptive']['std']],
        'Skewness': [results['descriptive']['skewness']],
        'Kurtosis': [results['descriptive']['kurtosis']],
        'Quintile_Slope': [results['quintile']['slope']],
        'Quintile_R2': [results['quintile']['r_squared']],
        'Quintile_P_Value': [results['quintile']['p_value']],
        'F1_Falsified': [results['quintile']['f1_falsified']],
        'Best_Distribution': [results['distribution_comparison']['best_fit']],
        'Best_KS': [results['distribution_comparison']['best_ks']],
        'F2_Falsified': [results['distribution_comparison']['f2_falsified']],
        'F5_Falsified': [results['skewness_kurtosis']['f5_falsified']],
    }
    
    # Add autocorrelation if evaluated
    if results['autocorrelation']['f4_falsified'] is not None:
        summary_data['F4_Falsified'] = [results['autocorrelation']['f4_falsified']]
        summary_data['Autocorr_Status'] = ['evaluated']
    else:
        summary_data['F4_Falsified'] = [None]
        summary_data['Autocorr_Status'] = ['not_evaluated']
    
    return pd.DataFrame(summary_data)
