# Import necessary libraries (requires Biopython and NumPy installed)
# Import Bio.Seq with proper error handling to prevent confusion
try:
    from Bio.Seq import Seq  # For sequence handling from Biopython
except ImportError:
    raise ImportError("Bio.Seq requires biopython package. Install with: pip install biopython") from None

import numpy as np     # For numerical operations and binning
from math import log, exp, sqrt  # For mathematical computations

# Define divisor count function d(n) from Z Framework
# This counts the number of divisors for n, used in complexity metric κ(n)
def d(n):
    """
    Compute the number of divisors of n.
    - Uses trial division up to sqrt(n) for efficiency.
    - Returns 0 for n <= 0 to avoid errors.
    """
    if n <= 0:
        return 0
    count = 0
    for i in range(1, int(sqrt(n)) + 1):
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
    return count

# Define κ(n) from Z Framework
# Measures "complexity" as d(n) * ln(n+1) / e²; low values indicate simplicity (e.g., primes have d(n)=2)
def kappa(n):
    """
    Compute κ(n) = d(n) * log(n+1) / e².
    - Low κ regions are used to filter simple structures.
    - Returns 0 for n <= 0.
    """
    if n <= 0:
        return 0
    return d(n) * log(n + 1) / exp(1)**2

# Define θ'(n, k) from Z Framework
# Geometric transformation: φ * {n/φ}^k, where φ is the golden ratio
# Maps n to a curved space [0, φ) for clustering analysis
def theta(n, k):
    """
    Compute θ'(n, k) = φ * ((n % φ) / φ)^k.
    - φ ≈ 1.618 (golden ratio) introduces natural scaling.
    - k=0.3 is optimal for prime clustering per framework.
    """
    phi = (1 + 5**0.5) / 2
    mod = n % phi  # Floating-point modulo for continuous mapping
    return phi * (mod / phi) ** k

# Simple sieve to find primes up to N (for demo "special" positions)
def find_primes_up_to(N):
    """
    Generate list of primes up to N using Sieve of Eratosthenes.
    - Used here as proxy for biologically "simple" positions (e.g., conserved sites).
    """
    if N < 2:
        return []
    sieve = [True] * (N + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(sqrt(N)) + 1):
        if sieve[i]:
            for j in range(i*i, N+1, i):
                sieve[j] = False
    return [i for i in range(2, N+1) if sieve[i]]

# Demo: Apply Z Framework to a biological sequence
# Hardcoded sample DNA sequence (could load from FASTA via Bio.SeqIO)
seq = Seq("ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATC")  # Example gene fragment
N = len(seq)  # Sequence length as upper limit for positions (1 to N)

print(f"Analyzing sequence of length {N}: {seq[:20]}...")  # Show snippet

# Compute κ for all positions 1 to N
kappa_vals = np.array([kappa(n) for n in range(1, N+1)])

# Identify lowest 20% κ positions (low complexity, e.g., potential functional regions)
low_kappa_threshold = np.percentile(kappa_vals, 20)
low_kappa_positions = [n for n in range(1, N+1) if kappa(n) <= low_kappa_threshold]

# Define "special" positions: here, prime-numbered positions as demo (could be start codons, GC-rich, etc.)
special_positions = find_primes_up_to(N)  # Primes simulate simple/conserved sites

# Filter special positions in low-κ region
low_kappa_special = [n for n in special_positions if n in low_kappa_positions]

# Compute θ' for low-κ special and total low-κ positions (k=0.3 optimal)
k = 0.3
theta_special = np.array([theta(n, k) for n in low_kappa_special])
theta_total = np.array([theta(n, k) for n in low_kappa_positions])

# Bin into 20 intervals over [0, φ)
phi = (1 + 5**0.5) / 2
bins = np.linspace(0, phi, 21)  # 20 bins
hist_special, _ = np.histogram(theta_special, bins=bins)
hist_total, _ = np.histogram(theta_total, bins=bins)

# Compute relative density and enhancement (max relative density boost)
overall_density = len(low_kappa_special) / len(low_kappa_positions) if low_kappa_positions else 0
rel_density = np.divide(hist_special, hist_total, where=hist_total != 0) / overall_density
enhancement = (np.nanmax(rel_density) - 1) * 100 if overall_density > 0 else 0

# Output results
print(f"Low-κ positions: {len(low_kappa_positions)} ({20}% of {N})")
print(f"Special (prime) positions in low-κ: {len(low_kappa_special)}")
print(f"Max density enhancement in θ' space: {enhancement:.2f}%")
print("Interpretation: Positive enhancement indicates clustering of special positions in geometric space, potentially highlighting biological patterns.")

# Example extension: Check bases at clustered positions (for real analysis)
max_bin_idx = np.argmax(rel_density)
bin_start, bin_end = bins[max_bin_idx], bins[max_bin_idx + 1]
clustered_positions = [n for n in low_kappa_special if bin_start <= theta(n, k) < bin_end]
clustered_bases = [seq[n-1] for n in clustered_positions]
print(f"Bases in max-density bin: {''.join(clustered_bases)}")