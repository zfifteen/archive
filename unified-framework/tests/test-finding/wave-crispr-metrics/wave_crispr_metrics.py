"""
Wave-CRISPR Metrics Implementation

This module implements the four required metrics for CRISPR sequence analysis:
- Δf1: Fundamental frequency change
- ΔPeaks: Spectral peak count change  
- ΔEntropy: Enhanced entropy change (∝ O / ln n)
- Score: Composite score = Z · |Δf1| + ΔPeaks + ΔEntropy

Integrated with Z framework for cross-domain statistical invariants.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
from scipy.stats import entropy
from collections import Counter
import sys
import os

# Add core modules for Z framework integration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from core.axioms import universal_invariance, curvature
    from core.domain import DiscreteZetaShift
except ImportError:
    print("Warning: Z framework modules not available, using fallback implementations")
    
    def universal_invariance(B, c):
        """Fallback universal invariance calculation."""
        if c == 0:
            return 0.0
        return B / c
    
    class DiscreteZetaShift:
        """Fallback DiscreteZetaShift class."""
        def __init__(self, position, length):
            self.position = position
            self.length = length
        
        def get_5d_coordinates(self):
            """Simple 5D coordinate fallback."""
            return [0, 0, 0, 0, self.position / self.length]

# Physical constants
SPEED_OF_LIGHT = 299792458  # m/s - universal invariant

# Base weights mapping nucleotides to complex wave functions
NUCLEOTIDE_WEIGHTS = {
    'A': 1 + 0j,    # Adenine: positive real
    'T': -1 + 0j,   # Thymine: negative real  
    'C': 0 + 1j,    # Cytosine: positive imaginary
    'G': 0 - 1j     # Guanine: negative imaginary
}

class WaveCRISPRMetrics:
    """
    Wave-CRISPR metrics calculator implementing the four required metrics
    with Z framework integration for cross-domain statistical invariants.
    """
    
    def __init__(self, sequence, d_spacing=0.34):
        """
        Initialize Wave-CRISPR metrics calculator.
        
        Args:
            sequence (str): DNA sequence (A, T, C, G)
            d_spacing (float): Base pair spacing in nm (default 0.34)
        """
        self.sequence = sequence.upper()
        self.d_spacing = d_spacing
        self.length = len(sequence)
        
        # Validate sequence
        if not all(base in NUCLEOTIDE_WEIGHTS for base in self.sequence):
            raise ValueError("Sequence must contain only A, T, C, G nucleotides")
    
    def build_waveform(self, sequence, zeta_shift_map=None):
        """
        Build complex waveform from DNA sequence with optional zeta shifts.
        
        Args:
            sequence (str): DNA sequence
            zeta_shift_map (dict): Optional position-dependent zeta shifts
            
        Returns:
            np.ndarray: Complex waveform
        """
        waveform = np.zeros(len(sequence), dtype=complex)
        
        for i, base in enumerate(sequence):
            weight = NUCLEOTIDE_WEIGHTS[base]
            
            # Apply zeta shift if provided
            if zeta_shift_map and i in zeta_shift_map:
                zeta_factor = 1.0 + zeta_shift_map[i]
                weight *= zeta_factor
            
            waveform[i] = weight
        
        return waveform
    
    def compute_spectrum(self, waveform):
        """
        Compute power spectrum from waveform.
        
        Args:
            waveform (np.ndarray): Complex waveform
            
        Returns:
            np.ndarray: Power spectrum
        """
        spectrum = np.abs(fft(waveform))**2
        return spectrum
    
    def compute_delta_f1(self, base_spectrum, mutated_spectrum):
        """
        Compute Δf1 - fundamental frequency change.
        
        Formula: Δf1 = 100 × (F1_mut - F1_base) / F1_base
        
        Args:
            base_spectrum (np.ndarray): Baseline power spectrum
            mutated_spectrum (np.ndarray): Mutated power spectrum
            
        Returns:
            float: Δf1 percentage change
        """
        # Use frequency bin 10 as fundamental frequency component
        f1_index = min(10, len(base_spectrum) - 1)
        
        f1_base = base_spectrum[f1_index]
        f1_mut = mutated_spectrum[f1_index]
        
        if f1_base == 0:
            return 0.0
        
        delta_f1 = 100.0 * (f1_mut - f1_base) / f1_base
        return delta_f1
    
    def compute_delta_peaks(self, base_spectrum, mutated_spectrum):
        """
        Compute ΔPeaks - spectral peak count change.
        
        Formula: ΔPeaks = Peaks_mut - Peaks_base
        
        Args:
            base_spectrum (np.ndarray): Baseline power spectrum
            mutated_spectrum (np.ndarray): Mutated power spectrum
            
        Returns:
            int: Change in number of significant peaks
        """
        def count_peaks(spectrum):
            """Count peaks above 25% of maximum."""
            if len(spectrum) == 0:
                return 0
            
            threshold = 0.25 * np.max(spectrum)
            peaks = 0
            
            for i in range(1, len(spectrum) - 1):
                if (spectrum[i] > spectrum[i-1] and 
                    spectrum[i] > spectrum[i+1] and 
                    spectrum[i] > threshold):
                    peaks += 1
            
            return peaks
        
        base_peaks = count_peaks(base_spectrum)
        mut_peaks = count_peaks(mutated_spectrum)
        
        return mut_peaks - base_peaks
    
    def compute_delta_entropy(self, base_spectrum, mutated_spectrum, position):
        """
        Compute ΔEntropy - enhanced entropy change (∝ O / ln n).
        
        Formula: ΔEntropy = (O_mut / ln(n+1)) - (O_base / ln(n+1))
        where O = 1 / Σ(p_i²) is the spectral order (inverse participation ratio)
        
        Args:
            base_spectrum (np.ndarray): Baseline power spectrum
            mutated_spectrum (np.ndarray): Mutated power spectrum
            position (int): Mutation position for discrete geometry scaling
            
        Returns:
            float: Enhanced entropy change
        """
        def compute_spectral_order(spectrum):
            """Compute spectral order O = 1 / Σ(p_i²)."""
            if np.sum(spectrum) == 0:
                return 0.0
            
            # Normalize to probabilities
            p = spectrum / np.sum(spectrum)
            
            # Compute inverse participation ratio
            participation = np.sum(p**2)
            if participation == 0:
                return 0.0
            
            order = 1.0 / participation
            return order
        
        # Compute spectral orders
        o_base = compute_spectral_order(base_spectrum)
        o_mut = compute_spectral_order(mutated_spectrum)
        
        # Discrete geometry scaling factor
        n = position + 1  # Position index (1-based)
        scaling = np.log(n + 1)
        
        if scaling == 0:
            return 0.0
        
        # Enhanced entropy change
        delta_entropy = (o_mut / scaling) - (o_base / scaling)
        return delta_entropy
    
    def compute_z_factor(self, position):
        """
        Compute Z factor using universal invariance Z = A(B/c).
        
        Args:
            position (int): Mutation position
            
        Returns:
            float: Z factor for position weighting
        """
        try:
            # Create zeta shift for position
            zeta_shift = DiscreteZetaShift(position, self.length)
            z_coords = zeta_shift.get_5d_coordinates()
            zeta_value = z_coords[4] if len(z_coords) > 4 else 0
        except:
            # Fallback calculation
            zeta_value = position / self.length
        
        # Universal invariance calculation
        z_factor = universal_invariance(zeta_value, SPEED_OF_LIGHT)
        
        return z_factor
    
    def compute_composite_score(self, delta_f1, delta_peaks, delta_entropy, z_factor):
        """
        Compute composite score = Z · |Δf1| + ΔPeaks + ΔEntropy.
        
        Args:
            delta_f1 (float): Δf1 percentage change
            delta_peaks (int): ΔPeaks count change
            delta_entropy (float): ΔEntropy change
            z_factor (float): Z factor weight
            
        Returns:
            float: Composite score
        """
        score = z_factor * abs(delta_f1) + delta_peaks + delta_entropy
        return score
    
    def analyze_mutation(self, position, new_base):
        """
        Analyze the impact of a single mutation.
        
        Args:
            position (int): Position to mutate (0-based)
            new_base (str): New nucleotide (A, T, C, G)
            
        Returns:
            dict: Analysis results or None if no mutation
        """
        if position < 0 or position >= self.length:
            raise ValueError(f"Position {position} out of range [0, {self.length-1}]")
        
        if new_base not in NUCLEOTIDE_WEIGHTS:
            raise ValueError(f"Invalid nucleotide: {new_base}")
        
        original_base = self.sequence[position]
        
        # Skip if no actual mutation
        if original_base == new_base:
            return None
        
        # Create mutated sequence
        mutated_sequence = list(self.sequence)
        mutated_sequence[position] = new_base
        mutated_sequence = ''.join(mutated_sequence)
        
        # Compute Z factor for position
        z_factor = self.compute_z_factor(position)
        
        # Create zeta shift map for mutation
        try:
            zeta_shift = DiscreteZetaShift(position, self.length)
            z_coords = zeta_shift.get_5d_coordinates()
            zeta_value = z_coords[4] if len(z_coords) > 4 else 0
        except:
            zeta_value = position / self.length
        
        zeta_shift_map = {position: zeta_value}
        
        # Build waveforms
        base_waveform = self.build_waveform(self.sequence)
        mut_waveform = self.build_waveform(mutated_sequence, zeta_shift_map)
        
        # Compute spectra
        base_spectrum = self.compute_spectrum(base_waveform)
        mut_spectrum = self.compute_spectrum(mut_waveform)
        
        # Compute enhanced metrics
        delta_f1 = self.compute_delta_f1(base_spectrum, mut_spectrum)
        delta_peaks = self.compute_delta_peaks(base_spectrum, mut_spectrum)
        delta_entropy = self.compute_delta_entropy(base_spectrum, mut_spectrum, position)
        
        # Compute composite score
        composite_score = self.compute_composite_score(delta_f1, delta_peaks, delta_entropy, z_factor)
        
        return {
            'position': position,
            'original_base': original_base,
            'mutated_base': new_base,
            'delta_f1': delta_f1,
            'delta_peaks': delta_peaks,
            'delta_entropy': delta_entropy,
            'z_factor': z_factor,
            'composite_score': composite_score
        }
    
    def analyze_sequence(self, step_size=5, bases=None):
        """
        Analyze mutations across the entire sequence.
        
        Args:
            step_size (int): Step size for position sampling
            bases (list): Bases to test (default: all A,T,C,G)
            
        Returns:
            list: Sorted analysis results by composite score
        """
        if bases is None:
            bases = ['A', 'T', 'C', 'G']
        
        results = []
        
        # Sample positions across sequence
        positions = range(0, self.length, step_size)
        
        for pos in positions:
            original_base = self.sequence[pos]
            
            for new_base in bases:
                if new_base != original_base:
                    result = self.analyze_mutation(pos, new_base)
                    if result:
                        results.append(result)
        
        # Sort by composite score (descending)
        results.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return results
    
    def generate_report(self, results, top_n=10):
        """
        Generate a formatted analysis report.
        
        Args:
            results (list): Analysis results
            top_n (int): Number of top mutations to include
            
        Returns:
            str: Formatted report
        """
        if not results:
            return "No mutation results to report."
        
        report = []
        report.append("=" * 80)
        report.append("WAVE-CRISPR METRICS ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Sequence Length: {self.length} bp")
        report.append(f"Total Mutations Analyzed: {len(results)}")
        report.append("")
        report.append("Enhanced Metrics Definition:")
        report.append("- Δf1: Percentage change in fundamental frequency component")
        report.append("- ΔPeaks: Change in number of significant spectral peaks")
        report.append("- ΔEntropy: Entropy change ∝ O / ln n (spectral order / log position)")
        report.append("- Composite Score: Z · |Δf1| + ΔPeaks + ΔEntropy")
        report.append("- Z Factor: Universal invariance factor from Z = A(B/c) framework")
        report.append("")
        report.append(f"TOP {min(top_n, len(results))} MUTATIONS BY COMPOSITE SCORE:")
        report.append("-" * 80)
        report.append(f"{'Pos':<4} {'Mut':<6} {'Δf1':<8} {'ΔPeaks':<8} {'ΔEntropy':<10} {'Score':<8} {'Z':<8}")
        report.append("-" * 80)
        
        for i, result in enumerate(results[:top_n]):
            report.append(
                f"{result['position']:<4} "
                f"{result['original_base']}→{result['mutated_base']:<4} "
                f"{result['delta_f1']:+.1f}%   "
                f"{result['delta_peaks']:+d:<8} "
                f"{result['delta_entropy']:+.3f:<10} "
                f"{result['composite_score']:.2f}    "
                f"{result['z_factor']:.1e}"
            )
        
        report.append("")
        report.append("Interpretation:")
        report.append("- Higher composite scores indicate greater mutation impact")
        report.append("- Z factor integrates position-dependent geometric effects")
        report.append("- ΔEntropy incorporates spectral complexity and discrete geometry")
        report.append("- Results connect genetic mutations to universal invariance principles")
        
        return "\n".join(report)

def compute_metrics_summary(sequence, mutations=None):
    """
    Compute a summary of Wave-CRISPR metrics for a sequence.
    
    Args:
        sequence (str): DNA sequence
        mutations (list): Optional specific mutations to analyze
        
    Returns:
        dict: Metrics summary
    """
    metrics = WaveCRISPRMetrics(sequence)
    
    if mutations is None:
        # Default sampling
        results = metrics.analyze_sequence(step_size=max(5, len(sequence)//10))
    else:
        # Analyze specific mutations
        results = []
        for pos, new_base in mutations:
            result = metrics.analyze_mutation(pos, new_base)
            if result:
                results.append(result)
    
    if not results:
        return {"error": "No valid mutations analyzed"}
    
    # Compute summary statistics
    scores = [r['composite_score'] for r in results]
    delta_f1_values = [r['delta_f1'] for r in results]
    delta_peaks_values = [r['delta_peaks'] for r in results]
    delta_entropy_values = [r['delta_entropy'] for r in results]
    z_factors = [r['z_factor'] for r in results]
    
    return {
        "sequence_length": len(sequence),
        "mutations_analyzed": len(results),
        "composite_score": {
            "max": max(scores),
            "min": min(scores),
            "mean": np.mean(scores),
            "std": np.std(scores)
        },
        "delta_f1": {
            "max": max(delta_f1_values),
            "min": min(delta_f1_values),
            "mean": np.mean(delta_f1_values),
            "std": np.std(delta_f1_values)
        },
        "delta_peaks": {
            "max": max(delta_peaks_values),
            "min": min(delta_peaks_values),
            "mean": np.mean(delta_peaks_values),
            "std": np.std(delta_peaks_values)
        },
        "delta_entropy": {
            "max": max(delta_entropy_values),
            "min": min(delta_entropy_values),
            "mean": np.mean(delta_entropy_values),
            "std": np.std(delta_entropy_values)
        },
        "z_factor": {
            "max": max(z_factors),
            "min": min(z_factors),
            "mean": np.mean(z_factors),
            "std": np.std(z_factors)
        },
        "top_mutations": results[:5]
    }