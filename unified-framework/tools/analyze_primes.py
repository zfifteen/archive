import numpy as np
import mpmath as mp

mp.dps = 50

# Generate first 100 primes
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

primes = []
n = 2
while len(primes) < 100:
    if is_prime(n):
        primes.append(n)
    n += 1

gaps = np.diff(primes)

# Z = n * gap / pi
pi_val = float(mp.pi)
Z_vals = [(i+1) * gap / pi_val for i, gap in enumerate(gaps)]

print("Average Z:", np.mean(Z_vals))
print("Std Z:", np.std(Z_vals))
print("Min Z:", np.min(Z_vals))
print("Max Z:", np.max(Z_vals))