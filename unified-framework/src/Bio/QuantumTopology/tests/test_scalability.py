"""
Scalability and Performance Benchmarks for Bio.QuantumTopology

Tests the performance characteristics of quantum topology functions across
various sequence lengths, from small test cases to full gene-length sequences.

Provides benchmarks for:
- Coordinate generation performance vs sequence length
- Memory usage scaling
- Quantum correlation computation efficiency
- Optimization recommendations for genomic-scale analysis
"""

import unittest
import time
import numpy as np
import sys
import os

# Import Bio.Seq with proper error handling to prevent confusion
try:
    from Bio.Seq import Seq
except ImportError:
    import pytest
    pytest.importorskip("Bio", minversion="1.83", reason="Bio.Seq requires biopython package. Install with: pip install biopython")

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.Bio.QuantumTopology.helical import (
    generate_helical_coordinates,
    compute_quantum_correlations,
    complexity_metric,
    geodesic_transform
)
from src.Bio.QuantumTopology.alignment import quantum_alignment


class TestScalabilityBenchmarks(unittest.TestCase):
    """Benchmarks for testing scalability across various sequence lengths."""
    
    def setUp(self):
        """Set up test sequences of various lengths."""
        # Generate realistic DNA sequences of different lengths
        bases = 'ATGC'
        np.random.seed(42)  # For reproducible tests
        
        # Test sequence lengths representing different genomic scales
        self.sequences = {
            'small': Seq(''.join(np.random.choice(list(bases), 10))),      # 10 bases
            'medium': Seq(''.join(np.random.choice(list(bases), 100))),    # 100 bases  
            'large': Seq(''.join(np.random.choice(list(bases), 1000))),    # 1KB
            'gene_size': Seq(''.join(np.random.choice(list(bases), 3000))), # Typical gene
            'large_gene': Seq(''.join(np.random.choice(list(bases), 10000))) # Large gene
        }
        
        # Store performance results for analysis
        self.performance_results = {}
    
    def benchmark_coordinate_generation(self, seq_name, seq):
        """Benchmark helical coordinate generation for a sequence."""
        start_time = time.time()
        coords = generate_helical_coordinates(seq, hypothetical=False)
        end_time = time.time()
        
        execution_time = end_time - start_time
        sequence_length = len(seq)
        
        # Basic validation
        self.assertEqual(len(coords['x']), sequence_length)
        self.assertEqual(len(coords['y']), sequence_length)
        self.assertEqual(len(coords['z']), sequence_length)
        
        return {
            'sequence_length': sequence_length,
            'execution_time': execution_time,
            'time_per_base': execution_time / max(sequence_length, 1),
            'coordinates_generated': sequence_length * 3  # x, y, z
        }
    
    def benchmark_quantum_correlations(self, seq_name, seq):
        """Benchmark quantum correlation computation for a sequence."""
        if len(seq) == 0:
            return None
            
        start_time = time.time()
        correlations = compute_quantum_correlations(seq, window_size=min(10, len(seq)), hypothetical=False)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Validate results structure
        self.assertIn('correlations', correlations)
        self.assertIn('entangled_regions', correlations)
        
        return {
            'sequence_length': len(seq),
            'execution_time': execution_time,
            'time_per_base': execution_time / len(seq)
        }
    
    def test_coordinate_generation_scaling(self):
        """Test performance scaling of coordinate generation across sequence lengths."""
        print("\n=== Coordinate Generation Scaling Benchmark ===")
        
        results = {}
        for seq_name, seq in self.sequences.items():
            benchmark = self.benchmark_coordinate_generation(seq_name, seq)
            results[seq_name] = benchmark
            
            print(f"{seq_name:12} ({benchmark['sequence_length']:5d} bases): "
                  f"{benchmark['execution_time']:.4f}s "
                  f"({benchmark['time_per_base']*1000:.3f} ms/base)")
        
        # Verify linear scaling (O(n) complexity)
        lengths = [results[name]['sequence_length'] for name in ['small', 'medium', 'large']]
        times = [results[name]['execution_time'] for name in ['small', 'medium', 'large']]
        
        # Check that time scales roughly linearly with sequence length
        # Allow some overhead for small sequences
        for i in range(1, len(lengths)):
            ratio_length = lengths[i] / lengths[i-1]
            ratio_time = times[i] / times[i-1]
            
            # Should be roughly linear, but allow overhead factor of 2-3x for small sequences
            self.assertLess(ratio_time, ratio_length * 3.0, 
                          f"Scaling worse than O(n): length ratio {ratio_length:.1f}, time ratio {ratio_time:.1f}")
        
        self.performance_results['coordinate_generation'] = results
    
    def test_quantum_correlations_scaling(self):
        """Test performance scaling of quantum correlation computation."""
        print("\n=== Quantum Correlations Scaling Benchmark ===")
        
        results = {}
        # Test smaller sequences for correlation analysis (computationally more intensive)
        test_sequences = {k: v for k, v in self.sequences.items() if len(v) <= 3000}
        
        for seq_name, seq in test_sequences.items():
            benchmark = self.benchmark_quantum_correlations(seq_name, seq)
            if benchmark:
                results[seq_name] = benchmark
                
                print(f"{seq_name:12} ({benchmark['sequence_length']:5d} bases): "
                      f"{benchmark['execution_time']:.4f}s "
                      f"({benchmark['time_per_base']*1000:.3f} ms/base)")
        
        self.performance_results['quantum_correlations'] = results
    
    def test_memory_usage_estimation(self):
        """Estimate memory usage for different sequence lengths."""
        print("\n=== Memory Usage Analysis ===")
        
        for seq_name, seq in self.sequences.items():
            seq_len = len(seq)
            
            # Each coordinate array (x, y, z, theta) is float64 = 8 bytes
            coord_memory = seq_len * 4 * 8  # 4 arrays * 8 bytes
            
            # Base sequence memory (roughly 1 byte per base)
            seq_memory = seq_len
            
            total_mb = (coord_memory + seq_memory) / (1024 * 1024)
            
            print(f"{seq_name:12} ({seq_len:5d} bases): ~{total_mb:.2f} MB")
            
            # Verify memory usage is reasonable (< 100MB for largest test)
            self.assertLess(total_mb, 100, 
                          f"Memory usage too high: {total_mb:.1f} MB for {seq_len} bases")
    
    def test_alignment_scaling(self):
        """Test quantum alignment performance with different sequence lengths."""
        print("\n=== Quantum Alignment Scaling Benchmark ===")
        
        # Test alignment between sequences of similar lengths
        test_pairs = [
            ('small', 'small'),
            ('medium', 'medium'), 
            ('large', 'large')
        ]
        
        for seq1_name, seq2_name in test_pairs:
            seq1 = self.sequences[seq1_name]
            seq2 = self.sequences[seq2_name]
            
            start_time = time.time()
            alignment = quantum_alignment(seq1, seq2, method='bell_violation', hypothetical=False)
            end_time = time.time()
            
            execution_time = end_time - start_time
            seq_length = len(seq1)
            
            print(f"{seq1_name} vs {seq2_name} ({seq_length:4d} bases): "
                  f"{execution_time:.4f}s ({execution_time/(seq_length**2)*1000:.3f} ms/base²)")
            
            # Validate alignment result
            self.assertIn('alignment_score', alignment)
            self.assertTrue(0 <= alignment['alignment_score'] <= 1)
    
    def test_performance_regression_thresholds(self):
        """Test that performance stays within reasonable bounds."""
        print("\n=== Performance Regression Checks ===")
        
        # Performance thresholds (generous to avoid flaky tests)
        thresholds = {
            'coordinate_generation_100_bases': 0.1,    # 100ms max for 100 bases
            'coordinate_generation_1000_bases': 0.5,   # 500ms max for 1000 bases
            'coordinate_generation_10000_bases': 2.0,  # 2s max for 10,000 bases
        }
        
        # Test 100-base sequence
        seq_100 = self.sequences['medium']
        start = time.time()
        generate_helical_coordinates(seq_100, hypothetical=False)
        time_100 = time.time() - start
        
        self.assertLess(time_100, thresholds['coordinate_generation_100_bases'],
                       f"100-base generation too slow: {time_100:.3f}s > {thresholds['coordinate_generation_100_bases']}s")
        
        # Test 1000-base sequence  
        seq_1000 = self.sequences['large']
        start = time.time()
        generate_helical_coordinates(seq_1000, hypothetical=False)
        time_1000 = time.time() - start
        
        self.assertLess(time_1000, thresholds['coordinate_generation_1000_bases'],
                       f"1000-base generation too slow: {time_1000:.3f}s > {thresholds['coordinate_generation_1000_bases']}s")
        
        # Test 10000-base sequence
        seq_10000 = self.sequences['large_gene']
        start = time.time()
        generate_helical_coordinates(seq_10000, hypothetical=False)
        time_10000 = time.time() - start
        
        self.assertLess(time_10000, thresholds['coordinate_generation_10000_bases'],
                       f"10000-base generation too slow: {time_10000:.3f}s > {thresholds['coordinate_generation_10000_bases']}s")
        
        print(f"✓ Coordinate generation performance within thresholds")
        print(f"  100 bases: {time_100:.3f}s (limit: {thresholds['coordinate_generation_100_bases']}s)")
        print(f"  1000 bases: {time_1000:.3f}s (limit: {thresholds['coordinate_generation_1000_bases']}s)")
        print(f"  10000 bases: {time_10000:.3f}s (limit: {thresholds['coordinate_generation_10000_bases']}s)")
    
    def test_complexity_analysis(self):
        """Analyze computational complexity of core operations."""
        print("\n=== Computational Complexity Analysis ===")
        
        # Test divisor counting complexity (used in complexity_metric)
        test_values = [10, 100, 1000, 10000]
        times = []
        
        for n in test_values:
            start = time.time()
            for i in range(1, min(n, 100) + 1):  # Test first 100 positions
                complexity_metric(i)
            end = time.time()
            times.append(end - start)
            
        print("Complexity metric scaling:")
        for i, (n, t) in enumerate(zip(test_values, times)):
            print(f"  n={n:5d}: {t:.4f}s")
        
        # The divisor count function is O(√n) per call, which is acceptable
        # for moderate sequence lengths but may need optimization for very large sequences
    
    def test_optimization_recommendations(self):
        """Provide optimization recommendations based on benchmarks."""
        print("\n=== Optimization Recommendations ===")
        
        recommendations = []
        
        # Check if large sequences take too long
        large_seq = self.sequences['large_gene']
        start = time.time()
        generate_helical_coordinates(large_seq, hypothetical=False)
        large_time = time.time() - start
        
        if large_time > 1.0:
            recommendations.append(
                f"Large sequence performance: {large_time:.2f}s for {len(large_seq)} bases. "
                "Consider vectorizing divisor_count() for better performance."
            )
        
        # Memory recommendations
        estimated_memory_mb = len(large_seq) * 4 * 8 / (1024 * 1024)
        if estimated_memory_mb > 50:
            recommendations.append(
                f"Memory usage: ~{estimated_memory_mb:.1f}MB for {len(large_seq)} bases. "
                "Consider streaming processing for very large genomes."
            )
        
        # General recommendations
        recommendations.extend([
            "For full genomic analysis (3B+ bases), implement chunk-based processing",
            "Consider caching divisor counts for repeated complexity metric calls",
            "For interactive applications, add progress callbacks for long sequences",
            "Profile memory usage with real genomic data to optimize array allocation"
        ])
        
        print("Performance optimization suggestions:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Test passes if we can make recommendations (no assertions needed)
        self.assertTrue(len(recommendations) > 0)


class TestRealWorldScenarios(unittest.TestCase):
    """Test scenarios that represent real genomic analysis use cases."""
    
    def test_gene_analysis_workflow(self):
        """Test a complete workflow for analyzing a gene-sized sequence."""
        # Simulate a real gene sequence (e.g., human BRCA1 partial sequence)
        np.random.seed(123)
        gene_seq = Seq(''.join(np.random.choice(['A', 'T', 'G', 'C'], 2500)))
        
        print(f"\n=== Gene Analysis Workflow ({len(gene_seq)} bases) ===")
        
        # Step 1: Generate coordinates
        start = time.time()
        coords = generate_helical_coordinates(gene_seq, k=0.3, hypothetical=False)
        coord_time = time.time() - start
        
        # Step 2: Compute correlations for windows
        start = time.time()
        correlations = compute_quantum_correlations(gene_seq, window_size=20, hypothetical=False)
        corr_time = time.time() - start
        
        # Step 3: Find interesting regions
        if len(correlations['correlations']) > 0:
            max_correlation = np.max(correlations['correlations'])
            entangled_count = np.sum(correlations['entangled_regions'])
        else:
            max_correlation = 0
            entangled_count = 0
        
        total_time = coord_time + corr_time
        
        print(f"Coordinate generation: {coord_time:.3f}s")
        print(f"Correlation analysis: {corr_time:.3f}s") 
        print(f"Total analysis time: {total_time:.3f}s")
        print(f"Max correlation: {max_correlation:.3f}")
        print(f"Entangled regions: {entangled_count}")
        
        # Workflow should complete in reasonable time for gene-sized sequences
        self.assertLess(total_time, 5.0, f"Gene analysis too slow: {total_time:.2f}s")
        
        # Results should be valid
        self.assertEqual(len(coords['x']), len(gene_seq))
        self.assertIsInstance(correlations['correlations'], np.ndarray)
    
    def test_comparative_genomics_scenario(self):
        """Test comparing multiple sequences as in comparative genomics."""
        # Simulate comparing orthologous genes from different species
        np.random.seed(456)
        
        sequences = [
            Seq(''.join(np.random.choice(['A', 'T', 'G', 'C'], 800))),
            Seq(''.join(np.random.choice(['A', 'T', 'G', 'C'], 850))),
            Seq(''.join(np.random.choice(['A', 'T', 'G', 'C'], 790)))
        ]
        
        print(f"\n=== Comparative Genomics Scenario ===")
        
        # Compare all pairs
        comparisons = []
        total_time = 0
        
        for i in range(len(sequences)):
            for j in range(i + 1, len(sequences)):
                start = time.time()
                alignment = quantum_alignment(sequences[i], sequences[j], 
                                            method='bell_violation', hypothetical=False)
                end = time.time()
                
                comparison_time = end - start
                total_time += comparison_time
                
                comparisons.append({
                    'sequences': (i, j),
                    'lengths': (len(sequences[i]), len(sequences[j])),
                    'score': alignment['alignment_score'],
                    'time': comparison_time
                })
        
        print(f"Pairwise comparisons: {len(comparisons)}")
        print(f"Total comparison time: {total_time:.3f}s")
        print(f"Average time per comparison: {total_time/len(comparisons):.3f}s")
        
        for comp in comparisons:
            print(f"  Seq {comp['sequences'][0]} vs {comp['sequences'][1]} "
                  f"({comp['lengths'][0]}x{comp['lengths'][1]} bases): "
                  f"score={comp['score']:.3f}, time={comp['time']:.3f}s")
        
        # All comparisons should complete successfully
        self.assertEqual(len(comparisons), 3)  # 3 choose 2
        for comp in comparisons:
            self.assertTrue(0 <= comp['score'] <= 1)


if __name__ == '__main__':
    # Run with verbose output to see benchmark results
    unittest.main(verbosity=2)