"""
Resonance Plotting Utilities

Creates visualizations for geometric-resonance factorization A/B experiment results.
Note: Main resonance implementation lives in z-sandbox repo.
"""

from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def plot_ttf_survival_curves(
    baseline_ttf: np.ndarray,
    treatment_ttf: np.ndarray,
    treatment_name: str,
    output_path: Path,
    band: str = "unknown",
) -> None:
    """Plot time-to-first-factor survival curves.

    Args:
        baseline_ttf: Baseline TTF measurements
        treatment_ttf: Treatment TTF measurements
        treatment_name: Name of treatment condition
        output_path: Where to save the plot
        band: Difficulty band (easy/med/hard)
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Compute empirical survival functions
    def survival_curve(data):
        sorted_data = np.sort(data)
        n = len(sorted_data)
        survival = 1.0 - np.arange(1, n + 1) / n
        return sorted_data, survival

    times_base, surv_base = survival_curve(baseline_ttf)
    times_treat, surv_treat = survival_curve(treatment_ttf)

    # Plot
    ax.step(
        times_base,
        surv_base,
        where="post",
        label="Baseline",
        linewidth=2,
        color="red",
        alpha=0.7,
    )
    ax.step(
        times_treat,
        surv_treat,
        where="post",
        label=treatment_name,
        linewidth=2,
        color="green",
        alpha=0.7,
    )

    ax.set_xlabel("Time to First Factor (seconds)", fontsize=12)
    ax.set_ylabel("Survival Probability", fontsize=12)
    ax.set_title(
        f"TTF Survival Curves - {band.capitalize()} Band",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)

    # Add median lines
    median_base = np.median(baseline_ttf)
    median_treat = np.median(treatment_ttf)
    ax.axvline(
        median_base,
        color="red",
        linestyle="--",
        alpha=0.5,
        label=f"Baseline Median: {median_base:.2f}s",
    )
    ax.axvline(
        median_treat,
        color="green",
        linestyle="--",
        alpha=0.5,
        label=f"{treatment_name} Median: {median_treat:.2f}s",
    )

    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


def plot_precision_recall(
    baseline_pr: Dict[str, float],
    treatment_pr: Dict[str, float],
    treatment_name: str,
    output_path: Path,
    band: str = "unknown",
) -> None:
    """Plot precision/recall comparison for top-K factors.

    Args:
        baseline_pr: Baseline precision/recall dict with keys like 'top10_precision'
        treatment_pr: Treatment precision/recall dict
        treatment_name: Name of treatment condition
        output_path: Where to save the plot
        band: Difficulty band
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Extract K values and metrics
    k_values = [10, 25, 50]

    baseline_prec = [baseline_pr.get(f"top{k}_precision", 0) for k in k_values]
    treatment_prec = [treatment_pr.get(f"top{k}_precision", 0) for k in k_values]

    baseline_recall = [baseline_pr.get(f"top{k}_recall", 0) for k in k_values]
    treatment_recall = [treatment_pr.get(f"top{k}_recall", 0) for k in k_values]

    x = np.arange(len(k_values))
    width = 0.35

    # Precision plot
    ax1.bar(
        x - width / 2,
        baseline_prec,
        width,
        label="Baseline",
        color="lightcoral",
        alpha=0.8,
    )
    ax1.bar(
        x + width / 2,
        treatment_prec,
        width,
        label=treatment_name,
        color="lightgreen",
        alpha=0.8,
    )
    ax1.set_xlabel("Top-K", fontsize=12)
    ax1.set_ylabel("Precision", fontsize=12)
    ax1.set_title("Precision Comparison", fontsize=12, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"K={k}" for k in k_values])
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)
    ax1.set_ylim(0, 1.0)

    # Recall plot
    ax2.bar(
        x - width / 2,
        baseline_recall,
        width,
        label="Baseline",
        color="lightcoral",
        alpha=0.8,
    )
    ax2.bar(
        x + width / 2,
        treatment_recall,
        width,
        label=treatment_name,
        color="lightgreen",
        alpha=0.8,
    )
    ax2.set_xlabel("Top-K", fontsize=12)
    ax2.set_ylabel("Recall", fontsize=12)
    ax2.set_title("Recall Comparison", fontsize=12, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"K={k}" for k in k_values])
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)
    ax2.set_ylim(0, 1.0)

    plt.suptitle(
        f"Top-K Precision/Recall - {band.capitalize()} Band",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


def plot_tail_comparison(
    baseline_tail: Dict[str, float],
    treatment_tail: Dict[str, float],
    treatment_name: str,
    output_path: Path,
    band: str = "unknown",
) -> None:
    """Plot tail statistics comparison.

    Args:
        baseline_tail: Baseline tail statistics dict
        treatment_tail: Treatment tail statistics dict
        treatment_name: Name of treatment condition
        output_path: Where to save the plot
        band: Difficulty band
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Tail index comparison
    tail_indices = [baseline_tail["tail_index"], treatment_tail["tail_index"]]
    colors = ["lightcoral", "lightgreen"]
    labels = ["Baseline", treatment_name]

    bars1 = ax1.bar(labels, tail_indices, color=colors, alpha=0.8)
    ax1.set_ylabel("Tail Index", fontsize=12)
    ax1.set_title("Tail Index (Lower = Lighter Tail)", fontsize=12, fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)

    # Add value labels
    for bar, val in zip(bars1, tail_indices):
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    # Q1 hazard comparison
    hazards = [baseline_tail["q1_hazard"], treatment_tail["q1_hazard"]]

    bars2 = ax2.bar(labels, hazards, color=colors, alpha=0.8)
    ax2.set_ylabel("Q1 Hazard Rate", fontsize=12)
    ax2.set_title(
        "First-Quartile Hazard (Higher = Faster Early)", fontsize=12, fontweight="bold"
    )
    ax2.grid(axis="y", alpha=0.3)

    # Add value labels
    for bar, val in zip(bars2, hazards):
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{val:.4f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    plt.suptitle(
        f"Tail Statistics - {band.capitalize()} Band",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


def create_resonance_summary_plot(
    results_summary: Dict[str, Any],
    output_path: Path,
) -> None:
    """Create comprehensive summary plot for resonance experiment.

    Args:
        results_summary: Complete results summary dict
        output_path: Where to save the plot
    """
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    # This is a placeholder for a more comprehensive summary
    # that would combine TTF, precision/recall, and tail stats

    ax = fig.add_subplot(gs[:, :])
    ax.text(
        0.5,
        0.5,
        "Resonance Experiment Summary\n\n"
        "Main implementation in z-sandbox repo.\n"
        "Use plot_ttf_survival_curves, plot_precision_recall,\n"
        "and plot_tail_comparison for detailed visualizations.",
        ha="center",
        va="center",
        fontsize=14,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    ax.axis("off")

    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


__all__ = [
    "plot_ttf_survival_curves",
    "plot_precision_recall",
    "plot_tail_comparison",
    "create_resonance_summary_plot",
]
