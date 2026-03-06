#!/usr/bin/env python3
"""
Z_5D Enhanced Features Demonstration

This script demonstrates the enhancements made to the Z_5D Prime Enumeration
Predictor based on code review feedback, including:

1. Scale-specific calibration for optimal accuracy across different ranges
2. Enhanced error handling for edge cases
3. Extended validation capabilities
4. Dynamic parameter selection based on input scale

The enhancements address the code review suggestions for improved performance
at ultra-large scales and better robustness.
"""

import numpy as np
import sys
import os

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

from z_framework.discrete.z5d_predictor import (
    z5d_prime, 
    extended_scale_validation,
    validate_z5d_accuracy,
    _get_optimal_calibration,
    SCALE_CALIBRATIONS
)


def demonstrate_scale_specific_calibration():
    """Demonstrate scale-specific parameter calibration."""
    print("=" * 60)
    print("SCALE-SPECIFIC CALIBRATION DEMONSTRATION")
    print("=" * 60)
    
    print("\nCalibration parameters by scale:")
    print("Scale Range" + " " * 8 + "c parameter" + " " * 6 + "k* parameter")
    print("-" * 50)
    
    for scale_name, params in SCALE_CALIBRATIONS.items():
        max_k_str = f"≤ 10^{int(np.log10(params['max_k']))}" if params['max_k'] != float('inf') else "> 10^12"
        print(f"{scale_name:12} ({max_k_str:8}): c={params['c']:9.6f}, k*={params['k_star']:8.5f}")
    
    print("\nDemonstrating automatic parameter selection:")
    test_k_values = [1e3, 1e5, 1e8, 1e12]
    
    for k in test_k_values:
        c, k_star = _get_optimal_calibration(k)
        pred_auto = z5d_prime(k, auto_calibrate=True)
        pred_default = z5d_prime(k, auto_calibrate=False)
        
        print(f"\nk = {k:.0e}:")
        print(f"  Auto calibration: c={c:.6f}, k*={k_star:.6f} → prediction={pred_auto:.2e}")
        print(f"  Default params:   c={-0.00247:.6f}, k*={0.04449:.6f} → prediction={pred_default:.2e}")
        print(f"  Difference: {abs(pred_auto - pred_default):.2e}")


def demonstrate_enhanced_error_handling():
    """Demonstrate enhanced input validation and error handling."""
    print("\n" + "=" * 60)
    print("ENHANCED ERROR HANDLING DEMONSTRATION")
    print("=" * 60)
    
    test_cases = [
        ("Negative values", [-1, 1000]),
        ("NaN values", [np.nan, 1000]),
        ("Infinite values", [np.inf, 1000]),
        ("Mixed valid/invalid", [0, 1000, 5000]),
        ("Float values (should work with warning)", [1000.5, 2000.7])
    ]
    
    for description, test_input in test_cases:
        print(f"\n{description}:")
        try:
            result = z5d_prime(test_input)
            print(f"  ✓ Result: {result}")
        except (ValueError, TypeError) as e:
            print(f"  ✓ Correctly handled error: {str(e)}")
        except Exception as e:
            print(f"  ✗ Unexpected error: {str(e)}")


def demonstrate_extended_validation():
    """Demonstrate extended validation capabilities."""
    print("\n" + "=" * 60)
    print("EXTENDED VALIDATION DEMONSTRATION")
    print("=" * 60)
    
    # Test with moderate scales (SymPy computation limit)
    test_scales = [1000, 5000, 10000]
    
    print(f"\nRunning extended validation for k = {test_scales}...")
    try:
        results = extended_scale_validation(test_scales)
        
        print("\nValidation Results:")
        print("-" * 40)
        
        for k, result in results['scale_results'].items():
            auto_error_pct = result['auto_error'] * 100
            default_error_pct = result['default_error'] * 100
            improvement = result['improvement_ratio']
            
            print(f"\nk = {k:,}:")
            print(f"  True prime: {result['true_prime']:,}")
            print(f"  Auto prediction: {result['auto_prediction']:.2f}")
            print(f"  Auto error: {auto_error_pct:.4f}%")
            print(f"  Default error: {default_error_pct:.4f}%")
            print(f"  Improvement ratio: {improvement:.2f}x")
        
        summary = results['performance_summary']
        print(f"\nOverall Performance Summary:")
        print(f"  Auto calibration mean error: {summary['auto_mean_error']*100:.4f}%")
        print(f"  Default parameters mean error: {summary['default_mean_error']*100:.4f}%")
        print(f"  Mean improvement ratio: {summary['mean_improvement_ratio']:.2f}x")
        
        effectiveness = results['calibration_effectiveness']
        print(f"\nCalibration Effectiveness:")
        print(f"  Auto calibration better in {effectiveness['auto_calibration_better']}/{effectiveness['total_comparisons']} cases")
        print(f"  Effectiveness ratio: {effectiveness['effectiveness_ratio']:.1%}")
        
    except Exception as e:
        print(f"Error in extended validation: {e}")


def demonstrate_benchmark_comparison():
    """Demonstrate accuracy comparison with original benchmarks."""
    print("\n" + "=" * 60)
    print("BENCHMARK COMPARISON WITH CODE REVIEW DATA")
    print("=" * 60)
    
    # Benchmark data from the code review
    benchmark_data = [
        (1000, 7919),
        (10000, 104729),
        (100000, 1299709),
        (1000000, 15485863),
    ]
    
    print("\nComparison with code review benchmark data:")
    print("k" + " " * 10 + "True Prime" + " " * 4 + "Z_5D Prediction" + " " * 4 + "Error (%)")
    print("-" * 70)
    
    for k, true_prime in benchmark_data:
        if k <= 100000:  # Limit for reasonable computation time
            try:
                prediction = z5d_prime(k, auto_calibrate=True)
                error_pct = abs((prediction - true_prime) / true_prime) * 100
                print(f"{k:12,} {true_prime:14,} {prediction:18,.2f} {error_pct:9.4f}%")
            except Exception as e:
                print(f"{k:12,} {true_prime:14,} {'Error':>18} {str(e)}")
        else:
            # For larger k, just show the prediction without validation
            prediction = z5d_prime(k, auto_calibrate=True)
            print(f"{k:12,} {true_prime:14,} {prediction:18,.2f} {'N/A':>9}")


def main():
    """Run all demonstrations."""
    print("Z_5D ENHANCED FEATURES DEMONSTRATION")
    print("Based on code review feedback by Dionisio Alberto Lopez III")
    print("Demonstrates scale-specific calibration, enhanced error handling,")
    print("and extended validation capabilities.")
    
    try:
        demonstrate_scale_specific_calibration()
        demonstrate_enhanced_error_handling()
        demonstrate_extended_validation()
        demonstrate_benchmark_comparison()
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nKey improvements implemented:")
        print("✓ Scale-specific parameter calibration for optimal accuracy")
        print("✓ Enhanced input validation with comprehensive error handling")
        print("✓ Extended validation framework for multi-scale analysis")
        print("✓ Automatic parameter selection based on input scale")
        print("✓ Improved documentation and error messages")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()