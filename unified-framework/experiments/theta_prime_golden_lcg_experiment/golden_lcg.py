"""
Golden Ratio Linear Congruential Generator (LCG)
Deterministic 64-bit integer-based RNG using golden ratio constant.
Invariant #3: Deterministic φ w/o floats: 64-bit golden LCG G=0x9E3779B97F4A7C15
"""

class GoldenLCG:
    """64-bit Golden Ratio Linear Congruential Generator."""
    
    # Golden ratio constant (φ in 64-bit fixed point)
    GOLDEN_RATIO = 0x9E3779B97F4A7C15
    MODULUS = 2**64
    
    def __init__(self, seed=0):
        """Initialize golden LCG with seed."""
        self.seed = seed
        self.state = seed
    
    def next_u64(self):
        """Generate next 64-bit unsigned integer."""
        self.state = (self.state * self.GOLDEN_RATIO) % self.MODULUS
        return self.state
    
    def next_uniform(self):
        """Generate uniform random value in [0, 1)."""
        u64 = self.next_u64()
        # u = ((slot*G) mod 2^64)/2^64
        return u64 / self.MODULUS
    
    def next_range(self, low, high):
        """Generate random integer in [low, high)."""
        u = self.next_uniform()
        return int(low + u * (high - low))
    
    def shuffle_indices(self, n):
        """Generate shuffled indices 0..n-1 using golden LCG."""
        indices = list(range(n))
        # Fisher-Yates shuffle with golden LCG
        for i in range(n - 1, 0, -1):
            j = self.next_range(0, i + 1)
            indices[i], indices[j] = indices[j], indices[i]
        return indices


def test_golden_lcg():
    """Test golden LCG properties."""
    print("Testing Golden LCG...")
    
    # Test determinism
    lcg1 = GoldenLCG(seed=42)
    lcg2 = GoldenLCG(seed=42)
    
    vals1 = [lcg1.next_uniform() for _ in range(10)]
    vals2 = [lcg2.next_uniform() for _ in range(10)]
    
    assert vals1 == vals2, "Golden LCG should be deterministic"
    print("✓ Determinism verified")
    
    # Test range
    lcg = GoldenLCG(seed=123)
    uniforms = [lcg.next_uniform() for _ in range(1000)]
    assert all(0 <= u < 1.0 for u in uniforms), "Values should be in [0, 1)"
    print("✓ Range [0, 1) verified")
    
    # Test distribution (rough check)
    mean = sum(uniforms) / len(uniforms)
    assert 0.4 < mean < 0.6, f"Mean should be ~0.5, got {mean}"
    print(f"✓ Mean ≈ 0.5 (got {mean:.3f})")
    
    # Test shuffle
    lcg = GoldenLCG(seed=999)
    indices = lcg.shuffle_indices(20)
    assert sorted(indices) == list(range(20)), "Shuffle should preserve all indices"
    assert indices != list(range(20)), "Shuffle should reorder indices"
    print("✓ Shuffle verified")
    
    print("All Golden LCG tests passed!\n")


if __name__ == "__main__":
    test_golden_lcg()
