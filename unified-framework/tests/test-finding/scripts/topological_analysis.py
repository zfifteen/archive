import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import Isomap
import json
from topological_prime_gaps import PrimeGapTopology

# Initialize analysis with larger prime range for better statistics
print("Initializing topological analysis...")
topology = PrimeGapTopology(max_prime=10000)

print(f"Generated {len(topology.primes)} primes up to {topology.max_prime}")
print(f"Computing {len(topology.gaps)} prime gaps")

# 3D transform implementations
transform_methods = {
    'helical': topology.helical_embedding,
    'mobius': topology.mobius_embedding,
    'knot': topology.knot_embedding,
    'hyperbolic': topology.hyperbolic_embedding,
    'spherical': topology.spherical_embedding,
    'klein': topology.klein_bottle_embedding
}

# Save topological structure data
structured_embeddings = {}
print("\nComputing embeddings...")

for name, method in transform_methods.items():
    try:
        print(f"Processing {name} embedding...")
        x, y, z = method()
        
        # Ensure arrays are finite and not too large
        if np.any(~np.isfinite(x)) or np.any(~np.isfinite(y)) or np.any(~np.isfinite(z)):
            print(f"Warning: Non-finite values in {name} embedding")
            # Replace non-finite values with zeros
            x = np.nan_to_num(x, nan=0.0, posinf=1e6, neginf=-1e6)
            y = np.nan_to_num(y, nan=0.0, posinf=1e6, neginf=-1e6)
            z = np.nan_to_num(z, nan=0.0, posinf=1e6, neginf=-1e6)
        
        structured_embeddings[name] = {
            'x': x.tolist(),
            'y': y.tolist(),
            'z': z.tolist(),
            'gaps': topology.gaps.tolist(),
            'primes': topology.primes[:-1].tolist()  # Exclude last prime since gaps is one shorter
        }
        print(f"  {name}: {len(x)} points embedded")
        
    except Exception as e:
        print(f"Error in {name}: {e}")
        continue

# Compute additional topological features
print("\nComputing topological features...")

# Manifold learning - dimension reduction to find intrinsic dimensionality
try:
    # Create feature matrix combining gap values and positions
    feature_matrix = np.column_stack([
        topology.gaps, 
        np.arange(len(topology.gaps)),
        np.log(topology.primes[:-1])  # Log of prime values
    ])
    
    # Apply Isomap for nonlinear dimensionality reduction
    isomap = Isomap(n_components=3, n_neighbors=min(10, len(topology.gaps)//2))
    reduced_coords = isomap.fit_transform(feature_matrix)
    
    structured_embeddings['isomap_reduction'] = {
        'x': reduced_coords[:, 0].tolist(),
        'y': reduced_coords[:, 1].tolist(),
        'z': reduced_coords[:, 2].tolist(),
        'gaps': topology.gaps.tolist(),
        'reconstruction_error': float(isomap.reconstruction_error())
    }
    print(f"Isomap reconstruction error: {isomap.reconstruction_error():.6f}")
    
except Exception as e:
    print(f"Error in manifold learning: {e}")

# Compute geometric properties for each embedding
geometric_properties = {}

for name, embed in structured_embeddings.items():
    if name == 'isomap_reduction':
        continue
        
    try:
        x, y, z = np.array(embed['x']), np.array(embed['y']), np.array(embed['z'])
        
        # Compute distances between consecutive points
        distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2 + np.diff(z)**2)
        
        # Compute angles between consecutive segments
        def compute_angles(x, y, z):
            if len(x) < 3:
                return np.array([])
            
            # Vectors between consecutive points
            v1 = np.column_stack([np.diff(x)[:-1], np.diff(y)[:-1], np.diff(z)[:-1]])
            v2 = np.column_stack([np.diff(x)[1:], np.diff(y)[1:], np.diff(z)[1:]])
            
            # Compute angles using dot product
            dot_products = np.sum(v1 * v2, axis=1)
            norms1 = np.linalg.norm(v1, axis=1)
            norms2 = np.linalg.norm(v2, axis=1)
            
            # Avoid division by zero
            valid_mask = (norms1 > 1e-10) & (norms2 > 1e-10)
            angles = np.zeros(len(dot_products))
            
            if np.any(valid_mask):
                cos_angles = dot_products[valid_mask] / (norms1[valid_mask] * norms2[valid_mask])
                cos_angles = np.clip(cos_angles, -1, 1)  # Ensure valid range for arccos
                angles[valid_mask] = np.arccos(cos_angles)
            
            return angles
        
        angles = compute_angles(x, y, z)
        
        geometric_properties[name] = {
            'mean_distance': float(np.mean(distances)),
            'std_distance': float(np.std(distances)),
            'total_length': float(np.sum(distances)),
            'mean_angle': float(np.mean(angles)) if len(angles) > 0 else 0.0,
            'std_angle': float(np.std(angles)) if len(angles) > 0 else 0.0,
            'bounding_box_volume': float(
                (np.max(x) - np.min(x)) * 
                (np.max(y) - np.min(y)) * 
                (np.max(z) - np.min(z))
            )
        }
        
    except Exception as e:
        print(f"Error computing geometric properties for {name}: {e}")

# Save all data to JSON files
print("\nSaving results...")

with open('/home/sandbox/topological_embeddings.json', 'w') as f:
    json.dump(structured_embeddings, f, indent=2)

with open('/home/sandbox/geometric_properties.json', 'w') as f:
    json.dump(geometric_properties, f, indent=2)

print("Analysis complete! Files saved:")
print("- topological_embeddings.json: 3D coordinate data for all embeddings")
print("- geometric_properties.json: Computed geometric properties")

# Generate summary statistics
print("\n=== EMBEDDING SUMMARY ===")
print(f"Total primes analyzed: {len(topology.primes)}")
print(f"Total gaps computed: {len(topology.gaps)}")
print(f"Gap range: {np.min(topology.gaps)} to {np.max(topology.gaps)}")
print(f"Mean gap: {np.mean(topology.gaps):.2f}")
print(f"Successful embeddings: {len(structured_embeddings)}")

for name in structured_embeddings.keys():
    if name in geometric_properties:
        props = geometric_properties[name]
        print(f"\n{name.upper()} EMBEDDING:")
        print(f"  Mean distance: {props['mean_distance']:.4f}")
        print(f"  Total length: {props['total_length']:.4f}")
        print(f"  Bounding volume: {props['bounding_box_volume']:.4f}")