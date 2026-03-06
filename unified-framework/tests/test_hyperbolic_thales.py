import random
import mpmath as mp
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from geometry.hyperbolic_thales import hyperbolic_thales_curve

mp.mp.dps = 50
phi = mp.mpf((1 + mp.sqrt(5)) / 2)

def reference_theta(n, k=mp.mpf("0.3")):
    """Reference implementation matching existing θ'(n,k) = φ * ((n mod φ)/φ)^k"""
    return phi * ((mp.fmod(n, phi) / phi) ** k)

def test_against_reference_small_n():
    """Test that hyperbolic implementation produces reasonable results compared to reference"""
    rng = random.Random(42)
    
    # Test that both functions produce values in similar ranges
    ref_values = []
    hyp_values = []
    
    for _ in range(100):
        n = rng.randint(2, 10**3)
        z_new = hyperbolic_thales_curve(n)
        z_old = reference_theta(n)
        
        ref_values.append(float(z_old))
        hyp_values.append(float(z_new))
        
        # Both should be positive and in reasonable range
        assert z_new > 0, f"Hyperbolic result should be positive: {z_new}"
        assert z_old > 0, f"Reference result should be positive: {z_old}"
        assert z_new < 10, f"Hyperbolic result should be reasonable: {z_new}"
        assert z_old < 10, f"Reference result should be reasonable: {z_old}"
    
    # Check that the ranges are comparable (within an order of magnitude)
    ref_mean = sum(ref_values) / len(ref_values)
    hyp_mean = sum(hyp_values) / len(hyp_values)
    ratio = hyp_mean / ref_mean
    assert 0.1 < ratio < 10, f"Mean ratio {ratio} indicates very different scales"

def test_precision_stability():
    """Test that large n values don't blow up numeric precision"""
    # n near 1e6 should not blow up numeric precision
    n = 10 ** 6
    val = hyperbolic_thales_curve(n)
    assert val < 1e6, f"Value {val} too large for n={n}"  # coarse sanity
    assert mp.isfinite(val), f"Value {val} should be finite"

def test_non_positive_kappa_requirement():
    """Test that κ ≤ 0 raises ValueError"""
    try:
        hyperbolic_thales_curve(100, kappa=0)
        assert False, "Should have raised ValueError for κ=0"
    except ValueError:
        pass
    
    try:
        hyperbolic_thales_curve(100, kappa=-1)
        assert False, "Should have raised ValueError for κ=-1"
    except ValueError:
        pass

def test_basic_functionality():
    """Basic sanity check that function returns reasonable values"""
    result = hyperbolic_thales_curve(100)
    assert isinstance(result, mp.mpf), f"Expected mp.mpf, got {type(result)}"
    assert result > 0, f"Expected positive result, got {result}"
    assert result < 100, f"Expected reasonable magnitude, got {result}"

def test_scale_invariance_property():
    """Test that the hyperbolic approach exhibits scale-invariant properties"""
    # Test that scaling n by φ produces predictable results
    base_n = 100
    scaled_n = int(base_n * float(phi))
    
    result_base = hyperbolic_thales_curve(base_n)
    result_scaled = hyperbolic_thales_curve(scaled_n)
    
    # Both should be finite and positive
    assert mp.isfinite(result_base) and result_base > 0
    assert mp.isfinite(result_scaled) and result_scaled > 0
    
    # The ratio should be reasonably bounded (scale-invariance property)
    ratio = result_scaled / result_base
    assert 0.1 < ratio < 10, f"Scale ratio {ratio} indicates poor scale invariance"

if __name__ == "__main__":
    print("Running test_basic_functionality...")
    test_basic_functionality()
    print("✓ Basic functionality test passed")
    
    print("Running test_non_positive_kappa_requirement...")
    test_non_positive_kappa_requirement()
    print("✓ Non-positive κ requirement test passed")
    
    print("Running test_precision_stability...")
    test_precision_stability()
    print("✓ Precision stability test passed")
    
    print("Running test_scale_invariance_property...")
    test_scale_invariance_property()
    print("✓ Scale invariance test passed")
    
    print("Running test_against_reference_small_n...")
    test_against_reference_small_n()
    print("✓ Reference comparison test passed")
    
    print("All tests passed!")