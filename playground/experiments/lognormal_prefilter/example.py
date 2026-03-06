#!/usr/bin/env python3
"""
Example usage of the lognormal pre-filter factorization pipeline.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from model import create_default_model_store
from config import SearchPolicyConfig
from pipeline import factor_with_lognormal_prefilter


def main():
    """Demonstrate factorization of various semiprimes."""
    
    print("=" * 70)
    print("Lognormal Pre-Filter Factorization Pipeline - Example")
    print("=" * 70)
    print()
    
    # Create model and config
    model_store = create_default_model_store()
    config = SearchPolicyConfig(max_steps=10000, random_seed=42)
    
    # Test cases
    test_cases = [
        ("Small semiprime", 15),
        ("Medium semiprime", 10007 * 10009),
        ("Another medium", 10037 * 10039),
        ("Larger composite", 999983 * 999979),  # Two primes near 10^6
    ]
    
    print("Test Cases:")
    print("-" * 70)
    
    for description, N in test_cases:
        print(f"\n{description}: N = {N}")
        print(f"  sqrt(N) ≈ {int(N**0.5)}")
        
        factor = factor_with_lognormal_prefilter(N, model_store, config)
        
        if factor:
            other_factor = N // factor
            print(f"  ✓ Found factors: {factor} × {other_factor}")
            
            # Verify
            assert factor * other_factor == N
            print(f"  ✓ Verification: {factor} × {other_factor} = {N}")
        else:
            print(f"  ✗ Could not factor {N}")
    
    print()
    print("=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
