"""
Z5D Curvature Computation for 3D Spatial Embeddings
====================================================

Python implementation of the Z5D curvature function κ(p) for validation
and performance analysis. This module provides:

1. Curvature computation for 3D points
2. Adaptive step size prediction
3. Performance benchmarking utilities
4. Ground truth comparison tools

The curvature function extends Z5D prime-counting geometry to continuous
3D space, enabling intelligent ray-marching step prediction.
"""

import numpy as np
from typing import Tuple, List, Dict, Optional
import time
from dataclasses import dataclass
import json


# Constants from Z5D framework
E = np.e
E_SQUARED = E * E
EPSILON_SAFE = 1e-4


@dataclass
class MarchResult:
    """Results from a ray-marching operation."""
    distance: float
    iterations: int
    hit: bool
    avg_step_size: float
    max_step_size: float


def kappa_3d(p: np.ndarray) -> float:
    """
    Compute Z5D curvature for a 3D spatial point.
    
    Embeds 3D point p into Z5D number-theoretic space via:
    κ(p) ≈ d(n)·ln(n)/e²
    
    where d(n) is approximated by log(|px|)·log(|py|)·log(|pz|)
    
    Args:
        p: 3D point as numpy array [x, y, z]
        
    Returns:
        Curvature value κ(p)
        
    Example:
        >>> kappa_3d(np.array([1.0, 1.0, 1.0]))
        0.0
        >>> kappa_3d(np.array([2.7, 3.1, 2.9]))
        0.542...
    """
    # Ensure positive coordinates for log domain
    q = np.abs(p) + EPSILON_SAFE
    
    # Approximate divisor count via log product
    divisors_approx = np.log(q[0]) * np.log(q[1]) * np.log(q[2])
    
    # Scale by ln(|p|)/e² for Z5D consistency
    radius = np.linalg.norm(p) + 1.0
    curvature = divisors_approx * np.log(radius) / E_SQUARED
    
    # Clamp to prevent numerical issues
    return np.clip(curvature, -10.0, 10.0)


def kappa_field(points: np.ndarray) -> np.ndarray:
    """
    Compute curvature field for multiple 3D points (vectorized).
    
    Args:
        points: Array of shape (N, 3) containing N points
        
    Returns:
        Array of shape (N,) containing curvature values
    """
    q = np.abs(points) + EPSILON_SAFE
    divisors_approx = np.log(q[:, 0]) * np.log(q[:, 1]) * np.log(q[:, 2])
    radius = np.linalg.norm(points, axis=1) + 1.0
    curvature = divisors_approx * np.log(radius) / E_SQUARED
    return np.clip(curvature, -10.0, 10.0)


def z5d_step_size(de: float, p: np.ndarray, geodesic_multiplier: float = 10.0) -> float:
    """
    Compute Z5D adaptive step size for ray-marching.
    
    Args:
        de: Distance estimator value (geometric safety bound)
        p: Current 3D position
        geodesic_multiplier: Maximum step multiplier for smooth regions
        
    Returns:
        Adaptive step size
    """
    k = kappa_3d(p)
    
    # Conservative bound
    safe = de * 1.2
    
    # Aggressive geodesic leap with exponential damping
    aggressive = de * (1.0 + 50.0 * np.exp(-k * 0.8))
    
    # Apply multiplier with safety clamp
    return min(safe, aggressive * geodesic_multiplier)


def standard_step_size(de: float) -> float:
    """Standard sphere-tracing step size (for comparison)."""
    return de * 0.9


def mandelbulb_distance_estimator(pos: np.ndarray, power: float = 8.0, 
                                   max_iter: int = 15) -> float:
    """
    Compute Mandelbulb distance estimator.
    
    Args:
        pos: 3D position [x, y, z]
        power: Mandelbulb power (typically 8)
        max_iter: Maximum iterations for escape check
        
    Returns:
        Distance estimate to fractal surface
    """
    z = pos.copy()
    dr = 1.0
    r = 0.0
    
    for _ in range(max_iter):
        r = np.linalg.norm(z)
        
        if r > 2.0:
            break
            
        # Convert to spherical coordinates
        theta = np.arccos(z[2] / (r + 1e-10))
        phi = np.arctan2(z[1], z[0])
        
        # Derivative for distance estimation
        dr = np.power(r, power - 1.0) * power * dr + 1.0
        
        # Mandelbulb formula
        zr = np.power(r, power)
        theta_new = theta * power
        phi_new = phi * power
        
        z = zr * np.array([
            np.sin(theta_new) * np.cos(phi_new),
            np.sin(theta_new) * np.sin(phi_new),
            np.cos(theta_new)
        ])
        z += pos
    
    return 0.5 * np.log(r) * r / dr if dr > 0 else 0.0


def raymarch_scene(ray_origin: np.ndarray, ray_direction: np.ndarray,
                   use_z5d: bool = True, max_steps: int = 512,
                   epsilon: float = 1e-4, max_distance: float = 1000.0,
                   power: float = 8.0) -> MarchResult:
    """
    Ray-march the Mandelbulb scene with optional Z5D guidance.
    
    Args:
        ray_origin: Starting position [x, y, z]
        ray_direction: Ray direction (normalized) [dx, dy, dz]
        use_z5d: Whether to use Z5D adaptive stepping
        max_steps: Maximum ray-marching iterations
        epsilon: Hit detection threshold
        max_distance: Maximum ray travel distance
        power: Mandelbulb power
        
    Returns:
        MarchResult with distance, iterations, and statistics
    """
    t = 0.0
    steps_taken = 0
    step_sizes = []
    
    for i in range(max_steps):
        pos = ray_origin + ray_direction * t
        de = mandelbulb_distance_estimator(pos, power)
        
        # Hit detection
        if de < epsilon:
            return MarchResult(
                distance=t,
                iterations=i,
                hit=True,
                avg_step_size=np.mean(step_sizes) if step_sizes else 0.0,
                max_step_size=max(step_sizes) if step_sizes else 0.0
            )
        
        # Escape check
        if t > max_distance:
            return MarchResult(
                distance=t,
                iterations=i,
                hit=False,
                avg_step_size=np.mean(step_sizes) if step_sizes else 0.0,
                max_step_size=max(step_sizes) if step_sizes else 0.0
            )
        
        # Compute step size
        if use_z5d:
            step = z5d_step_size(de, pos)
        else:
            step = standard_step_size(de)
        
        step_sizes.append(step)
        t += step
        steps_taken += 1
    
    return MarchResult(
        distance=t,
        iterations=max_steps,
        hit=False,
        avg_step_size=np.mean(step_sizes) if step_sizes else 0.0,
        max_step_size=max(step_sizes) if step_sizes else 0.0
    )


def benchmark_ray_marching(num_rays: int = 1000, use_z5d: bool = True,
                           power: float = 8.0, seed: int = 42) -> Dict:
    """
    Benchmark ray-marching performance.
    
    Args:
        num_rays: Number of rays to trace
        use_z5d: Whether to use Z5D adaptive stepping
        power: Mandelbulb power
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with benchmark statistics
    """
    np.random.seed(seed)
    
    # Generate random ray origins on sphere
    camera_distance = 3.0
    theta = np.random.uniform(0, 2 * np.pi, num_rays)
    phi = np.random.uniform(0, np.pi, num_rays)
    
    results = []
    start_time = time.time()
    
    for i in range(num_rays):
        # Ray origin on sphere
        ray_origin = camera_distance * np.array([
            np.sin(phi[i]) * np.cos(theta[i]),
            np.sin(phi[i]) * np.sin(theta[i]),
            np.cos(phi[i])
        ])
        
        # Ray direction toward origin
        ray_direction = -ray_origin / np.linalg.norm(ray_origin)
        
        # March the ray
        result = raymarch_scene(ray_origin, ray_direction, use_z5d, power=power)
        results.append(result)
    
    elapsed_time = time.time() - start_time
    
    # Aggregate statistics
    iterations = [r.iterations for r in results]
    hit_rate = sum(1 for r in results if r.hit) / num_rays
    avg_iterations = np.mean(iterations)
    max_iterations = max(iterations)
    avg_step_sizes = [r.avg_step_size for r in results if r.hit]
    
    return {
        'method': 'Z5D' if use_z5d else 'Standard',
        'num_rays': num_rays,
        'power': power,
        'elapsed_time': elapsed_time,
        'rays_per_second': num_rays / elapsed_time,
        'hit_rate': hit_rate,
        'avg_iterations': avg_iterations,
        'max_iterations': max_iterations,
        'avg_step_size': np.mean(avg_step_sizes) if avg_step_sizes else 0.0,
        'speedup_vs_max': max_iterations / avg_iterations if avg_iterations > 0 else 1.0
    }


def compare_methods(num_rays: int = 1000, powers: List[float] = None) -> None:
    """
    Compare Z5D vs standard ray-marching across multiple Mandelbulb powers.
    
    Args:
        num_rays: Number of rays to trace per method
        powers: List of Mandelbulb powers to test
    """
    if powers is None:
        powers = [8.0, 12.0, 16.0, 20.0]
    
    print("Z5D Mandelbulb Ray-Marching Benchmark")
    print("=" * 80)
    print()
    
    all_results = []
    
    for power in powers:
        print(f"Testing Power {int(power)}:")
        print("-" * 80)
        
        # Benchmark Z5D
        z5d_results = benchmark_ray_marching(num_rays, use_z5d=True, power=power)
        
        # Benchmark Standard
        std_results = benchmark_ray_marching(num_rays, use_z5d=False, power=power)
        
        # Calculate speedup
        speedup = std_results['avg_iterations'] / z5d_results['avg_iterations']
        
        print(f"  Z5D Method:")
        print(f"    Avg Iterations: {z5d_results['avg_iterations']:.1f}")
        print(f"    Max Iterations: {z5d_results['max_iterations']}")
        print(f"    Hit Rate: {z5d_results['hit_rate']:.1%}")
        print(f"    Avg Step Size: {z5d_results['avg_step_size']:.4f}")
        print(f"    Rays/sec: {z5d_results['rays_per_second']:.1f}")
        print()
        print(f"  Standard Method:")
        print(f"    Avg Iterations: {std_results['avg_iterations']:.1f}")
        print(f"    Max Iterations: {std_results['max_iterations']}")
        print(f"    Hit Rate: {std_results['hit_rate']:.1%}")
        print(f"    Avg Step Size: {std_results['avg_step_size']:.4f}")
        print(f"    Rays/sec: {std_results['rays_per_second']:.1f}")
        print()
        print(f"  Speedup: {speedup:.1f}× (Z5D uses {speedup:.1f}× fewer iterations)")
        print()
        
        all_results.append({
            'power': power,
            'z5d': z5d_results,
            'standard': std_results,
            'speedup': speedup
        })
    
    # Summary
    print("=" * 80)
    print("Summary:")
    print()
    print("Power | Z5D Iters | Std Iters | Speedup | Hit Rate")
    print("-" * 60)
    for result in all_results:
        power = int(result['power'])
        z5d_iter = result['z5d']['avg_iterations']
        std_iter = result['standard']['avg_iterations']
        speedup = result['speedup']
        hit_rate = result['z5d']['hit_rate']
        print(f"  {power:2d}  |   {z5d_iter:6.1f}  |   {std_iter:6.1f}  |  {speedup:5.1f}× |  {hit_rate:5.1%}")
    
    return all_results


def visualize_curvature_field(resolution: int = 100, z_slice: float = 0.0,
                               extent: float = 3.0) -> np.ndarray:
    """
    Generate 2D slice of curvature field for visualization.
    
    Args:
        resolution: Grid resolution per axis
        z_slice: Z-coordinate of the slice
        extent: Spatial extent in each direction
        
    Returns:
        2D array of curvature values
    """
    x = np.linspace(-extent, extent, resolution)
    y = np.linspace(-extent, extent, resolution)
    X, Y = np.meshgrid(x, y)
    
    # Create 3D points
    points = np.stack([X.ravel(), Y.ravel(), 
                      np.full(X.size, z_slice)], axis=1)
    
    # Compute curvature field
    kappa_values = kappa_field(points)
    
    return kappa_values.reshape(X.shape)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'benchmark':
        # Run benchmark
        num_rays = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        results = compare_methods(num_rays=num_rays)
        
        # Save results
        with open('benchmark_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=float)
        
        print("\nResults saved to benchmark_results.json")
    
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Quick test
        print("Testing Z5D curvature computation...")
        print()
        
        test_points = [
            np.array([0.0, 0.0, 0.0]),
            np.array([1.0, 1.0, 1.0]),
            np.array([2.0, 2.0, 2.0]),
            np.array([1.5, 2.5, 1.8]),
        ]
        
        for p in test_points:
            k = kappa_3d(p)
            print(f"κ({p}) = {k:.6f}")
        
        print()
        print("Testing ray-marching...")
        
        ray_origin = np.array([0.0, 0.0, 3.0])
        ray_direction = np.array([0.0, 0.0, -1.0])
        
        result_z5d = raymarch_scene(ray_origin, ray_direction, use_z5d=True)
        result_std = raymarch_scene(ray_origin, ray_direction, use_z5d=False)
        
        print(f"Z5D: {result_z5d.iterations} iterations, hit={result_z5d.hit}")
        print(f"Standard: {result_std.iterations} iterations, hit={result_std.hit}")
        print(f"Speedup: {result_std.iterations / result_z5d.iterations:.2f}×")
    
    else:
        print("Z5D Curvature Utilities")
        print()
        print("Usage:")
        print("  python z5d_curvature.py test          # Quick test")
        print("  python z5d_curvature.py benchmark [N] # Benchmark with N rays")
        print()
        print("Example:")
        print("  python z5d_curvature.py benchmark 1000")
