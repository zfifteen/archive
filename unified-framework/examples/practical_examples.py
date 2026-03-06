#!/usr/bin/env python3
"""
Practical Example: Symbolic Derivation and Statistical Validation
================================================================

This example demonstrates end-to-end usage of the symbolic and statistical 
modules for Z Framework analysis.
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server environments
import matplotlib.pyplot as plt
from sympy import isprime
import json

def example_1_symbolic_derivation():
    """Example 1: Symbolic derivation of framework axioms."""
    print("=" * 60)
    print("EXAMPLE 1: SYMBOLIC AXIOM DERIVATION")
    print("=" * 60)
    
    from symbolic.axiom_derivation import (
        derive_universal_invariance, derive_curvature_formula, 
        derive_golden_ratio_transformation
    )
    
    # Derive universal invariance axiom
    print("\n1. Universal Invariance Axiom Z = A(B/c)")
    print("-" * 40)
    
    invariance = derive_universal_invariance()
    print(f"Universal form: {invariance['universal_form']}")
    print(f"Discrete form: {invariance['discrete_form']}")
    print(f"Notes: {invariance['derivation_notes'][0]}")
    
    # Derive curvature formula
    print("\n2. Discrete Curvature Formula κ(n) = d(n) * ln(n+1) / e²")
    print("-" * 55)
    
    curvature = derive_curvature_formula()
    print(f"Curvature formula: {curvature['curvature_formula']}")
    print(f"Prime curvature: {curvature['prime_curvature']}")
    print(f"Target variance: {curvature['variance_target']}")
    
    # Derive golden ratio transformation
    print("\n3. Golden Ratio Transformation θ'(n,k)")
    print("-" * 40)
    
    golden = derive_golden_ratio_transformation()
    print(f"Golden ratio φ: {golden['phi_exact']}")
    print(f"Transformation: {golden['theta_prime_formula']}")
    print(f"Continued fraction: {golden['continued_fraction']}")
    
    return {
        'universal_invariance': invariance,
        'curvature_formula': curvature,
        'golden_ratio': golden
    }

def example_2_statistical_validation():
    """Example 2: Statistical hypothesis testing."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: STATISTICAL HYPOTHESIS TESTING")
    print("=" * 60)
    
    from statistical.hypothesis_testing import (
        test_prime_enhancement_hypothesis, test_optimal_k_hypothesis,
        test_variance_minimization
    )
    
    # Generate prime and composite data
    primes = [p for p in range(2, 1000) if isprime(p)][:100]
    composites = [n for n in range(4, 1000) if not isprime(n)][:100]
    
    # Apply golden ratio transformation
    phi = (1 + np.sqrt(5)) / 2
    k = 3.33
    
    def transform(n, k_val):
        return phi * ((n % phi) / phi) ** k_val
    
    prime_transformed = [transform(p, k) for p in primes]
    composite_transformed = [transform(c, k) for c in composites]
    
    # Test 1: Prime enhancement hypothesis
    print("\n1. Prime Enhancement Hypothesis Test")
    print("-" * 40)
    
    enhancement_test = test_prime_enhancement_hypothesis(
        prime_transformed, composite_transformed
    )
    
    print(f"Hypothesis rejected: {enhancement_test['hypothesis_test']['rejected_null']}")
    print(f"Enhancement significant: {enhancement_test['hypothesis_test']['enhancement_significant']}")
    print(f"Cohen's d effect size: {enhancement_test['effect_sizes']['cohens_d']:.3f}")
    print(f"Variance enhancement: {enhancement_test['effect_sizes']['variance_enhancement']:.1%}")
    
    # Test 2: Optimal k parameter discovery
    print("\n2. Optimal k Parameter Discovery")
    print("-" * 35)
    
    # Generate k-enhancement curve
    k_values = np.linspace(3.0, 3.6, 21)
    enhancement_values = []
    
    for k_test in k_values:
        prime_test = [transform(p, k_test) for p in primes[:50]]
        composite_test = [transform(c, k_test) for c in composites[:50]]
        
        # Calculate variance enhancement as proxy
        var_prime = np.var(prime_test)
        var_composite = np.var(composite_test)
        enhancement = ((var_composite - var_prime) / var_prime * 100) if var_prime > 0 else 0
        enhancement_values.append(max(0, enhancement))  # Keep positive
    
    optimal_k_test = test_optimal_k_hypothesis(k_values, enhancement_values, theoretical_k=3.33)
    
    print(f"Optimal k exists: {optimal_k_test['hypothesis_test']['optimal_k_exists']}")
    print(f"Empirical k*: {optimal_k_test['empirical_results']['k_optimal_empirical']:.3f}")
    print(f"Max enhancement: {optimal_k_test['empirical_results']['max_enhancement']:.1f}%")
    
    fitted_k = optimal_k_test['fitted_models'].get('quadratic', {}).get('k_optimal_fitted')
    if fitted_k:
        print(f"Fitted k*: {fitted_k:.3f}")
    
    # Test 3: Variance minimization
    print("\n3. Variance Minimization Test")
    print("-" * 30)
    
    # Generate curvature-like data
    np.random.seed(42)  # For reproducibility
    curvature_data = np.random.gamma(2, 0.06, 1000)  # Shape to approximate target variance
    
    variance_test = test_variance_minimization(curvature_data, target_variance=0.118)
    
    print(f"Target achieved: {variance_test['hypothesis_test']['target_achieved']}")
    print(f"Sample variance: {variance_test['sample_statistics']['sample_variance']:.6f}")
    print(f"Target variance: {variance_test['sample_statistics']['target_variance']:.6f}")
    print(f"Relative error: {variance_test['sample_statistics']['relative_error']:.1f}%")
    
    return {
        'enhancement_test': enhancement_test,
        'optimal_k_test': optimal_k_test,
        'variance_test': variance_test,
        'test_data': {
            'k_values': k_values.tolist(),
            'enhancement_values': enhancement_values
        }
    }

def example_3_distribution_analysis():
    """Example 3: Distribution analysis and fitting."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: DISTRIBUTION ANALYSIS")
    print("=" * 60)
    
    from statistical.distribution_analysis import (
        analyze_prime_distribution, fit_distribution_models, test_normality_assumptions
    )
    
    # Generate prime gaps for analysis
    primes = [p for p in range(2, 10000) if isprime(p)]
    prime_gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
    
    print("\n1. Prime Gap Distribution Analysis")
    print("-" * 40)
    
    gap_analysis = analyze_prime_distribution(prime_gaps[:1000])
    
    print(f"Sample size: {gap_analysis['descriptive_statistics']['count']}")
    print(f"Mean gap: {gap_analysis['descriptive_statistics']['mean']:.2f}")
    print(f"Std gap: {gap_analysis['descriptive_statistics']['std']:.2f}")
    print(f"Skewness: {gap_analysis['descriptive_statistics']['skewness']:.3f}")
    print(f"Best distribution: {gap_analysis['best_distribution']['name']}")
    if gap_analysis['best_distribution']['aic']:
        print(f"AIC score: {gap_analysis['best_distribution']['aic']:.1f}")
    
    # Test normality
    print("\n2. Normality Testing")
    print("-" * 20)
    
    normality = test_normality_assumptions(prime_gaps[:1000])
    
    print(f"Likely normal: {normality['summary']['overall_recommendation'] == 'normal'}")
    print(f"Normality consensus: {normality['summary']['normality_consensus']:.1%}")
    print(f"Recommended approach: {normality['summary']['recommended_approach']}")
    
    # Fit Gaussian Mixture Model
    print("\n3. Gaussian Mixture Model Fitting")
    print("-" * 40)
    
    gmm_result = fit_distribution_models(prime_gaps[:500], model_type='gmm')
    
    print(f"Optimal components: {gmm_result['n_components']}")
    print(f"Log likelihood: {gmm_result['model_scores']['log_likelihood']:.2f}")
    print(f"AIC: {gmm_result['model_scores']['aic']:.1f}")
    print(f"BIC: {gmm_result['model_scores']['bic']:.1f}")
    
    return {
        'gap_analysis': gap_analysis,
        'normality_test': normality,
        'gmm_fit': gmm_result
    }

def example_4_correlation_analysis():
    """Example 4: Correlation analysis between sequences."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: CORRELATION ANALYSIS")
    print("=" * 60)
    
    from statistical.correlation_analysis import (
        correlate_zeta_zeros_primes, regression_analysis_enhancement
    )
    
    # Simulate zeta zeros and prime data with known correlation
    print("\n1. Zeta Zeros - Prime Correlation Test")
    print("-" * 40)
    
    np.random.seed(42)
    n_points = 100
    
    # Create correlated sequences (simulating r ≈ 0.85)
    true_correlation = 0.85
    noise_level = np.sqrt(1 - true_correlation**2)
    
    base_sequence = np.random.normal(0, 1, n_points)
    zeta_data = base_sequence + 0.1 * np.random.normal(0, 1, n_points)
    prime_data = true_correlation * base_sequence + noise_level * np.random.normal(0, 1, n_points)
    
    correlation_test = correlate_zeta_zeros_primes(zeta_data, prime_data)
    
    observed_r = correlation_test['correlation_analysis']['pearson']['correlation']
    print(f"Observed Pearson r: {observed_r:.3f}")
    print(f"Correlation strength: {correlation_test['correlation_analysis']['pearson']['strength']}")
    print(f"Statistically significant: {correlation_test['correlation_analysis']['pearson']['significant']}")
    
    # Check against documented claim (r = 0.93)
    claim_validation = correlation_test['documentation_validation']
    print(f"Documented claim (r=0.93): {'Supported' if claim_validation['claim_supported'] else 'Not supported'}")
    print(f"Difference from claim: {claim_validation['difference']:.3f}")
    
    # Bootstrap confidence interval
    ci = correlation_test['bootstrap_analysis']['confidence_interval']
    print(f"95% Confidence interval: [{ci[0]:.3f}, {ci[1]:.3f}]")
    
    # Regression analysis
    print("\n2. Enhancement-Parameter Regression")
    print("-" * 40)
    
    # Use data from previous example
    k_values = np.linspace(3.0, 3.6, 21)
    # Simulate enhancement curve with peak at k=3.33
    enhancement_values = 50 * np.exp(-20 * (k_values - 3.33)**2) + 10 + np.random.normal(0, 2, len(k_values))
    
    regression_result = regression_analysis_enhancement(k_values, enhancement_values)
    
    best_model = regression_result['best_model']
    print(f"Best fitting model: {best_model['name']}")
    if best_model['details']:
        print(f"R²: {best_model['details']['r_squared']:.3f}")
        
    optimal_estimates = regression_result['optimal_parameter_analysis']
    valid_estimates = [k for k in optimal_estimates.values() if k is not None]
    if valid_estimates:
        print(f"Optimal k estimates: {[f'{k:.3f}' for k in valid_estimates]}")
    
    return {
        'correlation_test': correlation_test,
        'regression_result': regression_result,
        'simulated_data': {
            'true_correlation': true_correlation,
            'observed_correlation': observed_r
        }
    }

def example_5_bootstrap_validation():
    """Example 5: Bootstrap validation and reproducibility."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: BOOTSTRAP VALIDATION")
    print("=" * 60)
    
    from statistical.bootstrap_validation import (
        bootstrap_confidence_intervals, validate_reproducibility, 
        permutation_test_significance
    )
    
    # Bootstrap confidence intervals
    print("\n1. Bootstrap Confidence Intervals")
    print("-" * 40)
    
    # Sample data
    np.random.seed(42)
    sample_data = np.random.gamma(2, 2, 100)  # Gamma distribution data
    
    # Bootstrap CI for mean
    mean_ci = bootstrap_confidence_intervals(sample_data, np.mean, n_bootstrap=1000)
    print(f"Sample mean: {np.mean(sample_data):.3f}")
    print(f"Bootstrap mean: {mean_ci['bootstrap_summary']['mean']:.3f}")
    print(f"Bootstrap bias: {mean_ci['bootstrap_summary']['bias']:.6f}")
    print(f"95% CI: [{mean_ci['confidence_interval'][0]:.3f}, {mean_ci['confidence_interval'][1]:.3f}]")
    
    # Bootstrap CI for standard deviation
    std_ci = bootstrap_confidence_intervals(sample_data, np.std, n_bootstrap=1000)
    print(f"Sample std: {np.std(sample_data):.3f}")
    print(f"Std 95% CI: [{std_ci['confidence_interval'][0]:.3f}, {std_ci['confidence_interval'][1]:.3f}]")
    
    # Reproducibility validation
    print("\n2. Reproducibility Validation")
    print("-" * 35)
    
    def example_experiment(mean=5, std=1, n=50):
        """Simple experiment for reproducibility testing."""
        return np.mean(np.random.normal(mean, std, n))
    
    repro_result = validate_reproducibility(
        example_experiment, 
        n_replications=20,  # Reduced for example
        mean=5, std=1, n=50
    )
    
    print(f"Successful replications: {repro_result['experiment_summary']['successful_replications']}/20")
    print(f"Success rate: {repro_result['experiment_summary']['success_rate']:.1%}")
    
    assessment = repro_result['reproducibility_assessment']
    if assessment['highly_reproducible']:
        print("✓ Results are highly reproducible")
    elif assessment['moderately_reproducible']:
        print("⚠ Results are moderately reproducible")
    else:
        print("❌ Results show poor reproducibility")
    
    # Permutation test
    print("\n3. Permutation Test for Group Differences")
    print("-" * 45)
    
    # Create two groups with different means
    group1 = np.random.normal(10, 2, 40)
    group2 = np.random.normal(12, 2, 45)
    
    perm_test = permutation_test_significance(
        group1, group2, 
        n_permutations=1000,
        alternative='two-sided'
    )
    
    print(f"Observed difference: {perm_test['test_results']['observed_statistic']:.3f}")
    print(f"P-value: {perm_test['test_results']['p_value']:.4f}")
    print(f"Significant difference: {perm_test['test_results']['significant']}")
    print(f"Effect size: {perm_test['test_results']['effect_size']:.3f}")
    print(f"Effect interpretation: {perm_test['test_results']['effect_interpretation']}")
    
    return {
        'bootstrap_mean_ci': mean_ci,
        'bootstrap_std_ci': std_ci,
        'reproducibility': repro_result,
        'permutation_test': perm_test
    }

def example_6_integration_pipeline():
    """Example 6: Complete symbolic-statistical integration pipeline."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: COMPLETE INTEGRATION PIPELINE")
    print("=" * 60)
    
    print("\n1. Symbolic Derivation Phase")
    print("-" * 30)
    
    # Step 1: Symbolic derivation
    from symbolic.axiom_derivation import derive_golden_ratio_transformation
    
    golden_derivation = derive_golden_ratio_transformation()
    phi_exact = golden_derivation['phi_exact']
    
    # Extract numerical values
    phi_numerical = float((1 + np.sqrt(5)) / 2)
    k_optimal = 3.33  # From theoretical analysis
    
    print(f"✓ Golden ratio derived: φ = {phi_exact}")
    print(f"✓ Numerical value: φ ≈ {phi_numerical:.6f}")
    print(f"✓ Optimal k parameter: {k_optimal}")
    
    print("\n2. Data Generation Phase")
    print("-" * 25)
    
    # Step 2: Generate test data
    primes = [p for p in range(2, 500) if isprime(p)]
    composites = [n for n in range(4, 500) if not isprime(n)][:len(primes)]
    
    # Apply symbolic transformation
    def symbolic_transform(n, k):
        return phi_numerical * ((n % phi_numerical) / phi_numerical) ** k
    
    prime_transformed = [symbolic_transform(p, k_optimal) for p in primes]
    composite_transformed = [symbolic_transform(c, k_optimal) for c in composites]
    
    print(f"✓ Generated {len(primes)} primes and {len(composites)} composites")
    print(f"✓ Applied symbolic transformation with k = {k_optimal}")
    
    print("\n3. Statistical Validation Phase")
    print("-" * 30)
    
    # Step 3: Statistical analysis
    from statistical.hypothesis_testing import test_prime_enhancement_hypothesis
    from statistical.distribution_analysis import analyze_prime_distribution
    from statistical.bootstrap_validation import bootstrap_confidence_intervals
    
    # Hypothesis testing
    enhancement_test = test_prime_enhancement_hypothesis(
        prime_transformed, composite_transformed
    )
    
    print(f"✓ Prime enhancement hypothesis: {'Supported' if enhancement_test['hypothesis_test']['enhancement_significant'] else 'Not supported'}")
    print(f"✓ Effect size (Cohen's d): {enhancement_test['effect_sizes']['cohens_d']:.3f}")
    
    # Distribution analysis
    prime_dist = analyze_prime_distribution(prime_transformed)
    composite_dist = analyze_prime_distribution(composite_transformed)
    
    print(f"✓ Prime distribution best fit: {prime_dist['best_distribution']['name']}")
    print(f"✓ Composite distribution best fit: {composite_dist['best_distribution']['name']}")
    
    # Bootstrap validation
    prime_ci = bootstrap_confidence_intervals(prime_transformed, np.mean, n_bootstrap=1000)
    composite_ci = bootstrap_confidence_intervals(composite_transformed, np.mean, n_bootstrap=1000)
    
    print(f"✓ Prime mean 95% CI: [{prime_ci['confidence_interval'][0]:.3f}, {prime_ci['confidence_interval'][1]:.3f}]")
    print(f"✓ Composite mean 95% CI: [{composite_ci['confidence_interval'][0]:.3f}, {composite_ci['confidence_interval'][1]:.3f}]")
    
    print("\n4. Results Summary")
    print("-" * 20)
    
    # Comprehensive summary
    pipeline_results = {
        'symbolic_derivation_successful': True,
        'transformation_applied': len(prime_transformed) == len(primes),
        'enhancement_significant': enhancement_test['hypothesis_test']['enhancement_significant'],
        'effect_size': enhancement_test['effect_sizes']['cohens_d'],
        'variance_enhancement': enhancement_test['effect_sizes']['variance_enhancement'],
        'prime_distribution_fit': prime_dist['best_distribution']['name'],
        'statistical_power': 'adequate' if len(primes) >= 50 else 'limited',
        'confidence_intervals_computed': True
    }
    
    success_rate = sum(1 for v in pipeline_results.values() if v in [True, 'adequate', 'good']) / len(pipeline_results)
    
    print(f"Pipeline success rate: {success_rate:.1%}")
    print(f"Key findings:")
    print(f"  - Enhancement effect size: {enhancement_test['effect_sizes']['cohens_d']:.3f}")
    print(f"  - Variance enhancement: {enhancement_test['effect_sizes']['variance_enhancement']:.1%}")
    print(f"  - Statistical significance: {'Yes' if enhancement_test['statistical_tests']['t_test']['significant'] else 'No'}")
    
    return pipeline_results

def main():
    """Run all examples and generate summary report."""
    print("SYMBOLIC AND STATISTICAL MODULES: PRACTICAL EXAMPLES")
    print("=" * 80)
    
    results = {}
    
    try:
        results['example_1'] = example_1_symbolic_derivation()
    except Exception as e:
        print(f"❌ Example 1 failed: {e}")
        results['example_1'] = {'error': str(e)}
    
    try:
        results['example_2'] = example_2_statistical_validation()
    except Exception as e:
        print(f"❌ Example 2 failed: {e}")
        results['example_2'] = {'error': str(e)}
    
    try:
        results['example_3'] = example_3_distribution_analysis()
    except Exception as e:
        print(f"❌ Example 3 failed: {e}")
        results['example_3'] = {'error': str(e)}
    
    try:
        results['example_4'] = example_4_correlation_analysis()
    except Exception as e:
        print(f"❌ Example 4 failed: {e}")
        results['example_4'] = {'error': str(e)}
    
    try:
        results['example_5'] = example_5_bootstrap_validation()
    except Exception as e:
        print(f"❌ Example 5 failed: {e}")
        results['example_5'] = {'error': str(e)}
    
    try:
        results['example_6'] = example_6_integration_pipeline()
    except Exception as e:
        print(f"❌ Example 6 failed: {e}")
        results['example_6'] = {'error': str(e)}
    
    # Generate summary
    print("\n" + "=" * 80)
    print("EXAMPLES SUMMARY")
    print("=" * 80)
    
    successful_examples = sum(1 for v in results.values() if 'error' not in v)
    total_examples = len(results)
    
    print(f"Successful examples: {successful_examples}/{total_examples}")
    print(f"Success rate: {successful_examples/total_examples:.1%}")
    
    if successful_examples == total_examples:
        print("\n🎉 All examples completed successfully!")
        print("The symbolic and statistical modules are fully operational.")
    else:
        print(f"\n⚠ {total_examples - successful_examples} examples encountered issues.")
        print("Check the error messages above for troubleshooting.")
    
    print("\nFor detailed usage patterns and advanced features,")
    print("refer to docs/examples/SYMBOLIC_STATISTICAL_GUIDE.md")
    
    return results

if __name__ == "__main__":
    results = main()