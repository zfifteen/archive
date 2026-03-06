#!/usr/bin/env python3
"""
Z5D Mandelbulb Integration Example
===================================

Demonstrates how to integrate Z5D curvature-guided ray-marching
into existing graphics pipelines and applications.
"""

import numpy as np
from typing import Tuple, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from z5d_curvature import (
    kappa_3d,
    z5d_step_size,
    standard_step_size,
    mandelbulb_distance_estimator,
    raymarch_scene
)


class Z5DRenderer:
    """
    Example renderer class showing Z5D integration.
    
    This class demonstrates how to use Z5D curvature for:
    - Adaptive ray-marching
    - LOD (level of detail) selection
    - Sample distribution optimization
    """
    
    def __init__(self, use_z5d: bool = True, geodesic_multiplier: float = 10.0):
        """
        Initialize renderer.
        
        Args:
            use_z5d: Enable Z5D adaptive stepping
            geodesic_multiplier: Step size multiplier for smooth regions
        """
        self.use_z5d = use_z5d
        self.geodesic_multiplier = geodesic_multiplier
        self.stats = {
            'total_rays': 0,
            'total_iterations': 0,
            'hits': 0
        }
    
    def render_pixel(self, ray_origin: np.ndarray, 
                     ray_direction: np.ndarray,
                     power: float = 8.0) -> Tuple[Optional[float], int]:
        """
        Render a single pixel using ray-marching.
        
        Args:
            ray_origin: Camera position [x, y, z]
            ray_direction: Ray direction (normalized) [dx, dy, dz]
            power: Mandelbulb power
            
        Returns:
            (distance, iterations) or (None, iterations) if miss
        """
        result = raymarch_scene(
            ray_origin, 
            ray_direction,
            use_z5d=self.use_z5d,
            power=power
        )
        
        # Update statistics
        self.stats['total_rays'] += 1
        self.stats['total_iterations'] += result.iterations
        if result.hit:
            self.stats['hits'] += 1
        
        return (result.distance if result.hit else None, result.iterations)
    
    def get_lod_level(self, position: np.ndarray) -> int:
        """
        Determine level-of-detail based on Z5D curvature.
        
        High curvature areas get higher LOD (more detail).
        
        Args:
            position: 3D position
            
        Returns:
            LOD level (0-3, higher = more detail)
        """
        k = kappa_3d(position)
        
        # Map curvature to LOD levels
        if k > 0.5:
            return 3  # Maximum detail
        elif k > 0.2:
            return 2
        elif k > 0.05:
            return 1
        else:
            return 0  # Minimum detail
    
    def adaptive_sample_count(self, position: np.ndarray, 
                             base_samples: int = 16) -> int:
        """
        Compute adaptive sample count for path tracing.
        
        Args:
            position: 3D position
            base_samples: Base sample count
            
        Returns:
            Adaptive sample count
        """
        k = kappa_3d(position)
        
        # Exponential scaling based on curvature
        # High k → more samples needed
        multiplier = 1.0 + 3.0 * np.exp(k)
        
        return int(base_samples * multiplier)
    
    def get_statistics(self) -> dict:
        """Get rendering statistics."""
        if self.stats['total_rays'] == 0:
            return self.stats
        
        avg_iterations = self.stats['total_iterations'] / self.stats['total_rays']
        hit_rate = self.stats['hits'] / self.stats['total_rays']
        
        return {
            **self.stats,
            'avg_iterations': avg_iterations,
            'hit_rate': hit_rate
        }
    
    def reset_statistics(self):
        """Reset rendering statistics."""
        self.stats = {
            'total_rays': 0,
            'total_iterations': 0,
            'hits': 0
        }


def example_basic_usage():
    """Basic usage example."""
    print("\n" + "=" * 70)
    print("Example 1: Basic Ray-Marching")
    print("=" * 70)
    
    # Create renderer
    renderer = Z5DRenderer(use_z5d=True)
    
    # Define camera and ray
    camera_pos = np.array([0.0, 0.0, 3.0])
    ray_dir = np.array([0.0, 0.0, -1.0])  # Looking toward origin
    
    # Render pixel
    distance, iterations = renderer.render_pixel(camera_pos, ray_dir, power=8.0)
    
    if distance is not None:
        hit_point = camera_pos + ray_dir * distance
        print(f"  Hit at distance: {distance:.4f}")
        print(f"  Hit point: {hit_point}")
        print(f"  Iterations: {iterations}")
    else:
        print(f"  Miss (iterations: {iterations})")
    
    stats = renderer.get_statistics()
    print(f"  Average iterations: {stats['avg_iterations']:.1f}")


def example_comparison():
    """Compare Z5D vs standard rendering."""
    print("\n" + "=" * 70)
    print("Example 2: Method Comparison")
    print("=" * 70)
    
    # Test rays
    test_rays = [
        (np.array([0.0, 0.0, 3.0]), np.array([0.0, 0.0, -1.0])),  # Center
        (np.array([1.5, 1.5, 3.0]), np.array([-0.3, -0.3, -0.9])),  # Off-center
        (np.array([2.0, 0.0, 2.0]), np.array([-0.7, 0.0, -0.7])),  # Side
    ]
    
    # Z5D renderer
    z5d_renderer = Z5DRenderer(use_z5d=True)
    
    # Standard renderer
    std_renderer = Z5DRenderer(use_z5d=False)
    
    print("\n  Tracing 3 test rays...")
    print()
    
    for i, (origin, direction) in enumerate(test_rays):
        # Normalize direction
        direction = direction / np.linalg.norm(direction)
        
        # Render with both methods
        z5d_dist, z5d_iter = z5d_renderer.render_pixel(origin, direction)
        std_dist, std_iter = std_renderer.render_pixel(origin, direction)
        
        speedup = std_iter / z5d_iter if z5d_iter > 0 else 0
        
        print(f"  Ray {i+1}:")
        print(f"    Z5D:      {z5d_iter:3d} iterations")
        print(f"    Standard: {std_iter:3d} iterations")
        print(f"    Speedup:  {speedup:5.2f}×")
        print()
    
    # Overall statistics
    z5d_stats = z5d_renderer.get_statistics()
    std_stats = std_renderer.get_statistics()
    
    overall_speedup = std_stats['avg_iterations'] / z5d_stats['avg_iterations']
    
    print("  Overall:")
    print(f"    Z5D avg:      {z5d_stats['avg_iterations']:6.1f} iterations")
    print(f"    Standard avg: {std_stats['avg_iterations']:6.1f} iterations")
    print(f"    Speedup:      {overall_speedup:6.2f}×")


def example_adaptive_lod():
    """Demonstrate adaptive LOD based on curvature."""
    print("\n" + "=" * 70)
    print("Example 3: Adaptive Level of Detail")
    print("=" * 70)
    
    renderer = Z5DRenderer(use_z5d=True)
    
    # Test positions at different distances from fractal
    test_positions = [
        np.array([0.0, 0.0, 0.0]),    # Origin (complex)
        np.array([1.5, 1.5, 1.5]),    # Near fractal
        np.array([5.0, 5.0, 5.0]),    # Far away (smooth)
    ]
    
    print("\n  Computing LOD levels for test positions...")
    print()
    
    for i, pos in enumerate(test_positions):
        lod = renderer.get_lod_level(pos)
        k = kappa_3d(pos)
        samples = renderer.adaptive_sample_count(pos)
        
        print(f"  Position {i+1}: {pos}")
        print(f"    Curvature κ(p): {k:7.4f}")
        print(f"    LOD level:      {lod}")
        print(f"    Sample count:   {samples}")
        print()


def example_batch_rendering():
    """Demonstrate batch rendering with statistics."""
    print("\n" + "=" * 70)
    print("Example 4: Batch Rendering")
    print("=" * 70)
    
    renderer = Z5DRenderer(use_z5d=True)
    
    # Generate random rays on hemisphere
    num_rays = 100
    np.random.seed(42)
    
    camera_pos = np.array([0.0, 0.0, 3.0])
    
    print(f"\n  Rendering {num_rays} rays...")
    
    for i in range(num_rays):
        # Random direction toward lower hemisphere
        theta = np.random.uniform(-0.5, 0.5)
        phi = np.random.uniform(-0.5, 0.5)
        
        direction = np.array([
            np.sin(theta),
            np.sin(phi),
            -np.sqrt(1 - np.sin(theta)**2 - np.sin(phi)**2)
        ])
        
        renderer.render_pixel(camera_pos, direction)
    
    # Print statistics
    stats = renderer.get_statistics()
    
    print()
    print(f"  Total rays:         {stats['total_rays']}")
    print(f"  Total iterations:   {stats['total_iterations']}")
    print(f"  Average iterations: {stats['avg_iterations']:.1f}")
    print(f"  Hit rate:           {stats['hit_rate']:.1%}")
    print(f"  Efficiency:         {stats['avg_iterations']:.1f} iters/ray")


def main():
    """Run all examples."""
    print()
    print("=" * 70)
    print("Z5D Mandelbulb Integration Examples")
    print("=" * 70)
    print()
    print("These examples demonstrate how to integrate Z5D curvature-guided")
    print("ray-marching into your own graphics pipelines and applications.")
    
    # Run examples
    example_basic_usage()
    example_comparison()
    example_adaptive_lod()
    example_batch_rendering()
    
    print()
    print("=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print()
    print("Integration tips:")
    print("  1. Use kappa_3d() to compute curvature at any 3D point")
    print("  2. Use z5d_step_size() for adaptive ray-marching step sizes")
    print("  3. Adjust geodesic_multiplier (5-20) to tune speed vs safety")
    print("  4. Higher curvature = more complexity = need more samples/detail")
    print()


if __name__ == '__main__':
    main()
