#!/usr/bin/env python3
"""
RSA-2048 k-Parameter Sweep for Seed Accuracy Analysis
=====================================================

This script systematically evaluates multiple resonance parameters (k values)
with fixed ±0.5% detunes against a known 2048-bit RSA semiprime to determine
which k setting produces the closest seed to the true 1024-bit factor.

The script measures seed proximity without running refinement, allowing us to
assess whether tuning k alone can reduce relative error toward the range where
±1000 refinement becomes practical.

This implements Issue #193 requirements:
- Fixed k_base values: [0.250, 0.260, ..., 0.350]
- Each k_base evaluated with ±0.5% detune variants
- Distance-to-truth scoring for all returned seeds
- Per-k_base aggregation of best seed
- Global best-k identification
- Deterministic/reproducible execution
- No modifications to existing pipeline
- No refinement loop execution
"""

import sys
import os
import argparse
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

# Import precision control
from mpmath import mp

# ============================================================================
# Known 2048-bit RSA semiprime (same as rsa_factor_benchmark.py)
# ============================================================================
# These are ground truth for distance measurement ONLY
# They are NEVER fed to the seed generator

N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637

P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459

Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143


# ============================================================================
# k-Sweep Configuration
# ============================================================================

# Base k values to evaluate (per issue requirement)
K_BASE_VALUES = [
    0.250, 0.260, 0.270, 0.280, 0.290,
    0.300, 0.310, 0.320, 0.330, 0.340, 0.350
]

# Fixed detune percentage (±0.5%)
DETUNE_OFFSET = 0.005

# Deterministic seed for reproducibility
DETERMINISTIC_SEED = 1337

# Maximum candidates to collect per k variant
MAX_CANDIDATES = 100

# Precision for mpmath (consistent across all calls)
MPMATH_PRECISION = 100  # decimal places


# ============================================================================
# Helper Functions
# ============================================================================

def compute_distance_to_truth(seed: int, p_true: int, q_true: int) -> Dict[str, Any]:
    """
    Compute distance metrics from seed to closest true factor.
    
    Args:
        seed: Candidate seed value
        p_true: True factor p
        q_true: True factor q
        
    Returns:
        Dictionary with distance metrics and which factor is closest
        
    Note:
        If distances are equal, 'q' is chosen (tie-breaking rule)
    """
    dist_p = abs(seed - p_true)
    dist_q = abs(seed - q_true)
    
    if dist_p < dist_q:
        abs_distance = dist_p
        closest_to = 'p'
    else:
        abs_distance = dist_q
        closest_to = 'q'  # If equal distances, defaults to q (tie-breaking rule)
    
    # Compute relative distance (using the closer factor as denominator)
    rel_distance = abs_distance / (p_true if closest_to == 'p' else q_true)
    
    return {
        'abs_distance': abs_distance,
        'rel_distance': rel_distance,
        'closest_to': closest_to
    }


def evaluate_k_variant(
    N: int,
    k: float,
    k_label: str,
    config: RefinementConfig
) -> List[Dict[str, Any]]:
    """
    Evaluate a single k variant and collect all seed metrics.
    
    Args:
        N: Semiprime to factor
        k: Wave number parameter
        k_label: Label for this k variant ("k_base", "k_plus", "k_minus")
        config: Refinement configuration
        
    Returns:
        List of seed info dicts with distance metrics
    """
    # Set precision consistently
    mp.dps = MPMATH_PRECISION
    
    # Call the resonance pipeline
    result = factorize_greens(
        N,
        k=k,
        config=config,
        max_candidates=MAX_CANDIDATES
    )
    
    # Extract seeds
    candidates = result.get('candidates', [])
    
    seed_infos = []
    for cand in candidates:
        seed = cand.p_candidate
        
        # Compute distance to truth
        dist_metrics = compute_distance_to_truth(seed, P_TRUE, Q_TRUE)
        
        # Build seed info
        seed_info = {
            'p_prime': seed,
            'p_prime_bits': seed.bit_length(),
            'abs_distance': dist_metrics['abs_distance'],
            'rel_distance': dist_metrics['rel_distance'],
            'closest_to': dist_metrics['closest_to'],
            'confidence': cand.score,  # Pipeline's score
            'amplitude': cand.amplitude,
            'phase': cand.phase,
            'kappa_weight': cand.kappa_weight,
            'm_value': cand.m_value,
            'k_used': k,
            'k_source': k_label
        }
        seed_infos.append(seed_info)
    
    return seed_infos


def aggregate_k_base_group(
    k_base: float,
    seeds_base: List[Dict[str, Any]],
    seeds_plus: List[Dict[str, Any]],
    seeds_minus: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Aggregate results for a k_base group (base + plus + minus).
    
    Finds the single best seed across all three variants by minimum rel_distance.
    
    Args:
        k_base: Base k value
        seeds_base: Seeds from k_base
        seeds_plus: Seeds from k_plus
        seeds_minus: Seeds from k_minus
        
    Returns:
        Aggregated result dict for this k_base group
    """
    k_plus = k_base * (1.0 + DETUNE_OFFSET)
    k_minus = k_base * (1.0 - DETUNE_OFFSET)
    
    # Combine all seeds from this group
    all_seeds = seeds_base + seeds_plus + seeds_minus
    num_seeds_total = len(all_seeds)
    
    # Find best seed by rel_distance
    if num_seeds_total > 0:
        best_seed = min(all_seeds, key=lambda s: s['rel_distance'])
        
        return {
            'k_base': k_base,
            'k_plus': k_plus,
            'k_minus': k_minus,
            'best_abs_distance': best_seed['abs_distance'],
            'best_rel_distance': best_seed['rel_distance'],
            'best_seed_bits': best_seed['p_prime_bits'],
            'best_seed_confidence': best_seed['confidence'],
            'best_seed_source': best_seed['k_source'],
            'num_seeds_total': num_seeds_total,
            'determinism_info': {
                'seed': DETERMINISTIC_SEED,
                'detune_offset': DETUNE_OFFSET,
                'mpmath_dps': MPMATH_PRECISION
            }
        }
    else:
        # No seeds returned for this group
        return {
            'k_base': k_base,
            'k_plus': k_plus,
            'k_minus': k_minus,
            'best_abs_distance': None,
            'best_rel_distance': None,
            'best_seed_bits': None,
            'best_seed_confidence': None,
            'best_seed_source': None,
            'num_seeds_total': 0,
            'determinism_info': {
                'seed': DETERMINISTIC_SEED,
                'detune_offset': DETUNE_OFFSET,
                'mpmath_dps': MPMATH_PRECISION
            }
        }


# ============================================================================
# Main Sweep Function
# ============================================================================

def run_k_sweep(N: int, p_true: int, q_true: int, profile: str = "balanced_2048") -> Dict[str, Any]:
    """
    Run the complete k-parameter sweep.
    
    For each k_base in K_BASE_VALUES:
    1. Evaluate k_base, k_plus, k_minus
    2. Collect all seeds and compute distance metrics
    3. Aggregate best seed for the k_base group
    4. Build final report with global best
    
    Returns:
        Complete report dict with per-group and global results
    """
    print("=" * 80)
    print(f"RSA K-PARAMETER SWEEP FOR SEED ACCURACY ({profile})")
    print("=" * 80)
    print()
    print("Testing resonance parameter (k) impact on seed proximity to true factors")
    print()

    # Display test case info
    N_str = str(N)
    p_str = str(p_true)
    q_str = str(q_true)

    print(f"N ({N.bit_length()} bits) = {N_str[:16]}...{N_str[-16:]}")
    print(f"p ({p_true.bit_length()} bits) = {p_str[:16]}...{p_str[-16:]}")
    print(f"q ({q_true.bit_length()} bits) = {q_str[:16]}...{q_str[-16:]}")
    print(f"Profile: {profile}")
    print()
    print("Note: p and q are used ONLY for distance metrics, not for seed generation")
    print()
    print("Testing resonance parameter (k) impact on seed proximity to true factors")
    print()
    
    # Display test case info
    N_str = str(N_TEST)
    p_str = str(P_TRUE)
    q_str = str(Q_TRUE)
    
    print(f"N ({N_TEST.bit_length()} bits) = {N_str[:16]}...{N_str[-16:]}")
    print(f"p ({P_TRUE.bit_length()} bits) = {p_str[:16]}...{p_str[-16:]}")
    print(f"q ({Q_TRUE.bit_length()} bits) = {q_str[:16]}...{q_str[-16:]}")
    print()
    print("Note: p and q are used ONLY for distance measurement, never for seed generation")
    print()
    
    # Configuration
    print("-" * 80)
    print("CONFIGURATION")
    print("-" * 80)
    print()
    print(f"k_base values to sweep: {K_BASE_VALUES}")
    print(f"Detune offset: ±{DETUNE_OFFSET * 100:.1f}%")
    print(f"Deterministic seed: {DETERMINISTIC_SEED}")
    print(f"Max candidates per k: {MAX_CANDIDATES}")
    print(f"mpmath precision: {MPMATH_PRECISION} decimal places")
    print()
    
    # Pipeline config (same as benchmark but without dual-k for speed)
    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_dual_k=False,  # Disabled for speed
        use_kappa_weight=True,
        use_adaptive_k=False,  # We're controlling k explicitly
        # Issue #199: Use second-order bias model for generalized correction
        use_bias_model=True,
        profile=profile  # Profile-aware correction
    )
    
    print("Pipeline configuration:")
    print("  ✓ Green's function amplitude")
    print("  ✓ Phase-bias correction")
    print("  ✓ Dirichlet kernel sharpening")
    print("  ✓ κ-weighted scoring")
    print("  - Dual-k: disabled (we're sweeping k externally)")
    print("  - Adaptive-k: disabled (we control k explicitly)")
    print()
    
    print("-" * 80)
    print("RUNNING K-SWEEP")
    print("-" * 80)
    print()
    
    results = []
    
    for i, k_base in enumerate(K_BASE_VALUES):
        k_plus = k_base * (1.0 + DETUNE_OFFSET)
        k_minus = k_base * (1.0 - DETUNE_OFFSET)
        
        print(f"[{i+1}/{len(K_BASE_VALUES)}] k_base={k_base:.3f}, k+={k_plus:.6f}, k-={k_minus:.6f}")
        
        # Evaluate each variant
        print("  Evaluating k_base...", end=" ")
        sys.stdout.flush()
        seeds_base = evaluate_k_variant(N, k_base, "k_base", config)
        seeds_plus = evaluate_k_variant(N, k_plus, "k_plus", config)
        seeds_minus = evaluate_k_variant(N, k_minus, "k_minus", config)
        print(f"{len(seeds_minus)} seeds")
        
        # Aggregate this k_base group
        group_result = aggregate_k_base_group(
            k_base,
            seeds_base,
            seeds_plus,
            seeds_minus
        )
        
        # Display summary
        if group_result['best_rel_distance'] is not None:
            print(f"  → Best: {group_result['best_rel_distance']:.6e} rel_dist "
                  f"from {group_result['best_seed_source']}, "
                  f"{group_result['num_seeds_total']} total seeds")
        else:
            print(f"  → No seeds returned")
        print()
        
        results.append(group_result)
    
    # Find global best
    print("-" * 80)
    print("FINDING GLOBAL BEST")
    print("-" * 80)
    print()
    
    # Filter groups with valid results
    valid_results = [r for r in results if r['best_rel_distance'] is not None]
    
    if valid_results:
        global_best = min(valid_results, key=lambda r: r['best_rel_distance'])
        global_best_k_base = global_best['k_base']
        global_best_source = global_best['best_seed_source']
        global_best_abs_distance = global_best['best_abs_distance']
        global_best_rel_distance = global_best['best_rel_distance']
        
        print(f"Global best k_base: {global_best_k_base:.3f}")
        print(f"Global best source: {global_best_source}")
        print(f"Global best abs_distance: {global_best_abs_distance:.6e}")
        print(f"Global best rel_distance: {global_best_rel_distance:.6e}")
    else:
        print("No valid results found (all k groups returned zero seeds)")
        global_best_k_base = None
        global_best_source = None
        global_best_abs_distance = None
        global_best_rel_distance = None
    
    print()
    
    # Build final report
    report = {
        'N_bits': N.bit_length(),
        'profile': profile,
        'global_best_k_base': global_best_k_base,
        'global_best_source': global_best_source,
        'global_best_abs_distance': global_best_abs_distance,
        'global_best_rel_distance': global_best_rel_distance,
        'results': results
    }
    
    return report


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="RSA k-parameter sweep for seed accuracy")
    parser.add_argument('--N', type=int, help='Semiprime N')
    parser.add_argument('--p', type=int, help='True factor p')
    parser.add_argument('--q', type=int, help='True factor q')
    parser.add_argument('--profile', type=str, default='balanced_2048',
                       help='Modulus profile (e.g., balanced_2048, skewed_2048)')

    args = parser.parse_args()

    # Use provided args or defaults
    N = args.N if args.N else N_TEST
    p_true = args.p if args.p else P_TRUE
    q_true = args.q if args.q else Q_TRUE
    profile = args.profile

    report = run_k_sweep(N, p_true, q_true, profile)

    print("=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    print()
    print(report)
    print()


if __name__ == "__main__":
    main()
