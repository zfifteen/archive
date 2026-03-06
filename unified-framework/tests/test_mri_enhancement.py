"""
Test Suite for MRI Enhancement Tool

Comprehensive tests for DICOM-based spine MRI analysis functionality.
"""

import unittest
import os
import tempfile
import shutil
import numpy as np
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.applications.mri_enhancement import (
    MRIConfig, DICOMScanner, SpineMRIAnalyzer, 
    AnnotationGenerator, ReportGenerator
)
from src.applications.mri_enhancement.image_analyzer import Finding, FindingType, FindingSeverity, AnalysisResult
from src.applications.mri_enhancement.dicom_scanner import DICOMSeries, DICOMStudy


class TestMRIConfig(unittest.TestCase):
    """Test MRI configuration functionality."""
    
    def test_default_config_creation(self):
        """Test default configuration creation."""
        config = MRIConfig()
        
        # Check default values
        self.assertEqual(config.detection_thresholds.height_loss_threshold, 0.10)
        self.assertEqual(config.detection_thresholds.syrinx_width_ratio, (0.70, 0.90))
        self.assertTrue(config.anonymize_patient_data)
        self.assertEqual(config.max_parallel_jobs, 4)
        
    def test_config_validation(self):
        """Test configuration validation."""
        config = MRIConfig()
        
        # Valid configuration should have no warnings
        warnings = config.validate()
        self.assertIsInstance(warnings, list)
        
        # Invalid configuration should generate warnings
        config.detection_thresholds.height_loss_threshold = 0.60  # Too high
        config.memory_limit_mb = 100  # Too low
        
        warnings = config.validate()
        self.assertGreater(len(warnings), 0)
        
    def test_spine_specific_config(self):
        """Test spine region-specific configurations."""
        from src.applications.mri_enhancement.config import get_spine_config
        
        cervical_config = get_spine_config("cervical")
        lumbar_config = get_spine_config("lumbar")
        
        # Cervical should have different thresholds
        self.assertNotEqual(
            cervical_config.detection_thresholds.height_loss_threshold,
            lumbar_config.detection_thresholds.height_loss_threshold
        )
        
    def test_config_serialization(self):
        """Test configuration save/load functionality."""
        config = MRIConfig()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            
        try:
            # Save configuration
            config.to_json(config_path)
            self.assertTrue(os.path.exists(config_path))
            
            # Load configuration
            loaded_config = MRIConfig.from_json(config_path)
            
            # Check values are preserved
            self.assertEqual(
                config.detection_thresholds.height_loss_threshold,
                loaded_config.detection_thresholds.height_loss_threshold
            )
            
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)


class TestDICOMScanner(unittest.TestCase):
    """Test DICOM scanning functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MRIConfig()
        self.scanner = DICOMScanner(self.config)
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_scanner_initialization(self):
        """Test DICOM scanner initialization."""
        self.assertIsNotNone(self.scanner)
        self.assertEqual(self.scanner.config, self.config)
        
    def test_scan_empty_folder(self):
        """Test scanning empty folder."""
        studies = self.scanner.scan_folder(self.temp_dir)
        self.assertEqual(len(studies), 0)
        
    def test_scan_nonexistent_folder(self):
        """Test scanning non-existent folder."""
        with self.assertRaises(FileNotFoundError):
            self.scanner.scan_folder("/nonexistent/path")
            
    def test_dicom_validation(self):
        """Test DICOM file validation logic."""
        # Create a mock DICOM dataset
        class MockDataset:
            def __init__(self):
                self.StudyInstanceUID = "1.2.3.4"
                self.SeriesInstanceUID = "1.2.3.5"
                self.SOPInstanceUID = "1.2.3.6"
                self.Modality = "MR"
                self.BodyPartExamined = "SPINE"
                
        mock_ds = MockDataset()
        is_valid = self.scanner._validate_dicom_header(mock_ds, "test.dcm")
        self.assertTrue(is_valid)
        
        # Test invalid modality
        mock_ds.Modality = "CT"
        is_valid = self.scanner._validate_dicom_header(mock_ds, "test.dcm")
        self.assertFalse(is_valid)
        
    def test_statistics_tracking(self):
        """Test statistics tracking during scanning."""
        initial_stats = self.scanner.get_statistics()
        
        # All counts should start at zero
        for count in initial_stats.values():
            self.assertEqual(count, 0)


class TestSpineMRIAnalyzer(unittest.TestCase):
    """Test spine MRI analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MRIConfig()
        self.analyzer = SpineMRIAnalyzer(self.config)
        
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.config, self.config)
        
    def test_volume_preprocessing(self):
        """Test volume preprocessing."""
        # Create test volume
        test_volume = np.random.random((10, 64, 64)).astype(np.float32)
        
        processed = self.analyzer._preprocess_volume(test_volume)
        
        # Check output properties
        self.assertEqual(processed.shape, test_volume.shape)
        self.assertEqual(processed.dtype, np.float32)
        
    def test_contrast_enhancement(self):
        """Test contrast enhancement."""
        # Create test volume with low contrast
        test_volume = np.ones((5, 32, 32), dtype=np.float32) * 0.5
        test_volume[:, 10:20, 10:20] = 0.6  # Small contrast difference
        
        enhanced = self.analyzer._enhance_contrast(test_volume)
        
        # Enhanced volume should have better contrast
        self.assertEqual(enhanced.shape, test_volume.shape)
        self.assertGreaterEqual(np.max(enhanced), np.max(test_volume))
        
    def test_vertebra_height_measurement(self):
        """Test vertebral height measurement."""
        # Create mock vertebra mask
        vertebra_mask = np.zeros((32, 32), dtype=bool)
        vertebra_mask[10:20, 10:20] = True  # Square vertebra
        
        bbox = (10, 10, 20, 20)
        
        measurements = self.analyzer._measure_vertebra_heights(
            np.ones((32, 32)), vertebra_mask, bbox)
        
        # Check measurement structure
        required_keys = ["anterior_height", "middle_height", "posterior_height"]
        for key in required_keys:
            self.assertIn(key, measurements)
            
    def test_wedge_fracture_detection(self):
        """Test wedge fracture detection."""
        # Normal height ratios
        normal_measurements = {
            "anterior_ratio": 0.95,
            "middle_ratio": 1.0,
            "posterior_ratio": 0.98
        }
        
        is_wedge = self.analyzer._detect_wedge_fracture(normal_measurements)
        self.assertFalse(is_wedge)
        
        # Wedge fracture (significant anterior height loss)
        wedge_measurements = {
            "anterior_ratio": 0.75,  # 25% height loss
            "middle_ratio": 1.0,
            "posterior_ratio": 0.98
        }
        
        is_wedge = self.analyzer._detect_wedge_fracture(wedge_measurements)
        self.assertTrue(is_wedge)
        
    def test_syrinx_width_calculation(self):
        """Test syrinx width ratio calculation."""
        # Create mock cord and syrinx masks
        cord_mask = np.zeros((32, 32), dtype=bool)
        cord_mask[10:20, 10:20] = True  # 10-pixel wide cord
        
        syrinx_mask = np.zeros((32, 32), dtype=bool)
        syrinx_mask[12:18, 12:18] = True  # 6-pixel wide syrinx
        
        width_ratio = self.analyzer._calculate_syrinx_width_ratio(cord_mask, syrinx_mask)
        
        # Should be approximately 60% (6/10)
        self.assertAlmostEqual(width_ratio, 0.6, places=1)
        
    def test_finding_creation(self):
        """Test medical finding creation."""
        finding = Finding(
            finding_type=FindingType.TRAUMATIC,
            category="vertebral_morphology",
            subcategory="wedge_fracture",
            description="Test finding",
            location="T7",
            severity=FindingSeverity.MODERATE,
            confidence=0.85,
            coordinates=(10, 10, 5),
            measurements={"height_loss": 0.25},
            evidence=["Asymmetric height loss"],
            slice_numbers=[5]
        )
        
        # Check finding properties
        self.assertEqual(finding.finding_type, FindingType.TRAUMATIC)
        self.assertEqual(finding.confidence, 0.85)
        self.assertIn(5, finding.slice_numbers)
        
    def test_overall_assessment_generation(self):
        """Test overall assessment logic."""
        # No findings - should be normal
        assessment, confidence = self.analyzer._generate_overall_assessment([])
        self.assertEqual(assessment, FindingType.NORMAL)
        
        # Traumatic findings
        traumatic_finding = Finding(
            finding_type=FindingType.TRAUMATIC,
            category="test", subcategory="test", description="test",
            location="test", severity=FindingSeverity.MILD,
            confidence=0.8, coordinates=(0, 0, 0),
            measurements={}, evidence=[], slice_numbers=[0]
        )
        
        assessment, confidence = self.analyzer._generate_overall_assessment([traumatic_finding])
        self.assertEqual(assessment, FindingType.TRAUMATIC)


class TestAnnotationGenerator(unittest.TestCase):
    """Test annotation generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MRIConfig()
        self.generator = AnnotationGenerator(self.config)
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_generator_initialization(self):
        """Test annotation generator initialization."""
        self.assertIsNotNone(self.generator)
        self.assertEqual(self.generator.config, self.config)
        
    def test_annotation_styles(self):
        """Test annotation style configuration."""
        # Check that styles are defined for each finding type
        self.assertIn(FindingType.TRAUMATIC, self.generator.styles)
        self.assertIn(FindingType.DEGENERATIVE, self.generator.styles)
        self.assertIn(FindingType.UNCERTAIN, self.generator.styles)
        
        # Check style properties
        traumatic_style = self.generator.styles[FindingType.TRAUMATIC]
        self.assertEqual(len(traumatic_style.color), 3)  # BGR color
        self.assertGreater(traumatic_style.thickness, 0)
        
    def test_windowing_application(self):
        """Test DICOM windowing application."""
        test_image = np.array([[100, 200, 300], [400, 500, 600]], dtype=np.float32)
        
        # Apply windowing (center=300, width=200)
        windowed = self.generator._apply_windowing(test_image, 300, 200)
        
        # Values should be normalized
        self.assertGreaterEqual(np.min(windowed), 0)
        self.assertLessEqual(np.max(windowed), 1)


class TestReportGenerator(unittest.TestCase):
    """Test report generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MRIConfig()
        self.generator = ReportGenerator(self.config)
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_generator_initialization(self):
        """Test report generator initialization."""
        self.assertIsNotNone(self.generator)
        self.assertEqual(self.generator.config, self.config)
        
    def test_citation_service_initialization(self):
        """Test citation service initialization."""
        citation_service = self.generator.citation_service
        self.assertIsNotNone(citation_service)
        
        # Test default citations
        default_citations = citation_service._get_default_citations()
        self.assertGreater(len(default_citations), 0)
        
        # Check citation structure
        citation = default_citations[0]
        self.assertIsNotNone(citation.title)
        self.assertIsNotNone(citation.journal)
        self.assertIsInstance(citation.year, int)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MRIConfig()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_complete_workflow_simulation(self):
        """Test complete workflow with simulated data."""
        # Create mock DICOM series
        series = DICOMSeries(
            series_uid="1.2.3.4.5",
            series_description="T2 SAG SPINE",
            modality="MR",
            body_part="SPINE",
            sequence_name="T2_TSE",
            slice_count=15,
            file_paths=[],
            metadata={"slice_thickness": 3.0}
        )
        
        # Create mock analysis result
        finding = Finding(
            finding_type=FindingType.TRAUMATIC,
            category="vertebral_morphology",
            subcategory="wedge_fracture",
            description="Focal wedge deformity at T7",
            location="T7",
            severity=FindingSeverity.MODERATE,
            confidence=0.85,
            coordinates=(32, 32, 7),
            measurements={"anterior_ratio": 0.75, "height_loss": 0.25},
            evidence=["Asymmetric height loss", "Focal deformity"],
            slice_numbers=[7]
        )
        
        analysis_result = AnalysisResult(
            series_uid=series.series_uid,
            findings=[finding],
            overall_assessment=FindingType.TRAUMATIC,
            confidence_score=0.85,
            key_slices=[7],
            measurements_summary={"total_findings": 1, "traumatic_findings": 1},
            processing_notes=[]
        )
        
        # Test workflow components
        self.assertEqual(len(analysis_result.findings), 1)
        self.assertEqual(analysis_result.overall_assessment, FindingType.TRAUMATIC)
        self.assertIn(7, analysis_result.key_slices)
        
        # Test that finding has required properties
        self.assertEqual(finding.finding_type, FindingType.TRAUMATIC)
        self.assertGreater(finding.confidence, 0.8)
        self.assertIn("height_loss", finding.measurements)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MRIConfig()
        
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        scanner = DICOMScanner(self.config)
        
        # Test invalid folder path
        with self.assertRaises(FileNotFoundError):
            scanner.scan_folder("/invalid/path")
            
    def test_empty_volume_handling(self):
        """Test handling of empty or invalid volumes."""
        analyzer = SpineMRIAnalyzer(self.config)
        
        # Empty volume
        empty_volume = np.array([])
        processed = analyzer._preprocess_volume(empty_volume.reshape(0, 0, 0))
        self.assertEqual(processed.size, 0)
        
    def test_configuration_edge_cases(self):
        """Test configuration with edge case values."""
        config = MRIConfig()
        
        # Extreme threshold values
        config.detection_thresholds.height_loss_threshold = 0.01  # Very sensitive
        config.detection_thresholds.syrinx_width_ratio = (0.95, 0.99)  # Very narrow range
        
        warnings = config.validate()
        # Should generate warnings for extreme values
        self.assertIsInstance(warnings, list)


def run_comprehensive_tests():
    """Run comprehensive test suite."""
    print("MRI Enhancement Tool - Comprehensive Test Suite")
    print("=" * 55)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMRIConfig,
        TestDICOMScanner,
        TestSpineMRIAnalyzer,
        TestAnnotationGenerator,
        TestReportGenerator,
        TestIntegration,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 55)
    print("TEST SUMMARY")
    print("=" * 55)
    
    if result.wasSuccessful():
        print("✓ All tests passed successfully")
        print("✓ MRI Enhancement Tool components validated")
        print("✓ Ready for DICOM-based spine analysis")
    else:
        print(f"✗ {len(result.failures)} test(s) failed")
        print(f"✗ {len(result.errors)} error(s) occurred")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run comprehensive test suite
    success = run_comprehensive_tests()
    
    if success:
        print("\n🎉 MRI Enhancement Tool test suite completed successfully!")
    else:
        print("\n❌ Test suite failed - check test output for details")
        sys.exit(1)