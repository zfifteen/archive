"""
Visualization Module

This module creates plots to make the log-gap data "visible" and testable.
Humans think in pictures – histograms show shapes, Q-Q plots check fits, trends reveal decay.
These visuals help "see" if log-gaps behave like damped circuit signals.
All plots can be saved as PNGs for the experiment's figures folder.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os


def plot_log_gap_histogram(log_gaps: np.ndarray, save_path: str = None, title_suffix: str = ""):
    """
    Create a histogram to visualize the shape of log-gap distribution.

    A histogram is like a bar chart of frequencies: how often do gaps fall in each range?
    This shows if gaps are symmetric (normal) or skewed (log-normal, with a long tail).
    50 bins give detail without noise; alpha/transparency makes it readable.
    Grid helps estimate values; saves to file if path given, else displays.
    
    Args:
        log_gaps: Array of log-gap values
        save_path: Optional path to save the plot
        title_suffix: Optional suffix to add to title (e.g., scale info)
    """
    plt.figure(figsize=(10, 6))  # Wide figure for clarity
    plt.hist(
        log_gaps, bins=50, alpha=0.7, edgecolor="black"
    )  # 50 bins, semi-transparent
    plt.xlabel("Log Gap")  # X: gap value
    plt.ylabel("Frequency")  # Y: count in each bin
    title = f"Histogram of Prime Log-Gaps {title_suffix}".strip()
    plt.title(title)  # Descriptive title
    plt.grid(True, alpha=0.3)  # Light grid
    if save_path:
        plt.savefig(save_path)  # Save as PNG
        plt.close()  # Don't show if saving
    else:
        plt.show()  # Interactive display


def plot_qq_lognormal(log_gaps: np.ndarray, save_path: str = None, title_suffix: str = ""):
    """
    Q-Q (Quantile-Quantile) plot to check if log-gaps match log-normal perfectly.

    Q-Q compares data quantiles (percentiles) to a theoretical distribution's quantiles.
    If points lie on the diagonal line, the fit is perfect; deviations show mismatches.
    We fit log-normal parameters first, then plot. This visually confirms (or rejects) our hypothesis.
    Square figure for symmetry; title explains the comparison.
    
    Args:
        log_gaps: Array of log-gap values
        save_path: Optional path to save the plot
        title_suffix: Optional suffix to add to title (e.g., scale info)
    """
    plt.figure(figsize=(8, 8))  # Square for balance
    # Fit log-normal to data (fix loc at 0 since gaps >0)
    shape, loc, scale = stats.lognorm.fit(log_gaps, floc=0)
    # Generate Q-Q plot: data vs. fitted log-normal
    stats.probplot(log_gaps, dist="lognorm", sparams=(shape, loc, scale), plot=plt)
    title = f"Q-Q Plot: Log-Gaps vs Log-Normal {title_suffix}".strip()
    plt.title(title)  # Clear title
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_decay_trend(
    bin_means: np.ndarray,
    save_path: str = None,
    title_suffix: str = None,
    *,
    decile_means: np.ndarray = None
):
    """
    Line plot showing how average log-gaps change across prime groups.

    Primary analysis uses 50 bins for robust statistical proof.
    If decile_means is provided (legacy), it will be plotted alongside for comparison.
    X-axis: bin index (0 = smallest primes, higher = larger primes).
    Y-axis: average gap in that bin.
    A downward slope indicates "decay" – gaps shrinking relatively as primes grow.
    This plot visually tests the damping hypothesis.
    
    Args:
        bin_means: Array of bin means (primary analysis, default 50 bins) or dict with 'bin_means'/'means'
        save_path: Optional path to save the plot as PNG
        title_suffix: Optional suffix for the plot title (e.g., "(N=1,000,000)")
        decile_means: Optional legacy decile means for comparison overlay (keyword-only)
    """
    # Handle both dict and array inputs
    if isinstance(bin_means, dict):
        means = bin_means.get('bin_means', bin_means.get('means', None))
    else:
        means = bin_means
    
    if means is None:
        raise ValueError("Could not extract bin_means from input")
    
    plt.figure(figsize=(12, 6))  # Wide for trend visibility with more bins
    x_bins = np.arange(len(means))  # Indices 0-49 for 50 bins
    plt.plot(
        x_bins, means, "o-", label=f"{len(means)} Bins", markersize=4, alpha=0.8
    )  # Circles with line
    
    if decile_means is not None:
        x_decile = np.arange(len(decile_means))  # Indices 0-9
        # Scale x-axis to align decile bins with primary bin positions
        decile_scale_factor = len(means) / len(decile_means)
        x_decile_scaled = x_decile * decile_scale_factor
        plt.plot(
            x_decile_scaled, decile_means, "s-", 
            label="Deciles (legacy)", markersize=6, alpha=0.6
        )  # Squares with line, scaled x-axis
    
    plt.xlabel("Bin Index")  # Group position
    plt.ylabel("Mean Log-Gap")  # Average value
    title = f"Log-Gap Mean Decay Trend ({len(means)} Bins)"
    if title_suffix:
        title = f"{title} {title_suffix}"
    plt.title(title)  # Emphasizes decay
    plt.legend()  # Show labels
    plt.grid(True, alpha=0.3)  # Light grid
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_acf_pacf(
    acf_results, save_path: str = None, title_suffix: str = ""
):
    """
    Two-panel plot of autocorrelation functions to reveal gap "memory."

    Top: ACF bars show correlation strength at each lag (delay in gaps).
    Bars above zero = positive memory; below = negative.
    Dashed line at zero for reference.

    Bottom: PACF isolates direct correlations, helping identify patterns like AR(1).
    Together, they check if gaps behave like a circuit's filtered signal.
    Tall figure for two subplots; bars are narrow for clarity.
    
    Args:
        acf_results: Either a dict with 'acf' and 'pacf' keys, or ACF array (for backward compat)
        save_path: Optional path to save the plot
        title_suffix: Optional suffix for the title
    """
    # Handle both old (acf_values, pacf_values) and new (acf_results dict) calling conventions
    if isinstance(acf_results, dict):
        acf_values = acf_results['acf']
        pacf_values = acf_results.get('pacf', None)
    else:
        acf_values = acf_results
        pacf_values = None
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))  # Two rows, one column
    lags = np.arange(len(acf_values))  # Lag indices: 0, 1, 2, ...
    
    # Top subplot: ACF
    axes[0].bar(lags, acf_values, width=0.3)  # Bar chart of correlations
    axes[0].axhline(y=0, color="black", linestyle="--")  # Zero reference line
    title = f"Autocorrelation Function (ACF) {title_suffix}".strip()
    axes[0].set_title(title)  # Title for top
    axes[0].set_xlabel("Lag")  # X: time delay
    axes[0].set_ylabel("ACF")  # Y: correlation value
    axes[0].grid(True, alpha=0.3)  # Light grid
    
    # Bottom subplot: PACF (if available)
    if pacf_values is not None:
        axes[1].bar(lags, pacf_values, width=0.3, color="orange")
        axes[1].axhline(y=0, color="black", linestyle="--")
        title_pacf = f"Partial Autocorrelation Function (PACF) {title_suffix}".strip()
        axes[1].set_title(title_pacf)
        axes[1].set_xlabel("Lag")
        axes[1].set_ylabel("PACF")
        axes[1].grid(True, alpha=0.3)
    else:
        axes[1].text(0.5, 0.5, "PACF not available", 
                    ha='center', va='center', transform=axes[1].transAxes)
        axes[1].set_title(f"PACF (not evaluated)")
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def generate_all_plots(
    log_gaps: np.ndarray,
    bin_means: np.ndarray,
    decile_means: np.ndarray,
    acf_values: np.ndarray,
    pacf_values: np.ndarray,
    output_dir: str = "results/figures",
):
    """
    Batch-generate all four key plots and save them as PNGs.

    This is the main entry point for visualization in the experiment.
    It creates the full figure set: histogram, Q-Q, decay, ACF/PACF.
    Output directory is created if needed; files are named clearly for reports.
    Used by run_analysis.py to produce the results/figures/ folder.
    
    Note: bin_means should be 50-bin means for robust statistical analysis.
    """
    os.makedirs(output_dir, exist_ok=True)  # Ensure dir exists
    # Generate each plot with its filename
    plot_log_gap_histogram(log_gaps, os.path.join(output_dir, "log_gap_histogram.png"))
    plot_qq_lognormal(log_gaps, os.path.join(output_dir, "qq_plot_lognormal.png"))
    plot_decay_trend(
        bin_means, os.path.join(output_dir, "decay_trend.png"), decile_means=decile_means
    )
    plot_acf_pacf(acf_values, pacf_values, os.path.join(output_dir, "acf_pacf.png"))


if __name__ == "__main__":
    # Test the plotting functions with dummy data
    np.random.seed(42)  # Reproducible
    log_gaps = np.random.lognormal(0, 1, 1000)  # Fake log-normal gaps
    bin_means = np.linspace(1.0, 0.1, 50)  # 50 decreasing averages
    decile_means = np.array(
        [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    )  # Legacy deciles
    acf_values = np.random.randn(21) * 0.1  # Random correlations
    pacf_values = np.random.randn(21) * 0.1
    generate_all_plots(
        log_gaps, bin_means, decile_means, acf_values, pacf_values
    )  # Save to default dir


def plot_scale_comparison(all_results: dict, save_path: str = None):
    """
    Plot comparison of results across multiple scales.
    
    Visualizes how key metrics (like quintile means, slopes) vary with scale.
    
    Args:
        all_results: Dictionary mapping scale to results
        save_path: Path to save the plot (optional)
    """
    scales = sorted(all_results.keys())
    
    # Extract metrics for comparison
    quintile_slopes = [all_results[s]['quintile']['slope'] for s in scales]
    quintile_r2 = [all_results[s]['quintile']['r_squared'] for s in scales]
    mean_log_gaps = [all_results[s]['descriptive']['mean'] for s in scales]
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Cross-Scale Comparison', fontsize=14, fontweight='bold')
    
    # Plot 1: Quintile slope vs scale
    axes[0, 0].plot(scales, quintile_slopes, 'o-', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('Scale (N)')
    axes[0, 0].set_ylabel('Quintile Slope')
    axes[0, 0].set_title('Decay Trend Consistency')
    axes[0, 0].set_xscale('log')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Zero slope')
    axes[0, 0].legend()
    
    # Plot 2: R² vs scale
    axes[0, 1].plot(scales, quintile_r2, 's-', linewidth=2, markersize=8, color='green')
    axes[0, 1].set_xlabel('Scale (N)')
    axes[0, 1].set_ylabel('R²')
    axes[0, 1].set_title('Fit Quality Across Scales')
    axes[0, 1].set_xscale('log')
    axes[0, 1].set_ylim([0, 1])
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Mean log-gap vs scale
    axes[1, 0].plot(scales, mean_log_gaps, '^-', linewidth=2, markersize=8, color='purple')
    axes[1, 0].set_xlabel('Scale (N)')
    axes[1, 0].set_ylabel('Mean Log-Gap')
    axes[1, 0].set_title('Average Gap Behavior')
    axes[1, 0].set_xscale('log')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Summary table
    axes[1, 1].axis('off')
    summary_text = "Scale Summary:\n\n"
    for scale in scales:
        scale_name = f"10^{int(np.log10(scale))}"
        slope = all_results[scale]['quintile']['slope']
        r2 = all_results[scale]['quintile']['r_squared']
        summary_text += f"{scale_name}:  slope={slope:.4e}, R²={r2:.3f}\n"
    axes[1, 1].text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
                    verticalalignment='center')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
