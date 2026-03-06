"""
Visualization and Export for Quantum Topology Analysis

This module provides visualization tools for quantum-topological analysis
of biological sequences, with optional Plotly integration for interactive
visualizations and Matplotlib fallback for static plots.

Key Functions:
- export_helical_visualization: Create 3D helical plots
- plot_quantum_correlations: Visualize correlation patterns
- export_bell_violation_analysis: Bell violation visualization

Dependencies:
- matplotlib (required)
- plotly (optional, for interactive plots)
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings

# Optional Plotly import
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from .helical import generate_helical_coordinates, compute_quantum_correlations
from .alignment import compute_bell_violation


def export_helical_visualization(seq, k=0.3, output_format='html', filename=None, 
                                interactive=True, hypothetical=True):
    """
    Create 3D helical visualization of sequence geodesic coordinates.
    
    Args:
        seq: Bio.Seq object
        k: Curvature parameter
        output_format: 'html', 'png', 'svg'
        filename: Output filename (auto-generated if None)
        interactive: Use Plotly if available
        hypothetical: Mark as experimental
        
    Returns:
        Dictionary containing plot data and metadata
    """
    if hypothetical:
        print("Warning: Helical visualization represents experimental quantum-geodesic mapping.")
    
    # Generate helical coordinates
    coords = generate_helical_coordinates(seq, k=k, hypothetical=False)
    x, y, z = coords['x'], coords['y'], coords['z']
    
    # Color mapping for bases
    base_colors = {'A': 'red', 'T': 'blue', 'C': 'green', 'G': 'orange'}
    colors = [base_colors.get(str(base).upper(), 'gray') for base in seq]
    
    if interactive and PLOTLY_AVAILABLE:
        return _create_plotly_helix(x, y, z, seq, colors, coords, filename, output_format)
    else:
        return _create_matplotlib_helix(x, y, z, seq, colors, coords, filename, output_format)


def _create_plotly_helix(x, y, z, seq, colors, coords, filename, output_format):
    """Create interactive Plotly 3D helix visualization."""
    
    # Create 3D scatter plot
    fig = go.Figure(data=go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers+lines',
        marker=dict(
            size=8,
            color=colors,
            opacity=0.8,
        ),
        line=dict(
            color='lightblue',
            width=2
        ),
        text=[f"Position: {i+1}, Base: {base}" for i, base in enumerate(seq)],
        hovertemplate="<b>%{text}</b><br>" +
                     "X: %{x:.3f}<br>" +
                     "Y: %{y:.3f}<br>" +
                     "Z: %{z:.3f}<br>" +
                     "<extra></extra>"
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Quantum-Helical Visualization (k={coords['metadata']['curvature_k']:.3f})",
        scene=dict(
            xaxis_title="X (φ-scaled)",
            yaxis_title="Y (φ-scaled)", 
            zaxis_title="Z (helical progression)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        width=800,
        height=600,
        annotations=[
            dict(
                text="⚠️ Experimental/Hypothetical Quantum-Geodesic Transform",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.02, xanchor='center', yanchor='bottom',
                font=dict(color="red", size=10)
            )
        ]
    )
    
    # Save if filename provided
    if filename:
        if output_format == 'html':
            fig.write_html(filename)
        elif output_format == 'png':
            fig.write_image(filename)
        elif output_format == 'svg':
            fig.write_image(filename)
    
    return {
        'figure': fig,
        'coordinates': coords,
        'visualization_type': 'interactive_plotly',
        'output_format': output_format,
        'filename': filename,
        'hypothetical': True
    }


def _create_matplotlib_helix(x, y, z, seq, colors, coords, filename, output_format):
    """Create static Matplotlib 3D helix visualization."""
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot helical structure
    ax.plot(x, y, z, 'b-', alpha=0.6, linewidth=1)
    
    # Color-code bases
    unique_bases = list(set(str(base).upper() for base in seq))
    base_colors = {'A': 'red', 'T': 'blue', 'C': 'green', 'G': 'orange'}
    
    for base in unique_bases:
        mask = [str(b).upper() == base for b in seq]
        if any(mask):
            ax.scatter(x[mask], y[mask], z[mask], 
                      c=base_colors.get(base, 'gray'), 
                      label=f'Base {base}', s=50, alpha=0.8)
    
    # Labels and title
    ax.set_xlabel('X (φ-scaled)')
    ax.set_ylabel('Y (φ-scaled)')
    ax.set_zlabel('Z (helical progression)')
    ax.set_title(f'Quantum-Helical Visualization (k={coords["metadata"]["curvature_k"]:.3f})')
    ax.legend()
    
    # Add experimental warning
    fig.suptitle('⚠️ Experimental/Hypothetical Quantum-Geodesic Transform', 
                color='red', fontsize=10, y=0.02)
    
    plt.tight_layout()
    
    # Save if filename provided
    if filename:
        plt.savefig(filename, format=output_format, dpi=300, bbox_inches='tight')
    
    return {
        'figure': fig,
        'axes': ax,
        'coordinates': coords,
        'visualization_type': 'static_matplotlib',
        'output_format': output_format,
        'filename': filename,
        'hypothetical': True
    }


def plot_quantum_correlations(seq, window_size=10, k=0.3, filename=None, 
                             interactive=True, hypothetical=True):
    """
    Visualize quantum correlation patterns along sequence.
    
    Args:
        seq: Bio.Seq object
        window_size: Size of correlation window
        k: Curvature parameter
        filename: Output filename
        interactive: Use Plotly if available
        hypothetical: Mark as experimental
        
    Returns:
        Plot object and correlation data
    """
    if hypothetical:
        print("Warning: Quantum correlation analysis is experimental/hypothetical.")
    
    # Compute quantum correlations
    corr_data = compute_quantum_correlations(seq, window_size=window_size, k=k, hypothetical=False)
    
    correlations = corr_data['correlations']
    entangled_regions = corr_data['entangled_regions']
    positions = np.arange(1, len(correlations) + 1)
    
    if interactive and PLOTLY_AVAILABLE:
        return _create_plotly_correlations(correlations, entangled_regions, positions, 
                                         corr_data, filename)
    else:
        return _create_matplotlib_correlations(correlations, entangled_regions, positions, 
                                             corr_data, filename)


def _create_plotly_correlations(correlations, entangled_regions, positions, corr_data, filename):
    """Create interactive Plotly correlation plot."""
    
    fig = go.Figure()
    
    # Main correlation trace
    fig.add_trace(go.Scatter(
        x=positions,
        y=correlations,
        mode='lines+markers',
        name='Quantum Correlations',
        line=dict(color='blue', width=2),
        marker=dict(size=4)
    ))
    
    # Highlight entangled regions
    if np.any(entangled_regions):
        entangled_x = positions[entangled_regions]
        entangled_y = correlations[entangled_regions]
        
        fig.add_trace(go.Scatter(
            x=entangled_x,
            y=entangled_y,
            mode='markers',
            name='Potential Entanglement',
            marker=dict(color='red', size=8, symbol='diamond')
        ))
    
    # Add threshold line
    threshold = corr_data['correlation_threshold']
    fig.add_hline(y=threshold, line_dash="dash", line_color="red", 
                  annotation_text=f"Entanglement Threshold: {threshold:.3f}")
    
    # Update layout
    fig.update_layout(
        title="Quantum Correlation Analysis",
        xaxis_title="Sequence Position",
        yaxis_title="Correlation Coefficient",
        showlegend=True,
        annotations=[
            dict(
                text="⚠️ Experimental/Hypothetical Quantum Analysis",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.02, xanchor='center', yanchor='bottom',
                font=dict(color="red", size=10)
            )
        ]
    )
    
    if filename:
        fig.write_html(filename)
    
    return {
        'figure': fig,
        'correlation_data': corr_data,
        'visualization_type': 'interactive_plotly'
    }


def _create_matplotlib_correlations(correlations, entangled_regions, positions, corr_data, filename):
    """Create static Matplotlib correlation plot."""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot correlations
    ax.plot(positions, correlations, 'b-', linewidth=2, label='Quantum Correlations')
    ax.scatter(positions, correlations, c='blue', s=20, alpha=0.6)
    
    # Highlight entangled regions
    if np.any(entangled_regions):
        entangled_x = positions[entangled_regions]
        entangled_y = correlations[entangled_regions]
        ax.scatter(entangled_x, entangled_y, c='red', s=50, marker='D', 
                  label='Potential Entanglement', alpha=0.8)
    
    # Add threshold line
    threshold = corr_data['correlation_threshold']
    ax.axhline(y=threshold, color='red', linestyle='--', alpha=0.7,
              label=f'Entanglement Threshold: {threshold:.3f}')
    
    # Labels and formatting
    ax.set_xlabel('Sequence Position')
    ax.set_ylabel('Correlation Coefficient')
    ax.set_title('Quantum Correlation Analysis')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add experimental warning
    fig.suptitle('⚠️ Experimental/Hypothetical Quantum Analysis', 
                color='red', fontsize=10, y=0.02)
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    return {
        'figure': fig,
        'axes': ax,
        'correlation_data': corr_data,
        'visualization_type': 'static_matplotlib'
    }


def export_bell_violation_analysis(seq1, seq2, k=0.3, filename=None, 
                                  interactive=True, hypothetical=True):
    """
    Create visualization of Bell violation analysis between two sequences.
    
    Args:
        seq1: First Bio.Seq object
        seq2: Second Bio.Seq object
        k: Curvature parameter
        filename: Output filename
        interactive: Use Plotly if available
        hypothetical: Mark as experimental
        
    Returns:
        Visualization and analysis results
    """
    if hypothetical:
        print("Warning: Bell violation analysis is experimental/hypothetical.")
    
    # Generate coordinates for both sequences
    coords1 = generate_helical_coordinates(seq1, k=k, hypothetical=False)
    coords2 = generate_helical_coordinates(seq2, k=k, hypothetical=False)
    
    # Compute Bell violation
    violation, p_value = compute_bell_violation(coords1, coords2)
    
    # Create comparison visualization
    if interactive and PLOTLY_AVAILABLE:
        return _create_plotly_bell_analysis(coords1, coords2, seq1, seq2, violation, p_value, filename)
    else:
        return _create_matplotlib_bell_analysis(coords1, coords2, seq1, seq2, violation, p_value, filename)


def _create_plotly_bell_analysis(coords1, coords2, seq1, seq2, violation, p_value, filename):
    """Create interactive Plotly Bell violation analysis."""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Sequence 1 Helix', 'Sequence 2 Helix', 
                       'X-Y Correlations', 'Bell Violation Analysis'),
        specs=[[{"type": "scatter3d"}, {"type": "scatter3d"}],
               [{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # Sequence 1 helix
    fig.add_trace(go.Scatter3d(
        x=coords1['x'], y=coords1['y'], z=coords1['z'],
        mode='markers+lines',
        name='Seq 1',
        marker=dict(size=4, color='blue')
    ), row=1, col=1)
    
    # Sequence 2 helix  
    fig.add_trace(go.Scatter3d(
        x=coords2['x'], y=coords2['y'], z=coords2['z'],
        mode='markers+lines',
        name='Seq 2',
        marker=dict(size=4, color='red')
    ), row=1, col=2)
    
    # X-Y correlation plot
    fig.add_trace(go.Scatter(
        x=coords1['x'], y=coords1['y'],
        mode='markers',
        name='Seq 1 X-Y',
        marker=dict(color='blue', size=6)
    ), row=2, col=1)
    
    fig.add_trace(go.Scatter(
        x=coords2['x'], y=coords2['y'],
        mode='markers',
        name='Seq 2 X-Y',
        marker=dict(color='red', size=6)
    ), row=2, col=1)
    
    # Bell violation summary
    fig.add_trace(go.Bar(
        x=['Bell Violation', 'Classical Bound'],
        y=[violation + 2.0, 2.0],  # +2 to show violation above classical bound
        name='Bell Analysis',
        marker=dict(color=['red' if violation > 0 else 'blue', 'gray'])
    ), row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title=f"Bell Violation Analysis (Violation: {violation:.3f}, p: {p_value:.3f})",
        height=800
    )
    
    if filename:
        fig.write_html(filename)
    
    return {
        'figure': fig,
        'bell_violation': violation,
        'p_value': p_value,
        'visualization_type': 'interactive_plotly'
    }


def _create_matplotlib_bell_analysis(coords1, coords2, seq1, seq2, violation, p_value, filename):
    """Create static Matplotlib Bell violation analysis."""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Sequence 1 helix (3D projection)
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    ax1.plot(coords1['x'], coords1['y'], coords1['z'], 'b-', alpha=0.6)
    ax1.scatter(coords1['x'], coords1['y'], coords1['z'], c='blue', s=20)
    ax1.set_title('Sequence 1 Helix')
    
    # Sequence 2 helix (3D projection)
    ax2 = fig.add_subplot(2, 2, 2, projection='3d')
    ax2.plot(coords2['x'], coords2['y'], coords2['z'], 'r-', alpha=0.6)
    ax2.scatter(coords2['x'], coords2['y'], coords2['z'], c='red', s=20)
    ax2.set_title('Sequence 2 Helix')
    
    # X-Y correlations
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.scatter(coords1['x'], coords1['y'], c='blue', alpha=0.6, label='Seq 1')
    ax3.scatter(coords2['x'], coords2['y'], c='red', alpha=0.6, label='Seq 2')
    ax3.set_xlabel('X coordinate')
    ax3.set_ylabel('Y coordinate')
    ax3.set_title('X-Y Correlations')
    ax3.legend()
    
    # Bell violation analysis
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.bar(['Bell Violation', 'Classical Bound'], 
           [violation + 2.0, 2.0],  # +2 to show violation above classical bound
           color=['red' if violation > 0 else 'blue', 'gray'])
    ax4.set_ylabel('Bell Parameter')
    ax4.set_title(f'Bell Analysis (V: {violation:.3f}, p: {p_value:.3f})')
    ax4.axhline(y=2.0, color='black', linestyle='--', label='Classical Bound')
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    return {
        'figure': fig,
        'bell_violation': violation,
        'p_value': p_value,
        'visualization_type': 'static_matplotlib'
    }


def create_summary_report(seq, k=0.3, output_dir=None, hypothetical=True):
    """
    Create comprehensive analysis report with all visualizations.
    
    Args:
        seq: Bio.Seq object
        k: Curvature parameter
        output_dir: Directory for output files
        hypothetical: Mark as experimental
        
    Returns:
        Dictionary with all analysis results and file paths
    """
    if hypothetical:
        print("Warning: Comprehensive quantum analysis is experimental/hypothetical.")
    
    results = {}
    
    # Generate base filename
    base_name = f"quantum_analysis_k{k:.3f}"
    
    # Helical visualization
    helix_file = f"{base_name}_helix.html" if output_dir else None
    results['helix'] = export_helical_visualization(seq, k=k, filename=helix_file, hypothetical=False)
    
    # Quantum correlations
    corr_file = f"{base_name}_correlations.html" if output_dir else None
    results['correlations'] = plot_quantum_correlations(seq, k=k, filename=corr_file, hypothetical=False)
    
    # Summary statistics
    coords = generate_helical_coordinates(seq, k=k, hypothetical=False)
    corr_data = compute_quantum_correlations(seq, k=k, hypothetical=False)
    
    results['summary'] = {
        'sequence_length': len(seq),
        'curvature_parameter': k,
        'mean_correlation': corr_data['mean_correlation'],
        'entangled_regions': np.sum(corr_data['entangled_regions']),
        'coordinate_range': {
            'x': [float(np.min(coords['x'])), float(np.max(coords['x']))],
            'y': [float(np.min(coords['y'])), float(np.max(coords['y']))],
            'z': [float(np.min(coords['z'])), float(np.max(coords['z']))]
        },
        'hypothetical': hypothetical
    }
    
    return results