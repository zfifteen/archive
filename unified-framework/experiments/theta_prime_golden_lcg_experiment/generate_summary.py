"""
Generate text-based summary report from experiment results.
Alternative to plots when matplotlib is not available.
"""

import json
from pathlib import Path


def generate_text_report(results_file, output_file='results/experiment_summary.txt'):
    """Generate a text-based summary report."""
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    output = []
    output.append("=" * 70)
    output.append("θ′-BIASED ORDERING HYPOTHESIS TEST - RESULTS SUMMARY")
    output.append("=" * 70)
    output.append("")
    
    # RSA Results
    output.append("-" * 70)
    output.append("RSA QMC VARIANCE REDUCTION")
    output.append("-" * 70)
    
    rsa = results['rsa']
    output.append(f"Hypothesis: {rsa['hypothesis']}")
    output.append(f"Verdict: {rsa['verdict']}")
    output.append("")
    
    output.append("Detailed Results:")
    for r in rsa['detailed_results']:
        output.append(f"  {r['rsa_name']} (n={r['n']}):")
        output.append(f"    Baseline variance: {r['baseline']['variance']:.2f}")
        output.append(f"    θ′-biased variance: {r['theta_prime']['variance']:.2f}")
        output.append(f"    Reduction: {r['variance_reduction_pct']:.2f}%")
        output.append("")
    
    boot = rsa['bootstrap']
    output.append(f"Bootstrap Statistics (n={boot['n_bootstrap']}):")
    output.append(f"  Mean variance reduction: {boot['mean_reduction_pct']:.2f}%")
    output.append(f"  95% CI: [{boot['ci_95_lower']:.2f}%, {boot['ci_95_upper']:.2f}%]")
    output.append(f"  Elapsed time: {rsa['elapsed_time_sec']:.1f}s")
    output.append("")
    
    # CRISPR Results
    output.append("-" * 70)
    output.append("CRISPR SPECTRAL DISRUPTION SCORING")
    output.append("-" * 70)
    
    crispr = results['crispr']
    output.append(f"Hypothesis: {crispr['hypothesis']}")
    output.append(f"Verdict: {crispr['verdict']}")
    output.append("")
    
    detailed = crispr['detailed_result']
    output.append(f"Detailed Results (n={detailed['n_guides']} guides):")
    output.append(f"  Baseline entropy: {detailed['baseline_entropy']:.4f}")
    output.append(f"  θ′-biased entropy: {detailed['theta_entropy']:.4f}")
    output.append(f"  Entropy Δ: {detailed['entropy_delta_pct']:.2f}%")
    output.append(f"  Baseline resonance: {detailed['baseline_resonance']:.4f}")
    output.append(f"  θ′-biased resonance: {detailed['theta_resonance']:.4f}")
    output.append(f"  Resonance Δ: {detailed['resonance_delta_pct']:.2f}%")
    output.append("")
    
    boot = crispr['bootstrap']
    output.append(f"Bootstrap Statistics (n={boot['n_bootstrap']}):")
    output.append(f"  Mean entropy Δ: {boot['entropy_delta_mean']:.2f}%")
    output.append(f"  95% CI: [{boot['entropy_ci_95'][0]:.2f}%, {boot['entropy_ci_95'][1]:.2f}%]")
    output.append(f"  Mean resonance Δ: {boot['resonance_delta_mean']:.2f}%")
    output.append(f"  95% CI: [{boot['resonance_ci_95'][0]:.2f}%, {boot['resonance_ci_95'][1]:.2f}%]")
    output.append(f"  Elapsed time: {crispr['elapsed_time_sec']:.1f}s")
    output.append("")
    
    # Crypto Results
    output.append("-" * 70)
    output.append("CRYPTO REKEY DRIFT TOLERANCE")
    output.append("-" * 70)
    
    crypto = results['crypto']
    output.append(f"Hypothesis: {crypto['hypothesis']}")
    output.append(f"Verdict: {crypto['verdict']}")
    output.append("")
    
    output.append("Detailed Results:")
    for r in crypto['detailed_results']:
        output.append(f"  σ={r['sigma']}ms ({r['drift_type']}):")
        output.append(f"    Baseline fail rate: {r['baseline']['fail_rate_pct']:.2f}%")
        output.append(f"    θ′-biased fail rate: {r['theta_prime']['fail_rate_pct']:.2f}%")
        output.append(f"    Absolute Δ: {r['fail_rate_delta_pct']:.2f}%")
        output.append(f"    Relative improvement: {r['fail_rate_delta_rel_pct']:.2f}%")
        output.append(f"    Latency Δ: {r['latency_delta_ms']:.2f}ms")
        output.append("")
    
    output.append("Bootstrap Statistics:")
    for sigma_str, stats in crypto['bootstrap'].items():
        output.append(f"  σ={sigma_str}ms:")
        output.append(f"    Mean Δ: {stats['mean_delta_pct']:.2f}%")
        output.append(f"    95% CI: [{stats['ci_95'][0]:.2f}%, {stats['ci_95'][1]:.2f}%]")
    
    output.append(f"\n  Mean improvement across all σ: {crypto['mean_improvement_pct']:.2f}%")
    output.append(f"  Elapsed time: {crypto['elapsed_time_sec']:.1f}s")
    output.append("")
    
    # Cross-Validation
    output.append("-" * 70)
    output.append("CROSS-DOMAIN VALIDATION")
    output.append("-" * 70)
    
    cv = results['cross_validation']
    validation = cv['validation']
    
    output.append(f"Domains validated: {', '.join(validation['domains'])}")
    output.append(f"All features present: {validation['all_features_present']}")
    output.append("")
    
    output.append("Shared Feature Ranges:")
    output.append(f"  Z = A(B/c): [{validation['Z_range'][0]:.4f}, {validation['Z_range'][1]:.4f}]")
    output.append(f"  κ(n): [{validation['kappa_range'][0]:.4f}, {validation['kappa_range'][1]:.4f}]")
    output.append(f"  θ′(n,k): [{validation['theta_prime_range'][0]:.4f}, {validation['theta_prime_range'][1]:.4f}]")
    output.append(f"  Feature correlation: {validation['feature_correlation']:.4f}")
    output.append("")
    
    output.append("Feature Extraction by Domain:")
    for features in cv['features']:
        output.append(f"  {features['domain']}:")
        output.append(f"    Z = {features['Z']:.4f}")
        output.append(f"    κ = {features['kappa']:.4f}")
        output.append(f"    θ′ = {features['theta_prime']:.4f}")
        output.append(f"    n_param = {features['n_param']}")
    output.append("")
    
    # Summary
    output.append("=" * 70)
    output.append("OVERALL SUMMARY")
    output.append("=" * 70)
    
    summary = results['summary']
    output.append(f"Hypothesis: {summary['hypothesis']}")
    output.append("")
    
    output.append("Results by Domain:")
    for domain, data in summary['results'].items():
        output.append(f"  {domain} ({data['metric']}):")
        output.append(f"    Lift: {data['lift_pct']:.2f}%")
        if isinstance(data['ci_95'], list) and len(data['ci_95']) == 2:
            output.append(f"    95% CI: [{data['ci_95'][0]:.2f}%, {data['ci_95'][1]:.2f}%]")
        else:
            output.append(f"    95% CI: {data['ci_95']}")
        output.append(f"    Verdict: {data['verdict']}")
        output.append("")
    
    output.append(f"OVERALL VERDICT: {summary['overall_verdict']}")
    output.append("")
    output.append("=" * 70)
    
    # Write to file
    report_text = "\n".join(output)
    with open(output_file, 'w') as f:
        f.write(report_text)
    
    # Also print to console
    print(report_text)
    
    print(f"\n📄 Report saved to: {output_file}")
    return output_file


def main():
    import sys
    
    if len(sys.argv) < 2:
        results_file = 'results/experiment_results.json'
    else:
        results_file = sys.argv[1]
    
    if not Path(results_file).exists():
        print(f"Error: Results file not found: {results_file}")
        print("Run the experiment first: python run_experiment.py")
        return 1
    
    generate_text_report(results_file)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
