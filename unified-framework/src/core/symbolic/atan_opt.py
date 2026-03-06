# src/core/symbolic/atan_opt.py
"""
Arctan half-angle identities and a lightweight symbolic optimizer.

Identities used
---------------
1) atan((sqrt(1 + u**2) - 1)/u) = (1/2)*atan(u),  (u > 0)
   => d/du = 1/(2*(1 + u**2))

2) atan( (2*x*sqrt(1 - x**2)) / (1 - 2*x**2) ) at x=1/2 = pi/3

Notes
-----
- We keep the optimizer minimal and local: no global rewrites.
- Safe for use anywhere we build small symbolic expressions that may include the
  recognizable half-angle arctan structure.

Usage
-----
>>> import sympy as sp
>>> from src.core.symbolic.atan_opt import simplify_arctan_half_angle
>>> x = sp.symbols('x', positive=True)
>>> expr = sp.atan((sp.sqrt(1 + x**2) - 1)/x)
>>> simplify_arctan_half_angle(expr)
atan(x)/2
"""
from __future__ import annotations
import sympy as sp

def simplify_arctan_half_angle(expr: sp.Expr) -> sp.Expr:
    """
    Replace atan((sqrt(1 + u**2) - 1)/u) with (1/2)*atan(u) when matched,
    but only when u is provably positive under SymPy assumptions.

    Parameters
    ----------
    expr : sp.Expr
        A sympy expression.

    Returns
    -------
    sp.Expr
        Expression with the specific arctan half-angle pattern simplified.
        If u is not provably positive, returns a Piecewise expression or
        keeps the original form.
    """
    u = sp.Wild('u')
    pattern_arg = (sp.sqrt(1 + u**2) - 1) / u

    def _is_target(e: sp.Expr) -> bool:
        return isinstance(e, sp.atan) and e.args and e.args[0].match(pattern_arg)

    def _rewrite(e: sp.Expr) -> sp.Expr:
        m = e.args[0].match(pattern_arg)
        u_val = m[u]
        
        # Only rewrite if u is provably positive
        if sp.ask(sp.Q.positive(u_val)) is True:
            return sp.Rational(1, 2) * sp.atan(u_val)
        else:
            # Return Piecewise for safety when positivity is unknown
            return sp.Piecewise(
                (sp.Rational(1, 2) * sp.atan(u_val), sp.Q.positive(u_val)),
                (e, True)
            )

    return expr.replace(_is_target, _rewrite)


def atan_half_angle_derivative(u: sp.Symbol | sp.Expr) -> sp.Expr:
    """
    Closed form derivative of (1/2)*atan(u): 1/(2*(1 + u**2))
    """
    return 1 / (2 * (1 + u**2))


def simplify_arctan_double_angle_at_half(expr: sp.Expr) -> sp.Expr:
    """
    Replace atan((2*x*sqrt(1 - x**2))/(1 - 2*x**2)) at x=1/2 with π/3.
    
    This identity specifically targets the double-angle arctan expression
    that evaluates to π/3 when x = 1/2.
    
    Parameters
    ----------
    expr : sp.Expr
        A sympy expression.
    
    Returns
    -------
    sp.Expr
        Expression with the specific double-angle arctan pattern simplified
        to π/3 when x = 1/2.
    """
    x = sp.Wild('x')
    pattern_arg = (2*x*sp.sqrt(1 - x**2)) / (1 - 2*x**2)
    
    def _is_target(e: sp.Expr) -> bool:
        return isinstance(e, sp.atan) and e.args and e.args[0].match(pattern_arg)
    
    def _rewrite(e: sp.Expr) -> sp.Expr:
        m = e.args[0].match(pattern_arg)
        if m and x in m:
            x_val = m[x]
            # Check if x = 1/2
            if x_val == sp.Rational(1, 2):
                return sp.pi / 3
            else:
                # For other values, keep the original expression
                return e
        return e
    
    return expr.replace(_is_target, _rewrite)


def apply_arctan_optimizations(expr: sp.Expr) -> sp.Expr:
    """
    Apply all available arctan optimizations to an expression.
    
    This function sequentially applies:
    1. Half-angle identity simplification
    2. Double-angle identity at x=1/2 simplification
    
    Parameters
    ----------
    expr : sp.Expr
        A sympy expression that may contain arctan terms.
    
    Returns
    -------
    sp.Expr
        Expression with all applicable arctan optimizations applied.
    """
    # Apply half-angle simplification first
    result = simplify_arctan_half_angle(expr)
    
    # Apply double-angle simplification
    result = simplify_arctan_double_angle_at_half(result)
    
    return result