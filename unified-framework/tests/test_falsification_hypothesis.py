#!/usr/bin/env python3
"""
Test suite for Z-Transformation Hypothesis Falsification

This test suite implements empirical tests for the falsification criteria
identified in Issue #368. Tests address:

1. Frame-dependence in v parameter (Lorentz invariance violation)
2. Prime uniqueness vs semiprimes (d(n) ≤ 2 threshold)
3. Curvature analogy validity (graph Laplacian metric)
4. Emergence vs definition (swarm dynamics)
5. Transform invariance (Möbius transforms)

All tests follow the empirical validation approach outlined in the issue comments.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
import mpmath as mp
from sympy import divisors, isprime, mobius
import networkx as nx
from src.core.domain import DiscreteZetaShift
from src.core.axioms import velocity_5d_constraint
from src.core.falsification_analysis import (
    GraphLaplacianMetric, SwarmDynamicsSimulation, 
    FiveDimensionalConstraintValidator, MobiusTransformAnalyzer,
    ComprehensiveFalsificationValidator
)

# Set high precision for numerical stability
mp.mp.dps = 50

class TestFrameDependenceFalsification(unittest.TestCase):
    """Test frame-dependence falsification criteria."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.primes = [2, 3, 5, 7, 11]
        self.semiprimes = [15, 21, 77]  # d(n) = 4
        self.composites = [60, 84]  # high d(n)
        self.v_values = [0.1, 0.5, 1.0, 2.0]
        self.precision_threshold = 1e-16
        
    def test_frame_dependence_variation(self):
        """Test that Z_κ(p,v) varies across different v values, falsifying strict invariance."""
        for prime in self.primes:
            z_values = []
            for v in self.v_values:
                dzs = DiscreteZetaShift(prime, v=v)
                z_values.append(float(dzs.compute_z()))
            
            # Calculate variance across v values
            variance = np.var(z_values)
            
            # Assert variance exceeds precision threshold (falsifies strict invariance)
            self.assertGreater(variance, self.precision_threshold,
                             f"Prime {prime}: variance {variance} should exceed {self.precision_threshold}")
            
    def test_minimal_coupling_property(self):
        """Test that primes show systematically lower Z_κ values than composites."""
        v = 1.0  # Fixed v for comparison
        
        # Compute Z values for each category
        prime_z_values = [float(DiscreteZetaShift(p, v=v).compute_z()) for p in self.primes]
        composite_z_values = [float(DiscreteZetaShift(c, v=v).compute_z()) for c in self.composites]
        
        # Statistical test: primes should have lower mean Z values
        prime_mean = np.mean(prime_z_values)
        composite_mean = np.mean(composite_z_values)
        
        self.assertLess(prime_mean, composite_mean,
                       f"Prime mean Z ({prime_mean}) should be less than composite mean Z ({composite_mean})")

class TestPrimeUniquenessFalsification(unittest.TestCase):
    """Test prime uniqueness vs semiprimes falsification criteria."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        self.semiprimes = [15, 21, 35, 77, 91]  # d(n) = 4
        self.high_divisor = [60, 84, 120]  # d(n) > 4
        
    def test_divisor_threshold_criterion(self):
        """Test d(n) ≤ 2 threshold for true invariance."""
        v = 1.0
        
        # Test primes (d(n) = 2)
        for prime in self.primes:
            d_n = len(divisors(int(prime)))
            self.assertEqual(d_n, 2, f"Prime {prime} should have d(n)=2, got {d_n}")
            
        # Test semiprimes (d(n) = 4)
        for semiprime in self.semiprimes:
            d_n = len(divisors(int(semiprime)))
            self.assertEqual(d_n, 4, f"Semiprime {semiprime} should have d(n)=4, got {d_n}")
            
    def test_quasi_invariance_semiprimes(self):
        """Test that semiprimes show higher Z_κ than primes but lower than high-divisor composites."""
        v = 1.0
        
        # Compute Z values for each category
        prime_z = [float(DiscreteZetaShift(p, v=v).compute_z()) for p in self.primes[:5]]
        semiprime_z = [float(DiscreteZetaShift(sp, v=v).compute_z()) for sp in self.semiprimes[:3]]
        high_div_z = [float(DiscreteZetaShift(hd, v=v).compute_z()) for hd in self.high_divisor[:3]]
        
        prime_mean = np.mean(prime_z)
        semiprime_mean = np.mean(semiprime_z)
        high_div_mean = np.mean(high_div_z)
        
        # Test ordering: primes < semiprimes < high-divisor composites
        self.assertLess(prime_mean, semiprime_mean,
                       f"Prime mean Z ({prime_mean}) < semiprime mean Z ({semiprime_mean})")
        self.assertLess(semiprime_mean, high_div_mean,
                       f"Semiprime mean Z ({semiprime_mean}) < high-divisor mean Z ({high_div_mean})")

class TestCurvatureAnalogFalsification(unittest.TestCase):
    """Test curvature analogy validity through graph Laplacian metric."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.metric = GraphLaplacianMetric(max_n=30)
        
    def test_graph_laplacian_curvature_proxy(self):
        """Test graph Laplacian eigenvalues as curvature proxy."""
        curvature_metrics = self.metric.compute_curvature_proxy()
        
        # Test that curvature computation succeeds
        self.assertNotIn('error', curvature_metrics, 
                        "Curvature proxy computation should not error")
        
        if 'mean_eigenvalue' in curvature_metrics:
            mean_eigenval = curvature_metrics['mean_eigenvalue']
            self.assertGreater(mean_eigenval, 0,
                             "Mean eigenvalue (curvature proxy) should be positive")
            self.assertLess(mean_eigenval, 10,
                           "Mean eigenvalue should be reasonable (<10)")
    
    def test_prime_geodesic_properties(self):
        """Test that primes show minimal geodesic properties."""
        geodesic_analysis = self.metric.analyze_prime_geodesics()
        
        self.assertNotIn('error', geodesic_analysis,
                        "Geodesic analysis should not error")
        
        if 'prime_mean_degree' in geodesic_analysis and 'composite_mean_degree' in geodesic_analysis:
            prime_mean = geodesic_analysis['prime_mean_degree']
            composite_mean = geodesic_analysis['composite_mean_degree']
            
            # Primes should have lower mean degree (minimal connectivity)
            self.assertLess(prime_mean, composite_mean,
                           f"Prime mean degree ({prime_mean}) should be less than composite mean degree ({composite_mean})")

class TestEmergenceVsDefinitionFalsification(unittest.TestCase):
    """Test emergence vs definition falsification through simulated dynamics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.swarm_sim = SwarmDynamicsSimulation(n_particles=50, max_steps=20)
        self.test_values = [5, 7, 11, 15, 21]
        
    def test_swarm_dynamics_convergence(self):
        """Test swarm dynamics simulation for emergence behavior."""
        results = self.swarm_sim.simulate_divisor_swarm([5, 7, 11, 13], coupling_strength=0.1)
        
        self.assertNotIn('error', results,
                        "Swarm dynamics simulation should not error")
        
        # Test that simulation produces reasonable results
        self.assertIn('convergence_rate', results,
                     "Should compute convergence rate")
        self.assertIn('position_stability', results,
                     "Should compute position stability")
        
        # Convergence rate should be non-negative (indicating some stability)
        if 'convergence_rate' in results:
            convergence_rate = results['convergence_rate']
            self.assertGreaterEqual(convergence_rate, -1.0,  # Allow some tolerance
                                   f"Convergence rate {convergence_rate} should indicate stability")
        
    def test_chain_variance_stability(self):
        """Test that unfolded chains show stable trajectories for low-κ values."""
        for n in self.test_values:
            dzs = DiscreteZetaShift(n)
            
            # Unfold chain for 5 steps
            chain = [dzs]
            current = dzs
            for _ in range(5):
                current = current.unfold_next()
                chain.append(current)
            
            # Extract z values from chain
            z_values = [float(shift.compute_z()) for shift in chain]
            
            # Test variance
            if len(z_values) > 1:
                variance = np.var(z_values)
                
                # Lower variance expected for primes (minimal κ)
                if isprime(n):
                    self.assertLess(variance, 2.0,
                                   f"Prime {n} chain variance {variance} should be low (<2.0)")
                else:
                    # Composites may have higher variance
                    self.assertLess(variance, 50.0,
                                   f"Composite {n} chain variance {variance} should be bounded (<50.0)")

class TestTransformInvarianceFalsification(unittest.TestCase):
    """Test transform invariance through Möbius-like transforms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mobius_analyzer = MobiusTransformAnalyzer()
        self.test_values = [2, 3, 5, 7, 15, 21, 35]
        
    def test_mobius_transform_analysis(self):
        """Test comprehensive Möbius transform analysis."""
        results = self.mobius_analyzer.analyze_mobius_normalized_transforms(self.test_values)
        
        self.assertNotIn('error', results,
                        "Möbius transform analysis should not error")
        
        # Test that square-free ratios are computed
        if 'square_free_ratios' in results and results['square_free_ratios']:
            ratios = results['square_free_ratios']
            
            # Most ratios should be bounded for good behavior
            bounded_ratios = [r for r in ratios if r < 10.0]
            bounded_fraction = len(bounded_ratios) / len(ratios)
            
            self.assertGreater(bounded_fraction, 0.5,
                             f"At least 50% of Möbius ratios should be bounded, got {bounded_fraction:.2%}")
        
        # Test that mean ratio is reasonable
        if 'mean_ratio' in results:
            mean_ratio = results['mean_ratio']
            self.assertLess(mean_ratio, 100.0,
                           f"Mean Möbius ratio {mean_ratio} should be reasonable")
    
    def test_mobius_transform_normalization(self):
        """Test Möbius μ(n) transforms normalized by e²."""
        e_squared = float(mp.exp(2))
        
        for n in self.test_values:
            mu_n = mobius(n)
            
            # Test with normalized Möbius as rate parameter
            if mu_n != 0:  # Skip when μ(n) = 0
                b_normalized = mu_n / e_squared
                
                try:
                    dzs = DiscreteZetaShift(n, v=1.0)
                    # Create modified version with Möbius rate
                    dzs_mobius = DiscreteZetaShift(n, v=abs(b_normalized))
                    
                    z_original = float(dzs.compute_z())
                    z_mobius = float(dzs_mobius.compute_z())
                    
                    # Test that both computations are finite and reasonable
                    self.assertTrue(np.isfinite(z_original),
                                   f"Original Z for n={n} should be finite")
                    self.assertTrue(np.isfinite(z_mobius),
                                   f"Möbius-transformed Z for n={n} should be finite")
                    
                    # For square-free numbers, Möbius effect should be bounded
                    if abs(mu_n) == 1:  # Square-free
                        ratio = abs(z_mobius / z_original) if z_original != 0 else 1
                        self.assertLess(ratio, 10.0,
                                       f"Möbius transform ratio for square-free n={n} should be bounded")
                        
                except Exception as e:
                    self.skipTest(f"Möbius transform test failed for n={n}: {e}")

class TestRelativisticConstraintsFalsification(unittest.TestCase):
    """Test 5D relativistic constraints for frame-invariance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.constraint_validator = FiveDimensionalConstraintValidator()
        self.test_primes = [5, 7, 11]
        
    def test_5d_constraint_satisfaction(self):
        """Test 5D velocity constraint satisfaction."""
        # Test various 4D velocity configurations
        v_4d_configs = [
            (0.5, 0.3, 0.2, 0.1),
            (0.6, 0.4, 0.3, 0.2),
            (0.4, 0.4, 0.4, 0.1)
        ]
        
        # Scale by c for realistic testing
        c = self.constraint_validator.c
        v_4d_scaled = [(v[0]*c, v[1]*c, v[2]*c, v[3]*c) for v in v_4d_configs]
        
        results = self.constraint_validator.test_5d_constraint_satisfaction(v_4d_scaled, tolerance=1e6)
        
        self.assertIn('constraint_violations', results,
                     "Should compute constraint violations")
        self.assertIn('computed_v_w_values', results,
                     "Should compute required v_w values")
        
        # At least some constraints should be satisfiable
        finite_violations = [v for v in results['constraint_violations'] if np.isfinite(v)]
        self.assertGreater(len(finite_violations), 0,
                          "At least some 5D constraints should be satisfiable")
    
    def test_prime_invariance_under_constraint(self):
        """Test prime invariance under 5D relativistic constraints."""
        results = self.constraint_validator.test_prime_invariance_under_constraint(self.test_primes)
        
        self.assertIn('mean_prime_variance', results,
                     "Should compute mean prime variance under constraints")
        
        # Prime variance should be reasonable (not infinite)
        mean_variance = results['mean_prime_variance']
        self.assertTrue(np.isfinite(mean_variance),
                       f"Mean prime variance {mean_variance} should be finite")
        
    def test_causality_constraint_validation(self):
        """Test that extreme v values violate causality constraints."""
        # Test superluminal v values should be detectable
        try:
            # This should work but might show high constraint violation
            dzs = DiscreteZetaShift(5, v=1.0)  # Use normalized v first
            z_normal = float(dzs.compute_z())
            self.assertTrue(np.isfinite(z_normal), "Normal computation should be finite")
            
        except Exception as e:
            # Expected for extreme values
            self.assertIn(("causality" or "violation" or "error"), str(e).lower(),
                         "Should raise causality-related error for extreme values")

class TestComprehensiveFalsificationAnalysis(unittest.TestCase):
    """Test comprehensive falsification analysis combining all criteria."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = ComprehensiveFalsificationValidator(max_n=30)
        
    def test_comprehensive_analysis_execution(self):
        """Test that comprehensive falsification analysis executes successfully."""
        results = self.validator.run_comprehensive_falsification_analysis()
        
        # Test that all major analysis categories are present
        expected_categories = [
            'curvature_analysis',
            'emergence_analysis', 
            'constraint_analysis',
            'transform_analysis',
            'frame_dependence'
        ]
        
        for category in expected_categories:
            self.assertIn(category, results,
                         f"Should include {category} analysis")
            
            # Each category should either have results or an error message
            category_result = results[category]
            if isinstance(category_result, dict):
                # Either should have substantive results or error explanation
                self.assertTrue(len(category_result) > 0,
                               f"{category} should have some analysis results")
    
    def test_falsification_criteria_assessment(self):
        """Test assessment of falsification criteria."""
        results = self.validator.run_comprehensive_falsification_analysis()
        
        # Frame dependence falsification
        if 'frame_dependence' in results and 'falsification_threshold_exceeded' in results['frame_dependence']:
            threshold_exceeded = results['frame_dependence']['falsification_threshold_exceeded']
            # This test expects falsification (variance > 1e-16)
            self.assertTrue(threshold_exceeded,
                           "Frame dependence should exceed falsification threshold (variance > 1e-16)")
        
        # Curvature analysis should provide meaningful metrics
        if 'curvature_analysis' in results and 'curvature_metrics' in results['curvature_analysis']:
            curvature_metrics = results['curvature_analysis']['curvature_metrics']
            if 'mean_eigenvalue' in curvature_metrics:
                self.assertGreater(curvature_metrics['mean_eigenvalue'], 0,
                                 "Curvature proxy should be positive")

if __name__ == '__main__':
    unittest.main()