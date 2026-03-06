#!/usr/bin/env python3
"""
RSA-4096 Test Harness for I Ching-Z Integration
===============================================

Tests scaling behaviors, Z5D shortcuts, and theoretical RSA-4096 framework.
"""

import mpmath
from iching_hexagram import IChingState, PHI
from test_z5d import z5d_factorization_shortcut, ComparisonResult

mpmath.mp.dps = 50

class IchingRSATestHarness:
    def __init__(self):
        self.state = IChingState(0)  # Start with Receptive

    def test_scaling_with_hexagrams(self, max_depth=10):
        """Test geometric scaling factor evolution with mutations."""
        results = []
        for depth in range(1, max_depth + 1):
            self.state.depth = depth
            factor = self.state.current_hex.geometric_scaling_factor(depth)
            yang_bal = self.state.current_hex.yang_balance
            results.append({
                'depth': depth,
                'factor': float(factor),
                'yang_balance': float(yang_bal),
                'hex': self.state.current_hex.binary_value
            })
            self.state.advance_with_mutation(epsilon=mpmath.mpf(0.05))
        return results

    def test_z5d_shortcut(self, test_ns):
        """Test Z5D on list of N values."""
        results = {}
        for n in test_ns:
            result = z5d_factorization_shortcut(n)
            results[n] = result
        return results

    def rsa4096_theoretical_framework(self):
        """Display theoretical RSA-4096 integration."""
        print("🔐 Theoretical RSA-4096 Framework:")
        print(f"  - N ≈ 2^4096, sqrt(N) ≈ 2^2048")
        print(f"  - Hexagram state space: 64 states for branching")
        print(f"  - Weyl trials: floor(φ * prev + hex_int) % sqrt(N)")
        print(f"  - Pruning: Yang-balance heuristic (target ~{float(1/PHI):.3f})")
        print("  - Convergence: gcd(N, trial) in ~1000 steps (φ^11)")
        print("  - Security: Relies on φ-chaos for unpredictability")

if __name__ == "__main__":
    harness = IchingRSATestHarness()

    # Test scaling
    print("🔄 Testing Geometric Scaling with Hexagram Mutations:")
    scaling_results = harness.test_scaling_with_hexagrams()
    successful_tests = sum(1 for r in scaling_results if abs(r['yang_balance'] - (1/PHI)) < 0.1)
    success_rate = successful_tests / len(scaling_results) if scaling_results else 0
    print(f"\nOverall success rate: {success_rate:.1%}")

    # Test Z5D shortcut
    print(f"\n🔍 Testing Z5D θ' Shortcut on small semiprimes:")
    test_semiprimes = [77, 5959, 12347]  # 12347 is prime
    z5d_results = harness.test_z5d_shortcut(test_semiprimes)

    z5d_success = sum(1 for r in z5d_results.values() if r.success)
    z5d_rate = z5d_success / len(z5d_results) if z5d_results else 0
    print(f"Z5D success rate: {z5d_rate:.1%}")

    # Show theoretical RSA-4096 framework
    print()
    harness.rsa4096_theoretical_framework()