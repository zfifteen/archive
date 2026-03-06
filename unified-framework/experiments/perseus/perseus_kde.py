import math
import mpmath as mp
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import random

# Set high precision for calculations
mp.mp.dps = 50

# --- Official SHA-256 "Nothing Up My Sleeve" Constants ---
H_CONSTANTS_FRAC = [
    0x6a09e667 / (2**32), 0xbb67ae85 / (2**32), 0x3c6ef372 / (2**32), 0xa54ff53a / (2**32),
    0x510e527f / (2**32), 0x9b05688c / (2**32), 0x1f83d9ab / (2**32), 0x5be0cd19 / (2**32),
    ]
K_CONSTANTS_FRAC = [
    0x428a2f98 / (2**32), 0x71374491 / (2**32), 0xb5c0fbcf / (2**32), 0xe9b5dba5 / (2**32),
    0x3956c25b / (2**32), 0x59f111f1 / (2**32), 0x923f82a4 / (2**32), 0xab1c5ed5 / (2**32),
    0xd807aa98 / (2**32), 0x12835b01 / (2**32), 0x243185be / (2**32), 0x550c7dc3 / (2**32),
    0x72be5d74 / (2**32), 0x80deb1fe / (2**32), 0x9bdc06a7 / (2**32), 0xc19bf174 / (2**32),
    0xe49b69c1 / (2**32), 0xefbe4786 / (2**32), 0x0fc19dc6 / (2**32), 0x240ca1cc / (2**32),
    0x2de92c6f / (2**32), 0x4a7484aa / (2**32), 0x5cb0a9dc / (2**32), 0x76f988da / (2**32),
    0x983e5152 / (2**32), 0xa831c66d / (2**32), 0xb00327c8 / (2**32), 0xbf597fc7 / (2**32),
    0xc6e00bf3 / (2**32), 0xd5a79147 / (2**32), 0x06ca6351 / (2**32), 0x14292967 / (2**32),
    0x27b70a85 / (2**32), 0x2e1b2138 / (2**32), 0x4d2c6dfc / (2**32), 0x53380d13 / (2**32),
    0x650a7354 / (2**32), 0x766a0abb / (2**32), 0x81c2c92e / (2**32), 0x92722c85 / (2**32),
    0xa2bfe8a1 / (2**32), 0xa81a664b / (2**32), 0xc24b8b70 / (2**32), 0xc76c51a3 / (2**32),
    0xd192e819 / (2**32), 0xd6990624 / (2**32), 0xf40e3585 / (2**32), 0x106aa070 / (2**32),
    0x19a4c116 / (2**32), 0x1e376c08 / (2**32), 0x2748774c / (2**32), 0x34b0bcb5 / (2**32),
    0x391c0cb3 / (2**32), 0x4ed8aa4a / (2**32), 0x5b9cca4f / (2**32), 0x682e6ff3 / (2**32),
    0x748f82ee / (2**32), 0x78a5636f / (2**32), 0x84c87814 / (2**32), 0x8cc70208 / (2**32),
    0x90befffa / (2**32), 0xa4506ceb / (2**32), 0xbef9a3f7 / (2**32), 0xc67178f2 / (2**32),
    ]

# --- Core Number Theory and Math Functions ---

def is_prime(num):
    """Helper function to check for primality."""
    if num < 2: return False
    if num == 2: return True
    if num % 2 == 0: return False
    for i in range(3, int(math.sqrt(num)) + 1, 2):
        if num % i == 0: return False
    return True

def get_n_composites(n):
    """Gets a list of the first n composite numbers."""
    composites = []
    candidate = 4
    while len(composites) < n:
        if not is_prime(candidate):
            composites.append(candidate)
        candidate += 1
    return composites

def generate_primes_up_to(limit):
    """Generate primes up to a given limit using a sieve."""
    primes = []
    sieve = [True] * (limit + 1)
    for num in range(2, limit + 1):
        if sieve[num]:
            primes.append(num)
            for multiple in range(num*num, limit + 1, num):
                sieve[multiple] = False
    return primes

def fractional_sqrt(x):
    r = mp.sqrt(x)
    return r - mp.floor(r)

def fractional_cbrt(x):
    r = mp.cbrt(x)
    return r - mp.floor(r)

# --- Plotting Function for 1D KDE Heatmap ---

def create_1d_kde_plot(data, title, num_points):
    """Generates a 1D KDE plot visualized as a horizontal heatmap."""
    kde = gaussian_kde(data)

    # Create a grid for the x-axis
    x_grid = np.linspace(0, 1, 500)
    density = kde.evaluate(x_grid)

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 4))

    # Use imshow to create the heatmap from the 1D density array
    # We reshape the density to be (1, N) and display it across the y-axis
    ax.imshow(density[np.newaxis, :], aspect='auto', cmap='viridis', extent=[0, 1, 0, 1])

    # Add a "rug plot" at the bottom to show individual data points
    for point in data:
        ax.axvline(point, ymin=0, ymax=0.1, color='w', alpha=0.5, linewidth=1)

    ax.set_title(title, fontsize=14)
    ax.set_xlabel('Fractional Part Value', fontsize=12)
    ax.set_yticks([]) # Hide y-axis ticks as it's just for visualization
    ax.set_xlim(0, 1)
    fig.suptitle(f'N = {num_points} data points', fontsize=10, y=0.92)


# --- Main Analysis Functions ---

def analyze_sha_constants_distribution():
    """Plot 1: KDE of all official SHA-256 seed constants."""
    print("--- Analyzing SHA-256 Seed Constant Distribution ---")

    # Combine all 72 constants (8 from H, 64 from K)
    all_constants = H_CONSTANTS_FRAC + K_CONSTANTS_FRAC
    data = np.array(all_constants)

    create_1d_kde_plot(
        data,
        'KDE of All SHA-256 Seed Constant Fractional Parts',
        len(all_constants)
    )
    print("SHA constants plot generated.")

def analyze_composite_counterparts_distribution():
    """Plot 2: KDE of composite counterparts to the SHA constants."""
    print("\n--- Analyzing Composite Counterpart Distribution ---")

    # Get fractional parts from first 8 composites (sqrt)
    composites_h = get_n_composites(8)
    frac_h = [float(fractional_sqrt(c)) for c in composites_h]

    # Get fractional parts from first 64 composites (cbrt)
    composites_k = get_n_composites(64)
    frac_k = [float(fractional_cbrt(c)) for c in composites_k]

    all_composites_frac = frac_h + frac_k
    data = np.array(all_composites_frac)

    create_1d_kde_plot(
        data,
        'KDE of Composite Counterpart Fractional Parts',
        len(all_composites_frac)
    )
    print("Composite counterparts plot generated.")

def analyze_large_primes_distribution():
    """Plot 3: KDE of a random sample of primes up to 100,000."""
    num_points = 72 # Match the sample size of the SHA constants
    prime_limit = 100_000
    print(f"\n--- Analyzing Distribution of {num_points} Random Primes < {prime_limit:,} ---")

    # Generate a large pool of primes
    primes_pool = generate_primes_up_to(prime_limit)

    # Take a random sample
    random_sample = random.sample(primes_pool, num_points)

    # Calculate fractional cube roots for the sample
    frac_parts = [float(fractional_cbrt(p)) for p in random_sample]
    data = np.array(frac_parts)

    create_1d_kde_plot(
        data,
        f'KDE of Random Sample of Prime Fractional Parts (cbrt, Primes < {prime_limit:,})',
        num_points
    )
    print("Large primes sample plot generated.")

if __name__ == "__main__":
    # Run the three requested distribution analyses
    analyze_sha_constants_distribution()
    analyze_composite_counterparts_distribution()
    analyze_large_primes_distribution()

    # Show all generated plots at the end
    print("\nDisplaying all plots...")
    plt.show()

