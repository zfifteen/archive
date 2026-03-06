"""
Main Experiment Runner
Executes the complete θ′-biased ordering hypothesis test across all domains.
Generates results and plots as specified in the hypothesis.
"""

import json
import time
import sys
from pathlib import Path

# Import test modules
from rsa_qmc_test import RSAQMCTest, bootstrap_variance_reduction
from crispr_spectral_test import CRISPRSpectralTest, bootstrap_crispr_accuracy
from crypto_rekey_test import CryptoRekeyTest, bootstrap_crypto_tolerance
from cross_validation import CrossValidation


class ExperimentRunner:
    """Main experiment coordinator."""
    
    def __init__(self, output_dir='results', seed=42):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.seed = seed
        self.results = {}
    
    def run_rsa_experiment(self, n_bootstrap=1000):
        """Run RSA QMC variance reduction experiment."""
        print("=" * 60)
        print("RUNNING RSA QMC VARIANCE REDUCTION EXPERIMENT")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test cases
        test_cases = ['RSA-10', 'RSA-15', 'RSA-20', 'RSA-25']
        
        # Detailed results for each test case
        detailed_results = []
        for rsa_name in test_cases:
            print(f"\nTesting {rsa_name}...")
            tester = RSAQMCTest(seed=self.seed)
            result = tester.run_variance_comparison(rsa_name, n_samples=500)
            detailed_results.append(result)
            
            print(f"  Baseline variance: {result['baseline']['variance']:.2f}")
            print(f"  θ′-biased variance: {result['theta_prime']['variance']:.2f}")
            print(f"  Reduction: {result['variance_reduction_pct']:.2f}%")
        
        # Bootstrap confidence intervals
        print(f"\nRunning bootstrap (n={n_bootstrap})...")
        boot_result = bootstrap_variance_reduction(test_cases, n_bootstrap=n_bootstrap)
        
        elapsed = time.time() - start_time
        
        results = {
            'domain': 'RSA',
            'detailed_results': detailed_results,
            'bootstrap': boot_result,
            'elapsed_time_sec': elapsed,
            'hypothesis': 'θ′-biased ordering yields >0% lift in variance reduction',
            'verdict': 'SUPPORTED' if boot_result['mean_reduction_pct'] > 0 else 'REJECTED',
        }
        
        print(f"\n📊 RSA Results:")
        print(f"  Mean variance reduction: {boot_result['mean_reduction_pct']:.2f}%")
        print(f"  95% CI: [{boot_result['ci_95_lower']:.2f}%, {boot_result['ci_95_upper']:.2f}%]")
        print(f"  Verdict: {results['verdict']}")
        print(f"  Time: {elapsed:.1f}s")
        
        self.results['rsa'] = results
        return results
    
    def run_crispr_experiment(self, n_guides=100, n_bootstrap=1000):
        """Run CRISPR spectral disruption experiment."""
        print("\n" + "=" * 60)
        print("RUNNING CRISPR SPECTRAL DISRUPTION EXPERIMENT")
        print("=" * 60)
        
        start_time = time.time()
        
        # Detailed test
        print(f"\nTesting with {n_guides} guides...")
        tester = CRISPRSpectralTest(seed=self.seed)
        detailed = tester.compare_scoring_accuracy(n_guides=n_guides)
        
        print(f"  Entropy Δ: {detailed['entropy_delta_pct']:.2f}%")
        print(f"  Resonance Δ: {detailed['resonance_delta_pct']:.2f}%")
        
        # Bootstrap
        print(f"\nRunning bootstrap (n={n_bootstrap})...")
        boot_result = bootstrap_crispr_accuracy(n_guides=n_guides, n_bootstrap=n_bootstrap)
        
        elapsed = time.time() - start_time
        
        results = {
            'domain': 'CRISPR',
            'detailed_result': detailed,
            'bootstrap': boot_result,
            'elapsed_time_sec': elapsed,
            'hypothesis': 'θ′-biased ordering yields >0% lift in spectral disruption accuracy',
            'verdict': 'SUPPORTED' if boot_result['entropy_delta_mean'] > 0 else 'REJECTED',
        }
        
        print(f"\n📊 CRISPR Results:")
        print(f"  Mean entropy Δ: {boot_result['entropy_delta_mean']:.2f}%")
        print(f"  95% CI: [{boot_result['entropy_ci_95'][0]:.2f}%, {boot_result['entropy_ci_95'][1]:.2f}%]")
        print(f"  Mean resonance Δ: {boot_result['resonance_delta_mean']:.2f}%")
        print(f"  95% CI: [{boot_result['resonance_ci_95'][0]:.2f}%, {boot_result['resonance_ci_95'][1]:.2f}%]")
        print(f"  Verdict: {results['verdict']}")
        print(f"  Time: {elapsed:.1f}s")
        
        self.results['crispr'] = results
        return results
    
    def run_crypto_experiment(self, sigma_values=[1, 10, 50, 100], n_bootstrap=1000):
        """Run crypto rekey drift tolerance experiment."""
        print("\n" + "=" * 60)
        print("RUNNING CRYPTO REKEY DRIFT TOLERANCE EXPERIMENT")
        print("=" * 60)
        
        start_time = time.time()
        
        # Detailed results for each sigma
        detailed_results = []
        for sigma in sigma_values:
            print(f"\nTesting σ={sigma}ms...")
            tester = CryptoRekeyTest(seed=self.seed)
            result = tester.compare_rekey_tolerance(sigma, n_rekeys=1000, 
                                                   drift_type='gaussian')
            detailed_results.append(result)
            
            print(f"  Baseline fail rate: {result['baseline']['fail_rate_pct']:.2f}%")
            print(f"  θ′-biased fail rate: {result['theta_prime']['fail_rate_pct']:.2f}%")
            print(f"  Relative improvement: {result['fail_rate_delta_rel_pct']:.2f}%")
        
        # Bootstrap
        print(f"\nRunning bootstrap (n={n_bootstrap})...")
        boot_result = bootstrap_crypto_tolerance(sigma_values, n_bootstrap=n_bootstrap)
        
        elapsed = time.time() - start_time
        
        # Compute mean improvement across all sigma values
        mean_improvement = sum(boot_result[s]['mean_delta_pct'] for s in sigma_values) / len(sigma_values)
        
        results = {
            'domain': 'Crypto',
            'detailed_results': detailed_results,
            'bootstrap': boot_result,
            'mean_improvement_pct': mean_improvement,
            'elapsed_time_sec': elapsed,
            'hypothesis': 'θ′-biased ordering yields >0% lift in rekey success under drift',
            'verdict': 'SUPPORTED' if mean_improvement > 0 else 'REJECTED',
        }
        
        print(f"\n📊 Crypto Results:")
        for sigma in sigma_values:
            stats = boot_result[sigma]
            print(f"  σ={sigma}ms: Δ={stats['mean_delta_pct']:.2f}%, "
                  f"CI=[{stats['ci_95'][0]:.2f}%, {stats['ci_95'][1]:.2f}%]")
        print(f"  Mean improvement: {mean_improvement:.2f}%")
        print(f"  Verdict: {results['verdict']}")
        print(f"  Time: {elapsed:.1f}s")
        
        self.results['crypto'] = results
        return results
    
    def run_cross_validation(self):
        """Run cross-domain feature validation."""
        print("\n" + "=" * 60)
        print("RUNNING CROSS-DOMAIN VALIDATION")
        print("=" * 60)
        
        cv = CrossValidation()
        
        # Extract features from each domain using results
        rsa_result = self.results['rsa']['detailed_results'][0]  # First test case
        crispr_result = self.results['crispr']['detailed_result']
        crypto_result = self.results['crypto']['detailed_results'][0]  # First sigma
        
        rsa_features = cv.extract_rsa_features(
            n=rsa_result['n'],
            candidate_variance=rsa_result['baseline']['variance']
        )
        
        crispr_features = cv.extract_crispr_features(
            n_guides=crispr_result['n_guides'],
            entropy_mean=crispr_result['baseline_entropy']
        )
        
        crypto_features = cv.extract_crypto_features(
            n_rekeys=crypto_result['baseline']['n_rekeys'],
            fail_rate=crypto_result['baseline']['fail_rate_pct']
        )
        
        # Cross-validate
        all_features = [rsa_features, crispr_features, crypto_features]
        validation = cv.cross_validate_features(all_features)
        
        print(f"\n📊 Cross-Validation Results:")
        print(f"  Domains: {', '.join(validation['domains'])}")
        print(f"  All features present: {validation['all_features_present']}")
        print(f"  Z range: [{validation['Z_range'][0]:.4f}, {validation['Z_range'][1]:.4f}]")
        print(f"  κ range: [{validation['kappa_range'][0]:.4f}, {validation['kappa_range'][1]:.4f}]")
        print(f"  θ′ range: [{validation['theta_prime_range'][0]:.4f}, {validation['theta_prime_range'][1]:.4f}]")
        print(f"  Feature correlation: {validation['feature_correlation']:.4f}")
        
        self.results['cross_validation'] = {
            'features': all_features,
            'validation': validation,
        }
        
        return validation
    
    def generate_summary(self):
        """Generate experiment summary."""
        print("\n" + "=" * 60)
        print("EXPERIMENT SUMMARY")
        print("=" * 60)
        
        summary = {
            'hypothesis': 'θ′-biased ordering via golden LCG yields >0% lift across domains',
            'domains_tested': ['RSA', 'CRISPR', 'Crypto'],
            'results': {},
            'overall_verdict': 'SUPPORTED',
        }
        
        # RSA
        rsa = self.results['rsa']
        summary['results']['RSA'] = {
            'metric': 'Variance Reduction',
            'lift_pct': rsa['bootstrap']['mean_reduction_pct'],
            'ci_95': [rsa['bootstrap']['ci_95_lower'], rsa['bootstrap']['ci_95_upper']],
            'verdict': rsa['verdict'],
        }
        print(f"\n✓ RSA QMC: {rsa['bootstrap']['mean_reduction_pct']:.2f}% "
              f"[{rsa['bootstrap']['ci_95_lower']:.2f}%, {rsa['bootstrap']['ci_95_upper']:.2f}%] - {rsa['verdict']}")
        
        # CRISPR
        crispr = self.results['crispr']
        summary['results']['CRISPR'] = {
            'metric': 'Entropy Accuracy',
            'lift_pct': crispr['bootstrap']['entropy_delta_mean'],
            'ci_95': crispr['bootstrap']['entropy_ci_95'],
            'verdict': crispr['verdict'],
        }
        print(f"✓ CRISPR Spectral: {crispr['bootstrap']['entropy_delta_mean']:.2f}% "
              f"[{crispr['bootstrap']['entropy_ci_95'][0]:.2f}%, {crispr['bootstrap']['entropy_ci_95'][1]:.2f}%] - {crispr['verdict']}")
        
        # Crypto
        crypto = self.results['crypto']
        summary['results']['Crypto'] = {
            'metric': 'Rekey Tolerance',
            'lift_pct': crypto['mean_improvement_pct'],
            'ci_95': 'varies by σ',
            'verdict': crypto['verdict'],
        }
        print(f"✓ Crypto Rekey: {crypto['mean_improvement_pct']:.2f}% - {crypto['verdict']}")
        
        # Overall verdict
        if all(r['verdict'] == 'SUPPORTED' for r in [rsa, crispr, crypto]):
            summary['overall_verdict'] = 'SUPPORTED'
            print(f"\n🎉 OVERALL VERDICT: HYPOTHESIS SUPPORTED")
        else:
            summary['overall_verdict'] = 'PARTIAL' 
            print(f"\n⚠️  OVERALL VERDICT: HYPOTHESIS PARTIALLY SUPPORTED")
        
        self.results['summary'] = summary
        return summary
    
    def save_results(self):
        """Save all results to JSON file."""
        output_file = self.output_dir / 'experiment_results.json'
        
        # Convert Path objects to strings for JSON serialization
        serializable_results = json.loads(json.dumps(self.results, default=str))
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        return output_file


def main():
    """Main experiment execution."""
    print("=" * 60)
    print("θ′-BIASED ORDERING HYPOTHESIS TEST")
    print("Golden LCG Experiment")
    print("=" * 60)
    print()
    
    # Use smaller bootstrap for faster execution in testing
    # For full experiment, use n_bootstrap=1000
    n_bootstrap = 100 if '--quick' in sys.argv else 1000
    
    print(f"Configuration:")
    print(f"  Bootstrap replicates: {n_bootstrap}")
    print(f"  Seed: 42")
    print()
    
    runner = ExperimentRunner(output_dir='results', seed=42)
    
    try:
        # Run all experiments
        runner.run_rsa_experiment(n_bootstrap=n_bootstrap)
        runner.run_crispr_experiment(n_guides=100, n_bootstrap=n_bootstrap)
        runner.run_crypto_experiment(sigma_values=[1, 10, 50, 100], n_bootstrap=n_bootstrap)
        
        # Cross-validate
        runner.run_cross_validation()
        
        # Generate summary
        runner.generate_summary()
        
        # Save results
        runner.save_results()
        
        print("\n" + "=" * 60)
        print("EXPERIMENT COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
