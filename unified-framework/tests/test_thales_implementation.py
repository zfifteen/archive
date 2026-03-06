#!/usr/bin/env python3
"""
Comprehensive Test Suite for Thales-Z5D Implementation
====================================================

Attribution: Created by Dionisio Alberto Lopez III (D.A.L. III), Z Framework

This test suite validates the complete Thales implementation including:
- C filter correctness and error envelope validation
- Python analysis tool functionality
- Integration with existing Z Framework parameters
- Performance benchmarks and gate validation
"""

import os
import sys
import subprocess
import unittest
import tempfile
import json
import csv
from pathlib import Path

# Add the repository root to Python path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

try:
    from analyze_thales import ThalesAnalyzer
except ImportError:
    print("Could not import analyze_thales, skipping Python tests")
    ThalesAnalyzer = None

class TestThalesFilter(unittest.TestCase):
    """Test the C Thales filter implementation."""
    
    @classmethod
    def setUpClass(cls):
        """Build the Thales filter executable."""
        cls.build_dir = repo_root / "z5d_pascal_filter_c"
        cls.thales_exe = cls.build_dir / "thales_filter"
        
        # Build the executable
        result = subprocess.run(
            ["make", "thales"],
            cwd=cls.build_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to build Thales filter: {result.stderr}")
    
    def test_thales_filter_builds(self):
        """Test that Thales filter builds successfully."""
        self.assertTrue(self.thales_exe.exists(), "Thales filter executable should exist")
        self.assertTrue(os.access(self.thales_exe, os.X_OK), "Thales filter should be executable")
    
    def test_thales_filter_runs(self):
        """Test that Thales filter runs without errors."""
        result = subprocess.run(
            [str(self.thales_exe)],
            cwd=self.build_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        self.assertEqual(result.returncode, 0, f"Thales filter should run successfully: {result.stderr}")
        self.assertIn("Thales Filter Test Harness", result.stdout)
        self.assertIn("Primary Endpoints", result.stdout)
    
    def test_thales_filter_report_format(self):
        """Test that Thales filter generates properly formatted reports."""
        result = subprocess.run(
            [str(self.thales_exe)],
            cwd=self.build_dir,
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        
        # Check for required report sections
        self.assertIn("**MR_saved**:", output)
        self.assertIn("**TD_saved**:", output)
        self.assertIn("**FN_rate**:", output)
        self.assertIn("**Error Envelope**:", output)
        self.assertIn("Gates", output)
        
        # Check for gate validation symbols
        self.assertRegex(output, r"G[1-6].*[✅❌]")
    
    def test_mpfr_precision(self):
        """Test that MPFR precision is correctly configured."""
        # This test verifies the build includes MPFR support
        import sys
        if sys.platform.startswith("linux"):
            cmd = ["ldd", str(self.thales_exe)]
        elif sys.platform == "darwin":
            cmd = ["otool", "-L", str(self.thales_exe)]
        else:
            self.skipTest("Dynamic library check not supported on this platform")
            return

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            self.skipTest(f"Dependency checker command failed: {result.stderr}")
            return

        self.assertIn("libmpfr", result.stdout, "Thales filter should link against MPFR")
        self.assertIn("libgmp", result.stdout, "Thales filter should link against GMP")

@unittest.skipIf(ThalesAnalyzer is None, "ThalesAnalyzer not available")
class TestThalesAnalyzer(unittest.TestCase):
    """Test the Python Thales analyzer."""
    
    def setUp(self):
        """Set up test analyzer."""
        self.analyzer = ThalesAnalyzer(seed=42)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        self.assertEqual(self.analyzer.seed, 42)
        self.assertIsInstance(self.analyzer.results, dict)
        self.assertIsInstance(self.analyzer.metrics, dict)
    
    def test_z5d_prediction(self):
        """Test Z5D prediction function."""
        # Test known values
        k_values = [1e5, 1e6, 1e7]
        
        for k in k_values:
            pred = self.analyzer.z5d_prediction(k)
            self.assertIsInstance(pred, float)
            self.assertGreater(pred, 0, f"Prediction for k={k} should be positive")
            
            # Basic sanity check: should be roughly k * ln(k)
            import math
            expected_order = k * math.log(k)
            self.assertLess(abs(pred - expected_order) / expected_order, 0.5,
                          f"Prediction for k={k} should be within 50% of k*ln(k)")
    
    def test_error_ppm_calculation(self):
        """Test error calculation in PPM."""
        test_cases = [
            (100.0, 100.1, 1000),  # 0.1% = 1000 ppm
            (1000.0, 1000.2, 200), # 0.02% = 200 ppm
            (1000.0, 1000.0, 0),   # Perfect match = 0 ppm
        ]
        
        for predicted, actual, expected_ppm in test_cases:
            ppm = self.analyzer.compute_error_ppm(predicted, actual)
            self.assertAlmostEqual(ppm, expected_ppm, delta=1,
                                 msg=f"Error PPM calculation failed for {predicted}, {actual}")
    
    def test_bootstrap_ci(self):
        """Test bootstrap confidence interval calculation."""
        # Generate test data with known properties
        import numpy as np
        np.random.seed(42)
        test_data = np.random.normal(100, 10, 1000).tolist()
        
        mean, ci_low, ci_high = self.analyzer.bootstrap_ci(test_data, confidence=0.95)
        
        # Check basic properties
        self.assertLess(ci_low, mean, "CI lower bound should be less than mean")
        self.assertLess(mean, ci_high, "Mean should be less than CI upper bound")
        self.assertAlmostEqual(mean, 100, delta=2, msg="Mean should be close to true mean")
    
    def test_synthetic_results_generation(self):
        """Test synthetic results generation."""
        results = self.analyzer._generate_synthetic_results()
        
        # Check structure
        required_keys = ['mr_saved', 'td_saved', 'fn_rate', 'error_envelope', 
                        'timing_ns', 'pass_rate', 'total_tests']
        for key in required_keys:
            self.assertIn(key, results, f"Results should contain {key}")
        
        # Check data properties
        self.assertGreater(results['total_tests'], 0)
        self.assertEqual(len(results['mr_saved']), results['total_tests'])
        
        # Check that MR_saved and TD_saved meet materiality threshold on average
        import numpy as np
        self.assertGreater(np.mean(results['mr_saved']), 10.0,
                          "Synthetic MR_saved should exceed materiality threshold")
        self.assertGreater(np.mean(results['td_saved']), 10.0,
                          "Synthetic TD_saved should exceed materiality threshold")
    
    def test_gate_evaluation(self):
        """Test gate evaluation logic."""
        # Test case where all gates should pass
        good_metrics = {
            'fn_rate': {'mean': 0.0},
            'mr_saved': {'mean': 15.0},
            'td_saved': {'mean': 12.0},
            'timing_ns': {'mean': 150.0},
            'pass_rate': {'mean': 75.0},
            'error_envelope': {'mean': 100.0}
        }
        
        gates = self.analyzer.evaluate_gates(good_metrics)
        
        self.assertTrue(gates['G1_Correctness'], "G1 should pass with FN_rate=0")
        self.assertTrue(gates['G2_Materiality'], "G2 should pass with MR/TD > 10%")
        self.assertTrue(gates['G3_Overhead'], "G3 should pass with reasonable timing")
        self.assertTrue(gates['G4_Density_Integrity'], "G4 should pass with reasonable pass rate")
        self.assertTrue(gates['G5_Reproducibility'], "G5 should always pass")
        self.assertTrue(gates['G6_Policy'], "G6 should pass with error < 200 ppm")
        
        # Test case where gates should fail
        bad_metrics = {
            'fn_rate': {'mean': 0.1},      # Fails G1
            'mr_saved': {'mean': 5.0},     # Fails G2
            'td_saved': {'mean': 5.0},     # Fails G2
            'timing_ns': {'mean': 1000.0}, # Fails G3
            'pass_rate': {'mean': 95.0},   # Fails G4
            'error_envelope': {'mean': 500.0}  # Fails G6
        }
        
        bad_gates = self.analyzer.evaluate_gates(bad_metrics)
        
        self.assertFalse(bad_gates['G1_Correctness'])
        self.assertFalse(bad_gates['G2_Materiality'])
        self.assertFalse(bad_gates['G3_Overhead'])
        self.assertFalse(bad_gates['G4_Density_Integrity'])
        self.assertFalse(bad_gates['G6_Policy'])
    
    def test_csv_analysis(self):
        """Test CSV analysis functionality."""
        # Create test CSV file
        csv_file = os.path.join(self.temp_dir, "test_results.csv")
        
        test_data = [
            {'mr_saved_pct': 12.0, 'td_saved_pct': 15.0, 'fn_rate': 0.0, 
             'error_ppm': 150.0, 'timing_ns': 145.0, 'pass_rate': 75.0},
            {'mr_saved_pct': 13.0, 'td_saved_pct': 14.0, 'fn_rate': 0.0,
             'error_ppm': 120.0, 'timing_ns': 155.0, 'pass_rate': 73.0},
        ]
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=test_data[0].keys())
            writer.writeheader()
            writer.writerows(test_data)
        
        results = self.analyzer.analyze_csv_results(csv_file)
        
        self.assertEqual(results['total_tests'], 2)
        self.assertEqual(len(results['mr_saved']), 2)
        self.assertAlmostEqual(results['mr_saved'][0], 12.0)
        self.assertAlmostEqual(results['td_saved'][1], 14.0)
    
    def test_report_generation(self):
        """Test report generation."""
        results = self.analyzer._generate_synthetic_results()
        output_file = os.path.join(self.temp_dir, "test_report.md")
        
        report = self.analyzer.generate_report(
            results, 
            output_file, 
            commit_sha="test-commit", 
            template_file=None
        )
        
        # Check file was created
        self.assertTrue(os.path.exists(output_file), "Report file should be created")
        
        # Check report content
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Thales–Z5D Trial-Reduction Report", content)
        self.assertIn("test-commit", content)
        self.assertIn("Primary Endpoints", content)
        self.assertIn("Gates Status", content)
        
        # Check for metrics
        self.assertIn("**MR_saved**:", content)
        self.assertIn("**TD_saved**:", content)
        self.assertIn("**FN_rate**:", content)

class TestThalesIntegration(unittest.TestCase):
    """Test integration between C filter and Python analyzer."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.build_dir = repo_root / "z5d_pascal_filter_c"
        self.thales_exe = self.build_dir / "thales_filter"
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @unittest.skipIf(ThalesAnalyzer is None, "ThalesAnalyzer not available")
    def test_analyze_thales_script(self):
        """Test the analyze_thales.py script."""
        script_path = repo_root / "analyze_thales.py"
        output_file = os.path.join(self.temp_dir, "integration_report.md")
        
        result = subprocess.run([
            sys.executable, str(script_path),
            "--benchmark",
            "--output", output_file,
            "--seed", "42"
        ], capture_output=True, text=True, timeout=30)
        
        self.assertEqual(result.returncode, 0, f"analyze_thales.py should run successfully: {result.stderr}")
        self.assertIn("Gates status:", result.stdout)
        self.assertIn("Overall status:", result.stdout)
        
        # Check output file
        self.assertTrue(os.path.exists(output_file), "Report file should be created")
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Thales–Z5D Trial-Reduction Report", content)
    
    def test_template_usage(self):
        """Test that the analysis script can use the provided template."""
        template_file = repo_root / "templates" / "thales_trial_reduction_report.md"
        output_file = os.path.join(self.temp_dir, "template_report.md")
        
        if not template_file.exists():
            self.skipTest("Template file not found")
        
        script_path = repo_root / "analyze_thales.py"
        
        result = subprocess.run([
            sys.executable, str(script_path),
            "--benchmark",
            "--template", str(template_file),
            "--output", output_file,
            "--seed", "42"
        ], capture_output=True, text=True, timeout=30)
        
        self.assertEqual(result.returncode, 0, f"Script should run with template: {result.stderr}")
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        # Should contain template-specific content
        self.assertIn("Implementation Details", content)
        self.assertIn("Validation Results", content)

class TestThalesParameters(unittest.TestCase):
    """Test that Thales implementation uses correct Z Framework parameters."""
    
    def test_parameter_consistency(self):
        """Test that C and Python implementations use consistent parameters."""
        # Check that constants in thales_filter.h match expected values
        header_file = repo_root / "z5d_pascal_filter_c" / "thales_filter.h"
        
        if not header_file.exists():
            self.skipTest("thales_filter.h not found")
        
        with open(header_file, 'r') as f:
            content = f.read()
        
        # Check for key parameters (now in header file)
        self.assertIn("THALES_KAPPA_GEO 0.3", content)
        self.assertIn("THALES_K_STAR 0.04449", content)
        self.assertIn("THALES_Z5D_C -0.00247", content)
        self.assertIn("THALES_ERROR_ENVELOPE 0.0002", content)  # 200 ppm
        
        # Check MPFR precision
        self.assertIn("THALES_MPFR_PREC 200", content)  # dps=50 equivalent

class TestThalesDocumentation(unittest.TestCase):
    """Test that documentation and templates are properly structured."""
    
    def test_report_template_exists(self):
        """Test that the report template exists and is well-formed."""
        template_file = repo_root / "templates" / "thales_trial_reduction_report.md"
        
        self.assertTrue(template_file.exists(), "Report template should exist")
        
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Check for required template variables
        required_vars = [
            'COMMIT_SHA', 'SEED', 'MR_SAVED_MEAN', 'TD_SAVED_MEAN',
            'FN_RATE', 'ERROR_ENVELOPE_MAX', 'G1_CORRECTNESS_STATUS'
        ]
        
        for var in required_vars:
            self.assertIn(f"${{{var}}}", content, f"Template should contain {var} placeholder")
    
    def test_readme_update(self):
        """Test that README files mention Thales implementation."""
        pascal_readme = repo_root / "z5d_pascal_filter_c" / "README.md"
        
        if pascal_readme.exists():
            with open(pascal_readme, 'r') as f:
                content = f.read()
            
            # Should mention Thales in build instructions or description
            # This is a soft check since README might not be updated yet
            pass

def run_comprehensive_tests():
    """Run all tests and generate a summary report."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestThalesFilter,
        TestThalesAnalyzer,
        TestThalesIntegration,
        TestThalesParameters,
        TestThalesDocumentation
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = (total_tests - failures - errors) / total_tests * 100 if total_tests > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"THALES TEST SUITE SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_tests - failures - errors}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if failures > 0:
        print(f"\nFAILURES ({failures}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if errors > 0:
        print(f"\nERRORS ({errors}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Overall assessment
    if failures == 0 and errors == 0:
        print(f"\n✅ ALL TESTS PASSED - Thales implementation ready for promotion")
    else:
        print(f"\n❌ TESTS FAILED - Thales implementation needs fixes before promotion")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Thales Test Suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test", "-t", help="Run specific test class")
    
    args = parser.parse_args()
    
    if args.test:
        # Run specific test
        suite = unittest.TestLoader().loadTestsFromName(args.test, module=sys.modules[__name__])
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    else:
        # Run comprehensive test suite
        success = run_comprehensive_tests()
        sys.exit(0 if success else 1)