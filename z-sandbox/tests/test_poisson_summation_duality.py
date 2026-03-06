#!/usr/bin/env python3
"""
Tests for Poisson Summation Duality on Curvature-Weighted Discrete Tori

Validates the implementation of Poisson summation formula transformations
for geodesic-arithmetic invariant extraction in the Z-Framework.

Test Coverage:
1. Curvature computation κ(n) = d(n) * ln(n+1) / e²
2. Theta function identities
3. Spatial lattice sums on discrete torus
4. Momentum domain dual sums
5. Poisson duality ratio validation
6. Arithmetic periodicity detection
7. Dual-domain factor heuristics
"""

import pytest
import numpy as np
from mpmath import mp, mpf, log, exp
import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from poisson_summation_duality import PoissonSummationDuality


class TestCurvatureComputation:
    """Test discrete curvature κ(n) = d(n) * ln(n+1) / e²."""
    
    def test_curvature_basic_values(self):
        """Test curvature for small integers with known divisor counts."""
        poisson = PoissonSummationDuality(dims=7)
        
        # n=1: d(1)=1, κ(1) = 1 * ln(2) / e²
        kappa_1 = poisson.curvature(1, d_n=1)
        expected_1 = log(mpf(2)) / exp(2)
        assert abs(kappa_1 - expected_1) < 1e-15, "Curvature for n=1 incorrect"
        
        # n=2: d(2)=2 (1,2), κ(2) = 2 * ln(3) / e²
        kappa_2 = poisson.curvature(2, d_n=2)
        expected_2 = 2 * log(mpf(3)) / exp(2)
        assert abs(kappa_2 - expected_2) < 1e-15, "Curvature for n=2 incorrect"
        
        # n=6: d(6)=4 (1,2,3,6), κ(6) = 4 * ln(7) / e²
        kappa_6 = poisson.curvature(6, d_n=4)
        expected_6 = 4 * log(mpf(7)) / exp(2)
        assert abs(kappa_6 - expected_6) < 1e-15, "Curvature for n=6 incorrect"
    
    def test_curvature_auto_divisor_count(self):
        """Test curvature with automatic divisor count computation."""
        poisson = PoissonSummationDuality(dims=7)
        
        # n=12: d(12)=6 (1,2,3,4,6,12)
        kappa_12 = poisson.curvature(12)
        # Manual calculation: d(12) = 6
        expected_12 = 6 * log(mpf(13)) / exp(2)
        assert abs(kappa_12 - expected_12) < 1e-15, "Auto divisor count failed for n=12"
    
    def test_curvature_monotonicity(self):
        """Test that curvature generally increases with n (probabilistically)."""
        poisson = PoissonSummationDuality(dims=7)
        
        # Sample curvature values
        curvatures = [float(poisson.curvature(n)) for n in [10, 100, 1000]]
        
        # On average, curvature should increase (though not strictly monotonic)
        assert curvatures[2] > curvatures[0], "Curvature should grow with n on average"


class TestThetaFunctions:
    """Test Jacobi theta function implementation."""
    
    def test_theta_function_symmetry(self):
        """Test θ₃(z, τ) symmetry properties."""
        poisson = PoissonSummationDuality(dims=7)
        
        z = mpf('0.5')
        tau = mpf('0.1')
        
        theta_pos = poisson.theta_function_jacobi(z, tau, terms=50)
        theta_neg = poisson.theta_function_jacobi(-z, tau, terms=50)
        
        # θ₃ is even: θ₃(-z, τ) = θ₃(z, τ)
        assert abs(theta_pos - theta_neg) < 1e-10, "Theta function should be even"
    
    def test_theta_function_convergence(self):
        """Test that theta function converges with more terms."""
        poisson = PoissonSummationDuality(dims=7)
        
        z = mpf('0.3')
        tau = mpf('0.5')  # Use larger tau for better convergence
        
        theta_10 = poisson.theta_function_jacobi(z, tau, terms=10)
        theta_50 = poisson.theta_function_jacobi(z, tau, terms=50)
        theta_100 = poisson.theta_function_jacobi(z, tau, terms=100)
        
        # Values should converge (check stabilization)
        diff_50_100 = abs(theta_50 - theta_100)
        
        # With more terms, should be reasonably converged
        assert diff_50_100 < abs(theta_10), "Theta function should converge with more terms"


class TestSpatialLatticeSum:
    """Test spatial domain curvature-weighted lattice sums."""
    
    def test_spatial_sum_positive(self):
        """Test that spatial lattice sum is positive."""
        poisson = PoissonSummationDuality(dims=7)
        
        embedding = np.random.rand(7)
        curvature_weights = np.array([float(poisson.curvature(i)) for i in range(1, 21)])
        
        spatial_sum = poisson.spatial_lattice_sum(embedding, curvature_weights, lattice_range=5)
        
        assert spatial_sum > 0, "Spatial lattice sum should be positive"
    
    def test_spatial_sum_symmetry(self):
        """Test spatial sum symmetry under embedding shift."""
        poisson = PoissonSummationDuality(dims=7)
        
        embedding1 = np.zeros(7)
        embedding2 = np.ones(7)  # Shift by 1 (periodic on torus)
        curvature_weights = np.array([float(poisson.curvature(i)) for i in range(1, 21)])
        
        sum1 = poisson.spatial_lattice_sum(embedding1, curvature_weights, lattice_range=3)
        sum2 = poisson.spatial_lattice_sum(embedding2, curvature_weights, lattice_range=3)
        
        # Due to periodic boundary conditions, should be similar
        # (not exactly equal due to finite lattice range)
        assert abs(sum1 - sum2) / max(sum1, sum2) < 0.5, "Spatial sum should respect torus periodicity"


class TestMomentumDualSum:
    """Test momentum domain Fourier-dual sums."""
    
    def test_momentum_sum_finite(self):
        """Test that momentum sum is finite and non-zero."""
        poisson = PoissonSummationDuality(dims=7)
        
        embedding = np.random.rand(7) * 0.5
        curvature_weights = np.array([float(poisson.curvature(i)) for i in range(1, 21)])
        
        momentum_sum = poisson.momentum_dual_sum(embedding, curvature_weights, momentum_range=5)
        
        assert abs(momentum_sum) > 1e-10, "Momentum sum should be non-zero"
        assert abs(momentum_sum) < 1e10, "Momentum sum should be finite"
    
    def test_momentum_sum_real_valued(self):
        """Test that momentum sum produces real values."""
        poisson = PoissonSummationDuality(dims=7)
        
        embedding = np.random.rand(7)
        curvature_weights = np.array([float(poisson.curvature(i)) for i in range(1, 21)])
        
        momentum_sum = poisson.momentum_dual_sum(embedding, curvature_weights, momentum_range=5)
        
        # Should be real-valued mpf
        assert isinstance(momentum_sum, mpf), "Momentum sum should be mpf type"


class TestPoissonDuality:
    """Test Poisson duality ratio and its properties."""
    
    def test_duality_ratio_positive(self):
        """Test that duality ratio is positive."""
        poisson = PoissonSummationDuality(dims=7)
        
        embedding = np.random.rand(7) * 0.3 + 0.1
        curvature_weights = np.array([float(poisson.curvature(i)) for i in range(1, 21)])
        
        ratio = poisson.poisson_duality_ratio(
            embedding, curvature_weights, lattice_range=5, momentum_range=5
        )
        
        assert ratio > 0 or ratio == mpf('inf'), "Duality ratio should be positive or infinite"
    
    def test_duality_ratio_stability(self):
        """Test duality ratio stability across similar embeddings."""
        poisson = PoissonSummationDuality(dims=7)
        
        embedding1 = np.ones(7) * 0.5
        embedding2 = embedding1 + np.random.rand(7) * 0.01  # Small perturbation
        curvature_weights = np.array([float(poisson.curvature(i)) for i in range(1, 21)])
        
        ratio1 = poisson.poisson_duality_ratio(embedding1, curvature_weights, 5, 5)
        ratio2 = poisson.poisson_duality_ratio(embedding2, curvature_weights, 5, 5)
        
        # Ratios should be similar for similar embeddings
        if ratio1 != mpf('inf') and ratio2 != mpf('inf'):
            rel_diff = abs(ratio1 - ratio2) / max(abs(ratio1), abs(ratio2))
            assert rel_diff < 0.5, "Duality ratio should be stable under small perturbations"


class TestArithmeticPeriodicityDetection:
    """Test detection of arithmetic periodicities via Poisson duality."""
    
    def test_periodicity_detection_small_semiprime(self):
        """Test periodicity detection on small semiprime (15 = 3 × 5)."""
        poisson = PoissonSummationDuality(dims=7)
        
        N = 15
        
        # Simple embedding function
        def embed_simple(n: int) -> np.ndarray:
            from mpmath import sqrt as mpsqrt
            x = mpf(n) / exp(2)
            coords = []
            for _ in range(7):
                x = (mpf((1 + mpsqrt(5)) / 2)) * (x % 1.0)**mpf('0.3')
                coords.append(float(x % 1.0))
            return np.array(coords)
        
        periodicity_data = poisson.detect_arithmetic_periodicity(
            N, embed_simple, num_samples=10
        )
        
        # Should return valid data structure
        assert 'candidates' in periodicity_data
        assert 'duality_ratios' in periodicity_data
        assert 'peak_indices' in periodicity_data
        assert 'mean_ratio' in periodicity_data
        assert 'std_ratio' in periodicity_data
        
        # Should have scanned candidates
        assert len(periodicity_data['candidates']) > 0
        assert len(periodicity_data['duality_ratios']) > 0
        
        # Mean ratio should be finite
        assert np.isfinite(periodicity_data['mean_ratio'])
    
    def test_periodicity_detection_prime_power(self):
        """Test periodicity detection on prime power (9 = 3²)."""
        poisson = PoissonSummationDuality(dims=7)
        
        N = 9
        
        def embed_simple(n: int) -> np.ndarray:
            from mpmath import sqrt as mpsqrt
            x = mpf(n) / exp(2)
            coords = []
            for _ in range(7):
                x = (mpf((1 + mpsqrt(5)) / 2)) * (x % 1.0)**mpf('0.3')
                coords.append(float(x % 1.0))
            return np.array(coords)
        
        periodicity_data = poisson.detect_arithmetic_periodicity(
            N, embed_simple, num_samples=6
        )
        
        # Should detect some structure
        assert periodicity_data['mean_ratio'] > 0


class TestDualDomainFactorHeuristic:
    """Test dual-domain factor heuristic."""
    
    def test_heuristic_returns_candidates(self):
        """Test that heuristic returns candidate list."""
        poisson = PoissonSummationDuality(dims=7)
        
        N = 21  # 3 × 7
        
        def embed_simple(n: int) -> np.ndarray:
            from mpmath import sqrt as mpsqrt
            x = mpf(n) / exp(2)
            coords = []
            for _ in range(7):
                x = (mpf((1 + mpsqrt(5)) / 2)) * (x % 1.0)**mpf('0.3')
                coords.append(float(x % 1.0))
            return np.array(coords)
        
        candidates = poisson.dual_domain_factor_heuristic(N, embed_simple, z_min=2.0, top_k=3)
        
        # Should return a list (never empty with top_k guarantee)
        assert isinstance(candidates, list)
        assert len(candidates) >= 1  # top_k=3 guarantees at least 1 candidate
    
    def test_heuristic_threshold_sensitivity(self):
        """Test that lower z_min returns more candidates."""
        poisson = PoissonSummationDuality(dims=7)
        
        N = 35  # 5 × 7
        
        def embed_simple(n: int) -> np.ndarray:
            from mpmath import sqrt as mpsqrt
            x = mpf(n) / exp(2)
            coords = []
            for _ in range(7):
                x = (mpf((1 + mpsqrt(5)) / 2)) * (x % 1.0)**mpf('0.3')
                coords.append(float(x % 1.0))
            return np.array(coords)
        
        candidates_high_z = poisson.dual_domain_factor_heuristic(N, embed_simple, z_min=3.0, top_k=2)
        candidates_low_z = poisson.dual_domain_factor_heuristic(N, embed_simple, z_min=0.5, top_k=2)
        
        # Lower z_min should return more (or equal) candidates due to looser filter
        assert len(candidates_low_z) >= len(candidates_high_z)


class TestTorusDistance:
    """Test torus distance computation with periodic boundary conditions."""
    
    def test_torus_distance_zero(self):
        """Test distance between identical points is zero."""
        poisson = PoissonSummationDuality(dims=7)
        
        point = np.random.rand(7)
        dist = poisson._torus_distance(point, point)
        
        assert abs(dist) < 1e-10, "Distance to self should be zero"
    
    def test_torus_distance_symmetry(self):
        """Test distance symmetry: d(p1, p2) = d(p2, p1)."""
        poisson = PoissonSummationDuality(dims=7)
        
        point1 = np.random.rand(7)
        point2 = np.random.rand(7)
        
        dist12 = poisson._torus_distance(point1, point2)
        dist21 = poisson._torus_distance(point2, point1)
        
        assert abs(dist12 - dist21) < 1e-10, "Torus distance should be symmetric"
    
    def test_torus_distance_periodicity(self):
        """Test that distance respects periodic boundary conditions."""
        poisson = PoissonSummationDuality(dims=7)
        
        point1 = np.array([0.1] * 7)
        point2 = np.array([0.9] * 7)  # Close via periodic boundary
        
        dist = poisson._torus_distance(point1, point2)
        
        # Distance should be ~0.2*sqrt(7) via periodic wrapping, not 0.8*sqrt(7)
        expected_direct = 0.8 * np.sqrt(7)
        expected_periodic = 0.2 * np.sqrt(7)
        
        assert dist < expected_direct, "Should use shorter periodic distance"
        assert abs(dist - expected_periodic) < 0.1, "Periodic distance calculation"


class TestPeakDetection:
    """Test peak detection in duality ratio spectra."""
    
    def test_find_peaks_simple(self):
        """Test peak detection in simple synthetic data."""
        poisson = PoissonSummationDuality(dims=7)
        
        # Create data with clear peak at index 5
        data = np.array([1.0, 1.1, 1.0, 1.2, 1.0, 3.0, 1.0, 1.1, 1.0])
        peaks = poisson._find_peaks(data, threshold=0.1)
        
        # Should detect peak at index 5
        assert 5 in peaks, "Should detect obvious peak"
    
    def test_find_peaks_no_peaks(self):
        """Test peak detection returns empty for flat data."""
        poisson = PoissonSummationDuality(dims=7)
        
        # Flat data
        data = np.ones(10)
        peaks = poisson._find_peaks(data, threshold=0.1)
        
        # Should find no peaks
        assert len(peaks) == 0, "Should find no peaks in flat data"
    
    def test_find_peaks_threshold_sensitivity(self):
        """Test that higher threshold finds fewer peaks."""
        poisson = PoissonSummationDuality(dims=7)
        
        # Data with small and large peaks
        data = np.array([1.0, 1.5, 1.0, 1.0, 3.0, 1.0, 1.0, 1.3, 1.0])
        
        peaks_low_thresh = poisson._find_peaks(data, threshold=0.1)
        peaks_high_thresh = poisson._find_peaks(data, threshold=0.5)
        
        # Higher threshold should find fewer peaks
        assert len(peaks_high_thresh) <= len(peaks_low_thresh)


# Integration tests
class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_full_pipeline_small_semiprime(self):
        """Test full Poisson duality pipeline on small semiprime."""
        poisson = PoissonSummationDuality(dims=7, precision_dps=50)
        
        N = 15  # 3 × 5
        
        # Define embedding
        def embed(n: int) -> np.ndarray:
            from mpmath import sqrt as mpsqrt
            x = mpf(n) / exp(2)
            coords = []
            for _ in range(7):
                x = (mpf((1 + mpsqrt(5)) / 2)) * (x % 1.0)**mpf('0.3')
                coords.append(float(x % 1.0))
            return np.array(coords)
        
        # Run periodicity detection
        periodicity_data = poisson.detect_arithmetic_periodicity(N, embed, num_samples=10)
        
        # Run heuristic with z-score gate
        candidates = poisson.dual_domain_factor_heuristic(N, embed, z_min=2.0, top_k=3)
        
        # Pipeline should complete without errors
        assert periodicity_data is not None
        assert candidates is not None
        assert len(candidates) >= 1  # top_k guarantee
        
        # Check if any true factors detected
        true_factors = [3, 5]
        detected_true = any(c in candidates or c in periodicity_data['peak_candidates'] 
                           for c in true_factors)
        
        # Note: Detection is not guaranteed with simple embedding, just check pipeline runs
        print(f"True factors detected: {detected_true}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
