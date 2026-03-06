#!/usr/bin/env python3
"""
Test Runner for Hybrid Prime Identification Enhanced Tests
===========================================================

Runs all tests related to the enhanced hybrid prime identification functionality.
Provides summary of test results and any failures.

Author: Z Framework Team
"""

import unittest
import sys
import os
import warnings
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Suppress system warnings during tests
warnings.filterwarnings("ignore", category=UserWarning)

# Import test modules
from test_hybrid_prime_changes import TestKeyChanges, TestPerformanceAndEdgeCases
from test_hybrid_prime_integration import (
    TestDataFrameIntegration, 
    TestPerformanceOptimizations,
    TestErrorHandlingAndEdgeCases,
    TestMetricsAndDiagnostics
)


def run_test_suite():
    """Run comprehensive test suite for hybrid prime identification."""
    print("=" * 70)
    print("Enhanced Hybrid Prime Identification - Test Suite")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestKeyChanges,
        TestPerformanceAndEdgeCases,
        TestDataFrameIntegration,
        TestPerformanceOptimizations,
        TestErrorHandlingAndEdgeCases,
        TestMetricsAndDiagnostics
    ]
    
    total_tests = 0
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        total_tests += tests.countTestCases()
    
    print(f"Running {total_tests} tests across {len(test_classes)} test classes...")
    print()
    
    # Run tests
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else 'See details above'}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else 'See details above'}")
    
    print("\n" + "=" * 70)
    
    return result.wasSuccessful()


def run_quick_validation():
    """Run a quick validation test to ensure basic functionality works."""
    print("Running quick validation test...")
    
    try:
        from core.hybrid_prime_identification import hybrid_prime_identification
        
        # Test basic functionality
        result = hybrid_prime_identification(10, log_diagnostics=False)
        
        if result['predicted_prime'] is not None:
            print(f"✅ Quick validation PASSED: Found 10th prime = {result['predicted_prime']}")
            return True
        else:
            print("❌ Quick validation FAILED: No prime found")
            return False
            
    except Exception as e:
        print(f"❌ Quick validation ERROR: {e}")
        return False


if __name__ == '__main__':
    # Check if quick validation requested
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        success = run_quick_validation()
        sys.exit(0 if success else 1)
    
    # Run full test suite
    success = run_test_suite()
    
    if success:
        print("🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please review the results above.")
        sys.exit(1)