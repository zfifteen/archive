"""
Distribution Testing Module

This module checks what kind of statistical "shape" the log-gaps follow.
We don't assume they're normal (bell-curve); instead, we test against several distributions using the Kolmogorov-Smirnov (KS) test.
KS compares our data to a theoretical distribution and gives a statistic (how different they are) and p-value (chance of difference being random).
Low KS = good fit; high p-value = not significantly different.

Why multiple distributions? Our hypothesis suggests log-gaps might be "log-normal" (products of random factors, like circuit gains).
But we test others (normal, exponential, etc.) to falsify alternatives and confirm superiority.
This is key for deciding if gaps are multiplicative (log-normal) vs. additive (normal).
"""

import numpy as np
from scipy import stats
from scipy.optimize import minimize  # Not used here, but imported
import warnings


def ks_test_normal(data: np.ndarray):
    """
    Test if log-gaps fit a normal (Gaussian) distribution.

    Normal is symmetric, bell-shaped – common for additive processes (like measurement errors).
    If gaps were simple sums of random additions, they'd be normal.
    But our hypothesis predicts they're not, due to multiplicative effects.
    Fit parameters: mu (mean), sigma (spread).
    """
    # Estimate the best normal curve for our data
    mu, sigma = stats.norm.fit(data)
    # KS test: how well does the data match this normal?
    ks_stat, p_value = stats.kstest(data, "norm", args=(mu, sigma))
    return {
        "ks_stat": ks_stat,  # Distance between data and normal (0 = perfect)
        "p_value": p_value,  # Probability the difference is random (high = good fit)
        "params": {"mu": mu, "sigma": sigma},  # Fitted parameters
    }


def ks_test_lognormal(data: np.ndarray):
    """
    Test if log-gaps fit a log-normal distribution.

    Log-normal arises from products of independent random factors (multiplicative processes).
    In circuits, gains multiply; here, prime factors might "multiply" gaps logarithmically.
    This is our favored distribution per the hypothesis – if it fits best, it supports the analogy.
    Parameters: shape (related to spread), loc (shift), scale (size).
    Also compute MLE (maximum likelihood) mu/sigma for logs of data.
    """
    # Fit the log-normal curve to data (fix location at 0 since gaps >0)
    shape, loc, scale = stats.lognorm.fit(data, floc=0)
    # Test how well it matches
    ks_stat, p_value = stats.kstest(data, "lognorm", args=(shape, loc, scale))
    # For comparison, compute log parameters directly (MLE style)
    log_data = np.log(data)
    mu_mle = np.mean(log_data)  # Mean of logs
    sigma_mle = np.std(log_data)  # Std of logs
    return {
        "ks_stat": ks_stat,
        "p_value": p_value,
        "params": {"shape": shape, "loc": loc, "scale": scale},
        "mle_params": {"mu": mu_mle, "sigma": sigma_mle},  # Alternative params
    }


def ks_test_exponential(data: np.ndarray):
    """
    Test against exponential distribution (memoryless decay).

    Exponential is for waiting times or decay processes (like radioactive half-life).
    If gaps decayed exponentially, this might fit, but our hypothesis leans toward log-normal.
    Parameter: scale (rate of decay).
    """
    loc, scale = stats.expon.fit(data, floc=0)
    ks_stat, p_value = stats.kstest(data, "expon", args=(loc, scale))
    return {
        "ks_stat": ks_stat,
        "p_value": p_value,
        "params": {"loc": loc, "scale": scale},
    }


def ks_test_gamma(data: np.ndarray):
    """
    Test against gamma distribution (sums of exponentials).

    Gamma generalizes exponential; it's for positive, skewed data from additive processes.
    Useful to check if log-gaps look like compounded waiting times.
    Parameters: a (shape), scale (spread).
    """
    a, loc, scale = stats.gamma.fit(data, floc=0)
    ks_stat, p_value = stats.kstest(data, "gamma", args=(a, loc, scale))
    return {
        "ks_stat": ks_stat,
        "p_value": p_value,
        "params": {"a": a, "loc": loc, "scale": scale},
    }


def ks_test_weibull(data: np.ndarray):
    """
    Test against Weibull distribution (failure analysis).

    Weibull models time-to-failure or extreme values; it's flexible for skewed data.
    Could fit if gaps relate to "breakdowns" in prime distribution.
    Parameter: c (shape, controls tail).
    """
    c, loc, scale = stats.weibull_min.fit(data, floc=0)
    ks_stat, p_value = stats.kstest(data, "weibull_min", args=(c, loc, scale))
    return {
        "ks_stat": ks_stat,
        "p_value": p_value,
        "params": {"c": c, "loc": loc, "scale": scale},
    }


def ks_test_uniform(data: np.ndarray):
    """
    Test against uniform distribution (for falsification).

    Uniform means all gaps equally likely – random, no pattern.
    This is a strawman: if gaps are truly random, this fits, falsifying our hypothesis.
    Low p-value here means some structure exists.
    """
    loc, scale = stats.uniform.fit(data)
    ks_stat, p_value = stats.kstest(data, "uniform", args=(loc, scale))
    return {
        "ks_stat": ks_stat,
        "p_value": p_value,
        "params": {"loc": loc, "scale": scale},
    }


def run_distribution_tests(data: np.ndarray):
    """
    Run KS tests against all candidate distributions.

    This is the core: we compare log-gaps to normal (additive), log-normal (multiplicative), etc.
    Results help decide if gaps are circuit-like (log-normal wins) or random (uniform wins).
    Returns a dict of test results for each distribution.
    """
    tests = {
        "normal": ks_test_normal(data),
        "lognormal": ks_test_lognormal(data),
        "exponential": ks_test_exponential(data),
        "gamma": ks_test_gamma(data),
        "weibull": ks_test_weibull(data),
        "uniform": ks_test_uniform(data),
    }
    return tests


def find_best_fit(tests: dict):
    """
    Identify the distribution that fits the data best.

    Picks the one with the smallest KS statistic (closest match).
    In our experiment, if log-normal wins, it supports the multiplicative hypothesis.
    Returns the name and its KS score.
    """
    best_dist = min(tests, key=lambda x: tests[x]["ks_stat"])  # Find min KS
    return best_dist, tests[best_dist]["ks_stat"]


if __name__ == "__main__":
    # Demo with fake log-normal data to test the functions
    np.random.seed(42)  # Reproducible randomness
    data = np.random.lognormal(0, 1, 100)  # Generate test data
    tests = run_distribution_tests(data)  # Run all tests
    print("Best fit:", find_best_fit(tests))  # Show winner
    for dist, result in tests.items():  # Print each result
        print(f"{dist}: KS={result['ks_stat']:.4f}, p={result['p_value']:.4f}")


# Compatibility wrappers for run_experiment.py
def fit_distributions(log_gaps: np.ndarray) -> dict:
    """
    Fit multiple distributions to log-gaps data.
    
    Compatibility wrapper that runs all distribution tests.
    """
    return run_distribution_tests(log_gaps)


def compare_distributions(dist_fits: dict) -> dict:
    """
    Compare distribution fits and determine best match.
    
    Args:
        dist_fits: Dictionary of distribution test results
        
    Returns:
        Dictionary with comparison metrics and falsification checks
    """
    best_fit, best_ks = find_best_fit(dist_fits)
    
    normal_ks = dist_fits['normal']['ks_stat']
    lognormal_ks = dist_fits['lognormal']['ks_stat']
    
    # KS ratio: how much better is lognormal than normal?
    ks_ratio_normal_lognormal = normal_ks / lognormal_ks if lognormal_ks > 0 else float('inf')
    
    # F2 falsification: Normal fits better than log-normal
    f2_falsified = normal_ks < lognormal_ks
    
    return {
        'best_fit': best_fit,
        'best_ks': best_ks,
        'normal_ks': normal_ks,
        'lognormal_ks': lognormal_ks,
        'ks_ratio_normal_lognormal': ks_ratio_normal_lognormal,
        'f2_falsified': f2_falsified,
        'all_fits': dist_fits
    }


def compute_skewness_kurtosis_check(log_gaps: np.ndarray) -> dict:
    """
    Check if skewness and kurtosis are normal-like.
    
    Returns falsification check for F5 (normal-like distribution).
    """
    skewness = stats.skew(log_gaps)
    kurtosis = stats.kurtosis(log_gaps)  # Excess kurtosis
    
    # F5: Check if distribution is normal-like
    # Normal has skewness ~ 0 and excess kurtosis ~ 0
    # We use generous thresholds: |skewness| < 1 and |kurtosis| < 3
    is_normal_like_skewness = abs(skewness) < 1.0
    is_normal_like_kurtosis = abs(kurtosis) < 3.0
    is_normal_like = is_normal_like_skewness and is_normal_like_kurtosis
    
    # F5 is falsified if distribution IS normal-like (we expect heavy tails)
    f5_falsified = is_normal_like
    
    return {
        'skewness': skewness,
        'kurtosis': kurtosis,
        'is_normal_like_skewness': is_normal_like_skewness,
        'is_normal_like_kurtosis': is_normal_like_kurtosis,
        'is_normal_like': is_normal_like,
        'f5_falsified': f5_falsified
    }
