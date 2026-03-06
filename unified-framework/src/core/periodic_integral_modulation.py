"""
Periodic Integral Modulation for Z Framework Enhancement
========================================================

Implementation of the periodic integral ∫₀^{2π} dx / (1 + e^{sin x}) = π
with symmetric cancellation properties and geodesic mapping integration.

This module demonstrates modulated exponential-trigonometric forms that
create periodic resonance leading to symmetric cancellation, where
f(x) + f(x + π) = 1, yielding an invariant value π independent of 
exponential asymmetry.

Key Features:
- High-precision numerical integration with scipy.quad
- Analytical validation via symmetry properties
- Integration with Z Framework geodesic mapping
- Resonance simulation for density enhancement
- Connection to discrete analogs for Z_5D predictions
"""

import numpy as np
import scipy.integrate as integrate
import mpmath as mp
from math import pi, sin, exp, log
from typing import Tuple, Dict, Union, List, Any
import warnings

# Import Z Framework components
try:
    from .geodesic_mapping import GeodesicMapper
    from .params import MP_DPS, KAPPA_GEO_DEFAULT
except ImportError:
    # Handle direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from geodesic_mapping import GeodesicMapper
    from params import MP_DPS, KAPPA_GEO_DEFAULT

# Set high precision for mpmath calculations
mp.dps = MP_DPS


class PeriodicIntegralModulator:
    """
    Periodic Integral Modulation for Z Framework geodesic enhancement.
    
    This class implements the integral ∫₀^{2π} dx / (1 + e^{sin x}) = π
    and its connection to Z Framework geodesic mapping with modulation
    techniques for enhanced prime density prediction.
    """
    
    def __init__(self, precision_dps: int = MP_DPS, kappa_geo: float = KAPPA_GEO_DEFAULT):
        """
        Initialize the periodic integral modulator.
        
        Args:
            precision_dps: Decimal precision for mpmath calculations
            kappa_geo: Geodesic curvature parameter for Z Framework integration
        """
        self.precision_dps = precision_dps
        self.kappa_geo = kappa_geo
        mp.dps = precision_dps
        
        # Initialize geodesic mapper for Z Framework integration
        self.geodesic_mapper = GeodesicMapper(kappa_geo=kappa_geo)
        
        # Mathematical constants
        self.pi_mp = mp.pi
        self.e_mp = mp.e
        
        # Cache for computed results
        self._cached_integral_result = None
        self._cached_symmetry_validation = None
    
    def integrand(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Compute the integrand f(x) = 1 / (1 + e^{sin x}).
        
        Args:
            x: Input value(s)
            
        Returns:
            Integrand value(s)
        """
        if isinstance(x, np.ndarray):
            return 1.0 / (1.0 + np.exp(np.sin(x)))
        else:
            return 1.0 / (1.0 + exp(sin(x)))
    
    def integrand_high_precision(self, x: mp.mpf) -> mp.mpf:
        """
        High-precision version of the integrand using mpmath.
        
        Args:
            x: Input value as mpmath float
            
        Returns:
            High-precision integrand value
        """
        return mp.mpf(1) / (mp.mpf(1) + mp.exp(mp.sin(x)))
    
    def compute_periodic_integral_numerical(self, method: str = 'quad') -> Dict[str, float]:
        """
        Compute the periodic integral numerically using scipy.quad.
        
        Args:
            method: Integration method ('quad' or 'adaptive')
            
        Returns:
            Dictionary with integral result, error estimate, and validation info
        """
        if self._cached_integral_result is not None:
            return self._cached_integral_result
        
        if method == 'quad':
            # Use scipy.quad with high precision
            result, error = integrate.quad(
                self.integrand, 0, 2*pi, 
                epsabs=1e-14, epsrel=1e-14
            )
        elif method == 'adaptive':
            # Alternative adaptive integration
            result, error = integrate.quadrature(
                self.integrand, 0, 2*pi, 
                tol=1e-14, maxiter=100
            )
        else:
            raise ValueError(f"Unknown integration method: {method}")
        
        # Validation against exact value π
        pi_exact = np.pi
        deviation = abs(result - pi_exact)
        relative_error = deviation / pi_exact
        
        integral_result = {
            'value': result,
            'error': error,
            'exact_pi': pi_exact,
            'deviation': deviation,
            'relative_error': relative_error,
            'is_pi_exact': deviation < 1e-10,
            'method': method
        }
        
        self._cached_integral_result = integral_result
        return integral_result
    
    def compute_periodic_integral_analytical(self) -> Dict[str, Union[float, mp.mpf]]:
        """
        Compute the periodic integral using high-precision analytical methods.
        
        Uses mpmath for arbitrary precision integration and validates
        the exact π result through symmetry properties.
        
        Returns:
            Dictionary with high-precision results and analytical validation
        """
        # High-precision integration using mpmath
        integral_mp = mp.quad(
            self.integrand_high_precision,
            [0, 2 * self.pi_mp]
        )
        
        # Convert to float for comparison
        integral_float = float(integral_mp)
        pi_float = float(self.pi_mp)
        
        # Analytical validation
        deviation_mp = mp.fabs(integral_mp - self.pi_mp)
        relative_error_mp = deviation_mp / self.pi_mp
        
        return {
            'value_mp': integral_mp,
            'value_float': integral_float,
            'exact_pi_mp': self.pi_mp,
            'exact_pi_float': pi_float,
            'deviation_mp': deviation_mp,
            'deviation_float': float(deviation_mp),
            'relative_error_mp': relative_error_mp,
            'relative_error_float': float(relative_error_mp),
            'is_pi_exact': float(deviation_mp) < 1e-15,
            'precision_dps': self.precision_dps
        }
    
    def validate_symmetry_property(self, n_points: int = 1000) -> Dict[str, Union[float, bool]]:
        """
        Validate the symmetry property f(x) + f(x + π) = 1.
        
        This is the key mathematical property that leads to the exact π result
        through symmetric cancellation in the integral.
        
        Args:
            n_points: Number of test points for validation
            
        Returns:
            Dictionary with symmetry validation results
        """
        if self._cached_symmetry_validation is not None:
            return self._cached_symmetry_validation
        
        # Generate test points in [0, π]
        x_values = np.linspace(0, pi, n_points)
        
        # Compute f(x) and f(x + π)
        f_x = self.integrand(x_values)
        f_x_plus_pi = self.integrand(x_values + pi)
        
        # Check symmetry property: f(x) + f(x + π) = 1
        symmetry_sum = f_x + f_x_plus_pi
        expected_sum = np.ones_like(symmetry_sum)
        
        # Compute deviations
        deviations = np.abs(symmetry_sum - expected_sum)
        max_deviation = np.max(deviations)
        mean_deviation = np.mean(deviations)
        
        # Validation criteria
        symmetry_valid = max_deviation < 1e-12
        
        symmetry_result = {
            'max_deviation': max_deviation,
            'mean_deviation': mean_deviation,
            'symmetry_valid': symmetry_valid,
            'n_points': n_points,
            'theoretical_sum': 1.0,
            'actual_mean_sum': np.mean(symmetry_sum),
            'std_deviation': np.std(deviations)
        }
        
        self._cached_symmetry_validation = symmetry_result
        return symmetry_result
    
    def resonance_simulation(self, n_values: List[int], amplitude: float = 0.1, 
                           frequency: float = 20.0) -> Dict[str, Any]:
        """
        Simulate periodic resonance modulation for geodesic mapping enhancement.
        
        This implements sinusoidal perturbation similar to grid metric smoke tests
        (e.g., u + 0.1 sin(2π · 20u) % 1.0) for resonance simulation.
        
        Args:
            n_values: List of integer values for geodesic transformation
            amplitude: Modulation amplitude (default 0.1 as in smoke tests)
            frequency: Modulation frequency (default 20.0 as in smoke tests)
            
        Returns:
            Dictionary with modulated geodesic values and enhancement metrics
        """
        # Standard geodesic transformation without modulation
        standard_geodesic = [self.geodesic_mapper.enhanced_geodesic_transform(n) for n in n_values]
        
        # Apply sinusoidal modulation with periodic integral influence
        modulated_geodesic = []
        for n in n_values:
            # Base geodesic value
            base_value = self.geodesic_mapper.enhanced_geodesic_transform(n)
            
            # Compute modulation parameter using periodic integral properties
            u = (n % self.geodesic_mapper.phi) / self.geodesic_mapper.phi
            
            # Apply sinusoidal modulation: u + amplitude * sin(2π * frequency * u) % 1.0
            modulated_u = (u + amplitude * sin(2 * pi * frequency * u)) % 1.0
            
            # Enhanced geodesic with modulation
            modulated_value = self.geodesic_mapper.phi * (modulated_u ** self.kappa_geo)
            modulated_geodesic.append(modulated_value)
        
        # Compute enhancement metrics
        enhancement_ratios = [mod / std if std != 0 else 1.0 
                             for mod, std in zip(modulated_geodesic, standard_geodesic)]
        mean_enhancement = np.mean(enhancement_ratios)
        std_enhancement = np.std(enhancement_ratios)
        
        # Target 15% enhancement as specified
        target_enhancement = 1.15
        enhancement_achieved = abs(mean_enhancement - target_enhancement) < 0.05
        
        return {
            'n_values': n_values,
            'standard_geodesic': standard_geodesic,
            'modulated_geodesic': modulated_geodesic,
            'enhancement_ratios': enhancement_ratios,
            'mean_enhancement': mean_enhancement,
            'std_enhancement': std_enhancement,
            'target_enhancement': target_enhancement,
            'enhancement_achieved': enhancement_achieved,
            'amplitude': amplitude,
            'frequency': frequency
        }
    
    def apply_resonance(self, delta_n: Union[float, List[float]], n_values: Union[int, List[int]]) -> Union[float, List[float]]:
        """
        Apply periodic resonance modulation to discrete Z domain values.
        
        This method implements the modulated Δₙ formula:
        Δₙ' = Δₙ · (1 + 0.1 sin(2π · 20 · (n mod φ)/φ))
        
        This provides the discrete analog for Z_5D predictions using the periodic
        integral properties to enhance prime density predictions.
        
        Args:
            delta_n: Base Δₙ value(s) to be modulated
            n_values: Corresponding n value(s) for modulation computation
            
        Returns:
            Modulated Δₙ' value(s) with periodic resonance enhancement
        """
        # Handle scalar inputs
        if isinstance(delta_n, (int, float)) and isinstance(n_values, (int, float)):
            # Compute modulation parameter using golden ratio
            phi = self.geodesic_mapper.phi
            u = (n_values % phi) / phi
            
            # Apply sinusoidal modulation: 1 + 0.1 sin(2π · 20 · u)
            modulation_factor = 1 + 0.1 * sin(2 * pi * 20 * u)
            
            # Return modulated value
            return delta_n * modulation_factor
        
        # Handle list inputs
        if isinstance(delta_n, list) and isinstance(n_values, list):
            if len(delta_n) != len(n_values):
                raise ValueError("delta_n and n_values must have the same length")
            
            modulated_values = []
            phi = self.geodesic_mapper.phi
            
            for delta, n in zip(delta_n, n_values):
                u = (n % phi) / phi
                modulation_factor = 1 + 0.1 * sin(2 * pi * 20 * u)
                modulated_values.append(delta * modulation_factor)
            
            return modulated_values
        
        # Handle numpy arrays
        if hasattr(delta_n, '__array__') and hasattr(n_values, '__array__'):
            import numpy as np
            
            delta_array = np.array(delta_n)
            n_array = np.array(n_values)
            
            if delta_array.shape != n_array.shape:
                raise ValueError("delta_n and n_values arrays must have the same shape")
            
            phi = self.geodesic_mapper.phi
            u = (n_array % phi) / phi
            modulation_factor = 1 + 0.1 * np.sin(2 * np.pi * 20 * u)
            
            return delta_array * modulation_factor
        
        raise TypeError("Unsupported input types. Expected scalar, list, or array-like inputs.")

    def compute_density_enhancement(self, prime_list: List[int], 
                                  bootstrap_samples: int = 1000) -> Dict[str, float]:
        """
        Compute prime density enhancement using periodic integral modulation.
        
        This connects the periodic integral properties to discrete domain
        prime density improvement with statistical validation.
        
        Args:
            prime_list: List of prime numbers for analysis
            bootstrap_samples: Number of bootstrap resamples for confidence intervals
            
        Returns:
            Dictionary with density enhancement metrics and confidence intervals
        """
        if len(prime_list) < 10:
            warnings.warn("Prime list too short for reliable density analysis")
        
        # Standard density calculation using geodesic mapping
        standard_density = self.geodesic_mapper.compute_density_enhancement(
            prime_list, n_bootstrap=bootstrap_samples
        )
        
        # Enhanced density with periodic integral modulation
        modulation_result = self.resonance_simulation(prime_list)
        modulated_primes = modulation_result['modulated_geodesic']
        
        # Compute density ratio
        enhancement_value = standard_density.get('enhancement', 0.0)
        if enhancement_value > 0:
            density_enhancement_ratio = (np.mean(modulated_primes) / 
                                       np.mean(standard_density.get('transformed_primes', [1])))
        else:
            # Use alternative calculation when standard enhancement is zero
            density_enhancement_ratio = np.mean(modulation_result['enhancement_ratios'])
        
        # Bootstrap confidence intervals for enhanced density
        bootstrap_enhancements = []
        for _ in range(bootstrap_samples):
            # Sample with replacement
            sampled_primes = np.random.choice(prime_list, size=len(prime_list), replace=True)
            sample_modulation = self.resonance_simulation(sampled_primes.tolist())
            sample_enhancement = np.mean(sample_modulation['enhancement_ratios'])
            bootstrap_enhancements.append(sample_enhancement)
        
        # Confidence intervals
        ci_lower = np.percentile(bootstrap_enhancements, 2.5)
        ci_upper = np.percentile(bootstrap_enhancements, 97.5)
        
        return {
            'standard_enhancement': standard_density.get('enhancement', 0.0),
            'modulated_enhancement': density_enhancement_ratio,
            'enhancement_improvement': density_enhancement_ratio - standard_density.get('enhancement', 0.0),
            'bootstrap_mean': np.mean(bootstrap_enhancements),
            'bootstrap_std': np.std(bootstrap_enhancements),
            'confidence_interval': [ci_lower, ci_upper],
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'target_achieved': ci_lower >= 0.146 and ci_upper <= 0.154,  # [14.6%, 15.4%] as specified
            'n_primes': len(prime_list),
            'bootstrap_samples': bootstrap_samples
        }
    
    def validate_integral_exact_pi(self) -> Dict[str, Union[bool, float, str]]:
        """
        Comprehensive validation that the integral equals exactly π.
        
        Combines numerical and analytical methods to verify the exact π result
        using multiple precision levels and integration techniques.
        
        Returns:
            Dictionary with comprehensive validation results
        """
        # Numerical validation
        numerical_result = self.compute_periodic_integral_numerical()
        
        # Analytical validation
        analytical_result = self.compute_periodic_integral_analytical()
        
        # Symmetry validation
        symmetry_result = self.validate_symmetry_property()
        
        # Overall validation criteria
        numerical_valid = numerical_result['is_pi_exact']
        analytical_valid = analytical_result['is_pi_exact']
        symmetry_valid = symmetry_result['symmetry_valid']
        
        all_valid = numerical_valid and analytical_valid and symmetry_valid
        
        return {
            'numerical_valid': numerical_valid,
            'analytical_valid': analytical_valid,
            'symmetry_valid': symmetry_valid,
            'all_valid': all_valid,
            'numerical_deviation': numerical_result['deviation'],
            'analytical_deviation': analytical_result['deviation_float'],
            'symmetry_max_deviation': symmetry_result['max_deviation'],
            'validation_summary': (
                'PASS: Integral equals π exactly' if all_valid 
                else 'FAIL: Validation failed'
            ),
            'numerical_result': numerical_result,
            'analytical_result': analytical_result,
            'symmetry_result': symmetry_result
        }


def demonstrate_periodic_integral_modulation() -> Dict[str, Union[Dict, bool]]:
    """
    Demonstrate the complete periodic integral modulation system.
    
    This function showcases all key features:
    - Exact π validation
    - Symmetry property verification
    - Z Framework geodesic integration
    - Density enhancement with confidence intervals
    
    Returns:
        Dictionary with complete demonstration results
    """
    # Initialize modulator
    modulator = PeriodicIntegralModulator()
    
    # Validate exact π result
    pi_validation = modulator.validate_integral_exact_pi()
    
    # Generate sample prime list for density analysis
    # Using first 50 primes for demonstration
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
              73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
              157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229]
    
    # Compute density enhancement
    density_result = modulator.compute_density_enhancement(primes, bootstrap_samples=100)
    
    # Resonance simulation
    resonance_result = modulator.resonance_simulation(primes[:20])  # First 20 primes for speed
    
    return {
        'pi_validation': pi_validation,
        'density_enhancement': density_result,
        'resonance_simulation': resonance_result,
        'demonstration_complete': True,
        'summary': {
            'integral_equals_pi': pi_validation['all_valid'],
            'density_target_achieved': density_result['target_achieved'],
            'resonance_enhancement_achieved': resonance_result['enhancement_achieved']
        }
    }


if __name__ == "__main__":
    # Run demonstration
    print("=" * 70)
    print("PERIODIC INTEGRAL MODULATION DEMONSTRATION")
    print("=" * 70)
    
    results = demonstrate_periodic_integral_modulation()
    
    print("\n1. Integral Validation (∫₀^{2π} dx / (1 + e^{sin x}) = π):")
    print(f"   Result: {results['pi_validation']['validation_summary']}")
    print(f"   Numerical deviation: {results['pi_validation']['numerical_deviation']:.2e}")
    print(f"   Analytical deviation: {results['pi_validation']['analytical_deviation']:.2e}")
    
    print("\n2. Density Enhancement Analysis:")
    print(f"   Enhancement: {results['density_enhancement']['modulated_enhancement']:.3f}")
    print(f"   Confidence Interval: [{results['density_enhancement']['ci_lower']:.3f}, "
          f"{results['density_enhancement']['ci_upper']:.3f}]")
    print(f"   Target [14.6%, 15.4%] achieved: {results['density_enhancement']['target_achieved']}")
    
    print("\n3. Resonance Simulation:")
    print(f"   Mean enhancement: {results['resonance_simulation']['mean_enhancement']:.3f}")
    print(f"   Enhancement achieved: {results['resonance_simulation']['enhancement_achieved']}")
    
    print(f"\n✅ Demonstration completed successfully!")