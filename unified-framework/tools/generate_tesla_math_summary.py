#!/usr/bin/env python3
"""
Tesla Math Falsification Summary Generator
==========================================

Generates a comprehensive summary of the Tesla Math falsification experiment
including key results, statistical analysis, and conclusions.

Usage:
    python generate_tesla_math_summary.py

Output:
    - Experimental results printed to console
    - Results saved to tesla_math_results.json
    - Summary added to white paper

Author: Z Framework Research Team
Date: 2024
"""

import json
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from experiments.tesla_math_falsification import TeslaMathExperiment


def generate_summary():
    """Generate comprehensive experimental summary."""
    print("Tesla Math Efficiency Falsification Experiment")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run experiment
    print("Running scientific falsification experiment...")
    experiment = TeslaMathExperiment(random_seed=42)
    results = experiment.run_full_experiment()
    
    print("\n" + "=" * 60)
    print("SCIENTIFIC SUMMARY")
    print("=" * 60)
    
    # Extract key findings
    triangle_results = results['hypothesis_tests']['triangle_filter']
    zeta_results = results['hypothesis_tests']['discrete_zeta_shift']
    efficiency_results = results['hypothesis_tests']['overall_efficiency']
    
    # Primary findings
    print("\n1. TRIANGLE FILTER ANALYSIS")
    print("-" * 30)
    print(f"   • Mean Tesla capture rate: {triangle_results['mean_tesla_capture']:.1f}%")
    print(f"   • Mean random capture rate: {triangle_results['mean_random_capture']:.1f}%")
    print(f"   • Claimed 70% threshold: {'✓ MET' if triangle_results['meets_70_percent_claim'] else '✗ FAILED'}")
    print(f"   • Statistical significance: p = {triangle_results['p_value']:.3f}")
    print(f"   • H₀ (Tesla ≤ Random): {'REJECTED' if triangle_results['h0_rejected'] else 'NOT REJECTED'}")
    
    print("\n2. DISCRETE ZETA SHIFT ANALYSIS")
    print("-" * 35)
    print(f"   • Mean Tesla variance: {zeta_results['mean_tesla_variance']:.3f}")
    print(f"   • Mean linear variance: {zeta_results['mean_linear_variance']:.3f}")
    print(f"   • Variance improvement: {zeta_results['variance_improvement']:.1f}×")
    print(f"   • Statistical significance: p = {zeta_results['p_value']:.3f}")
    print(f"   • H₀ (Tesla ≤ Linear): {'REJECTED' if zeta_results['h0_rejected'] else 'NOT REJECTED'}")
    
    print("\n3. COMPUTATIONAL EFFICIENCY")
    print("-" * 30)
    print(f"   • Triangle vs Random efficiency: {efficiency_results['triangle_vs_random']:.2f}×")
    print(f"   • Time vs Sieve efficiency: {efficiency_results['time_vs_sieve']:.2f}×")
    print(f"   • Overall efficiency gains: {'✓ DETECTED' if efficiency_results['has_efficiency_gains'] else '✗ NOT DETECTED'}")
    
    # Scientific conclusion
    hypothesis_supported = (
        triangle_results['h0_rejected'] and 
        triangle_results['meets_70_percent_claim'] and
        zeta_results['h0_rejected'] and 
        efficiency_results['has_efficiency_gains']
    )
    
    print("\n" + "=" * 60)
    print("SCIENTIFIC CONCLUSION")
    print("=" * 60)
    
    if hypothesis_supported:
        conclusion = "HYPOTHESIS SUPPORTED"
        verdict = "Tesla Math demonstrates statistically significant efficiency gains."
        color = "GREEN"
    else:
        conclusion = "HYPOTHESIS FALSIFIED"
        verdict = "Tesla Math fails to demonstrate meaningful efficiency gains."
        color = "RED"
    
    print(f"\n**{conclusion}**")
    print(f"\n{verdict}")
    
    # Detailed breakdown
    print(f"\nEvidence Summary:")
    print(f"• Triangle Filter 70% claim: {'✓' if triangle_results['meets_70_percent_claim'] else '✗'}")
    print(f"• Triangle Filter superiority: {'✓' if triangle_results['h0_rejected'] else '✗'}")
    print(f"• Zeta Shift superiority: {'✓' if zeta_results['h0_rejected'] else '✗'}")
    print(f"• Computational efficiency: {'✓' if efficiency_results['has_efficiency_gains'] else '✗'}")
    
    # Research implications
    print(f"\nResearch Implications:")
    if hypothesis_supported:
        print("• Tesla Math patterns warrant further scientific investigation")
        print("• Vortex mathematics may contain undiscovered computational insights")
        print("• Applications in prime theory and number-theoretic algorithms")
    else:
        print("• Tesla Math does not provide practical computational benefits")
        print("• Vortex mathematics patterns lack algorithmic utility")
        print("• Standard mathematical methods remain superior")
    
    print(f"\nReproducibility:")
    params = results['experimental_parameters']
    print(f"• Random seed: {params['random_seed']}")
    print(f"• Test scales: n={params['n_values']}, k={params['k_values']}")
    print(f"• Bootstrap samples: {params['n_bootstrap']}")
    print(f"• All code available in /src/experiments/tesla_math_falsification.py")
    
    # Save results to JSON
    output_file = "tesla_math_experimental_results.json"
    with open(output_file, 'w') as f:
        # Convert numpy types to Python types for JSON serialization
        json_results = json.loads(json.dumps(results, default=str))
        json.dump(json_results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    
    return results, conclusion


def main():
    """Main execution function."""
    try:
        results, conclusion = generate_summary()
        
        # Return appropriate exit code
        if conclusion == "HYPOTHESIS SUPPORTED":
            return 0  # Success: hypothesis supported
        else:
            return 1  # Success: hypothesis falsified (this is the expected outcome)
            
    except Exception as e:
        print(f"Error running experiment: {e}")
        return 2  # Error


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)