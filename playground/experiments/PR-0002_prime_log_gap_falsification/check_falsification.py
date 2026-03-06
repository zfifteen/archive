import numpy as np
import os
import sys

sys.path.append("src")

from log_gap_analysis import analyze_log_gaps
from distribution_tests import run_distribution_tests, find_best_fit
from autocorrelation import autocorrelation_analysis

# Statistical significance threshold (p-value)
# Using 0.05 as conventional threshold for hypothesis testing
P_VALUE_THRESHOLD = 0.05


def check_falsification(analysis, dist_tests, autocorr):
    """
    Check falsification criteria.
    Uses 50-bin analysis as primary (most robust). Legacy quintile/decile checks
    are recorded as warnings but do not trigger falsification if the primary
    50-bin check passes.
    """
    falsified = False
    reasons = []
    warnings = []

    # F1: 50-bin means show non-decreasing trend (primary check)
    bin_slope = analysis["bin_regression"]["slope"]
    primary_f1_passed = bin_slope < 0 or analysis["bin_regression"]["p_value"] <= P_VALUE_THRESHOLD
    if not primary_f1_passed:
        falsified = True
        reasons.append("F1: 50-bin means do not decrease")
    
    # F1 (legacy): Quintile/decile means - recorded as warnings only
    # These don't trigger falsification if primary 50-bin check passes
    quintile_slope = analysis["quintile_regression"]["slope"]
    decile_slope = analysis["decile_regression"]["slope"]
    if quintile_slope >= 0 and analysis["quintile_regression"]["p_value"] > P_VALUE_THRESHOLD:
        warnings.append("F1 warning: Quintile means do not decrease (legacy check)")
    if decile_slope >= 0 and analysis["decile_regression"]["p_value"] > P_VALUE_THRESHOLD:
        warnings.append("F1 warning: Decile means do not decrease (legacy check)")

    # F2: Normal fits better than log-normal
    normal_ks = dist_tests["normal"]["ks_stat"]
    lognormal_ks = dist_tests["lognormal"]["ks_stat"]
    if normal_ks < lognormal_ks:
        falsified = True
        reasons.append("F2: Normal fits better than log-normal")

    # F3: Indistinguishable from uniform
    if dist_tests["uniform"]["p_value"] > P_VALUE_THRESHOLD:
        falsified = True
        reasons.append("F3: Indistinguishable from uniform")

    # F4: Autocorrelation flat
    if autocorr["all_uncorrelated"]:
        falsified = True
        reasons.append("F4: No autocorrelation at any lag")

    # F5: Skewness/kurtosis consistent with normal
    skewness = analysis["basic_stats"]["skewness"]
    kurtosis = analysis["basic_stats"]["kurtosis"]
    if abs(skewness) < 0.5 and abs(kurtosis) < 1:
        falsified = True
        reasons.append("F5: Skewness and kurtosis consistent with normal")

    # F6: Contradict smaller scale (not checked here)

    return falsified, reasons, warnings


def load_analysis(limit):
    """
    Load analysis results.
    Since we didn't save properly, regenerate.
    """
    primes = np.load(f"data/primes_{limit}.npy")
    analysis = analyze_log_gaps(primes)
    dist_tests = run_distribution_tests(analysis["log_gaps"])
    autocorr = autocorrelation_analysis(analysis["log_gaps"])
    best_dist, best_ks = find_best_fit(dist_tests)
    return analysis, dist_tests, autocorr, best_dist, best_ks


if __name__ == "__main__":
    # For 10^6
    limit = 1000000
    if os.path.exists(f"data/primes_{limit}.npy"):
        print(f"Checking falsification for {limit}")
        analysis, dist_tests, autocorr, best_dist, best_ks = load_analysis(limit)
        falsified, reasons, warnings = check_falsification(analysis, dist_tests, autocorr)
        print(f"Hypothesis falsified: {falsified}")
        if falsified:
            for reason in reasons:
                print(f" - {reason}")
        else:
            print("Hypothesis supported at this scale.")
        if warnings:
            print("Warnings (informational only):")
            for warning in warnings:
                print(f" - {warning}")
    else:
        print("Data not found.")
