import hashlib
import mpmath
import random
import statistics
from scipy.stats import ttest_ind

mpmath.mp.dps = 50
phi = (1 + mpmath.sqrt(5)) / 2
k_star = mpmath.mpf('0.04449')
width_factor = 0.5

def bound_width(n):
    n_mod_phi = mpmath.fmod(mpmath.mpf(n), phi)
    return float(phi * ((n_mod_phi / phi) ** k_star) * width_factor)

def mine_trial(strategy='brute', difficulty=2, max_attempts=10000):
    target = '0' * difficulty
    base = b"Sim block " + str(random.randint(0, 1000000)).encode()
    nonce = 0
    attempts = 0
    skipped = 0
    while attempts < max_attempts:
        if strategy == 'z5d_filter' and bound_width(nonce) > 0.7:
            nonce += 1
            skipped += 1
            continue
        hash_val = hashlib.sha256(base + str(nonce).encode()).hexdigest()
        attempts += 1
        if hash_val.startswith(target):
            return attempts, skipped
        nonce += 1
    return max_attempts, skipped

brute = [mine_trial('brute') for _ in range(20)]
z5d = [mine_trial('z5d_filter') for _ in range(20)]

brute_attempts = [x[0] for x in brute]
z5d_attempts = [x[0] for x in z5d]
z5d_skipped = [x[1] for x in z5d]

print(f"Brute avg attempts: {statistics.mean(brute_attempts):.0f}, std: {statistics.stdev(brute_attempts):.0f}")
print(f"Z5D-filtered avg: {statistics.mean(z5d_attempts):.0f}, std: {statistics.stdev(z5d_attempts):.0f}")
print(f"Z5D avg skipped per trial: {statistics.mean(z5d_skipped):.0f} (out of ~10000 max nonce checks)")

t_stat, p_val = ttest_ind(brute_attempts, z5d_attempts)
print(f"T-test: t-stat={t_stat:.3f}, p-value={p_val:.3f} (p<0.05 means significant difference)")