#!/usr/bin/env python3
"""
Poisson Summation Dualities on Curvature-Weighted Discrete Tori

This module implements Poisson summation formula transformations for geodesic-arithmetic
invariant extraction in the Z-Framework. It provides spatial-to-momentum domain duality
for curvature-weighted discrete toroidal embeddings used in GVA factorization.

Mathematical Foundation:
- Poisson Summation Formula: ∑_{n∈Z} f(n) = ∑_{n∈Z} f̂(n)
- Discrete Torus: T^d = (R/Z)^d with periodic boundary conditions
- Curvature Weighting: κ(n) = d(n) * ln(n+1) / e²
- Theta Functions: θ(z,τ) for arithmetic periodicities

References:
- Poisson summation on discrete tori: https://www.math.uni-bielefeld.de/~grigor/tori.pdf
- Theta functions and zeta: https://www.math.columbia.edu/~woit/fourier-analysis/theta-zeta.pdf
- Classical Poisson formula: https://user.math.uzh.ch/burrin/download/Topics2022.pdf
- GVA curvature embeddings: docs/methods/geometric/GVA_Method_Explanation.md
"""

import numpy as np
from mpmath import mp, mpf, log, exp, sqrt as mpsqrt, pi as mp_pi, cos, sin, fac
from typing import Tuple, List, Optional, Callable, Dict, Any
from scipy import fft
import warnings

# Set high precision for numerical validation
mp.dps = 50

# Universal constants from Z-Framework
PHI = mpf((1 + mpsqrt(5)) / 2)  # Golden ratio
E2 = exp(2)  # e² invariant


class PoissonSummationDuality:
    """
    Implements Poisson summation formula for curvature-weighted discrete tori.
    
    Provides spatial-to-momentum domain transformations to expose arithmetic
    periodicities in geodesic embeddings, enabling dual-domain heuristics for
    factorization without exhaustive modular trials.
    
    Core Transformations:
    1. Spatial domain: Curvature-weighted lattice sums on discrete torus
    2. Momentum domain: Fourier-dual representation with theta function structure
    3. Arithmetic periodicities: Factor-structure signatures in momentum space
    """
    
    def __init__(self, dims: int = 7, precision_dps: int = 50):
        """
        Initialize Poisson summation duality framework.
        
        Args:
            dims: Dimensionality of discrete torus (default: 7 for GVA)
            precision_dps: Decimal precision for mpmath computations
        """
        self.dims = dims
        mp.dps = precision_dps
        self.phi = PHI
        self.e2 = E2
        
    def curvature(self, n: int, d_n: Optional[int] = None) -> mpf:
        """
        Compute discrete curvature κ(n) = d(n) * ln(n+1) / e².
        
        Args:
            n: Integer to compute curvature for
            d_n: Optional divisor count d(n). If None, computed via trial division.
            
        Returns:
            Curvature value κ(n) as mpmath float
        """
        if d_n is None:
            # Compute divisor count via trial division
            d_n = sum(1 for i in range(1, int(np.sqrt(n)) + 1) if n % i == 0) * 2
            if int(np.sqrt(n)) ** 2 == n:
                d_n -= 1
        
        return mpf(d_n) * log(mpf(n) + 1) / self.e2
    
    def theta_function_jacobi(self, z: mpf, tau: mpf, terms: int = 100) -> mpf:
        """
        Compute Jacobi theta function θ₃(z, τ) for arithmetic periodicities.
        
        θ₃(z, τ) = ∑_{n=-∞}^∞ exp(πi n² τ + 2πi n z)
        
        Used to expose factor-structure signatures in momentum space.
        
        Args:
            z: Complex argument (real part as mpf)
            tau: Complex modular parameter (imaginary part as mpf)
            terms: Number of terms in series approximation
            
        Returns:
            Theta function value as mpf
        """
        result = mpf(0)
        q = exp(mp_pi * 1j * tau)  # Nome
        
        for n in range(-terms, terms + 1):
            # θ₃(z,τ) term: exp(πi n² τ) * exp(2πi n z)
            exponent = mp_pi * 1j * (mpf(n**2) * tau + 2 * mpf(n) * z)
            result += exp(exponent)
        
        return abs(result)  # Return magnitude for real-valued analysis
    
    def spatial_lattice_sum(
        self,
        embedding: np.ndarray,
        curvature_weights: np.ndarray,
        lattice_range: int = 10
    ) -> mpf:
        """
        Compute curvature-weighted lattice sum on discrete torus (spatial domain).
        
        S_spatial = ∑_{k∈Z^d, |k|≤R} κ(k) * f(embedding + k)
        
        where κ(k) provides curvature weighting based on lattice site.
        
        Args:
            embedding: Point on discrete torus (d-dimensional array)
            curvature_weights: Precomputed curvature values for lattice sites
            lattice_range: Maximum lattice index to sum over
            
        Returns:
            Spatial domain lattice sum as mpf
        """
        lattice_sum = mpf(0)
        
        # Generate lattice points within range
        for k_idx in range(-lattice_range, lattice_range + 1):
            # Project lattice point to torus (mod 1)
            k_vector = np.array([k_idx % self.dims for _ in range(self.dims)])
            
            # Compute distance on torus (periodic boundary conditions)
            torus_dist = self._torus_distance(embedding, k_vector)
            
            # Weight by curvature and distance kernel
            # Using Gaussian-like kernel: exp(-π * dist²)
            kernel_val = exp(-mp_pi * mpf(torus_dist**2))
            
            # Get curvature weight (use modular arithmetic for indexing)
            weight_idx = abs(k_idx) % len(curvature_weights)
            curvature_weight = curvature_weights[weight_idx]
            
            lattice_sum += curvature_weight * kernel_val
        
        return lattice_sum
    
    def momentum_dual_sum(
        self,
        embedding: np.ndarray,
        curvature_weights: np.ndarray,
        momentum_range: int = 10
    ) -> mpf:
        """
        Compute Fourier-dual momentum space sum (Poisson dual of spatial sum).
        
        S_momentum = ∑_{k∈Z^d, |k|≤R} κ̂(k) * exp(2πi k · embedding)
        
        where κ̂(k) is the Fourier transform of curvature weighting.
        
        Args:
            embedding: Point on discrete torus (d-dimensional array)
            curvature_weights: Curvature values in spatial domain
            momentum_range: Maximum momentum mode to sum over
            
        Returns:
            Momentum domain sum as mpf
        """
        # Compute Fourier transform of curvature weights
        curvature_fft = fft.fft(curvature_weights)
        
        momentum_sum = mpf(0)
        
        for k_idx in range(-momentum_range, momentum_range + 1):
            # Momentum mode k
            k_mod = k_idx % len(curvature_fft)
            curvature_fourier = abs(curvature_fft[k_mod])
            
            # Compute phase factor: exp(2πi k · embedding)
            phase = 2 * mp_pi * mpf(k_idx) * mpf(np.mean(embedding))
            phase_factor = cos(phase)  # Real part for magnitude
            
            momentum_sum += mpf(curvature_fourier) * phase_factor
        
        return momentum_sum
    
    def poisson_duality_ratio(
        self,
        embedding: np.ndarray,
        curvature_weights: np.ndarray,
        lattice_range: int = 10,
        momentum_range: int = 10
    ) -> mpf:
        """
        Compute ratio of spatial to momentum representations (duality measure).
        
        R(embedding) = S_spatial / S_momentum
        
        Deviations from unity indicate arithmetic periodicities that may
        correlate with factor structure.
        
        Args:
            embedding: Point on discrete torus
            curvature_weights: Curvature values
            lattice_range: Spatial domain sum range
            momentum_range: Momentum domain sum range
            
        Returns:
            Duality ratio as mpf
        """
        spatial_sum = self.spatial_lattice_sum(embedding, curvature_weights, lattice_range)
        momentum_sum = self.momentum_dual_sum(embedding, curvature_weights, momentum_range)
        
        # Handle zero momentum sum
        if abs(momentum_sum) < 1e-15:
            return mpf('inf')
        
        return spatial_sum / momentum_sum
    
    def detect_arithmetic_periodicity(
        self,
        N: int,
        embedding_func: Callable[[int], np.ndarray],
        num_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Detect arithmetic periodicities in embeddings via Poisson duality analysis.
        
        Scans candidate values near sqrt(N) and computes duality ratios.
        Peaks in the ratio spectrum may indicate factor-related periodicities.
        
        Args:
            N: Semiprime to analyze
            embedding_func: Function mapping integers to torus embeddings
            num_samples: Number of candidates to sample
            
        Returns:
            Dictionary with detected periodicities and peak locations
        """
        sqrt_n = int(np.sqrt(N))
        candidates = range(sqrt_n - num_samples // 2, sqrt_n + num_samples // 2)
        
        # Precompute curvature weights for lattice/momentum sums
        curvature_weights = np.array([
            float(self.curvature(i)) for i in range(1, 100)
        ])
        
        duality_ratios = []
        candidate_list = []
        
        for candidate in candidates:
            if candidate <= 0:
                continue
                
            embedding = embedding_func(candidate)
            ratio = self.poisson_duality_ratio(
                embedding,
                curvature_weights,
                lattice_range=5,
                momentum_range=5
            )
            
            duality_ratios.append(float(ratio) if ratio != mpf('inf') else 1e10)
            candidate_list.append(candidate)
        
        # Detect peaks (local maxima) in duality ratio spectrum
        duality_array = np.array(duality_ratios)
        peaks = self._find_peaks(duality_array, threshold=0.1)
        
        return {
            'candidates': candidate_list,
            'duality_ratios': duality_ratios,
            'peak_indices': peaks,
            'peak_candidates': [candidate_list[i] for i in peaks],
            'mean_ratio': np.mean(duality_ratios),
            'std_ratio': np.std(duality_ratios),
        }
    
    def dual_domain_factor_heuristic(
        self,
        N: int,
        embedding_func: Callable[[int], np.ndarray],
        z_min: float = 2.0,
        top_k: int = 3
    ) -> List[int]:
        """
        Use dual-domain analysis to suggest factor candidates without modular trials.
        
        Uses z-score gate to identify candidates with anomalous duality ratios,
        indicating potential factor-structure resonance. Always returns top K peaks
        to ensure non-empty candidate list.
        
        Args:
            N: Semiprime to factor
            embedding_func: Torus embedding function
            z_min: Minimum z-score threshold for candidates (default: 2.0)
            top_k: Number of top peaks to always include (default: 3)
            
        Returns:
            List of candidate factors suggested by duality analysis
        """
        periodicity_data = self.detect_arithmetic_periodicity(N, embedding_func)
        
        # Compute z-scores for duality ratios
        mean_ratio = periodicity_data['mean_ratio']
        std_ratio = periodicity_data['std_ratio']
        
        # Avoid division by zero
        if std_ratio < 1e-15:
            std_ratio = 1e-15
        
        z_scores = []
        for ratio in periodicity_data['duality_ratios']:
            z = (ratio - mean_ratio) / std_ratio
            z_scores.append(z)
        
        # Filter candidates by z-score
        candidates_by_zscore = []
        for i, z in enumerate(z_scores):
            if z >= z_min:
                candidates_by_zscore.append(periodicity_data['candidates'][i])
        
        # Always keep top K peaks by z-score
        z_array = np.array(z_scores)
        top_k_indices = np.argsort(z_array)[-top_k:]  # Get indices of top K z-scores
        top_k_candidates = [periodicity_data['candidates'][i] for i in top_k_indices]
        
        # Combine and deduplicate
        all_candidates = list(set(candidates_by_zscore + top_k_candidates))
        
        return sorted(all_candidates)
    
    def _torus_distance(self, point1: np.ndarray, point2: np.ndarray) -> float:
        """
        Compute distance on discrete torus with periodic boundary conditions.
        
        d_torus(p1, p2) = min(|p1 - p2|, 1 - |p1 - p2|) for each dimension
        
        Args:
            point1: First point on torus
            point2: Second point on torus
            
        Returns:
            Torus distance as float
        """
        dists = []
        for c1, c2 in zip(point1, point2):
            # Normalize to [0, 1]
            c1_norm = c1 % 1.0
            c2_norm = c2 % 1.0
            
            # Periodic distance
            d = abs(c1_norm - c2_norm)
            d_periodic = min(d, 1.0 - d)
            dists.append(d_periodic)
        
        return np.sqrt(np.sum(np.array(dists)**2))
    
    def _find_peaks(self, data: np.ndarray, threshold: float = 0.1) -> List[int]:
        """
        Find local maxima (peaks) in 1D data.
        
        Args:
            data: 1D array of values
            threshold: Minimum relative prominence for peak detection
            
        Returns:
            Indices of detected peaks
        """
        peaks = []
        
        for i in range(1, len(data) - 1):
            # Check if local maximum
            if data[i] > data[i-1] and data[i] > data[i+1]:
                # Check prominence
                baseline = (data[i-1] + data[i+1]) / 2
                prominence = (data[i] - baseline) / (baseline + 1e-10)
                
                if prominence > threshold:
                    peaks.append(i)
        
        return peaks

    def calibrate_heuristic(
        self,
        test_cases: List[tuple],
        embedding_func: Callable[[int], np.ndarray],
        z_min_range: np.ndarray = None,
        top_k_range: List[int] = None
    ) -> Dict[str, Any]:
        """
        Calibration harness for tuning z-score threshold and top-K parameters.
        
        Tests the heuristic on known semiprimes and tracks hit rates to find
        optimal z_min and top_k values.
        
        Args:
            test_cases: List of (N, p, q) tuples where N = p × q
            embedding_func: Torus embedding function
            z_min_range: Array of z-score thresholds to test (default: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
            top_k_range: List of top-K values to test (default: [1, 2, 3, 5, 10])
            
        Returns:
            Dictionary with calibration results and optimal parameters
        """
        if z_min_range is None:
            z_min_range = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
        if top_k_range is None:
            top_k_range = [1, 2, 3, 5, 10]
        
        results = []
        
        print("=" * 80)
        print("Calibration Harness: Testing z_min and top_k parameters")
        print("=" * 80)
        
        for N, p, q in test_cases:
            true_factors = {p, q}
            
            # Get periodicity data once per test case
            periodicity_data = self.detect_arithmetic_periodicity(N, embedding_func, num_samples=20)
            mean_ratio = periodicity_data['mean_ratio']
            std_ratio = periodicity_data['std_ratio']
            
            if std_ratio < 1e-15:
                std_ratio = 1e-15
            
            # Compute z-scores
            z_scores = [(r - mean_ratio) / std_ratio for r in periodicity_data['duality_ratios']]
            
            # Test parameter combinations
            for z_min in z_min_range:
                for top_k in top_k_range:
                    # Apply z-score filter
                    candidates_by_zscore = [
                        periodicity_data['candidates'][i] 
                        for i, z in enumerate(z_scores) if z >= z_min
                    ]
                    
                    # Add top K
                    z_array = np.array(z_scores)
                    top_k_indices = np.argsort(z_array)[-top_k:]
                    top_k_candidates = [periodicity_data['candidates'][i] for i in top_k_indices]
                    
                    all_candidates = set(candidates_by_zscore + top_k_candidates)
                    
                    # Check hit rate
                    hits = len(true_factors & all_candidates)
                    hit_rate = hits / len(true_factors)
                    
                    results.append({
                        'N': N,
                        'z_min': z_min,
                        'top_k': top_k,
                        'candidates': len(all_candidates),
                        'hits': hits,
                        'hit_rate': hit_rate,
                        'true_in_candidates': list(true_factors & all_candidates)
                    })
        
        # Aggregate results by parameter combination
        param_stats = {}
        for z_min in z_min_range:
            for top_k in top_k_range:
                key = (z_min, top_k)
                filtered = [r for r in results if r['z_min'] == z_min and r['top_k'] == top_k]
                avg_hit_rate = np.mean([r['hit_rate'] for r in filtered])
                avg_candidates = np.mean([r['candidates'] for r in filtered])
                param_stats[key] = {
                    'avg_hit_rate': avg_hit_rate,
                    'avg_candidates': avg_candidates,
                    'score': avg_hit_rate / (avg_candidates + 1)  # Favor high hit rate, low candidates
                }
        
        # Find optimal parameters
        best_key = max(param_stats.keys(), key=lambda k: param_stats[k]['score'])
        optimal_z_min, optimal_top_k = best_key
        
        print(f"\nTested {len(test_cases)} cases × {len(z_min_range)} z_min × {len(top_k_range)} top_k")
        print(f"Total configurations: {len(z_min_range) * len(top_k_range)}")
        print(f"\nOptimal parameters:")
        print(f"  z_min = {optimal_z_min:.2f}")
        print(f"  top_k = {optimal_top_k}")
        print(f"  Average hit rate: {param_stats[best_key]['avg_hit_rate']:.2%}")
        print(f"  Average candidates: {param_stats[best_key]['avg_candidates']:.1f}")
        
        return {
            'results': results,
            'param_stats': param_stats,
            'optimal_z_min': optimal_z_min,
            'optimal_top_k': optimal_top_k,
            'optimal_hit_rate': param_stats[best_key]['avg_hit_rate'],
            'optimal_candidates': param_stats[best_key]['avg_candidates']
        }



def demo_poisson_duality_gva():
    """
    Demonstration of Poisson summation duality for GVA factorization.
    
    Shows how spatial-momentum duality can expose factor-related periodicities
    in curvature-weighted toroidal embeddings.
    """
    print("=" * 70)
    print("Poisson Summation Duality Demo for GVA")
    print("=" * 70)
    
    # Initialize duality framework
    poisson = PoissonSummationDuality(dims=7, precision_dps=50)
    
    # Example: Small semiprime for demonstration
    N = 15  # 3 × 5
    print(f"\nTarget semiprime N = {N}")
    print(f"True factors: 3, 5")
    
    # Define simple torus embedding (GVA-style)
    def embed_gva(n: int) -> np.ndarray:
        """Simple GVA-style embedding for demo."""
        x = mpf(n) / poisson.e2
        coords = []
        for _ in range(poisson.dims):
            x = poisson.phi * (x % 1.0)**mpf('0.3')
            coords.append(float(x % 1.0))
        return np.array(coords)
    
    # Detect arithmetic periodicities
    print("\n" + "-" * 70)
    print("Detecting arithmetic periodicities via Poisson duality...")
    print("-" * 70)
    
    periodicity_data = poisson.detect_arithmetic_periodicity(
        N, embed_gva, num_samples=10
    )
    
    print(f"\nScanned {len(periodicity_data['candidates'])} candidates")
    print(f"Mean duality ratio: {periodicity_data['mean_ratio']:.4f}")
    print(f"Std duality ratio: {periodicity_data['std_ratio']:.4f}")
    print(f"Detected {len(periodicity_data['peak_indices'])} peaks")
    
    if periodicity_data['peak_candidates']:
        print(f"\nPeak candidates: {periodicity_data['peak_candidates']}")
        
        # Check if true factors are in peaks
        true_factors = [3, 5]
        for factor in true_factors:
            if factor in periodicity_data['peak_candidates']:
                print(f"  ✓ True factor {factor} detected in peaks!")
    
    # Dual-domain factor heuristic (z-score gate)
    print("\n" + "-" * 70)
    print("Dual-domain factor heuristic (z-score gate, z_min=2.0, top_k=3)...")
    print("-" * 70)
    
    suggested_candidates = poisson.dual_domain_factor_heuristic(
        N, embed_gva, z_min=2.0, top_k=3
    )
    
    print(f"\nSuggested candidates: {suggested_candidates}")
    
    # Verify suggestions
    true_hits = [c for c in suggested_candidates if N % c == 0]
    if true_hits:
        print(f"✓ True factors found: {true_hits}")
    else:
        print("✗ No true factors in suggestions (adjust threshold or embedding)")
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    # Run demonstration
    demo_poisson_duality_gva()
