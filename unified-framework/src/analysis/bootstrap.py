"""
Bootstrap Confidence Interval Analysis

Provides percentile bootstrap confidence intervals for experiment metrics.
All RNG states are recorded for reproducibility.
"""

from typing import Dict, Any
import numpy as np
from dataclasses import dataclass


@dataclass
class BootstrapResult:
    """Result of bootstrap confidence interval calculation."""

    point_estimate: float
    ci_lower: float
    ci_upper: float
    confidence_level: float
    bootstrap_samples: int
    seed: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "point_estimate": float(self.point_estimate),
            "ci_lower": float(self.ci_lower),
            "ci_upper": float(self.ci_upper),
            "confidence_level": float(self.confidence_level),
            "bootstrap_samples": int(self.bootstrap_samples),
            "seed": int(self.seed),
        }

    def crosses_zero(self) -> bool:
        """Check if confidence interval crosses zero."""
        return self.ci_lower < 0 < self.ci_upper

    def is_significant_increase(self) -> bool:
        """Check if both bounds are positive (significant increase)."""
        return self.ci_lower > 0

    def is_significant_decrease(self) -> bool:
        """Check if both bounds are negative (significant decrease)."""
        return self.ci_upper < 0


def bootstrap_percentile_ci(
    data: np.ndarray,
    statistic: callable = np.median,
    n_iterations: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> BootstrapResult:
    """Calculate percentile bootstrap confidence interval.

    Args:
        data: 1D array of observations
        statistic: Function to compute (default: median)
        n_iterations: Number of bootstrap samples
        confidence_level: Confidence level (default 0.95 for 95% CI)
        seed: Random seed for reproducibility

    Returns:
        BootstrapResult with point estimate and CI

    Example:
        >>> data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        >>> result = bootstrap_percentile_ci(data, np.mean, n_iterations=1000, seed=42)
        >>> result.point_estimate
        3.0
    """
    rng = np.random.RandomState(seed)
    data = np.asarray(data)

    # Compute point estimate
    point = statistic(data)

    # Bootstrap resampling
    n = len(data)
    bootstrap_stats = np.zeros(n_iterations)

    for i in range(n_iterations):
        sample = rng.choice(data, size=n, replace=True)
        bootstrap_stats[i] = statistic(sample)

    # Percentile CI
    alpha = 1.0 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100

    ci_lower = np.percentile(bootstrap_stats, lower_percentile)
    ci_upper = np.percentile(bootstrap_stats, upper_percentile)

    return BootstrapResult(
        point_estimate=float(point),
        ci_lower=float(ci_lower),
        ci_upper=float(ci_upper),
        confidence_level=confidence_level,
        bootstrap_samples=n_iterations,
        seed=seed,
    )


def bootstrap_difference_ci(
    data_baseline: np.ndarray,
    data_treatment: np.ndarray,
    statistic: callable = np.median,
    n_iterations: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> BootstrapResult:
    """Calculate CI for difference between two conditions.

    Positive difference means treatment > baseline.

    Args:
        data_baseline: Baseline condition observations
        data_treatment: Treatment condition observations
        statistic: Function to compute on each sample
        n_iterations: Bootstrap samples
        confidence_level: CI level
        seed: Random seed

    Returns:
        BootstrapResult for the difference (treatment - baseline)
    """
    rng = np.random.RandomState(seed)
    data_baseline = np.asarray(data_baseline)
    data_treatment = np.asarray(data_treatment)

    # Point estimate of difference
    point = statistic(data_treatment) - statistic(data_baseline)

    # Bootstrap resampling
    n_base = len(data_baseline)
    n_treat = len(data_treatment)
    bootstrap_diffs = np.zeros(n_iterations)

    for i in range(n_iterations):
        sample_base = rng.choice(data_baseline, size=n_base, replace=True)
        sample_treat = rng.choice(data_treatment, size=n_treat, replace=True)

        stat_base = statistic(sample_base)
        stat_treat = statistic(sample_treat)
        bootstrap_diffs[i] = stat_treat - stat_base

    # Percentile CI
    alpha = 1.0 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100

    ci_lower = np.percentile(bootstrap_diffs, lower_percentile)
    ci_upper = np.percentile(bootstrap_diffs, upper_percentile)

    return BootstrapResult(
        point_estimate=float(point),
        ci_lower=float(ci_lower),
        ci_upper=float(ci_upper),
        confidence_level=confidence_level,
        bootstrap_samples=n_iterations,
        seed=seed,
    )


def bootstrap_percent_change_ci(
    data_baseline: np.ndarray,
    data_treatment: np.ndarray,
    statistic: callable = np.median,
    n_iterations: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> BootstrapResult:
    """Calculate CI for percent change: ((treatment - baseline) / baseline) * 100.

    Positive means improvement/increase, negative means reduction/decrease.

    Args:
        data_baseline: Baseline condition observations
        data_treatment: Treatment condition observations
        statistic: Function to compute on each sample
        n_iterations: Bootstrap samples
        confidence_level: CI level
        seed: Random seed

    Returns:
        BootstrapResult for percent change
    """
    rng = np.random.RandomState(seed)
    data_baseline = np.asarray(data_baseline)
    data_treatment = np.asarray(data_treatment)

    # Point estimate
    base_stat = statistic(data_baseline)
    treat_stat = statistic(data_treatment)
    point = ((treat_stat - base_stat) / base_stat) * 100.0

    # Bootstrap
    n_base = len(data_baseline)
    n_treat = len(data_treatment)
    bootstrap_pcts = np.zeros(n_iterations)

    for i in range(n_iterations):
        sample_base = rng.choice(data_baseline, size=n_base, replace=True)
        sample_treat = rng.choice(data_treatment, size=n_treat, replace=True)

        stat_base = statistic(sample_base)
        stat_treat = statistic(sample_treat)

        if stat_base != 0:
            bootstrap_pcts[i] = ((stat_treat - stat_base) / stat_base) * 100.0
        else:
            bootstrap_pcts[i] = 0.0

    # Percentile CI
    alpha = 1.0 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100

    ci_lower = np.percentile(bootstrap_pcts, lower_percentile)
    ci_upper = np.percentile(bootstrap_pcts, upper_percentile)

    return BootstrapResult(
        point_estimate=float(point),
        ci_lower=float(ci_lower),
        ci_upper=float(ci_upper),
        confidence_level=confidence_level,
        bootstrap_samples=n_iterations,
        seed=seed,
    )


def compare_conditions(
    baseline: np.ndarray,
    treatment: np.ndarray,
    metric_name: str = "metric",
    n_iterations: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """Comprehensive comparison of two conditions.

    Returns both absolute difference and percent change with CIs.

    Args:
        baseline: Baseline observations
        treatment: Treatment observations
        metric_name: Name of metric for reporting
        n_iterations: Bootstrap iterations
        seed: Random seed

    Returns:
        Dictionary with baseline stats, treatment stats, difference, and percent change
    """
    # Individual condition CIs
    baseline_ci = bootstrap_percentile_ci(baseline, np.median, n_iterations, seed=seed)
    treatment_ci = bootstrap_percentile_ci(
        treatment, np.median, n_iterations, seed=seed + 1
    )

    # Difference CI
    diff_ci = bootstrap_difference_ci(
        baseline, treatment, np.median, n_iterations, seed=seed + 2
    )

    # Percent change CI
    pct_ci = bootstrap_percent_change_ci(
        baseline, treatment, np.median, n_iterations, seed=seed + 3
    )

    return {
        "metric": metric_name,
        "baseline": baseline_ci.to_dict(),
        "treatment": treatment_ci.to_dict(),
        "difference": diff_ci.to_dict(),
        "percent_change": pct_ci.to_dict(),
        "significant": not pct_ci.crosses_zero(),
        "n_baseline": len(baseline),
        "n_treatment": len(treatment),
    }


__all__ = [
    "BootstrapResult",
    "bootstrap_percentile_ci",
    "bootstrap_difference_ci",
    "bootstrap_percent_change_ci",
    "compare_conditions",
]
