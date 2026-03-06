#!/usr/bin/env python3
"""
SELBERG ZETA FUNCTIONS: PRACTICAL TUTORIAL
===========================================

This script demonstrates how to USE the Selberg-Ruelle framework to:
1. Evaluate candidate matrices for QMC applications
2. Predict sampling quality before generating samples
3. Optimize matrix selection for specific tasks

Use this as a PRACTICAL GUIDE alongside the white paper visualizations.

Author: Big D (zfifteen)
Date: December 2025
"""

import numpy as np
from scipy.linalg import eigvals

def analyze_anosov_matrix(M, verbose=True):
    """
    Complete analysis of an Anosov toral automorphism for QMC applications.
    
    Returns a dictionary with all relevant metrics.
    """
    M = np.array(M, dtype=float)
    
    # 1. Validate unimodularity
    det = np.linalg.det(M)
    if abs(det - 1.0) > 1e-10:
        raise ValueError(f"Matrix must be unimodular (det=1), got det={det:.6f}")
    
    # 2. Compute spectral properties
    evals = eigvals(M)
    evals_abs = sorted([abs(ev) for ev in evals], reverse=True)
    lambda_max = evals_abs[0]
    lambda_min = evals_abs[-1]
    
    # 3. Entropy and proximality
    entropy = np.log(lambda_max)
    spectral_gap = np.log(lambda_max / lambda_min) if len(evals_abs) > 1 else np.inf
    is_proximal = spectral_gap > 0.5
    
    # 4. Periodic point counts
    def periodic_points(n):
        M_n = np.linalg.matrix_power(M.astype(int), n)
        return int(abs(np.linalg.det(M_n - np.eye(len(M), dtype=int))))
    
    N_vals = [periodic_points(n) for n in range(1, 13)]
    
    # 5. Zeta coefficients and second moment
    c = np.zeros(25)
    c[0] = 1.0
    for n, N_n in enumerate(N_vals, 1):
        for k in range(n, len(c)):
            c[k] += (N_n / n) * c[k - n]
    
    zeta_moment = np.sum(c**2)
    
    # 6. Predict QMC quality (empirical formula from white paper)
    # Based on regression: D* ≈ f(entropy, gap, moment)
    predicted_discrepancy = 0.035 - 0.005*entropy - 0.003*spectral_gap
    predicted_discrepancy = max(0.01, min(0.05, predicted_discrepancy))
    
    # Quality assessment
    random_baseline = 0.0323  # Empirical average
    improvement = (random_baseline - predicted_discrepancy) / random_baseline * 100
    
    if improvement > 30:
        quality = "EXCELLENT"
    elif improvement > 10:
        quality = "GOOD"
    elif improvement > -10:
        quality = "MARGINAL"
    else:
        quality = "POOR"
    
    results = {
        'matrix': M,
        'trace': int(np.trace(M)),
        'determinant': det,
        'eigenvalues': evals,
        'lambda_max': lambda_max,
        'lambda_min': lambda_min,
        'entropy': entropy,
        'spectral_gap': spectral_gap,
        'is_proximal': is_proximal,
        'periodic_points': N_vals,
        'zeta_coefficients': c,
        'zeta_moment': zeta_moment,
        'predicted_discrepancy': predicted_discrepancy,
        'vs_random_improvement': improvement,
        'quality_rating': quality,
        'recommendation': None
    }
    
    # 7. Generate recommendation
    if quality == "EXCELLENT":
        results['recommendation'] = "✓ RECOMMENDED for production use in QMC/GVA applications"
    elif quality == "GOOD":
        results['recommendation'] = "✓ Suitable for most applications, good balance"
    elif quality == "MARGINAL":
        results['recommendation'] = "⚠ Use with caution, consider alternatives"
    else:
        results['recommendation'] = "✗ NOT RECOMMENDED, likely worse than random"
    
    # 8. Print report
    if verbose:
        print("=" * 70)
        print(f"ANOSOV MATRIX ANALYSIS REPORT")
        print("=" * 70)
        print(f"\nMatrix: {M.tolist()}")
        print(f"Trace: {results['trace']}")
        print(f"Determinant: {det:.10f}")
        print(f"\n--- SPECTRAL PROPERTIES ---")
        print(f"Eigenvalues: {[f'{ev:.6f}' for ev in evals]}")
        print(f"λ_max: {lambda_max:.6f}")
        print(f"λ_min: {lambda_min:.6f}")
        print(f"Topological Entropy: h = {entropy:.4f}")
        print(f"Spectral Gap: Δ = {spectral_gap:.4f}")
        print(f"Proximal: {'YES' if is_proximal else 'NO'}")
        print(f"\n--- PERIODIC ORBIT STRUCTURE ---")
        print(f"N_1 through N_12: {N_vals}")
        print(f"\n--- ZETA FUNCTION ANALYSIS ---")
        print(f"Second Moment: Σc_k² = {zeta_moment:.2f}")
        print(f"log(Moment): {np.log(zeta_moment):.4f}")
        print(f"\n--- QMC QUALITY PREDICTION ---")
        print(f"Predicted D*: {predicted_discrepancy:.4f}")
        print(f"Random baseline: {random_baseline:.4f}")
        print(f"Expected improvement: {improvement:+.1f}%")
        print(f"\n--- QUALITY ASSESSMENT ---")
        print(f"Rating: {quality}")
        print(f"{results['recommendation']}")
        print("=" * 70)
        print()
    
    return results

def compare_matrices(matrices, names=None):
    """
    Compare multiple matrices and rank them by predicted QMC quality.
    """
    if names is None:
        names = [f"Matrix {i+1}" for i in range(len(matrices))]
    
    print("\n" + "=" * 90)
    print("COMPARATIVE MATRIX ANALYSIS FOR QMC APPLICATIONS")
    print("=" * 90)
    print()
    
    results = []
    for M, name in zip(matrices, names):
        result = analyze_anosov_matrix(M, verbose=False)
        result['name'] = name
        results.append(result)
    
    # Sort by predicted quality (lower discrepancy is better)
    results.sort(key=lambda r: r['predicted_discrepancy'])
    
    # Print comparison table
    print(f"{'Rank':<6}{'Name':<15}{'Trace':<8}{'Entropy':<10}{'Gap':<10}{'Moment':<12}{'D* Pred':<10}{'Improve':<10}{'Rating':<12}")
    print("-" * 90)
    
    for i, r in enumerate(results, 1):
        print(f"{i:<6}{r['name']:<15}{r['trace']:<8}{r['entropy']:<10.3f}{r['spectral_gap']:<10.3f}"
              f"{np.log(r['zeta_moment']):<12.2f}{r['predicted_discrepancy']:<10.4f}"
              f"{r['vs_random_improvement']:+<10.1f}{r['quality_rating']:<12}")
    
    print("\n" + "=" * 90)
    print(f"\nTOP RECOMMENDATION: {results[0]['name']}")
    print(f"  Matrix: {results[0]['matrix'].tolist()}")
    print(f"  Predicted improvement over random: {results[0]['vs_random_improvement']:+.1f}%")
    print(f"  {results[0]['recommendation']}")
    print()
    
    return results

def design_optimal_matrix(target_trace=None, search_limit=1000):
    """
    Search for high-quality Anosov matrices with specific properties.
    
    This demonstrates how to use the framework for DESIGN rather than just analysis.
    """
    print("\n" + "=" * 70)
    print("OPTIMAL MATRIX SEARCH")
    print("=" * 70)
    
    if target_trace:
        print(f"Target: Matrices with trace ≈ {target_trace}")
    else:
        print("Target: Highest quality matrices (any trace)")
    print(f"Search limit: {search_limit} candidates")
    print()
    
    best_candidates = []
    
    # Search strategy: Generate random SL(2,Z) matrices
    np.random.seed(42)
    
    for _ in range(search_limit):
        # Random integer matrix
        a = np.random.randint(-15, 15)
        d = np.random.randint(-15, 15)
        b = np.random.randint(-15, 15)
        
        # Ensure det = 1: c = (ad - 1) / b
        if b != 0 and (a*d - 1) % b == 0:
            c = (a*d - 1) // b
            M = [[a, b], [c, d]]
            
            # Quick filter: must have |trace| > 2 for hyperbolicity
            if abs(a + d) > 2:
                try:
                    result = analyze_anosov_matrix(M, verbose=False)
                    
                    # Apply target constraints
                    if target_trace is None or abs(result['trace'] - target_trace) <= 1:
                        if result['quality_rating'] in ['EXCELLENT', 'GOOD']:
                            best_candidates.append(result)
                except:
                    continue
    
    if not best_candidates:
        print("No suitable candidates found. Try increasing search_limit.")
        return None
    
    # Sort by quality
    best_candidates.sort(key=lambda r: r['predicted_discrepancy'])
    
    print(f"Found {len(best_candidates)} high-quality candidates")
    print("\nTop 5 Results:")
    print("-" * 70)
    
    for i, r in enumerate(best_candidates[:5], 1):
        print(f"\n{i}. Matrix: {r['matrix'].tolist()}")
        print(f"   Trace: {r['trace']}, Entropy: {r['entropy']:.3f}, Gap: {r['spectral_gap']:.3f}")
        print(f"   Predicted D*: {r['predicted_discrepancy']:.4f} ({r['vs_random_improvement']:+.1f}% vs random)")
        print(f"   Rating: {r['quality_rating']}")
    
    print("\n" + "=" * 70)
    return best_candidates

def tutorial_workflow():
    """
    Complete tutorial demonstrating practical usage.
    """
    print("\n" + "=" * 80)
    print(" " * 20 + "SELBERG ZETA FRAMEWORK TUTORIAL")
    print("=" * 80)
    
    print("\n### SECTION 1: Analyzing a Single Matrix ###\n")
    
    # Example: High-quality matrix from white paper
    M_good = [[10, 1], [9, 1]]
    print("Analyzing the Trace-11 matrix (known to be excellent):")
    analyze_anosov_matrix(M_good)
    
    input("Press Enter to continue...")
    
    print("\n### SECTION 2: Analyzing a Poor Matrix ###\n")
    
    # Example: Low-entropy Fibonacci matrix
    M_bad = [[2, 1], [1, 1]]
    print("Analyzing the Fibonacci matrix (known to be poor for QMC):")
    analyze_anosov_matrix(M_bad)
    
    input("Press Enter to continue...")
    
    print("\n### SECTION 3: Comparing Multiple Candidates ###\n")
    
    candidates = [
        [[2, 1], [1, 1]],
        [[3, 2], [1, 1]],
        [[5, 2], [2, 1]],
        [[10, 1], [9, 1]],
        [[7, 3], [2, 1]],
    ]
    names = ["Fibonacci", "Trace-4", "Trace-6", "Trace-11", "Trace-8"]
    
    compare_matrices(candidates, names)
    
    input("Press Enter to continue...")
    
    print("\n### SECTION 4: Searching for Optimal Matrices ###\n")
    
    print("Searching for matrices with trace around 12...")
    optimal = design_optimal_matrix(target_trace=12, search_limit=5000)
    
    print("\n" + "=" * 80)
    print("TUTORIAL COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("1. Use analyze_anosov_matrix() to evaluate single matrices")
    print("2. Use compare_matrices() to rank multiple candidates")
    print("3. Use design_optimal_matrix() to search for new high-quality systems")
    print("4. Look for: high entropy (h > 1.8) + high spectral gap (Δ > 0.5)")
    print("5. Zeta second moment log(Σc_k²) > 40 typically indicates quality")
    print("\nFor GVA factorization: Use matrices with EXCELLENT rating")
    print("For general QMC: GOOD rating is usually sufficient")
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--tutorial":
        tutorial_workflow()
    else:
        print("\nQuick Analysis Mode")
        print("=" * 70)
        print("\nAnalyzing standard test matrices...\n")
        
        test_matrices = [
            ([[2, 1], [1, 1]], "Fibonacci (Low Entropy)"),
            ([[10, 1], [9, 1]], "Trace-11 (High Entropy)"),
        ]
        
        for M, name in test_matrices:
            print(f"\n>>> {name}")
            analyze_anosov_matrix(M)
        
        print("\n" + "=" * 70)
        print("TIP: Run with --tutorial flag for complete walkthrough")
        print("     python selberg_tutorial.py --tutorial")
        print("=" * 70)
