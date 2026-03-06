import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from mpl_toolkits.mplot3d import Axes3D

# ----------------------------
# Universal Frame Shift Constants
# ----------------------------
UNIVERSAL = math.e  # The invariant limit in discrete domain
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio - fundamental to frame geometry
PI_E_RATIO = math.pi / math.e  # Natural scaling between circular and exponential domains

class UniversalFrameShift:
    """
    Implements the Universal Form: Z = A(B/C)
    In discrete domain: Z = n(Δₙ/Δmax)
    """
    def __init__(self, rate: float, invariant_limit: float = UNIVERSAL):
        if rate == 0:
            raise ValueError("Rate cannot be zero")
        self._rate = rate
        self._invariant_limit = invariant_limit
        # Pre-compute the correction factor
        self._correction_factor = rate / invariant_limit

    def transform(self, observed_quantity: float) -> float:
        """Transform from observer frame to universal frame"""
        return observed_quantity * self._correction_factor

    def inverse_transform(self, universal_quantity: float) -> float:
        """Transform from universal frame back to observer frame"""
        return universal_quantity / self._correction_factor

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    r = int(math.sqrt(n)) + 1
    for i in range(3, r, 2):  # Only check odd divisors
        if n % i == 0:
            return False
    return True

def compute_frame_shift(n: int, max_n: int) -> float:
    """
    Compute the frame shift Δₙ at position n
    Based on the logarithmic spiral nature of prime distribution
    """
    if n <= 1:
        return 0.0

    # Frame shift grows logarithmically with position
    # This captures the "stretching" of number space as we move away from origin
    base_shift = math.log(n) / math.log(max_n)

    # Add oscillatory component based on prime gaps
    # This captures the local frame distortions
    gap_phase = 2 * math.pi * n / (math.log(n) + 1) if n > 1 else 0
    oscillation = 0.1 * math.sin(gap_phase)

    return base_shift + oscillation

def prime_density_with_frame_correction(rate: float, helix_freq: float, N_POINTS: int):
    """
    Measure prime density after applying Universal Frame Shift correction
    """
    n = np.arange(1, N_POINTS + 1)
    primality = np.vectorize(is_prime)(n)

    # Compute frame shifts for each position
    frame_shifts = np.array([compute_frame_shift(i, N_POINTS) for i in n])

    # Apply Universal Frame Shift transformation
    transformer = UniversalFrameShift(rate=rate)

    # Base coordinate system enhanced with frame shift awareness
    x = n  # Keep x as natural position

    # Y coordinate: incorporate frame shift into the growth function
    # Using n²/π but modified by frame shift to reveal true structure
    y_base = n * (n / math.pi)
    y_corrected = transformer.transform(y_base * (1 + frame_shifts))

    # Z coordinate: helical component with frame-aware frequency
    # Frequency itself should be corrected for frame shift
    effective_freq = helix_freq * (1 + np.mean(frame_shifts))
    z = np.sin(math.pi * effective_freq * n) * (1 + 0.5 * frame_shifts)

    # Gather corrected prime positions
    prime_indices = primality
    if np.sum(prime_indices) < 2:
        return 0.0

    pts = np.vstack((
        x[prime_indices],
        y_corrected[prime_indices],
        z[prime_indices]
    )).T

    # Use weighted distance calculation
    # Primes closer to origin have different geometric significance
    tree = KDTree(pts)
    dists, indices = tree.query(pts, k=min(3, len(pts)))  # Consider 2 nearest neighbors

    if dists.shape[1] > 1:
        # Weight distances by position to account for frame expansion
        weights = 1.0 / (np.sqrt(pts[:, 0]) + 1)  # Position-based weighting
        weighted_distances = dists[:, 1] * weights
        mean_distance = np.mean(weighted_distances)
    else:
        mean_distance = 1.0

    return 1.0 / mean_distance if mean_distance > 0 else 0.0

def optimize_universal_parameters():
    """
    Optimized parameter search based on Universal Frame Shift principles
    """
    N_POINTS = 3000  # Increased for better statistical significance
    N_CANDIDATES = 200  # More thorough search
    TOP_K = 15

    # Rate parameter (B) search focused around mathematically significant values
    # These ranges are based on universal constants and their relationships
    np.random.seed(42)

    # Focus search around key mathematical relationships
    rate_centers = [
        UNIVERSAL / PHI,      # e/φ - golden ratio scaling
        UNIVERSAL / math.pi,  # e/π - circular to exponential
        UNIVERSAL / 2,        # e/2 - half-domain
        UNIVERSAL,            # e - identity
        UNIVERSAL * PHI / 2,  # e*φ/2 - golden mean
        UNIVERSAL * PI_E_RATIO, # e*π/e = π
    ]

    rates = []
    for center in rate_centers:
        # Add samples around each center with gaussian distribution
        samples = np.random.normal(center, center * 0.15, N_CANDIDATES // len(rate_centers))
        rates.extend(samples)

    # Add some uniform samples to fill gaps
    extra_samples = N_CANDIDATES - len(rates)
    if extra_samples > 0:
        rates.extend(np.random.uniform(UNIVERSAL/3, UNIVERSAL*2, extra_samples))

    rates = np.array(rates[:N_CANDIDATES])

    # Helix frequency search - focus on harmonics of fundamental frequencies
    # Based on the idea that universal frame has natural resonant frequencies
    fundamental_freq = 1.0 / (2 * math.pi)  # Base frequency
    freq_harmonics = [
        fundamental_freq * 0.5,
        fundamental_freq * PHI / 3,
        fundamental_freq * 1.0,
        fundamental_freq * math.sqrt(2),
        fundamental_freq * PHI,
        fundamental_freq * 2.0,
        ]

    frequencies = []
    for harmonic in freq_harmonics:
        samples = np.random.normal(harmonic, harmonic * 0.1, N_CANDIDATES // len(freq_harmonics))
        frequencies.extend(samples)

    extra_freq = N_CANDIDATES - len(frequencies)
    if extra_freq > 0:
        frequencies.extend(np.random.uniform(0.02, 0.25, extra_freq))

    frequencies = np.array(frequencies[:N_CANDIDATES])
    frequencies = np.clip(frequencies, 0.01, 0.5)  # Ensure reasonable bounds

    # Evaluate all combinations
    results = []
    print("Optimizing Universal Frame Shift parameters...")

    for i, (rate, freq) in enumerate(zip(rates, frequencies)):
        if i % 50 == 0:
            print(f"Progress: {i}/{N_CANDIDATES}")

        score = prime_density_with_frame_correction(rate, freq, N_POINTS)
        results.append({
            'rate': rate,
            'freq': freq,
            'score': score,
            'rate_ratio': rate / UNIVERSAL,  # How far from identity transformation
            'mathematical_significance': abs(rate - UNIVERSAL/PHI) + abs(rate - UNIVERSAL/math.pi)  # Closeness to key ratios
        })

    # Sort by score, but also consider mathematical significance
    def composite_score(result):
        normalized_score = result['score']
        # Bonus for mathematically significant ratios
        significance_bonus = 1.0 / (1.0 + result['mathematical_significance'])
        return normalized_score * (1.0 + 0.1 * significance_bonus)

    results.sort(key=composite_score, reverse=True)
    topk = results[:TOP_K]

    return topk, N_POINTS

def visualize_results(topk, N_POINTS):
    """Enhanced visualization with frame shift awareness"""
    # Bar chart of top results
    labels = [f"B/e={r['rate']/UNIVERSAL:.3f}\nf={r['freq']:.3f}" for r in topk]
    scores = [r['score'] for r in topk]

    plt.figure(figsize=(14, 6))
    bars = plt.bar(range(len(topk)), scores, color='darkslategray', alpha=0.8)

    # Color bars by mathematical significance
    for i, (bar, result) in enumerate(zip(bars, topk)):
        if abs(result['rate'] - UNIVERSAL/PHI) < 0.1:
            bar.set_color('gold')  # Golden ratio region
        elif abs(result['rate'] - UNIVERSAL/math.pi) < 0.1:
            bar.set_color('crimson')  # π scaling region

    plt.xticks(range(len(topk)), labels, rotation=45, ha='right')
    plt.ylabel("Frame-Corrected Prime Density Score")
    plt.title("Universal Frame Shift Optimization Results\n(Gold: φ-region, Red: π-region)")
    plt.tight_layout()
    plt.show()

    # Detailed 3D visualization for top 3 results
    n = np.arange(1, N_POINTS + 1)
    primality = np.vectorize(is_prime)(n)
    frame_shifts = np.array([compute_frame_shift(i, N_POINTS) for i in n])

    for idx, params in enumerate(topk[:3], 1):
        rate, freq = params['rate'], params['freq']
        transformer = UniversalFrameShift(rate=rate)

        # Apply transformations
        y_base = n * (n / math.pi)
        y = transformer.transform(y_base * (1 + frame_shifts))
        effective_freq = freq * (1 + np.mean(frame_shifts))
        z = np.sin(math.pi * effective_freq * n) * (1 + 0.5 * frame_shifts)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Plot with frame-shift color coding
        composite_colors = plt.cm.viridis(frame_shifts[~primality] / np.max(frame_shifts))
        ax.scatter(n[~primality], y[~primality], z[~primality],
                   c=composite_colors, alpha=0.3, s=8, label='Composites')

        ax.scatter(n[primality], y[primality], z[primality],
                   c='red', marker='*', s=60, alpha=0.9, label='Primes')

        ax.set_title(f"#{idx}: Rate/e={rate/UNIVERSAL:.3f}, freq={freq:.3f}\n"
                     f"Score={params['score']:.6f}")
        ax.set_xlabel('n (Natural Position)')
        ax.set_ylabel('Frame-Corrected Y')
        ax.set_zlabel('Frame-Aware Helix Z')
        ax.legend()
        plt.tight_layout()
        plt.show()

def main():
    print("Universal Frame Shift Prime Analysis")
    print("="*50)
    print(f"Universal constant (e): {UNIVERSAL:.6f}")
    print(f"Golden ratio (φ): {PHI:.6f}")
    print(f"π/e ratio: {PI_E_RATIO:.6f}")
    print()

    topk, N_POINTS = optimize_universal_parameters()

    print("\nTop Universal Frame Shift Parameters:")
    print("-" * 60)
    for i, result in enumerate(topk[:5], 1):
        print(f"#{i}: Rate={result['rate']:.4f} (B/e={result['rate']/UNIVERSAL:.3f}), "
              f"Freq={result['freq']:.4f}, Score={result['score']:.6f}")

    visualize_results(topk, N_POINTS)

if __name__ == "__main__":
    main()