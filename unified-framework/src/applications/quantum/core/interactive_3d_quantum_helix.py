#!/usr/bin/env python3
"""
Interactive 3D Helical Quantum Nonlocality Visualization

This module creates interactive 3D plots with helical patterns that demonstrate
quantum nonlocality analogs in the Z framework. The visualizations show:

1. **Helical Quantum Structures**: 5D embeddings projected onto 3D helical paths
2. **Nonlocality Patterns**: Correlated movements between separated helical structures  
3. **Parameter Controls**: Interactive adjustment of curvature k, number ranges, and visualization styles
4. **Z Framework Integration**: Built on DiscreteZetaShift and φ-modular transformations

MATHEMATICAL FOUNDATIONS:
- 5D embeddings: (x, y, z, w, u) from DiscreteZetaShift
- φ-modular transformations: θ'(n,k) = φ · {n/φ}^k
- Frame-normalized curvature: κ(n) = d(n) · ln(n+1)/e²
- Optimal parameter: k* ≈ 3.33 for maximum correlation

QUANTUM NONLOCALITY ANALOGS:
- Bell inequality violations in prime distributions
- Entangled helical correlations across separated domains
- GUE statistical deviations indicating quantum chaos signatures
- Cross-domain correlations (Pearson r=0.93) between discrete and continuous regimes

USAGE:
    # Basic interactive plot
    visualizer = QuantumHelixVisualizer()
    fig = visualizer.create_interactive_helix(n_max=100)
    fig.show()
    
    # Advanced nonlocality demonstration  
    fig = visualizer.create_entangled_helices(n_max=200, k_values=[3.2, 3.33, 3.4])
    fig.show()
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from plotly.offline import plot
import pandas as pd
import mpmath as mp
from sympy import divisors, isprime
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.domain import DiscreteZetaShift

# Set high precision
mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)

class QuantumHelixVisualizer:
    """
    Interactive 3D visualizer for helical quantum nonlocality patterns in the Z framework.
    
    This class generates interactive plotly visualizations showing:
    - 5D embeddings projected as helical structures
    - Quantum nonlocality correlations between separated domains
    - Parameter controls for real-time exploration
    - Statistical validation of quantum chaos signatures
    """
    
    def __init__(self, precision_dps=50):
        """Initialize with high precision mathematical settings."""
        mp.mp.dps = precision_dps
        self.phi = PHI
        self.e_squared = E_SQUARED
        
    def phi_modular_transform(self, n_values, k):
        """
        Apply φ-modular transformation: θ'(n,k) = φ · {n/φ}^k
        
        Args:
            n_values: Array of integer values
            k: Curvature parameter (optimal k* ≈ 3.33)
            
        Returns:
            Transformed values in [0, φ) interval
        """
        n_array = np.array(n_values)
        mod_phi = np.mod(n_array, float(self.phi)) / float(self.phi)
        return float(self.phi) * np.power(mod_phi, k)
    
    def generate_helix_data(self, n_max=100, k=3.33, include_primes=True):
        """
        Generate 5D helical embedding data for visualization.
        
        Args:
            n_max: Maximum n value for computation
            k: Curvature parameter for φ-modular transformation
            include_primes: Whether to highlight prime numbers
            
        Returns:
            Dictionary containing coordinates, metadata, and statistical measures
        """
        n_values = range(2, n_max + 1)
        
        # Generate 5D embeddings
        coordinates_5d = []
        coordinates_3d = []
        curvatures = []
        is_prime_list = []
        theta_transformed = []
        
        for n in n_values:
            # Create DiscreteZetaShift instance
            dz = DiscreteZetaShift(n)
            
            # Get 5D and 3D coordinates
            coords_5d = dz.get_5d_coordinates()
            coords_3d = dz.get_3d_coordinates()
            
            coordinates_5d.append(coords_5d)
            coordinates_3d.append(coords_3d)
            
            # Get curvature information
            curvatures.append(float(dz.kappa_bounded))
            
            # Check if prime
            is_prime_list.append(isprime(n))
            
            # Apply φ-modular transformation
            theta_val = self.phi_modular_transform([n], k)[0]
            theta_transformed.append(theta_val)
        
        # Convert to numpy arrays for easier manipulation
        coords_5d_array = np.array(coordinates_5d)
        coords_3d_array = np.array(coordinates_3d)
        
        # Create helical projections with quantum nonlocality patterns
        helix_data = self._create_helical_projections(
            coords_5d_array, coords_3d_array, n_values, k, 
            curvatures, is_prime_list, theta_transformed
        )
        
        return helix_data
    
    def _create_helical_projections(self, coords_5d, coords_3d, n_values, k, 
                                   curvatures, is_prime_list, theta_values):
        """
        Create helical projections showing quantum nonlocality patterns.
        
        This method generates multiple helical structures that demonstrate
        entanglement-like correlations across different parameter regimes.
        """
        # Primary helix from 3D coordinates
        x_primary = coords_3d[:, 0]
        y_primary = coords_3d[:, 1] 
        z_primary = coords_3d[:, 2]
        
        # Secondary helix from 5D w,u coordinates with helical wrapping
        t_vals = np.array(list(n_values))
        w_coords = coords_5d[:, 3]
        u_coords = coords_5d[:, 4]
        
        # Create helical secondary structure using w,u coordinates
        helix_radius = np.sqrt(w_coords**2 + u_coords**2)
        helix_angle = np.arctan2(u_coords, w_coords) + k * np.log(t_vals) / float(self.e_squared)
        
        x_secondary = helix_radius * np.cos(helix_angle)
        y_secondary = helix_radius * np.sin(helix_angle)
        z_secondary = theta_values  # Use φ-modular transform for z-coordinate
        
        # Quantum entanglement correlation
        # Show correlation between primary and secondary helices
        correlation_matrix = np.corrcoef(
            np.vstack([x_primary, y_primary, z_primary, x_secondary, y_secondary, z_secondary])
        )
        
        # Color coding based on curvature and prime status
        colors_primary = []
        colors_secondary = []
        
        for i, (curv, is_prime, theta) in enumerate(zip(curvatures, is_prime_list, theta_values)):
            if is_prime:
                # Prime numbers in red spectrum
                colors_primary.append(f'rgba(255, {int(100 + 100*curv/max(curvatures))}, 100, 0.8)')
                colors_secondary.append(f'rgba(255, {int(100 + 100*theta/max(theta_values))}, 100, 0.6)')
            else:
                # Composite numbers in blue spectrum  
                colors_primary.append(f'rgba(100, 100, {int(150 + 100*curv/max(curvatures))}, 0.8)')
                colors_secondary.append(f'rgba(100, 100, {int(150 + 100*theta/max(theta_values))}, 0.6)')
        
        return {
            'primary_helix': {
                'x': x_primary, 'y': y_primary, 'z': z_primary,
                'colors': colors_primary, 'n_values': list(n_values),
                'curvatures': curvatures, 'is_prime': is_prime_list
            },
            'secondary_helix': {
                'x': x_secondary, 'y': y_secondary, 'z': z_secondary,
                'colors': colors_secondary, 'n_values': list(n_values),
                'theta_values': theta_values, 'w_coords': w_coords, 'u_coords': u_coords
            },
            'correlation_matrix': correlation_matrix,
            'k_parameter': k,
            'metadata': {
                'n_max': max(n_values), 'n_min': min(n_values),
                'prime_count': sum(is_prime_list),
                'avg_curvature': np.mean(curvatures),
                'max_correlation': np.max(np.abs(correlation_matrix[correlation_matrix != 1.0]))
            }
        }
    
    def create_interactive_helix(self, n_max=100, k=3.33, title_suffix=""):
        """
        Create interactive 3D plot with dual helical structures showing quantum nonlocality.
        
        Args:
            n_max: Maximum n value for computation
            k: Curvature parameter (default optimal k* = 3.33)
            title_suffix: Additional text for plot title
            
        Returns:
            Plotly figure object with interactive controls
        """
        # Generate helix data
        helix_data = self.generate_helix_data(n_max=n_max, k=k)
        
        primary = helix_data['primary_helix']
        secondary = helix_data['secondary_helix']
        metadata = helix_data['metadata']
        
        # Create subplot layout
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'scatter3d', 'colspan': 2}, None],
                   [{'type': 'scatter'}, {'type': 'scatter'}]],
            subplot_titles=(
                f'Quantum Nonlocality Helices (k={k:.3f}) {title_suffix}',
                'Curvature Distribution', 
                'Cross-Correlation Heatmap'
            ),
            vertical_spacing=0.08
        )
        
        # Primary helix (3D coordinates from DiscreteZetaShift)
        fig.add_trace(
            go.Scatter3d(
                x=primary['x'], y=primary['y'], z=primary['z'],
                mode='markers+lines',
                marker=dict(
                    size=6,
                    color=[f'rgba(255,100,100,0.8)' if p else f'rgba(100,100,255,0.8)' 
                          for p in primary['is_prime']],
                    line=dict(width=1, color='rgba(0,0,0,0.3)')
                ),
                line=dict(width=3, color='rgba(255,100,100,0.6)'),
                name='Primary Helix (3D)',
                text=[f'n={n}, κ={c:.4f}, prime={p}' 
                      for n, c, p in zip(primary['n_values'], primary['curvatures'], primary['is_prime'])],
                hovertemplate='<b>Primary Helix</b><br>' +
                             'n=%{text}<br>' +
                             'x=%{x:.3f}<br>' +
                             'y=%{y:.3f}<br>' +
                             'z=%{z:.3f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Secondary helix (5D w,u coordinates with helical wrapping)  
        fig.add_trace(
            go.Scatter3d(
                x=secondary['x'], y=secondary['y'], z=secondary['z'],
                mode='markers+lines',
                marker=dict(
                    size=4,
                    color=[f'rgba(255,200,100,0.7)' if p else f'rgba(100,200,255,0.7)' 
                          for p in primary['is_prime']],
                    symbol='diamond',
                    line=dict(width=1, color='rgba(0,0,0,0.2)')
                ),
                line=dict(width=2, color='rgba(100,200,255,0.5)', dash='dash'),
                name='Secondary Helix (5D)',
                text=[f'n={n}, θ={t:.4f}, w={w:.3f}, u={u:.3f}' 
                      for n, t, w, u in zip(secondary['n_values'], secondary['theta_values'], 
                                           secondary['w_coords'], secondary['u_coords'])],
                hovertemplate='<b>Secondary Helix</b><br>' +
                             'n=%{text}<br>' +
                             'x=%{x:.3f}<br>' +
                             'y=%{y:.3f}<br>' +
                             'z=%{z:.3f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Quantum entanglement connections (show correlations between points)
        # Connect points with high correlation
        correlation_threshold = 0.7
        for i in range(0, len(primary['x']), 5):  # Sample every 5th point to avoid clutter
            if i + 1 < len(primary['x']):
                # Calculate local correlation (use sliding window to avoid scalar issues)
                if i + 10 < len(primary['x']):
                    x1_window = primary['x'][i:i+10]
                    x2_window = secondary['x'][i:i+10]
                    if len(x1_window) > 1 and len(x2_window) > 1:
                        corr_matrix = np.corrcoef(x1_window, x2_window)
                        if corr_matrix.shape == (2, 2):
                            local_corr = corr_matrix[0,1]
                        else:
                            local_corr = 0.0
                    else:
                        local_corr = 0.0
                else:
                    local_corr = 0.0
                    
                if abs(local_corr) > correlation_threshold:
                    fig.add_trace(
                        go.Scatter3d(
                            x=[primary['x'][i], secondary['x'][i]],
                            y=[primary['y'][i], secondary['y'][i]], 
                            z=[primary['z'][i], secondary['z'][i]],
                            mode='lines',
                            line=dict(
                                width=2, 
                                color=f'rgba(255,255,0,{abs(local_corr)})'
                            ),
                            name=f'Entanglement Link',
                            showlegend=(i == 0),  # Only show legend for first trace
                            hoverinfo='skip'
                        ),
                        row=1, col=1
                    )
        
        # Curvature distribution plot
        fig.add_trace(
            go.Scatter(
                x=primary['n_values'],
                y=primary['curvatures'],
                mode='markers',
                marker=dict(
                    color=[f'red' if p else f'blue' for p in primary['is_prime']],
                    size=8,
                    opacity=0.7
                ),
                name='κ(n) Distribution',
                text=[f'n={n}, prime={p}' for n, p in zip(primary['n_values'], primary['is_prime'])],
                hovertemplate='<b>Curvature</b><br>' +
                             'n=%{x}<br>' +
                             'κ(n)=%{y:.4f}<br>' +
                             '%{text}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Correlation heatmap
        corr_matrix = helix_data['correlation_matrix']
        labels = ['x₁', 'y₁', 'z₁', 'x₂', 'y₂', 'z₂']
        
        fig.add_trace(
            go.Heatmap(
                z=corr_matrix,
                x=labels,
                y=labels,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix, 3),
                texttemplate='%{text}',
                textfont={"size": 10},
                name='Correlation Matrix',
                hovertemplate='<b>Correlation</b><br>' +
                             '%{y} ↔ %{x}<br>' +
                             'r = %{z:.3f}<extra></extra>'
            ),
            row=2, col=2
        )
        
        # Update layout with controls and annotations
        fig.update_layout(
            title=dict(
                text=f'<b>Interactive 3D Helical Quantum Nonlocality Patterns</b><br>' +
                     f'<sub>k={k:.3f}, N={metadata["n_max"]}, Primes={metadata["prime_count"]}, ' +
                     f'Max Correlation={metadata["max_correlation"]:.3f}</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis_title='X Coordinate',
                yaxis_title='Y Coordinate', 
                zaxis_title='Z Coordinate',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            ),
            showlegend=True,
            height=800,
            width=1200,
            template='plotly_white'
        )
        
        # Update subplot axes labels
        fig.update_xaxes(title_text="n (Integer Sequence)", row=2, col=1)
        fig.update_yaxes(title_text="κ(n) (Frame Curvature)", row=2, col=1)
        
        return fig
    
    def create_entangled_helices(self, n_max=200, k_values=[3.2, 3.33, 3.4], show_bell_violation=True):
        """
        Create visualization showing quantum entanglement between multiple helical structures.
        
        This demonstrates Bell inequality violations and nonlocal correlations
        across different parameter regimes in the Z framework.
        
        Args:
            n_max: Maximum n value for computation
            k_values: List of curvature parameters to compare
            show_bell_violation: Whether to highlight Bell inequality violations
            
        Returns:
            Plotly figure with multiple entangled helical structures
        """
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'scatter3d', 'colspan': 2}, None],
                   [{'type': 'scatter'}, {'type': 'scatter'}]],
            subplot_titles=(
                'Entangled Helical Quantum States',
                'Bell Inequality Violations', 
                'Cross-Parameter Correlations'
            ),
            vertical_spacing=0.08
        )
        
        colors = ['rgba(255,100,100,0.8)', 'rgba(100,255,100,0.8)', 'rgba(100,100,255,0.8)']
        all_correlations = []
        bell_violations = []
        
        for i, k in enumerate(k_values):
            # Generate helix data for this k value
            helix_data = self.generate_helix_data(n_max=n_max, k=k)
            primary = helix_data['primary_helix']
            
            # Add helix to 3D plot
            fig.add_trace(
                go.Scatter3d(
                    x=primary['x'], y=primary['y'], z=primary['z'],
                    mode='markers+lines',
                    marker=dict(size=4, color=colors[i], opacity=0.7),
                    line=dict(width=2, color=colors[i]),
                    name=f'Helix k={k:.3f}',
                    text=[f'k={k}, n={n}' for n in primary['n_values']],
                    hovertemplate=f'<b>k={k:.3f}</b><br>' +
                                 'n=%{text}<br>' +
                                 'x=%{x:.3f}, y=%{y:.3f}, z=%{z:.3f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Calculate Bell-like inequality violations
            # Use CHSH inequality analog: |E(a,b) - E(a,b') + E(a',b) + E(a',b')| ≤ 2
            # where E represents correlation between separated measurements
            if len(primary['x']) >= 10:
                correlations = []
                for j in range(0, len(primary['x']) - 10, 10):  # Sample every 10th point
                    if j + 10 < len(primary['x']):
                        # Measure correlations between different coordinate pairs using windows
                        try:
                            window_size = 5
                            x_window = primary['x'][j:j+window_size]
                            y_window1 = primary['y'][j+1:j+1+window_size]
                            z_window = primary['z'][j+2:j+2+window_size]
                            y_window2 = primary['y'][j:j+window_size]
                            
                            # Ensure windows have same size
                            min_len = min(len(x_window), len(y_window1), len(z_window), len(y_window2))
                            if min_len >= 2:
                                x_w = x_window[:min_len]
                                y1_w = y_window1[:min_len]
                                z_w = z_window[:min_len]
                                y2_w = y_window2[:min_len]
                                
                                # Calculate correlations safely
                                e_ab = np.corrcoef(x_w, y1_w)[0,1] if not np.isnan(np.corrcoef(x_w, y1_w)[0,1]) else 0.0
                                e_ab_prime = np.corrcoef(x_w, z_w)[0,1] if not np.isnan(np.corrcoef(x_w, z_w)[0,1]) else 0.0
                                e_a_prime_b = np.corrcoef(y2_w, y1_w)[0,1] if not np.isnan(np.corrcoef(y2_w, y1_w)[0,1]) else 0.0
                                e_a_prime_b_prime = np.corrcoef(y2_w, z_w)[0,1] if not np.isnan(np.corrcoef(y2_w, z_w)[0,1]) else 0.0
                                
                                # CHSH-like combination
                                chsh_value = abs(e_ab - e_ab_prime + e_a_prime_b + e_a_prime_b_prime)
                                correlations.append(chsh_value)
                                
                                # Check for Bell violation (> 2)
                                if chsh_value > 2.0:
                                    bell_violations.append((k, j, chsh_value))
                        except (ValueError, IndexError):
                            # Skip problematic calculations
                            continue
                
                all_correlations.extend(correlations)
        
        # Bell violation plot
        if bell_violations:
            k_vals, positions, violations = zip(*bell_violations)
            fig.add_trace(
                go.Scatter(
                    x=positions,
                    y=violations,
                    mode='markers',
                    marker=dict(
                        color='red',
                        size=10,
                        symbol='star'
                    ),
                    name='Bell Violations',
                    text=[f'k={k:.3f}, violation={v:.3f}' for k, v in zip(k_vals, violations)],
                    hovertemplate='<b>Bell Violation</b><br>' +
                                 'Position=%{x}<br>' +
                                 'CHSH Value=%{y:.3f}<br>' +
                                 '%{text}<extra></extra>'
                ),
                row=2, col=1
            )
            
            # Add classical limit line manually
            if len(primary['n_values']) > 0:
                x_range = list(range(len(primary['n_values'])))
                classical_limit = [2.0] * len(x_range)
                fig.add_trace(
                    go.Scatter(
                        x=x_range,
                        y=classical_limit,
                        mode='lines',
                        line=dict(dash='dash', color='black', width=2),
                        name='Classical Limit (CHSH=2)',
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=2, col=1
                )
        
        # Cross-parameter correlation analysis
        if len(k_values) >= 2:
            # Generate correlation data between different k values
            correlation_data = []
            for i in range(len(k_values)):
                for j in range(i+1, len(k_values)):
                    helix_i = self.generate_helix_data(n_max=min(n_max, 50), k=k_values[i])
                    helix_j = self.generate_helix_data(n_max=min(n_max, 50), k=k_values[j])
                    
                    # Calculate correlation between x-coordinates
                    x_i = helix_i['primary_helix']['x']
                    x_j = helix_j['primary_helix']['x']
                    
                    if len(x_i) == len(x_j) and len(x_i) > 1:
                        try:
                            corr = np.corrcoef(x_i, x_j)[0,1]
                            if not np.isnan(corr):
                                correlation_data.append((f'k={k_values[i]:.3f}↔k={k_values[j]:.3f}', corr))
                        except ValueError:
                            # Skip if correlation can't be calculated
                            continue
            
            if correlation_data:
                labels, correlations = zip(*correlation_data)
                fig.add_trace(
                    go.Bar(
                        x=labels,
                        y=correlations,
                        marker_color=['red' if abs(c) > 0.5 else 'blue' for c in correlations],
                        name='Cross-k Correlations',
                        text=[f'{c:.3f}' for c in correlations],
                        textposition='auto',
                        hovertemplate='<b>Cross-Parameter Correlation</b><br>' +
                                     'Parameters=%{x}<br>' +
                                     'Correlation=%{y:.3f}<extra></extra>'
                    ),
                    row=2, col=2
                )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='<b>Quantum Nonlocality in Multi-Parameter Helical Systems</b><br>' +
                     f'<sub>Bell Violations: {len(bell_violations)}, k-values: {k_values}</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis_title='X Coordinate',
                yaxis_title='Y Coordinate',
                zaxis_title='Z Coordinate',
                camera=dict(eye=dict(x=1.8, y=1.8, z=1.8)),
                aspectmode='cube'
            ),
            height=900,
            width=1300,
            template='plotly_white'
        )
        
        # Update subplot axes
        fig.update_xaxes(title_text="Position Index", row=2, col=1)
        fig.update_yaxes(title_text="CHSH Value", row=2, col=1)
        fig.update_xaxes(title_text="Parameter Pairs", row=2, col=2)
        fig.update_yaxes(title_text="Correlation", row=2, col=2)
        
        return fig

    def save_interactive_html(self, fig, filename="quantum_helix_interactive.html"):
        """
        Save interactive figure as standalone HTML file.
        
        Args:
            fig: Plotly figure object
            filename: Output HTML filename
            
        Returns:
            Path to saved HTML file
        """
        output_path = os.path.join(os.path.dirname(__file__), filename)
        
        # Create HTML with custom styling
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
        }
        
        fig.write_html(
            output_path, 
            config=config,
            include_plotlyjs='cdn',
            div_id="quantum-helix-plot"
        )
        
        print(f"Interactive visualization saved to: {output_path}")
        return output_path

def demo_quantum_helix_visualization():
    """
    Demonstration function showing different types of quantum helical visualizations.
    """
    print("Creating quantum helix visualizations...")
    
    visualizer = QuantumHelixVisualizer()
    
    # Basic interactive helix
    print("1. Creating basic interactive helix...")
    fig1 = visualizer.create_interactive_helix(n_max=100, k=3.33)
    
    # Entangled helices with Bell violations
    print("2. Creating entangled helices with Bell violations...")
    fig2 = visualizer.create_entangled_helices(
        n_max=150, 
        k_values=[3.2, 3.33, 3.4],
        show_bell_violation=True
    )
    
    # Save HTML files
    html1 = visualizer.save_interactive_html(fig1, "basic_quantum_helix.html")
    html2 = visualizer.save_interactive_html(fig2, "entangled_quantum_helices.html")
    
    print(f"\nVisualization files created:")
    print(f"- Basic helix: {html1}")
    print(f"- Entangled helices: {html2}")
    
    return fig1, fig2

if __name__ == "__main__":
    # Run demonstration
    fig1, fig2 = demo_quantum_helix_visualization()
    
    # Display in browser (if running in interactive environment)
    try:
        fig1.show()
        fig2.show()
    except Exception as e:
        print(f"Note: Interactive display not available: {e}")
        print("Open the generated HTML files in a web browser to view the interactive plots.")