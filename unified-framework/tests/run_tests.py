#!/usr/bin/env python3
"""
Test runner for the golden master test suite.

Usage:
    python3 run_tests.py
    python3 run_tests.py --verbose
    python3 run_tests.py --test density_enhancement
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

def run_test(test_name, verbose=False):
    """Run a specific test and return success status."""
    
    # Special handling for RSA probe validation
    if test_name == "rsa_probe_validation":
        try:
            print("Running RSA Probe Validation...")
            import subprocess
            result = subprocess.run([
                sys.executable, 
                str(Path(__file__).parent / "ci_rsa_probe_validation.py")
            ], capture_output=True, text=True)
            
            if verbose:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            if success:
                print("✅ rsa_probe_validation: PASS")
            else:
                print("❌ rsa_probe_validation: FAIL")
                if not verbose:
                    print("  Run with --verbose for details")
            return success
        except Exception as e:
            print(f"❌ rsa_probe_validation: FAIL - {e}")
            return False
    
    # Special handling for LET integration tests
    if test_name == "let_integration":
        try:
            from tests.performance.test_let_integration import LETIntegrationTestSuite
            print("Running LET Integration Test Suite...")
            suite = LETIntegrationTestSuite(max_n=10**5)  # Quick mode
            results = suite.run_full_test_suite(quick_mode=True)
            
            success = results['summary']['overall_suite_pass']
            if success:
                print("✅ let_integration: PASS")
            else:
                print("❌ let_integration: PARTIAL PASS")
                pass_rate = results['summary']['pass_rate'] * 100
                print(f"  Pass rate: {pass_rate:.1f}%")
            return success
        except Exception as e:
            print(f"❌ let_integration: FAIL - {e}")
            return False
    
    # Original test handling
    test_file = f"test_{test_name}.py"
    test_path = Path(__file__).parent / test_file
    
    if not test_path.exists():
        print(f"Error: Test file {test_file} not found")
        return False
    
    try:
        if verbose:
            print(f"Running {test_file}...")
            result = subprocess.run([sys.executable, str(test_path)], 
                                  capture_output=False, text=True)
        else:
            result = subprocess.run([sys.executable, str(test_path)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {test_name}: PASS")
            else:
                print(f"❌ {test_name}: FAIL")
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run golden master tests")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Show detailed output")
    parser.add_argument("--test", "-t", 
                       help="Run specific test (e.g., 'density_enhancement_minimal')")
    
    args = parser.parse_args()
    
    # Available tests
    available_tests = ["density_enhancement_minimal", "claim_linking", "rsa_probe_validation"]
    
    # Add LET integration tests if available (check at runtime)
    try:
        # Ensure we can import from the current directory
        current_dir = Path(__file__).parent.parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
            
        from tests.performance.test_let_integration import LETIntegrationTestSuite
        available_tests.append("let_integration")
    except ImportError:
        pass
    
    if args.test:
        if args.test in available_tests:
            success = run_test(args.test, args.verbose)
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown test: {args.test}")
            print(f"Available tests: {', '.join(available_tests)}")
            sys.exit(1)
    
    # Run all tests
    print("Running all golden master tests...")
    all_passed = True
    
    for test in available_tests:
        success = run_test(test, args.verbose)
        all_passed = all_passed and success
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All tests PASSED!")
    else:
        print("💥 Some tests FAILED!")
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()