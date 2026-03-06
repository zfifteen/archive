#!/usr/bin/env python3
import math, random, statistics
from math import gcd

# --- 64-bit Miller–Rabin ---

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    small = [2,3,5,7,11,13,17,19,23,29]
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in [2,325,9375,28178,450775,9780504,1795265022]:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# --- Pollard rho factorization (64-bit) ---

def pollard_rho(n: int) -> int:
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    while True:
        x = random.randrange(2, n - 1)
        c = random.randrange(1, n - 1)
        y = x
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = gcd(abs(x - y), n)
            if d == n:
                break
        if 1 < d < n:
            return d

def factor(n: int, res: dict):
    if n == 1:
        return
    if is_prime(n):
        res[n] = res.get(n, 0) + 1
    else:
        d = pollard_rho(n)
        factor(d, res)
        factor(n // d, res)

# --- Z(n) = n * Δ_n with Δ_n = τ(n) * log n (Δ_max factor cancels in rankings) ---

Z_cache = {}
tau_known = {}

def Z(n: int) -> float:
    z = Z_cache.get(n)
    if z is not None:
        return z
    t = tau_known.get(n)
    if t is None:
        f = {}
        factor(n, f)
        t = 1
        for e in f.values():
            t *= (e + 1)
    val = n * t * math.log(n)
    Z_cache[n] = val
    return val

# --- random primes and semiprimes in 10^14–10^18 ---

def random_prime(lo: int, hi: int) -> int:
    while True:
        n = random.randrange(lo | 1, hi + 1, 2)
        if is_prime(n):
            return n

def build_semiprimes(N_min: int, N_max: int, count: int):
    semis = {}
    while len(semis) < count:
        p = random_prime(10**7, 10**9)
        q = random_prime(10**7, 10**9)
        if p == q:
            continue
        N = p * q
        if N < N_min or N > N_max:
            continue
        semis[N] = (p, q)
    return semis

# --- experiment: KK–Z resonance at 10^14–10^18 ---

def run_experiment():
    random.seed(0)

    N_min = 10**14
    N_max = 10**18
    TARGET_COUNT = 40
    NUM_RANDOM = 200

    semis = build_semiprimes(N_min, N_max, TARGET_COUNT)

    for N, (p, q) in semis.items():
        tau_known[N] = 4      # distinct primes
        tau_known[p] = 2
        tau_known[q] = 2

    ranks = []
    true_diffs = []
    rand_diffs = []
    S = NUM_RANDOM + 1

    for N, (p, q) in semis.items():
        root = int(math.isqrt(N))
        lo = max(2, root - root // 4)
        hi = root + root // 4

        ZN = Z(N)
        Zp = Z(p)
        Zq = Z(q)

        diff_true = abs(Zp + Zq - ZN)
        true_diffs.append(diff_true)
        diffs = [diff_true]

        for _ in range(NUM_RANDOM):
            a = random.randint(lo, hi)
            b = random.randint(lo, hi)
            diff_rand = abs(Z(a) + Z(b) - ZN)
            diffs.append(diff_rand)
            rand_diffs.append(diff_rand)

        rank = sorted(diffs).index(diff_true) + 1
        ranks.append(rank)

    mean_rank = statistics.mean(ranks)
    expected_rank = (S + 1) / 2.0
    frac_best = sum(r == 1 for r in ranks) / len(ranks)
    top_bound = max(1, int(0.1 * S))
    frac_top10 = sum(r <= top_bound for r in ranks) / len(ranks)

    mean_true = statistics.mean(true_diffs)
    mean_rand = statistics.mean(rand_diffs)
    st_true = statistics.pstdev(true_diffs)
    st_rand = statistics.pstdev(rand_diffs)
    pooled = math.sqrt((st_true**2 + st_rand**2) / 2.0) if (st_true > 0 or st_rand > 0) else float("nan")
    effect = (mean_rand - mean_true) / pooled if pooled > 0 else float("nan")

    print("\n--- KK–Z resonance test for semiprimes ---")
    print(f"Semiprimes tested: {len(ranks)} in [{N_min}, {N_max}]")
    print(f"Random pairs per N: {NUM_RANDOM}")
    print(f"Average rank of true pair (1=best, {S}=worst): {mean_rank:.2f} (null ≈ {expected_rank:.2f})")
    print(f"Fraction with true pair rank = 1: {frac_best:.3f}")
    print(f"Fraction with true pair in top 10% of ranks: {frac_top10:.3f}")
    print(f"Mean |Z(p)+Z(q)-Z(N)| (true): {mean_true:.6g}")
    print(f"Mean |Z(a)+Z(b)-Z(N)| (random): {mean_rand:.6g}")
    print(f"Effect size (Cohen d, random - true): {effect:.3f}")

if __name__ == "__main__":
    run_experiment()
