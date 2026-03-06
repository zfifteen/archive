#!/usr/bin/env python3
"""
RSA-Scale Factor Candidate Extraction Benchmark
================================================

This benchmark evaluates whether the Green's function resonance method
can generate high-confidence factor seeds for a 2048-bit RSA semiprime
and refine them within a practical time budget.

The script operates on a known balanced 2048-bit semiprime (N = p × q)
where p and q are ~1024-bit primes. Ground truth is used only for
evaluation metrics; the pipeline must not use them during generation.

This implementation strictly follows Issue #178 requirements:
- Stage 1: Seed Generation (Green's function resonance)
- Stage 2: Distance-to-Truth Metrics (evaluation only)
- Stage 3: Bounded Local Refinement (±R=1000, big-int modulus)
- Stage 4: Timing and Budget (60s limit)
- Stage 5: Output Format (structured report)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import time
import math
from typing import Dict, List, Any, Optional

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


# ============================================================================
# Known 2048-bit RSA-style semiprime for testing
# ============================================================================
# These values are ground truth and used ONLY for metrics evaluation
# The seed generation pipeline does NOT use p_true or q_true

N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637

P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459

Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143


# ============================================================================
# Configuration
# ============================================================================
REFINEMENT_RADIUS = 1000  # Fixed ±R window for local search (per issue requirement)
TIME_BUDGET_MS = 60000    # 60 seconds
MAX_SEEDS = 20            # Maximum number of seeds to evaluate


def compute_distance_metrics(seed: int, true_factor: int) -> Dict[str, Any]:
    """
    Compute distance metrics between a seed and true factor.
    
    Args:
        seed: Candidate seed value
        true_factor: True factor (p or q)
        
    Returns:
        Dictionary with abs_distance and rel_distance
    """
    abs_distance = abs(seed - true_factor)
    rel_distance = abs_distance / true_factor
    
    return {
        'abs_distance': abs_distance,
        'rel_distance': rel_distance
    }


def get_closest_true_factor(seed: int) -> int:
    """
    Determine which true factor (p or q) is closest to the seed.
    
    Args:
        seed: Candidate seed value
        
    Returns:
        The closest true factor (P_TRUE or Q_TRUE)
    """
    dist_p = abs(seed - P_TRUE)
    dist_q = abs(seed - Q_TRUE)
    return P_TRUE if dist_p < dist_q else Q_TRUE


def bounded_local_refinement(
    N: int,
    seeds: List[int],
    radius: int = REFINEMENT_RADIUS
) -> Dict[str, Any]:
    """
    Perform bounded local refinement around each seed.
    
    Scans ±radius around each seed using big-int modulus to test
    for exact divisibility. Stops at first factor found.
    
    Args:
        N: Semiprime to factor
        seeds: List of candidate seeds
        radius: Search radius (fixed at 1000 per issue)
        
    Returns:
        Dictionary with refinement results
    """
    start_time = time.perf_counter()
    
    candidates_checked = 0
    found_factor = False
    factor_found = None
    seed_index_found = None
    offset_from_seed = None
    
    for seed_idx, seed in enumerate(seeds):
        # Define search window
        search_min = max(2, seed - radius)
        search_max = seed + radius
        
        # Test each candidate in window using big-int modulus
        for candidate in range(search_min, search_max + 1):
            candidates_checked += 1
            
            # Test exact divisibility
            if N % candidate == 0:
                found_factor = True
                factor_found = candidate
                seed_index_found = seed_idx
                offset_from_seed = candidate - seed
                break
        
        if found_factor:
            break
    
    elapsed_time = time.perf_counter() - start_time
    refine_time_ms = elapsed_time * 1000
    
    return {
        'refine_time_ms': refine_time_ms,
        'candidates_checked': candidates_checked,
        'found_factor': found_factor,
        'factor_found': factor_found,
        'seed_index_found': seed_index_found,
        'offset_from_seed': offset_from_seed
    }


def run_benchmark() -> Dict[str, Any]:
    """
    Run the complete RSA-2048 factor extraction benchmark.
    
    Follows Issue #178 structure:
    1. Seed Generation (Green's function resonance)
    2. Distance-to-Truth Metrics
    3. Bounded Local Refinement (±1000)
    4. Timing and Budget
    5. Output Format
    
    Returns:
        Dictionary with all benchmark results and metrics
    """
    print("=" * 80)
    print("RSA-2048 FACTOR CANDIDATE EXTRACTION BENCHMARK")
    print("=" * 80)
    print()
    print("Testing Green's Function Resonance Pipeline on 2048-bit RSA semiprime")
    print()
    
    # Display test case info (condensed per issue requirement)
    N_str = str(N_TEST)
    p_str = str(P_TRUE)
    q_str = str(Q_TRUE)
    
    print(f"N ({N_TEST.bit_length()} bits) = {N_str[:16]}...{N_str[-16:]} (bit_length={N_TEST.bit_length()})")
    print(f"p ({P_TRUE.bit_length()} bits) = {p_str[:16]}...{p_str[-16:]} (bit_length={P_TRUE.bit_length()})")
    print(f"q ({Q_TRUE.bit_length()} bits) = {q_str[:16]}...{q_str[-16:]} (bit_length={Q_TRUE.bit_length()})")
    print()
    print("Note: p and q are used ONLY for distance metrics, not for seed generation")
    print()
    
    # ========================================================================
    # STAGE 1: Seed Generation (Green's Function Resonance)
    # ========================================================================
    print("-" * 80)
    print("STAGE 1: SEED GENERATION (Green's Function Resonance)")
    print("-" * 80)
    print()
    
    # Estimate optimal k
    k_estimated = estimate_k_optimal(N_TEST, balance_estimate=1.0)
    print(f"Estimated k: {k_estimated:.6f}")
    print(f"Expected range: 0.25 - 0.35")
    print()
    
    # Configure refinements (use all mechanisms from PR #177 as specified in issue)
    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_dual_k=False,  # Can be enabled but may slow down
        use_kappa_weight=True,
        use_adaptive_k=True
    )
    
    print("Green's Function Resonance Pipeline Configuration:")
    print("  ✓ Green's function amplitude (wave interference in log space)")
    print("  ✓ Phase-bias correction")
    print("  ✓ Dirichlet kernel sharpening")
    print("  ✓ κ-weighted scoring (Z5D curvature)")
    print(f"  - Dual-k intersection: {'enabled' if config.use_dual_k else 'disabled'}")
    print()
    
    # Log deterministic controls for reproducibility
    print("Deterministic controls:")
    print(f"  - k value: {k_estimated:.6f} (estimated from N)")
    print(f"  - Balance estimate: 1.0 (assuming p ≈ q ≈ √N)")
    print(f"  - Max candidates: {MAX_SEEDS}")
    print(f"  - CPU-only execution (no GPU/network)")
    print()
    
    print("Generating seeds...")
    
    # Time the seed generation
    seed_gen_start = time.perf_counter()
    
    try:
        result = factorize_greens(
            N_TEST,
            k=k_estimated,
            config=config,
            max_candidates=MAX_SEEDS
        )
    except Exception as e:
        print(f"\n❌ ERROR during seed generation: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }
    
    seed_gen_end = time.perf_counter()
    seed_gen_time_ms = (seed_gen_end - seed_gen_start) * 1000
    
    # Extract seeds and metadata
    candidates = result['candidates']
    seeds = [cand.p_candidate for cand in candidates]
    num_seeds = len(seeds)
    k_used = result.get('k_used', k_estimated)

    # Check if dual-k was used (if enabled)
    k_secondary = result.get('k_secondary', None)
    
    print(f"✓ Generated {num_seeds} seeds in {seed_gen_time_ms:.2f} ms")
    print(f"  Primary k: {k_used:.6f}")
    if k_secondary is not None:
        print(f"  Secondary k (dual-k): {k_secondary:.6f}")
    print()
    
    # ========================================================================
    # STAGE 2: Distance-to-Truth Metrics
    # ========================================================================
    print("-" * 80)
    print("STAGE 2: DISTANCE-TO-TRUTH METRICS")
    print("-" * 80)
    print()
    print("Computing distance from each seed to true factors (p_true, q_true)")
    print("These metrics are for evaluation only and NOT fed back to the generator")
    print()
    
    seed_metrics = []
    
    # Table header
    print(f"{'Seed#':>6} | {'Bits':>6} | {'Abs Dist (log10)':>18} | {'Rel Distance':>15} | {'Confidence':>12} | {'k_used':>8}")
    print("-" * 100)
    
    for idx, (seed, cand) in enumerate(zip(seeds, candidates)):
        # Compute distance to nearest true factor (p or q)
        dist_p = compute_distance_metrics(seed, P_TRUE)
        dist_q = compute_distance_metrics(seed, Q_TRUE)
        
        # Use the smaller distance
        if dist_p['abs_distance'] < dist_q['abs_distance']:
            metrics = dist_p
            closest_to = 'p'
        else:
            metrics = dist_q
            closest_to = 'q'
        
        # Store metrics (per issue requirement)
        seed_info = {
            'seed_index': idx,
            'p_candidate': seed,
            'p_prime_bits': seed.bit_length(),
            'abs_distance': metrics['abs_distance'],
            'rel_distance': metrics['rel_distance'],
            'score': cand.score,  # Used for both confidence (issue) and score (tests)
            'k_used': k_used,
            'amplitude': cand.amplitude,
            'phase': cand.phase,
            'kappa_weight': cand.kappa_weight,
            'm_value': cand.m_value,
            'closest_to': closest_to
        }
        seed_metrics.append(seed_info)
        
        # Display (with log scale for large distances)
        abs_dist_log = math.log10(metrics['abs_distance']) if metrics['abs_distance'] > 0 else 0
        print(f"{idx:6d} | {seed.bit_length():6d} | {abs_dist_log:18.2f} | {metrics['rel_distance']:15.6e} | {cand.score:12.6f} | {k_used:8.6f}")
    
    print()
    print(f"✓ Computed distance metrics for {num_seeds} seeds")
    print()
    
    # ========================================================================
    # STAGE 3: Bounded Local Refinement
    # ========================================================================
    print("-" * 80)
    print("STAGE 3: BOUNDED LOCAL REFINEMENT")
    print("-" * 80)
    print()
    print("Performing bounded local refinement around each seed:")
    print(f"  - Refinement radius: ±{REFINEMENT_RADIUS}")
    print(f"  - Method: Big-int modulus (N % candidate == 0)")
    print(f"  - Search window per seed: [-R, +R] = [seed-{REFINEMENT_RADIUS}, seed+{REFINEMENT_RADIUS}]")
    print(f"  - Candidates tested per seed: ~{2 * REFINEMENT_RADIUS + 1}")
    print()
    print("Rules:")
    print("  ✓ No Miller-Rabin primality testing")
    print("  ✓ No Pollard's Rho, ECM, or other factorization algorithms")
    print("  ✓ No trial division over wide ranges")
    print("  ✓ No sieving")
    print("  ✓ Only big-int modulus divisibility testing within fixed radius")
    print()
    
    print("Starting refinement...")
    
    # Run bounded refinement
    refinement_result = bounded_local_refinement(N_TEST, seeds, REFINEMENT_RADIUS)
    
    refine_time_ms = refinement_result['refine_time_ms']
    candidates_checked = refinement_result['candidates_checked']
    found_factor = refinement_result['found_factor']
    
    print(f"✓ Refinement completed in {refine_time_ms:.2f} ms")
    print(f"  Candidates checked: {candidates_checked}")
    print()
    
    # ========================================================================
    # STAGE 4: Timing and Budget
    # ========================================================================
    print("-" * 80)
    print("STAGE 4: TIMING AND BUDGET")
    print("-" * 80)
    print()
    
    total_time_ms = seed_gen_time_ms + refine_time_ms
    within_budget = total_time_ms <= TIME_BUDGET_MS
    
    print("Timing breakdown:")
    print(f"  Seed generation time: {seed_gen_time_ms:10.2f} ms")
    print(f"  Refinement time:      {refine_time_ms:10.2f} ms")
    print(f"  ----------------------------------------")
    print(f"  Total time:           {total_time_ms:10.2f} ms ({total_time_ms/1000:.2f} s)")
    print()
    print(f"  Time budget:          {TIME_BUDGET_MS:10.2f} ms ({TIME_BUDGET_MS/1000:.0f} s)")
    print(f"  Within budget:        {'✓ YES' if within_budget else '✗ NO'}")
    print()
    
    # ========================================================================
    # STAGE 5: Results and Output Format
    # ========================================================================
    print("-" * 80)
    print("STAGE 5: RESULTS")
    print("-" * 80)
    print()
    
    if found_factor:
        factor = refinement_result['factor_found']
        seed_idx = refinement_result['seed_index_found']
        offset = refinement_result['offset_from_seed']
        
        print("✅ SUCCESS - Factor found!")
        print()
        print(f"  Factor: {factor}")
        print(f"  Factor bits: {factor.bit_length()}")
        print(f"  Found from seed index: {seed_idx}")
        print(f"  Offset from seed: {offset:+d}")
        print()
        
        # Verify
        other_factor = N_TEST // factor
        verification = (factor * other_factor == N_TEST)
        print(f"  Verification: {factor} × {other_factor} = N? {verification}")
        print()
        
        if verification:
            print("  Factor is a true divisor of N ✓")
        else:
            print("  ⚠️  WARNING: Factor verification failed!")
    else:
        print("⚠️  No exact factor found within bounded refinement")
        print()
        print(f"  Seeds tested: {num_seeds}")
        print(f"  Refinement radius: ±{REFINEMENT_RADIUS}")
        print(f"  Total candidates checked: {candidates_checked}")
        print()
        print("This indicates the seeds were not within ±1000 of true factors.")
        print("See distance-to-truth metrics above for proximity information.")
    
    print()
    
    # ========================================================================
    # Build final results dictionary (per issue specification)
    # ========================================================================
    results = {
        # Core metrics (required by issue)
        'N_bits': N_TEST.bit_length(),
        'num_seeds': num_seeds,
        'seed_gen_time_ms': seed_gen_time_ms,
        'refine_time_ms': refine_time_ms,
        'total_time_ms': total_time_ms,
        'within_time_budget': within_budget,
        'found_factor': found_factor,
        
        # k values (required by issue)
        'k_estimated': k_estimated,
        'k_used': k_used,
        'k_secondary': k_secondary,
        
        # Refinement config (required by issue)
        'refinement_radius': REFINEMENT_RADIUS,
        'candidates_checked': candidates_checked,
        
        # Per-seed metrics (required by issue)
        'seed_metrics': seed_metrics,
        
        # Configuration (for reproducibility)
        'config': {
            'use_phase_correction': config.use_phase_correction,
            'use_dirichlet': config.use_dirichlet,
            'use_dual_k': config.use_dual_k,
            'use_kappa_weight': config.use_kappa_weight,
            'use_adaptive_k': config.use_adaptive_k,
            'max_seeds': MAX_SEEDS,
            'time_budget_ms': TIME_BUDGET_MS
        }
    }
    
    # Add factor info if found (required by issue)
    if found_factor:
        results['factor_found'] = refinement_result['factor_found']
        results['factor_bits'] = refinement_result['factor_found'].bit_length()
        results['seed_index_found'] = refinement_result['seed_index_found']
        results['offset_from_seed'] = refinement_result['offset_from_seed']
    
    return results


def main():
    """Main entry point"""
    results = run_benchmark()

    if not results.get('success', True):
        print("\n❌ Benchmark failed due to error")
        return
    
    # Print machine-readable summary (required by issue)
    print("=" * 80)
    print("MACHINE-READABLE RESULTS")
    print("=" * 80)
    print()
    
    # Core metrics
    print("Core Metrics:")
    print(f"  N_bits: {results['N_bits']}")
    print(f"  num_seeds: {results['num_seeds']}")
    print(f"  k_used: {results['k_used']:.6f}")
    if results.get('k_secondary') is not None:
        print(f"  k_secondary: {results['k_secondary']:.6f}")
    print(f"  seed_gen_time_ms: {results['seed_gen_time_ms']:.4f}")
    print(f"  refine_time_ms: {results['refine_time_ms']:.4f}")
    print(f"  total_time_ms: {results['total_time_ms']:.4f}")
    print(f"  within_time_budget: {results['within_time_budget']}")
    print(f"  found_factor: {results['found_factor']}")
    print()
    
    if results['found_factor']:
        print("Factor Recovery:")
        print(f"  factor_bits: {results['factor_bits']}")
        print(f"  seed_index_found: {results['seed_index_found']}")
        print(f"  offset_from_seed: {results['offset_from_seed']}")
        print()
    
    print("Per-Seed Metrics:")
    print(f"  Total seeds: {len(results['seed_metrics'])}")
    print()
    
    # Show first 3 seeds as example
    for i, seed_info in enumerate(results['seed_metrics'][:3]):
        print(f"  Seed {i}:")
        print(f"    p_prime_bits: {seed_info['p_prime_bits']}")
        print(f"    abs_distance: {seed_info['abs_distance']:.6e}")
        print(f"    rel_distance: {seed_info['rel_distance']:.6e}")
        print(f"    confidence: {seed_info['score']:.6f}")
        print(f"    k_used: {seed_info['k_used']:.6f}")
        print()
    
    if len(results['seed_metrics']) > 3:
        print(f"  ... ({len(results['seed_metrics']) - 3} more seeds)")
        print()
    
    print("Configuration:")
    for key, value in results['config'].items():
        print(f"  {key}: {value}")
    print()
    
    print("=" * 80)
    print()
    
    # Final status summary
    if results['found_factor']:
        print("🎉 BENCHMARK PASSED: Factor successfully recovered within bounded refinement")
    else:
        print("ℹ️  BENCHMARK COMPLETED: No factor found, but all metrics collected")
    
    print(f"   Total time: {results['total_time_ms']/1000:.2f}s / {TIME_BUDGET_MS/1000:.0f}s budget")
    print()


if __name__ == "__main__":
    main()
