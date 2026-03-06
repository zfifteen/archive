#!/usr/bin/env python3
"""
Kaluza-Klein Semi-Prime Factorization Hypothesis Test
Tests the relationship between KK effective radii for semi-primes N = p × q

Hypotheses tested:
1. Reciprocal additivity: 1/R_eff(N) ≈ 1/R_eff(p) + 1/R_eff(q)
2. Curvature conservation: κ(N) ≈ f(κ(p), κ(q))
3. Domain shift composition: Δ_N ≈ g(Δ_p, Δ_q)
4. Geometric product: θ'(N) ≈ product(θ'(p), θ'(q))
5. Resonance score as factorization filter
"""

import numpy as np
from math import log, sqrt, exp, floor
import random

# ============================================================================
# CORE MATHEMATICAL FUNCTIONS (from axioms.py)
# ============================================================================

PHI = (1 + sqrt(5)) / 2  # Golden ratio
E_SQUARED = exp(2)

def divisor_count(n):
    """Count number of divisors of n"""
    if n <= 0:
        return 0
    count = 0
    for i in range(1, int(sqrt(n)) + 1):
        if n % i == 0:
            count += 2 if i * i != n else 1
    return count

def curvature(n, d_n=None):
    """κ(n) = d(n) · ln(n+1) / e²"""
    if d_n is None:
        d_n = divisor_count(n)
    return d_n * log(n + 1) / E_SQUARED

def theta_prime(n, k, phi=PHI):
    """
    Geodesic transformation: θ'(n,k) = φ · {n/φ}^k
    Where {x} is the fractional part of x
    """
    # High-precision fractional part
    n_mod_phi = n % phi
    normalized_residue = n_mod_phi / phi

    # Bounds checking
    if normalized_residue < 0:
        normalized_residue = 0
    elif normalized_residue >= 1:
        normalized_residue = 1 - 1e-15

    # Apply power transformation
    if k == 0:
        power_term = 1
    elif normalized_residue == 0:
        power_term = 0
    else:
        power_term = normalized_residue ** k

    result = phi * power_term

    # Ensure bounds
    if result < 0:
        result = 0
    elif result >= phi:
        result = phi - 1e-15

    return result

def compute_fractional_part(value):
    """Extract fractional part: value - floor(value)"""
    return value - floor(value)

def compute_Z_value(n, d_n=None):
    """
    Compute Z = n(Δ_n/Δ_max) where:
    Δ_n = v · κ(n) · (1 + m_n · R)
    For simplicity, using Δ_n ≈ κ(n) as approximation
    """
    if d_n is None:
        d_n = divisor_count(n)

    kappa_n = curvature(n, d_n)
    delta_n = kappa_n  # Simplified: v=1, m_n·R term small

    # Maximum domain shift
    delta_max = E_SQUARED * PHI

    Z = n * (delta_n / delta_max)
    return Z

def compute_R_eff(n, d_n=None):
    """Effective compactification radius: R_eff(n) ~ 1/Z(n)"""
    Z = compute_Z_value(n, d_n)
    if Z == 0:
        return float('inf')
    return 1.0 / Z

# ============================================================================
# PRIME GENERATION
# ============================================================================

def sieve_of_eratosthenes(limit):
    """Generate all primes up to limit"""
    if limit < 2:
        return []

    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False

    for i in range(2, int(sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False

    return [i for i in range(2, limit + 1) if sieve[i]]

# ============================================================================
# SEMI-PRIME GENERATION
# ============================================================================

def generate_semiprimes_in_range(target_min, target_max, count=100):
    """Generate semi-primes N = p × q in the target range"""
    # Generate primes up to sqrt(target_max) to ensure p*q is in range
    prime_limit = int(sqrt(target_max)) + 1000
    primes = sieve_of_eratosthenes(prime_limit)

    semiprimes = []
    attempts = 0
    max_attempts = count * 100

    while len(semiprimes) < count and attempts < max_attempts:
        attempts += 1

        # Pick two random primes
        p = random.choice(primes)
        q = random.choice(primes)

        N = p * q

        # Check if in range and not duplicate
        if target_min <= N <= target_max:
            if (p, q, N) not in semiprimes and (q, p, N) not in semiprimes:
                semiprimes.append((p, q, N))

    return semiprimes

# ============================================================================
# HYPOTHESIS TESTING FUNCTIONS
# ============================================================================

def check_reciprocal_additivity(p, q, N):
    """
    Test: 1/R_eff(N) ≈ 1/R_eff(p) + 1/R_eff(q)
    Returns: relative error
    """
    R_p = compute_R_eff(p, d_n=2)
    R_q = compute_R_eff(q, d_n=2)
    R_N = compute_R_eff(N, d_n=4)

    predicted = 1/R_p + 1/R_q
    actual = 1/R_N

    if actual == 0:
        return float('inf')

    relative_error = abs(predicted - actual) / actual
    return relative_error

def check_curvature_conservation(p, q, N):
    """
    Test various curvature relationships
    Returns: dict of relative errors for different hypotheses
    """
    κ_p = curvature(p, d_n=2)
    κ_q = curvature(q, d_n=2)
    κ_N = curvature(N, d_n=4)

    results = {}

    # Hypothesis 1: κ(N) ≈ κ(p) + κ(q)
    predicted_sum = κ_p + κ_q
    results['sum'] = abs(predicted_sum - κ_N) / κ_N if κ_N != 0 else float('inf')

    # Hypothesis 2: κ(N) ≈ 2(κ(p) + κ(q)) (factor of 2 from d(N)=4 vs d(p)=d(q)=2)
    predicted_2sum = 2 * (κ_p + κ_q)
    results['2sum'] = abs(predicted_2sum - κ_N) / κ_N if κ_N != 0 else float('inf')

    # Hypothesis 3: κ(N) ≈ geometric mean
    predicted_geom = sqrt(κ_p * κ_q)
    results['geom_mean'] = abs(predicted_geom - κ_N) / κ_N if κ_N != 0 else float('inf')

    # Hypothesis 4: κ(N) ≈ harmonic mean * 2
    predicted_harm = 2 / (1/κ_p + 1/κ_q)
    results['harm_mean'] = abs(predicted_harm - κ_N) / κ_N if κ_N != 0 else float('inf')

    return results

def check_theta_geometric_product(p, q, N, k=0.3):
    """
    Test geometric relationships between θ'(p), θ'(q), θ'(N)
    Returns: dict of relative errors for different operations
    """
    θ_p = theta_prime(p, k)
    θ_q = theta_prime(q, k)
    θ_N = theta_prime(N, k)

    results = {}

    # Hypothesis 1: θ'(N) ≈ θ'(p) · θ'(q) / φ (normalized product)
    predicted_prod = (θ_p * θ_q) / PHI
    results['normalized_product'] = abs(predicted_prod - θ_N) / θ_N if θ_N != 0 else float('inf')

    # Hypothesis 2: θ'(N) ≈ θ'(p) + θ'(q) (additive)
    predicted_sum = θ_p + θ_q
    results['sum'] = abs(predicted_sum - θ_N) / θ_N if θ_N != 0 else float('inf')

    # Hypothesis 3: θ'(N) ≈ sqrt(θ'(p) · θ'(q)) (geometric mean)
    predicted_geom = sqrt(θ_p * θ_q)
    results['geom_mean'] = abs(predicted_geom - θ_N) / θ_N if θ_N != 0 else float('inf')

    # Hypothesis 4: Modular composition θ'(N) ≈ {θ'(p) * θ'(q)}
    predicted_mod = (θ_p * θ_q) % PHI
    results['modular_product'] = abs(predicted_mod - θ_N) / θ_N if θ_N != 0 else float('inf')

    return results

def compute_resonance_score(p, q, N):
    """
    Composite resonance score combining multiple geometric features
    Lower score = better resonance
    """
    # R_eff reciprocal error
    reciprocal_error = check_reciprocal_additivity(p, q, N)

    # Best curvature error
    curvature_errors = check_curvature_conservation(p, q, N)
    best_curvature_error = min(curvature_errors.values())

    # Best theta error
    theta_errors = check_theta_geometric_product(p, q, N)
    best_theta_error = min(theta_errors.values())

    # Composite score (weighted average)
    score = 0.4 * reciprocal_error + 0.3 * best_curvature_error + 0.3 * best_theta_error

    return score

# ============================================================================
# FACTORIZATION TEST
# ============================================================================

def attempt_resonance_factorization(N, max_candidates=100):
    """
    Attempt to factor N using resonance scores
    Tests divisors and ranks by resonance score
    """
    if N < 4:
        return None

    candidates = []
    search_limit = min(int(sqrt(N)) + 1, max_candidates * 10)

    for d in range(2, search_limit):
        if N % d == 0:
            q = N // d
            score = compute_resonance_score(d, q, N)
            candidates.append((d, q, score))

    # Sort by resonance score (lower is better)
    candidates.sort(key=lambda x: x[2])

    return candidates[:max_candidates]

# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_experiment():
    """Run complete hypothesis test on semi-primes in 10^5 range"""

    print("=" * 80)
    print("KALUZA-KLEIN SEMI-PRIME FACTORIZATION HYPOTHESIS TEST")
    print("=" * 80)
    print()

    # Configuration
    TARGET_MIN = 10**5
    TARGET_MAX = 2 * 10**5
    NUM_SEMIPRIMES = 50

    print(f"Configuration:")
    print(f"  Target range: [{TARGET_MIN:,}, {TARGET_MAX:,}]")
    print(f"  Number of semi-primes: {NUM_SEMIPRIMES}")
    print(f"  Golden ratio φ: {PHI:.10f}")
    print(f"  e²: {E_SQUARED:.10f}")
    print()

    # Generate semi-primes
    print("Generating semi-primes...")
    semiprimes = generate_semiprimes_in_range(TARGET_MIN, TARGET_MAX, NUM_SEMIPRIMES)
    print(f"Generated {len(semiprimes)} semi-primes")
    print()

    # Store results
    reciprocal_errors = []
    curvature_sum_errors = []
    curvature_2sum_errors = []
    theta_product_errors = []
    resonance_scores = []

    # Test each semi-prime
    print("Testing hypotheses...")
    print("-" * 80)

    for i, (p, q, N) in enumerate(semiprimes[:10]):  # Show first 10 in detail
        print(f"\nSemi-prime #{i+1}: N = {N:,} = {p:,} × {q:,}")

        # Test 1: Reciprocal additivity
        recip_error = check_reciprocal_additivity(p, q, N)
        reciprocal_errors.append(recip_error)
        print(f"  Reciprocal additivity error: {recip_error:.6f}")

        # Test 2: Curvature conservation
        curv_errors = check_curvature_conservation(p, q, N)
        curvature_sum_errors.append(curv_errors['sum'])
        curvature_2sum_errors.append(curv_errors['2sum'])
        print(f"  Curvature sum error: {curv_errors['sum']:.6f}")
        print(f"  Curvature 2×sum error: {curv_errors['2sum']:.6f}")

        # Test 3: Theta geometric product
        theta_errors = check_theta_geometric_product(p, q, N)
        theta_product_errors.append(theta_errors['normalized_product'])
        print(f"  Theta normalized product error: {theta_errors['normalized_product']:.6f}")

        # Test 4: Resonance score
        resonance = compute_resonance_score(p, q, N)
        resonance_scores.append(resonance)
        print(f"  Composite resonance score: {resonance:.6f}")

    # Process remaining semi-primes silently
    for p, q, N in semiprimes[10:]:
        reciprocal_errors.append(check_reciprocal_additivity(p, q, N))
        curv_errors = check_curvature_conservation(p, q, N)
        curvature_sum_errors.append(curv_errors['sum'])
        curvature_2sum_errors.append(curv_errors['2sum'])
        theta_errors = check_theta_geometric_product(p, q, N)
        theta_product_errors.append(theta_errors['normalized_product'])
        resonance_scores.append(compute_resonance_score(p, q, N))

    print("\n" + "=" * 80)
    print("STATISTICAL SUMMARY")
    print("=" * 80)

    # Summary statistics
    def print_stats(name, errors):
        errors = [e for e in errors if e != float('inf')]
        if not errors:
            print(f"\n{name}: No valid data")
            return

        print(f"\n{name}:")
        print(f"  Mean error: {np.mean(errors):.6f}")
        print(f"  Median error: {np.median(errors):.6f}")
        print(f"  Std dev: {np.std(errors):.6f}")
        print(f"  Min error: {np.min(errors):.6f}")
        print(f"  Max error: {np.max(errors):.6f}")
        print(f"  % within 1% error: {100 * sum(1 for e in errors if e < 0.01) / len(errors):.1f}%")
        print(f"  % within 5% error: {100 * sum(1 for e in errors if e < 0.05) / len(errors):.1f}%")
        print(f"  % within 10% error: {100 * sum(1 for e in errors if e < 0.10) / len(errors):.1f}%")

    print_stats("Hypothesis 1: Reciprocal Additivity (1/R_N ≈ 1/R_p + 1/R_q)", reciprocal_errors)
    print_stats("Hypothesis 2a: Curvature Sum (κ(N) ≈ κ(p) + κ(q))", curvature_sum_errors)
    print_stats("Hypothesis 2b: Curvature 2×Sum (κ(N) ≈ 2(κ(p) + κ(q)))", curvature_2sum_errors)
    print_stats("Hypothesis 3: Theta Product (θ'(N) ≈ θ'(p)·θ'(q)/φ)", theta_product_errors)
    print_stats("Composite Resonance Score", resonance_scores)

    # Test factorization using resonance
    print("\n" + "=" * 80)
    print("FACTORIZATION TEST (using resonance as filter)")
    print("=" * 80)

    test_N = semiprimes[0][2]  # Use first semi-prime
    true_p, true_q = semiprimes[0][0], semiprimes[0][1]

    print(f"\nTarget: N = {test_N:,}")
    print(f"True factors: {true_p:,} × {true_q:,}")
    print(f"\nTesting all divisors, ranking by resonance score...")

    candidates = attempt_resonance_factorization(test_N, max_candidates=20)

    if candidates:
        print(f"\nTop 10 candidates (by resonance score):")
        print(f"{'Rank':<6} {'Factor p':>10} {'Factor q':>10} {'Score':>12} {'Correct?':<10}")
        print("-" * 60)

        for rank, (d, q, score) in enumerate(candidates[:10], 1):
            is_correct = (d == true_p and q == true_q) or (d == true_q and q == true_p)
            marker = "✓ TRUE" if is_correct else ""
            print(f"{rank:<6} {d:>10,} {q:>10,} {score:>12.6f} {marker:<10}")

        # Check if true factors are in top N
        true_found_rank = None
        for rank, (d, q, score) in enumerate(candidates, 1):
            if (d == true_p and q == true_q) or (d == true_q and q == true_p):
                true_found_rank = rank
                break

        if true_found_rank:
            print(f"\n✓ True factors found at rank {true_found_rank}")
        else:
            print(f"\n✗ True factors not in top {len(candidates)} candidates")

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)

    # Return summary for further analysis
    return {
        'semiprimes': semiprimes,
        'reciprocal_errors': reciprocal_errors,
        'curvature_sum_errors': curvature_sum_errors,
        'curvature_2sum_errors': curvature_2sum_errors,
        'theta_product_errors': theta_product_errors,
        'resonance_scores': resonance_scores
    }

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    results = run_experiment()