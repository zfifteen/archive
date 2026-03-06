"""
proof_of_concept_zeta_embedding.py

Simple proof‐of‐concept: three 3D visualizations of DiscreteZetaShift embeddings
that reveal prime‐driven twists and geodesic curvature.

Plots:
  1) 3D scatter of (X, Y, Z) = get_3d_coordinates(), primes vs. composites
  2) 3D scatter of (X, Y, Z) = get_4d_coordinates()[1:4], colored by time‐like t
  3) 3D scatter of (X, Y, Z) = first three dims of get_5d_coordinates(), colored by U
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sympy import isprime
from core.domain import DiscreteZetaShift, E_SQUARED

# PARAMETERS
START_N = 900000      # starting integer
COUNT   =   500       # number of shifts to visualize
V       =   1.0       # velocity‐like frame shift
K       =   0.3       # curvature exponent

# Generate DiscreteZetaShift instances
shifts = []
for i in range(START_N, START_N + COUNT):
    shifts.append(DiscreteZetaShift(i, v=V, delta_max=E_SQUARED))

# 1) 3D scatter of get_3d_coordinates
xs, ys, zs = [], [], []
colors = []
for s in shifts:
    x, y, z = s.get_3d_coordinates()
    xs.append(x); ys.append(y); zs.append(z)
    colors.append('red' if isprime(int(s.a)) else 'blue')

fig = plt.figure(figsize=(15, 5))
ax1 = fig.add_subplot(131, projection='3d')
ax1.scatter(xs, ys, zs, c=colors, s=20, alpha=0.8)
ax1.set_title(' (X,Y,Z) = get_3d_coordinates()\nPrimes=red, Composites=blue')
ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z (F/e²)')

# 2) 3D scatter of get_4d_coordinates (x,y,z) colored by t
xs4, ys4, zs4, ts = [], [], [], []
for s in shifts:
    t, x, y, z = s.get_4d_coordinates()
    xs4.append(x); ys4.append(y); zs4.append(z); ts.append(t)

ax2 = fig.add_subplot(132, projection='3d')
p = ax2.scatter(xs4, ys4, zs4, c=ts, cmap='viridis', s=20)
ax2.set_title('(X,Y,Z) from get_4d_coordinates()\nColored by t')
ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_zlabel('Z')
fig.colorbar(p, ax=ax2, label='t (time-like)')

# 3) 3D scatter of get_5d_coordinates (x,y,z) colored by U
xs5, ys5, zs5, us = [], [], [], []
for s in shifts:
    x, y, z, w, u = s.get_5d_coordinates()
    xs5.append(x); ys5.append(y); zs5.append(z); us.append(u)

ax3 = fig.add_subplot(133, projection='3d')
p2 = ax3.scatter(xs5, ys5, zs5, c=us, cmap='plasma', s=20)
ax3.set_title('(X,Y,Z) from get_5d_coordinates()\nColored by U')
ax3.set_xlabel('X'); ax3.set_ylabel('Y'); ax3.set_zlabel('Z')
fig.colorbar(p2, ax=ax3, label='U (O attribute)')

plt.tight_layout()
plt.show()
