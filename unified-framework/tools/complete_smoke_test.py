#!/usr/bin/env python3
"""
Z-Curvature Genomic Features - Complete Smoke Test Results

This script runs the complete smoke test suite and generates a summary report
answering the three key questions from the issue.
"""

import sys
import os
import json

# Add the applications module to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'applications'))

from genomic_smoke_test import GenomicSmokeTest

def run_complete_smoke_test():
    """Run all smoke test configurations and summarize results."""
    
    print("🚦 Z-CURVATURE GENOMIC FEATURES - COMPLETE SMOKE TEST")
    print("=" * 80)
    print()
    print("Background: Testing if Z-curvature features derived from θ'(i,k) = φ·{i/φ}^k")
    print("can capture 'prime-like' sparsity/structure for genomic tasks.")
    print()
    
    all_results = {}
    
    # Test 1: Quick mode with challenging dataset
    print("🏃 TEST 1: Quick Mode (Challenging Dataset)")
    print("-" * 50)
    quick_test = GenomicSmokeTest(quick_mode=True)
    results_quick = quick_test.run_smoke_test(dataset_type="challenging")
    all_results['quick_challenging'] = results_quick
    print()
    
    # Test 2: Full mode with challenging dataset  
    print("🔬 TEST 2: Full Mode (Challenging Dataset)")
    print("-" * 50)
    full_test = GenomicSmokeTest(quick_mode=False)
    full_test.n_samples = 100  # Reasonable size for smoke test
    results_full = full_test.run_smoke_test(dataset_type="challenging")
    all_results['full_challenging'] = results_full
    print()
    
    # Test 3: Real genomic data
    print("🧬 TEST 3: Real Genomic Sequences")
    print("-" * 50)
    real_test = GenomicSmokeTest(quick_mode=True)
    results_real = real_test.run_smoke_test(dataset_type="real")
    all_results['real_sequences'] = results_real
    print()
    
    # Summary Analysis
    print("📊 COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
    # Question 1: Measurable lift over baseline?
    print("❓ Q1: Do Z-features provide measurable lift over naive baseline?")
    
    lifts = []
    for test_name, result in all_results.items():
        z_auc = result['performance']['z_curvature']['auc']
        baseline_auc = result['performance']['baseline']['auc']
        if baseline_auc > 0:
            lift = (z_auc - baseline_auc) / baseline_auc * 100
            lifts.append(lift)
            print(f"   {test_name}: {lift:+.1f}% AUC lift")
    
    avg_lift = sum(lifts) / len(lifts) if lifts else 0
    if avg_lift > 1.0:
        q1_answer = f"✅ YES - Average {avg_lift:.1f}% improvement across tests"
    elif avg_lift > 0:
        q1_answer = f"⚠️  MARGINAL - Average {avg_lift:.1f}% improvement"
    else:
        q1_answer = f"❌ NO - Average {avg_lift:.1f}% change"
    print(f"   ANSWER: {q1_answer}")
    print()
    
    # Question 2: Robust to parameter changes?
    print("❓ Q2: Is the lift robust to trivial changes (window size and k)?")
    
    parameter_tests = [r for r in all_results.values() if len(r['parameters']['k_values']) > 1]
    if parameter_tests:
        q2_answer = "✅ YES - Multiple k values and window sizes tested"
    else:
        q2_answer = "⚠️  PARTIAL - Limited parameter testing in some tests"
    print(f"   ANSWER: {q2_answer}")
    print()
    
    # Question 3: Negligible compute cost?
    print("❓ Q3: Is the compute cost negligible (can run in <5 minutes)?")
    
    total_times = [r['timing']['total_time'] for r in all_results.values()]
    max_time = max(total_times)
    avg_time = sum(total_times) / len(total_times)
    
    if max_time < 300:  # 5 minutes
        q3_answer = f"✅ YES - Max time {max_time:.1f}s, average {avg_time:.1f}s"
    else:
        q3_answer = f"❌ NO - Max time {max_time:.1f}s exceeds 5 minutes"
    print(f"   ANSWER: {q3_answer}")
    print()
    
    # Overall Verdict
    print("🎯 OVERALL SMOKE TEST VERDICT")
    print("=" * 40)
    
    if avg_lift > 1.0 and max_time < 300:
        verdict = "✅ PASS - Z-curvature features show promise for genomic tasks"
        recommendation = "Recommend proceeding with full study"
    elif avg_lift > 0 and max_time < 300:
        verdict = "⚠️  MARGINAL - Small improvements detected"  
        recommendation = "Consider optimizing features before full study"
    else:
        verdict = "❌ FAIL - No significant advantage over baseline"
        recommendation = "Recommend exploring alternative approaches"
    
    print(f"   {verdict}")
    print(f"   {recommendation}")
    print()
    
    # Save detailed results (convert numpy arrays to lists for JSON)
    import numpy as np
    
    def convert_numpy(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        return obj
    
    json_results = convert_numpy(all_results)
    
    with open('z_curvature_smoke_test_results.json', 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"📁 Detailed results saved to: z_curvature_smoke_test_results.json")
    
    return {
        'verdict': verdict,
        'recommendation': recommendation,
        'avg_lift': avg_lift,
        'max_time': max_time,
        'all_results': all_results
    }


if __name__ == "__main__":
    run_complete_smoke_test()