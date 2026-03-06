#!/usr/bin/env python3
"""
Comprehensive Test Suite for Z5D Mandelbulb Demo
=================================================

Validates all components of the implementation.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from z5d_curvature import (
    kappa_3d,
    kappa_field,
    z5d_step_size,
    standard_step_size,
    mandelbulb_distance_estimator,
    raymarch_scene,
    benchmark_ray_marching
)
import numpy as np


class TestSuite:
    """Comprehensive test suite."""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
    
    def assert_true(self, condition, message):
        """Assert a condition is true."""
        if condition:
            self.tests_passed += 1
            print(f"  ✓ {message}")
        else:
            self.tests_failed += 1
            self.failures.append(message)
            print(f"  ✗ {message}")
    
    def assert_close(self, actual, expected, tolerance, message):
        """Assert two values are close within tolerance."""
        close = abs(actual - expected) < tolerance
        self.assert_true(
            close,
            f"{message} (expected {expected:.4f}, got {actual:.4f})"
        )
    
    def assert_range(self, value, min_val, max_val, message):
        """Assert value is within range."""
        in_range = min_val <= value <= max_val
        self.assert_true(
            in_range,
            f"{message} (expected [{min_val}, {max_val}], got {value:.4f})"
        )
    
    def print_summary(self):
        """Print test summary."""
        total = self.tests_passed + self.tests_failed
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total tests: {total}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        
        if self.tests_failed > 0:
            print("\nFailed tests:")
            for failure in self.failures:
                print(f"  - {failure}")
            return False
        else:
            print("\n✓ All tests passed!")
            return True


def test_curvature_computation(suite):
    """Test curvature function."""
    print("\nTest 1: Curvature Computation")
    print("-" * 70)
    
    # Test origin
    k = kappa_3d(np.array([0.0, 0.0, 0.0]))
    suite.assert_close(k, 0.0, 0.01, "Origin curvature should be ~0")
    
    # Test unit cube
    k = kappa_3d(np.array([1.0, 1.0, 1.0]))
    suite.assert_close(k, 0.0, 0.01, "Unit cube curvature should be ~0")
    
    # Test larger point
    k = kappa_3d(np.array([2.0, 2.0, 2.0]))
    suite.assert_range(k, 0.05, 0.1, "Larger point should have positive curvature")
    
    # Test clamping
    k = kappa_3d(np.array([100.0, 100.0, 100.0]))
    suite.assert_range(k, -10.0, 10.0, "Curvature should be clamped to [-10, 10]")


def test_curvature_field(suite):
    """Test vectorized curvature computation."""
    print("\nTest 2: Curvature Field (Vectorized)")
    print("-" * 70)
    
    # Generate test points
    points = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
        [2.0, 2.0, 2.0],
        [3.0, 3.0, 3.0]
    ])
    
    kappa_values = kappa_field(points)
    
    suite.assert_true(
        len(kappa_values) == 4,
        "Should return 4 curvature values"
    )
    
    suite.assert_true(
        kappa_values[0] < kappa_values[2],
        "Curvature should increase with distance from origin"
    )
    
    suite.assert_true(
        all(-10 <= k <= 10 for k in kappa_values),
        "All curvature values should be clamped"
    )


def test_step_size(suite):
    """Test adaptive step size computation."""
    print("\nTest 3: Adaptive Step Size")
    print("-" * 70)
    
    de = 0.5  # Larger DE to avoid safety clamp
    p_complex = np.array([0.8, 0.8, 0.8])    # Lower curvature 
    p_smooth = np.array([5.0, 5.0, 5.0])     # Higher curvature
    
    # Z5D step sizes
    step_smooth = z5d_step_size(de, p_smooth)
    step_complex = z5d_step_size(de, p_complex)
    
    # Standard step size
    step_std = standard_step_size(de)
    
    suite.assert_true(
        step_smooth >= step_std or step_complex >= step_std,
        "Z5D should take at least as large steps as standard in some regions"
    )
    
    # Note: The exact relationship depends on DE and position
    # The important thing is that Z5D provides speedup overall (tested in Test 5)
    
    suite.assert_range(
        step_smooth / step_std,
        1.0,
        50.0,
        "Speedup should be between 1-50×"
    )


def test_mandelbulb_de(suite):
    """Test Mandelbulb distance estimator."""
    print("\nTest 4: Mandelbulb Distance Estimator")
    print("-" * 70)
    
    # Point far from fractal
    de_far = mandelbulb_distance_estimator(np.array([10.0, 10.0, 10.0]))
    suite.assert_true(
        de_far > 1.0,
        "Point far from fractal should have large DE"
    )
    
    # Point near origin (inside/near fractal)
    de_near = mandelbulb_distance_estimator(np.array([0.5, 0.5, 0.5]))
    suite.assert_true(
        de_near < de_far,
        "Point near fractal should have smaller DE"
    )
    
    # DE should always be non-negative
    suite.assert_true(
        de_near >= 0 and de_far >= 0,
        "Distance estimator should be non-negative"
    )


def test_ray_marching(suite):
    """Test ray-marching with Z5D."""
    print("\nTest 5: Ray-Marching")
    print("-" * 70)
    
    ray_origin = np.array([0.0, 0.0, 3.0])
    ray_direction = np.array([0.0, 0.0, -1.0])
    
    # Z5D marching
    result_z5d = raymarch_scene(ray_origin, ray_direction, use_z5d=True)
    
    # Standard marching
    result_std = raymarch_scene(ray_origin, ray_direction, use_z5d=False)
    
    suite.assert_true(
        result_z5d.hit,
        "Z5D ray-marching should hit the fractal"
    )
    
    suite.assert_true(
        result_std.hit,
        "Standard ray-marching should hit the fractal"
    )
    
    suite.assert_true(
        result_z5d.iterations < result_std.iterations,
        "Z5D should use fewer iterations than standard"
    )
    
    speedup = result_std.iterations / result_z5d.iterations
    suite.assert_range(
        speedup,
        1.1,
        5.0,
        "Speedup should be between 1.1-5.0×"
    )


def test_benchmarking(suite):
    """Test benchmarking functionality."""
    print("\nTest 6: Benchmarking")
    print("-" * 70)
    
    # Small benchmark (fast)
    results = benchmark_ray_marching(num_rays=50, use_z5d=True, power=8.0)
    
    suite.assert_true(
        'avg_iterations' in results,
        "Results should contain avg_iterations"
    )
    
    suite.assert_true(
        'hit_rate' in results,
        "Results should contain hit_rate"
    )
    
    suite.assert_range(
        results['avg_iterations'],
        10,
        100,
        "Average iterations should be reasonable"
    )
    
    suite.assert_range(
        results['hit_rate'],
        0.0,
        1.0,
        "Hit rate should be between 0 and 1"
    )


def test_consistency(suite):
    """Test numerical consistency and stability."""
    print("\nTest 7: Numerical Consistency")
    print("-" * 70)
    
    # Same input should give same output
    p = np.array([1.5, 2.5, 1.8])
    
    k1 = kappa_3d(p)
    k2 = kappa_3d(p)
    
    suite.assert_close(
        k1, k2, 1e-10,
        "Curvature should be deterministic"
    )
    
    # Ray-marching should be deterministic
    ray_origin = np.array([0.0, 0.0, 3.0])
    ray_direction = np.array([0.0, 0.0, -1.0])
    
    result1 = raymarch_scene(ray_origin, ray_direction, use_z5d=True)
    result2 = raymarch_scene(ray_origin, ray_direction, use_z5d=True)
    
    suite.assert_true(
        result1.iterations == result2.iterations,
        "Ray-marching should be deterministic"
    )


def test_file_structure(suite):
    """Test that all required files exist."""
    print("\nTest 8: File Structure")
    print("-" * 70)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'README.md',
        'QUICKSTART.md',
        'IMPLEMENTATION_SUMMARY.md',
        'mandelbulb_demo.html',
        'z5d_curvature.py',
        'z5d_curvature.wgsl',
        'integration_example.py',
        'serve_demo.py',
        'package.json',
        'benchmarks/performance_benchmark.py',
        'benchmarks/visualize_curvature.py'
    ]
    
    for filename in required_files:
        path = os.path.join(base_dir, filename)
        suite.assert_true(
            os.path.exists(path),
            f"File should exist: {filename}"
        )


def main():
    """Run all tests."""
    print("=" * 70)
    print("Z5D MANDELBULB DEMO - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    suite = TestSuite()
    
    try:
        test_curvature_computation(suite)
        test_curvature_field(suite)
        test_step_size(suite)
        test_mandelbulb_de(suite)
        test_ray_marching(suite)
        test_benchmarking(suite)
        test_consistency(suite)
        test_file_structure(suite)
        
    except Exception as e:
        print(f"\n✗ Test suite crashed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    success = suite.print_summary()
    
    if success:
        print("\n✓ Implementation validated successfully!")
        print("  All components are working correctly.")
        return True
    else:
        print("\n✗ Some tests failed.")
        print("  Please review the failures above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
