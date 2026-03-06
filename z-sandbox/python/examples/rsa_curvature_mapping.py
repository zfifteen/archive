#!/usr/bin/env python3
"""
RSA Curvature Mapping Sweeps
============================

Maps local curvature around the attractor to identify knobs that bend the 4% wall.
Performs targeted sweeps of k, detunes, and secondary parameters.

This script evaluates:
- Fine k-zoom around best k_base
- Wider detune ranges
- Secondary parameter sweeps (κ-weight, φ-bias, Dirichlet window)

Usage: python3 rsa_curvature_mapping.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import math
import json
from dataclasses import replace
from typing import Dict, List, Any

try:
    from python.greens_function_factorization import (
        factorize_greens,
        estimate_k_optimal,
        RefinementConfig
    )
except ImportError:
    from greens_function_factorization import (
        factorize_greens,
        estimate_k_optimal,
        RefinementConfig
    )

# Hardcoded RSA-2048 test case
N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637
P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459
Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143

# Configuration constants
BEST_K_BASE = 0.250  # From baseline analysis
K_FINE_MIN = 0.245
K_FINE_MAX = 0.255
K_FINE_STEP = 0.0005
DETUNE_PCT_VALUES = [-0.02, -0.01, -0.005, 0.0, +0.005, +0.01, +0.02]  # ±2%, ±1%, ±0.5%
MAX_SEEDS = 20
RNG_SEED = 1337  # Fixed for reproducibility


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


def run_single_sweep(k: float, detune_pct: float, config: RefinementConfig) -> Dict[str, Any]:
    """Run a single factorization with given k, detune, and config."""
    try:
        result = factorize_greens(
            N_TEST,
            k=k,
            config=config,
            max_candidates=20
        )

        # Find best distance
        best_rel = float('inf')
        best_abs = float('inf')
        best_score = 0

        for cand in result['candidates']:
            true_factor = get_closest_true_factor(cand.p_candidate)
            metrics = compute_distance_metrics(cand.p_candidate, true_factor)
            if metrics['rel_distance'] < best_rel:
                best_rel = metrics['rel_distance']
                best_abs = metrics['abs_distance']
                best_score = cand.score

        return {
            'k': k,
            'detune_pct': detune_pct,
            'best_rel_distance': best_rel,
            'best_abs_distance': best_abs,
            'best_score': best_score,
            'num_candidates': len(result['candidates']),
            'status': 'success'
        }
    except Exception as e:
        return {
            'k': k,
            'detune_pct': detune_pct,
            'best_rel_distance': None,
            'best_abs_distance': None,
            'best_score': None,
            'num_candidates': 0,
            'status': 'error',
            'error_msg': str(e)
        }


def sweep_fine_k() -> List[Dict[str, Any]]:
    """Fine k-zoom around BEST_K_BASE."""
    print("Running fine k-zoom sweep...")
    results = []
    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_dual_k=True,
        use_kappa_weight=True,
        use_adaptive_k=True,
        rng_seed=RNG_SEED
    )

    k_values = [K_FINE_MIN + i * K_FINE_STEP for i in range(int((K_FINE_MAX - K_FINE_MIN) / K_FINE_STEP) + 1)]

    for k in k_values:
        result = run_single_sweep(k, 0.0, config)  # No detune for fine k
        results.append(result)
        if result['status'] == 'error':
            print(f"  Warning: k={k} failed - {result['error_msg']}")

    print(f"  Completed {len(results)} fine k evaluations")
    return results


def sweep_wider_detunes() -> List[Dict[str, Any]]:
    """Wider detune sweep around BEST_K_BASE."""
    print("Running wider detune sweep...")
    results = []
    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_dual_k=True,
        use_kappa_weight=True,
        use_adaptive_k=True,
        rng_seed=RNG_SEED
    )

    for detune_pct in DETUNE_PCT_VALUES:
        k = BEST_K_BASE * (1 + detune_pct)
        result = run_single_sweep(k, detune_pct, config)
        results.append(result)
        if result['status'] == 'error':
            print(f"  Warning: detune={detune_pct*100}% failed - {result['error_msg']}")

    print(f"  Completed {len(results)} detune evaluations")
    return results


def sweep_secondary_params() -> Dict[str, List[Dict[str, Any]]]:
    """Sweep secondary parameters with k fixed."""
    print("Running secondary parameter sweeps...")
    base_config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_dual_k=True,
        use_kappa_weight=True,
        use_adaptive_k=True,
        rng_seed=RNG_SEED
    )

    results = {}

    # κ-weight scale sweep
    print("  Sweeping κ-weight scale...")
    kappa_results = []
    for scale in [0.5, 0.75, 1.0, 1.25, 1.5]:
        config = replace(base_config, kappa_weight_scale=scale)
        result = run_single_sweep(BEST_K_BASE, 0.0, config)
        result['param_name'] = 'kappa_weight_scale'
        result['param_value'] = scale
        kappa_results.append(result)

    # φ-bias sweep
    print("  Sweeping φ-bias...")
    phi_results = []
    for phi in [1.0, 1.2, 1.4, 1.618, 1.8, 2.0]:  # Include golden ratio
        config = replace(base_config, phi_bias=phi)
        result = run_single_sweep(BEST_K_BASE, 0.0, config)
        result['param_name'] = 'phi_bias'
        result['param_value'] = phi
        phi_results.append(result)
    results['phi_bias'] = phi_results

    # Dirichlet window sweep
    print("  Sweeping Dirichlet window...")
    dirichlet_results = []
    for window in [2, 4, 6, 8, 10]:
        config = replace(base_config, dirichlet_J=window)
        result = run_single_sweep(BEST_K_BASE, 0.0, config)
        result['param_name'] = 'dirichlet_J'
        result['param_value'] = window
        dirichlet_results.append(result)
    results['dirichlet_window'] = dirichlet_results

    print(f"  Completed secondary parameter sweeps")
    return results


def analyze_wall_breaking(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze which sweeps bend the 4% wall."""
    baseline_wall = 0.04  # 4% from baseline

    analysis = {
        'baseline_wall': baseline_wall,
        'wall_breakers': [],
        'best_improvement': 0,
        'best_param': None,
        'best_value': None
    }

    # Check fine k results
    fine_k_best = min((r['best_rel_distance'] for r in results['fine_k'] if r['best_rel_distance']), default=float('inf'))
    if fine_k_best < baseline_wall:
        improvement = baseline_wall - fine_k_best
        analysis['wall_breakers'].append({
            'sweep': 'fine_k',
            'best_rel_distance': fine_k_best,
            'improvement': improvement
        })
        if improvement > analysis['best_improvement']:
            analysis['best_improvement'] = improvement
            analysis['best_param'] = 'fine_k'
            analysis['best_value'] = None  # Multiple values

    # Check detune results
    detune_best = min((r['best_rel_distance'] for r in results['wider_detunes'] if r['best_rel_distance']), default=float('inf'))
    if detune_best < baseline_wall:
        improvement = baseline_wall - detune_best
        analysis['wall_breakers'].append({
            'sweep': 'wider_detunes',
            'best_rel_distance': detune_best,
            'improvement': improvement
        })
        if improvement > analysis['best_improvement']:
            analysis['best_improvement'] = improvement
            analysis['best_param'] = 'wider_detunes'
            analysis['best_value'] = None

    # Check secondary params
    for param_name, param_results in results['secondary_params'].items():
        param_best = min((r['best_rel_distance'] for r in param_results if r['best_rel_distance']), default=float('inf'))
        if param_best < baseline_wall:
            improvement = baseline_wall - param_best
            best_value = next((r['param_value'] for r in param_results if r['best_rel_distance'] == param_best), None)
            analysis['wall_breakers'].append({
                'sweep': param_name,
                'best_rel_distance': param_best,
                'improvement': improvement,
                'best_value': best_value
            })
            if improvement > analysis['best_improvement']:
                analysis['best_improvement'] = improvement
                analysis['best_param'] = param_name
                analysis['best_value'] = best_value

    return analysis


def run_curvature_mapping() -> Dict[str, Any]:
    """Run full curvature mapping analysis."""
    print("=" * 80)
    print("RSA CURVATURE MAPPING SWEEPS")
    print("=" * 80)
    print()
    print(f"Testing N = {N_TEST.bit_length()}-bit RSA semiprime")
    print(f"Best k_base from baseline: {BEST_K_BASE}")
    print()

    # Run sweeps
    fine_k_results = sweep_fine_k()
    print()
    wider_detune_results = sweep_wider_detunes()
    print()
    secondary_results = sweep_secondary_params()
    print()

    # Analyze wall-breaking
    all_results = {
        'fine_k': fine_k_results,
        'wider_detunes': wider_detune_results,
        'secondary_params': secondary_results
    }

    analysis = analyze_wall_breaking(all_results)

    # Output results
    print("=" * 80)
    print("CURVATURE MAPPING RESULTS")
    print("=" * 80)
    print()

    print("Fine K-Zoom Results:")
    print(f"  Range: {K_FINE_MIN} to {K_FINE_MAX} (step {K_FINE_STEP})")
    valid_fine = [r for r in fine_k_results if r['status'] == 'success']
    if valid_fine:
        best_fine = min(valid_fine, key=lambda r: r['best_rel_distance'])
        print(f"  Best: k={best_fine['k']:.6f}, rel_dist={best_fine['best_rel_distance']:.6f}")
    else:
        print("  No valid results")
    print()

    print("Wider Detune Results:")
    print(f"  Detunes: {['{:.1%}'.format(d) for d in DETUNE_PCT_VALUES]}")
    valid_detune = [r for r in wider_detune_results if r['status'] == 'success']
    if valid_detune:
        best_detune = min(valid_detune, key=lambda r: r['best_rel_distance'])
        print(f"  Best: detune={best_detune['detune_pct']:.1%}, rel_dist={best_detune['best_rel_distance']:.6f}")
    else:
        print("  No valid results")
    print()

    print("Secondary Parameter Results:")
    for param_name, param_results in secondary_results.items():
        valid_param = [r for r in param_results if r['status'] == 'success']
        if valid_param:
            best_param = min(valid_param, key=lambda r: r['best_rel_distance'])
            print(f"  {param_name}: best_value={best_param['param_value']}, rel_dist={best_param['best_rel_distance']:.6f}")
        else:
            print(f"  {param_name}: No valid results")
    print()

    print("Wall-Breaking Analysis:")
    print(f"  Baseline wall: {analysis['baseline_wall']:.1%}")
    if analysis['wall_breakers']:
        print("  Wall-breakers found:")
        for breaker in analysis['wall_breakers']:
            print(f"    {breaker['sweep']}: {breaker['best_rel_distance']:.6f} ({breaker['improvement']:.6f} improvement)")
        print(f"  Best overall: {analysis['best_param']} (improvement: {analysis['best_improvement']:.6f})")
    else:
        print("  No wall-breakers found. All sweeps stayed above baseline.")
    print()

    # Build return dict
    return {
        'N_bits': N_TEST.bit_length(),
        'best_k_base': BEST_K_BASE,
        'fine_k_range': [K_FINE_MIN, K_FINE_MAX, K_FINE_STEP],
        'detune_values': DETUNE_PCT_VALUES,
        'results': all_results,
        'wall_analysis': analysis
    }


def main():
    """Main entry point."""
    results = run_curvature_mapping()

    # Print machine-readable summary
    print("=" * 80)
    print("MACHINE-READABLE RESULTS")
    print("=" * 80)
    print()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()