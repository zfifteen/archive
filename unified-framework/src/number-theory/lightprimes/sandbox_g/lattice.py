import math
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class Numberspace:
    """
    Represents the numberspace formula with C=π, taking integer B (position) in the constructor,
    exposing B and C (pi) as properties, and computing A (observed quantity)
    when called with a numberspace value, using A = numberspace * (B / π).
    """
    def __init__(self, B: int):
        self._B = B
        self._C = math.pi

    @property
    def B(self) -> int:
        """Position on the number line."""
        return self._B

    @property
    def C(self) -> float:
        """Pi as the invariant limit."""
        return self._C

    def __call__(self, numberspace: float) -> float:
        """
        Computes A from the formula: A = numberspace * (B / π)
        Raises ValueError if B is zero to avoid division by zero.
        """
        if self._B == 0:
            raise ValueError("B cannot be zero for computation.")
        return numberspace * (self._B / self._C)

def miller_rabin(n, k=10):
    """Miller-Rabin probabilistic primality test (factorization-avoidant)."""
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n < 2:
        return False
    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# Mock embed_z for z-axis (first dimension of 6D embedding)
def embed_z_dim0(n):
    """Returns sin component of first dimension, mimicking prime hologram embedding."""
    freq = 10000 ** (-2 * 0 / 6)  # First dimension frequency
    return np.sin(freq * n)

# Identify primes up to 1000 using Miller-Rabin
numbers = range(1, 1001)
primes = [n for n in numbers if miller_rabin(n)]

# Generate lattice points for two cases
# Case 1: Constant numberspace = 1.0
points_const = [(n, Numberspace(n)(1.0), np.cos(360 * n)(n)) for n in numbers]
# Case 2: Numberspace = B * log(B)
points_log = [(n, Numberspace(n)(n * math.log(n)), np.cos(360 * n)(n)) for n in numbers]

# Separate primes and non-primes for plotting
x_const, y_const, z_const = zip(*points_const)
x_log, y_log, z_log = zip(*points_log)
prime_indices = [i-1 for i in primes]  # Adjust for 0-based indexing
x_const_primes = [x_const[i] for i in prime_indices]
y_const_primes = [y_const[i] for i in prime_indices]
z_const_primes = [z_const[i] for i in prime_indices]
x_log_primes = [x_log[i] for i in prime_indices]
y_log_primes = [y_log[i] for i in prime_indices]
z_log_primes = [z_log[i] for i in prime_indices]
x_const_nonprimes = [x_const[i] for i in range(len(x_const)) if i not in prime_indices]
y_const_nonprimes = [y_const[i] for i in range(len(y_const)) if i not in prime_indices]
z_const_nonprimes = [z_const[i] for i in range(len(z_const)) if i not in prime_indices]
x_log_nonprimes = [x_log[i] for i in range(len(x_log)) if i not in prime_indices]
y_log_nonprimes = [y_log[i] for i in range(len(y_log)) if i not in prime_indices]
z_log_nonprimes = [z_log[i] for i in range(len(z_log)) if i not in prime_indices]

# Create figure with two 3D subplots
fig = plt.figure(figsize=(14, 6))

# Plot Case 1: Constant numberspace
ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(x_const_nonprimes, y_const_nonprimes, z_const_nonprimes, c='blue', alpha=0.3, s=10, label='Non-primes')
ax1.scatter(x_const_primes, y_const_primes, z_const_primes, c='red', marker='*', s=50, label='Primes')
ax1.set_xlabel('B (Position)')
ax1.set_ylabel('A (Numberspace * B/π)')
ax1.set_zlabel('Z (sin(B))')
ax1.set_title('3D Numberspace Lattice (Constant Input = 1.0, C=π)')
ax1.legend()

# Plot Case 2: Logarithmic numberspace
ax2 = fig.add_subplot(122, projection='3d')
ax2.scatter(x_log_nonprimes, y_log_nonprimes, z_log_nonprimes, c='blue', alpha=0.3, s=10, label='Non-primes')
ax2.scatter(x_log_primes, y_log_primes, z_log_primes, c='red', marker='*', s=50, label='Primes')
ax2.set_xlabel('B (Position)')
ax2.set_ylabel('A (Numberspace * B/π)')
ax2.set_zlabel('Z (sin(B))')
ax2.set_title('3D Numberspace Lattice (Numberspace = B*log(B), C=π)')
ax2.legend()

plt.tight_layout()
plt.savefig('numberspace_lattice_3d_pi_1000.png')
plt.close()