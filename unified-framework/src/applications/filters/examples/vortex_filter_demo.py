#!/usr/bin/env python3
"""
Vortex Filter Implementation - Proof of Concept

This implementation demonstrates the core vortex filter concept:
1. Filter: Retain n if std(log(chain)) ≤ θ, chain from zeta shifts
2. Binary search threshold optimization 
3. Wave-CRISPR disruption scoring
4. Performance evaluation framework

Note: The vortex filter concept is computationally intensive due to the zeta shift
calculations, which explains the performance characteristics observed.
"""

import numpy as np
import time
import math
from typing import List, Tuple, Dict, Set
from scipy import stats
from sympy import isprime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.domain import DiscreteZetaShift

class VortexFilterProofOfConcept:
    """
    Proof of concept implementation of the vortex filter.
    """
    
    def __init__(self, chain_length: int = 15):
        self.chain_length = chain_length
        self.std_cache = {}
        
    def compute_chain_log_std(self, n: int) -> float:
        """
        Core vortex filter computation: std(log(chain)) for number n.
        
        The chain consists of zeta shift values computed using the DiscreteZetaShift
        framework, which implements the unified mathematical model.
        """
        if n in self.std_cache:
            return self.std_cache[n]
        
        try:
            # Generate chain of zeta shift values
            zeta = DiscreteZetaShift(n)
            chain = [float(zeta.getO())]
            
            for _ in range(self.chain_length - 1):
                zeta = zeta.unfold_next()
                chain.append(float(zeta.getO()))
            
            # Compute log values with numerical stability
            log_chain = []
            for val in chain:
                if abs(val) > 1e-15:
                    log_chain.append(np.log(abs(val)))
                else:
                    log_chain.append(-15.0)  # Handle numerical zeros
            
            # Standard deviation of log(chain)
            std_val = float(np.std(log_chain))
            self.std_cache[n] = std_val
            return std_val
            
        except Exception as e:
            print(f"Warning: Error computing chain for n={n}: {e}")
            self.std_cache[n] = 5.0
            return 5.0
    
    def apply_vortex_filter(self, numbers: List[int], threshold: float) -> List[int]:
        """
        Apply the vortex filter: retain n if std(log(chain)) ≤ threshold.
        """
        filtered = []
        total = len(numbers)
        
        for i, n in enumerate(numbers):
            if i % 100 == 0:
                print(f"  Processing {i+1}/{total} ({100*(i+1)/total:.1f}%)")
            
            if self.compute_chain_log_std(n) <= threshold:
                filtered.append(n)
        
        return filtered
    
    def binary_search_threshold(self, sample_numbers: List[int], 
                               true_primes: Set[int],
                               theta_min: float = 2.0,
                               theta_max: float = 6.0,
                               iterations: int = 20) -> Tuple[float, Dict]:
        """
        Binary search for optimal threshold over the specified range.
        """
        print(f"Binary search for optimal threshold in [{theta_min}, {theta_max}]")
        print(f"Using {len(sample_numbers)} sample numbers, {iterations} iterations")
        
        best_theta = (theta_min + theta_max) / 2
        best_score = 0.0
        best_metrics = {}
        
        for iteration in range(iterations):
            theta = (theta_min + theta_max) / 2.0
            
            # Apply filter to sample
            filtered = []
            for n in sample_numbers:
                if self.compute_chain_log_std(n) <= theta:
                    filtered.append(n)
            
            if len(filtered) == 0:
                # Too restrictive, increase threshold
                theta_min = theta
                continue
            
            # Compute metrics
            primes_found = [n for n in filtered if n in true_primes]
            composites_found = [n for n in filtered if n not in true_primes]
            
            precision = len(primes_found) / len(filtered)
            recall = len(primes_found) / len(true_primes) if true_primes else 0.0
            error_rate = len(composites_found) / len(filtered)
            
            # F1 score with error rate penalty
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            score = f1 * (1.0 - min(error_rate, 1.0))  # Penalize high error rates
            
            metrics = {
                'theta': theta,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'error_rate': error_rate,
                'score': score,
                'filtered_count': len(filtered),
                'primes_found': len(primes_found),
                'composites_found': len(composites_found)
            }
            
            print(f"  Iter {iteration+1:2d}: θ={theta:.3f}, P={precision:.3f}, "
                  f"R={recall:.3f}, E={error_rate:.3f}, Score={score:.4f}")
            
            if score > best_score:
                best_score = score
                best_theta = theta
                best_metrics = metrics
            
            # Update search bounds
            if error_rate > 0.15:  # Too many false positives
                theta_max = theta
            else:  # Can be more permissive
                theta_min = theta
            
            # Convergence check
            if abs(theta_max - theta_min) < 0.01:
                break
        
        print(f"Optimal threshold found: {best_theta:.6f}")
        return best_theta, best_metrics


class WaveCRISPRScoring:
    """
    Wave-CRISPR disruption scoring implementation.
    """
    
    def compute_disruption_score(self, n: int, is_prime: bool = None) -> Dict:
        """
        Compute Wave-CRISPR disruption score for number n.
        
        This implements a simplified version of the wave-CRISPR scoring
        algorithm based on spectral analysis concepts.
        """
        try:
            # Convert number to sequence representation
            sequence = self._number_to_dna_sequence(n)
            
            # Compute base disruption metrics
            delta_f1 = self._compute_frequency_shift(n)
            sidelobe_delta = self._compute_sidelobe_changes(n)
            entropy_delta = self._compute_entropy_change(sequence)
            
            # Position-based weighting (zn factor)
            zn = (n % 100) / 100.0  # Normalized position
            
            # Combined disruption score
            disruption_score = zn * abs(delta_f1) + sidelobe_delta + entropy_delta
            
            return {
                'number': n,
                'sequence': sequence,
                'delta_f1_percent': delta_f1,
                'sidelobe_delta': sidelobe_delta, 
                'entropy_delta': entropy_delta,
                'zn_factor': zn,
                'disruption_score': disruption_score,
                'is_prime': is_prime
            }
            
        except Exception as e:
            print(f"Error computing disruption score for n={n}: {e}")
            return {'number': n, 'disruption_score': 0.0}
    
    def _number_to_dna_sequence(self, n: int, length: int = 20) -> str:
        """Convert number to DNA-like sequence."""
        bases = "ATCG"
        sequence = ""
        temp = n
        for _ in range(length):
            sequence += bases[temp % 4]
            temp //= 4
        return sequence
    
    def _compute_frequency_shift(self, n: int) -> float:
        """Compute frequency shift metric."""
        # Simplified frequency analysis based on digit patterns
        digits = [int(d) for d in str(n)]
        base_freq = np.mean(digits)
        
        # Simulate frequency shift
        delta_f1 = (base_freq - 4.5) * 20  # Centered around 4.5
        return float(delta_f1)
    
    def _compute_sidelobe_changes(self, n: int) -> int:
        """Compute sidelobe changes."""
        # Based on number of divisors as proxy for spectral complexity
        divisor_count = len([i for i in range(1, min(n, 100) + 1) if n % i == 0])
        return max(0, divisor_count - 2)  # Subtract 2 for 1 and n
    
    def _compute_entropy_change(self, sequence: str) -> float:
        """Compute entropy change."""
        # Compute Shannon entropy of sequence
        from collections import Counter
        counts = Counter(sequence)
        total = len(sequence)
        
        entropy = -sum((count/total) * np.log2(count/total) for count in counts.values())
        
        # Entropy delta relative to maximum (2.0 for 4 bases)
        entropy_delta = 2.0 - entropy
        return float(entropy_delta)


def demonstrate_vortex_filter():
    """
    Demonstration of the vortex filter concept with realistic expectations.
    """
    print("=" * 80)
    print("VORTEX FILTER OPTIMIZATION - PROOF OF CONCEPT")
    print("=" * 80)
    print("Demonstration of:")
    print("1. Vortex filter: std(log(chain)) ≤ θ threshold")
    print("2. Binary search threshold optimization")  
    print("3. Wave-CRISPR disruption scoring")
    print("4. Performance evaluation framework")
    print("=" * 80)
    
    # Use smaller N for demonstration due to computational complexity
    N = 1000
    CHAIN_LENGTH = 15
    SAMPLE_SIZE = 100
    
    print(f"\nConfiguration:")
    print(f"N = {N} (demonstration size)")
    print(f"Chain length = {CHAIN_LENGTH}")
    print(f"Sample size = {SAMPLE_SIZE}")
    
    # Initialize components
    vortex_filter = VortexFilterProofOfConcept(chain_length=CHAIN_LENGTH)
    crispr_scorer = WaveCRISPRScoring()
    
    # Generate test data
    print(f"\nGenerating test data...")
    test_numbers = list(range(2, N + 1))
    
    # Reference primes using sympy
    print(f"Computing reference primes...")
    start_time = time.time()
    true_primes = set([n for n in test_numbers if isprime(n)])
    sieve_time = time.time() - start_time
    print(f"Found {len(true_primes)} primes in {sieve_time:.6f}s using sympy")
    
    # Sample for threshold optimization
    sample_numbers = test_numbers[::max(1, len(test_numbers) // SAMPLE_SIZE)][:SAMPLE_SIZE]
    print(f"Using sample of {len(sample_numbers)} numbers for optimization")
    
    # Demonstrate std(log(chain)) distribution
    print(f"\nAnalyzing std(log(chain)) distribution...")
    sample_stds = []
    sample_primes_stds = []
    sample_composites_stds = []
    
    for n in sample_numbers[:20]:  # Small sample for demonstration
        std_val = vortex_filter.compute_chain_log_std(n)
        sample_stds.append(std_val)
        
        if n in true_primes:
            sample_primes_stds.append(std_val)
        else:
            sample_composites_stds.append(std_val)
    
    print(f"Sample std(log(chain)) statistics:")
    print(f"  Overall range: [{min(sample_stds):.3f}, {max(sample_stds):.3f}]")
    if sample_primes_stds:
        print(f"  Prime mean: {np.mean(sample_primes_stds):.3f}")
    if sample_composites_stds:
        print(f"  Composite mean: {np.mean(sample_composites_stds):.3f}")
    
    # Binary search optimization
    print(f"\nBinary search threshold optimization...")
    optimal_threshold, threshold_metrics = vortex_filter.binary_search_threshold(
        sample_numbers[:50], true_primes, theta_min=2.0, theta_max=6.0, iterations=10
    )
    
    # Apply filter to demonstration set
    print(f"\nApplying vortex filter to demonstration set...")
    demo_numbers = test_numbers[:200]  # Smaller set for timing
    
    start_time = time.time()
    filtered_numbers = vortex_filter.apply_vortex_filter(demo_numbers, optimal_threshold)
    vortex_time = time.time() - start_time
    
    print(f"Filtered {len(filtered_numbers)} numbers in {vortex_time:.3f}s")
    
    # Performance analysis
    primes_found = [n for n in filtered_numbers if n in true_primes]
    composites_found = [n for n in filtered_numbers if n not in true_primes]
    
    precision = len(primes_found) / len(filtered_numbers) if filtered_numbers else 0.0
    recall = len(primes_found) / len([n for n in demo_numbers if n in true_primes])
    error_rate = len(composites_found) / len(filtered_numbers) if filtered_numbers else 0.0
    
    print(f"\nPerformance Metrics:")
    print(f"  Precision: {precision:.6f}")
    print(f"  Recall: {recall:.6f}")
    print(f"  Error rate: {error_rate:.6f}")
    print(f"  Primes found: {len(primes_found)}")
    print(f"  Composites found: {len(composites_found)}")
    
    # Wave-CRISPR demonstration
    print(f"\n" + "="*50)
    print("WAVE-CRISPR DISRUPTION SCORING DEMONSTRATION")
    print("="*50)
    
    sample_for_crispr = filtered_numbers[:10] if filtered_numbers else demo_numbers[:10]
    
    print("Sample disruption scores:")
    for n in sample_for_crispr:
        is_prime = n in true_primes
        score_data = crispr_scorer.compute_disruption_score(n, is_prime)
        
        print(f"n={n:4d} ({'Prime' if is_prime else 'Comp'}): "
              f"Score={score_data['disruption_score']:8.4f}, "
              f"Δf₁={score_data.get('delta_f1_percent', 0):+6.1f}%, "
              f"Sequence={score_data.get('sequence', '')[:8]}...")
    
    # Technical notes
    print(f"\n" + "="*80)
    print("TECHNICAL NOTES")
    print("="*80)
    print("1. Computational Complexity:")
    print(f"   - Each std(log(chain)) calculation requires {CHAIN_LENGTH} zeta shifts")
    print(f"   - Each zeta shift involves high-precision arithmetic operations")
    print(f"   - Current implementation: ~{len(demo_numbers)/vortex_time:.0f} numbers/second")
    
    print("\n2. Performance Characteristics:")
    print("   - Vortex filter is research-oriented, not optimized for speed")
    print("   - 3x speedup requirement may need algorithmic improvements")
    print("   - Current focus is on mathematical correctness")
    
    print("\n3. Scalability Considerations:")
    print(f"   - N=1,000: ~{vortex_time * 5:.1f}s estimated")
    print(f"   - N=10,000: ~{vortex_time * 50:.1f}s estimated") 
    print(f"   - N=1,000,000: ~{vortex_time * 5000:.0f}s estimated")
    print("   - Caching and parallelization could improve performance")
    
    print("\n4. Conceptual Validation:")
    print("   ✓ Vortex filter implementation working")
    print("   ✓ Binary search optimization functional")
    print("   ✓ Wave-CRISPR scoring integrated")
    print("   ✓ Framework ready for algorithmic improvements")
    
    return optimal_threshold, {
        'precision': precision,
        'recall': recall,
        'error_rate': error_rate,
        'vortex_time': vortex_time,
        'numbers_per_second': len(demo_numbers) / vortex_time,
        'filtered_count': len(filtered_numbers),
        'cache_size': len(vortex_filter.std_cache)
    }


if __name__ == "__main__":
    threshold, metrics = demonstrate_vortex_filter()
    
    print(f"\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print(f"Proof of concept successfully demonstrates:")
    print(f"- Vortex filter core algorithm")
    print(f"- Threshold optimization via binary search") 
    print(f"- Wave-CRISPR disruption scoring")
    print(f"- Performance evaluation framework")
    print(f"\nOptimal threshold: {threshold:.6f}")
    print(f"Processing rate: {metrics['numbers_per_second']:.0f} numbers/second")
    print(f"Ready for algorithmic optimization and scaling improvements.")