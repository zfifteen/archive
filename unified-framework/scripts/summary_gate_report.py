#!/usr/bin/env python3
"""
Summary Gate Report Generator - Final Assessment
===============================================

Aggregates metrics from all test scripts and generates final PASS/FAIL report
as specified in Issue #677.

Consolidates results from:
- H1: Z5D Accuracy (test_z5d_accuracy.py)
- H2: Form Hit-Rate Uplift (bench_form_hitrate.py)  
- H3: Sqrt-Friendly Fraction QC (qc_sqrt_mod4.py)
- H4: Montgomery Multiplication Speed (bench_modmul_speed.py)
- H5: Density Enhancement (same as H2)
- H6: Zeta Consistency (optional)

Usage:
    python -m scripts.summary_gate_report --strict
    python -m scripts.summary_gate_report --metrics-dir metrics --output REPORT.md
"""

import sys
import os
import argparse
import json
import glob
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HypothesisResult:
    """Result for a single hypothesis test"""
    hypothesis: str
    description: str
    pass_gate: bool
    gate_reason: str
    metrics: Dict[str, Any]
    test_files: List[str]

@dataclass
class GateReport:
    """Complete gate report with all hypothesis results"""
    overall_pass: bool
    total_hypotheses: int
    passed_hypotheses: int
    failed_hypotheses: int
    hypothesis_results: List[HypothesisResult]
    generation_time: str
    test_summary: Dict[str, Any]

def find_metrics_files(metrics_dir: str) -> Dict[str, List[str]]:
    """
    Find all metrics files organized by hypothesis.
    
    Returns:
        Dict mapping hypothesis names to lists of metrics files
    """
    metrics_files = {
        'H1_accuracy': [],
        'H2_form_hitrate': [], 
        'H3_sqrt_friendly': [],
        'H4_modmul_speed': [],
        'H5_density_enhancement': [],  # Same as H2
        'H6_zeta_consistency': []
    }
    
    if not os.path.exists(metrics_dir):
        logger.warning(f"Metrics directory not found: {metrics_dir}")
        return metrics_files
    
    # Find accuracy metrics
    accuracy_files = glob.glob(os.path.join(metrics_dir, "accuracy*.json"))
    metrics_files['H1_accuracy'] = accuracy_files
    
    # Find form hit-rate metrics
    hitrate_files = glob.glob(os.path.join(metrics_dir, "form_hitrate_*.json"))
    metrics_files['H2_form_hitrate'] = hitrate_files
    metrics_files['H5_density_enhancement'] = hitrate_files  # H5 same as H2
    
    # Find sqrt-friendly metrics
    sqrt_files = glob.glob(os.path.join(metrics_dir, "sqrt_frac_*.json"))
    metrics_files['H3_sqrt_friendly'] = sqrt_files
    
    # Find modmul speed metrics
    modmul_files = glob.glob(os.path.join(metrics_dir, "modmul_*.json"))
    metrics_files['H4_modmul_speed'] = modmul_files
    
    # Find zeta consistency metrics (if present)
    zeta_files = glob.glob(os.path.join(metrics_dir, "zeta_consistency*.json"))
    metrics_files['H6_zeta_consistency'] = zeta_files
    
    logger.info(f"Found metrics files:")
    for hyp, files in metrics_files.items():
        logger.info(f"  {hyp}: {len(files)} files")
    
    return metrics_files

def load_metrics_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load and parse a metrics JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return None

def assess_h1_accuracy(metrics_files: List[str]) -> HypothesisResult:
    """Assess H1: Z5D Accuracy hypothesis"""
    if not metrics_files:
        return HypothesisResult(
            hypothesis="H1",
            description="Z5D Accuracy",
            pass_gate=False,
            gate_reason="No accuracy metrics found",
            metrics={},
            test_files=[]
        )
    
    all_metrics = []
    for file_path in metrics_files:
        metrics = load_metrics_file(file_path)
        if metrics:
            all_metrics.append(metrics)
    
    if not all_metrics:
        return HypothesisResult(
            hypothesis="H1",
            description="Z5D Accuracy",
            pass_gate=False,
            gate_reason="Could not load accuracy metrics",
            metrics={},
            test_files=metrics_files
        )
    
    # Aggregate results - all must pass for overall pass
    overall_pass = all(m.get('pass_gate', False) for m in all_metrics)
    
    # Collect key statistics
    median_errors = [m.get('median_relative_error') for m in all_metrics if m.get('median_relative_error') is not None]
    p99_errors = [m.get('p99_relative_error') for m in all_metrics if m.get('p99_relative_error') is not None]
    
    aggregated_metrics = {
        'total_tests': len(all_metrics),
        'passed_tests': sum(1 for m in all_metrics if m.get('pass_gate', False)),
        'median_relative_errors': median_errors,
        'p99_relative_errors': p99_errors,
        'best_median_error': min(median_errors) if median_errors else None,
        'worst_median_error': max(median_errors) if median_errors else None,
        'best_p99_error': min(p99_errors) if p99_errors else None,
        'worst_p99_error': max(p99_errors) if p99_errors else None
    }
    
    if overall_pass:
        gate_reason = f"All {len(all_metrics)} accuracy tests passed"
    else:
        failed_count = len(all_metrics) - sum(1 for m in all_metrics if m.get('pass_gate', False))
        gate_reason = f"{failed_count}/{len(all_metrics)} accuracy tests failed"
    
    return HypothesisResult(
        hypothesis="H1",
        description="Z5D Accuracy (median ≤ 0.01%, 99th-pct ≤ 0.03%)",
        pass_gate=overall_pass,
        gate_reason=gate_reason,
        metrics=aggregated_metrics,
        test_files=metrics_files
    )

def assess_h2_form_hitrate(metrics_files: List[str]) -> HypothesisResult:
    """Assess H2: Form Hit-Rate Uplift hypothesis"""
    if not metrics_files:
        return HypothesisResult(
            hypothesis="H2",
            description="Form Hit-Rate Uplift",
            pass_gate=False,
            gate_reason="No form hit-rate metrics found",
            metrics={},
            test_files=[]
        )
    
    all_metrics = []
    for file_path in metrics_files:
        metrics = load_metrics_file(file_path)
        if metrics and 'statistics' in metrics:
            all_metrics.append(metrics['statistics'])
    
    if not all_metrics:
        return HypothesisResult(
            hypothesis="H2", 
            description="Form Hit-Rate Uplift",
            pass_gate=False,
            gate_reason="Could not load hit-rate statistics",
            metrics={},
            test_files=metrics_files
        )
    
    # Aggregate results
    overall_pass = all(m.get('pass_gate', False) for m in all_metrics)
    
    # Collect key statistics
    deltas = [m.get('delta') for m in all_metrics if m.get('delta') is not None]
    ratios = [m.get('ratio') for m in all_metrics if m.get('ratio') is not None and m.get('ratio') != float('inf')]
    
    aggregated_metrics = {
        'total_tests': len(all_metrics),
        'passed_tests': sum(1 for m in all_metrics if m.get('pass_gate', False)),
        'hit_rate_deltas': deltas,
        'hit_rate_ratios': ratios,
        'best_delta': max(deltas) if deltas else None,
        'worst_delta': min(deltas) if deltas else None,
        'best_ratio': max(ratios) if ratios else None,
        'worst_ratio': min(ratios) if ratios else None
    }
    
    if overall_pass:
        gate_reason = f"All {len(all_metrics)} hit-rate tests passed"
    else:
        failed_count = len(all_metrics) - sum(1 for m in all_metrics if m.get('pass_gate', False))
        gate_reason = f"{failed_count}/{len(all_metrics)} hit-rate tests failed"
    
    return HypothesisResult(
        hypothesis="H2",
        description="Form Hit-Rate Uplift (≥20% improvement or ≥1.2× ratio)",
        pass_gate=overall_pass,
        gate_reason=gate_reason,
        metrics=aggregated_metrics,
        test_files=metrics_files
    )

def assess_h3_sqrt_friendly(metrics_files: List[str]) -> HypothesisResult:
    """Assess H3: Sqrt-Friendly Fraction QC hypothesis"""
    if not metrics_files:
        return HypothesisResult(
            hypothesis="H3",
            description="Sqrt-Friendly Fraction QC",
            pass_gate=False,
            gate_reason="No sqrt-friendly metrics found",
            metrics={},
            test_files=[]
        )
    
    all_metrics = []
    for file_path in metrics_files:
        metrics = load_metrics_file(file_path)
        if metrics and 'statistics' in metrics:
            all_metrics.append(metrics['statistics'])
    
    if not all_metrics:
        return HypothesisResult(
            hypothesis="H3",
            description="Sqrt-Friendly Fraction QC", 
            pass_gate=False,
            gate_reason="Could not load sqrt-friendly statistics",
            metrics={},
            test_files=metrics_files
        )
    
    # Aggregate results
    overall_pass = all(m.get('pass_gate', False) for m in all_metrics)
    
    # Collect key statistics
    z5d_fractions = [m.get('z5d_fraction') for m in all_metrics if m.get('z5d_fraction') is not None]
    unbiased_deviations = [m.get('unbiased_deviation') for m in all_metrics if m.get('unbiased_deviation') is not None]
    
    aggregated_metrics = {
        'total_tests': len(all_metrics),
        'passed_tests': sum(1 for m in all_metrics if m.get('pass_gate', False)),
        'z5d_fractions': z5d_fractions,
        'unbiased_deviations': unbiased_deviations,
        'closest_to_half': min(unbiased_deviations) if unbiased_deviations else None,
        'furthest_from_half': max(unbiased_deviations) if unbiased_deviations else None
    }
    
    if overall_pass:
        gate_reason = f"All {len(all_metrics)} sqrt-friendly tests passed"
    else:
        failed_count = len(all_metrics) - sum(1 for m in all_metrics if m.get('pass_gate', False))
        gate_reason = f"{failed_count}/{len(all_metrics)} sqrt-friendly tests failed"
    
    return HypothesisResult(
        hypothesis="H3",
        description="Sqrt-Friendly Fraction QC (unbiased ≈50%)",
        pass_gate=overall_pass,
        gate_reason=gate_reason,
        metrics=aggregated_metrics,
        test_files=metrics_files
    )

def assess_h4_modmul_speed(metrics_files: List[str]) -> HypothesisResult:
    """Assess H4: Montgomery Multiplication Speed hypothesis"""
    if not metrics_files:
        return HypothesisResult(
            hypothesis="H4",
            description="Montgomery Multiplication Speed",
            pass_gate=False,
            gate_reason="No modmul speed metrics found",
            metrics={},
            test_files=[]
        )
    
    all_metrics = []
    for file_path in metrics_files:
        metrics = load_metrics_file(file_path)
        if metrics:
            all_metrics.append(metrics)
    
    if not all_metrics:
        return HypothesisResult(
            hypothesis="H4",
            description="Montgomery Multiplication Speed",
            pass_gate=False,
            gate_reason="Could not load modmul speed metrics",
            metrics={},
            test_files=metrics_files
        )
    
    # Aggregate results - only count tests that had special-form primes
    valid_metrics = [m for m in all_metrics if m.get('special_form_primes')]
    overall_pass = all(m.get('pass_gate', False) for m in valid_metrics) if valid_metrics else False
    
    # Collect key statistics
    speedups = [m.get('speedup_percent') for m in valid_metrics if m.get('speedup_percent') is not None]
    
    aggregated_metrics = {
        'total_tests': len(all_metrics),
        'valid_tests': len(valid_metrics),
        'passed_tests': sum(1 for m in valid_metrics if m.get('pass_gate', False)),
        'speedup_percentages': speedups,
        'best_speedup': max(speedups) if speedups else None,
        'worst_speedup': min(speedups) if speedups else None,
        'average_speedup': sum(speedups) / len(speedups) if speedups else None
    }
    
    if not valid_metrics:
        gate_reason = "No tests with special-form primes found"
    elif overall_pass:
        gate_reason = f"All {len(valid_metrics)} speed tests passed"
    else:
        failed_count = len(valid_metrics) - sum(1 for m in valid_metrics if m.get('pass_gate', False))
        gate_reason = f"{failed_count}/{len(valid_metrics)} speed tests failed"
    
    return HypothesisResult(
        hypothesis="H4",
        description="Montgomery Multiplication Speed (≥10% speedup)",
        pass_gate=overall_pass,
        gate_reason=gate_reason,
        metrics=aggregated_metrics,
        test_files=metrics_files
    )

def assess_h6_zeta_consistency(metrics_files: List[str]) -> Optional[HypothesisResult]:
    """Assess H6: Zeta Consistency hypothesis (optional)"""
    if not metrics_files:
        return None  # Optional test
    
    # Implementation would depend on zeta consistency test format
    # For now, return a 'not implemented' status that does not affect pass/fail logic
    return HypothesisResult(
        hypothesis="H6",
        description="Zeta Consistency (optional)",
        pass_gate=None,
        gate_reason="Not implemented - test not evaluated",
        metrics={'note': 'Zeta consistency test not implemented'},
        test_files=metrics_files
    )

def generate_gate_report(metrics_dir: str, strict: bool = False) -> GateReport:
    """
    Generate comprehensive gate report from all metrics.
    
    Parameters:
    -----------
    metrics_dir : str
        Directory containing metrics JSON files
    strict : bool
        If True, requires all optional tests to pass
    """
    logger.info("Generating comprehensive gate report")
    
    # Find all metrics files
    metrics_files = find_metrics_files(metrics_dir)
    
    # Assess each hypothesis
    hypothesis_results = []
    
    # H1: Z5D Accuracy (required)
    h1_result = assess_h1_accuracy(metrics_files['H1_accuracy'])
    hypothesis_results.append(h1_result)
    
    # H2: Form Hit-Rate Uplift (required)
    h2_result = assess_h2_form_hitrate(metrics_files['H2_form_hitrate'])
    hypothesis_results.append(h2_result)
    
    # H3: Sqrt-Friendly Fraction QC (required)
    h3_result = assess_h3_sqrt_friendly(metrics_files['H3_sqrt_friendly'])
    hypothesis_results.append(h3_result)
    
    # H4: Montgomery Multiplication Speed (required if special-form primes found)
    h4_result = assess_h4_modmul_speed(metrics_files['H4_modmul_speed'])
    hypothesis_results.append(h4_result)
    
    # H5: Density Enhancement (same as H2)
    h5_result = HypothesisResult(
        hypothesis="H5",
        description="Density Enhancement (same as H2)",
        pass_gate=h2_result.pass_gate,
        gate_reason=f"Equivalent to H2: {h2_result.gate_reason}",
        metrics=h2_result.metrics,
        test_files=h2_result.test_files
    )
    hypothesis_results.append(h5_result)
    
    # H6: Zeta Consistency (optional)
    if strict or metrics_files['H6_zeta_consistency']:
        h6_result = assess_h6_zeta_consistency(metrics_files['H6_zeta_consistency'])
        if h6_result:
            hypothesis_results.append(h6_result)
    
    # Overall assessment
    required_results = [h1_result, h2_result, h3_result, h4_result, h5_result]
    passed_count = sum(1 for r in hypothesis_results if r.pass_gate)
    total_count = len(hypothesis_results)
    
    # For overall pass, all required hypotheses must pass
    overall_pass = all(r.pass_gate for r in required_results)
    
    # If strict mode, all hypotheses (including optional) must pass
    if strict:
        overall_pass = overall_pass and all(r.pass_gate for r in hypothesis_results)
    
    test_summary = {
        'required_hypotheses': 5,  # H1-H5
        'optional_hypotheses': len(hypothesis_results) - 5,
        'total_metrics_files': sum(len(files) for files in metrics_files.values()),
        'metrics_directory': metrics_dir,
        'strict_mode': strict
    }
    
    return GateReport(
        overall_pass=overall_pass,
        total_hypotheses=total_count,
        passed_hypotheses=passed_count,
        failed_hypotheses=total_count - passed_count,
        hypothesis_results=hypothesis_results,
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        test_summary=test_summary
    )

def format_markdown_report(report: GateReport) -> str:
    """Format gate report as Markdown"""
    md = []
    
    # Header
    md.append("# Z5D-Biased Generation of Crypto-Friendly Primes - Gate Report")
    md.append("")
    md.append(f"**Generated:** {report.generation_time}")
    md.append(f"**Test Mode:** {'Strict' if report.test_summary['strict_mode'] else 'Standard'}")
    md.append("")
    
    # Overall Result
    overall_badge = "🟢 **PASS**" if report.overall_pass else "🔴 **FAIL**"
    md.append(f"## Overall Result: {overall_badge}")
    md.append("")
    md.append(f"- **Hypotheses Tested:** {report.total_hypotheses}")
    md.append(f"- **Passed:** {report.passed_hypotheses}")
    md.append(f"- **Failed:** {report.failed_hypotheses}")
    md.append(f"- **Success Rate:** {report.passed_hypotheses/report.total_hypotheses*100:.1f}%")
    md.append("")
    
    # Summary Table
    md.append("## Hypothesis Summary")
    md.append("")
    md.append("| Hypothesis | Description | Result | Reason |")
    md.append("|------------|-------------|--------|--------|")
    
    for result in report.hypothesis_results:
        badge = "✅ PASS" if result.pass_gate else "❌ FAIL"
        reason_short = result.gate_reason[:50] + "..." if len(result.gate_reason) > 50 else result.gate_reason
        md.append(f"| **{result.hypothesis}** | {result.description} | {badge} | {reason_short} |")
    
    md.append("")
    
    # Detailed Results
    md.append("## Detailed Results")
    md.append("")
    
    for result in report.hypothesis_results:
        badge = "🟢 PASS" if result.pass_gate else "🔴 FAIL"
        md.append(f"### {result.hypothesis}: {result.description}")
        md.append("")
        md.append(f"**Result:** {badge}")
        md.append("")
        md.append(f"**Gate Reason:** {result.gate_reason}")
        md.append("")
        
        if result.metrics:
            md.append("**Key Metrics:**")
            
            # Format metrics based on hypothesis type
            if result.hypothesis == "H1":
                if result.metrics.get('median_relative_errors'):
                    best_med = result.metrics.get('best_median_error', 0)
                    worst_med = result.metrics.get('worst_median_error', 0)
                    md.append(f"- Median relative error range: {best_med:.6f} - {worst_med:.6f}")
                if result.metrics.get('p99_relative_errors'):
                    best_p99 = result.metrics.get('best_p99_error', 0)
                    worst_p99 = result.metrics.get('worst_p99_error', 0)
                    md.append(f"- 99th percentile error range: {best_p99:.6f} - {worst_p99:.6f}")
                    
            elif result.hypothesis in ["H2", "H5"]:
                if result.metrics.get('hit_rate_deltas'):
                    best_delta = result.metrics.get('best_delta', 0)
                    worst_delta = result.metrics.get('worst_delta', 0)
                    md.append(f"- Hit-rate delta range: {best_delta:.4f} - {worst_delta:.4f}")
                if result.metrics.get('hit_rate_ratios'):
                    best_ratio = result.metrics.get('best_ratio', 1)
                    worst_ratio = result.metrics.get('worst_ratio', 1)
                    md.append(f"- Hit-rate ratio range: {best_ratio:.3f}× - {worst_ratio:.3f}×")
                    
            elif result.hypothesis == "H3":
                if result.metrics.get('unbiased_deviations'):
                    closest = result.metrics.get('closest_to_half', 0)
                    furthest = result.metrics.get('furthest_from_half', 0)
                    md.append(f"- Deviation from 0.5 range: {closest:.4f} - {furthest:.4f}")
                    
            elif result.hypothesis == "H4":
                if result.metrics.get('speedup_percentages'):
                    best_speedup = result.metrics.get('best_speedup', 0)
                    worst_speedup = result.metrics.get('worst_speedup', 0)
                    avg_speedup = result.metrics.get('average_speedup', 0)
                    md.append(f"- Speedup percentage range: {worst_speedup:.1f}% - {best_speedup:.1f}%")
                    md.append(f"- Average speedup: {avg_speedup:.1f}%")
            
            md.append(f"- Tests passed: {result.metrics.get('passed_tests', 0)}/{result.metrics.get('total_tests', 0)}")
        
        if result.test_files:
            md.append("")
            md.append("**Test Files:**")
            for file_path in result.test_files:
                md.append(f"- `{os.path.basename(file_path)}`")
        
        md.append("")
    
    # Test Summary
    md.append("## Test Summary")
    md.append("")
    md.append(f"- **Required Hypotheses:** {report.test_summary['required_hypotheses']}")
    md.append(f"- **Optional Hypotheses:** {report.test_summary['optional_hypotheses']}")
    md.append(f"- **Total Metrics Files:** {report.test_summary['total_metrics_files']}")
    md.append(f"- **Metrics Directory:** `{report.test_summary['metrics_directory']}`")
    md.append("")
    
    # Gate Definitions
    md.append("## Gate Definitions")
    md.append("")
    md.append("- **H1 (Z5D Accuracy):** Median relative error ≤ 0.01% AND 99th-percentile ≤ 0.03%")
    md.append("- **H2 (Form Hit-Rate):** Lower CI(Δ) ≥ +20% OR ratio lower CI ≥ 1.2×")
    md.append("- **H3 (Sqrt-Friendly QC):** |Z5D_frac - 0.5| ≤ 1% AND |Z5D_frac - Baseline_frac| ≤ 1.5%")
    md.append("- **H4 (Montgomery Speed):** Median speedup ≥ 10% AND 95% CI lower bound ≥ 5%")
    md.append("- **H5 (Density Enhancement):** Same as H2")
    md.append("- **H6 (Zeta Consistency):** Pearson r ≥ 0.90, p < 1e-10 (optional)")
    md.append("")
    
    return "\n".join(md)

def save_gate_report(report: GateReport, output_file: str, output_json: str):
    """Save gate report to Markdown and JSON files"""
    
    # Save Markdown report
    markdown_content = format_markdown_report(report)
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(markdown_content)
    logger.info(f"Gate report saved to {output_file}")
    
    # Save JSON summary
    json_summary = {
        'overall_pass': report.overall_pass,
        'total_hypotheses': report.total_hypotheses,
        'passed_hypotheses': report.passed_hypotheses,
        'failed_hypotheses': report.failed_hypotheses,
        'generation_time': report.generation_time,
        'test_summary': report.test_summary,
        'hypothesis_results': [
            {
                'hypothesis': r.hypothesis,
                'description': r.description,
                'pass_gate': r.pass_gate,
                'gate_reason': r.gate_reason,
                'metrics': r.metrics,
                'test_files': r.test_files
            }
            for r in report.hypothesis_results
        ]
    }
    
    json_output_dir = os.path.dirname(output_json)
    if json_output_dir:
        os.makedirs(json_output_dir, exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(json_summary, f, indent=2)
    logger.info(f"Gate report JSON saved to {output_json}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate summary gate report for Z5D crypto-friendly primes test plan",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Standard mode (required hypotheses only)
    python -m scripts.summary_gate_report
    
    # Strict mode (all hypotheses must pass)
    python -m scripts.summary_gate_report --strict
    
    # Custom directories and output
    python -m scripts.summary_gate_report --metrics-dir metrics --output REPORT.md
        """
    )
    
    parser.add_argument(
        '--metrics-dir',
        type=str,
        default='metrics',
        help='Directory containing metrics JSON files (default: metrics)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='REPORT.md',
        help='Output Markdown file (default: REPORT.md)'
    )
    
    parser.add_argument(
        '--output-json',
        type=str,
        default='metrics/gate_report.json',
        help='Output JSON file (default: metrics/gate_report.json)'
    )
    
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Strict mode: all hypotheses (including optional) must pass'
    )
    
    args = parser.parse_args()
    
    try:
        # Generate gate report
        report = generate_gate_report(args.metrics_dir, args.strict)
        
        # Save report
        save_gate_report(report, args.output, args.output_json)
        
        # Print summary to console
        print("\n" + "="*80)
        print("Z5D CRYPTO-FRIENDLY PRIMES - FINAL GATE REPORT")
        print("="*80)
        print(f"Overall Result: {'✅ PASS' if report.overall_pass else '❌ FAIL'}")
        print(f"Hypotheses: {report.passed_hypotheses}/{report.total_hypotheses} passed")
        print(f"Report saved to: {args.output}")
        print("="*80)
        
        # Return appropriate exit code
        return 0 if report.overall_pass else 1
        
    except Exception as e:
        logger.error(f"Error generating gate report: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())