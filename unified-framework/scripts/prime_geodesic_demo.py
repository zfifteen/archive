#!/usr/bin/env python3
"""
Prime Geodesic CLI Demo

Command-line demonstration script for the Prime Geodesic Search Engine.
Shows basic functionality and generates sample visualizations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import argparse
import json
from src.applications.prime_geodesic_search import PrimeGeodesicSearchEngine

def run_basic_demo(start: int = 2, end: int = 102):
    """Run basic demonstration of search engine capabilities."""
    print("🔍 Prime Geodesic Search Engine - CLI Demo")
    print("=" * 50)
    
    # Initialize engine
    engine = PrimeGeodesicSearchEngine(k_optimal=0.3)
    print(f"✅ Initialized with optimal k* = {engine.k_optimal}")
    
    # Generate coordinates
    print(f"\n📊 Generating coordinates for range [{start}, {end}]...")
    points = engine.generate_sequence_coordinates(start, end)
    print(f"✅ Generated {len(points)} geodesic points")
    
    # Basic statistics
    primes = [p for p in points if p.is_prime]
    print(f"📈 Found {len(primes)} primes ({len(primes)/len(points)*100:.1f}%)")
    
    # Find clusters
    print(f"\n🎯 Searching for prime clusters...")
    clusters = engine.search_prime_clusters(points, eps=0.2, min_samples=3)
    print(f"✅ Found {len(clusters)} clusters")
    
    for i, cluster in enumerate(clusters[:3]):  # Show first 3 clusters
        cluster_primes = [p.n for p in cluster]
        print(f"   Cluster {i+1}: {cluster_primes[:10]}{'...' if len(cluster_primes) > 10 else ''}")
    
    # Detect anomalies
    print(f"\n🔍 Detecting anomalies...")
    anomalies = engine.search_gaps_and_anomalies(points)
    print(f"✅ Found {len(anomalies['gaps'])} gaps, {len(anomalies['anomalies'])} anomalies")
    
    # Statistical analysis
    print(f"\n📊 Statistical Analysis:")
    report = engine.generate_statistical_report(points)
    print(f"   Prime Enhancement: {report['density_enhancement']['mean_enhancement']:.2f}%")
    print(f"   Target Enhancement: {report['validation_metrics']['expected_prime_enhancement']:.1f}%")
    print(f"   Curvature Variance: {report['curvature_analysis']['curvature_variance']:.4f}")
    print(f"   Target Variance: {report['validation_metrics']['variance_target']:.3f}")
    
    # Export results
    print(f"\n💾 Exporting results...")
    try:
        csv_file = engine.export_coordinates(points, "cli_demo_results", format='csv')
        json_file = engine.export_coordinates(points, "cli_demo_results", format='json')
        print(f"✅ Exported to {csv_file} and {json_file}")
    except Exception as e:
        print(f"⚠️  Export failed: {e}")
    
    print(f"\n🎉 Demo completed successfully!")
    return engine, points, report

def run_search_demo(criteria: dict):
    """Demonstrate search functionality with specific criteria."""
    print("\n🔍 Search Demo with Criteria")
    print("-" * 30)
    
    engine = PrimeGeodesicSearchEngine(k_optimal=0.3)
    
    # Perform search
    search_result = engine.search_by_criteria(
        start=2, end=1000, criteria=criteria
    )
    
    print(f"Search criteria: {criteria}")
    print(f"Results found: {search_result.total_found}")
    print(f"Anomaly score: {search_result.anomaly_score:.3f}")
    
    # Show sample results
    sample_points = search_result.points[:10]
    print("\nSample results:")
    for point in sample_points:
        print(f"  n={point.n:3d}, prime={point.is_prime}, "
              f"curvature={point.curvature:.3f}, "
              f"enhancement={point.density_enhancement:.2f}%")

def run_validation_demo():
    """Demonstrate framework validation against benchmarks."""
    print("\n🧪 Framework Validation Demo")
    print("-" * 30)
    
    engine = PrimeGeodesicSearchEngine(k_optimal=0.3)
    
    # Test different ranges
    test_ranges = [
        (2, 100),
        (100, 500), 
        (500, 1000)
    ]
    
    for start, end in test_ranges:
        points = engine.generate_sequence_coordinates(start, end)
        primes = [p for p in points if p.is_prime]
        
        if primes:
            avg_enhancement = sum(p.density_enhancement for p in primes) / len(primes)
            print(f"Range [{start:3d}, {end:3d}]: "
                  f"{len(primes):2d} primes, "
                  f"enhancement={avg_enhancement:5.2f}% "
                  f"(target: 15.0%)")

def main():
    parser = argparse.ArgumentParser(description='Prime Geodesic Search Engine CLI Demo')
    parser.add_argument('--start', type=int, default=2, help='Start of range (default: 2)')
    parser.add_argument('--end', type=int, default=102, help='End of range (default: 102)')
    parser.add_argument('--demo', choices=['basic', 'search', 'validation', 'all'], 
                       default='basic', help='Demo type to run')
    
    # Search criteria options
    parser.add_argument('--primes-only', action='store_true', help='Search primes only')
    parser.add_argument('--min-curvature', type=float, help='Minimum curvature threshold')
    parser.add_argument('--max-curvature', type=float, help='Maximum curvature threshold')
    parser.add_argument('--min-enhancement', type=float, default=8.0, 
                       help='Minimum density enhancement (default: 8.0)')
    
    args = parser.parse_args()
    
    try:
        if args.demo in ['basic', 'all']:
            run_basic_demo(args.start, args.end)
        
        if args.demo in ['search', 'all']:
            criteria = {}
            if args.primes_only:
                criteria['primes_only'] = True
            if args.min_curvature:
                criteria['curvature_range'] = [args.min_curvature, args.max_curvature or 10.0]
            if args.min_enhancement:
                criteria['min_density_enhancement'] = args.min_enhancement
            
            run_search_demo(criteria)
        
        if args.demo in ['validation', 'all']:
            run_validation_demo()
            
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())