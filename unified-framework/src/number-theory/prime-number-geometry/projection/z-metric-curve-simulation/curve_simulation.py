import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Define Z-metric function
def z_metric(n, n1):
    delta_max = n - 1
    return n * (n1 / delta_max)

# Simulate range of principal quantum numbers
n_values = np.arange(5, 50, 1)  # from n=5 to n=49
# Assume n1 scales as 0.85*(n-1) to simulate low distortion regime
n1_values = 0.85 * (n_values - 1)
z_values = z_metric(n_values, n1_values)

# Define classical curvature baseline (linear reference)
def classical_baseline(n, a):
    return a * n

# Fit classical baseline to Z values
params, _ = curve_fit(classical_baseline, n_values, z_values)
baseline = classical_baseline(n_values, *params)

# Compute distortion gradient
distortion = z_values - baseline

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(n_values, z_values, label='Z-Metric Curvature', color='blue', linewidth=2)
plt.plot(n_values, baseline, label='Classical Baseline', color='gray', linestyle='--')
plt.fill_between(n_values, baseline, z_values, color='orange', alpha=0.3, label='Frame Shift Distortion')
plt.xlabel('Principal Quantum Number (n)')
plt.ylabel('Z-Metric Value')
plt.title('Z-Transformed Frame Shift in Hydrogen Stark States')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Print summary statistics
print("Z-Metric Simulation Summary:")
print(f"Fitted classical baseline slope: {params[0]:.3f}")
print(f"Average distortion: {np.mean(distortion):.3f}")
print(f"Max distortion: {np.max(distortion):.3f} at n = {n_values[np.argmax(distortion)]}")
