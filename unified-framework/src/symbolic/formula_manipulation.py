"""
Formula Manipulation Module
===========================

Advanced SymPy-based formula manipulation, simplification, and symbolic
computation utilities for the Z Framework.
"""

import sympy as sp
import numpy as np
from sympy import symbols, simplify, expand, factor, collect, cancel, apart
from sympy import trigsimp, powsimp, radsimp, together, separatevars
from sympy import series, limit, diff, integrate, solve, solveset
from sympy import Matrix, Poly, degree, LC, groebner
from sympy.abc import x, y, z, t, n, k
from sympy.physics.units import c as speed_of_light

def simplify_zeta_shift(zeta_expression, target_form='factored'):
    """
    Simplify zeta shift expressions using various SymPy techniques.
    
    Args:
        zeta_expression: SymPy expression representing zeta shift computation
        target_form: 'factored', 'expanded', 'collected', or 'simplified'
        
    Returns:
        dict: Various simplified forms of the expression
    """
    if isinstance(zeta_expression, str):
        zeta_expression = sp.sympify(zeta_expression)
    
    # Apply different simplification strategies
    simplified = simplify(zeta_expression)
    expanded = expand(zeta_expression)
    factored = factor(zeta_expression)
    
    # Collect terms by specific variables
    collected_n = collect(zeta_expression, n)
    collected_k = collect(zeta_expression, k) if k in zeta_expression.free_symbols else zeta_expression
    
    # Trigonometric simplification if applicable
    trig_simplified = trigsimp(zeta_expression)
    
    # Power simplification
    power_simplified = powsimp(zeta_expression)
    
    # Rational simplification
    rational_simplified = cancel(zeta_expression)
    
    result = {
        'original': zeta_expression,
        'simplified': simplified,
        'expanded': expanded,
        'factored': factored,
        'collected_n': collected_n,
        'collected_k': collected_k,
        'trigonometric': trig_simplified,
        'power_form': power_simplified,
        'rational_form': rational_simplified,
        'complexity_score': sp.count_ops(simplified)
    }
    
    # Return the requested target form
    if target_form in result:
        result['target'] = result[target_form]
    else:
        result['target'] = simplified
    
    return result

def expand_geometric_series(expression, variable=None, order=10):
    """
    Expand expressions as geometric series for asymptotic analysis.
    
    Args:
        expression: SymPy expression to expand
        variable: Variable to expand around (default: auto-detect)
        order: Order of series expansion
        
    Returns:
        dict: Series expansion and convergence analysis
    """
    if isinstance(expression, str):
        expression = sp.sympify(expression)
    
    if variable is None:
        # Auto-detect the main variable
        free_vars = expression.free_symbols
        if n in free_vars:
            variable = n
        elif x in free_vars:
            variable = x
        else:
            variable = list(free_vars)[0] if free_vars else n
    
    # Series expansion around infinity (for large n behavior)
    series_inf = series(expression, variable, sp.oo, n=order)
    
    # Series expansion around 0 (for small variable behavior)
    series_zero = series(expression, variable, 0, n=order)
    
    # Series expansion around 1 (for perturbative analysis)
    try:
        series_one = series(expression, variable, 1, n=order)
    except:
        series_one = None
    
    # Extract leading term and asymptotic behavior
    leading_term = series_inf.removeO().as_leading_term(variable)
    
    # Check for geometric series pattern
    is_geometric = False
    geometric_ratio = None
    
    try:
        # Try to identify if it's a geometric series
        expanded = expand(expression)
        coeffs = sp.Poly(expanded, variable).all_coeffs()
        if len(coeffs) > 1:
            ratios = [coeffs[i+1]/coeffs[i] for i in range(len(coeffs)-1)]
            if all(sp.simplify(r - ratios[0]) == 0 for r in ratios):
                is_geometric = True
                geometric_ratio = ratios[0]
    except:
        pass
    
    return {
        'original': expression,
        'series_at_infinity': series_inf,
        'series_at_zero': series_zero,
        'series_at_one': series_one,
        'leading_term': leading_term,
        'expansion_variable': variable,
        'expansion_order': order,
        'is_geometric_series': is_geometric,
        'geometric_ratio': geometric_ratio,
        'convergence_radius': None  # Would need more sophisticated analysis
    }

def factor_polynomial_expressions(expression, domain='ZZ'):
    """
    Factor polynomial expressions using various algebraic techniques.
    
    Args:
        expression: SymPy expression to factor
        domain: Algebraic domain ('ZZ', 'QQ', 'RR', 'CC')
        
    Returns:
        dict: Factorization results and algebraic analysis
    """
    if isinstance(expression, str):
        expression = sp.sympify(expression)
    
    # Basic factorization
    factored = factor(expression, domain=domain)
    
    # Collect variables for polynomial analysis
    variables = list(expression.free_symbols)
    
    if not variables:
        return {
            'original': expression,
            'factored': factored,
            'is_polynomial': False,
            'variables': []
        }
    
    result = {
        'original': expression,
        'factored': factored,
        'variables': variables,
        'domain': domain
    }
    
    # Analyze as polynomial in each variable
    for var in variables:
        try:
            poly = Poly(expression, var, domain=domain)
            result[f'polynomial_in_{var}'] = {
                'degree': degree(poly),
                'leading_coefficient': LC(poly),
                'coefficients': poly.all_coeffs(),
                'roots': solve(expression, var),
                'is_monic': poly.is_monic,
                'is_irreducible': poly.is_irreducible
            }
        except:
            result[f'polynomial_in_{var}'] = None
    
    # Multivariate polynomial analysis
    if len(variables) > 1:
        try:
            poly_multi = Poly(expression, variables, domain=domain)
            result['multivariate'] = {
                'total_degree': poly_multi.total_degree(),
                'is_homogeneous': poly_multi.is_homogeneous,
                'length': len(poly_multi.as_dict()),
                'ground_domain': poly_multi.get_domain()
            }
        except:
            result['multivariate'] = None
    
    # Groebner basis (for ideal-theoretic analysis)
    if len(variables) > 1:
        try:
            # Create a simple ideal for demonstration
            ideal_generators = [expression]
            gb = groebner(ideal_generators, variables, domain=domain)
            result['groebner_basis'] = gb
        except:
            result['groebner_basis'] = None
    
    result['is_polynomial'] = True
    return result

def manipulate_curvature_expressions(curvature_formula, operation='simplify'):
    """
    Specialized manipulation of curvature expressions κ(n) = d(n) * ln(n+1) / e².
    
    Args:
        curvature_formula: Curvature expression to manipulate
        operation: 'simplify', 'expand', 'asymptotic', 'differential'
        
    Returns:
        dict: Manipulated curvature expressions and analysis
    """
    if isinstance(curvature_formula, str):
        curvature_formula = sp.sympify(curvature_formula)
    
    result = {
        'original': curvature_formula,
        'operation': operation
    }
    
    if operation == 'simplify':
        result['simplified'] = simplify(curvature_formula)
        result['factored'] = factor(curvature_formula)
        result['expanded'] = expand(curvature_formula)
    
    elif operation == 'asymptotic':
        # Asymptotic expansion for large n
        n_sym = symbols('n', positive=True)
        d_n = symbols('d_n', positive=True)
        
        # Substitute asymptotic form of ln(n+1) ≈ ln(n) for large n
        asymptotic = curvature_formula.subs(sp.log(n_sym + 1), sp.log(n_sym))
        result['asymptotic_large_n'] = asymptotic
        
        # Series expansion
        try:
            series_expansion = series(curvature_formula, n_sym, sp.oo, n=5)
            result['series_expansion'] = series_expansion
        except:
            result['series_expansion'] = None
    
    elif operation == 'differential':
        # Derivatives for curvature analysis
        n_sym = symbols('n', positive=True)
        
        # First derivative (curvature gradient)
        first_derivative = diff(curvature_formula, n_sym)
        result['curvature_gradient'] = first_derivative
        
        # Second derivative (curvature acceleration)
        second_derivative = diff(first_derivative, n_sym)
        result['curvature_acceleration'] = second_derivative
        
        # Critical points (where gradient = 0)
        critical_points = solve(first_derivative, n_sym)
        result['critical_points'] = critical_points
        
        # Limits at infinity
        limit_inf = limit(curvature_formula, n_sym, sp.oo)
        result['limit_at_infinity'] = limit_inf
    
    elif operation == 'expand':
        result['expanded'] = expand(curvature_formula)
        result['expanded_log'] = expand_log(curvature_formula, force=True)
        result['expanded_power'] = expand_power_exp(curvature_formula)
    
    return result

def transform_golden_ratio_expressions(expression, form='exact'):
    """
    Transform expressions involving the golden ratio φ = (1+√5)/2.
    
    Args:
        expression: Expression containing golden ratio
        form: 'exact', 'numerical', 'continued_fraction', 'polynomial'
        
    Returns:
        dict: Various representations of golden ratio expressions
    """
    if isinstance(expression, str):
        expression = sp.sympify(expression)
    
    # Define golden ratio symbolically
    phi_exact = (1 + sp.sqrt(5)) / 2
    phi_sym = symbols('phi', positive=True)
    
    result = {
        'original': expression,
        'phi_exact': phi_exact,
        'target_form': form
    }
    
    if form == 'exact':
        # Substitute exact golden ratio value
        exact_form = expression.subs(phi_sym, phi_exact)
        result['exact'] = simplify(exact_form)
        result['rationalized'] = radsimp(exact_form)
    
    elif form == 'numerical':
        # High-precision numerical evaluation
        numerical = expression.subs(phi_sym, phi_exact).evalf(50)
        result['numerical'] = numerical
        result['float_value'] = float(numerical) if numerical.is_real else complex(numerical)
    
    elif form == 'continued_fraction':
        # Golden ratio continued fraction [1; 1, 1, 1, ...]
        cf_terms = [1] + [1] * 10  # First 10 terms
        cf_approximations = []
        
        for i in range(1, len(cf_terms) + 1):
            cf_approx = sp.continued_fraction_convergents(cf_terms[:i])[-1]
            cf_approximations.append(cf_approx)
        
        result['continued_fraction'] = cf_terms
        result['cf_convergents'] = cf_approximations
        result['cf_error'] = [sp.Abs(cf - phi_exact).evalf() for cf in cf_approximations]
    
    elif form == 'polynomial':
        # Golden ratio satisfies φ² = φ + 1
        phi_polynomial = phi_sym**2 - phi_sym - 1
        result['minimal_polynomial'] = phi_polynomial
        
        # Reduce higher powers using φ² = φ + 1
        reduced = expression
        for power in range(10, 1, -1):  # Reduce from highest to lowest power
            reduced = reduced.subs(phi_sym**power, 
                                 expand(phi_sym**(power-2) * (phi_sym + 1)))
        
        result['reduced_polynomial'] = simplify(reduced)
    
    # Fibonacci connection: F_n/F_{n-1} → φ as n → ∞
    F = sp.Function('F')  # Fibonacci function
    fibonacci_ratio = F(n) / F(n-1)
    result['fibonacci_limit'] = limit(fibonacci_ratio, n, sp.oo)
    
    return result

def manipulate_5d_expressions(expression_5d, coordinate_system='cartesian'):
    """
    Manipulate expressions in 5D spacetime coordinates.
    
    Args:
        expression_5d: 5D spacetime expression
        coordinate_system: 'cartesian', 'spherical', 'cylindrical'
        
    Returns:
        dict: Coordinate transformations and geometric analysis
    """
    if isinstance(expression_5d, str):
        expression_5d = sp.sympify(expression_5d)
    
    # Define 5D coordinates
    x, y, z, w, u = symbols('x y z w u', real=True)
    
    result = {
        'original': expression_5d,
        'coordinate_system': coordinate_system,
        'coordinates': [x, y, z, w, u]
    }
    
    if coordinate_system == 'cartesian':
        # Already in Cartesian form
        result['cartesian'] = expression_5d
        
        # Compute gradients in each direction
        gradients = [diff(expression_5d, coord) for coord in [x, y, z, w, u]]
        result['gradients'] = gradients
        
        # Laplacian (if expression is scalar)
        if not expression_5d.has(Matrix):
            laplacian = sum(diff(expression_5d, coord, 2) for coord in [x, y, z, w, u])
            result['laplacian'] = laplacian
    
    elif coordinate_system == 'spherical':
        # 5D spherical coordinates: (r, θ, φ, ψ, χ)
        r, theta, phi, psi, chi = symbols('r theta phi psi chi', real=True, positive=True)
        
        # Coordinate transformation
        x_spherical = r * sp.cos(theta)
        y_spherical = r * sp.sin(theta) * sp.cos(phi)
        z_spherical = r * sp.sin(theta) * sp.sin(phi) * sp.cos(psi)
        w_spherical = r * sp.sin(theta) * sp.sin(phi) * sp.sin(psi) * sp.cos(chi)
        u_spherical = r * sp.sin(theta) * sp.sin(phi) * sp.sin(psi) * sp.sin(chi)
        
        # Transform expression
        transformed = expression_5d.subs([
            (x, x_spherical), (y, y_spherical), (z, z_spherical),
            (w, w_spherical), (u, u_spherical)
        ])
        
        result['spherical'] = simplify(transformed)
        result['spherical_coordinates'] = [r, theta, phi, psi, chi]
    
    elif coordinate_system == 'cylindrical':
        # 5D cylindrical coordinates with mixed approach
        rho, phi_cyl, z_cyl, w_cyl, u_cyl = symbols('rho phi_cyl z_cyl w_cyl u_cyl', real=True)
        
        # Cylindrical transformation for first 3 coordinates
        x_cyl = rho * sp.cos(phi_cyl)
        y_cyl = rho * sp.sin(phi_cyl)
        z_cylindrical = z_cyl
        w_cylindrical = w_cyl
        u_cylindrical = u_cyl
        
        transformed = expression_5d.subs([
            (x, x_cyl), (y, y_cyl), (z, z_cylindrical),
            (w, w_cylindrical), (u, u_cylindrical)
        ])
        
        result['cylindrical'] = simplify(transformed)
        result['cylindrical_coordinates'] = [rho, phi_cyl, z_cyl, w_cyl, u_cyl]
    
    # Symmetry analysis
    symmetries = []
    for i, coord in enumerate([x, y, z, w, u]):
        # Test for even/odd symmetry in each coordinate
        neg_substitution = expression_5d.subs(coord, -coord)
        if simplify(neg_substitution - expression_5d) == 0:
            symmetries.append(f'even_in_{["x","y","z","w","u"][i]}')
        elif simplify(neg_substitution + expression_5d) == 0:
            symmetries.append(f'odd_in_{["x","y","z","w","u"][i]}')
    
    result['symmetries'] = symmetries
    
    return result

def optimize_symbolic_computation(expression, optimization_target='speed'):
    """
    Optimize symbolic expressions for computational efficiency.
    
    Args:
        expression: SymPy expression to optimize
        optimization_target: 'speed', 'memory', 'accuracy', 'readability'
        
    Returns:
        dict: Optimized expression forms and performance metrics
    """
    if isinstance(expression, str):
        expression = sp.sympify(expression)
    
    result = {
        'original': expression,
        'optimization_target': optimization_target,
        'original_complexity': sp.count_ops(expression)
    }
    
    if optimization_target == 'speed':
        # Simplify for computational speed
        speed_optimized = simplify(expression)
        speed_optimized = powsimp(speed_optimized)  # Combine powers
        speed_optimized = trigsimp(speed_optimized)  # Simplify trig functions
        
        result['speed_optimized'] = speed_optimized
        result['speed_complexity'] = sp.count_ops(speed_optimized)
        result['complexity_reduction'] = result['original_complexity'] - result['speed_complexity']
    
    elif optimization_target == 'memory':
        # Factor to reduce memory usage
        memory_optimized = factor(expression)
        memory_optimized = collect(memory_optimized, list(expression.free_symbols))
        
        result['memory_optimized'] = memory_optimized
        result['memory_complexity'] = sp.count_ops(memory_optimized)
    
    elif optimization_target == 'accuracy':
        # Maintain highest precision, minimal simplification
        accuracy_optimized = cancel(expression)  # Only cancel rational functions
        result['accuracy_optimized'] = accuracy_optimized
        result['accuracy_complexity'] = sp.count_ops(accuracy_optimized)
    
    elif optimization_target == 'readability':
        # Optimize for human readability
        readable = collect(expression, list(expression.free_symbols))
        readable = factor(readable)
        readable = trigsimp(readable)
        
        result['readable_optimized'] = readable
        result['readable_complexity'] = sp.count_ops(readable)
    
    return result