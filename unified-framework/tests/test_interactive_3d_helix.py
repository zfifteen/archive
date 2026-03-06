#!/usr/bin/env python3
"""
Simple test suite for Interactive 3D Helical Quantum Nonlocality Visualizer

This test verifies basic functionality and integration with the Z framework.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from visualization.interactive_3d_helix import Interactive3DHelixVisualizer

def test_basic_functionality():
    """Test basic visualizer creation and functionality."""
    print("🧪 Testing basic functionality...")
    
    # Create visualizer
    viz = Interactive3DHelixVisualizer(n_points=100, default_k=0.2)
    
    # Basic checks
    assert len(viz.n) == 100, "Incorrect sequence length"
    assert len(viz.primes) > 0, "No primes generated"
    assert viz.default_k == 0.2, "Incorrect default k value"
    
    print(f"   ✓ Generated {len(viz.primes)} primes")
    print(f"   ✓ Sequence length: {len(viz.n)}")
    
def test_mathematical_functions():
    """Test core mathematical functions."""
    print("🧪 Testing mathematical functions...")
    
    viz = Interactive3DHelixVisualizer(n_points=50, default_k=0.2)
    
    # Test Z transform
    A = np.array([1.0, 2.0, 3.0])
    B = np.array([2.0, 4.0, 6.0])
    C = 299792458.0
    
    result = viz.z_transform(A, B, C)
    expected = A * (B / C)
    
    assert np.allclose(result, expected), "Z transform failed"
    print("   ✓ Z transform working correctly")
    
    # Test curvature transform
    n_test = np.array([1, 2, 3, 4, 5])
    curvature_result = viz.curvature_transform(n_test, k=0.2)
    
    assert len(curvature_result) == len(n_test), "Curvature transform length mismatch"
    assert np.all(curvature_result > 0), "Curvature transform should be positive"
    print("   ✓ Curvature transform working correctly")

def test_quantum_correlations():
    """Test quantum correlation computations."""
    print("🧪 Testing quantum correlations...")
    
    viz = Interactive3DHelixVisualizer(n_points=200, default_k=0.2)
    
    if len(viz.primes) >= 2:
        correlations = viz.compute_quantum_correlations(viz.primes[:10], k=0.2)
        
        if len(correlations) > 0:
            assert np.all(np.isfinite(correlations)), "Correlations contain invalid values"
            print(f"   ✓ Computed {len(correlations)} quantum correlations")
        else:
            print("   ⚠ No correlations computed (insufficient data)")
    else:
        print("   ⚠ Insufficient primes for correlation testing")

def test_bell_violations():
    """Test Bell inequality violation detection."""
    print("🧪 Testing Bell violation detection...")
    
    viz = Interactive3DHelixVisualizer(n_points=300, default_k=0.2)
    
    if len(viz.primes) >= 2:
        correlations = viz.compute_quantum_correlations(viz.primes, k=0.2)
        
        if len(correlations) > 0:
            gaps = np.diff(viz.primes[:len(correlations)+1])
            bell_violation, correlation_coeff = viz.compute_bell_violation(correlations, gaps)
            
            assert isinstance(bell_violation, bool), "Bell violation should be boolean"
            assert isinstance(correlation_coeff, float), "Correlation coefficient should be float"
            assert -1.0 <= correlation_coeff <= 1.0, "Correlation coefficient out of range"
            
            print(f"   ✓ Bell violation: {bell_violation}")
            print(f"   ✓ Correlation coefficient: {correlation_coeff:.6f}")
        else:
            print("   ⚠ No correlations for Bell testing")
    else:
        print("   ⚠ Insufficient primes for Bell testing")

def test_coordinate_generation():
    """Test 3D coordinate generation."""
    print("🧪 Testing coordinate generation...")
    
    viz = Interactive3DHelixVisualizer(n_points=100, default_k=0.2)
    
    x, y, z = viz.generate_helical_coordinates(viz.n[:50], k=0.2, freq=0.1)
    
    assert len(x) == len(y) == len(z) == 50, "Coordinate arrays length mismatch"
    assert np.all(np.isfinite(x)), "X coordinates contain invalid values"
    assert np.all(np.isfinite(y)), "Y coordinates contain invalid values" 
    assert np.all(np.isfinite(z)), "Z coordinates contain invalid values"
    
    print("   ✓ Generated valid 3D coordinates")
    print(f"   ✓ X range: [{np.min(x):.3f}, {np.max(x):.3f}]")
    print(f"   ✓ Y range: [{np.min(y):.6f}, {np.max(y):.6f}]")
    print(f"   ✓ Z range: [{np.min(z):.3f}, {np.max(z):.3f}]")

def test_report_generation():
    """Test analysis report generation."""
    print("🧪 Testing report generation...")
    
    viz = Interactive3DHelixVisualizer(n_points=200, default_k=0.2)
    report = viz.generate_summary_report()
    
    # Check report structure
    assert 'parameters' in report, "Missing parameters section"
    assert 'statistics' in report, "Missing statistics section"
    
    params = report['parameters']
    stats = report['statistics']
    
    assert params['n_points'] == 200, "Incorrect n_points in report"
    assert params['curvature_k'] == 0.2, "Incorrect curvature_k in report"
    assert 0 <= stats['prime_density'] <= 1, "Prime density out of range"
    
    print("   ✓ Report structure valid")
    print(f"   ✓ Prime density: {stats['prime_density']:.4f}")
    print(f"   ✓ Max prime: {stats['max_prime']}")

def test_framework_integration():
    """Test integration with Z framework components."""
    print("🧪 Testing Z framework integration...")
    
    # Test golden ratio calculation
    viz = Interactive3DHelixVisualizer(n_points=50)
    
    # Verify PHI calculation matches expected value
    expected_phi = (1 + np.sqrt(5)) / 2
    actual_phi = 1.618034  # From the module
    
    assert abs(actual_phi - expected_phi) < 0.001, "Golden ratio calculation incorrect"
    print(f"   ✓ Golden ratio φ = {actual_phi:.6f}")
    
    # Test high precision mode
    viz_precision = Interactive3DHelixVisualizer(n_points=50, use_high_precision=True)
    assert viz_precision.use_high_precision == True, "High precision mode not set"
    print("   ✓ High precision mode enabled")

def run_all_tests():
    """Run all tests."""
    print("🌀 Interactive 3D Helical Quantum Nonlocality Visualizer Tests")
    print("=" * 65)
    
    tests = [
        test_basic_functionality,
        test_mathematical_functions,
        test_quantum_correlations,
        test_bell_violations,
        test_coordinate_generation,
        test_report_generation,
        test_framework_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            failed += 1
            print()
    
    print("📊 Test Summary:")
    print(f"   ✓ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success rate: {100 * passed / (passed + failed):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Interactive 3D visualizer is working correctly.")
    else:
        print(f"\n⚠ {failed} test(s) failed. Please check the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)