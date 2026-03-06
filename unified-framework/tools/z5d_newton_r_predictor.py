# -----------------------------------------------------------------------------
# Z5D Reference Implementation: Newton–R Prime Predictor (heavily commented)
#
# Goal
# ----
# Estimate the n-th prime p_n by solving R(x) = n with a *single* Newton step,
# where R(x) is the Riemann prime-counting function approximation:
#     R(x) = sum_{k=1..K} μ(k)/k * li(x^{1/k})
# This implementation:
#   • Keeps all arithmetic in high precision (mpmath mpf) for ppm/% fidelity.
#   • Uses a classic Dusart-like initializer for x0.
#   • Uses a truncated series (K terms) — K=5 is a good accuracy/speed tradeoff.
#   • Prints percent/ppm with robust formatting (no reliance on mpf __format__).
#
# Important design choices
# ------------------------
# 1) High precision (mp.dps = 50) ensures that tiny relative errors at large n
#    are not swallowed by floating-point rounding.
# 2) We only cast to float for *printing* small numbers; all math stays mpf.
# 3) We never compute primes; we compare against a known table of p_{10^k}.
# -----------------------------------------------------------------------------

import time
from functools import lru_cache

try:
    from mpmath import mp, li
    mp.dps = 50  # Use 50 decimal digits of precision across the board.
    # Rationale: At scales like p_{10^18} ~ 4.4e19, double floats
    # can’t represent sub-ppm differences reliably. mpf can.
except ImportError:
    # We explicitly depend on mpmath for high-precision arithmetic and li().
    raise ImportError("This module requires 'mpmath'. Install with: pip install mpmath")

@lru_cache(maxsize=None)
def mu(n: int) -> int:
    """Möbius function μ(n)."""
    # μ(1) := 1 by definition.
    if n == 1:
        return 1
    # We factor n by trial division. For moderate K in R(x) this is fine.
    # We only call mu() on small k (k <= K), so this is effectively O(1) here.
    prime_factors = 0
    i = 2
    temp_n = n
    # Trial division up to sqrt(temp_n).
    while i * i <= temp_n:
        if temp_n % i == 0:
            prime_factors += 1      # Count this prime factor once...
            temp_n //= i
            if temp_n % i == 0:     # ...but if i divides again, n has a square.
                return 0            # Not square-free ⇒ μ(n) = 0
        i += 1
    # If what's left is > 1, it is prime and contributes one factor.
    if temp_n > 1:
        prime_factors += 1
    # Square-free:
    #   even number of prime factors  → μ(n) =  +1
    #   odd  number of prime factors  → μ(n) =  -1
    return -1 if (prime_factors % 2) else 1

def riemann_R(x: mp.mpf, K: int) -> mp.mpf:
    """R(x) ≈ ∑_{k=1..K} μ(k)/k · li(x^{1/k})."""
    # R(x) is a smooth approximation to π(x).
    # We evaluate the truncated series up to K, which typically converges fast.
    # • μ(k) provides inclusion–exclusion.
    # • li(x^{1/k}) is the logarithmic integral at the k-th root of x.
    # We cast denominators to mpf to avoid integer division surprises.
    # mp.nsum performs a discrete sum (not an integral) with mpmath precision.
    return mp.nsum(lambda k: mu(int(k)) / mp.mpf(k) * li(x**(mp.mpf(1)/mp.mpf(k))), [1, K])

def riemann_R_prime(x: mp.mpf, K: int) -> mp.mpf:
    """R'(x) = (1/ln x) · ∑_{k=1..K} μ(k)/k · x^{1/k - 1}."""
    # Derivation sketch:
    #   R(x) = ∑ μ(k)/k · li(x^{1/k})
    #   d/dx li(u) = 1/ln(u) · du/dx
    #   u = x^{1/k} ⇒ du/dx = (1/k) · x^{1/k - 1}
    #   ln(u) = ln(x^{1/k}) = (1/k) ln x  ⇒ 1/ln(u) = k / ln x
    #   So: d/dx li(x^{1/k}) = (k/ln x) * (1/k) x^{1/k - 1} = x^{1/k - 1} / ln x
    # Multiply by μ(k)/k and sum:
    #   R'(x) = (1/ln x) ∑ μ(k)/k · x^{1/k - 1}
    ln_x = mp.log(x)
    series_sum = mp.nsum(lambda k: (mu(int(k)) / mp.mpf(k)) * x**(mp.mpf(1)/mp.mpf(k) - 1), [1, K])
    return series_sum / ln_x

def p_newton_R(n: int, K: int = 5) -> mp.mpf:
    """
    Estimate the n-th prime by one Newton step solving R(x) = n.
    Parameter-free; math stays mp.mpf throughout.
    """
    # Convert n to high-precision mpf immediately to keep all downstream math
    # consistent in precision and avoid mixed-type behavior.
    n_f = mp.mpf(n)
    # High-quality initializer x0:
    #   x0 = n (ln n + ln ln n − 1 + (ln ln n − 2)/ln n)
    # This is a classic Dusart-like expansion and generally lands very near p_n.
    L = mp.log(n_f)
    L2 = mp.log(L)
    x0 = n_f * (L + L2 - 1 + (L2 - 2) / L)  # Dusart-like initializer

    # One Newton step:
    #   f(x)  = R(x) − n
    #   f'(x) = R'(x)
    #   x1    = x0 − f(x0)/f'(x0)
    fx0 = riemann_R(x0, K) - n_f
    f_prime_x0 = riemann_R_prime(x0, K)
    if f_prime_x0 == 0:
        # Extremely unlikely, but safe-guard: if derivative is zero,
        # return the initializer rather than dividing by zero.
        return x0
    return x0 - fx0 / f_prime_x0

# ---------- formatting helpers (avoid mpf formatting pitfalls) ----------
def fmt_ppm(x: mp.mpf, decimals: int = 6) -> str:
    """Fixed decimals for ppm using float cast only for display."""
    # We *only* cast to float for display. The underlying computation uses mpf.
    # Reason: In some environments, mpf does not support f-string format codes.
    # Use mp.re() to ensure we get a real number for display
    return f"{float(mp.re(x)):.{decimals}f}"

def fmt_percent(x: mp.mpf) -> str:
    """
    For |x| >= 1e-6 (%) show fixed 7 decimals via float.
    For smaller values, show scientific with 6 significant digits via mp.nstr.
    """
    # At very large n, relative errors are often < 1e-6%.
    # Printing fixed 7 decimals would show as 0.0000000%. To preserve visibility,
    # we switch to scientific notation (string via mp.nstr) below that threshold.
    ax = mp.fabs(x)
    threshold = mp.mpf('1e-6')  # percent threshold
    if ax >= threshold:
        return f"{float(mp.re(x)):.7f}%"
    # mp.nstr returns a string in scientific notation with given significant digits.
    return mp.nstr(x, 6) + "%"

# -----------------------------------------------------------------------

if __name__ == '__main__':
    print("--- Z5D Reference Implementation: Newton-R Prime Predictor ---")

    # Build test set for decades: n = 10^k for k = 1..18
    # We avoid computing primes; we compare against a known truth table.
    tests = [(f"10^{k}", 10**k) for k in range(1, 19)]

    # Known values for p_{10^k}.
    # Source note: These are widely tabulated constants (e.g., OEIS A006988 context),
    # and are included here verbatim to avoid any prime computation.
    known_values = {
        10**1: 29,
        10**2: 541,
        10**3: 7919,
        10**4: 104729,
        10**5: 1299709,
        10**6: 15485863,
        10**7: 179424673,
        10**8: 2038074743,
        10**9: 22801763489,
        10**10: 252097800623,
        10**11: 2760727302517,
        10**12: 29996224275833,
        10**13: 323780508946331,
        10**14: 3475385758524527,
        10**15: 37124508045065437,
        10**16: 394906913903735329,
        10**17: 4185296581467695669,
        10**18: 44211790234832169331,
    }

    for label, n_val in tests:
        # Friendly header for each decade. We also print the integer form with commas.
        print(f"\nEstimating the n-th prime at n={label} (n={n_val:,})...")

        # Measure wall-clock time for the single Newton step pipeline at each n.
        start_time = time.perf_counter()
        prediction = p_newton_R(n_val, K=5)  # Keep as mp.mpf (no downcasting).
        end_time = time.perf_counter()

        duration_ms = (end_time - start_time) * 1000.0  # report in milliseconds

        # Pull the known truth as mpf for precise subtraction and ratio operations.
        true_val = mp.mpf(known_values[n_val])

        # Error metrics (signed):
        #   error             = prediction − truth
        #   ppm_error         = 1e6 * error / truth
        #   rel_error_percent = 100 * error / truth
        error = prediction - true_val
        ppm_error = mp.mpf('1e6') * error / true_val
        rel_error_percent = mp.mpf('100') * error / true_val

        # Pretty printing:
        # Convert large integers via mp.nint → int for comma-separated display,
        # but keep computations in mpf above.
        pred_disp = f"{int(mp.nint(prediction)):,}"
        true_disp = f"{int(true_val):,}"
        abs_err_disp = f"{int(mp.nint(error)):,}"

        print(f"  -> Prediction: {pred_disp}")
        print(f"  -> True Value: {true_disp}")
        print(f"  -> Abs. Error: {abs_err_disp}")
        print(f"  -> Rel. Error: {fmt_ppm(ppm_error)} ppm")
        print(f"  -> Rel. Error %: {fmt_percent(rel_error_percent)}")
        print(f"  -> Time Taken: {duration_ms:.3f} ms")

