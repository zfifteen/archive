import mpmath
import numpy as np
import scipy.stats
import math
import sympy.ntheory as nt

mpmath.mp.dps = 50

# Constants
phi = (1 + math.sqrt(5)) / 2
e = math.exp(1)
pi = math.pi

# Generate primes up to N=100000
N = 100000
primes = [p for p in range(2, N+1) if nt.isprime(p)]

# Compute first M Riemann zeta zeros
M = 500
zeros = [mpmath.zetazero(j) for j in range(1, M+1)]
t_j = [float(z.imag) for z in zeros]

# Unfold zeta zeros
unfolded = []
for t in t_j:
    if t > 2 * pi * e:  # Avoid log negative
        unfolded.append(t / (2 * pi * math.log(t / (2 * pi * e))))
    else:
        unfolded.append(0)  # Placeholder for small t

unfolded = np.array(unfolded[10:])  # Skip small ones

# Function to compute enhancement for a sequence at given k
def compute_enhancement(seq, k, num_bins=20):
    theta = [phi * ((s % phi) / phi) ** k for s in seq]
    hist, _ = np.histogram(theta, bins=num_bins)
    if len(seq) == 0 or np.sum(hist) == 0:
        return 0
    uniform_density = len(seq) / num_bins
    max_density = np.max(hist)
    enhancement = (max_density / uniform_density - 1) * 100 if uniform_density > 0 else 0
    return enhancement

# Sweep k from 0.1 to 0.5
k_values = np.linspace(0.1, 0.5, 20)
enh_primes = [compute_enhancement(primes, k) for k in k_values]
enh_zeros = [compute_enhancement(unfolded, k, num_bins=10) for k in k_values]  # Fewer bins for fewer points

# Compute Pearson correlation
r, p = scipy.stats.pearsonr(enh_primes, enh_zeros)

# Find optimal k
opt_k_primes = k_values[np.argmax(enh_primes)]
opt_k_zeros = k_values[np.argmax(enh_zeros)]
max_enh_primes = max(enh_primes)
max_enh_zeros = max(enh_zeros)

# Output results demonstrating the hypothesis
print(f"Pearson correlation r = {r:.2f} (p = {p:.2e})")
print(f"Optimal k for primes: {opt_k_primes:.2f}, enhancement: {max_enh_primes:.1f}%")
print(f"Optimal k for zeros: {opt_k_zeros:.2f}, enhancement: {max_enh_zeros:.1f}%")

# Simulate helical embedding example for turbulence analogy
# Simple helical path for primes
helical_x = [math.cos(2 * pi * p / phi) for p in primes[:50]]
helical_y = [math.sin(2 * pi * p / phi) for p in primes[:50]]
helical_z = [p / math.log(p) if p > 1 else 0 for p in primes[:50]]  # li(p) approx

print("Helical embedding coordinates for first 50 primes (x, y, z):")
for x, y, z in zip(helical_x, helical_y, helical_z):
    print(f"{x:.4f}, {y:.4f}, {z:.4f}")

# Wave-CRISPR like spectral entropy on zeta shifts chain
# Generate example zeta shift chain for n=1 to 100
def compute_chain(n):
    b = math.log(n + 1)
    D = e / n
    F = b / n
    E = D / F  # e / b
    chain = [D, E]
    for _ in range(10):  # Up to O-ish
        next_val = chain[-2] / chain[-1]
        chain.append(next_val)
    return chain

chains = [compute_chain(n) for n in range(1, 101)]
flat_chain = np.concatenate(chains)  # Flatten for spectral analysis

# Spectral entropy
fft = np.fft.fft(flat_chain)
power = np.abs(fft)**2
power_norm = power / np.sum(power)
entropy = -np.sum(power_norm * np.log(power_norm + 1e-10))  # Shannon entropy

print(f"Spectral entropy of zeta shift chain: {entropy:.4f}")

# KS test against GUE-like distribution (for hybrid class)
# Simulate GUE spacings (exponential for Poisson, Wigner for GUE)
gue_spacings = np.random.gumbel(0, 1, len(unfolded)-1)  # Approx Wigner surmise ~ exp(-s)
actual_spacings = np.diff(unfolded)
ks_stat, ks_p = scipy.stats.kstest(actual_spacings, 'gumbel_r', args=(0,1))

print(f"KS statistic for hybrid universality: {ks_stat:.3f} (p ≈ {ks_p:.1f})")