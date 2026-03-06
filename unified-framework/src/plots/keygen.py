"""
Keygen Plotting Utilities

Creates visualizations for RSA keygen A/B experiment results.
"""

from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json


def plot_candidates_comparison(
    results: Dict[str, Dict[str, Any]],
    output_path: Path,
    bit_length: int,
) -> None:
    """Plot candidates per prime comparison across conditions.

    Args:
        results: Dict mapping condition name to summary dict
        output_path: Where to save the plot
        bit_length: RSA bit length for title
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    conditions = list(results.keys())
    medians = [results[c]["median_candidates"] for c in conditions]
    means = [results[c]["mean_candidates"] for c in conditions]

    x = np.arange(len(conditions))
    width = 0.35

    ax.bar(x - width / 2, medians, width, label="Median", alpha=0.8)
    ax.bar(x + width / 2, means, width, label="Mean", alpha=0.8)

    ax.set_xlabel("Condition", fontsize=12)
    ax.set_ylabel("Candidates per Prime", fontsize=12)
    ax.set_title(
        f"Candidates per Prime - {bit_length}-bit RSA", fontsize=14, fontweight="bold"
    )
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


def plot_time_comparison(
    results: Dict[str, Dict[str, Any]],
    output_path: Path,
    bit_length: int,
) -> None:
    """Plot wall-clock time comparison across conditions.

    Args:
        results: Dict mapping condition name to summary dict
        output_path: Where to save the plot
        bit_length: RSA bit length for title
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    conditions = list(results.keys())
    medians = [results[c]["median_total_time_ms"] for c in conditions]

    colors = [
        "red" if c == "baseline" else "green" if c == "simplex" else "gray"
        for c in conditions
    ]

    bars = ax.bar(conditions, medians, color=colors, alpha=0.7)

    # Add value labels on bars
    for bar, val in zip(bars, medians):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{val:.1f}ms",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_xlabel("Condition", fontsize=12)
    ax.set_ylabel("Median Wall-Clock Time (ms)", fontsize=12)
    ax.set_title(
        f"Time per Keypair - {bit_length}-bit RSA", fontsize=14, fontweight="bold"
    )
    ax.set_xticklabels(conditions, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


def plot_speedup_with_ci(
    baseline_times: np.ndarray,
    treatment_times: np.ndarray,
    treatment_name: str,
    ci_result: Dict[str, Any],
    output_path: Path,
    bit_length: int,
) -> None:
    """Plot percent speedup with bootstrap confidence interval.

    Args:
        baseline_times: Baseline time measurements
        treatment_times: Treatment time measurements
        treatment_name: Name of treatment condition
        ci_result: Bootstrap CI result dict
        output_path: Where to save the plot
        bit_length: RSA bit length for title
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Box plots
    positions = [1, 2]
    bp = ax1.boxplot(
        [baseline_times, treatment_times],
        positions=positions,
        labels=["Baseline", treatment_name],
        patch_artist=True,
        showmeans=True,
    )

    bp["boxes"][0].set_facecolor("lightcoral")
    bp["boxes"][1].set_facecolor("lightgreen")

    ax1.set_ylabel("Wall-Clock Time (ms)", fontsize=12)
    ax1.set_title("Time Distribution Comparison", fontsize=12, fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)

    # Right: Percent change with CI
    pct_change = ci_result["percent_change"]["point_estimate"]
    ci_lower = ci_result["percent_change"]["ci_lower"]
    ci_upper = ci_result["percent_change"]["ci_upper"]

    ax2.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax2.errorbar(
        [1],
        [pct_change],
        yerr=[[pct_change - ci_lower], [ci_upper - pct_change]],
        fmt="o",
        markersize=10,
        capsize=10,
        capthick=2,
        color="green" if pct_change < 0 else "red",
    )

    ax2.axhspan(
        ci_lower, ci_upper, alpha=0.2, color="green" if pct_change < 0 else "red"
    )

    ax2.set_xlim(0.5, 1.5)
    ax2.set_xticks([1])
    ax2.set_xticklabels([f"{treatment_name} vs Baseline"])
    ax2.set_ylabel("Percent Change (%)", fontsize=12)
    ax2.set_title(
        f"Speedup: {pct_change:.2f}% (95% CI)", fontsize=12, fontweight="bold"
    )
    ax2.grid(axis="y", alpha=0.3)

    # Add text annotation
    significant = not (ci_lower < 0 < ci_upper)
    sig_text = "Significant" if significant else "Not Significant"
    ax2.text(
        1,
        ci_upper + (abs(ci_upper - ci_lower) * 0.1),
        sig_text,
        ha="center",
        fontsize=10,
        fontweight="bold",
        color="green" if significant and pct_change < 0 else "red",
    )

    plt.suptitle(
        f"{bit_length}-bit RSA Keygen Performance",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


def plot_ablation_study(
    results: Dict[str, Dict[str, Any]],
    output_path: Path,
    bit_length: int,
) -> None:
    """Plot ablation study showing component contributions.

    Args:
        results: Dict mapping condition name to summary dict
        output_path: Where to save the plot
        bit_length: RSA bit length for title
    """
    # Order: baseline, components, product
    order = ["baseline", "A4", "euler", "self_dual", "simplex"]
    conditions = [c for c in order if c in results]

    if "baseline" not in results:
        print("Warning: baseline not in results, skipping ablation plot")
        return

    baseline_time = results["baseline"]["median_total_time_ms"]

    fig, ax = plt.subplots(figsize=(10, 6))

    speedups = []
    colors = []
    for c in conditions:
        time = results[c]["median_total_time_ms"]
        pct_change = ((time - baseline_time) / baseline_time) * 100
        speedups.append(pct_change)

        if c == "baseline":
            colors.append("gray")
        elif c == "simplex":
            colors.append("darkgreen")
        else:
            colors.append("steelblue")

    bars = ax.bar(conditions, speedups, color=colors, alpha=0.7)

    # Add value labels
    for bar, val in zip(bars, speedups):
        height = bar.get_height()
        va = "bottom" if height >= 0 else "top"
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{val:.2f}%",
            ha="center",
            va=va,
            fontsize=10,
            fontweight="bold",
        )

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Condition", fontsize=12)
    ax.set_ylabel("Percent Change vs Baseline (%)", fontsize=12)
    ax.set_title(
        f"Ablation Study - {bit_length}-bit RSA", fontsize=14, fontweight="bold"
    )
    ax.set_xticklabels(conditions, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="gray", alpha=0.7, label="Baseline"),
        Patch(facecolor="steelblue", alpha=0.7, label="Components"),
        Patch(facecolor="darkgreen", alpha=0.7, label="Product"),
    ]
    ax.legend(handles=legend_elements, loc="best")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved: {output_path}")


def create_all_keygen_plots(
    results_dir: Path,
    output_dir: Path,
    bit_length: int,
) -> None:
    """Create all keygen plots from results directory.

    Args:
        results_dir: Directory containing condition subdirectories
        output_dir: Where to save plots
        bit_length: RSA bit length
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all summaries
    results = {}
    for condition_dir in Path(results_dir).glob("*"):
        if not condition_dir.is_dir():
            continue

        summary_path = condition_dir / "summary.json"
        if not summary_path.exists():
            continue

        with open(summary_path) as f:
            results[condition_dir.name.split("_")[0]] = json.load(f)

    if not results:
        print(f"No results found in {results_dir}")
        return

    print(f"Found results for conditions: {list(results.keys())}")

    # Generate plots
    plot_candidates_comparison(
        results,
        output_dir / f"candidates_comparison_{bit_length}bit.png",
        bit_length,
    )

    plot_time_comparison(
        results,
        output_dir / f"time_comparison_{bit_length}bit.png",
        bit_length,
    )

    if len(results) > 1:
        plot_ablation_study(
            results,
            output_dir / f"ablation_study_{bit_length}bit.png",
            bit_length,
        )


__all__ = [
    "plot_candidates_comparison",
    "plot_time_comparison",
    "plot_speedup_with_ci",
    "plot_ablation_study",
    "create_all_keygen_plots",
]
