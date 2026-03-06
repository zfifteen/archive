#!/usr/bin/env python3
"""
Universal Invariant Scoring Engine Demo

Demonstrates the Z-score API functionality with various data types.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.scoring_engine import create_scoring_engine
import json


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_result(data, result, data_type):
    """Print scoring result in a formatted way."""
    print(f"\nInput ({data_type}): {data}")
    print(f"Z-invariant Score: {result['z_invariant_score']:.6f}")
    print(f"Sequence Length: {result['sequence_length']}")
    print(f"Enhancement Factor: {result['density_metrics']['enhancement_factor']:.3f}")
    print(f"Anomaly Score: {result['anomaly_scores']['composite_anomaly_score']:.3f}")
    
    if result['metadata']['type'] == 'biological':
        print(f"Sequence Type: {result['metadata']['sequence_type']}")
        if result['metadata']['gc_content'] is not None:
            print(f"GC Content: {result['metadata']['gc_content']:.1%}")
    elif result['metadata']['type'] == 'network':
        print(f"Nodes: {result['metadata']['n_nodes']}, Edges: {result['metadata']['n_edges']}")
        print(f"Network Density: {result['metadata']['density']:.3f}")


def main():
    """Run the demo."""
    print("Universal Invariant Scoring Engine (Z-score API) Demo")
    print("Built on the Z Framework mathematical foundations")
    
    # Create scoring engine
    print_section("Initializing Scoring Engine")
    engine = create_scoring_engine()
    print("✓ Scoring engine initialized successfully")
    print("✓ Using Z Framework with high-precision arithmetic (dps=50)")
    print("✓ Golden ratio φ and optimal curvature k*≈0.3 incorporated")
    
    # Test numerical sequences
    print_section("Numerical Sequence Analysis")
    
    numerical_examples = [
        [1, 2, 3, 4, 5],
        [2, 3, 5, 7, 11, 13, 17, 19],  # Prime numbers
        [1, 1, 2, 3, 5, 8, 13, 21],    # Fibonacci sequence
        [1, 4, 9, 16, 25, 36, 49],     # Perfect squares
        list(range(50, 100))            # Linear sequence
    ]
    
    numerical_labels = [
        "Simple sequence",
        "Prime numbers",
        "Fibonacci sequence", 
        "Perfect squares",
        "Linear sequence (50-99)"
    ]
    
    for data, label in zip(numerical_examples, numerical_labels):
        result = engine.score_sequence(data, 'numerical')
        print(f"\n{label}:")
        print_result(data[:10] if len(data) > 10 else data, result, 'numerical')
    
    # Test biological sequences
    print_section("Biological Sequence Analysis")
    
    biological_examples = [
        ("ATGCATGCATGC", "Simple DNA repeat"),
        ("AUGCAUGCAUGC", "Simple RNA repeat"),
        ("ATGAAACGCATTAGCACCACCATTACCACCACCATCACCATTACCACAGGTAACGGTGCGGGCT", "E. coli gene fragment"),
        ("MVSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYG", "Green Fluorescent Protein fragment"),
        ("AAAAAAAAAAAAAAAA", "Poly-A sequence"),
        ("ATCGATCGATCGATCG", "Alternating AT-CG pattern")
    ]
    
    for sequence, label in biological_examples:
        result = engine.score_sequence(sequence, 'biological')
        print(f"\n{label}:")
        print_result(sequence, result, 'biological')
    
    # Test network data
    print_section("Network/Graph Analysis")
    
    network_examples = [
        ([[0, 1, 1], [1, 0, 1], [1, 1, 0]], "Complete graph K3"),
        ([[0, 1, 0], [1, 0, 1], [0, 1, 0]], "Path graph P3"),
        ([[0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]], "Star graph"),
        ([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], "Cycle C4"),
    ]
    
    for matrix, label in network_examples:
        result = engine.score_sequence(matrix, 'network')
        print(f"\n{label}:")
        print_result(f"{len(matrix)}x{len(matrix)} matrix", result, 'network')
    
    # Demonstrate batch processing
    print_section("Batch Processing Demonstration")
    
    batch_data = [
        [1, 2, 3, 4, 5],
        "ATGCATGC",
        [[0, 1], [1, 0]],
        [10, 20, 30, 40, 50],
        "PROTEIN"
    ]
    
    print("Processing batch of 5 diverse sequences...")
    batch_results = engine.batch_score(batch_data)
    
    print("\nBatch Results Summary:")
    for i, result in enumerate(batch_results):
        data_type = result['metadata']['type']
        score = result['z_invariant_score']
        print(f"  Sequence {i+1} ({data_type}): Z-score = {score:.6f}")
    
    # Cross-domain comparison
    print_section("Cross-Domain Score Comparison")
    
    comparison_data = [
        ([1, 2, 3, 5, 8, 13], "numerical"),
        ("ATGCGT", "biological"),
        ([[0, 1, 1], [1, 0, 1], [1, 1, 0]], "network")
    ]
    
    print("Comparing scores across different data domains:")
    scores = []
    for data, dtype in comparison_data:
        result = engine.score_sequence(data, dtype)
        score = result['z_invariant_score']
        scores.append((dtype, score))
        print(f"  {dtype.capitalize():12}: {score:.6f}")
    
    # Demonstrate anomaly detection
    print_section("Anomaly Detection")
    
    # Normal vs anomalous sequences
    normal_seq = list(range(1, 21))  # 1 to 20
    anomalous_seq = [1, 2, 3, 100, 5, 6, 7, 200, 9, 10]  # Contains outliers
    
    normal_result = engine.score_sequence(normal_seq, 'numerical')
    anomalous_result = engine.score_sequence(anomalous_seq, 'numerical')
    
    print("\nNormal sequence (1-20):")
    print(f"  Anomaly Score: {normal_result['anomaly_scores']['composite_anomaly_score']:.3f}")
    
    print("\nAnomalous sequence (with outliers 100, 200):")
    print(f"  Anomaly Score: {anomalous_result['anomaly_scores']['composite_anomaly_score']:.3f}")
    
    # Mathematical insights
    print_section("Z Framework Mathematical Insights")
    
    print("Key mathematical features demonstrated:")
    print("• Universal invariance Z = A(B/c) form applied to discrete sequences")
    print("• Golden ratio φ transformations for prime-like pattern detection")
    print("• Optimal curvature parameter k*≈0.3 providing conditional prime density improvement under canonical benchmark methodology")
    print("• Frame-normalized curvature κ(n) = d(n)·ln(n+1)/e² for geodesic analysis")
    print("• Cross-domain normalization enabling benchmarking across data types")
    print("• High-precision arithmetic (mpmath dps=50) for numerical stability")
    
    print("\nApplications:")
    print("• Genomics: DNA/RNA sequence quality and pattern detection")
    print("• Cryptography: Random number quality assessment")
    print("• Network Analysis: Graph structure characterization") 
    print("• Mathematics: Prime distribution and number theory research")
    print("• Anomaly Detection: Statistical outlier identification")
    
    print_section("Demo Complete")
    print("Universal Invariant Scoring Engine successfully demonstrated!")
    print("Ready for deployment as REST API service.")


if __name__ == '__main__':
    # Set up environment
    os.environ['PYTHONPATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Run demo
    main()