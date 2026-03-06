#!/usr/bin/env python3
"""
Z5D Prime Predictor - Benchmark Comparison

Compares Z5D predictor performance against traditional methods:
- Trial division
- sympy.prime() 
- Direct prime computation

Shows the speed vs accuracy tradeoff of the Z5D approach.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from z5d import predict_prime, benchmark_prediction
import time

# Try importing sympy for comparison
try:
    from sympy import prime as sympy_prime
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False
    print("Note: sympy not available for comparison")


def benchmark_z5d(n, iterations=5):
    """Benchmark Z5D predictor."""
    stats = benchmark_prediction(n, iterations)
    return {
        'method': 'Z5D Predictor',
        'result': predict_prime(n),
        'time_ms': stats['median_ms'],
        'iterations': iterations,
    }


def benchmark_sympy(n, iterations=5):
    """Benchmark sympy prime()."""
    if not HAS_SYMPY:
        return None
    
    times = []
    result = None
    for _ in range(iterations):
        t0 = time.perf_counter()
        result = sympy_prime(n)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
    
    return {
        'method': 'sympy.prime()',
        'result': result,
        'time_ms': sorted(times)[len(times)//2],
        'iterations': iterations,
    }


def compare_methods(n, z5d_iterations=5, sympy_iterations=3):
    """Compare different methods for finding nth prime."""
    print(f"\nComparing methods for n = {n:,}")
    print("="*70)
    
    # Benchmark Z5D
    print("Running Z5D predictor...")
    z5d_stats = benchmark_z5d(n, z5d_iterations)
    
    # Benchmark sympy if available
    sympy_stats = None
    if HAS_SYMPY and n <= 10**7:  # sympy gets slow beyond 10^7
        print("Running sympy.prime()...")
        sympy_stats = benchmark_sympy(n, sympy_iterations)
    
    # Display results
    print(f"\n{'Method':<20} {'Result':<20} {'Time (ms)':<15} {'Speedup'}")
    print("-"*70)
    
    baseline_time = z5d_stats['time_ms']
    
    print(f"{z5d_stats['method']:<20} {z5d_stats['result']:<20,} "
          f"{z5d_stats['time_ms']:<15.3f} 1.0x (baseline)")
    
    if sympy_stats:
        speedup = sympy_stats['time_ms'] / z5d_stats['time_ms']
        match = "✓" if sympy_stats['result'] == z5d_stats['result'] else "✗"
        print(f"{sympy_stats['method']:<20} {sympy_stats['result']:<20,} "
              f"{sympy_stats['time_ms']:<15.3f} {speedup:.1f}x {match}")
        
        # Check accuracy
        if sympy_stats['result'] != z5d_stats['result']:
            error = abs(z5d_stats['result'] - sympy_stats['result'])
            error_ppm = error / sympy_stats['result'] * 1e6
            print(f"\n  Note: Z5D prediction differs by {error:,} "
                  f"({error_ppm:.2f} ppm)")


def run_full_comparison():
    """Run comprehensive comparison across different scales."""
    print("\n" + "="*70)
    print(" Z5D PRIME PREDICTOR - COMPREHENSIVE BENCHMARK COMPARISON")
    print("="*70)
    
    print("\nTesting across different scales...")
    print("Note: sympy comparison limited to n ≤ 10^7 due to performance")
    
    test_cases = [
        (10**3, "Small", True),
        (10**4, "Medium", True),
        (10**5, "Large", True),
        (10**6, "Very Large", True),
        (10**7, "Huge", HAS_SYMPY),  # Include sympy if available
        (10**8, "Extreme", False),   # Skip sympy
        (10**15, "Massive", False),  # Skip sympy
    ]
    
    for n, label, include_sympy in test_cases:
        print(f"\n{label} Scale: n = {n:,}")
        print("-"*70)
        
        # Z5D benchmark
        z5d_stats = benchmark_z5d(n, iterations=5)
        print(f"Z5D:   {z5d_stats['time_ms']:>8.3f} ms  →  {z5d_stats['result']:,}")
        
        # sympy benchmark if requested and available
        if include_sympy and HAS_SYMPY:
            sympy_stats = benchmark_sympy(n, iterations=3)
            speedup = sympy_stats['time_ms'] / z5d_stats['time_ms']
            print(f"sympy: {sympy_stats['time_ms']:>8.3f} ms  →  {sympy_stats['result']:,}")
            print(f"Speedup: {speedup:.1f}x faster with Z5D")
            
            # Accuracy check
            if sympy_stats['result'] != z5d_stats['result']:
                error = abs(z5d_stats['result'] - sympy_stats['result'])
                error_ppm = error / sympy_stats['result'] * 1e6
                print(f"Error: {error:,} ({error_ppm:.2f} ppm)")


def run_accuracy_analysis():
    """Analyze accuracy characteristics of Z5D predictor."""
    print("\n" + "="*70)
    print(" Z5D ACCURACY ANALYSIS")
    print("="*70)
    
    print("\nComparing Z5D predictions with known exact values...")
    print(f"\n{'n':<15} {'Z5D Prediction':<20} {'Actual Prime':<20} {'Error':<15} {'PPM'}")
    print("-"*80)
    
    # Known exact values from OEIS or prime tables
    known_primes = {
        10**3: 7919,
        10**4: 104729,
        10**5: 1299709,
        10**6: 15485863,
        10**7: 179424673,
        10**8: 2038074743,
    }
    
    total_error_ppm = 0
    count = 0
    
    for n, actual in sorted(known_primes.items()):
        predicted = predict_prime(n)
        error = abs(predicted - actual)
        error_ppm = error / actual * 1e6
        total_error_ppm += error_ppm
        count += 1
        
        print(f"{n:<15,} {predicted:<20,} {actual:<20,} {error:<15,} {error_ppm:.3f}")
    
    print("-"*80)
    print(f"Average error: {total_error_ppm/count:.3f} ppm")
    print(f"Equivalent to: {100 - total_error_ppm/count/1e4:.6f}% accuracy")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'full':
            run_full_comparison()
        elif sys.argv[1] == 'accuracy':
            run_accuracy_analysis()
        elif sys.argv[1].isdigit():
            n = int(sys.argv[1])
            compare_methods(n)
        else:
            print("Usage:")
            print("  python z5d_benchmark_comparison.py              # Quick demo")
            print("  python z5d_benchmark_comparison.py full         # Full comparison")
            print("  python z5d_benchmark_comparison.py accuracy     # Accuracy analysis")
            print("  python z5d_benchmark_comparison.py <n>          # Compare for specific n")
    else:
        # Quick demo
        print("\n" + "="*70)
        print(" Z5D PRIME PREDICTOR - QUICK BENCHMARK")
        print("="*70)
        
        print("\nPerformance showcase:")
        for n in [10**5, 10**6, 10**7]:
            stats = benchmark_z5d(n, iterations=5)
            print(f"  n = 10^{len(str(n))-1}: {stats['time_ms']:.3f} ms  →  {stats['result']:,}")
        
        print("\nFor detailed comparison, run:")
        print("  python z5d_benchmark_comparison.py full")
        print("  python z5d_benchmark_comparison.py accuracy")


if __name__ == "__main__":
    main()
