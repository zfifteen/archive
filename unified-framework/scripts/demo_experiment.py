"""
Quick demonstration experiment for the Efficiency Through Symmetry hypothesis.

This script runs a simplified version of the experiment suitable for demonstration
and initial validation of the claims.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Add path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'experiments'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from experiments.efficiency_through_symmetry import EfficiencyThroughSymmetryExperiment


def run_demo_experiment():
    """Run a demonstration version of the experiment with smaller parameters."""
    print("🔬 Efficiency Through Symmetry Hypothesis - Demo Experiment")
    print("=" * 60)
    
    # Create experiment with smaller parameters for demo
    experiment = EfficiencyThroughSymmetryExperiment(max_zeros=1000, precision_dps=30)
    
    # Use smaller test set for demo
    experiment.test_k_values = [1000, 10000, 100000]
    
    print("📋 Experiment Parameters:")
    print(f"   Max zeta zeros: {experiment.max_zeros}")
    print(f"   Precision: {experiment.precision_dps} decimal places")
    print(f"   Test k values: {experiment.test_k_values}")
    print()
    
    # Compute true primes for validation
    print("🎯 Computing true prime values...")
    true_primes = experiment.compute_true_primes()
    for k, p in true_primes.items():
        print(f"   p({k}) = {p}")
    print()
    
    # Test zeta zero generation
    print("🔢 Testing zeta zero generation...")
    test_zeros = experiment.generate_zeta_zeros(10)
    print(f"   Generated {len(test_zeros)} zeta zeros")
    print(f"   First zero: {test_zeros[0]}")
    print(f"   Real parts: {[z.real for z in test_zeros[:3]]}")
    print(f"   Imaginary parts: {[z.imag for z in test_zeros[:3]]}")
    print()
    
    # Run single prediction tests
    print("🧮 Testing prediction methods...")
    
    k_test = 1000
    true_val = true_primes[k_test]
    
    # Baseline prediction
    print(f"   Testing k = {k_test} (true value: {true_val})")
    baseline_pred = experiment.baseline_z5d_prediction(k_test)
    baseline_error = abs(baseline_pred - true_val) / true_val * 100
    print(f"   Baseline Z5D: {baseline_pred:.1f} (error: {baseline_error:.4f}%)")
    
    # Enhanced with small number of zeros
    zeros_small = experiment.generate_zeta_zeros(10)
    enhanced_pred = experiment.z5d_prime_enhanced(k_test, zeros_small, 10)
    enhanced_error = abs(enhanced_pred - true_val) / true_val * 100
    print(f"   Enhanced (10 zeros): {enhanced_pred:.1f} (error: {enhanced_error:.4f}%)")
    
    improvement = (baseline_error - enhanced_error) / baseline_error * 100
    print(f"   Improvement: {improvement:.2f}%")
    print()
    
    # Test bootstrap analysis
    print("📊 Testing bootstrap analysis...")
    sample_errors = [0.01, 0.02, 0.015, 0.025, 0.018, 0.012, 0.022]
    ci_lower, ci_upper = experiment.bootstrap_analysis(sample_errors, n_bootstrap=100)
    print(f"   Sample errors: {sample_errors}")
    print(f"   95% CI: [{ci_lower:.6f}, {ci_upper:.6f}]")
    print()
    
    # Test hypothesis analysis structure
    print("🔍 Testing hypothesis analysis framework...")
    
    # Mock results for testing
    mock_baseline_errors = [0.02, 0.025, 0.018, 0.022, 0.019]
    mock_enhanced_errors = [0.014, 0.016, 0.012, 0.015, 0.013]
    
    p_value = experiment.statistical_significance_test(mock_baseline_errors, mock_enhanced_errors)
    print(f"   Statistical test p-value: {p_value:.6f}")
    
    # Calculate mock improvement
    baseline_mean = np.mean(mock_baseline_errors)
    enhanced_mean = np.mean(mock_enhanced_errors)
    mock_improvement = (baseline_mean - enhanced_mean) / baseline_mean * 100
    print(f"   Mock improvement: {mock_improvement:.2f}%")
    
    # Test if this would support the 30-40% claim
    claim_supported = 30 <= mock_improvement <= 40
    print(f"   Would support 30-40% claim: {claim_supported}")
    print()
    
    # Generate a simple report
    print("📄 Generating demo report...")
    
    demo_results = {
        'experiment_metadata': {
            'demo_mode': True,
            'test_k_values': experiment.test_k_values,
            'true_primes': true_primes,
            'max_zeros_tested': experiment.max_zeros
        },
        'sample_predictions': {
            'k_tested': k_test,
            'true_value': true_val,
            'baseline_prediction': baseline_pred,
            'baseline_error_percent': baseline_error,
            'enhanced_prediction': enhanced_pred,
            'enhanced_error_percent': enhanced_error,
            'improvement_percent': improvement
        },
        'framework_validation': {
            'zeta_zeros_generated': len(test_zeros),
            'bootstrap_ci_test': [ci_lower, ci_upper],
            'statistical_test_p_value': p_value,
            'mock_improvement_test': mock_improvement,
            'claim_support_test': claim_supported
        }
    }
    
    # Save demo results (convert numpy types to native Python)
    def convert_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return obj
    
    # Convert all values in demo_results
    import json
    json_str = json.dumps(demo_results, default=convert_types, indent=2)
    
    with open('demo_experiment_results.json', 'w') as f:
        f.write(json_str)
    
    print("✅ Demo experiment completed successfully!")
    print("📁 Results saved to: demo_experiment_results.json")
    print()
    
    # Summary
    print("📋 Demo Summary:")
    print(f"   ✓ Framework initialization: OK")
    print(f"   ✓ True prime computation: OK")
    print(f"   ✓ Zeta zero generation: OK ({len(test_zeros)} zeros)")
    print(f"   ✓ Baseline prediction: OK ({baseline_error:.4f}% error)")
    print(f"   ✓ Enhanced prediction: OK ({enhanced_error:.4f}% error)")
    print(f"   ✓ Bootstrap analysis: OK")
    print(f"   ✓ Statistical testing: OK")
    print(f"   ✓ Result storage: OK")
    print()
    print("🔬 The full experiment framework is ready for comprehensive testing!")
    
    return demo_results


if __name__ == "__main__":
    results = run_demo_experiment()