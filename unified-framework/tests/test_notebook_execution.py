#!/usr/bin/env python3
"""
Test script to execute notebook cells directly
"""

# Execute the configuration cell
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for CI
import matplotlib.pyplot as plt

# Configuration parameters
N_PRIMES = 2000  # Smaller for quick test
RNG_SEED = 42
BOOTSTRAP_B = 100

# Set random seed for reproducibility
np.random.seed(RNG_SEED)

# Configure matplotlib
plt.rcParams.update({'figure.figsize': (8, 4.8), 'axes.grid': True})

print(f"Config -> N_PRIMES={N_PRIMES:,}, BOOTSTRAP_B={BOOTSTRAP_B}, RNG_SEED={RNG_SEED}")

# Execute the Z5D math functions cell
# Calibrated Z5D parameters from the unified framework
C_CAL = -0.00247
K_STAR = 0.04449
KAPPA_GEO = 0.3

def base_pnt(k: int) -> float:
    """Base Prime Number Theorem estimator."""
    if k < 1: 
        return 0.0
    ln = math.log(k)
    if ln <= 0:
        return k * 0.5  # Simple fallback
    lnl = math.log(ln)
    return k * (ln + lnl - 1 + (lnl - 2) / ln)

def z5d_prime(k: int) -> float:
    """Calibrated Z5D prime predictor with geodesic modulation."""
    if k < 1: 
        return 2.0  # First prime
    
    pnt = base_pnt(k)
    if pnt <= 0: 
        # Fallback for small k where PNT breaks down
        return k * math.log(max(k, 2))
    
    # Dilation term: d(k) = (ln(p_PNT)/e^4)^2
    ln_pnt = math.log(pnt)
    d = (ln_pnt / math.exp(4))**2
    
    # Curvature proxy with geodesic modulation
    e = (k**2 + k + 2) / (k * (k + 1) * (k + 2))
    e *= KAPPA_GEO * (math.log(k + 1) / math.exp(2))  # Geodesic modulation
    
    # Z5D formula: p_Z5D(k) = p_PNT(k) * (1 + c*d + k*e)
    return pnt + C_CAL * d * pnt + K_STAR * e * pnt

print(f"Z5D Calibration: C={C_CAL}, K*={K_STAR}, κ_geo={KAPPA_GEO}")
print(f"Test: base_pnt(1000) = {base_pnt(1000):.2f}")
print(f"Test: z5d_prime(1000) = {z5d_prime(1000):.2f}")

# Execute prime generation cell
def nth_prime_upper_bound(n: int) -> int:
    """Upper bound for nth prime using n(ln n + ln ln n) for n >= 6."""
    if n < 6:
        return 30  # Conservative bound for small n
    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)
    return int(n * (ln_n + ln_ln_n) * 1.1)  # 10% safety margin

def sieve_of_eratosthenes(limit: int) -> list:
    """Generate all primes up to limit using Sieve of Eratosthenes."""
    if limit < 2:
        return []
    
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    return [i for i in range(2, limit + 1) if is_prime[i]]

def first_n_primes(n: int) -> list:
    """Generate first n primes using sieve with automatic bound doubling."""
    upper_bound = nth_prime_upper_bound(n)
    
    while True:
        primes = sieve_of_eratosthenes(upper_bound)
        if len(primes) >= n:
            return primes[:n]
        upper_bound *= 2  # Double the bound and try again

# Generate primes
primes = first_n_primes(N_PRIMES)
print(f"Generated {len(primes):,} primes. First 10: {primes[:10]}")
print(f"Last 5: {primes[-5:]}")
print(f"Largest prime: {primes[-1]:,}")

# Execute ratios + accuracy computation
# Create index array (k values)
k_idx = np.arange(1, len(primes) + 1)
p_arr = np.array(primes, dtype=float)

# Compute structural ratios
p_over_k = p_arr / k_idx
log_ratio = np.log(p_arr) / np.log(k_idx + 1)  # Avoid log(1) = 0 for k=1

# Compute prime gaps and gap ratios
gaps = np.diff(p_arr)
gap_ratio = np.where(gaps > 0, p_arr[1:], np.nan) / np.where(gaps > 0, gaps, np.nan)

# Generate estimates
pnt_est = np.array([base_pnt(int(k)) for k in k_idx], dtype=float)
z5d_est = np.array([z5d_prime(int(k)) for k in k_idx], dtype=float)

# Calculate absolute percentage errors
pnt_err_pct = np.abs(p_arr - pnt_est) / p_arr * 100.0
z5d_err_pct = np.abs(p_arr - z5d_est) / p_arr * 100.0

def pearson_r(x, y):
    """Compute Pearson correlation coefficient."""
    x = x.astype(float)
    y = y.astype(float)
    mx, my = x.mean(), y.mean()
    num = np.sum((x - mx) * (y - my))
    den = np.sqrt(np.sum((x - mx)**2) * np.sum((y - my)**2))
    return 0.0 if den == 0 else float(num / den)

# Calculate summary statistics
mean_pk = float(np.nanmean(p_over_k))
r_pk_log = pearson_r(p_over_k, log_ratio)
mean_gap_ratio = float(np.nanmean(gap_ratio))
mean_pnt = float(np.mean(pnt_err_pct))
mean_z5d = float(np.mean(z5d_err_pct))
improvement = (mean_pnt - mean_z5d) / (mean_pnt if mean_pnt else 1.0) * 100.0

print(f"Mean p/k: {mean_pk:.2f}")
print(f"Pearson r (p/k vs ln p / ln k): {r_pk_log:.2f}")
print(f"Mean p/gap: {mean_gap_ratio:.2f}")
print(f"PNT mean abs % error: {mean_pnt:.4f}%")
print(f"Z5D mean abs % error: {mean_z5d:.6f}%")
print(f"Improvement (Z5D vs PNT): {improvement:.1f}%")

# Test bootstrap functionality
def bootstrap_ci_mean(x, B=100, alpha=0.05):
    """Compute bootstrap confidence interval for the mean."""
    x = x[~np.isnan(x)]  # Remove NaN values
    n = len(x)
    if n == 0:
        return (float('nan'), float('nan'))
    
    means = np.empty(B, dtype=float)
    for b in range(B):
        idx = np.random.randint(0, n, size=n)
        means[b] = x[idx].mean()
    
    lo = float(np.quantile(means, alpha/2))
    hi = float(np.quantile(means, 1 - alpha/2))
    return lo, hi

# Bootstrap CI for mean p/k ratio
pk_lo, pk_hi = bootstrap_ci_mean(p_over_k, B=BOOTSTRAP_B)

# Bootstrap CI for mean difference in errors (PNT - Z5D)
diff_err = pnt_err_pct - z5d_err_pct
de_lo, de_hi = bootstrap_ci_mean(diff_err, B=BOOTSTRAP_B)

print(f"95% CI mean p/k: [{pk_lo:.2f}, {pk_hi:.2f}]")
print(f"95% CI mean(PNT-Z5D) abs % error: [{de_lo:.4f}%, {de_hi:.4f}%]")

# Test plotting functionality
max_pts = min(len(p_over_k), 1000)  # Limit points for performance

plt.figure()
plt.scatter(p_over_k[:max_pts], log_ratio[:max_pts], s=6, alpha=0.6)
plt.xlabel('p/k')
plt.ylabel('ln(p) / ln(k)')
plt.title('Prime Structure: p/k vs ln(p)/ln(k)')
plt.grid(True, alpha=0.3)
plt.text(0.05, 0.95, f'Pearson r = {r_pk_log:.3f}', transform=plt.gca().transAxes, 
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
plt.tight_layout()
plt.savefig('/tmp/structure_plot.png', dpi=150, bbox_inches='tight')
plt.close()

print("Structure plot saved to /tmp/structure_plot.png")

# Test accuracy plot
step = max(1, len(k_idx) // 1000)

plt.figure()
plt.plot(k_idx[::step], pnt_err_pct[::step], label='PNT abs % error', linewidth=1, alpha=0.8)
plt.plot(k_idx[::step], z5d_err_pct[::step], label='Z5D abs % error', linewidth=1, alpha=0.8)
plt.xlabel('k (prime index)')
plt.ylabel('Absolute % error')
plt.title('Estimator Accuracy vs k')
plt.legend()
plt.grid(True, alpha=0.3)
plt.yscale('log')  # Log scale to show the dramatic difference
plt.text(0.05, 0.95, f'Z5D improvement: {improvement:.1f}%', transform=plt.gca().transAxes,
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
plt.tight_layout()
plt.savefig('/tmp/accuracy_plot.png', dpi=150, bbox_inches='tight')
plt.close()

print("Accuracy plot saved to /tmp/accuracy_plot.png")

print("\n=== NOTEBOOK EXECUTION TEST COMPLETED SUCCESSFULLY ===")
print(f"All cells executed without errors for N_PRIMES={N_PRIMES}")
print(f"Results: Mean p/k={mean_pk:.2f}, Pearson r={r_pk_log:.2f}, Z5D improvement={improvement:.1f}%")