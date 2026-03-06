#!/usr/bin/env python3
"""
Z5D Hypothesis Validation Framework
Validates scale-invariant geometric resonance using statistical tests
"""

import sys
import math
import random
from typing import List, Tuple, Dict
import statistics

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("Warning: scipy not available, using simplified statistics", file=sys.stderr)

from z5d_adapter import n_est, geometric_resonance_score
from adversarial_test_adaptive import (
    is_prime_simple, find_next_prime, find_prev_prime,
    adaptive_window_search, analyze_asymmetric_enrichment
)


def generate_test_semiprimes(count=20, min_p=10, max_p=1000):
    """
    Generate test semiprimes with varying asymmetry.
    
    Args:
        count: Number of semiprimes to generate
        min_p: Minimum value for smaller prime
        max_p: Maximum value for smaller prime
    
    Returns:
        List of (N, p, q) tuples
    """
    semiprimes = []
    
    p = min_p
    while len(semiprimes) < count and p < max_p:
        if is_prime_simple(p):
            # Find a larger prime
            q_min = p
            q_max = min(max_p * 10, p * 50)  # Create some asymmetry
            
            # Random offset for asymmetry
            offset = random.randint(0, (q_max - q_min) // 2)
            q_candidate = q_min + offset
            
            q = find_next_prime(q_candidate)
            if q < q_max:
                N = p * q
                semiprimes.append((N, p, q))
        
        p += 1
    
    return semiprimes


def test_scale_invariance(scales: List[int], k_or_phase=0.27952859830111265):
    """
    Test scale invariance of geometric resonance patterns.
    
    Validates that Z5D scores remain consistent across different scales.
    
    Args:
        scales: List of scale exponents (e.g., [2, 4, 6] for 10^2, 10^4, 10^6)
        k_or_phase: Phase constant
    
    Returns:
        Scale invariance metrics
    """
    results = {
        'scales': scales,
        'z5d_scores': [],
        'variances': [],
        'scale_invariant': False
    }
    
    for scale in scales:
        # Generate semiprimes at this scale
        base = 10 ** scale
        
        # Find primes near sqrt(base)
        sqrt_base = int(math.sqrt(base))
        p = find_prev_prime(sqrt_base)
        q = find_next_prime(sqrt_base)
        
        N = p * q
        
        # Calculate Z5D score
        score = geometric_resonance_score(p, q, N)
        results['z5d_scores'].append(score)
        
        print(f"Scale 10^{scale}: N={N}, p={p}, q={q}, Z5D={score:.4f}")
    
    # Test for scale invariance: scores should have low variance
    if len(results['z5d_scores']) > 1:
        mean_score = statistics.mean(results['z5d_scores'])
        variance = statistics.variance(results['z5d_scores'])
        results['mean_score'] = mean_score
        results['variance'] = variance
        results['coefficient_of_variation'] = math.sqrt(variance) / abs(mean_score) if mean_score != 0 else float('inf')
        
        # Scale invariant if CV < 0.2 (20%)
        results['scale_invariant'] = results['coefficient_of_variation'] < 0.2
    
    return results


def kolmogorov_smirnov_test(data1: List[float], data2: List[float]):
    """
    Perform Kolmogorov-Smirnov test to compare two distributions.
    
    Args:
        data1: First dataset
        data2: Second dataset
    
    Returns:
        Dict with KS statistic and p-value
    """
    if HAS_SCIPY:
        ks_stat, p_value = stats.ks_2samp(data1, data2)
        return {
            'ks_statistic': ks_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    else:
        # Simplified KS test
        data1_sorted = sorted(data1)
        data2_sorted = sorted(data2)
        
        # Empirical CDFs
        n1, n2 = len(data1), len(data2)
        
        # Merge and calculate max difference
        all_values = sorted(set(data1_sorted + data2_sorted))
        max_diff = 0
        
        for value in all_values:
            cdf1 = sum(1 for x in data1_sorted if x <= value) / n1
            cdf2 = sum(1 for x in data2_sorted if x <= value) / n2
            diff = abs(cdf1 - cdf2)
            max_diff = max(max_diff, diff)
        
        return {
            'ks_statistic': max_diff,
            'p_value': None,  # Not computed without scipy
            'significant': max_diff > 0.3  # Rule of thumb
        }


def mann_whitney_test(data1: List[float], data2: List[float]):
    """
    Perform Mann-Whitney U test for comparing distributions.
    
    Args:
        data1: First dataset
        data2: Second dataset
    
    Returns:
        Dict with U statistic and p-value
    """
    if HAS_SCIPY:
        u_stat, p_value = stats.mannwhitneyu(data1, data2, alternative='two-sided')
        return {
            'u_statistic': u_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    else:
        # Simplified rank-sum test
        combined = [(x, 1) for x in data1] + [(x, 2) for x in data2]
        combined.sort(key=lambda x: x[0])
        
        rank_sum_1 = sum(i + 1 for i, (val, group) in enumerate(combined) if group == 1)
        n1, n2 = len(data1), len(data2)
        
        u1 = rank_sum_1 - n1 * (n1 + 1) / 2
        
        return {
            'u_statistic': u1,
            'p_value': None,
            'significant': abs(u1 - n1 * n2 / 2) > n1 * n2 / 4  # Rule of thumb
        }


def test_asymmetric_enrichment_hypothesis():
    """
    Test hypothesis: q (larger factor) shows preferential enrichment
    at distances farther from sqrt(N).
    
    Uses KS and Mann-Whitney tests to validate asymmetry.
    """
    print("\nAsymmetric Enrichment Hypothesis Test")
    print("=" * 60)
    
    # Generate test semiprimes with controlled asymmetry
    test_cases = []
    
    # Balanced semiprimes (p ≈ q)
    balanced = [
        (3, 5), (5, 7), (11, 13), (17, 19), (29, 31),
        (41, 43), (59, 61), (71, 73)
    ]
    
    # Unbalanced semiprimes (q >> p)
    unbalanced = [
        (3, 97), (5, 89), (7, 83), (11, 79), (13, 73),
        (17, 67), (19, 61), (23, 59)
    ]
    
    balanced_semiprimes = [p * q for p, q in balanced]
    unbalanced_semiprimes = [p * q for p, q in unbalanced]
    
    # Analyze enrichment patterns
    print("\nAnalyzing balanced semiprimes...")
    balanced_analysis = analyze_asymmetric_enrichment(balanced_semiprimes)
    
    print("\nAnalyzing unbalanced semiprimes...")
    unbalanced_analysis = analyze_asymmetric_enrichment(unbalanced_semiprimes)
    
    # Extract enrichment metrics
    balanced_q_enrichments = []
    unbalanced_q_enrichments = []
    
    for result in balanced_analysis['results']:
        for search in result['searches']:
            if search['q_enrichment'] > 0:
                balanced_q_enrichments.append(search['q_enrichment'])
    
    for result in unbalanced_analysis['results']:
        for search in result['searches']:
            if search['q_enrichment'] > 0:
                unbalanced_q_enrichments.append(search['q_enrichment'])
    
    print(f"\nBalanced semiprimes: {len(balanced_q_enrichments)} q-enrichment samples")
    print(f"Unbalanced semiprimes: {len(unbalanced_q_enrichments)} q-enrichment samples")
    
    # Statistical tests
    results = {
        'balanced_analysis': balanced_analysis,
        'unbalanced_analysis': unbalanced_analysis
    }
    
    if balanced_q_enrichments and unbalanced_q_enrichments:
        # KS test
        ks_result = kolmogorov_smirnov_test(balanced_q_enrichments, unbalanced_q_enrichments)
        print(f"\nKolmogorov-Smirnov Test:")
        print(f"  KS statistic: {ks_result['ks_statistic']:.4f}")
        if ks_result['p_value'] is not None:
            print(f"  p-value: {ks_result['p_value']:.4f}")
        print(f"  Significant difference: {ks_result['significant']}")
        
        # Mann-Whitney test
        mw_result = mann_whitney_test(balanced_q_enrichments, unbalanced_q_enrichments)
        print(f"\nMann-Whitney U Test:")
        print(f"  U statistic: {mw_result['u_statistic']:.4f}")
        if mw_result['p_value'] is not None:
            print(f"  p-value: {mw_result['p_value']:.4f}")
        print(f"  Significant difference: {mw_result['significant']}")
        
        results['ks_test'] = ks_result
        results['mw_test'] = mw_result
        results['hypothesis_supported'] = ks_result['significant'] or mw_result['significant']
    else:
        results['hypothesis_supported'] = False
    
    return results


def test_prime_prediction_accuracy(test_indices: List[int], k_or_phase=0.27952859830111265):
    """
    Test accuracy of nth prime prediction across scales.
    
    Args:
        test_indices: List of indices to test (e.g., [100, 1000, 10000])
        k_or_phase: Phase constant
    
    Returns:
        Accuracy metrics
    """
    print("\nPrime Prediction Accuracy Test")
    print("=" * 60)
    
    # Known primes for validation (small scale)
    known_primes = {
        1: 2,
        2: 3,
        10: 29,
        100: 541,
        1000: 7919,
    }
    
    results = {
        'tests': [],
        'mean_error_pct': None
    }
    
    errors = []
    
    for n in test_indices:
        if n in known_primes:
            actual = known_primes[n]
            estimated = int(n_est(n, k_or_phase))
            error_pct = abs(estimated - actual) / actual * 100
            
            print(f"n={n:6d}: actual={actual:8d}, estimated={estimated:8d}, error={error_pct:.4f}%")
            
            results['tests'].append({
                'n': n,
                'actual': actual,
                'estimated': estimated,
                'error_pct': error_pct
            })
            
            errors.append(error_pct)
    
    if errors:
        results['mean_error_pct'] = statistics.mean(errors)
        results['max_error_pct'] = max(errors)
        results['accuracy_acceptable'] = results['mean_error_pct'] < 1.0  # < 1% error
        
        print(f"\nMean error: {results['mean_error_pct']:.4f}%")
        print(f"Max error: {results['max_error_pct']:.4f}%")
        print(f"Accuracy acceptable: {results['accuracy_acceptable']}")
    
    return results


def comprehensive_validation():
    """
    Run comprehensive validation of all hypotheses.
    """
    print("=" * 60)
    print("Z5D Hypothesis Comprehensive Validation")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Scale invariance
    print("\n[Test 1/3] Scale Invariance Test")
    scales = [2, 3, 4, 5, 6]  # 10^2 to 10^6
    scale_results = test_scale_invariance(scales)
    results['scale_invariance'] = scale_results
    
    # Test 2: Asymmetric enrichment
    print("\n[Test 2/3] Asymmetric Enrichment Test")
    enrichment_results = test_asymmetric_enrichment_hypothesis()
    results['asymmetric_enrichment'] = enrichment_results
    
    # Test 3: Prime prediction accuracy
    print("\n[Test 3/3] Prime Prediction Accuracy Test")
    prediction_results = test_prime_prediction_accuracy([1, 2, 10, 100, 1000])
    results['prime_prediction'] = prediction_results
    
    # Overall assessment
    print("\n" + "=" * 60)
    print("OVERALL ASSESSMENT")
    print("=" * 60)
    
    scale_inv_pass = results['scale_invariance'].get('scale_invariant', False)
    enrichment_pass = results['asymmetric_enrichment'].get('hypothesis_supported', False)
    prediction_pass = results['prime_prediction'].get('accuracy_acceptable', False)
    
    print(f"Scale Invariance: {'✓ PASS' if scale_inv_pass else '✗ FAIL'}")
    print(f"Asymmetric Enrichment: {'✓ PASS' if enrichment_pass else '✗ FAIL'}")
    print(f"Prime Prediction Accuracy: {'✓ PASS' if prediction_pass else '✗ FAIL'}")
    
    all_pass = scale_inv_pass and enrichment_pass and prediction_pass
    results['all_tests_passed'] = all_pass
    
    print(f"\nFinal Verdict: {'✓ HYPOTHESIS VALIDATED' if all_pass else '✗ HYPOTHESIS NOT VALIDATED'}")
    
    return results


if __name__ == "__main__":
    results = comprehensive_validation()
    
    # Exit with appropriate code
    sys.exit(0 if results['all_tests_passed'] else 1)
