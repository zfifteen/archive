#!/usr/bin/env python3
"""
Integration Test for Computationally Intensive Validation Suite
==============================================================

This script validates that the computational validation suite integrates
properly with the existing Z Framework and produces expected results.
"""

import os
import sys
import subprocess
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_imports():
    """Test that all required modules can be imported."""
    print("Testing basic imports...")
    try:
        import numpy as np
        import scipy
        import pandas as pd
        import matplotlib
        import sympy as sp
        import mpmath as mp
        import sklearn
        print("✓ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_z_framework_integration():
    """Test integration with existing Z Framework."""
    print("Testing Z Framework integration...")
    try:
        # Test core module imports
        from src.core.axioms import universal_invariance
        from src.core.domain import UniversalZetaShift
        
        # Test basic functionality
        result = universal_invariance(1.0, 3e8)
        print(f"✓ Universal invariance calculation: {result}")
        
        # Test DiscreteZetaShift
        uzs = UniversalZetaShift(2, 3, 5)
        z_value = uzs.compute_z()
        print(f"✓ UniversalZetaShift computation: {z_value}")
        
        return True
    except Exception as e:
        print(f"✗ Z Framework integration error: {e}")
        return False

def test_computational_validation_basic():
    """Test basic computational validation functionality."""
    print("Testing computational validation (basic)...")
    try:
        # Set PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/runner/work/unified-framework/unified-framework'
        
        # Run basic validation with small scale
        cmd = [
            'python3', 
            'tests/computationally_intensive_validation.py'
        ]
        
        start_time = time.time()
        result = subprocess.run(
            cmd, 
            cwd='/home/runner/work/unified-framework/unified-framework',
            env=env,
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✓ Basic validation completed in {duration:.2f} seconds")
            # Check for key results in output
            if "Tests Passed:" in result.stdout:
                print("✓ Test results found in output")
                return True
            else:
                print("✗ Expected test results not found")
                return False
        else:
            print(f"✗ Validation failed with return code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Computational validation timed out")
        return False
    except Exception as e:
        print(f"✗ Computational validation error: {e}")
        return False

def test_high_scale_validation_basic():
    """Test high-scale validation with small parameters."""
    print("Testing high-scale validation (basic)...")
    try:
        # Set PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/runner/work/unified-framework/unified-framework'
        
        # Run high-scale validation with small scale
        cmd = [
            'python3', 
            'tests/high_scale_validation.py',
            '--max_n', '10000',
            '--test_cases', 'TC01'
        ]
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            cwd='/home/runner/work/unified-framework/unified-framework',
            env=env,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✓ High-scale validation completed in {duration:.2f} seconds")
            if "Tests Completed:" in result.stdout:
                print("✓ High-scale results found in output")
                return True
            else:
                print("✗ Expected high-scale results not found")
                return False
        else:
            print(f"✗ High-scale validation failed with return code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ High-scale validation timed out")
        return False
    except Exception as e:
        print(f"✗ High-scale validation error: {e}")
        return False

def test_existing_proof_compatibility():
    """Test that existing proof.py still works."""
    print("Testing existing proof.py compatibility...")
    try:
        # Set PYTHONPATH
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/runner/work/unified-framework/unified-framework'
        
        cmd = [
            'python3',
            'src/number-theory/prime-curve/proof.py'
        ]
        
        result = subprocess.run(
            cmd,
            cwd='/home/runner/work/unified-framework/unified-framework',
            env=env,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✓ Existing proof.py runs successfully")
            if "Optimal curvature exponent" in result.stdout:
                print("✓ Proof results found in output")
                return True
            else:
                print("✗ Expected proof results not found")
                return False
        else:
            print(f"✗ Existing proof.py failed")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Existing proof.py timed out")
        return False
    except Exception as e:
        print(f"✗ Existing proof.py error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("Z Framework: Computational Validation Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Z Framework Integration", test_z_framework_integration),
        ("Existing Proof Compatibility", test_existing_proof_compatibility),
        ("Computational Validation Basic", test_computational_validation_basic),
        ("High-Scale Validation Basic", test_high_scale_validation_basic),
    ]
    
    results = {}
    total_start = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Running: {test_name}")
        print(f"{'='*40}")
        
        try:
            start_time = time.time()
            success = test_func()
            duration = time.time() - start_time
            
            results[test_name] = {
                'success': success,
                'duration': duration
            }
            
            status = "PASS" if success else "FAIL"
            print(f"Result: {status} (Duration: {duration:.2f}s)")
            
        except Exception as e:
            results[test_name] = {
                'success': False,
                'duration': 0,
                'error': str(e)
            }
            print(f"Result: ERROR - {e}")
    
    total_duration = time.time() - total_start
    
    # Summary
    print(f"\n{'='*60}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    print(f"Total Duration: {total_duration:.2f} seconds")
    
    print(f"\nDetailed Results:")
    for test_name, result in results.items():
        status = "PASS" if result['success'] else "FAIL"
        duration = result['duration']
        print(f"  {test_name}: {status} ({duration:.2f}s)")
        if not result['success'] and 'error' in result:
            print(f"    Error: {result['error']}")
    
    # Overall success
    if passed == total:
        print(f"\n🎉 All integration tests PASSED!")
        return 0
    else:
        print(f"\n❌ {total - passed} integration tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())