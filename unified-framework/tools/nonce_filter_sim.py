import hashlib
import mpmath
import random
import statistics

mpmath.mp.dps = 50
phi = (1 + mpmath.sqrt(5)) / 2
k_star = mpmath.mpf('0.04449')
width_factor = 0.5

def bound_width(n, k=k_star):
    n_mod_phi = mpmath.fmod(mpmath.mpf(n), phi)
    return float(phi * ((n_mod_phi / phi) ** k) * width_factor)

def mine_trial(strategy='brute', difficulty=6, max_attempts=10**7):
    target = '0' * difficulty
    random.seed(42)  # Fixed seed for determinism
    base = b"Z block " + str(random.randint(0, 10**6)).encode()
    nonce = 0
    attempts = 0
    skipped = 0
    k_passes = [0.2, 0.45, 0.8] if strategy == 'z5d' else [k_star]
    for k in k_passes:
        while attempts < max_attempts:
            w = bound_width(nonce, k)
            if strategy == 'z5d' and w > 0.65:  # Skip loose bounds
                nonce += 1
                skipped += 1
                continue
            hash_val = hashlib.sha256(base + str(nonce).encode()).hexdigest()
            attempts += 1
            if hash_val.startswith(target):
                return attempts, skipped
            nonce += 1
    return max_attempts, skipped

# Run 50 trials for stats
brute_results = [mine_trial('brute') for _ in range(50)]
z5d_results = [mine_trial('z5d') for _ in range(50)]

brute_attempts = [r[0] for r in brute_results]
z5d_attempts = [r[0] for r in z5d_results]
skips = [r[1] for r in z5d_results]

print(f"Brute avg attempts: {statistics.mean(brute_attempts):.0f}, std: {statistics.stdev(brute_attempts):.0f}")
print(f"Z5D avg attempts: {statistics.mean(z5d_attempts):.0f}, std: {statistics.stdev(z5d_attempts):.0f}")
print(f"Z5D avg skip %: {statistics.mean([s/(a+s)*100 for a,s in zip(z5d_attempts, skips)]):.1f}%")