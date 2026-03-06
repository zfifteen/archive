import numpy as np
import os
import sys

sys.path.append("src")

from prime_generator import generate_primes_up_to, count_primes_up_to
from log_gap_analysis import analyze_log_gaps
from distribution_tests import run_distribution_tests, find_best_fit
from autocorrelation import autocorrelation_analysis
from visualization import generate_all_plots


def run_full_analysis(limit: int, save_data: bool = True):
    """
    Run full analysis for given limit.
    """
    print(f"Starting analysis for limit {limit}...")

    # Generate primes
    print("Generating primes...")
    primes = generate_primes_up_to(limit)
    count = len(primes)
    print(f"Generated {count} primes up to {limit}")

    # Validate count
    expected_counts = {10**6: 78498, 10**7: 664579, 10**8: 5761455}
    expected = expected_counts.get(limit)
    if expected is None:
        supported_limits = ", ".join(str(k) for k in sorted(expected_counts.keys()))
        raise ValueError(
            f"Unsupported limit {limit}. Expected one of: {supported_limits} "
            "(corresponding to 10**6, 10**7, 10**8)."
        )
    if abs(count - expected) > 1:
        print(f"Warning: Prime count {count} deviates from expected {expected}")
    else:
        print("Prime count validated.")

    # Compute analysis
    print("Computing log-gap analysis...")
    analysis = analyze_log_gaps(primes)

    # Distribution tests
    print("Running distribution tests...")
    dist_tests = run_distribution_tests(analysis["log_gaps"])
    best_dist, best_ks = find_best_fit(dist_tests)

    # Autocorrelation
    print("Running autocorrelation analysis...")
    autocorr = autocorrelation_analysis(analysis["log_gaps"])

    # Generate plots
    print("Generating plots...")
    generate_all_plots(
        analysis["log_gaps"],
        analysis["bin_means"],
        analysis["decile_means"],
        autocorr["acf"],
        autocorr["pacf"],
    )

    # Save data
    if save_data:
        os.makedirs("data", exist_ok=True)
        np.save(f"data/primes_{limit}.npy", primes)
        np.savetxt(f"data/log_gaps_{limit}.csv", analysis["log_gaps"], delimiter=",")

        os.makedirs("results", exist_ok=True)
        # Save summary
        summary = {
            "limit": limit,
            "prime_count": count,
            "basic_stats": analysis["basic_stats"],
            "bin_means": analysis["bin_means"].tolist(),  # Primary 50-bin analysis
            "bin_regression": analysis["bin_regression"],  # Primary regression
            "quintile_means": analysis["quintile_means"].tolist(),  # Legacy 5-bin
            "decile_means": analysis["decile_means"].tolist(),  # Legacy 10-bin
            "quintile_regression": analysis["quintile_regression"],
            "decile_regression": analysis["decile_regression"],
            "best_distribution": best_dist,
            "best_ks_stat": best_ks,
            "all_uncorrelated": autocorr["all_uncorrelated"],
            "significant_acf_lags": autocorr["significant_acf_lags"],
            "significant_pacf_lags": autocorr["significant_pacf_lags"],
        }
        np.save(f"results/analysis_{limit}.npy", summary)

    print(f"Analysis complete for {limit}")

    # Return key results for falsification check
    return {
        "analysis": analysis,
        "dist_tests": dist_tests,
        "autocorr": autocorr,
        "best_dist": best_dist,
        "best_ks": best_ks,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("limit", type=int, help="Upper limit for primes")
    args = parser.parse_args()
    run_full_analysis(args.limit)
