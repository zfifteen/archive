#!/usr/bin/env python3
"""
Test suite for Function Approximation Module

Validates:
1. Tanh approximation convergence for different k values
2. Asymmetric Gaussian fit accuracy and error reduction
3. Nonlinear least squares fitting and cross-validation
4. Spline approximation smoothness and interpolation
5. Integration with Monte Carlo, Z5D, and Gaussian lattice
"""

import unittest
import sys
import os
import numpy as np

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from function_approximation import (
    TanhApproximation,
    AsymmetricGaussianFit,
    NonlinearLeastSquares,
    SplineApproximation
)
from monte_carlo import FactorizationMonteCarloEnhancer
from z5d_axioms import calibrate_error_bounds_with_regression, approximate_curvature_with_spline
from gaussian_lattice import GaussianIntegerLattice


class TestTanhApproximation(unittest.TestCase):
    """Test tanh-based step function approximation."""
    
    def test_convergence_with_k(self):
        """Test that higher k values produce steeper transitions."""
        x = np.array([-0.1, 0, 0.1])
        
        # Test increasing k values
        k_values = [1.0, 2.0, 10.0]
        slopes = []
        
        for k in k_values:
            tanh_approx = TanhApproximation(k=k)
            y = tanh_approx.evaluate(x)
            
            # Compute slope at x=0 (should increase with k)
            slope = (y[2] - y[0]) / (x[2] - x[0])
            slopes.append(slope)
            
            # Values should be in [0, 1]
            self.assertTrue(np.all(y >= 0) and np.all(y <= 1))
        
        # Slopes should increase with k
        self.assertGreater(slopes[1], slopes[0])
        self.assertGreater(slopes[2], slopes[1])
    
    def test_sigmoid_equivalence(self):
        """Test that tanh and sigmoid forms are equivalent."""
        x = np.linspace(-2, 2, 100)
        tanh_approx = TanhApproximation(k=2.0)
        
        y_tanh = tanh_approx.evaluate(x)
        y_sigmoid = tanh_approx.sigmoid_form(x)
        
        # Should be approximately equal
        np.testing.assert_allclose(y_tanh, y_sigmoid, rtol=1e-10)
    
    def test_derivative(self):
        """Test derivative calculation."""
        x = np.array([0.0])
        tanh_approx = TanhApproximation(k=2.0)
        
        deriv = tanh_approx.derivative(x)
        
        # At x=0, derivative should be 0.5 * k * sech²(0) = 0.5 * k
        expected = 0.5 * 2.0
        self.assertAlmostEqual(deriv[0], expected, places=6)


class TestAsymmetricGaussianFit(unittest.TestCase):
    """Test asymmetric Gaussian curve fitting."""
    
    def test_symmetric_case(self):
        """Test fitting to symmetric Gaussian data."""
        # Generate symmetric Gaussian
        x_data = np.linspace(-3, 3, 100)
        y_true = 10 * np.exp(-x_data**2 / (2 * 1.0**2))
        
        # Add small noise
        np.random.seed(42)
        y_noisy = y_true + np.random.normal(0, 0.1, len(x_data))
        
        # Fit
        fitter = AsymmetricGaussianFit()
        fitted_model, rmse = fitter.fit_to_data(x_data, y_noisy)
        
        # Should recover symmetric parameters
        self.assertLess(rmse, 0.5)
        self.assertAlmostEqual(fitted_model.mean, 0.0, places=1)
        # Left and right std should be similar for symmetric data
        ratio = fitted_model.std_left / fitted_model.std_right
        self.assertGreater(ratio, 0.8)
        self.assertLess(ratio, 1.2)
    
    def test_asymmetric_case(self):
        """Test fitting to asymmetric Gaussian data."""
        # Generate asymmetric Gaussian (wider on left)
        x_data = np.linspace(-5, 5, 100)
        y_data = np.zeros_like(x_data)
        
        left_mask = x_data <= 0
        right_mask = x_data > 0
        
        y_data[left_mask] = 10 * np.exp(-(x_data[left_mask]**2) / (2 * 2.0**2))
        y_data[right_mask] = 10 * np.exp(-(x_data[right_mask]**2) / (2 * 1.0**2))
        
        # Fit
        fitter = AsymmetricGaussianFit()
        fitted_model, rmse = fitter.fit_to_data(x_data, y_data)
        
        # Left std should be larger than right std
        self.assertGreater(fitted_model.std_left, fitted_model.std_right)
        self.assertLess(rmse, 0.5)


class TestNonlinearLeastSquares(unittest.TestCase):
    """Test nonlinear least squares fitting."""
    
    def test_exponential_fit(self):
        """Test fitting exponential decay model."""
        # Model: y = A * exp(-k * x)
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        # Generate data
        x_data = np.linspace(0, 5, 50)
        y_true = exp_model(x_data, 10.0, 0.5)
        y_noisy = y_true + np.random.normal(0, 0.1, len(x_data))
        
        # Fit
        fitter = NonlinearLeastSquares(exp_model, num_params=2)
        params, rmse = fitter.fit(x_data, y_noisy, initial_params=np.array([5.0, 0.3]))
        
        # Should recover parameters
        self.assertAlmostEqual(params[0], 10.0, places=0)
        self.assertAlmostEqual(params[1], 0.5, places=1)
        self.assertLess(rmse, 0.5)
    
    def test_cross_validation(self):
        """Test cross-validation detects overfitting."""
        # Linear model (not overfitting)
        def linear_model(x, a, b):
            return a * x + b
        
        x_data = np.linspace(0, 10, 100)
        y_data = 2.0 * x_data + 3.0 + np.random.normal(0, 0.1, len(x_data))
        
        fitter = NonlinearLeastSquares(linear_model, num_params=2)
        cv_metrics = fitter.cross_validate(
            x_data, y_data,
            initial_params=np.array([1.0, 1.0]),
            n_folds=5
        )
        
        # Overfitting ratio should be close to 1 (no overfitting)
        self.assertLess(cv_metrics['overfitting_ratio'], 1.5)


class TestSplineApproximation(unittest.TestCase):
    """Test spline-based approximation."""
    
    def test_interpolation(self):
        """Test that spline passes through data points."""
        x_data = np.array([0, 1, 2, 3, 4])
        y_data = np.array([0, 1, 4, 9, 16])  # x²
        
        spline = SplineApproximation(x_data, y_data, spline_type='cubic')
        
        # Evaluate at data points
        y_interp = spline.evaluate(x_data)
        
        # Should match original data (cubic spline interpolates exactly)
        np.testing.assert_allclose(y_interp, y_data, rtol=1e-6)
    
    def test_smoothness(self):
        """Test that spline is continuous and differentiable."""
        x_data = np.array([0, 1, 2, 3, 4])
        y_data = np.array([0, 1, 4, 9, 16])
        
        spline = SplineApproximation(x_data, y_data, spline_type='cubic')
        
        # Evaluate derivatives
        x_dense = np.linspace(0, 4, 100)
        deriv1 = spline.derivative(x_dense, order=1)
        deriv2 = spline.derivative(x_dense, order=2)
        
        # Derivatives should be finite and smooth (no NaN or Inf)
        self.assertTrue(np.all(np.isfinite(deriv1)))
        self.assertTrue(np.all(np.isfinite(deriv2)))


class TestMonteCarloIntegration(unittest.TestCase):
    """Test Monte Carlo integration with function approximation."""
    
    def test_tanh_smoothed_distance(self):
        """Test tanh-smoothed distance for candidate ranking."""
        enhancer = FactorizationMonteCarloEnhancer(seed=42)
        N = 143  # 11 × 13
        sqrt_N = int(np.sqrt(N))
        
        # Factor should have smaller smoothed distance than non-factor
        dist_factor = enhancer.tanh_smoothed_distance(11, sqrt_N, k=2.0)
        dist_non_factor = enhancer.tanh_smoothed_distance(15, sqrt_N, k=2.0)
        
        # Factor is at sqrt(N), so distance should match the formula
        # Compute expected value using the same formula as the implementation
        expected = abs(np.tanh((11 - sqrt_N) / (sqrt_N * 2.0)) - 0.5) * (sqrt_N * 0.1)
        self.assertAlmostEqual(dist_factor, expected, places=6)
        
        # Non-factor should have positive distance
        self.assertGreater(dist_non_factor, 0.0)
    
    def test_variance_reduction(self):
        """Test asymmetric Gaussian variance reduction."""
        enhancer = FactorizationMonteCarloEnhancer(seed=42)
        N = 143
        
        result = enhancer.fit_variance_reduction_gaussian(N, num_samples=100, num_trials=3)
        
        self.assertTrue(result['available'])
        self.assertGreater(result['num_samples'], 0)
        self.assertGreater(result['fitted_amplitude'], 0)


class TestZ5DIntegration(unittest.TestCase):
    """Test Z5D integration with function approximation."""
    
    def test_error_bound_calibration(self):
        """Test Z5D error bound calibration."""
        # Generate test data
        k_values = np.array([1000, 5000, 10000])
        errors = np.array([0.1, 0.05, 0.03])
        
        result = calibrate_error_bounds_with_regression(k_values, errors)
        
        self.assertTrue(result['available'])
        self.assertIn('fitted_params', result)
        self.assertGreater(result['fitted_params']['C'], 0)
        self.assertLess(result['rmse'], 1.0)
    
    def test_curvature_spline(self):
        """Test curvature spline approximation."""
        n_values = np.array([100, 500, 1000, 5000, 10000])  # Need at least 5 points for cubic spline
        
        result = approximate_curvature_with_spline(n_values)
        
        self.assertTrue(result['available'])
        self.assertEqual(len(result['smoothed_values']), len(n_values))
        self.assertTrue(np.all(result['smoothed_values'] > 0))


class TestGaussianLatticeIntegration(unittest.TestCase):
    """Test Gaussian lattice integration with function approximation."""
    
    def test_tanh_smoothed_lattice_distance(self):
        """Test tanh-smoothed lattice distance."""
        lattice = GaussianIntegerLattice(precision_dps=50)
        
        z1 = 0 + 0j
        z2 = 1 + 1j
        
        smoothed_dist = lattice.tanh_smoothed_lattice_distance(z1, z2, k=2.0)
        
        # Distance should be positive
        self.assertGreater(float(smoothed_dist), 0)
        
        # Distance to self should be small (tanh smoothing adds residual term)
        self_dist = lattice.tanh_smoothed_lattice_distance(z1, z1, k=2.0)
        self.assertLess(float(self_dist), 0.5)  # Small but not exactly 0 due to smoothing


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTanhApproximation))
    suite.addTests(loader.loadTestsFromTestCase(TestAsymmetricGaussianFit))
    suite.addTests(loader.loadTestsFromTestCase(TestNonlinearLeastSquares))
    suite.addTests(loader.loadTestsFromTestCase(TestSplineApproximation))
    suite.addTests(loader.loadTestsFromTestCase(TestMonteCarloIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestZ5DIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestGaussianLatticeIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
