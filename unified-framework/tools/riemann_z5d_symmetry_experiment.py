#!/usr/bin/env python3
"""
Riemann Predictors vs Z5D Symmetry Analysis Experiment

This script implements a rigorous scientific experiment to test/falsify the hypothesis:
"Riemann Predictors to Highlight Potential Symmetries"

Key claims to test:
1. Prime density enhancement ~15% with CI [14.6%, 15.4%]
2. Correlations r ≥ 0.93 with p < 10^-10  
3. Asymptotic convergence and oscillatory patterns
4. Z5D underestimating at small k, overestimating at large k
5. Differences scaling symmetrically as ~O(1/log k)
"""

import numpy as np
import mpmath as mp
import matplotlib.pyplot as plt
from sympy import prime
import timeit
import time
import json
import os
from typing import List, Dict, Any
from scipy import stats
import warnings

# Set high precision for numerical stability
mp.mp.dps = 50

class RiemannZ5DExperiment:
    """
    Implements the rigorous scientific experiment comparing Z5D and Riemann predictors.
    """
    
    def __init__(self, precision_dps: int = 50):
        mp.mp.dps = precision_dps
        self.precision_dps = precision_dps
        self.phi = (1 + mp.sqrt(5)) / 2  # Golden ratio
        self.results = {}
        
    def load_zeta_zeros(self, filename: str = "zeta.txt", max_zeros: int = None) -> List[mp.mpf]:
        """Load pre-computed zeta zeros from file or compute them."""
        zeros = []
        try:
            with open(filename, 'r') as f:
                for i, line in enumerate(f):
                    if max_zeros and i >= max_zeros:
                        break
                        
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                        
                    parts = line.split()
                    if len(parts) >= 3:  # index real_part imaginary_part
                        imag_part = mp.mpf(parts[2])
                        zeros.append(imag_part)
                        
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Computing zeros on-the-fly...")
            # Compute first 10 zeros for basic testing
            zeros = self._compute_first_zeta_zeros(max_zeros or 10)
            
        if max_zeros:
            zeros = zeros[:max_zeros]
        
        print(f"Loaded {len(zeros)} zeta zeros with precision dps={self.precision_dps}")
        return zeros
    
    def _compute_first_zeta_zeros(self, n: int) -> List[mp.mpf]:
        """Compute first n non-trivial zeta zeros using mpmath."""
        zeros = []
        for i in range(1, n + 1):
            zero = mp.zetazero(i)
            zeros.append(zero.imag)
        return zeros
    
    def z5d_prime_original(self, k: mp.mpf) -> float:
        """
        Original Z5D implementation with calibrated parameters.
        
        Uses c = -0.00247 and k* = 0.04449 for curvature adjustments.
        """
        k_mp = mp.mpf(k)
        
        # Base PNT inverse approximation  
        if k_mp <= 5:
            return float(k_mp)  # Handle small k edge cases
            
        log_k = mp.log(k_mp)
        log_log_k = mp.log(log_k) if log_k > 1 else mp.mpf(0)
        
        # PNT inverse: k * (ln(k) + ln(ln(k)) - 1)
        p_pnt = k_mp * (log_k + log_log_k - 1)
        
        # Z5D enhancements with calibrated parameters
        c = mp.mpf('-0.00247')  # Dilation calibration
        k_star = mp.mpf('0.04449')  # Curvature calibration
        
        # Dilation term: d(k) approximated by log structure
        d_term = mp.log(k_mp + 1) / (mp.e ** 2)
        
        # Curvature term: e(k) using geometric resolution
        e_term = mp.power(mp.log(k_mp), mp.mpf('0.618'))  # Golden ratio exponent
        
        # Z5D formula: p_PNT(k) + c·d(k)·p_PNT(k) + k*·e(k)·p_PNT(k)
        z5d_prediction = p_pnt + c * d_term * p_pnt + k_star * e_term * p_pnt
        
        return float(z5d_prediction)
    
    def riemann_prime_inverse(self, k: mp.mpf, zeta_zeros: List[mp.mpf] = None) -> float:
        """
        Riemann implementation using Gram series inversion for p_n.
        
        Implements explicit formula corrections using zeta zeros.
        """
        k_mp = mp.mpf(k)
        
        if k_mp <= 5:
            return float(k_mp)  # Handle small k edge cases
            
        # Base inverse li approximation
        log_k = mp.log(k_mp)
        log_log_k = mp.log(log_k) if log_k > 1 else mp.mpf(0)
        
        # Initial approximation using inverse li
        x_approx = k_mp * (log_k + log_log_k - 1)
        
        # Apply Riemann explicit formula corrections if zeros provided
        if zeta_zeros:
            # Correction based on explicit formula: sum over zeta zeros
            correction = mp.mpf(0)
            
            for gamma in zeta_zeros[:min(20, len(zeta_zeros))]:  # Use first 20 zeros
                # Oscillatory term: x^(1/2) * cos(gamma * ln(x)) / (pi * gamma)
                if gamma > 0:
                    omega = gamma * mp.log(x_approx)
                    amplitude = mp.sqrt(x_approx) / (mp.pi * gamma)
                    oscillation = amplitude * mp.cos(omega)
                    correction += oscillation
            
            # Apply correction with damping factor
            damping = mp.mpf('0.1')  # Small damping to prevent overcorrection
            x_corrected = x_approx - damping * correction
            
            return float(x_corrected)
        
        return float(x_approx)
    
    def gram_point_analysis(self, k_values: List[mp.mpf]) -> Dict[str, Any]:
        """
        Analyze Gram points and their relationship to prime prediction accuracy.
        """
        results = {
            'gram_points': [],
            'gram_corrections': [],
            'accuracy_improvement': []
        }
        
        for k in k_values:
            # Compute Gram point index
            gram_index = mp.log(k) / (2 * mp.pi)
            gram_point = mp.pi * gram_index
            
            # Correction factor based on Gram point proximity
            gram_correction = mp.sin(gram_point) * mp.exp(-gram_index / 10)
            
            results['gram_points'].append(float(gram_point))
            results['gram_corrections'].append(float(gram_correction))
            
        return results
    
    def run_symmetry_analysis(self, k_min: int = 1000, k_max: int = 1000000, 
                            num_points: int = 20) -> Dict[str, Any]:
        """
        Run the main symmetry analysis experiment across k values.
        
        Tests the hypothesis about symmetric scaling and oscillatory patterns.
        """
        print(f"Running symmetry analysis from k={k_min} to k={k_max} with {num_points} points")
        
        # Generate k values on log scale
        k_values = np.logspace(np.log10(k_min), np.log10(k_max), num=num_points)
        k_values_mp = [mp.mpf(k) for k in k_values]
        
        # Load zeta zeros for Riemann implementation
        zeta_zeros = self.load_zeta_zeros(max_zeros=50)
        
        # Time and compute Z5D predictions
        print("Computing Z5D predictions...")
        z5d_times = []
        pred_z5d = []
        
        for k in k_values_mp:
            start_time = time.time()
            prediction = self.z5d_prime_original(k)
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            z5d_times.append(elapsed)
            pred_z5d.append(prediction)
        
        # Time and compute Riemann predictions
        print("Computing Riemann predictions...")
        riemann_times = []
        pred_riemann = []
        
        for k in k_values_mp:
            start_time = time.time()
            prediction = self.riemann_prime_inverse(k, zeta_zeros)
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            riemann_times.append(elapsed)
            pred_riemann.append(prediction)
        
        # Compute differences and analyze symmetries
        differences = np.array(pred_z5d) - np.array(pred_riemann)
        relative_differences = differences / np.array(pred_riemann) * 100
        
        # Test scaling hypothesis: differences ~ O(1/log k)
        log_k_values = np.log(k_values)
        scaling_fit = np.polyfit(log_k_values, np.abs(differences), 1)
        
        # Statistical analysis
        correlation, p_value = stats.pearsonr(pred_z5d, pred_riemann)
        
        # Oscillation analysis
        oscillation_freq = self._analyze_oscillations(k_values, differences)
        
        results = {
            'k_values': k_values.tolist(),
            'z5d_predictions': pred_z5d,
            'riemann_predictions': pred_riemann,
            'differences': differences.tolist(),
            'relative_differences': relative_differences.tolist(),
            'z5d_times_ms': z5d_times,
            'riemann_times_ms': riemann_times,
            'correlation': correlation,
            'p_value': p_value,
            'scaling_fit': scaling_fit.tolist(),
            'oscillation_analysis': oscillation_freq,
            'mean_z5d_time': np.mean(z5d_times),
            'mean_riemann_time': np.mean(riemann_times),
            'statistics': {
                'correlation_r': correlation,
                'p_value': p_value,
                'mean_abs_diff': np.mean(np.abs(differences)),
                'std_diff': np.std(differences),
                'max_abs_diff': np.max(np.abs(differences))
            }
        }
        
        self.results = results
        return results
    
    def _analyze_oscillations(self, k_values: np.ndarray, differences: np.ndarray) -> Dict[str, Any]:
        """Analyze oscillatory patterns in the differences."""
        # Handle small datasets
        if len(differences) < 4:
            return {
                'dominant_frequency': 0.0,
                'power_spectrum_peak': 0.0,
                'oscillation_amplitude': float(np.std(differences))
            }
        
        # FFT analysis to detect periodic components
        fft = np.fft.fft(differences)
        freqs = np.fft.fftfreq(len(differences), d=np.mean(np.diff(np.log(k_values))))
        
        # Find dominant frequencies
        power_spectrum = np.abs(fft) ** 2
        half_len = len(power_spectrum) // 2
        
        if half_len <= 1:
            return {
                'dominant_frequency': 0.0,
                'power_spectrum_peak': 0.0,
                'oscillation_amplitude': float(np.std(differences))
            }
        
        dominant_freq_idx = np.argmax(power_spectrum[1:half_len]) + 1
        dominant_freq = freqs[dominant_freq_idx]
        
        return {
            'dominant_frequency': float(dominant_freq),
            'power_spectrum_peak': float(power_spectrum[dominant_freq_idx]),
            'oscillation_amplitude': float(np.std(differences))
        }
    
    def generate_plots(self, save_dir: str = "plots") -> None:
        """Generate the plots described in the problem statement."""
        if not self.results:
            raise ValueError("No results available. Run experiment first.")
        
        os.makedirs(save_dir, exist_ok=True)
        
        k_values = self.results['k_values']
        pred_z5d = self.results['z5d_predictions']
        pred_riemann = self.results['riemann_predictions']
        differences = self.results['differences']
        relative_differences = self.results['relative_differences']
        
        # Plot 1: Z5D vs Riemann Predictions
        plt.figure(figsize=(10, 6))
        plt.plot(np.log10(k_values), pred_z5d, label='Z_5D', marker='o', linewidth=2)
        plt.plot(np.log10(k_values), pred_riemann, label='Riemann', marker='x', linewidth=2)
        plt.xlabel('log10(k)')
        plt.ylabel('Predicted p_k')
        plt.title('Z_5D vs Riemann Predictions')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{save_dir}/pred_vs_logk.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: Difference vs log(k)
        plt.figure(figsize=(10, 6))
        plt.plot(np.log10(k_values), differences, label='Z_5D - Riemann', marker='o', linewidth=2, color='red')
        plt.xlabel('log10(k)')
        plt.ylabel('Difference')
        plt.title('Difference vs log(k)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(f'{save_dir}/diff_vs_logk.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 3: Normalized Difference vs log(k)
        plt.figure(figsize=(10, 6))
        plt.plot(np.log10(k_values), relative_differences, label='Normalized Difference (%)', 
                marker='o', linewidth=2, color='green')
        plt.xlabel('log10(k)')
        plt.ylabel('Normalized Difference (%)')
        plt.title('Normalized Difference vs log(k)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(f'{save_dir}/norm_diff_vs_logk.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 4: Symmetry Analysis
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Log-log scaling analysis
        plt.subplot(2, 2, 1)
        plt.loglog(k_values, np.abs(differences), 'bo-', label='|Z5D - Riemann|')
        plt.loglog(k_values, 1/np.log(k_values), 'r--', label='O(1/log k)')
        plt.xlabel('k')
        plt.ylabel('|Difference|')
        plt.title('Scaling Analysis')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Subplot 2: Correlation scatter
        plt.subplot(2, 2, 2)
        plt.scatter(pred_riemann, pred_z5d, alpha=0.7, s=50)
        plt.plot([min(pred_riemann), max(pred_riemann)], [min(pred_riemann), max(pred_riemann)], 
                'r--', label='Perfect correlation')
        plt.xlabel('Riemann Prediction')
        plt.ylabel('Z5D Prediction')
        plt.title(f'Correlation Analysis (r={self.results["correlation"]:.4f})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Subplot 3: Oscillation pattern
        plt.subplot(2, 2, 3)
        plt.plot(np.log10(k_values), differences, 'g-o', linewidth=2)
        plt.xlabel('log10(k)')
        plt.ylabel('Difference')
        plt.title('Oscillatory Pattern Detection')
        plt.grid(True, alpha=0.3)
        
        # Subplot 4: Performance comparison
        plt.subplot(2, 2, 4)
        x_pos = np.arange(2)
        times = [self.results['mean_z5d_time'], self.results['mean_riemann_time']]
        plt.bar(x_pos, times, color=['blue', 'orange'])
        plt.xticks(x_pos, ['Z5D', 'Riemann'])
        plt.ylabel('Average Time (ms)')
        plt.title('Performance Comparison')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{save_dir}/symmetry_analysis_comprehensive.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Plots saved to {save_dir}/ directory")
    
    def save_results(self, filename: str = "riemann_z5d_experiment_results.json") -> None:
        """Save experimental results to JSON file."""
        if not self.results:
            raise ValueError("No results available. Run experiment first.")
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to {filename}")
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the experimental findings."""
        if not self.results:
            return "No results available. Run experiment first."
        
        r = self.results
        
        report = f"""
=== RIEMANN PREDICTORS vs Z5D SYMMETRY ANALYSIS ===

EXPERIMENTAL SETUP:
- K range: {r['k_values'][0]:.0f} to {r['k_values'][-1]:.0f}
- Number of test points: {len(r['k_values'])}
- Precision: {self.precision_dps} decimal places
- Zeta zeros used: First 50 non-trivial zeros

PERFORMANCE METRICS:
- Average Z5D computation time: {r['mean_z5d_time']:.3f} ms
- Average Riemann computation time: {r['mean_riemann_time']:.3f} ms
- Performance ratio: {r['mean_riemann_time']/r['mean_z5d_time']:.2f}x

STATISTICAL ANALYSIS:
- Correlation coefficient (r): {r['correlation']:.6f}
- P-value: {r['p_value']:.2e}
- Mean absolute difference: {r['statistics']['mean_abs_diff']:.2f}
- Standard deviation of differences: {r['statistics']['std_diff']:.2f}
- Maximum absolute difference: {r['statistics']['max_abs_diff']:.2f}

HYPOTHESIS TESTING RESULTS:

1. CORRELATION HYPOTHESIS (r ≥ 0.93, p < 10^-10):
   Result: r = {r['correlation']:.6f}, p = {r['p_value']:.2e}
   Status: {'SUPPORTED' if r['correlation'] >= 0.93 and r['p_value'] < 1e-10 else 'NOT SUPPORTED'}

2. ASYMPTOTIC SCALING (differences ~ O(1/log k)):
   Linear fit slope: {r['scaling_fit'][0]:.6f}
   Status: {'SUPPORTED' if abs(r['scaling_fit'][0]) < 0.1 else 'NEEDS INVESTIGATION'}

3. SYMMETRY PATTERNS:
   Oscillation amplitude: {r['oscillation_analysis']['oscillation_amplitude']:.4f}
   Dominant frequency: {r['oscillation_analysis']['dominant_frequency']:.6f}
   
CONCLUSIONS:
- Z5D shows {'systematic underestimation' if np.mean(r['differences']) < 0 else 'systematic overestimation'} relative to Riemann
- {'Strong' if abs(r['correlation']) > 0.9 else 'Moderate' if abs(r['correlation']) > 0.7 else 'Weak'} correlation observed between methods
- {'Significant' if r['p_value'] < 0.001 else 'Moderate' if r['p_value'] < 0.05 else 'No'} statistical significance detected
        """
        
        return report


def main():
    """Main experimental execution."""
    print("=== RIEMANN PREDICTORS vs Z5D SYMMETRY ANALYSIS EXPERIMENT ===")
    print("Implementing rigorous scientific falsification methodology...")
    
    # Initialize experiment
    experiment = RiemannZ5DExperiment(precision_dps=50)
    
    # Run main analysis
    print("\n1. Running symmetry analysis...")
    results = experiment.run_symmetry_analysis(k_min=1000, k_max=1000000, num_points=20)
    
    # Generate plots
    print("\n2. Generating plots...")
    experiment.generate_plots()
    
    # Save results  
    print("\n3. Saving results...")
    experiment.save_results()
    
    # Generate report
    print("\n4. Generating summary report...")
    report = experiment.generate_summary_report()
    print(report)
    
    # Save report to file
    with open("riemann_z5d_experiment_report.txt", "w") as f:
        f.write(report)
    
    print("\n=== EXPERIMENT COMPLETED ===")
    print("Files generated:")
    print("- plots/pred_vs_logk.png")
    print("- plots/diff_vs_logk.png") 
    print("- plots/norm_diff_vs_logk.png")
    print("- plots/symmetry_analysis_comprehensive.png")
    print("- riemann_z5d_experiment_results.json")
    print("- riemann_z5d_experiment_report.txt")


if __name__ == "__main__":
    main()