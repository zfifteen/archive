#!/usr/bin/env python3
"""
Focused test of Z5D pi estimation script for validation
"""
from z5d_pi_fast_integrated import load_zeros, benchmark_pk
import time

def run_focused_validation():
    """Run focused validation with key zero counts"""
    print("Z5D Pi Estimation Validation Test")
    print("=" * 50)
    
    # Load zeros
    zeros = load_zeros()
    print(f"Loaded {len(zeros)} zeta zeros")
    
    # Test representative zero counts: 1, 10, 20, 30, 50, 70, 99
    key_zero_counts = [1, 10, 20, 30, 50, 70, 99]
    
    print(f"\nRunning validation for max_zeros: {key_zero_counts}")
    print("Expected patterns:")
    print("- Relative errors should improve (get closer to 0)")
    print("- Timing should scale roughly linearly") 
    print("- Density enhancement ~194.8% for k=1000")
    print()
    
    start_time = time.time()
    benchmark_pk(zeros, max_zeros_range=key_zero_counts)
    total_time = time.time() - start_time
    
    print(f"\nTotal validation time: {total_time:.2f}s")
    print(f"Average per zero-count: {total_time/len(key_zero_counts):.2f}s")

if __name__ == "__main__":
    run_focused_validation()