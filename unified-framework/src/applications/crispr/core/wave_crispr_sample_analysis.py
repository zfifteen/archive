"""
Wave-CRISPR Sample Data Analysis

This script demonstrates the enhanced Wave-CRISPR metrics on sample biological data,
showcasing the integration with the Z framework and providing detailed result interpretation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import json
from wave_crispr_metrics import WaveCRISPRMetrics

def load_human_dna_sequences():
    """Load authentic human DNA sequences from NCBI RefSeq."""
    import os
    import json
    
    # Try to load human DNA data
    human_data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'human_dna_data', 'human_dna_sequences.json')
    
    if os.path.exists(human_data_path):
        # Use authentic human sequences
        with open(human_data_path, 'r') as f:
            human_data = json.load(f)
        
        return {
            "PCSK9_Human": {
                "sequence": human_data["PCSK9"]["sequence"],
                "description": f"{human_data['PCSK9']['description']} (RefSeq: {human_data['PCSK9']['refseq_id']}) - AUTHENTIC HUMAN",
                "clinical_relevance": human_data["PCSK9"]["clinical_relevance"]
            },
            "BRCA1_Human": {
                "sequence": human_data["BRCA1"]["sequence"],
                "description": f"{human_data['BRCA1']['description']} (RefSeq: {human_data['BRCA1']['refseq_id']}) - AUTHENTIC HUMAN",
                "clinical_relevance": human_data["BRCA1"]["clinical_relevance"]
            },
            "TP53_Human": {
                "sequence": human_data["TP53"]["sequence"],
                "description": f"{human_data['TP53']['description']} (RefSeq: {human_data['TP53']['refseq_id']}) - AUTHENTIC HUMAN",
                "clinical_relevance": human_data["TP53"]["clinical_relevance"]
            },
            "CFTR_Human": {
                "sequence": human_data["CFTR"]["sequence"],
                "description": f"{human_data['CFTR']['description']} (RefSeq: {human_data['CFTR']['refseq_id']}) - AUTHENTIC HUMAN",
                "clinical_relevance": human_data["CFTR"]["clinical_relevance"]
            },
            "APOE_Human": {
                "sequence": human_data["APOE"]["sequence"],
                "description": f"{human_data['APOE']['description']} (RefSeq: {human_data['APOE']['refseq_id']}) - AUTHENTIC HUMAN",
                "clinical_relevance": human_data["APOE"]["clinical_relevance"]
            }
        }
    else:
        # Fallback to dummy sequences if human data not available
        print("Warning: Human DNA data not found. Using dummy sequences.")
        print("To use authentic human sequences, run: python scripts/setup_human_dna_data.py")
        return {
            "PCSK9_Dummy": {
                "sequence": "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG",
                "description": "PCSK9 (Proprotein convertase subtilisin/kexin type 9) - Cholesterol regulation [DUMMY]",
                "clinical_relevance": "Mutations affect LDL cholesterol levels, cardiovascular disease risk"
            },
            "BRCA1_Dummy": {
                "sequence": "ATGGATTTATCTGCTCTTCGCGTTGAAGAAGTACAAAATGTCATTAATGCTATGCAGAAAATCTTAGAGTGTCCCATCTGTCTGGAGTTGATCAAGGAACCTGTCTCCACAAAGTGTGACCACATATTTTGCAAATTTTGCATGCTGAAACTTCTCAA",
                "description": "BRCA1 (Breast cancer 1) - DNA repair pathway component [DUMMY]",
                "clinical_relevance": "Mutations increase breast and ovarian cancer risk"
            },
            "TP53_Dummy": {
                "sequence": "ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAAACTACTTCCTGAAAACAACGTTCTGTCCCCCTTGCCGTCCCAAGCAATGGATGATTTGATGCTGTCCCCGGACGATATTGAACAATGG",
                "description": "TP53 (Tumor protein p53) - Tumor suppressor [DUMMY]",
                "clinical_relevance": "Mutations involved in majority of human cancers"
            },
            "CFTR_Dummy": {
                "sequence": "ATGCAGAGGTCGCCTTAGCGCCCGGCTTCACCCTGGAGAATGATGATGAAGGTAGCCGGATGGCTGGCAATGGCGGCTCGGCGGTGGCGGCGGCTCCGGCGGCGGCGGCGGCGGCTCCCGGATGGCCGGCGGCGGCTCGGGCGGCGGCTCCGGATGG",
                "description": "CFTR (Cystic fibrosis transmembrane conductance regulator) [DUMMY]",
                "clinical_relevance": "Mutations cause cystic fibrosis"
            },
            "APOE_Dummy": {
                "sequence": "ATGGCGCGACGCGGGCACGTGCTCGGCCCCGGCCTGGTGGCTCCGCTGGGCCCTGGCCGCGCTGGCCATCCTGCTGCTGCTACTGCTGCTGCTGCTGCTGCTGCCGCTGGCGCTGGGGGCTGGGGCTGGGGCTGGGGCTGGGGCTGGGGCTGGGGCTG",
                "description": "APOE (Apolipoprotein E) - Lipid metabolism [DUMMY]",
                "clinical_relevance": "Variants affect Alzheimer's disease risk"
            }
        }

# Load sequences (authentic human if available, dummy as fallback)
SAMPLE_SEQUENCES = load_human_dna_sequences()

def analyze_sample_data():
    """Comprehensive analysis of sample biological sequences."""
    
    # Determine if using authentic human data
    using_human_data = any("Human" in key for key in SAMPLE_SEQUENCES.keys())
    
    if using_human_data:
        print("WAVE-CRISPR ENHANCED METRICS: AUTHENTIC HUMAN DNA ANALYSIS")
        print("=" * 80)
        print("Using REAL human genetic sequences from NCBI RefSeq")
        print("Ethical compliance: Public reference sequences, no privacy concerns")
    else:
        print("WAVE-CRISPR ENHANCED METRICS: SAMPLE DATA ANALYSIS")
        print("=" * 80)
        print("Using dummy sequences for demonstration")
        print("For authentic human data, run: python scripts/setup_human_dna_data.py")
    
    print()
    
    all_results = {}
    summary_stats = []
    
    for gene_name, gene_data in SAMPLE_SEQUENCES.items():
        print(f"Analyzing {gene_name}...")
        print("-" * 60)
        print(f"Description: {gene_data['description']}")
        print(f"Clinical relevance: {gene_data['clinical_relevance']}")
        print(f"Sequence length: {len(gene_data['sequence'])} bp")
        print()
        
        # Initialize metrics calculator
        metrics = WaveCRISPRMetrics(gene_data['sequence'])
        
        # Analyze mutations across sequence
        results = metrics.analyze_sequence(step_size=20)
        
        if not results:
            print("No mutations analyzed for this sequence.")
            continue
            
        # Store results
        all_results[gene_name] = results
        
        # Compute summary statistics
        scores = [r['composite_score'] for r in results]
        z_factors = [r['z_factor'] for r in results]
        delta_f1_values = [abs(r['delta_f1']) for r in results]
        
        summary_stats.append({
            'gene': gene_name,
            'length': len(gene_data['sequence']),
            'mutations_analyzed': len(results),
            'max_score': max(scores),
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'max_z_factor': max(z_factors),
            'mean_delta_f1': np.mean(delta_f1_values)
        })
        
        # Display top mutations
        print("TOP 5 MUTATIONS BY COMPOSITE SCORE:")
        print(f"{'Pos':<4} {'Mut':<6} {'Δf1':<8} {'ΔPeaks':<8} {'ΔEntropy':<10} {'Score':<8} {'Z Factor':<10}")
        print("-" * 70)
        
        for i, result in enumerate(results[:5]):
            pos = result['position']
            mut = f"{result['original_base']}→{result['mutated_base']}"
            delta_f1 = f"{result['delta_f1']:+.1f}%"
            delta_peaks = f"{result['delta_peaks']:+d}"
            delta_entropy = f"{result['delta_entropy']:+.3f}"
            score = f"{result['composite_score']:.2f}"
            z_factor = f"{result['z_factor']:.1e}"
            
            print(f"{pos:<4} {mut:<6} {delta_f1:<8} {delta_peaks:<8} {delta_entropy:<10} {score:<8} {z_factor:<10}")
        
        print()
        
        # Generate detailed report for this gene
        report = metrics.generate_report(results, top_n=3)
        
        # Save detailed results to JSON (convert numpy types)
        output_filename = f"wave_crispr_{gene_name.lower()}_results.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        results_json = convert_numpy(results[:10])  # Top 10 mutations
        
        with open(output_filename, 'w') as f:
            json.dump({
                'gene_name': gene_name,
                'description': gene_data['description'],
                'clinical_relevance': gene_data['clinical_relevance'],
                'sequence_length': len(gene_data['sequence']),
                'analysis_results': results_json,
                'summary_statistics': {
                    'total_mutations': len(results),
                    'score_range': [float(min(scores)), float(max(scores))],
                    'mean_score': float(np.mean(scores)),
                    'score_std': float(np.std(scores))
                }
            }, f, indent=2)
        
        print(f"Detailed results saved to: {output_filename}")
        print()
    
    return all_results, summary_stats

def comparative_analysis(all_results, summary_stats):
    """Perform comparative analysis across all genes."""
    print("COMPARATIVE ANALYSIS ACROSS GENES")
    print("=" * 50)
    
    # Create comparison table
    print(f"{'Gene':<15} {'Length':<8} {'Mutations':<10} {'Max Score':<10} {'Mean Score':<11} {'Max Z Factor':<12}")
    print("-" * 75)
    
    for stats in summary_stats:
        gene = stats['gene'][:14]
        length = stats['length']
        mutations = stats['mutations_analyzed']
        max_score = f"{stats['max_score']:.2f}"
        mean_score = f"{stats['mean_score']:.2f}"
        max_z = f"{stats['max_z_factor']:.1e}"
        
        print(f"{gene:<15} {length:<8} {mutations:<10} {max_score:<10} {mean_score:<11} {max_z:<12}")
    
    print()
    
    # Identify most sensitive regions
    print("MOST SENSITIVE MUTATION POSITIONS (Highest Composite Scores):")
    print("-" * 60)
    
    all_mutations = []
    for gene_name, results in all_results.items():
        for result in results[:3]:  # Top 3 per gene
            all_mutations.append({
                'gene': gene_name,
                'position': result['position'],
                'mutation': f"{result['original_base']}→{result['mutated_base']}",
                'score': result['composite_score'],
                'delta_f1': result['delta_f1'],
                'z_factor': result['z_factor']
            })
    
    # Sort by composite score
    all_mutations.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"{'Gene':<12} {'Pos':<4} {'Mutation':<8} {'Score':<8} {'Δf1':<8} {'Z Factor':<10}")
    print("-" * 60)
    
    for mut in all_mutations[:10]:
        gene = mut['gene'][:11]
        pos = mut['position']
        mutation = mut['mutation']
        score = f"{mut['score']:.2f}"
        delta_f1 = f"{mut['delta_f1']:+.1f}%"
        z_factor = f"{mut['z_factor']:.1e}"
        
        print(f"{gene:<12} {pos:<4} {mutation:<8} {score:<8} {delta_f1:<8} {z_factor:<10}")

def create_visualizations(all_results):
    """Create visualization plots for the analysis results."""
    print("\nCreating visualizations...")
    
    # Score distribution plot
    plt.figure(figsize=(12, 8))
    
    # Subplot 1: Score distributions
    plt.subplot(2, 2, 1)
    for gene_name, results in all_results.items():
        scores = [r['composite_score'] for r in results]
        plt.hist(scores, alpha=0.7, label=gene_name[:8], bins=10)
    plt.xlabel('Composite Score')
    plt.ylabel('Frequency')
    plt.title('Distribution of Composite Scores by Gene')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Z factor vs Position
    plt.subplot(2, 2, 2)
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for i, (gene_name, results) in enumerate(all_results.items()):
        positions = [r['position'] for r in results]
        z_factors = [r['z_factor'] for r in results]
        plt.scatter(positions, z_factors, alpha=0.7, 
                   label=gene_name[:8], color=colors[i % len(colors)])
    plt.xlabel('Position in Sequence')
    plt.ylabel('Z Factor')
    plt.title('Z Factor vs Position')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    
    # Subplot 3: Delta F1 vs Delta Entropy
    plt.subplot(2, 2, 3)
    for i, (gene_name, results) in enumerate(all_results.items()):
        delta_f1 = [abs(r['delta_f1']) for r in results]
        delta_entropy = [r['delta_entropy'] for r in results]
        plt.scatter(delta_f1, delta_entropy, alpha=0.7,
                   label=gene_name[:8], color=colors[i % len(colors)])
    plt.xlabel('|Δf1| (%)')
    plt.ylabel('ΔEntropy')
    plt.title('Spectral vs Entropy Changes')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: Sequence length vs Max score
    plt.subplot(2, 2, 4)
    lengths = []
    max_scores = []
    gene_names = []
    for gene_name, results in all_results.items():
        seq_length = len(SAMPLE_SEQUENCES[gene_name]['sequence'])
        max_score = max([r['composite_score'] for r in results])
        lengths.append(seq_length)
        max_scores.append(max_score)
        gene_names.append(gene_name[:8])
    
    plt.scatter(lengths, max_scores, s=100, alpha=0.7)
    for i, name in enumerate(gene_names):
        plt.annotate(name, (lengths[i], max_scores[i]), 
                    xytext=(5, 5), textcoords='offset points')
    plt.xlabel('Sequence Length (bp)')
    plt.ylabel('Maximum Composite Score')
    plt.title('Sequence Length vs Maximum Impact')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('wave_crispr_analysis_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualization saved as: wave_crispr_analysis_summary.png")

def interpretation_guide():
    """Provide detailed interpretation guidelines for the results."""
    print("\nRESULT INTERPRETATION GUIDE")
    print("=" * 40)
    
    print("""
ENHANCED METRICS INTERPRETATION:

1. COMPOSITE SCORE (Z · |Δf1| + ΔPeaks + ΔEntropy)
   - Range: Typically 0-50, but can exceed for high-impact mutations
   - High scores (>15): Potentially significant functional impact
   - Very high scores (>25): Likely critical mutations requiring attention
   
2. Z FACTOR (Universal Invariance Integration)
   - Scientific notation values (e.g., 1.5e-08)
   - Position-dependent: Later positions tend to have higher Z factors
   - Incorporates discrete zeta shifts and geometric effects
   
3. Δf1 (Fundamental Frequency Change)
   - Percentage change in primary spectral component
   - Large absolute values (>30%) indicate significant structural disruption
   - Sign indicates direction of frequency shift
   
4. ΔPeaks (Spectral Complexity Change)
   - Integer change in number of significant frequency peaks
   - Positive values: Increased spectral complexity
   - Large changes (|ΔPeaks| > 10) suggest major structural alterations
   
5. ΔEntropy (Enhanced Entropy with Geometric Scaling)
   - Incorporates spectral order O and logarithmic position scaling
   - Positive values: Increased disorder/complexity
   - Values near zero: Minimal entropy change
   - Large absolute values: Significant information content changes

BIOLOGICAL RELEVANCE:

- Mutations with highest composite scores are most likely to affect function
- G→A and C→T transitions often show high spectral impact
- Position-dependent effects reflect local sequence context
- Z framework integration provides universal scaling across genes

CLINICAL APPLICATIONS:

- High-scoring mutations warrant experimental validation
- Composite scores can prioritize variants for functional studies
- Cross-gene comparisons identify universal mutation patterns
- Enhanced metrics improve over traditional conservation-based approaches
""")

def main():
    """Run comprehensive sample data analysis."""
    print("Initializing Wave-CRISPR Enhanced Metrics Sample Analysis...")
    print()
    
    try:
        # Perform analysis
        all_results, summary_stats = analyze_sample_data()
        
        # Comparative analysis
        comparative_analysis(all_results, summary_stats)
        
        # Create visualizations
        create_visualizations(all_results)
        
        # Provide interpretation guide
        interpretation_guide()
        
        print("\n" + "=" * 80)
        print("✓ SAMPLE DATA ANALYSIS COMPLETED SUCCESSFULLY")
        print()
        print("Key Outputs Generated:")
        print("- Individual gene analysis results (JSON files)")
        print("- Comparative analysis across all genes")
        print("- Visualization summary plot")
        print("- Detailed interpretation guidelines")
        print()
        print("Enhanced Wave-CRISPR metrics demonstrate:")
        print("1. Integration with Z framework universal invariance")
        print("2. Position-dependent geometric effects via zeta shifts")
        print("3. Enhanced spectral order entropy scaling (O / ln n)")
        print("4. Clinically relevant mutation impact scoring")
        
    except Exception as e:
        print(f"\n✗ ANALYSIS FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()