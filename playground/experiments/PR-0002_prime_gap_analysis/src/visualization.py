"""
Visualization Module

Generates plots for gap analysis:
- Q-Q plots for distribution testing
- ACF/PACF plots
- Gap histograms
- PNT deviation plots
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional, Dict


def plot_qq(gaps: np.ndarray, band: str, output: Optional[str] = None) -> None:
    """Generate Q-Q plot for testing lognormal hypothesis.
    
    Args:
        gaps: Array of gap values
        band: Band identifier (e.g., '1e6_1e7')
        output: Output file path (if None, displays plot)
    """
    from distribution_tests import compute_qq_data
    
    theoretical, sample = compute_qq_data(gaps)
    
    plt.figure(figsize=(8, 8))
    plt.scatter(theoretical, sample, alpha=0.5, s=1)
    
    # Reference line
    min_val = min(theoretical.min(), sample.min())
    max_val = max(theoretical.max(), sample.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Normal')
    
    plt.xlabel('Theoretical Normal Quantiles')
    plt.ylabel('Sample Quantiles (Standardized log(gap))')
    plt.title(f'Q-Q Plot: Normal vs log(gap) - Band {band}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_acf(gaps: np.ndarray, acf: np.ndarray, confidence_band: float,
             output: Optional[str] = None) -> None:
    """Plot autocorrelation function with confidence bands.
    
    Args:
        gaps: Array of gap values (for metadata)
        acf: Autocorrelation function values
        confidence_band: 95% confidence interval (e.g., 1.96/sqrt(n))
        output: Output file path
    """
    lags = np.arange(len(acf))
    
    plt.figure(figsize=(12, 5))
    
    # ACF plot
    plt.subplot(1, 2, 1)
    plt.stem(lags, acf, basefmt=' ')
    plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    plt.axhline(y=confidence_band, color='r', linestyle='--', label='95% CI')
    plt.axhline(y=-confidence_band, color='r', linestyle='--')
    plt.xlabel('Lag')
    plt.ylabel('ACF')
    plt.title('Autocorrelation Function')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Zoom on first 20 lags
    plt.subplot(1, 2, 2)
    plt.stem(lags[:20], acf[:20], basefmt=' ')
    plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    plt.axhline(y=confidence_band, color='r', linestyle='--', label='95% CI')
    plt.axhline(y=-confidence_band, color='r', linestyle='--')
    plt.xlabel('Lag')
    plt.ylabel('ACF')
    plt.title('ACF (First 20 Lags)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_gap_histogram(gaps: np.ndarray, output: Optional[str] = None) -> None:
    """Plot histogram of gap values.
    
    Args:
        gaps: Array of gap values
        output: Output file path
    """
    plt.figure(figsize=(12, 5))
    
    # Raw gaps
    plt.subplot(1, 2, 1)
    plt.hist(gaps, bins=50, edgecolor='black', alpha=0.7)
    plt.xlabel('Gap Size')
    plt.ylabel('Frequency')
    plt.title('Gap Distribution')
    plt.grid(True, alpha=0.3)
    
    # Log gaps
    plt.subplot(1, 2, 2)
    plt.hist(np.log(gaps), bins=50, edgecolor='black', alpha=0.7)
    plt.xlabel('log(Gap Size)')
    plt.ylabel('Frequency')
    plt.title('log(Gap) Distribution')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_pnt_deviation(primes: np.ndarray, normalized_gaps: np.ndarray,
                       pnt_results: Dict, output: Optional[str] = None) -> None:
    """Plot gap/log(p) vs prime magnitude to visualize PNT deviation.
    
    Args:
        primes: Array of prime numbers
        normalized_gaps: Array of gap/log(p) values
        pnt_results: Results from test_pnt_deviation
        output: Output file path
    """
    log_primes = np.log(primes[:-1])
    
    plt.figure(figsize=(12, 6))
    
    # Scatter plot with trend
    plt.subplot(1, 2, 1)
    # Sample for visibility
    step = max(1, len(log_primes) // 10000)
    plt.scatter(log_primes[::step], normalized_gaps[::step], alpha=0.3, s=1)
    plt.axhline(y=1.0, color='r', linestyle='--', label='PNT Prediction')
    plt.xlabel('log(p)')
    plt.ylabel('gap / log(p)')
    plt.title('Gap Normalization vs Prime Magnitude')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Mean per bin
    plt.subplot(1, 2, 2)
    n_bins = 100
    log_min = np.min(log_primes)
    log_max = np.max(log_primes)
    bin_edges = np.linspace(log_min, log_max, n_bins + 1)
    bin_indices = np.digitize(log_primes, bin_edges) - 1
    
    bin_means = []
    bin_centers = []
    for i in range(n_bins):
        mask = bin_indices == i
        if np.sum(mask) > 0:
            bin_means.append(np.mean(normalized_gaps[mask]))
            bin_centers.append((bin_edges[i] + bin_edges[i+1]) / 2)
    
    plt.plot(bin_centers, bin_means, 'b-', linewidth=2, label='Bin Means')
    plt.axhline(y=1.0, color='r', linestyle='--', label='PNT Prediction')
    plt.xlabel('log(p)')
    plt.ylabel('Mean gap / log(p)')
    plt.title(f'PNT Deviation (slope={pnt_results["slope"]:.6f}, p={pnt_results["p_value"]:.4f})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
