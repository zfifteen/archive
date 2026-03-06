#!/usr/bin/env python3
"""
Self-Contained Hypothesis Validator: Z-Geodesic Enhanced Miller-Rabin
Authored by Dionisio Alberto Lopez III (D.A.L. III), Z Framework

Hypothesis: Integrating Z-geodesic witness selection yields ~44% speedup with 100% accuracy vs. standard MR.
Run: python validate_hypothesis.py
Output: mr_results.csv + summary (proves if speedup>40% & acc==100%).

Key: Hardcoded zeta seeds; balanced corpus ~10^{12}; scalable for larger n.
"""

import csv
import time
import random
import math
import mpmath as mp
from sympy.ntheory import isprime as prob_isprime  # Probabilistic, 40 rounds
from typing import Sequence, Tuple

# Precision & Constants
mp.mp.dps = 100
PHI = (1 + mp.sqrt(5)) / 2
KAPPA_STAR_DEFAULT = 0.04449
KAPPA_STAR_DEFAULT_MP = mp.mpf(str(KAPPA_STAR_DEFAULT))
_RNG = random.Random(42)
PHI_f = float(PHI)
KAPPA_STAR_f = float(KAPPA_STAR_DEFAULT)
FLOAT64_PRECISION_THRESHOLD = 1 << 60

# Hardcoded zeta seeds (first 10 from zeta_1M.txt)
zeta_seeds_float = [
    14.1347251417346937904572519835625, 21.0220396387715549926284795938969,
    25.0108575801456887632137909925628, 30.4248761258595132103118975305840,
    32.9350615877391896906623689640747, 37.5861781588256712572177634807053,
    40.9187190121474951873981269146334, 43.3270732809149995194961221654068,
    48.0051508811671597279424727494277, 49.7738324776723021819167846785638,
]

def geodesic_mr(n: int, rounds: int, zeros: list, policy: str, early_standard_check: bool = True) -> Tuple[bool, int]:
    """Z-geodesic enhanced MR."""
    if n < 2: return (False, 0)
    if n in (2, 3): return (False, 0)
    if n % 2 == 0: return (True, 1)
    if n % 3 == 0 or n % 5 == 0 or n % 7 == 0 or n % 11 == 0: return (True, 1)

    if early_standard_check and rounds > 1:
        quick_a = _RNG.randrange(2, n - 1)
        d, s = n - 1, 0
        while (d & 1) == 0: d >>= 1; s += 1
        x = pow(quick_a, d, n)
        if x != 1 and x != n - 1:
            composite = True
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1: composite = False; break
            if composite: return (True, 1)

    d, s = n - 1, 0
    while (d & 1) == 0: d >>= 1; s += 1
    n_mp = None

    def _z_base(r_idx: int) -> int:
        nonlocal n_mp
        z_idx = r_idx % len(zeros)
        if n <= FLOAT64_PRECISION_THRESHOLD:
            z_f, n_f = zeros[z_idx], float(n)
            n_mod_phi = math.fmod(n_f * z_f, PHI_f)
            t = n_mod_phi / PHI_f
            u = t ** KAPPA_STAR_f
            a = 2 + int(u * (n - 3))
        else:
            if n_mp is None: n_mp = mp.mpf(n)
            z = mp.mpf(zeros[z_idx])
            n_mod_phi = mp.fmod(n_mp * z, PHI)
            t = n_mod_phi / PHI
            u = mp.power(t, KAPPA_STAR_DEFAULT_MP)
            a = 2 + int(u * (n - 3))
        a = max(2, min(a, n - 2))
        return a

    def _rand_base() -> int: return _RNG.randrange(2, n - 1)

    r_rand = {"hybrid-1R": 1, "hybrid-2R": 2}.get(policy, 0)
    rand_slots = {0} if r_rand >= 1 else set()
    if r_rand >= 2 and rounds > 1: rand_slots.add(rounds - 1)

    for r_idx in range(rounds):
        a = _rand_base() if r_idx in rand_slots else _z_base(r_idx)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        composite = True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: composite = False; break
        if composite: return (True, r_idx + 1)
    return (False, rounds)

def miller_rabin_standard(n, rounds=5):
    """Standard MR."""
    if n == 2 or n == 3: return True, 0
    if n % 2 == 0 or n < 2: return False, 1
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for round_num in range(1, rounds + 1):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False, round_num
    return True, rounds

def process_number(n, zeta_seeds):
    is_composite = not prob_isprime(n, tolerance=40)  # For large n
    t0 = time.perf_counter_ns()
    std_result, std_rounds = miller_rabin_standard(n, rounds=5)
    t1 = time.perf_counter_ns()
    u0 = time.perf_counter_ns()
    detected_enh, rounds_enh = geodesic_mr(n, 5, zeta_seeds, policy="hybrid-2R", early_standard_check=True)
    u1 = time.perf_counter_ns()
    time_ms_standard = (t1 - t0) / 1e6
    time_ms_enhanced = (u1 - u0) / 1e6
    time_ms = time_ms_standard + time_ms_enhanced
    enh_result = not detected_enh
    detected = is_composite and (not std_result) and (not enh_result)
    return [n, is_composite, std_rounds, rounds_enh, detected, f"{time_ms:.3f}", f"{time_ms_standard:.3f}", f"{time_ms_enhanced:.3f}", bool(std_result), bool(enh_result)]

def main(corpus_size=200, start=10**12, range_size=10**6):
    random.seed(42)
    zeta_seeds = zeta_seeds_float

    # Generate balanced corpus
    corpus_rng = random.Random(42)
    random_nums = sorted(corpus_rng.sample(range(start, start + range_size), corpus_size // 2))
    primes = list(primerange(start, start + 10**4))[:corpus_size // 4]
    composites = []
    for p in primes[:corpus_size // 4]:
        for q in [3, 5, 7]:
            comp = p * q
            if start <= comp < start + range_size: composites.append(comp)
    composites = composites[:corpus_size // 4]
    test_numbers = random_nums + primes + composites
    test_numbers = list(set(test_numbers))[:corpus_size]
    random.shuffle(test_numbers)
    print(f"Testing {len(test_numbers)} numbers around {start}")

    results = []
    for i, n in enumerate(test_numbers):
        row = process_number(n, zeta_seeds)
        results.append(row)
        if i % 50 == 0:
            print(f"Processed {i+1}/{len(test_numbers)}: n={n}, std={row[8]}, enh={row[9]}, std_time={row[6]}ms, enh_time={row[7]}ms")

    # Stats
    std_times = [float(r[6]) for r in results if float(r[6]) > 0]
    enh_times = [float(r[7]) for r in results if float(r[7]) > 0]
    speedups = [(s - e) / s * 100 for s, e in zip(std_times, enh_times) if s > 0]
    avg_speedup = sum(speedups) / len(speedups) if speedups else 0
    acc_std = sum(1 for r in results if (r[1] and not r[8]) or (not r[1] and r[8]))
    acc_enh = sum(1 for r in results if (r[1] and not r[9]) or (not r[1] and r[9]))
    print(f"Avg speedup: {avg_speedup:.2f}%")
    print(f"Std acc: {acc_std / len(results) * 100:.2f}%")
    print(f"Enh acc: {acc_enh / len(results) * 100:.2f}%")

    # CSV
    with open('mr_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["n", "is_composite", "rounds_standard", "rounds_enhanced", "detected", "time_ms", "time_ms_standard", "time_ms_enhanced", "std_result", "enh_result"])
        writer.writerows(results)

    hypothesis_proven = avg_speedup > 40 and acc_std == len(results) and acc_enh == len(results)
    print(f"Hypothesis proven: {hypothesis_proven} (Speedup >40%, Acc 100% for both)")
    if not hypothesis_proven:
        print("Note: For larger n (~10^15, N=1000), rerun with start=10**15 (slower due to isprime).")

if __name__ == "__main__":
    main(corpus_size=100, start=10**15, range_size=10**7)
