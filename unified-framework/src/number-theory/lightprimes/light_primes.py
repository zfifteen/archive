import math
import collections
import random
import logging
import sympy  # For isprime verification

PHI = (1 + math.sqrt(5)) / 2
E2 = math.exp(2)
K_STAR = 0.3
DELTA_MAX = E2
V = 1.0
UNFOLD_ITERS = 4
BOOTSTRAP_SAMPLES = 100
SAMPLE_FRACTION = 0.1

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('light_primes.log'), logging.StreamHandler()])

class DiscreteZetaShift:
    vortex = collections.deque()

    def __init__(self, n, v=V, delta_max=DELTA_MAX, max_n=10**6):
        self.a = n
        mod_phi = n % PHI
        theta_prime = PHI * (mod_phi / PHI) ** K_STAR
        ln_term = math.log(n + 1) if n > 1 else 0
        self.b = theta_prime * ln_term / E2
        self.c = delta_max
        self.z = self.a * (self.b / self.c)

        self.D = self.c / self.a if self.a != 0 else 0
        self.E = self.c / self.b if self.b != 0 else 0
        self.F = PHI * ((self.D / self.E % PHI) / PHI) ** K_STAR if self.E != 0 else 0
        self.G = (self.E / self.F) / E2 if self.F != 0 else 0
        self.H = self.F / self.G if self.G != 0 else 0
        self.I = PHI * ((self.G / self.H % PHI) / PHI) ** K_STAR if self.H != 0 else 0
        self.J = self.H / self.I if self.I != 0 else 0
        self.K = (self.I / self.J) / E2 if self.J != 0 else 0
        self.L = self.J / self.K if self.K != 0 else 0
        self.M = PHI * ((self.K / self.L % PHI) / PHI) ** K_STAR if self.L != 0 else 0
        self.N = self.L / self.M if self.M != 0 else 0
        self.O = self.M / self.N if self.N != 0 else 0

        log_log_max = math.log(math.log(max_n + 1) + 1) if max_n >= 100 else 0
        self.f = 3 if max_n < 100 else round(self.G) + log_log_max
        DiscreteZetaShift.vortex.append(self)
        while len(DiscreteZetaShift.vortex) > self.f:
            DiscreteZetaShift.vortex.popleft()

    def get_chain(self):
        return [self.D, self.E, self.F, self.G, self.H, self.I, self.J, self.K, self.L, self.M, self.N, self.O]

    def unfold_next(self):
        successor = DiscreteZetaShift(self.a + 1, v=self.b, delta_max=self.c, max_n=self.a + 1)
        DiscreteZetaShift.vortex.append(successor)
        while len(DiscreteZetaShift.vortex) > successor.f:
            DiscreteZetaShift.vortex.popleft()
        return successor

    def get_helical_coords(self):
        theta_d = PHI * ((self.D % PHI) / PHI) ** K_STAR
        theta_e = PHI * ((self.E % PHI) / PHI) ** K_STAR
        x = self.a * math.cos(theta_d)
        y = self.a * math.sin(theta_e)
        z = self.F / E2
        return x, y, z

def compute_proxy_curvature(n, max_n):
    unfold_iters = 3 if max_n < 1000 else UNFOLD_ITERS
    zeta = DiscreteZetaShift(n, max_n=max_n)
    o_values = [zeta.O]
    for _ in range(unfold_iters - 1):
        zeta = zeta.unfold_next()
        o_values.append(zeta.O)
    logs = [math.log(o + 1e-10) for o in o_values if o > 0]
    if not logs:
        return 0.0
    avg = sum(logs) / len(logs)
    variance = sum((log - avg) ** 2 for log in logs) / len(logs)
    return math.sqrt(variance)

def generate_candidates(start=2, end=10000):
    numbers = range(start, end + 1)
    curvatures = [compute_proxy_curvature(n, max_n=end) for n in numbers]
    target_elim = 0.5  # Conservative to ensure high recall
    quantiles = []
    for _ in range(BOOTSTRAP_SAMPLES):
        sample = random.choices(curvatures, k=len(curvatures))
        sorted_sample = sorted(sample)
        quantiles.append(sorted_sample[int(len(sorted_sample) * (1 - target_elim))])
    threshold = sum(quantiles) / len(quantiles)
    candidates = [n for n, curv in zip(numbers, curvatures) if curv <= threshold]
    return candidates

def refine_candidates(candidates, N):
    sample_size = max(10, int(N * SAMPLE_FRACTION))
    sample_ns = random.choices(range(2, N+1), k=sample_size)
    sample_z = [DiscreteZetaShift(i, max_n=N).get_helical_coords()[2] for i in sample_ns]
    median_z = sorted(sample_z)[sample_size // 2]
    z_threshold = median_z * 1.5  # Broadened to ensure no prime rejection
    refined = []
    for c in candidates:
        zeta = DiscreteZetaShift(c, max_n=N)
        _, _, z = zeta.get_helical_coords()
        if z < z_threshold:  # Invert for inclusion (low z retained)
            refined.append(c)
    return refined

def light_primes_in_range(start=2, end=10000):
    candidates = generate_candidates(start, end)
    return sorted(refine_candidates(candidates, end))

def test_filter_recall_precision(start=2, end=10000):
    generated = light_primes_in_range(start, end)
    true_primes = [n for n in range(start, end + 1) if sympy.isprime(n)]
    tp = [p for p in true_primes if p in generated]
    recall = len(tp) / len(true_primes) if true_primes else 0
    precision = len(tp) / len(generated) if generated else 0
    f1 = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0
    print(f"Generated: {len(generated)}, True primes: {len(true_primes)}, TP: {len(tp)}")
    print(f"Recall: {recall:.4f} (must be 1.0000), Precision: {precision:.4f}, F1: {f1:.4f}")
    if recall < 1:
        missing = set(true_primes) - set(generated)
        print(f"Missed primes: {sorted(missing)}")
    return recall == 1

if __name__ == "__main__":
    test_filter_recall_precision()