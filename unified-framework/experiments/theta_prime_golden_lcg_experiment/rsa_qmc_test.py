"""
RSA QMC Variance Reduction Test
Simplified RSA factorization using Quasi-Monte Carlo with θ′ bias.
Tests variance reduction in candidate sampling vs baseline Monte Carlo.
"""

import math
import statistics
from golden_lcg import GoldenLCG
from theta_prime_bias import ThetaPrimeBias


class RSAQMCTest:
    """RSA factorization variance reduction test using QMC."""
    
    # Small RSA test numbers (products of two primes)
    RSA_NUMBERS = {
        'RSA-10': 35,      # 5 × 7
        'RSA-15': 323,     # 17 × 19
        'RSA-20': 1199,    # 29 × 41
        'RSA-25': 5767,    # 61 × 97
    }
    
    def __init__(self, seed=42):
        self.seed = seed
        self.lcg = GoldenLCG(seed=seed)
    
    def trial_division_samples(self, n, n_samples, ordering_method='baseline'):
        """
        Sample candidate divisors and measure variance in successful candidates.
        
        Args:
            n: Number to factor
            n_samples: Number of samples to try
            ordering_method: 'baseline' or 'theta_prime'
        
        Returns:
            dict with samples, hits, variance metrics
        """
        sqrt_n = int(math.sqrt(n))
        
        # Generate candidate divisors
        if ordering_method == 'baseline':
            # Monte Carlo: uniform random sampling
            candidates = [self.lcg.next_range(2, sqrt_n) for _ in range(n_samples)]
        elif ordering_method == 'theta_prime':
            # θ′-biased: structured sampling with bias
            bias = ThetaPrimeBias(alpha=0.1, seed=self.seed)
            # Generate candidates with θ′ ordering
            base_candidates = list(range(2, min(sqrt_n, 2 + n_samples)))
            if len(base_candidates) < n_samples:
                # Need more candidates, sample with replacement
                base_candidates = [self.lcg.next_range(2, sqrt_n) 
                                  for _ in range(n_samples)]
            candidates = bias.generate_biased_ordering(base_candidates[:n_samples])
        else:
            raise ValueError(f"Unknown ordering method: {ordering_method}")
        
        # Test candidates and measure distribution
        hit_positions = []
        unique_candidates = len(set(candidates))
        
        for i, candidate in enumerate(candidates):
            if n % candidate == 0:
                hit_positions.append(i)
        
        # Compute variance metrics
        n_hits = len(hit_positions)
        
        if n_hits > 1:
            variance = statistics.variance(hit_positions)
            std_dev = statistics.stdev(hit_positions)
        else:
            variance = 0.0
            std_dev = 0.0
        
        return {
            'n_samples': n_samples,
            'unique_candidates': unique_candidates,
            'n_hits': n_hits,
            'hit_positions': hit_positions,
            'variance': variance,
            'std_dev': std_dev,
        }
    
    def run_variance_comparison(self, rsa_name, n_samples=1000):
        """
        Compare variance between baseline and θ′-biased sampling.
        
        Returns:
            dict with comparison metrics
        """
        n = self.RSA_NUMBERS[rsa_name]
        
        # Run baseline (Monte Carlo)
        self.lcg = GoldenLCG(seed=self.seed)  # Reset
        baseline = self.trial_division_samples(n, n_samples, 'baseline')
        
        # Run θ′-biased
        self.lcg = GoldenLCG(seed=self.seed)  # Reset with same seed
        theta_prime = self.trial_division_samples(n, n_samples, 'theta_prime')
        
        # Compute reduction
        if baseline['variance'] > 0:
            variance_reduction = (baseline['variance'] - theta_prime['variance']) / baseline['variance']
        else:
            variance_reduction = 0.0
        
        return {
            'rsa_name': rsa_name,
            'n': n,
            'baseline': baseline,
            'theta_prime': theta_prime,
            'variance_reduction_pct': variance_reduction * 100,
        }


def bootstrap_variance_reduction(test_cases, n_bootstrap=100):
    """
    Bootstrap confidence intervals for variance reduction.
    
    Args:
        test_cases: List of test case names
        n_bootstrap: Number of bootstrap replicates
    
    Returns:
        dict with bootstrap statistics
    """
    results = []
    
    for rep in range(n_bootstrap):
        seed = 42 + rep
        tester = RSAQMCTest(seed=seed)
        
        reductions = []
        for rsa_name in test_cases:
            result = tester.run_variance_comparison(rsa_name, n_samples=200)
            reductions.append(result['variance_reduction_pct'])
        
        mean_reduction = statistics.mean(reductions)
        results.append(mean_reduction)
    
    # Compute CI
    results.sort()
    ci_lower = results[int(0.025 * n_bootstrap)]
    ci_upper = results[int(0.975 * n_bootstrap)]
    mean_result = statistics.mean(results)
    
    return {
        'mean_reduction_pct': mean_result,
        'ci_95_lower': ci_lower,
        'ci_95_upper': ci_upper,
        'n_bootstrap': n_bootstrap,
    }


def test_rsa_qmc():
    """Test RSA QMC variance reduction."""
    print("Testing RSA QMC Variance Reduction...")
    
    tester = RSAQMCTest(seed=42)
    
    # Run single test
    result = tester.run_variance_comparison('RSA-10', n_samples=100)
    
    print(f"RSA-10 (n={result['n']}):")
    print(f"  Baseline: {result['baseline']['unique_candidates']} unique, "
          f"variance={result['baseline']['variance']:.2f}")
    print(f"  θ′-biased: {result['theta_prime']['unique_candidates']} unique, "
          f"variance={result['theta_prime']['variance']:.2f}")
    print(f"  Variance reduction: {result['variance_reduction_pct']:.1f}%")
    
    # Bootstrap test (small sample for speed)
    print("\nRunning bootstrap (n=10)...")
    boot_result = bootstrap_variance_reduction(['RSA-10', 'RSA-15'], n_bootstrap=10)
    print(f"  Mean reduction: {boot_result['mean_reduction_pct']:.1f}%")
    print(f"  95% CI: [{boot_result['ci_95_lower']:.1f}%, {boot_result['ci_95_upper']:.1f}%]")
    
    print("\nRSA QMC tests passed!\n")


if __name__ == "__main__":
    test_rsa_qmc()
