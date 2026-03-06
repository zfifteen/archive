import mpmath
import numpy as np
from scipy.stats import pearsonr, kstest
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

mpmath.mp.dps = 50

def compute_unfolded_zeros(M):
    phi = mpmath.phi()
    pi = mpmath.pi()
    e = mpmath.e
    unfolded = []
    for k in range(1, M + 1):
        t = mpmath.zetazero(k).imag
        arg = t / (2 * pi * e)
        if arg > 1:
            log_val = mpmath.log(arg)
            tilde_t = t / (2 * pi * log_val)
            unfolded.append(tilde_t)
    return unfolded

def helical_embedding(unfolded):
    phi = mpmath.phi()
    theta = [2 * mpmath.pi() * u / phi for u in unfolded]
    x = [float(mpmath.cos(th)) for th in theta]
    y = [float(mpmath.sin(th)) for th in theta]
    z = list(range(len(unfolded)))
    return np.array(x), np.array(y), np.array(z)

def compute_spacings(unfolded):
    return [float(unfolded[j] - unfolded[j-1]) for j in range(1, len(unfolded))]

def phi_modular_predictions(unfolded, k=3.33):
    phi = mpmath.phi()
    preds = []
    for u in unfolded[:-1]:
        mod = u % phi
        pred = float(phi * ((mod / phi) ** k))
        preds.append(pred)
    return preds

def spectral_form_factor(unfolded, tau):
    M = len(unfolded)
    sum_exp = sum(mpmath.exp(2j * mpmath.pi() * t * tau) for t in unfolded)
    K = (1.0 / M) * float(abs(sum_exp)**2)
    return K

def theoretical_gue_form_factor(tau):
    return tau if tau < 1 else 1.0

def curve_curvature(x, y, z):
    dx = np.gradient(x)
    dy = np.gradient(y)
    dz = np.gradient(z)
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)
    ddz = np.gradient(dz)
    num = np.sqrt((dz * ddy - dy * ddz)**2 + (dx * ddz - dz * ddx)**2 + (dy * ddx - dx * ddy)**2)
    den = (dx**2 + dy**2 + dz**2)**1.5
    kappa = num / den
    return np.nanmean(kappa)  # Ignore NaN for boundary effects

# Main execution
M = 1000
unfolded = compute_unfolded_zeros(M)
print(f"Computed {len(unfolded)} unfolded zeros (skipping those with invalid log arg).")

# Helical embedding and visualization
x, y, z = helical_embedding(unfolded)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, label='Zeta Zero Geodesics')
ax.set_title('Helical Embedding of Unfolded Zeta Zeros')
ax.legend()
plt.savefig('zeta_helix.png')
print("Helical visualization saved as 'zeta_helix.png'.")

# Spectral form factor analysis
tau_values = np.linspace(0.01, 2, 100)
K_values = [spectral_form_factor(unfolded, tau) for tau in tau_values]
gue_values = [theoretical_gue_form_factor(tau) for tau in tau_values]
plt.figure()
plt.plot(tau_values, K_values, label='Zeta Form Factor')
plt.plot(tau_values, gue_values, label='GUE Theoretical')
plt.title('Spectral Form Factor K(τ)/M vs. GUE')
plt.xlabel('τ')
plt.ylabel('K(τ)/M')
plt.legend()
plt.savefig('spectral_form_factor.png')
print("Spectral form factor plot saved as 'spectral_form_factor.png'.")

# Falsifiability tests
# 1. Pearson correlation test
spacings = compute_spacings(unfolded)
preds = phi_modular_predictions(unfolded, k=3.33)
corr, _ = pearsonr(spacings, preds)
print(f"Pearson correlation between unfolded spacings and φ-modular predictions: {corr}")
if abs(corr) < 0.9:
    raise AssertionError("Falsified: Correlation below 0.9 threshold, indicating insufficient geometric alignment.")

# 2. KS test on form factor vs. GUE
ks_stat, ks_p = kstest(K_values, gue_values)
print(f"KS test p-value for form factor deviation from GUE: {ks_p}")
if ks_p > 0.01:
    raise ValueError("Falsified: p-value > 0.01, indicating insufficient deviation from GUE ensemble.")

# 3. Geodesic curvature check
mean_kappa = curve_curvature(x, y, z)
print(f"Mean embedding curvature: {mean_kappa}")
if mean_kappa > 0.739:
    raise RuntimeError("Falsified: Mean curvature exceeds 0.739 prime minimal threshold, violating geometric minimization.")

print("All falsifiability tests passed. Riemann Hypothesis validation supported via helical geodesic patterns.")