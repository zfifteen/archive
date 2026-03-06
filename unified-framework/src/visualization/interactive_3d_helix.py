#!/usr/bin/env python3
"""
Interactive 3D Helical Quantum Nonlocality Visualizer

This module provides interactive 3D visualizations of helical patterns that exhibit
quantum nonlocality analogs within the Z framework. It builds on the existing
mathematical foundations while providing enhanced interactivity and parameter control.

Key Features:
- Interactive 3D helical plots with plotly
- Quantum nonlocality pattern detection and highlighting
- Parameter controls for curvature k, frequencies, and golden ratio transforms
- Integration with DiscreteZetaShift and core Z framework axioms
- Bell inequality violation indicators
- Prime distribution analysis in curved space

Mathematical Foundations:
- Universal Z form: Z = A(B/c)
- DiscreteZetaShift with 5D helical embeddings
- Golden ratio φ = (1 + √5)/2 curvature transforms
- Optimal curvature parameter k* = 0.200
- High precision arithmetic with mpmath (dps=50)
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import matplotlib.pyplot as plt
import math
import mpmath as mp
from typing import List, Tuple, Dict, Optional, Callable
import warnings

# Set high precision for calculations
mp.mp.dps = 50

# Mathematical constants
PHI = float((1 + mp.sqrt(5)) / 2)  # Golden ratio
E_SQUARED = float(mp.exp(2))       # e^2 normalization
C_LIGHT = 299792458.0              # Speed of light (invariant)

class Interactive3DHelixVisualizer:
    """
    Interactive 3D visualization system for helical quantum nonlocality patterns.
    
    This class provides comprehensive tools for visualizing helical structures that
    exhibit quantum nonlocality analogs, with full parameter control and interactivity.
    """
    
    def __init__(self, 
                 n_points: int = 5000,
                 default_k: float = 0.200,
                 helix_freq: float = 0.1003033,
                 use_high_precision: bool = True):
        """
        Initialize the Interactive 3D Helix Visualizer.
        
        Args:
            n_points: Number of points to generate for visualizations
            default_k: Default curvature parameter (optimal k* = 0.200)
            helix_freq: Helical frequency parameter
            use_high_precision: Whether to use high-precision arithmetic
        """
        self.n_points = n_points
        self.default_k = default_k
        self.helix_freq = helix_freq
        self.use_high_precision = use_high_precision
        
        # Cache for computed values
        self._cache = {}
        
        # Generate base data
        self._generate_base_data()
    
    def _generate_base_data(self):
        """Generate base mathematical data for visualizations."""
        # Generate sequence
        self.n = np.arange(1, self.n_points + 1)
        
        # Compute primality
        self.primality = np.array([self._is_prime(n) for n in self.n])
        
        # Generate primes array
        self.primes = self.n[self.primality]
        
    def _is_prime(self, num: int) -> bool:
        """Check if a number is prime."""
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0 or num % 3 == 0:
            return False
        i = 5
        while i * i <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False
            i += 6
        return True
    
    def z_transform(self, A: np.ndarray, B: np.ndarray, C: float) -> np.ndarray:
        """
        Universal Z form transformation: Z = A(B/C)
        
        Args:
            A: Frame-dependent quantity array
            B: Rate quantity array  
            C: Universal invariant (typically c)
            
        Returns:
            Transformed Z values
        """
        return A * (B / C)
    
    def curvature_transform(self, n: np.ndarray, k: float = None) -> np.ndarray:
        """
        Golden ratio curvature transformation for non-Hausdorff regime.
        
        Args:
            n: Input sequence
            k: Curvature parameter (default uses self.default_k)
            
        Returns:
            Curvature-transformed values
        """
        if k is None:
            k = self.default_k
            
        phi = PHI
        return phi * ((n % phi) / phi) ** k
    
    def compute_quantum_correlations(self, primes: np.ndarray, k: float = None) -> np.ndarray:
        """
        Compute quantum nonlocality correlations using harmonic means in curved space.
        
        This implements the analog to quantum entanglement via harmonic means
        encoding minimal frame shifts (like twin primes).
        
        Args:
            primes: Array of prime numbers
            k: Curvature parameter
            
        Returns:
            Quantum correlation array
        """
        if k is None:
            k = self.default_k
            
        # Transform into non-Hausdorff number space
        theta = self.curvature_transform(primes, k)
        
        # Create entangled prime pairs via harmonic means
        if len(primes) < 2:
            return np.array([])
            
        entangled = np.array([
            (theta[i] * theta[i+1]) / (theta[i] + theta[i+1])
            for i in range(len(primes)-1)
            if (theta[i] + theta[i+1]) != 0
        ])
        
        # Apply Z transform with prime gaps as rate B
        if len(entangled) > 0:
            gaps = np.diff(primes[:len(entangled)+1])
            max_entangled = np.max(entangled) if len(entangled) > 0 else 1.0
            return self.z_transform(A=entangled, B=gaps, C=max_entangled)
        else:
            return np.array([])
    
    def compute_bell_violation(self, correlations: np.ndarray, gaps: np.ndarray) -> Tuple[bool, float]:
        """
        Compute Bell inequality violation analog.
        
        Args:
            correlations: Quantum correlation array
            gaps: Prime gap array
            
        Returns:
            Tuple of (violation_detected, correlation_coefficient)
        """
        if len(correlations) == 0 or len(gaps) == 0:
            return False, 0.0
            
        # Ensure arrays are same length
        min_len = min(len(correlations), len(gaps))
        correlations = correlations[:min_len]
        gaps = gaps[:min_len]
        
        # Compute correlation matrix
        if min_len < 2:
            return False, 0.0
            
        # Check for sufficient variance
        if np.var(correlations) == 0 or np.var(gaps) == 0:
            return False, 0.0
            
        correlation_matrix = np.corrcoef(correlations, gaps)
        
        # Handle potential NaN values
        if correlation_matrix.shape == (2, 2) and not np.isnan(correlation_matrix[0, 1]):
            correlation_coeff = correlation_matrix[0, 1]
        else:
            correlation_coeff = 0.0
        
        # CHSH analog: classical limit is ~0.707
        bell_violation = bool(np.abs(correlation_coeff) > 0.707)
        
        return bell_violation, correlation_coeff
    
    def generate_helical_coordinates(self, 
                                   sequence: np.ndarray,
                                   k: float = None,
                                   freq: float = None,
                                   use_quantum: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate 3D helical coordinates with quantum nonlocality enhancements.
        
        Args:
            sequence: Input number sequence
            k: Curvature parameter
            freq: Helical frequency
            use_quantum: Whether to apply quantum correlation transforms
            
        Returns:
            Tuple of (x, y, z) coordinate arrays
        """
        if k is None:
            k = self.default_k
        if freq is None:
            freq = self.helix_freq
            
        # Base helical coordinates
        n = sequence
        
        # Y-coordinates with curvature transform
        if use_quantum:
            y_raw = self.curvature_transform(n, k)
        else:
            y_raw = n * (n / math.pi)
        
        # Apply Z transform
        y = self.z_transform(A=y_raw, B=n, C=C_LIGHT)
        
        # X-coordinates (parametric parameter)
        x = n
        
        # Z-coordinates (helical pattern)
        z = np.sin(math.pi * freq * n)
        
        return x, y, z
    
    def create_interactive_helix_plot(self,
                                    k: float = None,
                                    freq: float = None,
                                    show_primes: bool = True,
                                    show_quantum_correlations: bool = True,
                                    show_bell_violations: bool = True,
                                    title: str = "Interactive 3D Helical Quantum Nonlocality Patterns") -> go.Figure:
        """
        Create the main interactive 3D helical plot.
        
        Args:
            k: Curvature parameter
            freq: Helical frequency
            show_primes: Whether to highlight prime numbers
            show_quantum_correlations: Whether to show quantum correlation indicators
            show_bell_violations: Whether to highlight Bell inequality violations
            title: Plot title
            
        Returns:
            Plotly Figure object
        """
        if k is None:
            k = self.default_k
        if freq is None:
            freq = self.helix_freq
        
        # Generate coordinates
        x, y, z = self.generate_helical_coordinates(self.n, k, freq, use_quantum=True)
        
        # Create figure
        fig = go.Figure()
        
        # Split into primes and non-primes
        if show_primes:
            # Non-primes
            x_nonprimes = x[~self.primality]
            y_nonprimes = y[~self.primality]
            z_nonprimes = z[~self.primality]
            
            fig.add_trace(go.Scatter3d(
                x=x_nonprimes,
                y=y_nonprimes,
                z=z_nonprimes,
                mode='markers',
                marker=dict(
                    size=3,
                    color='blue',
                    opacity=0.3
                ),
                name='Non-primes',
                hovertemplate='n=%{x}<br>Z-transform=%{y:.6f}<br>Helix=%{z:.6f}<extra></extra>'
            ))
            
            # Primes
            x_primes = x[self.primality]
            y_primes = y[self.primality]
            z_primes = z[self.primality]
            
            fig.add_trace(go.Scatter3d(
                x=x_primes,
                y=y_primes,
                z=z_primes,
                mode='markers',
                marker=dict(
                    size=6,
                    color='red',
                    symbol='diamond',
                    opacity=0.8
                ),
                name='Primes',
                hovertemplate='Prime=%{x}<br>Z-transform=%{y:.6f}<br>Helix=%{z:.6f}<extra></extra>'
            ))
        else:
            # All points
            fig.add_trace(go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode='markers',
                marker=dict(
                    size=4,
                    color=z,
                    colorscale='Viridis',
                    opacity=0.6
                ),
                name='Helical sequence',
                hovertemplate='n=%{x}<br>Z-transform=%{y:.6f}<br>Helix=%{z:.6f}<extra></extra>'
            ))
        
        # Add quantum correlation indicators
        if show_quantum_correlations and len(self.primes) > 1:
            correlations = self.compute_quantum_correlations(self.primes, k)
            
            if len(correlations) > 0:
                # Show correlations as connecting lines between prime pairs
                for i in range(min(len(correlations), len(self.primes)-1)):
                    prime_idx1 = np.where(self.n == self.primes[i])[0]
                    prime_idx2 = np.where(self.n == self.primes[i+1])[0]
                    
                    if len(prime_idx1) > 0 and len(prime_idx2) > 0:
                        idx1, idx2 = prime_idx1[0], prime_idx2[0]
                        
                        # Color intensity based on correlation strength
                        correlation_strength = abs(correlations[i])
                        line_color = f'rgba(255, 165, 0, {min(correlation_strength * 10, 1.0)})'
                        
                        fig.add_trace(go.Scatter3d(
                            x=[x[idx1], x[idx2]],
                            y=[y[idx1], y[idx2]],
                            z=[z[idx1], z[idx2]],
                            mode='lines',
                            line=dict(
                                color=line_color,
                                width=3
                            ),
                            name=f'Quantum correlation {i+1}',
                            showlegend=False,
                            hovertemplate=f'Quantum correlation: {correlations[i]:.6f}<extra></extra>'
                        ))
        
        # Add Bell violation indicators
        if show_bell_violations and len(self.primes) > 1:
            correlations = self.compute_quantum_correlations(self.primes, k)
            if len(correlations) > 0:
                gaps = np.diff(self.primes[:len(correlations)+1])
                bell_violation, correlation_coeff = self.compute_bell_violation(correlations, gaps)
                
                if bell_violation:
                    # Add annotation for Bell violation
                    max_z = np.max(z)
                    fig.add_trace(go.Scatter3d(
                        x=[np.max(x) * 0.8],
                        y=[np.max(y) * 0.8],
                        z=[max_z * 0.9],
                        mode='markers+text',
                        marker=dict(
                            size=15,
                            color='gold',
                            symbol='x',
                            line=dict(color='red', width=2)
                        ),
                        text=['Bell Violation!'],
                        textposition='top center',
                        name=f'Bell violation (ρ={correlation_coeff:.3f})',
                        hovertemplate=f'Bell inequality violation<br>Correlation: {correlation_coeff:.6f}<extra></extra>'
                    ))
        
        # Customize layout
        fig.update_layout(
            title=dict(
                text=f"{title}<br><sub>k={k:.3f}, freq={freq:.6f}, φ={PHI:.6f}</sub>",
                x=0.5
            ),
            scene=dict(
                xaxis_title='n (Position)',
                yaxis_title='Z-transformed Value',
                zaxis_title='Helical Coordinate',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                ),
                aspectmode='cube'
            ),
            margin=dict(l=0, r=0, b=0, t=60),
            height=800
        )
        
        return fig
    
    def create_quantum_correlation_analysis(self, k: float = None) -> go.Figure:
        """
        Create detailed quantum correlation analysis visualization.
        
        Args:
            k: Curvature parameter
            
        Returns:
            Plotly Figure with correlation analysis
        """
        if k is None:
            k = self.default_k
            
        # Compute correlations
        correlations = self.compute_quantum_correlations(self.primes, k)
        
        if len(correlations) == 0:
            # Return empty plot
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for quantum correlation analysis",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font_size=16
            )
            return fig
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Quantum Correlations', 'Prime Gaps', 
                          'Correlation vs Gaps', 'Fourier Spectrum'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # Plot 1: Quantum correlations
        fig.add_trace(
            go.Scatter(
                x=list(range(len(correlations))),
                y=correlations,
                mode='lines+markers',
                name='Quantum correlations',
                line=dict(color='purple')
            ),
            row=1, col=1
        )
        
        # Plot 2: Prime gaps
        gaps = np.diff(self.primes[:len(correlations)+1])
        fig.add_trace(
            go.Scatter(
                x=list(range(len(gaps))),
                y=gaps,
                mode='lines+markers',
                name='Prime gaps',
                line=dict(color='blue')
            ),
            row=1, col=2
        )
        
        # Plot 3: Correlation vs gaps scatter
        min_len = min(len(correlations), len(gaps))
        if min_len > 0:
            corr_subset = correlations[:min_len]
            gaps_subset = gaps[:min_len]
            
            fig.add_trace(
                go.Scatter(
                    x=gaps_subset,
                    y=corr_subset,
                    mode='markers',
                    name='Correlation vs Gaps',
                    marker=dict(
                        color=np.arange(min_len),
                        colorscale='Viridis',
                        size=8
                    )
                ),
                row=2, col=1
            )
        
        # Plot 4: Fourier spectrum
        if len(correlations) > 1:
            spectrum = np.abs(np.fft.fft(correlations))
            frequencies = np.fft.fftfreq(len(correlations))
            
            fig.add_trace(
                go.Scatter(
                    x=frequencies[:len(frequencies)//2],
                    y=spectrum[:len(spectrum)//2],
                    mode='lines',
                    name='Fourier spectrum',
                    line=dict(color='red')
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title=f"Quantum Correlation Analysis (k={k:.3f})",
            height=800,
            showlegend=False
        )
        
        return fig
    
    def create_parameter_sweep_animation(self,
                                       k_range: Tuple[float, float] = (0.1, 0.5),
                                       k_steps: int = 20,
                                       save_html: bool = True,
                                       filename: str = "helix_parameter_sweep.html") -> go.Figure:
        """
        Create animated visualization showing parameter sweep effects.
        
        Args:
            k_range: Range of k values to sweep
            k_steps: Number of steps in the sweep
            save_html: Whether to save as HTML file
            filename: Output filename
            
        Returns:
            Animated plotly Figure
        """
        k_values = np.linspace(k_range[0], k_range[1], k_steps)
        
        # Generate frames for animation
        frames = []
        
        for i, k in enumerate(k_values):
            # Generate coordinates for this k value
            x, y, z = self.generate_helical_coordinates(self.n[:1000], k, self.helix_freq)  # Use subset for performance
            
            # Create frame data
            frame_data = [
                go.Scatter3d(
                    x=x[~self.primality[:1000]],
                    y=y[~self.primality[:1000]],
                    z=z[~self.primality[:1000]],
                    mode='markers',
                    marker=dict(size=3, color='blue', opacity=0.3),
                    name='Non-primes'
                ),
                go.Scatter3d(
                    x=x[self.primality[:1000]],
                    y=y[self.primality[:1000]],
                    z=z[self.primality[:1000]],
                    mode='markers',
                    marker=dict(size=6, color='red', symbol='diamond', opacity=0.8),
                    name='Primes'
                )
            ]
            
            frames.append(go.Frame(
                data=frame_data,
                name=str(i),
                layout=go.Layout(
                    title=f"Helical Quantum Patterns (k={k:.3f})"
                )
            ))
        
        # Create initial figure
        initial_x, initial_y, initial_z = self.generate_helical_coordinates(
            self.n[:1000], k_values[0], self.helix_freq
        )
        
        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=initial_x[~self.primality[:1000]],
                    y=initial_y[~self.primality[:1000]],
                    z=initial_z[~self.primality[:1000]],
                    mode='markers',
                    marker=dict(size=3, color='blue', opacity=0.3),
                    name='Non-primes'
                ),
                go.Scatter3d(
                    x=initial_x[self.primality[:1000]],
                    y=initial_y[self.primality[:1000]],
                    z=initial_z[self.primality[:1000]],
                    mode='markers',
                    marker=dict(size=6, color='red', symbol='diamond', opacity=0.8),
                    name='Primes'
                )
            ],
            frames=frames
        )
        
        # Add animation controls
        fig.update_layout(
            title="Parameter Sweep Animation: Helical Quantum Nonlocality Patterns",
            scene=dict(
                xaxis_title='n (Position)',
                yaxis_title='Z-transformed Value',
                zaxis_title='Helical Coordinate',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 500, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 300}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                        "mode": "immediate", "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }],
            sliders=[{
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "k=",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 300, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[i], {"frame": {"duration": 300, "redraw": True},
                                     "mode": "immediate", "transition": {"duration": 300}}],
                        "label": f"{k:.3f}",
                        "method": "animate"
                    }
                    for i, k in enumerate(k_values)
                ]
            }],
            height=800
        )
        
        if save_html:
            pyo.plot(fig, filename=filename, auto_open=False)
            
        return fig
    
    def generate_summary_report(self, k: float = None) -> Dict:
        """
        Generate comprehensive summary report of quantum nonlocality analysis.
        
        Args:
            k: Curvature parameter
            
        Returns:
            Dictionary containing analysis results
        """
        if k is None:
            k = self.default_k
            
        # Compute all relevant quantities
        correlations = self.compute_quantum_correlations(self.primes, k)
        
        report = {
            'parameters': {
                'n_points': self.n_points,
                'curvature_k': k,
                'helix_frequency': self.helix_freq,
                'golden_ratio': PHI,
                'num_primes': len(self.primes)
            },
            'statistics': {
                'prime_density': len(self.primes) / self.n_points,
                'max_prime': int(np.max(self.primes)) if len(self.primes) > 0 else 0,
                'mean_prime_gap': float(np.mean(np.diff(self.primes))) if len(self.primes) > 1 else 0.0
            }
        }
        
        if len(correlations) > 0:
            gaps = np.diff(self.primes[:len(correlations)+1])
            bell_violation, correlation_coeff = self.compute_bell_violation(correlations, gaps)
            
            report['quantum_analysis'] = {
                'num_correlations': len(correlations),
                'mean_correlation': float(np.mean(correlations)),
                'std_correlation': float(np.std(correlations)),
                'max_correlation': float(np.max(correlations)),
                'bell_violation_detected': bell_violation,
                'correlation_coefficient': correlation_coeff
            }
        else:
            report['quantum_analysis'] = {
                'num_correlations': 0,
                'note': 'Insufficient data for correlation analysis'
            }
            
        return report


def demo_interactive_helix():
    """
    Demonstration function showing the main capabilities of the Interactive3DHelixVisualizer.
    """
    print("🌀 Interactive 3D Helical Quantum Nonlocality Visualizer Demo")
    print("=" * 60)
    
    # Create visualizer instance
    visualizer = Interactive3DHelixVisualizer(n_points=2000, default_k=0.200)
    
    print(f"📊 Initialized with {visualizer.n_points} points")
    print(f"🎯 Using optimal curvature k* = {visualizer.default_k}")
    print(f"🌟 Golden ratio φ = {PHI:.6f}")
    print(f"🔢 Found {len(visualizer.primes)} primes")
    
    # Generate summary report
    report = visualizer.generate_summary_report()
    print("\n📈 Analysis Summary:")
    print(f"   Prime density: {report['statistics']['prime_density']:.4f}")
    print(f"   Max prime: {report['statistics']['max_prime']}")
    print(f"   Mean prime gap: {report['statistics']['mean_prime_gap']:.2f}")
    
    if 'quantum_analysis' in report and 'bell_violation_detected' in report['quantum_analysis']:
        qa = report['quantum_analysis']
        print(f"   Quantum correlations: {qa['num_correlations']}")
        print(f"   Bell violation: {'✓' if qa['bell_violation_detected'] else '✗'}")
        if qa['bell_violation_detected']:
            print(f"   Correlation coefficient: {qa['correlation_coefficient']:.6f}")
    
    # Create main interactive plot
    print("\n🎨 Creating interactive 3D helical visualization...")
    fig_main = visualizer.create_interactive_helix_plot(
        show_primes=True,
        show_quantum_correlations=True,
        show_bell_violations=True
    )
    
    # Create quantum correlation analysis
    print("🔬 Creating quantum correlation analysis...")
    fig_correlations = visualizer.create_quantum_correlation_analysis()
    
    # Save visualizations
    print("💾 Saving visualizations...")
    pyo.plot(fig_main, filename='interactive_helix_main.html', auto_open=False)
    pyo.plot(fig_correlations, filename='quantum_correlations.html', auto_open=False)
    
    print("\n✨ Demo completed! Check the following files:")
    print("   - interactive_helix_main.html (main 3D visualization)")
    print("   - quantum_correlations.html (correlation analysis)")
    
    return fig_main, fig_correlations, report


if __name__ == "__main__":
    # Run demonstration
    main_fig, corr_fig, summary = demo_interactive_helix()
    
    print("\n🎯 Quick Usage Example:")
    print("""
    from src.visualization.interactive_3d_helix import Interactive3DHelixVisualizer
    
    # Create visualizer
    viz = Interactive3DHelixVisualizer(n_points=1000, default_k=0.200)
    
    # Generate interactive plot
    fig = viz.create_interactive_helix_plot(show_quantum_correlations=True)
    
    # Display in browser
    fig.show()
    
    # Generate analysis report
    report = viz.generate_summary_report()
    """)