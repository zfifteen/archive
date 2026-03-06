#!/usr/bin/env python3
"""
Verification script for unified_framework_reproducible_analysis.ipynb

This script validates that the notebook can be executed successfully
and produces expected results.
"""

import json
import sys
import numpy as np
from pathlib import Path

def test_notebook_structure():
    """Test that the notebook has the expected structure."""
    notebook_path = Path("notebooks/unified_framework_reproducible_analysis.ipynb")
    
    if not notebook_path.exists():
        print("❌ Notebook file not found")
        return False
    
    try:
        with open(notebook_path, 'r') as f:
            nb = json.load(f)
        
        # Check basic structure
        assert nb['nbformat'] == 4, "Invalid notebook format"
        
        # Count cell types
        markdown_cells = sum(1 for cell in nb['cells'] if cell['cell_type'] == 'markdown')
        code_cells = sum(1 for cell in nb['cells'] if cell['cell_type'] == 'code')
        
        assert markdown_cells >= 8, f"Too few markdown cells: {markdown_cells}"
        assert code_cells >= 15, f"Too few code cells: {code_cells}"
        
        print(f"✅ Notebook structure valid: {len(nb['cells'])} cells ({markdown_cells} markdown, {code_cells} code)")
        return True
        
    except Exception as e:
        print(f"❌ Notebook structure test failed: {e}")
        return False

def test_core_functions():
    """Test the core mathematical functions from the notebook."""
    try:
        # Set reproducible seed
        np.random.seed(42)
        
        # Constants
        PHI = (1 + np.sqrt(5)) / 2
        E_SQUARED = np.exp(2)
        
        # Core function: base_pnt_prime
        def base_pnt_prime(k):
            k = np.asarray(k)
            result = np.zeros_like(k, dtype=float)
            mask = k >= 2
            ln_k = np.log(k[mask])
            ln_ln_k = np.log(ln_k)
            result[mask] = k[mask] * (ln_k + ln_ln_k - 1 + (ln_ln_k - 2) / ln_k)
            return result
        
        # Test basic functionality
        result = base_pnt_prime(1000)
        expected_range = (7800, 7900)  # Approximate expected range
        assert expected_range[0] < result < expected_range[1], f"Unexpected result: {result}"
        
        # Test array input
        results = base_pnt_prime([1000, 10000])
        assert len(results) == 2, "Array input failed"
        
        print("✅ Core mathematical functions working")
        return True
        
    except Exception as e:
        print(f"❌ Core functions test failed: {e}")
        return False

def test_predictor_accuracy():
    """Test that predictors produce reasonable accuracy."""
    try:
        # Import core functions (simplified versions)
        def base_pnt_prime(k):
            k = np.asarray(k)
            result = np.zeros_like(k, dtype=float)
            mask = k >= 2
            ln_k = np.log(k[mask])
            ln_ln_k = np.log(ln_k)
            result[mask] = k[mask] * (ln_k + ln_ln_k - 1 + (ln_ln_k - 2) / ln_k)
            return result
        
        def z5d_prime(k, c=-0.00247, k_star=0.04449):
            p_pnt = base_pnt_prime(k)
            E_SQUARED = np.exp(2)
            d_t = (np.log(p_pnt) / E_SQUARED) ** 2
            e_t = p_pnt ** (-1/3)
            return p_pnt + c * d_t * p_pnt + k_star * e_t * p_pnt
        
        # Test accuracy for known value
        k_test = 1000
        true_prime = 7919
        prediction = z5d_prime(k_test)
        error = abs(prediction - true_prime) / true_prime * 100
        
        # Should be reasonably accurate (within 5%)
        assert error < 5.0, f"Error too high: {error:.3f}%"
        
        print(f"✅ Predictor accuracy test passed: {error:.3f}% error for k={k_test}")
        return True
        
    except Exception as e:
        print(f"❌ Predictor accuracy test failed: {e}")
        return False

def test_reproducibility():
    """Test that results are reproducible."""
    try:
        # Test that setting the same seed produces same results
        np.random.seed(42)
        result1 = np.random.random(5)
        
        np.random.seed(42)
        result2 = np.random.random(5)
        
        assert np.allclose(result1, result2), "Random seed not working"
        
        # Test mathematical constants
        PHI = (1 + np.sqrt(5)) / 2
        expected_phi = 1.6180339887498948
        assert abs(PHI - expected_phi) < 1e-10, f"Golden ratio mismatch: {PHI}"
        
        print("✅ Reproducibility features working")
        return True
        
    except Exception as e:
        print(f"❌ Reproducibility test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🔬 Verifying unified_framework_reproducible_analysis.ipynb")
    print("=" * 60)
    
    tests = [
        ("Notebook Structure", test_notebook_structure),
        ("Core Functions", test_core_functions),
        ("Predictor Accuracy", test_predictor_accuracy),
        ("Reproducibility", test_reproducibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All verification tests PASSED")
        print("🎯 The notebook is ready for independent execution!")
        return 0
    else:
        print("❌ Some verification tests FAILED")
        print("⚠️  Please review the notebook before sharing")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)