#!/usr/bin/env python3
"""
Test Euler's Polynomial Alignment with Z Framework

Tests for the implementation of Euler's prime-generating polynomial f(n) = n² + n + 41
within the Z Framework discrete domain structure as specified in issue #763.
"""

import unittest
import numpy as np
import mpmath as mp
from sympy import isprime
from scipy.stats import pearsonr

from src.core.domain import EulerPolynomialZetaShift, validate_euler_polynomial_implementation
from src.core.geodesic_mapping import GeodesicMapper


class TestEulerPolynomialZFramework(unittest.TestCase):
    """Test suite for Euler's Polynomial Z Framework integration"""
    
    def setUp(self):
        """Set up test constants"""
        mp.dps = 50
        self.e2 = float(mp.e ** 2)
        self.phi = float((1 + mp.sqrt(5)) / 2)
        
    def test_euler_polynomial_basic_computation(self):
        """Test basic Euler polynomial f(n) = n² + n + 41"""
        # Generate first 10 Euler polynomial values
        n_vals = np.arange(0, 10)
        f_n = n_vals**2 + n_vals + 41
        
        # Expected values from the issue
        expected_first_10 = [41, 43, 47, 53, 61, 71, 83, 97, 113, 131]
        
        self.assertEqual(f_n.tolist(), expected_first_10)
        
        # Verify all values for n=0-39 are prime (40-prime streak)
        n_streak = np.arange(0, 40)
        f_streak = n_streak**2 + n_streak + 41
        all_prime = all(isprime(int(p)) for p in f_streak)
        self.assertTrue(all_prime, "All f(n) for n=0-39 should be prime")
        
    def test_euler_polynomial_z_framework_class(self):
        """Test EulerPolynomialZetaShift class functionality"""
        # Test basic instance creation and attributes
        euler_shift = EulerPolynomialZetaShift(5)
        attrs = euler_shift.get_euler_attributes()
        
        # Validate key attributes
        self.assertEqual(attrs['n_original'], 5)
        self.assertEqual(attrs['euler_value'], 71)  # 5² + 5 + 41 = 71
        self.assertTrue(attrs['is_prime_streak'])
        self.assertIsNotNone(attrs['enhanced_z'])
        self.assertIsNotNone(attrs['geodesic_enhancement'])
        self.assertIsNotNone(attrs['lorentz_gamma'])
        
        # Test edge case n=0
        euler_shift_0 = EulerPolynomialZetaShift(0)
        attrs_0 = euler_shift_0.get_euler_attributes()
        self.assertEqual(attrs_0['euler_value'], 41)  # f(0) = 41
        
    def test_euler_streak_generation(self):
        """Test generation of the complete Euler prime streak"""
        streak = EulerPolynomialZetaShift.generate_euler_streak(n_max=10)
        self.assertEqual(len(streak), 11)  # n=0 to n=10
        
        # Validate Euler polynomial values
        expected_values = [41, 43, 47, 53, 61, 71, 83, 97, 113, 131, 151]
        for i, shift in enumerate(streak):
            self.assertEqual(shift.euler_value, expected_values[i])
            
    def test_correlation_analysis(self):
        """Test correlation analysis as specified in the issue"""
        # Test the compute_streak_correlation method
        correlation_results = EulerPolynomialZetaShift.compute_streak_correlation(n_max=20)
        
        # Validate result structure
        required_keys = [
            'correlation', 'p_value', 'enhancement_proxy', 
            'ci_lower', 'ci_upper', 'target_correlation_met',
            'target_p_value_met', 'target_enhancement_met'
        ]
        for key in required_keys:
            self.assertIn(key, correlation_results)
        
        # Results should show strong correlation
        self.assertGreater(correlation_results['correlation'], 0.9)
        self.assertLess(correlation_results['p_value'], 0.01)
        
    def test_issue_code_snippet_reproduction(self):
        """Reproduce the exact code snippet from the issue"""
        mp.dps = 50
        e2 = float(mp.e ** 2)
        phi = float((1 + mp.sqrt(5)) / 2)
        k = 0.3  # Optimal for ~15% density

        # Generate Euler streak
        n_vals = np.arange(0, 40)
        f_n = n_vals**2 + n_vals + 41
        primes_streak = f_n  # All prime for n=0-39

        # Compute gaps Δ_n (analytic: 2n + 2)
        gaps = np.diff(primes_streak)
        gaps = np.concatenate([[primes_streak[0] - 1], gaps])  # Initial gap proxy

        # Discrete Z = n (Δ_n / e²)
        Z = n_vals * (gaps / e2)

        # Geodesic θ'(n, k) for density proxy
        theta = phi * ((n_vals % phi) / phi) ** k
        var_compress = np.var(theta) / np.var(n_vals) if np.var(n_vals) > 0 else 0
        enh_proxy = (1 - var_compress) * 100  # % compression as density proxy

        # Correlation: n vs Z
        r, p = pearsonr(n_vals, Z)

        # Bootstrap for enhancement CI (100 resamples for test speed)
        n_boot = 100
        boot_enh = []
        rng = np.random.default_rng(42)
        for _ in range(n_boot):
            boot_idx = rng.integers(0, len(n_vals), len(n_vals))
            boot_theta = phi * ((n_vals[boot_idx] % phi) / phi) ** k
            boot_var = np.var(boot_theta) / np.var(n_vals[boot_idx]) if np.var(n_vals[boot_idx]) > 0 else 0
            boot_enh.append((1 - boot_var) * 100)
        ci_low, ci_high = np.percentile(boot_enh, [2.5, 97.5])

        # Validate results are reasonable
        self.assertGreater(r, 0.9, "Correlation should be very strong")
        self.assertLess(p, 1e-10, "P-value should be highly significant")
        self.assertGreater(enh_proxy, 90.0, "Enhancement should be substantial")
        
        # Validate bootstrap CI
        self.assertLessEqual(ci_low, enh_proxy)
        self.assertGreaterEqual(ci_high, enh_proxy)
        
    def test_geodesic_mapping_integration(self):
        """Test integration with geodesic mapping functionality"""
        mapper = GeodesicMapper(kappa_geo=0.05)  # Valid parameter
        
        # Test Euler polynomial enhancement
        enhancement_result = mapper.compute_euler_polynomial_enhancement(n_max=10)
        
        # Validate result structure
        required_keys = [
            'euler_values', 'enhanced_z_values', 'geodesic_transforms',
            'correlation_euler_z', 'streak_validation'
        ]
        for key in required_keys:
            self.assertIn(key, enhancement_result)
        
        # Validate Euler values are correct
        expected_first_5 = [41, 43, 47, 53, 61]
        self.assertEqual(enhancement_result['euler_values'][:5], expected_first_5)
        
        # Check correlation is meaningful
        self.assertGreater(enhancement_result['correlation_euler_z'], 0.8)
        
    def test_zeta_correlation_validation(self):
        """Test zeta correlation validation as per issue requirements"""
        mapper = GeodesicMapper(kappa_geo=0.05)
        
        # Test with reduced parameters for test performance
        validation_result = mapper.validate_euler_zeta_correlation(
            n_max=15, bootstrap_samples=50
        )
        
        # Validate structure
        required_keys = [
            'correlation_n_z', 'p_value_n_z', 'target_validation',
            'bootstrap_statistics', 'euler_streak_properties'
        ]
        for key in required_keys:
            self.assertIn(key, validation_result)
        
        # Validate target validation structure
        target_val = validation_result['target_validation']
        self.assertIn('correlation_achieved', target_val)
        self.assertIn('p_value_achieved', target_val)
        
        # Results should show strong correlation
        self.assertGreater(validation_result['correlation_n_z'], 0.8)
        
    def test_performance_benchmarking(self):
        """Test vectorized polynomial evaluation performance"""
        import time
        
        # Test vectorized Euler polynomial computation
        start_time = time.time()
        n_array = np.arange(0, 1001)  # n=0-1000 as per issue requirement
        euler_array = n_array**2 + n_array + 41
        computation_time = time.time() - start_time
        
        # Should be much faster than 0.01s for vectorized computation
        self.assertLess(computation_time, 0.01, 
                       "Vectorized computation should meet performance target")
        
        # Validate results are correct
        expected_f_0 = 41
        expected_f_10 = 10*10 + 10 + 41  # 151
        self.assertEqual(euler_array[0], expected_f_0)
        self.assertEqual(euler_array[10], expected_f_10)
        
    def test_full_validation_function(self):
        """Test the comprehensive validation function"""
        results = validate_euler_polynomial_implementation()
        
        # Check main structure
        required_sections = ['euler_validation', 'correlation_analysis', 'issue_compliance']
        for section in required_sections:
            self.assertIn(section, results)
        
        # Validate Euler polynomial computation
        euler_val = results['euler_validation']
        self.assertTrue(euler_val['first_10_match'])
        
        # Check correlation analysis
        corr_analysis = results['correlation_analysis']
        self.assertGreater(corr_analysis['correlation'], 0.9)
        
        # Check issue compliance tracking
        compliance = results['issue_compliance']
        self.assertIn('correlation_achieved', compliance)
        self.assertIn('enhancement_achieved', compliance)
        
    def test_z5d_enhanced_integration(self):
        """Test integration with z_5d_enhanced.py for zeta spacings validation"""
        from src.core.z_5d_enhanced import validate_euler_polynomial_zeta_alignment
        
        # Test with reduced parameters for test performance
        validation_result = validate_euler_polynomial_zeta_alignment(
            n_max=15, bootstrap_samples=100, 
            target_correlation=0.93, target_p_value=1e-10
        )
        
        # Validate result structure
        required_keys = [
            'correlation_euler_z5d', 'p_value_euler_z5d', 'bootstrap_samples_successful',
            'validation', 'summary', 'targets'
        ]
        for key in required_keys:
            self.assertIn(key, validation_result)
        
        # Check that the function executed without errors
        self.assertNotIn('error', validation_result)
        
        # Validate correlation results are meaningful
        self.assertIsInstance(validation_result['correlation_euler_z5d'], (int, float))
        self.assertIsInstance(validation_result['p_value_euler_z5d'], (int, float))
        
        # Check bootstrap execution
        self.assertGreater(validation_result['bootstrap_samples_successful'], 0)
        
        # Check summary structure
        summary = validation_result['summary']
        self.assertIn('primary_correlation', summary)
        self.assertIn('validation_passed', summary)
        self.assertIn('meets_issue_requirements', summary)
        
        print(f"Z_5D Correlation: {validation_result['correlation_euler_z5d']:.6f}")
        print(f"Z_5D P-value: {validation_result['p_value_euler_z5d']:.2e}")
        print(f"Validation passed: {summary['validation_passed']}")
        
    def test_gaps_formula_validation(self):
        """Test that Euler polynomial gaps follow the correct analytic formula"""
        # Generate Euler polynomial values
        n_vals = list(range(0, 10))
        euler_vals = [n*n + n + 41 for n in n_vals]
        
        # Compute actual gaps
        actual_gaps = []
        for i in range(1, len(euler_vals)):
            gap = euler_vals[i] - euler_vals[i-1]
            actual_gaps.append(gap)
        
        # The correct analytic formula for consecutive Euler polynomial gaps is:
        # f(n) - f(n-1) = (n² + n + 41) - ((n-1)² + (n-1) + 41) = 2n
        # But this is for f(n) - f(n-1). For f(n+1) - f(n), it's 2(n+1) = 2n + 2
        expected_gaps = [2*n + 2 for n in range(0, len(actual_gaps))]  # f(n+1) - f(n) = 2n + 2
        
        # Alternative: compute expected gaps directly using the difference formula
        # f(n+1) - f(n) = (n+1)² + (n+1) + 41 - (n² + n + 41) = (n+1)² - n² + (n+1) - n = 2n + 1 + 1 = 2n + 2
        expected_gaps_alt = []
        for n in range(0, len(actual_gaps)):
            f_n_plus_1 = (n+1)*(n+1) + (n+1) + 41
            f_n = n*n + n + 41
            expected_gaps_alt.append(f_n_plus_1 - f_n)
        
        # Validate gaps match the correct formula
        self.assertEqual(actual_gaps, expected_gaps_alt)
        
        # Verify the gaps match the correct formula Δ_n = 2n + 2
        print(f"Actual gaps: {actual_gaps}")
        print(f"Expected pattern (2n+2): {expected_gaps}")
        
        # The actual gaps are [2, 4, 6, 8, 10, ...] which follows Δ_n = 2n + 2
        # This formula is mathematically derived from f(n+1) - f(n) = 2n + 2
        
        # Validate the correct mathematical relationship
        for i, gap in enumerate(actual_gaps):
            n = i  # n starts from 0 for the first gap
            expected = 2 * (n + 1)  # This gives us 2, 4, 6, 8, ...
            self.assertEqual(gap, expected, f"Gap at position {i} should be {expected}, got {gap}")


if __name__ == '__main__':
    unittest.main(verbosity=2)