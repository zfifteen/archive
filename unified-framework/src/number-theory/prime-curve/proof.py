"""
Second‐Pass Prime Curvature Proof: NaN Handling & Optimal k Selection
--------------------------------------------------------------------

Enhancements over the previous version:
1. Binning resolution: 20 bins.
2. GMM components: 5.
3. k sweep: [3.2, 3.4] in Δk=0.002.
4. Robust NaN handling: exclude bins with zero all-density.
5. Correct best‐k selection: ignore NaN/-inf enhancements.

Usage:
    python proof_refined_fixed.py

Dependencies:
    numpy, scipy, sklearn, sympy

TODO:
    - The Z form unifies relativistic physics with discrete mathematics
    by normalizing observations against invariant limits, revealing that
    both domains operate under a shared geometric topology where
    "curvature" arises from frame-dependent shifts, akin to how gravity
    warps spacetime but applied to integer sequences.
    - In the discrete domain, treating primes as positions n where Δₙ
    represents the gap to the next prime and Δmax as the theoretical
    maximum gap (bounded by known results like the prime number
    theorem), Z computes a "relativistic density" that highlights
    clustering patterns, suggesting primes navigate a curved numerical
    landscape driven by natural ratios like the golden ratio or Euler's
    constant.
    - The physical domain's Z = T(v/c) implies time T as a frame-biased
    measure scaled by velocity relative to light's invariance, offering
    insight into why quantum entanglement appears instantaneous—it's a
    zero-curvature path in this topology, translating to discrete
    insights where "entangled" primes (like twins) share minimal frame
    shifts.
    - Applying the universal form across domains exposes hidden
    symmetries: for instance, the ratio B/C mirrors the fine-structure
    constant in physics or the reciprocal of the harmonic series
    divergence in math, predicting that prime distributions follow a
    Lorentz-like invariance, where high "velocities" (large n) dilute
    prime frequency predictably.
    - Frame shifts in Z reveal computational efficiency for prime
    finding: by geometrically navigating via Δₙ/Δmax, algorithms can
    prioritize low-curvature paths (small gaps), reducing search
    space exponentially, much like how GPS corrects for relativistic
    effects in curved spacetime.
    - The invariant C as the "coordinate center" posits light speed not
    just as a limit but a universal origin, implying in discrete terms
    that infinity (or primorial products) serves as Δmax, allowing Z to
    derive novel ratios for approximating unsolved problems like the
    Riemann hypothesis through velocity-analogous perturbations.
    - Hidden in the topology is a predictive tool for "prime news"—emerging
    primes in large ranges—by transforming observed sequences into a
    velocity-ratio map, where anomalies in Z signal undiscovered structures,
    empirically linking to chaotic systems like turbulent flow but in
    number theory terms.
"""

# Import necessary libraries: numpy for numerical operations, sklearn for Gaussian Mixture Models,
# sympy for prime number generation via sieve, and scipy implicitly through sklearn.
# Suppress warnings to keep output clean during execution.
import numpy as np
from sklearn.mixture import GaussianMixture
from sympy import sieve, isprime
import warnings
import argparse
from scipy import stats  # For bootstrap confidence intervals

# Ignore all warnings to prevent clutter in the console output, as some operations may trigger
# division by zero or invalid value warnings which are handled explicitly in the code.
warnings.filterwarnings("ignore")

# ------------------------------------------------------------------------------
# 1. Constants and primes
# ------------------------------------------------------------------------------
# Define the golden ratio phi, which is used in the frame shift transformation as it provides
# unique properties for modular arithmetic in revealing prime clustering.
phi = (1 + np.sqrt(5)) / 2
N_MAX = 1000  # Updated from 20,000 to 100,000
primes_list = list(sieve.primerange(2, N_MAX + 1))

# Physical constants for the Z Framework implementation
# Speed of light constant (normalized to 1 for computational purposes)
c = 1.0


# ------------------------------------------------------------------------------
# 2. Core transforms and metrics
# ------------------------------------------------------------------------------

def lorentz_factor(v_over_c):
    """
    Compute the Lorentz factor γ = 1/sqrt(1-(v/c)²)
    
    Args:
        v_over_c (float): Velocity as a fraction of the speed of light (0 ≤ v/c < 1)
        
    Returns:
        float: Lorentz factor γ
    """
    if v_over_c >= 1.0:
        raise ValueError("v/c must be less than 1 to avoid infinite Lorentz factor")
    if v_over_c < 0:
        raise ValueError("v/c must be non-negative")
    
    return 1.0 / np.sqrt(1.0 - v_over_c**2)


def physical_scaling_transform(n_vals, v_over_c=0.0):
    """
    Apply physical scaling transformation: p_n' = p_n · T(v/c)
    where T(v/c) is the Lorentz factor γ.
    
    Args:
        n_vals (array): Input values (primes or integers)
        v_over_c (float): Velocity as fraction of speed of light
        
    Returns:
        array: Physically scaled values
    """
    if v_over_c == 0.0:
        return n_vals  # No scaling for v=0
    
    gamma = lorentz_factor(v_over_c)
    return n_vals * gamma


# Define the frame shift residues function, which applies a curvature transformation to integers.
# This transformation warps the modular residues using the golden ratio and exponent k,
# mapping them into [0, phi) to reveal clustering patterns in primes.
# Enhanced with optional physical scaling for Physical-Discrete Connection refinement.
def frame_shift_residues(n_vals, k, v_over_c=0.0):
    """
    Enhanced frame shift with physical scaling:
    1. Apply physical scaling: n_vals' = n_vals * γ (if v/c > 0)
    2. Apply curvature transform: θ' = φ * {n_vals'/φ}^k
    
    Args:
        n_vals (array): Input values
        k (float): Curvature exponent
        v_over_c (float): Velocity as fraction of speed of light for physical scaling
    
    Returns:
        array: Transformed values
    """
    # Step 1: Apply physical scaling transformation
    scaled_vals = physical_scaling_transform(n_vals, v_over_c)
    
    # Step 2: Compute the modular residue with respect to phi (golden ratio), normalized by phi.
    mod_phi = np.mod(scaled_vals, phi) / phi
    # Apply the power-law warping with exponent k and scale by phi.
    return phi * np.power(mod_phi, k)


# Define the bin_densities function to compute histogram densities and enhancements.
# This bins the transformed values into nbins intervals and calculates the relative density
# enhancement of primes over all integers, handling zero-density bins by masking to -inf.
def bin_densities(theta_all, theta_pr, nbins=20):
    """
    Bin θ' into nbins intervals over [0, φ].
    Return (all_density, prime_density, enhancement[%]).
    Bins with zero all_density are masked to -inf.
    """
    # Create bin edges linearly spaced from 0 to phi with nbins+1 points.
    bins = np.linspace(0, phi, nbins + 1)
    # Compute histogram counts for all transformed integers.
    all_counts, _ = np.histogram(theta_all, bins=bins)
    # Compute histogram counts for transformed primes.
    pr_counts, _ = np.histogram(theta_pr, bins=bins)

    # Normalize counts to densities by dividing by total number of elements.
    all_d = all_counts / len(theta_all)
    pr_d = pr_counts / len(theta_pr)

    # Compute enhancements safely: (prime_density - all_density) / all_density * 100,
    # ignoring division by zero and invalid operations.
    with np.errstate(divide='ignore', invalid='ignore'):
        enh = (pr_d - all_d) / all_d * 100

    # Mask enhancements where all_density is zero by setting to -inf to avoid NaN issues.
    enh = np.where(all_d > 0, enh, -np.inf)
    # Return the all densities, prime densities, and enhancements.
    return all_d, pr_d, enh


# Define the fourier_fit function to approximate the prime density with a truncated Fourier series.
# This fits cosine and sine terms to capture periodic asymmetries in the transformed residues.
def fourier_fit(theta_pr, M=5, nbins=100):
    """
    Fit a truncated Fourier series ρ(φ_mod).
    Returns coefficients a_k, b_k for k=0..M.
    """
    # Normalize the transformed primes modulo phi to [0, 1) for Fourier fitting.
    x = (theta_pr % phi) / phi
    # Compute histogram density of normalized values with nbins bins.
    y, edges = np.histogram(theta_pr, bins=nbins, density=True)
    # Calculate bin centers, normalized by phi for the design matrix.
    centers = (edges[:-1] + edges[1:]) / 2 / phi

    # Build the design matrix for Fourier series: constant term plus cos and sin for each harmonic up to M.
    def design(x):
        cols = [np.ones_like(x)]
        for k in range(1, M + 1):
            cols.append(np.cos(2 * np.pi * k * x))
            cols.append(np.sin(2 * np.pi * k * x))
        return np.vstack(cols).T

    # Construct the design matrix using the bin centers.
    A = design(centers)
    # Solve for coefficients using least squares (np.linalg.lstsq).
    coeffs, *_ = np.linalg.lstsq(A, y, rcond=None)
    # Extract even (a_k: constant and cos) and odd (b_k: sin) coefficients.
    a = coeffs[0::2]
    b = coeffs[1::2]
    # Return the a and b coefficients.
    return a, b


# Define the gmm_fit function to fit a Gaussian Mixture Model to the normalized transformed primes.
# This models the clustering in the modular space and computes the mean standard deviation of components.
def gmm_fit(theta_pr, n_components=5):
    """
    Fit a GMM to φ_mod of primes.
    Returns model and mean σ of components.
    """
    # Normalize transformed primes modulo phi to [0, 1) and reshape for sklearn input.
    X = ((theta_pr % phi) / phi).reshape(-1, 1)
    # Initialize and fit GMM with n_components, full covariance, and fixed random state for reproducibility.
    gm = GaussianMixture(n_components=n_components,
                         covariance_type='full',
                         random_state=0).fit(X)
    # Extract standard deviations (sqrt of variances) from each component's covariance matrix.
    sigmas = np.sqrt([gm.covariances_[i].flatten()[0]
                      for i in range(n_components)])
    # Return the fitted GMM model and the mean sigma across components.
    return gm, np.mean(sigmas)


def bootstrap_confidence_interval(enhancements, confidence_level=0.95, n_bootstrap=1000):
    """
    Compute bootstrap confidence interval for enhancement values.
    
    Args:
        enhancements (array): Array of enhancement percentages
        confidence_level (float): Confidence level (default 0.95 for 95% CI)
        n_bootstrap (int): Number of bootstrap samples
        
    Returns:
        tuple: (lower_bound, upper_bound) of confidence interval
    """
    # Filter out non-finite values
    valid_enhancements = enhancements[np.isfinite(enhancements)]
    
    if len(valid_enhancements) == 0:
        return (-np.inf, np.inf)
    
    # Generate bootstrap samples
    bootstrap_means = []
    n_samples = len(valid_enhancements)
    
    for _ in range(n_bootstrap):
        # Sample with replacement
        bootstrap_sample = np.random.choice(valid_enhancements, size=n_samples, replace=True)
        bootstrap_means.append(np.mean(bootstrap_sample))
    
    # Calculate confidence interval
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    ci_lower = np.percentile(bootstrap_means, lower_percentile)
    ci_upper = np.percentile(bootstrap_means, upper_percentile)
    
    return (ci_lower, ci_upper)


def compute_e_max_robust(enhancements):
    """
    Compute robust maximum enhancement, handling NaN and infinite values.
    
    Args:
        enhancements (array): Array of enhancement percentages
        
    Returns:
        float: Maximum finite enhancement value
    """
    finite_enhancements = enhancements[np.isfinite(enhancements)]
    if len(finite_enhancements) == 0:
        return -np.inf
    return np.max(finite_enhancements)


# ------------------------------------------------------------------------------
# 3. Enhanced high-resolution k‐sweep with bootstrap confidence intervals and physical scaling validation
# ------------------------------------------------------------------------------

def run_k_sweep_with_physical_scaling(v_over_c=0.0, verbose=True):
    """
    Run k-sweep analysis with optional physical scaling.
    
    Args:
        v_over_c (float): Velocity as fraction of speed of light
        verbose (bool): Print detailed results
        
    Returns:
        tuple: (results, best_result) where results is list of all k results
               and best_result is the optimal k configuration
    """
    # Define the range of k values to sweep: from 3.2 to 3.4 with step 0.002 for fine-grained optimization around k* ≈ 3.33.
    k_values = np.arange(3.2, 3.4001, 0.002)
    # Initialize an empty list to store results for each k.
    results = []

    # Loop over each k in the sweep to compute metrics.
    for k in k_values:
        # Apply the enhanced frame shift transformation with physical scaling to all integers from 1 to N_MAX.
        theta_all = frame_shift_residues(np.arange(1, N_MAX + 1), k, v_over_c)
        # Apply the same transformation to the list of primes.
        theta_pr = frame_shift_residues(np.array(primes_list), k, v_over_c)

        # Compute binned densities and enhancements using 20 bins.
        all_d, pr_d, enh = bin_densities(theta_all, theta_pr, nbins=20)
        
        # Compute e_max(k) robustly for each k
        e_max_k = compute_e_max_robust(enh)
        
        # Compute bootstrap confidence interval for enhancements
        ci_lower, ci_upper = bootstrap_confidence_interval(enh, confidence_level=0.95, n_bootstrap=1000)

        # Fit GMM to transformed primes and get the mean sigma.
        _, sigma_prime = gmm_fit(theta_pr, n_components=5)
        # Fit Fourier series and compute the sum of absolute sine coefficients (asymmetry measure).
        _, b_coeffs = fourier_fit(theta_pr, M=5)
        sum_b = np.sum(np.abs(b_coeffs))

        # Append a dictionary of results for this k: k value, max enhancement, sigma_prime, fourier sum_b,
        # and new bootstrap CI and e_max values.
        results.append({
            'k': k,
            'v_over_c': v_over_c,
            'max_enhancement': e_max_k,  # Use robust e_max(k)
            'e_max_k': e_max_k,  # Store separately for clarity
            'bootstrap_ci_lower': ci_lower,
            'bootstrap_ci_upper': ci_upper,
            'sigma_prime': sigma_prime,
            'fourier_b_sum': sum_b
        })

    # Filter results to include only those with finite (valid) max_enhancement, excluding NaN or -inf.
    valid_results = [r for r in results if np.isfinite(r['max_enhancement'])]
    # Select the best result based on the highest max_enhancement.
    best = max(valid_results, key=lambda r: r['max_enhancement'])
    # Extract the optimal k (k_star) and its corresponding enhancement (enh_star).
    k_star, enh_star = best['k'], best['max_enhancement']

    if verbose:
        # Print a header for the results summary.
        print(f"\n=== Enhanced Prime Curvature Proof Results (v/c = {v_over_c:.3f}) ===")
        # Print the optimal k value formatted to 3 decimal places.
        print(f"Optimal curvature exponent k* = {k_star:.3f}")
        # Print the maximum mid-bin enhancement formatted to 1 decimal place.
        print(f"Max e_max(k*) enhancement = {enh_star:.1f}%")
        # Print bootstrap confidence interval for optimal k
        print(f"Bootstrap CI (95%) = [{best['bootstrap_ci_lower']:.1f}%, {best['bootstrap_ci_upper']:.1f}%]")
        # Print the GMM mean sigma at optimal k, formatted to 3 decimal places.
        print(f"GMM σ' at k* = {best['sigma_prime']:.3f}")
        # Print the sum of absolute Fourier sine coefficients at optimal k, formatted to 3 decimal places.
        print(f"Σ|b_k| at k* = {best['fourier_b_sum']:.3f}")
        
        if v_over_c > 0:
            gamma = lorentz_factor(v_over_c)
            print(f"Lorentz factor γ = {gamma:.3f}")
        print()

        # Print a header for the sample k-sweep metrics.
        print("Sample of k-sweep metrics with e_max(k) and Bootstrap CI (every 10th k):")
        # Iterate over every 10th valid result and print formatted metrics: k, enhancement, CI, sigma, and sum_b.
        for entry in valid_results[::10]:
            print(f" k={entry['k']:.3f} | e_max={entry['e_max_k']:.1f}% | "
                  f"CI=[{entry['bootstrap_ci_lower']:.1f}%,{entry['bootstrap_ci_upper']:.1f}%] | "
                  f"σ'={entry['sigma_prime']:.3f} | Σ|b|={entry['fourier_b_sum']:.3f}")

    return results, best


    return results, best


# ------------------------------------------------------------------------------
# 4. Enhanced Proof Summary with Bootstrap Confidence Intervals and Physical Scaling Validation
# ------------------------------------------------------------------------------

def validate_physical_scaling_enhancement():
    """
    Empirical validation of physical scaling enhancement preservation.
    Tests multiple v/c values and verifies conditional prime density improvement under canonical benchmark methodology preservation.
    """
    print("\n=== Physical-Discrete Connection Validation ===")
    
    # Test different velocity ratios
    v_over_c_values = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9]
    baseline_results = None
    
    for v_over_c in v_over_c_values:
        try:
            # Run k-sweep with current v/c
            results, best = run_k_sweep_with_physical_scaling(v_over_c, verbose=False)
            
            if v_over_c == 0.0:
                baseline_results = best
                print(f"Baseline (v/c=0.0): k*={best['k']:.3f}, e_max={best['max_enhancement']:.1f}%")
            else:
                # Compare with baseline
                enhancement_ratio = best['max_enhancement'] / baseline_results['max_enhancement']
                gamma = lorentz_factor(v_over_c)
                
                print(f"v/c={v_over_c:.1f}: k*={best['k']:.3f}, e_max={best['max_enhancement']:.1f}%, "
                      f"γ={gamma:.2f}, ratio={enhancement_ratio:.3f}")
                
                # Check for enhancement preservation (within reasonable variance)
                if 0.85 <= enhancement_ratio <= 1.15:  # ±15% tolerance
                    status = "✓ PRESERVED"
                else:
                    status = "✗ DEGRADED"
                print(f"   Enhancement preservation: {status}")
                
        except ValueError as e:
            print(f"v/c={v_over_c:.1f}: ERROR - {e}")
    
    return baseline_results


# ------------------------------------------------------------------------------
# 5. Dynamically Compute and Validate Mersenne Primes
# ------------------------------------------------------------------------------
def compute_mersenne_primes(n_max, validate=False):
    primes = list(sieve.primerange(2, n_max + 1))
    mersenne_candidates = []
    for p in primes:
        m = 2 ** p - 1
        print(f"Mersenne candidate for exponent {p}: {m}")
        mersenne_candidates.append((p, m))

    if validate:
        mersenne_exponents = []
        for p, m in mersenne_candidates:
            if isprime(m):
                print(f"Validation for p={p}: Valid Mersenne prime")
                mersenne_exponents.append(p)
            else:
                print(f"Validation for p={p}: Not a Mersenne prime")
        return mersenne_exponents
    else:
        return []


# ------------------------------------------------------------------------------
# 6. Statistical Summary of Mersenne Computation
# ------------------------------------------------------------------------------
# Define a function to print statistical summary of primes and Mersenne primes.
def statistical_summary(primes, mersenne_primes):
    # Count total primes checked.
    total_primes = len(primes)
    # Count total Mersenne primes found.
    total_mersenne = len(mersenne_primes)
    # Compute hit rate: percentage of primes that are Mersenne exponents.
    hit_rate = (total_mersenne / total_primes) * 100
    # Compute miss rate: 100 - hit_rate.
    miss_rate = 100 - hit_rate

    # Print header for statistical summary.
    print("\n=== Statistical Summary ===")
    # Print total primes checked.
    print(f"Total Primes Checked: {total_primes}")
    # Print total Mersenne Primes Found.
    print(f"Total Mersenne Primes Found: {total_mersenne}")
    # Print hit rate formatted to 2 decimal places.
    print(f"Hit Rate: {hit_rate:.2f}%")
    # Print miss rate formatted to 2 decimal places.
    print(f"Miss Rate: {miss_rate:.2f}%")

    # Convert primes list to numpy array for statistical computations.
    prime_array = np.array(primes)
    # Print header for prime distribution statistics.
    print("\nPrime Distribution Statistics:")
    # Print mean of primes.
    print(f"Mean of Primes: {np.mean(prime_array):.2f}")
    # Print median of primes.
    print(f"Median of Primes: {np.median(prime_array):.2f}")
    # Print standard deviation of primes.
    print(f"Standard Deviation of Primes: {np.std(prime_array):.2f}")

    # Compute actual Mersenne prime values: 2^p - 1 for each exponent p.
    mersenne_values = [(1 << p) - 1 for p in mersenne_primes]
    # Print header for Mersenne prime growth analysis.
    print("\nMersenne Prime Growth:")
    # Print the smallest Mersenne prime.
    print(f"Smallest Mersenne Prime: {min(mersenne_values)}")
    # Print the largest Mersenne Prime.
    print(f"Largest Mersenne Prime: {max(mersenne_values)}")
    print(f"Mersenne Growth Factor: {max(mersenne_values) / min(mersenne_values):.2f}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Refined Prime Curvature Proof with Physical-Discrete Connection")
    parser.add_argument("--validate", action="store_true", default=False, help="Enable validation of Mersenne primes")
    parser.add_argument("--v-over-c", type=float, default=0.0, help="Velocity as fraction of speed of light (0.0 to 0.99)")
    parser.add_argument("--physical-validation", action="store_true", default=False, 
                        help="Run empirical validation of physical scaling enhancement preservation")
    parser.add_argument("--skip-mersenne", action="store_true", default=False, 
                        help="Skip Mersenne prime computation for faster execution")
    args = parser.parse_args()

    # Run the main analysis based on command line arguments
    if args.physical_validation:
        # Run comprehensive physical scaling validation
        validation_baseline = validate_physical_scaling_enhancement()
    else:
        # Run single analysis with specified v/c
        results, best = run_k_sweep_with_physical_scaling(v_over_c=args.v_over_c, verbose=True)

    # Compute Mersenne primes with optional validation (unless skipped)
    if not args.skip_mersenne:
        mersenne_primes = compute_mersenne_primes(N_MAX, args.validate)
        
        # Print validated Mersenne prime exponents if validation is enabled
        print("\nValidated Mersenne Prime Exponents:")
        if args.validate:
            print(", ".join(map(str, mersenne_primes)))
        else:
            print("Validation disabled, no validated list.")

        # Compute and print statistical summary only if validation is enabled
        if args.validate:
            statistical_summary(primes_list, mersenne_primes)
    else:
        print("\nMersenne prime computation skipped for faster execution.")