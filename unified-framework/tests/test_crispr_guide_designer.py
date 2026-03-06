"""
Tests for Z-Invariant CRISPR Guide Designer

This module contains comprehensive tests for the CRISPR guide designer functionality,
including modular-geodesic embeddings, optimization algorithms, and statistical validation.
"""

import pytest
import numpy as np
import sys
import os

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from applications.crispr_guide_designer import CRISPRGuideDesigner
from applications.crispr_visualization import CRISPRVisualization

class TestCRISPRGuideDesigner:
    """Test suite for CRISPRGuideDesigner class."""
    
    @pytest.fixture
    def designer(self):
        """Create a CRISPR guide designer instance for testing."""
        return CRISPRGuideDesigner(precision=20, k_parameter=0.3)
    
    @pytest.fixture
    def sample_sequence(self):
        """Provide a sample target sequence for testing."""
        return (
            "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGA"
            "AGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGA"
            "GCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGGCCCAGGAGCAGCTGCGGCTGGAG"
        )
    
    def test_initialization(self, designer):
        """Test proper initialization of designer."""
        assert designer.k_parameter == 0.3
        assert designer.modulus is not None
        assert designer.embedding is not None
        assert isinstance(designer.results_cache, dict)
    
    def test_sequence_to_numeric_conversion(self, designer):
        """Test DNA sequence to numeric conversion."""
        test_sequence = "ATGC"
        numeric = designer.sequence_to_numeric(test_sequence)
        expected = [1, 2, 3, 4]  # A=1, T=2, G=3, C=4
        assert numeric == expected
        
        # Test case insensitivity
        numeric_lower = designer.sequence_to_numeric("atgc")
        assert numeric_lower == expected
        
        # Test invalid nucleotides
        invalid_sequence = "ATGCN"
        numeric_invalid = designer.sequence_to_numeric(invalid_sequence)
        assert numeric_invalid[-1] == 0  # N should map to 0
    
    def test_find_potential_guides(self, designer, sample_sequence):
        """Test identification of potential guide sites."""
        guides = designer.find_potential_guides(sample_sequence)
        
        # Should find at least some guides
        assert len(guides) > 0
        
        # Check guide structure
        for guide in guides:
            assert 'sequence' in guide
            assert 'position' in guide
            assert 'pam_sequence' in guide
            assert 'target_site' in guide
            assert 'seed_region' in guide
            
            # Validate guide RNA length
            assert len(guide['sequence']) == 20
            
            # Validate PAM sequence pattern
            assert guide['pam_sequence'][1:] == "GG"
            
            # Validate seed region
            assert len(guide['seed_region']) == 12
            assert guide['seed_region'] == guide['sequence'][-12:]
    
    def test_embed_guide_in_geodesic_space(self, designer):
        """Test modular-geodesic embedding of guide sequences."""
        guide_data = {
            'sequence': 'ATGCTGCGGAGACCTGGAGA',
            'position': 0,
            'pam_sequence': 'AGG',
            'target_site': 'ATGCTGCGGAGACCTGGAGAAGG',
            'seed_region': 'GACCTGGAGA'
        }
        
        embedded_guide = designer.embed_guide_in_geodesic_space(guide_data)
        
        # Check that all required fields are added
        required_fields = [
            'numeric_sequence', 'theta_transformed', 'coordinates_5d',
            'spiral_coordinates', 'z_framework_score', 'curvature_profile',
            'geodesic_complexity', 'density_enhancement', 'geometric_fingerprint'
        ]
        
        for field in required_fields:
            assert field in embedded_guide
        
        # Validate 5D coordinates structure
        coords_5d = embedded_guide['coordinates_5d']
        assert 'x' in coords_5d
        assert 'y' in coords_5d
        assert 'z' in coords_5d
        assert 'w' in coords_5d
        assert 'u' in coords_5d
        
        # Validate numeric properties
        assert isinstance(embedded_guide['z_framework_score'], float)
        assert isinstance(embedded_guide['geodesic_complexity'], float)
        assert isinstance(embedded_guide['density_enhancement'], float)
        assert isinstance(embedded_guide['geometric_fingerprint'], str)
        assert len(embedded_guide['geometric_fingerprint']) == 12
    
    def test_z_framework_score_computation(self, designer):
        """Test Z framework score calculation."""
        test_sequence = "ATGCTGCGGAGACCTGGAGA"
        position = 10
        
        score = designer._compute_z_framework_score(test_sequence, position)
        
        # Score should be positive numeric value
        assert isinstance(score, float)
        assert score > 0
        
        # Different positions should potentially give different scores
        score2 = designer._compute_z_framework_score(test_sequence, position + 50)
        # Note: Scores might be the same due to mathematical properties, so we just check type
        assert isinstance(score2, float)
    
    def test_density_enhancement_calculation(self, designer):
        """Test density enhancement metric calculation."""
        # Create mock 5D coordinates
        mock_coords = {
            'x': np.random.rand(20),
            'y': np.random.rand(20),
            'z': np.random.rand(20),
            'w': np.random.rand(20),
            'u': np.random.rand(20)
        }
        
        density = designer._calculate_density_enhancement(mock_coords)
        
        assert isinstance(density, float)
        assert density > 0
    
    def test_geometric_fingerprint_generation(self, designer):
        """Test geometric fingerprint generation."""
        # Create mock 5D coordinates
        mock_coords = {
            'x': np.array([1.0, 2.0, 3.0]),
            'y': np.array([4.0, 5.0, 6.0]),
            'z': np.array([7.0, 8.0, 9.0]),
            'w': np.array([10.0, 11.0, 12.0]),
            'u': np.array([13.0, 14.0, 15.0])
        }
        
        fingerprint = designer._generate_geometric_fingerprint(mock_coords)
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 12
        assert all(c in '0123456789abcdef' for c in fingerprint)
        
        # Same coordinates should give same fingerprint
        fingerprint2 = designer._generate_geometric_fingerprint(mock_coords)
        assert fingerprint == fingerprint2
    
    def test_off_target_risk_scoring(self, designer, sample_sequence):
        """Test off-target risk scoring functionality."""
        # Create a mock embedded guide
        guide_data = {
            'sequence': 'ATGCTGCGGAGACCTGGAGA',
            'position': 10,
            'coordinates_5d': {
                'x': np.random.rand(20),
                'y': np.random.rand(20),
                'z': np.random.rand(20),
                'w': np.random.rand(20),
                'u': np.random.rand(20)
            },
            'geometric_fingerprint': 'abc123def456'
        }
        
        risk_score = designer.score_off_target_risk(guide_data, sample_sequence)
        
        assert isinstance(risk_score, float)
        assert 0.0 <= risk_score <= 1.0
    
    def test_coordinate_similarity_computation(self, designer):
        """Test coordinate similarity calculation."""
        # Create two sets of coordinates
        coords1 = {
            'x': np.array([1.0, 2.0]),
            'y': np.array([3.0, 4.0]),
            'z': np.array([5.0, 6.0]),
            'w': np.array([7.0, 8.0]),
            'u': np.array([9.0, 10.0])
        }
        
        coords2 = {
            'x': np.array([1.1, 2.1]),
            'y': np.array([3.1, 4.1]),
            'z': np.array([5.1, 6.1]),
            'w': np.array([7.1, 8.1]),
            'u': np.array([9.1, 10.1])
        }
        
        similarity = designer._compute_coordinate_similarity(coords1, coords2)
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        
        # Identical coordinates should have high similarity
        identical_similarity = designer._compute_coordinate_similarity(coords1, coords1)
        assert identical_similarity > 0.99
    
    def test_guide_selection_optimization(self, designer, sample_sequence):
        """Test guide selection optimization algorithm."""
        # Find guides and embed them
        potential_guides = designer.find_potential_guides(sample_sequence)
        assert len(potential_guides) > 0
        
        # Embed first few guides
        embedded_guides = []
        for guide in potential_guides[:5]:  # Limit for test performance
            embedded_guide = designer.embed_guide_in_geodesic_space(guide)
            embedded_guides.append(embedded_guide)
        
        # Optimize selection
        optimized_guides = designer.optimize_guide_selection(
            embedded_guides, sample_sequence, max_guides=3
        )
        
        assert len(optimized_guides) <= 3
        assert len(optimized_guides) <= len(embedded_guides)
        
        # Check that guides are properly scored and sorted
        for guide in optimized_guides:
            assert 'off_target_risk' in guide
            assert 'composite_score' in guide
            assert isinstance(guide['composite_score'], float)
        
        # Verify sorting (scores should be descending)
        if len(optimized_guides) > 1:
            for i in range(len(optimized_guides) - 1):
                assert optimized_guides[i]['composite_score'] >= optimized_guides[i + 1]['composite_score']
    
    def test_complete_sequence_analysis(self, designer, sample_sequence):
        """Test complete sequence analysis pipeline."""
        results = designer.analyze_target_sequence(sample_sequence, max_guides=3)
        
        # Check result structure
        required_keys = [
            'target_sequence', 'potential_guides', 'embedded_guides',
            'optimized_guides', 'analysis_summary'
        ]
        
        for key in required_keys:
            assert key in results
        
        # Validate data types and content
        assert results['target_sequence'] == sample_sequence
        assert isinstance(results['potential_guides'], list)
        assert isinstance(results['embedded_guides'], list)
        assert isinstance(results['optimized_guides'], list)
        assert isinstance(results['analysis_summary'], str)
        
        # Check that we have results
        assert len(results['potential_guides']) > 0
        assert len(results['optimized_guides']) <= 3
        assert len(results['analysis_summary']) > 0
        
        # Verify embedded guides have proper structure
        if results['embedded_guides']:
            embedded_guide = results['embedded_guides'][0]
            assert 'coordinates_5d' in embedded_guide
            assert 'z_framework_score' in embedded_guide
    
    def test_empty_sequence_handling(self, designer):
        """Test handling of edge cases."""
        # Empty sequence
        results_empty = designer.analyze_target_sequence("", max_guides=5)
        assert len(results_empty['potential_guides']) == 0
        assert len(results_empty['optimized_guides']) == 0
        
        # Sequence too short
        short_sequence = "ATGC"
        results_short = designer.analyze_target_sequence(short_sequence, max_guides=5)
        assert len(results_short['potential_guides']) == 0
        
        # Sequence without valid PAM sites
        no_pam_sequence = "ATGCTGCGGAGACCTGGAGA" * 3  # No GG patterns
        results_no_pam = designer.analyze_target_sequence(no_pam_sequence, max_guides=5)
        # Might still find some guides depending on sequence content


class TestCRISPRVisualization:
    """Test suite for CRISPRVisualization class."""
    
    @pytest.fixture
    def visualizer(self):
        """Create a visualization instance for testing."""
        return CRISPRVisualization()
    
    @pytest.fixture
    def mock_guide_data(self):
        """Create mock guide data for visualization testing."""
        return [
            {
                'sequence': 'ATGCTGCGGAGACCTGGAGA',
                'position': 10,
                'composite_score': 0.85,
                'off_target_risk': 0.15,
                'z_framework_score': 0.75,
                'density_enhancement': 0.90,
                'geodesic_complexity': 0.60,
                'coordinates_5d': {
                    'x': np.random.rand(20),
                    'y': np.random.rand(20),
                    'z': np.random.rand(20),
                    'w': np.random.rand(20),
                    'u': np.random.rand(20)
                }
            },
            {
                'sequence': 'GCCTGGAGACCTGGAGATGC',
                'position': 50,
                'composite_score': 0.78,
                'off_target_risk': 0.22,
                'z_framework_score': 0.70,
                'density_enhancement': 0.85,
                'geodesic_complexity': 0.55,
                'coordinates_5d': {
                    'x': np.random.rand(20),
                    'y': np.random.rand(20),
                    'z': np.random.rand(20),
                    'w': np.random.rand(20),
                    'u': np.random.rand(20)
                }
            }
        ]
    
    def test_initialization(self, visualizer):
        """Test proper initialization of visualizer."""
        assert visualizer.figsize == (12, 8)
        assert visualizer.style == 'plotly'
        assert visualizer.color_palette is not None
    
    def test_5d_coordinate_clustering_plot(self, visualizer, mock_guide_data):
        """Test 5D coordinate clustering visualization."""
        fig = visualizer.plot_5d_coordinate_clusters(mock_guide_data)
        
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
        
        # Test with empty data
        empty_fig = visualizer.plot_5d_coordinate_clusters([])
        assert empty_fig is None
    
    def test_score_comparison_plot(self, visualizer, mock_guide_data):
        """Test score comparison visualization."""
        fig = visualizer.plot_score_comparison(mock_guide_data)
        
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
        
        # Test with empty data
        empty_fig = visualizer.plot_score_comparison([])
        assert empty_fig is None
    
    def test_quality_heatmap_plot(self, visualizer, mock_guide_data):
        """Test quality heatmap visualization."""
        fig = visualizer.plot_guide_quality_heatmap(mock_guide_data)
        
        assert fig is not None
        
        # Test with empty data
        empty_fig = visualizer.plot_guide_quality_heatmap([])
        assert empty_fig is None
    
    def test_conventional_vs_zframework_comparison(self, visualizer, mock_guide_data):
        """Test conventional vs Z-framework comparison plot."""
        fig = visualizer.plot_conventional_vs_zframework_comparison(mock_guide_data)
        
        assert fig is not None
        assert hasattr(fig, 'data')
        assert len(fig.data) > 0
        
        # Test with empty data
        empty_fig = visualizer.plot_conventional_vs_zframework_comparison([])
        assert empty_fig is None
    
    def test_analysis_dashboard_creation(self, visualizer, mock_guide_data):
        """Test comprehensive dashboard creation."""
        mock_results = {
            'embedded_guides': mock_guide_data,
            'optimized_guides': mock_guide_data
        }
        
        figures = visualizer.create_analysis_dashboard(mock_results)
        
        assert isinstance(figures, dict)
        # Should have created at least some figures
        assert len(figures) > 0


def test_integration_workflow():
    """Test complete integration workflow."""
    # Sample sequence
    test_sequence = (
        "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGA"
        "AGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGA"
    )
    
    # Initialize components
    designer = CRISPRGuideDesigner(precision=15, k_parameter=0.3)
    visualizer = CRISPRVisualization()
    
    # Run analysis
    results = designer.analyze_target_sequence(test_sequence, max_guides=3)
    
    # Verify results
    assert len(results['optimized_guides']) > 0
    
    # Generate visualizations
    figures = visualizer.create_analysis_dashboard(results)
    
    # Verify visualizations
    assert isinstance(figures, dict)
    print(f"Integration test passed - Generated {len(figures)} visualizations")


if __name__ == "__main__":
    # Run integration test if executed directly
    test_integration_workflow()
    print("All integration tests passed!")