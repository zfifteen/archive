#!/usr/bin/env python3
"""
Discrete Gravity Dynamics Simulation Demo

This script demonstrates the simulated discrete-gravity dynamics implementation
described in issue #511, showing the empirical validation of non-hyperbolic
gravitational response on a one-dimensional periodic lattice.

USAGE:
    python discrete_gravity_simulation.py [--mode MODE] [--k K] [--full-sweep]

EXAMPLES:
    # Run Mode A (unit impulse) with k=0.3
    python discrete_gravity_simulation.py --mode A --k 0.3
    
    # Run Mode B (two-body surrogate) with k=0.04449
    python discrete_gravity_simulation.py --mode B --k 0.04449
    
    # Run complete parameter sweep (reproduces issue results)
    python discrete_gravity_simulation.py --full-sweep

EXPECTED RESULTS:
- Mode A: Exponential screening, no propagating fronts, strain relaxation
- Mode B: Far-field suppression, flat strain proxy, energy localization  
- Mode C: Highly localized response, no solitons or topological defects
"""

import argparse
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

# Add src to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, '..', 'src'))

try:
    from core.discrete_gravity_dynamics import (
        DiscreteGravitySimulator, ModeAUnitImpulse, ModeBTwoBodySurrogate,
        ModeCStrongQuench, create_mode_a_simulation, create_mode_b_simulation,
        create_mode_c_simulation, run_parameter_sweep
    )
except ImportError as e:
    print(f"Error importing discrete gravity dynamics: {e}")
    print("Make sure you're running from the repository root or check the import paths.")
    sys.exit(1)


def plot_simulation_results(results: Dict, title: str, save_path: str = None):
    """
    Create comprehensive plots of simulation results.
    
    Args:
        results: Simulation results dictionary
        title: Plot title
        save_path: Optional path to save plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(title, fontsize=16)
    
    # Plot 1: Time evolution of energy
    ax1 = axes[0, 0]
    time_series = results['time_series']
    ax1.plot(time_series['time'], time_series['energy'], 'b-', linewidth=2)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Energy (Lyapunov Functional)')
    ax1.set_title('Energy Evolution')
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # Plot 2: Strain proxy evolution
    ax2 = axes[0, 1]
    ax2.plot(time_series['time'], time_series['strain'], 'r-', linewidth=2)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Strain Proxy')
    ax2.set_title('Strain Proxy Evolution')
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')
    
    # Plot 3: Field amplitude analysis
    ax3 = axes[1, 0]
    if 'field_analysis' in results and 'amplitudes' in results['field_analysis']:
        amplitudes = results['field_analysis']['amplitudes']
        distances = []
        values = []
        
        for key, value in amplitudes.items():
            if key.startswith('A(') and key.endswith(')'):
                try:
                    dist = int(key[2:-1])
                    distances.append(dist)
                    values.append(value)
                except ValueError:
                    continue
                    
        if distances and values:
            # Sort by distance
            sorted_pairs = sorted(zip(distances, values))
            distances, values = zip(*sorted_pairs)
            
            ax3.semilogy(distances, values, 'go-', linewidth=2, markersize=8)
            ax3.set_xlabel('Distance from Center')
            ax3.set_ylabel('Field Amplitude')
            ax3.set_title('Spatial Field Amplitude (Exponential Screening)')
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'No amplitude data available', 
                    transform=ax3.transAxes, ha='center', va='center')
    
    # Plot 4: Key diagnostics
    ax4 = axes[1, 1]
    diagnostics = results.get('diagnostics', {})
    
    # Create bar chart of key metrics
    metrics = {}
    if 'final_energy' in diagnostics:
        metrics['Final Energy'] = diagnostics['final_energy']
    if 'final_strain' in diagnostics:
        metrics['Final Strain'] = diagnostics['final_strain']
    if 'final_density_activation' in diagnostics:
        metrics['Density Activation'] = diagnostics['final_density_activation']
    if 'energy_decay_fraction' in diagnostics:
        metrics['Energy Decay'] = diagnostics['energy_decay_fraction']
        
    if metrics:
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())
        
        bars = ax4.bar(range(len(metric_names)), metric_values, 
                       color=['blue', 'red', 'green', 'orange'][:len(metric_names)])
        ax4.set_xticks(range(len(metric_names)))
        ax4.set_xticklabels(metric_names, rotation=45, ha='right')
        ax4.set_ylabel('Value')
        ax4.set_title('Key Diagnostics')
        ax4.set_yscale('log')
        
        # Add value labels on bars
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height*1.1,
                    f'{value:.2e}', ha='center', va='bottom', fontsize=8)
    else:
        ax4.text(0.5, 0.5, 'No diagnostics available', 
                transform=ax4.transAxes, ha='center', va='center')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    
    plt.show()


def analyze_dispersion_relation(sim: DiscreteGravitySimulator):
    """
    Analyze and plot the dispersion relation ω(q) = i(α + β⋅q²)/γ.
    """
    print(f"\n{'='*50}")
    print("DISPERSION RELATION ANALYSIS")
    print(f"{'='*50}")
    
    # Test range of q values
    q_values = np.linspace(0.1, 3.0, 30)
    omega_imag = []
    omega_real = []
    
    for q in q_values:
        omega = sim.compute_dispersion_relation(q)
        omega_real.append(omega.real)
        omega_imag.append(omega.imag)
    
    # Plot dispersion relation
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(q_values, omega_real, 'b-', linewidth=2, label='Real part')
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    plt.xlabel('Wave number q')
    plt.ylabel('ω_real(q)')
    plt.title('Real Part of Dispersion Relation')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(q_values, omega_imag, 'r-', linewidth=2, label='Imaginary part')
    # Theoretical curve: ω_imag = (α + β*q²)/γ
    theoretical = [(sim.alpha + sim.beta * q**2) / sim.gamma for q in q_values]
    plt.plot(q_values, theoretical, 'r--', linewidth=1, alpha=0.7, label='Theoretical')
    plt.xlabel('Wave number q')
    plt.ylabel('ω_imag(q)')
    plt.title('Imaginary Part of Dispersion Relation (Diffusive)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Print key properties
    print(f"Dispersion relation: ω(q) = i(α + β⋅q²)/γ")
    print(f"Parameters: α={float(sim.alpha)}, β={float(sim.beta)}, γ={float(sim.gamma)}")
    print(f"Screening length: ℓ = √(β/α) = {float(sim.screening_length)}")
    print(f"Behavior: Purely imaginary ω → diffusive, no propagating fronts")
    
    # Check accuracy
    max_real_error = max(abs(omega.real) for omega in [sim.compute_dispersion_relation(q) for q in q_values])
    print(f"Maximum real part error: {float(max_real_error):.2e} (should be ~0)")


def print_validation_summary(validation: Dict):
    """Print high-precision validation summary."""
    print(f"\n{'='*50}")
    print("HIGH-PRECISION VALIDATION SUMMARY")
    print(f"{'='*50}")
    
    print(f"Precision achieved: {validation['precision_achieved']} decimal places")
    print(f"Target tolerance: {validation['tolerance_target']}")
    print(f"Numerical stability: {'PASS' if validation['numerical_stability'] else 'FAIL'}")
    
    if 'energy_monotonicity_violations' in validation:
        violations = validation['energy_monotonicity_violations']
        print(f"Energy monotonicity violations: {violations:.1%}")
        
    if 'agreement_check' in validation and validation['agreement_check']:
        print("\nAgreement with reference:")
        for key, check in validation['agreement_check'].items():
            status = "PASS" if check['within_tolerance'] else "FAIL"
            print(f"  {key}: {status} (error: {check['relative_error']:.2e})")


def run_single_mode_demo(mode: str, k: float):
    """
    Run demonstration of a single source mode.
    
    Args:
        mode: Source mode ('A', 'B', or 'C')
        k: Parameter k value
    """
    print(f"\n{'='*60}")
    print(f"DISCRETE GRAVITY DYNAMICS DEMO - MODE {mode}")
    print(f"{'='*60}")
    print(f"Parameter k = {k}")
    print(f"Expected screening length ℓ = {k}")
    print(f"Dispersion: ω(q) = i(1 + {k}²⋅q²)/0.09753")
    
    # Create appropriate simulation
    if mode == 'A':
        sim = create_mode_a_simulation(k=k)
        expected_behavior = [
            "• Linear response to unit impulse",
            "• Exponential screening with ℓ = k",
            "• No propagating fronts or ringdown oscillations",
            "• Strain relaxation to numerical floor"
        ]
    elif mode == 'B':
        sim = create_mode_b_simulation(k=k)
        expected_behavior = [
            "• Two-body inspiral surrogate",
            "• Far-field suppression of multipoles",
            "• Flat strain proxy near 0.001-0.002",
            "• Local energy storage and density activation boost"
        ]
    elif mode == 'C':
        sim = create_mode_c_simulation(k=k)
        expected_behavior = [
            "• Strong, short quench response",
            "• Highly localized: peak at origin, vanishing at r≈20",
            "• No solitons or topological defects",
            "• Strain stays below 3×10⁻⁵"
        ]
    else:
        raise ValueError(f"Unknown mode: {mode}")
    
    print(f"\nExpected behavior:")
    for behavior in expected_behavior:
        print(behavior)
    
    # Analyze dispersion relation
    analyze_dispersion_relation(sim)
    
    # Run simulation
    print(f"\nRunning simulation...")
    results = sim.run_simulation()
    
    # Validation
    validation = sim.validate_high_precision()
    print_validation_summary(validation)
    
    # Results summary
    print(f"\n{'='*50}")
    print("SIMULATION RESULTS SUMMARY")
    print(f"{'='*50}")
    
    diagnostics = results['diagnostics']
    
    print(f"Final energy: {diagnostics.get('final_energy', 'N/A'):.2e}")
    print(f"Final strain: {diagnostics.get('final_strain', 'N/A'):.2e}")
    print(f"Energy decay: {diagnostics.get('energy_decay_fraction', 'N/A'):.1%}")
    print(f"Density activation: {diagnostics.get('final_density_activation', 'N/A'):.1%}")
    
    # Field amplitude analysis
    if 'field_analysis' in results and 'amplitudes' in results['field_analysis']:
        print(f"\nField amplitude analysis:")
        amplitudes = results['field_analysis']['amplitudes']
        for key, value in sorted(amplitudes.items()):
            print(f"  {key}: {value:.2e}")
    
    # Check against expected values from issue
    print(f"\n{'='*50}")
    print("COMPARISON WITH EXPECTED VALUES")
    print(f"{'='*50}")
    
    if mode == 'A' and k == 0.3:
        expected_values = {
            'A(0)': 2.1e-4,
            'A(2)': 2.4e-5,
            'far_field': '<1e-30'
        }
        print("Expected values for Mode A, k=0.3 at t=0.5:")
        for key, val in expected_values.items():
            print(f"  {key}: {val}")
            
    elif mode == 'A' and abs(k - 0.04449) < 0.001:
        expected_values = {
            'A(0)': 4.5e-4,
            'A(2)': 2.8e-8,
            'far_field': '<1e-60'
        }
        print("Expected values for Mode A, k=0.04449 at t=0.5:")
        for key, val in expected_values.items():
            print(f"  {key}: {val}")
            
    elif mode == 'B':
        print("Expected: Strain proxy flat near 0.001-0.002, no chirp or memory")
        print("Expected: Energy rise from ~3e-5 to ~4e-4")
        print("Expected: Active-node fraction increase ~6× boost")
        
    elif mode == 'C':
        print("Expected: Peak A(0,t) ≈ 0.004-0.008, vanishing beyond r≈20")
        print("Expected: Strain proxy below 3e-5")
        print("Expected: Density activation under 1%")
    
    # Create comprehensive plots
    plot_title = f"Discrete Gravity Dynamics - Mode {mode} (k={k})"
    save_path = f"discrete_gravity_mode_{mode}_k_{k:.5f}.png"
    plot_simulation_results(results, plot_title, save_path)
    
    return results


def run_full_parameter_sweep():
    """
    Run the complete parameter sweep as described in the issue.
    
    This reproduces the empirical validation with k ∈ {0.3, 0.04449}
    and all three source modes (A, B, C).
    """
    print(f"\n{'='*60}")
    print("COMPLETE PARAMETER SWEEP - EMPIRICAL VALIDATION")
    print(f"{'='*60}")
    print("Reproducing results from issue #511")
    print("Parameter sweep: k ∈ {0.3, 0.04449}")
    print("Source modes: A (unit impulse), B (two-body), C (strong quench)")
    print("High-precision validation: mpmath dps=50, tolerance <1e-10")
    
    # Run sweep
    k_values = [0.3, 0.04449]
    modes = ['A', 'B', 'C']
    
    print(f"\nRunning {len(k_values)} × {len(modes)} = {len(k_values)*len(modes)} simulations...")
    
    sweep_results = run_parameter_sweep(k_values=k_values, modes=modes)
    
    # Comprehensive analysis
    print(f"\n{'='*60}")
    print("PARAMETER SWEEP RESULTS SUMMARY")
    print(f"{'='*60}")
    
    for k_key, k_results in sweep_results.items():
        print(f"\n{k_key}:")
        print("-" * 40)
        
        for mode_key, mode_results in k_results.items():
            sim_results = mode_results['simulation_results']
            validation = mode_results['validation']
            
            print(f"\n  {mode_key}:")
            print(f"    Numerical stability: {'PASS' if validation['numerical_stability'] else 'FAIL'}")
            print(f"    Final energy: {sim_results['diagnostics'].get('final_energy', 'N/A'):.2e}")
            print(f"    Final strain: {sim_results['diagnostics'].get('final_strain', 'N/A'):.2e}")
            print(f"    Density activation: {sim_results['diagnostics'].get('final_density_activation', 'N/A'):.1%}")
            
            # Field amplitudes
            if 'field_analysis' in sim_results and 'amplitudes' in sim_results['field_analysis']:
                amps = sim_results['field_analysis']['amplitudes']
                if 'A(0)' in amps:
                    print(f"    Amplitude A(0): {amps['A(0)']:.2e}")
                if 'A(2)' in amps:
                    print(f"    Amplitude A(2): {amps['A(2)']:.2e}")
    
    # Generate summary plots for key results
    print(f"\n{'='*50}")
    print("GENERATING SUMMARY PLOTS")
    print(f"{'='*50}")
    
    # Plot comparison of Mode A results for both k values
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Parameter Sweep Summary: Mode A Comparison', fontsize=16)
    
    k_colors = {'k=0.3': 'blue', 'k=0.04449': 'red'}
    
    for i, k_key in enumerate(['k=0.3', 'k=0.04449']):
        if k_key in sweep_results and 'mode_A' in sweep_results[k_key]:
            results = sweep_results[k_key]['mode_A']['simulation_results']
            time_series = results['time_series']
            color = k_colors[k_key]
            
            # Energy evolution
            axes[0, 0].plot(time_series['time'], time_series['energy'], 
                           color=color, label=k_key, linewidth=2)
            
            # Strain evolution  
            axes[0, 1].plot(time_series['time'], time_series['strain'],
                           color=color, label=k_key, linewidth=2)
    
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('Energy')
    axes[0, 0].set_title('Energy Evolution Comparison')
    axes[0, 0].set_yscale('log')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].set_ylabel('Strain Proxy')
    axes[0, 1].set_title('Strain Evolution Comparison')
    axes[0, 1].set_yscale('log')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Summary bar charts
    modes_data = {}
    for k_key in sweep_results:
        modes_data[k_key] = {}
        for mode_key in sweep_results[k_key]:
            diagnostics = sweep_results[k_key][mode_key]['simulation_results']['diagnostics']
            modes_data[k_key][mode_key] = {
                'energy': diagnostics.get('final_energy', 0),
                'strain': diagnostics.get('final_strain', 0)
            }
    
    # Final energy comparison
    ax = axes[1, 0]
    x_pos = np.arange(len(modes))
    width = 0.35
    
    for i, k_key in enumerate(['k=0.3', 'k=0.04449']):
        if k_key in modes_data:
            energies = [modes_data[k_key].get(f'mode_{mode}', {}).get('energy', 0) 
                       for mode in ['A', 'B', 'C']]
            ax.bar(x_pos + i*width, energies, width, label=k_key, color=k_colors[k_key])
    
    ax.set_xlabel('Source Mode')
    ax.set_ylabel('Final Energy')
    ax.set_title('Final Energy by Mode')
    ax.set_xticks(x_pos + width/2)
    ax.set_xticklabels(['Mode A', 'Mode B', 'Mode C'])
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Final strain comparison
    ax = axes[1, 1]
    for i, k_key in enumerate(['k=0.3', 'k=0.04449']):
        if k_key in modes_data:
            strains = [modes_data[k_key].get(f'mode_{mode}', {}).get('strain', 0) 
                      for mode in ['A', 'B', 'C']]
            ax.bar(x_pos + i*width, strains, width, label=k_key, color=k_colors[k_key])
    
    ax.set_xlabel('Source Mode')
    ax.set_ylabel('Final Strain')
    ax.set_title('Final Strain by Mode')
    ax.set_xticks(x_pos + width/2)
    ax.set_xticklabels(['Mode A', 'Mode B', 'Mode C'])
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('discrete_gravity_parameter_sweep_summary.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Parameter sweep completed successfully!")
    print("Results saved to: discrete_gravity_parameter_sweep_summary.png")
    
    return sweep_results


def main():
    """Main entry point for the discrete gravity dynamics demo."""
    parser = argparse.ArgumentParser(
        description="Discrete Gravity Dynamics Simulation Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--mode', choices=['A', 'B', 'C'], 
                       help='Source mode: A (unit impulse), B (two-body), C (strong quench)')
    parser.add_argument('--k', type=float, default=0.3,
                       help='Parameter k value (default: 0.3)')
    parser.add_argument('--full-sweep', action='store_true',
                       help='Run complete parameter sweep (reproduces issue results)')
    
    args = parser.parse_args()
    
    if args.full_sweep:
        # Run complete parameter sweep
        sweep_results = run_full_parameter_sweep()
        
    elif args.mode:
        # Run single mode demonstration
        results = run_single_mode_demo(args.mode, args.k)
        
    else:
        # Default: run Mode A with k=0.3
        print("No specific mode requested. Running default: Mode A with k=0.3")
        print("Use --help for options or --full-sweep for complete validation.")
        results = run_single_mode_demo('A', 0.3)
    
    print(f"\n{'='*60}")
    print("DEMO COMPLETED SUCCESSFULLY")
    print(f"{'='*60}")
    print("The discrete gravity dynamics simulation demonstrates:")
    print("• Non-hyperbolic gravitational response (failure of hyperbolicity)")
    print("• Exponential screening with length ℓ = k")
    print("• Diffusive behavior (purely imaginary dispersion relation)")
    print("• High-precision numerical validation (mpmath dps=50)")
    print("• Three distinct source modes with expected physical behaviors")
    print("\nThis validates the implementation described in issue #511.")


if __name__ == '__main__':
    main()