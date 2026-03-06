"""
θ′ (Theta-Prime) Biased Ordering Implementation
Implements mean-one cadence with bias parameter α, using golden LCG for determinism.

Invariant #2: Mean-one cadence: E[interval']=base; bias in [1−α,1+α], α≤0.2
Invariant #3: Deterministic φ w/o floats using golden LCG
"""

import math
from golden_lcg import GoldenLCG


class ThetaPrimeBias:
    """θ′-biased ordering with mean-one cadence."""
    
    def __init__(self, alpha=0.1, k=0.3, seed=42):
        """
        Initialize θ′ bias generator.
        
        Args:
            alpha: Bias parameter in [0, 0.2], controls deviation from mean
            k: Scaling parameter for θ′ function
            seed: Seed for golden LCG
        """
        assert 0 <= alpha <= 0.2, f"Alpha must be in [0, 0.2], got {alpha}"
        self.alpha = alpha
        self.k = k
        self.lcg = GoldenLCG(seed=seed)
    
    def theta_prime(self, n, k=None):
        """
        Compute θ′(n, k) - theta prime function.
        This is a placeholder geometric function that combines n and k.
        """
        if k is None:
            k = self.k
        # θ′(n,k) = geometric combination influenced by k
        # Using a simple formulation: weighted geometric mean
        return math.sqrt(n) * (1.0 + k * math.log(1 + n))
    
    def compute_bias_factor(self, slot):
        """
        Compute bias factor for a given slot using θ′ and golden LCG.
        Returns value in [1-α, 1+α] with mean 1.0.
        """
        # Generate deterministic pseudo-random value
        u = self.lcg.next_uniform()
        
        # Map u to bias range [1-α, 1+α]
        # Linear mapping: u ∈ [0,1) → bias ∈ [1-α, 1+α]
        bias = (1 - self.alpha) + u * (2 * self.alpha)
        
        # Clamp to ensure within bounds (should already be, but for safety)
        bias = max(1 - self.alpha, min(1 + self.alpha, bias))
        
        return bias
    
    def generate_biased_intervals(self, base_interval, n_intervals):
        """
        Generate n_intervals biased intervals with mean = base_interval.
        
        Args:
            base_interval: Base interval time (mean)
            n_intervals: Number of intervals to generate
            
        Returns:
            List of biased intervals with E[interval] ≈ base_interval
        """
        intervals = []
        for slot in range(n_intervals):
            bias = self.compute_bias_factor(slot)
            interval = base_interval * bias
            intervals.append(interval)
        
        return intervals
    
    def generate_biased_ordering(self, items):
        """
        Generate θ′-biased ordering of items using golden LCG.
        
        Args:
            items: List of items to order
            
        Returns:
            Reordered list based on θ′ bias
        """
        n = len(items)
        
        # Generate bias scores for each item
        bias_scores = []
        for i in range(n):
            theta = self.theta_prime(i + 1)  # θ′(n, k)
            u = self.lcg.next_uniform()
            # Combine θ′ with random perturbation scaled by α
            score = theta * (1 + self.alpha * (2 * u - 1))
            bias_scores.append(score)
        
        # Sort items by bias scores
        indexed_items = list(enumerate(items))
        sorted_items = sorted(indexed_items, key=lambda x: bias_scores[x[0]])
        
        return [item for idx, item in sorted_items]


def test_theta_prime_bias():
    """Test θ′ bias implementation."""
    print("Testing θ′-Biased Ordering...")
    
    # Test bias factor generation
    bias = ThetaPrimeBias(alpha=0.1, seed=42)
    factors = [bias.compute_bias_factor(i) for i in range(1000)]
    
    assert all(0.9 <= f <= 1.1 for f in factors), "Bias factors should be in [0.9, 1.1]"
    print(f"✓ Bias factors in [1-α, 1+α] range")
    
    # Test mean-one property
    mean_bias = sum(factors) / len(factors)
    assert 0.95 < mean_bias < 1.05, f"Mean bias should be ~1.0, got {mean_bias}"
    print(f"✓ Mean-one cadence verified (mean={mean_bias:.4f})")
    
    # Test interval generation
    base = 100.0
    intervals = bias.generate_biased_intervals(base, 1000)
    mean_interval = sum(intervals) / len(intervals)
    assert 95 < mean_interval < 105, f"Mean interval should be ~{base}, got {mean_interval}"
    print(f"✓ Mean interval ≈ base ({mean_interval:.2f} ≈ {base})")
    
    # Test ordering
    items = list(range(20))
    ordered = bias.generate_biased_ordering(items)
    assert sorted(ordered) == items, "Ordering should preserve all items"
    print(f"✓ Ordering preserves all items")
    
    # Test determinism
    bias1 = ThetaPrimeBias(alpha=0.1, seed=999)
    bias2 = ThetaPrimeBias(alpha=0.1, seed=999)
    
    items = list(range(10))
    order1 = bias1.generate_biased_ordering(items)
    order2 = bias2.generate_biased_ordering(items)
    assert order1 == order2, "Same seed should produce same ordering"
    print(f"✓ Deterministic ordering verified")
    
    print("All θ′ bias tests passed!\n")


if __name__ == "__main__":
    test_theta_prime_bias()
