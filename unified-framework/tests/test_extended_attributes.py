#!/usr/bin/env python3
"""
Test extended DiscreteZetaShift attributes (scaled_E and Δ_n).

This test validates the implementation of the extended attributes
as requested in issue #296.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import mpmath as mp
from src.core.domain import DiscreteZetaShift
from src.core.hybrid_prime_identification import compute_dzs_attributes

# Set precision for consistency
mp.mp.dps = 50

class TestExtendedAttributes(unittest.TestCase):
    """Test extended DiscreteZetaShift attributes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_values = [10, 17, 25, 100, 997]  # Mix of primes and composites
        self.phi = (1 + mp.sqrt(5)) / 2  # Golden ratio
        
    def test_scaled_E_attribute_exists(self):
        """Test that scaled_E attribute exists and is accessible."""
        for n in self.test_values:
            dzs = DiscreteZetaShift(n)
            attrs = dzs.attributes
            
            self.assertIn('scaled_E', attrs, 
                         f"scaled_E attribute missing for n={n}")
            
    def test_delta_n_attribute_exists(self):
        """Test that Δ_n attribute exists and is accessible."""
        for n in self.test_values:
            dzs = DiscreteZetaShift(n)
            attrs = dzs.attributes
            
            self.assertIn('Δ_n', attrs, 
                         f"Δ_n attribute missing for n={n}")
            
    def test_scaled_E_computation(self):
        """Test that scaled_E equals E/φ."""
        for n in self.test_values:
            dzs = DiscreteZetaShift(n)
            attrs = dzs.attributes
            
            expected_scaled_E = attrs['E'] / self.phi
            actual_scaled_E = attrs['scaled_E']
            
            relative_error = abs(float(actual_scaled_E - expected_scaled_E)) / float(abs(expected_scaled_E))
            
            self.assertLess(relative_error, 1e-10, 
                           f"scaled_E computation incorrect for n={n}: "
                           f"expected {expected_scaled_E}, got {actual_scaled_E}")
            
    def test_delta_n_matches_internal_value(self):
        """Test that Δ_n matches the internal delta_n value."""
        for n in self.test_values:
            dzs = DiscreteZetaShift(n)
            attrs = dzs.attributes
            
            # Get internal delta_n value
            internal_delta_n = dzs.delta_n
            exposed_delta_n = attrs['Δ_n']
            
            self.assertEqual(float(internal_delta_n), float(exposed_delta_n),
                           f"Δ_n doesn't match internal delta_n for n={n}")
            
    def test_attributes_count(self):
        """Test that we have the expected number of attributes."""
        dzs = DiscreteZetaShift(10)
        attrs = dzs.attributes
        
        # Original attributes: a, b, c, z, D, E, F, G, H, I, J, K, L, M, N, O (16)
        # Extended attributes: scaled_E, Δ_n, Z (3)
        # Total: 19 attributes
        expected_count = 19
        actual_count = len(attrs)
        
        self.assertEqual(actual_count, expected_count,
                        f"Expected {expected_count} attributes, got {actual_count}")
        
    def test_hybrid_prime_identification_compatibility(self):
        """Test that compute_dzs_attributes works with extended attributes."""
        for n in self.test_values:
            try:
                dzs_attrs = compute_dzs_attributes(n)
                
                # Check that new attributes are present
                self.assertIsInstance(dzs_attrs.scaled_E, float,
                                    f"scaled_E not a float in DZS attributes for n={n}")
                self.assertIsInstance(dzs_attrs.delta_n, float,
                                    f"delta_n not a float in DZS attributes for n={n}")
                
                # Verify they match the direct calculation
                dzs = DiscreteZetaShift(n)
                direct_attrs = dzs.attributes
                
                self.assertAlmostEqual(dzs_attrs.scaled_E, float(direct_attrs['scaled_E']), places=10,
                                     msg=f"DZS attributes scaled_E mismatch for n={n}")
                self.assertAlmostEqual(dzs_attrs.delta_n, float(direct_attrs['Δ_n']), places=10,
                                     msg=f"DZS attributes delta_n mismatch for n={n}")
                
            except Exception as e:
                self.fail(f"compute_dzs_attributes failed for n={n}: {e}")
                
    def test_extended_attributes_numerical_stability(self):
        """Test numerical stability of extended attributes for larger values."""
        large_values = [1000, 10000]
        
        for n in large_values:
            dzs = DiscreteZetaShift(n)
            attrs = dzs.attributes
            
            # Check that values are finite and reasonable
            self.assertTrue(mp.isfinite(attrs['scaled_E']),
                           f"scaled_E not finite for n={n}")
            self.assertTrue(mp.isfinite(attrs['Δ_n']),
                           f"Δ_n not finite for n={n}")
            
            # scaled_E should be positive
            self.assertGreater(float(attrs['scaled_E']), 0,
                             f"scaled_E not positive for n={n}")
            
            # Δ_n should be positive (frame shift)
            self.assertGreater(float(attrs['Δ_n']), 0,
                             f"Δ_n not positive for n={n}")


if __name__ == '__main__':
    unittest.main()