"""
Z-Curvature Features for Genomic Tasks - Smoke Test Implementation

This module implements a lightweight smoke test to evaluate whether Z-curvature 
features derived from θ'(i,k) = φ·{i/φ}^k can capture "prime-like" sparsity/structure 
that adds predictive signal for genomic tasks such as mutation hotspots and CRISPR off-targets.

The approach converts DNA sequences to position-indexed features using the Z-framework
transformation and compares against naive baseline features.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
import sys
import os

# Add the core modules to path for Z framework integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.axioms import theta_prime
import mpmath as mp

# Set precision for reproducible results
mp.dps = 15

class ZCurvatureGenomicFeatures:
    """
    Extract Z-curvature features from genomic sequences using θ'(i,k) transformation.
    
    This class applies the Z-framework geodesic transformation to DNA sequence positions
    to capture "prime-like" sparsity patterns that may correlate with genomic hotspots.
    """
    
    def __init__(self, k_values: List[float] = None, window_sizes: List[int] = None):
        """
        Initialize Z-curvature feature extractor.
        
        Args:
            k_values: List of curvature exponents to test (default: [0.2, 0.3, 0.4])
            window_sizes: List of window sizes for local analysis (default: [10, 20, 50])
        """
        self.k_values = k_values or [0.2, 0.3, 0.4]
        self.window_sizes = window_sizes or [10, 20, 50]
        self.phi = float((1 + mp.sqrt(5)) / 2)  # Golden ratio
        
    def sequence_to_numeric(self, sequence: str) -> np.ndarray:
        """
        Convert DNA sequence to numeric representation.
        
        Args:
            sequence: DNA sequence string (A, T, C, G)
            
        Returns:
            Numeric array where A=1, T=2, C=3, G=4, others=0
        """
        mapping = {'A': 1, 'T': 2, 'C': 3, 'G': 4}
        return np.array([mapping.get(base.upper(), 0) for base in sequence])
    
    def extract_z_features(self, sequence: str, k: float, window_size: int) -> Dict[str, float]:
        """
        Extract Z-curvature features from a sequence using θ'(i,k) transformation.
        
        Args:
            sequence: DNA sequence string
            k: Curvature exponent
            window_size: Window size for local analysis
            
        Returns:
            Dictionary of Z-curvature features
        """
        numeric_seq = self.sequence_to_numeric(sequence)
        seq_len = len(sequence)
        
        if seq_len < window_size:
            window_size = seq_len
            
        features = {}
        
        # Apply θ'(i,k) transformation to sequence positions (optimized)
        theta_values = np.zeros(seq_len)
        
        # Batch compute theta values for efficiency
        positions = np.arange(1, seq_len + 1)  # 1-indexed positions
        
        # Use simplified computation for speed in smoke test
        phi = self.phi
        epsilon = 1e-10
        for i in range(seq_len):
            pos = positions[i]
            # Simplified θ'(i,k) = φ · {i/φ}^k
            residue = (pos % phi) / phi
            if residue < epsilon:
                power_term = 0
            else:
                power_term = residue ** k
            theta_values[i] = phi * power_term
        
        # Extract statistical features from θ' values
        features[f'theta_mean_k{k}_w{window_size}'] = np.mean(theta_values)
        features[f'theta_std_k{k}_w{window_size}'] = np.std(theta_values)
        features[f'theta_skew_k{k}_w{window_size}'] = self._skewness(theta_values)
        
        # Position-weighted features using nucleotide values
        weighted_theta = theta_values * numeric_seq
        features[f'weighted_theta_mean_k{k}_w{window_size}'] = np.mean(weighted_theta)
        features[f'weighted_theta_std_k{k}_w{window_size}'] = np.std(weighted_theta)
        
        # Prime-like sparsity measures (simplified)
        # Look for patterns that align with golden ratio scaling
        golden_positions = theta_values / phi
        prime_like_count = np.sum(np.abs(golden_positions - np.round(golden_positions)) < 0.1)
        features[f'prime_like_density_k{k}_w{window_size}'] = prime_like_count / len(theta_values)
        
        return features
    
    def extract_all_features(self, sequence: str) -> Dict[str, float]:
        """
        Extract Z-curvature features for all k values and window sizes.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Dictionary of all Z-curvature features
        """
        all_features = {}
        
        for k in self.k_values:
            for window_size in self.window_sizes:
                features = self.extract_z_features(sequence, k, window_size)
                all_features.update(features)
        
        return all_features
    
    def _skewness(self, arr: np.ndarray) -> float:
        """Calculate skewness of array."""
        if len(arr) < 3:
            return 0.0
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return 0.0
        return np.mean(((arr - mean) / std) ** 3)
    
    def _kurtosis(self, arr: np.ndarray) -> float:
        """Calculate kurtosis of array."""
        if len(arr) < 4:
            return 0.0
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return 0.0
        return np.mean(((arr - mean) / std) ** 4) - 3.0


class BaselineGenomicFeatures:
    """
    Extract baseline (naive) features from genomic sequences for comparison.
    
    This provides simple sequence-based features that don't use the Z-framework
    to establish a baseline for comparison with Z-curvature features.
    """
    
    def __init__(self, window_sizes: List[int] = None):
        """
        Initialize baseline feature extractor.
        
        Args:
            window_sizes: List of window sizes for local analysis (default: [10, 20, 50])
        """
        self.window_sizes = window_sizes or [10, 20, 50]
    
    def extract_baseline_features(self, sequence: str, window_size: int) -> Dict[str, float]:
        """
        Extract baseline features from a sequence.
        
        Args:
            sequence: DNA sequence string
            window_size: Window size for local analysis
            
        Returns:
            Dictionary of baseline features
        """
        sequence = sequence.upper()
        seq_len = len(sequence)
        features = {}
        
        # Basic nucleotide composition
        for base in ['A', 'T', 'C', 'G']:
            count = sequence.count(base)
            features[f'{base}_freq_w{window_size}'] = count / seq_len if seq_len > 0 else 0
        
        # GC content
        gc_count = sequence.count('G') + sequence.count('C')
        features[f'gc_content_w{window_size}'] = gc_count / seq_len if seq_len > 0 else 0
        
        # Simple position-based features
        numeric_seq = np.array([ord(base) for base in sequence])
        features[f'position_mean_w{window_size}'] = np.mean(range(seq_len)) if seq_len > 0 else 0
        features[f'numeric_mean_w{window_size}'] = np.mean(numeric_seq) if seq_len > 0 else 0
        features[f'numeric_std_w{window_size}'] = np.std(numeric_seq) if seq_len > 0 else 0
        
        # Local variability
        if seq_len >= window_size:
            window_gc_contents = []
            for start in range(0, seq_len - window_size + 1, window_size // 2):
                end = start + window_size
                window_seq = sequence[start:end]
                window_gc = (window_seq.count('G') + window_seq.count('C')) / len(window_seq)
                window_gc_contents.append(window_gc)
            
            features[f'local_gc_var_w{window_size}'] = np.var(window_gc_contents) if window_gc_contents else 0
        
        return features
    
    def extract_all_features(self, sequence: str) -> Dict[str, float]:
        """
        Extract baseline features for all window sizes.
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Dictionary of all baseline features
        """
        all_features = {}
        
        for window_size in self.window_sizes:
            features = self.extract_baseline_features(sequence, window_size)
            all_features.update(features)
        
        return all_features


def create_synthetic_dataset(n_samples: int = 100, seq_length: int = 200) -> Tuple[List[str], List[int]]:
    """
    Create a synthetic dataset with controlled patterns for testing.
    This is the original simple version for backwards compatibility.
    """
    return create_challenging_dataset(n_samples, seq_length)


def create_challenging_dataset(n_samples: int = 100, seq_length: int = 200) -> Tuple[List[str], List[int]]:
    """
    Create a more challenging synthetic dataset where baseline and Z-curvature 
    features have different strengths.
    
    Args:
        n_samples: Number of sequences to generate
        seq_length: Length of each sequence
        
    Returns:
        Tuple of (sequences, labels) where labels indicate subtle pattern presence
    """
    np.random.seed(42)  # For reproducibility
    
    sequences = []
    labels = []
    
    bases = ['A', 'T', 'C', 'G']
    phi = 1.618033988749  # Golden ratio
    
    for i in range(n_samples):
        # Start with base sequence that has some natural bias (to make baseline competitive)
        if i % 2 == 0:
            # GC-rich background
            base_probs = [0.2, 0.2, 0.3, 0.3]  # A, T, C, G
        else:
            # AT-rich background  
            base_probs = [0.3, 0.3, 0.2, 0.2]
        
        sequence = list(np.random.choice(bases, seq_length, p=base_probs))
        
        # For half the sequences, add subtle Z-curvature patterns
        # These patterns are designed to be detectable by θ'(i,k) but subtle to baseline
        if i < n_samples // 2:
            label = 1  # Has subtle Z-pattern
            
            k_test = 0.3
            pattern_strength = 0.3  # Only modify 30% of eligible positions
            
            for pos in range(1, seq_length + 1):
                # Calculate θ'(pos, k) characteristics with noise tolerance
                residue = (pos % phi) / phi
                if residue > 0:
                    theta_val = phi * (residue ** k_test)
                    
                    # Only apply pattern probabilistically
                    if np.random.random() < pattern_strength:
                        # Subtle pattern based on θ' value ranges
                        if 0.8 < theta_val < 1.2 and pos-1 < len(sequence):
                            # High θ' region: slight bias toward purines (A, G)
                            if np.random.random() < 0.6:  # 60% chance
                                sequence[pos-1] = np.random.choice(['A', 'G'])
                        
                        elif 0.3 < theta_val < 0.7 and pos-1 < len(sequence):
                            # Medium θ' region: slight bias toward pyrimidines (C, T)
                            if np.random.random() < 0.6:  # 60% chance
                                sequence[pos-1] = np.random.choice(['C', 'T'])
                                
        else:
            label = 0  # No Z-pattern, just background bias
        
        sequences.append(''.join(sequence))
        labels.append(label)
    
    return sequences, labels


def test_with_real_sequences() -> Tuple[List[str], List[int]]:
    """
    Test with real genomic sequences from the sample_sequences.fasta file.
    Create labels based on known biological properties.
    
    Returns:
        Tuple of (sequences, labels) from real data
    """
    import os
    
    sequences = []
    labels = []
    
    # Load real sequences
    fasta_path = "sample_sequences.fasta"
    if os.path.exists(fasta_path):
        current_seq = ""
        current_name = ""
        
        with open(fasta_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_seq:
                        # Process previous sequence
                        # Create labels based on gene function (simplified)
                        if "BRCA1" in current_name or "TP53" in current_name:
                            label = 1  # Tumor suppressor genes (high mutation sensitivity)
                        else:
                            label = 0  # Other genes
                        
                        # Split long sequences into smaller chunks for analysis
                        chunk_size = 200
                        for i in range(0, len(current_seq), chunk_size):
                            chunk = current_seq[i:i+chunk_size]
                            if len(chunk) >= 50:  # Minimum size
                                sequences.append(chunk)
                                labels.append(label)
                    
                    current_name = line
                    current_seq = ""
                else:
                    current_seq += line.upper()
            
            # Process last sequence
            if current_seq:
                if "BRCA1" in current_name or "TP53" in current_name:
                    label = 1
                else:
                    label = 0
                
                chunk_size = 200
                for i in range(0, len(current_seq), chunk_size):
                    chunk = current_seq[i:i+chunk_size]
                    if len(chunk) >= 50:
                        sequences.append(chunk)
                        labels.append(label)
    
    return sequences, labels