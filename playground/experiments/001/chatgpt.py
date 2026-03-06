#!/usr/bin/env python3
import math, random, statistics

# --- Z(n) = n * (Δ_n / Δ_max), with Δ_n from divisor-based curvature ---

def divisor_counts(max_n: int):
    tau = [0] * (max_n + 1)
    for d in range(1, max_n + 1):
        for m in range(d, max_n + 1, d):
            tau[m] += 1
    return tau

def build_Z(max_n: int):
    tau = divisor_counts(max_n)
    delta = [0.0] * (max_n + 1)
    for n in range(2, max_n + 1):
        delta[n] = tau[n] * math.log(n)
    delta_max = max(delta)
    Z = [0.0] * (max_n + 1)
    if delta_max == 0.0:
        return Z
    for n in range(1, max_n + 1):
        Z[n] = n * (delta[n] / delta_max)
    return Z

# --- primes and semiprimes in [N_min, N_max] ---

def sieve_primes(limit: int):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for p in range(2, int(limit ** 0.5) + 1):
        if sieve[p]:
            for m in range(p * p, limit + 1, p):
                sieve[m] = False
    return [i for i, is_p in enumerate(sieve) if is_p]

def semiprimes_in_range(N_min: int, N_max: int, primes):
    semis = {}
    for i, p in enumerate(primes):
        if p * p > N_max:
            break
        for q in primes[i:]:
            N = p * q
            if N > N_max:
                break
            if N >= N_min:
                semis[N] = (p, q)
    return semis

# --- experiment: KK-style Z-resonance for true factors vs random pairs ---

def run_experiment():
    N_min = 10**5
    N_max = 2 * 10**5
    max_Z = N_max

    print(f"Building Z(n) up to {max_Z} ...")
    Z = build_Z(max_Z)

    print(f"Generating primes up to {N_max // 2} ...")
    primes = sieve_primes(N_max // 2)

    print(f"Collecting semiprimes in [{N_min}, {N_max}] ...")
    semis = semiprimes_in_range(N_min, N_max, primes)
    items = sorted(semis.items())
    if len(items) > 200:
        items = items[:200]  # cap for speed

    NUM_RANDOM = 200
    S = NUM_RANDOM + 1
    random.seed(0)

    ranks = []
    true_diffs = []
    rand_diffs = []

    for N, (p, q) in items:
        ZN = Z[N]
        Zp = Z[p]
        Zq = Z[q]
        diff_true = abs(Zp + Zq - ZN)
        true_diffs.append(diff_true)
        diffs = [diff_true]

        root = int(math.isqrt(N))
        lo = max(2, root // 2)
        hi = min(max_Z, root * 2)

        for _ in range(NUM_RANDOM):
            a = random.randint(lo, hi)
            b = random.randint(lo, hi)
            diff_rand = abs(Z[a] + Z[b] - ZN)
            diffs.append(diff_rand)
            rand_diffs.append(diff_rand)

        rank = sorted(diffs).index(diff_true) + 1  # 1 = best (smallest)
        ranks.append(rank)

    mean_rank = statistics.mean(ranks)
    expected_rank = (S + 1) / 2.0
    fraction_best = sum(r == 1 for r in ranks) / len(ranks)
    top_bound = max(1, int(0.1 * S))
    fraction_top10 = sum(r <= top_bound for r in ranks) / len(ranks)

    mean_true = statistics.mean(true_diffs)
    mean_rand = statistics.mean(rand_diffs)
    stdev_true = statistics.pstdev(true_diffs)
    stdev_rand = statistics.pstdev(rand_diffs)
    pooled_sd = math.sqrt((stdev_true ** 2 + stdev_rand ** 2) / 2.0) if (stdev_true > 0 or stdev_rand > 0) else float("nan")
    effect = (mean_rand - mean_true) / pooled_sd if pooled_sd > 0 else float("nan")

    print("\n--- KK–Z resonance test for semiprimes ---")
    print(f"Semiprimes tested: {len(ranks)} in [{N_min}, {N_max}]")
    print(f"Random pairs per N: {NUM_RANDOM}")
    print(f"Average rank of true factor pair (1=best, {S}=worst): {mean_rank:.2f} (null ≈ {expected_rank:.2f})")
    print(f"Fraction with true pair rank = 1: {fraction_best:.3f}")
    print(f"Fraction with true pair in top 10% of ranks: {fraction_top10:.3f}")
    print(f"Mean |Z(p)+Z(q)-Z(N)| (true): {mean_true:.6g}")
    print(f"Mean |Z(a)+Z(b)-Z(N)| (random): {mean_rand:.6g}")
    print(f"Effect size (Cohen d, random - true): {effect:.3f}")

if __name__ == "__main__":
    run_experiment()
