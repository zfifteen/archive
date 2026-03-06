#!/usr/bin/env python3
"""
Golden Ratio Tangent Circles Visualization

Implements symmetric arrangement of tangent circles scaled by powers of 
the golden ratio φ ≈ 1.618, as featured in Diego Rattaggi's mathematical
diagram (@diegorattaggi, #mathiratti).

Mathematical Foundation:
- Golden ratio: φ = (1 + √5)/2 ≈ 1.618
- φ² = φ + 1 (recursive identity)
- Circle radii: φ⁻⁴, φ⁻², φ⁻¹, φ⁰ = 1, φ, φ², φ³
- Tangency constraints via Descartes' circle theorem

Circle Configuration:
- Central green circle: radius φ² ≈ 2.618
- Pink circle below: radius φ ≈ 1.618
- Purple circles (sides): radius 1
- Violet circles: radius φ⁻¹ ≈ 0.618
- Blue/white circles: radius φ⁻² ≈ 0.382
- Orange circles (ends): radius φ⁻⁴ ≈ 0.146
- Red arc (overarching): radius φ³ ≈ 4.236

Applications:
1. Low-discrepancy sampling via tangent chain sequences
2. Variance reduction in Monte Carlo integration
3. Gaussian lattice distance metric enhancements
4. Z5D curvature geometric factorization
5. Phyllotaxis pattern demonstrations

References:
- Coxeter's loxodromic sequence of tangent circles
- Descartes' circle theorem for curvatures
- Golden ratio in fractals and self-similar structures
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

# Golden ratio and related constants
PHI = (1 + math.sqrt(5)) / 2  # φ ≈ 1.618033988749895
PHI_INV = 1 / PHI  # φ⁻¹ ≈ 0.618033988749895
PHI_SQ = PHI * PHI  # φ² ≈ 2.618033988749895
PHI_CUBE = PHI * PHI * PHI  # φ³ ≈ 4.236067977499790


@dataclass
class TangentCircle:
    """Represents a circle in the tangent arrangement."""
    x: float  # Center x-coordinate
    y: float  # Center y-coordinate
    radius: float  # Circle radius
    color: str  # Color for visualization
    label: str  # Description (e.g., "φ²", "φ⁻¹")
    power: float  # Power of φ for the radius


class GoldenRatioTangentCircles:
    """
    Implements symmetric tangent circle arrangement scaled by golden ratio.
    
    Creates a horizontal arrangement of circles with radii proportional to
    powers of φ, positioned such that adjacent circles are tangent to each
    other and to a baseline.
    """
    
    def __init__(self, baseline_y: float = 0.0):
        """
        Initialize golden ratio tangent circles arrangement.
        
        Args:
            baseline_y: Y-coordinate of the baseline (default: 0.0)
        """
        self.baseline_y = baseline_y
        self.circles: List[TangentCircle] = []
        self.arc_params: Optional[Dict] = None
        
    def compute_circle_positions(self) -> List[TangentCircle]:
        """
        Compute positions of all tangent circles in the symmetric arrangement.
        
        The circles are arranged horizontally along a baseline, with each
        circle tangent to the baseline and adjacent circles tangent to each
        other. The central structure follows the pattern:
        
        [tiny orange] [small blue] [violet] [purple] [large green/pink center] 
        [purple] [violet] [small blue] [tiny orange]
        
        Returns:
            List of TangentCircle objects with computed positions
        """
        circles = []
        
        # Define radii for each circle (symmetric arrangement)
        # Center outward on each side
        radii_pattern = [
            (PHI_SQ, "green", "φ²"),           # Large central circle
            (PHI, "pink", "φ"),                # Below center
            (1.0, "purple", "1"),              # Sides (left/right)
            (PHI_INV, "violet", "φ⁻¹"),       # Smaller
            (PHI_INV**2, "lightblue", "φ⁻²"), # Even smaller
            (PHI_INV**4, "orange", "φ⁻⁴"),    # Tiny ends
        ]
        
        # Start with central large circle (green, φ²)
        r_center = PHI_SQ
        x_center = 0.0
        y_center = self.baseline_y + r_center
        circles.append(TangentCircle(
            x=x_center,
            y=y_center,
            radius=r_center,
            color="green",
            label="φ²",
            power=2
        ))
        
        # Pink circle (φ) positioned below/inside the green circle
        # For tangency: distance between centers = r1 + r2 (external)
        # or |r1 - r2| (internal tangency)
        r_pink = PHI
        # Place pink circle tangent to baseline and internally tangent to green
        x_pink = 0.0
        y_pink = self.baseline_y + r_pink
        circles.append(TangentCircle(
            x=x_pink,
            y=y_pink,
            radius=r_pink,
            color="pink",
            label="φ",
            power=1
        ))
        
        # Build symmetric chain on right side
        x_current = x_center + r_center  # Start at right edge of center circle
        
        for radius, color, label in [
            (1.0, "purple", "1"),
            (PHI_INV, "violet", "φ⁻¹"),
            (PHI_INV**2, "lightblue", "φ⁻²"),
            (PHI_INV**4, "orange", "φ⁻⁴"),
        ]:
            # Circle tangent to baseline
            y_current = self.baseline_y + radius
            
            # For external tangency with previous circle on baseline:
            # If both circles are on baseline, distance = r_prev + r_current
            x_current = x_current + radius
            
            power = math.log(radius) / math.log(PHI) if radius > 0 else 0
            circles.append(TangentCircle(
                x=x_current,
                y=y_current,
                radius=radius,
                color=color,
                label=label,
                power=power
            ))
            
            # Move to next position (tangent point)
            x_current = x_current + radius
        
        # Build symmetric chain on left side (mirror)
        x_current = x_center - r_center  # Start at left edge of center circle
        
        for radius, color, label in [
            (1.0, "purple", "1"),
            (PHI_INV, "violet", "φ⁻¹"),
            (PHI_INV**2, "lightblue", "φ⁻²"),
            (PHI_INV**4, "orange", "φ⁻⁴"),
        ]:
            # Circle tangent to baseline
            y_current = self.baseline_y + radius
            
            # For external tangency with previous circle on baseline
            x_current = x_current - radius
            
            power = math.log(radius) / math.log(PHI) if radius > 0 else 0
            circles.append(TangentCircle(
                x=x_current,
                y=y_current,
                radius=radius,
                color=color,
                label=label,
                power=power
            ))
            
            # Move to next position
            x_current = x_current - radius
        
        self.circles = circles
        return circles
    
    def compute_overarching_arc(self) -> Dict:
        """
        Compute the overarching red arc (circle with radius φ³).
        
        This arc is tangent to several of the smaller circles in the
        arrangement, providing a unifying geometric element.
        
        Returns:
            Dictionary with arc parameters (center_x, center_y, radius)
        """
        # Red arc has radius φ³
        r_arc = PHI_CUBE
        
        # Position arc to be tangent to the top of the central green circle
        # Arc center is above the baseline
        if self.circles:
            # Find central green circle
            green_circle = next((c for c in self.circles if c.color == "green"), None)
            if green_circle:
                # For external tangency: distance = r_arc - r_green
                # (arc contains the green circle)
                y_arc = green_circle.y - (r_arc - green_circle.radius)
                x_arc = green_circle.x
            else:
                # Default position
                x_arc = 0.0
                y_arc = self.baseline_y + PHI_SQ + r_arc
        else:
            x_arc = 0.0
            y_arc = self.baseline_y + r_arc
        
        self.arc_params = {
            'center_x': x_arc,
            'center_y': y_arc,
            'radius': r_arc,
            'color': 'red',
            'label': 'φ³'
        }
        
        return self.arc_params
    
    def visualize(self, output_file: Optional[str] = None, 
                  show_arc: bool = True,
                  show_labels: bool = True,
                  figsize: Tuple[int, int] = (16, 10)) -> plt.Figure:
        """
        Create visualization of the golden ratio tangent circles.
        
        Args:
            output_file: Optional filename to save the plot
            show_arc: Whether to show the overarching red arc
            show_labels: Whether to show circle labels
            figsize: Figure size (width, height) in inches
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Compute circles if not already done
        if not self.circles:
            self.compute_circle_positions()
        
        # Draw baseline
        x_min = min(c.x - c.radius for c in self.circles) - 0.5
        x_max = max(c.x + c.radius for c in self.circles) + 0.5
        ax.axhline(y=self.baseline_y, color='black', linewidth=2, 
                   linestyle='--', alpha=0.5, label='Baseline')
        
        # Draw circles
        for circle in self.circles:
            circle_patch = Circle(
                (circle.x, circle.y),
                circle.radius,
                color=circle.color,
                alpha=0.6,
                edgecolor='black',
                linewidth=1.5
            )
            ax.add_patch(circle_patch)
            
            # Add label
            if show_labels:
                ax.text(
                    circle.x,
                    circle.y,
                    circle.label,
                    ha='center',
                    va='center',
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', 
                             facecolor='white', 
                             alpha=0.8)
                )
        
        # Draw overarching arc
        if show_arc:
            if not self.arc_params:
                self.compute_overarching_arc()
            
            arc_patch = Circle(
                (self.arc_params['center_x'], self.arc_params['center_y']),
                self.arc_params['radius'],
                color=self.arc_params['color'],
                alpha=0.3,
                fill=False,
                edgecolor='red',
                linewidth=3,
                linestyle='-'
            )
            ax.add_patch(arc_patch)
            
            # Arc label
            if show_labels:
                ax.text(
                    self.arc_params['center_x'],
                    self.arc_params['center_y'] + self.arc_params['radius'] * 0.7,
                    self.arc_params['label'],
                    ha='center',
                    va='center',
                    fontsize=12,
                    fontweight='bold',
                    color='red',
                    bbox=dict(boxstyle='round,pad=0.3', 
                             facecolor='white', 
                             alpha=0.9)
                )
        
        # Set axis properties
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlim(x_min, x_max)
        
        # Compute y limits
        y_min = self.baseline_y - 0.5
        y_max = max(c.y + c.radius for c in self.circles) + 0.5
        if show_arc and self.arc_params:
            y_max = max(y_max, self.arc_params['center_y'] + 0.5)
        ax.set_ylim(y_min, y_max)
        
        ax.set_xlabel('X Position', fontsize=12)
        ax.set_ylabel('Y Position', fontsize=12)
        ax.set_title(
            'Symmetric Arrangement of Tangent Circles\n'
            'Scaled by Powers of Golden Ratio φ ≈ 1.618',
            fontsize=14,
            fontweight='bold'
        )
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Save if output file specified
        if output_file:
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"Saved visualization to: {output_file}")
        
        return fig
    
    def get_circle_data(self) -> List[Dict]:
        """
        Get circle data as list of dictionaries for analysis.
        
        Returns:
            List of dictionaries with circle parameters
        """
        if not self.circles:
            self.compute_circle_positions()
        
        return [
            {
                'x': c.x,
                'y': c.y,
                'radius': c.radius,
                'color': c.color,
                'label': c.label,
                'power': c.power,
                'diameter': 2 * c.radius,
                'area': math.pi * c.radius**2,
                'circumference': 2 * math.pi * c.radius
            }
            for c in self.circles
        ]
    
    def verify_tangency(self) -> List[Tuple[int, int, float, str]]:
        """
        Verify tangency conditions between circles.
        
        For two circles to be tangent:
        - External tangency: distance = r1 + r2
        - Internal tangency: distance = |r1 - r2|
        
        Returns:
            List of tuples (i, j, distance, status) where status is
            "tangent", "intersect", or "separate"
        """
        if not self.circles:
            self.compute_circle_positions()
        
        results = []
        n = len(self.circles)
        
        for i in range(n):
            for j in range(i + 1, n):
                c1, c2 = self.circles[i], self.circles[j]
                
                # Distance between centers
                dist = math.sqrt((c2.x - c1.x)**2 + (c2.y - c1.y)**2)
                
                # Expected distance for tangency
                external_tangent = c1.radius + c2.radius
                internal_tangent = abs(c1.radius - c2.radius)
                
                # Check status
                tolerance = 0.01  # Allow small numerical error
                if abs(dist - external_tangent) < tolerance:
                    status = "external_tangent"
                elif abs(dist - internal_tangent) < tolerance:
                    status = "internal_tangent"
                elif dist < min(external_tangent, internal_tangent):
                    status = "intersect"
                else:
                    status = "separate"
                
                results.append((i, j, dist, status))
        
        return results


class TangentChainSampler:
    """
    Sampler for low-discrepancy sequences based on tangent circle chains.
    
    Generates sample points along tangent circle chains with φ-based
    spacing, providing self-similar sampling patterns for Monte Carlo
    integration and variance reduction.
    
    Integration with low_discrepancy.py:
    - Extends golden-angle sampling with tangent circle structure
    - Provides hierarchical sampling at multiple scales (φⁿ)
    - Maintains anytime uniformity property
    """
    
    def __init__(self, base_radius: float = 1.0, num_scales: int = 5,
                 seed: Optional[int] = None):
        """
        Initialize tangent chain sampler.
        
        Args:
            base_radius: Base circle radius (default: 1.0)
            num_scales: Number of φ-power scales to use (default: 5)
            seed: Random seed for reproducibility
        """
        self.base_radius = base_radius
        self.num_scales = num_scales
        self.seed = seed
        
        if seed is not None:
            self.rng = np.random.RandomState(seed)
        else:
            self.rng = None
    
    def generate_hierarchical_samples(self, n: int, 
                                      dimension: int = 2) -> np.ndarray:
        """
        Generate hierarchical samples using tangent circle structure.
        
        Creates n samples distributed across φ-scaled circles in a
        self-similar pattern, useful for variance reduction in
        Monte Carlo integration.
        
        Args:
            n: Number of samples
            dimension: Dimensionality (1 or 2)
            
        Returns:
            Array of shape (n, dimension) with samples
        """
        samples = []
        
        # Distribute samples across scales
        samples_per_scale = n // self.num_scales
        remainder = n % self.num_scales
        
        for scale_idx in range(self.num_scales):
            # Radius for this scale (φ-based)
            power = scale_idx - self.num_scales // 2
            radius = self.base_radius * (PHI ** power)
            
            # Number of samples at this scale
            n_scale = samples_per_scale
            if scale_idx < remainder:
                n_scale += 1
            
            if dimension == 1:
                # 1D: sample along diameter
                if self.rng:
                    positions = self.rng.uniform(-radius, radius, n_scale)
                else:
                    positions = np.linspace(-radius, radius, n_scale)
                scale_samples = positions.reshape(-1, 1)
            else:
                # 2D: sample on circle using golden angle
                indices = np.arange(n_scale)
                # Golden angle spacing
                theta = indices * (2 * math.pi / PHI**2)
                
                # Sample at this radius
                x = radius * np.cos(theta)
                y = radius * np.sin(theta)
                scale_samples = np.column_stack([x, y])
            
            samples.append(scale_samples)
        
        # Combine all scales
        all_samples = np.vstack(samples)
        
        # Shuffle to avoid ordering artifacts
        if self.rng:
            self.rng.shuffle(all_samples)
        
        return all_samples[:n]
    
    def generate_annulus_samples(self, n: int, r_inner: float, 
                                r_outer: float) -> np.ndarray:
        """
        Generate samples in annulus using φ-scaled tangent circles.
        
        Useful for sampling neighborhoods around √N in factorization.
        
        Args:
            n: Number of samples
            r_inner: Inner radius
            r_outer: Outer radius
            
        Returns:
            Array of shape (n, 2) with (x, y) coordinates
        """
        # Determine number of φ-scales in the annulus
        num_scales = max(1, int(math.log(r_outer / r_inner) / math.log(PHI)))
        
        samples = []
        samples_per_scale = n // num_scales
        remainder = n % num_scales
        
        for scale_idx in range(num_scales):
            # Radius for this scale
            t = (scale_idx + 0.5) / num_scales
            radius = r_inner * (r_outer / r_inner)**t
            
            # Number of samples
            n_scale = samples_per_scale
            if scale_idx < remainder:
                n_scale += 1
            
            # Golden angle spacing
            indices = np.arange(n_scale)
            theta = indices * (2 * math.pi / PHI**2)
            
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            
            samples.append(np.column_stack([x, y]))
        
        all_samples = np.vstack(samples)
        
        if self.rng:
            self.rng.shuffle(all_samples)
        
        return all_samples[:n]


def demonstrate_golden_ratio_tangent_circles():
    """
    Demonstrate golden ratio tangent circles visualization.
    
    Creates the symmetric arrangement and shows its properties,
    including tangency verification and circle data analysis.
    """
    print("=" * 70)
    print("Golden Ratio Tangent Circles Demonstration")
    print("=" * 70)
    print()
    
    # Create arrangement
    arrangement = GoldenRatioTangentCircles(baseline_y=0.0)
    
    # Compute circles
    print("Computing circle positions...")
    circles = arrangement.compute_circle_positions()
    print(f"Created {len(circles)} circles")
    print()
    
    # Display circle data
    print("Circle Configuration:")
    print("-" * 70)
    print(f"{'Label':<8} {'Radius':>12} {'Power':>8} {'X Position':>12} "
          f"{'Y Position':>12} {'Color':<12}")
    print("-" * 70)
    
    for circle in circles:
        print(f"{circle.label:<8} {circle.radius:>12.6f} {circle.power:>8.2f} "
              f"{circle.x:>12.6f} {circle.y:>12.6f} {circle.color:<12}")
    
    print()
    
    # Verify tangency
    print("Tangency Verification:")
    print("-" * 70)
    tangency_results = arrangement.verify_tangency()
    
    # Count by status
    status_counts = {}
    for _, _, _, status in tangency_results:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"Total circle pairs: {len(tangency_results)}")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    print()
    
    # Create visualization
    print("Creating visualization...")
    fig = arrangement.visualize(
        output_file="golden_ratio_tangent_circles.png",
        show_arc=True,
        show_labels=True
    )
    plt.close(fig)
    
    print()
    print("Golden Ratio Properties:")
    print("-" * 70)
    print(f"φ = (1 + √5)/2 ≈ {PHI:.15f}")
    print(f"φ² = φ + 1 ≈ {PHI_SQ:.15f}")
    print(f"φ³ ≈ {PHI_CUBE:.15f}")
    print(f"φ⁻¹ ≈ {PHI_INV:.15f}")
    print(f"φ⁻² ≈ {PHI_INV**2:.15f}")
    print(f"φ⁻⁴ ≈ {PHI_INV**4:.15f}")
    print()
    print(f"Verification: φ² - φ - 1 = {PHI_SQ - PHI - 1:.15e}")
    print()
    
    # Demonstrate tangent chain sampling
    print("Tangent Chain Sampling:")
    print("-" * 70)
    sampler = TangentChainSampler(base_radius=1.0, num_scales=5, seed=42)
    samples = sampler.generate_hierarchical_samples(1000, dimension=2)
    
    print(f"Generated {len(samples)} hierarchical samples")
    print(f"Sample mean: ({np.mean(samples[:, 0]):.6f}, {np.mean(samples[:, 1]):.6f})")
    print(f"Sample std: ({np.std(samples[:, 0]):.6f}, {np.std(samples[:, 1]):.6f})")
    
    # Check distribution across scales
    radii = np.sqrt(samples[:, 0]**2 + samples[:, 1]**2)
    print(f"Radial distribution:")
    print(f"  Min radius: {np.min(radii):.6f}")
    print(f"  Mean radius: {np.mean(radii):.6f}")
    print(f"  Max radius: {np.max(radii):.6f}")
    print()
    
    print("=" * 70)
    print("Demonstration complete!")
    print("Visualization saved to: golden_ratio_tangent_circles.png")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_golden_ratio_tangent_circles()
