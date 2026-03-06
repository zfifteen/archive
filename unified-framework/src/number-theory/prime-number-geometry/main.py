import math
from cProfile import label

import numpy as np
import matplotlib.pyplot as plt
import scipy
from mpl_toolkits.mplot3d import Axes3D

# Choose your universal constant
UNIVERSAL = math.e

class Numberspace:
    def __init__(self, B: float, C: float = UNIVERSAL):
        if B == 0:
            raise ValueError("B cannot be zero")
        self._B = B
        self._C = C

    def __call__(self, value: float) -> float:
        return value * (self._B / self._C)

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# Parameters
N_POINTS = 5000


# HELIX_FREQ = scipy.constants.golden_ratio   # you can tweak this ratio
HELIX_FREQ = .1003033  # you can tweak this ratio

LOG_SCALE = False     # toggle for log scaling on Y-axis

# Instantiate your transformer with a fixed B
transformer = Numberspace(B=math.e)  # e.g. scale factor base = 2

# Generate data
n = np.arange(1, N_POINTS)
primality = np.vectorize(is_prime)(n)

# Y-values: choose raw, log, or polynomial
if LOG_SCALE:
    y_raw = np.log(n, where=(n>1), out=np.zeros_like(n, dtype=float))
else:
    y_raw = n * (n / math.pi)

# Apply your Numberspace transform
y = transformer(y_raw)

# Z-values for the helix
z = np.sin( math.pi * HELIX_FREQ * n )

# Split into primes vs non-primes
x_primes   = n[primality]
y_primes   = y[primality]
z_primes   = z[primality]

x_nonprimes = n[~primality]
y_nonprimes = y[~primality]
z_nonprimes = z[~primality]

# Plot
fig = plt.figure(figsize=(12, 8))
ax  = fig.add_subplot(111, projection='3d')

ax.scatter(x_nonprimes, y_nonprimes, z_nonprimes,
           c='blue', alpha=0.3, s=10, label='Non-primes')

ax.scatter(x_primes, y_primes, z_primes,
           c='red', marker='*', s=50, label='Primes')

ax.set_xlabel('n (Position)')
ax.set_ylabel('Scaled Value')
ax.set_zlabel('Helical Coord')
ax.set_title('3D Prime Geometry Visualization')
ax.legend()

# If you want a log‐scaled axis instead of pre‐transform:
# ax.set_yscale('log')

plt.tight_layout()
plt.show()

# Logarithmic spiral with prime angles
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

angle = n * 0.1 * math.pi
radius = np.log(n)

x = radius * np.cos(angle)
y = radius * np.sin(angle)
z = np.sqrt(n)  # Height shows magnitude

ax.scatter(x[~primality], y[~primality], z[~primality], c='blue', alpha=0.3, s=10)
ax.scatter(x[primality], y[primality], z[primality], c='red', marker='*', s=50, label='Primes')

ax.set_title('Prime Angles in Logarithmic Spiral')
ax.set_xlabel('X (Real)')
ax.set_ylabel('Y (Imaginary)')
ax.set_zlabel('√n (Magnitude)')
plt.show()

# Prime probability waves
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

density = np.zeros(N_POINTS-1)
for i in range(1, N_POINTS):
    density[i-1] = np.sum(primality[:i]) / i  # Cumulative prime density

# Modular arithmetic prime clusters
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

mod_base = 30  # Highly composite number
mod_x = n % mod_base
mod_y = (n // mod_base) % mod_base
z = np.log(n)

# Create a color map for residue classes
colors = np.where(primality, 'red',
                  np.where(np.gcd(n, mod_base) > 1, 'purple', 'blue'))

ax.scatter(mod_x, mod_y, z, c=colors, alpha=0.7, s=15)
ax.scatter(mod_x[primality], mod_y[primality], z[primality],
           c='gold', marker='*', s=100, edgecolor='black', label='Primes')

ax.set_title(f'Prime Distribution mod {mod_base}')
ax.set_xlabel(f'n mod {mod_base}')
ax.set_ylabel(f'(n // {mod_base}) mod {mod_base}')
ax.set_zlabel('log(n)')
plt.show()

# Prime Riemann Zeta Landscape
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Create complex grid
real = np.linspace(0.1, 1, 100)
imag = np.linspace(10, 50, 100)
Re, Im = np.meshgrid(real, imag)
s = Re + 1j*Im

# Compute zeta values
zeta_vals = np.vectorize(scipy.special.zeta)(s)
zeta_mag = np.abs(zeta_vals)

# Plot surface
ax.plot_surface(Re, Im, np.log(zeta_mag),
                cmap='viridis', alpha=0.7)

# Overlay primes
prime_indices = np.where(primality)[0]
for idx in prime_indices[:300]:  # First 300 primes
    s_val = 0.5 + 1j * n[idx]
    z = scipy.special.zeta(s_val)
    ax.scatter(0.5, n[idx], np.log(np.abs(z)),
               c='red', s=50, edgecolor='gold', label='Primes')

ax.set_title('Riemann Zeta Landscape with Primes on Critical Line')
ax.set_xlabel('Real Part')
ax.set_ylabel('Imaginary Part')
ax.set_zlabel('log|ζ(s)|')
plt.show()

# Prime Harmonic Interference
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Create interference pattern
freq1 = math.pi
freq2 = math.e
harmonic = np.sin(freq1 * n) * np.cos(freq2 * n)

# Prime Gaussian Spirals
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Gaussian prime spiral
angles = np.cumsum(np.where(primality, math.pi/2, math.pi/8))
radii = np.sqrt(n)

x = radii * np.cos(angles)
y = radii * np.sin(angles)
z = np.where(primality, np.log(n), n/(N_POINTS/10))

ax.scatter(x[~primality], y[~primality], z[~primality],
           c='blue', alpha=0.4, s=15, label='Non-Primes')
ax.scatter(x[primality], y[primality], z[primality],
           c='red', marker='*', s=100, label='Primes')

# Connect primes in sequence
prime_mask = primality.copy()
prime_mask[0] = False  # Skip n=1
ax.plot(x[prime_mask], y[prime_mask], z[prime_mask],
        'r-', alpha=0.3)

ax.set_title('Gaussian Prime Spirals with Connection Lines')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Height')
plt.show()

# Modular Prime Torus
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Torus parameters
R, r = 10, 3  # Major and minor radii

# Create torus coordinates
mod1, mod2 = 17, 23  # Prime moduli
theta = 2 * np.pi * (n % mod1) / mod1
phi = 2 * np.pi * (n % mod2) / mod2

x = (R + r * np.cos(theta)) * np.cos(phi)
y = (R + r * np.cos(theta)) * np.sin(phi)
z = r * np.sin(theta)

# Color by residue class
res_class = n % 6  # Mod 6 classes
colors = np.where(primality, 'red',
                  np.where((res_class == 1) | (res_class == 5), 'blue', 'gray'))

ax.scatter(x[~primality], y[~primality], z[~primality],
           c=colors[~primality], alpha=0.5, s=15)
ax.scatter(x[primality], y[primality], z[primality],
           c='gold', marker='*', s=100, edgecolor='red')

# Draw torus structure
theta_t = np.linspace(0, 2*np.pi, 100)
phi_t = np.linspace(0, 2*np.pi, 100)
theta_t, phi_t = np.meshgrid(theta_t, phi_t)
x_t = (R + r * np.cos(theta_t)) * np.cos(phi_t)
y_t = (R + r * np.cos(theta_t)) * np.sin(phi_t)
z_t = r * np.sin(theta_t)
ax.plot_wireframe(x_t, y_t, z_t, color='gray', alpha=0.1)

ax.set_title(f'Modular Prime Torus (Residues mod {mod1} & {mod2})')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.view_init(30, 45)
plt.show()