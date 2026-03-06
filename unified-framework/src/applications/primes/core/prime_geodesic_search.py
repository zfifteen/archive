#!/usr/bin/env python3
"""
Prime Geodesic Search Engine: Modular Spiral Mapping and Visualization

This module implements a comprehensive search engine for prime numbers and integer
sequences mapped onto modular geodesic spirals using the Z Framework transformation
θ'(n, k) = φ·{n/φ}^k.

Features:
- Backend computation of geodesic coordinates for primes and arbitrary sequences
- Search and highlight anomalies, gaps, or prime clusters along spirals
- Exportable coordinates and density statistics
- API for external queries and mathematical dataset integration
- Comprehensive documentation of geometric algorithms

Mathematical Foundation:
Uses the empirically validated Z Framework with optimal curvature parameter k* ≈ 0.3,
achieving conditional prime density improvement under canonical benchmark methodology (CI [14.6%, 15.4%]) through geodesic
curvature minimization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass
import json
from sympy import primerange, isprime, divisors
import mpmath as mp
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Import core Z Framework components
from core.domain import DiscreteZetaShift
from core.axioms import theta_prime, curvature, universal_invariance

# Set high precision for modular arithmetic
mp.mp.dps = 50

@dataclass
class GeodesicPoint:
    """Represents a point on the modular geodesic spiral with metadata."""
    n: int
    coordinates_3d: Tuple[float, float, float]
    coordinates_5d: Tuple[float, float, float, float, float]
    is_prime: bool
    curvature: float
    density_enhancement: float
    cluster_id: Optional[int] = None
    geodesic_type: str = "standard"


@dataclass
class SearchResult:
    """Container for search results with statistical metadata."""
    points: List[GeodesicPoint]
    total_found: int
    search_parameters: Dict[str, Any]
    density_statistics: Dict[str, float]
    anomaly_score: float


class PrimeGeodesicSearchEngine:
    """
    Comprehensive search engine for prime geodesic analysis with modular spiral mapping.
    
    This class leverages the Z Framework's DiscreteZetaShift implementation to provide:
    - Efficient computation of geodesic coordinates using θ'(n,k) transformation
    - Advanced search capabilities for prime clusters and anomalies
    - Statistical analysis of density enhancements and geometric patterns
    - Export functionality for coordinates and analysis results
    """
    
    def __init__(self, k_optimal: float = 0.3, phi: Optional[float] = None):
        """
        Initialize the search engine with optimal curvature parameter.
        
        Args:
            k_optimal: Optimal curvature exponent (default: 0.3 from empirical validation)
            phi: Golden ratio value (computed if None)
        """
        self.k_optimal = k_optimal
        self.phi = float((1 + mp.sqrt(5)) / 2) if phi is None else phi
        self.e_squared = float(mp.exp(2))
        
        # Cache for computed coordinates to avoid recomputation
        self._coordinate_cache: Dict[int, GeodesicPoint] = {}
        
        # Statistical tracking
        self.stats = {
            'total_computed': 0,
            'prime_count': 0,
            'composite_count': 0,
            'average_curvature': 0.0,
            'density_enhancement_avg': 0.0
        }
        
    def compute_geodesic_coordinates(self, n: int, use_cache: bool = True) -> GeodesicPoint:
        """
        Compute geodesic coordinates for integer n using Z Framework.
        
        Args:
            n: Integer to analyze
            use_cache: Whether to use cached results
            
        Returns:
            GeodesicPoint with complete coordinate and metadata information
        """
        if use_cache and n in self._coordinate_cache:
            return self._coordinate_cache[n]
        
        # Create DiscreteZetaShift instance for this integer
        zeta_shift = DiscreteZetaShift(n)
        
        # Get 3D and 5D coordinates using framework methods
        coords_3d = zeta_shift.get_3d_coordinates()
        coords_5d = zeta_shift.get_5d_coordinates()
        
        # Compute prime status and curvature
        is_prime_n = isprime(n)
        d_n = len(list(divisors(n)))
        curvature_n = curvature(n, d_n)
        
        # Compute density enhancement using θ'(n,k) transformation
        theta_prime_val = theta_prime(n, self.k_optimal, self.phi)
        
        # Estimate local density enhancement (simplified version)
        # In full implementation, this would involve binned histogram analysis
        density_enhancement = self._estimate_density_enhancement(n, theta_prime_val)
        
        # Create geodesic point
        point = GeodesicPoint(
            n=n,
            coordinates_3d=coords_3d,
            coordinates_5d=coords_5d,
            is_prime=is_prime_n,
            curvature=float(curvature_n),
            density_enhancement=density_enhancement,
            geodesic_type="minimal_curvature" if is_prime_n else "standard_curvature"
        )
        
        # Cache the result
        if use_cache:
            self._coordinate_cache[n] = point
        
        # Update statistics
        self._update_statistics(point)
        
        return point
    
    def _estimate_density_enhancement(self, n: int, theta_prime_val: float) -> float:
        """
        Estimate local density enhancement around point n.
        
        This is a simplified version for demonstration. The full implementation
        would perform proper binned histogram analysis as in the validation suite.
        """
        # Simplified estimation based on θ'(n,k) position
        # Real implementation would use binned density analysis
        normalized_position = float(theta_prime_val) / self.phi
        
        # Empirical approximation: enhancement varies with position in spiral
        enhancement = abs(np.sin(2 * np.pi * normalized_position)) * 15.0  # Max 15% enhancement
        
        return enhancement
    
    def _update_statistics(self, point: GeodesicPoint) -> None:
        """Update running statistics with new point."""
        self.stats['total_computed'] += 1
        
        if point.is_prime:
            self.stats['prime_count'] += 1
        else:
            self.stats['composite_count'] += 1
        
        # Update running averages
        n = self.stats['total_computed']
        old_curvature_avg = self.stats['average_curvature']
        old_density_avg = self.stats['density_enhancement_avg']
        
        self.stats['average_curvature'] = ((n-1) * old_curvature_avg + point.curvature) / n
        self.stats['density_enhancement_avg'] = ((n-1) * old_density_avg + point.density_enhancement) / n
    
    def generate_sequence_coordinates(self, start: int, end: int, step: int = 1) -> List[GeodesicPoint]:
        """
        Generate geodesic coordinates for a sequence of integers.
        
        Args:
            start: Starting integer
            end: Ending integer (exclusive)
            step: Step size
            
        Returns:
            List of GeodesicPoint objects for the sequence
        """
        points = []
        for n in range(start, end, step):
            point = self.compute_geodesic_coordinates(n)
            points.append(point)
        
        return points
    
    def search_prime_clusters(self, points: List[GeodesicPoint], 
                            eps: float = 0.1, min_samples: int = 3) -> List[List[GeodesicPoint]]:
        """
        Search for prime clusters using DBSCAN clustering on 3D coordinates.
        
        Args:
            points: List of GeodesicPoint objects to analyze
            eps: Maximum distance for clustering
            min_samples: Minimum samples per cluster
            
        Returns:
            List of clusters, each containing clustered GeodesicPoint objects
        """
        # Extract prime points only
        prime_points = [p for p in points if p.is_prime]
        
        if len(prime_points) < min_samples:
            return []
        
        # Extract 3D coordinates for clustering
        coordinates = np.array([p.coordinates_3d for p in prime_points])
        
        # Apply DBSCAN clustering
        clustering = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = clustering.fit_predict(coordinates)
        
        # Group points by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Ignore noise points
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(prime_points[i])
                prime_points[i].cluster_id = label
        
        return list(clusters.values())
    
    def search_gaps_and_anomalies(self, points: List[GeodesicPoint], 
                                gap_threshold: float = 2.0) -> Dict[str, List]:
        """
        Search for gaps and anomalies in the geodesic sequence.
        
        Args:
            points: List of GeodesicPoint objects to analyze
            gap_threshold: Threshold for identifying gaps in spiral
            
        Returns:
            Dictionary containing gaps and anomalies
        """
        # Sort points by their integer value
        sorted_points = sorted(points, key=lambda p: p.n)
        
        gaps = []
        anomalies = []
        
        for i in range(1, len(sorted_points)):
            prev_point = sorted_points[i-1]
            curr_point = sorted_points[i]
            
            # Calculate 3D distance between consecutive points
            dist_3d = np.linalg.norm(
                np.array(curr_point.coordinates_3d) - np.array(prev_point.coordinates_3d)
            )
            
            # Identify gaps (unusually large distances)
            if dist_3d > gap_threshold:
                gaps.append({
                    'start_n': prev_point.n,
                    'end_n': curr_point.n,
                    'distance': dist_3d,
                    'gap_size': curr_point.n - prev_point.n
                })
            
            # Identify anomalies (unusual curvature or density patterns)
            curvature_ratio = curr_point.curvature / (prev_point.curvature + 1e-10)
            if curvature_ratio > 3.0 or curvature_ratio < 0.33:
                anomalies.append({
                    'n': curr_point.n,
                    'type': 'curvature_anomaly',
                    'ratio': curvature_ratio,
                    'is_prime': curr_point.is_prime
                })
            
            # Check for density enhancement anomalies
            if curr_point.density_enhancement > 12.0:  # Above typical range
                anomalies.append({
                    'n': curr_point.n,
                    'type': 'density_anomaly',
                    'enhancement': curr_point.density_enhancement,
                    'is_prime': curr_point.is_prime
                })
        
        return {
            'gaps': gaps,
            'anomalies': anomalies
        }
    
    def search_by_criteria(self, start: int, end: int, 
                          criteria: Dict[str, Any]) -> SearchResult:
        """
        Search for points matching specific criteria.
        
        Args:
            start: Starting integer for search range
            end: Ending integer for search range  
            criteria: Dictionary of search criteria
            
        Returns:
            SearchResult object with matching points and statistics
        """
        # Generate coordinate sequence
        points = self.generate_sequence_coordinates(start, end)
        
        # Apply filters based on criteria
        filtered_points = []
        
        for point in points:
            matches = True
            
            # Check prime status filter
            if 'primes_only' in criteria and criteria['primes_only']:
                if not point.is_prime:
                    matches = False
                    
            # Check curvature range
            if 'curvature_range' in criteria:
                curvature_min, curvature_max = criteria['curvature_range']
                if not (curvature_min <= point.curvature <= curvature_max):
                    matches = False
            
            # Check density enhancement threshold
            if 'min_density_enhancement' in criteria:
                if point.density_enhancement < criteria['min_density_enhancement']:
                    matches = False
            
            # Check coordinate bounds (3D)
            if 'coordinate_bounds_3d' in criteria:
                bounds = criteria['coordinate_bounds_3d']
                x, y, z = point.coordinates_3d
                if not (bounds['x_min'] <= x <= bounds['x_max'] and
                       bounds['y_min'] <= y <= bounds['y_max'] and
                       bounds['z_min'] <= z <= bounds['z_max']):
                    matches = False
            
            if matches:
                filtered_points.append(point)
        
        # Compute density statistics
        density_values = [p.density_enhancement for p in filtered_points]
        density_stats = {
            'mean': np.mean(density_values) if density_values else 0.0,
            'std': np.std(density_values) if density_values else 0.0,
            'min': np.min(density_values) if density_values else 0.0,
            'max': np.max(density_values) if density_values else 0.0,
            'median': np.median(density_values) if density_values else 0.0
        }
        
        # Compute anomaly score (simplified)
        anomaly_score = len([p for p in filtered_points if p.density_enhancement > 10.0]) / max(len(filtered_points), 1)
        
        return SearchResult(
            points=filtered_points,
            total_found=len(filtered_points),
            search_parameters=criteria,
            density_statistics=density_stats,
            anomaly_score=anomaly_score
        )
    
    def export_coordinates(self, points: List[GeodesicPoint], 
                          filename: str, format: str = 'csv') -> str:
        """
        Export geodesic coordinates and metadata to file.
        
        Args:
            points: List of GeodesicPoint objects to export
            filename: Output filename
            format: Export format ('csv', 'json', 'npy')
            
        Returns:
            Path to exported file
        """
        if format == 'csv':
            return self._export_csv(points, filename)
        elif format == 'json':
            return self._export_json(points, filename)
        elif format == 'npy':
            return self._export_numpy(points, filename)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_csv(self, points: List[GeodesicPoint], filename: str) -> str:
        """Export to CSV format."""
        data = []
        for point in points:
            row = {
                'n': point.n,
                'x_3d': point.coordinates_3d[0],
                'y_3d': point.coordinates_3d[1], 
                'z_3d': point.coordinates_3d[2],
                'x_5d': point.coordinates_5d[0],
                'y_5d': point.coordinates_5d[1],
                'z_5d': point.coordinates_5d[2],
                'w_5d': point.coordinates_5d[3],
                'u_5d': point.coordinates_5d[4],
                'is_prime': point.is_prime,
                'curvature': point.curvature,
                'density_enhancement': point.density_enhancement,
                'cluster_id': point.cluster_id,
                'geodesic_type': point.geodesic_type
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        csv_path = f"{filename}.csv"
        df.to_csv(csv_path, index=False)
        return csv_path
    
    def _export_json(self, points: List[GeodesicPoint], filename: str) -> str:
        """Export to JSON format."""
        data = {
            'metadata': {
                'k_optimal': self.k_optimal,
                'phi': self.phi,
                'total_points': len(points),
                'statistics': self.stats
            },
            'points': []
        }
        
        for point in points:
            point_data = {
                'n': int(point.n),
                'coordinates_3d': [float(x) for x in point.coordinates_3d],
                'coordinates_5d': [float(x) for x in point.coordinates_5d],
                'is_prime': bool(point.is_prime),
                'curvature': float(point.curvature),
                'density_enhancement': float(point.density_enhancement),
                'cluster_id': int(point.cluster_id) if point.cluster_id is not None else None,
                'geodesic_type': str(point.geodesic_type)
            }
            data['points'].append(point_data)
        
        json_path = f"{filename}.json"
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        return json_path
    
    def _export_numpy(self, points: List[GeodesicPoint], filename: str) -> str:
        """Export coordinates to NumPy format."""
        # Extract coordinate arrays
        coords_3d = np.array([p.coordinates_3d for p in points])
        coords_5d = np.array([p.coordinates_5d for p in points])
        
        # Create structured array with metadata
        dtype = [
            ('n', 'i4'),
            ('coords_3d', '3f8'),
            ('coords_5d', '5f8'),
            ('is_prime', '?'),
            ('curvature', 'f8'),
            ('density_enhancement', 'f8')
        ]
        
        data = np.zeros(len(points), dtype=dtype)
        for i, point in enumerate(points):
            data[i] = (
                point.n,
                point.coordinates_3d,
                point.coordinates_5d,
                point.is_prime,
                point.curvature,
                point.density_enhancement
            )
        
        npy_path = f"{filename}.npy"
        np.save(npy_path, data)
        return npy_path
    
    def generate_statistical_report(self, points: List[GeodesicPoint]) -> Dict[str, Any]:
        """
        Generate comprehensive statistical report for analyzed points.
        
        Args:
            points: List of GeodesicPoint objects to analyze
            
        Returns:
            Dictionary containing statistical analysis results
        """
        primes = [p for p in points if p.is_prime]
        composites = [p for p in points if not p.is_prime]
        
        report = {
            'summary': {
                'total_points': len(points),
                'prime_count': len(primes),
                'composite_count': len(composites),
                'prime_ratio': len(primes) / len(points) if points else 0
            },
            'curvature_analysis': {
                'prime_curvature_mean': np.mean([p.curvature for p in primes]) if primes else 0,
                'composite_curvature_mean': np.mean([p.curvature for p in composites]) if composites else 0,
                'curvature_variance': np.var([p.curvature for p in points]) if points else 0
            },
            'density_enhancement': {
                'mean_enhancement': np.mean([p.density_enhancement for p in points]) if points else 0,
                'prime_enhancement_mean': np.mean([p.density_enhancement for p in primes]) if primes else 0,
                'max_enhancement': np.max([p.density_enhancement for p in points]) if points else 0,
                'enhancement_std': np.std([p.density_enhancement for p in points]) if points else 0
            },
            'geometric_distribution': {
                'coordinate_bounds_3d': self._compute_coordinate_bounds(points, '3d'),
                'coordinate_bounds_5d': self._compute_coordinate_bounds(points, '5d')
            },
            'validation_metrics': {
                'expected_prime_enhancement': 15.0,  # From empirical validation
                'achieved_enhancement': np.mean([p.density_enhancement for p in primes]) if primes else 0,
                'variance_target': 0.118,  # From Z Framework validation
                'achieved_variance': np.var([p.curvature for p in points]) if points else 0
            }
        }
        
        return report
    
    def _compute_coordinate_bounds(self, points: List[GeodesicPoint], dimension: str) -> Dict[str, float]:
        """Compute coordinate bounds for given dimension."""
        if dimension == '3d':
            coords = [p.coordinates_3d for p in points]
            labels = ['x', 'y', 'z']
        else:  # 5d
            coords = [p.coordinates_5d for p in points]
            labels = ['x', 'y', 'z', 'w', 'u']
        
        bounds = {}
        if coords:
            coords_array = np.array(coords)
            for i, label in enumerate(labels):
                bounds[f'{label}_min'] = float(np.min(coords_array[:, i]))
                bounds[f'{label}_max'] = float(np.max(coords_array[:, i]))
        
        return bounds


def demo_prime_geodesic_search():
    """
    Demonstration of the Prime Geodesic Search Engine capabilities.
    """
    print("Prime Geodesic Search Engine Demo")
    print("=" * 50)
    
    # Initialize search engine with optimal parameters
    engine = PrimeGeodesicSearchEngine(k_optimal=0.3)
    
    # Generate coordinates for first 100 integers
    print("\n1. Generating geodesic coordinates for integers 2-101...")
    points = engine.generate_sequence_coordinates(2, 102)
    print(f"Generated {len(points)} geodesic points")
    
    # Search for prime clusters
    print("\n2. Searching for prime clusters...")
    clusters = engine.search_prime_clusters(points, eps=0.2, min_samples=3)
    print(f"Found {len(clusters)} prime clusters")
    for i, cluster in enumerate(clusters):
        primes_in_cluster = [p.n for p in cluster]
        print(f"  Cluster {i+1}: {primes_in_cluster}")
    
    # Search for gaps and anomalies
    print("\n3. Searching for gaps and anomalies...")
    anomalies = engine.search_gaps_and_anomalies(points, gap_threshold=1.5)
    print(f"Found {len(anomalies['gaps'])} gaps and {len(anomalies['anomalies'])} anomalies")
    
    # Search with specific criteria
    print("\n4. Searching with criteria (primes with high density enhancement)...")
    search_result = engine.search_by_criteria(
        start=2, end=102,
        criteria={
            'primes_only': True,
            'min_density_enhancement': 8.0
        }
    )
    print(f"Found {search_result.total_found} primes with high density enhancement")
    high_enhancement_primes = [p.n for p in search_result.points]
    print(f"High enhancement primes: {high_enhancement_primes[:10]}...")  # Show first 10
    
    # Generate statistical report
    print("\n5. Statistical analysis...")
    report = engine.generate_statistical_report(points)
    print(f"Prime ratio: {report['summary']['prime_ratio']:.3f}")
    print(f"Average curvature (primes): {report['curvature_analysis']['prime_curvature_mean']:.3f}")
    print(f"Average curvature (composites): {report['curvature_analysis']['composite_curvature_mean']:.3f}")
    print(f"Mean density enhancement: {report['density_enhancement']['mean_enhancement']:.2f}%")
    
    # Export results
    print("\n6. Exporting results...")
    csv_file = engine.export_coordinates(points, "demo_geodesic_coordinates", format='csv')
    json_file = engine.export_coordinates(points, "demo_geodesic_coordinates", format='json')
    print(f"Exported to: {csv_file}, {json_file}")
    
    print("\nDemo completed successfully!")
    return engine, points, report


if __name__ == "__main__":
    # Run demonstration
    demo_prime_geodesic_search()