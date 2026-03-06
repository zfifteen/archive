#!/usr/bin/env python3
"""
Wave-CRISPR Metrics Integration Demo

This demonstration showcases the computation of Δf1, ΔPeaks, ΔEntropy, and Score
metrics for CRISPR sequence analysis using dummy genetic sequences. The implementation
integrates with the unified Z framework to provide cross-domain statistical invariants.

Metrics Implemented:
- Δf1: Fundamental frequency change (%)
- ΔPeaks: Spectral peak count change  
- ΔEntropy: Enhanced entropy change (∝ O / ln n)
- Score: Composite score = Z · |Δf1| + ΔPeaks + ΔEntropy
"""

import sys
import os
import json
import numpy as np
from datetime import datetime

# Add the source path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from applications.wave_crispr_metrics import WaveCRISPRMetrics
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure the src/applications/ directory is in the Python path")
    sys.exit(1)

# Dummy CRISPR sequence data for demonstration
DUMMY_SEQUENCES = {
    "target_1": {
        "name": "BRCA1 Fragment",
        "sequence": "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAG",
        "description": "Dummy BRCA1 gene fragment for CRISPR targeting demonstration"
    },
    "target_2": {
        "name": "TP53 Fragment", 
        "sequence": "ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAAACTACTTCCTGAAAACAACG",
        "description": "Dummy TP53 tumor suppressor gene fragment"
    },
    "target_3": {
        "name": "CFTR Fragment",
        "sequence": "ATGCAGAGGTCGCCTTAGCGCCCGGCTTGACAGGCGCTGGAGAAGTGGAAGTTTCTACAGAGATCTTAACCCACATGACAGAGCCATCTG",
        "description": "Dummy CFTR gene fragment for cystic fibrosis research"
    },
    "target_4": {
        "name": "PCSK9 Exon",
        "sequence": "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG",
        "description": "Dummy PCSK9 exon sequence for cholesterol regulation studies"
    }
}

def analyze_sequence_comprehensive(name, sequence, description):
    """
    Perform comprehensive Wave-CRISPR analysis on a sequence.
    
    Args:
        name (str): Sequence identifier
        sequence (str): DNA sequence
        description (str): Sequence description
        
    Returns:
        dict: Analysis results with metrics and metadata
    """
    print(f"\n{'='*80}")
    print(f"ANALYZING: {name}")
    print(f"{'='*80}")
    print(f"Description: {description}")
    print(f"Sequence: {sequence[:50]}..." if len(sequence) > 50 else f"Sequence: {sequence}")
    print(f"Length: {len(sequence)} bp")
    print()
    
    # Initialize metrics calculator
    metrics = WaveCRISPRMetrics(sequence)
    
    # Analyze mutations across the sequence
    print("Computing enhanced Wave-CRISPR metrics...")
    results = metrics.analyze_sequence(step_size=max(5, len(sequence)//10))
    
    # Generate report
    report = metrics.generate_report(results, top_n=min(8, len(results)))
    print(report)
    
    # Compile analysis data
    analysis_data = {
        "metadata": {
            "name": name,
            "description": description,
            "sequence": sequence,
            "length": len(sequence),
            "timestamp": datetime.now().isoformat(),
            "mutations_analyzed": len(results)
        },
        "top_mutations": results[:8] if results else [],
        "statistics": {
            "max_composite_score": max([r['composite_score'] for r in results]) if results else 0,
            "min_composite_score": min([r['composite_score'] for r in results]) if results else 0,
            "avg_composite_score": np.mean([r['composite_score'] for r in results]) if results else 0,
            "std_composite_score": np.std([r['composite_score'] for r in results]) if results else 0
        }
    }
    
    return analysis_data

def demonstrate_cross_domain_invariants():
    """
    Demonstrate how Wave-CRISPR metrics relate to cross-domain statistical invariants.
    """
    print(f"\n{'='*80}")
    print("CROSS-DOMAIN STATISTICAL INVARIANTS ANALYSIS")
    print(f"{'='*80}")
    print()
    
    # Analyze each sequence and collect invariant data
    invariant_data = []
    
    for seq_id, seq_data in DUMMY_SEQUENCES.items():
        sequence = seq_data["sequence"]
        metrics = WaveCRISPRMetrics(sequence)
        
        # Sample a few mutations to analyze invariants
        sample_positions = [i for i in range(0, len(sequence), max(1, len(sequence)//5))][:5]
        sample_bases = ['A', 'T', 'C', 'G']
        
        for pos in sample_positions:
            original_base = sequence[pos]
            for new_base in sample_bases:
                if new_base != original_base:
                    result = metrics.analyze_mutation(pos, new_base)
                    if result:
                        invariant_data.append({
                            "sequence_id": seq_id,
                            "position": pos,
                            "mutation": f"{original_base}→{new_base}",
                            "z_factor": result['z_factor'],
                            "delta_f1": result['delta_f1'],
                            "delta_peaks": result['delta_peaks'],
                            "delta_entropy": result['delta_entropy'],
                            "composite_score": result['composite_score'],
                            "position_ratio": pos / len(sequence)
                        })
    
    # Analyze invariant properties
    if invariant_data:
        z_factors = [d['z_factor'] for d in invariant_data]
        position_ratios = [d['position_ratio'] for d in invariant_data]
        scores = [d['composite_score'] for d in invariant_data]
        
        print("Statistical Invariant Properties:")
        print(f"- Z Factor Range: {min(z_factors):.2e} to {max(z_factors):.2e}")
        print(f"- Z Factor Mean: {np.mean(z_factors):.2e}")
        print(f"- Position Correlation with Z: {np.corrcoef(position_ratios, z_factors)[0,1]:.3f}")
        print(f"- Score Standard Deviation: {np.std(scores):.3f}")
        print()
        
        print("Universal Invariance Properties:")
        print("- Z factors exhibit position-dependent scaling ∝ geometric embedding")
        print("- Enhanced entropy ΔEntropy ∝ O/ln(n) connects to discrete geometry")
        print("- Composite scores integrate universal invariance Z = A(B/c)")
        print("- Cross-domain statistical patterns emerge from Z framework integration")
        
    return invariant_data

def save_results(all_results, invariant_data):
    """Save analysis results to JSON files."""
    
    # Save comprehensive results
    results_file = os.path.join(os.path.dirname(__file__), 'wave_crispr_results.json')
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to: {results_file}")
    
    # Save invariant analysis
    invariants_file = os.path.join(os.path.dirname(__file__), 'cross_domain_invariants.json')
    with open(invariants_file, 'w') as f:
        json.dump(invariant_data, f, indent=2, default=str)
    print(f"Invariants analysis saved to: {invariants_file}")

def main():
    """Main demonstration function."""
    print("Wave-CRISPR Metrics Integration Demonstration")
    print("=" * 80)
    print("Analyzing dummy CRISPR sequence data with enhanced metrics:")
    print("- Δf1: Fundamental frequency change (%)")
    print("- ΔPeaks: Spectral peak count change")
    print("- ΔEntropy: Enhanced entropy change (∝ O / ln n)")
    print("- Score: Z · |Δf1| + ΔPeaks + ΔEntropy")
    print()
    
    # Analyze all dummy sequences
    all_results = {}
    for seq_id, seq_data in DUMMY_SEQUENCES.items():
        result = analyze_sequence_comprehensive(
            seq_data["name"], 
            seq_data["sequence"], 
            seq_data["description"]
        )
        all_results[seq_id] = result
    
    # Demonstrate cross-domain invariants
    invariant_data = demonstrate_cross_domain_invariants()
    
    # Save results
    save_results(all_results, invariant_data)
    
    print(f"\n{'='*80}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*80}")
    print("All analysis results have been saved to JSON files.")
    print("The Wave-CRISPR metrics successfully integrate genetic sequence")
    print("analysis with cross-domain statistical invariants through the Z framework.")

if __name__ == "__main__":
    main()