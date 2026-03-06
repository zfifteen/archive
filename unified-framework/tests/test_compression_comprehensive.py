"""
Comprehensive test suite for decompression correctness and performance benchmarks.

This module provides detailed testing for the fixed compression algorithm,
including integrity verification, benchmark comparisons, and performance profiling.
"""

import unittest
import numpy as np
import time
import sys
import os
import gzip
import bz2
import lzma
from typing import Dict, List, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from applications.prime_compression import (
    PrimeDrivenCompressor, 
    CompressionBenchmark,
    PrimeGeodesicTransform,
    HistogramClusterAnalyzer,
    ModularClusterAnalyzer,
    K_OPTIMAL, PHI
)


class TestDecompressionCorrectness(unittest.TestCase):
    """Test decompression correctness with comprehensive data integrity verification."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = PrimeDrivenCompressor(use_histogram_clustering=True)
        
    def test_empty_data_integrity(self):
        """Test compression/decompression of empty data."""
        empty_data = b''
        compressed, metrics = self.compressor.compress(empty_data)
        decompressed, integrity = self.compressor.decompress(compressed, metrics)
        
        self.assertEqual(decompressed, empty_data)
        self.assertTrue(integrity)
        self.assertEqual(len(decompressed), 0)
        
    def test_single_byte_integrity(self):
        """Test compression/decompression of single byte."""
        single_byte = b'A'
        compressed, metrics = self.compressor.compress(single_byte)
        decompressed, integrity = self.compressor.decompress(compressed, metrics)
        
        self.assertEqual(decompressed, single_byte)
        self.assertTrue(integrity)
        
    def test_repeated_bytes_integrity(self):
        """Test compression/decompression of repeated bytes."""
        repeated_data = b'A' * 100
        compressed, metrics = self.compressor.compress(repeated_data)
        decompressed, integrity = self.compressor.decompress(compressed, metrics)
        
        self.assertEqual(decompressed, repeated_data)
        self.assertTrue(integrity)
        self.assertEqual(len(decompressed), len(repeated_data))
        
    def test_random_data_integrity(self):
        """Test compression/decompression of random data."""
        np.random.seed(42)
        random_data = np.random.randint(0, 256, 500, dtype=np.uint8).tobytes()
        
        compressed, metrics = self.compressor.compress(random_data)
        decompressed, integrity = self.compressor.decompress(compressed, metrics)
        
        self.assertEqual(decompressed, random_data)
        self.assertTrue(integrity)
        self.assertEqual(len(decompressed), len(random_data))
        
    def test_binary_pattern_integrity(self):
        """Test compression/decompression of binary patterns."""
        test_patterns = [
            b'\x00' * 50 + b'\xFF' * 50,  # Binary pattern
            bytes(range(256)),            # Sequential bytes
            b'\x00\xFF' * 100,           # Alternating pattern
            b'Hello World!' * 20,        # Text pattern
        ]
        
        for i, pattern_data in enumerate(test_patterns):
            with self.subTest(pattern=i):
                compressed, metrics = self.compressor.compress(pattern_data)
                decompressed, integrity = self.compressor.decompress(compressed, metrics)
                
                self.assertEqual(decompressed, pattern_data, 
                               f"Pattern {i} integrity failed")
                self.assertTrue(integrity, f"Pattern {i} hash verification failed")
                
    def test_large_data_integrity(self):
        """Test compression/decompression of larger datasets."""
        large_data = b'Test data pattern for large file simulation. ' * 100
        
        compressed, metrics = self.compressor.compress(large_data)
        decompressed, integrity = self.compressor.decompress(compressed, metrics)
        
        self.assertEqual(decompressed, large_data)
        self.assertTrue(integrity)
        self.assertEqual(len(decompressed), len(large_data))
        
    def test_edge_case_data_integrity(self):
        """Test compression/decompression of edge case data."""
        edge_cases = [
            b'\x00',                    # Single null byte
            b'\xFF',                    # Single max byte
            b'\x00\xFF',               # Min-max pair
            b'\x80' * 10,              # Mid-range repeated
            b''.join(bytes([i]) for i in range(10, 20)),  # Small sequence
        ]
        
        for i, edge_data in enumerate(edge_cases):
            with self.subTest(edge_case=i):
                compressed, metrics = self.compressor.compress(edge_data)
                decompressed, integrity = self.compressor.decompress(compressed, metrics)
                
                self.assertEqual(decompressed, edge_data)
                self.assertTrue(integrity)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarks against standard compression algorithms."""
    
    def setUp(self):
        """Set up benchmark fixtures."""
        self.benchmark = CompressionBenchmark()
        self.prime_compressor = PrimeDrivenCompressor(use_histogram_clustering=True)
        
    def test_prime_generation_performance(self):
        """Test performance improvement in prime generation."""
        from sympy import isprime
        
        # Test sieve vs sympy performance
        n = 10000
        
        # Sympy method (old)
        start_time = time.time()
        sympy_primes = [isprime(i) for i in range(2, n + 2)]
        sympy_time = time.time() - start_time
        
        # Sieve method (new)
        start_time = time.time()
        sieve_primes = self.prime_compressor._generate_prime_mask_efficient(n)
        sieve_time = time.time() - start_time
        
        # Verify correctness
        self.assertEqual(len(sympy_primes), len(sieve_primes))
        self.assertTrue(np.array_equal(sympy_primes, sieve_primes))
        
        # Verify performance improvement
        speedup = sympy_time / sieve_time
        self.assertGreater(speedup, 5.0, f"Sieve should be >5x faster, got {speedup:.1f}x")
        
        print(f"Prime generation speedup: {speedup:.1f}x ({sympy_time:.3f}s vs {sieve_time:.3f}s)")
        
    def test_clustering_performance_comparison(self):
        """Test performance comparison between histogram and GMM clustering."""
        np.random.seed(42)
        theta_values = np.random.normal(1.0, 0.3, 1000)
        
        # Histogram clustering
        start_time = time.time()
        hist_analyzer = HistogramClusterAnalyzer(5)
        hist_results = hist_analyzer.fit_clusters(theta_values)
        hist_time = time.time() - start_time
        
        # GMM clustering
        start_time = time.time()
        gmm_analyzer = ModularClusterAnalyzer(5)
        gmm_results = gmm_analyzer.fit_clusters(theta_values)
        gmm_time = time.time() - start_time
        
        # Verify both methods work
        self.assertIn('labels', hist_results)
        self.assertIn('labels', gmm_results)
        self.assertEqual(len(hist_results['labels']), len(theta_values))
        self.assertEqual(len(gmm_results['labels']), len(theta_values))
        
        # Verify performance improvement
        speedup = gmm_time / hist_time
        self.assertGreater(speedup, 2.0, f"Histogram should be >2x faster, got {speedup:.1f}x")
        
        print(f"Clustering speedup: {speedup:.1f}x ({gmm_time:.3f}s vs {hist_time:.3f}s)")
        
    def test_compression_algorithm_benchmarks(self):
        """Benchmark prime-driven compression against standard algorithms."""
        test_cases = [
            ('sparse', 1000),
            ('random', 1000), 
            ('repetitive', 1000),
            ('mixed', 1000)
        ]
        
        results = {}
        
        for data_type, size in test_cases:
            test_data = self.benchmark.generate_test_data(data_type, size)
            
            case_results = {}
            algorithms = ['prime_driven', 'gzip', 'bzip2', 'lzma']
            
            for algorithm in algorithms:
                result = self.benchmark.benchmark_algorithm(algorithm, test_data)
                case_results[algorithm] = result
                
            results[f"{data_type}_{size}"] = case_results
            
        # Verify all algorithms completed successfully
        for case_name, case_results in results.items():
            for algorithm, result in case_results.items():
                with self.subTest(case=case_name, algorithm=algorithm):
                    self.assertTrue(result['success'], 
                                  f"{algorithm} failed on {case_name}: {result.get('error')}")
                    
        # Print benchmark summary
        self._print_benchmark_results(results)
        
        return results
        
    def _print_benchmark_results(self, results: Dict):
        """Print formatted benchmark results."""
        print("\n" + "="*80)
        print("COMPRESSION ALGORITHM BENCHMARK RESULTS")
        print("="*80)
        
        for case_name, case_results in results.items():
            print(f"\nTest Case: {case_name}")
            print("-" * 50)
            print("Algorithm    | Ratio | Time (ms) | Size (bytes) | Success")
            print("-" * 65)
            
            for algorithm, result in case_results.items():
                if result['success']:
                    metrics = result['metrics']
                    print(f"{algorithm:12} | {metrics.compression_ratio:5.2f} | "
                          f"{metrics.compression_time*1000:8.1f} | "
                          f"{metrics.compressed_size:6d} | ✓")
                    
                    if algorithm == 'prime_driven':
                        print(f"{'':12} | Enhancement: {metrics.enhancement_factor:.1f}x | "
                              f"Clusters: {metrics.prime_clusters_found}")
                else:
                    print(f"{algorithm:12} | ERROR | - | - | ✗")
                    
    def test_memory_efficiency(self):
        """Test memory efficiency of compression algorithm."""
        import tracemalloc
        
        test_data = b'Test data for memory profiling. ' * 1000  # ~33KB
        
        # Start memory tracing
        tracemalloc.start()
        
        # Compress data
        snapshot1 = tracemalloc.take_snapshot()
        compressed, metrics = self.prime_compressor.compress(test_data)
        snapshot2 = tracemalloc.take_snapshot()
        
        # Decompress data
        decompressed, integrity = self.prime_compressor.decompress(compressed, metrics)
        snapshot3 = tracemalloc.take_snapshot()
        
        tracemalloc.stop()
        
        # Analyze memory usage
        compression_stats = snapshot2.compare_to(snapshot1, 'lineno')
        decompression_stats = snapshot3.compare_to(snapshot2, 'lineno')
        
        # Get peak memory usage during compression
        compression_memory = sum(stat.size for stat in compression_stats if stat.size > 0)
        
        # Verify memory efficiency (should be reasonable compared to input size)
        input_size = len(test_data)
        memory_ratio = compression_memory / input_size
        
        self.assertLess(memory_ratio, 10.0, 
                       f"Memory usage should be <10x input size, got {memory_ratio:.1f}x")
        
        # Verify decompression correctness
        self.assertEqual(decompressed, test_data)
        self.assertTrue(integrity)
        
        print(f"Memory efficiency: {memory_ratio:.1f}x input size ({compression_memory:,} bytes)")


class TestMathematicalValidation(unittest.TestCase):
    """Test mathematical validation and Z Framework compliance."""
    
    def test_optimal_k_parameter_validation(self):
        """Test that k* = 0.3 provides optimal prime enhancement."""
        transformer = PrimeGeodesicTransform()
        
        # Test k values around the optimum
        k_values = [0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5]
        enhancements = []
        
        indices = np.arange(1, 1001)
        prime_mask = np.array([self._is_prime_simple(i) for i in range(2, 1002)])
        
        for k in k_values:
            transformer_k = PrimeGeodesicTransform(k)
            theta_values = transformer_k.frame_shift_residues(indices)
            enhancement = transformer_k.compute_prime_enhancement(theta_values, prime_mask)
            enhancements.append(enhancement)
            
        # Find the k that gives maximum enhancement
        max_idx = np.argmax(enhancements)
        optimal_k = k_values[max_idx]
        
        # Verify k* ≈ 0.3 is close to optimal
        self.assertLess(abs(optimal_k - 0.3), 0.1, 
                       f"Optimal k should be near 0.3, found {optimal_k}")
        
        print(f"K optimization results:")
        for k, enhancement in zip(k_values, enhancements):
            marker = " ← OPTIMAL" if k == optimal_k else ""
            print(f"  k={k:.2f}: enhancement={enhancement:.2f}x{marker}")
            
    def test_golden_ratio_precision(self):
        """Test golden ratio computation precision."""
        transformer = PrimeGeodesicTransform()
        
        # Verify golden ratio properties
        phi = float(PHI)
        self.assertAlmostEqual(phi**2, phi + 1, places=10, 
                              msg="φ² should equal φ + 1")
        self.assertAlmostEqual(1/phi, phi - 1, places=10,
                              msg="1/φ should equal φ - 1")
        
        # Test mathematical consistency in transformations
        test_indices = np.array([1, 2, 3, 5, 8, 13, 21])  # Fibonacci numbers
        theta_values = transformer.frame_shift_residues(test_indices)
        
        # All transformed values should be in [0, φ) range
        self.assertTrue(np.all(theta_values >= 0))
        self.assertTrue(np.all(theta_values < phi))
        
    def test_z_framework_compliance(self):
        """Test compliance with Z Framework principles."""
        compressor = PrimeDrivenCompressor()
        
        # Test universal invariant form Z = A(B/c)
        # For compression: A = compression_function, B = data_rate, c = invariant
        test_data = b'Z Framework compliance test data'
        
        compressed, metrics = compressor.compress(test_data)
        decompressed, integrity = compressor.decompress(compressed, metrics)
        
        # Z Framework requirements
        self.assertTrue(integrity, "Z Framework requires data integrity")
        self.assertGreater(metrics.enhancement_factor, 1.0, 
                          "Z Framework requires prime enhancement > 1")
        self.assertEqual(len(decompressed), len(test_data),
                        "Z Framework requires size preservation")
        
        # Mathematical validation
        self.assertAlmostEqual(float(compressor.k), 0.2, places=3,
                              msg="Should use optimal curvature k* ≈ 0.2")
        
    def _is_prime_simple(self, n):
        """Simple primality test for validation."""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True


class TestCanterburyCorpusValidation(unittest.TestCase):
    """Test on Canterbury Corpus-like datasets for standardized validation."""
    
    def setUp(self):
        """Set up corpus-like test data."""
        self.compressor = PrimeDrivenCompressor(use_histogram_clustering=True)
        self.benchmark = CompressionBenchmark()
        
    def test_text_data_compression(self):
        """Test compression of text-like data."""
        # Simulate text data with English letter frequencies
        text_data = self._generate_english_like_text(2000)
        
        compressed, metrics = self.compressor.compress(text_data)
        decompressed, integrity = self.compressor.decompress(compressed, metrics)
        
        self.assertEqual(decompressed, text_data)
        self.assertTrue(integrity)
        
        print(f"Text data: {metrics.compression_ratio:.3f} compression ratio")
        
    def test_executable_data_compression(self):
        """Test compression of executable-like binary data."""
        # Simulate executable with mixed patterns
        exec_data = self._generate_executable_like_data(2000)
        
        compressed, metrics = self.compressor.compress(exec_data)
        decompressed, integrity = self.compressor.decompress(compressed, metrics)
        
        self.assertEqual(decompressed, exec_data)
        self.assertTrue(integrity)
        
        print(f"Executable data: {metrics.compression_ratio:.3f} compression ratio")
        
    def test_image_data_compression(self):
        """Test compression of image-like data."""
        # Simulate image data with spatial correlation
        image_data = self._generate_image_like_data(2000)
        
        compressed, metrics = self.compressor.compress(image_data)
        decompressed, integrity = self.compressor.decompress(compressed, metrics)
        
        self.assertEqual(decompressed, image_data)
        self.assertTrue(integrity)
        
        print(f"Image data: {metrics.compression_ratio:.3f} compression ratio")
        
    def _generate_english_like_text(self, size: int) -> bytes:
        """Generate text with English-like letter frequencies."""
        np.random.seed(42)
        # Approximate English letter frequencies (normalized)
        letters = 'etaoinshrdlcumwfgypbvkjxqz'
        weights = [12.7, 9.1, 8.2, 7.5, 7.0, 6.7, 6.3, 6.1, 6.0, 4.3,
                  4.0, 2.8, 2.8, 2.4, 2.4, 2.2, 2.0, 1.9, 1.5, 1.0,
                  0.8, 0.2, 0.2, 0.1, 0.1, 0.1]
        space_weight = 15.0  # Weight for space character
        all_weights = weights + [space_weight]
        normalized_weights = np.array(all_weights) / sum(all_weights)
        
        text_chars = np.random.choice(list(letters + ' '), size, p=normalized_weights)
        return ''.join(text_chars).encode('ascii')
        
    def _generate_executable_like_data(self, size: int) -> bytes:
        """Generate data similar to executable files."""
        np.random.seed(42)
        # Mix of code patterns, null bytes, and structured data
        data = np.zeros(size, dtype=np.uint8)
        
        # Add some null bytes (common in executables)
        null_positions = np.random.choice(size, size // 4, replace=False)
        data[null_positions] = 0
        
        # Add some common byte patterns
        common_bytes = [0x00, 0xFF, 0x48, 0x89, 0xE5, 0xC3]  # x86 patterns
        pattern_positions = np.random.choice(size, size // 3, replace=False)
        data[pattern_positions] = np.random.choice(common_bytes, len(pattern_positions))
        
        # Fill remaining with random
        remaining = data == 0
        remaining_count = np.sum(remaining)
        if remaining_count > 0:
            data[remaining] = np.random.randint(1, 256, remaining_count)
            
        return data.tobytes()
        
    def _generate_image_like_data(self, size: int) -> bytes:
        """Generate data similar to image files."""
        np.random.seed(42)
        # Create data with spatial correlation (like images)
        width = int(np.sqrt(size))
        height = size // width
        
        # Generate smooth gradients and noise
        x, y = np.meshgrid(np.linspace(0, 1, width), np.linspace(0, 1, height))
        base = (128 * (np.sin(x * 2 * np.pi) + np.cos(y * 2 * np.pi))).astype(int)
        noise = np.random.normal(0, 20, (height, width))
        
        image_data = np.clip(base + noise, 0, 255).astype(np.uint8)
        
        # Pad to exact size if needed
        flat_data = image_data.flatten()
        if len(flat_data) < size:
            padding = np.random.randint(0, 256, size - len(flat_data), dtype=np.uint8)
            flat_data = np.concatenate([flat_data, padding])
        
        return flat_data[:size].tobytes()


if __name__ == '__main__':
    """Run comprehensive test suite with performance profiling."""
    
    print("="*80)
    print("COMPREHENSIVE COMPRESSION ALGORITHM TEST SUITE")
    print("="*80)
    print("Testing: Decompression correctness, performance benchmarks, mathematical validation")
    print()
    
    # Run test suites in order
    test_suites = [
        TestDecompressionCorrectness,
        TestPerformanceBenchmarks, 
        TestMathematicalValidation,
        TestCanterburyCorpusValidation
    ]
    
    overall_success = True
    
    for suite_class in test_suites:
        print(f"\nRunning {suite_class.__name__}...")
        print("-" * 60)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            overall_success = False
            
    print("\n" + "="*80)
    if overall_success:
        print("🎉 ALL TESTS PASSED - Compression algorithm validation complete!")
        print("✓ Data integrity verified across all test cases")
        print("✓ Performance benchmarks meet requirements") 
        print("✓ Mathematical validation confirms Z Framework compliance")
        print("✓ Canterbury Corpus-like validation successful")
    else:
        print("❌ SOME TESTS FAILED - Review output above for details")
        
    print("="*80)