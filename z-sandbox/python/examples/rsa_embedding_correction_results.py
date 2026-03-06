#!/usr/bin/env python3
"""
RSA Embedding Bias Correction Results
=====================================

Re-run harness with second-order bias model on all calibration moduli.
Generate results showing post-correction residuals and 1000-window feasibility.
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

# Test moduli from calibration
TEST_MODULI = [
    {
        "N": 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637,
        "p_true": 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459,
        "q_true": 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143,
        "profile": "balanced_2048_a"
    },
    {
        "N": 2213,  # 43 * 47
        "p_true": 43,
        "q_true": 47,
        "profile": "balanced_8_test"
    },
    {
        "N": 11413,  # 101 * 113
        "p_true": 101,
        "q_true": 113,
        "profile": "balanced_14_test"
    },
    {
        "N": 391,  # 17 * 23
        "p_true": 17,
        "q_true": 23,
        "profile": "skewed_9_test"
    }
]

def run_corrected_harness(N: int, p_true: int, q_true: int, profile: str) -> Dict[str, Any]:
    """Run harness with second-order bias correction."""
    print(f"Running corrected harness for {profile}...")

    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_dual_k=False,
        use_kappa_weight=True,
        use_adaptive_k=False,
        use_bias_model=True,
        profile=profile
    )

    result = factorize_greens(N, k=0.25, config=config, max_candidates=20)

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

    # Compute metrics
    abs_distance = abs(best_candidate - p_true)
    rel_distance = abs_distance / p_true
    within_1000_window = abs_distance <= 1000

    record = {
        "profile": profile,
        "N_bits": N.bit_length(),
        "p_bits": p_true.bit_length(),
        "best_rel_distance": float(rel_distance),
        "abs_distance": int(abs_distance),
        "within_1000_window": within_1000_window,
        "best_candidate": int(best_candidate),
        "p_true": int(p_true)
    }

    print(f"  Best rel distance: {rel_distance:.6f}")
    print(f"  Within ±1000: {within_1000_window}")

    return record

def main():
    """Generate correction results."""
    print("=" * 80)
    print("RSA EMBEDDING BIAS CORRECTION RESULTS")
    print("=" * 80)
    print()
    print("Running harness with second-order bias model on all calibration moduli...")
    print()

    results = []
    for modulus in TEST_MODULI:
        record = run_corrected_harness(
            modulus["N"],
            modulus["p_true"],
            modulus["q_true"],
            modulus["profile"]
        )
        if record:
            results.append(record)
        print()

    # Write results
    output_path = os.path.join(os.path.dirname(__file__), '../..', 'docs', 'geometric_embedding_bias_correction_results.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print("CORRECTION RESULTS GENERATED")
    print("=" * 80)
    print(f"Results written to: {output_path}")
    print()

    # Print summary
    print("Summary Table:")
    print(f"{'Profile':<20} | {'Rel Dist':<10} | {'Abs Dist':<15} | {'±1000 OK':<10}")
    print("-" * 60)
    for record in results:
        within_str = "✓" if record['within_1000_window'] else "✗"
        print(f"{record['profile']:<20} | {record['best_rel_distance']:<10.6f} | {record['abs_distance']:<15} | {within_str:<10}")

    print()
    print("Next: Analyze results and iterate on bias model if needed.")


if __name__ == "__main__":
    main()