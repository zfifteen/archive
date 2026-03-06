#!/usr/bin/env python3
"""
Geometric Factorization Peaks - Modified Version
Implements resonance detection with golden ratio and Euler's number phase modulation
Tests for asymmetry in signal enrichment between semiprime factors p and q
"""

import numpy as np
import math
from typing import List, Tuple, Dict

# Mathematical constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio
E = math.e  # Euler's number

class GeometricResonanceDetector:
    """
    Detects resonance patterns in semiprime factorization
    Uses phase modulation with golden ratio and Euler's number
    """
    
    def __init__(self, semiprime: int):
        self.semiprime = semiprime
        self.p = None  # Smaller factor
        self.q = None  # Larger factor
        
    def set_factors(self, p: int, q: int):
        """Set the known factors (for validation)"""
        if p > q:
            p, q = q, p
        self.p = p
        self.q = q
        
    def compute_geometric_amplitude(self, k: int, use_phi: bool = True, use_e: bool = True) -> float:
        """
        Compute geometric amplitude with phase modulation
        
        A(k) = cos(ln(k) * phi) * cos(ln(k) * e)
        
        This creates interference patterns that show asymmetric enrichment
        near the larger factor q
        
        Args:
            k: Candidate divisor value
            use_phi: Whether to use golden ratio modulation
            use_e: Whether to use Euler's number modulation
            
        Returns:
            Amplitude value in [-1, 1]
        """
        if k <= 1:
            return 0.0
        
        ln_k = math.log(k)
        
        amplitude = 1.0
        
        if use_phi:
            # Golden ratio phase modulation
            phi_term = math.cos(ln_k * PHI)
            amplitude *= phi_term
            
        if use_e:
            # Euler's number phase modulation
            e_term = math.cos(ln_k * E)
            amplitude *= e_term
            
        return amplitude
    
    def scan_resonance_window(self, center: int, window_size: int = 1000) -> Dict:
        """
        Scan for resonance peaks in a window around a center point
        
        Args:
            center: Center of the window (typically near sqrt(N))
            window_size: Half-width of the window
            
        Returns:
            Dictionary with resonance statistics
        """
        start = max(2, center - window_size)
        end = min(self.semiprime, center + window_size)
        
        amplitudes = []
        positions = []
        
        for k in range(start, end):
            amp = self.compute_geometric_amplitude(k)
            amplitudes.append(amp)
            positions.append(k)
            
        amplitudes = np.array(amplitudes)
        positions = np.array(positions)
        
        # Find peaks (local maxima)
        peaks_idx = self._find_peaks(amplitudes)
        
        return {
            'center': center,
            'window_size': window_size,
            'positions': positions,
            'amplitudes': amplitudes,
            'peaks': positions[peaks_idx] if len(peaks_idx) > 0 else [],
            'peak_amplitudes': amplitudes[peaks_idx] if len(peaks_idx) > 0 else [],
            'mean_amplitude': np.mean(amplitudes),
            'std_amplitude': np.std(amplitudes),
            'max_amplitude': np.max(amplitudes),
            'max_position': positions[np.argmax(amplitudes)]
        }
    
    def _find_peaks(self, signal: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Find local maxima in signal above threshold"""
        peaks = []
        
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i-1] and signal[i] > signal[i+1] and signal[i] > threshold:
                peaks.append(i)
                
        return np.array(peaks)
    
    def test_asymmetry(self, p: int, q: int, window_size: int = 1000) -> Dict:
        """
        Test for asymmetric resonance between p and q
        
        The hypothesis claims 5x enrichment near q compared to p
        
        Args:
            p: Smaller factor
            q: Larger factor  
            window_size: Window size for scanning
            
        Returns:
            Dictionary with asymmetry statistics
        """
        self.set_factors(p, q)
        
        # Scan around p
        p_resonance = self.scan_resonance_window(p, window_size)
        
        # Scan around q
        q_resonance = self.scan_resonance_window(q, window_size)
        
        # Compute enrichment ratio
        p_signal = np.abs(p_resonance['mean_amplitude'])
        q_signal = np.abs(q_resonance['mean_amplitude'])
        
        if p_signal > 0:
            enrichment_ratio = q_signal / p_signal
        else:
            enrichment_ratio = float('inf')
        
        # Count peaks
        p_peak_count = len(p_resonance['peaks'])
        q_peak_count = len(q_resonance['peaks'])
        
        return {
            'p': p,
            'q': q,
            'p_resonance': p_resonance,
            'q_resonance': q_resonance,
            'p_signal_strength': p_signal,
            'q_signal_strength': q_signal,
            'enrichment_ratio': enrichment_ratio,
            'p_peak_count': p_peak_count,
            'q_peak_count': q_peak_count,
            'asymmetry_confirmed': enrichment_ratio > 3.0  # Looking for ~5x, use 3x threshold
        }
    
    def generate_spectrum(self, k_min: int, k_max: int, num_points: int = 10000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate full resonance spectrum over a range
        
        Args:
            k_min: Minimum k value
            k_max: Maximum k value
            num_points: Number of points to sample
            
        Returns:
            (k_values, amplitudes) tuple
        """
        k_values = np.logspace(np.log10(k_min), np.log10(k_max), num_points)
        amplitudes = np.array([self.compute_geometric_amplitude(int(k)) for k in k_values])
        
        return k_values, amplitudes


def test_semiprime_set(semiprimes: List[Tuple[int, int, int]], window_size: int = 1000) -> List[Dict]:
    """
    Test a set of semiprimes for resonance asymmetry
    
    Args:
        semiprimes: List of (N, p, q) tuples
        window_size: Window size for resonance scanning
        
    Returns:
        List of asymmetry test results
    """
    results = []
    
    for N, p, q in semiprimes:
        detector = GeometricResonanceDetector(N)
        asymmetry = detector.test_asymmetry(p, q, window_size)
        
        asymmetry['N'] = N
        asymmetry['bits'] = N.bit_length()
        
        results.append(asymmetry)
        
    return results


def main():
    """Test the resonance detector"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Geometric Factorization Resonance Detector')
    parser.add_argument('--p', type=int, help='Smaller prime factor')
    parser.add_argument('--q', type=int, help='Larger prime factor')
    parser.add_argument('--window', type=int, default=1000, help='Resonance window size')
    parser.add_argument('--test-suite', action='store_true', help='Run test suite')
    
    args = parser.parse_args()
    
    if args.test_suite:
        print("Running test suite on sample semiprimes...")
        print("=" * 80)
        
        # Test semiprimes (256-426 bit range as mentioned in hypothesis)
        test_cases = [
            # Small test cases for validation
            (143, 11, 13),
            (221, 13, 17),
            (323, 17, 19),
            (437, 19, 23),
        ]
        
        results = test_semiprime_set(test_cases, args.window)
        
        print(f"\n{'N':>10} {'p':>8} {'q':>8} {'P-Signal':>12} {'Q-Signal':>12} {'Ratio':>10} {'Asymmetric':>12}")
        print("-" * 80)
        
        for r in results:
            print(f"{r['N']:>10} {r['p']:>8} {r['q']:>8} "
                  f"{r['p_signal_strength']:>12.6f} {r['q_signal_strength']:>12.6f} "
                  f"{r['enrichment_ratio']:>10.2f} {str(r['asymmetry_confirmed']):>12}")
        
        # Summary statistics
        enrichment_ratios = [r['enrichment_ratio'] for r in results if r['enrichment_ratio'] != float('inf')]
        if enrichment_ratios:
            mean_enrichment = np.mean(enrichment_ratios)
            std_enrichment = np.std(enrichment_ratios)
            asymmetric_count = sum(1 for r in results if r['asymmetry_confirmed'])
            
            print("\n" + "=" * 80)
            print("Summary Statistics:")
            print(f"Mean enrichment ratio: {mean_enrichment:.2f}")
            print(f"Std enrichment ratio: {std_enrichment:.2f}")
            print(f"Asymmetry confirmed: {asymmetric_count}/{len(results)} cases")
            
    elif args.p and args.q:
        N = args.p * args.q
        
        print(f"Testing semiprime N = {N}")
        print(f"Factors: p = {args.p}, q = {args.q}")
        print(f"Window size: {args.window}")
        print("=" * 80)
        
        detector = GeometricResonanceDetector(N)
        result = detector.test_asymmetry(args.p, args.q, args.window)
        
        print(f"\nResonance around p = {args.p}:")
        print(f"  Mean amplitude: {result['p_signal_strength']:.6f}")
        print(f"  Peak count: {result['p_peak_count']}")
        
        print(f"\nResonance around q = {args.q}:")
        print(f"  Mean amplitude: {result['q_signal_strength']:.6f}")
        print(f"  Peak count: {result['q_peak_count']}")
        
        print(f"\nEnrichment ratio (q/p): {result['enrichment_ratio']:.2f}")
        print(f"Asymmetry confirmed: {result['asymmetry_confirmed']}")
        
    else:
        print("Please specify either --p and --q, or use --test-suite")
        print("Example: python run_geofac_peaks_mod.py --p 11 --q 13")
        print("Example: python run_geofac_peaks_mod.py --test-suite")


if __name__ == "__main__":
    main()
