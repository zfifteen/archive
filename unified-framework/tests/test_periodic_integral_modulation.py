"""
Test suite for Periodic Integral Modulation implementation.

This module provides comprehensive testing for the periodic integral
∫₀^{2π} dx / (1 + e^{sin x}) = π and its integration with Z Framework
geodesic mapping for enhanced prime density prediction.
"""

import pytest
import numpy as np
import sys
import os
from math import pi, sin, exp
from typing import Dict, List

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.core.periodic_integral_modulation import (
        PeriodicIntegralModulator, 
        demonstrate_periodic_integral_modulation
    )
except ImportError:
    # Handle direct execution - add src directory to path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))
    from periodic_integral_modulation import (
        PeriodicIntegralModulator,
        demonstrate_periodic_integral_modulation
    )


class TestPeriodicIntegralModulation:
    """Test cases for the periodic integral modulation implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.modulator = PeriodicIntegralModulator()
        self.test_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        self.tolerance = 1e-10
    
    def test_initialization(self):
        """Test periodic integral modulator initialization"""
        assert self.modulator.precision_dps > 0
        assert self.modulator.kappa_geo > 0
        assert self.modulator.geodesic_mapper is not None
        assert hasattr(self.modulator, 'pi_mp')
        assert hasattr(self.modulator, 'e_mp')
    
    def test_integrand_computation(self):
        """Test integrand f(x) = 1 / (1 + e^{sin x}) computation"""
        # Test scalar input
        x = pi / 4
        result = self.modulator.integrand(x)
        expected = 1.0 / (1.0 + exp(sin(x)))
        assert abs(result - expected) < self.tolerance
        
        # Test array input
        x_array = np.array([0, pi/4, pi/2, pi, 3*pi/2])
        results = self.modulator.integrand(x_array)
        expected_array = 1.0 / (1.0 + np.exp(np.sin(x_array)))
        np.testing.assert_allclose(results, expected_array, atol=self.tolerance)
        
        # Test boundary conditions
        assert 0 < self.modulator.integrand(0) < 1
        assert 0 < self.modulator.integrand(pi) < 1
        assert 0 < self.modulator.integrand(2*pi) < 1
    
    def test_high_precision_integrand(self):
        """Test high-precision integrand computation with mpmath"""
        import mpmath as mp
        
        # Test high-precision computation
        x_mp = mp.mpf(pi / 4)
        result = self.modulator.integrand_high_precision(x_mp)
        
        # Verify result is an mpmath float
        assert isinstance(result, mp.mpf)
        
        # Compare with standard precision
        standard_result = self.modulator.integrand(float(x_mp))
        assert abs(float(result) - standard_result) < 1e-14
    
    def test_periodic_integral_numerical(self):
        """Test numerical computation of the periodic integral"""
        result = self.modulator.compute_periodic_integral_numerical()
        
        # Verify result structure
        required_keys = ['value', 'error', 'exact_pi', 'deviation', 'relative_error', 'is_pi_exact']
        for key in required_keys:
            assert key in result
        
        # Verify integral equals π within tolerance
        assert abs(result['value'] - pi) < 1e-10
        assert result['is_pi_exact']
        assert result['deviation'] < 1e-10
        assert result['relative_error'] < 1e-11
        
        # Test alternative integration method
        result_adaptive = self.modulator.compute_periodic_integral_numerical(method='adaptive')
        assert abs(result_adaptive['value'] - pi) < 1e-9
    
    def test_periodic_integral_analytical(self):
        """Test analytical computation with high-precision methods"""
        result = self.modulator.compute_periodic_integral_analytical()
        
        # Verify result structure
        required_keys = ['value_mp', 'value_float', 'exact_pi_mp', 'deviation_mp', 'is_pi_exact']
        for key in required_keys:
            assert key in result
        
        # Verify high-precision integral equals π
        assert result['is_pi_exact']
        assert float(result['deviation_mp']) < 1e-15
        assert abs(result['value_float'] - pi) < 1e-14
    
    def test_symmetry_property_validation(self):
        """Test the symmetry property f(x) + f(x + π) = 1"""
        result = self.modulator.validate_symmetry_property(n_points=100)
        
        # Verify result structure
        required_keys = ['max_deviation', 'mean_deviation', 'symmetry_valid', 'n_points']
        for key in required_keys:
            assert key in result
        
        # Verify symmetry property holds
        assert result['symmetry_valid']
        assert result['max_deviation'] < 1e-12
        assert result['mean_deviation'] < 1e-13
        assert abs(result['actual_mean_sum'] - 1.0) < 1e-12
        
        # Test with different numbers of points
        result_1000 = self.modulator.validate_symmetry_property(n_points=1000)
        assert result_1000['symmetry_valid']
    
    def test_symmetry_property_manual_verification(self):
        """Manually verify the symmetry property at specific points"""
        test_points = [0, pi/6, pi/4, pi/3, pi/2, 2*pi/3]
        
        for x in test_points:
            f_x = self.modulator.integrand(x)
            f_x_plus_pi = self.modulator.integrand(x + pi)
            symmetry_sum = f_x + f_x_plus_pi
            
            # Verify f(x) + f(x + π) = 1
            assert abs(symmetry_sum - 1.0) < 1e-14, f"Symmetry failed at x={x}"
    
    def test_resonance_simulation(self):
        """Test periodic resonance modulation for geodesic enhancement"""
        result = self.modulator.resonance_simulation(self.test_primes[:10])
        
        # Verify result structure
        required_keys = ['n_values', 'standard_geodesic', 'modulated_geodesic', 
                        'enhancement_ratios', 'mean_enhancement', 'enhancement_achieved']
        for key in required_keys:
            assert key in result
        
        # Verify modulation creates enhancement
        assert len(result['modulated_geodesic']) == len(self.test_primes[:10])
        assert len(result['enhancement_ratios']) == len(self.test_primes[:10])
        assert result['mean_enhancement'] > 0
        
        # Test with different parameters
        result_high_amp = self.modulator.resonance_simulation(
            self.test_primes[:5], amplitude=0.2, frequency=10.0
        )
        assert result_high_amp['amplitude'] == 0.2
        assert result_high_amp['frequency'] == 10.0
    
    def test_density_enhancement_computation(self):
        """Test prime density enhancement with bootstrap validation"""
        result = self.modulator.compute_density_enhancement(
            self.test_primes, bootstrap_samples=50
        )
        
        # Verify result structure
        required_keys = ['standard_enhancement', 'modulated_enhancement', 
                        'confidence_interval', 'ci_lower', 'ci_upper', 'bootstrap_samples']
        for key in required_keys:
            assert key in result
        
        # Verify bootstrap statistics
        assert result['bootstrap_samples'] == 50
        assert len(result['confidence_interval']) == 2
        assert result['ci_lower'] <= result['ci_upper']
        assert result['n_primes'] == len(self.test_primes)
        
        # Test with minimal prime list
        with pytest.warns(UserWarning):
            result_small = self.modulator.compute_density_enhancement([2, 3, 5])
    
    def test_integral_exact_pi_validation(self):
        """Test comprehensive validation that integral equals π exactly"""
        result = self.modulator.validate_integral_exact_pi()
        
        # Verify result structure
        required_keys = ['numerical_valid', 'analytical_valid', 'symmetry_valid', 
                        'all_valid', 'validation_summary']
        for key in required_keys:
            assert key in result
        
        # Verify all validation methods pass
        assert result['numerical_valid']
        assert result['analytical_valid'] 
        assert result['symmetry_valid']
        assert result['all_valid']
        assert 'PASS' in result['validation_summary']
        
        # Verify deviations are within tolerance
        assert result['numerical_deviation'] < 1e-10
        assert result['analytical_deviation'] < 1e-15
        assert result['symmetry_max_deviation'] < 1e-12
    
    def test_caching_mechanism(self):
        """Test that results are properly cached"""
        # First computation should populate cache
        result1 = self.modulator.compute_periodic_integral_numerical()
        assert self.modulator._cached_integral_result is not None
        
        # Second computation should use cache
        result2 = self.modulator.compute_periodic_integral_numerical()
        assert result1 == result2
        
        # Test symmetry caching
        symmetry1 = self.modulator.validate_symmetry_property()
        assert self.modulator._cached_symmetry_validation is not None
        
        symmetry2 = self.modulator.validate_symmetry_property()
        assert symmetry1 == symmetry2
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with minimum valid kappa_geo value for geodesic mapper
        # 0.05 is the minimum value that ensures numerical stability in geodesic calculations
        MIN_KAPPA_GEO = 0.05
        small_kappa_modulator = PeriodicIntegralModulator(kappa_geo=MIN_KAPPA_GEO)
        result = small_kappa_modulator.compute_periodic_integral_numerical()
        assert result['is_pi_exact']
        
        # Test with single prime
        single_prime_result = self.modulator.resonance_simulation([2])
        assert len(single_prime_result['modulated_geodesic']) == 1
        
        # Test with empty list (should handle gracefully)
        empty_result = self.modulator.resonance_simulation([])
        assert len(empty_result['modulated_geodesic']) == 0
    
    def test_mathematical_properties(self):
        """Test fundamental mathematical properties of the integral"""
        # Test integrand properties
        x_test = np.linspace(0, 2*pi, 100)
        f_values = self.modulator.integrand(x_test)
        
        # Integrand should be positive everywhere
        assert np.all(f_values > 0)
        
        # Integrand should be bounded between 0 and 1
        assert np.all(f_values < 1)
        
        # Test periodicity properties
        period_shift = 2 * pi
        f_shifted = self.modulator.integrand(x_test + period_shift)
        np.testing.assert_allclose(f_values, f_shifted, atol=1e-14)
    
    def test_z_framework_integration(self):
        """Test integration with Z Framework geodesic mapping"""
        # Verify geodesic mapper is properly initialized
        assert self.modulator.geodesic_mapper is not None
        assert hasattr(self.modulator.geodesic_mapper, 'enhanced_geodesic_transform')
        
        # Test geodesic transformation works
        test_n = 10
        geodesic_value = self.modulator.geodesic_mapper.enhanced_geodesic_transform(test_n)
        assert geodesic_value > 0
        
        # Test that modulation affects geodesic values
        resonance_result = self.modulator.resonance_simulation([test_n])
        standard_val = resonance_result['standard_geodesic'][0]
        modulated_val = resonance_result['modulated_geodesic'][0]
        
        # Values should be different (modulation effect)
        assert abs(standard_val - modulated_val) > 1e-10


class TestPeriodicIntegralModulationIntegration:
    """Integration tests for the complete system"""
    
    def test_complete_demonstration(self):
        """Test the complete demonstration function"""
        results = demonstrate_periodic_integral_modulation()
        
        # Verify result structure
        required_keys = ['pi_validation', 'density_enhancement', 'resonance_simulation', 
                        'demonstration_complete', 'summary']
        for key in required_keys:
            assert key in results
        
        # Verify demonstration completed successfully
        assert results['demonstration_complete']
        
        # Verify summary results
        summary = results['summary']
        assert 'integral_equals_pi' in summary
        assert 'density_target_achieved' in summary
        assert 'resonance_enhancement_achieved' in summary
    
    def test_performance_benchmarking(self):
        """Test performance of key computations"""
        import time
        
        modulator = PeriodicIntegralModulator()
        
        # Benchmark numerical integration
        start_time = time.time()
        numerical_result = modulator.compute_periodic_integral_numerical()
        numerical_time = time.time() - start_time
        
        assert numerical_time < 1.0  # Should complete within 1 second
        assert numerical_result['is_pi_exact']
        
        # Benchmark symmetry validation
        start_time = time.time()
        symmetry_result = modulator.validate_symmetry_property(n_points=1000)
        symmetry_time = time.time() - start_time
        
        assert symmetry_time < 0.5  # Should complete within 0.5 seconds
        assert symmetry_result['symmetry_valid']
    
    def test_precision_scaling(self):
        """Test behavior with different precision levels"""
        # Test with different precision levels
        precision_levels = [15, 25, 35]
        
        for precision in precision_levels:
            modulator = PeriodicIntegralModulator(precision_dps=precision)
            analytical_result = modulator.compute_periodic_integral_analytical()
            
            assert analytical_result['is_pi_exact']
            assert analytical_result['precision_dps'] == precision
            
            # Higher precision should give better results
            if precision > 15:
                assert float(analytical_result['deviation_mp']) < 1e-20


def test_module_imports():
    """Test that all required modules import correctly"""
    try:
        from src.core.periodic_integral_modulation import PeriodicIntegralModulator
        from src.core.geodesic_mapping import GeodesicMapper
        # Test that imported classes are callable
        assert callable(PeriodicIntegralModulator)
        assert callable(GeodesicMapper)
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_mathematical_constants():
    """Test mathematical constants and relationships"""
    modulator = PeriodicIntegralModulator()
    
    # Test π value accuracy
    pi_float = float(modulator.pi_mp)
    assert abs(pi_float - pi) < 1e-15
    
    # Test e value accuracy
    e_float = float(modulator.e_mp)
    import math
    assert abs(e_float - math.e) < 1e-15


if __name__ == "__main__":
    # Run basic test when executed directly
    print("🧪 Testing Periodic Integral Modulation Implementation")
    
    # Basic functionality test
    try:
        modulator = PeriodicIntegralModulator()
        
        # Test integral computation
        numerical_result = modulator.compute_periodic_integral_numerical()
        print(f"✓ Numerical integration: {numerical_result['value']:.15f}")
        print(f"  Deviation from π: {numerical_result['deviation']:.2e}")
        print(f"  Is π exact: {numerical_result['is_pi_exact']}")
        
        # Test symmetry property
        symmetry_result = modulator.validate_symmetry_property()
        print(f"✓ Symmetry validation: {symmetry_result['symmetry_valid']}")
        print(f"  Max deviation: {symmetry_result['max_deviation']:.2e}")
        
        # Test complete validation
        complete_validation = modulator.validate_integral_exact_pi()
        print(f"✓ Complete validation: {complete_validation['all_valid']}")
        print(f"  Status: {complete_validation['validation_summary']}")
        
        print("🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()