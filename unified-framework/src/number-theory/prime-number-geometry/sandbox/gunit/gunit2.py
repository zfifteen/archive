from mpmath import mp, mpf, gamma, pi, zeta, quad, cos, log
import matplotlib.pyplot as plt
import numpy as np

# Set decimal precision
mp.dps = 10  # Increased precision for better accuracy
print(f"Working precision: {mp.dps} decimal digits\n")

# Precompute ξ(1/2) - constant for all calculations
XI_HALF = None

def xi(s):
    """Riemann Xi function with analytic continuation."""
    global XI_HALF
    result = 0.5*s*(s-1) * pi**(-s/2) * gamma(s/2) * zeta(s)

    # Cache ξ(1/2) since it's used repeatedly
    if s == 0.5 and XI_HALF is None:
        XI_HALF = result
    return result

def f(t):
    """Compute the function f(t) = ξ(1/2)/(2π) ∫[ -∞ to ∞ ] cos(tx)/ξ(1/2 + ix) dx."""
    # Define complex integrand (real-valued due to symmetry)
    def integrand(x):
        s_val = mpf('0.5') + 1j*mpf(x)
        return cos(t*x) / xi(s_val)

    # Integrate with adaptive quadrature (wider range than original)
    integral = quad(integrand, [-20, 20], error=True)
    integral_value = integral[0].real  # Discard imaginary part (should be near zero)

    # Calculate final value using precomputed ξ(1/2)
    return (XI_HALF / (2 * pi)) * integral_value

# Main computation
if __name__ == "__main__":
    # Precompute ξ(1/2) by calling xi(0.5)
    _ = xi(mpf('0.5'))
    print(f"ξ(1/2) = {XI_HALF}\n")

    # Evaluate f(t) at critical points
    ts = [mpf(t) for t in [-0.8, 0, 0.8]]
    fs = [f(t) for t in ts]

    print("f(t) values:")
    for t, val in zip(ts, fs):
        print(f"f({t}) = {val:.12e}")
        if val <= 0:
            print("  Warning: Non-positive value detected!")

    # Compute integral over [-1,1]
    integral_f, error = quad(f, [-1, 1], error=True)
    print(f"\n∫f(t)dt over [-1,1] = {integral_f:.15f} ± {error:.2e}")
    print(f"Deviation from 1: {abs(1 - integral_f):.2e}\n")

    # Log-concavity check with correct step size
    log_fs = [log(val) for val in fs]
    h = mpf('0.8')  # Actual step size between t-values
    second_diffs = []
    for i in range(1, len(log_fs)-1):
        diff = (log_fs[i-1] - 2*log_fs[i] + log_fs[i+1]) / (h**2)
        second_diffs.append(diff)

    print("Second differences of log(f(t)) (should be negative for log-concavity):")
    for i, diff in enumerate(second_diffs):
        print(f"At t={ts[1]}: {diff:.6f} {'✓' if diff < 0 else '✗'}")