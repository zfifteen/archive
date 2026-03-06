# tests/test_atan_opt.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mpmath as mp
import sympy as sp

# Direct import to avoid src package initialization issues
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core', 'symbolic'))
from atan_opt import (
    simplify_arctan_half_angle, 
    atan_half_angle_derivative,
    simplify_arctan_double_angle_at_half,
    apply_arctan_optimizations
)

def test_symbolic_simplification_half_angle():
    x = sp.symbols('x', positive=True)
    expr = sp.atan((sp.sqrt(1 + x**2) - 1)/x)
    got = simplify_arctan_half_angle(expr)
    assert sp.simplify(got - sp.atan(x)/2) == 0

def test_symbolic_derivative_matches_identity():
    x = sp.symbols('x', positive=True)
    expr = sp.atan((sp.sqrt(1 + x**2) - 1)/x)
    dexpr = sp.diff(expr, x)
    target = atan_half_angle_derivative(x)
    assert sp.simplify(dexpr - target) == 0

def test_numeric_identity_points():
    mp.mp.dps = 50
    for val in [mp.mpf('0.1'), mp.mpf('0.5'), mp.mpf('1.0'), mp.mpf('2.0'), mp.mpf('10.0')]:
        lhs = mp.atan((mp.sqrt(1 + val*val) - 1)/val)
        rhs = 0.5 * mp.atan(val)
        assert mp.almosteq(lhs, rhs, rel_eps=mp.mpf('1e-45'), abs_eps=mp.mpf('1e-45'))

def test_specific_value_second_identity():
    # atan((2x sqrt(1-x^2))/(1-2x^2)) at x=1/2  -> pi/3
    x = sp.Rational(1, 2)
    expr = sp.atan((2*x*sp.sqrt(1 - x**2)) / (1 - 2*x**2))
    assert sp.simplify(expr - sp.pi/3) == 0

def test_domain_safety_unconstrained_symbol():
    """Test that unconstrained symbol results in Piecewise, not direct rewrite."""
    x = sp.symbols('x')  # no positive assumption
    expr = sp.atan((sp.sqrt(1 + x**2) - 1)/x)
    result = simplify_arctan_half_angle(expr)
    
    # Should return a Piecewise since x is not provably positive
    assert isinstance(result, sp.Piecewise)
    
def test_domain_safety_negative_value():
    """Test that negative substitution doesn't produce wrong simplification."""
    x = sp.symbols('x', positive=True)
    expr = sp.atan((sp.sqrt(1 + x**2) - 1)/x)
    simplified = simplify_arctan_half_angle(expr)
    
    # Test with negative value - should maintain numeric equality
    test_val = -1
    original_numeric = float(expr.subs(x, test_val).evalf())
    simplified_numeric = float(simplified.subs(x, test_val).evalf())
    
    # They should be equal numerically even for negative input 
    # (the Piecewise should handle this correctly)
    assert abs(original_numeric - simplified_numeric) < 1e-10

def test_double_angle_identity_at_half():
    """Test the double-angle identity at x=1/2 -> pi/3."""
    x = sp.Rational(1, 2)
    expr = sp.atan((2*x*sp.sqrt(1 - x**2)) / (1 - 2*x**2))
    simplified = simplify_arctan_double_angle_at_half(expr)
    assert sp.simplify(simplified - sp.pi/3) == 0

def test_double_angle_identity_other_values():
    """Test that double-angle identity leaves other values unchanged."""
    x = sp.Rational(1, 3)  # Not 1/2
    expr = sp.atan((2*x*sp.sqrt(1 - x**2)) / (1 - 2*x**2))
    simplified = simplify_arctan_double_angle_at_half(expr)
    # Should remain unchanged since x != 1/2
    assert simplified == expr

def test_combined_optimizations():
    """Test that apply_arctan_optimizations applies all optimizations."""
    x = sp.symbols('x', positive=True)
    
    # Expression with half-angle pattern
    expr1 = sp.atan((sp.sqrt(1 + x**2) - 1)/x)
    result1 = apply_arctan_optimizations(expr1)
    assert sp.simplify(result1 - sp.atan(x)/2) == 0
    
    # Expression with double-angle pattern at x=1/2
    expr2 = sp.atan((2*sp.Rational(1,2)*sp.sqrt(1 - sp.Rational(1,2)**2)) / (1 - 2*sp.Rational(1,2)**2))
    result2 = apply_arctan_optimizations(expr2)
    assert sp.simplify(result2 - sp.pi/3) == 0

def test_numerical_precision_high_dps():
    """Test numerical precision with mpmath high precision."""
    mp.mp.dps = 50
    
    # Test double-angle identity numerically  
    x_val = mp.mpf(0.5)
    lhs = mp.atan((2*x_val*mp.sqrt(1 - x_val*x_val)) / (1 - 2*x_val*x_val))
    rhs = mp.pi / 3
    assert mp.almosteq(lhs, rhs, rel_eps=mp.mpf('1e-45'), abs_eps=mp.mpf('1e-45'))