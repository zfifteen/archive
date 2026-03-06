#!/usr/bin/env python3
"""
RSA Geometric Embedding Bias Calibration
========================================

Measures residual bias after first-order geometric embedding correction.
Logs per-modulus residuals for second-order correction fitting.

This script evaluates the corrected embedding center across multiple moduli
to quantify remaining systematic bias.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Any

try:
    from python.greens_function_factorization import (
        factorize_greens,
        RefinementConfig
    )
except ImportError:
    from greens_function_factorization import (
        factorize_greens,
        RefinementConfig
    )

# Test moduli with known factors (ground truth for bias measurement)
TEST_MODULI = [
    # Balanced RSA-2048 (original)
    {
        "N": 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637,
        "p_true": 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459,
        "q_true": 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143,
        "profile": "balanced_2048_a"
    },
    # Second balanced RSA-2048 (different primes)
    {
        "N": 2213,  # Small test: 43 * 47
        "p_true": 43,
        "q_true": 47,
        "profile": "balanced_8_test"  # Small for quick validation
    },
    # Balanced RSA-1024 (smaller)
    {
        "N": 11413,  # 101 * 113
        "p_true": 101,
        "q_true": 113,
        "profile": "balanced_14_test"
    },
    # Skewed semiprime (p << q)
    {
        "N": 391,  # 17 * 23
        "p_true": 17,
        "q_true": 23,
        "profile": "skewed_9_test"
    }
]

# First-order correction (from Issue #198)
EMBEDDING_OFFSET = -0.0392  # -3.92% to reduce wall to ~0.15%

# Harness config with correction
CONFIG = RefinementConfig(
    use_phase_correction=True,
    use_dirichlet=True,
    use_dual_k=False,  # Speed for calibration
    use_kappa_weight=True,
    use_adaptive_k=False,
    rng_seed=1337,
    embedding_offset=EMBEDDING_OFFSET
)


def measure_embedding_bias(N: int, p_true: int, q_true: int, profile: str) -> Dict[str, Any]:
    """Measure residual bias for a single modulus."""
    print(f"Measuring bias for {profile} (N: {N.bit_length()} bits)...")

    # Run factorization with correction
    result = factorize_greens(N, k=0.25, config=CONFIG, max_candidates=20)

    # Find best candidate
    best_candidate = None
    best_score = 0
    for cand in result['candidates']:
        if cand.score > best_score:
            best_score = cand.score
            best_candidate = cand.p_candidate

    if best_candidate is None:
        print(f"  Warning: No candidates found for {profile}")
        return None

    # Compute errors
    candidate_abs_err = abs(best_candidate - p_true)
    candidate_rel_err = candidate_abs_err / p_true

    # For calibration, we need to estimate the embedding center
    # Since we can't directly access it, use the best candidate as proxy
    # (In pure resonance without refinement, they should be close)
    abs_bias = candidate_abs_err  # Approximation
    rel_bias = candidate_rel_err

    record = {
        "profile": profile,
        "N_bits": N.bit_length(),
        "p_bits": p_true.bit_length(),
        "q_bits": q_true.bit_length(),
        "abs_bias": int(abs_bias),
        "rel_bias": float(rel_bias),
        "candidate_abs_err": int(candidate_abs_err),
        "candidate_rel_err": float(candidate_rel_err),
        "embedding_offset_used": EMBEDDING_OFFSET,
        "best_candidate": int(best_candidate),
        "p_true": int(p_true)
    }

    print(f"  Rel bias: {rel_bias:.6f}")
    print(f"  Candidate rel err: {candidate_rel_err:.6f}")

    return record


def run_calibration() -> List[Dict[str, Any]]:
    """Run calibration across all test moduli."""
    print("=" * 80)
    print("RSA GEOMETRIC EMBEDDING BIAS CALIBRATION")
    print("=" * 80)
    print()
    print(f"First-order correction: {EMBEDDING_OFFSET*100:.1f}% embedding offset")
    print(f"Test moduli: {len(TEST_MODULI)}")
    print()

    records = []
    for modulus in TEST_MODULI:
        record = measure_embedding_bias(
            modulus["N"],
            modulus["p_true"],
            modulus["q_true"],
            modulus["profile"]
        )
        if record:
            records.append(record)
        print()

    return records


def main():
    """Main entry point."""
    records = run_calibration()

    # Write to JSON
    output_path = os.path.join(os.path.dirname(__file__), '../..', 'docs', 'geometric_embedding_bias_calibration.json')
    with open(output_path, 'w') as f:
        json.dump(records, f, indent=2)

    print("=" * 80)
    print("CALIBRATION COMPLETE")
    print("=" * 80)
    print(f"Results written to: {output_path}")
    print()

    # Print summary table
    print("Summary Table:")
    print(f"{'Profile':<20} | {'N_bits':<6} | {'Rel Bias':<10} | {'Candidate Err':<12}")
    print("-" * 60)
    for record in records:
        print(f"{record['profile']:<20} | {record['N_bits']:<6} | {record['rel_bias']:<10.6f} | {record['candidate_rel_err']:<12.6f}")

    print()
    print("Next: Use this data to fit second-order corrections.")


if __name__ == "__main__":
    main()