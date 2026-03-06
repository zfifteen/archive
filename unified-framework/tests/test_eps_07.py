import random
import math
import numpy as np

# Set RNG seed for reproducibility
random.seed(42)
np.random.seed(42)

# Golden ratio
phi = (1 + math.sqrt(5)) / 2

def theta_prime(n, k):
    return phi * ((n % phi) / phi) ** k

def circular_distance(a, b):
    diff = abs(a - b) % (2 * math.pi)
    return min(diff, 2 * math.pi - diff)

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

def generate_semiprime():
    p = random.randint(10000, 3000000)
    while not is_prime(p):
        p = random.randint(10000, 3000000)
    q = random.randint(10000, 3000000)
    while not is_prime(q):
        q = random.randint(10000, 3000000)
    return p * q, p, q

def factor_with_geom(n, eps=0.07):  # Increased eps to 0.07
    k_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    candidates = set()
    for k in k_values:
        theta_n = theta_prime(n, k) % (2 * math.pi)
        # Generate potential primes near theta_n within eps
        # For simplicity, brute-force small primes (up to 3e6 as before)
        for p in range(2, 3000001):
            if is_prime(p):
                theta_p = theta_prime(p, k) % (2 * math.pi)
                if circular_distance(theta_n, theta_p) <= eps:
                    candidates.add(p)
    # Now check candidates
    for p in sorted(candidates):
        if p > math.sqrt(n):
            break
        if n % p == 0:
            q = n // p
            if is_prime(q):
                return p, q
    return None

# Test on 10 random semiprimes first (conservative)
success_count = 0
total = 10
for i in range(total):
    n, true_p, true_q = generate_semiprime()
    result = factor_with_geom(n, eps=0.07)
    if result:
        success_count += 1
    else:
        print(f"Failed: N={n}, p={true_p}, q={true_q}")

print(f"Success rate with eps=0.07 on {total} tests: {success_count}/{total} = {success_count/total*100:.1f}%")