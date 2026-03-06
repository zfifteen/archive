"""
Discrete Domain Simulation: Z5D Prime Prediction

This module provides interactive simulation of the Z5D prime approximation with
geometric corrections. It incorporates curvature-based corrections (k* ≈ 0.04449)
and demonstrates predictive accuracy and unification with physical invariants.

Key Features:
- Interactive Z5D prime prediction with parameter variation
- Geometric correction with θ'(n, k) curvature analog
- Comparison with exact prime values using sympy
- Error analysis and accuracy validation
- Integration with existing Z Framework discrete domain tools
"""

import numpy as np
import matplotlib.pyplot as plt
import warnings
from typing import List, Dict, Union, Optional, Tuple
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from z_framework.discrete import z5d_prime, base_pnt_prime, d_term, e_term, validate_z5d_accuracy
    Z5D_AVAILABLE = True
except ImportError:
    Z5D_AVAILABLE = False
    warnings.warn("Z5D predictor not available. Using fallback implementation.")

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    warnings.warn("SymPy not available. Exact prime computation disabled.")

class Z5DPrimeSimulation:
    """
    Interactive simulation for Z5D prime prediction with geometric corrections.
    
    This simulation demonstrates the Z5D predictor's superior accuracy compared to
    classical Prime Number Theorem estimators, incorporating curvature-based 
    corrections and geometric transformations.
    """
    
    def __init__(self):
        """Initialize Z5D prime simulation with default parameters."""
        
        # Default Z5D calibration parameters (from framework)
        self.default_c = -0.00247  # Dilation calibration
        self.default_k_star = 0.04449  # Curvature calibration
        
        # Geometric correction parameters
        self.phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        self.default_k_geom = 0.3  # Optimal geometric curvature exponent
        
        # Simulation parameters
        self.default_k_range = (1000, 100000)  # Default k range for testing
        self.default_k_points = [1000, 5000, 10000, 25000, 50000, 100000]
        
        # Storage for results
        self.results = {}
        self.validation_data = {}
        
    def fallback_base_pnt_prime(self, k: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Fallback Prime Number Theorem estimator when Z5D not available.
        
        Parameters
        ----------
        k : float or array
            Index values for prime estimation
            
        Returns
        -------
        float or array
            Estimated kth prime(s)
        """
        k = np.asarray(k)
        is_scalar = k.ndim == 0
        if is_scalar:
            k = k.reshape(1)
        
        result = np.zeros_like(k, dtype=float)
        mask = k >= 2
        
        if np.any(mask):
            k_valid = k[mask]
            with np.errstate(divide='ignore', invalid='ignore'):
                ln_k = np.log(k_valid)
                ln_ln_k = np.log(ln_k)
                valid_log_mask = np.isfinite(ln_ln_k) & (ln_k > 0)
                
                if np.any(valid_log_mask):
                    k_log_valid = k_valid[valid_log_mask]
                    ln_k_valid = ln_k[valid_log_mask]
                    ln_ln_k_valid = ln_ln_k[valid_log_mask]
                    
                    pnt_values = k_log_valid * (
                        ln_k_valid + ln_ln_k_valid - 1 + 
                        (ln_ln_k_valid - 2) / ln_k_valid
                    )
                    
                    temp_result = np.zeros_like(k_valid)
                    temp_result[valid_log_mask] = pnt_values
                    result[mask] = temp_result
        
        return float(result[0]) if is_scalar else result
    
    def fallback_z5d_prime(self, k: Union[float, np.ndarray], 
                          c: float = None, k_star: float = None) -> Union[float, np.ndarray]:
        """
        Fallback Z5D implementation when framework module not available.
        
        Parameters
        ----------
        k : float or array
            Index values for prime estimation
        c : float, optional
            Dilation calibration parameter
        k_star : float, optional
            Curvature calibration parameter
            
        Returns
        -------
        float or array
            Z5D predicted kth prime(s)
        """
        if c is None:
            c = self.default_c
        if k_star is None:
            k_star = self.default_k_star
        
        k = np.asarray(k)
        is_scalar = k.ndim == 0
        if is_scalar:
            k = k.reshape(1)
        
        # Base PNT estimate
        pnt_values = self.fallback_base_pnt_prime(k)
        if np.isscalar(pnt_values):
            pnt_values = np.array([pnt_values])
        
        # Dilation term: d(k) = (ln(p_PNT(k)) / e^4)^2
        e_fourth = np.e**4
        d_values = np.zeros_like(pnt_values)
        valid_pnt = pnt_values > 1
        if np.any(valid_pnt):
            with np.errstate(divide='ignore', invalid='ignore'):
                ln_pnt = np.log(pnt_values[valid_pnt])
                valid_ln = np.isfinite(ln_pnt) & (ln_pnt > 0)
                if np.any(valid_ln):
                    d_temp = (ln_pnt[valid_ln] / e_fourth) ** 2
                    d_values[valid_pnt] = np.where(valid_ln, d_temp, 0)
        
        # Curvature term: e(k) = p_PNT(k)^(-1/3)
        e_values = np.zeros_like(pnt_values)
        valid_pnt_e = (pnt_values != 0) & np.isfinite(pnt_values)
        if np.any(valid_pnt_e):
            with np.errstate(divide='ignore', invalid='ignore'):
                e_temp = np.power(pnt_values[valid_pnt_e], -1.0/3.0)
                valid_e = np.isfinite(e_temp)
                e_values[valid_pnt_e] = np.where(valid_e, e_temp, 0)
        
        # Z5D formula: p_Z5D(k) = p_PNT(k) + c·d(k)·p_PNT(k) + k*·e(k)·p_PNT(k)
        z5d_values = pnt_values + c * d_values * pnt_values + k_star * e_values * pnt_values
        z5d_values = np.maximum(z5d_values, 0)  # Ensure non-negative
        
        return float(z5d_values[0]) if is_scalar else z5d_values
    
    def geometric_curvature_correction(self, n: Union[float, np.ndarray], 
                                     k: float = None) -> Union[float, np.ndarray]:
        """
        Apply geometric curvature correction θ'(n, k) = φ · {n/φ}^k.
        
        This implements the geodesic-based geometric correction mentioned in the
        Z Framework documentation for density enhancement.
        
        Parameters
        ----------
        n : float or array
            Input values (prime indices or prime values)
        k : float, optional
            Curvature exponent parameter (default: 0.3)
            
        Returns
        -------
        float or array
            Geometrically corrected values
        """
        if k is None:
            k = self.default_k_geom
        
        n = np.asarray(n)
        is_scalar = n.ndim == 0
        if is_scalar:
            n = n.reshape(1)
        
        # Apply geometric transformation: θ'(n, k) = φ · {n/φ}^k
        n_mod_phi = n % self.phi
        normalized = n_mod_phi / self.phi
        theta_prime = self.phi * (normalized ** k)
        
        return float(theta_prime[0]) if is_scalar else theta_prime
    
    def predict_primes(self, k_values: Union[List, np.ndarray],
                      c: Optional[float] = None,
                      k_star: Optional[float] = None,
                      apply_geometric_correction: bool = True,
                      k_geom: Optional[float] = None) -> Dict:
        """
        Predict nth primes using Z5D methodology with optional geometric corrections.
        
        Parameters
        ----------
        k_values : list or array
            List of k indices for prime prediction
        c : float, optional
            Dilation calibration parameter
        k_star : float, optional
            Curvature calibration parameter
        apply_geometric_correction : bool
            Whether to apply geometric curvature correction
        k_geom : float, optional
            Geometric curvature exponent
            
        Returns
        -------
        dict
            Prediction results including raw Z5D, corrected, and comparison data
        """
        k_values = np.asarray(k_values)
        
        # Use framework implementation if available, otherwise fallback
        if Z5D_AVAILABLE:
            z5d_predictions = z5d_prime(k_values, c=c, k_star=k_star, auto_calibrate=True)
            base_pnt_predictions = base_pnt_prime(k_values)
        else:
            z5d_predictions = self.fallback_z5d_prime(k_values, c=c, k_star=k_star)
            base_pnt_predictions = self.fallback_base_pnt_prime(k_values)
        
        # Apply geometric correction if requested
        if apply_geometric_correction:
            geometric_corrections = self.geometric_curvature_correction(z5d_predictions, k=k_geom)
            corrected_predictions = z5d_predictions + 0.01 * geometric_corrections  # Small correction factor
        else:
            corrected_predictions = z5d_predictions
            geometric_corrections = np.zeros_like(z5d_predictions)
        
        return {
            'k_values': k_values,
            'base_pnt': base_pnt_predictions,
            'z5d_raw': z5d_predictions,
            'geometric_corrections': geometric_corrections,
            'z5d_corrected': corrected_predictions,
            'parameters': {
                'c': c or self.default_c,
                'k_star': k_star or self.default_k_star,
                'k_geom': k_geom or self.default_k_geom,
                'geometric_applied': apply_geometric_correction
            }
        }
    
    def compute_exact_primes(self, k_values: Union[List, np.ndarray]) -> Optional[np.ndarray]:
        """
        Compute exact prime values using SymPy for comparison.
        
        Parameters
        ----------
        k_values : list or array
            List of k indices
            
        Returns
        -------
        array or None
            Exact prime values, or None if SymPy unavailable
        """
        if not SYMPY_AVAILABLE:
            warnings.warn("SymPy not available. Cannot compute exact primes.")
            return None
        
        k_values = np.asarray(k_values)
        exact_primes = []
        
        for k in k_values:
            try:
                # Limit to reasonable k values to avoid excessive computation
                if k <= 1000000:  # 1 million
                    prime = sp.ntheory.prime(int(k))
                    exact_primes.append(prime)
                else:
                    warnings.warn(f"k={k} too large for exact computation. Using approximation.")
                    exact_primes.append(0)  # Placeholder
            except Exception as e:
                warnings.warn(f"Failed to compute exact prime for k={k}: {e}")
                exact_primes.append(0)
        
        return np.array(exact_primes)
    
    def run_interactive_simulation(self, 
                                 k_values: Optional[List] = None,
                                 c: Optional[float] = None,
                                 k_star: Optional[float] = None,
                                 k_geom: Optional[float] = None,
                                 include_exact: bool = True,
                                 apply_geometric_correction: bool = True,
                                 plot: bool = True) -> Dict:
        """
        Run interactive Z5D prime prediction simulation.
        
        Parameters
        ----------
        k_values : list, optional
            List of k indices to test. Uses default if None.
        c : float, optional
            Dilation calibration parameter
        k_star : float, optional
            Curvature calibration parameter
        k_geom : float, optional
            Geometric curvature exponent
        include_exact : bool
            Whether to compute exact primes for comparison
        apply_geometric_correction : bool
            Whether to apply geometric curvature correction
        plot : bool
            Whether to generate visualization plots
            
        Returns
        -------
        dict
            Complete simulation results including predictions and error analysis
        """
        # Use default k values if not provided
        if k_values is None:
            k_values = self.default_k_points
        
        print("🔢 Z5D Prime Prediction Simulation")
        print("=" * 40)
        print(f"Testing k values: {k_values}")
        print(f"Dilation parameter c: {c or self.default_c}")
        print(f"Curvature parameter k*: {k_star or self.default_k_star}")
        print(f"Geometric correction: {'Enabled' if apply_geometric_correction else 'Disabled'}")
        if apply_geometric_correction:
            print(f"Geometric exponent k_geom: {k_geom or self.default_k_geom}")
        print()
        
        # Get Z5D predictions
        predictions = self.predict_primes(
            k_values, c=c, k_star=k_star, 
            apply_geometric_correction=apply_geometric_correction,
            k_geom=k_geom
        )
        
        # Get exact primes if requested and available
        exact_primes = None
        if include_exact:
            exact_primes = self.compute_exact_primes(k_values)
        
        # Calculate errors if exact primes available
        errors = {}
        if exact_primes is not None and np.any(exact_primes > 0):
            valid_mask = exact_primes > 0
            
            # Base PNT errors
            pnt_errors = np.abs(predictions['base_pnt'][valid_mask] - exact_primes[valid_mask]) / exact_primes[valid_mask] * 100
            
            # Z5D raw errors
            z5d_raw_errors = np.abs(predictions['z5d_raw'][valid_mask] - exact_primes[valid_mask]) / exact_primes[valid_mask] * 100
            
            # Z5D corrected errors
            z5d_corr_errors = np.abs(predictions['z5d_corrected'][valid_mask] - exact_primes[valid_mask]) / exact_primes[valid_mask] * 100
            
            errors = {
                'pnt_errors': pnt_errors,
                'z5d_raw_errors': z5d_raw_errors,
                'z5d_corrected_errors': z5d_corr_errors,
                'valid_mask': valid_mask,
                'mean_pnt_error': np.mean(pnt_errors),
                'mean_z5d_raw_error': np.mean(z5d_raw_errors),
                'mean_z5d_corrected_error': np.mean(z5d_corr_errors)
            }
        
        # Compile results
        results = {
            'predictions': predictions,
            'exact_primes': exact_primes,
            'errors': errors,
            'k_values': k_values
        }
        
        # Print summary table
        self._print_results_table(results)
        
        # Generate plots if requested
        if plot:
            self.plot_results(results)
        
        # Store results
        self.results = results
        return results
    
    def _print_results_table(self, results: Dict):
        """Print formatted results table."""
        predictions = results['predictions']
        exact_primes = results['exact_primes']
        errors = results['errors']
        k_values = results['k_values']
        
        print("📊 Prediction Results")
        print("-" * 80)
        print(f"{'k':>8} | {'Base PNT':>12} | {'Z5D Raw':>12} | {'Z5D Corr.':>12} | {'True':>12} | {'Error (%)':>10}")
        print("-" * 80)
        
        for i, k in enumerate(k_values):
            pnt_pred = predictions['base_pnt'][i]
            z5d_raw = predictions['z5d_raw'][i]
            z5d_corr = predictions['z5d_corrected'][i]
            
            if exact_primes is not None and i < len(exact_primes) and exact_primes[i] > 0:
                true_val = exact_primes[i]
                if errors and 'z5d_corrected_errors' in errors and i < len(errors['z5d_corrected_errors']):
                    error_val = errors['z5d_corrected_errors'][i]
                    error_str = f"{error_val:.4f}"
                else:
                    error_str = "N/A"
            else:
                true_val = "N/A"
                error_str = "N/A"
            
            print(f"{k:>8} | {pnt_pred:>12.2f} | {z5d_raw:>12.2f} | {z5d_corr:>12.2f} | {true_val:>12} | {error_str:>10}")
        
        print("-" * 80)
        
        if errors:
            print(f"\n📈 Error Summary:")
            print(f"  Mean Base PNT Error: {errors.get('mean_pnt_error', 'N/A'):.4f}%")
            print(f"  Mean Z5D Raw Error: {errors.get('mean_z5d_raw_error', 'N/A'):.4f}%")
            print(f"  Mean Z5D Corrected Error: {errors.get('mean_z5d_corrected_error', 'N/A'):.4f}%")
            
            if 'mean_z5d_corrected_error' in errors and 'mean_pnt_error' in errors:
                improvement = errors['mean_pnt_error'] - errors['mean_z5d_corrected_error']
                print(f"  Z5D Improvement: {improvement:.4f} percentage points")
    
    def plot_results(self, results: Optional[Dict] = None, save_plot: bool = False, filename: Optional[str] = None):
        """
        Generate visualization plots for simulation results.
        
        Parameters
        ----------
        results : dict, optional
            Results dictionary. Uses stored results if None.
        save_plot : bool
            Whether to save plot to file
        filename : str, optional
            Filename for saved plot
        """
        if results is None:
            results = self.results
        
        if not results:
            print("⚠️  No simulation results to plot. Run simulation first.")
            return
        
        predictions = results['predictions']
        exact_primes = results['exact_primes']
        errors = results['errors']
        k_values = results['k_values']
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        ax1, ax2, ax3, ax4 = axes.flatten()
        
        # Plot 1: Predictions comparison
        ax1.plot(k_values, predictions['base_pnt'], 'o-', label='Base PNT', alpha=0.7)
        ax1.plot(k_values, predictions['z5d_raw'], 's-', label='Z5D Raw', alpha=0.7)
        ax1.plot(k_values, predictions['z5d_corrected'], '^-', label='Z5D Corrected', alpha=0.7)
        
        if exact_primes is not None:
            valid_exact = exact_primes > 0
            if np.any(valid_exact):
                ax1.plot(np.array(k_values)[valid_exact], exact_primes[valid_exact], 
                        'ko-', label='Exact (SymPy)', markersize=3)
        
        ax1.set_xlabel('k (Prime Index)')
        ax1.set_ylabel('Prime Value')
        ax1.set_title('Prime Predictions Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        
        # Plot 2: Error comparison
        if errors:
            if 'pnt_errors' in errors and len(errors['pnt_errors']) > 0:
                valid_k = np.array(k_values)[errors['valid_mask']]
                ax2.plot(valid_k, errors['pnt_errors'], 'o-', label='Base PNT Error', alpha=0.7)
                ax2.plot(valid_k, errors['z5d_raw_errors'], 's-', label='Z5D Raw Error', alpha=0.7)
                ax2.plot(valid_k, errors['z5d_corrected_errors'], '^-', label='Z5D Corrected Error', alpha=0.7)
                
                ax2.set_xlabel('k (Prime Index)')
                ax2.set_ylabel('Relative Error (%)')
                ax2.set_title('Prediction Errors vs k')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                ax2.set_xscale('log')
                ax2.set_yscale('log')
            else:
                ax2.text(0.5, 0.5, 'Error data not available\n(SymPy required)', 
                        ha='center', va='center', transform=ax2.transAxes, fontsize=12)
                ax2.set_title('Prediction Errors (Not Available)')
        
        # Plot 3: Geometric corrections
        if 'geometric_corrections' in predictions:
            ax3.plot(k_values, predictions['geometric_corrections'], 'g^-', 
                    label='Geometric Corrections', alpha=0.7)
            ax3.set_xlabel('k (Prime Index)')
            ax3.set_ylabel('Correction Value')
            ax3.set_title('Geometric Curvature Corrections')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            ax3.set_xscale('log')
        
        # Plot 4: Enhancement ratios
        if exact_primes is not None and errors:
            if 'pnt_errors' in errors and 'z5d_corrected_errors' in errors:
                valid_k = np.array(k_values)[errors['valid_mask']]
                enhancement_ratios = errors['pnt_errors'] / errors['z5d_corrected_errors']
                ax4.plot(valid_k, enhancement_ratios, 'ro-', label='Z5D Enhancement Ratio', alpha=0.7)
                ax4.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='No Improvement')
                ax4.set_xlabel('k (Prime Index)')
                ax4.set_ylabel('Error Reduction Ratio')
                ax4.set_title('Z5D vs PNT Error Improvement')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
                ax4.set_xscale('log')
            else:
                ax4.text(0.5, 0.5, 'Enhancement analysis\nnot available', 
                        ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                ax4.set_title('Enhancement Analysis (Not Available)')
        
        plt.tight_layout()
        
        if save_plot:
            if filename is None:
                filename = 'z5d_prime_prediction_simulation.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"💾 Plot saved as {filename}")
        
        plt.show()
    
    def parameter_sensitivity_analysis(self, 
                                     k_test: int = 10000,
                                     c_range: Tuple[float, float] = (-0.01, 0.01),
                                     k_star_range: Tuple[float, float] = (-0.2, 0.2),
                                     n_points: int = 20) -> Dict:
        """
        Perform parameter sensitivity analysis for Z5D calibration.
        
        Parameters
        ----------
        k_test : int
            Test k value for sensitivity analysis
        c_range : tuple
            Range of c parameter values to test
        k_star_range : tuple
            Range of k_star parameter values to test
        n_points : int
            Number of points in parameter sweep
            
        Returns
        -------
        dict
            Sensitivity analysis results
        """
        print(f"🔬 Parameter Sensitivity Analysis (k = {k_test})")
        print("=" * 50)
        
        # Parameter ranges
        c_values = np.linspace(c_range[0], c_range[1], n_points)
        k_star_values = np.linspace(k_star_range[0], k_star_range[1], n_points)
        
        # Get reference exact prime if possible
        exact_prime = None
        if SYMPY_AVAILABLE and k_test <= 100000:
            try:
                exact_prime = sp.ntheory.prime(k_test)
                print(f"Reference exact prime: {exact_prime}")
            except:
                pass
        
        if exact_prime is None:
            print("Using base PNT as reference")
            if Z5D_AVAILABLE:
                exact_prime = base_pnt_prime(k_test)
            else:
                exact_prime = self.fallback_base_pnt_prime(k_test)
        
        # Parameter sweep
        sensitivity_results = {
            'c_values': c_values,
            'k_star_values': k_star_values,
            'c_sweep_errors': [],
            'k_star_sweep_errors': [],
            'reference_prime': exact_prime,
            'test_k': k_test
        }
        
        # c parameter sweep (fix k_star at default)
        print("Testing c parameter sensitivity...")
        for c in c_values:
            if Z5D_AVAILABLE:
                pred = z5d_prime(k_test, c=c, k_star=self.default_k_star)
            else:
                pred = self.fallback_z5d_prime(k_test, c=c, k_star=self.default_k_star)
            
            error = abs(pred - exact_prime) / exact_prime * 100
            sensitivity_results['c_sweep_errors'].append(error)
        
        # k_star parameter sweep (fix c at default)
        print("Testing k_star parameter sensitivity...")
        for k_star in k_star_values:
            if Z5D_AVAILABLE:
                pred = z5d_prime(k_test, c=self.default_c, k_star=k_star)
            else:
                pred = self.fallback_z5d_prime(k_test, c=self.default_c, k_star=k_star)
            
            error = abs(pred - exact_prime) / exact_prime * 100
            sensitivity_results['k_star_sweep_errors'].append(error)
        
        # Find optimal parameters
        c_errors = np.array(sensitivity_results['c_sweep_errors'])
        k_star_errors = np.array(sensitivity_results['k_star_sweep_errors'])
        
        optimal_c_idx = np.argmin(c_errors)
        optimal_k_star_idx = np.argmin(k_star_errors)
        
        sensitivity_results['optimal_c'] = c_values[optimal_c_idx]
        sensitivity_results['optimal_k_star'] = k_star_values[optimal_k_star_idx]
        sensitivity_results['min_c_error'] = c_errors[optimal_c_idx]
        sensitivity_results['min_k_star_error'] = k_star_errors[optimal_k_star_idx]
        
        print(f"\n📊 Sensitivity Results:")
        print(f"  Optimal c: {sensitivity_results['optimal_c']:.6f} (error: {sensitivity_results['min_c_error']:.4f}%)")
        print(f"  Default c: {self.default_c:.6f}")
        print(f"  Optimal k*: {sensitivity_results['optimal_k_star']:.6f} (error: {sensitivity_results['min_k_star_error']:.4f}%)")
        print(f"  Default k*: {self.default_k_star:.6f}")
        
        # Plot sensitivity curves
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        ax1.plot(c_values, c_errors, 'b-', linewidth=2)
        ax1.axvline(x=self.default_c, color='red', linestyle='--', label=f'Default c = {self.default_c}')
        ax1.axvline(x=sensitivity_results['optimal_c'], color='green', linestyle='--', label=f'Optimal c = {sensitivity_results["optimal_c"]:.6f}')
        ax1.set_xlabel('c (Dilation Parameter)')
        ax1.set_ylabel('Relative Error (%)')
        ax1.set_title('c Parameter Sensitivity')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(k_star_values, k_star_errors, 'r-', linewidth=2)
        ax2.axvline(x=self.default_k_star, color='red', linestyle='--', label=f'Default k* = {self.default_k_star}')
        ax2.axvline(x=sensitivity_results['optimal_k_star'], color='green', linestyle='--', label=f'Optimal k* = {sensitivity_results["optimal_k_star"]:.6f}')
        ax2.set_xlabel('k* (Curvature Parameter)')
        ax2.set_ylabel('Relative Error (%)')
        ax2.set_title('k* Parameter Sensitivity')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return sensitivity_results

def run_example_simulation():
    """
    Example usage of the Z5DPrimeSimulation class.
    Demonstrates typical usage patterns for engineering teams.
    """
    print("🚀 Example: Z5D Prime Prediction Simulation")
    print("=" * 50)
    
    # Initialize simulation
    sim = Z5DPrimeSimulation()
    
    # Run interactive simulation with default parameters
    results = sim.run_interactive_simulation(plot=True)
    
    # Run parameter sensitivity analysis
    sensitivity = sim.parameter_sensitivity_analysis(k_test=10000)
    
    # Print example verification as mentioned in issue
    print("\n📊 Example Verification (as mentioned in issue):")
    if results['predictions']:
        k_1000_idx = None
        k_values = results['k_values']
        for i, k in enumerate(k_values):
            if k == 1000:
                k_1000_idx = i
                break
        
        if k_1000_idx is not None:
            pred = results['predictions']['z5d_corrected'][k_1000_idx]
            if results['exact_primes'] is not None and k_1000_idx < len(results['exact_primes']):
                true_val = results['exact_primes'][k_1000_idx]
                if true_val > 0:
                    error = abs(pred - true_val) / true_val * 100
                    print(f"k=1000: Predicted={pred:.2f}, True={true_val}, Error={error:.4f}%")
                    print("(Expected low error as per Z5D framework validation)")
    
    return results, sensitivity

if __name__ == "__main__":
    # Run example when module is executed directly
    run_example_simulation()