/**
 * Z5D FFT-Zeta Enhancement - Header
 * @author Dionisio Alberto Lopez III (D.A.L. III)
 * 
 * z5d_fft_zeta.h - Header for FFT-based zeta enhancement for Z5D curvature
 */
#ifndef Z5D_FFT_ZETA_H
#define Z5D_FFT_ZETA_H

// Auto-detect MPFR availability
#ifndef __has_include
#  define __has_include(x) 0
#endif
#if __has_include("mpfr.h")
#  include <mpfr.h>
#  define Z5D_FFT_HAVE_MPFR 1
#else
#  define Z5D_FFT_HAVE_MPFR 0
#endif

#ifdef __cplusplus
extern "C" {
#endif

#if Z5D_FFT_HAVE_MPFR
/**
 * FFT-based zeta proxy for Z5D curvature enhancement
 * 
 * @param T MPFR value representing the imaginary part parameter
 * @param dps Decimal places for MPFR precision (typically 50)
 * @return Proxy value for kappa enhancement
 */
double z5d_zeta_proxy(mpfr_t T, int dps);
#endif

/**
 * Enhanced Z5D prime prediction with FFT-zeta integration
 * 
 * @param k Prime index
 * @param c_in Dilation calibration parameter
 * @param k_star_in Curvature calibration parameter
 * @param kappa_geo_in Geodesic exponent for enhancement
 * @param auto_calibrate Whether to use automatic calibration
 * @return Enhanced prime prediction
 */
double z5d_prime_with_fft_zeta(double k, double c_in, double k_star_in, double kappa_geo_in, int auto_calibrate);

/**
 * Lorentz factor calculation for the hypothesis
 * γ=1+(1/2)(ln p_k/(e^4+β ln p_k))^2, β≈30.34
 * 
 * @param p_k Prime value
 * @param beta Beta parameter (≈30.34)
 * @return Lorentz factor gamma
 */
double z5d_lorentz_gamma(double p_k, double beta);

/**
 * Validation function for FFT-zeta accuracy
 * 
 * @param test_k_values Array of k values to test
 * @param n_tests Number of test values
 * @param tolerance Acceptable relative difference tolerance
 * @return Number of tests passed
 */
int z5d_validate_fft_zeta(double* test_k_values, int n_tests, double tolerance);

#ifdef __cplusplus
}
#endif

#endif // Z5D_FFT_ZETA_H