
import math, random

PHI = (1 + 5 ** 0.5) / 2

def frac(x: float) -> float:
    return x - math.floor(x)

def theta_prime(n: int, k: float) -> float:
    # θ'(n,k) = frac( PHI * frac(n/PHI)^k )
    t = frac(n / PHI)
    return frac(PHI * (t ** k))

def circ_dist(a: float, b: float) -> float:
    d = (a - b + 0.5) % 1.0 - 0.5
    return abs(d)

def sieve(limit: int):
    if limit < 2: return []
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    for p in range(2, int(limit ** 0.5) + 1):
        if is_prime[p]:
            step = p
            start = p*p
            is_prime[start:limit+1:step] = b"\x00" * ((limit - start)//step + 1)
    return [i for i in range(2, limit+1) if is_prime[i]]

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

def wilson_ci(succ: int, n: int, z=1.96):
    if n == 0: return 0.0, 0.0, 0.0
    p = succ / n
    denom = 1 + (z*z)/n
    center = (p + (z*z)/(2*n)) / denom
    half = z * math.sqrt((p*(1-p)/n) + (z*z)/(4*n*n)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)

def sample_semiprimes_balanced(Nmax, prime_pool, samples, rng):
    # balanced: p, q around sqrt(Nmax)
    R = int(Nmax**0.5)
    band = (max(2, R//2), R*2)
    S = [p for p in prime_pool if band[0] <= p <= band[1]]
    if not S: S = prime_pool
    candidates = []
    while len(candidates) < samples:
        p = rng.choice(S); q = rng.choice(S)
        if p*q < Nmax:
            candidates.append((min(p,q), max(p,q), p*q))
    return candidates

def main():
    rng = random.Random(42)
    Nmax = 50_000_000  # keep it fast
    prime_limit = int(3*(Nmax**0.5)) + 200
    prime_pool = sieve(prime_limit)

    # Build dataset
    SAMPLES = 300
    k_values = [0.200, 0.450, 0.800]
    eps_success = 0.05
    eps_eff = 0.02

    # choose sampler
    semis = sample_semiprimes_balanced(Nmax, prime_pool, SAMPLES, rng)
    maxN = max(N for _,_,N in semis)
    naive = sum(1 for p in prime_pool if p <= int(maxN**0.5))

    # --- Success @ eps_success ---
    succ = 0; divs = 0; wins = {k:0 for k in k_values}
    for (p,q,N) in semis:
        ok, d, fac, k = factorize_multi_pass(N, eps_success, k_values, prime_pool)
        if ok:
            succ += 1
            wins[k] += 1
            divs += d
    rate, lo, hi = wilson_ci(succ, len(semis))
    avg_divs = (divs / succ) if succ else 0.0
    eff_gain = naive / avg_divs if avg_divs>0 else 0.0

    print("=== DEMO RESULTS ===")
    print(f"Semiprimes: {len(semis)}, Nmax={Nmax:,}, prime_pool<= {prime_limit:,} (|P|={len(prime_pool)})")
    print(f"Success @ eps={eps_success:.2f}: {rate*100:.1f}% ({lo*100:.1f}-{hi*100:.1f})")
    print(f"Avg divisions until success: {avg_divs:.1f}  |  Efficiency: {eff_gain:.1f}x faster vs naive~{naive}")
    print("Per-pass contribution:", {f'{k:.3f}': wins[k] for k in k_values})

    # --- Efficiency @ eps_eff ---
    succ2 = 0; divs2 = 0
    for (p,q,N) in semis:
        ok, d, fac, k = factorize_multi_pass(N, eps_eff, k_values, prime_pool)
        if ok:
            succ2 += 1
            divs2 += d
    avg_divs2 = (divs2 / succ2) if succ2 else 0.0
    eff_gain2 = naive / avg_divs2 if avg_divs2>0 else 0.0
    print(f"Efficiency @ eps={eps_eff:.2f}: {eff_gain2:.1f}x faster (avg divisions {avg_divs2:.1f})")

if __name__ == "__main__":
    main()
