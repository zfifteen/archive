"""
Visualization of GMM and Fourier Analysis Results
=================================================

Creates comprehensive visualizations of the θ' distribution analysis results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sympy import sieve
import os

# Set matplotlib backend and style
plt.switch_backend('Agg')
plt.style.use('default')
sns.set_palette("husl")

# Constants
phi = (1 + np.sqrt(5)) / 2
k_target = 0.3
M_FOURIER = 5
C_GMM = 5
N_MAX = 1000000

# Load results
results_dir = "/home/runner/work/unified-framework/unified-framework/number-theory/prime-curve/gmm_fourier_results"
output_dir = "/home/runner/work/unified-framework/unified-framework/number-theory/prime-curve/gmm_fourier_results"

results_table = pd.read_csv(f"{results_dir}/results_table.csv")
fourier_coeffs = pd.read_csv(f"{results_dir}/fourier_coefficients.csv")
gmm_params = pd.read_csv(f"{results_dir}/gmm_parameters.csv")
bootstrap_results = pd.read_csv(f"{results_dir}/bootstrap_results.csv")

def frame_shift_residues(n_vals, k):
    """θ'(n,k) = φ * {n/φ} ** k"""
    mod_phi = np.mod(n_vals, phi) / phi
    return phi * np.power(mod_phi, k)

def normalize_to_unit_interval(theta_vals):
    """Normalize θ' values to [0,1) by computing {θ'/φ}"""
    return (theta_vals % phi) / phi

# Regenerate data for visualization
print("Regenerating data for visualization...")
primes_list = list(sieve.primerange(2, N_MAX + 1))
primes_array = np.array(primes_list)
theta_primes = frame_shift_residues(primes_array, k_target)
x_primes = normalize_to_unit_interval(theta_primes)

# Create comprehensive visualization
fig = plt.figure(figsize=(20, 16))

# 1. θ' Distribution Histogram
ax1 = plt.subplot(3, 4, 1)
plt.hist(x_primes, bins=50, density=True, alpha=0.7, color='skyblue', edgecolor='black')
plt.title(f'θ\' Distribution (k={k_target})', fontsize=14, fontweight='bold')
plt.xlabel('Normalized θ\' values')
plt.ylabel('Density')
plt.grid(True, alpha=0.3)

# 2. GMM Fit Overlay
ax2 = plt.subplot(3, 4, 2)
plt.hist(x_primes, bins=50, density=True, alpha=0.7, color='skyblue', edgecolor='black', label='Data')

# Recreate GMM for plotting
scaler = StandardScaler()
X_scaled = scaler.fit_transform(x_primes.reshape(-1, 1))
gmm = GaussianMixture(n_components=C_GMM, random_state=0)
gmm.fit(X_scaled)

# Plot GMM components
x_plot = np.linspace(0, 1, 1000)
x_plot_scaled = scaler.transform(x_plot.reshape(-1, 1))
gmm_pdf = np.exp(gmm.score_samples(x_plot_scaled))

plt.plot(x_plot, gmm_pdf, 'r-', linewidth=2, label='GMM Fit')

# Plot individual components
for i in range(C_GMM):
    mean = gmm_params.iloc[i]['mean']
    sigma = gmm_params.iloc[i]['sigma']
    weight = gmm_params.iloc[i]['weight']
    
    component_pdf = weight * (1/np.sqrt(2*np.pi*sigma**2)) * np.exp(-0.5*((x_plot - mean)/sigma)**2)
    plt.plot(x_plot, component_pdf, '--', alpha=0.6, label=f'Component {i+1}')

plt.title('GMM Components Overlay', fontsize=14, fontweight='bold')
plt.xlabel('Normalized θ\' values')
plt.ylabel('Density')
plt.legend()
plt.grid(True, alpha=0.3)

# 3. Fourier Coefficients Bar Plot
ax3 = plt.subplot(3, 4, 3)
harmonics = range(M_FOURIER + 1)
a_coeffs = fourier_coeffs['a_coeffs'].values
b_coeffs = fourier_coeffs['b_coeffs'].values

x_pos = np.arange(len(harmonics))
width = 0.35

plt.bar(x_pos - width/2, a_coeffs, width, label='a_m (cosine)', alpha=0.8, color='blue')
plt.bar(x_pos + width/2, np.abs(b_coeffs), width, label='|b_m| (sine)', alpha=0.8, color='red')

plt.title('Fourier Coefficients', fontsize=14, fontweight='bold')
plt.xlabel('Harmonic m')
plt.ylabel('Coefficient Value')
plt.xticks(x_pos, harmonics)
plt.legend()
plt.grid(True, alpha=0.3)

# 4. Bootstrap Distributions
ax4 = plt.subplot(3, 4, 4)
plt.hist(bootstrap_results['S_b_bootstrap'], bins=30, alpha=0.7, color='green', density=True)
plt.axvline(results_table['S_b'].iloc[0], color='red', linestyle='--', linewidth=2, label='Actual S_b')
plt.axvline(results_table['CI_S_b_lower'].iloc[0], color='orange', linestyle=':', alpha=0.7, label='95% CI')
plt.axvline(results_table['CI_S_b_upper'].iloc[0], color='orange', linestyle=':', alpha=0.7)
plt.title('Bootstrap Distribution of S_b', fontsize=14, fontweight='bold')
plt.xlabel('S_b values')
plt.ylabel('Density')
plt.legend()
plt.grid(True, alpha=0.3)

# 5. Bootstrap σ Distribution  
ax5 = plt.subplot(3, 4, 5)
plt.hist(bootstrap_results['bar_sigma_bootstrap'], bins=30, alpha=0.7, color='purple', density=True)
plt.axvline(results_table['bar_σ'].iloc[0], color='red', linestyle='--', linewidth=2, label='Actual bar_σ')
plt.axvline(results_table['CI_bar_σ_lower'].iloc[0], color='orange', linestyle=':', alpha=0.7, label='95% CI')
plt.axvline(results_table['CI_bar_σ_upper'].iloc[0], color='orange', linestyle=':', alpha=0.7)
plt.title('Bootstrap Distribution of bar_σ', fontsize=14, fontweight='bold')
plt.xlabel('bar_σ values')
plt.ylabel('Density')
plt.legend()
plt.grid(True, alpha=0.3)

# 6. GMM Component Parameters
ax6 = plt.subplot(3, 4, 6)
components = gmm_params['component'].values
means = gmm_params['mean'].values
sigmas = gmm_params['sigma'].values
weights = gmm_params['weight'].values

plt.scatter(means, sigmas, s=weights*1000, alpha=0.7, c=components, cmap='viridis')
for i, (mean, sigma, weight) in enumerate(zip(means, sigmas, weights)):
    plt.annotate(f'C{i+1}', (mean, sigma), xytext=(5, 5), textcoords='offset points', fontsize=10)

plt.title('GMM Component Parameters', fontsize=14, fontweight='bold')
plt.xlabel('Mean (μ)')
plt.ylabel('Sigma (σ)')
plt.colorbar(label='Component')
plt.grid(True, alpha=0.3)

# 7. Fourier Series Reconstruction
ax7 = plt.subplot(3, 4, 7)
x_fine = np.linspace(0, 1, 1000)

# Compute histogram for comparison
hist, bin_edges = np.histogram(x_primes, bins=100, density=True)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Reconstruct Fourier series
def fourier_reconstruct(x, a_coeffs, b_coeffs):
    result = a_coeffs[0]  # a0
    for m in range(1, len(a_coeffs)):
        result += a_coeffs[m] * np.cos(2 * np.pi * m * x) + b_coeffs[m] * np.sin(2 * np.pi * m * x)
    return result

fourier_recon = fourier_reconstruct(x_fine, a_coeffs, b_coeffs)

plt.plot(bin_centers, hist, 'o-', alpha=0.7, label='Histogram', markersize=3)
plt.plot(x_fine, fourier_recon, 'r-', linewidth=2, label='Fourier Reconstruction')
plt.title('Fourier Series Reconstruction', fontsize=14, fontweight='bold')
plt.xlabel('x')
plt.ylabel('Density')
plt.legend()
plt.grid(True, alpha=0.3)

# 8. Results Summary Table
ax8 = plt.subplot(3, 4, 8)
ax8.axis('tight')
ax8.axis('off')

# Create summary table
summary_data = [
    ['Metric', 'Value', '95% CI'],
    ['S_b', f"{results_table['S_b'].iloc[0]:.3f}", 
     f"[{results_table['CI_S_b_lower'].iloc[0]:.3f}, {results_table['CI_S_b_upper'].iloc[0]:.3f}]"],
    ['bar_σ', f"{results_table['bar_σ'].iloc[0]:.3f}", 
     f"[{results_table['CI_bar_σ_lower'].iloc[0]:.3f}, {results_table['CI_bar_σ_upper'].iloc[0]:.3f}]"],
    ['BIC', f"{results_table['BIC'].iloc[0]:.1f}", '-'],
    ['AIC', f"{results_table['AIC'].iloc[0]:.1f}", '-'],
    ['N_primes', f"{len(primes_list)}", '-'],
    ['k', f"{k_target}", '-']
]

table = plt.table(cellText=summary_data, cellLoc='center', loc='center', 
                 colWidths=[0.3, 0.3, 0.4])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)

# Style the header row
for i in range(3):
    table[(0, i)].set_facecolor('#40466e')
    table[(0, i)].set_text_props(weight='bold', color='white')

plt.title('Results Summary', fontsize=14, fontweight='bold', pad=20)

# 9. Prime Density vs Position
ax9 = plt.subplot(3, 4, 9)
# Sample every 1000th prime for visualization
sample_indices = np.arange(0, len(primes_array), 1000)
sample_primes = primes_array[sample_indices]
sample_theta = theta_primes[sample_indices]

plt.scatter(sample_primes, sample_theta, alpha=0.6, s=10, c=range(len(sample_primes)), cmap='plasma')
plt.title('θ\' vs Prime Values (sampled)', fontsize=14, fontweight='bold')
plt.xlabel('Prime p')
plt.ylabel('θ\'(p, k=0.3)')
plt.colorbar(label='Prime Index')
plt.grid(True, alpha=0.3)

# 10. Cumulative Distribution
ax10 = plt.subplot(3, 4, 10)
sorted_x = np.sort(x_primes)
y_vals = np.arange(1, len(sorted_x) + 1) / len(sorted_x)
plt.plot(sorted_x, y_vals, 'b-', linewidth=2, label='Empirical CDF')

# Add uniform CDF for comparison
plt.plot([0, 1], [0, 1], 'r--', linewidth=2, alpha=0.7, label='Uniform CDF')

plt.title('Cumulative Distribution Function', fontsize=14, fontweight='bold')
plt.xlabel('Normalized θ\' values')
plt.ylabel('Cumulative Probability')
plt.legend()
plt.grid(True, alpha=0.3)

# 11. Residuals Analysis
ax11 = plt.subplot(3, 4, 11)
# Compute residuals between histogram and Fourier fit
hist_fine, bin_edges_fine = np.histogram(x_primes, bins=100, density=True)
bin_centers_fine = (bin_edges_fine[:-1] + bin_edges_fine[1:]) / 2
fourier_fit_vals = fourier_reconstruct(bin_centers_fine, a_coeffs, b_coeffs)
residuals = hist_fine - fourier_fit_vals

plt.plot(bin_centers_fine, residuals, 'go-', markersize=3, alpha=0.7)
plt.axhline(y=0, color='red', linestyle='--', alpha=0.7)
plt.title('Fourier Fit Residuals', fontsize=14, fontweight='bold')
plt.xlabel('x')
plt.ylabel('Residual')
plt.grid(True, alpha=0.3)

# 12. Model Comparison
ax12 = plt.subplot(3, 4, 12)
metrics = ['BIC', 'AIC']
values = [results_table['BIC'].iloc[0], results_table['AIC'].iloc[0]]
colors = ['lightcoral', 'lightblue']

bars = plt.bar(metrics, values, color=colors, alpha=0.8)
plt.title('Model Information Criteria', fontsize=14, fontweight='bold')
plt.ylabel('Value')

# Add value labels on bars
for bar, value in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01, 
             f'{value:.1f}', ha='center', va='bottom', fontweight='bold')

plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f"{output_dir}/gmm_fourier_comprehensive_analysis.png", dpi=300, bbox_inches='tight')
plt.close()

# Create a focused results visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

# Distribution with GMM overlay
ax1.hist(x_primes, bins=50, density=True, alpha=0.7, color='lightblue', edgecolor='black')
x_plot = np.linspace(0, 1, 1000)
x_plot_scaled = scaler.transform(x_plot.reshape(-1, 1))
gmm_pdf = np.exp(gmm.score_samples(x_plot_scaled))
ax1.plot(x_plot, gmm_pdf, 'red', linewidth=3, label=f'GMM (C={C_GMM})')
ax1.set_title('θ\' Distribution with GMM Fit', fontsize=16, fontweight='bold')
ax1.set_xlabel('Normalized θ\' values')
ax1.set_ylabel('Density')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Fourier coefficients
harmonics = range(M_FOURIER + 1)
x_pos = np.arange(len(harmonics))
width = 0.35
ax2.bar(x_pos - width/2, a_coeffs, width, label='a_m (cosine)', alpha=0.8, color='blue')
ax2.bar(x_pos + width/2, np.abs(b_coeffs), width, label='|b_m| (sine)', alpha=0.8, color='red')
ax2.set_title('Fourier Coefficients', fontsize=16, fontweight='bold')
ax2.set_xlabel('Harmonic m')
ax2.set_ylabel('Coefficient Value')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(harmonics)
ax2.legend()
ax2.grid(True, alpha=0.3)

# Bootstrap results
ax3.hist(bootstrap_results['S_b_bootstrap'], bins=30, alpha=0.7, color='green', density=True)
ax3.axvline(results_table['S_b'].iloc[0], color='red', linestyle='--', linewidth=3, label=f'S_b = {results_table["S_b"].iloc[0]:.3f}')
ax3.set_title('Bootstrap Distribution of S_b', fontsize=16, fontweight='bold')
ax3.set_xlabel('S_b values')
ax3.set_ylabel('Density')
ax3.legend()
ax3.grid(True, alpha=0.3)

# GMM parameters
components = gmm_params['component'].values
means = gmm_params['mean'].values
sigmas = gmm_params['sigma'].values
weights = gmm_params['weight'].values

scatter = ax4.scatter(means, sigmas, s=weights*2000, alpha=0.7, c=components, cmap='viridis', edgecolors='black')
for i, (mean, sigma, weight) in enumerate(zip(means, sigmas, weights)):
    ax4.annotate(f'C{i+1}\n(π={weight:.3f})', (mean, sigma), xytext=(5, 5), 
                textcoords='offset points', fontsize=10, ha='left')

ax4.set_title('GMM Component Parameters', fontsize=16, fontweight='bold')
ax4.set_xlabel('Mean (μ)')
ax4.set_ylabel('Sigma (σ)')
plt.colorbar(scatter, ax=ax4, label='Component Index')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/gmm_fourier_key_results.png", dpi=300, bbox_inches='tight')
plt.close()

print("Visualizations created:")
print(f"- {output_dir}/gmm_fourier_comprehensive_analysis.png")
print(f"- {output_dir}/gmm_fourier_key_results.png")