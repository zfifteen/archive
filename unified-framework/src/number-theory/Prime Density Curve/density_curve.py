import numpy as np  # For working with arrays and numerical operations
import matplotlib.pyplot as plt  # For making plots and visualizing results
from scipy.stats import entropy  # For calculating KL divergence between distributions
from sympy import primerange, divisors  # For getting prime numbers and divisors
from math import log, e  # For logarithm operations and the Euler's number (e)

# --- Configuration/Set-up ---
N = 1000  # We'll check numbers from 2 up to N
k = 0.313  # Empirically determined curvature exponent for optimal prime-composite separation

# --- Helper Functions ---

def d(n):
    """ 
    Calculate the number of divisors for the given number n.
    Example: divisors of 6 are [1, 2, 3, 6], so d(6) = 4.
    """
    return len(divisors(n))

def kappa(n):
    """
    Compute the curvature of the number n (κ(n)).
    Formula: κ(n) = d(n) * ln(n + 1) / e²
    Explanation: 
    - d(n) represents how "divisible" the number is.
    - ln(n + 1) captures the logarithmic growth of integers.
    - Dividing by e² reduces the range and smooths the curve.
    """
    return d(n) * log(n + 1) / (e ** 2)

def theta_prime(n: int, k: float) -> float:
    """
    Warp curvature value with modular transformation: θ′(n) = (κ(n)^k) mod 1.

    Args:
        n: Positive integer >= 2.
        k: Curvature exponent (e.g., 0.313 found empirically to maximize distribution separation).

    Returns:
        Fractional part of κ(n)^k, in [0, 1).
    """
    return (kappa(n) ** k) % 1

def zeta_shift(n, k):
    """
    Apply a second level of transformation (zeta shift).
    Formula: Z(n) = n * θ′(n)
    Explanation:
    - Multiplies the number n by its warped curvature θ′(n).
    """
    return n * theta_prime(n, k)

# --- Generate Data ---

# Create a list of numbers starting from 2 up to N
x = np.arange(2, N + 1)

# Find the curvature κ(n) for every number
kappa_vals = np.array([kappa(n) for n in x])

# Calculate warped curvature (θ′(n)) for every number
theta_vals = np.array([theta_prime(n, k) for n in x])

# Apply the zeta shift transformation Z(n) for every number
z_vals = np.array([zeta_shift(n, k) for n in x])

# --- Identify Primes ---

# Use sympy's primerange to get all prime numbers between 2 and N
primes = set(primerange(2, N + 1))

# Create an array: 1 for primes, 0 for composites
# (We check if each number in x is a prime)
is_prime = np.array([int(n in primes) for n in x])

# --- Analysis ---

# Set up bins for splitting θ′(n) into groups (e.g., 40 intervals from 0 to 1)
bins = np.linspace(0, 1, 40)

# Make histograms for primes and non-primes within θ′(n) space
hist_prime, _ = np.histogram(theta_vals[is_prime == 1], bins=bins, density=True)  # Primes
hist_comp, _ = np.histogram(theta_vals[is_prime == 0], bins=bins, density=True)  # Composites

# KL Divergence: Measure how different the prime and composite histograms are
# (A metric for comparing two sets of distributions)
kl_divergence = entropy(hist_prime + 1e-12, hist_comp + 1e-12)  # Add tiny smoothing to avoid issues with zeros

# Gini Coefficient: Measure inequality (like income inequality but for distributions)
def gini(array):
    """
    Calculate the Gini coefficient of the data.
    Explanation:
    - Sort the array from smallest to largest.
    - Compute the inequality based on cumulative sums of sorted values.
    """
    sorted_arr = np.sort(array)
    n = len(array)
    return (2 * np.sum((np.arange(1, n + 1)) * sorted_arr) / (n * np.sum(sorted_arr))) - (n + 1) / n

# Compute Gini Coefficients for primes and composites
gini_prime = gini(hist_prime)
gini_comp = gini(hist_comp)

# --- Plotting ---

# Plot histogram for θ′(n) distributions of primes and composites
plt.figure(figsize=(10, 6))
plt.hist(theta_vals[is_prime == 1], bins=bins, alpha=0.6, label='Primes', density=True)
plt.hist(theta_vals[is_prime == 0], bins=bins, alpha=0.6, label='Composites', density=True)
plt.title(f"θ′(n) Density Distribution (k = {k})")  # Title explains the plot
plt.xlabel("θ′(n)")  # x-axis shows the warped curvature values
plt.ylabel("Density")  # y-axis shows how often values appear
plt.legend()  # Add labels to explain which curve is for primes or composites
plt.grid(True)  # Add a grid for easier viewing
plt.tight_layout()  # Adjust space in the plot to fit everything nicely
plt.show()  # Display the plot

# --- Output Summary ---

# Print out the results of our calculations
print(f"KL Divergence (Primes || Composites): {kl_divergence:.4f}")
print(f"Gini Coefficient (Primes): {gini_prime:.4f}")
print(f"Gini Coefficient (Composites): {gini_comp:.4f}")

# Plot Z(n) data (trajectory of zeta-shift transform)
plt.figure(figsize=(10, 5))  # Set up the size of the plot
plt.plot(x, z_vals, label="Z(n) = n·θ′(n)", lw=0.8)  # Line plot for Z(n)
plt.title("Zeta-Shift Transform Trajectory Z(n)")  # Title for the plot
plt.xlabel("n")  # x-axis shows the number n
plt.ylabel("Z(n)")  # y-axis shows the value of Z(n)
plt.grid(True)  # Add grid to make it readable
plt.tight_layout()  # Tweak spacing so labels don't overlap
plt.show()  # Display the plot
