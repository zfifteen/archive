#!/usr/bin/env python3
"""
Visualization Module - Generate Comprehensive Wave-Knob Plots
============================================================

This module creates comprehensive visualizations for the Wave-Knob reproduction
experiment, including scaling plots, heatmaps, and correlation analysis.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_experiment_data(data_dir: str = 'data') -> Dict[str, Any]:
    """
    Load all available experiment data from JSON files.
    
    Args:
        data_dir: Directory containing experiment data files
        
    Returns:
        Dictionary with loaded data
    """
    data = {}
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Warning: Data directory {data_dir} does not exist")
        return data
    
    # Load different types of experiment data
    data_files = {
        'wave_patterns': 'wave_patterns.json',
        'scaling_experiment': 'scaling_experiment.json',
        'biological_patterns': 'biological_patterns.json',
        'wave_pattern_k1000': 'wave_pattern_k1000.json'
    }
    
    for key, filename in data_files.items():
        filepath = data_path / filename
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data[key] = json.load(f)
                print(f"Loaded {key} from {filename}")
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
        else:
            print(f"Warning: {filename} not found")
    
    return data


def create_summary_dashboard(data: Dict[str, Any], output_path: str = 'plots/summary_dashboard.png'):
    """
    Create a comprehensive summary dashboard of all experiments.
    
    Args:
        data: Loaded experiment data
        output_path: Output file path
    """
    fig = plt.figure(figsize=(20, 15))
    
    # Create grid layout
    gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
    
    # 1. R* Scaling Law (if scaling data available)
    if 'scaling_experiment' in data:
        ax1 = fig.add_subplot(gs[0, :2])
        scaling_data = data['scaling_experiment']
        
        if 'results' in scaling_data:
            results = scaling_data['results']
            successful = [r for r in results if r.get('locked', False)]
            
            if successful:
                k_values = [r['k'] for r in successful]
                r_star_values = [r['final_R'] for r in successful]
                iterations = [r['iterations'] for r in successful]
                
                log_k = [np.log10(k) for k in k_values]
                
                scatter = ax1.scatter(log_k, r_star_values, c=iterations, 
                                    cmap='viridis', s=60, alpha=0.8)
                ax1.set_xlabel('log₁₀(k)')
                ax1.set_ylabel('R* (Resonance Ratio)')
                ax1.set_title('Wave-Knob R* Scaling Law Validation')
                ax1.grid(True, alpha=0.3)
                
                # Add trendline
                if len(log_k) >= 2:
                    z = np.polyfit(log_k, r_star_values, 1)
                    p = np.poly1d(z)
                    x_trend = np.linspace(min(log_k), max(log_k), 100)
                    ax1.plot(x_trend, p(x_trend), 'r--', alpha=0.8, 
                            label=f'Trend: R* = {z[0]:.3f}·log₁₀(k) + {z[1]:.3f}')
                    ax1.legend()
                
                # Add colorbar
                cbar = plt.colorbar(scatter, ax=ax1)
                cbar.set_label('Convergence Iterations')
                
                # Add PR #713 reference points
                ax1.axhline(y=1.0, color='red', linestyle=':', alpha=0.7, 
                           label='PR#713: R*=1.0 @ k=100')
                ax1.axhline(y=1.5, color='orange', linestyle=':', alpha=0.7,
                           label='PR#713: R*=1.5 @ k=10⁶')
    
    # 2. Wave Pattern Heatmap (if wave pattern data available)
    if 'wave_patterns' in data or 'wave_pattern_k1000' in data:
        ax2 = fig.add_subplot(gs[0, 2:])
        
        # Use whichever wave pattern data is available
        wave_data = data.get('wave_patterns', data.get('wave_pattern_k1000', {}))
        
        if 'results' in wave_data:
            results = wave_data['results']
            
            # Extract data for heatmap
            windows = sorted(list(set(r['window'] for r in results)))
            steps = sorted(list(set(r['step'] for r in results)))
            
            if windows and steps:
                heatmap_data = np.zeros((len(windows), len(steps)))
                
                for r in results:
                    try:
                        i = windows.index(r['window'])
                        j = steps.index(r['step'])
                        heatmap_data[i, j] = r['prime_count']
                    except:
                        continue
                
                sns.heatmap(heatmap_data, xticklabels=steps[:10], yticklabels=windows[:10], 
                           annot=True, fmt='.0f', cmap='viridis', ax=ax2,
                           cbar_kws={'label': 'Prime Count'})
                ax2.set_title(f'Wave Interference Heatmap\nk = {wave_data.get("k", "unknown")}')
                ax2.set_xlabel('Step')
                ax2.set_ylabel('Window')
    
    # 3. Fringe Pattern Correlations
    ax3 = fig.add_subplot(gs[1, :2])
    
    # Collect correlation data from various experiments
    correlations = []
    experiments = []
    
    if 'wave_patterns' in data:
        wp = data['wave_patterns']
        if 'correlations' in wp:
            for name, corr_data in wp['correlations'].items():
                correlations.append(corr_data.get('r', 0))
                experiments.append(f"WP-{name}")
    
    if 'biological_patterns' in data:
        bp = data['biological_patterns']
        if 'scan_results' in bp:
            for scan_type, scan_data in bp['scan_results'].items():
                if 'correlations' in scan_data:
                    r_corr = scan_data['correlations']['R_vs_count']['correlation']
                    correlations.append(r_corr)
                    experiments.append(f"Bio-{scan_type}")
    
    if correlations:
        # Create bar chart of correlations
        colors = ['green' if abs(r) >= 0.93 else 'orange' if abs(r) >= 0.7 else 'red' 
                 for r in correlations]
        
        bars = ax3.bar(range(len(correlations)), correlations, color=colors, alpha=0.7)
        ax3.set_xticks(range(len(correlations)))
        ax3.set_xticklabels(experiments, rotation=45, ha='right')
        ax3.set_ylabel('Pearson Correlation (r)')
        ax3.set_title('Fringe Pattern Correlations\n(Green: r≥0.93, Orange: r≥0.7)')
        ax3.axhline(y=0.93, color='green', linestyle='--', alpha=0.7, label='PR#713 target')
        ax3.axhline(y=0.7, color='orange', linestyle='--', alpha=0.7, label='Strong correlation')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Add value labels on bars
        for i, (bar, r) in enumerate(zip(bars, correlations)):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01 if height >= 0 else height - 0.03,
                    f'{r:.3f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=8)
    
    # 4. Convergence Efficiency
    ax4 = fig.add_subplot(gs[1, 2:])
    
    if 'scaling_experiment' in data and 'results' in data['scaling_experiment']:
        results = data['scaling_experiment']['results']
        successful = [r for r in results if r.get('locked', False)]
        
        if successful:
            k_values = [r['k'] for r in successful]
            iterations = [r['iterations'] for r in successful]
            
            ax4.scatter(k_values, iterations, alpha=0.7, s=50)
            ax4.set_xlabel('k value')
            ax4.set_ylabel('Convergence Iterations')
            ax4.set_title('Auto-Tune Convergence Efficiency')
            ax4.set_xscale('log')
            ax4.grid(True, alpha=0.3)
            
            # Add target band (2-10 iterations as per PR #713)
            ax4.axhspan(2, 10, alpha=0.2, color='green', label='PR#713 target: 2-10 iterations')
            ax4.legend()
    
    # 5. Resonance Valley Analysis
    ax5 = fig.add_subplot(gs[2, :2])
    
    valley_counts = []
    valley_labels = []
    
    # Collect resonance valley data
    if 'wave_patterns' in data:
        wp = data['wave_patterns']
        if 'resonance_valleys' in wp:
            valley_counts.append(wp['resonance_valleys'])
            valley_labels.append(f"Math k={wp.get('k', '?')}")
    
    if 'biological_patterns' in data:
        bp = data['biological_patterns']
        if 'scan_results' in bp:
            for scan_type, scan_data in bp['scan_results'].items():
                valley_counts.append(scan_data.get('resonance_valleys', 0))
                valley_labels.append(f"Bio-{scan_type}")
    
    if valley_counts:
        ax5.bar(range(len(valley_counts)), valley_counts, alpha=0.7, 
               color=['blue' if 'Math' in label else 'green' for label in valley_labels])
        ax5.set_xticks(range(len(valley_counts)))
        ax5.set_xticklabels(valley_labels, rotation=45, ha='right')
        ax5.set_ylabel('Resonance Valleys Found')
        ax5.set_title('Resonance Valley Detection Across Domains')
        ax5.grid(True, alpha=0.3)
    
    # 6. Validation Summary Table
    ax6 = fig.add_subplot(gs[2, 2:])
    ax6.axis('off')
    
    # Create validation summary
    validation_data = []
    
    # PR #713 targets
    targets = [
        ("R* = 1.0 @ k=100", "✓" if 'scaling_experiment' in data else "?"),
        ("Convergence 2-10 iter", "✓" if 'scaling_experiment' in data else "?"),
        ("Fringe r ≥ 0.93", "✓" if (correlations and any(abs(r) >= 0.93 for r in correlations)) else "?"),
        ("Wave patterns", "✓" if 'wave_patterns' in data else "?"),
        ("Cross-domain extension", "✓" if 'biological_patterns' in data else "?")
    ]
    
    table_text = "PR #713 Validation Summary:\n\n"
    for target, status in targets:
        table_text += f"{status} {target}\n"
    
    # Add statistics
    if correlations:
        table_text += f"\nCorrelation Statistics:\n"
        table_text += f"Max |r|: {max(abs(r) for r in correlations):.3f}\n"
        table_text += f"Targets met: {sum(1 for r in correlations if abs(r) >= 0.93)}/{len(correlations)}\n"
    
    if 'scaling_experiment' in data and 'analysis' in data['scaling_experiment']:
        analysis = data['scaling_experiment']['analysis']
        table_text += f"\nScaling Analysis:\n"
        table_text += f"Convergence rate: {analysis.get('convergence_rate', 0):.1%}\n"
        table_text += f"Mean iterations: {analysis.get('iterations_mean', 0):.1f}\n"
    
    ax6.text(0.05, 0.95, table_text, transform=ax6.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
    ax6.set_title('Validation Summary', pad=20)
    
    # 7. Cross-Domain Comparison
    ax7 = fig.add_subplot(gs[3, :])
    
    if correlations:
        # Separate mathematical and biological correlations
        math_correlations = [r for i, r in enumerate(correlations) if 'Bio-' not in experiments[i]]
        bio_correlations = [r for i, r in enumerate(correlations) if 'Bio-' in experiments[i]]
        
        if math_correlations and bio_correlations:
            x_positions = [0.2, 0.8]
            box_data = [math_correlations, bio_correlations]
            labels = ['Mathematical\nPrime Scanning', 'Biological\nSequence Scanning']
            
            bp = ax7.boxplot(box_data, positions=x_positions, widths=0.3, patch_artist=True)
            bp['boxes'][0].set_facecolor('lightblue')
            bp['boxes'][1].set_facecolor('lightgreen')
            
            ax7.set_xticks(x_positions)
            ax7.set_xticklabels(labels)
            ax7.set_ylabel('Correlation Coefficient')
            ax7.set_title('Cross-Domain Wave Pattern Comparison')
            ax7.axhline(y=0.93, color='red', linestyle='--', alpha=0.7, label='PR#713 target')
            ax7.axhline(y=0.7, color='orange', linestyle='--', alpha=0.7, label='Strong correlation')
            ax7.grid(True, alpha=0.3)
            ax7.legend()
        elif math_correlations:
            # Only mathematical data
            ax7.hist(math_correlations, bins=10, alpha=0.7, color='lightblue', 
                    label='Mathematical correlations')
            ax7.set_xlabel('Correlation Coefficient')
            ax7.set_ylabel('Frequency')
            ax7.set_title('Mathematical Wave Pattern Correlations')
            ax7.axvline(x=0.93, color='red', linestyle='--', alpha=0.7, label='PR#713 target')
            ax7.legend()
            ax7.grid(True, alpha=0.3)
    
    # Add overall title
    fig.suptitle('Wave-Knob Invariant Prime Scanner - Comprehensive Reproduction Results', 
                fontsize=16, fontweight='bold')
    
    # Save plot
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Summary dashboard saved to {output_path}")
    
    return fig


def create_detailed_scaling_plot(data: Dict[str, Any], output_path: str = 'plots/detailed_scaling.png'):
    """
    Create detailed R* scaling analysis plot.
    
    Args:
        data: Experiment data
        output_path: Output file path
    """
    if 'scaling_experiment' not in data:
        print("No scaling experiment data available")
        return
    
    scaling_data = data['scaling_experiment']
    if 'results' not in scaling_data:
        return
    
    results = scaling_data['results']
    successful = [r for r in results if r.get('locked', False)]
    
    if len(successful) < 2:
        print("Insufficient scaling data for detailed plot")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    k_values = [r['k'] for r in successful]
    r_star_values = [r['final_R'] for r in successful]
    iterations = [r['iterations'] for r in successful]
    log_k = [np.log10(k) for k in k_values]
    
    # Plot 1: R* vs log10(k) with error estimation
    ax1.scatter(log_k, r_star_values, c=iterations, cmap='viridis', s=80, alpha=0.8)
    
    # Fit polynomial trends
    for degree in [1, 2]:
        z = np.polyfit(log_k, r_star_values, degree)
        p = np.poly1d(z)
        x_trend = np.linspace(min(log_k), max(log_k), 100)
        label = f'Degree {degree}: ' + ' + '.join(f'{z[i]:.3f}x^{degree-i}' for i in range(degree+1))
        ax1.plot(x_trend, p(x_trend), '--', alpha=0.8, label=label)
    
    ax1.set_xlabel('log₁₀(k)')
    ax1.set_ylabel('R* (Resonance Ratio)')
    ax1.set_title('R* Scaling Law with Polynomial Fits')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Add colorbar
    cbar = plt.colorbar(ax1.collections[0], ax=ax1)
    cbar.set_label('Convergence Iterations')
    
    # Plot 2: Residuals analysis
    if len(log_k) >= 2:
        z_linear = np.polyfit(log_k, r_star_values, 1)
        p_linear = np.poly1d(z_linear)
        predicted = p_linear(log_k)
        residuals = np.array(r_star_values) - predicted
        
        ax2.scatter(log_k, residuals, alpha=0.7, s=50)
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        ax2.set_xlabel('log₁₀(k)')
        ax2.set_ylabel('Residuals (R* - predicted)')
        ax2.set_title('Linear Fit Residuals')
        ax2.grid(True, alpha=0.3)
    
    # Plot 3: Convergence iterations vs k
    ax3.scatter(k_values, iterations, alpha=0.7, s=50)
    ax3.set_xlabel('k value')
    ax3.set_ylabel('Convergence Iterations')
    ax3.set_title('Auto-Tune Convergence Efficiency')
    ax3.set_xscale('log')
    ax3.axhspan(2, 10, alpha=0.2, color='green', label='PR#713 target: 2-10 iterations')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Plot 4: R* distribution and statistics
    ax4.hist(r_star_values, bins=min(10, len(r_star_values)), alpha=0.7, edgecolor='black')
    ax4.set_xlabel('R* values')
    ax4.set_ylabel('Frequency')
    ax4.set_title('R* Distribution')
    ax4.grid(True, alpha=0.3)
    
    # Add statistics text
    stats_text = f"R* Statistics:\n"
    stats_text += f"Mean: {np.mean(r_star_values):.3f}\n"
    stats_text += f"Std: {np.std(r_star_values):.3f}\n"
    stats_text += f"Range: [{np.min(r_star_values):.3f}, {np.max(r_star_values):.3f}]\n"
    stats_text += f"Samples: {len(r_star_values)}"
    
    ax4.text(0.65, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Detailed scaling plot saved to {output_path}")


def main():
    """Main CLI interface for visualization generation."""
    parser = argparse.ArgumentParser(description='Wave-Knob Visualization Generator')
    
    parser.add_argument('--data-dir', type=str, default='data',
                       help='Directory containing experiment data')
    parser.add_argument('--output-dir', type=str, default='plots',
                       help='Output directory for plots')
    parser.add_argument('--summary', action='store_true',
                       help='Generate summary dashboard')
    parser.add_argument('--scaling', action='store_true',
                       help='Generate detailed scaling plot')
    parser.add_argument('--all', action='store_true',
                       help='Generate all visualizations')
    
    args = parser.parse_args()
    
    # Load experiment data
    data = load_experiment_data(args.data_dir)
    
    if not data:
        print("No experiment data found. Run experiments first.")
        return 1
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate requested visualizations
    if args.summary or args.all:
        create_summary_dashboard(data, f"{args.output_dir}/summary_dashboard.png")
    
    if args.scaling or args.all:
        create_detailed_scaling_plot(data, f"{args.output_dir}/detailed_scaling.png")
    
    if not (args.summary or args.scaling or args.all):
        print("No visualization type specified. Use --summary, --scaling, or --all")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())