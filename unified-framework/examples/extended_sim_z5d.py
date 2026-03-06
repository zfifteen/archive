import mpmath as mp
from mpmath import mpmathify, exp, log, pi, sqrt, cos, sin, atan2
import gmpy2
import random

# Set high precision
mp.dps = 50

# Z5D parameters
k = mpmathify(0.04449)

def compute_theta(p, q):
    """Compute theta from p and q"""
    return (p + q) / 2

def compute_theta_prime(N, theta, epsilon, k):
    """Compute theta_prime with epsilon threshold"""
    delta = mp.sqrt(theta**2 - N)
    if abs(delta) < epsilon:
        delta = mpmathify(0)
    phi = atan2(mpmathify(0), delta)  # Assuming real part, but for complex
    # Simplified Z5D geodesic
    theta_prime = theta * exp(mpmathify(1j) * k * phi)
    return theta_prime

def kappa_n(success_count, total):
    """Simple kappa metric: success rate"""
    return success_count / total if total > 0 else 0

def delta_n_guard(p, q, N):
    """Delta_n guard: discriminant-like metric for separation"""
    return abs(p - q) / sqrt(N)

# Mock large N ~10^18: p,q ~10^9
def generate_mock_large_primes():
    p = gmpy2.next_prime(random.randint(10**9, 2*10**9))
    q = gmpy2.next_prime(random.randint(10**9, 2*10**9))
    N = p * q
    return mpmathify(p), mpmathify(q), mpmathify(N)

# Grid search epsilon
epsilons = [mpmathify(0.2 + i*0.01) for i in range(11)]
results = []

for eps in epsilons:
    successes = 0
    total = 100  # Small sim for speed
    deltas = []
    for _ in range(total):
        p, q, N = generate_mock_large_primes()
        theta = compute_theta(p, q)
        theta_prime = compute_theta_prime(N, theta, eps, k)
        # Mock success: if real(theta_prime) close to p or q (simplified)
        if abs(theta_prime.real - p) < 1e-10 or abs(theta_prime.real - q) < 1e-10:
            successes += 1
        deltas.append(delta_n_guard(p, q, N))
    avg_delta = sum(deltas) / len(deltas)
    kappa = kappa_n(successes, total)
    results.append((eps, kappa, avg_delta))

# Find optimal
optimal = max(results, key=lambda x: x[1])
print(f"Optimal epsilon: {optimal[0]}, kappa: {optimal[1]}, avg_delta: {optimal[2]}")
for r in results:
    print(f"Eps: {r[0]}, Kappa: {r[1]}, Delta: {r[2]}")