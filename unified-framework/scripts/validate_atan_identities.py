# scripts/validate_atan_identities.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mpmath as mp
import sympy as sp

# Direct import to avoid package initialization issues
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core', 'symbolic'))
from atan_opt import simplify_arctan_half_angle, atan_half_angle_derivative

def main():
    mp.mp.dps = 50
    x = sp.symbols('x', positive=True)

    # Identity 1: simplification and derivative
    expr = sp.atan((sp.sqrt(1 + x**2) - 1)/x)
    simplified = simplify_arctan_half_angle(expr)
    print("Simplified form:", simplified)  # expected atan(x)/2

    dexpr = sp.diff(expr, x)
    target = atan_half_angle_derivative(x)
    print("Derivative equal to 1/(2*(1+x^2)) ?",
          sp.simplify(dexpr - target) == 0)

    # Numeric spot-checks
    for val in [0.1, 0.5, 1, 2, 10]:
        lhs = mp.atan((mp.sqrt(1 + val*val) - 1)/val)
        rhs = 0.5 * mp.atan(val)
        delta = abs(lhs - rhs)
        print(f"x={val}: Δ={float(delta):.3e}")

    # Identity 2: specific evaluation
    s = sp.Rational(1, 2)
    expr2 = sp.atan((2*s*sp.sqrt(1 - s**2)) / (1 - 2*s**2))
    print("Second identity at x=1/2:", sp.simplify(expr2))  # expected pi/3

if __name__ == "__main__":
    main()