#!/usr/bin/env python3
"""
Benchmark for Dynamic Comb Step (PR #217, Issue #211)

This script demonstrates the dynamic comb_step behavior and validates
that it provides scale-adaptive sampling density. Results are saved to results/.

The benchmark shows:
1. Dynamic comb_step scales with modulus size
2. Sampling density increases for larger moduli
3. The calculation is deterministic and reproducible

Usage:
    python scripts/bench_dynamic_comb_step.py
"""

import sys
import os
import math
from mpmath import mp
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from greens_function_factorization import find_crest_near_sqrt, RefinementConfig, _dynamic_comb_step

# Set precision
mp.dps = 512


def bench_dynamic_comb_step():
    """
    Benchmark dynamic comb_step across multiple scales.
    
    Demonstrates that:
    1. comb_step scales appropriately with modulus size
    2. Sampling density increases for larger moduli
    3. The calculation is deterministic and reproducible
    """
    print("=" * 80)
    print("Dynamic Comb Step Benchmark - Multi-Scale")
    print("=" * 80)
    print()
    
    test_scales = [
        ("64-bit", 2**64 - 59),
        ("128-bit", 2**128 - 159),
        ("256-bit", 2**256 - 189),
        ("512-bit", (2**256 - 189) * (2**256 - 317)),
    ]
    
    results_data = []
    
    for scale_name, N in test_scales:
        print(f"{scale_name} modulus:")
        print("-" * 80)
        print(f"  N bit length: {N.bit_length()}")
        
        # Calculate dynamic comb_step
        comb_step = _dynamic_comb_step(N)
        log2_N = mp.log(mp.mpf(N), 2)
        expected_step = mp.mpf(1) / (mp.mpf(10) * log2_N)
        
        # Sampling density = 1 / comb_step (samples per unit m)
        sampling_density = 1 / comb_step
        
        print(f"  log2(N): {float(log2_N):.2f}")
        print(f"  Dynamic comb_step: {float(comb_step):.10f}")
        print(f"  Expected (1 / (10 * log2(N))): {float(expected_step):.10f}")
        print(f"  Match: {abs(comb_step - expected_step) < mp.mpf('1e-10')}")
        print(f"  Sampling density (samples/unit): ~{float(sampling_density):.0f}")
        print(f"  Type: {type(comb_step)}")
        print()
        
        results_data.append({
            'scale': scale_name,
            'bit_length': N.bit_length(),
            'log2_N': float(log2_N),
            'comb_step': float(comb_step),
            'sampling_density': float(sampling_density),
        })
    
    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f"bench_dynamic_comb_step_{timestamp}.txt")
    
    with open(results_file, "w") as f:
        f.write("Dynamic Comb Step Benchmark Results\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Precision (mp.dps): {mp.dps}\n")
        f.write("\n")
        f.write("Results by Scale:\n")
        f.write("-" * 80 + "\n")
        for data in results_data:
            f.write(f"{data['scale']} ({data['bit_length']} bits):\n")
            f.write(f"  log2(N): {data['log2_N']:.2f}\n")
            f.write(f"  comb_step: {data['comb_step']:.10f}\n")
            f.write(f"  sampling_density: ~{data['sampling_density']:.0f} samples/unit\n")
            f.write("\n")
        
        f.write("\nValidation:\n")
        f.write("-" * 80 + "\n")
        # Check that sampling density increases with scale
        densities = [d['sampling_density'] for d in results_data]
        monotonic = all(densities[i] < densities[i+1] for i in range(len(densities)-1))
        f.write(f"Sampling density increases with scale: {monotonic}\n")
        f.write(f"All comb_steps are fractional (< 1): {all(d['comb_step'] < 1.0 for d in results_data)}\n")
    
    print("=" * 80)
    print(f"Results saved to: {results_file}")
    print("=" * 80)
    print()
    
    # Validation
    print("Validation:")
    print("-" * 80)
    densities = [d['sampling_density'] for d in results_data]
    monotonic = all(densities[i] < densities[i+1] for i in range(len(densities)-1))
    all_fractional = all(d['comb_step'] < 1.0 for d in results_data)
    
    if monotonic and all_fractional:
        print("✓ PASS: Sampling density increases with scale")
        print("✓ PASS: All comb_steps are fractional (< 1.0)")
        print()
        print("Dynamic comb_step behavior validated successfully.")
    else:
        print("✗ FAIL: Validation criteria not met")
    
    print("=" * 80)
    
    return monotonic and all_fractional


if __name__ == "__main__":
    success = bench_dynamic_comb_step()
    sys.exit(0 if success else 1)
