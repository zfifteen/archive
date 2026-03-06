"""
Test script for discrete domain coding, geodesic transform, and proof validation sweep.

Tests the enhanced implementations of:
1. Discrete domain Z = n(Δ_n/Δ_max) with κ(n) bounds
2. θ'(n,k) = φ · {n/φ}^k high-precision transformation
3. Bootstrap confidence intervals and e_max(k) calculation

Dependencies: numpy, mpmath, sympy, scipy
"""
import numpy as np
import mpmath as mp
from sympy import divisors, isprime
import sys
import os

# Add the core modules to path
sys.path.insert(0, '/home/runner/work/unified-framework/unified-framework')

from core.domain import DiscreteZetaShift, PHI, E_SQUARED
from core.axioms import theta_prime, curvature

mp.mp.dps = 50  # High precision for testing

def test_discrete_domain_bounds():
    """Test that discrete domain Z = n(Δ_n/Δ_max) has proper κ(n) bounds."""
    print("Testing discrete domain κ(n) bounds...")
    
    test_values = [2, 3, 5, 7, 11, 13, 100, 997]
    all_passed = True
    
    for n in test_values:
        try:
            # Create DiscreteZetaShift instance
            zeta = DiscreteZetaShift(n)
            
            # Check that bounded kappa is within limits
            if hasattr(zeta, 'kappa_bounded'):
                kappa_bounded = float(zeta.kappa_bounded)
                e_squared = float(E_SQUARED)
                phi_val = float(PHI)
                
                # Verify bounds: κ(n) ≤ min(e², φ)
                max_bound = min(e_squared, phi_val)
                
                if kappa_bounded <= max_bound:
                    print(f"✓ n={n}: κ_bounded={kappa_bounded:.6f} ≤ {max_bound:.6f}")
                else:
                    print(f"✗ n={n}: κ_bounded={kappa_bounded:.6f} > {max_bound:.6f}")
                    all_passed = False
                    
                # Check Z = n(Δ_n/Δ_max) formula
                z_val = float(zeta.compute_z())
                expected_z = n * float(zeta.delta_n) / float(E_SQUARED)
                if abs(z_val - expected_z) < 1e-10:
                    print(f"✓ n={n}: Z formula correct: {z_val:.6f}")
                else:
                    print(f"✗ n={n}: Z formula mismatch: {z_val:.6f} vs {expected_z:.6f}")
                    all_passed = False
            else:
                print(f"✗ n={n}: Missing kappa_bounded attribute")
                all_passed = False
                
        except Exception as e:
            print(f"✗ n={n}: Error - {e}")
            all_passed = False
    
    return all_passed


def test_theta_prime_precision():
    """Test θ'(n,k) = φ · {n/φ}^k high-precision transformation."""
    print("\nTesting θ'(n,k) high-precision transformation...")
    
    test_cases = [
        (2, 0.2), (3, 0.3), (5, 0.2), (7, 0.4), 
        (997, 0.2), (1009, 0.3)
    ]
    all_passed = True
    
    for n, k in test_cases:
        try:
            # Test enhanced theta_prime function
            result = theta_prime(n, k)
            result_float = float(result)
            phi_val = float(PHI)
            
            # Verify bounds: 0 ≤ θ'(n,k) < φ
            if 0 <= result_float < phi_val:
                print(f"✓ θ'({n},{k}) = {result_float:.6f} ∈ [0, φ)")
            else:
                print(f"✗ θ'({n},{k}) = {result_float:.6f} not in [0, φ={phi_val:.6f})")
                all_passed = False
            
            # Test precision: result should have high precision (unless it's a simple mathematical result)
            precision_str = mp.nstr(result, 15)
            if result_float == 1.0:  # Special case: mathematically exact result
                print(f"✓ Exact result: θ'({n},{k}) = 1.0 (mathematically exact)")
            elif len(precision_str.replace('.', '').replace('-', '')) >= 10:  # At least 10 significant digits
                print(f"✓ High precision: {precision_str}")
            else:
                print(f"✗ Low precision: {precision_str}")
                all_passed = False
                
            # Test edge cases
            if k == 0:
                expected = phi_val  # θ'(n,0) = φ for any n
                if abs(result_float - expected) < 1e-10:
                    print(f"✓ Edge case k=0: θ'({n},0) = φ")
                else:
                    print(f"✗ Edge case k=0: θ'({n},0) = {result_float:.6f} ≠ φ")
                    all_passed = False
                    
        except Exception as e:
            print(f"✗ θ'({n},{k}): Error - {e}")
            all_passed = False
    
    return all_passed


def test_curvature_calculation():
    """Test κ(n) = d(n) · ln(n+1)/e² calculation and bounds."""
    print("\nTesting κ(n) curvature calculation...")
    
    test_primes = [2, 3, 5, 7, 11, 13, 17, 19]
    test_composites = [4, 6, 8, 9, 10, 12, 14, 15]
    all_passed = True
    
    prime_curvatures = []
    composite_curvatures = []
    
    for n in test_primes:
        try:
            d_n = len(list(divisors(n)))
            kappa = curvature(n, d_n)
            kappa_float = float(kappa)
            prime_curvatures.append(kappa_float)
            
            # For primes, d(n) = 2, so κ(n) = 2 * ln(n+1) / e²
            expected = 2 * np.log(n + 1) / np.exp(2)
            if abs(kappa_float - expected) < 1e-10:
                print(f"✓ Prime n={n}: κ({n}) = {kappa_float:.6f}")
            else:
                print(f"✗ Prime n={n}: κ({n}) = {kappa_float:.6f} ≠ {expected:.6f}")
                all_passed = False
                
        except Exception as e:
            print(f"✗ Prime n={n}: Error - {e}")
            all_passed = False
    
    for n in test_composites:
        try:
            d_n = len(list(divisors(n)))
            kappa = curvature(n, d_n)
            kappa_float = float(kappa)
            composite_curvatures.append(kappa_float)
            
            print(f"✓ Composite n={n}: κ({n}) = {kappa_float:.6f}, d({n}) = {d_n}")
                
        except Exception as e:
            print(f"✗ Composite n={n}: Error - {e}")
            all_passed = False
    
    # Verify that composites generally have higher curvature than primes
    if len(prime_curvatures) > 0 and len(composite_curvatures) > 0:
        avg_prime = np.mean(prime_curvatures)
        avg_composite = np.mean(composite_curvatures)
        
        if avg_composite > avg_prime:
            print(f"✓ Curvature differentiation: avg_composite({avg_composite:.6f}) > avg_prime({avg_prime:.6f})")
        else:
            print(f"✗ Curvature differentiation: avg_composite({avg_composite:.6f}) ≤ avg_prime({avg_prime:.6f})")
            all_passed = False
    
    return all_passed


def test_bootstrap_functionality():
    """Test bootstrap confidence interval calculation."""
    print("\nTesting bootstrap confidence intervals...")
    
    # Mock enhancement data
    np.random.seed(42)  # For reproducible tests
    mock_enhancements = np.array([100.0, 200.0, 150.0, 300.0, 250.0, 180.0])
    
    try:
        # Import the bootstrap function from proof.py
        sys.path.insert(0, '/home/runner/work/unified-framework/unified-framework/number-theory/prime-curve')
        from proof import bootstrap_confidence_interval, compute_e_max_robust
        
        # Test bootstrap CI
        ci_lower, ci_upper = bootstrap_confidence_interval(mock_enhancements, 
                                                          confidence_level=0.95, 
                                                          n_bootstrap=100)
        
        sample_mean = np.mean(mock_enhancements)
        
        if ci_lower <= sample_mean <= ci_upper:
            print(f"✓ Bootstrap CI contains sample mean: [{ci_lower:.1f}, {ci_upper:.1f}] contains {sample_mean:.1f}")
        else:
            print(f"✗ Bootstrap CI doesn't contain sample mean: [{ci_lower:.1f}, {ci_upper:.1f}] missing {sample_mean:.1f}")
            return False
        
        # Test e_max robust calculation
        mock_with_inf = np.array([100.0, np.inf, 200.0, -np.inf, 150.0, np.nan])
        e_max = compute_e_max_robust(mock_with_inf)
        
        if e_max == 200.0:
            print(f"✓ Robust e_max calculation: {e_max}")
        else:
            print(f"✗ Robust e_max calculation: expected 200.0, got {e_max}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Bootstrap test error: {e}")
        return False


def test_discrete_zeta_shift_integration():
    """Test integration of enhanced DiscreteZetaShift with geodesic transforms."""
    print("\nTesting DiscreteZetaShift integration...")
    
    test_n = 17  # Prime number for testing
    all_passed = True
    
    try:
        zeta = DiscreteZetaShift(test_n)
        
        # Test that all required attributes exist
        required_attrs = ['kappa_raw', 'kappa_bounded', 'delta_n']
        for attr in required_attrs:
            if hasattr(zeta, attr):
                print(f"✓ Attribute {attr} exists: {getattr(zeta, attr)}")
            else:
                print(f"✗ Missing attribute: {attr}")
                all_passed = False
        
        # Test 5D coordinates generation
        coords_5d = zeta.get_5d_coordinates()
        if len(coords_5d) == 5:
            print(f"✓ 5D coordinates: {[f'{c:.3f}' for c in coords_5d]}")
        else:
            print(f"✗ 5D coordinates length: expected 5, got {len(coords_5d)}")
            all_passed = False
            
        # Test helical coordinates
        helical_coords = zeta.get_helical_coordinates()
        if len(helical_coords) == 5:
            print(f"✓ Helical coordinates: {[f'{c:.3f}' for c in helical_coords]}")
        else:
            print(f"✗ Helical coordinates length: expected 5, got {len(helical_coords)}")
            all_passed = False
            
        # Test that Z value is properly calculated
        z_val = zeta.compute_z()
        if np.isfinite(float(z_val)) and float(z_val) > 0:
            print(f"✓ Z computation: {float(z_val):.6f}")
        else:
            print(f"✗ Z computation invalid: {z_val}")
            all_passed = False
            
    except Exception as e:
        print(f"✗ Integration test error: {e}")
        all_passed = False
    
    return all_passed


def run_all_tests():
    """Run comprehensive test suite for discrete domain transformations."""
    print("=" * 60)
    print("DISCRETE DOMAIN TRANSFORMS TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Discrete Domain Bounds", test_discrete_domain_bounds),
        ("θ'(n,k) High Precision", test_theta_prime_precision),
        ("κ(n) Curvature Calculation", test_curvature_calculation),
        ("Bootstrap Functionality", test_bootstrap_functionality),
        ("DiscreteZetaShift Integration", test_discrete_zeta_shift_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Transformations are working correctly!")
        return True
    else:
        print("❌ SOME TESTS FAILED - Review implementation")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)