import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# --- 1. Define the Inversion Function for 3D ---
def invert_point_3d(x, y, z):
    """Inverts a point (x, y, z) with respect to the unit sphere."""
    if x == 0 and y == 0 and z == 0:
        return float('inf'), float('inf'), float('inf')
    denominator = x**2 + y**2 + z**2
    if denominator == 0:
        return float('inf'), float('inf'), float('inf')
    return x / denominator, y / denominator, z / denominator

# --- 2. Create the Grid/Plane ---
def create_plane(z_offset, size=2):
    """Creates a square plane at a given z_offset."""
    x = np.linspace(-size, size, 20)
    y = np.linspace(-size, size, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.full(X.shape, z_offset)
    return X, Y, Z

# --- 3. Invert the Plane ---
def invert_plane(X, Y, Z):
    """Inverts all points on a given plane."""
    inverted_X = np.zeros_like(X)
    inverted_Y = np.zeros_like(Y)
    inverted_Z = np.zeros_like(Z)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            inv_x, inv_y, inv_z = invert_point_3d(X[i, j], Y[i, j], Z[i, j])
            inverted_X[i, j] = inv_x
            inverted_Y[i, j] = inv_y
            inverted_Z[i, j] = inv_z
    return inverted_X, inverted_Y, inverted_Z

# --- 4. Setup the Plot ---
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_title('Animated 3D Inversion of a Plane on a Unit Sphere')
ax.set_xlim([-3, 3])
ax.set_ylim([-3, 3])
ax.set_zlim([-3, 3])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

u = np.linspace(0, 2 * np.pi, 50)
v = np.linspace(0, np.pi, 50)
sphere_x = 1 * np.outer(np.cos(u), np.sin(v))
sphere_y = 1 * np.outer(np.sin(u), np.sin(v))
sphere_z = 1 * np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_surface(sphere_x, sphere_y, sphere_z, color='red', alpha=0.1, linewidth=0)

# ==================== FIX IS HERE ====================
# Initialize the plots with empty 2D NumPy arrays instead of empty lists
# This satisfies the requirement of ax.plot_surface for a 2D array input.
empty_2d_array = np.array([[], []])
original_plane_plot = ax.plot_surface(empty_2d_array, empty_2d_array, empty_2d_array, color='blue', alpha=0.6)
inverted_plane_plot = ax.plot_surface(empty_2d_array, empty_2d_array, empty_2d_array, color='purple', alpha=0.8)
# ======================================================

# --- 5. Animation Function ---
def update(frame):
    global original_plane_plot, inverted_plane_plot
    
    z_offset = np.sin(frame * 0.05) * 2.5 
    X_orig, Y_orig, Z_orig = create_plane(z_offset)
    X_inv, Y_inv, Z_inv = invert_plane(X_orig, Y_orig, Z_orig)

    # Remove the previous plots before drawing the new ones
    original_plane_plot.remove()
    inverted_plane_plot.remove()

    original_plane_plot = ax.plot_surface(X_orig, Y_orig, Z_orig, color='blue', alpha=0.6, label='Original Plane')
    inverted_plane_plot = ax.plot_surface(X_inv, Y_inv, Z_inv, color='purple', alpha=0.8, label='Inverted Plane')

    ax.set_title(f'Animated 3D Inversion (Plane at z={z_offset:.2f})')
    
    return original_plane_plot, inverted_plane_plot

# --- 6. Create and Save the Animation ---
ani = FuncAnimation(fig, update, frames=np.arange(0, 126), blit=False, interval=100)
ani.save('3d_inversion_animation.gif', writer='pillow', fps=15)

# This line is optional, uncomment it if you want the plot to pop up after saving.
plt.show()
