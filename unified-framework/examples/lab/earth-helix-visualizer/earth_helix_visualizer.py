import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Time array (in arbitrary units, e.g., days)
t = np.linspace(0, 1000, 10000)  # simulate ~3 years

# Parameters for nested motions
daily_radius = 0.01       # small loops from Earth's rotation
yearly_radius = 1.0       # Earth's orbit around the Sun
galactic_drift = 0.001    # slow forward motion of the Solar System

# Frequencies (in radians per unit time)
daily_freq = 2 * np.pi    # one rotation per day
yearly_freq = 2 * np.pi / 365  # one orbit per year

# Nested helical path
x = (yearly_radius * np.cos(yearly_freq * t) +
     daily_radius * np.cos(daily_freq * t))
y = (yearly_radius * np.sin(yearly_freq * t) +
     daily_radius * np.sin(daily_freq * t))
z = galactic_drift * t  # forward drift through space

# Plotting
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, color='royalblue', linewidth=1)

# Aesthetics
ax.set_title("Earth's Helical Trajectory Through Space", fontsize=14)
ax.set_xlabel("X (AU)")
ax.set_ylabel("Y (AU)")
ax.set_zlabel("Z (Drift Units)")
ax.view_init(elev=30, azim=120)
plt.tight_layout()
plt.show()
