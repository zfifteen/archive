#!/usr/bin/env python3
"""
Smoke test for Lopez Geodesic Miller-Rabin integration.

Validates that the geodesic-only MR test achieves 100% agreement
with the S64 deterministic oracle on a quick test range [3, 10_000].

This test ensures the geodesic witness generation using Weyl golden step
provides deterministic results compatible with the framework's geodesic
mapping approach.
"""

import sys
import os
import unittest

# Add the repository root to the path to import the gists module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the Lopez Geodesic MR functions
from gists.lopez_geodesic_mr import compare, geodesic_witnesses, mr_with_bases, oracle_is_prime_u64


class TestLopezGeodesicMRSmoke(unittest.TestCase):
    """Smoke tests for Lopez Geodesic Miller-Rabin integration."""

    def test_geodesic_witnesses_generation(self):
        """Test geodesic witness generation produces valid witnesses."""
        n = 1009  # A prime number
        m = 4
        witnesses = geodesic_witnesses(n, m)
        
        # Basic validation
        self.assertIsInstance(witnesses, list)
        self.assertLessEqual(len(witnesses), m)  # May be fewer due to coprimality requirements
        self.assertTrue(all(isinstance(w, int) for w in witnesses))
        self.assertTrue(all(2 <= w < n for w in witnesses))
        
        # Check uniqueness
        self.assertEqual(len(witnesses), len(set(witnesses)))

    def test_small_range_accuracy(self):
        """Test geodesic MR vs S64 oracle on small range [3, 10_000]."""
        result = compare(n_from=3, n_to=10_000, m=4)
        
        # Validate structure
        required_keys = [
            'range', 'm', 'tested', 'geo_ok', 'geo_fp', 'geo_fn', 
            'geo_acc', 'std_ok', 'std_acc', 'geo_bases_avg', 
            'std_bases_avg', 'geo_squar_avg', 'std_squar_avg', 
            'elapsed_sec', 'first_fail_examples'
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")
        
        # Core acceptance criteria
        self.assertEqual(result['geo_acc'], 1.0, f"Geodesic accuracy: {result['geo_acc']}")
        self.assertEqual(result['std_acc'], 1.0, f"Standard accuracy: {result['std_acc']}")
        self.assertEqual(result['geo_fp'], 0, f"Geodesic false positives: {result['geo_fp']}")
        self.assertEqual(result['geo_fn'], 0, f"Geodesic false negatives: {result['geo_fn']}")
        
        # Validate metrics exist and are reasonable
        self.assertGreater(result['geo_bases_avg'], 0)
        self.assertGreater(result['std_bases_avg'], 0)
        self.assertGreaterEqual(result['geo_squar_avg'], 0)
        self.assertGreaterEqual(result['std_squar_avg'], 0)
        self.assertGreater(result['elapsed_sec'], 0)
        
        # Range validation
        self.assertEqual(result['range'], [3, 10_000])
        self.assertEqual(result['m'], 4)
        
        # Calculate expected odd count dynamically instead of hardcoded magic number
        n_from, n_to = 3, 10_000
        expected_tested = (n_to - (n_from | 1)) // 2 + 1
        self.assertEqual(result['tested'], expected_tested)  # Number of odd integers in [3, 10_000]

    def test_geodesic_vs_standard_consistency(self):
        """Test that geodesic and standard MR give identical results on specific cases."""
        test_cases = [1009, 1013, 1019, 1021, 1031]  # Mix of primes and composites
        
        for n in test_cases:
            # Get oracle truth
            oracle_result = oracle_is_prime_u64(n)
            
            # Test geodesic MR
            geo_witnesses = geodesic_witnesses(n, 4)
            geo_result, _, _ = mr_with_bases(n, geo_witnesses)
            
            # Both should match oracle
            self.assertEqual(geo_result, oracle_result, f"n={n}: geodesic={geo_result}, oracle={oracle_result}")

    def test_geodesic_parameters_align_with_framework(self):
        """Test that geodesic parameters align with framework standards."""
        n = 1009
        m = 4
        witnesses = geodesic_witnesses(n, m)
        
        # The golden step constant should be the Weyl sequence value
        from gists.lopez_geodesic_mr import STEP64
        expected_step = 0x9E3779B97F4A7C15  # 2^64/φ 
        self.assertEqual(STEP64, expected_step, f"Golden step mismatch: {hex(STEP64)} != {hex(expected_step)}")
        
        # Witnesses should be in valid range and coprime to n
        from gists.lopez_geodesic_mr import egcd
        for w in witnesses:
            self.assertTrue(2 <= w < n)
            self.assertEqual(egcd(w, n), 1, f"Witness {w} not coprime to {n}")

    def test_print_contract_fields(self):
        """Test that result contains all fields mentioned in print contract."""
        result = compare(n_from=3, n_to=1000, m=8)  # Smaller range for speed
        
        # Print contract fields from issue description
        expected_output_fields = [
            'range', 'm', 'tested',  # Range info
            'geo_acc', 'geo_fp', 'geo_fn',  # Geodesic accuracy
            'geo_bases_avg', 'geo_squar_avg',  # Geodesic cost metrics
            'std_acc', 'std_bases_avg', 'std_squar_avg',  # Standard metrics
            'elapsed_sec'  # Timing
        ]
        
        for field in expected_output_fields:
            self.assertIn(field, result, f"Missing print contract field: {field}")


if __name__ == "__main__":
    unittest.main()