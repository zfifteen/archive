#!/usr/bin/env python3
"""
Visualization utilities for cross-linking 5D embeddings to quantum chaos
Creates plots showing correlations and cross-domain linkages
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from cross_link_5d_quantum_analysis import CrossLink5DQuantumAnalysis

def create_correlation_matrix_plot(correlation_results, save_path='correlation_matrix.png'):
    """
    Create heatmap of correlation matrix for all computed correlations
    """
    # Extract correlation values
    correlations = {}
    for key, result in correlation_results.items():
        if 'correlation' in result:
            correlations[key] = result['correlation']
    
    # Create correlation matrix (correlations with themselves = 1)
    keys = list(correlations.keys())
    n = len(keys)
    matrix = np.eye(n)
    
    # Fill with actual correlation values where available
    for i, key in enumerate(keys):
        matrix[i, i] = correlations[key]
    
    # Create heatmap
    plt.figure(figsize=(12, 8))
    
    # Custom labels for better readability
    labels = []
    for key in keys:
        if 'reference' in key:
            labels.append('φ-modular\n(target)')
        elif 'gue_vs_5d' in key:
            labels.append('GUE ↔ 5D\ncurvatures')
        elif 'log_curvature' in key:
            labels.append('Log curvature\ncascade')
        elif 'enhanced' in key:
            labels.append('Enhanced\nspacings')
        else:
            labels.append(key.replace('_', '\n'))
    
    # Create diagonal heatmap showing correlation strengths
    diag_values = [correlations[key] for key in keys]
    diag_matrix = np.diag(diag_values)
    
    sns.heatmap(diag_matrix, 
                annot=True, 
                fmt='.3f',
                xticklabels=labels,
                yticklabels=labels,
                cmap='RdBu_r',
                center=0,
                square=True,
                linewidths=0.5,
                cbar_kws={'label': 'Correlation Coefficient'})
    
    plt.title('Cross-Domain Correlation Strengths\n5D Embeddings ↔ Quantum Chaos', 
              fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Correlation matrix saved to {save_path}")
    
    return save_path

def create_5d_embedding_scatter(embeddings_5d, save_path='5d_embedding_scatter.png'):
    """
    Create 3D scatter plot of 5D embeddings (x, y, z coordinates)
    """
    fig = plt.figure(figsize=(15, 5))
    
    # Extract coordinates
    x, y, z = embeddings_5d['x'], embeddings_5d['y'], embeddings_5d['z']
    u, kappa = embeddings_5d['u'], embeddings_5d['kappa']
    
    # Plot 1: 3D scatter (x, y, z)
    ax1 = fig.add_subplot(131, projection='3d')
    scatter = ax1.scatter(x, y, z, c=kappa, cmap='viridis', alpha=0.6, s=20)
    ax1.set_xlabel('X (a·cos(θ_D))')
    ax1.set_ylabel('Y (a·sin(θ_E))')
    ax1.set_zlabel('Z (F/e²)')
    ax1.set_title('5D Helical Embeddings\n(colored by κ)')
    plt.colorbar(scatter, ax=ax1, shrink=0.5, label='κ(n)')
    
    # Plot 2: u vs kappa scatter
    ax2 = fig.add_subplot(132)
    ax2.scatter(kappa, u, alpha=0.6, s=20, c='blue')
    ax2.set_xlabel('Curvature κ(n)')
    ax2.set_ylabel('U coordinate (log(1+|O|))')
    ax2.set_title('5D U-coordinate vs Curvature')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Helical projection (x, y)
    ax3 = fig.add_subplot(133)
    scatter3 = ax3.scatter(x, y, c=u, cmap='plasma', alpha=0.7, s=25)
    ax3.set_xlabel('X (a·cos(θ_D))')
    ax3.set_ylabel('Y (a·sin(θ_E))')
    ax3.set_title('Helical Structure\n(colored by U)')
    ax3.set_aspect('equal')
    plt.colorbar(scatter3, ax=ax3, label='U coordinate')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"5D embedding scatter plot saved to {save_path}")
    
    return save_path

def create_gue_deviation_analysis(zero_spacings, gue_deviations, 
                                save_path='gue_deviation_analysis.png'):
    """
    Create plots showing GUE deviations and spacing statistics
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Zero spacing histogram
    axes[0,0].hist(zero_spacings, bins=30, alpha=0.7, color='blue', density=True)
    axes[0,0].set_xlabel('Zero Spacing')
    axes[0,0].set_ylabel('Density')
    axes[0,0].set_title('Zeta Zero Spacing Distribution')
    axes[0,0].grid(True, alpha=0.3)
    
    # Plot 2: GUE deviations
    axes[0,1].plot(gue_deviations, color='red', alpha=0.7)
    axes[0,1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[0,1].set_xlabel('Index')
    axes[0,1].set_ylabel('GUE Deviation')
    axes[0,1].set_title('GUE Statistical Deviations')
    axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: Spacing vs deviation scatter
    if len(zero_spacings) == len(gue_deviations):
        axes[1,0].scatter(zero_spacings, gue_deviations, alpha=0.6, s=20)
        axes[1,0].set_xlabel('Zero Spacing')
        axes[1,0].set_ylabel('GUE Deviation')
        axes[1,0].set_title('Spacings vs GUE Deviations')
    else:
        min_len = min(len(zero_spacings), len(gue_deviations))
        axes[1,0].scatter(zero_spacings[:min_len], gue_deviations[:min_len], 
                         alpha=0.6, s=20)
        axes[1,0].set_xlabel('Zero Spacing')
        axes[1,0].set_ylabel('GUE Deviation')
        axes[1,0].set_title(f'Spacings vs GUE Deviations (n={min_len})')
    axes[1,0].grid(True, alpha=0.3)
    
    # Plot 4: Cumulative GUE deviation
    cumulative_dev = np.cumsum(gue_deviations)
    axes[1,1].plot(cumulative_dev, color='green', alpha=0.8)
    axes[1,1].set_xlabel('Index')
    axes[1,1].set_ylabel('Cumulative GUE Deviation')
    axes[1,1].set_title('Cumulative GUE Deviation')
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"GUE deviation analysis saved to {save_path}")
    
    return save_path

def create_cross_domain_linkage_plot(correlation_results, embeddings_5d, 
                                   zero_spacings, gue_deviations,
                                   save_path='cross_domain_linkage.png'):
    """
    Create comprehensive plot showing cross-domain linkages
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Main correlation values
    ref_corr = correlation_results.get('reference_correlation', {}).get('correlation', 0)
    gue_corr = correlation_results.get('gue_vs_5d_curvatures', {}).get('correlation', 0)
    cascade_corr = correlation_results.get('log_curvature_cascade', {}).get('correlation', 0)
    
    # Plot 1: Correlation strength radar chart
    ax1 = fig.add_subplot(231, projection='polar')
    correlations = [abs(ref_corr), abs(gue_corr), abs(cascade_corr)]
    labels = ['φ-modular', 'GUE-5D', 'Cascade']
    angles = np.linspace(0, 2*np.pi, len(correlations), endpoint=False)
    
    correlations += correlations[:1]  # Complete the circle
    angles = np.append(angles, angles[0])
    
    ax1.plot(angles, correlations, 'o-', linewidth=2, color='red')
    ax1.fill(angles, correlations, alpha=0.25, color='red')
    ax1.set_ylim(0, 1)
    ax1.set_title('Correlation Strengths\n(Absolute Values)', pad=20)
    ax1.set_thetagrids(angles[:-1] * 180/np.pi, labels)
    
    # Plot 2: 5D embedding helical structure
    ax2 = fig.add_subplot(232, projection='3d')
    x, y, z = embeddings_5d['x'][:100], embeddings_5d['y'][:100], embeddings_5d['z'][:100]
    kappa = embeddings_5d['kappa'][:100]
    
    scatter = ax2.scatter(x, y, z, c=kappa, cmap='viridis', s=30, alpha=0.7)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y') 
    ax2.set_zlabel('Z')
    ax2.set_title('5D Helical Structure\n(100 points)')
    
    # Plot 3: Zero spacings time series
    ax3 = fig.add_subplot(233)
    ax3.plot(zero_spacings[:100], color='blue', alpha=0.8, linewidth=1)
    ax3.set_xlabel('Index')
    ax3.set_ylabel('Zero Spacing')
    ax3.set_title('Zeta Zero Spacings\n(first 100)')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: GUE deviations vs 5D curvatures
    ax4 = fig.add_subplot(234)
    min_len = min(len(gue_deviations), len(embeddings_5d['kappa']))
    ax4.scatter(embeddings_5d['kappa'][:min_len], gue_deviations[:min_len], 
               alpha=0.6, s=20, color='red')
    ax4.set_xlabel('5D Curvature κ(n)')
    ax4.set_ylabel('GUE Deviation')
    ax4.set_title(f'GUE ↔ 5D Linkage\nr = {gue_corr:.3f}')
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Prime vs composite variance visualization
    variance_info = correlation_results.get('helical_variance', {})
    prime_var = variance_info.get('prime_variance', 0)
    composite_var = variance_info.get('composite_variance', 0)
    
    ax5 = fig.add_subplot(235)
    categories = ['Primes', 'Composites']
    variances = [prime_var, composite_var]
    colors = ['gold', 'silver']
    
    bars = ax5.bar(categories, variances, color=colors, alpha=0.7)
    ax5.set_ylabel('Variance of U-coordinate')
    ax5.set_title(f'Prime/Composite Discrimination\nRatio = {prime_var/composite_var:.2f}')
    ax5.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, var in zip(bars, variances):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{var:.3f}', ha='center', va='bottom')
    
    # Plot 6: Summary linkage indicator
    ax6 = fig.add_subplot(236)
    
    # Linkage strength indicators
    linkage_names = ['5D ↔ Quantum\nChaos', 'Prime-Zero\nSpacings', 'Curvature\nCascades']
    linkage_strengths = [abs(gue_corr), abs(ref_corr), abs(cascade_corr)]
    
    # Color code by strength
    colors = ['green' if s > 0.3 else 'orange' if s > 0.1 else 'red' for s in linkage_strengths]
    
    bars = ax6.bar(linkage_names, linkage_strengths, color=colors, alpha=0.7)
    ax6.set_ylabel('Linkage Strength |r|')
    ax6.set_title('Cross-Domain Linkage Summary')
    ax6.set_ylim(0, 1)
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Add threshold lines
    ax6.axhline(y=0.3, color='green', linestyle='--', alpha=0.5, label='Strong')
    ax6.axhline(y=0.1, color='orange', linestyle='--', alpha=0.5, label='Moderate')
    ax6.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Cross-domain linkage plot saved to {save_path}")
    
    return save_path

def generate_all_visualizations(analyzer, output_dir='./'):
    """
    Generate all visualization plots for the cross-linking analysis
    """
    print("\n=== Generating Visualizations ===")
    
    # Ensure analysis is complete
    if not analyzer.correlation_results:
        print("Running correlation analysis...")
        analyzer.compute_cross_correlations()
    
    saved_plots = []
    
    try:
        # 1. Correlation matrix
        plot1 = create_correlation_matrix_plot(
            analyzer.correlation_results, 
            f'{output_dir}correlation_matrix.png'
        )
        saved_plots.append(plot1)
        
        # 2. 5D embedding scatter
        plot2 = create_5d_embedding_scatter(
            analyzer.embeddings_5d,
            f'{output_dir}5d_embedding_scatter.png'
        )
        saved_plots.append(plot2)
        
        # 3. GUE deviation analysis
        plot3 = create_gue_deviation_analysis(
            analyzer.zero_spacings,
            analyzer.gue_deviations,
            f'{output_dir}gue_deviation_analysis.png'
        )
        saved_plots.append(plot3)
        
        # 4. Cross-domain linkage comprehensive plot
        plot4 = create_cross_domain_linkage_plot(
            analyzer.correlation_results,
            analyzer.embeddings_5d,
            analyzer.zero_spacings,
            analyzer.gue_deviations,
            f'{output_dir}cross_domain_linkage.png'
        )
        saved_plots.append(plot4)
        
        print(f"\nGenerated {len(saved_plots)} visualization plots:")
        for plot in saved_plots:
            print(f"  - {plot}")
        
        return saved_plots
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()
        return []

def main_visualization_demo():
    """
    Demonstration of visualization capabilities
    """
    print("Cross-Link 5D Quantum Analysis - Visualization Demo")
    print("=" * 55)
    
    # Run analysis with moderate parameters
    analyzer = CrossLink5DQuantumAnalysis(M=150, N_primes=1000, N_seq=500)
    
    # Execute full analysis
    analyzer.compute_zeta_zeros_and_spacings()
    analyzer.compute_prime_curvatures_and_shifts()
    analyzer.generate_5d_embeddings()
    analyzer.compute_gue_deviations()
    analyzer.compute_cross_correlations()
    
    # Generate all visualizations
    plots = generate_all_visualizations(analyzer)
    
    # Generate summary
    summary = analyzer.generate_summary_report()
    
    print(f"\nVisualization demo completed!")
    print(f"Generated {len(plots)} plots showing cross-domain linkages")
    
    return analyzer, plots

if __name__ == "__main__":
    analyzer, plots = main_visualization_demo()