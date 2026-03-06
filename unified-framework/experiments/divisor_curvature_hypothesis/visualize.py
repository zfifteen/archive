#!/usr/bin/env python3
"""
Visualization script for divisor-based curvature hypothesis experiment.
Creates plots to illustrate the separation between primes and composites.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Skipping visualizations.")


def create_visualizations(results: Dict[str, Any], output_dir: Path):
    """Create visualization plots from experiment results."""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available. Cannot create visualizations.")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract data
    primes_data = results['data']['primes']
    # Note: composites are truncated in JSON, so we'll use statistics instead
    
    prime_stats = results['statistics']['primes']
    composite_stats = results['statistics']['composites']
    bootstrap = results['bootstrap']
    
    # Figure 1: Curvature distribution comparison
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Divisor-Based Curvature Hypothesis: Results Summary', fontsize=16, fontweight='bold')
    
    # Plot 1: Prime curvatures
    ax1 = axes[0, 0]
    prime_ns = [n for n, _ in primes_data]
    prime_kappas = [k for _, k in primes_data]
    ax1.scatter(prime_ns, prime_kappas, c='blue', alpha=0.6, s=50, label='Primes')
    ax1.axhline(y=prime_stats['mean'], color='blue', linestyle='--', linewidth=2, 
                label=f'Mean κ = {prime_stats["mean"]:.3f}')
    ax1.axhline(y=0.74, color='red', linestyle=':', linewidth=2, label='Target κ = 0.74')
    ax1.set_xlabel('n', fontsize=12)
    ax1.set_ylabel('κ(n)', fontsize=12)
    ax1.set_title('Prime Number Curvatures', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Statistics comparison
    ax2 = axes[0, 1]
    categories = ['Primes', 'Composites']
    means = [prime_stats['mean'], composite_stats['mean']]
    targets = [0.74, 2.25]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, means, width, label='Observed', color=['blue', 'orange'], alpha=0.7)
    bars2 = ax2.bar(x + width/2, targets, width, label='Target', color=['lightblue', 'lightsalmon'], alpha=0.7)
    
    ax2.set_ylabel('Mean κ', fontsize=12)
    ax2.set_title('Mean Curvature Comparison', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=9)
    
    # Plot 3: Bootstrap confidence intervals
    ax3 = axes[1, 0]
    prime_ci = bootstrap['prime_ci']
    composite_ci = bootstrap['composite_ci']
    
    y_pos = np.arange(len(categories))
    ci_widths_low = [
        means[0] - prime_ci[0],
        means[1] - composite_ci[0]
    ]
    ci_widths_high = [
        prime_ci[1] - means[0],
        composite_ci[1] - means[1]
    ]
    
    ax3.barh(y_pos, means, color=['blue', 'orange'], alpha=0.7, label='Mean')
    ax3.errorbar(means, y_pos, 
                xerr=[ci_widths_low, ci_widths_high],
                fmt='none', ecolor='black', capsize=5, capthick=2, label='95% CI')
    
    ax3.set_xlabel('κ', fontsize=12)
    ax3.set_title('Bootstrap Confidence Intervals (95%)', fontsize=13, fontweight='bold')
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(categories)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, axis='x')
    
    # Plot 4: Classification performance
    ax4 = axes[1, 1]
    classification = results['classification']
    accuracy_percent = classification['accuracy_percent']
    target_accuracy = 83.0
    
    metrics = ['Observed\nAccuracy', 'Target\nAccuracy']
    values = [accuracy_percent, target_accuracy]
    colors = ['green' if accuracy_percent >= target_accuracy else 'orange', 'lightgreen']
    
    bars = ax4.bar(metrics, values, color=colors, alpha=0.7)
    ax4.set_ylabel('Accuracy (%)', fontsize=12)
    ax4.set_title('Classification Accuracy', fontsize=13, fontweight='bold')
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add optimal threshold info
    threshold_text = f"Optimal threshold: κ = {classification['optimal_threshold']:.3f}"
    ax4.text(0.5, 0.95, threshold_text, transform=ax4.transAxes,
            ha='center', va='top', fontsize=10, 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    output_file = output_dir / 'curvature_analysis.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved visualization: {output_file}")
    plt.close()
    
    # Figure 2: Golden ratio equidistribution
    golden = results['golden_ratio']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Golden Ratio (φ) mod 1 Equidistribution Test', fontsize=16, fontweight='bold')
    
    # Plot 1: Histogram of bins
    ax1.bar(range(1, golden['n_bins'] + 1), golden['bins'], color='gold', alpha=0.7, edgecolor='black')
    ax1.axhline(y=golden['expected_per_bin'], color='red', linestyle='--', linewidth=2,
                label=f'Expected: {golden["expected_per_bin"]:.1f}')
    ax1.set_xlabel('Bin Number', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_title(f'Distribution in {golden["n_bins"]} Bins (n={golden["n_samples"]} samples)', 
                  fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Statistics
    ax2.axis('off')
    stats_text = f"""
Golden Ratio Equidistribution Test Results
────────────────────────────────────────
Samples: {golden['n_samples']}
Bins: {golden['n_bins']}
Expected per bin: {golden['expected_per_bin']:.1f}

Chi-square statistic: {golden['chi_square']:.3f}
Bin standard deviation: {golden['std_dev']:.3f}

Sequence mean: {golden['sequence_mean']:.4f}
Expected mean: 0.5000
Sequence std: {golden['sequence_std']:.4f}

Interpretation:
The golden ratio φ = (1+√5)/2 generates
an equidistributed sequence mod 1.
Low chi-square indicates good uniformity.
    """
    ax2.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
            verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    output_file = output_dir / 'golden_ratio_test.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved visualization: {output_file}")
    plt.close()
    
    print("\nAll visualizations created successfully!")


def main():
    parser = argparse.ArgumentParser(
        description="Create visualizations from experiment results"
    )
    parser.add_argument("--input", type=Path, default=Path("results.json"),
                       help="Input JSON results file")
    parser.add_argument("--output-dir", type=Path, default=Path("plots"),
                       help="Output directory for plots")
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Results file not found: {args.input}")
        print("Run the experiment first: python run_experiment.py --output results.json")
        return 1
    
    with args.input.open('r') as f:
        results = json.load(f)
    
    create_visualizations(results, args.output_dir)
    
    return 0


if __name__ == "__main__":
    exit(main())
