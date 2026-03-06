"""
Helical Coordinate Generation and Quantum Correlations

This module implements φ-geodesic helical coordinate generation for biological
sequences using the Z Framework's mathematical foundation.

Key Functions:
- generate_helical_coordinates: Transform sequences to helical coordinates
- compute_quantum_correlations: Calculate quantum-inspired correlations
- complexity_metric: Compute κ(n) complexity measure

Mathematical Foundation:
- Geodesic mapping: θ'(n, k) = φ·{n/φ}^k  
- Complexity: κ(n) = d(n) * ln(n+1) / e²
- Z-transform: Z = n(Δₙ / Δₘₐₓ) for discrete sequences
"""

import numpy as np
from math import log, sqrt, exp, sin, cos

# Import Bio.Seq with proper error handling to prevent confusion
try:
    from Bio.Seq import Seq
except ImportError:
    raise ImportError("Bio.Seq requires biopython package. Install with: pip install biopython") from None

# Constants from Z Framework
PHI = (1 + sqrt(5)) / 2  # Golden ratio
E_SQUARED = exp(2)  # e² for discrete normalization
OPTIMAL_K = 0.3  # Optimal curvature parameter


def divisor_count(n):
    """
    Compute the number of divisors of n using trial division.
    
    Args:
        n: Integer to find divisors for
        
    Returns:
        Number of divisors of n
    """
    if n <= 0:
        return 0
    count = 0
    for i in range(1, int(sqrt(n)) + 1):
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
    return count


def complexity_metric(n):
    """
    Compute κ(n) = d(n) * ln(n+1) / e² complexity measure.
    
    Low κ values indicate structural simplicity (e.g., primes have d(n)=2).
    Used to identify regions of low complexity for pattern detection.
    
    Args:
        n: Integer position
        
    Returns:
        Complexity metric κ(n)
    """
    if n <= 0:
        return 0
    return divisor_count(n) * log(n + 1) / E_SQUARED


def geodesic_transform(n, k=OPTIMAL_K):
    """
    Apply φ-geodesic transformation: θ'(n, k) = φ·{n/φ}^k
    
    Maps integers to curved space [0, φ) for topological clustering analysis.
    Optimal k ≈ 0.3 provides conditional prime density improvement under canonical benchmark methodology for pattern detection.
    
    Args:
        n: Input integer or array of integers
        k: Curvature parameter (default: 0.3)
        
    Returns:
        Transformed geodesic coordinates
    """
    if isinstance(n, (list, np.ndarray)):
        return np.array([PHI * ((x % PHI) / PHI) ** k for x in n])
    else:
        return PHI * ((n % PHI) / PHI) ** k


def generate_helical_coordinates(seq, k=OPTIMAL_K, attach_to_seq=False, hypothetical=False):
    """
    Generate φ-geodesic helical coordinates for a biological sequence.
    
    Applies Z-normalized geodesic transformation to sequence positions,
    mapping to helical coordinates using golden ratio curvature.
    
    Args:
        seq: Bio.Seq object containing biological sequence
        k: Curvature parameter (default: 0.3 for optimal density)
        attach_to_seq: If True, attach coordinates as sequence attribute
        hypothetical: If True, mark as experimental/hypothetical
        
    Returns:
        Dictionary containing:
        - 'x': X coordinates (cosine component)
        - 'y': Y coordinates (sine component)  
        - 'z': Z coordinates (helical progression)
        - 'theta': Geodesic angles
        - 'metadata': Analysis metadata
    """
    if hypothetical:
        print("Warning: Hypothetical quantum-geodesic transform; validate empirically.")
    
    # Convert sequence to numerical representation
    base_map = {'A': 1.618, 'T': 0.618, 'C': 2.618, 'G': 4.236}  # φ-based mapping
    numerical = np.array([base_map.get(str(base).upper(), 1.0) for base in seq])
    
    # Normalize using Z-transform: Z = n(Δₙ / Δₘₐₓ)
    normalized = numerical / E_SQUARED
    
    # Generate position array
    positions = np.arange(1, len(seq) + 1)
    
    # Apply geodesic transformation
    theta_geodesic = geodesic_transform(positions, k)
    
    # Generate helical coordinates
    # X, Y: circular cross-section, Z: helical progression
    x_coords = normalized * np.cos(theta_geodesic)
    y_coords = normalized * np.sin(theta_geodesic)
    
    # Handle empty sequence case
    if len(seq) == 0:
        z_coords = np.array([])
    else:
        z_coords = positions * (k / len(seq))  # Normalized helical progression
    
    coordinates = {
        'x': x_coords,
        'y': y_coords,
        'z': z_coords,
        'theta': theta_geodesic,
        'metadata': {
            'sequence_length': len(seq),
            'curvature_k': k,
            'phi_constant': PHI,
            'normalization': 'Z-transform with e² scaling',
            'hypothetical': hypothetical,
            'base_mapping': base_map
        }
    }
    
    # Optionally attach to sequence object
    if attach_to_seq and hasattr(seq, '__dict__'):
        seq.quantum_coords = coordinates
    
    return coordinates


def compute_quantum_correlations(seq, window_size=10, k=OPTIMAL_K, hypothetical=True):
    """
    Compute quantum-inspired correlations within sequence windows.
    
    Analyzes local correlations using geodesic coordinates to identify
    quantum-like entanglement patterns in biological sequences.
    
    Args:
        seq: Bio.Seq object
        window_size: Size of correlation window
        k: Curvature parameter
        hypothetical: Mark as experimental analysis
        
    Returns:
        Dictionary containing correlation analysis results
    """
    if hypothetical:
        print("Warning: Quantum correlation analysis is experimental/hypothetical.")
    
    # Generate helical coordinates
    coords = generate_helical_coordinates(seq, k=k, hypothetical=False)
    
    # Extract coordinate arrays
    x, y, z = coords['x'], coords['y'], coords['z']
    
    # Compute correlations within sliding windows
    correlations = []
    n_windows = len(seq) - window_size + 1
    
    for i in range(n_windows):
        window_x = x[i:i+window_size]
        window_y = y[i:i+window_size]
        
        # Compute correlation coefficient between x and y components
        correlation = np.corrcoef(window_x, window_y)[0, 1]
        if np.isnan(correlation):
            correlation = 0.0
        correlations.append(correlation)
    
    correlations = np.array(correlations)
    
    # Identify high-correlation regions (potential "entanglement")
    correlation_threshold = np.mean(correlations) + np.std(correlations)
    entangled_regions = correlations > correlation_threshold
    
    return {
        'correlations': correlations,
        'entangled_regions': entangled_regions,
        'correlation_threshold': correlation_threshold,
        'mean_correlation': np.mean(correlations),
        'std_correlation': np.std(correlations),
        'window_size': window_size,
        'hypothetical': hypothetical,
        'metadata': coords['metadata']
    }


def filter_low_complexity_positions(seq, percentile=20):
    """
    Identify low-complexity positions using κ(n) metric.
    
    Args:
        seq: Bio.Seq object
        percentile: Percentile threshold for low complexity
        
    Returns:
        Array of position indices with low complexity
    """
    positions = np.arange(1, len(seq) + 1)
    kappa_values = np.array([complexity_metric(n) for n in positions])
    
    threshold = np.percentile(kappa_values, percentile)
    low_complexity_positions = np.where(kappa_values <= threshold)[0] + 1  # 1-indexed
    
    return {
        'positions': low_complexity_positions,
        'kappa_values': kappa_values,
        'threshold': threshold,
        'percentile': percentile
    }