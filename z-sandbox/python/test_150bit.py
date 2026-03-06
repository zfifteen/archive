import sympy as sp
import math
import random
import mpmath as mp

mp.mp.dps = 50  # High precision

def generate_150bit_semiprime(seed=None):
    """Generate a balanced 150-bit semiprime."""
    if seed:
        random.seed(seed)

    # Generate two ~75-bit primes using nextprime for better distribution
    base = 2**74  # Each prime ~75 bits, product ~150 bits
    offset = random.randint(0, 10**6)  # Large offset range
    p = sp.nextprime(base + offset)
    q = sp.nextprime(base + offset + random.randint(1, 10**5))  # More spread
    N = int(p) * int(q)

    return N, int(p), int(q)

print("Testing generate_150bit_semiprime...")
N, p, q = generate_150bit_semiprime(12345)
print(f"N: {N}, bits: {N.bit_length()}")
print(f"p: {p}, q: {q}")

def embed(n, dims=11, k=None):
    """Embed number into d-dimensional torus using golden ratio modulation with residues."""
    phi = mp.mpf((1 + mp.sqrt(5)) / 2)
    c = mp.exp(2)
    if k is None:
        k = mp.mpf('0.3') / mp.log(mp.log(float(n) + 1), 2)  # use float for log
    x = mp.mpf(n) / c
    coords = []
    # Geometric dims
    for _ in range(dims):
        x = phi * mp.power(mp.frac(x / phi), k)
        coords.append(mp.frac(x))
    # Residue dims
    coords.append(mp.mpf(n % 1000000) / 1000000)
    coords.append(mp.mpf(n % 1000000000) / 1000000000)
    return coords

def riemann_dist(c1, c2, N):
    """Calculate Riemannian distance with curvature correction."""
    kappa = 4 * mp.log(N + 1) / mp.exp(2)
    deltas = [mp.mpf(min(abs(a - b), 1 - abs(a - b))) for a, b in zip(c1, c2)]
    dist_sq = sum((delta * (1 + kappa * delta))**2 for delta in deltas)
    return mp.sqrt(dist_sq)

print("Testing embed and dist...")
theta_N = embed(N)
print(f"theta_N length: {len(theta_N)}, first 5: {[float(t) for t in theta_N[:5]]}...")

sqrtN = int(math.sqrt(N))
R = 10000  # Smaller range for test
candidates = list(range(max(2, sqrtN - R), sqrtN + R + 1))
print(f"candidates around sqrtN: {sqrtN}, range: {len(candidates)}")

print("Sorting...")
ranked = sorted(candidates, key=lambda c: riemann_dist(embed(c), theta_N, N))
print(f"Top 5 ranked: {ranked[:5]}")

# Check if p or q is in top 50
top50 = ranked[:50]
if p in top50 or q in top50:
    print("SUCCESS: Factor in top 50")
else:
    print("FAIL: Factor not in top 50")