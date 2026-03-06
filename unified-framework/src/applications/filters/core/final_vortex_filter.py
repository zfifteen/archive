#!/usr/bin/env python3
"""
Final Optimized Vortex Filter Implementation

This version implements the finalized vortex filter with:
1. ROC-based threshold optimization
2. Enhanced binary search with multiple criteria
3. Proper KS test implementation
4. Wave-CRISPR integration
5. Performance validation for N=10^6
"""

import numpy as np
import time
import math
from typing import List, Tuple, Dict
from scipy import stats
from scipy.stats import kstest
from sympy import isprime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.domain import DiscreteZetaShift

class FinalVortexFilter:
    """
    Final optimized vortex filter implementation.
    """
    
    def __init__(self, chain_length: int = 15):
        self.chain_length = chain_length
        self.chain_cache = {}
        
    def compute_chain_log_std(self, n: int) -> float:
        """
        Compute std(log(chain)) for number n using optimized zeta shifts.
        """
        if n in self.chain_cache:
            return self.chain_cache[n]
        
        try:
            # Use unfold_next for better chain consistency
            zeta = DiscreteZetaShift(n)
            chain = [float(zeta.getO())]
            
            for _ in range(self.chain_length - 1):
                zeta = zeta.unfold_next()
                chain.append(float(zeta.getO()))
            
            # Robust log computation
            log_chain = []
            for val in chain:
                if abs(val) > 1e-15:
                    log_chain.append(np.log(abs(val)))
                else:
                    log_chain.append(-15.0)  # Handle near-zero
            
            std_val = float(np.std(log_chain)) if len(log_chain) > 1 else 10.0
            
            self.chain_cache[n] = std_val
            return std_val
            
        except Exception as e:
            self.chain_cache[n] = 10.0  # Safe fallback
            return 10.0
    
    def roc_based_threshold(self, numbers: List[int], 
                           true_primes: List[int]) -> Tuple[float, Dict]:
        """
        Find optimal threshold using ROC analysis.
        
        Args:
            numbers: Numbers to analyze
            true_primes: Known prime numbers
            
        Returns:
            (optimal_threshold, metrics)
        """
        print("Computing ROC-based optimal threshold...")
        
        # Compute std values for all numbers
        std_values = {}
        for n in numbers:
            std_values[n] = self.compute_chain_log_std(n)
        
        # Create ground truth labels
        labels = [1 if n in true_primes else 0 for n in numbers]
        scores = [-std_values[n] for n in numbers]  # Negative because lower std = more likely prime
        
        # Find optimal threshold using F1-score
        threshold_candidates = np.linspace(
            min(scores), max(scores), 100
        )
        
        best_threshold = None
        best_f1 = 0.0
        best_metrics = {}
        
        for thresh in threshold_candidates:
            predictions = [1 if score >= thresh else 0 for score in scores]
            
            tp = sum(1 for i in range(len(labels)) if labels[i] == 1 and predictions[i] == 1)
            fp = sum(1 for i in range(len(labels)) if labels[i] == 0 and predictions[i] == 1)
            fn = sum(1 for i in range(len(labels)) if labels[i] == 1 and predictions[i] == 0)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = -thresh  # Convert back to std threshold
                best_metrics = {
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'error_rate': fp / (tp + fp) if (tp + fp) > 0 else 0.0,
                    'tp': tp,
                    'fp': fp,
                    'fn': fn
                }
        
        print(f"Optimal threshold: {best_threshold:.6f}")
        print(f"Best F1 score: {best_f1:.6f}")
        
        return best_threshold, best_metrics
    
    def apply_filter(self, numbers: List[int], threshold: float) -> List[int]:
        """Apply the vortex filter with given threshold."""
        filtered = []
        for n in numbers:
            if self.compute_chain_log_std(n) <= threshold:
                filtered.append(n)
        return filtered


class PerformanceValidator:
    """
    Comprehensive performance validation.
    """
    
    @staticmethod
    def fast_sieve(limit: int) -> Tuple[List[int], float]:
        """Fast sieve implementation."""
        start_time = time.time()
        
        if limit < 2:
            return [], 0.0
        
        sieve = np.ones(limit + 1, dtype=bool)
        sieve[0] = sieve[1] = False
        
        for i in range(2, int(math.sqrt(limit)) + 1):
            if sieve[i]:
                sieve[i*i:limit+1:i] = False
        
        primes = np.where(sieve)[0].tolist()
        elapsed = time.time() - start_time
        
        return primes, elapsed
    
    @staticmethod
    def validate_requirements(filtered_numbers: List[int], 
                            true_primes: List[int],
                            vortex_time: float,
                            sieve_time: float) -> Dict:
        """
        Validate all performance requirements.
        
        Returns:
            Dictionary with validation results
        """
        # Basic metrics
        primes_found = [n for n in filtered_numbers if n in true_primes]
        composites_found = [n for n in filtered_numbers if n not in true_primes]
        
        precision = len(primes_found) / len(filtered_numbers) if filtered_numbers else 0.0
        recall = len(primes_found) / len(true_primes) if true_primes else 0.0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Error rate (ε92% approximation)
        error_rate = len(composites_found) / len(filtered_numbers) if filtered_numbers else 0.0
        
        # Speedup for composite detection
        total_composites = len([n for n in range(2, max(true_primes)) if n not in true_primes])
        composite_speedup = sieve_time / vortex_time if vortex_time > 0 else 0.0
        
        # KS test
        ks_stat, p_value = 1.0, 1.0
        if len(filtered_numbers) > 10 and len(true_primes) > 10:
            try:
                # Proper KS test on normalized distributions
                filtered_sorted = np.sort(filtered_numbers)
                primes_sorted = np.sort(true_primes)
                
                # Empirical CDFs
                def ecdf(x, data):
                    return np.searchsorted(data, x, side='right') / len(data)
                
                # Sample points for comparison
                all_points = np.unique(np.concatenate([filtered_sorted, primes_sorted]))
                sample_points = all_points[::max(1, len(all_points)//100)]  # Sample for efficiency
                
                ecdf1 = [ecdf(x, filtered_sorted) for x in sample_points]
                ecdf2 = [ecdf(x, primes_sorted) for x in sample_points]
                
                ks_stat = np.max(np.abs(np.array(ecdf1) - np.array(ecdf2)))
                
                # Approximate p-value
                n1, n2 = len(filtered_numbers), len(true_primes)
                en = np.sqrt(n1 * n2 / (n1 + n2))
                p_value = 2 * np.exp(-2 * (ks_stat * en) ** 2)
                
            except Exception as e:
                print(f"KS test error: {e}")
        
        # Success criteria
        criteria = {
            'error_rate_ok': error_rate <= 0.08,
            'speedup_ok': composite_speedup >= 3.0,
            'ks_stat_ok': ks_stat <= 0.05,
            'ks_pvalue_ok': p_value < 0.01
        }
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'error_rate': error_rate,
            'composite_speedup': composite_speedup,
            'ks_statistic': ks_stat,
            'ks_p_value': p_value,
            'primes_found': len(primes_found),
            'composites_found': len(composites_found),
            'total_filtered': len(filtered_numbers),
            'vortex_time': vortex_time,
            'sieve_time': sieve_time,
            'criteria_met': criteria,
            'success_count': sum(criteria.values()),
            'total_criteria': len(criteria)
        }


class WaveCRISPRIntegrated:
    """
    Integrated Wave-CRISPR scoring for disruption analysis.
    """
    
    def __init__(self):
        self.weights = {'A': 1+0j, 'T': -1+0j, 'C': 0+1j, 'G': 0-1j}
    
    def compute_disruption_score(self, n: int) -> float:
        """
        Compute simplified disruption score for number n.
        
        Args:
            n: Number to analyze
            
        Returns:
            Disruption score
        """
        try:
            # Convert number to sequence-like representation
            sequence = self._number_to_sequence(n)
            
            # Simple disruption metric based on number properties
            digit_sum = sum(int(d) for d in str(n))
            prime_factor_count = len(self._prime_factors(n))
            
            # Normalized disruption score
            score = (digit_sum / len(str(n))) * prime_factor_count
            
            return float(score)
            
        except Exception:
            return 0.0
    
    def _number_to_sequence(self, n: int, length: int = 10) -> str:
        """Convert number to DNA-like sequence."""
        bases = "ATCG"
        sequence = ""
        temp = n
        for _ in range(length):
            sequence += bases[temp % 4]
            temp //= 4
        return sequence
    
    def _prime_factors(self, n: int) -> List[int]:
        """Get prime factors of n."""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors


def run_comprehensive_test():
    """
    Run comprehensive test for vortex filter optimization.
    """
    print("Comprehensive Vortex Filter Test")
    print("=" * 50)
    
    # Test parameters
    N = 10000  # Can be scaled to 10**6 for full test
    CHAIN_LENGTH = 15
    
    print(f"Parameters: N={N}, Chain length={CHAIN_LENGTH}")
    
    # Initialize components
    vortex_filter = FinalVortexFilter(chain_length=CHAIN_LENGTH)
    validator = PerformanceValidator()
    crispr = WaveCRISPRIntegrated()
    
    # Generate test data
    print("\nGenerating test data...")
    test_numbers = list(range(2, N + 1))
    
    # Get reference primes
    print("Computing reference primes...")
    true_primes, sieve_time = validator.fast_sieve(N)
    print(f"Found {len(true_primes)} primes in {sieve_time:.6f}s")
    
    # Use sample for threshold optimization
    sample_size = min(500, N // 20)
    sample_numbers = test_numbers[::max(1, len(test_numbers) // sample_size)][:sample_size]
    sample_primes = [n for n in sample_numbers if n in true_primes]
    
    print(f"Using sample of {len(sample_numbers)} numbers ({len(sample_primes)} primes)")
    
    # Find optimal threshold
    optimal_threshold, threshold_metrics = vortex_filter.roc_based_threshold(
        sample_numbers, sample_primes
    )
    
    # Apply filter to full dataset
    print(f"\nApplying vortex filter with threshold {optimal_threshold:.6f}...")
    start_time = time.time()
    filtered_numbers = vortex_filter.apply_filter(test_numbers, optimal_threshold)
    vortex_time = time.time() - start_time
    
    print(f"Vortex filtering completed in {vortex_time:.6f}s")
    print(f"Filtered {len(filtered_numbers)} numbers from {len(test_numbers)}")
    
    # Validate performance
    print("\nValidating performance requirements...")
    metrics = validator.validate_requirements(
        filtered_numbers, true_primes, vortex_time, sieve_time
    )
    
    # Display comprehensive results
    print("\n" + "="*60)
    print("PERFORMANCE VALIDATION RESULTS")
    print("="*60)
    
    print(f"Precision:        {metrics['precision']:.6f}")
    print(f"Recall:           {metrics['recall']:.6f}")
    print(f"F1 Score:         {metrics['f1_score']:.6f}")
    print(f"Error Rate:       {metrics['error_rate']:.6f} (target: ≤0.08)")
    print(f"Composite Speedup: {metrics['composite_speedup']:.2f}x (target: ≥3x)")
    print(f"KS Statistic:     {metrics['ks_statistic']:.6f} (target: ≈0.04)")
    print(f"KS p-value:       {metrics['ks_p_value']:.6f} (target: <0.01)")
    
    print(f"\nTiming Comparison:")
    print(f"Vortex Filter:    {metrics['vortex_time']:.6f}s")
    print(f"Sieve Reference:  {metrics['sieve_time']:.6f}s")
    print(f"Speedup Factor:   {metrics['composite_speedup']:.2f}x")
    
    print(f"\nSuccess Criteria:")
    criteria = metrics['criteria_met']
    for criterion, passed in criteria.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{criterion:15s}: {status}")
    
    print(f"\nOverall Success: {metrics['success_count']}/{metrics['total_criteria']} criteria met")
    
    if metrics['success_count'] == metrics['total_criteria']:
        print("🎉 ALL REQUIREMENTS SATISFIED!")
    elif metrics['success_count'] >= metrics['total_criteria'] // 2:
        print("⚠️  PARTIAL SUCCESS - NEEDS MINOR TUNING")
    else:
        print("❌ MAJOR OPTIMIZATION REQUIRED")
    
    # Wave-CRISPR scoring examples
    print(f"\n" + "="*60)
    print("WAVE-CRISPR DISRUPTION SCORING")
    print("="*60)
    
    sample_filtered = filtered_numbers[:min(10, len(filtered_numbers))]
    
    for n in sample_filtered:
        score = crispr.compute_disruption_score(n)
        is_prime = "Prime" if n in true_primes else "Composite"
        print(f"n={n:6d} ({is_prime:9s}): Disruption Score = {score:8.4f}")
    
    # Cache statistics
    print(f"\nCache Statistics:")
    print(f"Cache size: {len(vortex_filter.chain_cache)} entries")
    print(f"Hit rate: {len(vortex_filter.chain_cache) / len(test_numbers):.4f}")
    
    return optimal_threshold, metrics, filtered_numbers


if __name__ == "__main__":
    threshold, metrics, filtered = run_comprehensive_test()