#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplex Anchoring and Tetrahedron Integration Demo
=================================================

Demonstration of tetrahedron geometric insights integrated into the Z5D
framework for enhanced symmetry operations and prime density predictions.

This demo showcases:
1. 3D tetrahedron embedding into 5D
2. A₄ group rotational symmetries (order 12)
3. Euler formula topological constraints
4. Tetrahedron self-duality optimization
5. Integration with Stadlmann distribution level (θ ≈ 0.525)

Reference: Issue #XXX - Integrate Tetrahedron Geometric Insights
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.core.geodesic_mapping import GeodesicMapper
from src.core.params import DIST_LEVEL_STADLMANN


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def demo_basic_simplex_anchoring():
    """Demonstrate basic simplex anchoring with small prime list"""
    print_section("1. Basic Simplex Anchoring")
    
    # Initialize mapper with standard geodesic parameter
    mapper = GeodesicMapper(kappa_geo=0.3)
    
    # Small prime list for demonstration
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    print(f"\nPrime list ({len(primes)} primes): {primes}")
    
    # Apply simplex anchoring
    result = mapper.simplex_anchor(primes)
    
    # Display results
    print(f"\nEnhancement Results:")
    print(f"  Base Enhancement:    {result['base_enhancement_percent']:>10.4f}%")
    print(f"  Simplex Boost:       {result['simplex_boost_percent']:>10.4f}%")
    print(f"  Total Enhancement:   {result['enhancement_percent']:>10.4f}%")
    print(f"\nConfidence Intervals (95%):")
    print(f"  CI Lower:            {result['ci_lower']:>10.4f}%")
    print(f"  CI Upper:            {result['ci_upper']:>10.4f}%")
    print(f"\nBootstrap Statistics:")
    print(f"  Successful samples:  {result['n_bootstrap_successful']:>10d}")
    print(f"  Variance:            {result['variance']:>10.6f}")


def demo_tetrahedron_embedding():
    """Demonstrate 3D tetrahedron embedding into 5D"""
    print_section("2. Tetrahedron Embedding into 5D")
    
    mapper = GeodesicMapper()
    primes = [2, 3, 5, 7, 11]
    
    result = mapper.simplex_anchor(primes)
    vertices_5d = result['tetrahedron_vertices_5d']
    
    print("\nStandard Tetrahedron Vertices (3D):")
    print("  (1,  1,  1)")
    print("  (1, -1, -1)")
    print("  (-1, 1, -1)")
    print("  (-1,-1,  1)")
    
    print("\nEmbedded into 5D (appending orthogonal dimensions):")
    for i, vertex in enumerate(vertices_5d[:4]):
        print(f"  Vertex {i+1}: {vertex}")
    
    print("\nOrthogonal Completion (for 5D simplex):")
    for i, vertex in enumerate(vertices_5d[4:], start=5):
        print(f"  Vertex {i}: {vertex}")
    
    print(f"\nTotal vertices: {len(vertices_5d)} (4 tetrahedron + 2 orthogonal)")


def demo_symmetry_factors():
    """Demonstrate A₄ group symmetries and other factors"""
    print_section("3. Symmetry Factors and Topological Constraints")
    
    mapper = GeodesicMapper()
    primes = [2, 3, 5, 7, 11, 13, 17]
    
    result = mapper.simplex_anchor(primes)
    
    print("\nA₄ Group (Alternating Group of Degree 4):")
    print(f"  Order:               {result['tetrahedron_properties']['a4_group_order']}")
    print(f"  Symmetry Factor:     {result['a4_symmetry_factor']:.6f}")
    print(f"  Contribution:        {(result['a4_symmetry_factor']-1)*100:.2f}%")
    
    print("\nEuler Formula Topological Constraint:")
    props = result['tetrahedron_properties']
    print(f"  Vertices (V):        {props['vertices']}")
    print(f"  Edges (E):           {props['edges']}")
    print(f"  Faces (F):           {props['faces']}")
    print(f"  Euler χ = V-E+F:     {result['euler_characteristic']}")
    print(f"  Formula Verified:    {props['euler_formula_verified']}")
    print(f"  Constraint Factor:   {result['euler_constraint_factor']:.6f}")
    print(f"  Contribution:        {(result['euler_constraint_factor']-1)*100:.2f}%")
    
    print("\nTetrahedron Self-Duality:")
    print(f"  Self-Dual:           {props['self_dual']}")
    print(f"  Self-Duality Factor: {result['self_duality_factor']:.6f}")
    print(f"  Contribution:        {(result['self_duality_factor']-1)*100:.2f}%")
    
    print("\nCombined Simplex Factor:")
    print(f"  A₄ × Euler × Self-Duality:")
    print(f"  {result['a4_symmetry_factor']:.6f} × {result['euler_constraint_factor']:.6f} × {result['self_duality_factor']:.6f}")
    print(f"  = {result['combined_simplex_factor']:.6f}")
    print(f"  Total Contribution:  {(result['combined_simplex_factor']-1)*100:.2f}%")


def demo_stadlmann_integration():
    """Demonstrate integration with Stadlmann distribution level"""
    print_section("4. Stadlmann Distribution Level Integration")
    
    mapper = GeodesicMapper(kappa_geo=0.3)
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
    
    print(f"\nStadlmann Distribution Level: θ = {DIST_LEVEL_STADLMANN}")
    print(f"Prime list: {len(primes)} primes")
    
    # Compare without and with custom dist_level
    result_default = mapper.simplex_anchor(primes, dist_level=DIST_LEVEL_STADLMANN)
    result_higher = mapper.simplex_anchor(primes, dist_level=0.55)
    
    print("\nWith Stadlmann Level (θ = 0.525):")
    print(f"  Enhancement:         {result_default['enhancement_percent']:>10.4f}%")
    print(f"  Simplex Boost:       {result_default['simplex_boost_percent']:>10.4f}%")
    
    print("\nWith Higher Level (θ = 0.55):")
    print(f"  Enhancement:         {result_higher['enhancement_percent']:>10.4f}%")
    print(f"  Simplex Boost:       {result_higher['simplex_boost_percent']:>10.4f}%")
    
    print(f"\nDistribution level impact:")
    diff = result_higher['enhancement_percent'] - result_default['enhancement_percent']
    print(f"  Δ Enhancement:       {diff:>10.4f}%")


def demo_custom_tetrahedron():
    """Demonstrate simplex anchoring with custom tetrahedron coordinates"""
    print_section("5. Custom Tetrahedron Coordinates")
    
    mapper = GeodesicMapper()
    primes = [2, 3, 5, 7, 11, 13]
    
    # Custom tetrahedron vertices
    custom_coords = [
        (2, 0, 0),      # Along x-axis
        (0, 2, 0),      # Along y-axis
        (0, 0, 2),      # Along z-axis
        (1, 1, 1)       # Body diagonal
    ]
    
    print("\nCustom 3D Tetrahedron Vertices:")
    for i, coord in enumerate(custom_coords):
        print(f"  Vertex {i+1}: {coord}")
    
    result = mapper.simplex_anchor(primes, base_coords=custom_coords)
    
    print("\nEmbedded into 5D:")
    for i, vertex in enumerate(result['tetrahedron_vertices_5d'][:4]):
        print(f"  Vertex {i+1}: {vertex}")
    
    print(f"\nEnhancement with custom coordinates:")
    print(f"  Total Enhancement:   {result['enhancement_percent']:>10.4f}%")
    print(f"  Simplex Boost:       {result['simplex_boost_percent']:>10.4f}%")


def demo_comparison_with_base():
    """Compare simplex anchoring with base geodesic enhancement"""
    print_section("6. Comparison: Base vs. Simplex-Anchored Enhancement")
    
    mapper = GeodesicMapper(kappa_geo=0.3)
    
    # Generate larger prime list for more stable statistics
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    primes = [n for n in range(2, 200) if is_prime(n)]
    print(f"\nUsing {len(primes)} primes from 2 to {primes[-1]}")
    
    # Base enhancement
    base_result = mapper.compute_density_enhancement_with_dist_level(
        primes,
        dist_level=DIST_LEVEL_STADLMANN,
        n_bootstrap=500
    )
    
    # Simplex-anchored enhancement
    simplex_result = mapper.simplex_anchor(
        primes,
        dist_level=DIST_LEVEL_STADLMANN,
        n_bootstrap=500
    )
    
    print("\nBase Geodesic Enhancement (with Stadlmann level):")
    print(f"  Enhancement:         {base_result['enhancement_percent']:>10.4f}%")
    print(f"  CI: [{base_result['ci_lower']:>8.4f}%, {base_result['ci_upper']:>8.4f}%]")
    
    print("\nSimplex-Anchored Enhancement:")
    print(f"  Enhancement:         {simplex_result['enhancement_percent']:>10.4f}%")
    print(f"  CI: [{simplex_result['ci_lower']:>8.4f}%, {simplex_result['ci_upper']:>8.4f}%]")
    print(f"\nSimplex Boost:")
    print(f"  Additional Boost:    {simplex_result['simplex_boost_percent']:>10.4f}%")
    print(f"  Combined Factor:     {simplex_result['combined_simplex_factor']:>10.6f}x")
    
    # Validate target range
    target_met = simplex_result['target_boost_met']
    target_range = simplex_result['target_boost_range']
    print(f"\nTarget Validation:")
    print(f"  Target Range:        [{target_range[0]:.1f}%, {target_range[1]:.1f}%]")
    print(f"  Target Met:          {target_met}")


def demo_performance_summary():
    """Summarize performance characteristics"""
    print_section("7. Performance Summary")
    
    print("\nTetrahedron Integration Features:")
    print("  ✓ 3D→5D embedding via orthogonal dimensions")
    print("  ✓ A₄ group symmetries (order 12)")
    print("  ✓ Euler formula constraints (V-E+F=2)")
    print("  ✓ Tetrahedron self-duality optimization")
    print("  ✓ Stadlmann distribution level integration")
    print("  ✓ Bootstrap-validated confidence intervals")
    
    print("\nKey Properties:")
    print("  • Tetrahedron Vertices: 4")
    print("  • Tetrahedron Edges: 6")
    print("  • Tetrahedron Faces: 4")
    print("  • Euler Characteristic: χ = 2")
    print("  • A₄ Group Order: 12")
    print("  • Self-Dual: Yes")
    
    print("\nPerformance Targets (from Issue #XXX):")
    print("  • Density Boost: 1-2% (CI [0.8%, 2.2%])")
    print("  • Prediction Time: <0.6ms for n=10^18")
    print("  • Error Bound: <0.00002 ppm")
    print("  • Enhancement CI: [14.6%, 15.4%] (baseline)")
    
    print("\nApplications:")
    print("  • Prime density predictions with AP filtering")
    print("  • Conical flow model integration")
    print("  • RSA tuning experiments")
    print("  • Semiprime factorization validation")
    print("  • Zeta function correlation analysis")


def main():
    """Run all demos"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  Simplex Anchoring & Tetrahedron Integration Demo".center(68) + "█")
    print("█" + "  Z5D Framework - Enhanced Symmetry Operations".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    try:
        demo_basic_simplex_anchoring()
        demo_tetrahedron_embedding()
        demo_symmetry_factors()
        demo_stadlmann_integration()
        demo_custom_tetrahedron()
        demo_comparison_with_base()
        demo_performance_summary()
        
        print_section("Demo Complete")
        print("\nAll demonstrations completed successfully!")
        print("\nFor more details, see:")
        print("  • src/core/geodesic_mapping.py (simplex_anchor method)")
        print("  • tests/test_tetrahedron_simplex_anchoring.py (test suite)")
        print("  • docs/ (documentation and visualizations)")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
