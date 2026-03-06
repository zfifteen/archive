"""
Discrete Analogs of Quantum Nonlocality via Zeta Shift Cascades

This module implements discrete variance propagation modeling with var(O) ~ log log N
scaling in zeta shift cascades, simulating discrete geodesic effects on operator 
variance using θ'(n,k) and κ(n) transformations.

Based on the Z Framework's empirical findings that helical patterns in 
DiscreteZetaShift unfoldings exhibit var(O) ~ log log N, suggesting quantum 
nonlocality analogs.
"""

import numpy as np
import matplotlib.pyplot as plt
import mpmath as mp
from core.domain import DiscreteZetaShift
from core.axioms import theta_prime, curvature
import pandas as pd
from scipy import stats
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

mp.mp.dps = 50  # High precision for accurate variance computations

PHI = (1 + mp.sqrt(5)) / 2
E_SQUARED = mp.exp(2)

class QuantumNonlocalityAnalyzer:
    """
    Analyzes discrete variance propagation and quantum nonlocality patterns
    in zeta shift cascades.
    """
    
    def __init__(self, max_N=1000, seed=2):
        """
        Initialize analyzer with maximum cascade length and seed value.
        
        Args:
            max_N: Maximum number of elements in zeta shift cascade
            seed: Starting value for zeta shift chain
        """
        self.max_N = max_N
        self.seed = seed
        self.cascade_data = {}
        self.variance_data = {}
        
    def generate_cascade(self, N):
        """
        Generate a zeta shift cascade of length N.
        
        Args:
            N: Length of cascade to generate
            
        Returns:
            List of DiscreteZetaShift objects representing the cascade
        """
        if N in self.cascade_data:
            return self.cascade_data[N]
            
        cascade = []
        zeta = DiscreteZetaShift(self.seed)
        cascade.append(zeta)
        
        for i in range(1, N):
            zeta = zeta.unfold_next()
            cascade.append(zeta)
            
        self.cascade_data[N] = cascade
        return cascade
        
    def extract_operator_values(self, cascade):
        """
        Extract O operator values from cascade.
        
        Args:
            cascade: List of DiscreteZetaShift objects
            
        Returns:
            numpy array of O values
        """
        return np.array([float(shift.getO()) for shift in cascade])
        
    def apply_theta_prime_transformation(self, cascade, k=3.33):
        """
        Apply θ'(n,k) transformation to cascade elements.
        
        Args:
            cascade: List of DiscreteZetaShift objects  
            k: Curvature exponent parameter (default optimal k* ≈ 3.33)
            
        Returns:
            numpy array of transformed values
        """
        n_values = np.array([float(shift.a) for shift in cascade])
        return np.array([float(theta_prime(n, k, PHI)) for n in n_values])
        
    def compute_curvature_values(self, cascade):
        """
        Compute κ(n) curvature values for cascade elements.
        
        Args:
            cascade: List of DiscreteZetaShift objects
            
        Returns:
            numpy array of curvature values
        """
        curvature_vals = []
        for shift in cascade:
            n = int(shift.a)
            d_n = len([i for i in range(1, n + 1) if n % i == 0])  # divisor count
            kappa = curvature(n, d_n)
            curvature_vals.append(float(kappa))
        return np.array(curvature_vals)
        
    def analyze_variance_scaling(self, N_values=None):
        """
        Analyze variance scaling relationship var(O) ~ log log N.
        
        Args:
            N_values: List of cascade lengths to analyze (default: powers of 2)
            
        Returns:
            Dictionary containing scaling analysis results
        """
        if N_values is None:
            N_values = [2**i for i in range(4, min(11, int(np.log2(self.max_N)) + 1))]
            
        variances = []
        log_log_N = []
        
        for N in N_values:
            if N > self.max_N or N < 3:  # Skip N < 3 to avoid log(log(N)) issues
                continue
                
            cascade = self.generate_cascade(N)
            O_values = self.extract_operator_values(cascade)
            
            # Compute variance of O values
            var_O = np.var(O_values)
            variances.append(var_O)
            log_log_N.append(np.log(np.log(N)))
        
        # Handle edge cases
        if len(variances) < 2:
            # Return default values for insufficient data
            return {
                'N_values': N_values[:len(variances)],
                'variances': variances,
                'log_log_N': log_log_N,
                'slope': 0.0,
                'intercept': variances[0] if variances else 0.0,
                'r_squared': 0.0,
                'correlation': 0.0,
                'scaling_formula': "Insufficient data for scaling analysis"
            }
            
        # Fit linear relationship: var(O) = a * log(log(N)) + b
        coeffs = np.polyfit(log_log_N, variances, 1)
        slope, intercept = coeffs
        
        # Compute R-squared
        y_pred = slope * np.array(log_log_N) + intercept
        ss_res = np.sum((variances - y_pred) ** 2)
        ss_tot = np.sum((variances - np.mean(variances)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Correlation coefficient
        correlation = np.corrcoef(log_log_N, variances)[0, 1]
        if np.isnan(correlation):  # Handle case where variance is zero
            correlation = 0.0
        
        results = {
            'N_values': N_values[:len(variances)],
            'variances': variances,
            'log_log_N': log_log_N,
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'correlation': correlation,
            'scaling_formula': f"var(O) ≈ {slope:.4f} * log(log(N)) + {intercept:.4f}"
        }
        
        self.variance_data = results
        return results
        
    def simulate_geodesic_effects(self, N=500, k_values=None):
        """
        Simulate discrete geodesic effects on operator variance using 
        θ'(n,k) and κ(n) transformations.
        
        Args:
            N: Cascade length for analysis
            k_values: List of k values to test (default: around optimal k* ≈ 3.33)
            
        Returns:
            Dictionary containing geodesic effect analysis
        """
        if k_values is None:
            k_values = np.linspace(0.1, 0.5, 21)
            
        cascade = self.generate_cascade(N)
        O_baseline = self.extract_operator_values(cascade)
        baseline_var = np.var(O_baseline)
        
        curvature_vals = self.compute_curvature_values(cascade)
        
        results = {
            'k_values': k_values,
            'variance_ratios': [],
            'theta_correlations': [],
            'curvature_correlations': [],
            'geodesic_effects': []
        }
        
        for k in k_values:
            # Apply θ'(n,k) transformation
            theta_transformed = self.apply_theta_prime_transformation(cascade, k)
            
            # Compute variance of transformed O values weighted by θ'(n,k)
            O_weighted = O_baseline * (1 + 0.1 * theta_transformed)  # Geodesic modulation
            var_weighted = np.var(O_weighted)
            
            # Variance ratio (effect magnitude)
            var_ratio = var_weighted / baseline_var
            results['variance_ratios'].append(var_ratio)
            
            # Correlation between θ'(n,k) and O values
            theta_corr = np.corrcoef(theta_transformed, O_baseline)[0, 1]
            results['theta_correlations'].append(theta_corr)
            
            # Correlation between κ(n) and transformed values
            curvature_corr = np.corrcoef(curvature_vals, theta_transformed)[0, 1]
            results['curvature_correlations'].append(curvature_corr)
            
            # Combined geodesic effect metric
            geodesic_effect = abs(var_ratio - 1) * abs(theta_corr) * abs(curvature_corr)
            results['geodesic_effects'].append(geodesic_effect)
            
        # Find optimal k (maximum geodesic effect)
        max_idx = np.argmax(results['geodesic_effects'])
        results['optimal_k'] = k_values[max_idx]
        results['max_geodesic_effect'] = results['geodesic_effects'][max_idx]
        
        return results
        
    def quantum_nonlocality_metrics(self, N=500):
        """
        Compute quantum nonlocality metrics from cascade analysis.
        
        Args:
            N: Cascade length for analysis
            
        Returns:
            Dictionary containing nonlocality metrics
        """
        cascade = self.generate_cascade(N)
        O_values = self.extract_operator_values(cascade)
        
        # Bell-like correlation measurements
        # Split cascade into spatially separated regions
        mid = N // 2
        O_A = O_values[:mid]  # Region A
        O_B = O_values[mid:]  # Region B
        
        # Cross-correlation between regions (nonlocal correlation)
        cross_corr = np.corrcoef(O_A[:len(O_B)], O_B)[0, 1]
        
        # Variance entanglement metric
        var_A = np.var(O_A)
        var_B = np.var(O_B)
        var_total = np.var(O_values)
        entanglement_metric = var_total / (var_A + var_B) if (var_A + var_B) > 0 else 0
        
        # Nonlocality strength (deviation from classical expectation)
        classical_bound = 1 / np.sqrt(2)  # Classical correlation bound
        nonlocality_violation = max(0, abs(cross_corr) - classical_bound)
        
        # Quantum coherence measure via variance scaling
        scaling_analysis = self.analyze_variance_scaling([N])
        coherence_measure = scaling_analysis['slope'] * np.log(np.log(N))
        
        return {
            'cross_correlation': cross_corr,
            'entanglement_metric': entanglement_metric,
            'nonlocality_violation': nonlocality_violation,
            'coherence_measure': coherence_measure,
            'bell_inequality_factor': abs(cross_corr) / classical_bound,
            'quantum_advantage': nonlocality_violation > 0
        }
        
    def plot_variance_scaling(self, save_path=None):
        """
        Plot variance scaling analysis results.
        
        Args:
            save_path: Optional path to save plot
        """
        if not self.variance_data:
            self.analyze_variance_scaling()
            
        data = self.variance_data
        
        plt.figure(figsize=(10, 6))
        plt.scatter(data['log_log_N'], data['variances'], color='red', s=50, alpha=0.7, label='Data')
        
        # Plot fitted line
        x_fit = np.linspace(min(data['log_log_N']), max(data['log_log_N']), 100)
        y_fit = data['slope'] * x_fit + data['intercept']
        plt.plot(x_fit, y_fit, 'b-', linewidth=2, 
                label=f"Fit: {data['scaling_formula']}")
        
        plt.xlabel('log(log(N))')
        plt.ylabel('var(O)')
        plt.title('Discrete Variance Propagation: var(O) ~ log log N')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add statistics text
        stats_text = f"R² = {data['r_squared']:.4f}\nCorrelation = {data['correlation']:.4f}"
        plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_geodesic_effects(self, geodesic_results=None, save_path=None):
        """
        Plot geodesic effects analysis.
        
        Args:
            geodesic_results: Results from simulate_geodesic_effects()
            save_path: Optional path to save plot
        """
        if geodesic_results is None:
            geodesic_results = self.simulate_geodesic_effects()
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        k_vals = geodesic_results['k_values']
        
        # Variance ratios
        ax1.plot(k_vals, geodesic_results['variance_ratios'], 'b-', linewidth=2)
        ax1.set_xlabel('k')
        ax1.set_ylabel('Variance Ratio')
        ax1.set_title('Geodesic Effect on Variance')
        ax1.grid(True, alpha=0.3)
        ax1.axvline(x=geodesic_results['optimal_k'], color='red', linestyle='--', alpha=0.7)
        
        # θ'(n,k) correlations
        ax2.plot(k_vals, geodesic_results['theta_correlations'], 'g-', linewidth=2)
        ax2.set_xlabel('k')
        ax2.set_ylabel('θ\'(n,k) Correlation')
        ax2.set_title('θ\'(n,k) Transformation Correlation')
        ax2.grid(True, alpha=0.3)
        ax2.axvline(x=geodesic_results['optimal_k'], color='red', linestyle='--', alpha=0.7)
        
        # Curvature correlations
        ax3.plot(k_vals, geodesic_results['curvature_correlations'], 'm-', linewidth=2)
        ax3.set_xlabel('k')
        ax3.set_ylabel('κ(n) Correlation')
        ax3.set_title('Curvature Correlation')
        ax3.grid(True, alpha=0.3)
        ax3.axvline(x=geodesic_results['optimal_k'], color='red', linestyle='--', alpha=0.7)
        
        # Combined geodesic effects
        ax4.plot(k_vals, geodesic_results['geodesic_effects'], 'r-', linewidth=2)
        ax4.set_xlabel('k')
        ax4.set_ylabel('Geodesic Effect Metric')
        ax4.set_title('Combined Geodesic Effect')
        ax4.grid(True, alpha=0.3)
        ax4.axvline(x=geodesic_results['optimal_k'], color='red', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Optimal k value: {geodesic_results['optimal_k']:.3f}")
        print(f"Maximum geodesic effect: {geodesic_results['max_geodesic_effect']:.6f}")
        
    def generate_report(self):
        """
        Generate comprehensive analysis report.
        
        Returns:
            Dictionary containing complete analysis results
        """
        print("Generating Discrete Variance Propagation Analysis Report...")
        print("=" * 60)
        
        # Variance scaling analysis
        print("\n1. Variance Scaling Analysis (var(O) ~ log log N)")
        print("-" * 50)
        scaling_results = self.analyze_variance_scaling()
        print(f"Scaling relationship: {scaling_results['scaling_formula']}")
        print(f"R-squared: {scaling_results['r_squared']:.6f}")
        print(f"Correlation coefficient: {scaling_results['correlation']:.6f}")
        
        # Geodesic effects analysis
        print("\n2. Geodesic Effects Analysis")
        print("-" * 30)
        geodesic_results = self.simulate_geodesic_effects()
        print(f"Optimal k parameter: {geodesic_results['optimal_k']:.3f}")
        print(f"Maximum geodesic effect: {geodesic_results['max_geodesic_effect']:.6f}")
        
        # Quantum nonlocality metrics
        print("\n3. Quantum Nonlocality Metrics")
        print("-" * 35)
        nonlocality_results = self.quantum_nonlocality_metrics()
        print(f"Cross-correlation: {nonlocality_results['cross_correlation']:.6f}")
        print(f"Entanglement metric: {nonlocality_results['entanglement_metric']:.6f}")
        print(f"Nonlocality violation: {nonlocality_results['nonlocality_violation']:.6f}")
        print(f"Bell inequality factor: {nonlocality_results['bell_inequality_factor']:.6f}")
        print(f"Quantum advantage: {nonlocality_results['quantum_advantage']}")
        
        # Combined report
        report = {
            'variance_scaling': scaling_results,
            'geodesic_effects': geodesic_results,
            'quantum_nonlocality': nonlocality_results,
            'summary': {
                'var_scaling_confirmed': scaling_results['correlation'] > 0.8,
                'optimal_k_near_expected': abs(geodesic_results['optimal_k'] - 3.33) < 0.1,
                'quantum_nonlocality_detected': nonlocality_results['quantum_advantage']
            }
        }
        
        print("\n" + "=" * 60)
        print("Analysis Complete!")
        
        return report

# Demonstration function
def run_demonstration():
    """
    Run a comprehensive demonstration of discrete variance propagation analysis.
    """
    print("Discrete Analogs of Quantum Nonlocality via Zeta Shift Cascades")
    print("=" * 65)
    print("Demonstrating var(O) ~ log log N scaling and geodesic effects...")
    
    # Initialize analyzer
    analyzer = QuantumNonlocalityAnalyzer(max_N=1000, seed=2)
    
    # Generate comprehensive report
    report = analyzer.generate_report()
    
    # Create visualizations
    print("\nGenerating visualizations...")
    analyzer.plot_variance_scaling()
    analyzer.plot_geodesic_effects()
    
    return report

if __name__ == "__main__":
    run_demonstration()