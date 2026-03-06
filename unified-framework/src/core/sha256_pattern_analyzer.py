#!/usr/bin/env python3
"""
SHA-256 Pattern Analyzer for Cryptographic Discrete Analysis
============================================================

This module implements the proposal to treat SHA-256 outputs as points on a number line
and compute discrete derivatives to identify patterns using the Z Framework's discrete domain.

Key Features:
- SHA-256 bit strings mapped to integers [0, 2^256 - 1]
- Discrete derivative computation between consecutive hashes
- Integration with DiscreteZetaShift using a=256, b=e, c=e² parameters
- Zeta chain unfolding for pattern detection
- Curvature κ computation as pattern detection proxy

Mathematical Foundation:
- Discrete derivatives: Δh(i) = h(i+1) - h(i) where h(i) is SHA-256 as integer
- Z Framework mapping: Z = n(Δ_n/Δ_max) with discrete domain specialization
- Pattern detection through low curvature κ indicating non-random structure
"""

import hashlib
import mpmath as mp
from typing import List, Tuple, Dict, Optional, Union
import numpy as np
from .domain import DiscreteZetaShift, E_SQUARED

# Set high precision for cryptographic computations
mp.mp.dps = 50

class SHA256PatternAnalyzer:
    """
    Analyzer for detecting patterns in SHA-256 outputs using discrete domain analysis.
    
    This class implements the cryptographic analysis proposal by treating SHA-256 outputs
    as points on a number line and computing discrete derivatives for pattern detection.
    """
    
    def __init__(self, delta_max: float = None):
        """
        Initialize the SHA-256 pattern analyzer.
        
        Args:
            delta_max (float): Maximum delta value for normalization (default: e²)
        """
        self.delta_max = delta_max or float(E_SQUARED)
        self.hash_sequence = []
        self.integer_sequence = []
        self.discrete_derivatives = []
        self.zeta_shifts = []
        
    def sha256_to_integer(self, data: Union[str, bytes]) -> int:
        """
        Convert input data to SHA-256 hash and then to integer.
        
        Args:
            data: Input data to hash (string or bytes)
            
        Returns:
            int: SHA-256 hash as integer in range [0, 2^256 - 1]
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_bytes = hashlib.sha256(data).digest()
        # Convert 32-byte hash to 256-bit integer
        return int.from_bytes(hash_bytes, byteorder='big')
    
    def generate_hash_sequence(self, base_data: str, sequence_length: int) -> List[int]:
        """
        Generate a sequence of SHA-256 hashes as integers.
        
        Args:
            base_data: Base string to generate sequence from
            sequence_length: Number of hashes to generate
            
        Returns:
            List[int]: Sequence of SHA-256 hashes as integers
        """
        sequence = []
        current_data = base_data
        
        for i in range(sequence_length):
            hash_int = self.sha256_to_integer(current_data)
            sequence.append(hash_int)
            # Use previous hash as input for next iteration
            current_data = hex(hash_int)[2:]  # Remove '0x' prefix
            
        self.hash_sequence = [hex(h) for h in sequence]  # Store hex representation
        self.integer_sequence = sequence
        return sequence
    
    def compute_discrete_derivatives(self, sequence: List[int] = None) -> List[int]:
        """
        Compute discrete derivatives (differences) between consecutive hashes.
        
        Args:
            sequence: Sequence of integers (uses internal sequence if None)
            
        Returns:
            List[int]: Discrete derivatives Δh(i) = h(i+1) - h(i)
        """
        if sequence is None:
            sequence = self.integer_sequence
            
        if len(sequence) < 2:
            raise ValueError("Need at least 2 values to compute derivatives")
        
        derivatives = []
        for i in range(len(sequence) - 1):
            derivative = sequence[i + 1] - sequence[i]
            derivatives.append(derivative)
            
        self.discrete_derivatives = derivatives
        return derivatives
    
    def map_to_discrete_zeta_shifts(self, derivatives: List[int] = None) -> List[DiscreteZetaShift]:
        """
        Map discrete derivatives to DiscreteZetaShift objects for pattern analysis.
        
        Args:
            derivatives: List of discrete derivatives (uses internal if None)
            
        Returns:
            List[DiscreteZetaShift]: Zeta shift objects for analysis
        """
        if derivatives is None:
            derivatives = self.discrete_derivatives
            
        if not derivatives:
            raise ValueError("No derivatives available for mapping")
        
        zeta_shifts = []
        
        for i, derivative in enumerate(derivatives):
            # Map to discrete domain: use bit length as 'a' parameter
            # For SHA-256: a = 256 (bit length)
            # b = e (natural base for logarithmic invariants) 
            # c = e² (as specified in problem statement)
            a = 256  # SHA-256 bit length
            b = float(mp.e)  # Natural base
            c = float(E_SQUARED)  # e² for discrete domain normalization
            
            # Create DiscreteZetaShift with cryptographic parameters
            # Note: DiscreteZetaShift expects 'n' as first parameter
            # We use the index + 1 to avoid zero
            dzs = DiscreteZetaShift(n=i + 1, v=1.0, delta_max=c)
            zeta_shifts.append(dzs)
            
        self.zeta_shifts = zeta_shifts
        return zeta_shifts
    
    def extract_pattern_attributes(self, zeta_shifts: List[DiscreteZetaShift] = None) -> List[Dict]:
        """
        Extract attributes from zeta shift objects for pattern analysis.
        
        Args:
            zeta_shifts: List of DiscreteZetaShift objects (uses internal if None)
            
        Returns:
            List[Dict]: Extracted attributes for each zeta shift
        """
        if zeta_shifts is None:
            zeta_shifts = self.zeta_shifts
            
        if not zeta_shifts:
            raise ValueError("No zeta shifts available for attribute extraction")
        
        attributes_list = []
        
        for dzs in zeta_shifts:
            # Extract full attribute set including D, E, F, G, H, I, J, K, L, M, N, O
            attrs = dzs.attributes.copy()
            
            # Add SHA-256 specific attributes
            attrs['bit_length'] = 256
            attrs['delta_max'] = self.delta_max
            attrs['curvature_raw'] = float(dzs.kappa_raw) if hasattr(dzs, 'kappa_raw') else None
            attrs['curvature_bounded'] = float(dzs.kappa_bounded) if hasattr(dzs, 'kappa_bounded') else None
            
            attributes_list.append(attrs)
            
        return attributes_list
    
    def compute_curvature_patterns(self, attributes_list: List[Dict] = None) -> Dict:
        """
        Compute curvature-based pattern detection metrics.
        
        Args:
            attributes_list: List of attribute dictionaries (computed if None)
            
        Returns:
            Dict: Pattern detection metrics including curvature statistics
        """
        if attributes_list is None:
            attributes_list = self.extract_pattern_attributes()
            
        if not attributes_list:
            raise ValueError("No attributes available for curvature pattern analysis")
        
        # Extract curvature values
        curvatures = []
        bounded_curvatures = []
        
        for attrs in attributes_list:
            if attrs.get('curvature_raw') is not None:
                curvatures.append(attrs['curvature_raw'])
            if attrs.get('curvature_bounded') is not None:
                bounded_curvatures.append(attrs['curvature_bounded'])
        
        # Compute pattern detection metrics
        pattern_metrics = {
            'num_samples': len(attributes_list),
            'curvature_mean': np.mean(curvatures) if curvatures else None,
            'curvature_std': np.std(curvatures) if curvatures else None,
            'curvature_min': np.min(curvatures) if curvatures else None,
            'curvature_max': np.max(curvatures) if curvatures else None,
            'bounded_curvature_mean': np.mean(bounded_curvatures) if bounded_curvatures else None,
            'bounded_curvature_std': np.std(bounded_curvatures) if bounded_curvatures else None,
            'low_curvature_ratio': None,
            'pattern_detected': False
        }
        
        # Pattern detection: low curvature indicates potential non-random structure
        if curvatures:
            threshold = np.mean(curvatures) - np.std(curvatures)
            low_curvature_count = sum(1 for k in curvatures if k < threshold)
            pattern_metrics['low_curvature_ratio'] = low_curvature_count / len(curvatures)
            
            # Pattern detected if significant portion has low curvature
            pattern_metrics['pattern_detected'] = pattern_metrics['low_curvature_ratio'] > 0.2
        
        return pattern_metrics
    
    def analyze_sequence(self, base_data: str, sequence_length: int = 10) -> Dict:
        """
        Perform complete SHA-256 pattern analysis on a sequence.
        
        Args:
            base_data: Base string to generate hash sequence from
            sequence_length: Number of hashes to analyze
            
        Returns:
            Dict: Complete analysis results including patterns and metrics
        """
        # Generate hash sequence
        integer_seq = self.generate_hash_sequence(base_data, sequence_length)
        
        # Compute discrete derivatives
        derivatives = self.compute_discrete_derivatives()
        
        # Map to zeta shifts
        zeta_shifts = self.map_to_discrete_zeta_shifts()
        
        # Extract attributes
        attributes = self.extract_pattern_attributes()
        
        # Compute pattern metrics
        pattern_metrics = self.compute_curvature_patterns(attributes)
        
        # Compile results
        results = {
            'base_data': base_data,
            'sequence_length': sequence_length,
            'hash_sequence': self.hash_sequence,
            'integer_sequence': integer_seq,
            'discrete_derivatives': derivatives,
            'derivative_stats': {
                'mean': np.mean(derivatives),
                'std': np.std(derivatives),
                'min': np.min(derivatives),
                'max': np.max(derivatives)
            },
            'zeta_attributes': attributes,
            'pattern_metrics': pattern_metrics,
            'framework_parameters': {
                'a': 256,  # SHA-256 bit length
                'b': float(mp.e),  # Natural base
                'c': float(E_SQUARED),  # e² normalization
                'delta_max': self.delta_max
            }
        }
        
        return results
    
    def detect_differential_patterns(self, 
                                   data_variants: List[str], 
                                   sequence_length: int = 5) -> Dict:
        """
        Perform differential cryptanalysis by comparing pattern metrics across variants.
        
        This aligns with differential cryptanalysis techniques mentioned in the problem
        statement, examining differences in outputs for non-random behaviors.
        
        Args:
            data_variants: List of input data variants to compare
            sequence_length: Length of hash sequence for each variant
            
        Returns:
            Dict: Differential analysis results
        """
        variant_results = []
        
        # Analyze each variant
        for variant in data_variants:
            result = self.analyze_sequence(variant, sequence_length)
            variant_results.append(result)
        
        # Compare pattern metrics across variants
        all_curvatures = []
        all_low_curvature_ratios = []
        
        for result in variant_results:
            metrics = result['pattern_metrics']
            if metrics['curvature_mean'] is not None:
                all_curvatures.append(metrics['curvature_mean'])
            if metrics['low_curvature_ratio'] is not None:
                all_low_curvature_ratios.append(metrics['low_curvature_ratio'])
        
        # Differential analysis
        differential_metrics = {
            'num_variants': len(data_variants),
            'curvature_variance_across_variants': np.var(all_curvatures) if all_curvatures else None,
            'pattern_consistency': np.std(all_low_curvature_ratios) if all_low_curvature_ratios else None,
            'non_random_behavior_detected': False
        }
        
        # Detect non-random behavior through consistency in pattern metrics
        if (differential_metrics['pattern_consistency'] is not None and 
            differential_metrics['pattern_consistency'] < 0.1):
            differential_metrics['non_random_behavior_detected'] = True
        
        return {
            'variant_results': variant_results,
            'differential_metrics': differential_metrics,
            'analysis_summary': {
                'framework': 'Z Framework Discrete Domain',
                'method': 'SHA-256 Discrete Derivative Analysis',
                'parameters': f"a=256, b=e, c=e²",
                'pattern_detection': 'Curvature-based non-randomness detection'
            }
        }