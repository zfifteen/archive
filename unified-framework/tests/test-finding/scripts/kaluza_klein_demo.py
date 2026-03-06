#!/usr/bin/env python3
"""
Kaluza-Klein Theory Integration Demonstration

This script demonstrates the integration of Kaluza-Klein theory with the Z framework,
showing how the mass tower formula m_n = n/R relates to domain shifts Z = n(Δₙ/Δmax)
and provides quantum simulation of predicted observables.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Set matplotlib backend for headless environments
plt.switch_backend('Agg')

# Add core modules to path
sys.path.append(os.path.dirname(__file__))
from core.kaluza_klein import KaluzaKleinTower, create_unified_mass_domain_system
from applications.quantum_simulation import (
    simulate_kaluza_klein_observables, 
    visualize_kaluza_klein_spectrum,
    KaluzaKleinQuantumSimulator,
    ObservablePredictor
)

def demonstrate_mass_tower():
    """Demonstrate the basic Kaluza-Klein mass tower formula m_n = n/R."""
    print("\n" + "="*60)
    print("KALUZA-KLEIN MASS TOWER DEMONSTRATION")
    print("="*60)
    
    # Create Kaluza-Klein tower with Planck-scale compactification
    R = 1e-16  # meters, near Planck length
    kk_tower = KaluzaKleinTower(R)
    
    print(f"Compactification radius R = {R:.2e} meters")
    print(f"Mass tower formula: m_n = n / R")
    print()
    
    # Calculate masses for first few modes
    print("Mode | Mass (1/meters)  | Energy (at rest)")
    print("-" * 45)
    for n in range(1, 11):
        mass = kk_tower.mass_tower(n)
        energy = kk_tower.energy_tower(n)
        print(f"{n:4d} | {float(mass):12.2e} | {float(energy):12.2e}")
    
    return kk_tower

def demonstrate_domain_shift_integration(kk_tower):
    """Demonstrate integration with domain shifts Z = n(Δₙ/Δmax)."""
    print("\n" + "="*60)
    print("DOMAIN SHIFT INTEGRATION")
    print("="*60)
    
    print("Relating Kaluza-Klein masses to Z framework domain shifts:")
    print("Z = n(Δₙ/Δmax) where Δₙ incorporates both curvature and mass effects")
    print()
    
    print("Mode | Mass m_n     | Domain Shift Δₙ | Z Value")
    print("-" * 55)
    
    masses = []
    domain_shifts = []
    z_values = []
    
    for n in range(1, 11):
        mass = kk_tower.mass_tower(n)
        delta_n, z_val = kk_tower.domain_shift_relation(n)
        
        masses.append(float(mass))
        domain_shifts.append(float(delta_n))
        z_values.append(float(z_val))
        
        print(f"{n:4d} | {float(mass):11.2e} | {float(delta_n):14.6f} | {float(z_val):7.4f}")
    
    # Compute correlations
    correlation_mass_domain = np.corrcoef(masses, domain_shifts)[0, 1]
    correlation_mass_z = np.corrcoef(masses, z_values)[0, 1]
    
    print()
    print(f"Correlation (mass, domain shift): {correlation_mass_domain:.4f}")
    print(f"Correlation (mass, Z value):      {correlation_mass_z:.4f}")
    
    return masses, domain_shifts, z_values

def demonstrate_quantum_simulation():
    """Demonstrate quantum simulation of Kaluza-Klein observables."""
    print("\n" + "="*60)
    print("QUANTUM SIMULATION OF OBSERVABLES")
    print("="*60)
    
    print("Simulating quantum observables for different Kaluza-Klein masses...")
    
    # Run comprehensive simulation
    results = simulate_kaluza_klein_observables(
        compactification_radius=1e-16,
        n_modes=8,
        evolution_time=0.5,
        n_time_steps=50
    )
    
    print("✓ Simulation completed")
    
    # Display key results
    eigenvalues = results['energy_spectrum']['eigenvalues']
    position_obs = results['observables']['position']
    energy_obs = results['observables']['energy']
    
    print(f"\nEnergy eigenvalues (first 5): {eigenvalues[:5]}")
    print(f"Position observables: {dict(list(position_obs.items())[:5])}")
    print(f"Energy observables: {dict(list(energy_obs.items())[:5])}")
    
    # Generate visualization
    visualize_kaluza_klein_spectrum(results, 'kaluza_klein_demonstration.png')
    print("✓ Visualization saved to kaluza_klein_demonstration.png")
    
    return results

def demonstrate_unified_system():
    """Demonstrate the unified mass-domain system."""
    print("\n" + "="*60)
    print("UNIFIED MASS-DOMAIN SYSTEM")
    print("="*60)
    
    print("Creating unified system combining Kaluza-Klein theory with Z framework...")
    
    # Create unified system
    system = create_unified_mass_domain_system(
        compactification_radius=1e-16,
        mode_range=(1, 15)
    )
    
    print("✓ Unified system created")
    
    # Display system properties
    correlations = system['correlations']
    stats = system['summary_stats']
    
    print(f"\nSystem correlations:")
    print(f"  Mass ↔ Domain Shift:  {correlations['mass_domain_correlation']:.4f}")
    print(f"  Mass ↔ Z Value:       {correlations['mass_Z_correlation']:.4f}")
    print(f"  Domain ↔ Z Value:     {correlations['domain_Z_correlation']:.4f}")
    
    print(f"\nSystem statistics:")
    print(f"  Total modes:          {stats['total_modes']}")
    print(f"  Mass range:           {stats['mass_range'][0]:.2e} to {stats['mass_range'][1]:.2e}")
    print(f"  Domain shift range:   {stats['domain_shift_range'][0]:.4f} to {stats['domain_shift_range'][1]:.4f}")
    print(f"  Z value range:        {stats['Z_value_range'][0]:.4f} to {stats['Z_value_range'][1]:.4f}")
    
    return system

def create_comparison_plot(system, results):
    """Create a comparison plot showing the integration."""
    print("\n" + "="*60)
    print("CREATING COMPREHENSIVE COMPARISON PLOT")
    print("="*60)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Extract data
    spectrum = system['spectrum']
    modes = [s['n'] for s in spectrum]
    masses = [float(s['mass']) for s in spectrum]
    domain_shifts = [float(s['delta_n']) for s in spectrum]
    z_values = [float(s['Z_value']) for s in spectrum]
    energies = [float(s['energy']) for s in spectrum]
    
    # Plot 1: Mass tower
    axes[0, 0].semilogy(modes, masses, 'bo-', linewidth=2, markersize=6)
    axes[0, 0].set_xlabel('Mode number n')
    axes[0, 0].set_ylabel('Mass m_n = n/R')
    axes[0, 0].set_title('Kaluza-Klein Mass Tower')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Domain shifts
    axes[0, 1].plot(modes, domain_shifts, 'ro-', linewidth=2, markersize=6)
    axes[0, 1].set_xlabel('Mode number n')
    axes[0, 1].set_ylabel('Domain shift Δₙ')
    axes[0, 1].set_title('Domain Shifts with Mass Coupling')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Z framework values
    axes[0, 2].plot(modes, z_values, 'go-', linewidth=2, markersize=6)
    axes[0, 2].set_xlabel('Mode number n')
    axes[0, 2].set_ylabel('Z = n(Δₙ/Δₘₐₓ)')
    axes[0, 2].set_title('Z Framework Integration')
    axes[0, 2].grid(True, alpha=0.3)
    
    # Plot 4: Mass vs Domain shift correlation
    axes[1, 0].scatter(masses, domain_shifts, c=modes, cmap='viridis', s=80)
    axes[1, 0].set_xlabel('Mass m_n')
    axes[1, 0].set_ylabel('Domain shift Δₙ')
    axes[1, 0].set_title('Mass-Domain Correlation')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 5: Energy spectrum
    quantum_energies = results['energy_spectrum']['eigenvalues'][:len(modes)]
    axes[1, 1].semilogy(modes[:len(quantum_energies)], quantum_energies, 'mo-', linewidth=2, markersize=6)
    axes[1, 1].set_xlabel('Mode number n')
    axes[1, 1].set_ylabel('Quantum Energy Eigenvalue')
    axes[1, 1].set_title('Quantum Energy Spectrum')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Plot 6: Cross-correlation matrix
    corr_data = np.array([
        [1.0, system['correlations']['mass_domain_correlation'], system['correlations']['mass_Z_correlation']],
        [system['correlations']['mass_domain_correlation'], 1.0, system['correlations']['domain_Z_correlation']],
        [system['correlations']['mass_Z_correlation'], system['correlations']['domain_Z_correlation'], 1.0]
    ])
    
    im = axes[1, 2].imshow(corr_data, cmap='RdBu_r', vmin=-1, vmax=1)
    axes[1, 2].set_xticks([0, 1, 2])
    axes[1, 2].set_yticks([0, 1, 2])
    axes[1, 2].set_xticklabels(['Mass', 'Domain', 'Z-value'])
    axes[1, 2].set_yticklabels(['Mass', 'Domain', 'Z-value'])
    axes[1, 2].set_title('Cross-Correlations')
    
    # Add correlation values as text
    for i in range(3):
        for j in range(3):
            axes[1, 2].text(j, i, f'{corr_data[i, j]:.3f}', 
                           ha='center', va='center', color='white', fontweight='bold')
    
    plt.colorbar(im, ax=axes[1, 2])
    plt.tight_layout()
    plt.savefig('kaluza_klein_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Comprehensive analysis plot saved to kaluza_klein_comprehensive_analysis.png")
    plt.close()

def main():
    """Main demonstration function."""
    print("KALUZA-KLEIN THEORY INTEGRATION WITH Z FRAMEWORK")
    print("=" * 70)
    print("Demonstrating the implementation of m_n = n/R mass tower formula")
    print("and its integration with domain shifts Z = n(Δₙ/Δmax)")
    print("=" * 70)
    
    # Step 1: Demonstrate mass tower
    kk_tower = demonstrate_mass_tower()
    
    # Step 2: Demonstrate domain shift integration
    masses, domain_shifts, z_values = demonstrate_domain_shift_integration(kk_tower)
    
    # Step 3: Demonstrate quantum simulation
    quantum_results = demonstrate_quantum_simulation()
    
    # Step 4: Demonstrate unified system
    unified_system = demonstrate_unified_system()
    
    # Step 5: Create comprehensive comparison plot
    create_comparison_plot(unified_system, quantum_results)
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("✓ Kaluza-Klein mass tower formula m_n = n/R implemented")
    print("✓ Domain shift integration Z = n(Δₙ/Δmax) established") 
    print("✓ Quantum simulations of observables completed")
    print("✓ Unified mass-domain system created")
    print("✓ Comprehensive visualizations generated")
    print()
    print("Generated files:")
    print("  - kaluza_klein_demonstration.png")
    print("  - kaluza_klein_comprehensive_analysis.png")
    print("  - kaluza_klein_spectrum.png")
    print()
    print("The implementation successfully bridges Kaluza-Klein theory")
    print("with the existing Z framework, enabling quantum simulations")
    print("of predicted observables for different masses m_n.")

if __name__ == "__main__":
    main()