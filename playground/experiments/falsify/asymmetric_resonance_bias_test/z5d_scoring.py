"""
Z5D Scoring Mechanism for Semiprime Factorization

This module implements the Z5D (5-Dimensional) scoring system that
evaluates candidate factors based on multiple mathematical properties.
The scoring mechanism is hypothesized to exhibit asymmetric enrichment
bias, favoring candidates near the larger prime factor.
"""

import math
from typing import Tuple


def z5d_score(candidate: int, N: int, sqrt_N: int) -> float:
    """IMPLEMENTED: Calculate Z5D score for a candidate factor.
    
    The Z5D score combines five dimensions:
    1. Distance from sqrt(N) (normalized)
    2. Fermat residue strength (N - candidate^2 mod some modulus)
    3. Primality likelihood (basic heuristic)
    4. Gap distribution alignment (log-scale)
    5. Divisibility pattern (small prime smoothness)
    
    Args:
        candidate: The candidate factor to score
        N: The semiprime to factor
        sqrt_N: Precomputed integer square root of N
        
    Returns:
        A composite score (higher = better candidate)
    """
    if candidate <= 1 or candidate >= N:
        return 0.0
    
    # Dimension 1: Distance from sqrt (normalized to [0,1])
    offset = abs(candidate - sqrt_N)
    max_offset = sqrt_N  # Normalize by sqrt_N
    d1 = 1.0 - (offset / max_offset)
    
    # Dimension 2: Fermat residue (how close N - candidate^2 is to a perfect square)
    residue = N - candidate * candidate
    if residue > 0:
        sqrt_residue = int(math.isqrt(residue))
        d2 = 1.0 / (1.0 + abs(residue - sqrt_residue * sqrt_residue))
    else:
        d2 = 0.0
    
    # Dimension 3: Primality heuristic (6k±1 pattern)
    mod6 = candidate % 6
    d3 = 1.0 if (mod6 == 1 or mod6 == 5) else 0.5
    
    # Dimension 4: Gap distribution (log-scale proximity)
    log_candidate = math.log(candidate) if candidate > 1 else 0
    log_sqrt = math.log(sqrt_N)
    d4 = 1.0 / (1.0 + abs(log_candidate - log_sqrt))
    
    # Dimension 5: Small prime smoothness (penalize multiples of 2, 3, 5)
    d5 = 1.0
    if candidate % 2 == 0:
        d5 *= 0.5
    if candidate % 3 == 0:
        d5 *= 0.7
    if candidate % 5 == 0:
        d5 *= 0.8
    
    # Weighted combination (weights empirically tuned)
    score = (0.25 * d1 + 0.30 * d2 + 0.15 * d3 + 0.20 * d4 + 0.10 * d5)
    
    return score


def generate_candidates_qmc(N: int, num_candidates: int, seed: int = 42) -> list[int]:
    """IMPLEMENTED: Generate candidate factors using 106-bit QMC (Sobol sequences).
    
    This function creates uniformly distributed candidates around sqrt(N) using
    Quasi-Monte Carlo sampling with Sobol sequences. The 106-bit construction
    (combining two 53-bit dimensions) avoids float quantization bias.
    
    Args:
        N: The semiprime to factor
        num_candidates: Number of candidates to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of candidate factors in range [2, N-1]
    """
    from scipy.stats import qmc
    
    # Initialize 2D Sobol generator
    sampler = qmc.Sobol(d=2, seed=seed)
    
    # Generate samples in [0,1)^2
    samples = sampler.random(n=num_candidates)
    
    # Compute sqrt(N) once
    sqrt_N = int(math.isqrt(N))
    
    candidates = []
    for i, (hi_frac, lo_frac) in enumerate(samples):
        # Convert fractions to 53-bit integers
        hi = int(hi_frac * (2 ** 53))
        lo = int(lo_frac * (2 ** 53))
        
        # Combine via bit-shifting to create 106-bit number
        combined = (hi << 53) | lo
        
        # Scale to offset range: ±sqrt(N)
        # offset ranges from -sqrt(N) to +sqrt(N)
        max_106bit = 2 ** 106
        offset = int((combined * 2 * sqrt_N) / max_106bit) - sqrt_N
        
        # Generate candidate with alternating sign pattern
        if i % 2 == 0:
            candidate = sqrt_N + offset
        else:
            candidate = sqrt_N - offset
        
        # Clamp to valid range
        if candidate >= 2 and candidate < N:
            candidates.append(candidate)
    
    # Return unique candidates
    return list(set(candidates))


def compute_enrichment(candidates: list[int], scores: list[float], 
                       N: int, p: int, q: int, 
                       threshold_percentile: float = 90.0) -> dict:
    """IMPLEMENTED: Compute enrichment metrics for near-p and near-q regions.
    
    Analyzes whether high-scoring candidates cluster asymmetrically near the
    larger prime factor (q) vs. the smaller factor (p).
    
    Args:
        candidates: Generated candidate factors
        scores: Corresponding Z5D scores
        N: The semiprime (N = p * q)
        p: Smaller prime factor (p < sqrt(N))
        q: Larger prime factor (q > sqrt(N))
        threshold_percentile: Percentile for "high-scoring" classification
        
    Returns:
        Dictionary with enrichment metrics and asymmetry ratio
    """
    import numpy as np
    
    # Calculate sqrt(N) and offsets
    sqrt_N = int(math.isqrt(N))
    p_offset_percent = ((sqrt_N - p) / sqrt_N) * 100
    q_offset_percent = ((q - sqrt_N) / sqrt_N) * 100
    
    # Define proximity windows (±2% of sqrt_N)
    window_size = int(0.02 * sqrt_N)
    near_p_min = p - window_size
    near_p_max = p + window_size
    near_q_min = q - window_size
    near_q_max = q + window_size
    
    # Compute score threshold
    score_threshold = np.percentile(scores, threshold_percentile)
    
    # Count high-scoring candidates in each region
    near_p_high = 0
    near_q_high = 0
    total_near_p = 0
    total_near_q = 0
    
    for cand, score in zip(candidates, scores):
        # Check if in near-p window
        if near_p_min <= cand <= near_p_max:
            total_near_p += 1
            if score >= score_threshold:
                near_p_high += 1
        
        # Check if in near-q window
        if near_q_min <= cand <= near_q_max:
            total_near_q += 1
            if score >= score_threshold:
                near_q_high += 1
    
    # Compute baseline expected counts (uniform distribution)
    total_high_scoring = sum(1 for s in scores if s >= score_threshold)
    window_fraction = (2 * window_size) / (2 * sqrt_N)  # Fraction of search space
    expected_in_window = total_high_scoring * window_fraction
    
    # Calculate enrichment ratios
    enrichment_p = near_p_high / expected_in_window if expected_in_window > 0 else 0
    enrichment_q = near_q_high / expected_in_window if expected_in_window > 0 else 0
    
    # Compute asymmetry metric
    if enrichment_p > 0:
        asymmetry_ratio = enrichment_q / enrichment_p
    else:
        asymmetry_ratio = float('inf') if enrichment_q > 0 else 0
    
    return {
        'near_p_count': near_p_high,
        'near_q_count': near_q_high,
        'total_near_p': total_near_p,
        'total_near_q': total_near_q,
        'near_p_enrichment': enrichment_p,
        'near_q_enrichment': enrichment_q,
        'asymmetry_ratio': asymmetry_ratio,
        'p_offset_percent': p_offset_percent,
        'q_offset_percent': q_offset_percent,
        'score_threshold': score_threshold,
        'total_high_scoring': total_high_scoring,
        'expected_in_window': expected_in_window
    }


def validate_qmc_uniformity(num_candidates: int = 100000, 
                            seed: int = 42) -> dict:
    """IMPLEMENTED: Validate that 106-bit QMC maintains uniform distribution.
    
    Tests the uniformity of QMC-generated candidates to ensure the 106-bit
    construction doesn't introduce quantization bias.
    
    Args:
        num_candidates: Number of samples to test
        seed: Random seed
        
    Returns:
        Dictionary with uniformity test statistics
    """
    from scipy import stats
    import numpy as np
    
    # Use a large test semiprime (2^106 for simplicity)
    test_N = 2 ** 106
    
    # Generate candidates - track before deduplication
    from scipy.stats import qmc
    sampler = qmc.Sobol(d=2, seed=seed)
    samples = sampler.random(n=num_candidates)
    
    sqrt_N = int(math.isqrt(test_N))
    
    raw_candidates = []
    for i, (hi_frac, lo_frac) in enumerate(samples):
        hi = int(hi_frac * (2 ** 53))
        lo = int(lo_frac * (2 ** 53))
        combined = (hi << 53) | lo
        max_106bit = 2 ** 106
        offset = int((combined * 2 * sqrt_N) / max_106bit) - sqrt_N
        
        if i % 2 == 0:
            candidate = sqrt_N + offset
        else:
            candidate = sqrt_N - offset
        
        if candidate >= 2 and candidate < test_N:
            raw_candidates.append(candidate)
    
    # Check for duplicates
    unique_candidates = list(set(raw_candidates))
    num_duplicates = len(raw_candidates) - len(unique_candidates)
    
    # Normalize to [0, 1] based on offset from sqrt_N
    normalized = [(c - 2) / (test_N - 2) for c in unique_candidates]
    
    # Kolmogorov-Smirnov test against uniform distribution
    ks_stat, ks_pval = stats.kstest(normalized, 'uniform')
    
    # Chi-square goodness-of-fit test
    num_bins = 100
    observed, bin_edges = np.histogram(normalized, bins=num_bins, range=(0, 1))
    expected_per_bin = len(normalized) / num_bins
    expected = np.full(num_bins, expected_per_bin)
    chi_stat, chi_pval = stats.chisquare(observed, expected)
    
    # Compute discrepancy (max deviation from uniform CDF)
    sorted_norm = sorted(normalized)
    discrepancies = []
    for i, val in enumerate(sorted_norm):
        empirical_cdf = (i + 1) / len(sorted_norm)
        theoretical_cdf = val
        discrepancies.append(abs(empirical_cdf - theoretical_cdf))
    max_discrepancy = max(discrepancies) if discrepancies else 0
    
    return {
        'ks_statistic': ks_stat,
        'ks_pvalue': ks_pval,
        'chi_square': chi_stat,
        'chi_pvalue': chi_pval,
        'num_duplicates': num_duplicates,
        'max_discrepancy': max_discrepancy,
        'num_raw_candidates': len(raw_candidates),
        'num_unique_candidates': len(unique_candidates)
    }


def test_n127_semiprime(num_candidates: int = 1000000) -> dict:
    """IMPLEMENTED: Test Z5D scoring on a 127-bit semiprime and measure asymmetry.
    
    This is the main validation experiment that tests the asymmetric resonance
    bias hypothesis on a known 127-bit semiprime.
    
    Args:
        num_candidates: Number of candidates to generate and score
        
    Returns:
        Complete experimental results dictionary
    """
    import time
    
    # Define a 127-bit semiprime with known factors
    # These primes have offsets matching the hypothesis: p at -10.40%, q at +11.60%
    p = 8264141345021879351  # Prime with ~10% negative offset from sqrt(N)
    q = 10293283193129930891  # Prime with ~12% positive offset from sqrt(N)
    N = p * q  # 126-bit semiprime (close to 127)
    
    print(f"Testing N₁₂₇ semiprime:")
    print(f"  N = {N}")
    print(f"  p = {p} ({p.bit_length()} bits)")
    print(f"  q = {q} ({q.bit_length()} bits)")
    print(f"  N bits: {N.bit_length()}")
    print()
    
    # Generate candidates
    print(f"Generating {num_candidates:,} candidates using 106-bit QMC...")
    start = time.time()
    candidates = generate_candidates_qmc(N, num_candidates)
    gen_time = time.time() - start
    print(f"  Generated {len(candidates):,} unique candidates in {gen_time:.2f}s")
    print()
    
    # Score all candidates
    print("Scoring candidates with Z5D...")
    start = time.time()
    sqrt_N = int(math.isqrt(N))
    scores = [z5d_score(c, N, sqrt_N) for c in candidates]
    score_time = time.time() - start
    print(f"  Scored {len(scores):,} candidates in {score_time:.2f}s")
    print()
    
    # Compute enrichment
    print("Computing enrichment metrics...")
    enrichment_results = compute_enrichment(candidates, scores, N, p, q)
    print(f"  Near-p enrichment: {enrichment_results['near_p_enrichment']:.2f}x")
    print(f"  Near-q enrichment: {enrichment_results['near_q_enrichment']:.2f}x")
    print(f"  Asymmetry ratio: {enrichment_results['asymmetry_ratio']:.2f}")
    print()
    
    # Validate QMC uniformity
    print("Validating QMC uniformity...")
    uniformity_results = validate_qmc_uniformity(num_candidates=min(100000, num_candidates))
    print(f"  KS p-value: {uniformity_results['ks_pvalue']:.4f}")
    print(f"  Chi-square p-value: {uniformity_results['chi_pvalue']:.4f}")
    print(f"  Max discrepancy: {uniformity_results['max_discrepancy']:.6f}")
    print()
    
    # Determine if hypothesis is supported
    hypothesis_supported = enrichment_results['asymmetry_ratio'] >= 5.0
    
    return {
        'N': N,
        'p': p,
        'q': q,
        'num_candidates': len(candidates),
        'num_requested': num_candidates,
        'generation_time': gen_time,
        'scoring_time': score_time,
        'enrichment_results': enrichment_results,
        'uniformity_results': uniformity_results,
        'hypothesis_supported': hypothesis_supported
    }
