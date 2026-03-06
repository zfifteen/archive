#!/usr/bin/env python3
"""
Demonstration of Gaussian Integer Lattice + Monte Carlo Enhanced Factorization

This example shows:
1. Basic usage of enhanced Pollard's rho
2. Comparison of different strategies
3. Low-discrepancy sampling benefits
4. Integration with existing z-sandbox components
5. Practical application scenarios
"""

import sys
import time
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pollard_gaussian_monte_carlo import GaussianLatticePollard
from gaussian_lattice import GaussianIntegerLattice
import sympy


def section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_1_basic_usage():
    """Example 1: Basic factorization."""
    section("Example 1: Basic Usage")
    
    # Initialize factorizer
    factorizer = GaussianLatticePollard(seed=42)
    
    # Factor a simple semiprime
    N = 899  # 29 × 31
    print(f"Factoring N = {N}")
    
    # Standard Pollard's rho
    factor = factorizer.standard_pollard_rho(N, max_iterations=10000)
    print(f"Standard Pollard: factor = {factor}")
    print(f"Verification: {N} = {factor} × {N // factor}")
    print(f"Both prime? {sympy.isprime(factor)} and {sympy.isprime(N // factor)}")


def example_2_strategy_comparison():
    """Example 2: Compare different strategies."""
    section("Example 2: Strategy Comparison")
    
    factorizer = GaussianLatticePollard(seed=42)
    
    test_cases = [
        (143, "11 × 13", "Very small"),
        (899, "29 × 31", "Small, close factors"),
        (1003, "17 × 59", "Small, distant factors"),
        (10403, "101 × 103", "Medium, close factors"),
    ]
    
    print(f"{'N':<8} {'Description':<25} {'Strategy':<20} {'Time (ms)':<12} {'Factor'}")
    print("-" * 90)
    
    for N, desc, category in test_cases:
        # Try standard
        start = time.time()
        factor = factorizer.standard_pollard_rho(N, max_iterations=10000)
        elapsed_ms = (time.time() - start) * 1000
        print(f"{N:<8} {desc:<25} {'Standard':<20} {elapsed_ms:>8.2f}     {factor}")
        
        # Try lattice-enhanced
        start = time.time()
        factor = factorizer.lattice_enhanced_pollard_rho(N, max_iterations=10000)
        elapsed_ms = (time.time() - start) * 1000
        print(f"{' '*8} {' '*25} {'Lattice-enhanced':<20} {elapsed_ms:>8.2f}     {factor}")
        
        # Try Monte Carlo with Sobol'
        start = time.time()
        factor = factorizer.monte_carlo_lattice_pollard(
            N, max_iterations=5000, num_trials=5, sampling_mode='sobol'
        )
        elapsed_ms = (time.time() - start) * 1000
        print(f"{' '*8} {' '*25} {'MC + Sobol':<20} {elapsed_ms:>8.2f}     {factor}")
        
        print()


def example_3_sampling_modes():
    """Example 3: Compare low-discrepancy sampling modes."""
    section("Example 3: Low-Discrepancy Sampling Comparison")
    
    factorizer = GaussianLatticePollard(seed=42)
    N = 899  # 29 × 31
    
    print(f"Target: N = {N} = 29 × 31\n")
    
    sampling_modes = ['uniform', 'sobol', 'golden-angle']
    
    print(f"{'Mode':<15} {'Trials':<8} {'Time (ms)':<12} {'Success':<10} {'Factor'}")
    print("-" * 60)
    
    for mode in sampling_modes:
        for num_trials in [5, 10, 20]:
            start = time.time()
            factor = factorizer.monte_carlo_lattice_pollard(
                N,
                max_iterations=5000,
                num_trials=num_trials,
                sampling_mode=mode
            )
            elapsed_ms = (time.time() - start) * 1000
            success = "✓" if factor in [29, 31] else "✗"
            
            print(f"{mode:<15} {num_trials:<8} {elapsed_ms:>8.2f}     {success:<10} {factor}")
    
    print("\nObservation: Low-discrepancy modes (Sobol', golden-angle) often")
    print("provide better coverage with fewer trials, though uniform can be")
    print("faster for simple cases with sufficient trials.")


def example_4_lattice_constants():
    """Example 4: Lattice-optimized constants."""
    section("Example 4: Lattice-Optimized Constants")
    
    factorizer = GaussianLatticePollard(seed=42)
    lattice = GaussianIntegerLattice()
    
    test_numbers = [143, 899, 1003, 10403]
    
    print(f"{'N':<8} {'sqrt(N)':<10} {'Lattice Constant':<20} {'Distance Scale'}")
    print("-" * 60)
    
    for N in test_numbers:
        import math
        sqrt_N = math.isqrt(N)
        
        # Compute lattice-optimized constant
        c = factorizer._lattice_optimized_constant(N)
        
        # Compute lattice distance scale
        z1 = complex(sqrt_N, 0)
        z2 = complex(sqrt_N + 1, 0)
        dist = lattice.lattice_enhanced_distance(z1, z2, lattice_scale=0.5)
        
        print(f"{N:<8} {sqrt_N:<10} {c:<20} {float(dist):.6f}")
    
    print("\nLattice-optimized constants are selected based on:")
    print("1. Gaussian integer lattice structure around √N")
    print("2. Epstein zeta function considerations")
    print("3. Golden ratio for optimal distribution")


def example_5_variance_reduction():
    """Example 5: Demonstrate variance reduction."""
    section("Example 5: Variance Reduction Analysis")
    
    factorizer = GaussianLatticePollard(seed=42)
    N = 899
    
    print(f"Analyzing starting point generation for N = {N}\n")
    
    num_points = 50
    sqrt_N = 29
    
    # Generate points with different modes
    uniform_points = factorizer._generate_starting_points(sqrt_N, num_points, 'uniform')
    sobol_points = factorizer._generate_starting_points(sqrt_N, num_points, 'sobol')
    golden_points = factorizer._generate_starting_points(sqrt_N, num_points, 'golden-angle')
    
    # Analyze uniqueness
    uniform_x = [int(x) for x, _ in uniform_points]
    sobol_x = [int(x) for x, _ in sobol_points]
    golden_x = [int(x) for x, _ in golden_points]
    
    unique_uniform = len(set(uniform_x))
    unique_sobol = len(set(sobol_x))
    unique_golden = len(set(golden_x))
    
    print(f"{'Mode':<15} {'Total Points':<15} {'Unique Points':<15} {'Coverage'}")
    print("-" * 60)
    print(f"{'Uniform':<15} {num_points:<15} {unique_uniform:<15} {unique_uniform/num_points*100:.1f}%")
    print(f"{'Sobol':<15} {num_points:<15} {unique_sobol:<15} {unique_sobol/num_points*100:.1f}%")
    print(f"{'Golden-angle':<15} {num_points:<15} {unique_golden:<15} {unique_golden/num_points*100:.1f}%")
    
    print(f"\nVariance Reduction Benefit:")
    print(f"  Low-discrepancy vs Uniform: {unique_sobol/unique_uniform:.2f}× better coverage")
    print(f"  Golden-angle vs Uniform: {unique_golden/unique_uniform:.2f}× better coverage")


def example_6_integration_gva():
    """Example 6: Integration with GVA framework."""
    section("Example 6: Integration with GVA Framework")
    
    print("The enhanced Pollard can serve as a fast preliminary screen")
    print("before applying more expensive GVA or ECM methods.\n")
    
    factorizer = GaussianLatticePollard(seed=42)
    
    # Simulate a factorization pipeline
    test_numbers = [143, 899, 1003, 10403]
    
    print(f"{'N':<8} {'Pollard Result':<20} {'Next Step':<25} {'Reason'}")
    print("-" * 80)
    
    for N in test_numbers:
        # Try quick Pollard first
        factor = factorizer.monte_carlo_lattice_pollard(
            N, max_iterations=5000, num_trials=5, sampling_mode='sobol'
        )
        
        if factor and factor > 1 and N % factor == 0:
            result = f"✓ Found: {factor}"
            next_step = "Verify and complete"
            reason = "Success in preliminary"
        else:
            result = "✗ No factor"
            next_step = "Proceed to GVA/ECM"
            reason = "Need stronger method"
        
        print(f"{N:<8} {result:<20} {next_step:<25} {reason}")
    
    print("\nBenefit: Fast elimination of easy cases before expensive methods.")


def example_7_cryptographic_testing():
    """Example 7: Cryptographic vulnerability testing scenario."""
    section("Example 7: Cryptographic Vulnerability Testing")
    
    print("Scenario: Testing RSA-like moduli for weak factorization\n")
    
    factorizer = GaussianLatticePollard(seed=42)
    
    # Simulate testing various moduli
    test_scenarios = [
        (143, "Toy example", "WEAK"),
        (899, "Close factors", "WEAK"),
        (10403, "Medium security", "WEAK"),
        (10000019, "Better separation", "MODERATE"),
    ]
    
    print(f"{'Modulus':<12} {'Description':<20} {'Risk Level':<15} {'Time (ms)'}")
    print("-" * 70)
    
    for N, desc, risk in test_scenarios:
        start = time.time()
        
        # Quick test with enhanced Pollard
        factor = factorizer.monte_carlo_lattice_pollard(
            N,
            max_iterations=20000,
            num_trials=10,
            sampling_mode='sobol'
        )
        
        elapsed_ms = (time.time() - start) * 1000
        
        if factor and factor > 1 and N % factor == 0:
            result = f"✗ FACTORED: {risk}"
        else:
            result = "✓ Passed quick test"
        
        print(f"{N:<12} {desc:<20} {result:<15} {elapsed_ms:>8.2f}")
    
    print("\nNote: This is a preliminary screen only. RSA security requires")
    print("much larger moduli (2048+ bits) and proper implementation.")


def example_8_benchmark_summary():
    """Example 8: Comprehensive benchmark."""
    section("Example 8: Comprehensive Benchmark Summary")
    
    factorizer = GaussianLatticePollard(seed=42)
    
    # Run comprehensive benchmark
    N = 10403  # 101 × 103
    print(f"Benchmarking all strategies on N = {N} (101 × 103)\n")
    
    results = factorizer.benchmark_strategies(N, max_iterations=10000)
    
    # Sort by time
    sorted_results = sorted(results.items(), key=lambda x: x[1]['time_seconds'])
    
    print(f"{'Strategy':<30} {'Time (ms)':<12} {'Success':<10} {'Factor'}")
    print("-" * 70)
    
    for strategy, result in sorted_results:
        time_ms = result['time_seconds'] * 1000
        success = "✓" if result['success'] else "✗"
        factor = result['factor'] if result['factor'] else "None"
        
        print(f"{strategy:<30} {time_ms:>8.2f}     {success:<10} {factor}")
    
    print("\nKey Insights:")
    print("- Standard Pollard is fastest for simple cases")
    print("- Lattice enhancement adds modest overhead but better convergence")
    print("- Monte Carlo variants trade time for reliability")
    print("- Choice depends on: N size, factor separation, time constraints")


def main():
    """Run all examples."""
    print("=" * 70)
    print("  Gaussian Integer Lattice + Monte Carlo Enhanced Factorization")
    print("  Demonstration Examples")
    print("=" * 70)
    
    examples = [
        ("Basic Usage", example_1_basic_usage),
        ("Strategy Comparison", example_2_strategy_comparison),
        ("Sampling Modes", example_3_sampling_modes),
        ("Lattice Constants", example_4_lattice_constants),
        ("Variance Reduction", example_5_variance_reduction),
        ("GVA Integration", example_6_integration_gva),
        ("Cryptographic Testing", example_7_cryptographic_testing),
        ("Benchmark Summary", example_8_benchmark_summary),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n[{i}/{len(examples)}] Running: {name}")
        try:
            func()
        except Exception as e:
            print(f"Error in {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("  All Examples Complete")
    print("=" * 70)
    print("\nFor more details, see:")
    print("  - docs/POLLARD_GAUSSIAN_MONTE_CARLO_INTEGRATION.md")
    print("  - tests/test_pollard_gaussian_monte_carlo.py")
    print("  - python/pollard_gaussian_monte_carlo.py")


if __name__ == "__main__":
    main()
