"""
Plotting and Visualization Module
Generates plots for RSA variance, CRISPR resonance, crypto fails, and cross-domain lift.
"""

import json
from pathlib import Path

# Try importing matplotlib, but make it optional
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, plots will not be generated")


class ExperimentPlotter:
    """Generate plots for experiment results."""
    
    def __init__(self, results_file, output_dir='plots'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        with open(results_file, 'r') as f:
            self.results = json.load(f)
    
    def plot_rsa_variance(self):
        """Plot RSA variance reduction comparison."""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        rsa = self.results['rsa']
        detailed = rsa['detailed_results']
        
        # Extract data
        names = [r['rsa_name'] for r in detailed]
        baseline_var = [r['baseline']['variance'] for r in detailed]
        theta_var = [r['theta_prime']['variance'] for r in detailed]
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Variance comparison
        x = range(len(names))
        width = 0.35
        ax1.bar([i - width/2 for i in x], baseline_var, width, label='Baseline', alpha=0.8)
        ax1.bar([i + width/2 for i in x], theta_var, width, label="θ′-biased", alpha=0.8)
        ax1.set_xlabel('RSA Test Case')
        ax1.set_ylabel('Variance')
        ax1.set_title('RSA QMC: Candidate Variance Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(names, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Reduction percentage
        reductions = [r['variance_reduction_pct'] for r in detailed]
        ax2.bar(x, reductions, color='green', alpha=0.8)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('RSA Test Case')
        ax2.set_ylabel('Variance Reduction (%)')
        ax2.set_title('RSA QMC: Variance Reduction')
        ax2.set_xticks(x)
        ax2.set_xticklabels(names, rotation=45)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / 'rsa_variance.png'
        plt.savefig(output_file, dpi=150)
        plt.close()
        
        print(f"  Saved: {output_file}")
        return output_file
    
    def plot_crispr_resonance(self):
        """Plot CRISPR spectral disruption improvements."""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        crispr = self.results['crispr']
        detailed = crispr['detailed_result']
        bootstrap = crispr['bootstrap']
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Entropy comparison
        metrics = ['Entropy', 'Resonance']
        baseline = [detailed['baseline_entropy'], detailed['baseline_resonance']]
        theta = [detailed['theta_entropy'], detailed['theta_resonance']]
        
        x = range(len(metrics))
        width = 0.35
        ax1.bar([i - width/2 for i in x], baseline, width, label='Baseline', alpha=0.8)
        ax1.bar([i + width/2 for i in x], theta, width, label="θ′-biased", alpha=0.8)
        ax1.set_xlabel('Metric')
        ax1.set_ylabel('Score')
        ax1.set_title('CRISPR: Scoring Metric Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(metrics)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Improvement with CI
        entropy_delta = bootstrap['entropy_delta_mean']
        resonance_delta = bootstrap['resonance_delta_mean']
        deltas = [entropy_delta, resonance_delta]
        
        entropy_ci = bootstrap['entropy_ci_95']
        resonance_ci = bootstrap['resonance_ci_95']
        errors = [
            [entropy_delta - entropy_ci[0], entropy_ci[1] - entropy_delta],
            [resonance_delta - resonance_ci[0], resonance_ci[1] - resonance_delta]
        ]
        yerr = [[e[0] for e in errors], [e[1] for e in errors]]
        ax2.bar(x, deltas, color='blue', alpha=0.8, yerr=yerr, capsize=5)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Metric')
        ax2.set_ylabel('Improvement (%)')
        ax2.set_title('CRISPR: Improvement with 95% CI')
        ax2.set_xticks(x)
        ax2.set_xticklabels(metrics)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / 'crispr_resonance.png'
        plt.savefig(output_file, dpi=150)
        plt.close()
        
        print(f"  Saved: {output_file}")
        return output_file
    
    def plot_crypto_fails(self):
        """Plot crypto rekey failure rate improvements."""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        crypto = self.results['crypto']
        detailed = crypto['detailed_results']
        bootstrap = crypto['bootstrap']
        
        # Extract data
        sigmas = [r['sigma'] for r in detailed]
        baseline_fails = [r['baseline']['fail_rate_pct'] for r in detailed]
        theta_fails = [r['theta_prime']['fail_rate_pct'] for r in detailed]
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Failure rate comparison
        x = range(len(sigmas))
        width = 0.35
        ax1.bar([i - width/2 for i in x], baseline_fails, width, label='Baseline', alpha=0.8)
        ax1.bar([i + width/2 for i in x], theta_fails, width, label="θ′-biased", alpha=0.8)
        ax1.set_xlabel('Drift σ (ms)')
        ax1.set_ylabel('Failure Rate (%)')
        ax1.set_title('Crypto Rekey: Failure Rate by Drift')
        ax1.set_xticks(x)
        ax1.set_xticklabels([f'{s}' for s in sigmas])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Improvement with CI
        improvements = [bootstrap[str(s)]['mean_delta_pct'] for s in sigmas]
        cis = [bootstrap[str(s)]['ci_95'] for s in sigmas]
        errors = [[imp - ci[0], ci[1] - imp] for imp, ci in zip(improvements, cis)]
        
        ax2.bar(x, improvements, color='green', alpha=0.8, 
               yerr=[[e[0] for e in errors], [e[1] for e in errors]], capsize=5)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Drift σ (ms)')
        ax2.set_ylabel('Relative Improvement (%)')
        ax2.set_title('Crypto Rekey: Improvement with 95% CI')
        ax2.set_xticks(x)
        ax2.set_xticklabels([f'{s}' for s in sigmas])
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / 'crypto_fails.png'
        plt.savefig(output_file, dpi=150)
        plt.close()
        
        print(f"  Saved: {output_file}")
        return output_file
    
    def plot_cross_lift(self):
        """Plot cross-domain lift comparison."""
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        summary = self.results['summary']
        
        # Extract data
        domains = []
        lifts = []
        ci_lowers = []
        ci_uppers = []
        
        for domain, data in summary['results'].items():
            domains.append(domain)
            lifts.append(data['lift_pct'])
            
            ci = data['ci_95']
            if isinstance(ci, list) and len(ci) == 2:
                ci_lowers.append(data['lift_pct'] - ci[0])
                ci_uppers.append(ci[1] - data['lift_pct'])
            else:
                ci_lowers.append(0)
                ci_uppers.append(0)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(domains))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        
        ax.bar(x, lifts, color=colors, alpha=0.8, 
              yerr=[ci_lowers, ci_uppers], capsize=5)
        ax.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Zero lift')
        ax.set_xlabel('Domain')
        ax.set_ylabel('Lift (%)')
        ax.set_title("θ′-Biased Ordering: Cross-Domain Lift with 95% CI")
        ax.set_xticks(x)
        ax.set_xticklabels(domains)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add value labels on bars
        for i, (lift, domain) in enumerate(zip(lifts, domains)):
            ax.text(i, lift + (ci_uppers[i] if ci_uppers[i] > 0 else 1), 
                   f'{lift:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        output_file = self.output_dir / 'cross_lift.png'
        plt.savefig(output_file, dpi=150)
        plt.close()
        
        print(f"  Saved: {output_file}")
        return output_file
    
    def generate_all_plots(self):
        """Generate all plots."""
        print("Generating plots...")
        
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️  Matplotlib not available, skipping plot generation")
            return
        
        self.plot_rsa_variance()
        self.plot_crispr_resonance()
        self.plot_crypto_fails()
        self.plot_cross_lift()
        
        print("✓ All plots generated")


def main():
    """Generate plots from results file."""
    import sys
    
    if len(sys.argv) < 2:
        results_file = 'results/experiment_results.json'
    else:
        results_file = sys.argv[1]
    
    if not Path(results_file).exists():
        print(f"Error: Results file not found: {results_file}")
        print("Run the experiment first: python run_experiment.py")
        return 1
    
    plotter = ExperimentPlotter(results_file, output_dir='plots')
    plotter.generate_all_plots()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
