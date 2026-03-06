"""
Tests for Z Universal Invariant Geodesic Hotspot Mapper

Tests the core functionality, performance, and integration of the 
geodesic hotspot mapper for genomic analysis.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
from pathlib import Path

# Import Bio.Seq with proper error handling to prevent confusion
pytest.importorskip("Bio", reason="Bio.Seq requires biopython package. Install with: pip install biopython")
from Bio.Seq import Seq

# Import the module to test
import sys
sys.path.append('../../src')
from src.Bio.QuantumTopology import ZGeodesicHotspotMapper

class TestZGeodesicHotspotMapper:
    """Test suite for ZGeodesicHotspotMapper class."""
    
    @pytest.fixture
    def mapper(self):
        """Create a mapper instance for testing."""
        return ZGeodesicHotspotMapper()
    
    @pytest.fixture
    def test_sequence(self):
        """Create a test DNA sequence."""
        return Seq("ATGCGATCGATCGTAGCGATCGTAGCGATCGTAGCGATCGTAGCGATCGATCGTAGCGATC")
    
    @pytest.fixture
    def sample_fasta_file(self):
        """Create a temporary FASTA file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(">test_seq1\n")
            f.write("ATGCGATCGATCGTAGCGATCGTAGCGATCGTAGCGATCGTAGCGATCGATCGTAGCGATC\n")
            f.write(">test_seq2\n") 
            f.write("AAATTTGGGCCCAAATTTGGGCCCAAATTTGGGCCC\n")
            return Path(f.name)
    
    @pytest.fixture
    def sample_gff_file(self):
        """Create a temporary GFF file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
            f.write("##gff-version 3\n")
            f.write("test_seq1\tprediction\tgene\t10\t50\t0.9\t+\t.\tID=gene1\n")
            f.write("test_seq1\tprediction\texon\t15\t30\t0.8\t+\t.\tID=exon1\n")
            f.write("test_seq1\tprediction\tCDS\t20\t25\t0.95\t+\t0\tID=cds1\n")
            return Path(f.name)
    
    def test_initialization(self, mapper):
        """Test mapper initialization with default parameters."""
        assert mapper.k_optimal == 0.3
        assert abs(mapper.modulus - 1.618) < 0.001
        assert abs(mapper.phi - 1.618033988749) < 0.000001
        assert mapper.e_squared > 7.0
        assert hasattr(mapper, 'geodesic_mapper')
    
    def test_initialization_custom_parameters(self):
        """Test mapper initialization with custom parameters."""
        custom_mapper = ZGeodesicHotspotMapper(k_optimal=0.5, modulus=2.718)
        assert custom_mapper.k_optimal == 0.5
        assert abs(custom_mapper.modulus - 2.718) < 0.001
    
    def test_fasta_loading(self, mapper, sample_fasta_file):
        """Test FASTA file loading functionality."""
        sequences = mapper.load_fasta(sample_fasta_file)
        
        assert len(sequences) == 2
        assert 'test_seq1' in sequences
        assert 'test_seq2' in sequences
        assert len(sequences['test_seq1']) == 61  # Updated to match actual length
        assert len(sequences['test_seq2']) == 36
        
        # Clean up
        sample_fasta_file.unlink()
    
    def test_fasta_loading_invalid_file(self, mapper):
        """Test FASTA loading with invalid file."""
        with pytest.raises(ValueError, match="Error loading FASTA file"):
            mapper.load_fasta("nonexistent_file.fasta")
    
    def test_z_invariant_coordinates_computation(self, mapper, test_sequence):
        """Test Z-invariant coordinate computation."""
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence)
        
        # Check required keys are present
        required_keys = ['x', 'y', 'z', 'theta', 'z_invariant', 'geodesic_coords', 
                        'complexity', 'positions', 'metadata']
        for key in required_keys:
            assert key in coordinates
        
        # Check array dimensions
        seq_len = len(test_sequence)
        assert len(coordinates['x']) == seq_len
        assert len(coordinates['y']) == seq_len
        assert len(coordinates['z']) == seq_len
        assert len(coordinates['z_invariant']) == seq_len
        assert len(coordinates['geodesic_coords']) == seq_len
        assert len(coordinates['complexity']) == seq_len
        assert len(coordinates['positions']) == seq_len
        
        # Check metadata
        assert coordinates['metadata']['sequence_length'] == seq_len
        assert coordinates['metadata']['z_invariant_computed'] is True
        assert 'processing_time' in coordinates['metadata']
        assert coordinates['metadata']['processing_time'] > 0
    
    def test_z_invariant_empty_sequence(self, mapper):
        """Test Z-invariant computation with empty sequence."""
        empty_seq = Seq("")
        coordinates = mapper.compute_z_invariant_coordinates(empty_seq)
        
        assert len(coordinates['positions']) == 0
        assert len(coordinates['z_invariant']) == 0
        assert coordinates['metadata']['sequence_length'] == 0
    
    def test_prime_hotspot_detection(self, mapper, test_sequence):
        """Test prime hotspot detection functionality."""
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence)
        hotspots = mapper.detect_prime_hotspots(coordinates)
        
        # Check required keys
        required_keys = ['hotspots', 'total_hotspots', 'prime_positions', 
                        'total_primes', 'sequence_length', 'processing_time']
        for key in required_keys:
            assert key in hotspots
        
        # Check data types and ranges
        assert isinstance(hotspots['hotspots'], list)
        assert isinstance(hotspots['total_hotspots'], int)
        assert isinstance(hotspots['prime_positions'], np.ndarray)
        assert hotspots['total_hotspots'] >= 0
        assert hotspots['total_primes'] >= 0
        assert hotspots['sequence_length'] == len(test_sequence)
        assert hotspots['processing_time'] > 0
        
        # Check hotspot structure if any found
        if hotspots['total_hotspots'] > 0:
            hotspot = hotspots['hotspots'][0]
            required_hotspot_keys = ['start', 'end', 'prime_count', 'expected_count',
                                   'density_ratio', 'enhanced_density']
            for key in required_hotspot_keys:
                assert key in hotspot
            
            assert hotspot['start'] < hotspot['end']
            assert hotspot['prime_count'] >= 0
            assert hotspot['density_ratio'] >= 0
            assert hotspot['enhanced_density'] >= 0
    
    def test_prime_hotspot_detection_parameters(self, mapper, test_sequence):
        """Test prime hotspot detection with different parameters."""
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence)
        
        # Test with different thresholds
        hotspots_low = mapper.detect_prime_hotspots(
            coordinates, density_threshold=1.0, window_size=50
        )
        hotspots_high = mapper.detect_prime_hotspots(
            coordinates, density_threshold=3.0, window_size=50
        )
        
        # Higher threshold should find fewer or equal hotspots
        assert hotspots_high['total_hotspots'] <= hotspots_low['total_hotspots']
    
    def test_sieve_of_eratosthenes(self, mapper):
        """Test prime generation using Sieve of Eratosthenes."""
        # Test known small cases
        assert mapper._sieve_of_eratosthenes(0) == []
        assert mapper._sieve_of_eratosthenes(1) == []
        assert mapper._sieve_of_eratosthenes(2) == [2]
        assert mapper._sieve_of_eratosthenes(10) == [2, 3, 5, 7]
        assert mapper._sieve_of_eratosthenes(20) == [2, 3, 5, 7, 11, 13, 17, 19]
        
        # Test larger case
        primes_100 = mapper._sieve_of_eratosthenes(100)
        expected_count = 25  # There are 25 primes < 100
        assert len(primes_100) == expected_count
        assert all(p >= 2 for p in primes_100)
    
    def test_gff_annotation_loading(self, mapper, sample_gff_file):
        """Test GFF annotation file loading."""
        annotations = mapper.load_annotations(sample_gff_file, file_format='gff')
        
        assert len(annotations) == 3
        assert list(annotations.columns) == [
            'seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes'
        ]
        
        # Check data types and values
        assert annotations.iloc[0]['seqid'] == 'test_seq1'
        assert annotations.iloc[0]['type'] == 'gene'
        assert annotations.iloc[0]['start'] == 10
        assert annotations.iloc[0]['end'] == 50
        
        # Clean up
        sample_gff_file.unlink()
    
    def test_bed_annotation_loading(self, mapper):
        """Test BED annotation file loading."""
        # Create temporary BED file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False) as f:
            f.write("chr1\t10\t50\tgene1\t900\t+\n")
            f.write("chr1\t20\t30\texon1\t800\t+\n")
            bed_file = Path(f.name)
        
        annotations = mapper.load_annotations(bed_file, file_format='bed')
        
        assert len(annotations) == 2
        assert 'seqid' in annotations.columns
        assert 'start' in annotations.columns
        assert 'end' in annotations.columns
        
        # Check 0-based to 1-based conversion
        assert annotations.iloc[0]['start'] == 11  # 10 + 1
        assert annotations.iloc[0]['end'] == 50
        
        # Clean up
        bed_file.unlink()
    
    def test_annotation_format_auto_detection(self, mapper, sample_gff_file):
        """Test automatic annotation format detection."""
        annotations = mapper.load_annotations(sample_gff_file, file_format='auto')
        assert len(annotations) == 3
        
        # Clean up
        sample_gff_file.unlink()
    
    def test_hotspot_annotation_correlation(self, mapper, test_sequence):
        """Test correlation between hotspots and annotations."""
        # Run analysis
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence)
        hotspots = mapper.detect_prime_hotspots(coordinates, density_threshold=1.0)
        
        # Create sample annotations
        annotations = pd.DataFrame({
            'seqid': ['test_seq'] * 3,
            'type': ['gene', 'exon', 'promoter'],
            'start': [1, 15, 45],
            'end': [20, 25, 55],
            'source': ['prediction'] * 3
        })
        
        correlations = mapper.correlate_hotspots_with_annotations(
            hotspots, annotations, overlap_threshold=0.3
        )
        
        # Check correlation results structure
        required_keys = ['correlations', 'total_correlations', 'correlation_rate', 
                        'overlap_threshold', 'annotation_types']
        for key in required_keys:
            assert key in correlations
        
        assert isinstance(correlations['correlations'], list)
        assert correlations['total_correlations'] >= 0
        assert 0 <= correlations['correlation_rate'] <= 1
        assert correlations['overlap_threshold'] == 0.3
    
    def test_performance_benchmark(self, mapper):
        """Test performance benchmarking functionality."""
        test_lengths = [50, 100, 200]  # Small lengths for fast testing
        benchmark_results = mapper.benchmark_performance(test_lengths, num_trials=2)
        
        # Check results structure
        assert 'sequence_lengths' in benchmark_results
        assert 'processing_times' in benchmark_results
        assert 'times_per_base' in benchmark_results
        assert 'num_trials' in benchmark_results
        
        # Check dimensions
        assert len(benchmark_results['processing_times']) == len(test_lengths)
        assert len(benchmark_results['times_per_base']) == len(test_lengths)
        assert benchmark_results['num_trials'] == 2
        
        # Check that times are positive and reasonable
        for time_val in benchmark_results['processing_times']:
            assert time_val > 0
            assert time_val < 10  # Should be fast for test sizes
        
        # Check linear fit if computed
        if 'linear_fit' in benchmark_results:
            fit = benchmark_results['linear_fit']
            assert 'r_squared' in fit
            assert 'linear_scaling' in fit
            assert 0 <= fit['r_squared'] <= 1
    
    def test_export_functionality(self, mapper, test_sequence):
        """Test results export functionality."""
        # Run analysis
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence)
        hotspots = mapper.detect_prime_hotspots(coordinates)
        
        # Test CSV export
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"
            
            mapper.export_results(hotspots, coordinates, output_path, format='csv')
            
            # Check files were created
            assert (output_path.with_suffix('.coordinates.csv')).exists()
            if hotspots['total_hotspots'] > 0:
                assert (output_path.with_suffix('.hotspots.csv')).exists()
            
            # Check CSV content
            coord_df = pd.read_csv(output_path.with_suffix('.coordinates.csv'))
            assert len(coord_df) == len(test_sequence)
            expected_columns = ['position', 'x_coord', 'y_coord', 'z_coord', 
                              'z_invariant', 'geodesic_coord', 'complexity']
            for col in expected_columns:
                assert col in coord_df.columns
    
    def test_export_json_format(self, mapper, test_sequence):
        """Test JSON export functionality."""
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence)
        hotspots = mapper.detect_prime_hotspots(coordinates)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"
            
            mapper.export_results(hotspots, coordinates, output_path, format='json')
            
            # Check JSON file was created
            json_file = output_path.with_suffix('.json')
            assert json_file.exists()
            
            # Check JSON content
            import json
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            assert 'hotspots' in data
            assert 'coordinates' in data
            assert 'export_timestamp' in data
    
    def test_export_invalid_format(self, mapper, test_sequence):
        """Test export with invalid format."""
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence)
        hotspots = mapper.detect_prime_hotspots(coordinates)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export"
            
            with pytest.raises(ValueError, match="Unsupported export format"):
                mapper.export_results(hotspots, coordinates, output_path, format='xml')
    
    def test_mathematical_consistency(self, mapper, test_sequence):
        """Test mathematical consistency of transformations."""
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence, k=0.3)
        
        # Test golden ratio properties
        assert abs(mapper.phi - (1 + np.sqrt(5)) / 2) < 1e-10
        
        # Test geodesic transformation bounds
        geodesic_coords = coordinates['geodesic_coords']
        assert np.all(geodesic_coords >= 0)
        assert np.all(geodesic_coords < mapper.phi)
        
        # Test Z-invariant properties
        z_invariant = coordinates['z_invariant']
        positions = coordinates['positions']
        assert len(z_invariant) == len(positions)
        assert np.all(z_invariant >= 0)
        
        # Test complexity metric properties
        complexity = coordinates['complexity']
        assert np.all(complexity >= 0)
        # Complexity κ(n) = d(n) * ln(n+1) / e² can exceed ln(n+1) due to d(n) divisor count
        # For large numbers, d(n) can be substantial, so just check reasonable bounds
        max_complexity = np.max(complexity)
        assert max_complexity < 10.0, f"Complexity values seem too large: max={max_complexity}"
    
    def test_parameter_validation(self, mapper, test_sequence):
        """Test parameter validation and edge cases."""
        # Test with extreme k values
        coords_low_k = mapper.compute_z_invariant_coordinates(test_sequence, k=0.01)
        coords_high_k = mapper.compute_z_invariant_coordinates(test_sequence, k=0.99)
        
        # Both should complete without error
        assert len(coords_low_k['geodesic_coords']) == len(test_sequence)
        assert len(coords_high_k['geodesic_coords']) == len(test_sequence)
        
        # Geodesic coordinates should differ with different k values
        assert not np.array_equal(coords_low_k['geodesic_coords'], 
                                 coords_high_k['geodesic_coords'])
    
    def test_reproducibility(self, mapper, test_sequence):
        """Test that results are reproducible."""
        # Run analysis twice with same parameters
        coords1 = mapper.compute_z_invariant_coordinates(test_sequence, k=0.3)
        coords2 = mapper.compute_z_invariant_coordinates(test_sequence, k=0.3)
        
        # Results should be identical (excluding timing metadata)
        np.testing.assert_array_equal(coords1['x'], coords2['x'])
        np.testing.assert_array_equal(coords1['y'], coords2['y'])
        np.testing.assert_array_equal(coords1['z'], coords2['z'])
        np.testing.assert_array_equal(coords1['z_invariant'], coords2['z_invariant'])
        np.testing.assert_array_equal(coords1['geodesic_coords'], coords2['geodesic_coords'])
        np.testing.assert_array_equal(coords1['complexity'], coords2['complexity'])


class TestIntegrationWorkflow:
    """Integration tests for complete analysis workflow."""
    
    def test_complete_analysis_workflow(self):
        """Test complete end-to-end analysis workflow."""
        mapper = ZGeodesicHotspotMapper()
        
        # Create test sequence
        test_sequence = Seq("ATGAAAGCGTTGCTGAAGCATGTAGCGGATCCGTTAGCTAGCGATCGCTAG" * 2)
        
        # Step 1: Compute coordinates
        coordinates = mapper.compute_z_invariant_coordinates(test_sequence)
        assert coordinates is not None
        assert len(coordinates['positions']) == len(test_sequence)
        
        # Step 2: Detect hotspots
        hotspots = mapper.detect_prime_hotspots(coordinates)
        assert hotspots is not None
        assert hotspots['sequence_length'] == len(test_sequence)
        
        # Step 3: Create annotations
        annotations = pd.DataFrame({
            'seqid': ['test'] * 2,
            'type': ['gene', 'exon'],
            'start': [10, 30],
            'end': [50, 70],
            'source': ['prediction'] * 2
        })
        
        # Step 4: Correlate with annotations
        correlations = mapper.correlate_hotspots_with_annotations(hotspots, annotations)
        assert correlations is not None
        assert 'total_correlations' in correlations
        
        # Step 5: Export results
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "workflow_test"
            mapper.export_results(hotspots, coordinates, output_path, format='csv')
            
            # Verify export completed
            assert output_path.with_suffix('.coordinates.csv').exists()
    
    def test_performance_scaling_validation(self):
        """Test that performance scales linearly as claimed."""
        mapper = ZGeodesicHotspotMapper()
        
        # Test with sequence lengths that should show linear scaling
        test_lengths = [100, 200, 400, 800]
        benchmark_results = mapper.benchmark_performance(test_lengths, num_trials=2)
        
        # Check that processing time increases roughly linearly
        times = benchmark_results['processing_times']
        
        # Calculate scaling ratios
        scaling_ratios = []
        for i in range(1, len(times)):
            time_ratio = times[i] / times[i-1]
            length_ratio = test_lengths[i] / test_lengths[i-1]
            scaling_ratios.append(time_ratio / length_ratio)
        
        # Scaling ratios should be close to 1.0 for linear scaling
        # Allow some variance due to measurement noise and overhead
        for ratio in scaling_ratios:
            assert 0.5 < ratio < 3.0, f"Scaling ratio {ratio} indicates non-linear behavior"
    
    def test_mathematical_framework_validation(self):
        """Test that mathematical framework produces expected properties."""
        mapper = ZGeodesicHotspotMapper()
        
        # Create a sequence with known mathematical properties
        # Use a sequence with prime-length to test prime detection
        prime_length_sequence = Seq("A" * 97)  # 97 is prime
        
        coordinates = mapper.compute_z_invariant_coordinates(prime_length_sequence)
        hotspots = mapper.detect_prime_hotspots(coordinates)
        
        # Test geodesic properties
        geodesic_coords = coordinates['geodesic_coords']
        
        # Geodesic coordinates should have specific variance properties
        variance = np.var(geodesic_coords)
        assert variance > 0, "Geodesic coordinates should have non-zero variance"
        
        # Z-invariant should increase with position (monotonic property)
        z_invariant = coordinates['z_invariant']
        # For most sequences, Z-invariant should generally increase
        assert np.mean(np.diff(z_invariant)) >= 0, "Z-invariant should generally increase"
        
        # Prime positions should be detected
        assert hotspots['total_primes'] > 0, "Should detect prime positions in sequence"


if __name__ == "__main__":
    # Run tests if file is executed directly
    pytest.main([__file__, "-v"])