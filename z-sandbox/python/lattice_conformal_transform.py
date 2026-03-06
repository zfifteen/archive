#!/usr/bin/env python3
"""
Lattice Conformal Transformation Module

Implements conformal transformations (z → z², z → 1/z) for Gaussian integer
lattice visualizations. Provides image warping capabilities to illustrate
geometric properties of factorization on the complex plane.

Mathematical Foundation:
    Conformal transformations preserve angles but not necessarily distances.
    Key transformations:
    1. Squaring: z → z² (doubles arguments, squares moduli)
    2. Inversion: z → 1/z (inverts moduli, negates arguments)

Applications:
    - Visualizing anisotropic distances in Pollard's Rho
    - Illustrating Gaussian lattice structure transformations
    - Educational demonstrations of complex analysis
    - Enhancing factor candidate visualization near √N

Integration with z-sandbox:
    - Extends visualization tools from multiplication_viz_factor.py
    - Complements Gaussian lattice theory in gaussian_lattice.py
    - Provides PNG outputs compatible with existing demo infrastructure
    - Supports barycentric coordinates and QMC-φ hybrid visualizations

Axioms followed:
1. Empirical Validation: Transform preserves conformality (Cauchy-Riemann)
2. Domain-Specific Forms: Bilinear interpolation for image sampling
3. Precision: Numerical stability with safe division checks
4. Verification: Visual outputs for manual inspection
"""

import sys
import math
from typing import Tuple, Optional, Callable, Union
from pathlib import Path

import numpy as np
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class LatticeConformalTransform:
    """
    Conformal transformation utilities for Gaussian lattice visualizations.
    
    Applies transformations z → z² and z → 1/z to lattice images,
    demonstrating geometric properties of complex mappings relevant
    to factorization algorithms.
    """
    
    def __init__(self, epsilon: float = 1e-10):
        """
        Initialize conformal transform handler.
        
        Args:
            epsilon: Threshold for numerical stability (default: 1e-10)
        """
        self.epsilon = epsilon
    
    @staticmethod
    def conformal_square(z: complex) -> complex:
        """
        Apply z → z² transformation.
        
        Derivation:
            For z = x + iy:
            z² = (x + iy)² = x² - y² + 2ixy
            
            Cauchy-Riemann verification:
            u(x,y) = x² - y²  →  u_x = 2x, u_y = -2y
            v(x,y) = 2xy      →  v_x = 2y, v_y = 2x
            Check: u_x = v_y ✓, u_y = -v_x ✓
        
        Args:
            z: Complex number
        
        Returns:
            z² (angle doubled, modulus squared)
        """
        return z * z
    
    def conformal_inversion(self, z: complex, epsilon: Optional[float] = None) -> Optional[complex]:
        """
        Apply z → 1/z transformation.
        
        Derivation:
            For z = x + iy, |z|² = x² + y²:
            1/z = (x - iy)/(x² + y²)
            
            u(x,y) = x/(x² + y²)
            v(x,y) = -y/(x² + y²)
            
            Cauchy-Riemann satisfied away from origin.
        
        Args:
            z: Complex number (non-zero)
            epsilon: Threshold for zero detection (uses instance epsilon if None)
        
        Returns:
            1/z or None if |z| < epsilon
        """
        eps = epsilon if epsilon is not None else self.epsilon
        if abs(z) < eps:
            return None
        return 1.0 / z
    
    def transform_lattice_image(
        self,
        input_path: Union[str, Path],
        transform: str = 'square',
        output_size: Tuple[int, int] = (800, 800),
        domain_range: Tuple[float, float] = (-1.0, 1.0),
        output_path: Optional[Union[str, Path]] = None,
        show_plot: bool = False
    ) -> Optional[np.ndarray]:
        """
        Apply conformal transformation to lattice visualization image.
        
        This implements the image warping described in the issue:
        1. Normalize input image to complex plane domain [-1, 1]²
        2. For each output pixel, apply inverse transform to find source
        3. Use bilinear interpolation to sample input image
        4. Generate transformed output
        
        Algorithm:
            - Forward transform: z_out = f(z_in)
            - For visualization: z_in = f^(-1)(z_out) for pulling samples
            - Square: f^(-1)(w) = √w (choose principal branch)
            - Inversion: f^(-1)(w) = 1/w (self-inverse)
        
        Args:
            input_path: Path to input image (lattice visualization)
            transform: 'square' or 'invert'
            output_size: Output image dimensions (width, height)
            domain_range: Complex plane domain (min, max)
            output_path: Optional path to save output
            show_plot: Whether to display using matplotlib
        
        Returns:
            Transformed image as numpy array, or None if PIL unavailable
        
        Example:
            >>> transformer = LatticeConformalTransform()
            >>> transformed = transformer.transform_lattice_image(
            ...     'pollard_paths.png',
            ...     transform='square',
            ...     output_path='transformed_lattice.png'
            ... )
        """
        if not PIL_AVAILABLE:
            print("Warning: PIL not available. Cannot transform images.")
            return None
        
        # Load input image
        img = Image.open(input_path).convert('RGB')
        img_array = np.array(img)
        h, w, channels = img_array.shape
        
        # Create output coordinate mesh
        r_min, r_max = domain_range
        x = np.linspace(r_min, r_max, output_size[1])
        y = np.linspace(r_min, r_max, output_size[0])
        X, Y = np.meshgrid(x, y)
        
        # Output complex coordinates
        Z_out = X + 1j * Y
        
        # Apply inverse transformation for sampling
        if transform == 'square':
            # Inverse of z² is √z (principal branch)
            Z_in = np.sqrt(Z_out)
        elif transform == 'invert':
            # Inverse of 1/z is 1/z (self-inverse)
            # Avoid division by zero
            mask = np.abs(Z_out) > self.epsilon
            Z_in = np.zeros_like(Z_out, dtype=complex)
            Z_in[mask] = 1.0 / Z_out[mask]
        else:
            raise ValueError(f"Unknown transform: {transform}. Use 'square' or 'invert'.")
        
        # Map complex coordinates to image coordinates
        # From [r_min, r_max] to [0, w-1] and [0, h-1]
        real_coords = (np.real(Z_in) - r_min) / (r_max - r_min) * (w - 1)
        imag_coords = (np.imag(Z_in) - r_min) / (r_max - r_min) * (h - 1)
        
        # Initialize output image
        transformed = np.zeros((output_size[0], output_size[1], channels), dtype=np.uint8)
        
        # Bilinear interpolation
        for i in range(output_size[0]):
            for j in range(output_size[1]):
                rx, ry = real_coords[i, j], imag_coords[i, j]
                
                # Check bounds
                if 0 <= rx < w - 1 and 0 <= ry < h - 1:
                    x0, y0 = int(rx), int(ry)
                    dx, dy = rx - x0, ry - y0
                    
                    # Bilinear interpolation coefficients
                    c00 = (1 - dx) * (1 - dy)
                    c10 = dx * (1 - dy)
                    c01 = (1 - dx) * dy
                    c11 = dx * dy
                    
                    # Sample and interpolate
                    transformed[i, j] = (
                        c00 * img_array[y0, x0] +
                        c10 * img_array[y0, x0 + 1] +
                        c01 * img_array[y0 + 1, x0] +
                        c11 * img_array[y0 + 1, x0 + 1]
                    )
        
        # Save if output path specified
        if output_path:
            output_img = Image.fromarray(transformed)
            output_img.save(output_path)
            print(f"Saved transformed image to: {output_path}")
        
        # Display if requested
        if show_plot and MATPLOTLIB_AVAILABLE:
            plt.figure(figsize=(12, 6))
            
            plt.subplot(1, 2, 1)
            plt.imshow(img_array)
            plt.title('Original Lattice Visualization')
            plt.axis('off')
            
            plt.subplot(1, 2, 2)
            plt.imshow(transformed)
            plt.title(f'Transformed ({transform})')
            plt.axis('off')
            
            plt.tight_layout()
            plt.show()
        
        return transformed
    
    def generate_lattice_grid(
        self,
        N: int,
        lattice_range: int = 10,
        output_path: Optional[Union[str, Path]] = None
    ) -> Optional[np.ndarray]:
        """
        Generate a basic Gaussian lattice grid visualization for transformation.
        
        Creates a simple grid showing lattice points near √N, suitable for
        demonstrating conformal transformations.
        
        Args:
            N: Semiprime to visualize
            lattice_range: Range of lattice coordinates
            output_path: Optional path to save grid image
        
        Returns:
            Grid image as numpy array, or None if matplotlib unavailable
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Warning: matplotlib not available.")
            return None
        
        sqrt_N = int(math.sqrt(N))
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Plot lattice points
        points = []
        for m in range(-lattice_range, lattice_range + 1):
            for n in range(-lattice_range, lattice_range + 1):
                z = complex(sqrt_N + m, n)
                points.append(z)
                ax.plot(z.real, z.imag, 'bo', markersize=3, alpha=0.6)
        
        # Highlight √N
        ax.plot(sqrt_N, 0, 'ro', markersize=10, label=f'√N ≈ {sqrt_N}')
        
        # Styling
        ax.set_xlabel('Real Axis')
        ax.set_ylabel('Imaginary Axis')
        ax.set_title(f'Gaussian Lattice Grid for N = {N}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Saved lattice grid to: {output_path}")
        
        # Convert to numpy array
        fig.canvas.draw()
        img_array = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        img_array = img_array.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        
        plt.close(fig)
        
        return img_array[:, :, :3]  # Remove alpha channel


def demo_conformal_transforms():
    """
    Demonstration of conformal transformations on lattice visualizations.
    
    Creates sample visualizations showing z → z² and z → 1/z applied to
    Gaussian integer lattice grids.
    """
    if not PIL_AVAILABLE or not MATPLOTLIB_AVAILABLE:
        print("Demo requires PIL and matplotlib.")
        return
    
    print("=" * 70)
    print("Conformal Transformation Demo")
    print("=" * 70)
    print()
    
    transformer = LatticeConformalTransform()
    
    # Test case: N = 143 = 11 × 13
    N = 143
    print(f"Generating lattice grid for N = {N} (11 × 13)")
    print()
    
    # Generate base lattice grid
    base_grid_path = '/tmp/lattice_grid_143.png'
    transformer.generate_lattice_grid(N, lattice_range=5, output_path=base_grid_path)
    
    # Apply square transformation
    print("Applying z → z² transformation...")
    transformed_square = transformer.transform_lattice_image(
        base_grid_path,
        transform='square',
        output_path='/tmp/lattice_transformed_square.png'
    )
    
    # Apply inversion transformation
    print("Applying z → 1/z transformation...")
    transformed_invert = transformer.transform_lattice_image(
        base_grid_path,
        transform='invert',
        output_path='/tmp/lattice_transformed_invert.png'
    )
    
    print()
    print("=" * 70)
    print("Conformal transformation demo complete!")
    print()
    print("Generated files:")
    print(f"  - {base_grid_path}")
    print(f"  - /tmp/lattice_transformed_square.png")
    print(f"  - /tmp/lattice_transformed_invert.png")
    print()
    print("Key observations:")
    print("  - z² doubles angles, squares moduli")
    print("  - 1/z inverts distances, preserves angles locally")
    print("  - Both preserve conformality (angle preservation)")
    print("=" * 70)


if __name__ == "__main__":
    demo_conformal_transforms()
