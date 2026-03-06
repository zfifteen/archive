#!/usr/bin/env python3
"""
Comparative Analysis: Cranley-Patterson vs Baseline

Performs rigorous statistical comparison to falsify the hypothesis:
"Cranley-Patterson rotations yield 1.3-1.8× variance reductions in RSA factor
candidate variance for distant cases."

Falsification Criteria:
1. Variance reduction < 1.3× (claimed lower bound)
2. p-value > 0.05 (not statistically significant)
3. Computational overhead > 2.0× baseline

If ANY criterion is met → HYPOTHESIS FALSIFIED

Author: Z-Sandbox Agent
Date: 2025-11-19
"""

import sys
import os
import json
import numpy as np
from typing import Dict, Tuple
from scipy import stats


def load_results(results_dir: str) -> Dict:
    """Load baseline and CP results from JSON files."""
    results = {
        'baseline': {},
        'cp_static': {},
        'cp_adaptive': {}
    }
    
    for challenge in ['RSA-100', 'RSA-129', 'RSA-155']:
        challenge_lower = challenge.lower()
        
        # Load baseline
        baseline_file = os.path.join(results_dir, f'baseline_{challenge_lower}.json')
        if os.path.exists(baseline_file):
            with open(baseline_file, 'r') as f:
                results['baseline'][challenge] = json.load(f)
        
        # Load CP static
        cp_static_file = os.path.join(results_dir, f'cp_static_{challenge_lower}.json')
        if os.path.exists(cp_static_file):
            with open(cp_static_file, 'r') as f:
                results['cp_static'][challenge] = json.load(f)
        
        # Load CP adaptive
        cp_adaptive_file = os.path.join(results_dir, f'cp_adaptive_{challenge_lower}.json')
        if os.path.exists(cp_adaptive_file):
            with open(cp_adaptive_file, 'r') as f:
                results['cp_adaptive'][challenge] = json.load(f)
    
    return results


def extract_variances(result_data: Dict) -> np.ndarray:
    """Extract variance array from result data."""
    return np.array([trial['variance'] for trial in result_data['trials']])


def extract_timings(result_data: Dict) -> np.ndarray:
    """Extract timing array from result data."""
    return np.array([trial['timing_sec'] for trial in result_data['trials']])


def compute_variance_reduction(
    baseline_var: float,
    treatment_var: float
) -> float:
    """
    Compute variance reduction ratio.
    
    Returns:
        Reduction factor (> 1.0 means treatment is better)
    """
    return baseline_var / treatment_var


def perform_ttest(
    baseline_data: np.ndarray,
    treatment_data: np.ndarray
) -> Tuple[float, float]:
    """
    Perform two-sample t-test.
    
    Returns:
        (t_statistic, p_value)
    """
    return stats.ttest_ind(baseline_data, treatment_data)


def compute_cohens_d(
    baseline_data: np.ndarray,
    treatment_data: np.ndarray
) -> float:
    """
    Compute Cohen's d effect size.
    
    Returns:
        Effect size (0.2=small, 0.5=medium, 0.8=large)
    """
    mean_diff = np.mean(baseline_data) - np.mean(treatment_data)
    pooled_std = np.sqrt(
        (np.var(baseline_data) + np.var(treatment_data)) / 2
    )
    return mean_diff / pooled_std if pooled_std > 0 else 0.0


def compare_treatments(
    baseline_result: Dict,
    treatment_result: Dict,
    treatment_name: str
) -> Dict:
    """
    Compare baseline vs treatment for a single RSA challenge.
    
    Returns:
        Comparison statistics and verdict
    """
    # Extract data
    baseline_vars = extract_variances(baseline_result)
    treatment_vars = extract_variances(treatment_result)
    baseline_times = extract_timings(baseline_result)
    treatment_times = extract_timings(treatment_result)
    
    # Variance comparison
    baseline_mean_var = np.mean(baseline_vars)
    treatment_mean_var = np.mean(treatment_vars)
    variance_reduction = compute_variance_reduction(baseline_mean_var, treatment_mean_var)
    
    # Statistical test
    t_stat, p_value = perform_ttest(baseline_vars, treatment_vars)
    cohens_d = compute_cohens_d(baseline_vars, treatment_vars)
    
    # Handle NaN values
    if np.isnan(p_value):
        p_value = 1.0  # Conservative: assume not significant
    if np.isnan(cohens_d):
        cohens_d = 0.0
    
    # Timing overhead
    baseline_mean_time = np.mean(baseline_times)
    treatment_mean_time = np.mean(treatment_times)
    timing_overhead = treatment_mean_time / baseline_mean_time
    
    # Falsification criteria
    criteria = {
        'variance_reduction_below_1.3x': bool(variance_reduction < 1.3),
        'not_significant': bool(p_value > 0.05),
        'overhead_above_2x': bool(timing_overhead > 2.0)
    }
    
    any_criterion_met = any(criteria.values())
    
    # Verdict
    if any_criterion_met:
        verdict = "FALSIFIED"
        confidence = "HIGH" if sum(criteria.values()) >= 2 else "MEDIUM"
    else:
        verdict = "NOT FALSIFIED"
        confidence = "MEDIUM"
    
    return {
        'treatment': treatment_name,
        'variance': {
            'baseline_mean': float(baseline_mean_var),
            'baseline_std': float(np.std(baseline_vars)),
            'treatment_mean': float(treatment_mean_var),
            'treatment_std': float(np.std(treatment_vars)),
            'reduction_factor': float(variance_reduction),
            'reduction_pct': float((variance_reduction - 1.0) * 100)
        },
        'statistics': {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'cohens_d': float(cohens_d),
            'significant': bool(p_value < 0.05)
        },
        'timing': {
            'baseline_mean_sec': float(baseline_mean_time),
            'treatment_mean_sec': float(treatment_mean_time),
            'overhead_factor': float(timing_overhead),
            'overhead_pct': float((timing_overhead - 1.0) * 100)
        },
        'falsification_criteria': criteria,
        'verdict': {
            'status': verdict,
            'confidence': confidence,
            'criteria_met': int(sum(criteria.values())),
            'total_criteria': len(criteria)
        }
    }


def generate_summary(all_comparisons: Dict) -> Dict:
    """
    Generate overall summary across all challenges and treatments.
    
    Returns:
        Summary statistics and final verdict
    """
    # Count verdicts
    total_comparisons = 0
    falsified_count = 0
    
    for challenge in all_comparisons:
        for treatment in all_comparisons[challenge]:
            total_comparisons += 1
            if all_comparisons[challenge][treatment]['verdict']['status'] == 'FALSIFIED':
                falsified_count += 1
    
    # Overall verdict
    if falsified_count == total_comparisons:
        overall_verdict = "HYPOTHESIS DEFINITIVELY FALSIFIED"
        overall_confidence = "HIGH"
    elif falsified_count > total_comparisons / 2:
        overall_verdict = "HYPOTHESIS LIKELY FALSIFIED"
        overall_confidence = "MEDIUM"
    else:
        overall_verdict = "HYPOTHESIS NOT FALSIFIED"
        overall_confidence = "LOW"
    
    return {
        'total_comparisons': total_comparisons,
        'falsified_count': falsified_count,
        'falsified_percentage': float(falsified_count / total_comparisons * 100),
        'overall_verdict': overall_verdict,
        'overall_confidence': overall_confidence
    }


def main():
    """Run comparative analysis and generate verdict."""
    results_dir = "../results"
    
    print("\n" + "="*70)
    print("CRANLEY-PATTERSON QMC VARIANCE REDUCTION: COMPARATIVE ANALYSIS")
    print("="*70)
    
    # Load results
    print("\nLoading results...")
    results = load_results(results_dir)
    
    # Perform comparisons
    all_comparisons = {}
    
    for challenge in ['RSA-100', 'RSA-129', 'RSA-155']:
        print(f"\n{'-'*70}")
        print(f"CHALLENGE: {challenge}")
        print(f"{'-'*70}")
        
        if challenge not in results['baseline']:
            print(f"  ✗ Baseline results not found for {challenge}")
            continue
        
        baseline = results['baseline'][challenge]
        all_comparisons[challenge] = {}
        
        # Compare each treatment
        for treatment_key, treatment_name in [('cp_static', 'CP-Static'), ('cp_adaptive', 'CP-Adaptive')]:
            if challenge not in results[treatment_key]:
                print(f"  ✗ {treatment_name} results not found for {challenge}")
                continue
            
            treatment = results[treatment_key][challenge]
            comparison = compare_treatments(baseline, treatment, treatment_name)
            all_comparisons[challenge][treatment_name] = comparison
            
            # Print results
            print(f"\n{treatment_name}:")
            print(f"  Variance Reduction: {comparison['variance']['reduction_factor']:.3f}× "
                  f"({comparison['variance']['reduction_pct']:+.1f}%)")
            print(f"  Statistical Significance: p={comparison['statistics']['p_value']:.4f} "
                  f"({'✓ YES' if comparison['statistics']['significant'] else '✗ NO'})")
            print(f"  Cohen's d: {comparison['statistics']['cohens_d']:.3f}")
            print(f"  Timing Overhead: {comparison['timing']['overhead_factor']:.3f}× "
                  f"({comparison['timing']['overhead_pct']:+.1f}%)")
            print(f"\n  Falsification Criteria:")
            for criterion, met in comparison['falsification_criteria'].items():
                status = "✓ MET" if met else "✗ NOT MET"
                print(f"    {criterion}: {status}")
            print(f"\n  VERDICT: {comparison['verdict']['status']} "
                  f"(Confidence: {comparison['verdict']['confidence']})")
    
    # Generate summary
    summary = generate_summary(all_comparisons)
    
    print(f"\n{'='*70}")
    print("OVERALL VERDICT")
    print(f"{'='*70}")
    print(f"Total Comparisons: {summary['total_comparisons']}")
    print(f"Falsified: {summary['falsified_count']} ({summary['falsified_percentage']:.1f}%)")
    print(f"\n{summary['overall_verdict']}")
    print(f"Confidence: {summary['overall_confidence']}")
    print()
    
    # Save results
    output = {
        'comparisons': all_comparisons,
        'summary': summary,
        'hypothesis': {
            'claim': 'Cranley-Patterson rotations yield 1.3-1.8× variance reductions',
            'falsification_criteria': [
                'Variance reduction < 1.3× (claimed lower bound)',
                'p-value > 0.05 (not statistically significant)',
                'Computational overhead > 2.0× baseline'
            ]
        }
    }
    
    output_file = os.path.join(results_dir, 'comparative_analysis.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"✓ Analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
