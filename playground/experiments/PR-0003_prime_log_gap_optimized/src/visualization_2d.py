"""
2D Visualization Module - Complete Implementation

Generates 12 required 2D plots for comprehensive analysis.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import gaussian_kde
from typing import Dict, Optional
import os


def plot_decay_trend(
    bin_analysis: Dict,
    regression_results: Dict,
    output_path: str,
    title_suffix: str = "",
) -> None:
    """Plot bin index vs mean log-gap with fitted regression line."""
    bin_means = bin_analysis["mean"]
    n_bins = len(bin_means)
    x = np.arange(1, n_bins + 1)

    # Filter NaN
    mask = ~np.isnan(bin_means)
    x_filtered = x[mask]
    y_filtered = bin_means[mask]

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.scatter(x_filtered, y_filtered, alpha=0.6, s=30, label="Bin means")

    # Plot regression line
    slope = regression_results["slope"]
    intercept = regression_results["intercept"]
    y_fit = slope * x_filtered + intercept
    plt.plot(
        x_filtered,
        y_fit,
        "r--",
        linewidth=2,
        label=f"Fit: y = {slope:.2e}x + {intercept:.2e}",
    )

    plt.xlabel("Bin Index", fontsize=12)
    plt.ylabel("Mean Log-Gap", fontsize=12)
    plt.title(
        f"Decay Trend Analysis {title_suffix}\n"
        + f"R² = {regression_results['r_squared']:.4f}, "
        + f"p = {regression_results['p_value']:.2e}",
        fontsize=14,
    )
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_log_gap_histogram(
    log_gaps: np.ndarray, output_path: str, n_bins: int = 100, title_suffix: str = ""
) -> None:
    """Create histogram of all log-gaps with 100 bins."""
    plt.figure(figsize=(10, 6))

    # Plot histogram
    counts, bins, patches = plt.hist(
        log_gaps, bins=n_bins, density=True, alpha=0.7, edgecolor="black", label="Data"
    )

    # Fit and overlay log-normal
    shape, loc, scale = stats.lognorm.fit(log_gaps, floc=0)
    x = np.linspace(log_gaps.min(), log_gaps.max(), 1000)
    pdf = stats.lognorm.pdf(x, shape, loc, scale)
    plt.plot(x, pdf, "r-", linewidth=2, label="Log-normal fit")

    plt.xlabel("Log-Gap Value", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title(f"Log-Gap Distribution {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_qq_lognormal(
    log_gaps: np.ndarray, output_path: str, title_suffix: str = ""
) -> None:
    """Generate Q-Q plot against log-normal distribution."""
    plt.figure(figsize=(8, 8))

    # Fit log-normal
    shape, loc, scale = stats.lognorm.fit(log_gaps, floc=0)

    # Generate theoretical quantiles
    sorted_data = np.sort(log_gaps)
    n = len(sorted_data)
    theoretical_quantiles = stats.lognorm.ppf(
        np.linspace(0.01, 0.99, n), shape, loc, scale
    )

    # Plot Q-Q
    plt.scatter(theoretical_quantiles, sorted_data, alpha=0.5, s=1)

    # Add diagonal line
    min_val = min(theoretical_quantiles.min(), sorted_data.min())
    max_val = max(theoretical_quantiles.max(), sorted_data.max())
    plt.plot(
        [min_val, max_val], [min_val, max_val], "r--", linewidth=2, label="Perfect fit"
    )

    plt.xlabel("Theoretical Quantiles (Log-normal)", fontsize=12)
    plt.ylabel("Empirical Quantiles", fontsize=12)
    plt.title(f"Q-Q Plot vs Log-Normal {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_acf(
    acf_results: Dict,
    output_path: str,
    title_suffix: str = "",
    ljungbox_status: str = "not_evaluated",
) -> None:
    """Plot autocorrelation function with confidence bounds."""
    if acf_results.get("error"):
        print(f"Cannot plot ACF: {acf_results['error']}")
        return

    acf_values = acf_results["acf"]
    nlags = acf_results["nlags"]
    confidence_bound = acf_results["confidence_bound"]

    plt.figure(figsize=(10, 6))

    # Stem plot
    lags = np.arange(len(acf_values))
    markerline, stemlines, baseline = plt.stem(lags, acf_values, basefmt=" ")
    plt.setp(markerline, "markersize", 4)

    # Confidence bounds
    plt.axhline(
        confidence_bound, color="r", linestyle="--", linewidth=1, label="95% CI"
    )
    plt.axhline(-confidence_bound, color="r", linestyle="--", linewidth=1)
    plt.axhline(0, color="k", linestyle="-", linewidth=0.5)

    plt.xlabel("Lag", fontsize=12)
    plt.ylabel("Autocorrelation", fontsize=12)
    status_note = (
        " (Ljung-Box Not Evaluated)" if ljungbox_status == "not_evaluated" else ""
    )
    plt.title(f"Autocorrelation Function {title_suffix}{status_note}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_pacf(
    acf_results: Dict,
    output_path: str,
    title_suffix: str = "",
    ljungbox_status: str = "not_evaluated",
) -> None:
    """Plot partial autocorrelation function with confidence bounds."""
    if acf_results.get("error"):
        print(f"Cannot plot PACF: {acf_results['error']}")
        return

    pacf_values = acf_results["pacf"]
    confidence_bound = acf_results["confidence_bound"]

    plt.figure(figsize=(10, 6))

    # Stem plot
    lags = np.arange(len(pacf_values))
    markerline, stemlines, baseline = plt.stem(lags, pacf_values, basefmt=" ")
    plt.setp(markerline, "markersize", 4)

    # Confidence bounds
    plt.axhline(
        confidence_bound, color="r", linestyle="--", linewidth=1, label="95% CI"
    )
    plt.axhline(-confidence_bound, color="r", linestyle="--", linewidth=1)
    plt.axhline(0, color="k", linestyle="-", linewidth=0.5)

    plt.xlabel("Lag", fontsize=12)
    plt.ylabel("Partial Autocorrelation", fontsize=12)
    plt.title(f"Partial Autocorrelation Function {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_log_prime_vs_log_gap(
    log_primes: np.ndarray,
    log_gaps: np.ndarray,
    output_path: str,
    title_suffix: str = "",
    sample_size: int = 10000,
) -> None:
    """Scatter plot of log-prime vs log-gap."""
    # Align lengths
    log_primes_aligned = log_primes[:-1]

    # Downsample for large datasets
    if len(log_gaps) > sample_size:
        indices = np.random.choice(len(log_gaps), sample_size, replace=False)
        log_primes_plot = log_primes_aligned[indices]
        log_gaps_plot = log_gaps[indices]
    else:
        log_primes_plot = log_primes_aligned
        log_gaps_plot = log_gaps

    plt.figure(figsize=(10, 6))
    plt.scatter(log_primes_plot, log_gaps_plot, alpha=0.3, s=1)

    plt.xlabel("ln(prime)", fontsize=12)
    plt.ylabel("Log-Gap", fontsize=12)
    plt.title(f"Log-Prime vs Log-Gap {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_box_plot_per_bin(
    log_gaps: np.ndarray,
    bin_assignments: np.ndarray,
    output_path: str,
    n_bins: int = 100,
    title_suffix: str = "",
) -> None:
    """Create box plots of log-gaps for each of 100 bins."""
    # Group by bins
    bin_groups = []
    for bin_idx in range(1, n_bins + 1):
        mask = bin_assignments == bin_idx
        if np.any(mask):
            bin_groups.append(log_gaps[mask])
        else:
            bin_groups.append([])

    # Filter empty bins
    non_empty_groups = [g for g in bin_groups if len(g) > 0]
    non_empty_indices = [i + 1 for i, g in enumerate(bin_groups) if len(g) > 0]

    if len(non_empty_groups) == 0:
        print("No data for box plot")
        return

    plt.figure(figsize=(14, 6))
    plt.boxplot(
        non_empty_groups,
        positions=non_empty_indices,
        widths=0.8,
        patch_artist=True,
        showfliers=False,
    )

    # Sample x-labels every 10th bin
    xticks = range(10, n_bins + 1, 10)
    plt.xticks(xticks, xticks)

    plt.xlabel("Bin Index", fontsize=12)
    plt.ylabel("Log-Gap", fontsize=12)
    plt.title(f"Log-Gap Distribution by Bin {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_cdf(log_gaps: np.ndarray, output_path: str, title_suffix: str = "") -> None:
    """Plot empirical CDF vs theoretical log-normal CDF."""
    # Sort for empirical CDF
    sorted_gaps = np.sort(log_gaps)
    n = len(sorted_gaps)
    y_empirical = np.arange(1, n + 1) / n

    # Fit log-normal
    shape, loc, scale = stats.lognorm.fit(log_gaps, floc=0)
    y_theoretical = stats.lognorm.cdf(sorted_gaps, shape, loc, scale)

    plt.figure(figsize=(10, 6))
    plt.plot(sorted_gaps, y_empirical, label="Empirical CDF", linewidth=2)
    plt.plot(sorted_gaps, y_theoretical, "--", label="Log-normal CDF", linewidth=2)

    plt.xlabel("Log-Gap", fontsize=12)
    plt.ylabel("Cumulative Probability", fontsize=12)
    plt.title(f"CDF Comparison {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_kde(log_gaps: np.ndarray, output_path: str, title_suffix: str = "") -> None:
    """Kernel density estimate with log-normal overlay."""
    # Compute KDE
    kde = gaussian_kde(log_gaps)
    x = np.linspace(log_gaps.min(), log_gaps.max(), 1000)
    kde_values = kde(x)

    # Fit log-normal
    shape, loc, scale = stats.lognorm.fit(log_gaps, floc=0)
    pdf_values = stats.lognorm.pdf(x, shape, loc, scale)

    plt.figure(figsize=(10, 6))
    plt.plot(x, kde_values, label="KDE", linewidth=2)
    plt.plot(x, pdf_values, "--", label="Log-normal PDF", linewidth=2)

    plt.xlabel("Log-Gap", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.title(f"Kernel Density Estimate {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_regression_residuals(
    bin_analysis: Dict,
    regression_results: Dict,
    output_path: str,
    title_suffix: str = "",
) -> None:
    """Plot residuals from regression vs bin index."""
    bin_means = bin_analysis["mean"]
    n_bins = len(bin_means)
    x = np.arange(1, n_bins + 1)

    # Compute fitted values
    slope = regression_results["slope"]
    intercept = regression_results["intercept"]
    y_fit = slope * x + intercept

    # Compute residuals
    residuals = bin_means - y_fit

    plt.figure(figsize=(10, 6))
    plt.scatter(x, residuals, alpha=0.6, s=30)
    plt.axhline(0, color="r", linestyle="--", linewidth=2)

    plt.xlabel("Bin Index", fontsize=12)
    plt.ylabel("Residual", fontsize=12)
    plt.title(f"Regression Residuals {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_log_gap_vs_regular_gap(
    regular_gaps: np.ndarray,
    log_gaps: np.ndarray,
    output_path: str,
    title_suffix: str = "",
    sample_size: int = 10000,
) -> None:
    """Scatter plot comparing regular gaps to log-gaps."""
    # Downsample for large datasets
    if len(log_gaps) > sample_size:
        indices = np.random.choice(len(log_gaps), sample_size, replace=False)
        regular_plot = regular_gaps[indices]
        log_plot = log_gaps[indices]
    else:
        regular_plot = regular_gaps
        log_plot = log_gaps

    plt.figure(figsize=(10, 6))
    plt.scatter(regular_plot, log_plot, alpha=0.3, s=1)

    plt.xlabel("Regular Gap", fontsize=12)
    plt.ylabel("Log-Gap", fontsize=12)
    plt.title(f"Regular Gap vs Log-Gap {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_prime_density(
    log_primes: np.ndarray, output_path: str, title_suffix: str = ""
) -> None:
    """Plot prime index vs log-prime to visualize density."""
    indices = np.arange(len(log_primes))

    plt.figure(figsize=(10, 6))
    plt.plot(indices, log_primes, linewidth=0.5)

    # Theoretical curve from PNT: ln(p_n) ≈ ln(n * ln(n))
    # Approximate for large n
    if len(indices) > 100:
        n_theory = indices[indices > 100]
        log_p_theory = np.log(n_theory * np.log(n_theory))
        plt.plot(n_theory, log_p_theory, "--", linewidth=2, label="PNT approximation")

    plt.xlabel("Prime Index", fontsize=12)
    plt.ylabel("ln(prime)", fontsize=12)
    plt.title(f"Prime Density {title_suffix}", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
