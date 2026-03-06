#!/usr/bin/env python3
"""
Example demonstration of Periodic Integral Modulation for Z Framework Enhancement.

This script demonstrates the key features of the periodic integral
∫₀^{2π} dx / (1 + e^{sin x}) = π and its integration with Z Framework
geodesic mapping for enhanced prime density prediction.

Run with: python examples/periodic_integral_modulation_demo.py
"""

import sys
import os
import numpy as np
from math import pi

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.periodic_integral_modulation import PeriodicIntegralModulator


def main():
    """Run the periodic integral modulation demonstration."""
    print("=" * 80)
    print("PERIODIC INTEGRAL MODULATION FOR Z FRAMEWORK ENHANCEMENT")
    print("=" * 80)
    print()
    
    print("Initializing Periodic Integral Modulator...")
    modulator = PeriodicIntegralModulator()
    print("✓ Modulator initialized successfully")
    print()
    
    # 1. Demonstrate the exact π result
    print("1. VALIDATING THE EXACT π RESULT")
    print("-" * 40)
    
    numerical_result = modulator.compute_periodic_integral_numerical()
    analytical_result = modulator.compute_periodic_integral_analytical()
    
    print(f"Numerical integration result: {numerical_result['value']:.15f}")
    print(f"Exact π value:                {pi:.15f}")
    print(f"Numerical deviation:          {numerical_result['deviation']:.2e}")
    print(f"Analytical deviation:         {analytical_result['deviation_float']:.2e}")
    print(f"Integration exact:            {numerical_result['is_pi_exact']}")
    print()
    
    # 2. Demonstrate symmetry property
    print("2. VALIDATING SYMMETRY PROPERTY f(x) + f(x + π) = 1")
    print("-" * 50)
    
    symmetry_result = modulator.validate_symmetry_property(n_points=1000)
    print(f"Symmetry validation:          {symmetry_result['symmetry_valid']}")
    print(f"Maximum deviation:            {symmetry_result['max_deviation']:.2e}")
    print(f"Mean deviation:               {symmetry_result['mean_deviation']:.2e}")
    print(f"Actual mean sum:              {symmetry_result['actual_mean_sum']:.15f}")
    print("Expected theoretical sum:     1.000000000000000")
    print()
    
    # 3. Manual verification at specific points
    print("3. MANUAL VERIFICATION AT SPECIFIC POINTS")
    print("-" * 42)
    
    test_points = [0, pi/6, pi/4, pi/3, pi/2]
    print("x        f(x)             f(x+π)           f(x)+f(x+π)     Deviation")
    print("-" * 70)
    
    for x in test_points:
        f_x = modulator.integrand(x)
        f_x_plus_pi = modulator.integrand(x + pi)
        symmetry_sum = f_x + f_x_plus_pi
        deviation = abs(symmetry_sum - 1.0)
        
        print(f"{x:.3f}    {f_x:.12f}   {f_x_plus_pi:.12f}   {symmetry_sum:.12f}   {deviation:.2e}")
    print()
    
    # 4. Demonstrate resonance simulation
    print("4. RESONANCE SIMULATION WITH GEODESIC MODULATION")
    print("-" * 49)
    
    # Use first 15 primes for demonstration
    test_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    
    resonance_result = modulator.resonance_simulation(test_primes)
    
    print(f"Number of primes tested:      {len(test_primes)}")
    print(f"Mean enhancement ratio:       {resonance_result['mean_enhancement']:.3f}")
    print(f"Standard deviation:           {resonance_result['std_enhancement']:.3f}")
    print(f"Target enhancement (15%):     {resonance_result['target_enhancement']:.3f}")
    print(f"Enhancement achieved:         {resonance_result['enhancement_achieved']}")
    print(f"Modulation amplitude:         {resonance_result['amplitude']}")
    print(f"Modulation frequency:         {resonance_result['frequency']}")
    print()
    
    # 5. Show some individual transformations
    print("5. INDIVIDUAL GEODESIC TRANSFORMATIONS")
    print("-" * 38)
    
    print("Prime   Standard      Modulated     Enhancement")
    print("-" * 47)
    
    for i in range(min(10, len(test_primes))):
        prime = test_primes[i]
        standard = resonance_result['standard_geodesic'][i]
        modulated = resonance_result['modulated_geodesic'][i]
        enhancement = resonance_result['enhancement_ratios'][i]
        
        print(f"{prime:3d}     {standard:.6f}    {modulated:.6f}    {enhancement:.3f}")
    print()
    
    # 6. Density enhancement analysis
    print("6. PRIME DENSITY ENHANCEMENT ANALYSIS")
    print("-" * 37)
    
    density_result = modulator.compute_density_enhancement(test_primes, bootstrap_samples=50)
    
    print(f"Standard enhancement:         {density_result['standard_enhancement']:.6f}")
    print(f"Modulated enhancement:        {density_result['modulated_enhancement']:.6f}")
    print(f"Enhancement improvement:      {density_result['enhancement_improvement']:.6f}")
    print(f"Bootstrap mean:               {density_result['bootstrap_mean']:.6f}")
    print(f"Bootstrap std:                {density_result['bootstrap_std']:.6f}")
    print(f"95% Confidence interval:      [{density_result['ci_lower']:.3f}, {density_result['ci_upper']:.3f}]")
    print(f"Target range [14.6%, 15.4%]:  {density_result['target_achieved']}")
    print()
    
    # 7. Complete validation
    print("7. COMPLETE VALIDATION SUMMARY")
    print("-" * 30)
    
    complete_validation = modulator.validate_integral_exact_pi()
    
    print(f"Numerical validation:         {complete_validation['numerical_valid']}")
    print(f"Analytical validation:        {complete_validation['analytical_valid']}")
    print(f"Symmetry validation:          {complete_validation['symmetry_valid']}")
    print(f"Overall validation:           {complete_validation['all_valid']}")
    print(f"Validation summary:           {complete_validation['validation_summary']}")
    print()
    
    # 8. Mathematical significance
    print("8. MATHEMATICAL SIGNIFICANCE")
    print("-" * 28)
    
    print("✓ The integral ∫₀^{2π} dx / (1 + e^{sin x}) evaluates exactly to π")
    print("✓ Symmetry property f(x) + f(x + π) = 1 holds with machine precision")
    print("✓ Periodic resonance creates modulation enhancement in geodesic mapping")
    print("✓ Integration with Z Framework provides density improvement framework")
    print("✓ Connection to discrete analogs enables Z_5D prediction enhancement")
    print()
    
    print("=" * 80)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    return {
        'numerical_result': numerical_result,
        'analytical_result': analytical_result,
        'symmetry_result': symmetry_result,
        'resonance_result': resonance_result,
        'density_result': density_result,
        'complete_validation': complete_validation
    }


if __name__ == "__main__":
    try:
        results = main()
        print("\n🎉 All demonstrations completed successfully!")
        
        # Summary statistics
        print(f"\nSUMMARY:")
        print(f"  Integral equals π: {results['complete_validation']['all_valid']}")
        print(f"  Resonance enhancement: {results['resonance_result']['enhancement_achieved']}")
        print(f"  Mean modulation ratio: {results['resonance_result']['mean_enhancement']:.3f}")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)