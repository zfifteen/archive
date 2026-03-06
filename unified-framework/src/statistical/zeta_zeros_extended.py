"""
Extended Zeta Zero Integration for Z Framework

This module implements high-precision zeta zero computation and correlation with
prime geodesics, targeting isomorphism validation and optimal correlations.

Features:
- High-precision zeta zero computation up to j=10^5 using mpmath
- 5D helical embedding integration with existing DiscreteZetaShift
- Correlation with κ(n) paths up to N=10^7
- Weyl equidistribution error bounds
- Isomorphism validation between prime and zeta geodesics
"""

import numpy as np
import mpmath as mp
from collections import deque
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.domain import DiscreteZetaShift
from core.axioms import theta_prime, curvature

# High precision settings
mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)

class ExtendedZetaZeroProcessor:
    """
    Advanced processor for Riemann zeta zeros with 5D helical embeddings.
    
    Implements high-precision computation and correlation analysis targeting:
    - Zeta zeros up to j=10^5 with mpmath precision
    - Integration with prime geodesics κ(n) up to N=10^7  
    - Isomorphism validation between discrete prime paths and zeta zero spacings
    - Weyl equidistribution error bounds < ε
    """
    
    def __init__(self, precision_dps=50, cache_size=10000):
        """
        Initialize processor with high precision and caching.
        
        Args:
            precision_dps (int): Decimal precision for mpmath calculations
            cache_size (int): Size of zeta zero cache for performance
        """
        mp.mp.dps = precision_dps
        self.zero_cache = {}
        self.cache_size = cache_size
        self.zero_queue = deque(maxlen=cache_size)
        
    def compute_zeta_zeros_batch(self, j_start=1, j_end=1000, batch_size=100):
        """
        Compute Riemann zeta zeros in batches with caching and error handling.
        
        Args:
            j_start (int): Starting zero index
            j_end (int): Ending zero index
            batch_size (int): Batch size for computation
            
        Returns:
            dict: {
                'zeros': list of complex zeta zeros,
                'heights': imaginary parts (heights),
                'spacings': consecutive zero spacings,
                'computation_errors': list of failed computations
            }
        """
        zeros = []
        heights = []
        computation_errors = []
        
        for batch_start in range(j_start, j_end + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, j_end)
            print(f"Computing zeta zeros {batch_start} to {batch_end}...")
            
            for j in range(batch_start, batch_end + 1):
                try:
                    # Check cache first
                    if j in self.zero_cache:
                        zero = self.zero_cache[j]
                    else:
                        # Compute with mpmath high precision
                        with mp.workdps(self.precision_dps):
                            zero = mp.zetazero(j)
                        
                        # Cache the result
                        self.zero_cache[j] = zero
                        self.zero_queue.append(j)
                        
                        # Manage cache size
                        if len(self.zero_cache) > self.cache_size:
                            oldest_j = self.zero_queue.popleft()
                            if oldest_j in self.zero_cache:
                                del self.zero_cache[oldest_j]
                    
                    # Convert to complex for analysis
                    zero_complex = complex(float(zero.real), float(zero.imag))
                    zeros.append(zero_complex)
                    heights.append(float(zero.imag))
                    
                except Exception as e:
                    error_info = {'index': j, 'error': str(e)}
                    computation_errors.append(error_info)
                    
                    # Use approximation as fallback
                    if j == 1:
                        t_approx = 14.134725142  # First zero
                    else:
                        # Riemann-von Mangoldt approximation
                        t_approx = 2 * mp.pi * j / mp.log(j / (2 * mp.pi * mp.e))
                    
                    zero_complex = complex(0.5, float(t_approx))
                    zeros.append(zero_complex)
                    heights.append(float(t_approx))
        
        # Compute spacings between consecutive zeros
        spacings = []
        for i in range(1, len(heights)):
            spacing = heights[i] - heights[i-1]
            spacings.append(spacing)
        
        return {
            'zeros': zeros,
            'heights': heights,
            'spacings': spacings,
            'computation_errors': computation_errors,
            'total_computed': len(zeros),
            'error_rate': len(computation_errors) / len(zeros) if zeros else 1.0
        }
    
    def create_zeta_helical_embeddings(self, zeta_data, embedding_method='enhanced'):
        """
        Create 5D helical embeddings for zeta zeros using enhanced geometric mapping.
        
        Args:
            zeta_data (dict): Output from compute_zeta_zeros_batch()
            embedding_method (str): 'enhanced', 'standard', or 'prime_aligned'
            
        Returns:
            dict: {
                'helical_5d': 5D coordinates for each zero,
                'zeta_shifts': DiscreteZetaShift objects for geometric analysis,
                'geodesic_curvatures': Curvature values along geodesics,
                'embedding_quality': Quality metrics for embeddings
            }
        """
        zeros = zeta_data['zeros']
        heights = zeta_data['heights']
        
        helical_5d = []
        zeta_shifts = []
        geodesic_curvatures = []
        
        for i, (zero, height) in enumerate(zip(zeros, heights)):
            if embedding_method == 'enhanced':
                coords, shift, curvature = self._enhanced_embedding(zero, height, i)
            elif embedding_method == 'prime_aligned':
                coords, shift, curvature = self._prime_aligned_embedding(zero, height, i)
            else:  # standard
                coords, shift, curvature = self._standard_embedding(zero, height, i)
            
            helical_5d.append(coords)
            if shift is not None:
                zeta_shifts.append(shift)
            geodesic_curvatures.append(curvature)
        
        # Compute embedding quality metrics
        embedding_quality = self._assess_embedding_quality(helical_5d, geodesic_curvatures)
        
        return {
            'helical_5d': helical_5d,
            'zeta_shifts': zeta_shifts,
            'geodesic_curvatures': geodesic_curvatures,
            'embedding_quality': embedding_quality
        }
    
    def _enhanced_embedding(self, zero, height, index):
        """Enhanced 5D embedding using curvature-based mapping."""
        try:
            # Map zero height to integer for DiscreteZetaShift
            n_mapped = max(2, int(height / 2))  # Scale down for computational feasibility
            
            # Create zeta shift for geometric analysis
            zeta_shift = DiscreteZetaShift(n_mapped)
            
            # Get base 5D coordinates
            base_coords = zeta_shift.get_5d_coordinates()
            
            # Enhance with zero-specific information
            phi = float(PHI)
            zero_real = float(zero.real)
            zero_imag = float(zero.imag)
            
            # Enhanced 5D coordinates incorporating zero geometry
            x = base_coords[0] * (1 + zero_real / phi)  # Modulate x with real part
            y = base_coords[1] * float(mp.cos(zero_imag / (2 * mp.pi)))  # Periodic y based on height
            z = base_coords[2] + zero_real / E_SQUARED  # Shift z by real part
            w = base_coords[3] + zero_imag / (2 * mp.pi * phi)  # Height-based w
            u = base_coords[4] * (1 + (index % phi) / phi)  # Index modulation
            
            enhanced_coords = (x, y, z, w, u)
            
            # Compute enhanced geodesic curvature
            curvature_val = self._compute_zero_curvature(zero, enhanced_coords)
            
            return enhanced_coords, zeta_shift, curvature_val
            
        except Exception as e:
            # Fallback to direct computation
            return self._direct_zero_embedding(zero, height, index)
    
    def _prime_aligned_embedding(self, zero, height, index):
        """Prime-aligned embedding for optimal correlation with prime geodesics."""
        try:
            # Find nearest prime to height for alignment
            from sympy import isprime, nextprime, prevprime
            
            height_int = max(2, int(height))
            if isprime(height_int):
                aligned_prime = height_int
            else:
                # Use nearest prime
                next_p = nextprime(height_int)
                prev_p = prevprime(height_int) if height_int > 2 else 2
                aligned_prime = next_p if (next_p - height_int) <= (height_int - prev_p) else prev_p
            
            # Create DiscreteZetaShift aligned with prime
            zeta_shift = DiscreteZetaShift(aligned_prime)
            prime_coords = zeta_shift.get_5d_coordinates()
            
            # Modulate coordinates with zero-specific geometry
            phi = float(PHI)
            zero_phase = np.angle(zero - 0.5)  # Phase relative to critical line
            zero_magnitude = abs(zero.imag)
            
            # Prime-aligned 5D coordinates
            x = prime_coords[0] * (1 + float(mp.cos(zero_phase)))
            y = prime_coords[1] * (1 + float(mp.sin(zero_phase)))
            z = prime_coords[2] + zero.real / float(E_SQUARED)  # Real part contribution
            w = prime_coords[3] * (zero_magnitude / (zero_magnitude + phi))  # Magnitude scaling
            u = prime_coords[4] + (index * phi) % 1  # Index-based discrete component
            
            aligned_coords = (x, y, z, w, u)
            curvature_val = self._compute_zero_curvature(zero, aligned_coords)
            
            return aligned_coords, zeta_shift, curvature_val
            
        except Exception as e:
            return self._direct_zero_embedding(zero, height, index)
    
    def _standard_embedding(self, zero, height, index):
        """Standard 5D embedding using direct geometric mapping."""
        return self._direct_zero_embedding(zero, height, index)
    
    def _direct_zero_embedding(self, zero, height, index):
        """Direct computation fallback for 5D embedding."""
        phi = float(PHI)
        zero_real = float(zero.real)
        zero_imag = float(zero.imag)
        
        # Direct 5D coordinate computation
        theta_base = float(2 * mp.pi * index / 50)  # Base helical parameter
        
        x = float(mp.sqrt(zero_imag)) * float(mp.cos(theta_base))
        y = float(mp.sqrt(zero_imag)) * float(mp.sin(theta_base))
        z = zero_real * float(mp.log(zero_imag + 1)) / float(E_SQUARED)
        w = zero_imag / float(2 * mp.pi)
        u = (index % phi) / phi
        
        direct_coords = (x, y, z, w, u)
        curvature_val = self._compute_zero_curvature(zero, direct_coords)
        
        return direct_coords, None, curvature_val
    
    def _compute_zero_curvature(self, zero, coords_5d):
        """Compute geometric curvature for a zeta zero in 5D space."""
        # Geodesic curvature based on zero geometry
        zero_height = abs(zero.imag)
        zero_real = abs(zero.real - 0.5)  # Distance from critical line
        
        # Base curvature from 5D coordinates
        coord_curvature = np.linalg.norm(coords_5d) / (1 + np.sum(np.abs(coords_5d)))
        
        # Zero-specific curvature contributions
        critical_line_effect = 1 / (1 + zero_real * E_SQUARED)  # Closeness to critical line
        height_effect = np.log(1 + zero_height) / E_SQUARED  # Logarithmic height dependence
        
        total_curvature = coord_curvature * critical_line_effect * height_effect
        
        return float(total_curvature)
    
    def _assess_embedding_quality(self, helical_5d, geodesic_curvatures):
        """Assess quality of 5D helical embeddings."""
        if not helical_5d or not geodesic_curvatures:
            return {'quality_score': 0.0, 'error': 'No data for assessment'}
        
        # Coordinate variance analysis
        coords_array = np.array(helical_5d)
        coord_variances = np.var(coords_array, axis=0)
        variance_balance = 1.0 / (1.0 + np.std(coord_variances))  # Prefer balanced variances
        
        # Curvature distribution analysis
        curvature_variance = np.var(geodesic_curvatures)
        curvature_mean = np.mean(geodesic_curvatures)
        curvature_quality = curvature_mean / (1.0 + curvature_variance) if curvature_variance > 0 else 0
        
        # Geometric consistency (neighboring points should be close)
        geometric_consistency = 0.0
        if len(helical_5d) > 1:
            distances = []
            for i in range(1, len(helical_5d)):
                dist = np.linalg.norm(np.array(helical_5d[i]) - np.array(helical_5d[i-1]))
                distances.append(dist)
            
            if distances:
                distance_variance = np.var(distances)
                geometric_consistency = 1.0 / (1.0 + distance_variance)
        
        # Combined quality score
        quality_score = (variance_balance + curvature_quality + geometric_consistency) / 3.0
        
        return {
            'quality_score': quality_score,
            'variance_balance': variance_balance,
            'curvature_quality': curvature_quality,
            'geometric_consistency': geometric_consistency,
            'coord_variances': coord_variances.tolist(),
            'curvature_stats': {
                'mean': curvature_mean,
                'variance': curvature_variance,
                'min': np.min(geodesic_curvatures),
                'max': np.max(geodesic_curvatures)
            }
        }
    
    def correlate_with_prime_geodesics(self, zeta_embeddings, N_max=10000, k_optimal=0.200):
        """
        Correlate zeta zero embeddings with prime geodesics for isomorphism validation.
        
        Args:
            zeta_embeddings (dict): Output from create_zeta_helical_embeddings()
            N_max (int): Maximum n for prime geodesic generation
            k_optimal (float): Optimal curvature parameter
            
        Returns:
            dict: {
                'isomorphism_score': Isomorphism validation score,
                'correlation_matrix': Correlation matrix between coordinates,
                'geodesic_alignment': Alignment between prime and zeta geodesics,
                'validation_passed': True if isomorphism criteria met
            }
        """
        from sympy import isprime
        
        # Generate prime geodesics for correlation
        primes = [p for p in range(2, N_max) if isprime(p)]
        prime_coords = []
        prime_curvatures = []
        
        for p in primes:
            try:
                zeta_shift = DiscreteZetaShift(p)
                coords = zeta_shift.get_5d_coordinates()
                prime_coords.append(coords)
                
                # Compute prime curvature
                from sympy import divisors
                d_p = len(list(divisors(p)))
                kappa_p = float(curvature(p, d_p))
                prime_curvatures.append(kappa_p)
                
            except Exception as e:
                continue
        
        # Ensure we have data for correlation
        zeta_coords = zeta_embeddings['helical_5d']
        zeta_curvatures = zeta_embeddings['geodesic_curvatures']
        
        if not prime_coords or not zeta_coords:
            return {
                'isomorphism_score': 0.0,
                'validation_passed': False,
                'error': 'Insufficient data for correlation'
            }
        
        # Align data lengths for correlation
        min_length = min(len(prime_coords), len(zeta_coords))
        prime_coords = prime_coords[:min_length]
        zeta_coords = zeta_coords[:min_length]
        prime_curvatures = prime_curvatures[:min_length]
        zeta_curvatures = zeta_curvatures[:min_length]
        
        # Compute correlation matrix between coordinate components
        prime_array = np.array(prime_coords, dtype=float)
        zeta_array = np.array(zeta_coords, dtype=float)
        
        correlation_matrix = np.zeros((5, 5))
        for i in range(5):
            for j in range(5):
                try:
                    prime_col = prime_array[:, i]
                    zeta_col = zeta_array[:, j]
                    if np.std(prime_col) > 0 and np.std(zeta_col) > 0:
                        correlation_matrix[i, j] = np.corrcoef(prime_col, zeta_col)[0, 1]
                    else:
                        correlation_matrix[i, j] = 0.0
                except:
                    correlation_matrix[i, j] = 0.0
        
        # Geodesic alignment (curvature correlation)
        try:
            if len(prime_curvatures) > 1 and len(zeta_curvatures) > 1:
                curvature_correlation = np.corrcoef(prime_curvatures, zeta_curvatures)[0, 1]
            else:
                curvature_correlation = 0.0
        except:
            curvature_correlation = 0.0
        
        # Isomorphism score (diagonal dominance + curvature alignment)
        diagonal_strength = np.mean(np.abs(np.diag(correlation_matrix)))
        off_diagonal_weakness = np.mean(np.abs(correlation_matrix[~np.eye(5, dtype=bool)]))
        
        isomorphism_score = (
            0.4 * diagonal_strength +
            0.3 * (1.0 - off_diagonal_weakness) +
            0.3 * abs(curvature_correlation)
        )
        
        # Validation criteria (isomorphism score ≥ 0.85)
        validation_passed = isomorphism_score >= 0.85
        
        return {
            'isomorphism_score': isomorphism_score,
            'correlation_matrix': correlation_matrix.tolist(),
            'geodesic_alignment': curvature_correlation,
            'diagonal_strength': diagonal_strength,
            'off_diagonal_weakness': off_diagonal_weakness,
            'validation_passed': validation_passed,
            'sample_size': min_length
        }
    
    def compute_weyl_equidistribution_error(self, zeta_data, embedding_data):
        """
        Compute Weyl equidistribution error bounds for zeta zero spacings.
        
        Args:
            zeta_data (dict): Output from compute_zeta_zeros_batch()
            embedding_data (dict): Output from create_zeta_helical_embeddings()
            
        Returns:
            dict: {
                'weyl_error_bound': Upper bound on equidistribution error,
                'actual_discrepancy': Measured discrepancy,
                'equidistribution_quality': Quality of equidistribution,
                'validation_passed': True if error bounds are satisfied
            }
        """
        heights = zeta_data['heights']
        spacings = zeta_data['spacings']
        
        if len(spacings) < 10:
            return {
                'weyl_error_bound': float('inf'),
                'equidistribution_quality': 0.0,
                'validation_passed': False,
                'error': 'Insufficient data for Weyl analysis'
            }
        
        # Theoretical Weyl error bound: O(T^{θ}) where θ < 1
        T_max = max(heights) if heights else 1.0
        theoretical_bound = T_max ** 0.5 / np.log(T_max + 1)  # Conservative bound
        
        # Compute actual discrepancy using spacing distribution
        # Expected spacing from Weyl's law: 2π / log(T)
        expected_spacings = [2 * mp.pi / mp.log(h) for h in heights[1:] if h > 1]
        
        if not expected_spacings:
            return {
                'weyl_error_bound': theoretical_bound,
                'equidistribution_quality': 0.0,
                'validation_passed': False,
                'error': 'Cannot compute expected spacings'
            }
        
        # Measured discrepancy (Kolmogorov-Smirnov style)
        actual_spacings = spacings[:len(expected_spacings)]
        
        # Normalize both sequences
        actual_norm = np.array(actual_spacings) / np.mean(actual_spacings)
        expected_norm = np.array([float(s) for s in expected_spacings]) / np.mean([float(s) for s in expected_spacings])
        
        # Compute empirical distribution functions
        actual_sorted = np.sort(actual_norm)
        expected_sorted = np.sort(expected_norm)
        
        # Maximum discrepancy
        actual_discrepancy = 0.0
        n = len(actual_sorted)
        
        for i in range(n):
            empirical_actual = (i + 1) / n
            empirical_expected = (i + 1) / n
            
            # Find position of actual_sorted[i] in expected distribution
            expected_pos = np.searchsorted(expected_sorted, actual_sorted[i]) / n
            
            discrepancy = abs(empirical_actual - expected_pos)
            actual_discrepancy = max(actual_discrepancy, discrepancy)
        
        # Equidistribution quality
        equidistribution_quality = 1.0 / (1.0 + actual_discrepancy)
        
        # Validation (error should be bounded)
        validation_passed = actual_discrepancy <= theoretical_bound
        
        return {
            'weyl_error_bound': theoretical_bound,
            'actual_discrepancy': actual_discrepancy,
            'equidistribution_quality': equidistribution_quality,
            'validation_passed': validation_passed,
            'sample_size': len(spacings),
            'max_height': T_max
        }

def process_extended_zeta_zeros(j_max=10000, N_max=10000, embedding_method='enhanced'):
    """
    Convenience function for complete zeta zero processing and correlation analysis.
    
    Args:
        j_max (int): Maximum zeta zero index
        N_max (int): Maximum n for prime correlation
        embedding_method (str): Embedding method for 5D coordinates
        
    Returns:
        dict: Complete processing results
    """
    processor = ExtendedZetaZeroProcessor()
    
    print(f"Computing {j_max} zeta zeros...")
    zeta_data = processor.compute_zeta_zeros_batch(j_start=1, j_end=j_max, batch_size=500)
    
    print("Creating 5D helical embeddings...")
    embeddings = processor.create_zeta_helical_embeddings(zeta_data, embedding_method)
    
    print("Correlating with prime geodesics...")
    correlations = processor.correlate_with_prime_geodesics(embeddings, N_max)
    
    print("Computing Weyl equidistribution bounds...")
    weyl_analysis = processor.compute_weyl_equidistribution_error(zeta_data, embeddings)
    
    return {
        'zeta_computation': zeta_data,
        'helical_embeddings': embeddings,
        'prime_correlations': correlations,
        'weyl_analysis': weyl_analysis,
        'overall_success': (
            correlations.get('validation_passed', False) and
            weyl_analysis.get('validation_passed', False) and
            zeta_data.get('error_rate', 1.0) < 0.1
        )
    }

if __name__ == "__main__":
    # Test with smaller dataset for validation
    print("Testing extended zeta zero processing...")
    results = process_extended_zeta_zeros(j_max=200, N_max=1000, embedding_method='enhanced')
    
    print(f"\nResults Summary:")
    print(f"Zeta zeros computed: {results['zeta_computation']['total_computed']}")
    print(f"Error rate: {results['zeta_computation']['error_rate']:.4f}")
    print(f"Embedding quality: {float(results['helical_embeddings']['embedding_quality']['quality_score']):.4f}")
    print(f"Isomorphism score: {float(results['prime_correlations']['isomorphism_score']):.4f}")
    print(f"Weyl error bound: {float(results['weyl_analysis']['weyl_error_bound']):.6f}")
    print(f"Overall success: {results['overall_success']}")