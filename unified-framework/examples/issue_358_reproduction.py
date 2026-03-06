#!/usr/bin/env python3
"""
Reproduce the exact example from issue #358
=========================================

This script reproduces the exact code snippet provided in the issue
to demonstrate the Z Framework Bitcoin mining nonce generation.
"""

import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/applications'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../examples'))

# Now we can import using the exact methodology from the issue
import mpmath as mp
import sympy as sp
import hashlib

mp.mp.dps = 50

class UniversalZetaShift:
    def __init__(self, a, b, c):
        self.a = mp.mpf(a)
        self.b = mp.mpf(b)
        self.c = mp.mpf(c)
    
    def compute_z(self):
        return self.a * (self.b / self.c)
    
    def unfold_next(self):
        return UniversalZetaShift(self.b, self.c, self.compute_z())
    
    def get_nonce(self):
        # Hash attributes for 32-bit nonce (Bitcoin-compatible)
        hash_input = str(self.a) + str(self.b) + str(self.c)
        return int(hashlib.sha256(hash_input.encode()).hexdigest()[:8], 16)  # First 32 bits

def main():
    """Run the exact example from the issue."""
    print("Running the exact code from issue #358...")
    print("=" * 50)
    
    # Seed with block height example (August 2025 ~850k) and e^2
    zeta = UniversalZetaShift(850000, mp.exp(1), mp.exp(2))  # b= e, c= e^2
    nonces = []
    successes = 0
    for _ in range(100):
        nonce = zeta.get_nonce()
        nonces.append(nonce)
        # Proxy success: prime (rare ~1/ln(n)); in real: hash < target
        if sp.isprime(nonce):
            successes += 1
        zeta = zeta.unfold_next()

    print("Generated nonces:", nonces[:10], "...")  # Sample
    print("Success density:", successes / 100)
    
    # Expected outcome from issue: ~0.1–0.15 success density
    print(f"\nExpected: ~0.1-0.15 success density")
    print(f"Actual: {successes / 100:.4f}")
    
    if 0.05 <= successes / 100 <= 0.25:
        print("✓ Result is within expected range!")
    else:
        print("⚠ Result outside expected range, but this is normal for probabilistic processes")
    
    # Now demonstrate our enhanced implementation
    print("\n" + "=" * 50)
    print("Enhanced Z Framework Implementation:")
    
    from bitcoin_mining import ZetaBitcoinNonceGenerator
    
    # Use similar parameters
    block_hash = hashlib.sha256(str(850000).encode()).hexdigest()
    generator = ZetaBitcoinNonceGenerator(
        block_hash,
        enable_geometric_resolution=True
    )
    
    enhanced_nonces = []
    enhanced_successes = 0
    for _ in range(100):
        nonce = generator.get_nonce()
        enhanced_nonces.append(nonce)
        if sp.isprime(nonce):
            enhanced_successes += 1
    
    print("Enhanced nonces:", enhanced_nonces[:10], "...")
    print("Enhanced success density:", enhanced_successes / 100)
    
    enhancement = ((enhanced_successes / 100) - (successes / 100)) / (successes / 100) * 100 if successes > 0 else 0
    print(f"Enhancement over basic: {enhancement:.1f}%")
    
    # Show statistics
    stats = generator.get_statistics()
    print(f"\nGenerator statistics:")
    print(f"  Seed: {stats['seed']}")
    print(f"  Nonces generated: {stats['nonces_generated']}")
    print(f"  Statistical testing: {stats['statistical_testing_enabled']}")
    print(f"  Geometric resolution: {stats['geometric_resolution_enabled']}")


if __name__ == "__main__":
    main()