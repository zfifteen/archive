#!/usr/bin/env python3
"""
Balanced Semiprime Factorization Evaluation Harness

Reproduces semiprime factorization navigation results where partial_rate 
(recovering either factor p or q) is the correct, practical success metric. 
Compares balanced vs. unbalanced sampling, sweeps ε, and includes A/B/C heuristics.

SUCCESS METRICS:
- partial_rate: Practical factorization success rate - finding either p or q
  This is the key metric since discovering one factor immediately gives the other
  via q = N/p, followed by primality verification.
- full_rate: Heuristic strength measure - finding both p and q in candidate set
  This measures how well the heuristic captures both factors but is less practical
  since only one factor needs to be found to complete factorization.

HEURISTIC STRATEGIES:
- Heuristic A (band): Single-band search around sqrt(N)
- Heuristic B (dual): Dual-band search with broader coverage  
- Heuristic C (minor): Minor arc approach with selective theta-based filtering

No external dependencies - includes its own sieve and Wilson confidence intervals.
"""

import math
import random
import statistics
import csv
import argparse
from typing import List, Tuple, Dict, Optional, Callable, NamedTuple
from dataclasses import dataclass
from pathlib import Path
import sys

# Constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio
K = 0.3  # Fixed parameter

@dataclass
class HeuristicSpec:
    """Specification for a heuristic function"""
    name: str
    func: Callable
    params: Dict

class SemiprimeSample(NamedTuple):
    """A sampled semiprime with metadata"""
    N: int
    p: int 
    q: int
    theta_p: float  # theta'(p)
    theta_q: float  # theta'(q)

class EvaluationResult(NamedTuple):
    """Results for a single heuristic evaluation"""
    heuristic: str
    eps: float
    max_candidates: int
    n: int
    partial_rate: float
    partial_ci95: Tuple[float, float]
    full_rate: float
    full_ci95: Tuple[float, float]
    avg_candidates: float

def sieve_of_eratosthenes(limit: int) -> List[int]:
    """Simple sieve implementation - no external dependencies"""
    if limit < 2:
        return []
    
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    return [i for i in range(2, limit + 1) if is_prime[i]]

def is_prime_simple(n: int) -> bool:
    """Simple primality test for moderate numbers"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def wilson_confidence_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Wilson score confidence interval for binomial proportion
    More robust than normal approximation for small samples
    """
    if total == 0:
        return (0.0, 0.0)
    
    # Z-score for confidence level
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_scores.get(confidence, 1.96)
    
    p = successes / total
    n = total
    
    # Wilson interval formula
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    
    return (lower, upper)

def theta_prime(x: float) -> float:
    """
    Approximation of θ'(x) = d/dx[Σ_{p≤x} log p]
    Using θ'(x) ≈ log(x) (prime number theorem asymptotic)
    """
    if x <= 1:
        return 0.0
    return math.log(x)

def sample_semiprimes(primes: List[int], target_count: int = 1000, 
                     Nmax: int = 1_000_000, seed: int = 42,
                     balanced: bool = True) -> List[SemiprimeSample]:
    """
    Sample semiprimes N = p*q with specified properties
    
    Args:
        primes: List of prime numbers to choose from
        target_count: Number of semiprimes to generate
        Nmax: Maximum value for N
        seed: Random seed for reproducibility
        balanced: If True, sample p,q near sqrt(N); if False, bias toward smaller p
    
    Returns:
        List of SemiprimeSample objects
    """
    random.seed(seed)
    samples = []
    
    # Define sampling range based on Nmax
    sqrt_Nmax = math.sqrt(Nmax)
    
    if balanced:
        # Balanced sampling: both p and q near sqrt(N)
        # Use a wider range to ensure we can find balanced factors
        p_min = int(sqrt_Nmax * 0.3)  # Expanded range
        p_max = int(sqrt_Nmax * 3.0)
    else:
        # Unbalanced sampling: favor smaller p
        p_min = 2
        p_max = int(sqrt_Nmax)
    
    # Filter primes to sampling range and ensure we have enough
    candidate_primes = [p for p in primes if p_min <= p <= p_max]
    if len(candidate_primes) < 20:
        # Expand range if we don't have enough primes
        p_max = min(max(primes), int(sqrt_Nmax * 5))
        candidate_primes = [p for p in primes if p_min <= p <= p_max]
    
    attempts = 0
    max_attempts = target_count * 20  # Increased max attempts
    
    while len(samples) < target_count and attempts < max_attempts:
        attempts += 1
        
        # Sample p
        p = random.choice(candidate_primes)
        
        if balanced:
            # For balanced, choose q such that p*q is reasonably balanced
            # Target q close to sqrt(target_N) / p where target_N is around Nmax/2
            target_N = random.uniform(Nmax * 0.1, Nmax)
            target_q = target_N / p
            
            # Find primes near target_q
            tolerance = target_q * 0.5
            q_candidates = [q for q in candidate_primes 
                          if abs(q - target_q) < tolerance and q != p]
        else:
            # For unbalanced, any q that gives N ≤ Nmax
            max_q = min(Nmax // p, p_max)
            q_candidates = [q for q in candidate_primes if q <= max_q and q != p]
        
        if not q_candidates:
            continue
            
        q = random.choice(q_candidates)
        N = p * q
        
        if N > Nmax or N < 1000:  # Ensure minimum size
            continue
        
        # For balanced sampling, ensure the factors are reasonably balanced
        if balanced:
            balance_ratio = max(p, q) / min(p, q)
            if balance_ratio > 10:  # Skip highly unbalanced pairs
                continue
            
        # Calculate theta' values
        theta_p_val = theta_prime(p)
        theta_q_val = theta_prime(q)
        
        samples.append(SemiprimeSample(N, p, q, theta_p_val, theta_q_val))
    
    return samples[:target_count]

def heuristic_band(N: int, ctx: Dict) -> List[int]:
    """
    Heuristic A: Single-band search around theoretical optimum
    
    Args:
        N: The semiprime to factor
        ctx: Context containing theta_pool, pool, and parameters
    
    Returns:
        List of candidate prime factors
    """
    eps = ctx.get("eps", 0.05)
    max_candidates = ctx.get("max_candidates", 1000)
    theta_pool = ctx.get("theta_pool", [])
    pool = ctx.get("pool", [])
    
    sqrt_N = math.sqrt(N)
    
    # Theoretical band around sqrt(N)
    band_center = sqrt_N
    band_width = eps * sqrt_N
    
    candidates = []
    
    # Search for primes in the band around sqrt(N)
    for i, p in enumerate(pool):
        if len(candidates) >= max_candidates:
            break
            
        # Check if prime is in the band around sqrt(N)
        if abs(p - band_center) <= band_width:
            candidates.append(p)
    
    return candidates

def heuristic_dual(N: int, ctx: Dict) -> List[int]:
    """
    Heuristic B: Dual-band search around both sqrt(N) and theoretical minima
    
    This heuristic searches in two bands: one around sqrt(N) like heuristic A,
    and a second band around the theoretical minimum value based on the golden ratio.
    This provides broader coverage while maintaining selectivity.
    
    Args:
        N: The semiprime to factor
        ctx: Context containing theta_pool, pool, and parameters
    
    Returns:
        List of candidate prime factors
    """
    eps = ctx.get("eps", 0.05)
    max_candidates = ctx.get("max_candidates", 1000)
    theta_pool = ctx.get("theta_pool", [])
    pool = ctx.get("pool", [])
    
    sqrt_N = math.sqrt(N)
    
    # Band 1: Around sqrt(N) (like heuristic A)
    band1_center = sqrt_N
    band1_width = eps * sqrt_N
    
    # Band 2: Around theoretical minimum based on golden ratio
    # Use a different center based on empirical observations
    band2_center = sqrt_N / PHI  # Golden ratio-based offset
    band2_width = eps * sqrt_N * 0.5  # Narrower second band
    
    candidates = []
    
    # Search for primes in both bands
    for i, p in enumerate(pool):
        if len(candidates) >= max_candidates:
            break
            
        # Check if prime is in either band
        in_band1 = abs(p - band1_center) <= band1_width
        in_band2 = abs(p - band2_center) <= band2_width
        
        if in_band1 or in_band2:
            candidates.append(p)
    
    return candidates

def heuristic_minor(N: int, ctx: Dict) -> List[int]:
    """
    Heuristic C: Minor arc search - selective strategy with reduced candidates
    
    This heuristic implements a "minor arc" approach, focusing on primes that are
    close to sqrt(N) but using a more selective criterion based on theta' values.
    The "minor arc" refers to selecting only primes whose theta'(p) values fall
    within a specific range that historically shows higher success rates.
    
    This strategy trades broader search coverage for computational efficiency by
    being more selective about which candidates to include.
    
    Args:
        N: The semiprime to factor
        ctx: Context containing theta_pool, pool, and parameters
    
    Returns:
        List of candidate prime factors (typically fewer than other heuristics)
    """
    eps = ctx.get("eps", 0.05)
    max_candidates = ctx.get("max_candidates", 1000)
    theta_pool = ctx.get("theta_pool", [])
    pool = ctx.get("pool", [])
    
    sqrt_N = math.sqrt(N)
    
    # Narrower band than heuristic A - more selective
    band_center = sqrt_N
    band_width = eps * sqrt_N * 0.6  # 60% of the width used by heuristic A
    
    candidates = []
    target_theta = theta_prime(int(sqrt_N))  # Target theta value
    
    # Search for primes with additional theta' filtering
    for i, p in enumerate(pool):
        if len(candidates) >= max_candidates // 2:  # Even more selective on count
            break
            
        # Check if prime is in the narrower band
        if abs(p - band_center) <= band_width:
            # Additional selectivity: only include primes with theta' values
            # that are close to the target theta'(sqrt(N))
            p_theta = theta_prime(p)
            if abs(p_theta - target_theta) <= 0.1:  # Theta proximity filter
                candidates.append(p)
    
    return candidates

def evaluate_heuristic(heuristic_spec: HeuristicSpec, samples: List[SemiprimeSample],
                      prime_pool: List[int]) -> EvaluationResult:
    """
    Evaluate a heuristic on the sample set
    
    Args:
        heuristic_spec: The heuristic to evaluate
        samples: List of semiprime samples
        prime_pool: Pool of prime numbers for context
    
    Returns:
        EvaluationResult with success rates and confidence intervals
    """
    eps = heuristic_spec.params.get("eps", 0.05)
    max_candidates = heuristic_spec.params.get("max_candidates", 1000)
    
    partial_successes = 0  # Found either p or q
    full_successes = 0     # Found both p and q
    total_candidates = 0
    
    # Build context
    theta_pool = [theta_prime(p) for p in prime_pool]
    ctx = {
        "eps": eps,
        "max_candidates": max_candidates,
        "theta_pool": theta_pool,
        "pool": prime_pool
    }
    
    for sample in samples:
        # Get candidates from heuristic
        candidates = heuristic_spec.func(sample.N, ctx)
        total_candidates += len(candidates)
        
        # Check for factor recovery
        found_p = sample.p in candidates
        found_q = sample.q in candidates
        
        if found_p or found_q:
            partial_successes += 1
        
        if found_p and found_q:
            full_successes += 1
    
    n = len(samples)
    partial_rate = partial_successes / n if n > 0 else 0.0
    full_rate = full_successes / n if n > 0 else 0.0
    avg_candidates = total_candidates / n if n > 0 else 0.0
    
    # Wilson confidence intervals
    partial_ci95 = wilson_confidence_interval(partial_successes, n)
    full_ci95 = wilson_confidence_interval(full_successes, n)
    
    return EvaluationResult(
        heuristic=heuristic_spec.name,
        eps=eps,
        max_candidates=max_candidates,
        n=n,
        partial_rate=partial_rate,
        partial_ci95=partial_ci95,
        full_rate=full_rate,
        full_ci95=full_ci95,
        avg_candidates=avg_candidates
    )

def calculate_correlation(samples: List[SemiprimeSample]) -> float:
    """
    Calculate Pearson correlation r(θ'(p), θ'(q)) across samples
    """
    if len(samples) < 2:
        return 0.0
    
    theta_p_values = [s.theta_p for s in samples]
    theta_q_values = [s.theta_q for s in samples]
    
    try:
        correlation = statistics.correlation(theta_p_values, theta_q_values)
        return correlation
    except statistics.StatisticsError:
        return 0.0

def write_csv_results(results: List[EvaluationResult], filename: str):
    """Write evaluation results to CSV file"""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            'heuristic', 'eps', 'max_candidates', 'n',
            'partial_rate', 'partial_ci95_lower', 'partial_ci95_upper',
            'full_rate', 'full_ci95_lower', 'full_ci95_upper',
            'avg_candidates'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'heuristic': result.heuristic,
                'eps': result.eps,
                'max_candidates': result.max_candidates,
                'n': result.n,
                'partial_rate': f"{result.partial_rate:.4f}",
                'partial_ci95_lower': f"{result.partial_ci95[0]:.4f}",
                'partial_ci95_upper': f"{result.partial_ci95[1]:.4f}",
                'full_rate': f"{result.full_rate:.4f}",
                'full_ci95_lower': f"{result.full_ci95[0]:.4f}",
                'full_ci95_upper': f"{result.full_ci95[1]:.4f}",
                'avg_candidates': f"{result.avg_candidates:.1f}"
            })

def write_markdown_results(results: List[EvaluationResult], samples: List[SemiprimeSample], 
                         correlation: float, filename: str):
    """Write evaluation results to Markdown file"""
    
    with open(filename, 'w') as mdfile:
        mdfile.write("# Balanced Semiprime Factorization Evaluation Results\n\n")
        
        # Summary
        mdfile.write("## Summary\n\n")
        mdfile.write(f"- **Total samples**: {len(samples)}\n")
        mdfile.write(f"- **Correlation r(θ'(p), θ'(q))**: {correlation:.4f}\n")
        mdfile.write(f"- **Evaluation type**: Balanced sampling\n")
        mdfile.write(f"- **Nmax**: 1,000,000\n")
        mdfile.write(f"- **Target count**: 1,000\n\n")
        
        # Results table
        mdfile.write("## Results\n\n")
        mdfile.write("| Heuristic | eps | max_candidates | n | partial_rate | partial_CI95 | full_rate | full_CI95 | avg_candidates |\n")
        mdfile.write("|-----------|-----|----------------|---|--------------|--------------|-----------|-----------|----------------|\n")
        
        for result in results:
            partial_ci = f"({result.partial_ci95[0]:.3f}, {result.partial_ci95[1]:.3f})"
            full_ci = f"({result.full_ci95[0]:.3f}, {result.full_ci95[1]:.3f})"
            
            mdfile.write(f"| {result.heuristic} | {result.eps} | {result.max_candidates} | "
                        f"{result.n} | {result.partial_rate:.4f} | {partial_ci} | "
                        f"{result.full_rate:.4f} | {full_ci} | {result.avg_candidates:.1f} |\n")
        
        # Interpretation
        mdfile.write("\n## Interpretation\n\n")
        mdfile.write("- **partial_rate**: Practical factorization rate (recovering either p or q)\n")
        mdfile.write("- **full_rate**: Complete factor recovery rate (both p and q)\n") 
        mdfile.write("- **avg_candidates**: Average number of candidates tested per sample\n")
        mdfile.write("- **Wilson CI95**: 95% confidence intervals using Wilson score method\n\n")
        
        mdfile.write("The partial_rate is the key metric since recovering one factor p ")
        mdfile.write("allows immediate calculation of q = N/p followed by primality verification.\n")

def main():
    """Main evaluation function"""
    parser = argparse.ArgumentParser(description="Balanced Semiprime Factorization Evaluation")
    parser.add_argument("--Nmax", type=int, default=1_000_000, help="Maximum semiprime value")
    parser.add_argument("--target-count", type=int, default=1000, help="Number of samples to generate")
    parser.add_argument("--eps", nargs="+", type=float, default=[0.02, 0.03, 0.04, 0.05], 
                       help="Epsilon values to sweep")
    parser.add_argument("--max-candidates", type=int, default=1000, help="Maximum candidates per heuristic")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--unbalanced", action="store_true", help="Use unbalanced sampling")
    parser.add_argument("--output-prefix", default="balanced_eval", help="Output file prefix")
    
    args = parser.parse_args()
    
    print("Semiprime Balanced Factorization Evaluation")
    print("=" * 50)
    print(f"Nmax: {args.Nmax:,}")
    print(f"Target samples: {args.target_count}")
    print(f"Eps values: {args.eps}")
    print(f"Max candidates: {args.max_candidates}")
    print(f"Seed: {args.seed}")
    print(f"Balanced sampling: {not args.unbalanced}")
    print()
    
    # Generate prime pool
    prime_limit = int(5 * math.sqrt(args.Nmax))  # Increased from 2x to 5x
    print(f"Generating primes up to {prime_limit:,}...")
    primes = sieve_of_eratosthenes(prime_limit)
    print(f"Generated {len(primes):,} primes")
    
    # Sample semiprimes
    print("Sampling semiprimes...")
    samples = sample_semiprimes(
        primes=primes,
        target_count=args.target_count,
        Nmax=args.Nmax,
        seed=args.seed,
        balanced=not args.unbalanced
    )
    print(f"Generated {len(samples)} semiprime samples")
    
    if len(samples) == 0:
        print("ERROR: No samples generated!")
        return 1
    
    # Calculate correlation
    correlation = calculate_correlation(samples)
    print(f"Correlation r(θ'(p), θ'(q)): {correlation:.4f}")
    
    # Set up heuristics
    heuristics = []
    eps_list = args.eps
    max_candidates = args.max_candidates
    
    # Register heuristic A (single-band)
    for eps in eps_list:
        heuristics.append(HeuristicSpec(
            name=f"A:band@{eps}",
            func=heuristic_band,
            params={"eps": eps, "max_candidates": max_candidates}
        ))
    
    # Enable basic implementations of B and C:
    for eps in eps_list:
        heuristics.append(HeuristicSpec(
            name=f"B:dual@{eps}",
            func=heuristic_dual,
            params={"eps": eps, "max_candidates": max_candidates}
        ))
        heuristics.append(HeuristicSpec(
            name=f"C:minor@{eps}",
            func=heuristic_minor,
            params={"eps": eps, "max_candidates": max_candidates}
        ))
    
    # Evaluate heuristics
    print("\nEvaluating heuristics...")
    results = []
    
    for heuristic_spec in heuristics:
        print(f"  Evaluating {heuristic_spec.name}...")
        result = evaluate_heuristic(heuristic_spec, samples, primes)
        results.append(result)
        print(f"    partial_rate: {result.partial_rate:.4f}, avg_candidates: {result.avg_candidates:.1f}")
    
    # Output files
    suffix = "_unbal" if args.unbalanced else ""
    csv_file = f"{args.output_prefix}{suffix}.csv"
    md_file = f"{args.output_prefix}{suffix}.md"
    
    # Write results
    print(f"\nWriting results to {csv_file} and {md_file}...")
    write_csv_results(results, csv_file)
    write_markdown_results(results, samples, correlation, md_file)
    
    print("Evaluation complete!")
    
    # Validation check
    print("\nValidation check:")
    for result in results:
        if "0.05" in result.heuristic:
            if 0.18 <= result.partial_rate <= 0.22:
                print(f"✓ {result.heuristic}: partial_rate {result.partial_rate:.4f} in expected range [0.18, 0.22]")
            else:
                print(f"⚠ {result.heuristic}: partial_rate {result.partial_rate:.4f} outside expected range [0.18, 0.22]")
        elif "0.02" in result.heuristic:
            if 0.07 <= result.partial_rate <= 0.10:
                print(f"✓ {result.heuristic}: partial_rate {result.partial_rate:.4f} in expected range [0.07, 0.10]")
            else:
                print(f"⚠ {result.heuristic}: partial_rate {result.partial_rate:.4f} outside expected range [0.07, 0.10]")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())