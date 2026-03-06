#!/usr/bin/env python3
"""
Prime Log-Gap Optimized Experiment - Main Entry Point

Runs complete analysis with 100 bins on log-prime axis for primes up to 10^9.
"""

import sys
import os
import json
import math
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np

# Import all modules
from prime_generator import generate_primes_to_limit, compute_gaps
from binning import analyze_bins
from statistics import (
    linear_regression,
    kolmogorov_smirnov_tests,
    ljung_box_test,
    compute_acf_pacf,
    check_decay_monotonic,
    compute_skewness_kurtosis,
)
from visualization_2d import (
    plot_decay_trend,
    plot_log_gap_histogram,
    plot_qq_lognormal,
    plot_acf,
    plot_pacf,
    plot_log_prime_vs_log_gap,
    plot_box_plot_per_bin,
    plot_cdf,
    plot_kde,
    plot_regression_residuals,
    plot_log_gap_vs_regular_gap,
    plot_prime_density,
)
from visualization_3d import (
    plot_scatter_3d,
    plot_surface_3d,
    plot_contour_3d,
    plot_wireframe_3d,
    plot_bar_3d,
)


def run_experiment(
    max_prime: int = 10**9,
    n_bins: int = 100,
    autocorr_mode: str = "none",
    max_lag: int = 40,
    subsample_rate: int = 100000,
    use_cache: bool = True,
    verbose: bool = True,
    backend: str = "auto",
    plots: bool = False,
):
    """Execute complete experiment pipeline."""

    if verbose:
        print("=" * 70)
        print("PR-0003: PRIME LOG-GAP OPTIMIZED ANALYSIS")
        print("=" * 70)
    print(f"Parameters:")
    print(f"  Max prime: {max_prime:,}")
    print(f"  Number of bins: {n_bins}")
    print(f"  Prime backend: {backend}")
    print(f"  Autocorr mode: {autocorr_mode}")
    print(f"  Max lag: {max_lag}")
    print(f"  Subsample rate: {subsample_rate}")
    print(f"  Use cache: {use_cache}")
    print()

    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    results_dir = base_dir / "results" / f"10^{int(math.log10(max_prime))}"

    # Create directories
    data_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)

    start_time = time.time()

    # Step 1: Generate/load primes
    if verbose:
        print("[1/8] Generating/loading primes...")
    cache_dir = str(data_dir) if use_cache else None
    primes = generate_primes_to_limit(
        max_prime, cache_dir=cache_dir, validate=True, backend=backend
    )

    # Step 2: Compute/load gaps
    if verbose:
        print("[2/8] Computing/loading gaps...")
    gaps_data = compute_gaps(primes, cache_dir=cache_dir, limit=max_prime)
    log_gaps = gaps_data["log_gaps"]
    log_primes = gaps_data["log_primes"]
    regular_gaps = gaps_data["regular_gaps"]

    # Step 3: Binning analysis
    if verbose:
        print(f"[3/8] Performing binning analysis ({n_bins} bins)...")
    bin_analysis = analyze_bins(log_primes, log_gaps, n_bins=n_bins)

    # Step 4: Statistical tests
    if verbose:
        print("[4/8] Running statistical tests...")

    # Linear regression
    regression = linear_regression(bin_analysis["mean"])

    # KS tests
    ks_tests = kolmogorov_smirnov_tests(log_gaps)

    # ACF/PACF (always computed for descriptive analysis)
    acf_pacf = compute_acf_pacf(log_gaps, nlags=max_lag)

    # Ljung-Box (optional, based on mode)
    if autocorr_mode == "none":
        ljung_box = None
    elif autocorr_mode == "ljungbox":
        ljung_box = ljung_box_test(log_gaps, max_lag=max_lag)
    elif autocorr_mode == "ljungbox-subsample":
        subsample_size = min(subsample_rate, len(log_gaps))
        ljung_box = ljung_box_test(
            log_gaps, max_lag=max_lag, subsample_size=subsample_size
        )
    else:
        raise ValueError(f"Invalid autocorr_mode: {autocorr_mode}")

    # Skewness/Kurtosis
    skew_kurt = compute_skewness_kurtosis(log_gaps)

    # Monotonic decay check
    is_monotonic = check_decay_monotonic(bin_analysis["mean"])

    # Step 5-6: Generate plots (optional)
    if plots:
        # Step 5: Generate 2D plots
        if verbose:
            print("[5/8] Generating 12 2D plots...")

        suffix = f"(N={max_prime:,})"

        plot_decay_trend(
            bin_analysis, regression, str(results_dir / "decay_trend.png"), suffix
        )
        plot_log_gap_histogram(
            log_gaps,
            str(results_dir / "log_gap_histogram.png"),
            n_bins=100,
            title_suffix=suffix,
        )
        plot_qq_lognormal(log_gaps, str(results_dir / "qq_plot_lognormal.png"), suffix)
        plot_acf(
            acf_pacf,
            str(results_dir / "acf.png"),
            suffix,
            ljung_box.get("status", "not_evaluated") if ljung_box else "not_evaluated",
        )
        plot_pacf(
            acf_pacf,
            str(results_dir / "pacf.png"),
            suffix,
            ljung_box.get("status", "not_evaluated") if ljung_box else "not_evaluated",
        )
        plot_log_prime_vs_log_gap(
            log_primes, log_gaps, str(results_dir / "log_prime_vs_log_gap.png"), suffix
        )
        plot_box_plot_per_bin(
            log_gaps,
            bin_analysis["assignments"][:-1],
            str(results_dir / "box_plot_per_bin.png"),
            n_bins=n_bins,
            title_suffix=suffix,
        )
        plot_cdf(log_gaps, str(results_dir / "cdf.png"), suffix)
        plot_kde(log_gaps, str(results_dir / "kde.png"), suffix)
        plot_regression_residuals(
            bin_analysis,
            regression,
            str(results_dir / "regression_residuals.png"),
            suffix,
        )
        plot_log_gap_vs_regular_gap(
            regular_gaps,
            log_gaps,
            str(results_dir / "log_gap_vs_regular_gap.png"),
            suffix,
        )
        plot_prime_density(log_primes, str(results_dir / "prime_density.png"), suffix)

        # Step 6: Generate 3D plots
        if verbose:
            print("[6/8] Generating 5 3D plots...")

        plot_scatter_3d(
            log_primes,
            log_gaps,
            str(results_dir / "scatter_3d.png"),
            sample_size=10000,
            title_suffix=suffix,
        )
        plot_surface_3d(
            log_primes,
            log_gaps,
            str(results_dir / "surface_3d.png"),
            n_bins_x=50,
            n_bins_y=50,
            title_suffix=suffix,
        )
        plot_contour_3d(
            log_gaps,
            str(results_dir / "contour_3d.png"),
            max_lag=50,
            n_scales=5,
            title_suffix=suffix,
        )
        plot_wireframe_3d(bin_analysis, str(results_dir / "wireframe_3d.png"), suffix)
        plot_bar_3d(
            bin_analysis,
            str(results_dir / "bar_3d.png"),
            n_groups=10,
            title_suffix=suffix,
        )
    else:
        if verbose:
            print("[5-6/8] Skipping plot generation (--plots not enabled)...")

    # Step 7: Compile results
    if verbose:
        print("[7/8] Compiling results...")

    def make_serializable(obj):
        """Convert numpy types to Python types for JSON."""
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.int64, np.int32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [make_serializable(v) for v in obj]
        elif obj is None or obj is True or obj is False:
            return obj
        else:
            return str(obj)  # Fallback to string for unknown types

    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "max_prime": max_prime,
            "n_bins": n_bins,
            "n_primes": len(primes),
            "n_gaps": len(log_gaps),
        },
        "binning": {
            "n_bins": n_bins,
            "bins_used": int(bin_analysis["bins_used"]),
            "bin_means": make_serializable(bin_analysis["mean"]),
            "bin_variances": make_serializable(bin_analysis["variance"]),
            "bin_skewness": make_serializable(bin_analysis["skewness"]),
            "bin_kurtosis": make_serializable(bin_analysis["kurtosis"]),
        },
        "regression": make_serializable(regression),
        "ks_tests": make_serializable(ks_tests),
        "autocorrelation": {
            "ljung_box": (
                make_serializable(ljung_box) if ljung_box is not None else None
            ),
            "acf_pacf_summary": {
                "significant_lags": make_serializable(
                    acf_pacf.get("significant_lags", [])
                ),
                "nlags": acf_pacf.get("nlags", max_lag),
            },
            "autocorr_mode": autocorr_mode,
            "ljungbox_status": (
                ljung_box.get("status", "not_evaluated")
                if ljung_box
                else "not_evaluated"
            ),
        },
        "moments": make_serializable(skew_kurt),
        "checks": {
            "is_decaying": regression["is_decaying"],
            "is_monotonic": is_monotonic,
            "f2_falsified": ks_tests["f2_falsified"],
            "f4_falsified": ljung_box.get("f4_falsified", False) if ljung_box else None,
            "f5_falsified": skew_kurt["f5_falsified"],
        },
    }

    # Step 8: Save results
    if verbose:
        print("[8/8] Saving results...")

    results_file = results_dir / "results.json"

    # Make all results serializable
    serializable_results = make_serializable(results)

    with open(results_file, "w") as f:
        json.dump(serializable_results, f, indent=2)

    elapsed = time.time() - start_time

    if verbose:
        print()
        print("=" * 70)
        print("EXPERIMENT COMPLETE")
        print("=" * 70)
        print(f"Time elapsed: {elapsed:.1f}s ({elapsed / 60:.1f} min)")
        print(f"Primes generated: {len(primes):,}")
        print(f"Bins used: {bin_analysis['bins_used']}/{n_bins}")
        print(
            f"Results saved to: {results_file} (in results/10^{int(math.log10(max_prime))}/)"
        )
        print()
        print("Key Findings:")
        print(
            f"  - Regression slope: {regression['slope']:.4e} (p={regression['p_value']:.2e})"
        )
        print(f"  - R²: {regression['r_squared']:.4f}")
        print(f"  - Is decaying: {regression['is_decaying']}")
        print(f"  - Best distribution fit: {ks_tests['best_fit']}")
        print(f"  - Skewness: {skew_kurt['skewness']:.2f}")
        print(f"  - Excess kurtosis: {skew_kurt['kurtosis']:.2f}")
        print(f"  - Autocorr mode: {autocorr_mode}")
        print("=" * 70)

    return results


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="PR-0003: Optimized Prime Log-Gap Analysis"
    )
    parser.add_argument(
        "--max-prime",
        type=float,
        default=1e9,
        help="Maximum prime to generate (default: 1e9)",
    )
    parser.add_argument(
        "--bins", type=int, default=100, help="Number of bins (default: 100)"
    )
    parser.add_argument(
        "--autocorr",
        choices=["none", "ljungbox", "ljungbox-subsample"],
        default="none",
        help="Autocorrelation test mode (default: none)",
    )
    parser.add_argument(
        "--max-lag",
        type=int,
        default=40,
        help="Maximum lag for Ljung-Box test (default: 40)",
    )
    parser.add_argument(
        "--subsample-rate",
        type=int,
        default=100000,
        help="Subsampling rate for approximate tests (default: 100000)",
    )
    parser.add_argument(
        "--prime-backend",
        type=str,
        choices=["segmented", "z5d", "auto"],
        default="auto",
        help="Prime generation backend: segmented (up to 10^9), z5d (up to 10^1233), or auto (switch at 10^9)",
    )
    parser.add_argument(
        "--plots",
        action="store_true",
        help="Enable plot generation (disabled by default)",
    )
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Verbose output (default: True)",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    try:
        max_prime = int(args.max_prime)
        results = run_experiment(
            max_prime=max_prime,
            n_bins=args.bins,
            autocorr_mode=args.autocorr,
            max_lag=args.max_lag,
            subsample_rate=args.subsample_rate,
            use_cache=not args.no_cache,
            verbose=args.verbose,
            backend=args.prime_backend,
            plots=args.plots,
        )
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
