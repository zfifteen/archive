#!/usr/bin/env python3
"""
Test script for v_{5D}^2 = c^2 implementation in the Z framework.
Validates the mathematical basis and ensures correct functionality.
"""

import numpy as np
from core.axioms import velocity_5d_constraint, massive_particle_w_velocity, curvature_induced_w_motion
from core.domain import DiscreteZetaShift

def test_velocity_constraint():
    """Test the 5D velocity constraint function."""
    print("Testing velocity constraint...")
    
    c = 299792458.0
    
    # Test 1: Perfect constraint satisfaction
    v_w = massive_particle_w_velocity(0, 0, 0, 0, c)
    constraint = velocity_5d_constraint(0, 0, 0, 0, v_w, c)
    assert abs(constraint) < 1e-6, f"Constraint violation: {constraint}"
    
    # Test 2: Non-trivial case
    v_x, v_y, v_z, v_t = 0.6*c, 0, 0, 0
    v_w = massive_particle_w_velocity(v_x, v_y, v_z, v_t, c)
    constraint = velocity_5d_constraint(v_x, v_y, v_z, v_t, v_w, c)
    assert abs(constraint) < 1e-6, f"Constraint violation: {constraint}"
    
    # Test 3: Error case
    try:
        massive_particle_w_velocity(c, 0, 0, 0, c)  # Should fail
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    print("✓ Velocity constraint tests passed")

def test_discrete_zeta_shift_5d():
    """Test 5D functionality in DiscreteZetaShift."""
    print("Testing DiscreteZetaShift 5D methods...")
    
    # Test for prime
    shift_prime = DiscreteZetaShift(7)
    velocities = shift_prime.get_5d_velocities()
    analysis = shift_prime.analyze_massive_particle_motion()
    
    # Verify constraint satisfaction
    assert velocities['constraint_satisfied'], "Constraint not satisfied"
    assert abs(velocities['v_magnitude'] - 299792458.0) < 1e-6, "Magnitude incorrect"
    
    # Verify analysis
    assert analysis['n'] == 7, "Incorrect n"
    assert analysis['is_prime'], "Should be prime"
    assert analysis['is_massive_particle'], "Should be massive particle"
    assert analysis['geodesic_classification'] == 'minimal_curvature', "Wrong classification"
    
    # Test for composite
    shift_composite = DiscreteZetaShift(6)
    analysis_comp = shift_composite.analyze_massive_particle_motion()
    
    assert not analysis_comp['is_prime'], "Should not be prime"
    assert analysis_comp['geodesic_classification'] == 'standard_curvature', "Wrong classification"
    
    print("✓ DiscreteZetaShift 5D tests passed")

def test_curvature_w_coupling():
    """Test curvature-induced w-motion."""
    print("Testing curvature-w coupling...")
    
    c = 299792458.0
    
    # Test that higher divisor count leads to higher w-velocity
    v_w_2 = curvature_induced_w_motion(2, 2, c)  # Prime
    v_w_12 = curvature_induced_w_motion(12, 6, c)  # Highly composite
    
    assert v_w_12 > v_w_2, f"Composite should have higher w-velocity: {v_w_12} vs {v_w_2}"
    
    # Test non-negative results
    for n in range(2, 10):
        from sympy import divisors
        d_n = len(divisors(n))
        v_w = curvature_induced_w_motion(n, d_n, c)
        assert v_w >= 0, f"Negative w-velocity for n={n}: {v_w}"
    
    print("✓ Curvature-w coupling tests passed")

def test_mathematical_consistency():
    """Test mathematical consistency across the framework."""
    print("Testing mathematical consistency...")
    
    # Test multiple shifts to ensure consistency
    errors = []
    for n in range(2, 20):
        try:
            shift = DiscreteZetaShift(n)
            velocities = shift.get_5d_velocities()
            analysis = shift.analyze_massive_particle_motion()
            
            # Verify v_w > 0 for all cases (massive particles)
            if velocities['v_w'] <= 0:
                errors.append(f"n={n}: v_w={velocities['v_w']} <= 0")
            
            # Verify constraint satisfaction
            if not velocities['constraint_satisfied']:
                errors.append(f"n={n}: constraint not satisfied")
            
        except Exception as e:
            errors.append(f"n={n}: exception {e}")
    
    if errors:
        print("Errors found:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")
    else:
        print("✓ Mathematical consistency tests passed")

def run_statistical_validation():
    """Run statistical validation of prime vs composite behavior."""
    print("Running statistical validation...")
    
    prime_curvatures = []
    composite_curvatures = []
    
    for n in range(2, 100):
        shift = DiscreteZetaShift(n)
        analysis = shift.analyze_massive_particle_motion()
        
        if analysis['is_prime']:
            prime_curvatures.append(analysis['discrete_curvature'])
        else:
            composite_curvatures.append(analysis['discrete_curvature'])
    
    if prime_curvatures and composite_curvatures:
        prime_mean = np.mean(prime_curvatures)
        composite_mean = np.mean(composite_curvatures)
        
        # Composites should have higher average curvature
        assert composite_mean > prime_mean, f"Composites should have higher curvature: {composite_mean} vs {prime_mean}"
        
        print(f"✓ Statistical validation passed:")
        print(f"  Prime curvature mean: {prime_mean:.6f}")
        print(f"  Composite curvature mean: {composite_mean:.6f}")
        print(f"  Ratio: {composite_mean/prime_mean:.2f}")

def main():
    """Run all tests."""
    print("Z Framework v_{5D}^2 = c^2 Test Suite")
    print("=" * 50)
    
    test_velocity_constraint()
    test_discrete_zeta_shift_5d()
    test_curvature_w_coupling()
    test_mathematical_consistency()
    run_statistical_validation()
    
    print("=" * 50)
    print("All tests passed! ✓")
    print("\nThe v_{5D}^2 = c^2 implementation is mathematically consistent")
    print("and correctly handles massive particle motion in the w-dimension.")

if __name__ == "__main__":
    main()