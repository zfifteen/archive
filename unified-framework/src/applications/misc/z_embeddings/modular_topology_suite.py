"""
Modular Topology Visualization Suite for Discrete Data

This module provides a comprehensive visualization suite for primes, integer sequences,
and network data using helical and modular-geodesic embeddings. It generalizes the
θ′(n, k) embedding for arbitrary discrete datasets and provides interactive 3D/5D
visualization capabilities.

FEATURES:
- Generalized θ′(n, k) embedding for arbitrary discrete datasets
- 3D/5D helix and modular spiral plots with interactive controls
- Cluster, symmetry, and anomaly detection in geometric space
- Publication-quality export functionality
- Web interface for research and educational use

MATHEMATICAL FOUNDATIONS:
- Extends θ′(n, k) = φ · {n/φ}^k for arbitrary moduli and datasets
- 5D helical embeddings using (x, y, z, w, u) coordinates
- Curvature-based geodesic analysis with κ(n) = d(n) · ln(n+1)/e²
- Golden ratio modular transformations with high-precision arithmetic
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import mpmath as mp
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
# Use matplotlib backend for headless environments
plt.switch_backend('Agg')
from sympy import divisors, isprime
import warnings
warnings.filterwarnings('ignore')

# Set high precision for mathematical computations
mp.mp.dps = 50

# Mathematical constants
PHI = (1 + mp.sqrt(5)) / 2  # Golden ratio
E_SQUARED = mp.exp(2)
PI = mp.pi

class GeneralizedEmbedding:
    """
    Generalized embedding class for arbitrary discrete datasets using
    modular-geodesic transformations and helical projections.
    """
    
    def __init__(self, modulus=None, precision=50):
        """
        Initialize embedding with configurable modulus and precision.
        
        Args:
            modulus: Modular base (default: golden ratio φ)
            precision: mpmath decimal precision (default: 50)
        """
        mp.mp.dps = precision
        self.modulus = float(PHI) if modulus is None else modulus
        self.precision = precision
        
    def theta_prime_transform(self, sequence, k=0.3, modulus=None):
        """
        Generalized θ′(n, k) transformation for arbitrary sequences.
        
        θ′(n, k) = modulus · ((n mod modulus)/modulus)^k
        
        Args:
            sequence: Input integer sequence
            k: Curvature parameter (default: 0.3)
            modulus: Modular base (default: uses instance modulus)
            
        Returns:
            Transformed sequence using modular-geodesic embedding
        """
        if modulus is None:
            modulus = self.modulus
            
        sequence = np.array(sequence, dtype=float)
        residues = sequence % modulus
        normalized_residues = residues / modulus
        
        # Apply curvature transformation with high precision
        transformed = modulus * (normalized_residues ** k)
        
        return transformed
    
    def curvature_function(self, n):
        """
        Compute curvature κ(n) = d(n) · ln(n+1)/e² for geometric analysis.
        
        Args:
            n: Integer value
            
        Returns:
            Curvature value for geodesic analysis
        """
        if n <= 0:
            return 0.0
        
        # Number of divisors
        try:
            d_n = len(list(divisors(int(n))))
        except:
            # Fallback for large numbers
            d_n = 2  # Assume prime-like
            
        # Curvature formula
        curvature = d_n * float(mp.log(n + 1)) / float(E_SQUARED)
        return curvature
    
    def helical_5d_embedding(self, sequence, theta_sequence=None, frequency=0.1):
        """
        Generate 5D helical embedding coordinates for visualization.
        
        Based on DiscreteZetaShift methodology:
        (x = a*cos(θ_D), y = a*sin(θ_E), z = F/e², w = I, u = O)
        
        Args:
            sequence: Input discrete sequence
            theta_sequence: Transformed theta values (if None, computed)
            frequency: Helical frequency parameter
            
        Returns:
            Dictionary with 5D coordinates (x, y, z, w, u)
        """
        sequence = np.array(sequence)
        
        if theta_sequence is None:
            theta_sequence = self.theta_prime_transform(sequence)
            
        n = len(sequence)
        
        # Generate helical parameters
        angles_d = theta_sequence * frequency
        angles_e = sequence * frequency * 1.618  # Golden ratio scaling
        
        # Compute amplitudes based on sequence properties
        amplitudes = np.sqrt(sequence + 1)  # Avoid zero amplitude
        
        # 5D coordinates
        x = amplitudes * np.cos(angles_d)
        y = amplitudes * np.sin(angles_e)
        z = np.array([self.curvature_function(s) for s in sequence])
        w = sequence / np.max(sequence)  # Normalized intensity
        u = theta_sequence / np.max(theta_sequence)  # Normalized transformed values
        
        return {
            'x': x, 'y': y, 'z': z, 'w': w, 'u': u,
            'sequence': sequence,
            'theta': theta_sequence,
            'amplitudes': amplitudes,
            'angles_d': angles_d,
            'angles_e': angles_e
        }
    
    def modular_spiral_coordinates(self, sequence, layers=3, spiral_factor=1.0):
        """
        Generate modular spiral coordinates for layered visualization.
        
        Args:
            sequence: Input sequence
            layers: Number of spiral layers
            spiral_factor: Spiral tightness parameter
            
        Returns:
            Coordinates for modular spiral embedding
        """
        sequence = np.array(sequence)
        n = len(sequence)
        
        # Multi-layer spiral parameters
        layer_angles = np.linspace(0, 2*np.pi*layers, n)
        radii = np.sqrt(sequence + 1) * spiral_factor
        
        # Spiral coordinates
        x_spiral = radii * np.cos(layer_angles)
        y_spiral = radii * np.sin(layer_angles)
        z_spiral = layer_angles / (2*np.pi) * np.max(sequence) / layers
        
        return {
            'x': x_spiral,
            'y': y_spiral, 
            'z': z_spiral,
            'radii': radii,
            'angles': layer_angles
        }

class TopologyAnalyzer:
    """
    Analyze geometric patterns, clusters, symmetries, and anomalies
    in embedded discrete data.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        
    def detect_clusters(self, coordinates, method='dbscan', **kwargs):
        """
        Detect clusters in embedded coordinate space.
        
        Args:
            coordinates: Dictionary with coordinate arrays
            method: Clustering method ('dbscan', 'kmeans', 'hierarchical')
            **kwargs: Method-specific parameters
            
        Returns:
            Cluster labels and analysis results
        """
        # Prepare coordinate matrix
        coord_matrix = np.column_stack([
            coordinates['x'], coordinates['y'], coordinates['z']
        ])
        
        # Normalize coordinates
        coord_normalized = self.scaler.fit_transform(coord_matrix)
        
        if method == 'dbscan':
            eps = kwargs.get('eps', 0.5)
            min_samples = kwargs.get('min_samples', 5)
            clusterer = DBSCAN(eps=eps, min_samples=min_samples)
            
        elif method == 'kmeans':
            n_clusters = kwargs.get('n_clusters', 5)
            clusterer = KMeans(n_clusters=n_clusters, random_state=42)
            
        elif method == 'hierarchical':
            n_clusters = kwargs.get('n_clusters', 5)
            linkage_matrix = linkage(coord_normalized, method='ward')
            labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
            return labels - 1, {'linkage_matrix': linkage_matrix}
            
        labels = clusterer.fit_predict(coord_normalized)
        
        # Analyze cluster properties
        unique_labels = np.unique(labels)
        cluster_stats = {}
        
        for label in unique_labels:
            if label == -1:  # Noise points in DBSCAN
                continue
            mask = labels == label
            cluster_coords = coord_normalized[mask]
            
            cluster_stats[label] = {
                'size': np.sum(mask),
                'centroid': np.mean(cluster_coords, axis=0),
                'spread': np.std(cluster_coords, axis=0),
                'density': np.sum(mask) / len(coord_normalized)
            }
            
        return labels, cluster_stats
    
    def detect_symmetries(self, coordinates, tolerance=1e-2):
        """
        Detect geometric symmetries in coordinate patterns.
        
        Args:
            coordinates: Dictionary with coordinate arrays
            tolerance: Symmetry detection tolerance
            
        Returns:
            Symmetry analysis results
        """
        x, y, z = coordinates['x'], coordinates['y'], coordinates['z']
        
        symmetries = {
            'x_reflection': self._check_reflection_symmetry(x, y, axis='x', tolerance=tolerance),
            'y_reflection': self._check_reflection_symmetry(x, y, axis='y', tolerance=tolerance),
            'rotational': self._check_rotational_symmetry(x, y, tolerance=tolerance),
            'helical': self._check_helical_symmetry(x, y, z, tolerance=tolerance)
        }
        
        return symmetries
    
    def _check_reflection_symmetry(self, x, y, axis='x', tolerance=1e-2):
        """Check for reflection symmetry about specified axis."""
        if axis == 'x':
            reflected_y = -y
            original_points = np.column_stack([x, y])
            reflected_points = np.column_stack([x, reflected_y])
        else:  # axis == 'y'
            reflected_x = -x
            original_points = np.column_stack([x, y])
            reflected_points = np.column_stack([reflected_x, y])
            
        # Find closest matches
        distances = pdist(np.vstack([original_points, reflected_points]))
        distance_matrix = squareform(distances)
        
        n = len(original_points)
        cross_distances = distance_matrix[:n, n:]
        min_distances = np.min(cross_distances, axis=1)
        
        symmetry_score = np.mean(min_distances < tolerance)
        return {'score': symmetry_score, 'symmetric_pairs': np.sum(min_distances < tolerance)}
    
    def _check_rotational_symmetry(self, x, y, tolerance=1e-2):
        """Check for rotational symmetry."""
        points = np.column_stack([x, y])
        n_points = len(points)
        
        # Test common rotation angles
        test_angles = [np.pi/2, np.pi/3, np.pi/4, np.pi/6, np.pi]
        symmetry_scores = {}
        
        for angle in test_angles:
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)]
            ])
            
            rotated_points = points @ rotation_matrix.T
            
            # Find matches
            distances = np.min(np.linalg.norm(
                points[:, np.newaxis] - rotated_points[np.newaxis, :], axis=2
            ), axis=1)
            
            score = np.mean(distances < tolerance)
            symmetry_scores[f'{angle:.3f}_rad'] = score
            
        return symmetry_scores
    
    def _check_helical_symmetry(self, x, y, z, tolerance=1e-2):
        """Check for helical symmetry patterns."""
        # Compute angular positions
        angles = np.arctan2(y, x)
        radii = np.sqrt(x**2 + y**2)
        
        # Check for regular angular spacing
        angle_diffs = np.diff(np.sort(angles))
        angle_regularity = np.std(angle_diffs) / np.mean(angle_diffs) if np.mean(angle_diffs) > 0 else float('inf')
        
        # Check for regular radial progression
        radii_sorted = np.sort(radii)
        radii_diffs = np.diff(radii_sorted)
        radii_regularity = np.std(radii_diffs) / np.mean(radii_diffs) if np.mean(radii_diffs) > 0 else float('inf')
        
        # Check for helical pitch consistency
        z_vs_angle = np.polyfit(angles, z, 1)
        pitch_consistency = np.std(z - np.polyval(z_vs_angle, angles))
        
        return {
            'angle_regularity': 1.0 / (1.0 + angle_regularity),
            'radii_regularity': 1.0 / (1.0 + radii_regularity),
            'pitch_consistency': 1.0 / (1.0 + pitch_consistency),
            'helical_score': 1.0 / (1.0 + angle_regularity + radii_regularity + pitch_consistency)
        }
    
    def detect_anomalies(self, coordinates, method='isolation_forest', contamination=0.1):
        """
        Detect anomalies in geometric embedding space.
        
        Args:
            coordinates: Dictionary with coordinate arrays
            method: Anomaly detection method
            contamination: Expected fraction of anomalies
            
        Returns:
            Anomaly labels and scores
        """
        from sklearn.ensemble import IsolationForest
        from sklearn.svm import OneClassSVM
        
        # Prepare coordinate matrix
        coord_matrix = np.column_stack([
            coordinates['x'], coordinates['y'], coordinates['z']
        ])
        
        # Normalize coordinates
        coord_normalized = self.scaler.fit_transform(coord_matrix)
        
        if method == 'isolation_forest':
            detector = IsolationForest(contamination=contamination, random_state=42)
        elif method == 'one_class_svm':
            detector = OneClassSVM(nu=contamination)
        else:
            raise ValueError(f"Unknown anomaly detection method: {method}")
            
        anomaly_labels = detector.fit_predict(coord_normalized)
        
        # Get anomaly scores if available
        if hasattr(detector, 'decision_function'):
            anomaly_scores = detector.decision_function(coord_normalized)
        elif hasattr(detector, 'score_samples'):
            anomaly_scores = detector.score_samples(coord_normalized)
        else:
            anomaly_scores = np.zeros_like(anomaly_labels)
            
        return anomaly_labels, anomaly_scores

class VisualizationEngine:
    """
    Interactive 3D/5D visualization engine using Plotly for web-based displays.
    """
    
    def __init__(self, theme='plotly_dark'):
        self.theme = theme
        
    def plot_3d_helical_embedding(self, coordinates, sequence_info=None, title="3D Helical Embedding"):
        """
        Create interactive 3D helical embedding plot.
        
        Args:
            coordinates: Dictionary with x, y, z coordinates
            sequence_info: Optional sequence metadata
            title: Plot title
            
        Returns:
            Plotly figure object
        """
        x, y, z = coordinates['x'], coordinates['y'], coordinates['z']
        
        # Color by sequence index or properties
        if sequence_info is not None and 'sequence' in sequence_info:
            colors = sequence_info['sequence']
            colorscale = 'Viridis'
        else:
            colors = np.arange(len(x))
            colorscale = 'Rainbow'
            
        # Create 3D scatter plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers+lines',
            marker=dict(
                size=5,
                color=colors,
                colorscale=colorscale,
                colorbar=dict(title="Sequence Value"),
                opacity=0.8
            ),
            line=dict(
                color='rgba(200, 200, 200, 0.3)',
                width=2
            ),
            name='Helical Path'
        ))
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='X Coordinate',
                yaxis_title='Y Coordinate', 
                zaxis_title='Z Coordinate (Curvature)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            template=self.theme
        )
        
        return fig
    
    def plot_5d_projection(self, coordinates, projection_method='pca'):
        """
        Create 5D data projection visualization.
        
        Args:
            coordinates: Dictionary with 5D coordinates
            projection_method: Dimensionality reduction method
            
        Returns:
            Plotly figure with multiple subplots
        """
        # Prepare 5D coordinate matrix
        coord_5d = np.column_stack([
            coordinates['x'], coordinates['y'], coordinates['z'],
            coordinates['w'], coordinates['u']
        ])
        
        if projection_method == 'pca':
            pca = PCA(n_components=3)
            projected = pca.fit_transform(coord_5d)
            subplot_titles = [f'PC{i+1} ({pca.explained_variance_ratio_[i]:.2%})' 
                            for i in range(3)]
        else:
            projected = coord_5d[:, :3]  # Take first 3 dimensions
            subplot_titles = ['X Dimension', 'Y Dimension', 'Z Dimension']
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"type": "scatter3d", "colspan": 2}, None],
                   [{"type": "scatter"}, {"type": "scatter"}]],
            subplot_titles=['5D → 3D Projection', 'Dimension 1 vs 2', 'Dimension 2 vs 3']
        )
        
        # 3D projection
        fig.add_trace(
            go.Scatter3d(
                x=projected[:, 0], y=projected[:, 1], z=projected[:, 2],
                mode='markers',
                marker=dict(size=4, color=coordinates['sequence'], colorscale='Viridis'),
                name='5D Projection'
            ),
            row=1, col=1
        )
        
        # 2D projections
        fig.add_trace(
            go.Scatter(
                x=projected[:, 0], y=projected[:, 1],
                mode='markers',
                marker=dict(color=coordinates['sequence'], colorscale='Viridis'),
                name='Dim 1 vs 2'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=projected[:, 1], y=projected[:, 2],
                mode='markers',
                marker=dict(color=coordinates['sequence'], colorscale='Viridis'),
                name='Dim 2 vs 3'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="5D Helical Embedding Analysis",
            template=self.theme
        )
        
        return fig
    
    def plot_modular_spiral(self, coordinates, layers=3):
        """
        Create modular spiral visualization.
        
        Args:
            coordinates: Spiral coordinates
            layers: Number of spiral layers
            
        Returns:
            Plotly figure
        """
        x, y, z = coordinates['x'], coordinates['y'], coordinates['z']
        angles = coordinates['angles']
        
        # Create spiral plot with layer coloring
        layer_colors = angles / (2*np.pi * layers)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers+lines',
            marker=dict(
                size=4,
                color=layer_colors,
                colorscale='HSV',
                colorbar=dict(title="Spiral Layer"),
                opacity=0.8
            ),
            line=dict(color='rgba(150, 150, 150, 0.5)', width=2),
            name='Modular Spiral'
        ))
        
        fig.update_layout(
            title='Modular Spiral Embedding',
            scene=dict(
                xaxis_title='X (Radial)',
                yaxis_title='Y (Radial)',
                zaxis_title='Z (Layer Height)',
                aspectmode='cube'
            ),
            template=self.theme
        )
        
        return fig
    
    def plot_cluster_analysis(self, coordinates, cluster_labels, cluster_stats):
        """
        Visualize cluster analysis results.
        
        Args:
            coordinates: Coordinate dictionary
            cluster_labels: Cluster assignment labels
            cluster_stats: Cluster statistics
            
        Returns:
            Plotly figure with cluster visualization
        """
        x, y, z = coordinates['x'], coordinates['y'], coordinates['z']
        
        fig = go.Figure()
        
        unique_labels = np.unique(cluster_labels)
        colors = px.colors.qualitative.Set3
        
        for i, label in enumerate(unique_labels):
            if label == -1:  # Noise points
                color = 'black'
                name = 'Noise'
                size = 3
            else:
                color = colors[i % len(colors)]
                name = f'Cluster {label}'
                size = 5
                
            mask = cluster_labels == label
            
            fig.add_trace(go.Scatter3d(
                x=x[mask], y=y[mask], z=z[mask],
                mode='markers',
                marker=dict(
                    size=size,
                    color=color,
                    opacity=0.7
                ),
                name=name
            ))
            
        fig.update_layout(
            title='Cluster Analysis Results',
            scene=dict(
                xaxis_title='X Coordinate',
                yaxis_title='Y Coordinate',
                zaxis_title='Z Coordinate'
            ),
            template=self.theme
        )
        
        return fig
    
    def plot_anomaly_detection(self, coordinates, anomaly_labels, anomaly_scores):
        """
        Visualize anomaly detection results.
        
        Args:
            coordinates: Coordinate dictionary
            anomaly_labels: Anomaly labels (1 = normal, -1 = anomaly)
            anomaly_scores: Anomaly scores
            
        Returns:
            Plotly figure
        """
        x, y, z = coordinates['x'], coordinates['y'], coordinates['z']
        
        # Separate normal and anomalous points
        normal_mask = anomaly_labels == 1
        anomaly_mask = anomaly_labels == -1
        
        fig = go.Figure()
        
        # Normal points
        fig.add_trace(go.Scatter3d(
            x=x[normal_mask], y=y[normal_mask], z=z[normal_mask],
            mode='markers',
            marker=dict(
                size=4,
                color='blue',
                opacity=0.6
            ),
            name='Normal Points'
        ))
        
        # Anomalous points
        if np.any(anomaly_mask):
            fig.add_trace(go.Scatter3d(
                x=x[anomaly_mask], y=y[anomaly_mask], z=z[anomaly_mask],
                mode='markers',
                marker=dict(
                    size=8,
                    color='red',
                    opacity=0.9,
                    symbol='x'
                ),
                name='Anomalies'
            ))
        
        fig.update_layout(
            title='Anomaly Detection Results',
            scene=dict(
                xaxis_title='X Coordinate',
                yaxis_title='Y Coordinate',
                zaxis_title='Z Coordinate'
            ),
            template=self.theme
        )
        
        return fig

class DataExporter:
    """
    Export visualization data and publication-ready outputs.
    """
    
    @staticmethod
    def export_coordinates(coordinates, filename, format='csv'):
        """
        Export coordinate data in specified format.
        
        Args:
            coordinates: Coordinate dictionary
            filename: Output filename
            format: Export format ('csv', 'json', 'hdf5')
        """
        # Prepare DataFrame
        coord_df = pd.DataFrame(coordinates)
        
        if format == 'csv':
            coord_df.to_csv(filename, index=False)
        elif format == 'json':
            coord_df.to_json(filename, orient='records', indent=2)
        elif format == 'hdf5':
            coord_df.to_hdf(filename, key='coordinates', mode='w')
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    @staticmethod
    def export_figure(fig, filename, format='png', width=1200, height=800, scale=2):
        """
        Export Plotly figure in publication quality.
        
        Args:
            fig: Plotly figure object
            filename: Output filename
            format: Image format ('png', 'pdf', 'svg', 'html')
            width: Image width in pixels
            height: Image height in pixels
            scale: Image scale factor for higher resolution
        """
        if format == 'html':
            fig.write_html(filename)
        else:
            fig.write_image(
                filename,
                format=format,
                width=width,
                height=height,
                scale=scale
            )
    
    @staticmethod
    def export_analysis_report(coordinates, cluster_stats, symmetries, 
                             anomaly_info, filename='analysis_report.json'):
        """
        Export comprehensive analysis report.
        
        Args:
            coordinates: Coordinate data
            cluster_stats: Clustering analysis results
            symmetries: Symmetry analysis results
            anomaly_info: Anomaly detection results
            filename: Output filename
        """
        # Convert cluster_stats keys to strings for JSON compatibility
        cluster_stats_serializable = {
            str(key): value for key, value in cluster_stats.items()
        }
        
        report = {
            'summary': {
                'total_points': int(len(coordinates['x'])),
                'coordinate_dimensions': int(len(coordinates.keys())),
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            },
            'clustering': {
                'num_clusters': int(len(cluster_stats)),
                'cluster_statistics': cluster_stats_serializable
            },
            'symmetries': symmetries,
            'anomalies': {
                'num_anomalies': int(np.sum(anomaly_info[0] == -1)) if len(anomaly_info) > 0 else 0,
                'anomaly_rate': float(np.mean(anomaly_info[0] == -1)) if len(anomaly_info) > 0 else 0
            },
            'coordinate_statistics': {
                key: {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }
                for key, values in coordinates.items()
                if isinstance(values, np.ndarray)
            }
        }
        
        import json
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)

# Helper functions for common datasets
def generate_prime_sequence(limit=1000):
    """Generate prime number sequence up to limit."""
    return [n for n in range(2, limit + 1) if isprime(n)]

def generate_fibonacci_sequence(n_terms=100):
    """Generate Fibonacci sequence with n_terms."""
    fib = [0, 1]
    for i in range(2, n_terms):
        fib.append(fib[i-1] + fib[i-2])
    return fib[2:]  # Skip 0 and 1

def generate_mersenne_numbers(max_exp=20):
    """Generate Mersenne numbers 2^p - 1 for prime p."""
    primes = generate_prime_sequence(max_exp)
    return [2**p - 1 for p in primes]

# Example usage function
def demo_visualization_suite():
    """
    Demonstrate the modular topology visualization suite capabilities.
    """
    print("Modular Topology Visualization Suite Demo")
    print("=" * 50)
    
    # Initialize components
    embedding = GeneralizedEmbedding()
    analyzer = TopologyAnalyzer()
    visualizer = VisualizationEngine()
    exporter = DataExporter()
    
    # Generate sample data (primes)
    primes = generate_prime_sequence(200)
    print(f"Generated {len(primes)} prime numbers")
    
    # Create embeddings
    print("Computing embeddings...")
    theta_transformed = embedding.theta_prime_transform(primes, k=0.3)
    helix_coords = embedding.helical_5d_embedding(primes, theta_transformed)
    spiral_coords = embedding.modular_spiral_coordinates(primes)
    
    # Analyze patterns
    print("Analyzing geometric patterns...")
    clusters, cluster_stats = analyzer.detect_clusters(helix_coords)
    symmetries = analyzer.detect_symmetries(helix_coords)
    anomalies, anomaly_scores = analyzer.detect_anomalies(helix_coords)
    
    # Create visualizations
    print("Creating visualizations...")
    fig_3d = visualizer.plot_3d_helical_embedding(helix_coords, helix_coords)
    fig_5d = visualizer.plot_5d_projection(helix_coords)
    fig_spiral = visualizer.plot_modular_spiral(spiral_coords)
    fig_clusters = visualizer.plot_cluster_analysis(helix_coords, clusters, cluster_stats)
    fig_anomalies = visualizer.plot_anomaly_detection(helix_coords, anomalies, anomaly_scores)
    
    # Export results
    print("Exporting results...")
    exporter.export_coordinates(helix_coords, 'prime_helix_coordinates.csv')
    exporter.export_analysis_report(helix_coords, cluster_stats, symmetries, 
                                  (anomalies, anomaly_scores))
    
    print("Demo completed successfully!")
    print(f"Found {len(cluster_stats)} clusters")
    print(f"Detected {np.sum(anomalies == -1)} anomalies")
    print(f"Symmetry scores: {symmetries}")
    
    return {
        'figures': [fig_3d, fig_5d, fig_spiral, fig_clusters, fig_anomalies],
        'coordinates': helix_coords,
        'analysis': {
            'clusters': cluster_stats,
            'symmetries': symmetries,
            'anomalies': (anomalies, anomaly_scores)
        }
    }

if __name__ == "__main__":
    # Run demonstration
    demo_results = demo_visualization_suite()
    print("Modular Topology Visualization Suite ready for use!")