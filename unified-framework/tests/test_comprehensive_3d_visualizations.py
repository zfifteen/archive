#!/usr/bin/env python3
"""
Comprehensive 3D Visualization Test Suite
========================================

Advanced 3D plotting capabilities for mathematical analysis including:
- Helical embeddings with quantum correlations
- Riemann zeta zero visualizations
- Prime distribution geometric analysis
- Modular arithmetic topology
- Cross-domain physical-discrete mappings

All 3D plots are interactive (plotly) and static (matplotlib) versions.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import mpmath as mp

# Set matplotlib backend for headless environment
plt.switch_backend('Agg')
warnings.filterwarnings('ignore')

# Add src to path for imports
current_dir = Path(__file__).parent
repo_root = current_dir.parent
src_path = repo_root / 'src'
sys.path.insert(0, str(src_path))

# High precision for mathematical computations
mp.mp.dps = 50

# Mathematical constants
PHI = (1 + mp.sqrt(5)) / 2  # Golden ratio
E_SQUARED = mp.exp(2)
PI = mp.pi

class Comprehensive3DVisualizationSuite:
    """Comprehensive 3D visualization suite for mathematical analysis."""
    
    def __init__(self, plots_dir: str = None):
        """Initialize the 3D visualization suite."""
        if plots_dir is None:
            plots_dir = current_dir / 'plots' / 'comprehensive_3d'
        
        self.plots_dir = Path(plots_dir)
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different types of 3D plots
        self.subdirs = {
            'helical': self.plots_dir / 'helical_embeddings',
            'zeta': self.plots_dir / 'riemann_zeta',
            'primes': self.plots_dir / 'prime_distributions', 
            'topology': self.plots_dir / 'modular_topology',
            'physical': self.plots_dir / 'physical_discrete'
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
    
    def generate_helical_embedding_3d(self) -> bool:
        """Generate 3D helical embeddings with quantum correlations."""
        print("  - Generating 3D helical embeddings...")
        try:
            # Generate prime sequence
            primes = self._generate_primes(100)
            
            # Helical embedding parameters
            k_values = [0.1, 0.3, 0.5, 0.7]
            
            for k in k_values:
                # Compute helical coordinates
                theta = []
                r = []
                z = []
                
                for i, p in enumerate(primes):
                    # Geodesic mapping
                    t = float(PHI) * ((p % float(PHI)) / float(PHI)) ** k
                    radius = np.sqrt(p)
                    height = i * 0.1
                    
                    theta.append(t)
                    r.append(radius)
                    z.append(height)
                
                # Convert to Cartesian coordinates
                x = np.array(r) * np.cos(theta)
                y = np.array(r) * np.sin(theta)
                z = np.array(z)
                
                # Create static 3D plot
                fig = plt.figure(figsize=(12, 10))
                ax = fig.add_subplot(111, projection='3d')
                
                # Color by prime value
                colors = primes
                scatter = ax.scatter(x, y, z, c=colors, cmap='viridis', s=50, alpha=0.8)
                
                ax.set_xlabel('X (Radial)')
                ax.set_ylabel('Y (Radial)')
                ax.set_zlabel('Z (Sequential)')
                ax.set_title(f'Prime Helical Embedding 3D (k={k})')
                
                plt.colorbar(scatter, label='Prime Value')
                plt.savefig(self.subdirs['helical'] / f'prime_helix_3d_k_{k:.1f}.png',
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                # Create interactive plotly version
                fig_plotly = go.Figure()
                
                fig_plotly.add_trace(go.Scatter3d(
                    x=x, y=y, z=z,
                    mode='markers+lines',
                    marker=dict(
                        size=8,
                        color=primes,
                        colorscale='Viridis',
                        colorbar=dict(title='Prime Value'),
                        opacity=0.8
                    ),
                    line=dict(
                        color='rgba(100,100,100,0.3)',
                        width=2
                    ),
                    text=[f'Prime: {p}' for p in primes],
                    name=f'k={k}'
                ))
                
                fig_plotly.update_layout(
                    title=f'Prime Helical Embedding 3D (k={k})',
                    scene=dict(
                        xaxis_title='X (Radial)',
                        yaxis_title='Y (Radial)',
                        zaxis_title='Z (Sequential)',
                        camera=dict(
                            eye=dict(x=1.2, y=1.2, z=1.2)
                        )
                    ),
                    width=800,
                    height=600
                )
                
                fig_plotly.write_html(str(self.subdirs['helical'] / f'prime_helix_3d_k_{k:.1f}.html'))
            
            return True
            
        except Exception as e:
            print(f"    Failed: {e}")
            return False
    
    def generate_riemann_zeta_3d(self) -> bool:
        """Generate 3D visualizations of Riemann zeta zeros."""
        print("  - Generating Riemann zeta 3D visualizations...")
        try:
            # Generate first few zeta zeros (simplified approximation)
            zeta_zeros = []
            for n in range(1, 51):  # First 50 zeros
                # Approximate nth zero (this is a simplified calculation)
                t_n = 2 * np.pi * n / np.log(n) + 10  # Rough approximation
                zeta_zeros.append(t_n)
            
            # Create 3D helical embedding of zeta zeros
            x_coords = []
            y_coords = []
            z_coords = []
            
            for i, t in enumerate(zeta_zeros):
                # Map to 3D space using Z framework principles
                k = 0.3
                theta = float(PHI) * ((t % float(PHI)) / float(PHI)) ** k
                r = np.sqrt(t)
                
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                z = i * 0.5
                
                x_coords.append(x)
                y_coords.append(y)
                z_coords.append(z)
            
            # Static matplotlib plot
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            scatter = ax.scatter(x_coords, y_coords, z_coords, 
                               c=zeta_zeros, cmap='plasma', s=80, alpha=0.8)
            
            # Connect with lines to show progression
            ax.plot(x_coords, y_coords, z_coords, 'k-', alpha=0.3, linewidth=1)
            
            ax.set_xlabel('X Coordinate')
            ax.set_ylabel('Y Coordinate')
            ax.set_zlabel('Zero Index')
            ax.set_title('Riemann Zeta Zeros - 3D Helical Embedding')
            
            plt.colorbar(scatter, label='Zero Value (t)')
            plt.savefig(self.subdirs['zeta'] / 'riemann_zeta_zeros_3d.png',
                       dpi=300, bbox_inches='tight')
            plt.close()
            
            # Interactive plotly version
            fig_plotly = go.Figure()
            
            # Add scatter plot for zeros
            fig_plotly.add_trace(go.Scatter3d(
                x=x_coords, y=y_coords, z=z_coords,
                mode='markers+lines',
                marker=dict(
                    size=10,
                    color=zeta_zeros,
                    colorscale='Plasma',
                    colorbar=dict(title='Zero Value (t)'),
                    opacity=0.8
                ),
                line=dict(
                    color='rgba(50,50,50,0.3)',
                    width=3
                ),
                text=[f'Zero {i+1}: {t:.2f}' for i, t in enumerate(zeta_zeros)],
                name='Zeta Zeros'
            ))
            
            fig_plotly.update_layout(
                title='Riemann Zeta Zeros - 3D Helical Embedding (Interactive)',
                scene=dict(
                    xaxis_title='X Coordinate',
                    yaxis_title='Y Coordinate',
                    zaxis_title='Zero Index',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                width=900,
                height=700
            )
            
            fig_plotly.write_html(str(self.subdirs['zeta'] / 'riemann_zeta_zeros_3d.html'))
            
            return True
            
        except Exception as e:
            print(f"    Failed: {e}")
            return False
    
    def generate_prime_distribution_3d(self) -> bool:
        """Generate 3D prime distribution analysis."""
        print("  - Generating 3D prime distribution analysis...")
        try:
            # Generate larger prime dataset
            primes = self._generate_primes(200)
            
            # Multiple views of prime distribution
            views = [
                ('spiral', 'Prime Spiral Distribution'),
                ('gaps', 'Prime Gap Analysis 3D'),
                ('density', 'Prime Density Visualization')
            ]
            
            for view_type, title in views:
                fig = plt.figure(figsize=(12, 10))
                ax = fig.add_subplot(111, projection='3d')
                
                if view_type == 'spiral':
                    # Spiral arrangement
                    angles = np.linspace(0, 8*np.pi, len(primes))
                    radii = np.sqrt(primes)
                    heights = np.arange(len(primes))
                    
                    x = radii * np.cos(angles)
                    y = radii * np.sin(angles) 
                    z = heights
                    
                    ax.scatter(x, y, z, c=primes, cmap='viridis', s=60, alpha=0.8)
                    ax.plot(x, y, z, 'k-', alpha=0.2, linewidth=1)
                    
                elif view_type == 'gaps':
                    # Prime gaps in 3D
                    gaps = np.diff(primes)
                    x = primes[1:]
                    y = gaps
                    z = np.arange(len(gaps))
                    
                    ax.scatter(x, y, z, c=gaps, cmap='plasma', s=60, alpha=0.8)
                    
                elif view_type == 'density':
                    # Local density analysis
                    window_size = 10
                    densities = []
                    centers = []
                    
                    for i in range(window_size, len(primes) - window_size):
                        window = primes[i-window_size:i+window_size]
                        density = len(window) / (max(window) - min(window))
                        densities.append(density)
                        centers.append(primes[i])
                    
                    x = centers
                    y = densities
                    z = np.arange(len(densities))
                    
                    ax.scatter(x, y, z, c=densities, cmap='coolwarm', s=60, alpha=0.8)
                
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.set_title(title)
                
                plt.savefig(self.subdirs['primes'] / f'prime_{view_type}_3d.png',
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                # Create interactive plotly versions
                if view_type == 'spiral':
                    fig_plotly = go.Figure()
                    fig_plotly.add_trace(go.Scatter3d(
                        x=x, y=y, z=z,
                        mode='markers+lines',
                        marker=dict(size=6, color=primes, colorscale='Viridis'),
                        line=dict(width=2, color='rgba(100,100,100,0.3)'),
                        text=[f'Prime: {p}' for p in primes]
                    ))
                    
                    fig_plotly.update_layout(
                        title=title + ' (Interactive)',
                        scene=dict(
                            xaxis_title='X',
                            yaxis_title='Y', 
                            zaxis_title='Index'
                        )
                    )
                    
                    fig_plotly.write_html(str(self.subdirs['primes'] / f'prime_{view_type}_3d.html'))
            
            return True
            
        except Exception as e:
            print(f"    Failed: {e}")
            return False
    
    def generate_modular_topology_3d(self) -> bool:
        """Generate 3D modular arithmetic topology visualizations."""
        print("  - Generating 3D modular topology visualizations...")
        try:
            # Modular arithmetic patterns
            moduli = [7, 11, 13, 17]
            
            for mod in moduli:
                # Generate points on modular circle
                n_points = 100
                numbers = np.arange(1, n_points + 1)
                
                # Map to 3D torus
                angles1 = 2 * np.pi * (numbers % mod) / mod  # Major circle
                angles2 = 2 * np.pi * numbers / (n_points/5)  # Minor circle
                
                R = 3  # Major radius
                r = 1  # Minor radius
                
                x = (R + r * np.cos(angles2)) * np.cos(angles1)
                y = (R + r * np.cos(angles2)) * np.sin(angles1)
                z = r * np.sin(angles2)
                
                # Color by primality
                is_prime = [self._is_prime(n) for n in numbers]
                colors = ['red' if prime else 'blue' for prime in is_prime]
                
                # Static plot
                fig = plt.figure(figsize=(12, 10))
                ax = fig.add_subplot(111, projection='3d')
                
                for i, (xi, yi, zi, color) in enumerate(zip(x, y, z, colors)):
                    ax.scatter(xi, yi, zi, c=color, s=40, alpha=0.7)
                
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.set_title(f'Modular Topology (mod {mod}) - Primes in Red')
                
                plt.savefig(self.subdirs['topology'] / f'modular_topology_mod_{mod}_3d.png',
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                # Interactive plotly version
                fig_plotly = go.Figure()
                
                # Separate traces for primes and composites
                prime_indices = [i for i, p in enumerate(is_prime) if p]
                composite_indices = [i for i, p in enumerate(is_prime) if not p]
                
                if prime_indices:
                    fig_plotly.add_trace(go.Scatter3d(
                        x=[x[i] for i in prime_indices],
                        y=[y[i] for i in prime_indices],
                        z=[z[i] for i in prime_indices],
                        mode='markers',
                        marker=dict(size=8, color='red', opacity=0.8),
                        name='Primes',
                        text=[f'Prime: {numbers[i]}' for i in prime_indices]
                    ))
                
                if composite_indices:
                    fig_plotly.add_trace(go.Scatter3d(
                        x=[x[i] for i in composite_indices],
                        y=[y[i] for i in composite_indices],
                        z=[z[i] for i in composite_indices],
                        mode='markers',
                        marker=dict(size=6, color='blue', opacity=0.6),
                        name='Composites',
                        text=[f'Composite: {numbers[i]}' for i in composite_indices]
                    ))
                
                fig_plotly.update_layout(
                    title=f'Modular Topology (mod {mod}) - Interactive',
                    scene=dict(
                        xaxis_title='X',
                        yaxis_title='Y',
                        zaxis_title='Z',
                        aspectmode='cube'
                    ),
                    width=800,
                    height=600
                )
                
                fig_plotly.write_html(str(self.subdirs['topology'] / f'modular_topology_mod_{mod}_3d.html'))
            
            return True
            
        except Exception as e:
            print(f"    Failed: {e}")
            return False
    
    def generate_physical_discrete_3d(self) -> bool:
        """Generate 3D physical-discrete connection visualizations."""
        print("  - Generating 3D physical-discrete connections...")
        try:
            # Physical constants mapping
            c = 299792458  # Speed of light
            h = 6.626e-34  # Planck constant
            
            # Generate sequence representing physical-discrete bridge
            n_values = np.arange(1, 101)
            
            # Map to physical domain
            velocities = c * np.tanh(n_values / 50)  # Relativistic velocities
            frequencies = h * n_values ** 2  # Quantum frequencies
            energies = 0.5 * velocities ** 2 / c ** 2  # Relativistic energy approx
            
            # Create 3D phase space
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            # Color by discrete index
            scatter = ax.scatter(velocities, frequencies, energies, 
                               c=n_values, cmap='viridis', s=60, alpha=0.8)
            
            ax.set_xlabel('Velocity (m/s)')
            ax.set_ylabel('Frequency (scaled)')
            ax.set_zlabel('Energy (scaled)')
            ax.set_title('Physical-Discrete Bridge Visualization')
            
            plt.colorbar(scatter, label='Discrete Index n')
            plt.savefig(self.subdirs['physical'] / 'physical_discrete_bridge_3d.png',
                       dpi=300, bbox_inches='tight')
            plt.close()
            
            # Interactive version
            fig_plotly = go.Figure()
            
            fig_plotly.add_trace(go.Scatter3d(
                x=velocities, y=frequencies, z=energies,
                mode='markers+lines',
                marker=dict(
                    size=8,
                    color=n_values,
                    colorscale='Viridis',
                    colorbar=dict(title='Discrete Index n'),
                    opacity=0.8
                ),
                line=dict(
                    color='rgba(100,100,100,0.3)',
                    width=3
                ),
                text=[f'n={n}, v={v:.0f} m/s' for n, v in zip(n_values, velocities)],
                name='Physical-Discrete Bridge'
            ))
            
            fig_plotly.update_layout(
                title='Physical-Discrete Bridge Visualization (Interactive)',
                scene=dict(
                    xaxis_title='Velocity (m/s)',
                    yaxis_title='Frequency (scaled)',
                    zaxis_title='Energy (scaled)',
                    camera=dict(
                        eye=dict(x=1.3, y=1.3, z=1.3)
                    )
                ),
                width=900,
                height=700
            )
            
            fig_plotly.write_html(str(self.subdirs['physical'] / 'physical_discrete_bridge_3d.html'))
            
            # Create relativistic transformation visualization
            gamma_factors = 1 / np.sqrt(1 - (velocities/c)**2)
            time_dilations = gamma_factors
            length_contractions = 1 / gamma_factors
            
            fig_plotly2 = go.Figure()
            
            fig_plotly2.add_trace(go.Scatter3d(
                x=velocities/c, y=time_dilations, z=length_contractions,
                mode='markers+lines',
                marker=dict(
                    size=8,
                    color=n_values,
                    colorscale='Plasma',
                    colorbar=dict(title='Discrete Index n'),
                    opacity=0.8
                ),
                line=dict(width=3),
                text=[f'n={n}, γ={g:.2f}' for n, g in zip(n_values, gamma_factors)],
                name='Relativistic Effects'
            ))
            
            fig_plotly2.update_layout(
                title='Relativistic Transformations - Discrete Mapping',
                scene=dict(
                    xaxis_title='v/c (Relative Velocity)',
                    yaxis_title='Time Dilation (γ)',
                    zaxis_title='Length Contraction (1/γ)',
                    camera=dict(
                        eye=dict(x=1.2, y=1.2, z=1.2)
                    )
                ),
                width=900,
                height=700
            )
            
            fig_plotly2.write_html(str(self.subdirs['physical'] / 'relativistic_transformations_3d.html'))
            
            return True
            
        except Exception as e:
            print(f"    Failed: {e}")
            return False
    
    def _generate_primes(self, n: int) -> List[int]:
        """Generate first n prime numbers."""
        primes = []
        num = 2
        while len(primes) < n:
            if self._is_prime(num):
                primes.append(num)
            num += 1
        return primes
    
    def _is_prime(self, n: int) -> bool:
        """Check if number is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(np.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def run_all_3d_visualizations(self) -> Dict:
        """Run all 3D visualization generators."""
        print("🌀 Generating Comprehensive 3D Visualization Suite...")
        
        generators = [
            ('Helical Embeddings', self.generate_helical_embedding_3d),
            ('Riemann Zeta 3D', self.generate_riemann_zeta_3d),
            ('Prime Distribution 3D', self.generate_prime_distribution_3d),
            ('Modular Topology 3D', self.generate_modular_topology_3d),
            ('Physical-Discrete 3D', self.generate_physical_discrete_3d),
        ]
        
        successful = []
        failed = []
        
        for name, generator in generators:
            try:
                if generator():
                    successful.append(name)
                    print(f"  ✅ {name}")
                else:
                    failed.append(name)
                    print(f"  ❌ {name}")
            except Exception as e:
                failed.append(name)
                print(f"  ❌ {name}: {e}")
        
        return {
            'successful': successful,
            'failed': failed,
            'plots_dir': str(self.plots_dir),
            'subdirs': {k: str(v) for k, v in self.subdirs.items()}
        }


def main():
    """Main entry point for comprehensive 3D visualization suite."""
    suite = Comprehensive3DVisualizationSuite()
    results = suite.run_all_3d_visualizations()
    
    print(f"\n🌀 Comprehensive 3D Visualizations completed:")
    print(f"   ✅ Successful: {len(results['successful'])}")
    print(f"   ❌ Failed: {len(results['failed'])}")
    print(f"   📁 Plots saved to: {results['plots_dir']}")
    
    for subdir_name, subdir_path in results['subdirs'].items():
        file_count = len([f for f in Path(subdir_path).iterdir() if f.is_file()])
        print(f"      - {subdir_name}: {file_count} files")
    
    return len(results['failed']) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)