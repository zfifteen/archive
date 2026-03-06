"""
Quantum-Inspired Sequence Alignment and Bell-Type Metrics

This module implements quantum-inspired alignment algorithms using Bell-type
violation metrics and quantum correlation measures for biological sequences.

Key Functions:
- quantum_alignment: Quantum-inspired sequence alignment scoring
- compute_bell_violation: Calculate Bell-type violations between sequences
- quantum_distance: Distance metric based on quantum correlations

Mathematical Foundation:
- Bell-type correlations for non-local sequence relationships
- Z-transform normalization: Z = A(B/c)
- Quantum correlation metrics replacing traditional Hamming distance
"""

import numpy as np
from math import sqrt, log

# Import Bio.Seq with proper error handling to prevent confusion
try:
    from Bio.Seq import Seq
except ImportError:
    raise ImportError("Bio.Seq requires biopython package. Install with: pip install biopython") from None

from .helical import generate_helical_coordinates, compute_quantum_correlations, PHI, E_SQUARED


def quantum_alignment(seq1, seq2, k=0.3, method='bell_violation', hypothetical=True):
    """
    Compute quantum-inspired alignment score between two sequences.
    
    Uses quantum correlation metrics instead of traditional alignment methods
    to detect non-local relationships and quantum-like entanglement patterns.
    
    Args:
        seq1: First Bio.Seq object
        seq2: Second Bio.Seq object  
        k: Curvature parameter for geodesic transformation
        method: Alignment method ('bell_violation', 'correlation', 'hybrid')
        hypothetical: Mark as experimental analysis
        
    Returns:
        Dictionary containing alignment analysis results
    """
    if hypothetical:
        print("Warning: Quantum alignment is experimental/hypothetical.")
    
    # Ensure sequences are same length for comparison
    min_len = min(len(seq1), len(seq2))
    seq1_trimmed = seq1[:min_len]
    seq2_trimmed = seq2[:min_len]
    
    if method == 'bell_violation':
        return _bell_violation_alignment(seq1_trimmed, seq2_trimmed, k, hypothetical)
    elif method == 'correlation':
        return _correlation_alignment(seq1_trimmed, seq2_trimmed, k, hypothetical)
    elif method == 'hybrid':
        return _hybrid_alignment(seq1_trimmed, seq2_trimmed, k, hypothetical)
    else:
        raise ValueError(f"Unknown alignment method: {method}")


def _bell_violation_alignment(seq1, seq2, k, hypothetical):
    """
    Compute alignment using Bell-type violation metric.
    
    Measures quantum-like correlations that violate classical bounds,
    indicating potential non-local relationships between sequences.
    """
    # Generate helical coordinates for both sequences
    coords1 = generate_helical_coordinates(seq1, k=k, hypothetical=False)
    coords2 = generate_helical_coordinates(seq2, k=k, hypothetical=False)
    
    # Extract coordinate components
    x1, y1 = coords1['x'], coords1['y']
    x2, y2 = coords2['x'], coords2['y']
    
    # Compute Bell-type correlations
    bell_violation, p_value = compute_bell_violation(coords1, coords2)
    
    # Calculate alignment score based on violation strength
    alignment_score = abs(bell_violation)  # Stronger violation = better alignment
    
    return {
        'alignment_score': alignment_score,
        'bell_violation': bell_violation,
        'p_value': p_value,
        'method': 'bell_violation',
        'sequence_length': len(seq1),
        'curvature_k': k,
        'hypothetical': hypothetical,
        'interpretation': 'Higher scores indicate stronger quantum-like correlations'
    }


def _correlation_alignment(seq1, seq2, k, hypothetical):
    """
    Compute alignment using direct quantum correlation comparison.
    """
    # Compute quantum correlations for both sequences
    corr1 = compute_quantum_correlations(seq1, k=k, hypothetical=False)
    corr2 = compute_quantum_correlations(seq2, k=k, hypothetical=False)
    
    # Compare correlation patterns
    correlations1 = corr1['correlations']
    correlations2 = corr2['correlations']
    
    # Ensure same length for comparison
    min_len = min(len(correlations1), len(correlations2))
    correlations1 = correlations1[:min_len]
    correlations2 = correlations2[:min_len]
    
    # Compute similarity of correlation patterns
    if len(correlations1) > 1:
        correlation_similarity = np.corrcoef(correlations1, correlations2)[0, 1]
        if np.isnan(correlation_similarity):
            correlation_similarity = 0.0
    else:
        correlation_similarity = 0.0
    
    alignment_score = abs(correlation_similarity)
    
    return {
        'alignment_score': alignment_score,
        'correlation_similarity': correlation_similarity,
        'method': 'correlation',
        'sequence_length': len(seq1),
        'curvature_k': k,
        'hypothetical': hypothetical,
        'interpretation': 'Higher scores indicate similar quantum correlation patterns'
    }


def _hybrid_alignment(seq1, seq2, k, hypothetical):
    """
    Compute alignment using hybrid Bell-violation and correlation methods.
    """
    bell_result = _bell_violation_alignment(seq1, seq2, k, hypothetical)
    corr_result = _correlation_alignment(seq1, seq2, k, hypothetical)
    
    # Weighted combination of both methods
    bell_weight = 0.6
    corr_weight = 0.4
    
    hybrid_score = (bell_weight * bell_result['alignment_score'] + 
                   corr_weight * corr_result['alignment_score'])
    
    return {
        'alignment_score': hybrid_score,
        'bell_component': bell_result,
        'correlation_component': corr_result,
        'method': 'hybrid',
        'weights': {'bell': bell_weight, 'correlation': corr_weight},
        'sequence_length': len(seq1),
        'curvature_k': k,
        'hypothetical': hypothetical,
        'interpretation': 'Hybrid score combining Bell violations and correlations'
    }


def compute_bell_violation(coords1, coords2, n_measurements=4):
    """
    Compute Bell-type violation between two coordinate sets.
    
    Calculates quantum-inspired correlation measure that can violate
    classical bounds, indicating non-local relationships.
    
    Args:
        coords1: Coordinate dictionary from first sequence
        coords2: Coordinate dictionary from second sequence
        n_measurements: Number of measurement orientations
        
    Returns:
        Tuple of (violation_strength, p_value)
    """
    x1, y1 = coords1['x'], coords1['y']
    x2, y2 = coords2['x'], coords2['y']
    
    # Ensure same length
    min_len = min(len(x1), len(x2))
    x1, y1 = x1[:min_len], y1[:min_len]
    x2, y2 = x2[:min_len], y2[:min_len]
    
    if min_len < 4:
        return 0.0, 1.0  # Insufficient data
    
    # Define measurement angles
    angles = np.linspace(0, np.pi/2, n_measurements)
    
    # Compute correlations at different measurement angles
    correlations = []
    
    for angle in angles:
        # Rotate measurement basis
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        
        # Project coordinates onto measurement basis
        proj1 = x1 * cos_a + y1 * sin_a
        proj2 = x2 * cos_a + y2 * sin_a
        
        # Compute correlation
        if np.std(proj1) > 0 and np.std(proj2) > 0:
            corr = np.corrcoef(proj1, proj2)[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)
    
    if len(correlations) < 2:
        return 0.0, 1.0
    
    correlations = np.array(correlations)
    
    # Compute Bell-type parameter (simplified CHSH-like)
    # Classical bound is 2, quantum can reach 2√2 ≈ 2.828
    S = abs(correlations[0] + correlations[1] + correlations[0] - correlations[-1])
    
    # Calculate violation strength (S > 2 indicates quantum-like behavior)
    violation = max(0, S - 2.0)  # Amount by which classical bound is violated
    
    # Estimate statistical significance (simplified)
    # In real quantum experiments, this would require proper statistical analysis
    z_score = violation / (np.std(correlations) / sqrt(len(correlations)) + 1e-10)
    p_value = 2 * (1 - _normal_cdf(abs(z_score)))  # Two-tailed test
    
    return violation, p_value


def _normal_cdf(x):
    """Approximate standard normal CDF using error function approximation."""
    return 0.5 * (1 + _erf(x / sqrt(2)))


def _erf(x):
    """Approximate error function using rational approximation."""
    # Abramowitz and Stegun approximation
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    
    sign = 1 if x >= 0 else -1
    x = abs(x)
    
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
    
    return sign * y


def quantum_distance(seq1, seq2, k=0.3, metric='bell_violation'):
    """
    Compute quantum-inspired distance between sequences.
    
    Args:
        seq1: First Bio.Seq object
        seq2: Second Bio.Seq object
        k: Curvature parameter
        metric: Distance metric ('bell_violation', 'correlation')
        
    Returns:
        Distance value (lower = more similar)
    """
    alignment_result = quantum_alignment(seq1, seq2, k=k, method=metric, hypothetical=True)
    
    # Convert alignment score to distance (invert and normalize)
    max_possible_score = 1.0  # Theoretical maximum
    distance = max_possible_score - alignment_result['alignment_score']
    
    return {
        'distance': distance,
        'alignment_score': alignment_result['alignment_score'],
        'metric': metric,
        'curvature_k': k,
        'interpretation': 'Lower distance indicates higher quantum similarity'
    }


def detect_quantum_motifs(seq, motif_length=6, k=0.3, threshold=0.5):
    """
    Detect potential quantum motifs in a sequence using Bell violations.
    
    Args:
        seq: Bio.Seq object
        motif_length: Length of motifs to search for
        k: Curvature parameter
        threshold: Threshold for significant quantum correlation
        
    Returns:
        List of potential quantum motifs with their positions and scores
    """
    motifs = []
    
    for i in range(len(seq) - motif_length + 1):
        motif = seq[i:i+motif_length]
        
        # Compute self-correlation as quantum coherence measure
        coords = generate_helical_coordinates(motif, k=k, hypothetical=False)
        
        # Calculate internal quantum correlations
        x, y = coords['x'], coords['y']
        if len(x) > 1 and np.std(x) > 0 and np.std(y) > 0:
            coherence = abs(np.corrcoef(x, y)[0, 1])
            if not np.isnan(coherence) and coherence > threshold:
                motifs.append({
                    'position': i,
                    'motif': str(motif),
                    'coherence': coherence,
                    'length': motif_length
                })
    
    # Sort by coherence strength
    motifs.sort(key=lambda x: x['coherence'], reverse=True)
    
    return {
        'motifs': motifs,
        'threshold': threshold,
        'motif_length': motif_length,
        'curvature_k': k,
        'hypothetical': True,
        'interpretation': 'Higher coherence indicates stronger quantum-like patterns'
    }