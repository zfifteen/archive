"""
Main experimental harness for testing asymmetric resonance bias hypothesis.

This script orchestrates the complete experiment:
1. Generates a 127-bit semiprime with known factors
2. Applies Z5D scoring to QMC-generated candidates
3. Analyzes enrichment asymmetry
4. Validates QMC uniformity
5. Documents findings
"""

from z5d_scoring import (
    z5d_score,
    generate_candidates_qmc,
    compute_enrichment,
    validate_qmc_uniformity,
    test_n127_semiprime
)
import json
import time


def is_prime(n: int) -> bool:
    """IMPLEMENTED: Miller-Rabin primality test (deterministic for n < 2^64).
    
    Args:
        n: Number to test
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witnesses for deterministic test up to 2^64
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    for a in witnesses:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_semiprime_127bit() -> tuple[int, int, int]:
    """IMPLEMENTED: Generate a 127-bit semiprime with known factors for testing.
    
    Returns:
        Tuple of (N, p, q) where N = p * q
    """
    # Use fixed large primes with proper offsets for reproducibility
    p = 8264141345021879351  # Prime with ~10% negative offset
    q = 10293283193129930891  # Prime with ~12% positive offset
    N = p * q
    
    # Verify they are prime
    assert is_prime(p), f"p={p} is not prime"
    assert is_prime(q), f"q={q} is not prime"
    assert N.bit_length() >= 126, f"N should be 126-127 bits, got {N.bit_length()}"
    
    return (N, p, q)


def write_findings(results: dict, filename: str = "FINDINGS.md") -> None:
    """IMPLEMENTED: Document experimental findings in markdown format.
    
    Args:
        results: Complete experimental results from test_n127_semiprime
        filename: Output filename
    """
    with open(filename, 'w') as f:
        # Lead with conclusion
        f.write("# FINDINGS: Asymmetric Resonance Bias in Semiprime Factorization\n\n")
        
        # Conclusion section
        f.write("## CONCLUSION\n\n")
        if results['hypothesis_supported']:
            f.write("**HYPOTHESIS SUPPORTED** ✓\n\n")
            f.write(f"The Z5D scoring mechanism demonstrates significant asymmetric enrichment bias ")
            f.write(f"with an asymmetry ratio of {results['enrichment_results']['asymmetry_ratio']:.2f}, ")
            f.write(f"strongly favoring candidates near the larger prime factor (q) over the smaller ")
            f.write(f"factor (p).\n\n")
        else:
            f.write("**HYPOTHESIS FALSIFIED** ✗\n\n")
            f.write(f"The Z5D scoring mechanism does NOT demonstrate the predicted asymmetric ")
            f.write(f"enrichment bias. Asymmetry ratio: {results['enrichment_results']['asymmetry_ratio']:.2f} ")
            f.write(f"(threshold: 5.0).\n\n")
        
        # Technical evidence
        f.write("## TECHNICAL EVIDENCE\n\n")
        
        f.write("### Test Subject: N₁₂₇\n\n")
        f.write(f"- **N** = {results['N']}\n")
        f.write(f"- **p** = {results['p']} ({results['p'].bit_length()} bits, smaller factor)\n")
        f.write(f"- **q** = {results['q']} ({results['q'].bit_length()} bits, larger factor)\n")
        f.write(f"- **N bit length** = {results['N'].bit_length()} bits\n")
        f.write(f"- **Verification**: p × q = {results['p'] * results['q']} {'✓' if results['p'] * results['q'] == results['N'] else '✗'}\n\n")
        
        f.write("### Experimental Parameters\n\n")
        f.write(f"- **Candidates requested**: {results['num_requested']:,}\n")
        f.write(f"- **Unique candidates generated**: {results['num_candidates']:,}\n")
        f.write(f"- **Generation method**: 106-bit QMC (Sobol sequences)\n")
        f.write(f"- **Generation time**: {results['generation_time']:.2f}s\n")
        f.write(f"- **Scoring time**: {results['scoring_time']:.2f}s\n\n")
        
        enrich = results['enrichment_results']
        f.write("### Enrichment Analysis\n\n")
        f.write(f"**Factor Offsets from √N:**\n")
        f.write(f"- p offset: {enrich['p_offset_percent']:.2f}% (below √N)\n")
        f.write(f"- q offset: +{enrich['q_offset_percent']:.2f}% (above √N)\n\n")
        
        f.write(f"**High-Scoring Candidate Distribution:**\n")
        f.write(f"- Score threshold (90th percentile): {enrich['score_threshold']:.6f}\n")
        f.write(f"- Total high-scoring candidates: {enrich['total_high_scoring']:,}\n")
        f.write(f"- Expected per window (uniform): {enrich['expected_in_window']:.1f}\n\n")
        
        f.write(f"**Near-p Region (±2% window around p):**\n")
        f.write(f"- Total candidates in window: {enrich['total_near_p']:,}\n")
        f.write(f"- High-scoring candidates: {enrich['near_p_count']}\n")
        f.write(f"- Enrichment ratio: {enrich['near_p_enrichment']:.2f}x\n\n")
        
        f.write(f"**Near-q Region (±2% window around q):**\n")
        f.write(f"- Total candidates in window: {enrich['total_near_q']:,}\n")
        f.write(f"- High-scoring candidates: {enrich['near_q_count']}\n")
        f.write(f"- Enrichment ratio: {enrich['near_q_enrichment']:.2f}x\n\n")
        
        f.write(f"**Asymmetry Metric:**\n")
        f.write(f"- Asymmetry ratio (q/p enrichment): **{enrich['asymmetry_ratio']:.2f}**\n")
        f.write(f"- Interpretation: The larger factor (q) shows ")
        f.write(f"{enrich['asymmetry_ratio']:.1f}x more enrichment than the smaller factor (p)\n\n")
        
        unif = results['uniformity_results']
        f.write("### QMC Uniformity Validation\n\n")
        f.write(f"**Statistical Tests:**\n")
        f.write(f"- Kolmogorov-Smirnov statistic: {unif['ks_statistic']:.6f}\n")
        f.write(f"- KS p-value: {unif['ks_pvalue']:.4f} ")
        f.write(f"({'PASS' if unif['ks_pvalue'] > 0.05 else 'FAIL'} at α=0.05)\n")
        f.write(f"- Chi-square statistic: {unif['chi_square']:.2f}\n")
        f.write(f"- Chi-square p-value: {unif['chi_pvalue']:.4f} ")
        f.write(f"({'PASS' if unif['chi_pvalue'] > 0.05 else 'FAIL'} at α=0.05)\n\n")
        
        f.write(f"**Quantization Analysis:**\n")
        f.write(f"- Raw candidates generated: {unif['num_raw_candidates']:,}\n")
        f.write(f"- Unique candidates: {unif['num_unique_candidates']:,}\n")
        f.write(f"- Duplicates detected: {unif['num_duplicates']:,}\n")
        f.write(f"- Maximum discrepancy: {unif['max_discrepancy']:.6f}\n\n")
        
        # Methodology
        f.write("## METHODOLOGY\n\n")
        f.write("### Z5D Scoring Mechanism\n\n")
        f.write("Candidates are evaluated across five dimensions:\n")
        f.write("1. **Distance from √N** (normalized, weight 0.25)\n")
        f.write("2. **Fermat residue strength** (proximity to perfect square, weight 0.30)\n")
        f.write("3. **Primality likelihood** (6k±1 pattern, weight 0.15)\n")
        f.write("4. **Gap distribution** (log-scale proximity, weight 0.20)\n")
        f.write("5. **Small prime smoothness** (divisibility penalty, weight 0.10)\n\n")
        
        f.write("### 106-bit QMC Construction\n\n")
        f.write("Candidates generated using Sobol sequences:\n")
        f.write("1. Generate 2D samples (hi, lo) from [0,1)²\n")
        f.write("2. Convert to 53-bit integers\n")
        f.write("3. Combine via bit-shifting: `(hi << 53) | lo`\n")
        f.write("4. Scale to ±√N offset range\n")
        f.write("5. Avoid float quantization at extreme scales\n\n")
        
        f.write("### Statistical Analysis\n\n")
        f.write("- **Enrichment ratio**: (observed high-scoring in window) / (expected under uniform)\n")
        f.write("- **Asymmetry ratio**: enrichment_q / enrichment_p\n")
        f.write("- **Success criterion**: Asymmetry ratio ≥ 5.0\n\n")
        
        # References
        f.write("## REFERENCES\n\n")
        f.write("- Prime Number Theorem: https://mathworld.wolfram.com/PrimeNumberTheorem.html\n")
        f.write("- Sobol Sequences: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.Sobol.html\n")
        f.write("- Experiment code: `/experiments/asymmetric_resonance_bias_test/`\n")


def run_full_experiment(num_candidates: int = 1000000) -> None:
    """IMPLEMENTED: Execute complete experimental workflow.
    
    Args:
        num_candidates: Number of candidates to test (default 1M)
    """
    import os
    
    # Change to experiment directory
    exp_dir = "/home/runner/work/playground/playground/experiments/asymmetric_resonance_bias_test"
    os.chdir(exp_dir)
    
    print("PARAMETERS:")
    print(f"  Candidates to generate: {num_candidates:,}")
    print(f"  Score threshold: 90th percentile")
    print(f"  Proximity window: ±2% of factor")
    print()
    
    # Run main test
    results = test_n127_semiprime(num_candidates=num_candidates)
    
    # Write findings
    print("Writing findings to FINDINGS.md...")
    write_findings(results, "FINDINGS.md")
    print("  ✓ FINDINGS.md created")
    print()
    
    # Save detailed JSON
    print("Saving detailed results to results.json...")
    with open("results.json", 'w') as f:
        # Convert to JSON-serializable format
        json_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                json_results[key] = value
            else:
                json_results[key] = str(value) if isinstance(value, int) and value > 2**53 else value
        json.dump(json_results, f, indent=2)
    print("  ✓ results.json created")
    print()
    
    # Print summary
    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    if results['hypothesis_supported']:
        print("RESULT: HYPOTHESIS SUPPORTED ✓")
        print(f"  Asymmetry ratio: {results['enrichment_results']['asymmetry_ratio']:.2f} (threshold: 5.0)")
    else:
        print("RESULT: HYPOTHESIS FALSIFIED ✗")
        print(f"  Asymmetry ratio: {results['enrichment_results']['asymmetry_ratio']:.2f} (threshold: 5.0)")
    print()
    print(f"Near-p enrichment: {results['enrichment_results']['near_p_enrichment']:.2f}x")
    print(f"Near-q enrichment: {results['enrichment_results']['near_q_enrichment']:.2f}x")
    print()
    print("See FINDINGS.md for full analysis.")


if __name__ == "__main__":
    # Entry point: run the experiment with default parameters
    print("=" * 80)
    print("Asymmetric Resonance Bias in Semiprime Factorization")
    print("Experimental Validation of Z5D Scoring Hypothesis")
    print("=" * 80)
    print()
    
    # Run with 1M candidates (adjust for testing)
    run_full_experiment(num_candidates=1000000)
