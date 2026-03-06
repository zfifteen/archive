#!/usr/bin/env python3
"""
Validation Framework for Z5D Factorization

Implements statistical validation including bootstrap analysis.
"""

import numpy as np
from scipy.stats import bootstrap

def bootstrap_analysis(times_naive, times_z5d, n_resamples=1000):
    """
    Perform bootstrap analysis on factorization times.
    
    Computes improvement ratio (naive / z5d) and confidence interval.
    """
    ratios = np.array([n / z for n, z in zip(times_naive, times_z5d)])
    
    boot = bootstrap((ratios,), np.mean, n_resamples=n_resamples)
    ci = boot.confidence_interval
    
    return {
        "mean_improvement_ratio": float(np.mean(ratios)),
        "ci_low": float(ci.low),
        "ci_high": float(ci.high),
        "n_resamples": n_resamples
    }