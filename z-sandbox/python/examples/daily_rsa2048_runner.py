#!/usr/bin/env python3
"""
Daily RSA-2048 Gap Reduction Runner
===================================

Executes the daily workflow from DAILY_TASK.md:
1. Reproduce baselines (bias, comb)
2. Unbreak combined pipeline
3. Single-pass log-scale fine bias
4. Comb resolution micro-tuning
5. Crest localization (analytic only)
6. Window width sanity
7. Two-pass re-center (optional)
8. Snapshot

PURE RESONANCE compliance:
- CPU-only, deterministic
- No GNFS/ECM, no gcd/trial-division
- No ±R integer scans
"""

import sys
import os
import json
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

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

# Hardcoded RSA-2048 test case
N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637
P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459
Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143

def compute_metrics(candidates: List[Any], mechanism: str, params: Dict[str, Any]) -> Tuple[float, int, int]:
    """
    Compute metrics for a factorization result.

    Returns: (rel_distance, abs_distance, best_candidate)
    """
    best_candidate = None
    best_distance = float('inf')

    for cand in candidates:
        # Check distance to both P_TRUE and Q_TRUE
        dist_p = abs(cand.p_candidate - P_TRUE)
        dist_q = abs(cand.p_candidate - Q_TRUE)
        min_dist = min(dist_p, dist_q)

        if min_dist < best_distance:
            best_distance = min_dist
            best_candidate = cand.p_candidate

    if best_candidate is None:
        return float('inf'), float('inf'), 0

    # Compute final metrics using closest true factor
    dist_to_p = abs(best_candidate - P_TRUE)
    dist_to_q = abs(best_candidate - Q_TRUE)

    if dist_to_p < dist_to_q:
        abs_distance = dist_to_p
        rel_distance = dist_to_p / P_TRUE
    else:
        abs_distance = dist_to_q
        rel_distance = dist_to_q / Q_TRUE

    return rel_distance, abs_distance, best_candidate

def run_bias_only(embedding_offset: float = 0.0) -> Dict[str, Any]:
    """Run bias-only mode."""
    print("Running BIAS-ONLY mode...")

    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_kappa_weight=True,
        use_bias_model=True,
        profile="balanced_2048",
        use_fractional_comb=False,  # DISABLED
        embedding_offset=embedding_offset
    )

    start_time = time.time()
    result = factorize_greens(N_TEST, k=0.25, config=config, max_candidates=1000)
    runtime_s = time.time() - start_time

    rel_distance, abs_distance, best_candidate = compute_metrics(
        result['candidates'],
        'bias',
        {'embedding_offset': embedding_offset}
    )

    return {
        'mechanism': 'bias',
        'rel_distance': rel_distance,
        'abs_distance': abs_distance,
        'best_candidate': best_candidate,
        'params': {'embedding_offset': embedding_offset},
        'runtime_s': runtime_s
    }

def run_comb_only(comb_step: float = 0.001, comb_range: int = 1) -> Dict[str, Any]:
    """Run comb-only mode."""
    print(f"Running COMB-ONLY mode (step={comb_step}, range={comb_range})...")

    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_kappa_weight=True,
        use_bias_model=False,  # DISABLED
        use_fractional_comb=True,
        comb_step=comb_step,
        comb_range=comb_range
    )

    start_time = time.time()
    max_candidates = int((2 * comb_range) / comb_step) + 1
    result = factorize_greens(N_TEST, k=0.25, config=config, max_candidates=max_candidates)
    runtime_s = time.time() - start_time

    rel_distance, abs_distance, best_candidate = compute_metrics(
        result['candidates'],
        'comb',
        {'comb_step': comb_step, 'comb_range': comb_range}
    )

    return {
        'mechanism': 'comb',
        'rel_distance': rel_distance,
        'abs_distance': abs_distance,
        'best_candidate': best_candidate,
        'params': {
            'comb_step': comb_step,
            'comb_range': comb_range
        },
        'runtime_s': runtime_s
    }

def run_combined(embedding_offset: float = 0.0, comb_step: float = 0.001,
                 comb_range: int = 1) -> Dict[str, Any]:
    """Run combined mode: bias → re-center → comb."""
    print(f"Running COMBINED mode (offset={embedding_offset}, step={comb_step}, range={comb_range})...")

    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_kappa_weight=True,
        use_bias_model=True,  # ENABLED
        profile="balanced_2048",
        embedding_offset=embedding_offset,
        use_fractional_comb=True,  # ENABLED
        comb_step=comb_step,
        comb_range=comb_range
    )

    start_time = time.time()
    max_candidates = int((2 * comb_range) / comb_step) + 1
    result = factorize_greens(N_TEST, k=0.25, config=config, max_candidates=max_candidates)
    runtime_s = time.time() - start_time

    rel_distance, abs_distance, best_candidate = compute_metrics(
        result['candidates'],
        'combined',
        {
            'embedding_offset': embedding_offset,
            'comb_step': comb_step,
            'comb_range': comb_range
        }
    )

    return {
        'mechanism': 'combined',
        'rel_distance': rel_distance,
        'abs_distance': abs_distance,
        'best_candidate': best_candidate,
        'params': {
            'embedding_offset': embedding_offset,
            'comb_step': comb_step,
            'comb_range': comb_range
        },
        'runtime_s': runtime_s
    }

def write_tsv_row(f, result: Dict[str, Any]):
    """Write a single TSV row."""
    timestamp = datetime.now().isoformat()
    mechanism = result['mechanism']
    rel_distance = result['rel_distance']
    abs_distance = result['abs_distance']
    params = json.dumps(result['params'])
    json_notes = json.dumps({'best_candidate': str(result['best_candidate'])})
    runtime_s = result['runtime_s']

    f.write(f"{timestamp}\t{mechanism}\t{rel_distance}\t{abs_distance}\t{params}\t{json_notes}\t{runtime_s}\n")

def main():
    """Execute the daily workflow."""
    print("=" * 80)
    print("DAILY RSA-2048 GAP REDUCTION RUNNER")
    print("=" * 80)
    print()

    results = []

    # Create output directories
    os.makedirs('results', exist_ok=True)
    os.makedirs('params', exist_ok=True)
    os.makedirs('notes', exist_ok=True)

    # Open TSV file
    tsv_path = 'results/2025-11-05.tsv'
    jsonl_path = 'results/2025-11-05.jsonl'

    with open(tsv_path, 'w') as tsv_file:
        # Write TSV header
        tsv_file.write("# DAILY RSA-2048 GAP REDUCTION\n")
        tsv_file.write(f"# Date: {datetime.now().isoformat()}\n")
        tsv_file.write("# Commit: (add git commit hash here)\n")
        tsv_file.write("# Python version: (add version here)\n")
        tsv_file.write("# mpmath version: (add version here)\n")
        tsv_file.write("timestamp\tmechanism\trel_distance\tabs_distance\tparams\tjson_notes\truntime_s\n")

        # STEP 1: Reproduce baselines
        print("\n" + "=" * 80)
        print("STEP 1: Reproduce baselines")
        print("=" * 80)

        # Run bias-only
        bias_result = run_bias_only(embedding_offset=0.0)
        results.append(bias_result)
        write_tsv_row(tsv_file, bias_result)
        print(f"✓ Bias: rel={bias_result['rel_distance']:.6f} ({bias_result['rel_distance']*100:.4f}%), abs={bias_result['abs_distance']}")

        # Run comb-only
        comb_result = run_comb_only(comb_step=0.001, comb_range=1)
        results.append(comb_result)
        write_tsv_row(tsv_file, comb_result)
        print(f"✓ Comb: rel={comb_result['rel_distance']:.6f} ({comb_result['rel_distance']*100:.4f}%), abs={comb_result['abs_distance']}")

        # STEP 2: Unbreak combined pipeline
        print("\n" + "=" * 80)
        print("STEP 2: Unbreak combined pipeline")
        print("=" * 80)

        combined_result = run_combined(embedding_offset=0.0, comb_step=0.001, comb_range=1)
        results.append(combined_result)
        write_tsv_row(tsv_file, combined_result)
        print(f"✓ Combined: rel={combined_result['rel_distance']:.6f} ({combined_result['rel_distance']*100:.4f}%), abs={combined_result['abs_distance']}")

        # Check monotonicity
        baseline_max = max(bias_result['rel_distance'], comb_result['rel_distance'])
        if combined_result['rel_distance'] > baseline_max:
            print(f"⚠️  WARNING: Combined ({combined_result['rel_distance']:.6f}) > max(bias, comb) ({baseline_max:.6f})")
            print("   Stopping per DAILY_TASK.md guardrails")
            return

        print(f"✓ Monotonicity check passed: combined ≤ max(bias, comb)")

        # STEP 3: Single-pass log-scale fine bias
        print("\n" + "=" * 80)
        print("STEP 3: Single-pass log-scale fine bias")
        print("=" * 80)

        # Try 3 embedding offset values within bounds [-0.002, 0]
        embedding_offset_values = [-0.002, -0.001, -0.0005]
        best_embedding_offset = 0.0
        best_embedding_offset_result = combined_result

        for eo in embedding_offset_values:
            eo_result = run_combined(embedding_offset=eo, comb_step=0.001, comb_range=1)
            results.append(eo_result)
            write_tsv_row(tsv_file, eo_result)
            print(f"  Embedding offset={eo}: rel={eo_result['rel_distance']:.6f} ({eo_result['rel_distance']*100:.4f}%), abs={eo_result['abs_distance']}")

            if eo_result['rel_distance'] < best_embedding_offset_result['rel_distance']:
                best_embedding_offset = eo
                best_embedding_offset_result = eo_result

        print(f"✓ Best embedding offset: {best_embedding_offset}")

        # STEP 4: Comb resolution micro-tuning
        print("\n" + "=" * 80)
        print("STEP 4: Comb resolution micro-tuning")
        print("=" * 80)

        comb_steps = [1e-3, 5e-4, 1e-4]
        best_comb_step = 0.001
        best_comb_step_result = best_embedding_offset_result

        for cs in comb_steps:
            cs_result = run_combined(embedding_offset=best_embedding_offset, comb_step=cs, comb_range=1)
            results.append(cs_result)
            write_tsv_row(tsv_file, cs_result)
            print(f"  Comb step={cs}: rel={cs_result['rel_distance']:.6f} ({cs_result['rel_distance']*100:.4f}%), abs={cs_result['abs_distance']}")

            if cs_result['rel_distance'] < best_comb_step_result['rel_distance']:
                best_comb_step = cs
                best_comb_step_result = cs_result

        print(f"✓ Best comb step: {best_comb_step}")

        # STEP 5: Crest localization (skip for now - needs implementation)
        print("\n" + "=" * 80)
        print("STEP 5: Crest localization")
        print("=" * 80)
        print("  (Quadratic vertex interpolation - TODO)")

        # STEP 6: Two-pass re-center
        print("\n" + "=" * 80)
        print("STEP 6: Two-pass re-center")
        print("=" * 80)

        improvement_pct = (combined_result['rel_distance'] - best_comb_step_result['rel_distance']) / combined_result['rel_distance'] * 100
        print(f"  Current improvement: {improvement_pct:.2f}%")

        if improvement_pct >= 2.0:
            print("  ✓ Improvement ≥2%, would try second re-center pass")
            print("    (Re-centering - TODO)")
        else:
            print("  Skip second re-center (improvement <2%)")

    # STEP 7: Write artifacts
    print("\n" + "=" * 80)
    print("STEP 7: Write artifacts")
    print("=" * 80)

    # Write JSONL
    with open(jsonl_path, 'w') as jsonl_file:
        for r in results:
            jsonl_file.write(json.dumps(r) + '\n')

    # Write best params
    best_result = min(results, key=lambda r: r['rel_distance'])
    params_path = 'params/2025-11-05_best.json'
    with open(params_path, 'w') as params_file:
        json.dump(best_result['params'], params_file, indent=2)

    # Write notes
    notes_path = 'notes/2025-11-05.md'
    with open(notes_path, 'w') as notes_file:
        notes_file.write("# Daily Notes — 2025-11-05\n\n")
        notes_file.write(f"**Best result:** {best_result['mechanism']} with rel_distance={best_result['rel_distance']:.6f}\n\n")
        notes_file.write(f"**What worked:**\n")
        notes_file.write(f"- Embedding offset: {best_embedding_offset}\n")
        notes_file.write(f"- Comb step: {best_comb_step}\n\n")
        notes_file.write(f"**What didn't:**\n")
        notes_file.write(f"- (Add observations)\n\n")
        notes_file.write(f"**Next knob to try:**\n")
        notes_file.write(f"- (Add recommendation)\n")

    print(f"✓ TSV: {tsv_path}")
    print(f"✓ JSONL: {jsonl_path}")
    print(f"✓ Params: {params_path}")
    print(f"✓ Notes: {notes_path}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total runs: {len(results)}")
    print(f"Best rel_distance: {best_result['rel_distance']:.6f} ({best_result['rel_distance']*100:.4f}%)")
    print(f"Best abs_distance: {best_result['abs_distance']}")
    print(f"Within ±1000: {best_result['abs_distance'] <= 1000}")
    print(f"Mechanism: {best_result['mechanism']}")
    print(f"Params: {json.dumps(best_result['params'], indent=2)}")

if __name__ == "__main__":
    main()
