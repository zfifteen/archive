"""
Wave-CRISPR Metrics Integration with Z Framework

This module integrates Wave-CRISPR signal analysis with the unified Z framework,
implementing the required metrics: Δf1, ΔPeaks, ΔEntropy (∝ O / ln n), and 
the composite Score = Z · |Δf1| + ΔPeaks + ΔEntropy.

The implementation bridges genetic sequence analysis with geometric number theory
through the universal invariance principle Z = A(B/c), where c represents the
empirical invariance (speed of light) and provides a universal bound.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
from scipy.stats import entropy
from collections import Counter
import sys
import os

# Add the core modules to path for Z framework integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.axioms import universal_invariance, curvature
from core.domain import DiscreteZetaShift

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
    Enhanced Wave-CRISPR metrics calculator integrated with Z framework.
    
    This class provides comprehensive signal analysis for genetic sequences,
    computing enhanced metrics that incorporate geometric number theory
    principles through the universal Z model.
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
    
    def build_waveform(self, sequence=None, zeta_shift_map=None):
        """
        Build complex waveform from DNA sequence with optional zeta shift modulation.
        
        Args:
            sequence (str, optional): DNA sequence. Uses self.sequence if None.
            zeta_shift_map (dict, optional): Position -> zeta shift mapping
            
        Returns:
            numpy.ndarray: Complex waveform array
        """
        if sequence is None:
            sequence = self.sequence
            
        # Compute spacing with zeta shift modulation
        if zeta_shift_map is None:
            spacings = [self.d_spacing] * len(sequence)
        else:
            spacings = []
            for i in range(len(sequence)):
                zeta_factor = zeta_shift_map.get(i, 0)
                spacing = self.d_spacing * (1 + zeta_factor)
                spacings.append(spacing)
        
        # Cumulative phase positions
        phase_positions = np.cumsum(spacings)
        
        # Build complex waveform
        waveform = []
        for i, base in enumerate(sequence):
            amplitude = NUCLEOTIDE_WEIGHTS[base]
            phase = 2j * np.pi * phase_positions[i]
            waveform.append(amplitude * np.exp(phase))
            
        return np.array(waveform)
    
    def compute_spectrum(self, waveform):
        """
        Compute frequency spectrum magnitude from complex waveform.
        
        Args:
            waveform (numpy.ndarray): Complex waveform
            
        Returns:
            numpy.ndarray: Frequency spectrum magnitudes
        """
        return np.abs(fft(waveform))
    
    def compute_delta_f1(self, base_spectrum, mutated_spectrum, f1_index=10):
        """
        Compute Δf1 metric: percentage change in fundamental frequency component.
        
        Args:
            base_spectrum (numpy.ndarray): Baseline frequency spectrum
            mutated_spectrum (numpy.ndarray): Mutated sequence spectrum
            f1_index (int): Index of fundamental frequency component
            
        Returns:
            float: Δf1 percentage change
        """
        if f1_index >= len(base_spectrum) or f1_index >= len(mutated_spectrum):
            return 0.0
            
        base_f1 = base_spectrum[f1_index]
        mut_f1 = mutated_spectrum[f1_index]
        
        if base_f1 == 0:
            return 0.0 if mut_f1 == 0 else 100.0
            
        delta_f1 = 100.0 * (mut_f1 - base_f1) / base_f1
        return delta_f1
    
    def compute_delta_peaks(self, base_spectrum, mutated_spectrum, threshold_ratio=0.25):
        """
        Compute ΔPeaks metric: change in number of significant spectral peaks.
        
        Args:
            base_spectrum (numpy.ndarray): Baseline frequency spectrum
            mutated_spectrum (numpy.ndarray): Mutated sequence spectrum
            threshold_ratio (float): Peak detection threshold as fraction of max
            
        Returns:
            int: Change in number of peaks
        """
        def count_peaks(spectrum):
            peak_threshold = threshold_ratio * np.max(spectrum)
            return np.sum(spectrum > peak_threshold)
        
        base_peaks = count_peaks(base_spectrum)
        mut_peaks = count_peaks(mutated_spectrum)
        
        return mut_peaks - base_peaks
    
    def compute_spectral_order(self, spectrum):
        """
        Compute spectral order O as measure of frequency complexity.
        
        The spectral order represents the effective number of significant
        frequency components, weighted by their relative magnitudes.
        
        Args:
            spectrum (numpy.ndarray): Frequency spectrum magnitudes
            
        Returns:
            float: Spectral order O
        """
        # Normalize spectrum
        if np.sum(spectrum) == 0:
            return 1.0
            
        normalized_spectrum = spectrum / np.sum(spectrum)
        
        # Compute effective number of components (inverse participation ratio)
        # O = 1 / Σ(p_i^2) where p_i are normalized magnitudes
        participation_ratio = np.sum(normalized_spectrum ** 2)
        
        if participation_ratio == 0:
            return 1.0
            
        spectral_order = 1.0 / participation_ratio
        return spectral_order
    
    def compute_delta_entropy(self, base_spectrum, mutated_spectrum, position):
        """
        Compute ΔEntropy metric: entropy change proportional to O / ln n.
        
        This enhanced entropy metric incorporates spectral order and 
        logarithmic scaling with sequence position, connecting to the
        discrete numberspace geometry of the Z framework.
        
        Args:
            base_spectrum (numpy.ndarray): Baseline frequency spectrum
            mutated_spectrum (numpy.ndarray): Mutated sequence spectrum
            position (int): Mutation position in sequence
            
        Returns:
            float: Enhanced ΔEntropy metric
        """
        # Compute spectral orders
        O_base = self.compute_spectral_order(base_spectrum)
        O_mut = self.compute_spectral_order(mutated_spectrum)
        
        # Logarithmic position scaling (avoid ln(0))
        ln_n = np.log(max(position + 1, 2))
        
        # Enhanced entropy incorporating spectral order
        entropy_base = O_base / ln_n
        entropy_mut = O_mut / ln_n
        
        delta_entropy = entropy_mut - entropy_base
        return delta_entropy
    
    def compute_z_factor(self, position, mutation_velocity=None):
        """
        Compute Z factor from unified framework: Z = A(B/c).
        
        Integrates the mutation analysis with the universal invariance
        principle, treating mutations as discrete transformations in
        geometric numberspace.
        
        Args:
            position (int): Mutation position in sequence
            mutation_velocity (float, optional): Mutation "velocity" parameter
            
        Returns:
            float: Z factor for composite score weighting
        """
        if mutation_velocity is None:
            # Default mutation velocity based on position and sequence length
            mutation_velocity = position / self.length
        
        # Apply universal invariance: Z = A(B/c)
        z_factor = universal_invariance(mutation_velocity, SPEED_OF_LIGHT)
        
        # Apply frame-dependent transformation A using discrete zeta shift
        try:
            zeta_shift = DiscreteZetaShift(position + 1)  # Avoid zero
            frame_transform = zeta_shift.compute_z()
            z_enhanced = float(z_factor * abs(frame_transform))
        except:
            # Fallback to simple geometric scaling
            phi = (1 + np.sqrt(5)) / 2
            frame_transform = phi * ((position % phi) / phi) ** 0.3
            z_enhanced = z_factor * frame_transform
            
        return z_enhanced
    
    def compute_composite_score(self, delta_f1, delta_peaks, delta_entropy, position):
        """
        Compute composite Wave-CRISPR score: Z · |Δf1| + ΔPeaks + ΔEntropy.
        
        This unified score integrates spectral changes with the Z framework,
        providing a geometric measure of mutation impact that respects
        universal invariance principles.
        
        Args:
            delta_f1 (float): Δf1 metric
            delta_peaks (int): ΔPeaks metric  
            delta_entropy (float): ΔEntropy metric
            position (int): Mutation position
            
        Returns:
            float: Composite Wave-CRISPR score
        """
        z_factor = self.compute_z_factor(position)
        
        # Composite score with Z framework integration
        composite_score = z_factor * abs(delta_f1) + delta_peaks + delta_entropy
        
        return composite_score
    
    def analyze_mutation(self, position, new_base):
        """
        Comprehensive mutation analysis with enhanced metrics.
        
        Args:
            position (int): Mutation position (0-indexed)
            new_base (str): New nucleotide (A, T, C, G)
            
        Returns:
            dict: Complete mutation analysis results
        """
        if position >= self.length:
            raise ValueError(f"Position {position} exceeds sequence length {self.length}")
            
        if new_base not in NUCLEOTIDE_WEIGHTS:
            raise ValueError(f"Invalid nucleotide: {new_base}")
            
        original_base = self.sequence[position]
        if original_base == new_base:
            return None  # No mutation
        
        # Create mutated sequence
        mutated_sequence = list(self.sequence)
        mutated_sequence[position] = new_base
        mutated_sequence = ''.join(mutated_sequence)
        
        # Compute zeta shift for geometric modulation
        try:
            zeta_shift = DiscreteZetaShift(position + 1)
            z_coords = zeta_shift.get_5d_coordinates()
            zeta_value = z_coords[4] if len(z_coords) > 4 else 0  # Use u-coordinate
        except:
            zeta_value = position / self.length  # Fallback
            
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
        composite_score = self.compute_composite_score(delta_f1, delta_peaks, delta_entropy, position)
        
        # Z framework integration
        z_factor = self.compute_z_factor(position)
        
        return {
            'position': position,
            'original_base': original_base,
            'mutated_base': new_base,
            'delta_f1': delta_f1,
            'delta_peaks': delta_peaks,
            'delta_entropy': delta_entropy,
            'composite_score': composite_score,
            'z_factor': z_factor,
            'zeta_shift': zeta_value,
            'spectral_order_base': self.compute_spectral_order(base_spectrum),
            'spectral_order_mut': self.compute_spectral_order(mut_spectrum)
        }
    
    def analyze_sequence(self, step_size=15, bases=None):
        """
        Analyze mutations across the sequence at regular intervals.
        
        Args:
            step_size (int): Position step size for analysis
            bases (list, optional): Bases to test. Default: ['A', 'T', 'C', 'G']
            
        Returns:
            list: List of mutation analysis results, sorted by composite score
        """
        if bases is None:
            bases = ['A', 'T', 'C', 'G']
            
        results = []
        
        for position in range(0, self.length, step_size):
            for base in bases:
                analysis = self.analyze_mutation(position, base)
                if analysis is not None:
                    results.append(analysis)
        
        # Sort by composite score (descending)
        results.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return results
    
    def plot_baseline_spectrum(self, save_path=None):
        """
        Plot the baseline vibrational spectrum.
        
        Args:
            save_path (str, optional): Path to save plot. If None, displays plot.
        """
        base_waveform = self.build_waveform()
        spectrum = self.compute_spectrum(base_waveform)
        
        plt.figure(figsize=(10, 6))
        plt.plot(spectrum)
        plt.title(f"Baseline Vibrational Spectrum (Length: {self.length} bp)")
        plt.xlabel("Frequency Index")
        plt.ylabel("Magnitude")
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def generate_report(self, results, top_n=10):
        """
        Generate a formatted report of mutation analysis results.
        
        Args:
            results (list): Mutation analysis results
            top_n (int): Number of top results to include
            
        Returns:
            str: Formatted report
        """
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
        
        report.append(f"TOP {top_n} MUTATIONS BY COMPOSITE SCORE:")
        report.append("-" * 80)
        report.append(f"{'Pos':<4} {'Mut':<6} {'Δf1':<8} {'ΔPeaks':<8} {'ΔEntropy':<10} {'Score':<8} {'Z':<8}")
        report.append("-" * 80)
        
        for i, result in enumerate(results[:top_n]):
            pos = result['position']
            mut = f"{result['original_base']}→{result['mutated_base']}"
            delta_f1 = f"{result['delta_f1']:+.1f}%"
            delta_peaks = f"{result['delta_peaks']:+d}"
            delta_entropy = f"{result['delta_entropy']:+.3f}"
            score = f"{result['composite_score']:.2f}"
            z_factor = f"{result['z_factor']:.1e}"
            
            report.append(f"{pos:<4} {mut:<6} {delta_f1:<8} {delta_peaks:<8} {delta_entropy:<10} {score:<8} {z_factor:<8}")
        
        report.append("")
        report.append("Interpretation:")
        report.append("- Higher composite scores indicate greater mutation impact")
        report.append("- Z factor integrates position-dependent geometric effects")
        report.append("- ΔEntropy incorporates spectral complexity and discrete geometry")
        report.append("- Results connect genetic mutations to universal invariance principles")
        
        return "\n".join(report)


def demo_analysis():
    """
    Demonstration of enhanced Wave-CRISPR metrics analysis.
    """
    # Sample PCSK9 Exon 1 sequence (150 bp)
    sequence = "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG"
    
    print("Wave-CRISPR Enhanced Metrics Analysis")
    print("=" * 50)
    print(f"Analyzing sequence: {sequence[:50]}...")
    print(f"Length: {len(sequence)} bp")
    print()
    
    # Initialize metrics calculator
    metrics = WaveCRISPRMetrics(sequence)
    
    # Analyze mutations
    print("Computing enhanced metrics...")
    results = metrics.analyze_sequence(step_size=15)
    
    # Generate and display report
    report = metrics.generate_report(results, top_n=6)
    print(report)
    
    # Plot baseline spectrum (headless mode for CI)
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    metrics.plot_baseline_spectrum()
    print("\nBaseline spectrum computed successfully.")
    
    return results


if __name__ == "__main__":
    demo_analysis()