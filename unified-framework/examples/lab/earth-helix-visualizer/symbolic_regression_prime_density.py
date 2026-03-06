# symbolic_regression_theta_prime.py

import numpy as np
from sympy import GoldenRatio, pi, E
from pysr import PySRRegressor
from sympy.ntheory import isprime

# -----------------------------
# Step 1: Generate Data
# -----------------------------
n_vals = np.arange(10, 1001)
k_vals = np.arange(1, 11)

# Create meshgrid of (n, k)
n_grid, k_grid = np.meshgrid(n_vals, k_vals)
n_flat = n_grid.flatten()
k_flat = k_grid.flatten()

# Prime density proxy: count of primes ≤ n
def prime_count(n):
    return sum(isprime(i) for i in range(2, n + 1))

# θ′(n, k): candidate formulation
def theta_prime(n, k):
    return np.log(n + k) * (n % k + 1) / (k + 1)

theta_vals = np.array([theta_prime(n, k) for n, k in zip(n_flat, k_flat)])

# Target: normalized prime count
prime_density = np.array([prime_count(n) / n for n in n_flat])

# -----------------------------
# Step 2: Prepare Feature Matrix
# -----------------------------
X = np.column_stack([
    n_flat,                          # n
    k_flat,                          # k
    np.log(n_flat),                  # log(n)
    np.sqrt(n_flat),                # sqrt(n)
    n_flat % k_flat,                 # modular residue
    theta_vals,                      # candidate θ′
    n_flat % float(GoldenRatio),     # {n/φ}
])

y = prime_density

# -----------------------------
# Step 3: Symbolic Regression
# -----------------------------
model = PySRRegressor(
    niterations=100,
    binary_operators=["+", "-", "*", "/", "^"],
    unary_operators=["log", "sqrt", "exp", "sin", "cos"],
    constraints={'^': (-1, 1)},
    extra_sympy_mappings={"phi": GoldenRatio, "pi": pi, "e": E},
    model_selection="best",
    verbosity=1,
    progress=True,
)

model.fit(X, y)

# -----------------------------
# Step 4: Display Results
# -----------------------------
print("\nBest symbolic expressions found:")
print(model)
