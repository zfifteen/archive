"""
Distribution Analysis and Statistical Tests

Provides KS test, log-rank test, and tail statistics for experiment validation.
"""

from typing import Dict, Any
import numpy as np
from scipy import stats
from dataclasses import dataclass


@dataclass
class KSTestResult:
    """Result of Kolmogorov-Smirnov test."""

    statistic: float
    pvalue: float
    significant: bool
    alpha: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "statistic": float(self.statistic),
            "pvalue": float(self.pvalue),
            "significant": bool(self.significant),
            "alpha": float(self.alpha),
        }


@dataclass
class LogRankResult:
    """Result of log-rank survival test."""

    statistic: float
    pvalue: float
    significant: bool
    alpha: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "statistic": float(self.statistic),
            "pvalue": float(self.pvalue),
            "significant": bool(self.significant),
            "alpha": float(self.alpha),
        }


@dataclass
class TailStatistics:
    """Tail statistics for heavy-tail characterization."""

    tail_index: float  # Higher = heavier tail
    q1_value: float  # First quartile
    q3_value: float  # Third quartile
    q1_hazard: float  # Hazard rate at Q1
    mean: float
    median: float
    p95: float  # 95th percentile
    p99: float  # 99th percentile

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tail_index": float(self.tail_index),
            "q1_value": float(self.q1_value),
            "q3_value": float(self.q3_value),
            "q1_hazard": float(self.q1_hazard),
            "mean": float(self.mean),
            "median": float(self.median),
            "p95": float(self.p95),
            "p99": float(self.p99),
        }


def ks_test_two_sample(
    data1: np.ndarray, data2: np.ndarray, alpha: float = 0.05
) -> KSTestResult:
    """Two-sample Kolmogorov-Smirnov test.

    Tests if two samples come from the same distribution.

    Args:
        data1: First sample
        data2: Second sample
        alpha: Significance level (default 0.05)

    Returns:
        KSTestResult with statistic, p-value, and significance

    Example:
        >>> baseline = np.random.normal(10, 1, 100)
        >>> treatment = np.random.normal(9, 1, 100)  # Different mean
        >>> result = ks_test_two_sample(baseline, treatment)
        >>> result.significant  # True if distributions differ
    """
    data1 = np.asarray(data1)
    data2 = np.asarray(data2)

    statistic, pvalue = stats.ks_2samp(data1, data2)

    return KSTestResult(
        statistic=float(statistic),
        pvalue=float(pvalue),
        significant=bool(pvalue < alpha),
        alpha=alpha,
    )


def log_rank_test(
    times1: np.ndarray, times2: np.ndarray, alpha: float = 0.05
) -> LogRankResult:
    """Log-rank test for survival curves (time-to-event data).

    Tests if two survival distributions differ significantly.
    Simplified implementation using Mantel-Haenszel statistic.

    Args:
        times1: Event times for group 1
        times2: Event times for group 2
        alpha: Significance level

    Returns:
        LogRankResult with test statistic and p-value
    """
    times1 = np.asarray(times1)
    times2 = np.asarray(times2)

    # Combine data with group labels
    all_times = np.concatenate([times1, times2])
    groups = np.concatenate([np.ones(len(times1)), np.zeros(len(times2))])

    # Get unique event times
    unique_times = np.sort(np.unique(all_times))

    # Compute log-rank statistic
    observed1 = 0
    expected1 = 0
    variance = 0

    for t in unique_times:
        # At-risk counts
        at_risk1 = np.sum(times1 >= t)
        at_risk2 = np.sum(times2 >= t)
        at_risk_total = at_risk1 + at_risk2

        if at_risk_total == 0:
            continue

        # Event counts at time t
        events1 = np.sum(times1 == t)
        events2 = np.sum(times2 == t)
        events_total = events1 + events2

        if events_total == 0:
            continue

        # Expected events and variance
        expected1_t = (at_risk1 / at_risk_total) * events_total
        expected1 += expected1_t
        observed1 += events1

        if at_risk_total > 1:
            var_t = (
                at_risk1 * at_risk2 * events_total * (at_risk_total - events_total)
            ) / (at_risk_total**2 * (at_risk_total - 1))
            variance += var_t

    # Test statistic (chi-square with 1 df)
    if variance > 0:
        statistic = (observed1 - expected1) ** 2 / variance
        pvalue = 1.0 - stats.chi2.cdf(statistic, df=1)
    else:
        statistic = 0.0
        pvalue = 1.0

    return LogRankResult(
        statistic=float(statistic),
        pvalue=float(pvalue),
        significant=bool(pvalue < alpha),
        alpha=alpha,
    )


def compute_tail_statistics(data: np.ndarray) -> TailStatistics:
    """Compute tail statistics for heavy-tail characterization.

    Args:
        data: Time-to-event or metric observations

    Returns:
        TailStatistics with tail index, quartiles, and hazard
    """
    data = np.asarray(data)
    data_sorted = np.sort(data)

    # Quartiles
    q1 = np.percentile(data, 25)
    q2 = np.percentile(data, 50)  # Median
    q3 = np.percentile(data, 75)
    p95 = np.percentile(data, 95)
    p99 = np.percentile(data, 99)

    # Tail index: ratio of 95th to median (higher = heavier tail)
    tail_index = p95 / q2 if q2 > 0 else 0.0

    # First-quartile hazard: approximate instantaneous failure rate at Q1
    # Hazard ≈ f(t) / S(t) where f is PDF and S is survival function
    # Use empirical: events near Q1 / survival at Q1
    q1_idx = np.searchsorted(data_sorted, q1)
    if q1_idx > 0 and q1_idx < len(data):
        # Events in small window around Q1
        window = max(1, int(len(data) * 0.05))  # 5% window
        lower = max(0, q1_idx - window // 2)
        upper = min(len(data), q1_idx + window // 2)
        events_near_q1 = upper - lower
        survival_at_q1 = (len(data) - q1_idx) / len(data)

        if survival_at_q1 > 0:
            q1_hazard = events_near_q1 / (len(data) * survival_at_q1)
        else:
            q1_hazard = 0.0
    else:
        q1_hazard = 0.0

    return TailStatistics(
        tail_index=float(tail_index),
        q1_value=float(q1),
        q3_value=float(q3),
        q1_hazard=float(q1_hazard),
        mean=float(np.mean(data)),
        median=float(q2),
        p95=float(p95),
        p99=float(p99),
    )


def compare_distributions(
    baseline: np.ndarray, treatment: np.ndarray, alpha: float = 0.05
) -> Dict[str, Any]:
    """Comprehensive distribution comparison.

    Includes KS test, log-rank test, and tail statistics.

    Args:
        baseline: Baseline condition data
        treatment: Treatment condition data
        alpha: Significance level for tests

    Returns:
        Dictionary with all test results and statistics
    """
    # KS test
    ks_result = ks_test_two_sample(baseline, treatment, alpha)

    # Log-rank test (survival analysis)
    lr_result = log_rank_test(baseline, treatment, alpha)

    # Tail statistics
    baseline_tail = compute_tail_statistics(baseline)
    treatment_tail = compute_tail_statistics(treatment)

    # Compare tail indices
    tail_improvement = baseline_tail.tail_index - treatment_tail.tail_index
    tail_lighter = tail_improvement > 0  # Positive = treatment has lighter tail

    # Compare hazards
    hazard_improvement = treatment_tail.q1_hazard - baseline_tail.q1_hazard
    hazard_higher = hazard_improvement > 0  # Positive = treatment fails faster early

    return {
        "ks_test": ks_result.to_dict(),
        "log_rank_test": lr_result.to_dict(),
        "baseline_tail": baseline_tail.to_dict(),
        "treatment_tail": treatment_tail.to_dict(),
        "tail_improvement": float(tail_improvement),
        "tail_is_lighter": bool(tail_lighter),
        "hazard_improvement": float(hazard_improvement),
        "hazard_is_higher": bool(hazard_higher),
        "distributions_differ": ks_result.significant or lr_result.significant,
    }


__all__ = [
    "KSTestResult",
    "LogRankResult",
    "TailStatistics",
    "ks_test_two_sample",
    "log_rank_test",
    "compute_tail_statistics",
    "compare_distributions",
]
