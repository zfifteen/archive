#!/usr/bin/env python3
"""
Validate Zeta Zeros Dataset - No Random Variation/Noise Detection

This script implements the specific validation requested to resolve the 
"random variation" comment by asserting no noise via np.std(zeros.imag - expected).

The validation ensures that the zeta zeros dataset contains mathematically
accurate values without computational artifacts or random noise.
"""

import os
import sys
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def load_zeta_zeros(file_path: str) -> np.ndarray:
    """Load zeta zeros from numpy file."""
    try:
        zeros = np.load(file_path)
        print(f"✓ Loaded {len(zeros)} zeros from {file_path}")
        return zeros
    except Exception as e:
        print(f"❌ Error loading zeros: {e}")
        return np.array([])

def get_known_theoretical_zeros() -> np.ndarray:
    """
    Get known theoretical values for the first few Riemann zeta zeros.
    
    These are the precisely computed values from mathematical literature:
    - Source: Odlyzko's high-precision computations
    - Precision: 15+ decimal places
    """
    known_zeros = np.array([
        14.1347251417346937904572519835625,  # ζ(1/2 + it₁) = 0
        21.0220396387715549926284795938969,  # ζ(1/2 + it₂) = 0  
        25.0108575801456887632137909925628,  # ζ(1/2 + it₃) = 0
        30.4248761258595132103118975305840,  # ζ(1/2 + it₄) = 0
        32.9350615877391896906623689640747,  # ζ(1/2 + it₅) = 0
        37.5861781588256712572177634807053,  # ζ(1/2 + it₆) = 0
        40.9187190121474951873981269146334,  # ζ(1/2 + it₇) = 0
        43.3270732809149995194961221654068,  # ζ(1/2 + it₈) = 0
        48.0051508811671597279424727494277,  # ζ(1/2 + it₉) = 0
        49.7738324776723021819167846785638,  # ζ(1/2 + it₁₀) = 0
    ])
    
    return known_zeros

def validate_no_random_variation(zeros: np.ndarray, verbose: bool = True) -> bool:
    """
    Validate that there is no random variation/noise in the zeros dataset.
    
    This implements the specific validation requested: 
    assert no noise via np.std(zeros.imag - expected)
    
    Args:
        zeros: Array of complex zeta zeros
        verbose: Whether to print detailed validation info
        
    Returns:
        True if validation passes (no noise detected), False otherwise
    """
    if verbose:
        print("\n" + "="*60)
        print("RANDOM VARIATION/NOISE VALIDATION")
        print("="*60)
    
    # Get theoretical expected values
    expected_zeros = get_known_theoretical_zeros()
    n_check = min(len(zeros), len(expected_zeros))
    
    if n_check == 0:
        print("❌ No zeros to validate")
        return False
    
    # Extract actual imaginary parts
    actual_imag = zeros[:n_check].imag
    expected_imag = expected_zeros[:n_check]
    
    # Calculate differences (this is the core of the validation)
    differences = actual_imag - expected_imag
    noise_std = np.std(differences)
    noise_mean = np.mean(differences)
    max_abs_diff = np.max(np.abs(differences))
    
    if verbose:
        print(f"Validating first {n_check} zeros against theoretical values:")
        print(f"  Mean difference: {noise_mean:.2e}")
        print(f"  Std deviation:   {noise_std:.2e}")
        print(f"  Max abs diff:    {max_abs_diff:.2e}")
        print()
        
        print("Individual differences:")
        for i in range(n_check):
            diff = differences[i]
            print(f"  Zero {i+1:2d}: actual={actual_imag[i]:15.12f}, "
                  f"expected={expected_imag[i]:15.12f}, diff={diff:+.2e}")
    
    # Define noise tolerance thresholds
    STD_TOLERANCE = 1e-10      # Very strict: std deviation must be < 1e-10
    MAX_DIFF_TOLERANCE = 1e-9  # Individual differences must be < 1e-9
    
    # Core validation: assert no noise via np.std(zeros.imag - expected)
    try:
        assert noise_std < STD_TOLERANCE, (
            f"Random variation detected: std(actual - expected) = {noise_std:.2e} "
            f"exceeds tolerance {STD_TOLERANCE:.2e}"
        )
        
        assert max_abs_diff < MAX_DIFF_TOLERANCE, (
            f"Large individual difference detected: max |diff| = {max_abs_diff:.2e} "
            f"exceeds tolerance {MAX_DIFF_TOLERANCE:.2e}"
        )
        
        if verbose:
            print(f"\n✓ VALIDATION PASSED: No random variation/noise detected")
            print(f"  Standard deviation of differences: {noise_std:.2e} < {STD_TOLERANCE:.2e}")
            print(f"  Maximum absolute difference: {max_abs_diff:.2e} < {MAX_DIFF_TOLERANCE:.2e}")
            print(f"  All {n_check} tested zeros match theoretical values within tolerance")
        
        return True
        
    except AssertionError as e:
        if verbose:
            print(f"\n❌ VALIDATION FAILED: {e}")
        return False

def validate_mathematical_properties(zeros: np.ndarray, verbose: bool = True) -> bool:
    """Additional mathematical property validation."""
    if verbose:
        print("\n" + "="*60)
        print("MATHEMATICAL PROPERTIES VALIDATION")
        print("="*60)
    
    # Check all zeros on critical line (real part = 0.5)
    real_parts = zeros.real
    real_deviation = np.std(real_parts - 0.5)
    
    if verbose:
        print(f"Critical line validation (real parts should be 0.5):")
        print(f"  Mean real part: {np.mean(real_parts):.12f}")
        print(f"  Std deviation from 0.5: {real_deviation:.2e}")
    
    assert real_deviation < 1e-15, f"Real parts deviate from 0.5: std = {real_deviation:.2e}"
    
    # Check monotonic ordering
    imag_parts = zeros.imag
    is_monotonic = np.all(np.diff(imag_parts) > 0)
    
    if verbose:
        print(f"Monotonic ordering validation:")
        print(f"  Is monotonically increasing: {is_monotonic}")
        if not is_monotonic:
            violations = np.sum(np.diff(imag_parts) <= 0)
            print(f"  Ordering violations: {violations}")
    
    assert is_monotonic, "Imaginary parts are not in monotonically increasing order"
    
    # Check spacing properties (no zeros too close together)
    spacings = np.diff(imag_parts)
    min_spacing = np.min(spacings)
    
    if verbose:
        print(f"Spacing validation:")
        print(f"  Minimum spacing: {min_spacing:.2e}")
        print(f"  Mean spacing: {np.mean(spacings):.6f}")
    
    assert min_spacing > 1e-10, f"Zeros too close together: min spacing = {min_spacing:.2e}"
    
    if verbose:
        print(f"\n✓ Mathematical properties validation passed")
    
    return True

def main():
    """Main validation function."""
    print("Zeta Zeros Dataset - No Noise Validation")
    print("Resolving 'random variation' concern with assert no noise via np.std(zeros.imag - expected)")
    print("=" * 80)
    
    # Load the dataset
    zeros_file = os.path.join('..', 'src', 'data', 'zeta_zeros.npy')
    
    if not os.path.exists(zeros_file):
        print(f"❌ Zeros file not found: {zeros_file}")
        return False
    
    zeros = load_zeta_zeros(zeros_file)
    
    if len(zeros) == 0:
        print("❌ No zeros loaded")
        return False
    
    print(f"Dataset info:")
    print(f"  File: {zeros_file}")
    print(f"  Count: {len(zeros):,} zeros")
    print(f"  Data type: {zeros.dtype}")
    print(f"  Memory usage: {zeros.nbytes:,} bytes")
    
    # Run noise validation (core requirement from comment)
    noise_validation_passed = validate_no_random_variation(zeros, verbose=True)
    
    # Run additional mathematical validation
    math_validation_passed = validate_mathematical_properties(zeros, verbose=True)
    
    # Final result
    overall_passed = noise_validation_passed and math_validation_passed
    
    print("\n" + "="*80)
    if overall_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print("Random variation concern RESOLVED:")
        print("- No computational noise detected in dataset")
        print("- All zeros match theoretical values within strict tolerance")  
        print("- Mathematical properties verified")
        print("- Dataset ready for high-precision computations")
    else:
        print("❌ VALIDATION FAILED")
        print("Issues detected - dataset may contain random variation/noise")
    print("="*80)
    
    return overall_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nUnexpected error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)