#!/usr/bin/env python3
"""
Comparative Analysis: Baseline vs Categorical GVA

Statistically compares baseline and categorical GVA implementations to
prove or falsify the biproduct enhancement hypothesis.

Mission Charter Compliance: See EXPERIMENT_REPORT.md for full charter elements.
"""

import sys
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats


def load_results(results_dir: Path) -> Tuple[List[Dict], List[Dict]]:
    """
    Load baseline and categorical results.
    
    Args:
        results_dir: Results directory path
        
    Returns:
        Tuple of (baseline_results, categorical_results)
    """
    baseline_file = results_dir / "baseline_profile.json"
    categorical_file = results_dir / "categorical_profile.json"
    
    baseline = []
    categorical = []
    
    if baseline_file.exists():
        with open(baseline_file) as f:
            baseline = json.load(f)
    
    if categorical_file.exists():
        with open(categorical_file) as f:
            categorical = json.load(f)
    
    return baseline, categorical


def compute_variance_ratio(baseline: List[Dict], categorical: List[Dict]) -> Dict:
    """
    Compute variance reduction ratio.
    
    Args:
        baseline: Baseline results
        categorical: Categorical results
        
    Returns:
        Variance analysis dictionary
    """
    # Extract total variances
    baseline_vars = [r['variance']['total'] for r in baseline]
    categorical_vars = [r['variance']['total'] for r in categorical]
    
    if not baseline_vars or not categorical_vars:
        return {"error": "Insufficient data"}
    
    # Compute ratio (categorical / baseline)
    mean_baseline = np.mean(baseline_vars)
    mean_categorical = np.mean(categorical_vars)
    
    ratio = mean_categorical / mean_baseline if mean_baseline > 0 else float('inf')
    reduction_pct = (1 - ratio) * 100
    
    # Statistical test (paired t-test if same test cases)
    if len(baseline_vars) == len(categorical_vars):
        t_stat, p_value = stats.ttest_rel(baseline_vars, categorical_vars)
    else:
        t_stat, p_value = stats.ttest_ind(baseline_vars, categorical_vars)
    
    return {
        "baseline_mean": mean_baseline,
        "baseline_std": float(np.std(baseline_vars)),
        "categorical_mean": mean_categorical,
        "categorical_std": float(np.std(categorical_vars)),
        "ratio": ratio,
        "reduction_percent": reduction_pct,
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
        "n_baseline": len(baseline_vars),
        "n_categorical": len(categorical_vars)
    }


def compute_timing_comparison(baseline: List[Dict], categorical: List[Dict]) -> Dict:
    """
    Compare computational efficiency.
    
    Args:
        baseline: Baseline results
        categorical: Categorical results
        
    Returns:
        Timing comparison dictionary
    """
    # Extract per-candidate times
    baseline_embed = [r['timing']['embed_per_candidate_sec'] * 1e6 for r in baseline]
    categorical_embed = [r['timing']['embed_per_candidate_sec'] * 1e6 for r in categorical]
    
    baseline_dist = [r['timing']['distance_per_candidate_sec'] * 1e6 for r in baseline]
    categorical_dist = [r['timing']['distance_per_candidate_sec'] * 1e6 for r in categorical]
    
    if not baseline_embed or not categorical_embed:
        return {"error": "Insufficient data"}
    
    embed_overhead = np.mean(categorical_embed) / np.mean(baseline_embed)
    dist_overhead = np.mean(categorical_dist) / np.mean(baseline_dist)
    
    return {
        "embedding": {
            "baseline_us_mean": float(np.mean(baseline_embed)),
            "baseline_us_std": float(np.std(baseline_embed)),
            "categorical_us_mean": float(np.mean(categorical_embed)),
            "categorical_us_std": float(np.std(categorical_embed)),
            "overhead_ratio": float(embed_overhead)
        },
        "distance": {
            "baseline_us_mean": float(np.mean(baseline_dist)),
            "baseline_us_std": float(np.std(baseline_dist)),
            "categorical_us_mean": float(np.mean(categorical_dist)),
            "categorical_us_std": float(np.std(categorical_dist)),
            "overhead_ratio": float(dist_overhead)
        }
    }


def compute_convergence_metrics(baseline: List[Dict], categorical: List[Dict]) -> Dict:
    """
    Compare convergence properties.
    
    Args:
        baseline: Baseline results
        categorical: Categorical results
        
    Returns:
        Convergence metrics dictionary
    """
    # Minimum distances to true factors
    baseline_min_p = [r['distances']['min_to_p'] for r in baseline]
    categorical_min_p = [r['distances']['min_to_p'] for r in categorical]
    
    baseline_min_q = [r['distances']['min_to_q'] for r in baseline]
    categorical_min_q = [r['distances']['min_to_q'] for r in categorical]
    
    if not baseline_min_p or not categorical_min_p:
        return {"error": "Insufficient data"}
    
    # Lower distance is better
    p_improvement = (np.mean(baseline_min_p) - np.mean(categorical_min_p)) / np.mean(baseline_min_p) * 100
    q_improvement = (np.mean(baseline_min_q) - np.mean(categorical_min_q)) / np.mean(baseline_min_q) * 100
    
    return {
        "min_distance_to_p": {
            "baseline_mean": float(np.mean(baseline_min_p)),
            "categorical_mean": float(np.mean(categorical_min_p)),
            "improvement_percent": float(p_improvement)
        },
        "min_distance_to_q": {
            "baseline_mean": float(np.mean(baseline_min_q)),
            "categorical_mean": float(np.mean(categorical_min_q)),
            "improvement_percent": float(q_improvement)
        }
    }


def apply_falsifiability_criteria(analysis: Dict) -> Dict:
    """
    Apply falsifiability criteria to determine verdict.
    
    Criteria (from THEORY.md):
    1. Variance ratio > 0.95 (less than 5% reduction) → FALSIFIED
    2. No significant improvement (p > 0.05) → FALSIFIED  
    3. Computational overhead > 2× → FALSIFIED
    4. No dimensional insights → FALSIFIED (subjective, check variance ratios)
    
    Args:
        analysis: Complete analysis dictionary
        
    Returns:
        Verdict dictionary
    """
    falsified_reasons = []
    proven_evidence = []
    
    # Criterion 1: Variance reduction
    var_analysis = analysis.get('variance_analysis', {})
    if 'ratio' in var_analysis:
        var_ratio = var_analysis['ratio']
        if var_ratio > 0.95:
            falsified_reasons.append(
                f"Variance ratio {var_ratio:.3f} > 0.95 (less than 5% reduction)"
            )
        else:
            reduction_pct = var_analysis.get('reduction_percent', 0)
            proven_evidence.append(
                f"Variance reduced by {reduction_pct:.2f}%"
            )
    
    # Criterion 2: Statistical significance
    if 'p_value' in var_analysis:
        p_val = var_analysis['p_value']
        significant = var_analysis.get('significant', False)
        if not significant:
            falsified_reasons.append(
                f"No significant variance difference (p={p_val:.4f} > 0.05)"
            )
        else:
            proven_evidence.append(
                f"Significant variance difference (p={p_val:.4f})"
            )
    
    # Criterion 3: Computational overhead
    timing = analysis.get('timing_comparison', {})
    embed_overhead = timing.get('embedding', {}).get('overhead_ratio', 1.0)
    dist_overhead = timing.get('distance', {}).get('overhead_ratio', 1.0)
    max_overhead = max(embed_overhead, dist_overhead)
    
    if max_overhead > 2.0:
        falsified_reasons.append(
            f"Computational overhead {max_overhead:.2f}× > 2.0×"
        )
    else:
        proven_evidence.append(
            f"Acceptable overhead (max {max_overhead:.2f}×)"
        )
    
    # Criterion 4: Dimensional insights (check variance component ratios)
    # Look for evidence that some dimensions matter more than others
    dimensional_insight = False
    if var_analysis.get('categorical_mean', 0) < var_analysis.get('baseline_mean', 1):
        dimensional_insight = True
        proven_evidence.append("Categorical decomposition shows dimensional structure")
    
    # Final verdict
    if falsified_reasons:
        verdict = "FALSIFIED"
        confidence = "HIGH" if len(falsified_reasons) >= 2 else "MODERATE"
    elif len(proven_evidence) >= 3:
        verdict = "PROVEN"
        confidence = "MODERATE"  # Need more test cases for HIGH
    else:
        verdict = "INCONCLUSIVE"
        confidence = "LOW"
    
    return {
        "verdict": verdict,
        "confidence": confidence,
        "falsified_reasons": falsified_reasons,
        "proven_evidence": proven_evidence,
        "criteria_summary": {
            "variance_reduction": var_ratio < 0.95 if 'ratio' in var_analysis else None,
            "statistical_significance": var_analysis.get('significant', False),
            "acceptable_overhead": max_overhead <= 2.0,
            "dimensional_insights": dimensional_insight
        }
    }


def main():
    """Run comparative analysis and generate verdict."""
    print("=" * 80)
    print("Comparative Analysis: Baseline vs Categorical GVA")
    print("=" * 80)
    print()
    
    results_dir = Path(__file__).parent.parent / "results"
    
    # Load results
    baseline, categorical = load_results(results_dir)
    
    if not baseline:
        print("Error: No baseline results found. Run baseline_gva_profile.py first.")
        return
    
    if not categorical:
        print("Error: No categorical results found. Run categorical_gva.py first.")
        return
    
    print(f"Loaded {len(baseline)} baseline results")
    print(f"Loaded {len(categorical)} categorical results")
    print()
    
    # Compute comparisons
    print("Computing variance analysis...")
    variance_analysis = compute_variance_ratio(baseline, categorical)
    
    print("Computing timing comparison...")
    timing_comparison = compute_timing_comparison(baseline, categorical)
    
    print("Computing convergence metrics...")
    convergence_metrics = compute_convergence_metrics(baseline, categorical)
    
    # Complete analysis
    analysis = {
        "variance_analysis": variance_analysis,
        "timing_comparison": timing_comparison,
        "convergence_metrics": convergence_metrics
    }
    
    # Apply falsifiability criteria
    print("Applying falsifiability criteria...")
    verdict = apply_falsifiability_criteria(analysis)
    analysis["verdict"] = verdict
    
    # Print results
    print()
    print("=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print()
    
    print("Variance Analysis:")
    print(f"  Baseline mean:      {variance_analysis['baseline_mean']:.6f}")
    print(f"  Categorical mean:   {variance_analysis['categorical_mean']:.6f}")
    print(f"  Ratio (cat/base):   {variance_analysis['ratio']:.3f}")
    print(f"  Reduction:          {variance_analysis['reduction_percent']:.2f}%")
    print(f"  t-statistic:        {variance_analysis['t_statistic']:.3f}")
    print(f"  p-value:            {variance_analysis['p_value']:.4f}")
    print(f"  Significant:        {variance_analysis['significant']}")
    print()
    
    print("Timing Comparison:")
    print(f"  Embedding overhead: {timing_comparison['embedding']['overhead_ratio']:.2f}×")
    print(f"  Distance overhead:  {timing_comparison['distance']['overhead_ratio']:.2f}×")
    print()
    
    print("Convergence Metrics:")
    conv_p = convergence_metrics['min_distance_to_p']
    conv_q = convergence_metrics['min_distance_to_q']
    print(f"  Min dist to p improvement: {conv_p['improvement_percent']:+.2f}%")
    print(f"  Min dist to q improvement: {conv_q['improvement_percent']:+.2f}%")
    print()
    
    print("=" * 80)
    print(f"VERDICT: {verdict['verdict']} (Confidence: {verdict['confidence']})")
    print("=" * 80)
    print()
    
    if verdict['falsified_reasons']:
        print("Falsified because:")
        for reason in verdict['falsified_reasons']:
            print(f"  ✗ {reason}")
        print()
    
    if verdict['proven_evidence']:
        print("Supporting evidence:")
        for evidence in verdict['proven_evidence']:
            print(f"  ✓ {evidence}")
        print()
    
    # Save analysis (convert numpy bools to Python bools)
    def convert_types(obj):
        """Convert numpy types to Python native types for JSON serialization."""
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(item) for item in obj]
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        else:
            return obj
    
    output_file = results_dir / "comparative_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(convert_types(analysis), f, indent=2)
    
    print(f"Full analysis saved to: {output_file}")
    print()
    
    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Hypothesis: Category-theoretic biproduct decomposition enhances GVA")
    print(f"Verdict:    {verdict['verdict']}")
    print(f"Confidence: {verdict['confidence']}")
    print()
    
    if verdict['verdict'] == "FALSIFIED":
        print("The hypothesis is FALSIFIED. Categorical biproduct decomposition")
        print("does not provide significant advantages over baseline GVA in the")
        print("tested configurations.")
    elif verdict['verdict'] == "PROVEN":
        print("The hypothesis shows PROMISING evidence. Categorical biproduct")
        print("decomposition provides measurable benefits. Further validation")
        print("on larger test sets is recommended.")
    else:
        print("The hypothesis is INCONCLUSIVE. More experiments are needed to")
        print("reach a definitive conclusion.")
    print()


if __name__ == "__main__":
    main()
