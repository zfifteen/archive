"""
Advanced Hologram Visualizations for Z Framework

This module provides advanced geometric visualizations including logarithmic spirals,
Gaussian prime spirals, modular tori, and 5D projections for the Z Framework.
The code is modular and supports interactive exploration of geometric phenomena
relevant to number theory and the Z framework.

Classes:
    AdvancedHologramVisualizer: Main controller for all visualizations
    ZetaShift: Base class for Z framework computations
    NumberLineZetaShift: Number line specific implementations

Examples:
    # Basic usage
    visualizer = AdvancedHologramVisualizer(n_points=1000)
    visualizer.visualize_all()
    
    # Interactive exploration
    visualizer.interactive_exploration()
    
    # Specific visualizations
    visualizer.logarithmic_spiral(spiral_rate=0.2, height_scale='sqrt')
    visualizer.gaussian_prime_spiral(angle_increment='golden')
    visualizer.modular_torus(mod1=17, mod2=23, torus_ratio=3.0)
    visualizer.projection_5d(projection_type='helical')
"""

from abc import ABC, abstractmethod
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.special  # For zeta function
from scipy import constants  # If needed, though commented
import sys
import os

# Add the core modules to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

try:
    from domain import UniversalZetaShift
    from axioms import universal_invariance
    CORE_MODULES_AVAILABLE = True
except ImportError:
    CORE_MODULES_AVAILABLE = False
    print("Warning: Core Z framework modules not available. Using local implementations.")

# Set matplotlib backend for headless environments
matplotlib_backend = 'Agg'  # Use non-interactive backend
plt.switch_backend(matplotlib_backend)

class ZetaShift(ABC):
    """
    Abstract base for ZetaShift, embodying Z = A(B/C) across domains.
    Enhanced with golden ratio transformations and 5D embeddings.
    """
    def __init__(self, observed_quantity: float, rate: float, invariant: float = 299792458.0):
        self.observed_quantity = observed_quantity
        self.rate = rate
        self.INVARIANT = invariant
        self.PHI = (1 + math.sqrt(5)) / 2  # Golden ratio

    @abstractmethod
    def compute_z(self) -> float:
        """Compute domain-specific Z."""
        pass

    def golden_ratio_transform(self, k: float = 3.33) -> float:
        """Apply golden ratio curvature transformation θ'(n,k) = φ·{n/φ}^k"""
        if self.observed_quantity <= 0:
            return 0.0
        residue = (self.observed_quantity % self.PHI) / self.PHI
        return self.PHI * (residue ** k)

    def embed_5d(self) -> tuple:
        """Create 5D helical embedding (x, y, z, w, u)"""
        n = self.observed_quantity
        phi = self.PHI
        theta_d = self.golden_ratio_transform()
        theta_e = self.golden_ratio_transform(k=2.0)
        
        # 5D coordinates following Z framework
        x = math.sqrt(n) * math.cos(theta_d)
        y = math.sqrt(n) * math.sin(theta_e)
        z = self.compute_z() / (math.e ** 2)  # Frame normalized
        w = math.log(n + 1) if n > 0 else 0  # Invariant dimension
        u = self.observed_quantity / self.INVARIANT  # Relativistic dimension
        
        return (x, y, z, w, u)

    @staticmethod
    def is_prime(num: int) -> bool:
        """Utility to check primality for flagging or adjustments."""
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

class NumberLineZetaShift(ZetaShift):
    """
    ZetaShift for the number line: Z = n (v_earth / c), with v_earth fixed to CMB velocity.
    Optional prime gap adjustment amplifies Z for prime resonance.
    """
    def __init__(self, n: float, rate: float = 369820.0, invariant: float = 299792458.0, use_prime_gap_adjustment: bool = False):
        super().__init__(n, rate, invariant)
        self.use_prime_gap_adjustment = use_prime_gap_adjustment

    def compute_z(self) -> float:
        base_z = self.observed_quantity * (self.rate / self.INVARIANT)
        if self.use_prime_gap_adjustment:
            gap = self._compute_prime_gap(int(self.observed_quantity))
            base_z *= (1 + gap / self.observed_quantity if self.observed_quantity != 0 else 1)
        return base_z

    def _compute_prime_gap(self, n: int) -> float:
        """Compute gap to next prime (0 if not prime)."""
        if not self.is_prime(n):
            return 0.0
        next_prime = n + 1
        while not self.is_prime(next_prime):
            next_prime += 1
        return next_prime - n

class AdvancedHologramVisualizer:
    """
    Advanced geometric visualizations for the Z Framework.
    
    This class provides modular, configurable visualizations including:
    - Enhanced logarithmic spirals with golden ratio transforms
    - Gaussian prime spirals with variable parameters  
    - Configurable modular tori with multiple bases
    - 5D projections using helical embeddings
    - Interactive parameter exploration
    
    Attributes:
        n_points (int): Number of points to compute (default: 5000)
        helix_freq (float): Frequency for helical coordinates (default: 0.1003033)
        use_log_scale (bool): Whether to use logarithmic scaling (default: False)
        figure_size (tuple): Size for matplotlib figures (default: (12, 8))
    """
    
    def __init__(self, n_points: int = 5000, helix_freq: float = 0.1003033, 
                 use_log_scale: bool = False, figure_size: tuple = (12, 8)):
        self.n_points = n_points
        self.helix_freq = helix_freq
        self.use_log_scale = use_log_scale
        self.figure_size = figure_size
        
        # Pre-compute base data
        self._compute_base_data()
        
        # Visualization parameters
        self.prime_color = 'red'
        self.prime_marker = '*'
        self.prime_size = 50
        self.nonprime_color = 'blue'
        self.nonprime_alpha = 0.3
        self.nonprime_size = 10

    def _compute_base_data(self):
        """Compute base numerical data for visualizations."""
        # Generate integer sequence
        self.n = np.arange(1, self.n_points)
        
        # Compute primality
        self.primality = np.vectorize(ZetaShift.is_prime)(self.n)
        
        # Y-values: choose raw, log, or polynomial
        if self.use_log_scale:
            self.y_raw = np.log(self.n, where=(self.n > 1), out=np.zeros_like(self.n, dtype=float))
        else:
            self.y_raw = self.n * (self.n / math.pi)
        
        # Apply ZetaShift transform
        self.y = vectorized_zeta(self.y_raw, use_gap=False)
        
        # Z-values for helix
        self.z = np.sin(math.pi * self.helix_freq * self.n)
        
        # Split into primes vs non-primes
        self.x_primes = self.n[self.primality]
        self.y_primes = self.y[self.primality]
        self.z_primes = self.z[self.primality]
        
        self.x_nonprimes = self.n[~self.primality]
        self.y_nonprimes = self.y[~self.primality]
        self.z_nonprimes = self.z[~self.primality]

    def prime_geometry_3d(self, save_path: str = None) -> plt.Figure:
        """
        Create 3D prime geometry visualization with ZetaShift transforms.
        
        Args:
            save_path (str, optional): Path to save the figure
            
        Returns:
            plt.Figure: The created figure
        """
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')
        
        ax.scatter(self.x_nonprimes, self.y_nonprimes, self.z_nonprimes, 
                  c=self.nonprime_color, alpha=self.nonprime_alpha, 
                  s=self.nonprime_size, label='Non-primes')
        ax.scatter(self.x_primes, self.y_primes, self.z_primes, 
                  c=self.prime_color, marker=self.prime_marker, 
                  s=self.prime_size, label='Primes')
        
        ax.set_xlabel('n (Position)')
        ax.set_ylabel('Scaled Value')
        ax.set_zlabel('Helical Coord')
        ax.set_title('3D Prime Geometry Visualization')
        ax.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig

    def logarithmic_spiral(self, spiral_rate: float = 0.1, height_scale: str = 'sqrt', 
                          projection: str = '3d', save_path: str = None) -> plt.Figure:
        """
        Enhanced logarithmic spiral with configurable parameters.
        
        Args:
            spiral_rate (float): Rate of spiral growth (default: 0.1)
            height_scale (str): Height scaling method: 'sqrt', 'log', 'linear' (default: 'sqrt')
            projection (str): Projection type: '3d', '2d' (default: '3d')
            save_path (str, optional): Path to save the figure
            
        Returns:
            plt.Figure: The created figure
        """
        fig = plt.figure(figsize=self.figure_size)
        
        # Compute spiral coordinates
        angle = self.n * spiral_rate * math.pi
        radius = np.log(self.n)
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        # Configurable height scaling
        if height_scale == 'sqrt':
            z = np.sqrt(self.n)
        elif height_scale == 'log':
            z = np.log(self.n)
        elif height_scale == 'linear':
            z = self.n / 100
        else:
            z = np.sqrt(self.n)
            
        if projection == '3d':
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(x[~self.primality], y[~self.primality], z[~self.primality], 
                      c=self.nonprime_color, alpha=self.nonprime_alpha, s=self.nonprime_size)
            ax.scatter(x[self.primality], y[self.primality], z[self.primality], 
                      c=self.prime_color, marker=self.prime_marker, s=self.prime_size, label='Primes')
            ax.set_zlabel(f'{height_scale.capitalize()}(n)')
        else:
            ax = fig.add_subplot(111)
            ax.scatter(x[~self.primality], y[~self.primality], 
                      c=self.nonprime_color, alpha=self.nonprime_alpha, s=self.nonprime_size)
            ax.scatter(x[self.primality], y[self.primality], 
                      c=self.prime_color, marker=self.prime_marker, s=self.prime_size, label='Primes')
        
        ax.set_title(f'Logarithmic Spiral (rate={spiral_rate}, height={height_scale})')
        ax.set_xlabel('X (Real)')
        ax.set_ylabel('Y (Imaginary)')
        ax.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig

    def gaussian_prime_spiral(self, angle_increment: str = 'golden', 
                            connection_lines: bool = True, save_path: str = None) -> plt.Figure:
        """
        Enhanced Gaussian prime spirals with configurable angle increments.
        
        Args:
            angle_increment (str): Type of angle increment: 'golden', 'pi', 'custom' (default: 'golden')
            connection_lines (bool): Whether to draw connection lines between primes (default: True)
            save_path (str, optional): Path to save the figure
            
        Returns:
            plt.Figure: The created figure
        """
        fig = plt.figure(figsize=self.figure_size)
        ax = fig.add_subplot(111, projection='3d')
        
        # Configurable angle increments
        if angle_increment == 'golden':
            phi = (1 + math.sqrt(5)) / 2
            angle_step_prime = math.pi / phi
            angle_step_nonprime = math.pi / (phi * 2)
        elif angle_increment == 'pi':
            angle_step_prime = math.pi / 2
            angle_step_nonprime = math.pi / 8
        else:  # custom
            angle_step_prime = math.pi / 3
            angle_step_nonprime = math.pi / 6
            
        angles = np.cumsum(np.where(self.primality, angle_step_prime, angle_step_nonprime))
        radii = np.sqrt(self.n)
        
        x = radii * np.cos(angles)
        y = radii * np.sin(angles)
        z = np.where(self.primality, np.log(self.n), self.n / (self.n_points / 10))
        
        ax.scatter(x[~self.primality], y[~self.primality], z[~self.primality], 
                  c=self.nonprime_color, alpha=self.nonprime_alpha, s=15, label='Non-Primes')
        ax.scatter(x[self.primality], y[self.primality], z[self.primality], 
                  c=self.prime_color, marker=self.prime_marker, s=100, label='Primes')
        
        # Optional connection lines between primes
        if connection_lines:
            prime_mask = self.primality.copy()
            prime_mask[0] = False
            ax.plot(x[prime_mask], y[prime_mask], z[prime_mask], 'r-', alpha=0.3)
        
        ax.set_title(f'Gaussian Prime Spirals ({angle_increment} angle increment)')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Height')
        ax.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig

    def modular_torus(self, mod1: int = 17, mod2: int = 23, 
                     torus_ratio: float = 3.0, residue_filter: int = 6,
                     save_path: str = None) -> plt.Figure:
        """
        Enhanced modular torus visualization with configurable parameters.
        
        Args:
            mod1 (int): First modular base (default: 17)
            mod2 (int): Second modular base (default: 23)
            torus_ratio (float): Ratio of minor to major radius (default: 3.0)
            residue_filter (int): Residue class filter (default: 6)
            save_path (str, optional): Path to save the figure
            
        Returns:
            plt.Figure: The created figure
        """
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Torus parameters
        R = 10  # Major radius
        r = R / torus_ratio  # Minor radius
        
        # Modular coordinates
        theta = 2 * np.pi * (self.n % mod1) / mod1
        phi = 2 * np.pi * (self.n % mod2) / mod2
        
        # Torus coordinates
        x = (R + r * np.cos(theta)) * np.cos(phi)
        y = (R + r * np.cos(theta)) * np.sin(phi)
        z = r * np.sin(theta)
        
        # Residue class coloring
        res_class = self.n % residue_filter
        colors = np.where(self.primality, 'red', 
                         np.where((res_class == 1) | (res_class == residue_filter-1), 'blue', 'gray'))
        
        # Plot points
        ax.scatter(x[~self.primality], y[~self.primality], z[~self.primality], 
                  c=colors[~self.primality], alpha=0.5, s=15)
        ax.scatter(x[self.primality], y[self.primality], z[self.primality], 
                  c='gold', marker='*', s=100, edgecolor='red')
        
        # Draw torus wireframe
        theta_t = np.linspace(0, 2 * np.pi, 50)
        phi_t = np.linspace(0, 2 * np.pi, 50)
        theta_t, phi_t = np.meshgrid(theta_t, phi_t)
        x_t = (R + r * np.cos(theta_t)) * np.cos(phi_t)
        y_t = (R + r * np.cos(theta_t)) * np.sin(phi_t)
        z_t = r * np.sin(theta_t)
        ax.plot_wireframe(x_t, y_t, z_t, color='gray', alpha=0.1)
        
        ax.set_title(f'Modular Prime Torus (mod {mod1} & {mod2}, ratio={torus_ratio})')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.view_init(30, 45)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig

    def projection_5d(self, projection_type: str = 'helical', 
                     dimensions: tuple = (0, 1, 2), save_path: str = None) -> plt.Figure:
        """
        5D projections using helical embeddings from the Z framework.
        
        Args:
            projection_type (str): Type of projection: 'helical', 'orthogonal', 'perspective' (default: 'helical')
            dimensions (tuple): Which 3 dimensions to project (default: (0, 1, 2))
            save_path (str, optional): Path to save the figure
            
        Returns:
            plt.Figure: The created figure
        """
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Compute 5D embeddings for each point
        embeddings = []
        for i, n_val in enumerate(self.n):
            zeta_shift = NumberLineZetaShift(n_val)
            coords_5d = zeta_shift.embed_5d()
            embeddings.append(coords_5d)
        
        embeddings = np.array(embeddings)
        
        # Extract the requested 3 dimensions
        x_proj = embeddings[:, dimensions[0]]
        y_proj = embeddings[:, dimensions[1]]
        z_proj = embeddings[:, dimensions[2]]
        
        # Apply projection transformation
        if projection_type == 'helical':
            # Apply helical transformation using golden ratio
            phi = (1 + math.sqrt(5)) / 2
            transformation_angle = self.n * math.pi / phi
            x_proj = x_proj * np.cos(transformation_angle) - y_proj * np.sin(transformation_angle)
            y_proj = x_proj * np.sin(transformation_angle) + y_proj * np.cos(transformation_angle)
        elif projection_type == 'perspective':
            # Apply perspective projection from 5D to 3D
            w_coord = embeddings[:, 3] if len(embeddings[0]) > 3 else np.ones_like(x_proj)
            perspective_factor = 1.0 / (1.0 + 0.1 * w_coord)
            x_proj *= perspective_factor
            y_proj *= perspective_factor
            z_proj *= perspective_factor
        # orthogonal is the default (no additional transformation)
        
        # Plot with prime highlighting
        ax.scatter(x_proj[~self.primality], y_proj[~self.primality], z_proj[~self.primality],
                  c=self.nonprime_color, alpha=self.nonprime_alpha, s=15, label='Non-Primes')
        ax.scatter(x_proj[self.primality], y_proj[self.primality], z_proj[self.primality],
                  c=self.prime_color, marker=self.prime_marker, s=100, 
                  edgecolor='gold', linewidth=1, label='Primes')
        
        # Add geodesic lines for structure visualization
        prime_indices = np.where(self.primality)[0]
        if len(prime_indices) > 1:
            for i in range(len(prime_indices) - 1):
                idx1, idx2 = prime_indices[i], prime_indices[i + 1]
                ax.plot([x_proj[idx1], x_proj[idx2]], 
                       [y_proj[idx1], y_proj[idx2]], 
                       [z_proj[idx1], z_proj[idx2]], 
                       'r-', alpha=0.2, linewidth=0.5)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig

    def riemann_zeta_landscape(self, real_range: tuple = (0.1, 1.0), 
                              imag_range: tuple = (10, 50), resolution: int = 100,
                              save_path: str = None) -> plt.Figure:
        """
        Enhanced Riemann zeta landscape visualization.
        
        Args:
            real_range (tuple): Range for real part of s (default: (0.1, 1.0))
            imag_range (tuple): Range for imaginary part of s (default: (10, 50))
            resolution (int): Grid resolution (default: 100)
            save_path (str, optional): Path to save the figure
            
        Returns:
            plt.Figure: The created figure
        """
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        real = np.linspace(real_range[0], real_range[1], resolution)
        imag = np.linspace(imag_range[0], imag_range[1], resolution)
        Re, Im = np.meshgrid(real, imag)
        s = Re + 1j * Im
        
        # Compute zeta values with error handling
        try:
            zeta_vals = np.vectorize(scipy.special.zeta)(s)
            zeta_mag = np.abs(zeta_vals)
            ax.plot_surface(Re, Im, np.log(zeta_mag), cmap='viridis', alpha=0.7)
        except:
            print("Warning: Could not compute zeta surface. Continuing with prime points only.")
        
        # Add prime points on critical line
        prime_indices = np.where(self.primality)[0]
        for idx in prime_indices[:min(300, len(prime_indices))]:
            s_val = 0.5 + 1j * self.n[idx]
            try:
                z_val = scipy.special.zeta(s_val)
                ax.scatter(0.5, self.n[idx], np.log(np.abs(z_val)), 
                          c='red', s=50, edgecolor='gold')
            except:
                continue
        
        ax.set_title('Riemann Zeta Landscape with Primes on Critical Line')
        ax.set_xlabel('Real Part')
        ax.set_ylabel('Imaginary Part')
        ax.set_zlabel('log|ζ(s)|')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        return fig

    def interactive_exploration(self, save_plots: bool = False, output_dir: str = "./hologram_output"):
        """
        Interactive exploration of all visualization types with parameter variations.
        
        Args:
            save_plots (bool): Whether to save all plots (default: False)
            output_dir (str): Directory to save plots (default: "./hologram_output")
        """
        if save_plots:
            import os
            os.makedirs(output_dir, exist_ok=True)
        
        print("Z Framework Advanced Hologram Visualizations")
        print("=" * 50)
        
        # 1. Basic 3D Prime Geometry
        print("1. Generating 3D Prime Geometry...")
        fig1 = self.prime_geometry_3d(
            save_path=f"{output_dir}/prime_geometry_3d.png" if save_plots else None
        )
        plt.close(fig1)
        
        # 2. Logarithmic Spirals with different parameters
        print("2. Generating Logarithmic Spirals...")
        spiral_configs = [
            {'spiral_rate': 0.1, 'height_scale': 'sqrt'},
            {'spiral_rate': 0.2, 'height_scale': 'log'},
            {'spiral_rate': 0.05, 'height_scale': 'linear'}
        ]
        
        for i, config in enumerate(spiral_configs):
            fig = self.logarithmic_spiral(
                **config,
                save_path=f"{output_dir}/logarithmic_spiral_{i+1}.png" if save_plots else None
            )
            plt.close(fig)
        
        # 3. Gaussian Prime Spirals
        print("3. Generating Gaussian Prime Spirals...")
        angle_types = ['golden', 'pi', 'custom']
        for angle_type in angle_types:
            fig = self.gaussian_prime_spiral(
                angle_increment=angle_type,
                save_path=f"{output_dir}/gaussian_spiral_{angle_type}.png" if save_plots else None
            )
            plt.close(fig)
        
        # 4. Modular Tori with different parameters
        print("4. Generating Modular Tori...")
        torus_configs = [
            {'mod1': 17, 'mod2': 23, 'torus_ratio': 3.0},
            {'mod1': 11, 'mod2': 13, 'torus_ratio': 2.5},
            {'mod1': 7, 'mod2': 19, 'torus_ratio': 4.0}
        ]
        
        for i, config in enumerate(torus_configs):
            fig = self.modular_torus(
                **config,
                save_path=f"{output_dir}/modular_torus_{i+1}.png" if save_plots else None
            )
            plt.close(fig)
        
        # 5. 5D Projections
        print("5. Generating 5D Projections...")
        projection_configs = [
            {'projection_type': 'helical', 'dimensions': (0, 1, 2)},
            {'projection_type': 'orthogonal', 'dimensions': (1, 2, 3)},
            {'projection_type': 'perspective', 'dimensions': (0, 2, 4)}
        ]
        
        for i, config in enumerate(projection_configs):
            try:
                fig = self.projection_5d(
                    **config,
                    save_path=f"{output_dir}/projection_5d_{i+1}.png" if save_plots else None
                )
                plt.close(fig)
            except Exception as e:
                print(f"Warning: Could not generate 5D projection {i+1}: {e}")
        
        # 6. Riemann Zeta Landscape
        print("6. Generating Riemann Zeta Landscape...")
        try:
            fig = self.riemann_zeta_landscape(
                save_path=f"{output_dir}/zeta_landscape.png" if save_plots else None
            )
            plt.close(fig)
        except Exception as e:
            print(f"Warning: Could not generate zeta landscape: {e}")
        
        print("\nVisualization generation completed!")
        if save_plots:
            print(f"Plots saved to: {output_dir}")

    def visualize_all(self, save_plots: bool = False, output_dir: str = "./hologram_output"):
        """
        Generate all visualizations with default parameters.
        
        Args:
            save_plots (bool): Whether to save plots to files (default: False)
            output_dir (str): Directory to save plots (default: "./hologram_output")
        """
        self.interactive_exploration(save_plots=save_plots, output_dir=output_dir)

    def get_statistics(self) -> dict:
        """
        Get statistical information about the computed data.
        
        Returns:
            dict: Dictionary containing various statistics
        """
        prime_count = np.sum(self.primality)
        total_count = len(self.n)
        prime_density = prime_count / total_count
        
        # Compute 5D embeddings for statistical analysis
        try:
            sample_size = min(1000, len(self.n))
            sample_indices = np.random.choice(len(self.n), sample_size, replace=False)
            embeddings = []
            
            for idx in sample_indices:
                zeta_shift = NumberLineZetaShift(self.n[idx])
                coords_5d = zeta_shift.embed_5d()
                embeddings.append(coords_5d)
            
            embeddings = np.array(embeddings)
            embedding_stats = {
                'mean': np.mean(embeddings, axis=0).tolist(),
                'std': np.std(embeddings, axis=0).tolist(),
                'min': np.min(embeddings, axis=0).tolist(),
                'max': np.max(embeddings, axis=0).tolist()
            }
        except Exception:
            embedding_stats = None
        
        return {
            'n_points': total_count,
            'prime_count': int(prime_count),
            'prime_density': float(prime_density),
            'helix_frequency': self.helix_freq,
            'use_log_scale': self.use_log_scale,
            'embedding_statistics': embedding_stats,
            'prime_indices': np.where(self.primality)[0][:100].tolist()  # First 100 primes
        }

# Zeta-based transformer function (compatibility with original)
def zeta_transform(value: float, rate: float = math.e, invariant: float = math.e, use_gap: bool = False) -> float:
    """Compatibility function for zeta transformations."""
    shift = NumberLineZetaShift(value, rate=rate, invariant=invariant, use_prime_gap_adjustment=use_gap)
    return shift.compute_z()

# Vectorized version for arrays
vectorized_zeta = np.vectorize(zeta_transform)

def main():
    """
    Main function demonstrating all visualization capabilities.
    """
    print("Z Framework Advanced Hologram Visualizations")
    print("=" * 50)
    print("\nInitializing visualizer...")
    
    # Create visualizer with moderate number of points for demo
    visualizer = AdvancedHologramVisualizer(n_points=2000)
    
    print(f"Computing base data for {visualizer.n_points} points...")
    
    # Get statistics
    stats = visualizer.get_statistics()
    print(f"\nStatistics:")
    print(f"- Total points: {stats['n_points']}")
    print(f"- Prime count: {stats['prime_count']}")
    print(f"- Prime density: {stats['prime_density']:.4f}")
    
    print("\nRunning interactive exploration (saving plots)...")
    visualizer.interactive_exploration(save_plots=True)
    
    print("\nDemonstration completed successfully!")

if __name__ == "__main__":
    main()