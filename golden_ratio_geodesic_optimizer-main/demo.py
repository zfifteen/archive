import math
import sympy as sp
import mpmath as mp
from golden_ratio_geodesic_optimizer import theta_prime, kappa

mp.mp.dps = 50  # Precision

phi = (1 + math.sqrt(5)) / 2

# Sample: Compute for n=899 (semiprime 29*31)
n = 899
print(f"θ′({n}, 0.3): {theta_prime(n):.10f}")
print(f"κ({n}): {kappa(n):.10f}")

# Symbolic validation (half-angle example)
theta = sp.symbols('theta')
half_angle = sp.tan(theta/2)
print(sp.simplify(half_angle))  # Demo; extend for geodesic