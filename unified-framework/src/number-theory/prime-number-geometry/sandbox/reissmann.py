import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy
from scipy.interpolate import splprep, splev
from matplotlib.colors import LogNorm

# Choose your universal constant
UNIVERSAL = math.pi  # Changed to π per README.md and Reissnmann's insights

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
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

# Parameters
N_POINTS = 10000
HELIX_FREQ = scipy.constants.golden_ratio * 0.1  # Golden ratio modulation
LOG_SCALE = True  # Enabled per Reissnmann's suggestion

# Instantiate transformer with π scaling
transformer = Numberspace(B=math.pi)

# Generate data with prime gaps
n = np.arange(1, N_POINTS)
primality = np.vectorize(is_prime)(n)
primes = n[primality]

# Calculate prime gaps and curvature
prime_gaps = np.diff(primes)
gap_dict = {p: g for p, g in zip(primes[1:], prime_gaps)}
gap_dict[primes[0]] = 0  # First prime has gap=0

# Y-values with log scaling
y_raw = np.log(n) if LOG_SCALE else n

# Apply Numberspace transform
y = transformer(y_raw)

# Z-values with golden ratio modulation
z = np.sin(math.pi * HELIX_FREQ * n)

# Create opacity gradient (per Reissnmann)
opacity = np.linspace(0.2, 1.0, N_POINTS-1)

# Calculate local curvature (per Reissnmann)
def calculate_curvature(x, y, z, window=5):
    curvatures = np.zeros(len(x))
    for i in range(window, len(x)-window):
        idx = slice(i-window, i+window+1)
        tck, u = splprep([x[idx], y[idx], z[idx]], s=0)
        der1, der2 = splev(u, tck, der=1), splev(u, tck, der=2)
        num = np.linalg.norm(np.cross(der1, der2), axis=0)
        den = np.linalg.norm(der1, axis=0)**3
        curvatures[i] = np.mean(np.divide(num, den, where=den!=0))
    return curvatures

# ========== Enhanced Main Visualization ==========
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Create colormap for gap sizes (per Reissnmann)
gap_colors = np.array([gap_dict.get(i, 0) for i in n])
cmap = plt.cm.viridis

# Non-primes with opacity gradient
non_prime_mask = ~primality
sc_nonprime = ax.scatter(
    n[non_prime_mask], 
    y[non_prime_mask], 
    z[non_prime_mask],
    c=gap_colors[non_prime_mask],
    cmap=cmap,
    alpha=opacity[non_prime_mask],
    s=10,
    norm=LogNorm(vmin=1, vmax=max(prime_gaps))
)

# Primes with star markers and gap-based coloring
prime_mask = primality.copy()
sc_prime = ax.scatter(
    n[prime_mask], 
    y[prime_mask], 
    z[prime_mask],
    c=gap_colors[prime_mask],
    cmap=cmap,
    marker='*',
    s=80,
    edgecolors='gold',
    norm=LogNorm(vmin=1, vmax=max(prime_gaps))
)

# Calculate and plot curvature (per Reissnmann)
curvature = calculate_curvature(n, y, z)
high_curv = curvature > np.percentile(curvature, 90)
ax.scatter(
    n[high_curv], 
    y[high_curv], 
    z[high_curv],
    s=50,
    facecolors='none',
    edgecolors='r',
    alpha=0.7,
    label='High Curvature'
)

ax.set_xlabel('n (Position)')
ax.set_ylabel('π-scaled Value')
ax.set_zlabel('Helical Coordinate')
ax.set_title('Enhanced 3D Prime Geometry with Curvature Analysis')
cbar = fig.colorbar(sc_prime, ax=ax)
cbar.set_label('Prime Gap Size')
ax.legend()
plt.tight_layout()
plt.show()

# ========== Gap-Based Transformation ==========
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Calculate Z-values per README.md formula
z_gap = np.zeros(len(primes))
for i, p in enumerate(primes[1:], 1):
    gap = p - primes[i-1]
    z_gap[i] = i * gap / math.pi

# Create toroidal transformation (per Reissnmann)
theta = 2 * np.pi * np.arange(len(primes)) / len(primes)
phi = 2 * np.pi * z_gap / max(z_gap[1:])
R, r = 10, 3  # Torus radii
x_torus = (R + r * np.cos(theta)) * np.cos(phi)
y_torus = (R + r * np.cos(theta)) * np.sin(phi)
z_torus = r * np.sin(theta)

# Plot torus structure
theta_t = np.linspace(0, 2*np.pi, 100)
phi_t = np.linspace(0, 2*np.pi, 100)
theta_t, phi_t = np.meshgrid(theta_t, phi_t)
x_t = (R + r * np.cos(theta_t)) * np.cos(phi_t)
y_t = (R + r * np.cos(theta_t)) * np.sin(phi_t)
z_t = r * np.sin(theta_t)
ax.plot_wireframe(x_t, y_t, z_t, color='gray', alpha=0.1)

# Plot primes on torus
sc = ax.scatter(
    x_torus[1:], 
    y_torus[1:], 
    z_torus[1:], 
    c=prime_gaps,
    cmap='plasma',
    s=50,
    norm=LogNorm(vmin=min(prime_gaps), vmax=max(prime_gaps))
)

# Connect consecutive primes
for i in range(1, len(primes)-1):
    ax.plot(
        [x_torus[i], x_torus[i+1]],
        [y_torus[i], y_torus[i+1]],
        [z_torus[i], z_torus[i+1]],
        'r-', alpha=0.3, lw=0.5
    )

ax.set_title('Prime Gap Transformation on Toroidal Manifold')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label('Prime Gap Size')
ax.view_init(30, 45)
plt.show()

# ========== Riemann Zeta Landscape ==========
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Create complex grid
real = np.linspace(0.01, 1, 50)
imag = np.linspace(10, 50, 50)
Re, Im = np.meshgrid(real, imag)
s = Re + 1j*Im

# Compute zeta values
zeta_vals = np.vectorize(scipy.special.zeta)(s, 1)
zeta_mag = np.abs(zeta_vals)

# Plot surface
surf = ax.plot_surface(
    Re, Im, np.log(zeta_mag),
    cmap='viridis', 
    alpha=0.7,
    edgecolor='none'
)

# Overlay primes and Riemann zeros
prime_indices = np.where(primality)[0][:300]  # First 300 primes
for idx in prime_indices:
    s_val = 0.5 + 1j * n[idx]
    z_val = scipy.special.zeta(s_val, 1)
    ax.scatter(
        0.5, n[idx], np.log(np.abs(z_val)),
        c='red', 
        s=30,
        edgecolor='gold'
    )

ax.set_title('Riemann Zeta Landscape with Primes on Critical Line')
ax.set_xlabel('Real Part')
ax.set_ylabel('Imaginary Part')
ax.set_zlabel('log|ζ(s)|')
plt.show()

# ========== Density Visualization ==========
from scipy.stats import gaussian_kde

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Create 3D density estimate (per Reissnmann)
prime_points = np.vstack([n[prime_mask], y[prime_mask], z[prime_mask]]).T
kde = gaussian_kde(prime_points.T)
density = kde(prime_points.T)

# Plot density isosurfaces
sc = ax.scatter(
    n[prime_mask], 
    y[prime_mask], 
    z[prime_mask],
    c=density,
    cmap='hot',
    s=20,
    alpha=0.7
)

ax.set_xlabel('n (Position)')
ax.set_ylabel('π-scaled Value')
ax.set_zlabel('Helical Coordinate')
ax.set_title('3D Prime Density Estimation')
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label('Density Estimate')
plt.show()