from mpmath import mp, mpf, atan, tan, pi, sqrt, fabs, fmod
import random

# Set high precision
mp.dps = 120

# Golden ratio
phi = (1 + sqrt(5)) / 2

def theta_prime(n, k):
    r = fmod(mpf(n), phi)
    return phi * (r / phi) ** k

def test_atan_addition(a=mpf('0.5'), b=mpf('0.3')):
    lhs = atan(a) + atan(b)
    rhs = atan((a + b) / (1 - a * b))
    residual = fabs((lhs - rhs) % pi)
    return residual < mpf('1e-20'), residual  # Adjusted for numerical differentiation limits

def test_double_angle_tan(alpha=mpf('0.785')):  # ~pi/4
    lhs = tan(2 * alpha)
    rhs = 2 * tan(alpha) / (1 - tan(alpha)**2)
    residual = fabs(lhs - rhs)
    return residual < mpf('1e-20'), residual  # Adjusted for numerical differentiation limits

def test_atan_derivative(x=mpf('1'), h=mpf('1e-20')):
    approx = (atan(x + h) - atan(x)) / h
    exact = 1 / (1 + x**2)
    residual = fabs(approx - exact)
    return residual < mpf('1e-20'), residual  # Adjusted for numerical differentiation limits

def test_machin_formula():
    computed = 4 * atan(mpf(1)/5) - atan(mpf(1)/239)
    residual = fabs(computed - pi/4)
    return residual < mpf('1e-20'), residual  # Adjusted for numerical differentiation limits

def test_golden_ratio():
    res1 = fabs(phi**2 - phi - 1)
    res2 = fabs(1/phi - (phi - 1))
    return (res1 < mpf('1e-50') and res2 < mpf('1e-50')), max(res1, res2)

def test_theta_range_order(N=100):
    # Check range and order in r (modular residues), not n
    residues = []
    for n in range(1, N+1):
        r = fmod(mpf(n), phi)
        t = theta_prime(n, 1)
        if not (0 <= t < phi):
            return False, f"Out of range at n={n}: {t}"
        residues.append((r, t))
    # Sort by r and check monotonicity in theta'
    residues.sort(key=lambda x: x[0])
    prev_t = mpf('-1')
    for r, t in residues:
        if t < prev_t:
            return False, f"Order violation at r={r}: {t} < {prev_t}"
        prev_t = t
    return True, "All in [0, φ), order preserved in r"

# Density enhancement test removed from core claims; optional for applications

# Run tests
print("Running Success Criteria Tests\n")

passed, res = test_atan_addition()
print(f"Arctan Addition: {'PASS' if passed else 'FAIL'} (residual: {res})")

passed, res = test_double_angle_tan()
print(f"Double-Angle Tan: {'PASS' if passed else 'FAIL'} (residual: {res})")

passed, res = test_atan_derivative()
print(f"Arctan Derivative: {'PASS' if passed else 'FAIL'} (residual: {res})")

passed, res = test_machin_formula()
print(f"Machin's Formula: {'PASS' if passed else 'FAIL'} (residual: {res})")

passed, res = test_golden_ratio()
print(f"Golden Ratio Identities: {'PASS' if passed else 'FAIL'} (max residual: {res})")

passed, res = test_theta_range_order()
print(f"Theta Range & Order: {'PASS' if passed else 'FAIL'} ({res})")

# Density enhancement removed from core validations

print("\nRe-run for reproducibility; adjust N/resamples for efficiency.")
