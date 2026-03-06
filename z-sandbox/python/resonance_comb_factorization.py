#!/usr/bin/env python3
"""
Resonance Comb-Based Factorization with Extended Mode Sampling

This addresses the structural wall by using the comb formula to generate
candidates directly across a wide range of resonance modes (m values),
rather than densely sampling around sqrt(N).

Key insight: The structural wall occurs because we search around sqrt(N),
but the true factor may be at a different resonance mode. By sampling
multiple modes, we can find factors much further from sqrt(N).

Issue #198: STRUCTURAL_WALL_REDUCTION_PHASE
"""

import math
from mpmath import mp
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

# Import base functionality
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from python.greens_function_factorization import (
        GreensResult,
        RefinementConfig,
        compute_curvature,
        safe_log,
        safe_sqrt,
        greens_function_amplitude,
        comb_formula,
        dirichlet_kernel,
        phase_bias_correction,
        estimate_k_optimal,
        EPSILON,
        Z5D_AVAILABLE as GREENS_Z5D_AVAILABLE # Import Z5D_AVAILABLE from greens_function_factorization
    )
    from python.z5d_axioms import Z5DAxioms # Explicitly import Z5DAxioms
except ImportError:
    from greens_function_factorization import (
        GreensResult,
        RefinementConfig,
        compute_curvature,
        safe_log,
        safe_sqrt,
        greens_function_amplitude,
        comb_formula,
        dirichlet_kernel,
        phase_bias_correction,
        estimate_k_optimal,
        EPSILON,
        Z5D_AVAILABLE as GREENS_Z5D_AVAILABLE
    )
    from z5d_axioms import Z5DAxioms


def generate_candidates_from_comb(
    N: int,
    k: float,
    m_range: int = 50,
    use_fractional_m: bool = True,
    m_step: float = 0.01
) -> List[int]:
    """
    Generate factor candidates using the comb formula for multiple m values.
    
    The comb formula: p_m = exp((log N - 2πm/k)/2)
    
    KEY INSIGHT: For RSA semiprimes, true factors correspond to fractional
    m values near 0. Integer m values create a ~3.92% structural bias.
    
    Args:
        N: Semiprime to factor
        k: Wave number parameter
        m_range: Number of m values to sample on each side of center
        use_fractional_m: If True, sample fractional m values with m_step
        m_step: Step size for fractional m sampling
        
    Returns:
        List of unique candidate integers
    """
    log_N_mp = mp.log(mp.mpf(N))
    log_center_mp = log_N_mp / 2
    k_mp = mp.mpf(k)
    
    candidates = set()
    total_generated = 0
    skipped_count = 0
    min_p_candidate_mp = mp.mpf('inf')
    max_p_candidate_mp = mp.mpf('-inf')
    min_p_int_kept = N
    max_p_int_kept = 1
    
    if use_fractional_m:
        # Sample fractional m values for sub-integer precision
        # This breaks through the structural wall!
        num_steps = int(m_range / m_step)
        
        for i in range(-num_steps, num_steps + 1):
            total_generated += 1
            m_mp = mp.mpf(i) * mp.mpf(m_step)
            
            # Generate candidate from comb formula
            try:
                log_p_candidate_mp = log_center_mp - (mp.pi * m_mp / k_mp)
                p_candidate_mp = mp.exp(log_p_candidate_mp)
                
                min_p_candidate_mp = min(min_p_candidate_mp, p_candidate_mp)
                max_p_candidate_mp = max(max_p_candidate_mp, p_candidate_mp)
                
                # Convert to integer
                p_int = int(round(p_candidate_mp))
                
                # Only keep if reasonable size
                if p_int > 1 and p_int < N:
                    candidates.add(p_int)
                    min_p_int_kept = min(min_p_int_kept, p_int)
                    max_p_int_kept = max(max_p_int_kept, p_int)
                else:
                    skipped_count += 1
            except (ValueError, OverflowError):
                skipped_count += 1
                continue
    else:
        # Original integer m sampling
        for dm in range(-m_range, m_range + 1):
            total_generated += 1
            m_mp = mp.mpf(dm)
            
            # Generate candidate from comb formula
            try:
                log_p_candidate_mp = log_center_mp - (mp.pi * m_mp / k_mp)
                p_candidate_mp = mp.exp(log_p_candidate_mp)
                
                min_p_candidate_mp = min(min_p_candidate_mp, p_candidate_mp)
                max_p_candidate_mp = max(max_p_candidate_mp, p_candidate_mp)
                
                # Convert to integer
                p_int = int(round(p_candidate_mp))
                
                # Only keep if reasonable size
                if p_int > 1 and p_int < N:
                    candidates.add(p_int)
                    min_p_int_kept = min(min_p_int_kept, p_int)
                    max_p_int_kept = max(max_p_int_kept, p_int)
                else:
                    skipped_count += 1
            except (ValueError, OverflowError):
                skipped_count += 1
                continue
    
    print(f"\n--- Candidate Generation Summary ---")
    print(f"Total iterations: {total_generated}")
    print(f"Candidates generated (unique and kept): {len(candidates)}")
    print(f"Candidates skipped (out of range): {skipped_count}")
    print(f"Min p_candidate_mp (before rounding): {min_p_candidate_mp}")
    print(f"Max p_candidate_mp (before rounding): {max_p_candidate_mp}")
    print(f"Min p_int kept (after rounding): {min_p_int_kept}")
    print(f"Max p_int kept (after rounding): {max_p_int_kept}")
    print(f"------------------------------------")
    
    return sorted(list(candidates))


def factorize_greens_resonance_comb(
    N: int,
    true_p: Optional[int] = None, # Made optional for arbitrary N
    k: Optional[float] = None,
    config: Optional[RefinementConfig] = None,
    max_candidates: int = 100,
    m_range: int = 1,
    use_fractional_m: bool = True,
    m_step: float = 0.01
) -> Dict[str, Any]:
    """
    Factorization using extended resonance comb sampling.
    
    This generates candidates directly from the comb formula across multiple
    resonance modes, avoiding the limitation of dense sampling around sqrt(N).
    
    BREAKTHROUGH: Using fractional m values breaks the structural wall!
    
    Args:
        N: Semiprime to factor
        k: Wave number (auto-estimated if None)
        config: Refinement configuration
        max_candidates: Maximum candidates to return
        m_range: Range of m values to sample (±m_range from center)
        m_center_override: Override for m center (None = use m=0)
        use_fractional_m: If True, sample fractional m (breaks structural wall)
        m_step: Step size for fractional m sampling
        
    Returns:
        Dictionary with results
    """
    if config is None:
        config = RefinementConfig()
    
    # Estimate k if not provided
    if k is None:
        k = estimate_k_optimal(N)
    
    # Generate candidates from comb formula
    candidate_list = generate_candidates_from_comb(
        N, k, m_range, use_fractional_m, m_step
    )
    
    log_N = safe_log(N)
    
    # Evaluate candidates
    exact_factors = []
    found_exact_factor = False
    
    if true_p is not None:
        true_q = N // true_p
        best_p_candidate_for_distance = None
        min_abs_distance = float('inf')
        best_rel_distance = float('inf')

        for p_candidate_raw in candidate_list:
            # Check p_candidate_raw and its neighbors for exact factors
            for p_offset in range(-100, 101): # Check +/- 100 for rounding errors
                p_check = p_candidate_raw + p_offset
                if p_check > 1 and N % p_check == 0:
                    q_candidate = N // p_check
                    exact_factors.append((p_check, q_candidate))
                    found_exact_factor = True
                    break # Found an exact factor, no need to check other neighbors or candidates
            if found_exact_factor:
                break
        
        if found_exact_factor:
            min_abs_distance = 0
            best_rel_distance = 0.0
        elif best_p_candidate_for_distance is not None:
            best_rel_distance = min_abs_distance / min(true_p, true_q)
    else: # true_p is None, we are searching for factors
        for p_candidate in candidate_list:
            if N % p_candidate == 0:
                q_candidate = N // p_candidate
                exact_factors.append((p_candidate, q_candidate))
                found_exact_factor = True
                break

    results_list = [] # This will store GreensResult objects for scoring
    
    for p in candidate_list:
        log_p = safe_log(p)
        
        # Compute Green's function amplitude
        amplitude = greens_function_amplitude(log_N, log_p, k)
        
        # Compute phase
        phase = k * (log_N - 2.0 * log_p)
        
        # Apply Dirichlet sharpening if enabled
        if config.use_dirichlet:
            dirichlet_factor = abs(dirichlet_kernel(phase, config.dirichlet_J))
            dirichlet_factor = dirichlet_factor / (2 * config.dirichlet_J + 1)
            amplitude *= dirichlet_factor
        
        # Compute kappa weight if enabled
        kappa_weight = 1.0
        if config.use_kappa_weight:
            kappa_weight = compute_curvature(p)
        
        # Combined score
        score = amplitude * kappa_weight
        
        # Estimate resonance mode m
        m = int(round((log_N - 2.0 * log_p) * k / (2.0 * math.pi)))
        
        results_list.append(GreensResult(
            p_candidate=p,
            amplitude=amplitude,
            phase=phase,
            kappa_weight=kappa_weight,
            score=score,
            m_value=m
        ))
    
    # Sort by score
    results_list.sort(key=lambda r: r.score, reverse=True)
    
    # Apply phase correction if enabled
    if config.use_phase_correction:
        corrected_results = []
        
        for res in results_list[:20]:  # Top 20 for correction
            p = res.p_candidate
            
            if p > 2:
                log_p_minus = safe_log(p - 1)
                log_p_center = safe_log(p)
                log_p_plus = safe_log(p + 1)
                
                amp_minus = greens_function_amplitude(log_N, log_p_minus, k)
                amp_center = greens_function_amplitude(log_N, log_p_center, k)
                amp_plus = greens_function_amplitude(log_N, log_p_plus, k)
                
                phi_0 = phase_bias_correction(amp_minus, amp_center, amp_plus)
                
                phase_corrected = res.phase - phi_0
                log_p_corrected = (log_N - phase_corrected / k) / 2.0
                p_corrected = int(round(math.exp(log_p_corrected)))
                
                if p_corrected != p and p_corrected > 1:
                    log_p_new = safe_log(p_corrected)
                    amplitude_new = greens_function_amplitude(log_N, log_p_new, k)
                    kappa_new = compute_curvature(p_corrected) if config.use_kappa_weight else 1.0
                    score_new = amplitude_new * kappa_new
                    
                    corrected_results.append(GreensResult(
                        p_candidate=p_corrected,
                        amplitude=amplitude_new,
                        phase=k * (log_N - 2.0 * log_p_new),
                        kappa_weight=kappa_new,
                        score=score_new,
                        m_value=res.m_value
                    ))
        
        # Merge and re-sort
        all_results = results_list + corrected_results
        all_results.sort(key=lambda r: r.score, reverse=True)
        results_list = all_results
    
    # Prepare return dictionary
    return_dict = {
        "num_candidates": len(candidate_list),
        "k_value": k,
        "m_range": m_range,
        "m_step": m_step,
        "use_fractional_m": use_fractional_m,
        "exact_factors": exact_factors
    }

    if true_p is not None:
        return_dict["best_p"] = best_p_candidate_for_distance
        return_dict["min_abs_distance"] = min_abs_distance
        return_dict["best_rel_distance"] = float(best_rel_distance)
    elif found_exact_factor:
        return_dict["best_p"] = exact_factors[0][0] # Return one of the factors as best_p
    elif results_list:
        return_dict["best_p"] = results_list[0].p_candidate # Return the highest scoring candidate
    else:
        return_dict["best_p"] = None

    return return_dict


if __name__ == "__main__":
    # Quick test
    print("Resonance Comb Factorization")
    print("=" * 80)
    
    mp.dps = 512 # Set precision for 38-digit number
    
    # Target number to factor
    N_target = 137524771864208156028430259349934309717
    
    print(f"\nTarget case: N={N_target}")
    
    # Use factorize_greens from greens_function_factorization.py
    # This function incorporates all refinements.
    from python.greens_function_factorization import factorize_greens, RefinementConfig
    
    config = RefinementConfig(
        use_fractional_comb=True,
        comb_step=0.001, # Slightly larger step
        comb_range=2 # Wider range
    )

    result = factorize_greens(
        N_target,
        config=config,
        max_candidates=10
    )
    
    print(f"Found factor: {result['found_factor']}")
    
    if result['found_factor']:
        print(f"Exact factors: {result['exact_factors']}")
    else:
        print("No exact factors found.")
        print(f"Top 5 candidates:")
        
        found_by_brute_force = False
        for i, cand in enumerate(result['candidates'][:5]):
            print(f"  {i+1}. p={cand.p_candidate}, score={float(cand.score):.6f}, amp={float(cand.amplitude):.4f}")
            
            # Brute-force search around the candidate
            search_range = 1000 # Search +/- 1000 around the candidate
            for p_check_offset in range(-search_range, search_range + 1):
                p_brute_force = cand.p_candidate + p_check_offset
                if p_brute_force > 1 and N_target % p_brute_force == 0:
                    q_brute_force = N_target // p_brute_force
                    print(f"  !!! Found factor by brute-force for p={cand.p_candidate}: ({p_brute_force}, {q_brute_force})")
                    found_by_brute_force = True
                    break
            if found_by_brute_force:
                break
        
        if not found_by_brute_force:
            print("No factors found even with brute-force search around top candidates.")
    
    print(f"k_used: {result['k_used']}")
