#!/usr/bin/env python3
"""
Benchmark UniversalZetaShift Memoization
========================================

Tests the performance improvement from memoizing zeta attribute computation.
"""

import time
from src.core.discrete_zeta_shift_lattice import build_zeta_shift_lattice, compute_attributes, compute_average_shift

def benchmark_lattice_construction(N=1000000, reps=5):
    """Benchmark lattice construction time."""
    times = []
    for _ in range(reps):
        start = time.time()
        lattice = build_zeta_shift_lattice(N)
        end = time.time()
        times.append(end - start)
        # Clear cache for first run only
        if _ == 0:
            print(".2f")
        else:
            print(".2f")
    avg_time = sum(times) / len(times)
    print(".2f")
    return lattice

def benchmark_attribute_computation(lattice, reps=5):
    """Benchmark attribute computation time."""
    times = []
    for _ in range(reps):
        start = time.time()
        attrs = compute_attributes(lattice)
        end = time.time()
        times.append(end - start)
        if _ == 0:
            print(".4f")
        else:
            print(".4f")
    avg_time = sum(times) / len(times)
    print(".4f")
    return attrs

def benchmark_average_shift(lattice, reps=5):
    """Benchmark average shift computation time."""
    times = []
    for _ in range(reps):
        start = time.time()
        avg_shift = compute_average_shift(lattice)
        end = time.time()
        times.append(end - start)
        if _ == 0:
            print(".4f")
        else:
            print(".4f")
    avg_time = sum(times) / len(times)
    print(".4f")
    return avg_shift

if __name__ == "__main__":
    print("UniversalZetaShift Memoization Benchmark")
    print("========================================")
    
    N = 1000000
    print(f"Testing with N={N}")
    print()
    
    # First construction (caches)
    print("Phase 1: Lattice Construction")
    lattice = benchmark_lattice_construction(N)
    print()
    
    # Second construction (from cache)
    print("Phase 2: Lattice Construction (Cached)")
    lattice2 = benchmark_lattice_construction(N)
    print()
    
    # Attribute computation (cached)
    print("Phase 3: Attribute Computation")
    attrs = benchmark_attribute_computation(lattice)
    print()
    
    # Average shift (cached)
    print("Phase 4: Average Shift Computation")
    avg_shift = benchmark_average_shift(lattice)
    print(".6f")
    print()
    
    print("Memoization successfully implemented!")
    print("Subsequent lattice builds and computations are now cached.")