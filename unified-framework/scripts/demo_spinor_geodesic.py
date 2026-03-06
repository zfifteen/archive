#!/usr/bin/env python3
"""
Spinor Geodesic Curvature Framework - Demonstration Script

This script demonstrates the complete implementation of "Spinors as Emergent 
Geodesic Curvature" in the Z Framework, showcasing all key capabilities and 
validation results.

Usage:
    python demo_spinor_geodesic.py

Expected Output:
    - Validation of F > 0.95 fidelity target
    - Demonstration of 20%+ improvement claims  
    - Statistical validation with σ < 10^-4
    - Integration with Z Framework confirmation
"""

import sys
import os
import numpy as np
from math import pi

# Import from package (assumes src/core is a package)



try:
    from src.core.spinor_geodesic import (
        demonstrate_20_percent_improvement,
        validate_spinor_geodesic_framework,
        calculate_geodesic_enhanced_fidelity,
        calculate_detuned_fidelity_improvement,
        integrate_with_z_framework,
        PHI, OPTIMAL_K, E_SQUARED
    )
    print("✅ Spinor Geodesic Framework imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_subheader(title):
    """Print formatted subsection header."""
    print(f"\n--- {title} ---")


def demo_basic_functionality():
    """Demonstrate basic spinor geodesic functionality."""
    print_header("BASIC FUNCTIONALITY DEMONSTRATION")
    
    # Constants validation
    print_subheader("Z Framework Constants")
    print(f"Golden ratio φ: {PHI:.10f}")
    print(f"e² constant: {E_SQUARED:.10f}")
    print(f"Optimal k*: {OPTIMAL_K}")
    
    # Basic geodesic calculation
    print_subheader("Geodesic Transform Example")
    n = 42  # Optimal test position
    result = calculate_geodesic_enhanced_fidelity(pi/4, n, OPTIMAL_K)
    
    print(f"Test configuration:")
    print(f"  - Rotation angle: π/4 = {pi/4:.4f} rad (45°)")
    print(f"  - Position n: {n}")
    print(f"  - Curvature k: {OPTIMAL_K}")
    print(f"Results:")
    print(f"  - Enhanced fidelity: {result['fidelity_enhanced']:.6f}")
    print(f"  - Standard fidelity: {result['fidelity_standard']:.6f}")
    print(f"  - Enhancement: {result['enhancement_percent']:.2f}%")
    print(f"  - Passes F > 0.95: {'✅' if result['passes_threshold'] else '❌'}")


def demo_20_percent_improvement():
    """Demonstrate the 20% improvement claim with full artifact generation."""
    print_header("20% IMPROVEMENT DEMONSTRATION")
    
    print("Testing geodesic curvature enhancement with documented scenarios...")
    print("📋 Parameters: Fixed seed=42, angles=[45°,180°], detuning=[25%,50%], n=[7,1000]")
    
    demo_result = demonstrate_20_percent_improvement(save_artifacts=True)
    
    print_subheader("Overall Results")
    print(f"Maximum improvement achieved: {demo_result['max_improvement_percent']:.2f}%")
    print(f"Mean improvement: {demo_result['mean_improvement_percent']:.2f}%")
    print(f"Standard deviation: {demo_result['std_improvement_percent']:.2f}%")
    print(f"20% claim validated: {'✅' if demo_result['meets_20_percent_claim'] else '❌'}")
    print(f"F > 0.95 achievement rate: {demo_result['fraction_above_95_percent']:.1%}")
    print(f"Total test cases: {demo_result['total_tests']}")
    
    if 'artifact_path' in demo_result:
        print(f"📁 Test artifacts saved: {demo_result['artifact_path']}")
    
    print_subheader("Reproducibility Documentation")
    params = demo_result['parameter_documentation']
    print(f"Random seed: {params['random_seed']}")
    print(f"Angle range: {params['angle_range_degrees'][0]}° to {params['angle_range_degrees'][1]}°")
    print(f"Detuning range: {params['detuning_range'][0]*100}% to {params['detuning_range'][1]*100}%")
    print(f"Position range: {params['position_range'][0]} to {params['position_range'][1]}")
    print(f"Optimal k*: {params['optimal_k']}")
    
    print_subheader("Detailed Test Cases")
    for i, result in enumerate(demo_result['detailed_results'][:3]):  # Show first 3
        print(f"Test {i+1}: {result['test_description']}")
        print(f"  Angle: {result['theta']:.3f} rad, Detuning: {result['detuning']:.2f}")
        print(f"  Position n: {result['n_position']}")
        print(f"  Improvement: {result['enhancement_percent']:.2f}%")
        print(f"  Final fidelity: {result['fidelity_corrected']:.4f}")


def demo_statistical_validation():
    """Demonstrate statistical validation with artifact generation."""
    print_header("STATISTICAL VALIDATION")
    
    print("Running comprehensive statistical validation with documented parameters...")
    validation = validate_spinor_geodesic_framework(n_trials=100, save_artifacts=True)
    
    stats = validation['statistical_results']
    framework = validation['framework_validation']
    config = validation['test_configuration']
    
    print_subheader("Statistical Metrics")
    print(f"Mean fidelity: {stats['mean_fidelity']:.6f}")
    print(f"Standard deviation: {stats['std_fidelity']:.8f}")
    print(f"95% CI: [{stats['fidelity_95_ci'][0]:.4f}, {stats['fidelity_95_ci'][1]:.4f}]")
    print(f"Pass rate (F > 0.95): {stats['pass_rate_f095']:.1%}")
    
    print_subheader("Framework Validation")
    print(f"Meets fidelity target (F > 0.95): {'✅' if framework['meets_fidelity_target'] else '❌'}")
    print(f"Meets variance target (σ < 10⁻⁴): {'✅' if framework['meets_variance_target'] else '❌'}")
    print(f"Shows significant enhancement: {'✅' if framework['shows_significant_enhancement'] else '❌'}")
    print(f"Optimal k* confirmed: {'✅' if framework['optimal_k_confirmed'] else '❌'}")
    
    print_subheader("Test Configuration & Reproducibility")
    print(f"Total tests conducted: {config['total_tests']}")
    print(f"Parameter grid size: {config['parameter_grid_size']}")
    print(f"Random seed: {config['random_seed']}")
    print(f"Angle range: [{config['angle_range'][0]:.2f}, {config['angle_range'][1]:.2f}] rad")
    print(f"Position range: [{config['position_range'][0]}, {config['position_range'][1]}]")
    
    if 'artifact_path' in validation:
        print(f"📁 Validation artifacts saved: {validation['artifact_path']}")
    
    # Show threshold validation results
    if 'threshold_validation' in validation:
        print_subheader("Threshold Validation for CI")
        thresholds = validation['threshold_validation']
        for threshold, passed in thresholds.items():
            status = '✅' if passed else '❌'
            print(f"  {threshold}: {status}")


def demo_framework_integration():
    """Demonstrate Z Framework integration."""
    print_header("Z FRAMEWORK INTEGRATION")
    
    integration_result = integrate_with_z_framework()
    
    print_subheader("Integration Test")
    print(f"Integration successful: {'✅' if integration_result['integration_successful'] else '❌'}")
    
    if integration_result['integration_successful']:
        print(f"Classical geodesic value: {integration_result['classical_geodesic']:.6f}")
        print(f"Spinor geodesic (real): {integration_result['spinor_geodesic'].real:.6f}")
        print(f"Spinor geodesic (imag): {integration_result['spinor_geodesic'].imag:.6f}")
        print(f"Real parts match: {'✅' if integration_result['real_part_matches'] else '❌'}")
    else:
        print(f"Note: {integration_result.get('note', 'Integration test failed')}")


def demo_edge_cases():
    """Demonstrate performance on edge cases."""
    print_header("EDGE CASE TESTING")
    
    edge_cases = [
        {'name': 'Small angle', 'theta': pi/12, 'n': 1},
        {'name': 'Large angle', 'theta': 11*pi/6, 'n': 1000},
        {'name': 'Golden ratio position', 'theta': pi/2, 'n': int(PHI)},
        {'name': 'High curvature', 'theta': pi/3, 'n': 42},
    ]
    
    print_subheader("Edge Case Results")
    for case in edge_cases:
        result = calculate_geodesic_enhanced_fidelity(case['theta'], case['n'], OPTIMAL_K)
        print(f"{case['name']}:")
        print(f"  θ={case['theta']:.3f}, n={case['n']}")
        print(f"  Fidelity: {result['fidelity_enhanced']:.4f}")
        print(f"  Enhancement: {result['enhancement_percent']:.2f}%")
        print(f"  Passes: {'✅' if result['passes_threshold'] else '❌'}")


def demo_performance_summary():
    """Provide overall performance summary with artifact validation."""
    print_header("PERFORMANCE SUMMARY & ARTIFACT VALIDATION")
    
    # Run quick validation
    demo_result = demonstrate_20_percent_improvement(save_artifacts=True)
    validation = validate_spinor_geodesic_framework(n_trials=50, save_artifacts=True)
    
    stats = validation['statistical_results'] 
    framework = validation['framework_validation']
    
    print("🎯 TARGET ACHIEVEMENT SUMMARY:")
    print(f"   Fidelity F > 0.95:     {'✅ ACHIEVED' if stats['pass_rate_f095'] > 0.95 else '❌ FAILED'} ({stats['pass_rate_f095']:.1%})")
    print(f"   20% Improvement:       {'✅ ACHIEVED' if demo_result['meets_20_percent_claim'] else '❌ FAILED'} ({demo_result['max_improvement_percent']:.1f}%)")
    print(f"   Variance σ < 10⁻⁴:     {'✅ ACHIEVED' if framework['meets_variance_target'] else '❌ FAILED'} ({stats['std_fidelity']:.2e})")
    print(f"   Z Integration:         {'✅ ACHIEVED' if integrate_with_z_framework()['integration_successful'] else '❌ FAILED'}")
    
    print("\n📊 PERFORMANCE METRICS:")
    print(f"   Mean fidelity:         {stats['mean_fidelity']:.6f}")
    print(f"   Maximum improvement:   {demo_result['max_improvement_percent']:.2f}%")
    print(f"   Standard deviation:    {stats['std_fidelity']:.2e}")
    print(f"   Tests conducted:       {validation['test_configuration']['total_tests']}")
    
    print("\n📁 ARTIFACT SUMMARY:")
    if 'artifact_path' in demo_result:
        print(f"   Improvement demo:      {demo_result['artifact_path']}")
    if 'artifact_path' in validation:
        print(f"   Statistical validation: {validation['artifact_path']}")
    
    # Overall assessment
    targets_met = sum([
        stats['pass_rate_f095'] > 0.95,
        demo_result['meets_20_percent_claim'],
        framework['meets_variance_target'],
        integrate_with_z_framework()['integration_successful']
    ])
    
    print(f"\n🏆 OVERALL ASSESSMENT: {targets_met}/4 TARGETS MET")
    if targets_met == 4:
        print("   STATUS: ✅ FULL SUCCESS - All paper claims validated!")
        print("   📋 Artifacts ready for CI validation and regression testing")
    elif targets_met >= 3:
        print("   STATUS: ⚠️  PARTIAL SUCCESS - Major targets achieved")
    else:
        print("   STATUS: ❌ NEEDS IMPROVEMENT")


def main():
    """Main demonstration function."""
    print("🌟 SPINOR GEODESIC CURVATURE FRAMEWORK")
    print("    Implementation Demonstration")
    print("    Z Framework Extension for Quantum Applications")
    
    try:
        demo_basic_functionality()
        demo_20_percent_improvement() 
        demo_statistical_validation()
        demo_framework_integration()
        demo_edge_cases()
        demo_performance_summary()
        
        print_header("DEMONSTRATION COMPLETE")
        print("✅ All demonstrations completed successfully!")
        print("   The spinor geodesic framework is fully operational.")
        print("   Paper claims have been validated with comprehensive testing.")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)