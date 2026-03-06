#!/usr/bin/env python3
"""
Visualization: Cranley-Patterson QMC Variance Comparison

Generates plots comparing baseline vs CP-rotated QMC sampling.

Author: Z-Sandbox Agent
Date: 2025-11-19
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, List


def load_analysis_results(results_dir: str) -> Dict:
    """Load comparative analysis results."""
    analysis_file = os.path.join(results_dir, 'comparative_analysis.json')
    
    if not os.path.exists(analysis_file):
        raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
    
    with open(analysis_file, 'r') as f:
        return json.load(f)


def plot_variance_comparison(analysis_data: Dict, output_dir: str):
    """
    Plot variance reduction comparison across challenges and treatments.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Cranley-Patterson QMC Variance Reduction Analysis', fontsize=16, fontweight='bold')
    
    challenges = ['RSA-100', 'RSA-129', 'RSA-155']
    treatments = ['CP-Static', 'CP-Adaptive']
    colors = {'CP-Static': '#3498db', 'CP-Adaptive': '#e74c3c'}
    
    # Extract data
    comparisons = analysis_data['comparisons']
    
    # Top-left: Variance reduction factors
    ax = axes[0, 0]
    x_pos = np.arange(len(challenges))
    width = 0.35
    
    for i, treatment in enumerate(treatments):
        reductions = []
        for challenge in challenges:
            if challenge in comparisons and treatment in comparisons[challenge]:
                reductions.append(comparisons[challenge][treatment]['variance']['reduction_factor'])
            else:
                reductions.append(0)
        
        ax.bar(x_pos + i * width, reductions, width, label=treatment, color=colors[treatment], alpha=0.8)
    
    ax.axhline(y=1.3, color='green', linestyle='--', linewidth=2, label='Claimed Min (1.3×)')
    ax.axhline(y=1.8, color='orange', linestyle='--', linewidth=2, label='Claimed Max (1.8×)')
    ax.axhline(y=1.0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    
    ax.set_xlabel('RSA Challenge', fontweight='bold')
    ax.set_ylabel('Variance Reduction Factor', fontweight='bold')
    ax.set_title('Variance Reduction: Baseline vs CP-Rotated', fontweight='bold')
    ax.set_xticks(x_pos + width / 2)
    ax.set_xticklabels(challenges)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Top-right: p-values
    ax = axes[0, 1]
    
    for i, treatment in enumerate(treatments):
        p_values = []
        for challenge in challenges:
            if challenge in comparisons and treatment in comparisons[challenge]:
                p_values.append(comparisons[challenge][treatment]['statistics']['p_value'])
            else:
                p_values.append(1.0)
        
        ax.bar(x_pos + i * width, p_values, width, label=treatment, color=colors[treatment], alpha=0.8)
    
    ax.axhline(y=0.05, color='red', linestyle='--', linewidth=2, label='Significance Threshold (0.05)')
    ax.set_xlabel('RSA Challenge', fontweight='bold')
    ax.set_ylabel('p-value', fontweight='bold')
    ax.set_title('Statistical Significance Test', fontweight='bold')
    ax.set_xticks(x_pos + width / 2)
    ax.set_xticklabels(challenges)
    ax.set_yscale('log')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Bottom-left: Timing overhead
    ax = axes[1, 0]
    
    for i, treatment in enumerate(treatments):
        overheads = []
        for challenge in challenges:
            if challenge in comparisons and treatment in comparisons[challenge]:
                overheads.append(comparisons[challenge][treatment]['timing']['overhead_factor'])
            else:
                overheads.append(1.0)
        
        ax.bar(x_pos + i * width, overheads, width, label=treatment, color=colors[treatment], alpha=0.8)
    
    ax.axhline(y=2.0, color='red', linestyle='--', linewidth=2, label='Threshold (2.0×)')
    ax.axhline(y=1.0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    ax.set_xlabel('RSA Challenge', fontweight='bold')
    ax.set_ylabel('Timing Overhead Factor', fontweight='bold')
    ax.set_title('Computational Overhead', fontweight='bold')
    ax.set_xticks(x_pos + width / 2)
    ax.set_xticklabels(challenges)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Bottom-right: Verdict summary
    ax = axes[1, 1]
    ax.axis('off')
    
    # Summary statistics
    summary = analysis_data['summary']
    verdict_text = f"""
HYPOTHESIS VERDICT

{summary['overall_verdict']}
Confidence: {summary['overall_confidence']}

Total Comparisons: {summary['total_comparisons']}
Falsified: {summary['falsified_count']} ({summary['falsified_percentage']:.1f}%)

Falsification Criteria:
1. Variance reduction < 1.3× (claimed lower bound)
2. p-value > 0.05 (not statistically significant)
3. Computational overhead > 2.0× baseline

Result: If ANY criterion met → FALSIFIED
    """
    
    ax.text(0.5, 0.5, verdict_text, 
            ha='center', va='center',
            fontsize=11, family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save
    output_file = os.path.join(output_dir, 'comparison_plot.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved plot: {output_file}")
    
    plt.close()


def plot_variance_distributions(analysis_data: Dict, results_dir: str, output_dir: str):
    """
    Plot variance distributions for each challenge.
    """
    # Load baseline and CP results
    challenges = ['RSA-100', 'RSA-129', 'RSA-155']
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Variance Distributions: Baseline vs Cranley-Patterson', fontsize=14, fontweight='bold')
    
    for idx, challenge in enumerate(challenges):
        ax = axes[idx]
        
        # Load data
        baseline_file = os.path.join(results_dir, f'baseline_{challenge.lower()}.json')
        cp_static_file = os.path.join(results_dir, f'cp_static_{challenge.lower()}.json')
        cp_adaptive_file = os.path.join(results_dir, f'cp_adaptive_{challenge.lower()}.json')
        
        baseline_vars = []
        cp_static_vars = []
        cp_adaptive_vars = []
        
        if os.path.exists(baseline_file):
            with open(baseline_file, 'r') as f:
                data = json.load(f)
                baseline_vars = [trial['variance'] for trial in data['trials']]
        
        if os.path.exists(cp_static_file):
            with open(cp_static_file, 'r') as f:
                data = json.load(f)
                cp_static_vars = [trial['variance'] for trial in data['trials']]
        
        if os.path.exists(cp_adaptive_file):
            with open(cp_adaptive_file, 'r') as f:
                data = json.load(f)
                cp_adaptive_vars = [trial['variance'] for trial in data['trials']]
        
        # Plot distributions
        if baseline_vars:
            # Check if there's any variance
            if np.std(baseline_vars) > 1e-10:
                ax.hist(baseline_vars, bins=15, alpha=0.6, label='Baseline', color='gray', edgecolor='black')
            else:
                # All values identical - plot as single bar
                ax.axvline(np.mean(baseline_vars), color='gray', linewidth=3, label='Baseline (constant)', alpha=0.6)
        
        if cp_static_vars:
            if np.std(cp_static_vars) > 1e-10:
                ax.hist(cp_static_vars, bins=15, alpha=0.6, label='CP-Static', color='#3498db', edgecolor='black')
            else:
                ax.axvline(np.mean(cp_static_vars), color='#3498db', linewidth=3, label='CP-Static (constant)', alpha=0.6)
        
        if cp_adaptive_vars:
            if np.std(cp_adaptive_vars) > 1e-10:
                ax.hist(cp_adaptive_vars, bins=15, alpha=0.6, label='CP-Adaptive', color='#e74c3c', edgecolor='black')
            else:
                ax.axvline(np.mean(cp_adaptive_vars), color='#e74c3c', linewidth=3, label='CP-Adaptive (constant)', alpha=0.6)
        
        ax.set_xlabel('Variance', fontweight='bold')
        ax.set_ylabel('Frequency', fontweight='bold')
        ax.set_title(f'{challenge}', fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'variance_distributions.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved plot: {output_file}")
    
    plt.close()


def main():
    """Generate all visualizations."""
    results_dir = "../results"
    output_dir = results_dir
    
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    # Load analysis data
    try:
        analysis_data = load_analysis_results(results_dir)
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("  Run comparative_analysis.py first to generate analysis results.")
        return
    
    # Generate plots
    print("\nGenerating comparison plot...")
    plot_variance_comparison(analysis_data, output_dir)
    
    print("\nGenerating distribution plots...")
    plot_variance_distributions(analysis_data, results_dir, output_dir)
    
    print("\n✓ All visualizations generated successfully")


if __name__ == "__main__":
    main()
