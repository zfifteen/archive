#!/usr/bin/env python3
"""
Mid-Scale Validation Visualization

Generate plots and visualizations from validation results:
1. Success rate curves vs. bit-length
2. Variance reduction histograms
3. Timing breakdown charts
4. Phase performance analysis

Usage:
    python3 python/mid_scale_visualize.py --input mid_scale_results.csv --output plots/
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("Error: matplotlib and numpy required for visualization")
    print("Install with: pip install matplotlib numpy")
    sys.exit(1)


def load_results(csv_file: str) -> List[Dict]:
    """Load results from CSV file."""
    results = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['N_bits'] = int(row['N_bits'])
            # Robust boolean conversion
            row['success'] = str(row['success']).strip().lower() in ('true', '1')
            row['total_time_sec'] = float(row['total_time_sec'])
            row['embedding_time_sec'] = float(row['embedding_time_sec'])
            row['perturbation_time_sec'] = float(row['perturbation_time_sec'])
            row['sampling_time_sec'] = float(row['sampling_time_sec'])
            row['verification_time_sec'] = float(row['verification_time_sec'])
            row['num_candidates'] = int(row['num_candidates'])
            row['num_samples'] = int(row['num_samples'])
            row['variance_reduction_factor'] = float(row['variance_reduction_factor'])
            
            results.append(row)
    
    return results


def plot_success_rate_vs_bits(results: List[Dict], output_dir: Path):
    """Plot success rate vs. bit length."""
    # Group by bit length
    bit_groups = {}
    for r in results:
        bits = r['N_bits']
        if bits not in bit_groups:
            bit_groups[bits] = []
        bit_groups[bits].append(r['success'])
    
    # Calculate success rates
    bit_lengths = sorted(bit_groups.keys())
    success_rates = []
    for bits in bit_lengths:
        successes = sum(1 for s in bit_groups[bits] if s)
        total = len(bit_groups[bits])
        success_rates.append(100.0 * successes / total)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(bit_lengths, success_rates, 'o-', linewidth=2, markersize=8)
    ax.axhline(y=50, color='r', linestyle='--', label='Target: 50%')
    ax.set_xlabel('Semiprime Bit Length', fontsize=12)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Factorization Success Rate vs. Bit Length', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Save
    output_file = output_dir / 'success_rate_vs_bits.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved {output_file}")


def plot_variance_reduction_histogram(results: List[Dict], output_dir: Path):
    """Plot histogram of variance reduction factors."""
    variance_factors = [r['variance_reduction_factor'] for r in results]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(variance_factors, bins=20, edgecolor='black', alpha=0.7)
    ax.axvline(x=1000, color='r', linestyle='--', linewidth=2, label='Target: 1,000×')
    ax.set_xlabel('Variance Reduction Factor', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('RQMC Variance Reduction Distribution', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add statistics
    mean_vr = np.mean(variance_factors)
    median_vr = np.median(variance_factors)
    ax.text(0.02, 0.98, f'Mean: {mean_vr:.1f}×\nMedian: {median_vr:.1f}×',
            transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    output_file = output_dir / 'variance_reduction_histogram.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved {output_file}")


def plot_timing_breakdown(results: List[Dict], output_dir: Path):
    """Plot stacked bar chart of timing breakdown."""
    # Group by bit length
    bit_groups = {}
    for r in results:
        bits = r['N_bits']
        if bits not in bit_groups:
            bit_groups[bits] = {
                'embedding': [],
                'perturbation': [],
                'sampling': [],
                'verification': []
            }
        bit_groups[bits]['embedding'].append(r['embedding_time_sec'])
        bit_groups[bits]['perturbation'].append(r['perturbation_time_sec'])
        bit_groups[bits]['sampling'].append(r['sampling_time_sec'])
        bit_groups[bits]['verification'].append(r['verification_time_sec'])
    
    # Calculate averages
    bit_lengths = sorted(bit_groups.keys())
    avg_embedding = [np.mean(bit_groups[b]['embedding']) for b in bit_lengths]
    avg_perturbation = [np.mean(bit_groups[b]['perturbation']) for b in bit_lengths]
    avg_sampling = [np.mean(bit_groups[b]['sampling']) for b in bit_lengths]
    avg_verification = [np.mean(bit_groups[b]['verification']) for b in bit_lengths]
    
    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.6
    x = np.arange(len(bit_lengths))
    
    p1 = ax.bar(x, avg_embedding, width, label='Embedding', color='#3498db')
    p2 = ax.bar(x, avg_perturbation, width, bottom=avg_embedding, label='Perturbation', color='#e74c3c')
    p3 = ax.bar(x, avg_sampling, width, 
                bottom=np.array(avg_embedding) + np.array(avg_perturbation),
                label='Sampling', color='#2ecc71')
    p4 = ax.bar(x, avg_verification, width,
                bottom=np.array(avg_embedding) + np.array(avg_perturbation) + np.array(avg_sampling),
                label='Verification', color='#f39c12')
    
    ax.set_xlabel('Semiprime Bit Length', fontsize=12)
    ax.set_ylabel('Average Time (seconds)', fontsize=12)
    ax.set_title('Timing Breakdown by Phase', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{b}b' for b in bit_lengths])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    output_file = output_dir / 'timing_breakdown.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved {output_file}")


def plot_phase_performance(results: List[Dict], output_dir: Path):
    """Plot performance metrics for each phase."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Extract data
    bit_lengths = [r['N_bits'] for r in results]
    
    # Subplot 1: Total time vs bit length
    total_times = [r['total_time_sec'] for r in results]
    ax1.scatter(bit_lengths, total_times, alpha=0.6, s=50)
    ax1.set_xlabel('Bit Length')
    ax1.set_ylabel('Total Time (s)')
    ax1.set_title('Total Runtime vs. Bit Length')
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Variance reduction vs bit length
    variance_factors = [r['variance_reduction_factor'] for r in results]
    ax2.scatter(bit_lengths, variance_factors, alpha=0.6, s=50, color='green')
    ax2.axhline(y=1000, color='r', linestyle='--', label='Target: 1,000×')
    ax2.set_xlabel('Bit Length')
    ax2.set_ylabel('Variance Reduction Factor')
    ax2.set_title('Variance Reduction vs. Bit Length')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Number of candidates vs bit length
    num_candidates = [r['num_candidates'] for r in results]
    ax3.scatter(bit_lengths, num_candidates, alpha=0.6, s=50, color='orange')
    ax3.set_xlabel('Bit Length')
    ax3.set_ylabel('Number of Candidates')
    ax3.set_title('Candidate Count vs. Bit Length')
    ax3.grid(True, alpha=0.3)
    
    # Subplot 4: Success indicators
    success_bits = [r['N_bits'] for r in results if r['success']]
    failure_bits = [r['N_bits'] for r in results if not r['success']]
    ax4.hist([success_bits, failure_bits], bins=10, label=['Success', 'Failure'],
             color=['green', 'red'], alpha=0.7, edgecolor='black')
    ax4.set_xlabel('Bit Length')
    ax4.set_ylabel('Count')
    ax4.set_title('Success/Failure Distribution')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_file = output_dir / 'phase_performance.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved {output_file}")


def generate_summary_report(results: List[Dict], output_dir: Path):
    """Generate text summary report."""
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    success_rate = 100.0 * successful / total if total > 0 else 0.0
    
    avg_time = np.mean([r['total_time_sec'] for r in results])
    avg_variance = np.mean([r['variance_reduction_factor'] for r in results])
    avg_candidates = np.mean([r['num_candidates'] for r in results])
    
    report = f"""
{'='*80}
MID-SCALE VALIDATION SUMMARY REPORT
{'='*80}

Dataset:
  Total targets:                {total}
  Successful factorizations:    {successful}
  Failed factorizations:        {total - successful}
  
Performance:
  Success rate:                 {success_rate:.1f}%
  Average runtime:              {avg_time:.2f}s
  Average variance reduction:   {avg_variance:.1f}×
  Average candidates:           {avg_candidates:.0f}

Metrics by Bit Length:
"""
    
    # Group by bit length
    bit_groups = {}
    for r in results:
        bits = r['N_bits']
        if bits not in bit_groups:
            bit_groups[bits] = []
        bit_groups[bits].append(r)
    
    for bits in sorted(bit_groups.keys()):
        group = bit_groups[bits]
        group_success = sum(1 for r in group if r['success'])
        group_total = len(group)
        group_rate = 100.0 * group_success / group_total
        group_time = np.mean([r['total_time_sec'] for r in group])
        
        report += f"\n  {bits}-bit: {group_success}/{group_total} ({group_rate:.1f}%), avg time: {group_time:.2f}s"
    
    report += f"\n\n{'='*80}\n"
    
    # Save report
    output_file = output_dir / 'summary_report.txt'
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(report)
    print(f"✓ Saved {output_file}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Visualize mid-scale validation results"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Input CSV file with results"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="plots",
        help="Output directory for plots (default: plots/)"
    )
    
    args = parser.parse_args()
    
    # Check input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading results from {input_path}...")
    results = load_results(args.input)
    print(f"✓ Loaded {len(results)} results")
    
    print(f"\nGenerating visualizations...")
    print("-" * 80)
    
    # Generate all plots
    plot_success_rate_vs_bits(results, output_dir)
    plot_variance_reduction_histogram(results, output_dir)
    plot_timing_breakdown(results, output_dir)
    plot_phase_performance(results, output_dir)
    generate_summary_report(results, output_dir)
    
    print("-" * 80)
    print(f"\n✓ All visualizations saved to {output_dir}/")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
