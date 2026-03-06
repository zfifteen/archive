import mpmath as mp
from functools import lru_cache
import math

# Test constants
TEST_SEMIPRIME_N = 18446334808417774117
TEST_FACTOR_P = 4294908329
TEST_FACTOR_Q = 4294930973
mp.dps = 50

@lru_cache(maxsize=None)
def mu(n: int) -> int:
    if n == 1:
        return 1
    prime_factors = 0
    i = 2
    temp_n = n
    while i * i <= temp_n:
        if temp_n % i == 0:
            prime_factors += 1
            temp_n //= i
            if temp_n % i == 0:
                return 0
        i += 1
    if temp_n > 1:
        prime_factors += 1
    return -1 if (prime_factors % 2) else 1

def riemann_R(x: mp.mpf, K: int) -> mp.mpf:
    return mp.nsum(lambda k: mu(int(k)) / mp.mpf(k) * mp.li(x**(mp.mpf(1)/mp.mpf(k))), [1, K])

def riemann_R_prime(x: mp.mpf, K: int) -> mp.mpf:
    ln_x = mp.log(x)
    series_sum = mp.nsum(lambda k: (mu(int(k)) / mp.mpf(k)) * x**(mp.mpf(1)/mp.mpf(k) - 1), [1, K])
    return series_sum / ln_x

def p_newton_R(n: int, K: int = 5, steps: int = 1) -> mp.mpf:
    n_f = mp.mpf(n)
    L = mp.log(n_f)
    L2 = mp.log(L)
    x0 = n_f * (L + L2 - 1 + (L2 - 2) / L)

    x = x0
    for _ in range(steps):
        fx = riemann_R(x, K) - n_f
        f_prime_x = riemann_R_prime(x, K)
        if f_prime_x == 0:
            break
        x = x - fx / f_prime_x
    return x

def is_prime_trial(n):
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

# For the n
n = TEST_SEMIPRIME_N
p = TEST_FACTOR_P
q = TEST_FACTOR_Q
print(f"n = {n}")
print(f"p = {p}, q = {q}")
print(f"sqrt(n) ≈ {n**0.5}")

# To predict next prime after n, since n = p*q, next prime is next after q
# Compute approx pi(q)
approx_pi_q = riemann_R(mp.mpf(q), K=10)
print(f"approx pi({q}) = {float(approx_pi_q)}")

k_next = int(approx_pi_q) + 1
print(f"k_next = {k_next}")

pred_next_prime = p_newton_R(k_next, K=10, steps=2)
print(f"predicted next prime after {q} = {float(pred_next_prime)}")

pred_int = int(pred_next_prime)
print(f"predicted as int: {pred_int}")

# Check if pred_int is prime
is_pred_prime = is_prime_trial(pred_int)
print(f"is {pred_int} prime? {is_pred_prime}")

if not is_pred_prime:
    # Find the next one
    next_candidate = pred_int + 2
    while not is_prime_trial(next_candidate):
        next_candidate += 2
    print(f"actual next prime: {next_candidate}")
else:
    print("prediction matches")

# Also, perhaps use Z framework
# Z = A * (B / c), with c = φ ≈ 1.618
phi = mp.phi
k = 0.3  # recommended
theta_prime = phi * ((q % phi) / phi)**k
print(f"θ'({q}, {k}) = {float(theta_prime)}")

# Perhaps the prediction is the increment or something, but for now, this is it.