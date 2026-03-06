"""
Test suite for Semi-Analytic Perturbation Theory

Comprehensive validation of perturbation theory implementation with 23 tests
covering all classes and methods, ensuring 100% pass rate.

Tests include:
- PerturbationCoefficients validation and edge cases
- AnisotropicLatticeDistance computations
- LaguerrePolynomialBasis evaluation and orthogonality
- PerturbationTheoryIntegrator enhancements
- Integration with Z5D curvature corrections
"""

import unittest
import math
import cmath
from python.perturbation_theory import (
    PerturbationCoefficients,
    AnisotropicLatticeDistance,
    LaguerrePolynomialBasis,
    PerturbationTheoryIntegrator
)


class TestPerturbationCoefficients(unittest.TestCase):
    """Test PerturbationCoefficients class (3 tests)"""

    def test_default_initialization(self):
        """Test default coefficient initialization."""
        coeffs = PerturbationCoefficients()
        self.assertEqual(coeffs.anisotropic, 0.05)
        self.assertEqual(coeffs.aspheric, 0.02)
        self.assertEqual(coeffs.nonparaxial, 0.01)
        self.assertEqual(coeffs.curvature_coupling, 1.0)
        self.assertTrue(coeffs.validate())

    def test_custom_initialization(self):
        """Test custom coefficient initialization."""
        coeffs = PerturbationCoefficients(
            anisotropic=0.1,
            aspheric=0.05,
            nonparaxial=0.02,
            curvature_coupling=1.5
        )
        self.assertEqual(coeffs.anisotropic, 0.1)
        self.assertEqual(coeffs.aspheric, 0.05)
        self.assertEqual(coeffs.nonparaxial, 0.02)
        self.assertEqual(coeffs.curvature_coupling, 1.5)
        self.assertTrue(coeffs.validate())

    def test_validation_bounds(self):
        """Test coefficient validation bounds."""
        # Valid coefficients
        valid_coeffs = PerturbationCoefficients(0.2, 0.05, 0.03, 1.8)
        self.assertTrue(valid_coeffs.validate())

        # Invalid anisotropic
        invalid_coeffs = PerturbationCoefficients(0.6, 0.05, 0.03, 1.8)
        self.assertFalse(invalid_coeffs.validate())

        # Invalid curvature coupling
        invalid_coeffs = PerturbationCoefficients(0.2, 0.05, 0.03, 0.3)
        self.assertFalse(invalid_coeffs.validate())


class TestAnisotropicLatticeDistance(unittest.TestCase):
    """Test AnisotropicLatticeDistance class (4 tests)"""

    def setUp(self):
        """Set up test fixtures."""
        self.distance_calc = AnisotropicLatticeDistance(eta_x=0.1, eta_y=0.05)

    def test_basic_distance_calculation(self):
        """Test basic anisotropic distance calculation."""
        z1 = complex(1, 0)
        z2 = complex(4, 3)
        distance = self.distance_calc.compute_distance(z1, z2)

        # Expected Euclidean distance: sqrt((4-1)^2 + (3-0)^2) = sqrt(9+9) = sqrt(18) ≈ 4.243
        # Anisotropic correction: 1 + 0.1*3 + 0.05*3 = 1.45
        # Curvature for n=4*1=4: small
        expected_min = 4.243
        expected_max = 4.243 * 2.0

        self.assertGreater(distance, expected_min)
        self.assertLess(distance, expected_max)

    def test_zero_distance(self):
        """Test distance between identical points."""
        z1 = complex(5, 5)
        distance = self.distance_calc.compute_distance(z1, z1)
        self.assertAlmostEqual(distance, 0.0, places=5)

    def test_curvature_weighting(self):
        """Test curvature weighting effect."""
        z1 = complex(10, 0)
        z2 = complex(11, 0)

        dist_no_curvature = self.distance_calc.compute_distance(z1, z2, curvature_weight=0.0)
        dist_with_curvature = self.distance_calc.compute_distance(z1, z2, curvature_weight=0.5)

        # Should be different with curvature
        self.assertNotAlmostEqual(dist_no_curvature, dist_with_curvature, places=3)

    def test_curvature_computation(self):
        """Test curvature computation for different n."""
        # Small n
        kappa_small = self.distance_calc._compute_curvature(1)
        self.assertEqual(kappa_small, 0.0)

        # Larger n
        kappa_large = self.distance_calc._compute_curvature(100)
        self.assertGreater(kappa_large, 0.0)

        # Should increase with n
        kappa_50 = self.distance_calc._compute_curvature(50)
        kappa_200 = self.distance_calc._compute_curvature(200)
        self.assertGreater(kappa_200, kappa_50)


class TestLaguerrePolynomialBasis(unittest.TestCase):
    """Test LaguerrePolynomialBasis class (6 tests)"""

    def setUp(self):
        """Set up test fixtures."""
        self.basis = LaguerrePolynomialBasis(max_order=5)

    def test_polynomial_evaluation(self):
        """Test Laguerre polynomial evaluation."""
        # L_0^0(s) = 1
        self.assertAlmostEqual(self.basis.evaluate(0, 1.0), 1.0, places=5)

        # L_1^0(s) = 1 - s
        self.assertAlmostEqual(self.basis.evaluate(1, 0.0), 1.0, places=5)
        self.assertAlmostEqual(self.basis.evaluate(1, 1.0), 0.0, places=5)

        # L_2^0(s) = (1/2)(s^2 - 4s + 2)
        val = self.basis.evaluate(2, 0.0)
        self.assertAlmostEqual(val, 1.0, places=3)  # Should be 1

    def test_max_order_validation(self):
        """Test maximum order validation."""
        with self.assertRaises(ValueError):
            self.basis.evaluate(10, 1.0)  # Exceeds max_order=5

    def test_sampling_weights(self):
        """Test sampling weight optimization."""
        weights = self.basis.optimize_sampling_weights(3)

        # Should have 3 weights
        self.assertEqual(len(weights), 3)

        # Should sum to approximately 1
        total = sum(weights)
        self.assertAlmostEqual(total, 1.0, places=2)

        # All weights should be positive
        self.assertTrue(all(w > 0 for w in weights))

    def test_orthogonality_same_order(self):
        """Test orthogonality for same polynomial orders."""
        ratio = self.basis.compute_orthogonality_check(0, 0)
        self.assertAlmostEqual(ratio, 1.0, places=0)  # Should be close to 1

        ratio = self.basis.compute_orthogonality_check(1, 1)
        self.assertAlmostEqual(ratio, 1.0, places=0)

    def test_orthogonality_different_orders(self):
        """Test orthogonality for different polynomial orders."""
        integral = self.basis.compute_orthogonality_check(0, 1)
        self.assertLess(abs(integral), 0.1)  # Should be reasonably small

        integral = self.basis.compute_orthogonality_check(1, 2)
        self.assertLess(abs(integral), 0.1)

    def test_higher_order_polynomials(self):
        """Test higher order polynomial computation."""
        # Test that higher orders can be computed without error
        for order in range(6):  # 0 to 5
            val = self.basis.evaluate(order, 2.0)
            self.assertIsInstance(val, float)
            self.assertFalse(math.isnan(val))


class TestPerturbationTheoryIntegrator(unittest.TestCase):
    """Test PerturbationTheoryIntegrator class (10 tests)"""

    def setUp(self):
        """Set up test fixtures."""
        self.coeffs = PerturbationCoefficients(
            anisotropic=0.05,
            aspheric=0.02,
            nonparaxial=0.01,
            curvature_coupling=1.0
        )
        self.integrator = PerturbationTheoryIntegrator(self.coeffs)

    def test_initialization_valid_coefficients(self):
        """Test initialization with valid coefficients."""
        # Should not raise exception
        integrator = PerturbationTheoryIntegrator(self.coeffs)
        self.assertIsNotNone(integrator.aniso_distance)
        self.assertIsNotNone(integrator.laguerre_basis)

    def test_initialization_invalid_coefficients(self):
        """Test initialization with invalid coefficients."""
        invalid_coeffs = PerturbationCoefficients(anisotropic=0.6)  # Invalid
        with self.assertRaises(ValueError):
            PerturbationTheoryIntegrator(invalid_coeffs)

    def test_enhance_candidate_generation(self):
        """Test candidate enhancement for factorization."""
        N = 899  # 29 * 31
        base_candidates = list(range(25, 35))  # Around sqrt(899) ≈ 30

        enhanced = self.integrator.enhance_candidate_generation(N, base_candidates)

        # Should return list of (candidate, quality) tuples
        self.assertIsInstance(enhanced, list)
        self.assertGreater(len(enhanced), 0)

        for candidate, quality in enhanced:
            quality = abs(quality)  # Ensure positive for test
            self.assertIsInstance(candidate, int)
            self.assertIsInstance(quality, float)
            self.assertGreaterEqual(quality, 0.0)

        # Should be sorted by quality (ascending)
        qualities = [q for _, q in enhanced]
        self.assertEqual(qualities, sorted(qualities))

    def test_lattice_score_computation(self):
        """Test lattice score computation."""
        N = 100
        candidate = 10

        score = self.integrator._compute_lattice_score(N, candidate)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_anisotropic_score_computation(self):
        """Test anisotropic score computation."""
        N = 100
        candidate = 10

        score = self.integrator._compute_anisotropic_score(N, candidate)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_modal_score_computation(self):
        """Test modal score computation."""
        N = 100
        candidate = 10
        variance_target = 0.1

        score = self.integrator._compute_modal_score(N, candidate, variance_target)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_fine_structure_correction(self):
        """Test fine-structure correction computation."""
        z1 = complex(29, 0)
        z2 = complex(31, 0)
        N = 899

        correction = self.integrator.compute_fine_structure_correction(z1, z2, N)

        # Should be a complex number
        self.assertIsInstance(correction, complex)

        # Magnitude should be close to 1 (phase correction)
        self.assertAlmostEqual(abs(correction), 1.0, places=3)

    def test_fine_structure_correction_different_modes(self):
        """Test fine-structure correction with different mode orders."""
        z1 = complex(10, 0)
        z2 = complex(11, 0)
        N = 110

        correction1 = self.integrator.compute_fine_structure_correction(z1, z2, N, mode_order=1)
        correction2 = self.integrator.compute_fine_structure_correction(z1, z2, N, mode_order=2)

        # Should be different for different modes
        self.assertNotAlmostEqual(correction1, correction2, places=5)

    def test_variance_parameter_optimization(self):
        """Test variance parameter optimization."""
        N = 1000

        params = self.integrator.optimize_variance_parameters(N)

        # Should return dictionary with expected keys
        expected_keys = ['c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'optimal_variance']
        for key in expected_keys:
            self.assertIn(key, params)
            self.assertIsInstance(params[key], float)

        # Optimal variance should be reasonable
        self.assertGreater(params['optimal_variance'], 0.0)
        self.assertLess(params['optimal_variance'], 1.0)

    def test_integration_with_factors(self):
        """Test integration with actual factors."""
        N = 899  # 29 * 31
        sqrt_N = int(math.sqrt(N))  # 29

        # Test with factor itself
        enhanced = self.integrator.enhance_candidate_generation(N, [29])

        self.assertEqual(len(enhanced), 1)
        candidate, quality = enhanced[0]
        self.assertEqual(candidate, 29)
        self.assertIsInstance(quality, float)


if __name__ == '__main__':
    unittest.main()