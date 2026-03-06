"""
Statistical Tests Module

Implements statistical tests from PR-0002 preserved:
- Linear regression (slope, CI, R², p-value)
- Kolmogorov-Smirnov tests (normal, log-normal, exponential, etc.)
- Ljung-Box autocorrelation test
- Decay-check logic
"""

import numpy as np
from scipy import stats
from typing import Dict, Tuple, Optional

try:
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.stattools import acf, pacf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


def linear_regression(bin_means: np.ndarray) -> Dict:
    """
    Perform linear regression on bin means vs bin index.

    Args:
        bin_means: Array of mean log-gap per bin

    Returns:
        Dict with slope, intercept, r_squared, p_value, confidence_interval, is_decaying
    """
    # Create bin indices
    x = np.arange(1, len(bin_means) + 1)

    # Filter out NaN values
    mask = ~np.isnan(bin_means)
    x_filtered = x[mask]
    y_filtered = bin_means[mask]

    if len(x_filtered) < 2:
        return {
            "slope": np.nan,
            "intercept": np.nan,
            "r_squared": np.nan,
            "p_value": np.nan,
            "std_err": np.nan,
            "confidence_interval": (np.nan, np.nan),
            "is_decaying": False,
        }

    # Perform regression
    result = stats.linregress(x_filtered, y_filtered)

    # Compute 95% confidence interval for slope
    ci_margin = 1.96 * result.stderr
    ci = (result.slope - ci_margin, result.slope + ci_margin)

    # Check for significant decay
    is_decaying = (result.slope < 0) and (result.pvalue < 0.001)

    return {
        "slope": result.slope,
        "intercept": result.intercept,
        "r_squared": result.rvalue**2,
        "p_value": result.pvalue,
        "std_err": result.stderr,
        "confidence_interval": ci,
        "is_decaying": is_decaying,
    }


def kolmogorov_smirnov_tests(log_gaps: np.ndarray) -> Dict:
    """
    Test log-gaps against multiple theoretical distributions.

    Args:
        log_gaps: Array of log-gap values

    Returns:
        Dict with fit results for each distribution and comparison
    """
    results = {}

    # Fit normal distribution
    norm_params = stats.norm.fit(log_gaps)
    norm_ks = stats.kstest(log_gaps, "norm", args=norm_params)
    results["normal"] = {
        "params": {"mean": norm_params[0], "std": norm_params[1]},
        "ks_statistic": norm_ks.statistic,
        "p_value": norm_ks.pvalue,
    }

    # Fit log-normal distribution
    lognorm_params = stats.lognorm.fit(log_gaps, floc=0)
    lognorm_ks = stats.kstest(log_gaps, "lognorm", args=lognorm_params)
    results["lognormal"] = {
        "params": {
            "shape": lognorm_params[0],
            "loc": lognorm_params[1],
            "scale": lognorm_params[2],
        },
        "ks_statistic": lognorm_ks.statistic,
        "p_value": lognorm_ks.pvalue,
    }

    # Fit exponential distribution
    expon_params = stats.expon.fit(log_gaps)
    expon_ks = stats.kstest(log_gaps, "expon", args=expon_params)
    results["exponential"] = {
        "params": {"loc": expon_params[0], "scale": expon_params[1]},
        "ks_statistic": expon_ks.statistic,
        "p_value": expon_ks.pvalue,
    }

    # Fit gamma distribution
    gamma_params = stats.gamma.fit(log_gaps)
    gamma_ks = stats.kstest(log_gaps, "gamma", args=gamma_params)
    results["gamma"] = {
        "params": {
            "alpha": gamma_params[0],
            "loc": gamma_params[1],
            "scale": gamma_params[2],
        },
        "ks_statistic": gamma_ks.statistic,
        "p_value": gamma_ks.pvalue,
    }

    # Fit Weibull distribution
    weibull_params = stats.weibull_min.fit(log_gaps)
    weibull_ks = stats.kstest(log_gaps, "weibull_min", args=weibull_params)
    results["weibull"] = {
        "params": {
            "shape": weibull_params[0],
            "loc": weibull_params[1],
            "scale": weibull_params[2],
        },
        "ks_statistic": weibull_ks.statistic,
        "p_value": weibull_ks.pvalue,
    }

    # Find best fit
    ks_values = {name: data["ks_statistic"] for name, data in results.items()}
    best_fit = min(ks_values, key=ks_values.get)

    # Check F2 falsification (normal fits better than lognormal)
    f2_falsified = (
        results["normal"]["ks_statistic"] < results["lognormal"]["ks_statistic"]
    )

    return {
        "distributions": results,
        "best_fit": best_fit,
        "best_ks": ks_values[best_fit],
        "f2_falsified": f2_falsified,
    }


def ljung_box_test(
    log_gaps: np.ndarray, max_lag: int = 50, subsample_size: Optional[int] = None
) -> Dict:
    """
    Test autocorrelation significance using Ljung-Box test.

    Args:
        log_gaps: Array of log-gap values
        max_lag: Maximum lag to test
        subsample_size: If not None, subsample to this size for approximate test

    Returns:
        Dict with ljungbox results and falsification check
    """
    if not STATSMODELS_AVAILABLE:
        return {
            "error": "statsmodels not available",
            "lb_stats": None,
            "p_values": None,
            "significant_lags": [],
            "f4_falsified": False,
            "status": "error",
            "mode": "unavailable",
            "subsample_size": None,
        }

    # Handle subsampling
    if subsample_size is not None and subsample_size < len(log_gaps):
        np.random.seed(42)  # For reproducibility
        indices = np.random.choice(len(log_gaps), size=subsample_size, replace=False)
        test_data = log_gaps[indices]
        method = "subsampled"
    else:
        test_data = log_gaps
        method = "full"

    # Compute Ljung-Box test
    lb_result = acorr_ljungbox(test_data, lags=max_lag, return_df=False)

    # Handle different return formats
    if isinstance(lb_result, tuple):
        lb_stats, p_values = lb_result
    else:
        # Assume DataFrame
        lb_stats = (
            lb_result["lb_stat"].values
            if hasattr(lb_result, "lb_stat")
            else lb_result.iloc[:, 0].values
        )
        p_values = (
            lb_result["lb_pvalue"].values
            if hasattr(lb_result, "lb_pvalue")
            else lb_result.iloc[:, 1].values
        )

    # Ensure arrays
    if hasattr(lb_stats, "values"):
        lb_stats = lb_stats.values
    if hasattr(p_values, "values"):
        p_values = p_values.values

    # Find significant lags
    significant_lags = np.where(p_values < 0.05)[0] + 1  # +1 because lags start at 1

    # F4: All p-values > 0.05 means white noise (falsified)
    f4_falsified = np.all(p_values > 0.05)

    return {
        "lb_stats": lb_stats.tolist()
        if hasattr(lb_stats, "tolist")
        else list(lb_stats),
        "p_values": p_values.tolist()
        if hasattr(p_values, "tolist")
        else list(p_values),
        "significant_lags": significant_lags.tolist(),
        "f4_falsified": f4_falsified,
        "has_autocorrelation": len(significant_lags) > 0,
        "status": "evaluated",
        "mode": method,
        "subsample_size": len(test_data) if subsample_size else None,
    }


def compute_acf_pacf(log_gaps: np.ndarray, nlags: int = 50) -> Dict:
    """
    Compute autocorrelation (ACF) and partial autocorrelation (PACF).

    Args:
        log_gaps: Array of log-gap values
        nlags: Number of lags to compute

    Returns:
        Dict with acf, pacf, confidence_bound, significant_lags
    """
    if not STATSMODELS_AVAILABLE:
        return {
            "error": "statsmodels not available",
            "acf": None,
            "pacf": None,
            "confidence_bound": None,
            "significant_lags": [],
        }

    # Compute ACF and PACF
    acf_values = acf(log_gaps, nlags=nlags)
    pacf_values = pacf(log_gaps, nlags=nlags)

    # Compute confidence bound
    n = len(log_gaps)
    confidence_bound = 1.96 / np.sqrt(n)

    # Find significant lags (excluding lag 0 which is always 1)
    significant_lags = np.where(np.abs(acf_values[1:]) > confidence_bound)[0] + 1

    return {
        "acf": acf_values,
        "pacf": pacf_values,
        "confidence_bound": confidence_bound,
        "significant_lags": significant_lags.tolist(),
        "nlags": nlags,
    }


def check_decay_monotonic(bin_means: np.ndarray) -> bool:
    """
    Check if bin means decrease monotonically.

    Args:
        bin_means: Array of mean log-gap per bin

    Returns:
        True if monotonically decreasing, False otherwise
    """
    # Filter out NaN values
    filtered_means = bin_means[~np.isnan(bin_means)]

    if len(filtered_means) < 2:
        return False

    # Check if all differences are negative
    return np.all(np.diff(filtered_means) < 0)


def compute_skewness_kurtosis(log_gaps: np.ndarray) -> Dict:
    """
    Compute skewness and kurtosis with normality check.

    Args:
        log_gaps: Array of log-gap values

    Returns:
        Dict with skewness, kurtosis, f5_falsified
    """
    skewness = stats.skew(log_gaps)
    kurtosis = stats.kurtosis(log_gaps)  # Excess kurtosis

    # F5: Normal-like skewness and kurtosis (falsified if true)
    f5_falsified = (np.abs(skewness) < 0.5) and (np.abs(kurtosis) < 1)

    return {"skewness": skewness, "kurtosis": kurtosis, "f5_falsified": f5_falsified}
