#!/usr/bin/env python3
"""
Demo Script: Mod-3 Residue Triangle Tesla 369 Filter

This script demonstrates the mod-3 residue triangle pre-filter implementation
for Z5D geodesic mappings as specified in Issue #531.

Usage: python demo_mod3_tesla_filter.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import mpmath as mp
from sympy import sieve
from core.geodesic_mapping import GeodesicMapper

# Set high precision as specified
mp.mp.dps = 50

def demonstrate_tesla_369_partitioning():
    """Demonstrate Tesla 369 mod-3 residue partitioning."""
    print("=" * 60)
    print("TESLA 369 MOD-3 RESIDUE TRIANGLE DEMONSTRATION")
    print("=" * 60)
    
    mapper = GeodesicMapper(kappa_geo=0.3)
    
    # Step 1: Demonstrate basic mod-3 residue partitioning (1-12)
    print("\n1. Basic Tesla 369 Partitioning (1-12):")
    sequence_1_12 = list(range(1, 13))
    partitions = mapper.partition_mod3_residues(sequence_1_12)
    
    print(f"   Input sequence: {sequence_1_12}")
    print(f"   Residue class 0 (multiples of 3): {partitions[0]}")
    print(f"   Residue class 1 (1 mod 3): {partitions[1]}")
    print(f"   Residue class 2 (2 mod 3): {partitions[2]}")
    
    # Verify matches Tesla 369 specification
    expected_0 = [3, 6, 9, 12]
    expected_1 = [1, 4, 7, 10]
    expected_2 = [2, 5, 8, 11]
    
    print(f"\n   ✓ Matches Tesla 369 specification:")
    print(f"     {partitions[0]} == {expected_0}: {partitions[0] == expected_0}")
    print(f"     {partitions[1]} == {expected_1}: {partitions[1] == expected_1}")
    print(f"     {partitions[2]} == {expected_2}: {partitions[2] == expected_2}")

def demonstrate_geodesic_transformations():
    """Demonstrate geodesic transformations with and without filtering."""
    print("\n2. Geodesic Transformations θ'(n,k) = φ·{n/φ}^k:")
    
    mapper = GeodesicMapper(kappa_geo=0.3)
    test_values = [1, 2, 3, 10, 100]
    
    print(f"   k (curvature parameter): {mapper._effective_kappa_geo}")
    print(f"   φ (golden ratio): {mapper.phi:.10f}")
    
    print("\n   Standard transformations:")
    for n in test_values:
        transform = mapper.enhanced_geodesic_transform(n)
        print(f"     θ'({n}) = {transform:.10f}")
    
    print("\n   High-precision reference (mpmath dps=50):")
    for n in test_values:
        hp_transform = mapper.enhanced_geodesic_transform_high_precision(n)
        print(f"     θ'({n}) = {hp_transform:.16f}")

def demonstrate_invariant_attractor_hypothesis():
    """Demonstrate the invariant attractor hypothesis for residue class 0."""
    print("\n3. Invariant Attractor Hypothesis (Residue Class 0):")
    
    mapper = GeodesicMapper(kappa_geo=0.3)
    
    # Generate multiples of 3 (residue class 0)
    multiples_of_3 = [3 * i for i in range(1, 21)]  # [3, 6, 9, ..., 60]
    
    # Apply geodesic transformation
    transforms_res_0 = [mapper.enhanced_geodesic_transform(n) for n in multiples_of_3]
    variance_0 = np.var(transforms_res_0)
    mean_0 = np.mean(transforms_res_0)
    
    print(f"   Multiples of 3: {multiples_of_3[:10]}... (first 10)")
    print(f"   Transformed values: {[f'{t:.6f}' for t in transforms_res_0[:5]]}... (first 5)")
    print(f"   Mean: {mean_0:.10f}")
    print(f"   Variance: {variance_0:.10f}")
    
    # Compare with other residue classes
    residue_1_nums = [3 * i + 1 for i in range(20)]  # [1, 4, 7, ...]
    residue_2_nums = [3 * i + 2 for i in range(20)]  # [2, 5, 8, ...]
    
    transforms_res_1 = [mapper.enhanced_geodesic_transform(n) for n in residue_1_nums]
    transforms_res_2 = [mapper.enhanced_geodesic_transform(n) for n in residue_2_nums]
    
    variance_1 = np.var(transforms_res_1)
    variance_2 = np.var(transforms_res_2)
    
    print(f"\n   Comparison with other residue classes:")
    print(f"     Residue 0 variance: {variance_0:.10f}")
    print(f"     Residue 1 variance: {variance_1:.10f}")
    print(f"     Residue 2 variance: {variance_2:.10f}")
    
    if variance_0 < variance_1 and variance_0 < variance_2:
        print("   ✓ Residue 0 shows lowest variance (supports invariant attractor hypothesis)")
    else:
        print("   ⚠ Residue 0 variance pattern requires further analysis")

def demonstrate_density_enhancement_comparison():
    """Demonstrate density enhancement with and without mod-3 filtering."""
    print("\n4. Density Enhancement Comparison:")
    
    mapper = GeodesicMapper(kappa_geo=0.3)
    
    # Generate primes for testing
    primes = list(sieve.primerange(2, 1000))
    print(f"   Testing with {len(primes)} primes up to 1000")
    
    # Compute density enhancement without filter
    print("   Computing enhancement without mod-3 filter...")
    enhancement_no_filter = mapper.compute_density_enhancement_with_mod3_filter(
        primes, n_bins=30, n_bootstrap=100, apply_filter=False
    )
    
    # Compute density enhancement with mod-3 filter
    print("   Computing enhancement with mod-3 filter...")
    enhancement_with_filter = mapper.compute_density_enhancement_with_mod3_filter(
        primes, n_bins=30, n_bootstrap=100, apply_filter=True
    )
    
    # Display results
    enh_no_filter = enhancement_no_filter['enhancement_percent']
    enh_with_filter = enhancement_with_filter['enhancement_percent']
    
    print(f"\n   Results:")
    print(f"     Without filter: {enh_no_filter:.3f}% (CI: [{enhancement_no_filter['ci_lower']:.3f}%, {enhancement_no_filter['ci_upper']:.3f}%])")
    print(f"     With filter:    {enh_with_filter:.3f}% (CI: [{enhancement_with_filter['ci_lower']:.3f}%, {enhancement_with_filter['ci_upper']:.3f}%])")
    print(f"     Difference:     {abs(enh_with_filter - enh_no_filter):.3f}%")
    
    # Show mod-3 partition statistics
    if enhancement_with_filter['mod3_partitions']:
        partitions = enhancement_with_filter['mod3_partitions']
        print(f"\n   Mod-3 partition distribution:")
        print(f"     Residue 0 (3 is the only prime multiple of 3): {partitions['residue_0_count']}")
        print(f"     Residue 1 (1 mod 3): {partitions['residue_1_count']}")
        print(f"     Residue 2 (2 mod 3): {partitions['residue_2_count']}")
        print(f"     Total: {partitions['total_filtered']}")

def demonstrate_precision_validation():
    """Demonstrate high-precision validation capabilities."""
    print("\n5. Precision Validation (mpmath dps=50):")
    
    mapper = GeodesicMapper(kappa_geo=0.3)
    
    test_values = [1, 10, 100, 1000]
    print(f"   Comparing standard vs high-precision implementations:")
    
    max_error = 0
    for n in test_values:
        standard = mapper.enhanced_geodesic_transform(n)
        high_precision = mapper.enhanced_geodesic_transform_high_precision(n)
        error = abs(standard - high_precision)
        max_error = max(max_error, error)
        
        print(f"     n={n:4d}: standard={standard:.15f}, hp={high_precision:.15f}, error={error:.2e}")
    
    print(f"\n   Maximum precision error: {max_error:.2e}")
    if max_error < 2e-15:
        print("   ✓ Precision requirements met (< 2e-15)")
    else:
        print("   ⚠ Precision error exceeds expected bounds")

def main():
    """Run the complete demonstration."""
    print("Mod-3 Residue Triangle Tesla 369 Filter Demonstration")
    print("Issue #531: Hypothesis testing framework implementation")
    
    try:
        demonstrate_tesla_369_partitioning()
        demonstrate_geodesic_transformations()
        demonstrate_invariant_attractor_hypothesis()
        demonstrate_density_enhancement_comparison()
        demonstrate_precision_validation()
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nNext steps for research:")
        print("- Run comprehensive tests: python -m pytest tests/test_mod3_residue_triangle_filter.py")
        print("- Explore different parameter values for k and bin sizes")
        print("- Test with larger prime datasets for statistical significance")
        print("- Analyze variance patterns across residue classes")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        print("This may indicate missing dependencies or configuration issues.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())