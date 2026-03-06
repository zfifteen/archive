#!/usr/bin/env python3
"""
Command Line Interface for Modular Topology Visualization Suite

This script provides a simple command-line interface for running the
modular topology visualization suite without the web interface.
"""

import argparse
import sys
import os
import numpy as np

# Add the applications directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'applications'))

from modular_topology_suite import (
    GeneralizedEmbedding, TopologyAnalyzer, VisualizationEngine, DataExporter,
    generate_prime_sequence, generate_fibonacci_sequence, generate_mersenne_numbers
)

def main():
    parser = argparse.ArgumentParser(
        description='Modular Topology Visualization Suite CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cli_demo.py --dataset primes --limit 100 --k 0.3
  python3 cli_demo.py --dataset fibonacci --limit 50 --export-coords
  python3 cli_demo.py --dataset custom --file data.txt --analyze-clusters
        """
    )
    
    # Dataset options
    parser.add_argument('--dataset', choices=['primes', 'fibonacci', 'mersenne', 'custom'],
                        default='primes', help='Dataset type to analyze')
    parser.add_argument('--file', help='Input file for custom dataset')
    parser.add_argument('--limit', type=int, default=200, 
                        help='Sequence limit (default: 200)')
    
    # Transformation parameters
    parser.add_argument('--k', type=float, default=0.3,
                        help='Curvature parameter k (default: 0.3)')
    parser.add_argument('--modulus', type=float, default=1.618,
                        help='Modulus value (default: φ ≈ 1.618)')
    parser.add_argument('--frequency', type=float, default=0.1,
                        help='Helical frequency (default: 0.1)')
    
    # Analysis options
    parser.add_argument('--analyze-clusters', action='store_true',
                        help='Perform cluster analysis')
    parser.add_argument('--analyze-symmetries', action='store_true',
                        help='Perform symmetry analysis')
    parser.add_argument('--analyze-anomalies', action='store_true',
                        help='Perform anomaly detection')
    parser.add_argument('--clustering-method', choices=['dbscan', 'kmeans', 'hierarchical'],
                        default='dbscan', help='Clustering method')
    parser.add_argument('--n-clusters', type=int, default=5,
                        help='Number of clusters for kmeans/hierarchical')
    
    # Export options
    parser.add_argument('--export-coords', action='store_true',
                        help='Export coordinate data to CSV')
    parser.add_argument('--export-report', action='store_true', 
                        help='Export analysis report to JSON')
    parser.add_argument('--export-images', action='store_true',
                        help='Export visualization images')
    parser.add_argument('--output-dir', default='./output',
                        help='Output directory (default: ./output)')
    
    # Visualization options
    parser.add_argument('--show-summary', action='store_true',
                        help='Show analysis summary')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.verbose:
        print("Modular Topology Visualization Suite CLI")
        print("=" * 50)
    
    # Load dataset
    if args.dataset == 'primes':
        sequence = generate_prime_sequence(args.limit)
        if args.verbose:
            print(f"Generated {len(sequence)} prime numbers up to {args.limit}")
    elif args.dataset == 'fibonacci':
        sequence = generate_fibonacci_sequence(args.limit)
        if args.verbose:
            print(f"Generated {len(sequence)} Fibonacci numbers")
    elif args.dataset == 'mersenne':
        max_exp = min(20, args.limit // 10)
        sequence = generate_mersenne_numbers(max_exp)
        if args.verbose:
            print(f"Generated {len(sequence)} Mersenne numbers")
    elif args.dataset == 'custom':
        if not args.file:
            print("Error: --file required for custom dataset")
            return 1
        try:
            with open(args.file, 'r') as f:
                sequence = [int(float(line.strip())) for line in f if line.strip()]
            if args.verbose:
                print(f"Loaded {len(sequence)} numbers from {args.file}")
        except Exception as e:
            print(f"Error loading custom dataset: {e}")
            return 1
    
    if len(sequence) == 0:
        print("Error: No data points loaded")
        return 1
    
    # Initialize components
    embedding = GeneralizedEmbedding(modulus=args.modulus)
    analyzer = TopologyAnalyzer()
    visualizer = VisualizationEngine(theme='plotly_white')
    exporter = DataExporter()
    
    # Compute embeddings
    if args.verbose:
        print("Computing embeddings...")
    
    theta_transformed = embedding.theta_prime_transform(sequence, k=args.k)
    helix_coords = embedding.helical_5d_embedding(sequence, theta_transformed, frequency=args.frequency)
    spiral_coords = embedding.modular_spiral_coordinates(sequence)
    
    # Add spiral coordinates
    helix_coords['spiral_x'] = spiral_coords['x']
    helix_coords['spiral_y'] = spiral_coords['y']
    helix_coords['spiral_z'] = spiral_coords['z']
    
    # Perform analysis
    cluster_stats = {}
    symmetries = {}
    anomaly_info = (np.array([]), np.array([]))
    
    if args.analyze_clusters:
        if args.verbose:
            print("Analyzing clusters...")
        cluster_kwargs = {'n_clusters': args.n_clusters} if args.clustering_method != 'dbscan' else {}
        clusters, cluster_stats = analyzer.detect_clusters(
            helix_coords, method=args.clustering_method, **cluster_kwargs
        )
        print(f"Found {len(cluster_stats)} clusters using {args.clustering_method}")
        
    if args.analyze_symmetries:
        if args.verbose:
            print("Analyzing symmetries...")
        symmetries = analyzer.detect_symmetries(helix_coords)
        print("Symmetry analysis completed")
        
    if args.analyze_anomalies:
        if args.verbose:
            print("Detecting anomalies...")
        anomalies, anomaly_scores = analyzer.detect_anomalies(helix_coords)
        anomaly_info = (anomalies, anomaly_scores)
        n_anomalies = np.sum(anomalies == -1)
        anomaly_rate = np.mean(anomalies == -1) * 100
        print(f"Detected {n_anomalies} anomalies ({anomaly_rate:.1f}% anomaly rate)")
    
    # Show summary
    if args.show_summary:
        print("\nAnalysis Summary:")
        print("-" * 30)
        print(f"Dataset: {args.dataset}")
        print(f"Data points: {len(sequence)}")
        print(f"Curvature parameter k: {args.k}")
        print(f"Modulus: {args.modulus}")
        print(f"Helical frequency: {args.frequency}")
        
        if args.analyze_clusters and cluster_stats:
            print(f"Clusters found: {len(cluster_stats)}")
            for label, stats in cluster_stats.items():
                print(f"  Cluster {label}: {stats['size']} points, density {stats['density']:.3f}")
                
        if args.analyze_symmetries and symmetries:
            print("Symmetries:")
            if 'helical' in symmetries:
                helical = symmetries['helical']
                print(f"  Helical score: {helical.get('helical_score', 0):.3f}")
                
        if args.analyze_anomalies and len(anomaly_info[0]) > 0:
            n_anomalies = np.sum(anomaly_info[0] == -1)
            print(f"Anomalies: {n_anomalies} detected")
    
    # Export data
    if args.export_coords:
        coords_file = os.path.join(args.output_dir, f'{args.dataset}_coordinates.csv')
        exporter.export_coordinates(helix_coords, coords_file, format='csv')
        print(f"Coordinates exported to {coords_file}")
        
    if args.export_report:
        report_file = os.path.join(args.output_dir, f'{args.dataset}_analysis_report.json')
        exporter.export_analysis_report(helix_coords, cluster_stats, symmetries, anomaly_info, report_file)
        print(f"Analysis report exported to {report_file}")
    
    if args.export_images:
        if args.verbose:
            print("Creating visualizations...")
        
        # Generate visualizations
        fig_3d = visualizer.plot_3d_helical_embedding(helix_coords, helix_coords)
        fig_spiral = visualizer.plot_modular_spiral(spiral_coords)
        
        # Export images
        try:
            fig_3d.write_html(os.path.join(args.output_dir, f'{args.dataset}_3d_helix.html'))
            fig_spiral.write_html(os.path.join(args.output_dir, f'{args.dataset}_spiral.html'))
            print(f"Visualizations exported to {args.output_dir}")
        except Exception as e:
            print(f"Warning: Could not export images: {e}")
    
    if args.verbose:
        print("Analysis completed successfully!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())