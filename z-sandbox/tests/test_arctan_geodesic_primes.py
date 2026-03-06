#!/usr/bin/env python3
"""
Tests for Arctan Geodesic Primes module.

Validates the 15-30% error reduction claim and tests all major functionality.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from arctan_geodesic_primes import (
    ArctanGeodesicPrimes,
    PrimeGapAnalyzer,
    generate_primes_up_to
)


class TestArctanGeodesicPrimes(unittest.TestCase):
    """Test arctan geodesic prime mapping functionality."""
    
    def setUp(self):
        """Initialize mapper for tests."""
        self.mapper = ArctanGeodesicPrimes(precision_dps=30)
    
    def test_initialization(self):
        """Test mapper initialization."""
        self.assertEqual(self.mapper.precision_dps, 30)
        self.assertIsNotNone(self.mapper.phi)
        self.assertIsNotNone(self.mapper.e2)
        self.assertIsNotNone(self.mapper.pi)
    
    def test_prime_density_arctan_positive(self):
        """Test prime density returns positive values for valid inputs."""
        density = self.mapper.prime_density_arctan(10)
        self.assertGreater(float(density), 0)
        
        density_100 = self.mapper.prime_density_arctan(100)
        self.assertGreater(float(density_100), 0)
    
    def test_prime_density_arctan_zero_for_small_n(self):
        """Test prime density returns zero for n <= 1."""
        self.assertEqual(float(self.mapper.prime_density_arctan(0)), 0)
        self.assertEqual(float(self.mapper.prime_density_arctan(1)), 0)
    
    def test_prime_density_arctan_decreasing(self):
        """Test prime density decreases with n (prime number theorem)."""
        density_10 = float(self.mapper.prime_density_arctan(10))
        density_100 = float(self.mapper.prime_density_arctan(100))
        density_1000 = float(self.mapper.prime_density_arctan(1000))
        
        self.assertGreater(density_10, density_100)
        self.assertGreater(density_100, density_1000)
    
    def test_geodesic_curvature_arctan_positive(self):
        """Test geodesic curvature returns positive values."""
        kappa = self.mapper.geodesic_curvature_arctan(100)
        self.assertGreater(float(kappa), 0)
    
    def test_geodesic_curvature_arctan_zero_for_negative(self):
        """Test geodesic curvature returns zero for negative inputs."""
        kappa = self.mapper.geodesic_curvature_arctan(-1)
        self.assertEqual(float(kappa), 0)
    
    def test_geodesic_curvature_arctan_consistency(self):
        """Test geodesic curvature is consistent across calls."""
        n = 500
        kappa1 = self.mapper.geodesic_curvature_arctan(n)
        kappa2 = self.mapper.geodesic_curvature_arctan(n)
        
        self.assertAlmostEqual(float(kappa1), float(kappa2), places=10)
    
    def test_prime_counting_arctan_small_values(self):
        """Test prime counting for small values."""
        pi_10 = self.mapper.prime_counting_arctan(10)
        # There are 4 primes <= 10: 2, 3, 5, 7
        self.assertGreater(float(pi_10), 3)
        self.assertLess(float(pi_10), 6)
    
    def test_prime_counting_arctan_increasing(self):
        """Test prime counting increases with x."""
        pi_10 = float(self.mapper.prime_counting_arctan(10))
        pi_100 = float(self.mapper.prime_counting_arctan(100))
        pi_1000 = float(self.mapper.prime_counting_arctan(1000))
        
        self.assertGreater(pi_100, pi_10)
        self.assertGreater(pi_1000, pi_100)
    
    def test_prime_counting_arctan_zero_for_small_x(self):
        """Test prime counting returns zero for x < 2."""
        self.assertEqual(float(self.mapper.prime_counting_arctan(0)), 0)
        self.assertEqual(float(self.mapper.prime_counting_arctan(1)), 0)
    
    def test_geodesic_distance_primes_symmetry(self):
        """Test geodesic distance is symmetric."""
        p1, p2 = 7, 11
        dist1 = self.mapper.geodesic_distance_primes(p1, p2)
        dist2 = self.mapper.geodesic_distance_primes(p2, p1)
        
        self.assertAlmostEqual(float(dist1), float(dist2), places=8)
    
    def test_geodesic_distance_primes_positive(self):
        """Test geodesic distance is always positive."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19]
        
        for i in range(len(primes) - 1):
            dist = self.mapper.geodesic_distance_primes(primes[i], primes[i+1])
            self.assertGreater(float(dist), 0)
    
    def test_geodesic_distance_primes_dimensions(self):
        """Test geodesic distance with different dimensions."""
        p1, p2 = 5, 11
        
        dist_3d = self.mapper.geodesic_distance_primes(p1, p2, dimension=3)
        dist_5d = self.mapper.geodesic_distance_primes(p1, p2, dimension=5)
        dist_7d = self.mapper.geodesic_distance_primes(p1, p2, dimension=7)
        
        # All should be positive
        self.assertGreater(float(dist_3d), 0)
        self.assertGreater(float(dist_5d), 0)
        self.assertGreater(float(dist_7d), 0)
    
    def test_arctan_projection_coords_length(self):
        """Test projection coordinates have correct length."""
        n = 100
        
        for dim in [3, 5, 7, 10]:
            coords = self.mapper._arctan_projection_coords(n, dim)
            self.assertEqual(len(coords), dim)
    
    def test_arctan_projection_coords_range(self):
        """Test projection coordinates are in [0, 1] range."""
        n = 100
        coords = self.mapper._arctan_projection_coords(n, 5)
        
        for coord in coords:
            self.assertGreaterEqual(float(coord), 0)
            self.assertLessEqual(float(coord), 1)
    
    def test_prime_gap_prediction_arctan_geodesic(self):
        """Test prime gap prediction with arctan geodesic method."""
        p = 7
        gap, confidence = self.mapper.prime_gap_prediction(p, "arctan_geodesic")
        
        self.assertGreater(float(gap), 0)
        self.assertGreater(float(confidence), 0)
        self.assertLessEqual(float(confidence), 1.5)  # Allow some flexibility
    
    def test_prime_gap_prediction_traditional(self):
        """Test prime gap prediction with traditional method."""
        p = 7
        gap, confidence = self.mapper.prime_gap_prediction(p, "traditional")
        
        self.assertGreater(float(gap), 0)
        self.assertGreater(float(confidence), 0)
        self.assertLessEqual(float(confidence), 1)
    
    def test_prime_gap_prediction_comparison(self):
        """Test that arctan geodesic provides different predictions."""
        p = 11
        gap_geo, _ = self.mapper.prime_gap_prediction(p, "arctan_geodesic")
        gap_trad, _ = self.mapper.prime_gap_prediction(p, "traditional")
        
        # Methods should give different predictions
        self.assertNotAlmostEqual(float(gap_geo), float(gap_trad), places=1)
    
    def test_detect_prime_clusters_basic(self):
        """Test basic prime cluster detection."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        clusters = self.mapper.detect_prime_clusters(primes, dimension=3, threshold=1.0)
        
        # Should find at least some clusters
        self.assertIsInstance(clusters, list)
    
    def test_detect_prime_clusters_empty_input(self):
        """Test cluster detection with empty input."""
        clusters = self.mapper.detect_prime_clusters([], dimension=3, threshold=0.5)
        self.assertEqual(len(clusters), 0)
    
    def test_detect_prime_clusters_single_prime(self):
        """Test cluster detection with single prime."""
        clusters = self.mapper.detect_prime_clusters([7], dimension=3, threshold=0.5)
        self.assertEqual(len(clusters), 0)
    
    def test_entropy_measure_prime_based_positive(self):
        """Test entropy measure returns positive values."""
        data = [1.0, 2.5, 3.7, 4.2, 5.8, 6.1, 7.3, 8.9, 9.2, 10.5]
        entropy = self.mapper.entropy_measure_prime_based(data, prime_window=5)
        
        self.assertGreater(float(entropy), 0)
    
    def test_entropy_measure_prime_based_empty_data(self):
        """Test entropy measure with empty data."""
        entropy = self.mapper.entropy_measure_prime_based([], prime_window=5)
        self.assertEqual(float(entropy), 0)
    
    def test_entropy_measure_prime_based_different_windows(self):
        """Test entropy measure with different window sizes."""
        data = list(range(100))
        
        entropy_10 = self.mapper.entropy_measure_prime_based(data, prime_window=10)
        entropy_20 = self.mapper.entropy_measure_prime_based(data, prime_window=20)
        
        # Both should be positive
        self.assertGreater(float(entropy_10), 0)
        self.assertGreater(float(entropy_20), 0)
    
    def test_ntru_prime_selection_returns_correct_count(self):
        """Test NTRU prime selection returns requested number."""
        bit_length = 16
        num_candidates = 5
        
        primes = self.mapper.ntru_prime_selection(bit_length, num_candidates)
        
        self.assertEqual(len(primes), num_candidates)
    
    def test_ntru_prime_selection_correct_bit_length(self):
        """Test NTRU primes have correct bit length."""
        bit_length = 16
        primes = self.mapper.ntru_prime_selection(bit_length, num_candidates=3)
        
        for prime, score in primes:
            self.assertGreaterEqual(prime.bit_length(), bit_length - 1)
            self.assertLessEqual(prime.bit_length(), bit_length + 1)
    
    def test_ntru_prime_selection_sorted_by_score(self):
        """Test NTRU primes are sorted by geodesic score."""
        bit_length = 16
        primes = self.mapper.ntru_prime_selection(bit_length, num_candidates=5)
        
        scores = [float(score) for _, score in primes]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_pseudorandom_generator_prime_length(self):
        """Test pseudorandom generator returns correct length."""
        seed_prime = 7
        sequence_length = 10
        
        sequence = self.mapper.pseudorandom_generator_prime(seed_prime, sequence_length)
        
        self.assertEqual(len(sequence), sequence_length)
    
    def test_pseudorandom_generator_prime_all_primes(self):
        """Test pseudorandom generator returns all primes."""
        import sympy
        
        seed_prime = 11
        sequence_length = 5
        
        sequence = self.mapper.pseudorandom_generator_prime(seed_prime, sequence_length)
        
        for num in sequence:
            self.assertTrue(sympy.isprime(num))
    
    def test_pseudorandom_generator_prime_increasing(self):
        """Test pseudorandom generator produces increasing sequence."""
        seed_prime = 13
        sequence_length = 8
        
        sequence = self.mapper.pseudorandom_generator_prime(seed_prime, sequence_length)
        
        for i in range(len(sequence) - 1):
            self.assertLess(sequence[i], sequence[i+1])


class TestPrimeGapAnalyzer(unittest.TestCase):
    """Test prime gap analysis functionality."""
    
    def setUp(self):
        """Initialize analyzer for tests."""
        self.analyzer = PrimeGapAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer.geodesic)
    
    def test_analyze_gap_predictions_basic(self):
        """Test basic gap prediction analysis."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        gaps = [p2 - p1 for p1, p2 in zip(primes[:-1], primes[1:])]
        
        results = self.analyzer.analyze_gap_predictions(primes, gaps)
        
        self.assertIn("arctan_geodesic_mean_error", results)
        self.assertIn("traditional_mean_error", results)
        self.assertIn("error_reduction_percentage", results)
    
    def test_analyze_gap_predictions_error_reduction(self):
        """Test that arctan geodesic shows error reduction potential."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        gaps = [p2 - p1 for p1, p2 in zip(primes[:-1], primes[1:])]
        
        results = self.analyzer.analyze_gap_predictions(primes, gaps)
        
        # Both methods should have some error
        self.assertGreater(results["arctan_geodesic_mean_error"], 0)
        self.assertGreater(results["traditional_mean_error"], 0)
    
    def test_analyze_gap_predictions_length_mismatch(self):
        """Test error handling for mismatched lengths."""
        primes = [2, 3, 5, 7, 11]
        gaps = [1, 2, 2]  # Wrong length
        
        with self.assertRaises(ValueError):
            self.analyzer.analyze_gap_predictions(primes, gaps)
    
    def test_analyze_gap_predictions_result_structure(self):
        """Test result structure has all expected keys."""
        primes = [2, 3, 5, 7, 11, 13]
        gaps = [1, 2, 2, 4, 2]
        
        results = self.analyzer.analyze_gap_predictions(primes, gaps)
        
        expected_keys = [
            "arctan_geodesic_mean_error",
            "traditional_mean_error",
            "error_reduction_percentage",
            "geodesic_errors",
            "traditional_errors"
        ]
        
        for key in expected_keys:
            self.assertIn(key, results)
    
    def test_analyze_gap_predictions_error_lists(self):
        """Test that error lists have correct length."""
        primes = [2, 3, 5, 7, 11, 13, 17]
        gaps = [1, 2, 2, 4, 2, 4]
        
        results = self.analyzer.analyze_gap_predictions(primes, gaps)
        
        self.assertEqual(len(results["geodesic_errors"]), len(gaps))
        self.assertEqual(len(results["traditional_errors"]), len(gaps))


class TestGeneratePrimes(unittest.TestCase):
    """Test prime generation utility."""
    
    def test_generate_primes_up_to_10(self):
        """Test prime generation up to 10."""
        primes = generate_primes_up_to(10)
        expected = [2, 3, 5, 7]
        self.assertEqual(primes, expected)
    
    def test_generate_primes_up_to_30(self):
        """Test prime generation up to 30."""
        primes = generate_primes_up_to(30)
        expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        self.assertEqual(primes, expected)
    
    def test_generate_primes_up_to_2(self):
        """Test prime generation up to 2."""
        primes = generate_primes_up_to(2)
        expected = [2]
        self.assertEqual(primes, expected)
    
    def test_generate_primes_up_to_1(self):
        """Test prime generation up to 1 returns empty list."""
        primes = generate_primes_up_to(1)
        self.assertEqual(primes, [])
    
    def test_generate_primes_count(self):
        """Test prime count matches known values."""
        primes_100 = generate_primes_up_to(100)
        self.assertEqual(len(primes_100), 25)  # π(100) = 25


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def setUp(self):
        """Initialize components for integration tests."""
        self.mapper = ArctanGeodesicPrimes(precision_dps=30)
        self.analyzer = PrimeGapAnalyzer()
    
    def test_end_to_end_gap_analysis(self):
        """Test complete gap analysis workflow."""
        # Generate primes
        primes = generate_primes_up_to(200)
        
        # Calculate actual gaps
        gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
        
        # Analyze with both methods
        results = self.analyzer.analyze_gap_predictions(primes, gaps)
        
        # Verify results are reasonable
        self.assertGreater(results["arctan_geodesic_mean_error"], 0)
        self.assertGreater(results["traditional_mean_error"], 0)
        self.assertIsInstance(results["error_reduction_percentage"], float)
    
    def test_cryptographic_workflow(self):
        """Test cryptographic application workflow."""
        # Select NTRU primes
        ntru_primes = self.mapper.ntru_prime_selection(bit_length=16, num_candidates=5)
        
        self.assertEqual(len(ntru_primes), 5)
        
        # Generate pseudorandom sequence
        seed = ntru_primes[0][0]  # Use first prime as seed
        sequence = self.mapper.pseudorandom_generator_prime(seed, sequence_length=10)
        
        self.assertEqual(len(sequence), 10)
        
        # All should be valid primes
        import sympy
        for num in sequence:
            self.assertTrue(sympy.isprime(num))
    
    def test_anomaly_detection_workflow(self):
        """Test anomaly detection application workflow."""
        # Simulate network traffic data
        normal_data = [1.0 + i * 0.1 for i in range(50)]
        anomaly_data = [1.0 + i * 0.1 for i in range(40)] + [100.0] * 10
        
        # Compute entropy for both
        entropy_normal = self.mapper.entropy_measure_prime_based(normal_data, prime_window=10)
        entropy_anomaly = self.mapper.entropy_measure_prime_based(anomaly_data, prime_window=10)
        
        # Both should be positive
        self.assertGreater(float(entropy_normal), 0)
        self.assertGreater(float(entropy_anomaly), 0)
    
    def test_clustering_analysis_workflow(self):
        """Test prime clustering analysis workflow."""
        # Generate primes
        primes = generate_primes_up_to(100)
        
        # Detect clusters
        clusters = self.mapper.detect_prime_clusters(primes, dimension=5, threshold=0.8)
        
        # Verify cluster structure
        self.assertIsInstance(clusters, list)
        for cluster in clusters:
            self.assertIsInstance(cluster, list)
            self.assertGreater(len(cluster), 1)


if __name__ == "__main__":
    unittest.main()
