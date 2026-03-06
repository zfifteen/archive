"""Precision stress tests for geometric resonance method.

Tests:
1. Complex Dirichlet kernel summation accuracy vs closed-form across precisions & J.
2. Summation strategies: naive, Kahan, pairwise, vs closed form.
3. Error scaling with J and mp.dps; recommended precision targets.
4. Adaptive m0 sensitivity: score differences for m0, m0±1 across bit sizes (127,160,192,256).

Run: PYTHONPATH=python python3 src/python/resonance_precision_tests.py
"""
from math import log2
import random
import mpmath as mp

# Closed form for complex geometric series sum_{j=0}^J e^{i j θ}
def dirichlet_closed(theta, J):
    # Handle theta ≈ 0 to avoid division by tiny number
    if mp.fabs(mp.fmod(theta, 2*mp.pi)) < 1e-32:
        return J + 1
    return (1 - mp.e**(1j * (J + 1) * theta)) / (1 - mp.e**(1j * theta))

# Naive summation
def dirichlet_naive(theta, J):
    return mp.nsum(lambda j: mp.e**(1j * j * theta), [0, J]) if J < 500 else sum(mp.e**(1j * j * theta) for j in range(0, J + 1))

# Pairwise summation (recursive)
def dirichlet_pairwise(theta, J):
    terms = [mp.e**(1j * j * theta) for j in range(0, J + 1)]
    while len(terms) > 1:
        nxt = []
        for i in range(0, len(terms), 2):
            if i + 1 < len(terms):
                nxt.append(terms[i] + terms[i+1])
            else:
                nxt.append(terms[i])
        terms = nxt
    return terms[0]

# Kahan compensated summation
def dirichlet_kahan(theta, J):
    c = 0+0j
    s = 0+0j
    for j in range(0, J + 1):
        y = mp.e**(1j * j * theta) - c
        t = s + y
        c = (t - s) - y
        s = t
    return s

def rel_err(a, b):
    denom = mp.fabs(b) if b != 0 else 1
    return mp.fabs(a - b) / denom

# Adaptive m0 formula under Z framework
# m0 = round( k * (ln N - 2 ln sqrt(N)) / (2π) ) = round( k * (ln N - ln N) / (2π) ) -> zero if using this simplification.
# Successful run used variant with subtle offset terms; include synthetic curvature adjustment using ln(N+1).

def adaptive_m0(N, k):
    LN = mp.log(N + 1)
    sqrtN = mp.sqrt(N)
    expr = k * (LN - 2 * mp.log(sqrtN)) / (2 * mp.pi)
    return mp.nint(expr)

# Resonance score proxy: higher is better alignment; penalize distance to nearest integer for q_hat
# Use fractional comb approximate p_hat and derive q_hat; purely heuristic for sensitivity comparison.

def resonance_score(N, k, m0):
    # Simplified candidate prime estimate: p_hat ≈ exp( (ln N)/2 - m0/(k+1e-12) )
    LN = mp.log(N)
    p_hat = mp.e**(LN/2 - m0/(k + 1e-12))
    q_hat = N / p_hat
    dist_to_int = mp.fabs(q_hat - mp.nint(q_hat))
    if dist_to_int < mp.mpf('1e-100'):
        return mp.mpf(100)
    return -mp.log(dist_to_int)

# Generate random semiprime near bit size

def random_semiprime(bits):
    # Choose two primes of ~bits/2 each quickly (not cryptographic).
    target_bits_each = bits // 2
    lower = 2**(target_bits_each - 1)
    upper = 2**target_bits_each - 1
    # Use simple primality test (mp.isprime is available)
    # Simple probabilistic primality test (Miller-Rabin) since mpmath lacks isprime
    def is_probable_prime(n, rounds=12):
        if n < 2: return False
        for psmall in [2,3,5,7,11,13,17,19,23,29]:
            if n % psmall == 0:
                return n == psmall
        # write n-1 = d * 2^s
        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for _ in range(rounds):
            a = random.randrange(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for __ in range(s - 1):
                x = (x * x) % n
                if x == n - 1:
                    break
            else:
                return False
        return True
    def rand_prime():
        while True:
            n = random.randrange(lower, upper)
            if is_probable_prime(n):
                return n
    p = rand_prime()
    q = rand_prime()
    return p * q

def test_dirichlet_precision():
    print("== Dirichlet Kernel Precision Tests ==")
    for dps in [64, 128, 256, 512]:
        mp.mp.dps = dps
        print(f"Precision mp.dps={dps}")
        for J in [64, 256, 1024, 4096]:
            # Fixed theta set stressing cancellation
            thetas = [mp.pi/7, mp.pi/13, mp.pi/29, 1/mp.e, mp.pi*mp.sqrt(2)/J]
            for theta in thetas:
                closed = dirichlet_closed(theta, J)
                naive = dirichlet_naive(theta, J)
                pairw = dirichlet_pairwise(theta, J)
                kahan = dirichlet_kahan(theta, J)
                err_naive = rel_err(naive, closed)
                err_pair = rel_err(pairw, closed)
                err_kahan = rel_err(kahan, closed)
                print(f"J={J:5d} theta={mp.nstr(theta,8)} err_naive={float(err_naive):.2e} err_pair={float(err_pair):.2e} err_kahan={float(err_kahan):.2e}")
        print()

def test_m0_sensitivity():
    print("== Adaptive m0 Sensitivity ==")
    random.seed(42)
    for bits in [127, 160, 192, 256]:
        N = random_semiprime(bits)
        mp.mp.dps = 256
        k = mp.mpf('0.30')
        m0 = adaptive_m0(N, k)
        scores = {}
        for delta in [-2, -1, 0, 1, 2]:
            scores[delta] = resonance_score(N, k, m0 + delta)
        spread = max(scores.values()) - min(scores.values())
        print(f"bits={bits} m0={m0} scores={{delta: float(val) for delta,val in scores.items()}} spread={float(spread):.4f}")
    print()

if __name__ == "__main__":
    test_dirichlet_precision()
    test_m0_sensitivity()
    print("Done.")
