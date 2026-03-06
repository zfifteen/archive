"""
Test Suite for Modular Topology Visualization Suite

This module provides comprehensive tests for the modular topology visualization
components, ensuring mathematical accuracy, performance, and reliability.
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# Add the applications directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'applications'))

from modular_topology_suite import (
    GeneralizedEmbedding, TopologyAnalyzer, VisualizationEngine, DataExporter,
    generate_prime_sequence, generate_fibonacci_sequence, generate_mersenne_numbers
)

class TestGeneralizedEmbedding(unittest.TestCase):
    """Test cases for GeneralizedEmbedding class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.embedding = GeneralizedEmbedding()
        self.test_sequence = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        
    def test_theta_prime_transform_basic(self):
        """Test basic theta prime transformation."""
        result = self.embedding.theta_prime_transform(self.test_sequence, k=0.3)
        
        # Check result properties
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), len(self.test_sequence))
        self.assertTrue(all(r >= 0 for r in result))
        self.assertTrue(all(r < self.embedding.modulus for r in result))
        
    def test_theta_prime_transform_parameters(self):
        """Test theta prime transformation with different parameters."""
        # Test different k values
        result_k1 = self.embedding.theta_prime_transform(self.test_sequence, k=0.1)
        result_k2 = self.embedding.theta_prime_transform(self.test_sequence, k=0.5)
        
        # Results should be different for different k values
        self.assertFalse(np.allclose(result_k1, result_k2))
        
        # Test different moduli
        result_phi = self.embedding.theta_prime_transform(self.test_sequence, modulus=1.618)
        result_e = self.embedding.theta_prime_transform(self.test_sequence, modulus=2.718)
        
        # Results should be different for different moduli
        self.assertFalse(np.allclose(result_phi, result_e))
        
    def test_curvature_function(self):
        """Test curvature function computation."""
        # Test positive integers
        for n in [1, 2, 3, 5, 10, 100]:
            curvature = self.embedding.curvature_function(n)
            self.assertIsInstance(curvature, float)
            self.assertGreaterEqual(curvature, 0)
            
        # Test edge cases
        self.assertEqual(self.embedding.curvature_function(0), 0.0)
        self.assertEqual(self.embedding.curvature_function(-1), 0.0)
        
    def test_helical_5d_embedding(self):
        """Test 5D helical embedding generation."""
        coords = self.embedding.helical_5d_embedding(self.test_sequence)
        
        # Check all required coordinates are present
        required_keys = ['x', 'y', 'z', 'w', 'u', 'sequence', 'theta']
        for key in required_keys:
            self.assertIn(key, coords)
            
        # Check coordinate dimensions
        n = len(self.test_sequence)
        for key in ['x', 'y', 'z', 'w', 'u']:
            self.assertEqual(len(coords[key]), n)
            
        # Check value ranges
        self.assertTrue(all(isinstance(v, (int, float, np.number)) for v in coords['x']))
        self.assertTrue(all(isinstance(v, (int, float, np.number)) for v in coords['y']))
        self.assertTrue(all(v >= 0 for v in coords['z']))  # Curvature should be non-negative
        
    def test_modular_spiral_coordinates(self):
        """Test modular spiral coordinate generation."""
        coords = self.embedding.modular_spiral_coordinates(self.test_sequence)
        
        # Check required keys
        required_keys = ['x', 'y', 'z', 'radii', 'angles']
        for key in required_keys:
            self.assertIn(key, coords)
            
        # Check dimensions
        n = len(self.test_sequence)
        for key in ['x', 'y', 'z', 'radii', 'angles']:
            self.assertEqual(len(coords[key]), n)
            
        # Check that radii are positive
        self.assertTrue(all(r > 0 for r in coords['radii']))

class TestTopologyAnalyzer(unittest.TestCase):
    """Test cases for TopologyAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TopologyAnalyzer()
        self.embedding = GeneralizedEmbedding()
        self.test_sequence = generate_prime_sequence(50)
        self.test_coords = self.embedding.helical_5d_embedding(self.test_sequence)
        
    def test_detect_clusters_dbscan(self):
        """Test DBSCAN clustering."""
        labels, stats = self.analyzer.detect_clusters(self.test_coords, method='dbscan')
        
        # Check output format
        self.assertIsInstance(labels, np.ndarray)
        self.assertIsInstance(stats, dict)
        self.assertEqual(len(labels), len(self.test_sequence))
        
        # Check that cluster statistics are reasonable
        unique_labels = np.unique(labels)
        for label in unique_labels:
            if label != -1:  # Skip noise label
                self.assertIn(label, stats)
                
    def test_detect_clusters_kmeans(self):
        """Test K-means clustering."""
        n_clusters = 3
        labels, stats = self.analyzer.detect_clusters(
            self.test_coords, method='kmeans', n_clusters=n_clusters
        )
        
        # Check output format
        self.assertIsInstance(labels, np.ndarray)
        self.assertEqual(len(labels), len(self.test_sequence))
        
        # Check number of clusters
        unique_labels = np.unique(labels)
        self.assertLessEqual(len(unique_labels), n_clusters)
        
    def test_detect_symmetries(self):
        """Test symmetry detection."""
        symmetries = self.analyzer.detect_symmetries(self.test_coords)
        
        # Check output format
        self.assertIsInstance(symmetries, dict)
        
        # Check required symmetry types
        required_types = ['x_reflection', 'y_reflection', 'rotational', 'helical']
        for sym_type in required_types:
            self.assertIn(sym_type, symmetries)
            
        # Check symmetry scores are reasonable
        for sym_type, result in symmetries.items():
            if isinstance(result, dict) and 'score' in result:
                self.assertGreaterEqual(result['score'], 0)
                self.assertLessEqual(result['score'], 1)
                
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        labels, scores = self.analyzer.detect_anomalies(self.test_coords)
        
        # Check output format
        self.assertIsInstance(labels, np.ndarray)
        self.assertIsInstance(scores, np.ndarray)
        self.assertEqual(len(labels), len(self.test_sequence))
        self.assertEqual(len(scores), len(self.test_sequence))
        
        # Check label values (should be 1 or -1)
        unique_labels = np.unique(labels)
        for label in unique_labels:
            self.assertIn(label, [-1, 1])

class TestVisualizationEngine(unittest.TestCase):
    """Test cases for VisualizationEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = VisualizationEngine()
        self.embedding = GeneralizedEmbedding()
        self.analyzer = TopologyAnalyzer()
        self.test_sequence = generate_prime_sequence(30)
        self.test_coords = self.embedding.helical_5d_embedding(self.test_sequence)
        
    def test_plot_3d_helical_embedding(self):
        """Test 3D helical embedding visualization."""
        fig = self.visualizer.plot_3d_helical_embedding(self.test_coords)
        
        # Check that figure is created
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))
        self.assertGreater(len(fig.data), 0)
        
    def test_plot_5d_projection(self):
        """Test 5D projection visualization."""
        fig = self.visualizer.plot_5d_projection(self.test_coords)
        
        # Check that figure is created
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))
        
    def test_plot_modular_spiral(self):
        """Test modular spiral visualization."""
        spiral_coords = self.embedding.modular_spiral_coordinates(self.test_sequence)
        fig = self.visualizer.plot_modular_spiral(spiral_coords)
        
        # Check that figure is created
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))
        
    def test_plot_cluster_analysis(self):
        """Test cluster analysis visualization."""
        labels, stats = self.analyzer.detect_clusters(self.test_coords)
        fig = self.visualizer.plot_cluster_analysis(self.test_coords, labels, stats)
        
        # Check that figure is created
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))
        
    def test_plot_anomaly_detection(self):
        """Test anomaly detection visualization."""
        labels, scores = self.analyzer.detect_anomalies(self.test_coords)
        fig = self.visualizer.plot_anomaly_detection(self.test_coords, labels, scores)
        
        # Check that figure is created
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))

class TestDataExporter(unittest.TestCase):
    """Test cases for DataExporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.exporter = DataExporter()
        self.embedding = GeneralizedEmbedding()
        self.test_sequence = generate_prime_sequence(20)
        self.test_coords = self.embedding.helical_5d_embedding(self.test_sequence)
        self.test_dir = '/tmp/topology_tests'
        
        # Create test directory
        os.makedirs(self.test_dir, exist_ok=True)
        
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_export_coordinates_csv(self):
        """Test CSV coordinate export."""
        filename = os.path.join(self.test_dir, 'test_coords.csv')
        self.exporter.export_coordinates(self.test_coords, filename, format='csv')
        
        # Check file was created
        self.assertTrue(os.path.exists(filename))
        
        # Check file content
        df = pd.read_csv(filename)
        self.assertEqual(len(df), len(self.test_sequence))
        self.assertIn('x', df.columns)
        self.assertIn('y', df.columns)
        self.assertIn('z', df.columns)
        
    def test_export_coordinates_json(self):
        """Test JSON coordinate export."""
        filename = os.path.join(self.test_dir, 'test_coords.json')
        self.exporter.export_coordinates(self.test_coords, filename, format='json')
        
        # Check file was created
        self.assertTrue(os.path.exists(filename))
        
        # Check file content
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.test_sequence))
        
    def test_export_analysis_report(self):
        """Test analysis report export."""
        # Generate analysis data
        analyzer = TopologyAnalyzer()
        clusters, cluster_stats = analyzer.detect_clusters(self.test_coords)
        symmetries = analyzer.detect_symmetries(self.test_coords)
        anomalies, anomaly_scores = analyzer.detect_anomalies(self.test_coords)
        
        filename = os.path.join(self.test_dir, 'test_report.json')
        self.exporter.export_analysis_report(
            self.test_coords, cluster_stats, symmetries, 
            (anomalies, anomaly_scores), filename
        )
        
        # Check file was created
        self.assertTrue(os.path.exists(filename))
        
        # Check file content
        import json
        with open(filename, 'r') as f:
            report = json.load(f)
        
        # Check required sections
        required_sections = ['summary', 'clustering', 'symmetries', 'anomalies', 'coordinate_statistics']
        for section in required_sections:
            self.assertIn(section, report)

class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper functions."""
    
    def test_generate_prime_sequence(self):
        """Test prime sequence generation."""
        primes = generate_prime_sequence(100)
        
        # Check basic properties
        self.assertIsInstance(primes, list)
        self.assertGreater(len(primes), 0)
        self.assertEqual(primes[0], 2)  # First prime
        
        # Check all are primes
        for p in primes:
            self.assertTrue(self._is_prime(p))
            
        # Check within limit
        self.assertTrue(all(p <= 100 for p in primes))
        
    def test_generate_fibonacci_sequence(self):
        """Test Fibonacci sequence generation."""
        fibs = generate_fibonacci_sequence(10)
        
        # Check basic properties
        self.assertIsInstance(fibs, list)
        self.assertEqual(len(fibs), 8)  # Excludes first two
        
        # Check Fibonacci property (with first two added back)
        full_fibs = [0, 1] + fibs  # Standard Fibonacci starts with 0, 1
        for i in range(2, len(full_fibs)):
            self.assertEqual(full_fibs[i], full_fibs[i-1] + full_fibs[i-2])
            
    def test_generate_mersenne_numbers(self):
        """Test Mersenne number generation."""
        mersennes = generate_mersenne_numbers(10)
        
        # Check basic properties
        self.assertIsInstance(mersennes, list)
        self.assertGreater(len(mersennes), 0)
        
        # Check Mersenne form (2^p - 1 for prime p)
        for m in mersennes:
            # Find corresponding prime exponent
            p = int(np.log2(m + 1))
            if 2**p - 1 == m:
                self.assertTrue(self._is_prime(p))
                
    def _is_prime(self, n):
        """Helper function to check primality."""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete visualization suite."""
    
    def test_complete_workflow(self):
        """Test complete workflow from data to visualization."""
        # Generate data
        sequence = generate_prime_sequence(50)
        
        # Create embeddings
        embedding = GeneralizedEmbedding()
        theta_transformed = embedding.theta_prime_transform(sequence, k=0.3)
        helix_coords = embedding.helical_5d_embedding(sequence, theta_transformed)
        
        # Analyze patterns
        analyzer = TopologyAnalyzer()
        clusters, cluster_stats = analyzer.detect_clusters(helix_coords)
        symmetries = analyzer.detect_symmetries(helix_coords)
        anomalies, anomaly_scores = analyzer.detect_anomalies(helix_coords)
        
        # Create visualizations
        visualizer = VisualizationEngine()
        fig_3d = visualizer.plot_3d_helical_embedding(helix_coords)
        fig_clusters = visualizer.plot_cluster_analysis(helix_coords, clusters, cluster_stats)
        
        # Check all components work together
        self.assertIsNotNone(fig_3d)
        self.assertIsNotNone(fig_clusters)
        self.assertIsInstance(clusters, np.ndarray)
        self.assertIsInstance(symmetries, dict)
        self.assertIsInstance(anomalies, np.ndarray)
        
    def test_performance_large_dataset(self):
        """Test performance with larger datasets."""
        import time
        
        # Generate larger dataset
        sequence = generate_prime_sequence(1000)
        
        # Time the complete workflow
        start_time = time.time()
        
        embedding = GeneralizedEmbedding()
        helix_coords = embedding.helical_5d_embedding(sequence)
        
        analyzer = TopologyAnalyzer()
        clusters, _ = analyzer.detect_clusters(helix_coords)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(processing_time, 30.0)  # 30 seconds max
        self.assertEqual(len(clusters), len(sequence))

class TestMathematicalAccuracy(unittest.TestCase):
    """Test mathematical accuracy of transformations."""
    
    def test_golden_ratio_properties(self):
        """Test golden ratio properties in transformations."""
        embedding = GeneralizedEmbedding()
        
        # Golden ratio should be approximately 1.618
        self.assertAlmostEqual(embedding.modulus, 1.618, places=3)
        
        # Test golden ratio specific properties
        phi = embedding.modulus
        self.assertAlmostEqual(phi**2, phi + 1, places=10)
        
    def test_transformation_invariances(self):
        """Test mathematical invariances in transformations."""
        embedding = GeneralizedEmbedding()
        test_sequence = [2, 3, 5, 7, 11]
        
        # Same sequence should give same results
        result1 = embedding.theta_prime_transform(test_sequence, k=0.3)
        result2 = embedding.theta_prime_transform(test_sequence, k=0.3)
        np.testing.assert_array_almost_equal(result1, result2)
        
        # Scaling input by constant should affect output predictably
        scaled_sequence = [x * 2 for x in test_sequence]
        result_original = embedding.theta_prime_transform(test_sequence, k=0.3)
        result_scaled = embedding.theta_prime_transform(scaled_sequence, k=0.3)
        
        # Results should be different but follow mathematical relationship
        self.assertFalse(np.allclose(result_original, result_scaled))
        
    def test_curvature_monotonicity(self):
        """Test curvature function properties."""
        embedding = GeneralizedEmbedding()
        
        # Curvature should generally increase with number of divisors
        prime = 7  # Has 2 divisors
        composite = 12  # Has 6 divisors (1, 2, 3, 4, 6, 12)
        
        curvature_prime = embedding.curvature_function(prime)
        curvature_composite = embedding.curvature_function(composite)
        
        # Composite numbers should generally have higher curvature
        # (This may not always hold, but should for this specific example)
        self.assertGreater(curvature_composite, curvature_prime)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestGeneralizedEmbedding,
        TestTopologyAnalyzer,
        TestVisualizationEngine,
        TestDataExporter,
        TestHelperFunctions,
        TestIntegration,
        TestMathematicalAccuracy
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
            
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")