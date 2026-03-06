import os
import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.fft import fft, fftfreq
from scipy.stats import zscore, entropy
from sklearn.mixture import GaussianMixture
from sympy import divisor_count, isprime
from domain import UniversalZetaShift

# Write domain.py if not exists
if not os.path.exists('domain.py'):
    with open('domain.py', 'w') as f:
        f.write('''"""
domain.py: Implementation of the Zeta Shift inheritance model based on the Universal Form Transformer.

This module defines classes that faithfully reproduce the inheritance model for the Z definition,
unifying relativistic physics with discrete mathematics by normalizing observations against invariant limits.

Key Aspects:
- Universal Form: Z = A(B/C), where A is the reference frame-dependent quantity,
  B is the rate, and C is the universal invariant (speed of light or analogous limit).
- Physical Domain: Z = T(v/c), specializing A=T (measured quantity), B=v (velocity), C=c (speed of light).
- Discrete Domain: Z = n(Δₙ/Δmax), specializing A=n (integer observation), B=Δₙ (frame shift at n), C=Δmax (max frame shift).

The model reveals shared geometric topology across domains, emphasizing curvature from frame-dependent shifts.
"""

from abc import ABC
import math

class UniversalZetaShift(ABC):
    def __init__(self, a, b, c):
        if c == 0:
            raise ValueError("Universal invariant C cannot be zero.")
        self.a = a
        self.b = b
        self.c = c

    def compute_z(self):
        return self.a * (self.b / self.c)

    def getD(self):
        if self.a == 0:
            raise ValueError("Division by zero: 'a' cannot be zero in getD().")
        return self.c / self.a

    def getE(self):
        if self.b == 0:
            raise ValueError("Division by zero: 'b' cannot be zero in getE().")
        return self.c / self.b

    def getF(self):
        return self.getD() / self.getE()

    def getG(self):
        f = self.getF()
        if f == 0:
            raise ValueError("Division by zero: 'F' cannot be zero in getG().")
        return self.getE() / f

    def getH(self):
        g = self.getG()
        if g == 0:
            raise ValueError("Division by zero: 'G' cannot be zero in getH().")
        return self.getF() / g

    def getI(self):
        h = self.getH()
        if h == 0:
            raise ValueError("Division by zero: 'H' cannot be zero in getI().")
        return self.getG() / h

    def getJ(self):
        i = self.getI()
        if i == 0:
            raise ValueError("Division by zero: 'I' cannot be zero in getJ().")
        return self.getH() / i

    def getK(self):
        j = self.getJ()
        if j == 0:
            raise ValueError("Division by zero: 'J' cannot be zero in getK().")
        return self.getI() / j

    def getL(self):
        k = self.getK()
        if k == 0:
            raise ValueError("Division by zero: 'K' cannot be zero in getL().")
        return self.getJ() / k

    def getM(self):
        l = self.getL()
        if l == 0:
            raise ValueError("Division by zero: 'L' cannot be zero in getM().")
        return self.getK() / l

    def getN(self):
        m = self.getM()
        if m == 0:
            raise ValueError("Division by zero: 'M' cannot be zero in getN().")
        return self.getL() / m

    def getO(self):
        n = self.getN()
        if n == 0:
            raise ValueError("Division by zero: 'N' cannot be zero in getO().")
        return self.getM() / n''')

# Generate CSV if not exists
DATA_PATH = "zeta_shifts_1_to_100000.csv"
if not os.path.exists(DATA_PATH):
    from domain import UniversalZetaShift

    data = []
    for n in range(1, 100001):
        a = float(n)
        b = np.log(a + 1)
        c = np.exp(1)
        uz = UniversalZetaShift(a, b, c)
        row = {
            'n': n,
            'a': a,
            'b': b,
            'c': c,
            'z': uz.compute_z(),
            'D': uz.getD(),
            'E': uz.getE(),
            'F': uz.getF(),
            'G': uz.getG(),
            'H': uz.getH(),
            'I': uz.getI(),
            'J': uz.getJ(),
            'K': uz.getK(),
            'L': uz.getL(),
            'M': uz.getM(),
            'N': uz.getN(),
            'O': uz.getO(),
        }
        data.append(row)

    df_gen = pd.DataFrame(data)
    df_gen.to_csv(DATA_PATH, index=False)

# Now run the analysis

sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# 1. Load & Validate Data
df = pd.read_csv(DATA_PATH)
print("✅ Loaded:", DATA_PATH)

print("\nSchema and Sample Rows:")
print(df.dtypes)
print(df.head(10))

print("\nMissing Values:")
print(df.isnull().sum())

req_cols = ['n','a','b','c','z','D','E','F','G','H','I','J','K','L','M','N','O']
missing = set(req_cols) - set(df.columns)
if missing:
    print("⚠️ Missing columns:", missing)

# 2. Recompute Z–O via UniversalZetaShift (validation & augmentation)
print("\nRecomputing Z–O with UniversalZetaShift...")
c_global = df['c'].iloc[0] if df['c'].nunique()==1 else df['b'].max()
metrics = ['z','D','E','F','G','H','I','J','K','L','M','N','O']
for m in metrics:
    df[m + "_calc"] = np.nan

for idx, row in df.iterrows():
    uz = UniversalZetaShift(a=row['a'], b=row['b'], c=c_global)
    df.at[idx, 'z_calc'] = uz.compute_z()
    df.at[idx, 'D_calc'] = uz.getD()
    df.at[idx, 'E_calc'] = uz.getE()
    df.at[idx, 'F_calc'] = uz.getF()
    df.at[idx, 'G_calc'] = uz.getG()
    df.at[idx, 'H_calc'] = uz.getH()
    df.at[idx, 'I_calc'] = uz.getI()
    df.at[idx, 'J_calc'] = uz.getJ()
    df.at[idx, 'K_calc'] = uz.getK()
    df.at[idx, 'L_calc'] = uz.getL()
    df.at[idx, 'M_calc'] = uz.getM()
    df.at[idx, 'N_calc'] = uz.getN()
    df.at[idx, 'O_calc'] = uz.getO()

# Quick check: compare original vs. recomputed
diffs = {m: np.max(np.abs(df[m] - df[f"{m}_calc"])) for m in metrics if m in df}
print("\nMax absolute differences (orig vs. calc):")
print(diffs)

# 3. Summary Statistics & Correlations
print("\nDescriptive Statistics for Z–O:")
print(df[[f"{m}_calc" for m in metrics]].describe().T)

plt.figure()
sns.heatmap(df[['a','b','z_calc','D_calc','E_calc','F_calc']].corr(),
            annot=True, fmt=".2f", cmap="vlag")
plt.title("Correlation Matrix (select metrics)")
plt.show()

# 4. Distributional Analyses
fig, axes = plt.subplots(2, 2, figsize=(12,8))
sns.histplot(df['b'], bins=50, ax=axes[0,0]).set(title="Distribution of b")
sns.histplot(df['z_calc'], bins=50, ax=axes[0,1]).set(title="Distribution of Z")
sns.histplot(np.log(df['O_calc'] + 1), bins=50, ax=axes[1,0]).set(title="Log Distribution of O")
sns.boxplot(x=df['F_calc'], ax=axes[1,1]).set(title="Boxplot of F")
plt.tight_layout()
plt.show()

# 5. Fourier / Spectral Analysis on b (or z)
signal = df['b'] - df['b'].mean()
N = len(signal)
freqs = fftfreq(N)
fft_vals = fft(signal.values)
power = np.abs(fft_vals)**2

plt.figure()
plt.plot(freqs[1:N//2], power[1:N//2])
plt.title("FFT Power Spectrum of (b - mean)")
plt.xlabel("Frequency")
plt.ylabel("Power")
plt.show()

# 6. Golden-Ratio Transform & Helical Geodesics
phi = (1 + np.sqrt(5)) / 2
k_opt = 3.33
df['theta_phi'] = phi * ((df['n'] % phi) / phi) ** k_opt

# Helical coords
df['helix_x'] = df['z_calc'] * np.sin(2 * np.pi * df['n'] / 10)
df['helix_y'] = df['z_calc'] * np.cos(2 * np.pi * df['n'] / 10)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(df['n'], df['helix_x'], df['helix_y'],
           c=df['theta_phi'], cmap='viridis', s=5)
ax.set(title="Helical Geodesic Colored by θ'(n)")
plt.show()

# 7. Fractal Dimension (box-Counting) of O_calc sequence
def box_count(series, box_sizes):
    counts = []
    vals = series.values
    finite_vals = vals[np.isfinite(vals)]
    if len(finite_vals) == 0:
        return [0] * len(box_sizes)
    min_val = finite_vals.min()
    max_val = finite_vals.max()
    for size in box_sizes:
        bins = np.arange(min_val, max_val + size, size)
        hist, _ = np.histogram(finite_vals, bins)
        counts.append(np.sum(hist > 0))
    return counts

log_O = np.log(df['O_calc'] + 1)
box_sizes = np.logspace(np.log10(log_O.min() + 1e-10), np.log10(log_O.max() + 1), 20)
counts = box_count(log_O, box_sizes)
coef = np.polyfit(np.log(box_sizes), np.log(counts + 1e-10), 1)[0]
print(f"\nEstimated Fractal Dimension (-box-count slope on log O): {-coef:.3f}")

# 8. Prime-Geometry & κ(n) Metric
df['is_prime'] = df['n'].apply(isprime)
df['kappa'] = df['n'].apply(divisor_count) * np.log(df['n'] + 1) / math.e**2

# Compute prime gaps
primes = df.loc[df['is_prime'], 'n'].values
if len(primes) > 1:
    gaps = np.diff(primes)
    prime_gap_map = {p: g for p, g in zip(primes[:-1], gaps)}
    df['prime_gap'] = df['n'].map(prime_gap_map).fillna(0).astype(int)
else:
    df['prime_gap'] = 0

sns.histplot(df.loc[df['is_prime'], 'kappa'], color='C1', label='primes', alpha=0.6)
sns.histplot(df.loc[~df['is_prime'], 'kappa'], color='C2', label='composites', alpha=0.6)
plt.legend()
plt.title("κ(n) Distribution: Primes vs. Composites")
plt.show()

# 9. Clustering & Anomaly Detection
features = df[['z_calc','kappa','prime_gap']].fillna(0)
gmm = GaussianMixture(n_components=3, random_state=42).fit(features)
df['cluster'] = gmm.predict(features)

sns.scatterplot(x='z_calc', y='kappa', hue='cluster', data=df, palette='tab10', s=10)
plt.title("GMM Clusters in (Z, κ) Space")
plt.show()

# Anomalies in O_calc (z-score > 4)
df['O_zscore'] = zscore(np.log(df['O_calc'] + 1))
anomalies = df[np.abs(df['O_zscore']) > 4]
print("\nTop anomalies in O_calc (|z|>4):")
print(anomalies[['n','O_calc','O_zscore']].head(10))

# 10. Spectral Entropy & Wave-CRISPR-Style Score
window = 128
entropies = []
for i in range(len(df) - window + 1):
    seg = df['z_calc'].iloc[i:i+window]
    if len(seg) < window:
        entropies.append(np.nan)
        continue
    mean_seg = seg.mean()
    segCentered = seg - mean_seg
    ps = np.abs(fft(segCentered.values))**2 + 1e-10  # Avoid zero
    ps_norm = ps / ps.sum()
    ent = entropy(ps_norm)
    entropies.append(ent if np.isfinite(ent) else 0)
if len(entropies) < len(df):
    entropies += [np.nan] * (len(df) - len(entropies))
df['spectral_entropy'] = entropies

# Define a toy “wave-CRISPR” score
df['wave_crispr'] = df['z_calc'] * df['spectral_entropy']

# Plot spectral entropy
plt.plot(df['n'], df['spectral_entropy'], alpha=0.7)
plt.title("Spectral Entropy of Z (sliding window)")
plt.xlabel("n")
plt.ylabel("Entropy")
plt.show()

# Save augmented dataset & key figures
OUT_DIR = "analysis_output"
os.makedirs(OUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUT_DIR, "zeta_shifts_enriched.csv"), index=False)
print(f"\n✅ Saved enriched dataset to {OUT_DIR}/zeta_shifts_enriched.csv")