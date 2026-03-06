import math
import mpmath as mp
import subprocess
import sys
import os
import re

mp.mp.dps = 50

# Path to z5d_prime_gen executable (adjust if needed)
Z5D_GEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'z5d_prime_gen')

# Import the predictor function
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from z5d_newton_r_predictor import p_newton_R

# Known small primes for approximation
SMALL_PRIMES = [None, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

# Used to compute the modular distance bounds for the fractional part
K_STAR = 0.2
WIDTH_FACTOR = 0.3
PHI = (1 + mp.sqrt(5)) / 2

def nth_prime(n):
    """Get the n-th prime using z5d prime gen (no sieve)."""
    if n == 1:
        return 2
    if n < 1:
        raise ValueError("n must be >= 1")
    try:
        result = subprocess.run([Z5D_GEN_PATH, str(n)], capture_output=True, text=True, check=True)
        # Parse the output for the refined prime
        lines = result.stdout.strip().split('\n')
        for line in reversed(lines):
            if line.startswith('Refined p_'):
                match = re.search(r'Refined p_\d+: (\d+)', line)
                if match:
                    return int(match.group(1))
        raise RuntimeError("Could not parse prime from output")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"z5d_prime_gen failed: {e}")
    except FileNotFoundError:
        raise RuntimeError("z5d_prime_gen executable not found. Ensure it's built and in the project root.")

def fractional_sqrt(x):
    """Return fractional part of sqrt(x) with high precision"""
    r = mp.sqrt(x)
    return r - mp.floor(r)

def sha256_frac_to_u32_hex(frac):
    """Convert fractional part to SHA-256 style 32-bit word"""
    val = int(mp.floor(frac * (1 << 32)))
    return f"0x{val:08x}"

def prime_approximation(m):
    """Approximate the m-th prime using x5d predictor (Newton-R method)"""
    if m < len(SMALL_PRIMES):
        return mp.mpf(SMALL_PRIMES[m])
    else:
        return p_newton_R(m)

def calculate_theta_prime(m):
    """Calculate theta_prime for geometric adjustment"""
    m_mod_phi = mp.fmod(m, PHI)
    ratio = m_mod_phi / PHI
    return PHI * (ratio ** K_STAR)

def main():
    # Parameter sweep for K_STAR and WIDTH_FACTOR
    K_STAR_VALUES = [0.1]
    WIDTH_FACTOR_VALUES = [0.6]
    total_tests = 100000
    results = []

    for k_star in K_STAR_VALUES:
        for width_factor in WIDTH_FACTOR_VALUES:
            within_bounds_count = 0
            failing_ms = []
            for m in range(1, total_tests + 1):
                p_true = nth_prime(m)
                frac_true = float(fractional_sqrt(p_true))
                p_approx = prime_approximation(m)
                frac_pred = float(fractional_sqrt(p_approx))

                # Dynamic width
                m_mod_phi = mp.fmod(m, PHI)
                ratio = m_mod_phi / PHI
                theta_prime = PHI * (ratio ** k_star)
                width = float(theta_prime * width_factor)

                diff = abs(frac_true - frac_pred)
                circular_diff = min(diff, 1 - diff)
                if circular_diff <= width:
                    within_bounds_count += 1
                else:
                    failing_ms.append(m)

            success_rate = within_bounds_count / total_tests * 100
            results.append((k_star, width_factor, success_rate, failing_ms))

    # Print sorted optimization results
    print("Optimization Results:")
    for k_star, width_factor, success_rate, failing_ms in sorted(results, key=lambda x: x[2], reverse=True):
        print(f"K_STAR={k_star}, WIDTH_FACTOR={width_factor} => {success_rate:.1f}%")
        if failing_ms:
            print(f"Failing m's: {failing_ms}")

if __name__ == "__main__":
    main()