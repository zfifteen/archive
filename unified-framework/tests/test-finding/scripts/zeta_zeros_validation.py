#!/usr/bin/env python3
"""
Riemann Zeta Zeros Validation with Unfolding Transformation and GUE Analysis

This script implements comprehensive validation of Riemann zeta zeros using:
1. High-precision computation of 1000 zeta zeros with mpmath (dps=50)
2. Unfolding transformation: tilde_t = t / (2π log(t / (2π e)))
3. Spacing statistics comparison to GUE (Gaussian Unitary Ensemble) predictions
4. Statistical analysis and visualization

Methodology:
- Computes first 1000 non-trivial Riemann zeta zeros
- Applies theoretical unfolding transformation from Random Matrix Theory
- Analyzes nearest neighbor spacing statistics
- Compares to Wigner surmise and GUE predictions
- Generates comprehensive statistical report

Author: Z Framework Validation System
"""

import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environment
import matplotlib.pyplot as plt
import mpmath as mp
from scipy import stats
import seaborn as sns
from pathlib import Path

# Set high precision for mathematical computations
mp.mp.dps = 50

# Mathematical constants with high precision
PI = mp.pi
E = mp.e
TWO_PI = 2 * PI
TWO_PI_E = TWO_PI * E

class ZetaZerosValidator:
    """
    High-precision Riemann zeta zeros validator with unfolding transformation and GUE analysis.
    """
    
    def __init__(self, num_zeros=1000, output_dir="validation_output"):
        self.num_zeros = num_zeros
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.zeros = []
        self.unfolded_zeros = []
        self.spacings = []
        
        # Results
        self.results = {}
        
    def compute_zeta_zeros(self):
        """
        Compute the first num_zeros Riemann zeta zeros using mpmath with high precision.
        """
        print(f"Computing {self.num_zeros} Riemann zeta zeros with {mp.mp.dps} decimal precision...")
        start_time = time.time()
        
        self.zeros = []
        for k in range(1, self.num_zeros + 1):
            if k % 100 == 0:
                elapsed = time.time() - start_time
                print(f"Computed {k}/{self.num_zeros} zeros (elapsed: {elapsed:.1f}s)")
            
            zero = mp.zetazero(k)
            imag_part = mp.im(zero)
            self.zeros.append(float(imag_part))
        
        elapsed = time.time() - start_time
        print(f"Completed computation of {len(self.zeros)} zeros in {elapsed:.2f} seconds")
        
        # Save raw zeros
        zeros_df = pd.DataFrame({
            'index': range(1, len(self.zeros) + 1),
            'imaginary_part': self.zeros
        })
        zeros_file = self.output_dir / "riemann_zeta_zeros_1000.csv"
        zeros_df.to_csv(zeros_file, index=False)
        print(f"Raw zeros saved to: {zeros_file}")
        
        return self.zeros
    
    def apply_unfolding_transformation(self):
        """
        Apply the unfolding transformation: tilde_t = t / (2π log(t / (2π e)))
        
        This transformation is used in Random Matrix Theory to "unfold" the spectrum
        so that the average spacing becomes unity, allowing for universal statistical analysis.
        
        Note: The transformation is only valid for t > 2πe ≈ 17.08, so we exclude smaller zeros.
        """
        print("Applying unfolding transformation...")
        
        # Filter out zeros that are too small for the transformation
        threshold = float(TWO_PI_E)
        valid_zeros = [t for t in self.zeros if t > threshold]
        excluded_count = len(self.zeros) - len(valid_zeros)
        
        if excluded_count > 0:
            print(f"Excluding {excluded_count} zeros below threshold t > {threshold:.3f}")
        
        self.unfolded_zeros = []
        self.valid_original_zeros = valid_zeros  # Store for reference
        
        for t in valid_zeros:
            # Convert to high precision for computation
            t_mp = mp.mpf(t)
            
            # Compute log(t / (2π e))
            log_term = mp.log(t_mp / TWO_PI_E)
            
            # Apply unfolding: tilde_t = t / (2π log(t / (2π e)))
            unfolded_t = t_mp / (TWO_PI * log_term)
            
            self.unfolded_zeros.append(float(unfolded_t))
        
        print(f"Applied unfolding transformation to {len(self.unfolded_zeros)} valid zeros")
        
        # Save unfolded zeros
        unfolded_df = pd.DataFrame({
            'index': range(1, len(self.unfolded_zeros) + 1),
            'original': self.valid_original_zeros,
            'unfolded': self.unfolded_zeros
        })
        unfolded_file = self.output_dir / "unfolded_zeta_zeros.csv"
        unfolded_df.to_csv(unfolded_file, index=False)
        print(f"Unfolded zeros saved to: {unfolded_file}")
        
        return self.unfolded_zeros
    
    def compute_spacings(self):
        """
        Compute nearest neighbor spacings from unfolded zeros.
        """
        print("Computing nearest neighbor spacings...")
        
        # Sort unfolded zeros to ensure proper ordering
        sorted_unfolded = sorted(self.unfolded_zeros)
        
        # Compute spacings: s_i = x_{i+1} - x_i
        self.spacings = []
        for i in range(len(sorted_unfolded) - 1):
            spacing = sorted_unfolded[i + 1] - sorted_unfolded[i]
            self.spacings.append(spacing)
        
        print(f"Computed {len(self.spacings)} spacings")
        
        # Save spacings
        spacings_df = pd.DataFrame({
            'index': range(1, len(self.spacings) + 1),
            'spacing': self.spacings
        })
        spacings_file = self.output_dir / "spacing_statistics.csv"
        spacings_df.to_csv(spacings_file, index=False)
        print(f"Spacings saved to: {spacings_file}")
        
        return self.spacings
    
    def wigner_surmise(self, s):
        """
        Wigner surmise for GUE spacing distribution: P(s) = (π/2) * s * exp(-πs²/4)
        """
        return (np.pi / 2) * s * np.exp(-np.pi * s**2 / 4)
    
    def analyze_gue_statistics(self):
        """
        Analyze spacing statistics and compare to GUE predictions.
        """
        print("Analyzing GUE spacing statistics...")
        
        spacings_array = np.array(self.spacings)
        
        # Basic statistics
        mean_spacing = np.mean(spacings_array)
        std_spacing = np.std(spacings_array)
        min_spacing = np.min(spacings_array)
        max_spacing = np.max(spacings_array)
        
        # Normalize spacings to have unit mean (standard procedure)
        normalized_spacings = spacings_array / mean_spacing
        
        # Statistics for normalized spacings
        normalized_mean = np.mean(normalized_spacings)
        normalized_std = np.std(normalized_spacings)
        
        # Theoretical GUE predictions
        gue_mean = 1.0  # By construction after normalization
        gue_std = np.sqrt(2 - np.pi/2)  # Theoretical GUE standard deviation ≈ 0.5227
        
        # Store results
        self.results = {
            'total_zeros_computed': self.num_zeros,
            'excluded_zeros': self.num_zeros - len(self.valid_original_zeros) if hasattr(self, 'valid_original_zeros') else 0,
            'valid_zeros_for_analysis': len(self.valid_original_zeros) if hasattr(self, 'valid_original_zeros') else len(self.zeros),
            'total_spacings': len(self.spacings),
            'exclusion_threshold': float(TWO_PI_E),
            'raw_spacing_mean': mean_spacing,
            'raw_spacing_std': std_spacing,
            'raw_spacing_min': min_spacing,
            'raw_spacing_max': max_spacing,
            'normalized_spacing_mean': normalized_mean,
            'normalized_spacing_std': normalized_std,
            'gue_theoretical_mean': gue_mean,
            'gue_theoretical_std': gue_std,
            'std_deviation_from_gue': abs(normalized_std - gue_std),
            'std_relative_error': abs(normalized_std - gue_std) / gue_std
        }
        
        print(f"Mean spacing (raw): {mean_spacing:.6f}")
        print(f"Std spacing (raw): {std_spacing:.6f}")
        print(f"Mean spacing (normalized): {normalized_mean:.6f}")
        print(f"Std spacing (normalized): {normalized_std:.6f}")
        print(f"GUE theoretical std: {gue_std:.6f}")
        print(f"Relative error from GUE: {self.results['std_relative_error']:.4f}")
        
        return normalized_spacings
    
    def generate_visualizations(self):
        """
        Generate comprehensive visualizations of the analysis.
        """
        print("Generating visualizations...")
        
        # Ensure we have the data
        if not self.spacings:
            raise ValueError("No spacing data available. Run compute_spacings first.")
        
        spacings_array = np.array(self.spacings)
        normalized_spacings = spacings_array / np.mean(spacings_array)
        
        # Set up the plot style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create a comprehensive figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Riemann Zeta Zeros: Unfolding Transformation and GUE Analysis', fontsize=16)
        
        # 1. Original zeros plot
        zeros_to_plot = self.valid_original_zeros if hasattr(self, 'valid_original_zeros') else self.zeros
        axes[0, 0].plot(range(1, len(zeros_to_plot) + 1), zeros_to_plot, 'b-', alpha=0.7, linewidth=0.8)
        axes[0, 0].set_title(f'Original Riemann Zeta Zeros (Valid: {len(zeros_to_plot)})')
        axes[0, 0].set_xlabel('Zero Index')
        axes[0, 0].set_ylabel('Imaginary Part')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Unfolded zeros plot
        axes[0, 1].plot(range(1, len(self.unfolded_zeros) + 1), self.unfolded_zeros, 'g-', alpha=0.7, linewidth=0.8)
        axes[0, 1].set_title('Unfolded Zeta Zeros')
        axes[0, 1].set_xlabel('Zero Index')
        axes[0, 1].set_ylabel('Unfolded Value')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Spacing distribution histogram
        axes[0, 2].hist(normalized_spacings, bins=50, density=True, alpha=0.7, color='skyblue', label='Data')
        
        # Overlay Wigner surmise
        s_range = np.linspace(0, 4, 1000)
        wigner_values = self.wigner_surmise(s_range)
        axes[0, 2].plot(s_range, wigner_values, 'r-', linewidth=2, label='Wigner Surmise (GUE)')
        
        axes[0, 2].set_title('Spacing Distribution vs GUE')
        axes[0, 2].set_xlabel('Normalized Spacing')
        axes[0, 2].set_ylabel('Probability Density')
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Cumulative distribution comparison
        sorted_spacings = np.sort(normalized_spacings)
        empirical_cdf = np.arange(1, len(sorted_spacings) + 1) / len(sorted_spacings)
        
        axes[1, 0].plot(sorted_spacings, empirical_cdf, 'b-', linewidth=2, label='Empirical CDF')
        
        # Theoretical GUE CDF (integral of Wigner surmise)
        s_fine = np.linspace(0, np.max(sorted_spacings), 1000)
        theoretical_cdf = []
        for s in s_fine:
            # Numerical integration of Wigner surmise
            s_int = np.linspace(0, s, 1000)
            if len(s_int) > 1:
                cdf_val = np.trapz(self.wigner_surmise(s_int), s_int)
            else:
                cdf_val = 0
            theoretical_cdf.append(cdf_val)
        
        axes[1, 0].plot(s_fine, theoretical_cdf, 'r--', linewidth=2, label='GUE Theory')
        axes[1, 0].set_title('Cumulative Distribution Comparison')
        axes[1, 0].set_xlabel('Normalized Spacing')
        axes[1, 0].set_ylabel('Cumulative Probability')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 5. Q-Q plot against GUE
        # Generate theoretical GUE samples for comparison
        np.random.seed(42)  # For reproducibility
        n_samples = len(normalized_spacings)
        gue_samples = []
        for _ in range(n_samples):
            # Inverse transform sampling for Wigner distribution
            u = np.random.random()
            # Approximate inverse (could be improved with numerical inversion)
            s_approx = np.sqrt(-4 * np.log(1 - u) / np.pi)
            gue_samples.append(s_approx)
        
        gue_samples = np.array(gue_samples)
        stats.probplot(normalized_spacings, dist=stats.norm, plot=None)
        
        # Simple Q-Q plot
        sorted_data = np.sort(normalized_spacings)
        sorted_gue = np.sort(gue_samples)
        axes[1, 1].scatter(sorted_gue, sorted_data, alpha=0.6, s=20)
        
        # Perfect correlation line
        min_val = min(np.min(sorted_gue), np.min(sorted_data))
        max_val = max(np.max(sorted_gue), np.max(sorted_data))
        axes[1, 1].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
        
        axes[1, 1].set_title('Q-Q Plot: Data vs GUE Theory')
        axes[1, 1].set_xlabel('Theoretical GUE Quantiles')
        axes[1, 1].set_ylabel('Empirical Quantiles')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Statistics summary
        axes[1, 2].axis('off')
        stats_text = f"""
Statistical Summary:

Total Zeros Computed: {self.results['total_zeros_computed']:,}
Excluded (t < {self.results['exclusion_threshold']:.2f}): {self.results['excluded_zeros']}
Valid for Analysis: {self.results['valid_zeros_for_analysis']:,}
Total Spacings: {self.results['total_spacings']:,}

Raw Spacings:
  Mean: {self.results['raw_spacing_mean']:.6f}
  Std: {self.results['raw_spacing_std']:.6f}
  Range: [{self.results['raw_spacing_min']:.4f}, {self.results['raw_spacing_max']:.4f}]

Normalized Spacings:
  Mean: {self.results['normalized_spacing_mean']:.6f}
  Std: {self.results['normalized_spacing_std']:.6f}

GUE Comparison:
  Theoretical Std: {self.results['gue_theoretical_std']:.6f}
  Deviation: {self.results['std_deviation_from_gue']:.6f}
  Relative Error: {self.results['std_relative_error']:.4f}

Precision: {mp.mp.dps} decimal places
        """
        
        axes[1, 2].text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                        verticalalignment='center', transform=axes[1, 2].transAxes,
                        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        plt.tight_layout()
        
        # Save the visualization
        viz_file = self.output_dir / "zeta_zeros_analysis.png"
        plt.savefig(viz_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {viz_file}")
        
        plt.show()  # Note: this won't display in headless environment but won't cause errors
        
        return fig
    
    def save_results(self):
        """
        Save comprehensive results to JSON and text files.
        """
        import json
        
        # Save results as JSON
        results_file = self.output_dir / "validation_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=4)
        
        # Save detailed methodology and results as text
        methodology_file = self.output_dir / "methodology_and_results.txt"
        with open(methodology_file, 'w') as f:
            f.write("Riemann Zeta Zeros Validation: Methodology and Results\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("METHODOLOGY:\n")
            f.write("-" * 12 + "\n")
            f.write(f"1. High-precision computation of {self.num_zeros} Riemann zeta zeros\n")
            f.write(f"   - Used mpmath library with {mp.mp.dps} decimal precision\n")
            f.write("   - Computed imaginary parts of non-trivial zeros\n\n")
            
            f.write("2. Unfolding transformation applied:\n")
            f.write("   - Formula: tilde_t = t / (2π log(t / (2π e)))\n")
            f.write("   - Purpose: Normalize average spacing to unity for universal analysis\n\n")
            
            f.write("3. Spacing statistics analysis:\n")
            f.write("   - Computed nearest neighbor spacings\n")
            f.write("   - Normalized to unit mean\n")
            f.write("   - Compared to GUE (Gaussian Unitary Ensemble) predictions\n\n")
            
            f.write("RESULTS:\n")
            f.write("-" * 8 + "\n")
            for key, value in self.results.items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.6f}\n")
                else:
                    f.write(f"{key}: {value}\n")
            
            f.write(f"\nFILES GENERATED:\n")
            f.write("-" * 16 + "\n")
            f.write(f"- Raw zeros: riemann_zeta_zeros_1000.csv\n")
            f.write(f"- Unfolded zeros: unfolded_zeta_zeros.csv\n")
            f.write(f"- Spacings: spacing_statistics.csv\n")
            f.write(f"- Results: validation_results.json\n")
            f.write(f"- Visualization: zeta_zeros_analysis.png\n")
            f.write(f"- This report: methodology_and_results.txt\n")
        
        print(f"Results saved to: {results_file}")
        print(f"Methodology report saved to: {methodology_file}")
    
    def run_full_validation(self):
        """
        Run the complete validation pipeline.
        """
        print("Starting Riemann Zeta Zeros Validation Pipeline")
        print("=" * 50)
        
        try:
            # Step 1: Compute zeros
            self.compute_zeta_zeros()
            
            # Step 2: Apply unfolding
            self.apply_unfolding_transformation()
            
            # Step 3: Compute spacings
            self.compute_spacings()
            
            # Step 4: GUE analysis
            normalized_spacings = self.analyze_gue_statistics()
            
            # Step 5: Generate visualizations
            self.generate_visualizations()
            
            # Step 6: Save results
            self.save_results()
            
            print("\n" + "=" * 50)
            print("Validation pipeline completed successfully!")
            print(f"Results saved in: {self.output_dir}")
            
            return True
            
        except Exception as e:
            print(f"Error in validation pipeline: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """
    Main function to run the zeta zeros validation.
    """
    # Create validator instance
    validator = ZetaZerosValidator(num_zeros=1000, output_dir="zeta_validation_results")
    
    # Run full validation
    success = validator.run_full_validation()
    
    if success:
        print("\nValidation Summary:")
        print("-" * 18)
        print(f"✓ Computed {validator.results['total_zeros_computed']} zeta zeros")
        print(f"✓ Applied unfolding transformation ({validator.results['valid_zeros_for_analysis']} valid)")
        print(f"✓ Analyzed {validator.results['total_spacings']} spacings")
        print(f"✓ GUE relative error: {validator.results['std_relative_error']:.4f}")
        print(f"✓ All results saved to: {validator.output_dir}")
    else:
        print("\nValidation failed. Check error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())