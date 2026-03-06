import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mpmath
from sympy import isprime  # For prime check if needed
from sympy.ntheory import divisor_count  # For d(n)

mpmath.mp.dps = 15  # Reduced for speed

# Constants from Z model
PHI = (1 + math.sqrt(5)) / 2
K_STAR = 0.3
E2 = math.exp(2)

# Adapted from vortex_filter.py: Compute frame shift with theta_prime
def compute_frame_shift(n):
    if n <= 1:
        return 0.0
    mod = n % PHI
    theta_prime = PHI * (mod / PHI) ** K_STAR
    d_n = divisor_count(n)
    kappa = d_n * theta_prime
    ln_term = math.log(n + 1)
    delta_n = kappa * ln_term / E2
    delta_max = PHI  # Geometric bound
    return delta_n / delta_max

# From domain.py: UniversalZetaShift base class (simplified for integration)
class UniversalZetaShift:
    def __init__(self, a, b, c):
        if a == 0 or b == 0 or c == 0:
            raise ValueError("Parameters cannot be zero.")
        self.a = a
        self.b = b
        self.c = c

    def compute_z(self):
        return self.a * (self.b / self.c)

# DiscreteZetaShift adapted for prime shifts
class DiscreteZetaShift(UniversalZetaShift):
    def __init__(self, n, v=1.0, delta_max=PHI):  # Use PHI as default bound
        if n <= 1:
            super().__init__(a=n, b=0, c=delta_max)
        else:
            delta_n = v * (divisor_count(n) * math.log(n + 1) / E2)
            super().__init__(a=n, b=delta_n, c=delta_max)

# Efficient prime generation using Sieve of Eratosthenes
def generate_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(math.sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return [n for n in range(2, limit + 1) if sieve[n]]

# Generate first 100 primes (adjusted for computation)
primes = generate_primes(110000)[:100]

# Compute Z-shifts using DiscreteZetaShift and frame shift
Z_list = []
for p in primes:
    zeta = DiscreteZetaShift(p)
    frame_shift = compute_frame_shift(p)
    z_shift = zeta.compute_z() * frame_shift  # Geometric scaling
    Z_list.append(z_shift)

# Compute first 100 non-trivial zeros' imaginary parts
known_zeros_im = [float(mpmath.im(mpmath.zetazero(n))) for n in range(1, 101)]

# Unfold zeros for helical alignment
unfolded_zeros = []
for t in known_zeros_im:
    if t > 0:
        log_term = math.log(t / (2 * math.pi * math.e))
        if log_term > 0:  # Avoid log(negative)
            unfolded_t = t / (2 * math.pi * log_term)
            theta_zero = 2 * math.pi * unfolded_t / PHI  # Helical warp
            unfolded_zeros.append(theta_zero)

# Set up coarser grid for surface
max_imag = max(Z_list) * 1.1 if Z_list else 100
real = np.linspace(0.1, 1.2, 20)  # Coarser
imag = np.linspace(0, max_imag, 50)  # Coarser
Re, Im = np.meshgrid(real, imag)

# Compute log|zeta| on grid
zeta_mag = np.zeros(Re.shape)
for i in range(Re.shape[0]):
    for j in range(Re.shape[1]):
        s = complex(Re[i, j], Im[i, j])
        zeta = mpmath.zeta(s)
        abs_zeta = abs(zeta)
        zeta_mag[i, j] = float(mpmath.log(abs_zeta)) if abs_zeta > 0 else -10

# Plot the surface
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(Re, Im, zeta_mag, cmap='viridis', alpha=0.7)

# Add colorbar
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='log|ζ(s)|')

# Overlay frame-shifted primes (subsample every 10th for clarity)
for idx, z_im in enumerate(Z_list[::10]):
    s = complex(0.5, z_im)
    zeta = mpmath.zeta(s)
    abs_zeta = abs(zeta)
    log_abs = float(mpmath.log(abs_zeta)) if abs_zeta > 0 else -10
    adjusted_log = log_abs * (z_im / PHI)  # Geometric adjustment
    ax.scatter(0.5, z_im, adjusted_log, c='red', s=50, edgecolor='gold', label='Shifted Primes' if idx == 0 else None)

# Overlay unfolded zeros (subsample every 10th)
min_log = np.min(zeta_mag) - 5
for idx, t_zero in enumerate(unfolded_zeros[::10]):
    if t_zero <= max_imag:
        ax.scatter(0.5, t_zero, min_log, c='blue', s=100, marker='x', label='Unfolded Zeros' if idx == 0 else None)

ax.set_title('Riemann Zeta Landscape: Curvature-Adjusted Frame-Shifted Primes and Helically Unfolded Zeros')
ax.set_xlabel('Real Part')
ax.set_ylabel('Imaginary Part (Z-Shifted for Primes, Unfolded for Zeros)')
ax.set_zlabel('log|ζ(s)| (Geometrically Scaled)')
ax.legend()
ax.view_init(elev=30, azim=135)
plt.show()