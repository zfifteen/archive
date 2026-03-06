#!/usr/bin/env python3
"""
Function Approximation Module

Implements function approximation techniques for simplifying complex models in
geometric factorization and Monte Carlo sampling, following the educational
framework by Joachim Schork from Statistics Globe.

Core Concepts:
1. Tanh-based step function approximations for smoothing discontinuities
2. Asymmetric Gaussian curve fitting for noisy data regression
3. Nonlinear least squares for error bound calibration
4. Spline-based smooth approximations for curvature functions

Benefits:
- Simplifies complex models for easier interpretation
- Improves prediction accuracy through better generalization
- Reduces computational cost by avoiding exact calculations
- Provides error control via least squares minimization
- Enables flexible approximation methods for diverse data

Applications to z-sandbox:
- Tanh smoothing for discontinuous distance metrics in lattice embeddings
- Asymmetric Gaussian fits for RQMC sampling noise reduction
- Nonlinear least squares for Z5D error bound calibration
- Spline approximations for geometric curvature in GVA

Mathematical Foundations:
- Tanh approximation: f(x) = 0.5 + 0.5 * tanh(kx) = 1/(1 + exp(-2kx))
  Higher k → steeper transition, better step function approximation
- Asymmetric Gaussian: f(x) = A * exp(-((x-μ)²)/(2σ²)) with left/right σ
  Captures skewed distributions common in sampling data
- Least squares: min Σ(y_i - f(x_i))² for optimal parameter fitting
  
References:
- Statistics Globe educational post on function approximation
- Wikipedia: Function approximation theory
- SciPy/NumPy documentation for curve fitting
"""

import math
import numpy as np
from typing import Tuple, List, Optional, Callable, Dict, Any
from scipy.optimize import curve_fit, minimize
from scipy.interpolate import UnivariateSpline, CubicSpline
from mpmath import mp, mpf, log as mp_log, exp as mp_exp, tanh as mp_tanh

# Set precision for high-accuracy approximations
mp.dps = 50


class TanhApproximation:
    """
    Tanh-based step function approximation.
    
    Implements the hyperbolic tangent approximation of discontinuous step functions,
    providing smooth transitions that improve with higher steepness parameters.
    
    Formula: f(x; k) = 0.5 + 0.5 * tanh(kx) = 1/(1 + exp(-2kx))
    
    Properties:
    - k=1: Gentle slope, gradual transition
    - k=2: Steeper slope, faster transition
    - k=10: Nearly vertical, close to ideal step function
    - As k→∞: Approaches sign(x) step function
    
    Applications:
    - Smooth discontinuous distance metrics in Gaussian lattices
    - Neural network activation functions
    - Signal processing edge detection
    - Geometric filtering with smooth cutoffs
    """
    
    def __init__(self, k: float = 1.0):
        """
        Initialize tanh approximation.
        
        Args:
            k: Steepness parameter (higher k → steeper transition)
        """
        self.k = k
    
    def evaluate(self, x: np.ndarray) -> np.ndarray:
        """
        Evaluate tanh approximation at given points.
        
        Args:
            x: Input values
            
        Returns:
            Approximated values in [-1, 1] or [0, 1] range
        """
        return 0.5 + 0.5 * np.tanh(self.k * x)
    
    def sigmoid_form(self, x: np.ndarray) -> np.ndarray:
        """
        Evaluate using sigmoid form: 1/(1 + exp(-2kx))
        
        This is numerically equivalent to the tanh form but may have
        better stability for extreme values.
        
        Args:
            x: Input values
            
        Returns:
            Approximated values in [0, 1]
        """
        return 1.0 / (1.0 + np.exp(-2.0 * self.k * x))
    
    def derivative(self, x: np.ndarray) -> np.ndarray:
        """
        Compute derivative of tanh approximation.
        
        d/dx[0.5 + 0.5*tanh(kx)] = 0.5k*sech²(kx) = 0.5k*(1 - tanh²(kx))
        
        Args:
            x: Input values
            
        Returns:
            Derivative values
        """
        tanh_kx = np.tanh(self.k * x)
        return 0.5 * self.k * (1.0 - tanh_kx**2)
    
    def fit_to_step(self, x_data: np.ndarray, y_data: np.ndarray, 
                    initial_k: float = 1.0) -> Tuple[float, float]:
        """
        Fit tanh approximation to step function data.
        
        Estimates optimal k parameter to match given step-like data.
        
        Args:
            x_data: Input x values
            y_data: Target step function values
            initial_k: Initial guess for k parameter
            
        Returns:
            (optimal_k, fit_error)
        """
        def tanh_model(x, k):
            return 0.5 + 0.5 * np.tanh(k * x)
        
        try:
            popt, _ = curve_fit(tanh_model, x_data, y_data, p0=[initial_k])
            optimal_k = popt[0]
            
            # Compute fit error
            y_pred = tanh_model(x_data, optimal_k)
            error = np.sqrt(np.mean((y_data - y_pred)**2))
            
            return optimal_k, error
        except Exception as e:
            # Return initial k if fitting fails
            return initial_k, float('inf')


class AsymmetricGaussianFit:
    """
    Asymmetric (skewed) Gaussian curve fitting for noisy data.
    
    Fits an asymmetric Gaussian distribution to data with different left/right
    standard deviations, capturing skewness common in real-world sampling data.
    
    Formula:
    - Left side (x ≤ μ): f(x) = A * exp(-((x-μ)²)/(2σ_left²))
    - Right side (x > μ): f(x) = A * exp(-((x-μ)²)/(2σ_right²))
    
    Parameters:
    - A: Amplitude (peak height)
    - μ: Mean (peak location)
    - σ_left: Left standard deviation
    - σ_right: Right standard deviation
    
    Applications:
    - Fitting noisy RQMC sampling distributions
    - Modeling asymmetric error distributions
    - Variance reduction via error minimization
    - Visual error reduction in line-intersection plots
    """
    
    def __init__(self, amplitude: float = 1.0, mean: float = 0.0,
                 std_left: float = 1.0, std_right: float = 1.0):
        """
        Initialize asymmetric Gaussian fit.
        
        Args:
            amplitude: Peak height
            mean: Peak location
            std_left: Standard deviation on left side
            std_right: Standard deviation on right side
        """
        self.amplitude = amplitude
        self.mean = mean
        self.std_left = std_left
        self.std_right = std_right
    
    def evaluate(self, x: np.ndarray) -> np.ndarray:
        """
        Evaluate asymmetric Gaussian at given points.
        
        Args:
            x: Input values
            
        Returns:
            Fitted Gaussian values
        """
        result = np.zeros_like(x, dtype=float)
        
        # Left side (x <= mean)
        left_mask = x <= self.mean
        if np.any(left_mask):
            result[left_mask] = self.amplitude * np.exp(
                -((x[left_mask] - self.mean)**2) / (2 * self.std_left**2)
            )
        
        # Right side (x > mean)
        right_mask = x > self.mean
        if np.any(right_mask):
            result[right_mask] = self.amplitude * np.exp(
                -((x[right_mask] - self.mean)**2) / (2 * self.std_right**2)
            )
        
        return result
    
    def fit_to_data(self, x_data: np.ndarray, y_data: np.ndarray,
                    initial_params: Optional[Tuple[float, float, float, float]] = None
                    ) -> Tuple['AsymmetricGaussianFit', float]:
        """
        Fit asymmetric Gaussian to noisy data using least squares.
        
        Args:
            x_data: Input x values
            y_data: Noisy y values to fit
            initial_params: Optional (amplitude, mean, std_left, std_right) guess
            
        Returns:
            (fitted_model, rmse)
        """
        def asym_gaussian_func(x, amp, mean, std_left, std_right):
            result = np.zeros_like(x, dtype=float)
            left_mask = x <= mean
            right_mask = x > mean
            
            if np.any(left_mask):
                result[left_mask] = amp * np.exp(-((x[left_mask] - mean)**2) / (2 * std_left**2))
            if np.any(right_mask):
                result[right_mask] = amp * np.exp(-((x[right_mask] - mean)**2) / (2 * std_right**2))
            
            return result
        
        # Initial parameter guess
        if initial_params is None:
            amp_guess = np.max(y_data)
            mean_guess = x_data[np.argmax(y_data)]
            std_guess = (np.max(x_data) - np.min(x_data)) / 4.0
            initial_params = (amp_guess, mean_guess, std_guess, std_guess)
        
        try:
            # Fit using curve_fit with bounds to ensure positive std devs
            bounds = ([0, -np.inf, 0, 0], [np.inf, np.inf, np.inf, np.inf])
            popt, _ = curve_fit(asym_gaussian_func, x_data, y_data, 
                              p0=initial_params, bounds=bounds, maxfev=10000)
            
            amp, mean, std_left, std_right = popt
            
            # Create fitted model
            fitted_model = AsymmetricGaussianFit(amp, mean, std_left, std_right)
            
            # Compute RMSE
            y_pred = fitted_model.evaluate(x_data)
            rmse = np.sqrt(np.mean((y_data - y_pred)**2))
            
            return fitted_model, rmse
            
        except Exception as e:
            # Return initial model if fitting fails
            fitted_model = AsymmetricGaussianFit(*initial_params)
            rmse = float('inf')
            return fitted_model, rmse


class NonlinearLeastSquares:
    """
    Nonlinear least squares fitting for error bound calibration.
    
    Implements general nonlinear least squares optimization for fitting
    arbitrary functions to data, with applications to Z5D error bound
    calibration and prime prediction refinement.
    
    Applications:
    - Z5D error bound calibration: C / (k^α * ln(k)^β * ln(ln(k))^γ)
    - Prime prediction refinement via regression
    - Cross-validation to prevent overfitting
    - Parameter estimation for geometric models
    
    Methods:
    - Levenberg-Marquardt algorithm (via scipy.optimize)
    - Trust region reflective
    - Dogleg
    """
    
    def __init__(self, model_func: Callable, num_params: int):
        """
        Initialize nonlinear least squares fitter.
        
        Args:
            model_func: Model function f(x, *params) to fit
            num_params: Number of parameters in model
        """
        self.model_func = model_func
        self.num_params = num_params
        self.fitted_params = None
        self.fit_error = None
    
    def fit(self, x_data: np.ndarray, y_data: np.ndarray,
            initial_params: np.ndarray,
            bounds: Optional[Tuple[List[float], List[float]]] = None,
            method: str = 'lm') -> Tuple[np.ndarray, float]:
        """
        Fit model to data using nonlinear least squares.
        
        Args:
            x_data: Input x values
            y_data: Target y values
            initial_params: Initial parameter guess
            bounds: Optional parameter bounds (lower, upper)
            method: Optimization method ('lm', 'trf', 'dogbox')
            
        Returns:
            (fitted_params, rmse)
        """
        try:
            if bounds is not None and method == 'lm':
                # Levenberg-Marquardt doesn't support bounds, use 'trf' instead
                method = 'trf'
            
            popt, pcov = curve_fit(
                self.model_func, x_data, y_data,
                p0=initial_params,
                bounds=bounds if bounds else (-np.inf, np.inf),
                method=method,
                maxfev=10000
            )
            
            self.fitted_params = popt
            
            # Compute RMSE
            y_pred = self.model_func(x_data, *popt)
            rmse = np.sqrt(np.mean((y_data - y_pred)**2))
            self.fit_error = rmse
            
            return popt, rmse
            
        except Exception as e:
            # Return initial params if fitting fails
            self.fitted_params = initial_params
            self.fit_error = float('inf')
            return initial_params, float('inf')
    
    def predict(self, x_new: np.ndarray) -> np.ndarray:
        """
        Predict y values at new x points using fitted model.
        
        Args:
            x_new: New x values
            
        Returns:
            Predicted y values
        """
        if self.fitted_params is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        
        return self.model_func(x_new, *self.fitted_params)
    
    def cross_validate(self, x_data: np.ndarray, y_data: np.ndarray,
                      initial_params: np.ndarray,
                      n_folds: int = 5) -> Dict[str, float]:
        """
        Perform k-fold cross-validation to detect overfitting.
        
        Args:
            x_data: Input x values
            y_data: Target y values
            initial_params: Initial parameter guess
            n_folds: Number of cross-validation folds
            
        Returns:
            Dictionary with cross-validation metrics
        """
        n = len(x_data)
        fold_size = n // n_folds
        train_errors = []
        val_errors = []
        
        for fold in range(n_folds):
            # Split data
            val_start = fold * fold_size
            val_end = val_start + fold_size if fold < n_folds - 1 else n
            
            val_indices = np.arange(val_start, val_end)
            train_indices = np.concatenate([np.arange(0, val_start), np.arange(val_end, n)])
            
            x_train = x_data[train_indices]
            y_train = y_data[train_indices]
            x_val = x_data[val_indices]
            y_val = y_data[val_indices]
            
            # Fit on training data
            params, train_error = self.fit(x_train, y_train, initial_params)
            train_errors.append(train_error)
            
            # Evaluate on validation data
            y_val_pred = self.model_func(x_val, *params)
            val_error = np.sqrt(np.mean((y_val - y_val_pred)**2))
            val_errors.append(val_error)
        
        return {
            'mean_train_error': np.mean(train_errors),
            'mean_val_error': np.mean(val_errors),
            'std_train_error': np.std(train_errors),
            'std_val_error': np.std(val_errors),
            'overfitting_ratio': np.mean(val_errors) / np.mean(train_errors) if np.mean(train_errors) > 0 else float('inf')
        }


class SplineApproximation:
    """
    Spline-based smooth approximation for curvature functions.
    
    Uses cubic or univariate splines to approximate complex curvature
    functions with smooth, differentiable representations suitable for
    geometric calculations and affine-invariant operations.
    
    Types:
    - UnivariateSpline: General smooth spline with adjustable smoothing
    - CubicSpline: Piecewise cubic with continuous second derivative
    - B-spline: Basis spline for control point-based design
    
    Applications:
    - Smooth κ(n) = d(n)·ln(n+1)/e² approximations
    - Affine-invariant barycentric operations
    - Geodesic distance metric smoothing
    - Visualization of multiplication ladders
    """
    
    def __init__(self, x_data: np.ndarray, y_data: np.ndarray,
                 spline_type: str = 'cubic', smoothing: Optional[float] = None):
        """
        Initialize spline approximation.
        
        Args:
            x_data: Known x values
            y_data: Known y values
            spline_type: 'cubic' or 'univariate'
            smoothing: Smoothing parameter (for UnivariateSpline)
        """
        self.x_data = x_data
        self.y_data = y_data
        self.spline_type = spline_type
        
        if spline_type == 'cubic':
            self.spline = CubicSpline(x_data, y_data)
        elif spline_type == 'univariate':
            s = smoothing if smoothing is not None else 0.0
            self.spline = UnivariateSpline(x_data, y_data, s=s)
        else:
            raise ValueError(f"Unknown spline type: {spline_type}")
    
    def evaluate(self, x_new: np.ndarray) -> np.ndarray:
        """
        Evaluate spline at new points.
        
        Args:
            x_new: New x values
            
        Returns:
            Interpolated y values
        """
        return self.spline(x_new)
    
    def derivative(self, x_new: np.ndarray, order: int = 1) -> np.ndarray:
        """
        Evaluate spline derivative.
        
        Args:
            x_new: New x values
            order: Derivative order (1, 2, ...)
            
        Returns:
            Derivative values
        """
        return self.spline(x_new, nu=order)
    
    def integrate(self, a: float, b: float) -> float:
        """
        Integrate spline over interval [a, b].
        
        Args:
            a: Lower bound
            b: Upper bound
            
        Returns:
            Integral value
        """
        if self.spline_type == 'univariate':
            return self.spline.integral(a, b)
        else:
            # For CubicSpline, use quadrature
            from scipy.integrate import quad
            return quad(self.spline, a, b)[0]


def demonstrate_approximations():
    """
    Demonstrate function approximation techniques matching the issue examples.
    
    Creates visualizations for:
    1. Tanh-based step function approximations (k=1, 2, 10)
    2. Asymmetric Gaussian fit to noisy data
    
    Matches the educational post examples from Joachim Schork.
    """
    import matplotlib.pyplot as plt
    
    print("=" * 70)
    print("Function Approximation Demonstration")
    print("=" * 70)
    print()
    
    # Example 1: Tanh approximations of step function
    print("1. Tanh-Based Step Function Approximations")
    print("-" * 70)
    
    x = np.linspace(-4, 4, 400)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left plot: Tanh approximations with different k values
    for k in [1, 2, 10]:
        tanh_approx = TanhApproximation(k=k)
        y = tanh_approx.evaluate(x)
        ax1.plot(x, y, label=f'k={k}', linewidth=2)
    
    ax1.axhline(0, color='black', linestyle='--', linewidth=0.5)
    ax1.axhline(1, color='black', linestyle='--', linewidth=0.5)
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_title('Tanh Approximations of Step Function')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-0.2, 1.2)
    
    print("  Formula: f(x; k) = 0.5 + 0.5 * tanh(kx)")
    print("  k=1:  Gentle slope, gradual transition")
    print("  k=2:  Steeper slope, faster transition")
    print("  k=10: Nearly vertical, close to ideal step function")
    print()
    
    # Example 2: Asymmetric Gaussian fit to noisy data
    print("2. Asymmetric Gaussian Fit to Noisy Data")
    print("-" * 70)
    
    # Generate noisy asymmetric data
    x_data = np.linspace(-3, 3, 100)
    # True asymmetric Gaussian (peak at 0, skewed right)
    y_true_left = 10 * np.exp(-(x_data[x_data <= 0]**2) / (2 * 1.0**2))
    y_true_right = 10 * np.exp(-(x_data[x_data > 0]**2) / (2 * 0.5**2))
    y_true = np.concatenate([y_true_left, y_true_right])
    
    # Add noise
    np.random.seed(42)
    y_noisy = y_true + np.random.normal(0, 1.0, len(x_data))
    
    # Fit asymmetric Gaussian
    fitter = AsymmetricGaussianFit()
    fitted_model, rmse = fitter.fit_to_data(x_data, y_noisy)
    y_fit = fitted_model.evaluate(x_data)
    
    # Right plot: Noisy data and fitted curve
    ax2.plot(x_data, y_noisy, 'b-', alpha=0.6, label='Noisy Data', linewidth=1)
    ax2.plot(x_data, y_fit, 'r-', label='Asymmetric Gaussian Fit', linewidth=2)
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    ax2.set_title('Asymmetric Gaussian Fit to Noisy Data')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    print(f"  Fitted parameters:")
    print(f"    Amplitude: {fitted_model.amplitude:.3f}")
    print(f"    Mean: {fitted_model.mean:.3f}")
    print(f"    Std (left):  {fitted_model.std_left:.3f}")
    print(f"    Std (right): {fitted_model.std_right:.3f}")
    print(f"  RMSE: {rmse:.4f}")
    print()
    
    plt.tight_layout()
    plt.savefig('/home/runner/work/z-sandbox/z-sandbox/plots/function_approximation_demo.png', dpi=150)
    print("  Plot saved to: plots/function_approximation_demo.png")
    print()
    
    print("=" * 70)
    print("Function approximation demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_approximations()
