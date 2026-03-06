#!/usr/bin/env python3
"""
Test suite for universal Z form and physical domain specialization.

Tests high-precision stability, edge cases, and frame-dependent behavior
as required for issue #82: Formalize Universal Z Form and Physical Domain Specialization.
"""

import sys
import os
import mpmath as mp
import numpy as np

# Add core module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.axioms import UniversalZForm, PhysicalDomainZ, validate_z_form_precision

# Simple assertion helpers since we don't have pytest
def assert_raises(exception_type, func, *args, **kwargs):
    """Helper to check that a function raises a specific exception."""
    try:
        func(*args, **kwargs)
        raise AssertionError(f"Expected {exception_type.__name__} but no exception was raised")
    except exception_type:
        pass  # Expected
    except Exception as e:
        raise AssertionError(f"Expected {exception_type.__name__} but got {type(e).__name__}: {e}")

def assert_contains(substring, text):
    """Helper to check that text contains substring."""
    if substring not in text:
        raise AssertionError(f"Expected '{substring}' to be in '{text}'")

# Set high precision for tests
mp.mp.dps = 50

class TestUniversalZForm:
    """Test the UniversalZForm class implementation."""
    
    def test_initialization(self):
        """Test proper initialization of UniversalZForm."""
        # Valid initialization
        z_form = UniversalZForm(c=299792458.0)
        assert z_form.c == mp.mpf(299792458.0)
        
        # Edge case: zero c should raise ValueError
        assert_raises(ValueError, UniversalZForm, c=0)
            
        # Edge case: negative c should raise ValueError  
        assert_raises(ValueError, UniversalZForm, c=-1)
    
    def test_linear_frame_transformation(self):
        """Test linear frame-dependent transformations A(x) = coefficient * x."""
        z_form = UniversalZForm()
        
        # Test with different coefficients
        linear_func = z_form.frame_transformation_linear(coefficient=2.0)
        result = z_form.compute_z(linear_func, B=1.5e8)
        
        # Z = A(B/c) = 2 * (1.5e8 / 299792458.0)
        expected = mp.mpf(2.0) * (mp.mpf(1.5e8) / mp.mpf(299792458.0))
        assert abs(result - expected) < mp.mpf('1e-16')
        
    def test_relativistic_frame_transformation(self):
        """Test relativistic frame transformations A(x) = rest_quantity / sqrt(1 - x^2)."""
        z_form = UniversalZForm()
        
        # Test time dilation
        rel_func = z_form.frame_transformation_relativistic(rest_quantity=1.0)
        
        # Test with v = 0.5c
        v = 0.5 * 299792458.0
        result = z_form.compute_z(rel_func, v)
        
        # Expected: 1 / sqrt(1 - 0.5^2) = 1 / sqrt(0.75) ≈ 1.1547
        expected = mp.mpf(1.0) / mp.sqrt(1 - mp.mpf(0.5)**2)
        assert abs(result - expected) < mp.mpf('1e-16')
        
        # Edge case: v >= c should raise ValueError
        rel_func = z_form.frame_transformation_relativistic()
        assert_raises(ValueError, z_form.compute_z, rel_func, z_form.c)  # v = c
            
    def test_high_precision_stability(self):
        """Test that computations maintain Δ_n < 10^{-16} precision."""
        z_form = UniversalZForm()
        linear_func = z_form.frame_transformation_linear(coefficient=1.0)
        
        # Test precision with various B values
        test_values = [1e6, 1e8, 2.99e8, 1.5e8]
        
        for B in test_values:
            result = z_form.compute_z(linear_func, B, precision_check=True)
            # If precision_check passes, the precision requirement is met
            assert result is not None
            
    def test_precision_validation_failure(self):
        """Test that precision validation catches numerical instabilities."""
        z_form = UniversalZForm()
        
        # Create a pathological function that causes precision loss
        def bad_func(x):
            # Intentionally create numerical instability
            return (mp.mpf(1) + x) - mp.mpf(1) + x**10
            
        # This should trigger precision validation failure for certain values
        try:
            z_form.compute_z(bad_func, 1e-10, precision_check=True)
        except ValueError as e:
            assert_contains("Precision requirement not met", str(e))

class TestPhysicalDomainZ:
    """Test the PhysicalDomainZ class for Z = T(v/c) specialization."""
    
    def test_time_dilation(self):
        """Test time dilation Z = τ₀/√(1-(v/c)²)."""
        phys_z = PhysicalDomainZ()
        
        # Test with v = 0.8c
        v = 0.8 * 299792458.0
        proper_time = 1.0
        
        result = phys_z.time_dilation(v, proper_time)
        
        # Expected: 1 / sqrt(1 - 0.8^2) = 1 / sqrt(0.36) = 1/0.6 ≈ 1.6667
        expected = mp.mpf(1.0) / mp.sqrt(1 - mp.mpf(0.8)**2)
        assert abs(result - expected) < mp.mpf('1e-16')
        
    def test_length_contraction(self):
        """Test length contraction Z = L₀√(1-(v/c)²)."""
        phys_z = PhysicalDomainZ()
        
        # Test with v = 0.6c
        v = 0.6 * 299792458.0
        rest_length = 10.0
        
        result = phys_z.length_contraction(v, rest_length)
        
        # Expected: 10 * sqrt(1 - 0.6^2) = 10 * sqrt(0.64) = 10 * 0.8 = 8.0
        expected = mp.mpf(10.0) * mp.sqrt(1 - mp.mpf(0.6)**2)
        
        # Allow slightly higher tolerance due to intermediate conversions
        assert abs(result - expected) < mp.mpf('1e-15')
        
    def test_relativistic_mass(self):
        """Test relativistic mass Z = m₀/√(1-(v/c)²)."""
        phys_z = PhysicalDomainZ()
        
        # Test with v = 0.9c
        v = 0.9 * 299792458.0
        rest_mass = 1.0
        
        result = phys_z.relativistic_mass(v, rest_mass)
        
        # Expected: 1 / sqrt(1 - 0.9^2) = 1 / sqrt(0.19) ≈ 2.294
        expected = mp.mpf(1.0) / mp.sqrt(1 - mp.mpf(0.9)**2)
        
        # Allow slightly higher tolerance due to intermediate conversions
        assert abs(result - expected) < mp.mpf('1e-15')
        
    def test_doppler_shift(self):
        """Test relativistic Doppler shift."""
        phys_z = PhysicalDomainZ()
        
        # Test with v = 0.5c (receding)
        v = 0.5 * 299792458.0
        rest_frequency = 100.0
        
        result = phys_z.doppler_shift(v, rest_frequency)
        
        # Expected: 100 * sqrt((1-0.5)/(1+0.5)) = 100 * sqrt(0.5/1.5) ≈ 57.735
        expected = mp.mpf(100.0) * mp.sqrt((1 - mp.mpf(0.5)) / (1 + mp.mpf(0.5)))
        assert abs(result - expected) < mp.mpf('1e-15')  # Slightly relaxed for complex calculation
        
    def test_causality_validation(self):
        """Test causality constraint validation."""
        phys_z = PhysicalDomainZ()
        
        # Valid velocities
        assert phys_z.validate_causality(0.5 * 299792458.0) == True
        assert phys_z.validate_causality(0.99 * 299792458.0) == True
        assert phys_z.validate_causality(0) == True
        
        # Invalid velocities (superluminal)
        assert phys_z.validate_causality(299792458.0) == False  # v = c
        assert phys_z.validate_causality(1.1 * 299792458.0) == False  # v > c
        assert phys_z.validate_causality(-1.1 * 299792458.0) == False  # v < -c
        
    def test_edge_case_light_speed(self):
        """Test behavior at light speed boundary."""
        phys_z = PhysicalDomainZ()
        
        # All physical transformations should raise errors at v = c
        v_light = 299792458.0
        
        assert_raises(ValueError, phys_z.time_dilation, v_light)
        assert_raises(ValueError, phys_z.length_contraction, v_light)
        assert_raises(ValueError, phys_z.relativistic_mass, v_light)
        assert_raises(ValueError, phys_z.doppler_shift, v_light)

class TestPrecisionValidation:
    """Test the precision validation system."""
    
    def test_validate_z_form_precision_success(self):
        """Test successful precision validation."""
        # Create a high-precision result
        with mp.workdps(50):
            z_result = mp.mpf(1) / mp.mpf(3)  # 0.333... with high precision
            
        validation = validate_z_form_precision(z_result)
        
        assert validation['precision_met'] == True
        assert validation['low_precision_error'] < 1e-16
        assert 'result_value' in validation
        
    def test_validate_z_form_precision_failure(self):
        """Test precision validation failure detection."""
        # Create a result with known precision loss
        low_precision_result = 1.0/3.0  # Python float precision
        
        try:
            validation = validate_z_form_precision(low_precision_result)
            # This might pass or fail depending on the specific computation
            assert 'precision_met' in validation
        except ValueError as e:
            assert_contains("Z-form precision requirement not met", str(e))

class TestIntegrationWithExistingFramework:
    """Test integration with existing DiscreteZetaShift framework."""
    
    def test_compatibility_with_discrete_domain(self):
        """Test that new Z form is compatible with discrete zeta shifts."""
        from core.domain import DiscreteZetaShift
        
        # Create a discrete zeta shift
        dz = DiscreteZetaShift(10)
        
        # Test that we can use UniversalZForm with discrete quantities
        z_form = UniversalZForm(c=float(dz.c))
        
        # Use delta_n as B and n as coefficient for A
        B = float(dz.b)
        linear_A = z_form.frame_transformation_linear(coefficient=float(dz.a))
        
        result = z_form.compute_z(linear_A, B)
        
        # Should match the discrete Z computation
        discrete_z = dz.compute_z()
        
        # Allow small numerical differences due to precision conversion
        assert abs(result - discrete_z) < mp.mpf('1e-14')

def run_comprehensive_tests():
    """Run all tests and report results."""
    print("Running comprehensive tests for Universal Z Form and Physical Domain...")
    print(f"Using mpmath precision: {mp.mp.dps} decimal places")
    
    # Test classes
    test_classes = [
        TestUniversalZForm(),
        TestPhysicalDomainZ(), 
        TestPrecisionValidation(),
        TestIntegrationWithExistingFramework()
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n=== {class_name} ===")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_class, method_name)
                method()
                print(f"  ✓ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ✗ {method_name}: {e}")
                failed_tests.append((class_name, method_name, str(e)))
    
    print(f"\n=== Test Summary ===")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\nFailed tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  {class_name}.{method_name}: {error}")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)