"""
Binning Module - 100 Equal-Width Bins on Log-Prime Axis

Implements binning strategy that divides the log-prime range into 100 equal-width bins
(not by prime index). For each bin, computes mean, variance, skewness, and kurtosis
of log-gaps.
"""

import numpy as np
from scipy import stats
from typing import Dict, List


def compute_log_prime_bins(log_primes: np.ndarray, 
                           n_bins: int = 100) -> Dict:
    """
    Create equal-width bins on log-prime axis.
    
    Args:
        log_primes: Array of ln(prime) values
        n_bins: Number of bins (default 100)
        
    Returns:
        Dictionary with binning information
    """
    # Find range
    min_log = np.min(log_primes)
    max_log = np.max(log_primes)
    
    # Create bin edges
    edges = np.linspace(min_log, max_log, n_bins + 1)
    
    # Assign each log_prime to a bin
    assignments = np.digitize(log_primes, edges)
    
    # Compute bin centers
    centers = (edges[:-1] + edges[1:]) / 2
    
    # Count items per bin
    counts = np.bincount(assignments, minlength=n_bins+2)[1:n_bins+1]
    
    return {
        'edges': edges,
        'centers': centers,
        'assignments': assignments,
        'counts': counts,
        'n_bins': n_bins
    }


def compute_bin_statistics(log_gaps: np.ndarray,
                           bin_assignments: np.ndarray,
                           n_bins: int = 100) -> Dict:
    """
    Compute statistical moments for log-gaps in each bin.
    
    Args:
        log_gaps: Array of log-gap values
        bin_assignments: Bin index for each log_gap
        n_bins: Total number of bins
        
    Returns:
        Dictionary with 'mean', 'variance', 'skewness', 'kurtosis' arrays
    """
    # Initialize arrays
    means = np.full(n_bins, np.nan)
    variances = np.full(n_bins, np.nan)
    skewnesses = np.full(n_bins, np.nan)
    kurtoses = np.full(n_bins, np.nan)
    
    # Compute statistics for each bin
    for bin_idx in range(1, n_bins + 1):
        # Extract log_gaps for this bin
        mask = bin_assignments == bin_idx
        bin_log_gaps = log_gaps[mask]
        
        if len(bin_log_gaps) == 0:
            continue
        
        # Compute moments
        means[bin_idx - 1] = np.mean(bin_log_gaps)
        variances[bin_idx - 1] = np.var(bin_log_gaps)
        
        if len(bin_log_gaps) >= 3:  # Need at least 3 points for skewness/kurtosis
            skewnesses[bin_idx - 1] = stats.skew(bin_log_gaps)
            kurtoses[bin_idx - 1] = stats.kurtosis(bin_log_gaps)
    
    return {
        'mean': means,
        'variance': variances,
        'skewness': skewnesses,
        'kurtosis': kurtoses
    }


def analyze_bins(log_primes: np.ndarray,
                log_gaps: np.ndarray,
                n_bins: int = 100) -> Dict:
    """
    Complete binning analysis combining binning and statistics.
    
    Args:
        log_primes: ln(prime) values (length N)
        log_gaps: log-gap values (length N-1)
        n_bins: Number of bins (default 100)
        
    Returns:
        Comprehensive dictionary with binning and statistics
    """
    # Create bin structure
    bin_info = compute_log_prime_bins(log_primes, n_bins)
    
    # Align log_primes with log_gaps (log_gaps has length N-1)
    log_primes_aligned = log_primes[:-1]
    bin_assignments_aligned = bin_info['assignments'][:-1]
    
    # Compute statistics per bin
    bin_stats = compute_bin_statistics(log_gaps, bin_assignments_aligned, n_bins)
    
    # Merge results
    result = {
        **bin_info,
        **bin_stats,
        'total_gaps': len(log_gaps),
        'bins_used': np.sum(bin_info['counts'] > 0)
    }
    
    return result
