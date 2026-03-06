#!/usr/bin/env python3
"""
Dependency Import Test for Spinor Geodesic Framework

This test validates that all required dependencies can be imported
and are functional for the spinor geodesic curvature implementation.

Run this test first before running the full test suite to ensure
environment is properly configured.
"""

import sys
import traceback

def test_numpy_import():
    """Test NumPy import and basic functionality."""
    try:
        import numpy as np
        # Test basic operations
        arr = np.array([1, 2, 3])
        assert arr.shape == (3,)
        assert np.sum(arr) == 6
        print("✅ NumPy: Import and basic operations successful")
        return True
    except Exception as e:
        print(f"❌ NumPy: Failed - {e}")
        return False

def test_qutip_import():
    """Test QuTiP import and basic functionality."""
    try:
        import qutip as qt
        # Test basic QuTiP operations
        basis_0 = qt.basis(2, 0)
        basis_1 = qt.basis(2, 1)
        superpos = (basis_0 + basis_1).unit()
        assert basis_0.shape == (2, 1)
        assert abs(superpos.norm() - 1.0) < 1e-10
        
        # Test Pauli matrices
        sigma_x = qt.sigmax()
        sigma_y = qt.sigmay()
        sigma_z = qt.sigmaz()
        identity = qt.qeye(2)
        
        assert sigma_x.shape == (2, 2)
        assert identity.shape == (2, 2)
        
        print("✅ QuTiP: Import and basic operations successful")
        return True
    except Exception as e:
        print(f"❌ QuTiP: Failed - {e}")
        traceback.print_exc()
        return False

def test_mpmath_import():
    """Test mpmath import and basic functionality."""
    try:
        import mpmath as mp
        # Test high precision arithmetic
        mp.dps = 50
        pi_val = mp.pi
        e_val = mp.e
        assert abs(float(pi_val) - 3.14159265359) < 1e-10
        assert abs(float(e_val) - 2.71828182846) < 1e-10
        print("✅ mpmath: Import and basic operations successful")
        return True
    except Exception as e:
        print(f"❌ mpmath: Failed - {e}")
        return False

def test_scipy_import():
    """Test SciPy import (indirect dependency)."""
    try:
        import scipy
        import scipy.linalg
        # Test basic linear algebra
        import numpy as np
        A = np.array([[1, 2], [3, 4]])
        det = scipy.linalg.det(A)
        assert abs(det - (-2.0)) < 1e-10
        print("✅ SciPy: Import and basic operations successful")
        return True
    except Exception as e:
        print(f"❌ SciPy: Failed - {e}")
        return False

def test_framework_imports():
    """Test that our framework modules can be imported."""
    try:
        sys.path.append('src/core')
        from spinor_geodesic import (
            PHI, OPTIMAL_K, E_SQUARED,
            spinor_geodesic_transform, su2_rotation_matrix,
            calculate_fidelity, demonstrate_20_percent_improvement
        )
        
        # Test constants are reasonable
        assert 1.6 < PHI < 1.7  # Golden ratio
        assert 0.25 < OPTIMAL_K < 0.35  # k*
        assert 7 < E_SQUARED < 8  # e²
        
        print("✅ Framework: Core module imports successful")
        return True
    except Exception as e:
        print(f"❌ Framework: Failed - {e}")
        traceback.print_exc()
        return False

def main():
    """Run all dependency tests."""
    print("=" * 60)
    print("Dependency Import Test for Spinor Geodesic Framework")
    print("=" * 60)
    
    tests = [
        test_numpy_import,
        test_qutip_import, 
        test_mpmath_import,
        test_scipy_import,
        test_framework_imports
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Dependency Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All dependencies are properly installed and functional!")
        print("You can now run the full test suite.")
        return 0
    else:
        print("❌ Some dependencies failed. Please install missing packages:")
        print("   pip install qutip numpy scipy mpmath")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)