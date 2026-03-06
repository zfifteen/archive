import math, random
from sympy import sieve

PHI = (1 + 5 ** 0.5) / 2

def frac(x: float) -> float:
    return x - math.floor(x)

def theta_prime(n: int, k: float) -> float:
    t = frac(n / PHI)
    return frac(PHI * (t ** k))

def circ_dist(a: float, b: float) -> float:
    d = (a - b + 0.5) % 1.0 - 0.5
    return abs(d)

def is_probable_prime(n: int) -> bool:
    if n < 2: return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # Deterministic Miller-Rabin for 64-bit
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in [2, 3, 5, 7, 11, 13]:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: 
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_candidates(N: int, eps: float, k: float, prime_pool):
    tN = theta_prime(N, k)
    C = []
    for p in prime_pool:
        tp = theta_prime(p, k)
        if circ_dist(tp, tN) <= eps:
            C.append(p)
    return C

def factorize_multi_pass(N: int, eps: float, k_values, prime_pool):
    divisions = 0
    for k in k_values:
        C = generate_candidates(N, eps, k, prime_pool)
        divisions += len(C)
        for p in C:
            if p > 1 and N % p == 0:
                q = N // p
                if is_probable_prime(q):
                    return True, divisions, (p, q), k
    return False, divisions, None, None

def sample_semiprimes(Nmax, samples, rng):
    semis = []
    while len(semis) < samples:
        # Generate two random primes
        p = rng.randint(2, int(Nmax**0.5))
        while not is_probable_prime(p):
            p = rng.randint(2, int(Nmax**0.5))
        q = rng.randint(2, int(Nmax**0.5))
        while not is_probable_prime(q):
            q = rng.randint(2, int(Nmax**0.5))
        if p * q < Nmax:
            semis.append((min(p,q), max(p,q), p*q))
    return semis

def main():
    rng = random.Random(42)
    Nmax = 10**12  # Larger N for RSA-like
    prime_limit = int(3 * (Nmax**0.5)) + 200
    print(f"Generating primes up to {prime_limit}")
    prime_pool = list(sieve.primerange(prime_limit))

    SAMPLES = 100
    k_values = [i/10.0 for i in range(1,10)]  # Experiment: 0.1 to 0.9 in steps of 0.1
    eps = 0.05  # eps_success

    semis = sample_semiprimes(Nmax, SAMPLES, rng)

    succ = 0
    failed = []
    for (p,q,N) in semis:
        ok, d, fac, k = factorize_multi_pass(N, eps, k_values, prime_pool)
        if ok:
            succ += 1
        else:
            failed.append((p,q,N))

    print(f"Success rate: {succ / SAMPLES * 100}% ({succ}/{SAMPLES})")
    print(f"Failed cases: {len(failed)}")

    # Analyze first 5 failed
    for i, (p,q,N) in enumerate(failed[:5]):
        print(f"\nFailed {i+1}: N={N}, p={p}, q={q}")
        min_dist_p = min(circ_dist(theta_prime(N, k), theta_prime(p, k)) for k in k_values)
        min_dist_q = min(circ_dist(theta_prime(N, k), theta_prime(q, k)) for k in k_values)
        print(f"Min circ_dist for p: {min_dist_p}")
        print(f"Min circ_dist for q: {min_dist_q}")
        print(f"eps: {eps}")

if __name__ == "__main__":
    main()