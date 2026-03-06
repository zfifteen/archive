#!/usr/bin/env python3
"""
RSA K-Sweep Variance Characterization
=====================================

Characterizes variance in k-sweep results across multiple RNG seeds.
Tests whether the ~4% wall is structural (stable) or stochastic (luck-based).

This script repeats the k-sweep for multiple seeds and computes:
- Min/median/max relative distance per k_base
- Stability metrics (spread, 95% CI)
- Global best across all seeds

Usage: python3 rsa_k_sweep_variance.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import math
import json
from typing import Dict, List, Any
from python.greens_function_factorization import (
    factorize_greens,
    estimate_k_optimal,
    RefinementConfig
)

# Hardcoded RSA-2048 test case (same as benchmark)
N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637
P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459
Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143

# Configuration
K_BASES = [0.250 + i * 0.010 for i in range(11)]  # 0.250 to 0.350
DETUNE_PCT = 0.005  # ±0.5%
VARIANCE_SEEDS = [1337, 1338, 1339, 1340]  # 4 seeds for variance analysis
MAX_SEEDS = 20


def get_closest_true_factor(seed: int) -> int:
    """Determine which true factor is closest to the seed."""
    dist_p = abs(seed - P_TRUE)
    dist_q = abs(seed - Q_TRUE)
    return P_TRUE if dist_p < dist_q else Q_TRUE


def compute_distance_metrics(seed: int, true_factor: int) -> Dict[str, Any]:
    """Compute distance metrics."""
    abs_distance = abs(seed - true_factor)
    rel_distance = abs_distance / true_factor
    return {
        'abs_distance': abs_distance,
        'rel_distance': rel_distance
    }


def run_single_k_sweep(k_base: float, rng_seed: int) -> Dict[str, Any]:
    """Run k-sweep for a single k_base with detunes, using fixed RNG seed."""
    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_dual_k=True,
        use_kappa_weight=True,
        use_adaptive_k=True,
        rng_seed=rng_seed
    )

    k_plus = k_base * (1 + DETUNE_PCT)
    k_minus = k_base * (1 - DETUNE_PCT)
    k_variants = [k_base, k_plus, k_minus]

    all_candidates = []
    for k in k_variants:
        try:
            result = factorize_greens(
                N_TEST,
                k=k,
                config=config,
                max_candidates=MAX_SEEDS
            )
            for cand in result['candidates']:
                all_candidates.append({
                    'p_candidate': cand.p_candidate,
                    'score': cand.score,
                    'k_used': k,
                    'variant': 'k_base' if k == k_base else ('k_plus' if k == k_plus else 'k_minus')
                })
        except Exception as e:
            print(f"Warning: Failed for k={k}, seed={rng_seed}: {e}")
            continue

    # Find best distance for this k_base
    if not all_candidates:
        return {
            'k_base': k_base,
            'k_plus': k_plus,
            'k_minus': k_minus,
            'best_rel_distance': None,
            'best_abs_distance': None,
            'best_seed_source': None,
            'num_seeds_total': 0,
            'rng_seed': rng_seed
        }

    best_rel = float('inf')
    best_abs = float('inf')
    best_source = None

    for cand in all_candidates:
        true_factor = get_closest_true_factor(cand['p_candidate'])
        metrics = compute_distance_metrics(cand['p_candidate'], true_factor)
        if metrics['rel_distance'] < best_rel:
            best_rel = metrics['rel_distance']
            best_abs = metrics['abs_distance']
            best_source = cand['variant']

    return {
        'k_base': k_base,
        'k_plus': k_plus,
        'k_minus': k_minus,
        'best_rel_distance': best_rel,
        'best_abs_distance': best_abs,
        'best_seed_source': best_source,
        'num_seeds_total': len(all_candidates),
        'rng_seed': rng_seed
    }


def compute_variance_stats(results_per_seed: List[Dict]) -> Dict[str, Any]:
    """Compute variance statistics across seeds."""
    if not results_per_seed:
        return {}

    rel_distances = [r['best_rel_distance'] for r in results_per_seed if r['best_rel_distance'] is not None]
    if not rel_distances:
        return {'error': 'No valid distances'}

    # Basic stats
    min_dist = min(rel_distances)
    max_dist = max(rel_distances)
    median_dist = sorted(rel_distances)[len(rel_distances) // 2]
    mean_dist = sum(rel_distances) / len(rel_distances)

    # Spread (max - min)
    spread = max_dist - min_dist

    # Simple 95% CI approximation (assuming normal-ish distribution)
    import statistics
    if len(rel_distances) > 1:
        stdev = statistics.stdev(rel_distances)
        ci_95 = 1.96 * stdev / math.sqrt(len(rel_distances))
    else:
        ci_95 = 0

    return {
        'min': min_dist,
        'max': max_dist,
        'median': median_dist,
        'mean': mean_dist,
        'spread': spread,
        'ci_95': ci_95,
        'sample_size': len(rel_distances)
    }


def run_variance_analysis() -> Dict[str, Any]:
    """Run full variance analysis across seeds and k_bases."""
    print("=" * 80)
    print("RSA K-SWEEP VARIANCE CHARACTERIZATION")
    print("=" * 80)
    print()
    print(f"Testing N = {N_TEST.bit_length()}-bit RSA semiprime")
    print(f"K bases: {len(K_BASES)} values from {K_BASES[0]} to {K_BASES[-1]}")
    print(f"Detune: ±{DETUNE_PCT*100}% per k_base")
    print(f"Variance seeds: {VARIANCE_SEEDS}")
    print()

    # Run sweeps for each seed
    all_results = {}
    global_best_rel = float('inf')
    global_best_k = None
    global_best_seed = None

    for rng_seed in VARIANCE_SEEDS:
        print(f"Running k-sweep with RNG seed {rng_seed}...")
        seed_results = []
        for k_base in K_BASES:
            result = run_single_k_sweep(k_base, rng_seed)
            seed_results.append(result)

            # Track global best
            if result['best_rel_distance'] is not None and result['best_rel_distance'] < global_best_rel:
                global_best_rel = result['best_rel_distance']
                global_best_k = k_base
                global_best_seed = rng_seed

        all_results[rng_seed] = seed_results
        print(f"  Completed {len(seed_results)} k_base evaluations")
        print()

    # Compute per-k_base variance
    per_k_stats = {}
    for i, k_base in enumerate(K_BASES):
        results_for_k = [all_results[seed][i] for seed in VARIANCE_SEEDS]
        stats = compute_variance_stats(results_for_k)
        per_k_stats[k_base] = stats

    # Output results
    print("=" * 80)
    print("VARIANCE ANALYSIS RESULTS")
    print("=" * 80)
    print()

    print("Per-K Variance Statistics:")
    print(f"{'k_base':>6} | {'Min':>10} | {'Median':>10} | {'Max':>10} | {'Spread':>10} | {'95% CI':>10}")
    print("-" * 80)
    for k_base, stats in per_k_stats.items():
        if 'error' in stats:
            print(f"{k_base:6.3f} | {'ERROR':>10} | {'ERROR':>10} | {'ERROR':>10} | {'ERROR':>10} | {'ERROR':>10}")
        else:
            print(f"{k_base:6.3f} | {stats['min']:10.6f} | {stats['median']:10.6f} | {stats['max']:10.6f} | {stats['spread']:10.6f} | {stats['ci_95']:10.6f}")
    print()

    print("Global Statistics:")
    print(f"  Best relative distance: {global_best_rel:.6f}")
    print(f"  Achieved at k_base: {global_best_k}")
    print(f"  With RNG seed: {global_best_seed}")
    print()

    # Assess stability
    spreads = [stats.get('spread', 0) for stats in per_k_stats.values()]
    avg_spread = sum(spreads) / len(spreads) if spreads else 0
    max_spread = max(spreads) if spreads else 0

    print("Stability Assessment:")
    print(f"  Average spread across k_bases: {avg_spread:.6f}")
    print(f"  Maximum spread: {max_spread:.6f}")
    if avg_spread < 0.001:  # <0.1% variation
        print("  CONCLUSION: Wall appears STRUCTURAL (stable across seeds)")
    elif avg_spread < 0.01:  # <1% variation
        print("  CONCLUSION: Moderate variance; wall may be partially stochastic")
    else:
        print("  CONCLUSION: High variance; wall appears STOCHASTIC (luck-based)")
    print()

    # Build return dict
    return {
        'N_bits': N_TEST.bit_length(),
        'variance_seeds': VARIANCE_SEEDS,
        'k_bases': K_BASES,
        'detune_pct': DETUNE_PCT,
        'per_k_stats': per_k_stats,
        'global_best_rel_distance': global_best_rel,
        'global_best_k_base': global_best_k,
        'global_best_seed': global_best_seed,
        'avg_spread': avg_spread,
        'max_spread': max_spread,
        'stability_conclusion': 'structural' if avg_spread < 0.001 else ('moderate' if avg_spread < 0.01 else 'stochastic')
    }


def main():
    """Main entry point."""
    results = run_variance_analysis()

    # Print machine-readable summary
    print("=" * 80)
    print("MACHINE-READABLE RESULTS")
    print("=" * 80)
    print()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()