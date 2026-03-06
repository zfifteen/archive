#!/usr/bin/env python3
"""
Demonstration of v_{5D}^2 = c^2 constraint for massive particles in the Z framework.

This script demonstrates the mathematical basis for assigning v_{5D}^2 = c^2 as an extra-dimensional
velocity invariant and analyzes implications for massive particles' motion along the w-dimension
using the Z definition and curvature-based geodesics.
"""

import numpy as np
import matplotlib.pyplot as plt
from core.axioms import velocity_5d_constraint, massive_particle_w_velocity, curvature_induced_w_motion
from core.domain import DiscreteZetaShift
from sympy import isprime

# Set matplotlib backend for headless environment
plt.switch_backend('Agg')

def demonstrate_5d_velocity_constraint():
    """Demonstrate the v_{5D}^2 = c^2 constraint for various velocity configurations."""
    print("=== Demonstrating v_{5D}^2 = c^2 Velocity Constraint ===")
    
    c = 299792458.0  # Speed of light in m/s
    
    # Test cases: different 4D velocity configurations
    test_cases = [
        (0, 0, 0, 0, "Rest case"),
        (0.1*c, 0, 0, 0, "10% c in x-direction"),
        (0.3*c, 0.4*c, 0, 0, "Pythagoras 3-4-5 scaled"),
        (0.6*c, 0.6*c, 0.2*c, 0.2*c, "High 4D velocity")
    ]
    
    print(f"{'Case':<25} {'v_4D/c':<10} {'v_w/c':<10} {'Constraint':<15}")
    print("-" * 70)
    
    for v_x, v_y, v_z, v_t, description in test_cases:
        try:
            # Calculate required w-velocity for massive particles
            v_w = massive_particle_w_velocity(v_x, v_y, v_z, v_t, c)
            
            # Verify constraint
            constraint_violation = velocity_5d_constraint(v_x, v_y, v_z, v_t, v_w, c)
            
            v_4d_magnitude = np.sqrt(v_x**2 + v_y**2 + v_z**2 + v_t**2)
            
            print(f"{description:<25} {v_4d_magnitude/c:<10.3f} {v_w/c:<10.3f} {constraint_violation:<15.2e}")
            
        except ValueError as e:
            print(f"{description:<25} {'ERROR':<10} {'N/A':<10} {str(e)}")
    
    print()

def analyze_massive_particle_geodesics():
    """Analyze massive particle motion along w-dimension for primes vs composites."""
    print("=== Analyzing Massive Particle Motion Along W-Dimension ===")
    
    # Analyze motion for first 20 integers
    results = []
    for n in range(2, 22):
        shift = DiscreteZetaShift(n)
        analysis = shift.analyze_massive_particle_motion()
        results.append(analysis)
    
    # Separate primes and composites
    prime_results = [r for r in results if r['is_prime']]
    composite_results = [r for r in results if not r['is_prime']]
    
    print(f"{'n':<4} {'Type':<10} {'v_w/c':<12} {'κ(n)':<12} {'Geodesic':<20}")
    print("-" * 70)
    
    for r in results:
        n_type = "Prime" if r['is_prime'] else "Composite"
        print(f"{r['n']:<4} {n_type:<10} {r['v_w']/299792458.0:<12.6f} {r['discrete_curvature']:<12.6f} {r['geodesic_classification']:<20}")
    
    # Statistical analysis
    if prime_results and composite_results:
        prime_curvatures = [r['discrete_curvature'] for r in prime_results]
        composite_curvatures = [r['discrete_curvature'] for r in composite_results]
        
        print(f"\nStatistical Analysis:")
        print(f"Prime curvatures (κ): mean={np.mean(prime_curvatures):.6f}, std={np.std(prime_curvatures):.6f}")
        print(f"Composite curvatures (κ): mean={np.mean(composite_curvatures):.6f}, std={np.std(composite_curvatures):.6f}")
        
        prime_w_velocities = [r['v_w'] for r in prime_results]
        composite_w_velocities = [r['v_w'] for r in composite_results]
        
        print(f"Prime w-velocities: mean={np.mean(prime_w_velocities)/299792458.0:.6f}c, std={np.std(prime_w_velocities)/299792458.0:.6f}c")
        print(f"Composite w-velocities: mean={np.mean(composite_w_velocities)/299792458.0:.6f}c, std={np.std(composite_w_velocities)/299792458.0:.6f}c")
    
    print()

def demonstrate_curvature_w_coupling():
    """Demonstrate how discrete curvature influences w-dimension motion."""
    print("=== Curvature-Induced W-Dimension Motion ===")
    
    c = 299792458.0
    
    # Test various integers and their curvature-induced w-motion
    print(f"{'n':<4} {'d(n)':<6} {'κ(n)':<12} {'v_w_curvature/c':<15} {'Type':<10}")
    print("-" * 60)
    
    for n in range(2, 16):
        from sympy import divisors
        d_n = len(divisors(n))
        v_w_curv = curvature_induced_w_motion(n, d_n, c)
        n_type = "Prime" if isprime(n) else "Composite"
        
        kappa = d_n * np.log(n + 1) / np.exp(2)
        
        print(f"{n:<4} {d_n:<6} {kappa:<12.6f} {v_w_curv/c:<15.6f} {n_type:<10}")
    
    print()

def create_visualization():
    """Create visualizations of 5D motion and w-dimension analysis."""
    print("=== Creating Visualizations ===")
    
    # Generate data for N=50 integers
    n_values = []
    curvatures = []
    w_velocities = []
    is_prime_list = []
    
    for n in range(2, 52):
        shift = DiscreteZetaShift(n)
        analysis = shift.analyze_massive_particle_motion()
        
        n_values.append(n)
        curvatures.append(analysis['discrete_curvature'])
        w_velocities.append(analysis['v_w'])
        is_prime_list.append(analysis['is_prime'])
    
    # Create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot 1: Curvature vs n, colored by prime/composite
    primes = np.array(is_prime_list)
    ax1.scatter(np.array(n_values)[primes], np.array(curvatures)[primes], 
                c='red', label='Primes', alpha=0.7, s=50)
    ax1.scatter(np.array(n_values)[~primes], np.array(curvatures)[~primes], 
                c='blue', label='Composites', alpha=0.7, s=50)
    ax1.set_xlabel('n')
    ax1.set_ylabel('Discrete Curvature κ(n)')
    ax1.set_title('Discrete Curvature vs Integer n')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: W-dimension velocity vs n
    c = 299792458.0
    w_vel_normalized = np.array(w_velocities) / c
    ax2.scatter(np.array(n_values)[primes], w_vel_normalized[primes], 
                c='red', label='Primes', alpha=0.7, s=50)
    ax2.scatter(np.array(n_values)[~primes], w_vel_normalized[~primes], 
                c='blue', label='Composites', alpha=0.7, s=50)
    ax2.set_xlabel('n')
    ax2.set_ylabel('W-dimension Velocity (v_w/c)')
    ax2.set_title('W-Dimension Velocity for Massive Particles')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('v5d_massive_particles_analysis.png', dpi=150, bbox_inches='tight')
    print("Visualization saved as 'v5d_massive_particles_analysis.png'")
    plt.close()

def main():
    """Main demonstration function."""
    print("Z Framework: v_{5D}^2 = c^2 for Massive Particles")
    print("=" * 60)
    print()
    
    # Demonstrate theoretical constraint
    demonstrate_5d_velocity_constraint()
    
    # Analyze discrete geodesics
    analyze_massive_particle_geodesics()
    
    # Show curvature coupling
    demonstrate_curvature_w_coupling()
    
    # Create visualizations
    create_visualization()
    
    print("Mathematical Basis Summary:")
    print("- v_{5D}^2 = v_x^2 + v_y^2 + v_z^2 + v_t^2 + v_w^2 = c^2")
    print("- For massive particles: v_w > 0 required")
    print("- W-motion connected to discrete curvature κ(n) = d(n)·ln(n+1)/e²")
    print("- Primes exhibit minimal curvature → distinct w-dimension geodesics")
    print("- Framework unifies Kaluza-Klein theory with discrete number theory")

if __name__ == "__main__":
    main()