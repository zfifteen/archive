import matplotlib.pyplot as plt
import numpy as np

# --- 1. Define the Grid ---
# Create a grid of lines
x_lines = np.arange(-2, 2.1, 0.2)
y_lines = np.arange(-2, 2.1, 0.2)

# --- 2. Define the Inversion Function ---
def invert_point(x, y):
    """Inverts a point (x, y) with respect to the unit circle."""
    # Avoid division by zero at the origin
    if x == 0 and y == 0:
        return float('inf'), float('inf')
    
    denominator = x**2 + y**2
    return x / denominator, y / denominator

def invert_line(points):
    """Inverts a series of points (a line)."""
    inverted_points = np.array([invert_point(x, y) for x, y in points])
    return inverted_points

# --- 3. Apply the Inversion ---
# Generate points for each line and apply the inversion
inverted_grid = []

# Vertical lines
for x in x_lines:
    points = np.array([[x, y] for y in np.linspace(-2, 2, 500)])
    inverted_grid.append(invert_line(points))

# Horizontal lines
for y in y_lines:
    points = np.array([[x, y] for x in np.linspace(-2, 2, 500)])
    inverted_grid.append(invert_line(points))

# --- 4. Plot the Results ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Subplot 1: Original Grid
ax1.set_title('Original Square Grid and Unit Circle')
ax1.set_aspect('equal', adjustable='box')
ax1.set_xlim(-2, 2)
ax1.set_ylim(-2, 2)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

# Draw the unit circle
unit_circle = plt.Circle((0, 0), 1, color='red', fill=False, linewidth=2)
ax1.add_artist(unit_circle)

# Draw the grid lines
for x in x_lines:
    ax1.axvline(x, color='blue', lw=0.5)
for y in y_lines:
    ax1.axhline(y, color='blue', lw=0.5)
ax1.set_xlabel("x")
ax1.set_ylabel("y")

# Subplot 2: Inverted Grid
ax2.set_title('Inversion of the Grid on the Unit Circle')
ax2.set_aspect('equal', adjustable='box')
ax2.set_xlim(-2, 2)
ax2.set_ylim(-2, 2)
ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

# Draw the unit circle
unit_circle_inverted = plt.Circle((0, 0), 1, color='red', fill=False, linewidth=2)
ax2.add_artist(unit_circle_inverted)

# Draw the inverted grid lines
for line in inverted_grid:
    # Remove infinite values for plotting
    line = line[np.isfinite(line).all(axis=1)]
    ax2.plot(line[:, 0], line[:, 1], color='purple', lw=0.7)
ax2.set_xlabel("x'")
ax2.set_ylabel("y'")

# --- 5. Add the Z formula calculation ---
A = 5  # observed arcs
B = 2  # increase in nested circles per step
C = 10 # maximum observable complexity
Z = A * (B / C)

z_text = f"Z = A * (B / C)\nZ = {A} * ({B} / {C}) = {Z}"
ax2.text(0.95, 0.05, z_text, transform=ax2.transAxes, fontsize=10,
         verticalalignment='bottom', horizontalalignment='right',
         bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig("grid_inversion.png")
