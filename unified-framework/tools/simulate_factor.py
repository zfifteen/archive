import mpmath
import random
import math

mpmath.mp.dps = 50
phi = (1 + mpmath.sqrt(5)) / 2
k_star = mpmath.mpf('0.04449')
width_factor = 0.5

def bound_width(n, k=k_star):
    n_mod_phi = mpmath.fmod(mpmath.mpf(n), phi)
    return float(phi * ((n_mod_phi / phi) ** k) * width_factor)

def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def generate_small_semiprime():
    p = random.randint(10, 100)
    while not is_prime(p):
        p += 1
    q = random.randint(10, 100)
    while not is_prime(q) or q == p:
        q += 1
    return p * q, p, q

def factor_shortcut(N, epsilon=0.05):
    sqrtN = int(math.sqrt(N)) + 1
    candidates = []
    k_passes = [0.2, 0.45, 0.8]
    for k in k_passes:
        for i in range(2, sqrtN):
            w = bound_width(i, k)
            if abs(0.5 - w) < epsilon:
                if N % i == 0:
                    return i, N // i, True
    return None, None, False

# Simulate 50 small moduli
random.seed(42)  # For reproducibility
success = 0
total = 50
for _ in range(total):
    N, p, q = generate_small_semiprime()
    f1, f2, factored = factor_shortcut(N)
    if factored:
        success += 1
        print(f"Factored {N} = {f1} x {f2}")
print(f"Success rate: {success / total * 100:.1f}%")