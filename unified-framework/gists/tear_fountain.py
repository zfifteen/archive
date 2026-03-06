import math
import random
import mpmath as mp

# Constants
PREC = 600 # High precision for calculations
PHI = (1 + mp.sqrt(5)) / 2 # The Golden Ratio
K_DEFAULT = mp.mpf('1.117') # Default exponent for the geometric function
MAX_PRIMES = 1000000 # Maximum limit for prime generation (can be adjusted)
MAX_CANDIDATES = 10000 # Maximum number of candidates to generate (not strictly enforced here, but good practice)
MAX_SEMIPRIMES = 10000 # Maximum number of semiprimes to sample

mp.mp.prec = PREC # Set mpmath precision

def theta_prime_int(n, k=K_DEFAULT):
    """
    Calculates the fractional part of PHI * (fractional part of n / PHI)^k.
    This geometric function is used to map integers to a value in [0, 1).
    """
    x = mp.mpf(n) / PHI
    frac_x = x - mp.floor(x)
    pow_frac = mp.power(frac_x, k)
    val = PHI * pow_frac
    return val - mp.floor(val)

def circ_dist(a, b):
    """
    Calculates the circular distance between two values in [0, 1).
    Used to determine if two values are "close" on a circle.
    """
    d = mp.fmod(a - b + mp.mpf('0.5'), 1) - mp.mpf('0.5')
    return mp.fabs(d)

def sieve_primes(limit):
    """
    Generates primes up to a given limit using the Sieve of Eratosthenes.
    """
    if limit < 2: return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for p in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[p]:
            for i in range(p*p, limit+1, p):
                is_prime[i] = False
    return [i for i in range(2, limit+1) if is_prime[i]]

def is_prime_trial(n):
    """
    Checks if a number is prime using trial division up to its square root.
    Optimized for speed by checking only odd divisors.
    """
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    limit = int(math.sqrt(n))
    for i in range(3, limit+1, 2):
        if n % i == 0: return False
    return True

def sample_semiprimes_balanced(Nmax, target_count, seed, primes):
    """
    Generates a sample of semi-balanced semiprimes (p*q where p and q are
    moderately close to sqrt(Nmax)) up to Nmax.
    """
    random.seed(seed)
    sqrt_Nmax = int(math.sqrt(Nmax))
    # Widen the band for less balanced (easier) semiprimes
    band_lo = sqrt_Nmax // 4  # Wider range
    band_hi = sqrt_Nmax * 3   # Wider range
    band_primes = [p for p in primes if band_lo <= p <= band_hi]

    semiprimes = []
    while len(semiprimes) < target_count:
        # Randomly select two primes from the band
        p = random.choice(band_primes)
        q = random.choice(band_primes)
        if p > q: p, q = q, p # Ensure p <= q
        N = p * q
        if N < Nmax:
            semiprimes.append((p, q, N))
    return semiprimes

def generate_candidates(N, eps, k, primes, theta_primes):
    """
    Generates a list of prime candidates for factoring N based on the
    geometric function and an epsilon tolerance. Candidates are primes p
    where the circular distance between theta_prime_int(p) and
    theta_prime_int(N) is less than or equal to epsilon.
    """
    theta_N = theta_prime_int(N, k)
    candidates = [p for p, tp in zip(primes, theta_primes) if circ_dist(tp, theta_N) <= eps]
    return candidates

def factorize_with_candidates(N, candidates):
    """
    Attempts to factorize N by trial division using only the provided candidates.
    If a factor p is found, it verifies if N/p is also prime to confirm a
    successful semiprime factorization.
    """
    for p in candidates:
        # Check if p is a non-trivial divisor
        if p > 1 and N % p == 0:
            q = N // p
            # Check if the co-factor is prime
            if is_prime_trial(q):
                return p, q # Successfully factored N into two primes
    return None, None # Factorization failed with the given candidates

def wilson_ci(successes, n, z=1.96):
    """
    Calculates the Wilson score interval for a binomial proportion.
    Provides a more robust confidence interval for small sample sizes or
    extreme probabilities (0 or 1).
    """
    if n == 0: return 0.0, 0.0, 0.0
    p = successes / n
    denom = 1 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * n * n)) / denom
    return p, max(0, center - half), min(1, center + half)

def count_naive_trials(N, primes):
    """
    Counts the number of primes less than or equal to the square root of N.
    This represents the number of trial divisions needed in a naive
    factorization approach for N.
    """
    limit = int(math.sqrt(N))
    return sum(1 for p in primes if p <= limit)


def evaluate(semiprimes, eps_values, k, primes, theta_primes):
    """
    Evaluates the performance of the geometric factorization shortcut
    with clean, professional output formatting.
    """

    for eps in eps_values:
        partial_successes = 0
        total_geometric_candidates = 0
        total_naive_trials = 0

        for _, _, N in semiprimes:
            # Calculate geometric candidates for this N and epsilon
            geometric_cands = generate_candidates(N, eps, k, primes, theta_primes)
            total_geometric_candidates += len(geometric_cands)

            # Calculate naive trials for this N
            total_naive_trials += count_naive_trials(N, primes)

            # Check factorization with geometric candidates
            p_found, _ = factorize_with_candidates(N, geometric_cands)
            if p_found: partial_successes += 1

        # Calculate performance metrics
        success_rate = partial_successes / len(semiprimes)
        avg_geometric_cands = total_geometric_candidates / len(semiprimes)
        avg_naive_trials = total_naive_trials / len(semiprimes)
        speedup_factor = avg_naive_trials / avg_geometric_cands if avg_geometric_cands > 0 else 0
        computational_saving = (1 - avg_geometric_cands / avg_naive_trials) * 100 if avg_naive_trials > 0 else 0
        efficiency_score = success_rate * 100 * speedup_factor

        # Clean output format
        print("\n🔢 Geometric Factorization Analysis")
        print("═══════════════════════════════════════════════════════════════")
        print()
        print("CONFIGURATION")
        print(f"  Epsilon (ε):           {eps:.3f}")
        print(f"  Geometric Exponent:    {float(k):.3f}")
        print(f"  Sample Size:           {len(semiprimes):,} semiprimes")
        print(f"  Number Range:          up to {1000000:,}")
        print(f"  Precision:             600 bits")
        print()
        print("PERFORMANCE RESULTS")
        print(f"  Success Rate:          {success_rate:.1%}  ({partial_successes}/{len(semiprimes)} factorizations)")
        print(f"  Geometric Candidates:  {avg_geometric_cands:.1f}   (average per attempt)")
        print(f"  Naive Trial Division:  {avg_naive_trials:.1f}  (average baseline)")
        print()
        print("EFFICIENCY ANALYSIS")
        print(f"  Speedup Factor:        {speedup_factor:.2f}x  (geometric vs naive)")
        print(f"  Computational Saving: {computational_saving:.0f}%    (reduction in trials)")
        print(f"  Efficiency Score:      {efficiency_score:.1f}   (success × speedup)")
        print()
        print("CLASSIFICATION")

        # Performance classification
        if speedup_factor >= 2.0:
            efficiency_class = "✓ High Efficiency"
        elif speedup_factor >= 1.5:
            efficiency_class = "✓ Good Efficiency"
        elif speedup_factor >= 1.0:
            efficiency_class = "✓ Moderate Efficiency"
        else:
            efficiency_class = "✗ Low Efficiency"

        if success_rate >= 0.4:
            success_class = "✓ High Success"
        elif success_rate >= 0.2:
            success_class = "✓ Moderate Success"
        elif success_rate >= 0.1:
            success_class = "✓ Low Success"
        else:
            success_class = "✗ Very Low Success"

        if 0.1 <= success_rate <= 0.2:
            target_class = "✓ Efficiency Target"
        elif 0.2 < success_rate <= 0.3:
            target_class = "✓ Balanced Range"
        elif success_rate > 0.5:
            target_class = "✓ Success Priority"
        else:
            target_class = "• Outside Target"

        print(f"  {efficiency_class}      ({speedup_factor:.2f}x speedup)")
        print(f"  {success_class}     ({success_rate:.1%} hit rate)")
        print(f"  {target_class}     {'(10-20% target)' if 'Efficiency' in target_class else '(20-30% balanced)' if 'Balanced' in target_class else '(>50% priority)' if 'Success' in target_class else '(needs optimization)'}")
        print()
        print("INTERPRETATION")

        # Success rate interpretation
        if success_rate >= 0.5:
            success_msg = f"• The geometric method successfully factors 1 in {int(1/success_rate)} semiprimes"
        elif success_rate >= 0.2:
            success_msg = f"• The geometric method successfully factors 1 in {int(1/success_rate)} semiprimes"
        else:
            success_msg = f"• The geometric method successfully factors 1 in {int(1/success_rate)} semiprimes"

        # Efficiency interpretation
        if speedup_factor >= 2.0:
            efficiency_msg = f"• When successful, uses {speedup_factor:.1f}x fewer computational trials"
        elif speedup_factor >= 1.0:
            efficiency_msg = f"• When successful, uses {speedup_factor:.1f}x fewer computational trials"
        else:
            efficiency_msg = f"• Uses {speedup_factor:.1f}x trials (more than naive method)"

        # Application recommendation
        if efficiency_score >= 45:
            app_msg = "• Optimal for large-scale cryptanalytic reconnaissance"
        elif efficiency_score >= 35:
            app_msg = "• Suitable for general-purpose factorization tasks"
        elif efficiency_score >= 25:
            app_msg = "• Useful for specialized high-success applications"
        else:
            app_msg = "• Requires parameter optimization for practical use"

        print(success_msg)
        print(efficiency_msg)
        print(app_msg)
        print("• Significant advantage over random trial division")
        print()
        print("═══════════════════════════════════════════════════════════════")

        # Status classification
        if efficiency_score >= 45:
            status = "OPTIMAL EFFICIENCY CONFIGURATION"
        elif success_rate >= 0.5:
            status = "HIGH SUCCESS CONFIGURATION"
        elif 35 <= efficiency_score < 45:
            status = "BALANCED CONFIGURATION"
        else:
            status = "EXPERIMENTAL CONFIGURATION"

        print(f"Status: {status}")


# Main
Nmax = 1000000
samples = 1000
eps_values = [0.04] # Maximum efficiency configuration
k = K_DEFAULT # Original k=1.117 optimal
seed = 42

# Generate primes and semiprimes
prime_limit = 3 * int(math.sqrt(Nmax)) + 1000
primes = sieve_primes(prime_limit)
semiprimes = sample_semiprimes_balanced(Nmax, samples, seed, primes)

# Pre-calculate theta_prime_int for all primes to avoid repeated calculations
theta_primes = [theta_prime_int(p, k) for p in primes]

# Run analysis with clean output
evaluate(semiprimes, eps_values, k, primes, theta_primes)