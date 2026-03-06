#!/usr/bin/env python3
"""
Bias-Corrected RSA-2048 K-Sweep

Tests the bias-corrected geometric embedding against the baseline.

Usage: python3 bias_corrected_k_sweep.py [--method METHOD]

Issue #198: STRUCTURAL_WALL_REDUCTION_PHASE
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import argparse
from typing import Dict, List, Any
from mpmath import mp

try:
    from python.bias_corrected_greens_factorization import factorize_greens_bias_corrected
    from python.greens_function_factorization import RefinementConfig
except ImportError:
    from bias_corrected_greens_factorization import factorize_greens_bias_corrected
    from greens_function_factorization import RefinementConfig


# Known RSA-2048 test case
N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637

P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459

Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143

MPMATH_PRECISION = 100
K_BASE_VALUES = [0.250, 0.260, 0.270, 0.280, 0.290, 0.300]


def compute_distance_to_truth(seed: int, p_true: int, q_true: int) -> Dict[str, Any]:
    """Compute distance metrics from seed to closest true factor."""
    dist_p = abs(seed - p_true)
    dist_q = abs(seed - q_true)
    
    if dist_p < dist_q:
        abs_distance = dist_p
        closest_to = 'p'
    else:
        abs_distance = dist_q
        closest_to = 'q'
    
    rel_distance = abs_distance / (p_true if closest_to == 'p' else q_true)
    
    return {
        'abs_distance': abs_distance,
        'rel_distance': rel_distance,
        'closest_to': closest_to
    }


def run_bias_corrected_sweep(
    k_values: List[float],
    bias_method: str = 'phase'
) -> Dict[str, Any]:
    """
    Run k-sweep with bias correction.
    
    Args:
        k_values: List of k values to test
        bias_method: Bias correction method ('phase', 'amplitude', 'none')
        
    Returns:
        Results dictionary
    """
    print("=" * 80)
    print(f"BIAS-CORRECTED RSA-2048 K-SWEEP (method={bias_method})")
    print("=" * 80)
    print()
    
    N_str = str(N_TEST)
    p_str = str(P_TRUE)
    q_str = str(Q_TRUE)
    
    print(f"N ({N_TEST.bit_length()} bits) = {N_str[:16]}...{N_str[-16:]}")
    print(f"p ({P_TRUE.bit_length()} bits) = {p_str[:16]}...{p_str[-16:]}")
    print(f"q ({Q_TRUE.bit_length()} bits) = {q_str[:16]}...{q_str[-16:]}")
    print()
    print(f"Testing k values: {k_values}")
    print(f"Bias correction method: {bias_method}")
    print()
    
    # Set precision
    mp.dps = MPMATH_PRECISION
    
    # Pipeline config (match baseline)
    config = RefinementConfig(
        use_phase_correction=True,
        use_dirichlet=True,
        use_dual_k=False,
        use_kappa_weight=True,
        use_adaptive_k=False
    )
    
    results = []
    global_best_k = None
    global_best_rel_distance = float('inf')
    global_best_bias_info = None
    
    for i, k_base in enumerate(k_values):
        print(f"\n[{i+1}/{len(k_values)}] Testing k_base={k_base:.3f}")
        print("-" * 80)
        
        try:
            result = factorize_greens_bias_corrected(
                N_TEST,
                k=k_base,
                config=config,
                max_candidates=100,
                bias_correction_method=bias_method
            )
            
            # Display bias correction info
            bias_info = result['bias_correction']
            print(f"Bias correction applied:")
            print(f"  Original center (sqrt(N)): {bias_info['original_center']}")
            print(f"  Corrected center:          {bias_info['corrected_center']}")
            print(f"  Bias magnitude:            {bias_info['bias_magnitude']}")
            print(f"  Relative bias:             {bias_info['relative_bias']:.6e}")
            
            # Find best candidate and its distance
            if result['candidates']:
                all_distances = []
                
                for cand in result['candidates']:
                    dist_metrics = compute_distance_to_truth(cand.p_candidate, P_TRUE, Q_TRUE)
                    all_distances.append(dist_metrics['rel_distance'])
                
                best_rel_distance = min(all_distances)
                
                print(f"\nBest rel_distance: {best_rel_distance:.6e}")
                
                if best_rel_distance < global_best_rel_distance:
                    global_best_rel_distance = best_rel_distance
                    global_best_k = k_base
                    global_best_bias_info = bias_info
                
                results.append({
                    'k_base': k_base,
                    'best_rel_distance': best_rel_distance,
                    'bias_info': bias_info
                })
            else:
                print("No candidates returned")
                results.append({
                    'k_base': k_base,
                    'best_rel_distance': None,
                    'bias_info': bias_info
                })
        
        except Exception as e:
            print(f"Error testing k={k_base}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Print final summary
    print("\n")
    print("=" * 80)
    print("BIAS-CORRECTED SWEEP RESULTS")
    print("=" * 80)
    print()
    
    print(f"Global best k_base: {global_best_k}")
    print(f"Global best rel_distance: {global_best_rel_distance:.6e}")
    
    if global_best_bias_info:
        print()
        print(f"Bias info at best k:")
        print(f"  Original center: {global_best_bias_info['original_center']}")
        print(f"  Corrected center: {global_best_bias_info['corrected_center']}")
        print(f"  Bias applied: {global_best_bias_info['bias_applied']}")
        print(f"  Relative bias: {global_best_bias_info['relative_bias']:.6e}")
    
    print()
    
    # Compare to baseline
    baseline_rel_distance = 0.03922032
    
    print("=" * 80)
    print("COMPARISON TO BASELINE")
    print("=" * 80)
    print()
    print(f"Baseline (no correction):     {baseline_rel_distance:.6e} (~3.92%)")
    print(f"Bias-corrected ({bias_method}):  {global_best_rel_distance:.6e}")
    
    if global_best_rel_distance < baseline_rel_distance:
        improvement = (baseline_rel_distance - global_best_rel_distance) / baseline_rel_distance * 100
        print(f"Improvement: {improvement:.2f}%")
        
        if global_best_rel_distance < 0.01:
            print()
            print("✓✓✓ SUCCESS! Wall reduced below 1% target! ✓✓✓")
        else:
            print()
            print(f"Partial success. Current: {global_best_rel_distance*100:.4f}%, target: <1%")
    else:
        print("Warning: No improvement over baseline")
    
    print()
    
    return {
        'method': bias_method,
        'global_best_k': global_best_k,
        'global_best_rel_distance': global_best_rel_distance,
        'baseline_rel_distance': baseline_rel_distance,
        'results': results
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Bias-corrected RSA k-sweep"
    )
    parser.add_argument(
        '--method',
        type=str,
        default='phase',
        choices=['phase', 'amplitude', 'none'],
        help='Bias correction method'
    )
    parser.add_argument(
        '--k',
        type=float,
        help='Single k value to test (skips sweep)'
    )
    
    args = parser.parse_args()
    
    if args.k:
        k_values = [args.k]
    else:
        k_values = K_BASE_VALUES
    
    results = run_bias_corrected_sweep(k_values, args.method)
    
    print("\n")
    print("=" * 80)
    print("BIAS CORRECTION TEST COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
