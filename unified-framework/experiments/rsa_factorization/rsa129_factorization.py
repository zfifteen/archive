# Modified RSA-129 Factorization Script
# Based on the RSA-260 script, targeting RSA-129 for validation

import time
import json
import sys
import os
# Ensure src is in the Python path for absolute import to work
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
import math
from datetime import datetime
from typing import Optional, Dict, Any

# Import the existing RSA factorization framework
from src.applications.primes.core.rsa_probe_validation import (
    RSA_CHALLENGE_NUMBERS,
    probe_semiprime_with_timeout,
    compensated_k_estimation
)

def log_rsa129_attempt(result: Dict[str, Any], factors: Optional[tuple] = None) -> None:
    """Log RSA-129 factorization attempt."""

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'challenge_number': 'RSA-129',
        'rsa_129_value': RSA_CHALLENGE_NUMBERS['RSA-129'],
        'digits': len(RSA_CHALLENGE_NUMBERS['RSA-129']),
        'bits_estimated': len(RSA_CHALLENGE_NUMBERS['RSA-129']) * math.log(10) / math.log(2),
        'algorithm': 'Enhanced Z5D Prime Predictor with Error Growth Compensation',
        'factorization_attempt': result,
        'factors_discovered': None,
        'verification_status': 'No factors found'
    }

    if factors:
        factor1, factor2 = factors
        log_entry['factors_discovered'] = {
            'factor_1': str(factor1),
            'factor_2': str(factor2),
            'factor_1_digits': len(str(factor1)),
            'factor_2_digits': len(str(factor2))
        }

        # Verify
        n = int(RSA_CHALLENGE_NUMBERS['RSA-129'])
        if factor1 * factor2 == n:
            log_entry['verification_status'] = 'VERIFIED - Factors multiply to RSA-129'
        else:
            log_entry['verification_status'] = 'ERROR - Factors do not multiply to RSA-129'

    with open('rsa129_factorization_log.json', 'w') as f:
        json.dump(log_entry, f, indent=2)

    print("📝 Factorization attempt logged to: rsa129_factorization_log.json")

def attempt_rsa129_factorization(trials: int = 1000, timeout_minutes: int = 30) -> Dict[str, Any]:
    """Attempt to factorize RSA-129 using enhanced Z5D algorithms."""

    print("=" * 80)
    print("RSA-129 FACTORIZATION ATTEMPT")
    print("=" * 80)
    print("Challenge: RSA-129 (129 decimal digits, ~429 bits)")
    print("Algorithm: Enhanced Z5D Prime Predictor with Error Growth Compensation")
    print("Goal: Derive the prime factors of RSA-129")
    print("=" * 80)

    n_str = RSA_CHALLENGE_NUMBERS['RSA-129']
    timeout_seconds = timeout_minutes * 60

    print(f"RSA-129 value: {n_str[:50]}...{n_str[-20:]}")
    print(f"Digits: {len(n_str)}")
    print(f"Estimated bits: {len(n_str) * math.log(10) / math.log(2):.0f}")
    print(f"Parameters: trials={trials}, timeout={timeout_minutes}min")

    # Calculate enhanced k estimation
    print("\nCalculating enhanced k estimation...")
    try:
        k_est = compensated_k_estimation(n_str, error_compensation=True)
        k_order = f"10^{int(math.log10(k_est))}" if k_est > 0 else "N/A"
        print(f"Enhanced k_est: {k_est:.2e}")
        print(f"k_est order: {k_order}")
    except Exception as e:
        print(f"Warning: k_est calculation failed: {e}")
        k_est = 0
        k_order = "N/A"

    print("\nStarting factorization attempt...")
    print("-" * 40)

    start_time = time.time()
    factor_found = None

    try:
        factor_found = probe_semiprime_with_timeout(
            n_str,
            trials=trials,
            timeout_seconds=timeout_seconds,
            enable_error_compensation=True
        )
    except TimeoutError:
        print(f"⏰ TIMEOUT: Exceeded {timeout_minutes} minute limit")
    except Exception as e:
        print(f"⚠️ ERROR: Factorization error: {e}")

    end_time = time.time()
    runtime_seconds = end_time - start_time

    result = {
        'digits': len(n_str),
        'enhanced_k_est': k_est,
        'k_est_order': k_order,
        'factor_found': factor_found,
        'runtime_seconds': runtime_seconds,
        'runtime_minutes': runtime_seconds / 60,
        'trials_attempted': trials,
        'timeout_seconds': timeout_seconds,
        'algorithm_used': 'Enhanced Z5D with error compensation',
        'precision_used': 'High precision arithmetic (mpmath)',
        'status': 'SUCCESS - Factor found' if factor_found else 'No factor detected'
    }

    print(f"\nRESULTS:")
    print(f"Runtime: {runtime_seconds:.3f}s ({runtime_seconds/60:.2f} minutes)")
    print(f"Factor found: {factor_found}")
    print(f"Status: {result['status']}")

    factors_tuple = None

    if factor_found:
        print("\n🎉 SUCCESS: FACTOR DISCOVERED FOR RSA-129!")
        print("=" * 50)

        n = int(n_str)
        if n % factor_found == 0:
            other_factor = n // factor_found
            factors_tuple = (factor_found, other_factor)

            print("✓ VERIFIED FACTORS:")
            print(f"  Factor 1: {factor_found}")
            print(f"  Factor 2: {other_factor}")
            print(f"  Factor 1 digits: {len(str(factor_found))}")
            print(f"  Factor 2 digits: {len(str(other_factor))}")
            print(f"  Verification: {factor_found} × {other_factor} = RSA-129")

            product = factor_found * other_factor
            if product == n:
                print("✓ Double verification: Product equals original RSA-129")
            else:
                print("⚠️ Verification error: Product does not match RSA-129")

        else:
            print("⚠️ WARNING: Factor verification failed!")
            print(f"Factor {factor_found} does not divide RSA-129")
    else:
        print("\nNo factor detected in this attempt.")
        print("RSA-129 may require more trials or different parameters.")

    log_rsa129_attempt(result, factors_tuple)

    return result

def main():
    """Main execution."""
    print("RSA-129 Factorization Using Enhanced Z5D Algorithms")

    result = attempt_rsa129_factorization(trials=1000, timeout_minutes=30)

    print("\n" + "=" * 80)
    print("FACTORIZATION ATTEMPT COMPLETE")
    print("=" * 80)
    print(f"Total runtime: {result['runtime_seconds']:.1f}s")
    print(f"Algorithm: {result['algorithm_used']}")
    print(f"Final status: {result['status']}")

    if result['factor_found']:
        print("\n🎉 RSA-129 FACTORIZATION SUCCESSFUL!")
    else:
        print("\nNo factors found. May need more trials or parameter tuning.")

    print("\nDetailed log saved to: rsa129_factorization_log.json")

if __name__ == "__main__":
    main()