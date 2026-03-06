#!/usr/bin/env python3
"""
Comprehensive demonstration of conic sections for integer factorization.

Shows practical applications of:
- Fermat's method (hyperbola x² - y² = N)
- Pell equation solutions
- Multiple quadratic forms
- Integration with GVA and Monte Carlo
- Gaussian lattice enhancements
"""

import sys
import time
import traceback
import math

# Try relative imports first, fallback to path manipulation
try:
    from conic_sections import (
        ConicSections,
        FermatFactorization,
        PellEquation,
        QuadraticForms,
        ConicFactorization
    )
    from conic_integration import (
        ConicGVAIntegration,
        ConicMonteCarloIntegration,
        ConicGaussianLatticeIntegration
    )
except ImportError:
    # Fallback: add python directory to path
    sys.path.append("python")
    from conic_sections import (
        ConicSections,
        FermatFactorization,
        PellEquation,
        QuadraticForms,
        ConicFactorization
    )
    from conic_integration import (
        ConicGVAIntegration,
        ConicMonteCarloIntegration,
        ConicGaussianLatticeIntegration
    )


def demo_fermat_factorization():
    """Demonstrate Fermat's factorization method."""
    print("\n" + "=" * 70)
    print("DEMO 1: Fermat Factorization (Hyperbola x² - y² = N)")
    print("=" * 70)
    
    fermat = FermatFactorization()
    
    test_cases = [
        (143, "Small balanced semiprime"),
        (899, "QMC benchmark semiprime"),
        (1003, "Moderate gap semiprime"),
        (10403, "Larger balanced semiprime"),
        (1234567, "7-digit semiprime"),
    ]
    
    print("\n{:<12} {:<20} {:<15} {:<10}".format("N", "Description", "Factors", "Time (ms)"))
    print("-" * 70)
    
    for N, description in test_cases:
        start = time.time()
        result = fermat.factorize(N, max_iterations=100000)
        elapsed_ms = (time.time() - start) * 1000
        
        if result:
            p, q = result
            factors_str = f"{p} × {q}"
            
            # Verify
            assert p * q == N, "Invalid factorization"
            print(f"{N:<12} {description:<20} {factors_str:<15} {elapsed_ms:.2f}")
        else:
            print(f"{N:<12} {description:<20} {'Not found':<15} {elapsed_ms:.2f}")


def demo_pell_equation():
    """Demonstrate Pell equation solutions."""
    print("\n" + "=" * 70)
    print("DEMO 2: Pell Equation Solutions (x² - dy² = 1)")
    print("=" * 70)
    
    pell_values = [2, 3, 5, 7, 10]
    
    for d in pell_values:
        print(f"\n--- Pell equation for d = {d} ---")
        
        try:
            pell = PellEquation(d)
            fundamental = pell.find_fundamental_solution()
            
            if fundamental:
                x1, y1 = fundamental
                print(f"Fundamental solution: ({x1}, {y1})")
                print(f"Verification: {x1}² - {d}×{y1}² = {x1*x1 - d*y1*y1}")
                
                # Show first few solutions
                solutions = pell.generate_solutions(3)
                print(f"\nFirst 3 solutions:")
                for i, (x, y) in enumerate(solutions, 1):
                    print(f"  {i}. ({x}, {y})")
        
        except ValueError as e:
            print(f"Error: {e}")


def demo_quadratic_forms():
    """Demonstrate multiple quadratic forms."""
    print("\n" + "=" * 70)
    print("DEMO 3: Multiple Quadratic Forms")
    print("=" * 70)
    
    qf = QuadraticForms()
    
    # Sum of squares
    print("\n--- Representations as x² + y² ---")
    for N in [25, 50, 125]:
        reps = qf.represent_as_sum_of_squares(N)
        print(f"\n{N} = x² + y²:")
        for x, y in reps[:5]:
            print(f"  {N} = {x}² + {y}² = {x*x} + {y*y}")
    
    # Difference of squares
    print("\n--- Representations as x² - y² (Fermat) ---")
    for N in [143, 899]:
        reps = qf.represent_as_difference_of_squares(N)
        print(f"\n{N} = x² - y²:")
        for x, y in reps[:3]:
            print(f"  {N} = {x}² - {y}² = {x*x} - {y*y}")
            # Show factorization
            p, q = x - y, x + y
            print(f"      → ({x}-{y}) × ({x}+{y}) = {p} × {q}")
    
    # Weighted forms
    print("\n--- Weighted Forms: 2x² + 3y² ---")
    for N in [50, 100]:
        reps = qf.represent_as_mx2_plus_ny2(N, 2, 3)
        print(f"\n{N} = 2x² + 3y²:")
        for x, y in reps:
            result = 2*x*x + 3*y*y
            print(f"  {N} = 2×{x}² + 3×{y}² = {result}")


def demo_conic_gva_integration():
    """Demonstrate conic-GVA integration."""
    print("\n" + "=" * 70)
    print("DEMO 4: Conic-GVA Integration (Z5D Weighted Candidates)")
    print("=" * 70)
    
    gva_conic = ConicGVAIntegration()
    
    test_cases = [
        (143, "11 × 13"),
        (899, "29 × 31"),
        (10403, "101 × 103"),
    ]
    
    for N, expected in test_cases:
        print(f"\n--- N = {N} (expected: {expected}) ---")
        
        # Get Z5D-weighted candidates
        weighted = gva_conic.conic_candidates_with_z5d_curvature(N, num_candidates=10, k=0.3)
        
        print("Top 10 Z5D-weighted candidates:")
        print("{:<5} {:<8} {:<12} {:<10}".format("Rank", "Value", "Weight", "Factor?"))
        print("-" * 40)
        
        for i, (candidate, weight) in enumerate(weighted, 1):
            is_factor = "✓" if N % candidate == 0 else ""
            print(f"{i:<5} {candidate:<8} {weight:.6f}   {is_factor}")
        
        # Try factorization
        result = gva_conic.factorize_with_conic_gva(N, max_candidates=100)
        if result:
            p, q = result
            print(f"\n✓ Factored: {p} × {q}")
        else:
            print(f"\n✗ Factorization failed")


def demo_monte_carlo_integration():
    """Demonstrate Monte Carlo sampling on conics."""
    print("\n" + "=" * 70)
    print("DEMO 5: Monte Carlo Sampling on Hyperbola")
    print("=" * 70)
    
    mc_conic = ConicMonteCarloIntegration(seed=42)
    
    N = 899
    print(f"\nTesting N = {N} with different sampling modes:")
    
    modes = ['uniform', 'phi-biased', 'stratified']
    
    for mode in modes:
        print(f"\n--- Sampling mode: {mode} ---")
        
        start = time.time()
        candidates = mc_conic.monte_carlo_conic_candidates(N, num_samples=500, mode=mode)
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"Generated {len(candidates)} unique candidates in {elapsed_ms:.2f}ms")
        
        # Check for true factors
        true_factors = [29, 31]
        found = [f for f in true_factors if f in candidates]
        
        if found:
            ranks = [candidates.index(f) for f in found]
            print(f"✓ Found factors {found} at ranks {ranks}")
        else:
            print(f"✗ True factors not in candidates")


def demo_gaussian_lattice_integration():
    """Demonstrate Gaussian lattice integration."""
    print("\n" + "=" * 70)
    print("DEMO 6: Gaussian Lattice Enhanced Distances")
    print("=" * 70)
    
    try:
        lattice_conic = ConicGaussianLatticeIntegration()
        
        N = 899
        sqrt_n = int(math.sqrt(N))
        
        print(f"\nN = {N}, √N ≈ {sqrt_n}")
        print("\nLattice-enhanced distances:")
        print("{:<10} {:<15} {:<10}".format("Candidate", "Distance", "Factor?"))
        print("-" * 40)
        
        for delta in range(-5, 6):
            candidate = sqrt_n + delta
            distance = lattice_conic.lattice_enhanced_conic_distance(candidate, N, lattice_scale=0.5)
            is_factor = "✓" if N % candidate == 0 else ""
            print(f"{candidate:<10} {distance:.6f}      {is_factor}")
        
        # Show Gaussian Pell solutions
        print("\n--- Gaussian Pell Solutions (d=2) ---")
        gaussian_sols = lattice_conic.gaussian_pell_solutions(d=2, num_solutions=5)
        
        print("{:<5} {:<20} {:<10}".format("Rank", "z (Gaussian)", "Norm"))
        print("-" * 40)
        
        for i, (z, norm) in enumerate(gaussian_sols, 1):
            print(f"{i:<5} {z.real:.0f} + {z.imag:.0f}i      {norm:.2f}")
    
    except Exception as e:
        print(f"Note: Gaussian lattice module not available: {e}")


def demo_performance_comparison():
    """Compare conic methods with different strategies."""
    print("\n" + "=" * 70)
    print("DEMO 7: Performance Comparison (Conic Strategies)")
    print("=" * 70)
    
    conic_fact = ConicFactorization()
    
    test_cases = [143, 899, 1003, 10403]
    strategies_list = [
        ['fermat'],
        ['pell'],
        ['sum_of_squares'],
        ['multiple_forms'],
        ['fermat', 'pell', 'multiple_forms'],
    ]
    
    print("\n{:<12} {:<30} {:<12} {:<10}".format("N", "Strategies", "Result", "Time (ms)"))
    print("-" * 70)
    
    for N in test_cases:
        for strategies in strategies_list:
            strategy_str = "+".join(strategies)
            
            start = time.time()
            result = conic_fact.factorize_via_conics(N, strategies=strategies)
            elapsed_ms = (time.time() - start) * 1000
            
            if result:
                p, q = result
                result_str = f"{p}×{q}"
            else:
                result_str = "None"
            
            print(f"{N:<12} {strategy_str:<30} {result_str:<12} {elapsed_ms:.2f}")
        print()


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print(" CONIC SECTIONS FOR INTEGER FACTORIZATION - COMPREHENSIVE DEMO")
    print("=" * 70)
    
    demos = [
        demo_fermat_factorization,
        demo_pell_equation,
        demo_quadratic_forms,
        demo_conic_gva_integration,
        demo_monte_carlo_integration,
        demo_gaussian_lattice_integration,
        demo_performance_comparison,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\nError in {demo.__name__}: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(" DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
