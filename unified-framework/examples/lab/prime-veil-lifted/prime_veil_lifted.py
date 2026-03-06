import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from scipy.stats import entropy
from sympy import primerange, isprime
from random import shuffle

# --- PARAMETERS ---
N = 10000  # Total numbers to process
USE_TSNE = False  # Use PCA or t-SNE for 2D projection

# --- TRANSFORM: Replace with your actual transformation ---
def wave_embedding(n):
    from math import log, exp, sqrt, sin, pi
    if n <= 1: return [0.0, 0.0, 0.0]
    return [
        sin(n / (2 * pi)) / log(n),
        n / exp(log(n)),
        sqrt(n) * sin(log(n))
    ]

# --- Generate Dataset ---
all_nums = list(range(2, N + 2))
primes = [n for n in all_nums if isprime(n)]
composites = [n for n in all_nums if not isprime(n)]

# --- Apply Embedding ---
def embed_sequence(seq):
    return np.array([wave_embedding(n) for n in seq])

embedded_all = embed_sequence(all_nums)
labels_all = np.array([1 if isprime(n) else 0 for n in all_nums])

# --- Dimensionality Reduction ---
def reduce_to_2d(embeddings):
    if USE_TSNE:
        return TSNE(n_components=2, perplexity=30, random_state=42).fit_transform(embeddings)
    return PCA(n_components=2).fit_transform(embeddings)

projected_all = reduce_to_2d(embedded_all)

# --- Visualization ---
def plot_embeddings(proj, labels, title="Prime Separation in Embedding Space"):
    plt.figure(figsize=(10, 6))
    plt.scatter(proj[labels == 0][:, 0], proj[labels == 0][:, 1], alpha=0.3, c='gray', label='Composites')
    plt.scatter(proj[labels == 1][:, 0], proj[labels == 1][:, 1], alpha=0.7, c='red', label='Primes')
    plt.legend()
    plt.title(title)
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

plot_embeddings(projected_all, labels_all)

# --- Disruption Score ---
def sequence_entropy(embeddings):
    flat = embeddings.flatten()
    hist, _ = np.histogram(flat, bins=100, density=True)
    hist = hist[hist > 0]
    return entropy(hist)

full_score = sequence_entropy(embedded_all)
prime_score = sequence_entropy(embed_sequence(primes))
comp_score = sequence_entropy(embed_sequence(composites))

print("Disruption Score Summary")
print("------------------------")
print(f"Full sequence disruption score: {full_score}")
print(f"Prime subsequence disruption score: {prime_score}")
print(f"Composite subsequence disruption score: {comp_score}")

# --- Falsification Run (Shuffled Primes) ---
shuffled = primes.copy()
shuffle(shuffled)
shuffled_proj = reduce_to_2d(embed_sequence(shuffled))
plot_embeddings(shuffled_proj, np.ones_like(shuffled), title="Shuffled Primes: Structure Lost")
