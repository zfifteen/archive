#!/usr/bin/env python3
"""
Visualize RSA prime factors on 2D grid
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analyze_and_visualize(csv_file):
    """Load and visualize prime factor grid data"""

    # Load data
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} prime factors from {csv_file}")
    print(f"Prime range: [{df['N'].min()}, {df['N'].max()}]")
    print(f"Grid range: x=[{df['x'].min()}, {df['x'].max()}], y=[{df['y'].min()}, {df['y'].max()}]")

    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot 1: Full grid scatter
    ax1.scatter(df['x'], df['y'], alpha=0.7, s=50, c='red', edgecolors='black')
    ax1.set_xlabel('x coordinate')
    ax1.set_ylabel('y coordinate')
    ax1.set_title(f'RSA Prime Factors on Grid (10^7 scale)\n{len(df)} factors from 20 RSA keys')
    ax1.grid(True, alpha=0.3)

    # Add annotations for clustering analysis
    unique_x = df['x'].unique()
    for x_val in unique_x:
        count = len(df[df['x'] == x_val])
        if count > 1:
            y_vals = df[df['x'] == x_val]['y']
            ax1.annotate(f'{count} factors',
                        xy=(x_val, y_vals.mean()),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8, alpha=0.7)

    # Plot 2: Factor distribution by x coordinate
    x_counts = df.groupby('x').size()
    ax2.bar(x_counts.index, x_counts.values, alpha=0.7, color='blue', edgecolor='black')
    ax2.set_xlabel('x coordinate (N // 10^7)')
    ax2.set_ylabel('Number of prime factors')
    ax2.set_title('Prime Factor Clustering by x-coordinate')
    ax2.grid(True, alpha=0.3)

    # Add value labels on bars
    for i, count in enumerate(x_counts.values):
        ax2.text(x_counts.index[i], count + 0.1, str(count),
                ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig('rsa_prime_factor_visualization.png', dpi=150, bbox_inches='tight')
    plt.show()

    # Analysis summary
    print("\n" + "="*50)
    print("CLUSTERING ANALYSIS")
    print("="*50)

    print(f"Total unique x-coordinates: {len(unique_x)}")
    print(f"Max factors per x-coordinate: {x_counts.max()}")
    print(f"X-coordinates with multiple factors:")

    for x_val in sorted(unique_x):
        count = x_counts[x_val]
        if count > 1:
            factors_at_x = df[df['x'] == x_val]['N'].tolist()
            print(f"  x={x_val}: {count} factors - {factors_at_x}")

    # Check for potential patterns
    clustering_ratio = len(df) / len(unique_x)
    print(f"\nClustering ratio: {clustering_ratio:.2f} (factors per unique x-coordinate)")

    if clustering_ratio > 1.5:
        print("⚠️  SIGNIFICANT CLUSTERING DETECTED - Some x-coordinates have multiple prime factors")
    else:
        print("✓  Factors appear well-distributed across x-coordinates")

if __name__ == "__main__":
    analyze_and_visualize("rsa_prime_grid.csv")