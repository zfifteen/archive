#!/usr/bin/env python3
"""
Test suite for Reproduce Scale Test: RSA-100 Geometric Factorization
==================================================================

Tests the functionality of the RSA-100 scale test reproduction script.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_rsa100_scale_test_import():
    """Test that the scale test reproduction script can be imported."""
    try:
        from reproduce_scale_test import RSA100ScaleTestReproducer
        assert RSA100ScaleTestReproducer is not None
        print("✅ Import test passed")
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_rsa100_scale_test_initialization():
    """Test that the scale test reproducer initializes correctly."""
    try:
        from reproduce_scale_test import RSA100ScaleTestReproducer
        reproducer = RSA100ScaleTestReproducer()
        
        # Check that required attributes exist
        assert hasattr(reproducer, 'rsa100_n')
        assert hasattr(reproducer, 'rsa100_p')
        assert hasattr(reproducer, 'rsa100_q')
        assert hasattr(reproducer, 'optimized_params')
        assert hasattr(reproducer, 'z5d')
        
        # Check RSA-100 values are correct
        assert reproducer.rsa100_p * reproducer.rsa100_q == reproducer.rsa100_n
        
        print("✅ Initialization test passed")
        return True
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        return False

def test_rsa100_geometric_validation():
    """Test RSA-100 geometric factorization validation."""
    try:
        from reproduce_scale_test import RSA100ScaleTestReproducer
        reproducer = RSA100ScaleTestReproducer()
        
        results = reproducer.validate_rsa100_geometric_factorization()
        
        # Check required result fields
        required_fields = [
            'factorization_correct', 'geometric_balance_ratio', 
            'z5d_prediction_accuracy', 'sierpinski_correlation',
            'e2_invariant'
        ]
        
        for field in required_fields:
            assert field in results, f"Missing field: {field}"
        
        # Check that factorization is correct
        assert results['factorization_correct'] == True
        
        # Check that balance ratio is reasonable (close to 1.0 for balanced factors)
        assert 0.8 <= results['geometric_balance_ratio'] <= 1.0
        
        print("✅ Geometric validation test passed")
        return True
    except Exception as e:
        print(f"❌ Geometric validation test failed: {e}")
        return False

def test_correlation_computation():
    """Test correlation computation methods."""
    try:
        from reproduce_scale_test import RSA100ScaleTestReproducer
        reproducer = RSA100ScaleTestReproducer()
        
        # Test Sierpiński correlation
        sierpinski_corr = reproducer._compute_sierpinski_correlation(
            reproducer.rsa100_p, reproducer.rsa100_q
        )
        assert 0.0 <= sierpinski_corr <= 1.0
        
        # Test e² invariant
        e2_invariant = reproducer._compute_e2_invariant(
            reproducer.rsa100_p, reproducer.rsa100_q
        )
        assert e2_invariant > 0.0
        
        print("✅ Correlation computation test passed")
        return True
    except Exception as e:
        print(f"❌ Correlation computation test failed: {e}")
        return False

def test_scale_test_sample_generation():
    """Test scale test sample generation."""
    try:
        from reproduce_scale_test import RSA100ScaleTestReproducer
        reproducer = RSA100ScaleTestReproducer()
        
        # Generate samples for a smaller scale factor
        samples = reproducer._generate_scale_test_samples(1e6, count=10)
        
        # Check that we got some samples
        assert len(samples) > 0
        
        # Check sample structure
        for sample in samples:
            assert 'N' in sample
            assert 'p' in sample
            assert 'q' in sample
            assert sample['p'] * sample['q'] == sample['N']
        
        print("✅ Sample generation test passed")
        return True
    except Exception as e:
        print(f"❌ Sample generation test failed: {e}")
        return False

def test_results_saving():
    """Test that results can be saved to JSON file."""
    try:
        from reproduce_scale_test import RSA100ScaleTestReproducer
        reproducer = RSA100ScaleTestReproducer()
        
        # Use a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            temp_filename = tmp.name
        
        try:
            # Generate a minimal report and save it
            results = reproducer.validate_rsa100_geometric_factorization()
            
            # Create a minimal report structure
            report = {
                'test_type': 'RSA-100 Geometric Factorization Scale Test',
                'rsa100_validation': results,
                'success': True
            }
            
            with open(temp_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            # Verify the file was created and contains valid JSON
            assert os.path.exists(temp_filename)
            
            with open(temp_filename, 'r') as f:
                loaded_report = json.load(f)
            
            assert loaded_report['test_type'] == 'RSA-100 Geometric Factorization Scale Test'
            assert 'rsa100_validation' in loaded_report
            
            print("✅ Results saving test passed")
            return True
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
                
    except Exception as e:
        print(f"❌ Results saving test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and return summary."""
    tests = [
        test_rsa100_scale_test_import,
        test_rsa100_scale_test_initialization,
        test_rsa100_geometric_validation,
        test_correlation_computation,
        test_scale_test_sample_generation,
        test_results_saving
    ]
    
    print("🧪 Running RSA-100 Scale Test Reproduction Tests")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        print(f"\nRunning {test_func.__name__}...")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)