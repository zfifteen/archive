#!/usr/bin/env python3
"""
SHA-256 Pattern Detection Example
=================================

Practical demonstration of SHA-256 cryptographic analysis using the Z Framework's
discrete domain for pattern detection through discrete derivatives.

This example shows:
1. Basic SHA-256 pattern analysis
2. Differential cryptanalysis comparison
3. Curvature-based pattern detection
4. Integration with Z Framework parameters
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/runner/work/unified-framework/unified-framework')

from src.core.sha256_pattern_analyzer import SHA256PatternAnalyzer
import json

def basic_pattern_analysis_example():
    """Demonstrate basic SHA-256 pattern analysis."""
    print("=" * 60)
    print("SHA-256 PATTERN ANALYSIS EXAMPLE")
    print("=" * 60)
    
    analyzer = SHA256PatternAnalyzer()
    
    # Analyze a simple sequence
    test_input = "cryptographic_analysis_test"
    sequence_length = 8
    
    print(f"Base input: '{test_input}'")
    print(f"Analyzing sequence of {sequence_length} hashes...")
    print()
    
    # Perform complete analysis
    results = analyzer.analyze_sequence(test_input, sequence_length)
    
    # Display hash sequence
    print("Generated Hash Sequence:")
    print("-" * 25)
    for i, hash_hex in enumerate(results['hash_sequence']):
        print(f"{i+1}: {hash_hex}")
    print()
    
    # Display discrete derivatives
    print("Discrete Derivatives (consecutive differences):")
    print("-" * 45)
    derivatives = results['discrete_derivatives']
    for i, derivative in enumerate(derivatives):
        print(f"Δh({i+1}): {derivative:+d}")
    print()
    
    # Display derivative statistics
    print("Derivative Statistics:")
    print("-" * 20)
    stats = results['derivative_stats']
    print(f"Mean: {stats['mean']:,.0f}")
    print(f"Std:  {stats['std']:,.0f}")
    print(f"Min:  {stats['min']:,.0f}")
    print(f"Max:  {stats['max']:,.0f}")
    print()
    
    # Display pattern metrics
    print("Pattern Detection Metrics:")
    print("-" * 25)
    pattern_metrics = results['pattern_metrics']
    print(f"Number of samples: {pattern_metrics['num_samples']}")
    print(f"Curvature mean: {pattern_metrics['curvature_mean']:.6f}")
    print(f"Curvature std:  {pattern_metrics['curvature_std']:.6f}")
    print(f"Low curvature ratio: {pattern_metrics['low_curvature_ratio']:.3f}")
    print(f"Pattern detected: {pattern_metrics['pattern_detected']}")
    print()
    
    # Display framework parameters
    print("Z Framework Parameters:")
    print("-" * 22)
    params = results['framework_parameters']
    print(f"a (bit length): {params['a']}")
    print(f"b (natural base): {params['b']:.6f}")
    print(f"c (e² normalization): {params['c']:.6f}")
    print(f"Δ_max: {params['delta_max']:.6f}")
    print()
    
    return results

def differential_cryptanalysis_example():
    """Demonstrate differential cryptanalysis with multiple variants."""
    print("=" * 60)
    print("DIFFERENTIAL CRYPTANALYSIS EXAMPLE")
    print("=" * 60)
    
    analyzer = SHA256PatternAnalyzer()
    
    # Test with slight variations in input
    base_input = "secure_message"
    variants = [
        base_input,
        base_input + "1",
        base_input + "2", 
        base_input + "_modified",
        base_input.upper()
    ]
    
    print(f"Base input: '{base_input}'")
    print("Testing variants:")
    for i, variant in enumerate(variants):
        print(f"  {i+1}: '{variant}'")
    print()
    
    # Perform differential analysis
    results = analyzer.detect_differential_patterns(variants, sequence_length=5)
    
    # Display results for each variant
    print("Individual Variant Results:")
    print("-" * 26)
    for i, result in enumerate(results['variant_results']):
        metrics = result['pattern_metrics']
        print(f"Variant {i+1} ('{result['base_data']}'):")
        print(f"  Curvature mean: {metrics['curvature_mean']:.6f}")
        print(f"  Pattern detected: {metrics['pattern_detected']}")
        print(f"  Low curvature ratio: {metrics['low_curvature_ratio']:.3f}")
        print()
    
    # Display differential metrics
    print("Differential Analysis Results:")
    print("-" * 28)
    diff_metrics = results['differential_metrics']
    print(f"Number of variants: {diff_metrics['num_variants']}")
    print(f"Curvature variance across variants: {diff_metrics['curvature_variance_across_variants']:.6f}")
    print(f"Pattern consistency: {diff_metrics['pattern_consistency']:.6f}")
    print(f"Non-random behavior detected: {diff_metrics['non_random_behavior_detected']}")
    print()
    
    # Display analysis summary
    print("Analysis Summary:")
    print("-" * 15)
    summary = results['analysis_summary']
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print()
    
    return results

def avalanche_effect_demonstration():
    """Demonstrate SHA-256 avalanche effect with pattern analysis."""
    print("=" * 60)
    print("SHA-256 AVALANCHE EFFECT DEMONSTRATION")
    print("=" * 60)
    
    analyzer = SHA256PatternAnalyzer()
    
    # Test minimal input changes
    input1 = "avalanche_test_input"
    input2 = "avalanche_test_input_"  # Just one character added
    
    hash1 = analyzer.sha256_to_integer(input1)
    hash2 = analyzer.sha256_to_integer(input2)
    
    print(f"Input 1: '{input1}'")
    print(f"Input 2: '{input2}'")
    print()
    
    print("SHA-256 Hashes as integers:")
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    print()
    
    # Calculate bit differences
    xor_result = hash1 ^ hash2
    hamming_distance = bin(xor_result).count('1')
    
    print("Avalanche Effect Analysis:")
    print(f"XOR result: {xor_result}")
    print(f"Hamming distance: {hamming_distance} bits")
    print(f"Percentage of bits changed: {hamming_distance/256*100:.1f}%")
    print()
    
    # Expected avalanche effect for good cryptographic hash
    expected_min = 256 * 0.25  # At least 25% bits should change
    expected_max = 256 * 0.75  # At most 75% bits should change
    
    print("Avalanche Effect Assessment:")
    if expected_min <= hamming_distance <= expected_max:
        print("✓ Good avalanche effect - significant bit changes for minimal input change")
    else:
        print("⚠ Unexpected avalanche behavior")
    print()

def curvature_pattern_analysis():
    """Demonstrate detailed curvature-based pattern analysis."""
    print("=" * 60)
    print("CURVATURE-BASED PATTERN ANALYSIS")
    print("=" * 60)
    
    analyzer = SHA256PatternAnalyzer()
    
    # Analyze multiple sequences with different characteristics
    test_cases = [
        ("random_string_abc123", "Random-like input"),
        ("1111111111111111111", "Repetitive input"),
        ("cryptographically_secure_input_data", "Long descriptive input"),
        ("a", "Minimal input"),
        ("The quick brown fox jumps over the lazy dog", "Standard test phrase")
    ]
    
    print("Analyzing different input types for curvature patterns:")
    print()
    
    all_results = []
    
    for test_input, description in test_cases:
        print(f"Input: '{test_input}'")
        print(f"Type: {description}")
        
        results = analyzer.analyze_sequence(test_input, sequence_length=6)
        pattern_metrics = results['pattern_metrics']
        
        print(f"Curvature mean: {pattern_metrics['curvature_mean']:.6f}")
        print(f"Curvature std:  {pattern_metrics['curvature_std']:.6f}")
        print(f"Low curvature ratio: {pattern_metrics['low_curvature_ratio']:.3f}")
        print(f"Pattern detected: {'Yes' if pattern_metrics['pattern_detected'] else 'No'}")
        print("-" * 40)
        
        all_results.append({
            'input': test_input,
            'description': description,
            'metrics': pattern_metrics
        })
    
    # Summary analysis
    print("Summary of Curvature Analysis:")
    print()
    curvature_means = [r['metrics']['curvature_mean'] for r in all_results]
    pattern_detections = [r['metrics']['pattern_detected'] for r in all_results]
    
    print(f"Average curvature across all inputs: {sum(curvature_means)/len(curvature_means):.6f}")
    print(f"Patterns detected in {sum(pattern_detections)}/{len(pattern_detections)} cases")
    print()
    
    return all_results

def framework_integration_demonstration():
    """Demonstrate integration with Z Framework parameters and concepts."""
    print("=" * 60)
    print("Z FRAMEWORK INTEGRATION DEMONSTRATION")
    print("=" * 60)
    
    analyzer = SHA256PatternAnalyzer()
    
    # Generate analysis with focus on Z Framework integration
    test_input = "z_framework_integration_test"
    results = analyzer.analyze_sequence(test_input, sequence_length=6)
    
    print("Z Framework Parameter Mapping:")
    print("-" * 28)
    params = results['framework_parameters']
    print(f"a = {params['a']} (SHA-256 bit length)")
    print(f"b = {params['b']:.6f} (e, natural logarithm base)")
    print(f"c = {params['c']:.6f} (e², discrete domain normalization)")
    print(f"Δ_max = {params['delta_max']:.6f} (maximum delta for Z computation)")
    print()
    
    print("Zeta Shift Attributes (sample from first object):")
    print("-" * 44)
    if results['zeta_attributes']:
        first_attrs = results['zeta_attributes'][0]
        zeta_keys = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        for key in zeta_keys:
            if key in first_attrs:
                value = float(first_attrs[key]) if hasattr(first_attrs[key], '__float__') else first_attrs[key]
                print(f"{key}: {value:.6f}")
    print()
    
    print("Discrete Domain Computation:")
    print("-" * 25)
    print(f"Z = n(Δ_n/Δ_max) formula applied to SHA-256 derivatives")
    print(f"Number of discrete derivatives: {len(results['discrete_derivatives'])}")
    print(f"Derivative range: [{min(results['discrete_derivatives']):,}, {max(results['discrete_derivatives']):,}]")
    print()
    
    print("Pattern Detection Summary:")
    print("-" * 23)
    metrics = results['pattern_metrics']
    print(f"✓ {metrics['num_samples']} samples analyzed")
    print(f"✓ Curvature-based detection: {'Pattern found' if metrics['pattern_detected'] else 'No pattern'}")
    print(f"✓ Low curvature ratio: {metrics['low_curvature_ratio']:.1%}")
    print()

def main():
    """Run all SHA-256 pattern detection examples."""
    print("SHA-256 CRYPTOGRAPHIC PATTERN DETECTION")
    print("Using Z Framework Discrete Domain Analysis")
    print("===============================================")
    print()
    
    try:
        # Run all examples
        basic_pattern_analysis_example()
        differential_cryptanalysis_example()
        avalanche_effect_demonstration()
        curvature_pattern_analysis()
        framework_integration_demonstration()
        
        print("=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("The SHA-256 pattern analyzer successfully demonstrates:")
        print("• Conversion of 256-bit hashes to number line points")
        print("• Discrete derivative computation for pattern detection")
        print("• Integration with Z Framework parameters (a=256, b=e, c=e²)")
        print("• Curvature-based non-randomness detection")
        print("• Differential cryptanalysis capabilities")
        print("• Zeta chain unfolding and attribute extraction")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)