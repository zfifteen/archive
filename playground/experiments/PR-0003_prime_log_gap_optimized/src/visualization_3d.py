"""
3D Visualization Module - Complete Implementation

Generates 5 required 3D plots for advanced analysis.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
from typing import Dict, Optional

try:
    from statsmodels.tsa.stattools import acf
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


def plot_scatter_3d(log_primes: np.ndarray,
                   log_gaps: np.ndarray,
                   output_path: str,
                   sample_size: Optional[int] = 10000,
                   title_suffix: str = "") -> None:
    """Create 3D scatter plot of (index, log-prime, log-gap)."""
    log_primes_aligned = log_primes[:-1]
    indices = np.arange(len(log_gaps))
    
    # Downsample
    if len(log_gaps) > sample_size:
        idx = np.random.choice(len(log_gaps), sample_size, replace=False)
        indices_plot = indices[idx]
        log_primes_plot = log_primes_aligned[idx]
        log_gaps_plot = log_gaps[idx]
    else:
        indices_plot = indices
        log_primes_plot = log_primes_aligned
        log_gaps_plot = log_gaps
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.scatter(indices_plot, log_primes_plot, log_gaps_plot, 
              alpha=0.3, s=1, c=log_gaps_plot, cmap='viridis')
    
    ax.set_xlabel('Prime Index')
    ax.set_ylabel('ln(prime)')
    ax.set_zlabel('Log-Gap')
    ax.set_title(f'3D Scatter {title_suffix}')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_surface_3d(log_primes: np.ndarray,
                   log_gaps: np.ndarray,
                   output_path: str,
                   n_bins_x: int = 50,
                   n_bins_y: int = 50,
                   title_suffix: str = "") -> None:
    """Create 3D surface plot from 2D histogram."""
    log_primes_aligned = log_primes[:-1]
    
    # Create 2D histogram
    H, x_edges, y_edges = np.histogram2d(log_primes_aligned, log_gaps, 
                                         bins=(n_bins_x, n_bins_y))
    
    # Create meshgrid
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    X, Y = np.meshgrid(x_centers, y_centers)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(X, Y, H.T, cmap='viridis', alpha=0.8)
    
    ax.set_xlabel('ln(prime)')
    ax.set_ylabel('Log-Gap')
    ax.set_zlabel('Count')
    ax.set_title(f'3D Surface {title_suffix}')
    
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_contour_3d(log_gaps: np.ndarray,
                   output_path: str,
                   max_lag: int = 50,
                   n_scales: int = 5,
                   title_suffix: str = "") -> None:
    """Plot autocorrelation as function of lag and scale."""
    if not STATSMODELS_AVAILABLE:
        print("Statsmodels not available, skipping contour_3d")
        # Create empty plot
        fig = plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'Statsmodels not available', 
                ha='center', va='center', fontsize=14)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return
    
    # Define scales
    n = len(log_gaps)
    scales = np.linspace(min(1000, n//10), n, n_scales, dtype=int)
    
    # Compute ACF for each scale
    ACF_matrix = np.zeros((n_scales, max_lag + 1))
    for i, scale in enumerate(scales):
        if scale < max_lag + 2:
            continue
        acf_vals = acf(log_gaps[:scale], nlags=max_lag)
        ACF_matrix[i, :] = acf_vals
    
    # Create meshgrid
    Lags, Scales = np.meshgrid(np.arange(max_lag + 1), scales)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(Lags, Scales, ACF_matrix, cmap='coolwarm', alpha=0.8)
    
    ax.set_xlabel('Lag')
    ax.set_ylabel('Scale (data points)')
    ax.set_zlabel('ACF')
    ax.set_title(f'ACF vs Lag and Scale {title_suffix}')
    
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_wireframe_3d(bin_analysis_multi_scale: Dict,
                     output_path: str,
                     title_suffix: str = "") -> None:
    """Wireframe plot of bin means by bin index and scale."""
    # If single scale, create dummy multi-scale data
    if not isinstance(bin_analysis_multi_scale, dict) or 'mean' in bin_analysis_multi_scale:
        # Single scale - create dummy visualization
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        if 'mean' in bin_analysis_multi_scale:
            means = bin_analysis_multi_scale['mean']
            bins = np.arange(1, len(means) + 1)
            scales = np.array([1])
            Bins, Scales = np.meshgrid(bins, scales)
            Means = means.reshape(1, -1)
        else:
            Bins, Scales, Means = np.meshgrid([1], [1], [0])
        
        ax.plot_wireframe(Bins, Scales, Means)
        ax.set_xlabel('Bin Index')
        ax.set_ylabel('Scale')
        ax.set_zlabel('Mean Log-Gap')
        ax.set_title(f'Wireframe (Single Scale) {title_suffix}')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return
    
    # Multi-scale data
    scales = sorted(bin_analysis_multi_scale.keys())
    n_bins = len(bin_analysis_multi_scale[scales[0]]['mean'])
    
    Means_matrix = np.zeros((len(scales), n_bins))
    for i, scale in enumerate(scales):
        Means_matrix[i, :] = bin_analysis_multi_scale[scale]['mean']
    
    bins = np.arange(1, n_bins + 1)
    Bins, Scales = np.meshgrid(bins, scales)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot_wireframe(Bins, Scales, Means_matrix)
    ax.set_xlabel('Bin Index')
    ax.set_ylabel('Scale')
    ax.set_zlabel('Mean Log-Gap')
    ax.set_title(f'Wireframe {title_suffix}')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_bar_3d(bin_analysis: Dict,
               output_path: str,
               n_groups: int = 10,
               title_suffix: str = "") -> None:
    """3D bar plot of skewness and kurtosis per bin group."""
    skewness = bin_analysis.get('skewness', np.array([]))
    kurtosis = bin_analysis.get('kurtosis', np.array([]))
    
    if len(skewness) == 0 or len(kurtosis) == 0:
        print("No skewness/kurtosis data for bar_3d")
        fig = plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'No data available', ha='center', va='center')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return
    
    # Group bins
    n_bins = len(skewness)
    bins_per_group = max(1, n_bins // n_groups)
    
    grouped_skew = []
    grouped_kurt = []
    
    for i in range(n_groups):
        start = i * bins_per_group
        end = min((i + 1) * bins_per_group, n_bins)
        if start >= n_bins:
            break
        
        group_skew = skewness[start:end]
        group_kurt = kurtosis[start:end]
        
        # Filter NaN
        group_skew_clean = group_skew[~np.isnan(group_skew)]
        group_kurt_clean = group_kurt[~np.isnan(group_kurt)]
        
        if len(group_skew_clean) > 0:
            grouped_skew.append(np.mean(group_skew_clean))
        else:
            grouped_skew.append(0)
        
        if len(group_kurt_clean) > 0:
            grouped_kurt.append(np.mean(group_kurt_clean))
        else:
            grouped_kurt.append(0)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create bar positions
    x_pos = np.arange(len(grouped_skew))
    y_pos_skew = np.zeros(len(grouped_skew))
    y_pos_kurt = np.ones(len(grouped_kurt))
    
    # Bar dimensions
    dx = dy = 0.4
    dz_skew = grouped_skew
    dz_kurt = grouped_kurt
    
    # Plot bars
    ax.bar3d(x_pos, y_pos_skew, np.zeros(len(x_pos)), dx, dy, dz_skew, 
            color='blue', alpha=0.7, label='Skewness')
    ax.bar3d(x_pos, y_pos_kurt, np.zeros(len(x_pos)), dx, dy, dz_kurt, 
            color='red', alpha=0.7, label='Kurtosis')
    
    ax.set_xlabel('Bin Group')
    ax.set_ylabel('Metric (0=Skew, 1=Kurt)')
    ax.set_zlabel('Value')
    ax.set_title(f'Skewness and Kurtosis by Bin Group {title_suffix}')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Skew', 'Kurt'])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
