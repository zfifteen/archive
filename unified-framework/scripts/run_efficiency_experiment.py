"""
Complete Efficiency Through Symmetry Hypothesis Falsification Experiment Runner

This script executes the full experimental protocol to test the hypothesis that
100,000 zeta zeros provide 30-40% error reduction over baseline Z5D implementation.

The experiment runs controlled comparisons and generates a comprehensive report
with statistical analysis and hypothesis validation.
"""

import sys
import os
import time
import json
import logging
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'experiments'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from experiments.efficiency_through_symmetry import EfficiencyThroughSymmetryExperiment


def setup_logging():
    """Setup comprehensive logging for the experiment."""
    log_filename = f"efficiency_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def run_full_experiment(max_zeros=100000):
    """
    Run the complete Efficiency Through Symmetry experiment.
    
    Args:
        max_zeros: Maximum number of zeta zeros to test (default: 100000)
        
    Returns:
        Dictionary containing all experimental results
    """
    logger = setup_logging()
    
    print("🔬 EFFICIENCY THROUGH SYMMETRY HYPOTHESIS FALSIFICATION EXPERIMENT")
    print("=" * 80)
    print(f"Starting comprehensive experiment with {max_zeros:,} zeta zeros")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Initialize experiment with full parameters
    logger.info(f"Initializing experiment with max_zeros={max_zeros}")
    experiment = EfficiencyThroughSymmetryExperiment(
        max_zeros=max_zeros,
        precision_dps=50
    )
    
    # Record experiment start time
    start_time = time.time()
    
    try:
        # Run the comprehensive experiment
        logger.info("Starting comprehensive experiment execution")
        results = experiment.run_comprehensive_experiment()
        
        # Record completion time
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info(f"Experiment completed in {execution_time:.2f} seconds")
        
        # Add timing information to results
        results['experiment_metadata']['execution_time_seconds'] = execution_time
        results['experiment_metadata']['start_time'] = datetime.fromtimestamp(start_time).isoformat()
        results['experiment_metadata']['end_time'] = datetime.fromtimestamp(end_time).isoformat()
        
        # Generate comprehensive report
        logger.info("Generating comprehensive report")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"efficiency_through_symmetry_report_{timestamp}.md"
        results_filename = f"efficiency_through_symmetry_results_{timestamp}.json"
        
        report = experiment.generate_report(results, report_filename)
        
        # Save results to JSON
        logger.info(f"Saving results to {results_filename}")
        with open(results_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        print_experiment_summary(results, execution_time)
        
        print(f"\n📁 Results saved to: {results_filename}")
        print(f"📄 Report saved to: {report_filename}")
        
        return results
        
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def print_experiment_summary(results, execution_time):
    """Print a summary of experimental results."""
    print("\n" + "="*80)
    print("EXPERIMENT SUMMARY")
    print("="*80)
    
    # Basic info
    metadata = results.get('experiment_metadata', {})
    print(f"⏱️  Execution time: {execution_time:.2f} seconds")
    print(f"🔢 Max zeta zeros: {metadata.get('max_zeros_tested', 'Unknown'):,}")
    print(f"🎯 Test k values: {metadata.get('test_k_values', [])}")
    print()
    
    # Statistical summaries
    summaries = results.get('statistical_summaries', [])
    if summaries:
        print("📊 PERFORMANCE SUMMARY")
        print("-" * 60)
        print(f"{'Method':<20} {'Zeros':<8} {'Mean Error':<12} {'95% CI Range':<15}")
        print("-" * 60)
        
        for summary in summaries:
            method = summary['method']
            num_zeros = summary['num_zeros']
            mean_error = summary['mean_error'] * 100
            ci_lower = summary['bootstrap_ci_lower'] * 100
            ci_upper = summary['bootstrap_ci_upper'] * 100
            ci_range = f"[{ci_lower:.4f}, {ci_upper:.4f}]%"
            
            print(f"{method:<20} {num_zeros:<8} {mean_error:.6f}%   {ci_range:<15}")
        print()
    
    # Hypothesis test results
    hyp_analysis = results.get('hypothesis_analysis', {})
    print("🧪 HYPOTHESIS TEST RESULTS")
    print("-" * 40)
    
    # Error reduction claim
    error_claim = hyp_analysis.get('error_reduction_claim', {})
    if error_claim:
        observed = error_claim.get('observed_reduction_percent', 0)
        supported = error_claim.get('claim_supported', False)
        status = "✅ SUPPORTED" if supported else "❌ FALSIFIED"
        print(f"Error Reduction (30-40%):     {status}")
        print(f"  Observed: {observed:.2f}%")
    
    # Confidence interval claim  
    ci_claim = hyp_analysis.get('confidence_interval_claim', {})
    if ci_claim:
        observed_ci = ci_claim.get('observed_ci', [0, 0])
        supported = ci_claim.get('claim_supported', False)
        status = "✅ SUPPORTED" if supported else "❌ FALSIFIED"
        print(f"CI Claim [28.5%, 41.2%]:     {status}")
        print(f"  Observed: [{observed_ci[0]:.2f}%, {observed_ci[1]:.2f}%]")
    
    # Statistical significance
    sig_claim = hyp_analysis.get('statistical_significance', {})
    if sig_claim:
        p_value = sig_claim.get('p_value', 1.0)
        supported = sig_claim.get('claim_supported', False)
        status = "✅ SUPPORTED" if supported else "❌ FALSIFIED"
        print(f"Significance (p < 10^-10):   {status}")
        print(f"  Observed: p = {p_value:.2e}")
    
    print()
    
    # Overall conclusion
    total_claims = 3
    supported_claims = sum([
        error_claim.get('claim_supported', False),
        ci_claim.get('claim_supported', False), 
        sig_claim.get('claim_supported', False)
    ])
    
    print("🎯 OVERALL CONCLUSION")
    print("-" * 30)
    print(f"Claims supported: {supported_claims}/{total_claims}")
    
    if supported_claims == total_claims:
        print("✅ HYPOTHESIS SUPPORTED: All claims validated")
    elif supported_claims > 0:
        print("⚠️  HYPOTHESIS PARTIALLY SUPPORTED: Mixed evidence")
    else:
        print("❌ HYPOTHESIS FALSIFIED: Claims not supported by evidence")
    
    print("="*80)


def run_scaled_experiment():
    """
    Run a scaled version of the experiment suitable for demonstration.
    
    This version uses fewer zeta zeros and smaller test cases for faster execution
    while maintaining the same experimental methodology.
    """
    print("🔬 SCALED EFFICIENCY THROUGH SYMMETRY EXPERIMENT")
    print("=" * 60)
    print("Running scaled version for demonstration purposes")
    print()
    
    # Use smaller parameters for faster execution
    scaled_experiment = EfficiencyThroughSymmetryExperiment(
        max_zeros=1000,  # Reduced from 100,000
        precision_dps=30  # Reduced from 50
    )
    
    # Use smaller test set
    scaled_experiment.test_k_values = [1000, 10000, 100000]
    
    start_time = time.time()
    
    try:
        # Run scaled experiment
        results = scaled_experiment.run_comprehensive_experiment()
        
        execution_time = time.time() - start_time
        
        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"scaled_efficiency_experiment_{timestamp}.md"
        results_filename = f"scaled_efficiency_results_{timestamp}.json"
        
        report = scaled_experiment.generate_report(results, report_filename)
        
        # Save results
        with open(results_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print_experiment_summary(results, execution_time)
        
        print(f"\n📁 Scaled results saved to: {results_filename}")
        print(f"📄 Scaled report saved to: {report_filename}")
        
        return results
        
    except Exception as e:
        print(f"❌ Scaled experiment failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main execution function with user choice."""
    print("🔬 Efficiency Through Symmetry Hypothesis Falsification")
    print("Choose experiment mode:")
    print("1. Full Experiment (100K zeta zeros - may take significant time)")
    print("2. Scaled Experiment (1K zeta zeros - faster demonstration)")
    print("3. Demo Only (framework validation)")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting FULL experiment...")
            results = run_full_experiment(max_zeros=100000)
        elif choice == "2":
            print("\n🚀 Starting SCALED experiment...")
            results = run_scaled_experiment()
        elif choice == "3":
            print("\n🚀 Running DEMO validation...")
            results = run_demo_experiment()
        else:
            print("❌ Invalid choice. Exiting.")
            return
            
        if results:
            print("\n✅ Experiment completed successfully!")
        else:
            print("\n❌ Experiment failed.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Experiment interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()