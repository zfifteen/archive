import matplotlib.pyplot as plt
import numpy as np

# Data: k values and corresponding relative errors
k_values = [10**15, 10**16, 10**18, 10**19]
errors = [0.0017, 0.0012, 0.00032, 0.000032]
log_k = np.log10(k_values)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(log_k, errors, 'o-', color='blue', label='Z5D Prediction Error')
plt.xlabel('log(k)')
plt.ylabel('Relative Error (%)')
plt.title('Z5D Prime Prediction Error vs. log(k) at Ultra-Extreme Scales')
plt.grid(True, which='both', linestyle='--', alpha=0.7)
plt.legend()
plt.savefig('results/error_vs_logk_plot.png')
plt.close()
print("Plot saved as 'results/error_vs_logk_plot.png'")
