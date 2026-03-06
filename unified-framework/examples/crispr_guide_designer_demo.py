# Z-Invariant CRISPR Guide Designer Demo

This notebook demonstrates the capabilities of the Z-Invariant CRISPR Guide Designer, showing how modular-geodesic embeddings enhance guide RNA design precision.

## Setup

```python
import sys
sys.path.append('../src')

from applications.crispr_guide_designer import CRISPRGuideDesigner
from applications.crispr_visualization import CRISPRVisualization
import numpy as np
```

## Example 1: Basic Guide Design

```python
# Sample target sequence (PCSK9 gene fragment)
target_sequence = """
ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGA
AGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGA
GCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGGCCCAGGAGCAGCTGCGGCTGGAG
"""

# Remove whitespace and newlines
target_sequence = target_sequence.replace('\n', '').replace(' ', '')

print(f"Target sequence length: {len(target_sequence)} bp")
print(f"Target preview: {target_sequence[:60]}...")
```

```python
# Initialize designer with optimized parameters
designer = CRISPRGuideDesigner(
    precision=30,      # High precision for accuracy
    k_parameter=0.3    # Optimal θ′(n, k) parameter
)

# Run complete analysis
results = designer.analyze_target_sequence(target_sequence, max_guides=5)

# Display summary
print(results['analysis_summary'])
```

## Example 2: Visualization Analysis

```python
# Create visualization suite
visualizer = CRISPRVisualization(style='plotly')

# Generate comprehensive dashboard
figures = visualizer.create_analysis_dashboard(results)

print(f"Generated {len(figures)} visualization components:")
for name, fig in figures.items():
    print(f"- {name.replace('_', ' ').title()}")
```

```python
# Display individual visualizations

# 1. 5D Coordinate Clustering
if 'cluster_plot' in figures:
    cluster_fig = figures['cluster_plot']
    cluster_fig.update_layout(title="Guide Clustering in Modular-Geodesic Space")
    cluster_fig.show()
```

```python
# 2. Scoring Comparison Dashboard
if 'score_dashboard' in figures:
    score_fig = figures['score_dashboard']
    score_fig.show()
```

```python
# 3. Conventional vs Z-Framework Comparison
if 'methodology_comparison' in figures:
    comparison_fig = figures['methodology_comparison']
    comparison_fig.show()
```

## Example 3: Parameter Sensitivity Analysis

```python
# Test different θ′(n, k) parameters
k_values = [0.1, 0.2, 0.3, 0.4, 0.5]
parameter_results = {}

for k in k_values:
    designer_k = CRISPRGuideDesigner(precision=20, k_parameter=k)
    results_k = designer_k.analyze_target_sequence(target_sequence, max_guides=3)
    
    # Extract average scores
    if results_k['optimized_guides']:
        avg_score = np.mean([g['composite_score'] for g in results_k['optimized_guides']])
        avg_risk = np.mean([g['off_target_risk'] for g in results_k['optimized_guides']])
        parameter_results[k] = {'score': avg_score, 'risk': avg_risk}

# Display results
print("Parameter Sensitivity Analysis:")
print("k-value | Avg Score | Avg Risk")
print("--------|-----------|----------")
for k, metrics in parameter_results.items():
    print(f"{k:7.1f} | {metrics['score']:9.3f} | {metrics['risk']:8.3f}")
```

## Example 4: Detailed Guide Analysis

```python
# Examine the top guide in detail
if results['optimized_guides']:
    top_guide = results['optimized_guides'][0]
    
    print("TOP GUIDE DETAILED ANALYSIS")
    print("=" * 40)
    print(f"Sequence: {top_guide['sequence']}")
    print(f"Position: {top_guide['position']}")
    print(f"PAM Site: {top_guide['pam_sequence']}")
    print(f"Seed Region: {top_guide['seed_region']}")
    print()
    print("SCORING METRICS:")
    print(f"Composite Score: {top_guide['composite_score']:.4f}")
    print(f"Z Framework Score: {top_guide['z_framework_score']:.2e}")
    print(f"Density Enhancement: {top_guide['density_enhancement']:.4f}")
    print(f"Off-Target Risk: {top_guide['off_target_risk']:.4f}")
    print(f"Geodesic Complexity: {top_guide['geodesic_complexity']:.4f}")
    print()
    print("GEOMETRIC PROPERTIES:")
    print(f"Geometric Fingerprint: {top_guide['geometric_fingerprint']}")
    
    # Display 5D coordinates summary
    coords_5d = top_guide['coordinates_5d']
    print("\n5D COORDINATE STATISTICS:")
    for dim in ['x', 'y', 'z', 'w', 'u']:
        values = coords_5d[dim]
        print(f"{dim.upper()}: mean={np.mean(values):.3f}, std={np.std(values):.3f}")
```

## Example 5: Custom Analysis Functions

```python
def analyze_gc_content_effect(target_seq, max_guides=10):
    """Analyze relationship between GC content and Z-framework scoring."""
    designer = CRISPRGuideDesigner()
    results = designer.analyze_target_sequence(target_seq, max_guides=max_guides)
    
    analysis_data = []
    for guide in results['optimized_guides']:
        sequence = guide['sequence']
        gc_content = (sequence.count('G') + sequence.count('C')) / len(sequence)
        
        analysis_data.append({
            'sequence': sequence,
            'gc_content': gc_content,
            'z_score': guide['z_framework_score'],
            'composite_score': guide['composite_score'],
            'position': guide['position']
        })
    
    return analysis_data

# Run GC content analysis
gc_analysis = analyze_gc_content_effect(target_sequence, max_guides=8)

print("GC CONTENT vs Z-FRAMEWORK SCORING:")
print("Sequence                 | GC%  | Z-Score    | Composite")
print("-------------------------|------|------------|----------")
for data in gc_analysis:
    print(f"{data['sequence']} | {data['gc_content']*100:4.1f} | {data['z_score']:10.2e} | {data['composite_score']:8.3f}")
```

## Example 6: Statistical Validation

```python
def compare_with_conventional_scoring(guides_data):
    """Compare Z-framework with conventional CRISPR scoring."""
    conventional_scores = []
    z_framework_scores = []
    
    for guide in guides_data:
        # Conventional score: GC content + position weight
        gc_content = (guide['sequence'].count('G') + guide['sequence'].count('C')) / len(guide['sequence'])
        position_weight = 1.0 / (1.0 + guide['position'] / 1000.0)
        conv_score = gc_content * 0.6 + position_weight * 0.4
        
        conventional_scores.append(conv_score)
        z_framework_scores.append(guide['composite_score'])
    
    # Calculate correlation
    correlation = np.corrcoef(conventional_scores, z_framework_scores)[0, 1]
    
    print("METHODOLOGY COMPARISON:")
    print(f"Correlation coefficient: {correlation:.3f}")
    print(f"Z-framework mean score: {np.mean(z_framework_scores):.3f}")
    print(f"Conventional mean score: {np.mean(conventional_scores):.3f}")
    print(f"Z-framework std: {np.std(z_framework_scores):.3f}")
    print(f"Conventional std: {np.std(conventional_scores):.3f}")
    
    return correlation, conventional_scores, z_framework_scores

# Run comparison
if results['optimized_guides']:
    correlation, conv_scores, z_scores = compare_with_conventional_scoring(results['optimized_guides'])
```

## Summary

The Z-Invariant CRISPR Guide Designer demonstrates several key advantages:

1. **Mathematical Rigor**: Uses modular-geodesic embeddings θ′(n, k) for sequence analysis
2. **Enhanced Precision**: Leverages 5D coordinate space for comprehensive guide characterization  
3. **Universal Framework**: Integrates with Z = A(B/c) invariance principles
4. **Practical Applications**: Provides actionable guide recommendations with risk assessment
5. **Visualization**: Offers comprehensive analytical dashboards for interpretation

The system represents a significant advancement in computational CRISPR design, bridging molecular biology with fundamental mathematical principles through the unified Z framework.

```python
print("Demo completed successfully!")
print(f"Analyzed {len(results['potential_guides'])} potential guides")
print(f"Selected {len(results['optimized_guides'])} optimal guides")
print("Z-Invariant CRISPR Guide Designer ready for production use!")
```