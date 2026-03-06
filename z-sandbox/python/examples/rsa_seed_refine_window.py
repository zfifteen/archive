#!/usr/bin/env python3
"""
RSA Seed Refinement Window
==========================

Finisher-assisted phase: Take best seed from resonance sweeps and run
bounded ±R divisibility refinement to attempt factor recovery.

This script is separate from pure resonance sweeps to maintain methodological purity.

Usage: python3 rsa_seed_refine_window.py --seed <seed> --R <radius>
"""

import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, List, Any

# Hardcoded RSA-2048 test case
N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637
P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459
Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143

# Phase marker for CI
PHASE = "FINISHER_ASSISTED"


def run_refinement(seed: int, R: int, N: int = N_TEST) -> Dict[str, Any]:
    """Run bounded ±R divisibility refinement around seed."""
    print(f"Running ±{R} refinement around seed {seed}")
    print(f"Search range: [{max(2, seed - R)}, {seed + R}]")
    print(f"Candidates to check: {2 * R + 1}")
    print()

    candidates_checked = 0
    found_factor = False
    factor_found = None
    offset_from_seed = None

    search_min = max(2, seed - R)
    search_max = seed + R

    for candidate in range(search_min, search_max + 1):
        candidates_checked += 1

        # Test divisibility
        if N % candidate == 0:
            found_factor = True
            factor_found = candidate
            offset_from_seed = candidate - seed
            break

    # Verify if found
    if found_factor and factor_found is not None:
        other_factor = N // factor_found
        verification = (factor_found * other_factor == N)
        true_factor = factor_found if factor_found in [P_TRUE, Q_TRUE] else other_factor
        is_correct = true_factor in [P_TRUE, Q_TRUE]
    else:
        verification = False
        is_correct = False

    return {
        'seed': seed,
        'R': R,
        'candidates_checked': candidates_checked,
        'found_factor': found_factor,
        'factor_found': factor_found,
        'offset_from_seed': offset_from_seed,
        'verification': verification,
        'is_correct_factor': is_correct,
        'search_range': [search_min, search_max]
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RSA seed refinement window")
    parser.add_argument('--seed', type=int, required=True, help='Seed to refine around')
    parser.add_argument('--R', type=int, default=1000, help='Refinement radius (±R)')
    parser.add_argument('--N', type=int, help='Semiprime N (default: hardcoded RSA-2048)')

    args = parser.parse_args()

    N = args.N if args.N else N_TEST
    seed = args.seed
    R = args.R

    print("=" * 80)
    print("RSA SEED REFINEMENT WINDOW")
    print("=" * 80)
    print()
    print(f"Phase: {PHASE}")
    print(f"N: {N.bit_length()}-bit semiprime")
    print(f"Seed: {seed}")
    print(f"Radius: ±{R}")
    print()

    result = run_refinement(seed, R, N)

    print("=" * 80)
    print("REFINEMENT RESULTS")
    print("=" * 80)
    print()

    if result['found_factor']:
        print("✅ FACTOR FOUND!")
        print(f"  Factor: {result['factor_found']}")
        print(f"  Offset from seed: {result['offset_from_seed']:+d}")
        print(f"  Verification: {'✓' if result['verification'] else '✗'}")
        print(f"  Correct factor: {'✓' if result['is_correct_factor'] else '✗'}")
        if result['is_correct_factor']:
            print("  🎉 SUCCESS: Recovered true RSA factor!")
        else:
            print("  ⚠️  Found divisor, but not a true RSA factor")
    else:
        print("❌ No factor found within ±R")
        print(f"  Candidates checked: {result['candidates_checked']}")

    print()
    print("Search details:")
    print(f"  Range: [{result['search_range'][0]}, {result['search_range'][1]}]")
    print(f"  Total candidates: {result['candidates_checked']}")
    print()

    # Machine-readable output
    print("=" * 80)
    print("MACHINE-READABLE RESULTS")
    print("=" * 80)
    print()
    import json
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()