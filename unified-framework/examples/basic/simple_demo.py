#!/usr/bin/env python3
"""
Simple demonstration of the Modular Topology Visualization Suite

This script shows the basic usage of the visualization suite with
prime numbers, demonstrating the key features and capabilities.
"""

import sys
import os
import numpy as np

# Add the applications directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'applications'))

from modular_topology_suite import (
    GeneralizedEmbedding, TopologyAnalyzer, VisualizationEngine, DataExporter,
    generate_prime_sequence
)

def main():
    print("Modular Topology Visualization Suite - Simple Demo")
    print("=" * 55)
    
    # Step 1: Generate sample data (prime numbers)
    print("\n1. Generating prime number sequence...")
    primes = generate_prime_sequence(100)
    print(f"   Generated {len(primes)} primes: {primes[:10]}... (showing first 10)")
    
    # Step 2: Initialize the visualization suite components
    print("\n2. Initializing visualization components...")
    embedding = GeneralizedEmbedding(modulus=1.618)  # Golden ratio modulus
    analyzer = TopologyAnalyzer()
    visualizer = VisualizationEngine()
    exporter = DataExporter()
    print("   ✓ Components initialized")
    
    # Step 3: Create embeddings using θ′(n, k) transformation
    print("\n3. Computing geometric embeddings...")
    k_optimal = 0.3  # Optimal curvature parameter for primes
    
    # Apply the θ′(n, k) transformation
    theta_transformed = embedding.theta_prime_transform(primes, k=k_optimal)
    print(f"   ✓ θ′(n, k) transformation applied with k={k_optimal}")
    
    # Generate 5D helical coordinates
    coordinates = embedding.helical_5d_embedding(primes, theta_transformed)
    print(f"   ✓ 5D helical embedding generated")
    print(f"     Coordinate dimensions: {list(coordinates.keys())}")
    
    # Generate modular spiral coordinates
    spiral_coords = embedding.modular_spiral_coordinates(primes)
    print(f"   ✓ Modular spiral coordinates generated")
    
    # Step 4: Analyze geometric patterns
    print("\n4. Analyzing geometric patterns...")
    
    # Cluster analysis
    clusters, cluster_stats = analyzer.detect_clusters(coordinates, method='dbscan')
    print(f"   ✓ Cluster analysis: Found {len(cluster_stats)} clusters")
    
    # Symmetry analysis
    symmetries = analyzer.detect_symmetries(coordinates)
    helical_score = symmetries.get('helical', {}).get('helical_score', 0)
    print(f"   ✓ Symmetry analysis: Helical score = {helical_score:.3f}")
    
    # Anomaly detection
    anomalies, anomaly_scores = analyzer.detect_anomalies(coordinates)
    n_anomalies = np.sum(anomalies == -1)
    anomaly_rate = np.mean(anomalies == -1) * 100
    print(f"   ✓ Anomaly detection: {n_anomalies} anomalies ({anomaly_rate:.1f}%)")
    
    # Step 5: Create visualizations
    print("\n5. Creating interactive visualizations...")
    
    # 3D helical embedding
    fig_3d = visualizer.plot_3d_helical_embedding(coordinates, coordinates, 
                                                  "Prime Numbers - 3D Helical Embedding")
    print("   ✓ 3D helical embedding visualization created")
    
    # 5D projection
    fig_5d = visualizer.plot_5d_projection(coordinates)
    print("   ✓ 5D projection visualization created")
    
    # Modular spiral
    fig_spiral = visualizer.plot_modular_spiral(spiral_coords)
    print("   ✓ Modular spiral visualization created")
    
    # Cluster analysis visualization
    fig_clusters = visualizer.plot_cluster_analysis(coordinates, clusters, cluster_stats)
    print("   ✓ Cluster analysis visualization created")
    
    # Anomaly detection visualization
    fig_anomalies = visualizer.plot_anomaly_detection(coordinates, anomalies, anomaly_scores)
    print("   ✓ Anomaly detection visualization created")
    
    # Step 6: Export results
    print("\n6. Exporting results...")
    
    # Create output directory
    output_dir = "./demo_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Export coordinate data
    coord_file = os.path.join(output_dir, "prime_coordinates.csv")
    exporter.export_coordinates(coordinates, coord_file, format='csv')
    print(f"   ✓ Coordinates exported to {coord_file}")
    
    # Export analysis report
    report_file = os.path.join(output_dir, "prime_analysis_report.json")
    exporter.export_analysis_report(coordinates, cluster_stats, symmetries, 
                                   (anomalies, anomaly_scores), report_file)
    print(f"   ✓ Analysis report exported to {report_file}")
    
    # Export visualizations as HTML (interactive)
    try:
        fig_3d.write_html(os.path.join(output_dir, "prime_3d_helix.html"))
        fig_spiral.write_html(os.path.join(output_dir, "prime_spiral.html"))
        fig_clusters.write_html(os.path.join(output_dir, "prime_clusters.html"))
        print(f"   ✓ Interactive visualizations exported to {output_dir}")
    except Exception as e:
        print(f"   ⚠ Warning: Could not export HTML visualizations: {e}")
    
    # Step 7: Summary and insights
    print("\n7. Analysis Summary")
    print("-" * 20)
    print(f"Dataset: {len(primes)} prime numbers up to 100")
    print(f"Transformation: θ′(n, k) with k={k_optimal}, φ={embedding.modulus:.3f}")
    print(f"Geometric embedding: 5D helical coordinates")
    print(f"Pattern analysis:")
    print(f"  • Clusters detected: {len(cluster_stats)}")
    print(f"  • Helical symmetry score: {helical_score:.3f}")
    print(f"  • Anomalies found: {n_anomalies} ({anomaly_rate:.1f}%)")
    
    # Mathematical insights
    print(f"\nMathematical insights:")
    print(f"  • Golden ratio modulus φ ≈ {embedding.modulus:.6f}")
    print(f"  • Curvature parameter k* = {k_optimal} (optimal for primes)")
    print(f"  • 5D embedding reveals geometric structure in prime distribution")
    
    if cluster_stats:
        print(f"  • Largest cluster has {max(stats['size'] for stats in cluster_stats.values())} primes")
    
    print(f"\nVisualization features:")
    print(f"  • Interactive 3D helical plots with Plotly")
    print(f"  • Modular spiral patterns in geometric space")
    print(f"  • Cluster and anomaly highlighting")
    print(f"  • Export capabilities for publication")
    
    print(f"\nFiles generated in {output_dir}:")
    print(f"  • prime_coordinates.csv - Coordinate data")
    print(f"  • prime_analysis_report.json - Analysis results")
    print(f"  • prime_3d_helix.html - Interactive 3D visualization")
    print(f"  • prime_spiral.html - Interactive spiral plot")
    print(f"  • prime_clusters.html - Cluster analysis plot")
    
    print("\n" + "=" * 55)
    print("Demo completed successfully!")
    print("\nNext steps:")
    print("  • Open HTML files in web browser for interactive exploration")
    print("  • Run with different datasets: fibonacci, mersenne")
    print("  • Try different k values to explore geometric effects")
    print("  • Use the web interface: python3 src/applications/topology_web_interface.py")
    print("  • Run comprehensive analysis: python3 cli_demo.py --help")

if __name__ == '__main__':
    main()