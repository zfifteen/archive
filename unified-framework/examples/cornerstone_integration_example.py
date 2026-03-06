"""
Cornerstone Invariant Integration Example

This example demonstrates how the cornerstone invariant principle
integrates with existing Z Framework components:
1. z_baseline: Baseline predictions using discrete invariant
2. axioms: Universal Z form alignment
3. params: Parameter standardization with invariants

Shows practical integration patterns for using cornerstone invariants
in existing Z Framework workflows.
"""

import sys
import os
from math import e, log

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from cornerstone_invariant import (
    CornerstoneInvariant,
    PhysicalInvariant,
    DiscreteInvariant,
    NumberTheoreticInvariant
)


def example_1_baseline_integration():
    """
    Example 1: Integration with z_baseline framework
    
    Shows how discrete invariant aligns with baseline Z predictor
    using the same Δₘₐₓ = e² invariant.
    """
    print("=" * 80)
    print("EXAMPLE 1: Integration with z_baseline Framework")
    print("=" * 80)
    print()
    
    # Create discrete invariant matching z_baseline's e² constant
    discrete = DiscreteInvariant(delta_max=e**2)
    
    print(f"Discrete invariant: Δₘₐₓ = e² = {float(discrete.c):.6f}")
    print()
    
    # Demonstrate dilation factor computation (from z_baseline)
    print("Dilation Factor Analysis:")
    print("-" * 80)
    
    test_n_values = [100, 1000, 10000, 100000]
    
    for n in test_n_values:
        # Compute baseline dilation: Δₙ = d(n)·ln(n+1)/e²
        d_n = log(n) if n > 1 else 1
        ln_term = log(n + 1)
        delta_n = (d_n * ln_term) / (e**2)
        
        # Use cornerstone invariant for normalization
        normalized = discrete.compute_normalized_density(n, delta_n)
        
        print(f"n = {n:6d} | Δₙ = {delta_n:.6f} | Z = {float(normalized):10.2f}")
    
    print()
    print("Observation: Cornerstone invariant provides consistent normalization")
    print("             framework for baseline predictions.")
    print()


def example_2_physical_to_discrete_mapping():
    """
    Example 2: Mapping between physical and discrete domains
    
    Demonstrates how the same Z = A(B/c) equation applies across
    domains with different invariants.
    """
    print("=" * 80)
    print("EXAMPLE 2: Physical to Discrete Domain Mapping")
    print("=" * 80)
    print()
    
    # Create invariants for both domains
    phys = PhysicalInvariant()
    discrete = DiscreteInvariant()
    
    print("Domain Invariants:")
    print(f"  Physical: c = {float(phys.c):.2e} m/s")
    print(f"  Discrete: Δₘₐₓ = {float(discrete.c):.6f}")
    print()
    
    # Show how the same equation structure applies
    print("Cross-Domain Computation Structure:")
    print("-" * 80)
    
    # Physical example: velocity as fraction of c
    v = 0.5 * phys.c
    beta = v / phys.c
    print(f"Physical domain:")
    print(f"  v/c = {float(beta):.2f} (velocity ratio)")
    
    # Discrete example: delta as fraction of delta_max
    delta_n = 3.5
    discrete_ratio = delta_n / float(discrete.c)
    print(f"Discrete domain:")
    print(f"  Δₙ/Δₘₐₓ = {discrete_ratio:.4f} (density shift ratio)")
    print()
    
    print("Both use Z = A(B/c) structure:")
    print("  Physical: Z = T(v/c) with T = time dilation factor")
    print("  Discrete: Z = n(Δₙ/Δₘₐₓ) with n = integer frame")
    print()


def example_3_golden_ratio_optimization():
    """
    Example 3: Golden ratio invariant for optimization
    
    Shows how number-theoretic invariant enables geodesic
    optimization and density enhancement.
    """
    print("=" * 80)
    print("EXAMPLE 3: Golden Ratio Invariant for Optimization")
    print("=" * 80)
    print()
    
    nt = NumberTheoreticInvariant()
    
    print(f"Golden ratio invariant: φ = {float(nt.c):.6f}")
    print()
    
    # Demonstrate geodesic transformation for optimization
    print("Geodesic Transformation θ'(n,k) = φ·{n/φ}^k:")
    print("-" * 80)
    
    # Different k values represent different optimization strategies
    k_strategies = {
        0.1: "Conservative (low curvature)",
        0.3: "Balanced (optimal for many cases)",
        0.5: "Moderate (mid-range curvature)",
        0.7: "Aggressive (high curvature)"
    }
    
    n = 1000
    print(f"For n = {n}:")
    print()
    
    for k, strategy in k_strategies.items():
        result = nt.compute_geodesic_transform(n, k)
        print(f"  k = {k:.1f} ({strategy:30s}) → θ' = {float(result):10.4f}")
    
    print()
    print("Application: Different k values provide tuning parameter for")
    print("             geodesic density enhancement and optimization.")
    print()


def example_4_parameter_standardization():
    """
    Example 4: Parameter standardization with invariants
    
    Shows how cornerstone invariants provide standardization
    similar to params.py constants.
    """
    print("=" * 80)
    print("EXAMPLE 4: Parameter Standardization with Invariants")
    print("=" * 80)
    print()
    
    # Demonstrate different invariant choices for different contexts
    invariants = [
        ("Physical", PhysicalInvariant(), "Speed of light"),
        ("Discrete", DiscreteInvariant(), "e² (Euler constant squared)"),
        ("Golden", NumberTheoreticInvariant(), "φ (golden ratio)"),
        ("Custom", CornerstoneInvariant(c=100.0, domain="custom"), "Domain-specific constant")
    ]
    
    print("Framework Invariants:")
    print("-" * 80)
    
    for name, inv, description in invariants:
        props = inv.get_invariant_properties()
        print(f"{name:12s}: c = {props['invariant_c']:12.6f} | {description}")
    
    print()
    print("Each invariant provides:")
    print("  • Reference frame consistency")
    print("  • Reproducible measurements")
    print("  • Cross-domain compatibility")
    print()


def example_5_multi_domain_workflow():
    """
    Example 5: Complete multi-domain workflow
    
    Demonstrates a workflow using multiple invariants together
    for a comprehensive analysis.
    """
    print("=" * 80)
    print("EXAMPLE 5: Multi-Domain Workflow")
    print("=" * 80)
    print()
    
    print("Scenario: Analyzing a system with multiple domain aspects")
    print("-" * 80)
    print()
    
    # Step 1: Physical domain analysis
    print("Step 1: Physical domain - relativistic effects")
    phys = PhysicalInvariant()
    velocity = 0.8 * phys.c
    
    gamma = phys.time_dilation(1.0, velocity)
    length = phys.length_contraction(1.0, velocity)
    
    print(f"  Velocity: v = 0.8c")
    print(f"  Time dilation: γ = {float(gamma):.6f}")
    print(f"  Length contraction: L/L₀ = {float(length):.6f}")
    print()
    
    # Step 2: Discrete domain analysis
    print("Step 2: Discrete domain - density normalization")
    discrete = DiscreteInvariant()
    
    n_values = [100, 500, 1000]
    for n in n_values:
        delta_n = 0.5
        z_discrete = discrete.compute_normalized_density(n, delta_n)
        print(f"  n = {n:4d}: Z_discrete = {float(z_discrete):.2f}")
    print()
    
    # Step 3: Number-theoretic optimization
    print("Step 3: Number-theoretic domain - geodesic optimization")
    nt = NumberTheoreticInvariant()
    
    optimal_k = 0.3  # From KAPPA_GEO_DEFAULT in params.py
    n_opt = 1000
    
    theta_prime = nt.compute_geodesic_transform(n_opt, optimal_k)
    print(f"  Optimal k = {optimal_k}")
    print(f"  θ'({n_opt}, {optimal_k}) = {float(theta_prime):.6f}")
    print()
    
    # Summary
    print("Summary:")
    print("-" * 80)
    print("All three domains use the same cornerstone principle Z = A(B/c):")
    print(f"  • Physical:        Z = {float(gamma):.6f} (with c = speed of light)")
    print(f"  • Discrete:        Z = {float(z_discrete):.2f} (with c = e²)")
    print(f"  • Number-theoretic: Z = {float(theta_prime):.6f} (with c = φ)")
    print()
    print("This demonstrates the universality and power of the invariant principle.")
    print()


def main():
    """Run all integration examples."""
    print()
    print("=" * 80)
    print(" CORNERSTONE INVARIANT INTEGRATION EXAMPLES")
    print(" Practical Integration with Z Framework Components")
    print("=" * 80)
    print()
    
    # Run all examples
    example_1_baseline_integration()
    example_2_physical_to_discrete_mapping()
    example_3_golden_ratio_optimization()
    example_4_parameter_standardization()
    example_5_multi_domain_workflow()
    
    # Final notes
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("The cornerstone invariant principle provides:")
    print()
    print("1. UNIFIED FOUNDATION")
    print("   Same equation Z = A(B/c) works across all domains")
    print()
    print("2. STANDARDIZATION")
    print("   Consistent parameter definitions via domain invariants")
    print()
    print("3. INTEGRATION")
    print("   Natural compatibility with existing Z Framework components")
    print()
    print("4. FLEXIBILITY")
    print("   Easy to extend to new domains with custom invariants")
    print()
    print("This is the scaffolding that unifies all Z Framework work.")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
