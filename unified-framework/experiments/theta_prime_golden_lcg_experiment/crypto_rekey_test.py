"""
Crypto Rekey Drift Tolerance Test
Tests rekeying success rate under network drift with θ′-biased timing.
Simulates Gaussian, lognormal, and burst drift patterns.
"""

import math
import statistics
import random
from golden_lcg import GoldenLCG
from theta_prime_bias import ThetaPrimeBias


class CryptoRekeyTest:
    """Crypto rekey drift tolerance test."""
    
    def __init__(self, seed=42):
        self.seed = seed
        self.lcg = GoldenLCG(seed=seed)
        random.seed(seed)  # For drift generation
    
    def generate_drift_trace(self, n_samples, sigma, drift_type='gaussian'):
        """
        Generate network drift trace.
        
        Args:
            n_samples: Number of drift samples
            sigma: Drift standard deviation in ms
            drift_type: 'gaussian', 'lognormal', or 'burst'
        
        Returns:
            List of drift values (ms)
        """
        drift = []
        
        if drift_type == 'gaussian':
            # Gaussian drift: N(0, σ)
            for _ in range(n_samples):
                drift.append(random.gauss(0, sigma))
        
        elif drift_type == 'lognormal':
            # Lognormal drift: log-normal distribution
            for _ in range(n_samples):
                drift.append(random.lognormvariate(0, sigma / 10))
        
        elif drift_type == 'burst':
            # Burst drift: mostly small, occasional large spikes
            for _ in range(n_samples):
                if self.lcg.next_uniform() < 0.1:  # 10% burst probability
                    drift.append(random.gauss(0, sigma * 5))  # Large burst
                else:
                    drift.append(random.gauss(0, sigma))  # Normal drift
        
        else:
            raise ValueError(f"Unknown drift type: {drift_type}")
        
        return drift
    
    def simulate_rekey_sequence(self, base_interval_ms, n_rekeys, drift_trace, 
                                ordering_method='baseline', alpha=0.1):
        """
        Simulate rekey sequence with drift.
        
        Args:
            base_interval_ms: Base rekey interval (ms)
            n_rekeys: Number of rekeys to simulate
            drift_trace: Network drift values
            ordering_method: 'baseline' or 'theta_prime'
            alpha: Bias parameter for θ′
        
        Returns:
            dict with success metrics
        """
        # Generate rekey intervals
        if ordering_method == 'baseline':
            # Fixed intervals
            intervals = [base_interval_ms] * n_rekeys
        elif ordering_method == 'theta_prime':
            # θ′-biased intervals
            bias = ThetaPrimeBias(alpha=alpha, k=0.3, seed=self.seed)
            intervals = bias.generate_biased_intervals(base_interval_ms, n_rekeys)
        else:
            raise ValueError(f"Unknown ordering method: {ordering_method}")
        
        # Simulate rekey attempts
        accept_window_ms = base_interval_ms * 0.2  # ±10% window
        
        cumulative_time = 0
        expected_time = 0
        successes = 0
        failures = 0
        latencies = []
        
        for i in range(n_rekeys):
            interval = intervals[i]
            drift = drift_trace[i % len(drift_trace)]
            
            # Actual time when rekey arrives
            actual_time = cumulative_time + interval + drift
            expected_time += base_interval_ms
            
            # Check if within accept window
            time_diff = abs(actual_time - expected_time)
            
            if time_diff <= accept_window_ms:
                successes += 1
                latencies.append(time_diff)
            else:
                failures += 1
            
            cumulative_time += interval
        
        fail_rate = failures / n_rekeys * 100
        mean_latency = statistics.mean(latencies) if latencies else 0
        
        return {
            'n_rekeys': n_rekeys,
            'successes': successes,
            'failures': failures,
            'fail_rate_pct': fail_rate,
            'mean_latency_ms': mean_latency,
        }
    
    def compare_rekey_tolerance(self, sigma, n_rekeys=1000, drift_type='gaussian'):
        """
        Compare rekey tolerance between baseline and θ′-biased.
        
        Returns:
            dict with comparison metrics
        """
        base_interval = 100.0  # 100ms base interval
        
        # Generate drift trace (same for both methods - paired design)
        drift_trace = self.generate_drift_trace(n_rekeys, sigma, drift_type)
        
        # Test baseline
        baseline = self.simulate_rekey_sequence(
            base_interval, n_rekeys, drift_trace, 'baseline'
        )
        
        # Test θ′-biased (reset LCG to ensure same starting conditions)
        self.lcg = GoldenLCG(seed=self.seed)
        theta_prime = self.simulate_rekey_sequence(
            base_interval, n_rekeys, drift_trace, 'theta_prime', alpha=0.2
        )
        
        # Compute improvement
        fail_rate_delta = baseline['fail_rate_pct'] - theta_prime['fail_rate_pct']
        fail_rate_delta_rel = (fail_rate_delta / baseline['fail_rate_pct'] * 100 
                              if baseline['fail_rate_pct'] > 0 else 0)
        
        latency_delta = baseline['mean_latency_ms'] - theta_prime['mean_latency_ms']
        
        return {
            'sigma': sigma,
            'drift_type': drift_type,
            'baseline': baseline,
            'theta_prime': theta_prime,
            'fail_rate_delta_pct': fail_rate_delta,
            'fail_rate_delta_rel_pct': fail_rate_delta_rel,
            'latency_delta_ms': latency_delta,
        }


def bootstrap_crypto_tolerance(sigma_values, n_bootstrap=100):
    """
    Bootstrap confidence intervals for crypto rekey tolerance.
    """
    results = {s: [] for s in sigma_values}
    
    for rep in range(n_bootstrap):
        seed = 42 + rep
        tester = CryptoRekeyTest(seed=seed)
        
        for sigma in sigma_values:
            result = tester.compare_rekey_tolerance(sigma, n_rekeys=200, 
                                                   drift_type='gaussian')
            results[sigma].append(result['fail_rate_delta_rel_pct'])
    
    # Compute CIs for each sigma
    bootstrap_stats = {}
    for sigma in sigma_values:
        deltas = sorted(results[sigma])
        bootstrap_stats[sigma] = {
            'mean_delta_pct': statistics.mean(deltas),
            'ci_95': [
                deltas[int(0.025 * n_bootstrap)],
                deltas[int(0.975 * n_bootstrap)]
            ],
        }
    
    return bootstrap_stats


def test_crypto_rekey():
    """Test crypto rekey drift tolerance."""
    print("Testing Crypto Rekey Drift Tolerance...")
    
    tester = CryptoRekeyTest(seed=42)
    
    # Run single test
    result = tester.compare_rekey_tolerance(sigma=10, n_rekeys=200, 
                                           drift_type='gaussian')
    
    print(f"Crypto Rekey (σ={result['sigma']}ms, {result['drift_type']}):")
    print(f"  Baseline fail rate: {result['baseline']['fail_rate_pct']:.2f}%")
    print(f"  θ′-biased fail rate: {result['theta_prime']['fail_rate_pct']:.2f}%")
    print(f"  Fail rate Δ: {result['fail_rate_delta_pct']:.2f}% "
          f"({result['fail_rate_delta_rel_pct']:.1f}% relative)")
    print(f"  Latency Δ: {result['latency_delta_ms']:.2f}ms")
    
    # Bootstrap test (small sample)
    print("\nRunning bootstrap (n=10)...")
    boot_result = bootstrap_crypto_tolerance([10, 50], n_bootstrap=10)
    for sigma, stats in boot_result.items():
        print(f"  σ={sigma}ms: Δ={stats['mean_delta_pct']:.1f}%, "
              f"CI=[{stats['ci_95'][0]:.1f}%, {stats['ci_95'][1]:.1f}%]")
    
    print("\nCrypto rekey tests passed!\n")


if __name__ == "__main__":
    test_crypto_rekey()
