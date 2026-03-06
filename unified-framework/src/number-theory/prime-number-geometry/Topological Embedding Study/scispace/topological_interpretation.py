import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy
import json
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

print("Loading embeddings for topological interpretation...")

# Load embeddings for interpretation
try:
    with open('/home/sandbox/topological_embeddings.json', 'r') as f:
        embeddings = json.load(f)
    print(f"Loaded {len(embeddings)} embeddings")
except FileNotFoundError:
    print("Error: topological_embeddings.json not found. Run topological_analysis.py first.")
    exit(1)

# Geometric structure analysis functions
def compute_curvature(x, y, z):
    """Compute discrete curvature of the embedded manifold"""
    if len(x) < 3:
        return np.array([0])
    
    # Compute first and second derivatives using finite differences
    dx = np.gradient(x)
    dy = np.gradient(y)
    dz = np.gradient(z)
    dx2 = np.gradient(dx)
    dy2 = np.gradient(dy)
    dz2 = np.gradient(dz)
    
    # Compute curvature using discrete approximation
    # κ = |r'' × r'| / |r'|³
    cross_x = dy * dz2 - dz * dy2
    cross_y = dz * dx2 - dx * dz2
    cross_z = dx * dy2 - dy * dx2
    
    cross_magnitude = np.sqrt(cross_x**2 + cross_y**2 + cross_z**2)
    velocity_magnitude = np.sqrt(dx**2 + dy**2 + dz**2)
    
    # Avoid division by zero
    curvature = np.zeros_like(cross_magnitude)
    valid_mask = velocity_magnitude > 1e-10
    curvature[valid_mask] = cross_magnitude[valid_mask] / (velocity_magnitude[valid_mask]**3)
    
    return curvature

def compute_torsion(x, y, z):
    """Compute discrete torsion of the embedded curve"""
    if len(x) < 4:
        return np.array([0])
    
    # First derivatives
    dx = np.gradient(x)
    dy = np.gradient(y)
    dz = np.gradient(z)
    
    # Second derivatives
    dx2 = np.gradient(dx)
    dy2 = np.gradient(dy)
    dz2 = np.gradient(dz)
    
    # Third derivatives
    dx3 = np.gradient(dx2)
    dy3 = np.gradient(dy2)
    dz3 = np.gradient(dz2)
    
    # Compute torsion: τ = (r' × r'') · r''' / |r' × r''|²
    cross_x = dy * dz2 - dz * dy2
    cross_y = dz * dx2 - dx * dz2
    cross_z = dx * dy2 - dy * dx2
    
    dot_product = cross_x * dx3 + cross_y * dy3 + cross_z * dz3
    cross_magnitude_sq = cross_x**2 + cross_y**2 + cross_z**2
    
    torsion = np.zeros_like(dot_product)
    valid_mask = cross_magnitude_sq > 1e-10
    torsion[valid_mask] = dot_product[valid_mask] / cross_magnitude_sq[valid_mask]
    
    return torsion

def compute_persistent_homology_approximation(points, max_distance=None):
    """Approximate persistent homology using distance-based filtration"""
    if len(points) < 4:
        return {'betti_0': 1, 'betti_1': 0, 'betti_2': 0}
    
    # Compute pairwise distances
    distances = pdist(points)
    
    if max_distance is None:
        max_distance = np.percentile(distances, 75)  # Use 75th percentile as threshold
    
    # Create adjacency matrix for points within threshold distance
    distance_matrix = squareform(distances)
    adjacency = (distance_matrix <= max_distance).astype(int)
    
    # Convert to sparse matrix for efficiency
    sparse_adj = csr_matrix(adjacency)
    
    # Compute connected components (approximation of 0th Betti number)
    n_components, labels = connected_components(sparse_adj, directed=False)
    
    # Simple approximation of higher Betti numbers based on local connectivity
    # This is a rough approximation, not rigorous persistent homology
    avg_degree = np.mean(np.sum(adjacency, axis=1))
    
    # Heuristic estimates
    betti_0 = n_components
    betti_1 = max(0, int(len(points) - n_components - avg_degree/2))  # Rough estimate
    betti_2 = max(0, int(avg_degree/6))  # Very rough estimate
    
    return {
        'betti_0': betti_0,
        'betti_1': betti_1,
        'betti_2': betti_2,
        'threshold_distance': max_distance,
        'mean_degree': avg_degree
    }

def connected_components(adjacency_matrix, directed=False):
    """Find connected components in adjacency matrix"""
    from scipy.sparse.csgraph import connected_components as cc
    n_components, labels = cc(adjacency_matrix, directed=directed)
    return n_components, labels

def compute_fractal_dimension(points):
    """Estimate fractal dimension using box-counting method"""
    if len(points) < 10:
        return 1.0
    
    # Normalize points to unit cube
    points = np.array(points)
    points_min = np.min(points, axis=0)
    points_max = np.max(points, axis=0)
    
    # Avoid division by zero
    ranges = points_max - points_min
    ranges[ranges == 0] = 1
    
    normalized_points = (points - points_min) / ranges
    
    # Box sizes (powers of 2 for efficiency)
    box_sizes = [1/2**i for i in range(2, 8)]
    box_counts = []
    
    for box_size in box_sizes:
        # Count number of boxes containing points
        n_boxes_per_dim = int(1 / box_size)
        
        # Discretize points into boxes
        box_indices = (normalized_points * n_boxes_per_dim).astype(int)
        box_indices = np.clip(box_indices, 0, n_boxes_per_dim - 1)
        
        # Count unique boxes
        unique_boxes = set()
        for point_box in box_indices:
            unique_boxes.add(tuple(point_box))
        
        box_counts.append(len(unique_boxes))
    
    # Fit line to log-log plot to estimate fractal dimension
    if len(box_counts) > 2 and all(count > 0 for count in box_counts):
        log_sizes = np.log(box_sizes)
        log_counts = np.log(box_counts)
        
        # Linear regression
        coeffs = np.polyfit(log_sizes, log_counts, 1)
        fractal_dim = -coeffs[0]  # Negative slope gives fractal dimension
        
        return max(1.0, min(3.0, fractal_dim))  # Clamp to reasonable range
    
    return 2.0  # Default fallback

# Generate interpretation for each embedding
print("\nComputing topological interpretations...")
interpretation = {}

for name, embed in embeddings.items():
    if name == 'isomap_reduction':
        continue
        
    print(f"Analyzing {name} embedding...")
    
    try:
        x, y, z = np.array(embed['x']), np.array(embed['y']), np.array(embed['z'])
        gaps = np.array(embed['gaps'])
        
        # Ensure we have valid data
        if len(x) == 0 or not np.all(np.isfinite(x)):
            print(f"  Warning: Invalid data in {name}")
            continue
        
        # Compute geometric properties
        curvature = compute_curvature(x, y, z)
        torsion = compute_torsion(x, y, z)
        
        # Combine coordinates for topological analysis
        points = np.column_stack([x, y, z])
        
        # Compute topological invariants (approximations)
        homology = compute_persistent_homology_approximation(points)
        
        # Compute fractal dimension
        fractal_dim = compute_fractal_dimension(points)
        
        # Gap correlation analysis
        gap_position_correlation = np.corrcoef(gaps, np.arange(len(gaps)))[0, 1]
        
        # Curvature-gap correlation
        if len(curvature) == len(gaps):
            curvature_gap_correlation = np.corrcoef(curvature, gaps)[0, 1]
        else:
            curvature_gap_correlation = 0.0
        
        interpretation[name] = {
            'curvature_stats': {
                'mean': float(np.mean(curvature)),
                'std': float(np.std(curvature)),
                'max': float(np.max(curvature)),
                'min': float(np.min(curvature))
            },
            'torsion_stats': {
                'mean': float(np.mean(torsion)),
                'std': float(np.std(torsion)),
                'max': float(np.max(torsion)),
                'min': float(np.min(torsion))
            },
            'topological_invariants': homology,
            'fractal_dimension': float(fractal_dim),
            'gap_correlations': {
                'position_correlation': float(gap_position_correlation),
                'curvature_correlation': float(curvature_gap_correlation)
            },
            'embedding_quality': {
                'point_density': len(points) / (np.max(points) - np.min(points)).prod(),
                'coordinate_range': {
                    'x': [float(np.min(x)), float(np.max(x))],
                    'y': [float(np.min(y)), float(np.max(y))],
                    'z': [float(np.min(z)), float(np.max(z))]
                }
            }
        }
        
        print(f"  Curvature: mean={np.mean(curvature):.4f}, max={np.max(curvature):.4f}")
        print(f"  Betti numbers: β₀={homology['betti_0']}, β₁={homology['betti_1']}")
        print(f"  Fractal dimension: {fractal_dim:.3f}")
        
    except Exception as e:
        print(f"  Error analyzing {name}: {e}")
        continue

# Save interpretation results
print("\nSaving interpretation results...")
with open('/home/sandbox/topological_interpretation.json', 'w') as f:
    json.dump(interpretation, f, indent=2)

# Generate comparative analysis
print("\n=== COMPARATIVE TOPOLOGICAL ANALYSIS ===")

if len(interpretation) > 0:
    # Compare curvature across embeddings
    print("\nCURVATURE COMPARISON:")
    curvatures = {}
    for name, data in interpretation.items():
        curvatures[name] = data['curvature_stats']['mean']
    
    sorted_curvatures = sorted(curvatures.items(), key=lambda x: x[1], reverse=True)
    for name, curv in sorted_curvatures:
        print(f"  {name}: {curv:.6f}")
    
    # Compare fractal dimensions
    print("\nFRACTAL DIMENSION COMPARISON:")
    fractal_dims = {}
    for name, data in interpretation.items():
        fractal_dims[name] = data['fractal_dimension']
    
    sorted_fractals = sorted(fractal_dims.items(), key=lambda x: x[1], reverse=True)
    for name, dim in sorted_fractals:
        print(f"  {name}: {dim:.3f}")
    
    # Compare topological complexity
    print("\nTOPOLOGICAL COMPLEXITY (Betti numbers):")
    for name, data in interpretation.items():
        betti = data['topological_invariants']
        complexity = betti['betti_0'] + betti['betti_1'] + betti['betti_2']
        print(f"  {name}: β₀={betti['betti_0']}, β₁={betti['betti_1']}, β₂={betti['betti_2']} (total: {complexity})")

print(f"\nInterpretation complete! Results saved to topological_interpretation.json")