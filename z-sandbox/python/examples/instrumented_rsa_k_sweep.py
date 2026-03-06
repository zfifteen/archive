#!/usr/bin/env python3
"""
Instrumented RSA-2048 K-Sweep for Bias Attribution

This script runs the k-sweep with detailed instrumentation to identify
which pipeline stage contributes most to the ~3.92% structural wall.

Usage: python3 instrumented_rsa_k_sweep.py [--k K_VALUE]

Issue #198: STRUCTURAL_WALL_REDUCTION_PHASE
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import argparse
from typing import Dict, List, Any
from mpmath import mp

try:
    from python.instrumented_greens_factorization import (
        factorize_greens_instrumented,
        StageMetrics
    )
    from python.greens_function_factorization import RefinementConfig
except ImportError:
    from instrumented_greens_factorization import (
        factorize_greens_instrumented,
        StageMetrics
    )
    from greens_function_factorization import RefinementConfig


# Known RSA-2048 test case
N_TEST = 19565052573783926362804955826185174525728078526810712384495116220075771203165815540350320318234128109502866404040441646380733489768005779750907460852666274829374234588862350999665490821796652462380009427451532262669780600090584349311855804897481279577689230978047661163247172188041684808930232313420099220509975125970254512319302192626041901541490412992887762283300565206734618291529115764983558780812801167921784644100839569587504288169305437609858438979156657056535415039123177205165132056618062514534266865794937597754711033463786911711252396693196372442794203778085999392377806478126752931833456678124819568916637

P_TRUE = 134596225071135757293877433819413042692936037953129096730037533712099883422087322247202866162901551695219265438464014797133085167763724652777056857132766942498195472133731530346298881967275916900943816351152798867657836673578516686085149202952019670806806720314963439188663312724081358033818044077490265379459

Q_TRUE = 145361079506082402319115985685104724044029974560950724482315821335626420254076928561868556125783099818250531777010570908673902127477196129280179451308959161688423703684550768103325410322153626376997013729837192552778234164200704030452467012179884274065691245690105207571454569357259438464162984053635783106143

# K values to test
K_BASE_VALUES = [0.250, 0.260, 0.270, 0.280, 0.290, 0.300]
MPMATH_PRECISION = 100


def run_instrumented_sweep(k_values: List[float]) -> Dict[str, Any]:
    """
    Run instrumented k-sweep to identify bias sources.
    
    Args:
        k_values: List of k values to test
        
    Returns:
        Dictionary with aggregated stage metrics
    """
    print("=" * 80)
    print("INSTRUMENTED RSA-2048 K-SWEEP FOR BIAS ATTRIBUTION")
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
    
    # Aggregate stage metrics across k values
    stage_contributions = {}
    best_k = None
    best_rel_distance = float('inf')
    best_metrics = None
    
    for i, k in enumerate(k_values):
        print(f"\n[{i+1}/{len(k_values)}] Testing k={k:.3f}")
        print("-" * 80)
        
        try:
            result = factorize_greens_instrumented(
                N_TEST,
                k=k,
                config=config,
                max_candidates=100,
                p_true=P_TRUE,
                q_true=Q_TRUE,
                verbose=True
            )
            
            # Find best candidate
            if result.candidates:
                best_cand = result.candidates[0]
                
                # Compute distance to truth
                dist_p = abs(best_cand.p_candidate - P_TRUE)
                dist_q = abs(best_cand.p_candidate - Q_TRUE)
                
                if dist_p < dist_q:
                    rel_distance = dist_p / P_TRUE
                else:
                    rel_distance = dist_q / Q_TRUE
                
                print(f"\nBest candidate rel_distance: {rel_distance:.6e}")
                
                if rel_distance < best_rel_distance:
                    best_rel_distance = rel_distance
                    best_k = k
                    best_metrics = result.stage_metrics
                
                # Aggregate stage contributions
                for m in result.stage_metrics:
                    if m.stage_name not in stage_contributions:
                        stage_contributions[m.stage_name] = []
                    stage_contributions[m.stage_name].append(m.distortion_contribution)
        
        except Exception as e:
            print(f"Error testing k={k}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Print aggregate results
    print("\n")
    print("=" * 80)
    print("AGGREGATE BIAS ATTRIBUTION ACROSS K VALUES")
    print("=" * 80)
    print()
    
    print(f"Best k: {best_k}")
    print(f"Best rel_distance: {best_rel_distance:.6e}")
    print()
    
    if stage_contributions:
        print("Average distortion contribution per stage:")
        print()
        
        total_avg = 0.0
        stage_avgs = {}
        
        for stage_name, contributions in stage_contributions.items():
            avg_contrib = sum(contributions) / len(contributions)
            stage_avgs[stage_name] = avg_contrib
            total_avg += avg_contrib
        
        # Sort by contribution
        sorted_stages = sorted(stage_avgs.items(), key=lambda x: x[1], reverse=True)
        
        for stage_name, avg_contrib in sorted_stages:
            pct = (avg_contrib / total_avg * 100) if total_avg > 0 else 0
            print(f"  {stage_name:25s}: {avg_contrib:10.6e} ({pct:5.1f}%)")
        
        print()
        print(f"Total average distortion: {total_avg:.6e}")
        print()
        
        # Identify highest contributor
        if sorted_stages:
            highest_stage, highest_contrib = sorted_stages[0]
            highest_pct = (highest_contrib / total_avg * 100) if total_avg > 0 else 0
            
            print("=" * 80)
            print("KEY FINDING")
            print("=" * 80)
            print()
            print(f"Highest distortion stage: {highest_stage}")
            print(f"Contribution: {highest_contrib:.6e} ({highest_pct:.1f}% of total)")
            print()
            print("This stage is the primary target for bias correction.")
            print()
    
    return {
        'best_k': best_k,
        'best_rel_distance': best_rel_distance,
        'stage_contributions': stage_contributions,
        'best_metrics': best_metrics
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Instrumented RSA k-sweep for bias attribution"
    )
    parser.add_argument(
        '--k',
        type=float,
        help='Single k value to test (skips sweep)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Test all k values from baseline sweep'
    )
    
    args = parser.parse_args()
    
    if args.k:
        k_values = [args.k]
    elif args.all:
        k_values = [0.250, 0.260, 0.270, 0.280, 0.290, 0.300, 0.310, 0.320, 0.330, 0.340, 0.350]
    else:
        # Default: test subset for speed
        k_values = K_BASE_VALUES
    
    results = run_instrumented_sweep(k_values)
    
    print("\n")
    print("=" * 80)
    print("INSTRUMENTATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Implement bias correction for highest-distortion stage")
    print("2. Re-run k-sweep with correction applied")
    print("3. Validate best_rel_distance < 0.01")
    print()


if __name__ == "__main__":
    main()
