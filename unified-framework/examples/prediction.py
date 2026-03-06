import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

PHI = (1 + math.sqrt(5)) / 2
K_OPT = 0.3
THETA_MIN = 0.4
THETA_MAX = 1.2

def is_prime(n):
    """Ground-truth primality test."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def theta_prime(n, k=K_OPT):
    """Geodesic map for prime prediction."""
    mod_phi = n % PHI
    return PHI * ((mod_phi / PHI) ** k)

def predict_candidates(max_n, theta_min=THETA_MIN, theta_max=THETA_MAX):
    """Predict prime candidates using geodesic threshold."""
    candidates = []
    for n in range(2, max_n + 1):
        if n % 2 == 0 and n > 2: continue
        if n % 3 == 0 and n > 3: continue
        theta = theta_prime(n)
        if theta_min <= theta <= theta_max:
            candidates.append(n)
    return candidates

def compute_stats(max_n, candidates):
    """Compute prediction statistics."""
    true_primes = [n for n in range(2, max_n + 1) if is_prime(n)]
    tp = sum(1 for c in candidates if is_prime(c))
    fp = len(candidates) - tp
    fn = len(true_primes) - tp
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    reduction = (1 - len(candidates) / (max_n - 1)) * 100 if max_n > 1 else 0
    print(f"True Primes: {len(true_primes)}")
    print(f"Candidates: {len(candidates)} (Reduction: {reduction:.1f}%)")
    print(f"TP: {tp}, FP: {fp}, FN: {fn}")
    print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
    return true_primes

def visualize_3d(max_n, candidates, true_primes):
    """3D visualization of geodesic embedding."""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Generate positions for all n
    ns = np.arange(2, max_n + 1)
    rs = np.sqrt(ns)
    thetas_scaled = [theta_prime(n) * 2 * math.pi / PHI for n in ns]
    zs = np.log(ns)

    # Plot all points (gray, small)
    ax.scatter(rs * np.cos(thetas_scaled), rs * np.sin(thetas_scaled), zs, c='gray', s=1, alpha=0.1, label='All n')

    # Plot candidates (blue, medium)
    cand_idx = [i for i, n in enumerate(ns) if n in candidates]
    ax.scatter(rs[cand_idx] * np.cos(np.array(thetas_scaled)[cand_idx]),
               rs[cand_idx] * np.sin(np.array(thetas_scaled)[cand_idx]),
               zs[cand_idx], c='blue', s=10, label='Predicted Candidates')

    # Plot true primes (red, large)
    prime_idx = [i for i, n in enumerate(ns) if n in true_primes]
    ax.scatter(rs[prime_idx] * np.cos(np.array(thetas_scaled)[prime_idx]),
               rs[prime_idx] * np.sin(np.array(thetas_scaled)[prime_idx]),
               zs[prime_idx], c='red', s=20, label='True Primes')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z (log n)')
    ax.set_title('3D Geodesic Prime Embedding')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    max_n = 10000  # Adjustable; larger for denser plots
    candidates = predict_candidates(max_n)
    true_primes = compute_stats(max_n, candidates)
    visualize_3d(max_n, candidates, true_primes)