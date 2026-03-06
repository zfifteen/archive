"""
Test suite for Universal Invariant Scoring Engine API

Tests the scoring engine, API endpoints, and client library functionality.
"""

import unittest
import tempfile
import threading
import time
import sys
import os
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.api.scoring_engine import create_scoring_engine, UniversalScoringEngine
from src.api.server import create_app
from src.api.client import ZScoreAPIClient


class TestScoringEngine(unittest.TestCase):
    """Test the core scoring engine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = create_scoring_engine()
    
    def test_engine_creation(self):
        """Test scoring engine can be created."""
        self.assertIsInstance(self.engine, UniversalScoringEngine)
        self.assertIn('numerical', self.engine.normalizers)
        self.assertIn('biological', self.engine.normalizers)
        self.assertIn('network', self.engine.normalizers)
    
    def test_numerical_scoring(self):
        """Test scoring of numerical sequences."""
        # Test simple numerical sequence
        data = [1, 2, 3, 4, 5]
        result = self.engine.score_sequence(data, 'numerical')
        
        self.assertIn('z_invariant_score', result)
        self.assertIn('metadata', result)
        self.assertIn('z_scores', result)
        self.assertIn('density_metrics', result)
        self.assertIn('anomaly_scores', result)
        
        # Check metadata
        metadata = result['metadata']
        self.assertEqual(metadata['type'], 'numerical')
        self.assertEqual(metadata['length'], 5)
        self.assertEqual(metadata['mean'], 3.0)
        
        # Check score is a number
        self.assertIsInstance(result['z_invariant_score'], (int, float))
    
    def test_biological_scoring(self):
        """Test scoring of biological sequences."""
        # Test DNA sequence
        dna = "ATGCATGC"
        result = self.engine.score_sequence(dna, 'biological')
        
        self.assertIn('z_invariant_score', result)
        metadata = result['metadata']
        self.assertEqual(metadata['type'], 'biological')
        self.assertEqual(metadata['sequence_type'], 'DNA')
        self.assertEqual(metadata['length'], 8)
        
        # Test RNA sequence
        rna = "AUGCAUGC"
        result = self.engine.score_sequence(rna, 'biological')
        metadata = result['metadata']
        self.assertEqual(metadata['sequence_type'], 'RNA')
        
        # Test protein sequence
        protein = "MVSKGEELFTGVVP"
        result = self.engine.score_sequence(protein, 'biological')
        metadata = result['metadata']
        self.assertEqual(metadata['sequence_type'], 'protein')
    
    def test_network_scoring(self):
        """Test scoring of network data."""
        # Simple 3x3 adjacency matrix
        matrix = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
        result = self.engine.score_sequence(matrix, 'network')
        
        self.assertIn('z_invariant_score', result)
        metadata = result['metadata']
        self.assertEqual(metadata['type'], 'network')
        self.assertEqual(metadata['n_nodes'], 3)
        self.assertEqual(metadata['n_edges'], 3)
    
    def test_auto_detection(self):
        """Test automatic data type detection."""
        # Numerical data
        result = self.engine.score_sequence([1, 2, 3], 'auto')
        self.assertEqual(result['metadata']['type'], 'numerical')
        
        # Biological data
        result = self.engine.score_sequence("ATGC", 'auto')
        self.assertEqual(result['metadata']['type'], 'biological')
        
        # Network data
        result = self.engine.score_sequence([[0, 1], [1, 0]], 'auto')
        self.assertEqual(result['metadata']['type'], 'network')
    
    def test_batch_scoring(self):
        """Test batch scoring functionality."""
        data_list = [
            [1, 2, 3],
            "ATGC",
            [[0, 1], [1, 0]]
        ]
        
        results = self.engine.batch_score(data_list)
        
        self.assertEqual(len(results), 3)
        for i, result in enumerate(results):
            self.assertEqual(result['batch_index'], i)
            self.assertIn('z_invariant_score', result)
    
    def test_empty_sequences(self):
        """Test handling of empty sequences."""
        result = self.engine.score_sequence([], 'numerical')
        self.assertEqual(result['z_invariant_score'], 0.0)
        self.assertEqual(result['sequence_length'], 0)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Invalid data type
        with self.assertRaises(ValueError):
            self.engine.score_sequence([1, 2, 3], 'invalid_type')


class TestAPIServer(unittest.TestCase):
    """Test the Flask API server."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test server."""
        cls.app = create_app({'TESTING': True})
        cls.client = cls.app.test_client()
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_score_endpoint(self):
        """Test single scoring endpoint."""
        payload = {
            'data': [1, 2, 3, 4, 5],
            'data_type': 'numerical'
        }
        
        response = self.client.post('/api/score', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('result', data)
        self.assertIn('z_invariant_score', data['result'])
    
    def test_batch_score_endpoint(self):
        """Test batch scoring endpoint."""
        payload = {
            'data_list': [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ],
            'data_types': ['numerical', 'numerical', 'numerical']
        }
        
        response = self.client.post('/api/batch_score', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['results']), 3)
    
    def test_analyze_endpoint(self):
        """Test comprehensive analysis endpoint."""
        payload = {
            'data': [1, 2, 3, 4, 5],
            'data_type': 'numerical',
            'detailed_metrics': True
        }
        
        response = self.client.post('/api/analyze', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('analysis', data)
        self.assertIn('summary', data['analysis'])
    
    def test_info_endpoint(self):
        """Test API info endpoint."""
        response = self.client.get('/api/info')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('service', data)
        self.assertIn('supported_data_types', data)
        self.assertIn('endpoints', data)
    
    def test_error_handling(self):
        """Test API error handling."""
        # Missing data field
        response = self.client.post('/api/score', json={})
        self.assertEqual(response.status_code, 400)
        
        # Invalid JSON
        response = self.client.post('/api/score', data='invalid json')
        self.assertEqual(response.status_code, 400)
        
        # 404 endpoint
        response = self.client.get('/api/nonexistent')
        self.assertEqual(response.status_code, 404)


class TestPythonClient(unittest.TestCase):
    """Test the Python client library."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client with mock server."""
        cls.app = create_app({'TESTING': True})
        cls.test_client = cls.app.test_client()
        
        # Start a test server in a separate thread
        cls.server_thread = None
        cls.server_port = 5555
        
    def setUp(self):
        """Set up client for each test."""
        # For testing, we'll use the test client directly
        # In a real scenario, you'd use a running server
        pass
    
    def test_client_initialization(self):
        """Test client can be initialized."""
        client = ZScoreAPIClient(f"http://localhost:{self.server_port}")
        self.assertEqual(client.base_url, f"http://localhost:{self.server_port}")
        self.assertEqual(client.timeout, 30)
    
    def test_convenience_methods(self):
        """Test convenience scoring methods."""
        # These tests would need a running server
        # For now, we'll test the method signatures
        client = ZScoreAPIClient()
        
        # Test that methods exist and have proper signatures
        self.assertTrue(hasattr(client, 'score_numerical'))
        self.assertTrue(hasattr(client, 'score_biological'))
        self.assertTrue(hasattr(client, 'score_network'))
        self.assertTrue(hasattr(client, 'detect_anomalies'))
        self.assertTrue(hasattr(client, 'benchmark_sequences'))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_end_to_end_numerical(self):
        """Test end-to-end scoring of numerical data."""
        engine = create_scoring_engine()
        
        # Test various numerical sequences
        test_cases = [
            [1, 2, 3, 4, 5],
            [10, 20, 30, 40, 50],
            [0.1, 0.2, 0.3, 0.4, 0.5],
            list(range(100))  # Larger sequence
        ]
        
        for data in test_cases:
            result = engine.score_sequence(data, 'numerical')
            
            # Validate result structure
            self.assertIn('z_invariant_score', result)
            self.assertIn('metadata', result)
            self.assertIsInstance(result['z_invariant_score'], (int, float))
            
            # Validate metadata
            metadata = result['metadata']
            self.assertEqual(metadata['type'], 'numerical')
            self.assertEqual(metadata['length'], len(data))
    
    def test_end_to_end_biological(self):
        """Test end-to-end scoring of biological sequences."""
        engine = create_scoring_engine()
        
        test_cases = [
            ("ATGCATGC", "DNA"),
            ("AUGCAUGC", "RNA"),
            ("MVSKGEELFTGVVP", "protein"),
            ("AAAAAAAAAA", "DNA"),  # Homogeneous sequence
            ("ATGCGTACGATCGTAGC", "DNA")  # Longer sequence
        ]
        
        for sequence, expected_type in test_cases:
            result = engine.score_sequence(sequence, 'biological')
            
            # Validate result
            self.assertIn('z_invariant_score', result)
            metadata = result['metadata']
            self.assertEqual(metadata['type'], 'biological')
            self.assertEqual(metadata['sequence_type'], expected_type)
    
    def test_cross_domain_comparison(self):
        """Test that scores are comparable across domains."""
        engine = create_scoring_engine()
        
        # Score sequences from different domains
        numerical_result = engine.score_sequence([1, 2, 3, 4, 5], 'numerical')
        biological_result = engine.score_sequence("ATGCATGC", 'biological')
        network_result = engine.score_sequence([[0, 1], [1, 0]], 'network')
        
        # All should have comparable score structures
        for result in [numerical_result, biological_result, network_result]:
            self.assertIn('z_invariant_score', result)
            self.assertIn('density_metrics', result)
            self.assertIn('anomaly_scores', result)
            
            # Scores should be numerical
            self.assertIsInstance(result['z_invariant_score'], (int, float))
            
            # Enhancement factor should be around 1.0 (baseline)
            enhancement = result['density_metrics']['enhancement_factor']
            self.assertGreaterEqual(enhancement, 0.5)
            self.assertLessEqual(enhancement, 2.0)
    
    def test_performance_batch_processing(self):
        """Test performance of batch processing."""
        engine = create_scoring_engine()
        
        # Create a batch of sequences
        batch_size = 50
        data_list = []
        
        for i in range(batch_size):
            if i % 3 == 0:
                data_list.append(list(range(i+1, i+6)))  # Numerical
            elif i % 3 == 1:
                data_list.append("ATGC" * (i % 5 + 1))   # Biological
            else:
                size = i % 3 + 2
                matrix = [[1 if j != k else 0 for k in range(size)] for j in range(size)]
                data_list.append(matrix)  # Network
        
        # Time the batch processing
        import time
        start_time = time.time()
        results = engine.batch_score(data_list)
        end_time = time.time()
        
        # Validate results
        self.assertEqual(len(results), batch_size)
        
        # Performance check (should complete within reasonable time)
        processing_time = end_time - start_time
        self.assertLess(processing_time, 30.0)  # Should complete within 30 seconds
        
        print(f"Batch processing of {batch_size} sequences took {processing_time:.2f} seconds")


if __name__ == '__main__':
    # Set up test environment
    os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run tests
    unittest.main(verbosity=2)