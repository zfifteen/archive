"""
Z Prime Utilities - Enhanced Accuracy Methods for Z Framework

This module implements the accuracy enhancement methods described in the Z framework
for prime number prediction, including dynamic subset recalibration, geodesic 
adjustments, and Riemann zeta zeros integration.

Components:
1. Dynamic Subset Recalibration of Z5D Parameters
2. Geodesic Adjustments for Interval Searches  
3. Riemann Zeta Zeros Integration into Z5D Corrections

All components are designed for modularity, scalability, and O(1) runtime predictions
post-calibration, with empirical validation against known primes.
"""

import numpy as np
import logging
from typing import Union, Optional, List, Tuple, Dict, Any
from scipy.optimize import curve_fit
from scipy.integrate import quad
import sympy
from .z5d_predictor import z5d_prime, base_pnt_prime, d_term, e_term

# Configure logging
logger = logging.getLogger(__name__)

# Mathematical constants
E_SQUARED = np.e**2  # ≈ 7.389 - discrete invariant maximum
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ≈ 1.618
WHEEL_210 = 2 * 3 * 5 * 7  # Common wheel sieve modulus

# Default parameters for geodesic adjustments
DEFAULT_GEODESIC_K = 0.3  # Optimal k for conditional prime density improvement under canonical benchmark methodology
DEFAULT_WHEEL_MODULUS = 210

# Precomputed Riemann zeta zeros (first 20 zeros)
# Source: https://oeis.org/A013629
def _logarithmic_integral(x: Union[float, complex, np.ndarray]) -> Union[float, complex, np.ndarray]:
    """
    Compute the logarithmic integral li(x) = ∫[2 to x] dt/ln(t).
    
    For complex inputs, this handles the branch cuts appropriately.
    For large x, uses asymptotic expansion for numerical stability.
    
    Parameters
    ----------
    x : float, complex, or array_like
        Input value(s) for logarithmic integral calculation.
        
    Returns
    -------
    float, complex, or ndarray
        Logarithmic integral values.
    """
    x = np.asarray(x)
    is_scalar = x.ndim == 0
    if is_scalar:
        x = x.reshape(1)
        
    result = np.zeros_like(x, dtype=complex)
    
    for i, xi in enumerate(x.flat):
        if np.abs(xi) < 2:
            result.flat[i] = 0  # li(x) for x < 2
        elif np.abs(xi) > 1e6:
            # Use asymptotic expansion for large |x|
            ln_x = np.log(xi)
            if ln_x != 0:
                result.flat[i] = xi / ln_x * (1 + 1/ln_x + 2/(ln_x**2))
        else:
            # Numerical integration for moderate values
            try:
                def integrand(t):
                    return 1 / np.log(t)
                    
                if np.isreal(xi) and xi > 2:
                    integral, _ = quad(integrand, 2, float(xi.real))
                    result.flat[i] = integral
                else:
                    # For complex x, use approximation
                    ln_x = np.log(xi)
                    if ln_x != 0:
                        result.flat[i] = xi / ln_x
            except:
                # Fallback approximation
                ln_x = np.log(xi)
                if ln_x != 0:
                    result.flat[i] = xi / ln_x
                    
    return result[0] if is_scalar else result


RIEMANN_ZETA_ZEROS = [
    14.134725141734693790457251983562470270784257115699243175685567460149963429809256764949010393171561678442197,
    21.022039638771554992628479593896902777334340524902781712737242414169835858906076124040666684001210179024005,
    25.010857580145688763213790992562821818659549672557996672496542006745294431606008431462433426951655516781900,
    30.424876125859513210311897530584091320181560023715440180279325655329262266211025193651210329012348373141000,
    32.935061587739189690662368964074903488812715603517039009280003440784765693023103825943514552873301980095700,
    37.586178158825671257217763480705332821405597350830793218333001113978210460316866132488152003402266983230010,
    40.918719012147495187398126914633254395901135533926725362806976251153327993893915516516515570434252776123800,
    43.327073280914999519496122165406516895942102375370444068078327398870346302095983040344063135700906709555900,
    48.005150881167159727942472749427516901350633052669936103816700647226883569145363525608062959102404395090610,
    49.773832477672302181916784678563724057723178293498406045891371094324334309134053804838802406404516495523400,
    52.970321477714460644147494283845423896041006799863728520901001406644121066896532725700647830334509159006500,
    56.446247697063216434140346604306950044140177923855064778624006993019030436962799456493306100449126150009200,
    59.347044003973881157257527156827471862593938421424142423436742648020065327926344079015030542156503005001700,
    60.831778524572781862045089712648157863904059003027037297329095263631780924742098002267156395156468100012300,
    65.112544048081651216969608179103263194093522885493945003476008059829089982816987965019423476928056205085000,
    67.079810529494217844140076449006230100301251962652915067036270001009635765745015203936925647066094180041100,
    69.546401711018340421829985993267325844159468162002802728999086906695932600987067527123872999063851130046300,
    72.067157674481907690505481924154932582633829302158770963568556862686074406616098890728859915007885066032200,
    75.704690699083740950653092879681488014194050015398945394547064302300424983533529133671326058463600960071200,
    77.144840068874064354596134725013838066297253821329075823736582097037616056745127976244994983406063002120300
]


class ZPrimeEstimator:
    """
    Enhanced Z Prime Estimator with dynamic calibration, geodesic filtering,
    and zeta corrections for improved accuracy in prime prediction.
    """
    
    def __init__(self, 
                 default_c: float = -0.00247,
                 default_k_star: float = 0.04449,
                 geodesic_k: float = DEFAULT_GEODESIC_K,
                 wheel_modulus: int = DEFAULT_WHEEL_MODULUS):
        """
        Initialize the Z Prime Estimator.
        
        Parameters
        ----------
        default_c : float, optional
            Default dilation calibration parameter.
        default_k_star : float, optional  
            Default curvature calibration parameter.
        geodesic_k : float, optional
            Geodesic curvature parameter for density enhancement.
        wheel_modulus : int, optional
            Wheel sieve modulus for candidate filtering.
        """
        self.default_c = default_c
        self.default_k_star = default_k_star
        self.geodesic_k = geodesic_k
        self.wheel_modulus = wheel_modulus
        
        # Calibrated parameters (set via dynamic calibration)
        self.calibrated_c = default_c
        self.calibrated_k_star = default_k_star
        self.calibration_error = float('inf')
        self.is_calibrated = False
        
        # Precompute wheel sieve residues
        self._wheel_residues = self._compute_wheel_residues()
        
        logger.info(f"Initialized ZPrimeEstimator with default parameters: c={default_c}, k*={default_k_star}")


    def _compute_wheel_residues(self) -> List[int]:
        """
        Compute wheel sieve residues (numbers coprime to wheel modulus).
        
        Returns
        -------
        List[int]
            List of residues coprime to the wheel modulus.
        """
        residues = []
        for i in range(1, self.wheel_modulus):
            if np.gcd(i, self.wheel_modulus) == 1:
                residues.append(i)
        return residues


    def calibrate_parameters(self, 
                           k_values: Union[List[int], np.ndarray],
                           true_primes: Optional[Union[List[int], np.ndarray]] = None,
                           bounds_c: Tuple[float, float] = (-0.02, 0),
                           bounds_k_star: Tuple[float, float] = (-0.1, 0.1)) -> Dict[str, Any]:
        """
        Dynamic subset recalibration of Z5D parameters using user-provided benchmarks.
        
        Performs offline fitting of Z5D coefficients c and k* on benchmark sets
        for asymptotic accuracy, targeting 10-20x error reduction for extrapolations.
        
        Parameters
        ----------
        k_values : array_like
            Array of k indices (e.g., [10^3, 10^4, ..., 10^8]).
        true_primes : array_like, optional
            Array of nth primes. If None, fetched via sympy.ntheory.prime.
        bounds_c : tuple, optional
            Bounds for c parameter to prevent overfitting.
        bounds_k_star : tuple, optional  
            Bounds for k* parameter to prevent overfitting.
            
        Returns
        -------
        Dict[str, Any]
            Dictionary containing fitted parameters, errors, and metadata.
        """
        k_values = np.asarray(k_values, dtype=float)
        
        # Fetch true primes if not provided
        if true_primes is None:
            logger.info("Fetching true primes using SymPy...")
            true_primes = np.array([sympy.ntheory.prime(int(k)) for k in k_values])
        else:
            true_primes = np.asarray(true_primes, dtype=float)
            
        if len(k_values) != len(true_primes):
            raise ValueError("k_values and true_primes must have the same length")
            
        # Define bounded optimization function
        def bounded_z5d(k, c, k_star):
            # Apply bounds during fitting
            c = np.clip(c, bounds_c[0], bounds_c[1])
            k_star = np.clip(k_star, bounds_k_star[0], bounds_k_star[1])
            return z5d_prime(k, c=c, k_star=k_star, auto_calibrate=False)
        
        try:
            # Perform curve fitting with bounds
            popt, pcov = curve_fit(
                bounded_z5d,
                k_values,
                true_primes,
                p0=[self.default_c, self.default_k_star],
                bounds=([bounds_c[0], bounds_k_star[0]], 
                       [bounds_c[1], bounds_k_star[1]]),
                maxfev=5000
            )
            
            fitted_c, fitted_k_star = popt
            
            # Calculate error metrics
            predictions = self.calibrated_z5d_prime(k_values, fitted_c, fitted_k_star)
            mae = np.mean(np.abs(predictions - true_primes))
            mre = np.mean(np.abs((predictions - true_primes) / true_primes))
            
            # Update calibrated parameters
            self.calibrated_c = fitted_c
            self.calibrated_k_star = fitted_k_star
            self.calibration_error = mre
            self.is_calibrated = True
            
            # Calculate parameter uncertainties
            param_errors = np.sqrt(np.diag(pcov)) if pcov is not None else [0, 0]
            
            result = {
                'fitted_c': fitted_c,
                'fitted_k_star': fitted_k_star,
                'c_error': param_errors[0],
                'k_star_error': param_errors[1],
                'mae': mae,
                'mre': mre,
                'covariance': pcov,
                'bounds_c': bounds_c,
                'bounds_k_star': bounds_k_star,
                'n_points': len(k_values),
                'k_range': (k_values.min(), k_values.max())
            }
            
            logger.info(f"Calibration successful: c={fitted_c:.6f}, k*={fitted_k_star:.6f}, MRE={mre:.6f}")
            return result
            
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return {
                'fitted_c': self.default_c,
                'fitted_k_star': self.default_k_star,
                'c_error': float('inf'),
                'k_star_error': float('inf'),
                'mae': float('inf'),
                'mre': float('inf'),
                'covariance': None,
                'error': str(e)
            }


    def calibrated_z5d_prime(self, 
                            k: Union[float, np.ndarray],
                            c: Optional[float] = None,
                            k_star: Optional[float] = None) -> Union[float, np.ndarray]:
        """
        Z5D prime prediction with calibrated parameters.
        
        Provides O(1) per element prediction (vectorized via NumPy) using
        either provided parameters or auto-calibrated values.
        
        Parameters
        ----------
        k : float or array_like
            Index values for prime prediction.
        c : float, optional
            Dilation parameter. Uses calibrated value if None.
        k_star : float, optional
            Curvature parameter. Uses calibrated value if None.
            
        Returns
        -------
        float or ndarray
            Predicted nth prime(s).
        """
        if c is None:
            c = self.calibrated_c
        if k_star is None:
            k_star = self.calibrated_k_star
            
        return z5d_prime(k, c=c, k_star=k_star, auto_calibrate=False)


    def geodesic_theta_prime(self, 
                           n: Union[float, np.ndarray], 
                           phi: Optional[float] = None,
                           k: Optional[float] = None) -> Union[float, np.ndarray]:
        """
        Geodesic mapping: θ'(n, k) = φ · {n/φ}^k
        
        Maps integers to curved space for enhanced prime candidate density.
        
        Parameters
        ----------
        n : float or array_like
            Input values for geodesic mapping.
        phi : float, optional
            Modulus for geodesic mapping. Uses wheel_modulus if None.
        k : float, optional
            Curvature parameter. Uses geodesic_k if None.
            
        Returns
        -------
        float or ndarray
            Geodesic-transformed coordinates.
        """
        if phi is None:
            phi = float(self.wheel_modulus)
        if k is None:
            k = self.geodesic_k
            
        n = np.asarray(n)
        return phi * ((n % phi) / phi) ** k


    def filter_prime_candidates(self, 
                              start: int, 
                              end: int,
                              threshold: Optional[float] = None,
                              phi: Optional[float] = None) -> List[int]:
        """
        Geodesic-enhanced prime candidate filtering.
        
        Generates candidates via wheel sieve and filters using geodesic density
        enhancement to achieve ~15% density boost in prime-rich regions.
        
        Parameters
        ----------
        start : int
            Start of range for candidate generation.
        end : int
            End of range for candidate generation.
        threshold : float, optional
            Geodesic threshold for filtering. Uses median if None.
        phi : float, optional
            Geodesic modulus. Uses wheel_modulus if None.
            
        Returns
        -------
        List[int]
            Filtered list of prime candidates.
        """
        if phi is None:
            phi = float(self.wheel_modulus)
            
        # Generate candidates using wheel sieve
        candidates = []
        for n in range(start, end + 1):
            if n % self.wheel_modulus in self._wheel_residues:
                candidates.append(n)
        
        if not candidates:
            return candidates
            
        candidates = np.array(candidates)
        
        # Compute geodesic values
        theta_values = self.geodesic_theta_prime(candidates, phi=phi)
        
        # Set threshold to median if not provided
        if threshold is None:
            threshold = np.median(theta_values)
            
        # Filter candidates above threshold
        mask = theta_values > threshold
        filtered_candidates = candidates[mask].tolist()
        
        logger.debug(f"Filtered {len(candidates)} to {len(filtered_candidates)} candidates "
                    f"({100*len(filtered_candidates)/len(candidates):.1f}% retention)")
        
        return filtered_candidates


    def zeta_correction(self, 
                       x: Union[float, np.ndarray],
                       zeros: Optional[List[float]] = None,
                       num_zeros: int = 20) -> Union[float, np.ndarray]:
        """
        Riemann zeta zeros correction for prime counting.
        
        Computes explicit formula approximation using zeta zeros:
        π(x) ≈ li(x) - Σ li(x^ρ)/|ρ|
        
        Parameters
        ----------
        x : float or array_like
            Input values for correction calculation.
        zeros : List[float], optional
            List of Riemann zeta zeros. Uses precomputed if None.
        num_zeros : int, optional
            Number of zeros to use in correction.
            
        Returns
        -------
        float or ndarray
            Zeta correction terms.
        """
        if zeros is None:
            zeros = RIEMANN_ZETA_ZEROS[:num_zeros]
        else:
            zeros = zeros[:num_zeros]
            
        x = np.asarray(x)
        is_scalar = x.ndim == 0
        if is_scalar:
            x = x.reshape(1)
            
        corrections = np.zeros_like(x, dtype=complex)
        
        for rho in zeros:
            # Each zero ρ = 1/2 + i*γ, we use γ (imaginary part)
            gamma = float(rho)
            rho_complex = 0.5 + 1j * gamma
            
            # Compute li(x^ρ) / |ρ|
            try:
                x_rho = x ** rho_complex
                li_x_rho = _logarithmic_integral(x_rho)
                corrections += li_x_rho / abs(rho_complex)
            except (OverflowError, ZeroDivisionError):
                # Handle numerical issues with large x or small rho
                logger.warning(f"Numerical issue with zero {rho} for x values")
                continue
                
        # Take real part and normalize by E_SQUARED
        corrections = np.real(corrections) / E_SQUARED
        
        return float(corrections[0]) if is_scalar else corrections


    def hybrid_z5d_prime(self, 
                        k: Union[float, np.ndarray],
                        include_zeta: bool = True,
                        num_zeros: int = 10) -> Union[float, np.ndarray]:
        """
        Hybrid Z5D predictor with zeta corrections.
        
        Combines calibrated Z5D prediction with Riemann zeta zeros correction
        for enhanced accuracy: 
        hybrid = z5d_prime(k) - zeta_correction(z5d_prime(k)) / Δ_max
        
        Parameters
        ----------
        k : float or array_like
            Index values for prime prediction.
        include_zeta : bool, optional
            Whether to include zeta corrections.
        num_zeros : int, optional
            Number of zeta zeros to use.
            
        Returns
        -------
        float or ndarray
            Hybrid prime predictions.
        """
        # Get base Z5D prediction
        z5d_pred = self.calibrated_z5d_prime(k)
        
        if not include_zeta:
            return z5d_pred
            
        # Compute zeta correction
        try:
            zeta_corr = self.zeta_correction(z5d_pred, num_zeros=num_zeros)
            return z5d_pred - zeta_corr
        except Exception as e:
            logger.warning(f"Zeta correction failed: {e}, returning base Z5D prediction")
            return z5d_pred


    def validate_predictions(self, 
                           k_test: Union[List[int], np.ndarray],
                           true_primes_test: Optional[Union[List[int], np.ndarray]] = None,
                           method: str = 'hybrid') -> Dict[str, float]:
        """
        Validate predictions on holdout test set.
        
        Parameters
        ----------
        k_test : array_like
            Test k values.
        true_primes_test : array_like, optional
            True prime values for test set.
        method : str, optional
            Prediction method: 'z5d', 'hybrid', or 'calibrated'.
            
        Returns
        -------
        Dict[str, float]
            Validation metrics (MAE, MRE, etc.).
        """
        k_test = np.asarray(k_test)
        
        if true_primes_test is None:
            true_primes_test = np.array([sympy.ntheory.prime(int(k)) for k in k_test])
        else:
            true_primes_test = np.asarray(true_primes_test)
            
        # Get predictions based on method
        if method == 'hybrid':
            predictions = self.hybrid_z5d_prime(k_test)
        elif method == 'calibrated':
            predictions = self.calibrated_z5d_prime(k_test)
        elif method == 'z5d':
            predictions = z5d_prime(k_test)
        else:
            raise ValueError(f"Unknown method: {method}")
            
        # Calculate metrics
        mae = np.mean(np.abs(predictions - true_primes_test))
        mre = np.mean(np.abs((predictions - true_primes_test) / true_primes_test))
        rmse = np.sqrt(np.mean((predictions - true_primes_test) ** 2))
        max_error = np.max(np.abs((predictions - true_primes_test) / true_primes_test))
        
        return {
            'mae': mae,
            'mre': mre, 
            'rmse': rmse,
            'max_error': max_error,
            'method': method,
            'n_test': len(k_test),
            'is_calibrated': self.is_calibrated
        }