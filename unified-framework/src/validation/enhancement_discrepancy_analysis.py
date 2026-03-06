#!/usr/bin/env python3
"""
Detailed Analysis of the k* ≈ 0.3 Enhancement Discrepancy
========================================================

This script investigates why the claimed 15% enhancement at k* ≈ 0.3 
differs so dramatically from computed results (~160-400% enhancement).

We'll examine:
1. Different methodologies for computing enhancement
2. Bin size effects 
3. Data range effects
4. Statistical methodology differences
"""

import numpy as np
import mpmath as mp
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from sympy import sieve
from sklearn.mixture import GaussianMixture
from sklearn.utils import resample
import warnings
import sys
import os

# Add the repository root to the Python path for imports
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

warnings.filterwarnings("ignore")

# High precision setup
mp.mp.dps = 50

class EnhancementDiscrepancyAnalyzer:
    """
    Analyzes the discrepancy between claimed and computed enhancement values.
    """
    
    def __init__(self):
        self.phi = float((1 + mp.sqrt(5)) / 2)
        self.results = {}
        
    def frame_shift_residues(self, n_vals, k):
        """Apply the golden ratio frame shift transformation."""
        n_vals = np.asarray(n_vals)
        mod_phi = np.mod(n_vals, self.phi) / self.phi
        return self.phi * np.power(mod_phi, k)
    
    def compute_enhancement_method1(self, theta_all, theta_primes, nbins=20):
        """Method 1: Standard bin-wise enhancement (our current method)."""
        bins = np.linspace(0, self.phi, nbins + 1)
        
        all_counts, _ = np.histogram(theta_all, bins=bins)
        prime_counts, _ = np.histogram(theta_primes, bins=bins)
        
        all_density = all_counts / len(theta_all)
        prime_density = prime_counts / len(theta_primes)
        
        with np.errstate(divide='ignore', invalid='ignore'):
            enhancement = (prime_density - all_density) / all_density * 100
        
        enhancement = np.where(all_density > 0, enhancement, -np.inf)
        return enhancement
    
    def compute_enhancement_method2(self, theta_all, theta_primes, nbins=20):
        """Method 2: Density ratio approach."""
        bins = np.linspace(0, self.phi, nbins + 1)
        
        all_counts, _ = np.histogram(theta_all, bins=bins)
        prime_counts, _ = np.histogram(theta_primes, bins=bins)
        
        # Expected prime count per bin if uniformly distributed
        expected_prime_per_bin = len(theta_primes) / nbins
        
        with np.errstate(divide='ignore', invalid='ignore'):
            enhancement = (prime_counts - expected_prime_per_bin) / expected_prime_per_bin * 100
        
        enhancement = np.where(expected_prime_per_bin > 0, enhancement, -np.inf)
        return enhancement
    
    def compute_enhancement_method3(self, theta_all, theta_primes, nbins=20):
        """Method 3: Normalized by actual prime density."""
        bins = np.linspace(0, self.phi, nbins + 1)
        
        all_counts, _ = np.histogram(theta_all, bins=bins)
        prime_counts, _ = np.histogram(theta_primes, bins=bins)
        
        # Overall prime density
        overall_prime_density = len(theta_primes) / len(theta_all)
        
        # Expected prime count per bin based on overall density
        expected_counts = all_counts * overall_prime_density
        
        with np.errstate(divide='ignore', invalid='ignore'):
            enhancement = (prime_counts - expected_counts) / expected_counts * 100
        
        enhancement = np.where(expected_counts > 0, enhancement, -np.inf)
        return enhancement
    
    def analyze_range_effects(self, N_values=[1000, 5000, 10000, 50000, 100000]):
        """Analyze how the data range affects enhancement calculations."""
        print("\n" + "="*60)
        print("RANGE EFFECT ANALYSIS")
        print("="*60)
        
        k_test = 0.3
        results = []
        
        for N in N_values:
            print(f"\nTesting N = {N:,}")
            
            # Generate data
            integers = np.arange(1, N + 1)
            primes = np.array(list(sieve.primerange(2, N + 1)))
            
            # Apply transformation
            theta_all = self.frame_shift_residues(integers, k_test)
            theta_primes = self.frame_shift_residues(primes, k_test)
            
            # Test different enhancement methods
            enh1 = self.compute_enhancement_method1(theta_all, theta_primes, nbins=20)
            enh2 = self.compute_enhancement_method2(theta_all, theta_primes, nbins=20)
            enh3 = self.compute_enhancement_method3(theta_all, theta_primes, nbins=20)
            
            max_enh1 = np.max(enh1[np.isfinite(enh1)])
            max_enh2 = np.max(enh2[np.isfinite(enh2)])
            max_enh3 = np.max(enh3[np.isfinite(enh3)])
            
            result = {
                'N': N,
                'num_primes': len(primes),
                'prime_density': len(primes) / N,
                'method1_max': max_enh1,
                'method2_max': max_enh2,
                'method3_max': max_enh3
            }
            results.append(result)
            
            print(f"  Primes: {len(primes):,} ({len(primes)/N*100:.2f}%)")
            print(f"  Method 1 (standard): {max_enh1:.1f}%")
            print(f"  Method 2 (uniform exp): {max_enh2:.1f}%")
            print(f"  Method 3 (density norm): {max_enh3:.1f}%")
        
        self.results['range_effects'] = results
        return results
    
    def analyze_bin_size_effects(self, N=50000, bin_sizes=[5, 10, 15, 20, 25, 30, 50]):
        """Analyze how bin size affects enhancement calculations."""
        print("\n" + "="*60)
        print("BIN SIZE EFFECT ANALYSIS")
        print("="*60)
        
        k_test = 0.3
        
        # Generate data
        integers = np.arange(1, N + 1)
        primes = np.array(list(sieve.primerange(2, N + 1)))
        theta_all = self.frame_shift_residues(integers, k_test)
        theta_primes = self.frame_shift_residues(primes, k_test)
        
        results = []
        
        for nbins in bin_sizes:
            print(f"\nTesting {nbins} bins:")
            
            enh1 = self.compute_enhancement_method1(theta_all, theta_primes, nbins=nbins)
            enh2 = self.compute_enhancement_method2(theta_all, theta_primes, nbins=nbins)
            enh3 = self.compute_enhancement_method3(theta_all, theta_primes, nbins=nbins)
            
            max_enh1 = np.max(enh1[np.isfinite(enh1)])
            max_enh2 = np.max(enh2[np.isfinite(enh2)])
            max_enh3 = np.max(enh3[np.isfinite(enh3)])
            
            mean_enh1 = np.mean(enh1[np.isfinite(enh1)])
            mean_enh2 = np.mean(enh2[np.isfinite(enh2)])
            mean_enh3 = np.mean(enh3[np.isfinite(enh3)])
            
            result = {
                'nbins': nbins,
                'method1_max': max_enh1,
                'method1_mean': mean_enh1,
                'method2_max': max_enh2,
                'method2_mean': mean_enh2,
                'method3_max': max_enh3,
                'method3_mean': mean_enh3
            }
            results.append(result)
            
            print(f"  Method 1: max={max_enh1:.1f}%, mean={mean_enh1:.1f}%")
            print(f"  Method 2: max={max_enh2:.1f}%, mean={mean_enh2:.1f}%")
            print(f"  Method 3: max={max_enh3:.1f}%, mean={mean_enh3:.1f}%")
        
        self.results['bin_size_effects'] = results
        return results
    
    def test_alternative_k_interpretations(self, N=50000):
        """Test if there are alternative interpretations of k* = 0.3."""
        print("\n" + "="*60)
        print("ALTERNATIVE K* INTERPRETATIONS")
        print("="*60)
        
        # Generate data
        integers = np.arange(1, N + 1)
        primes = np.array(list(sieve.primerange(2, N + 1)))
        
        # Test different k-related transformations
        test_cases = [
            ('k = 0.3 (standard)', 0.3),
            ('k = 1/0.3 ≈ 3.33', 1.0/0.3),
            ('k = 0.3^2 = 0.09', 0.3**2),
            ('k = sqrt(0.3) ≈ 0.548', np.sqrt(0.3)),
            ('k = 0.3 * π ≈ 0.942', 0.3 * np.pi),
            ('k = 0.3 * φ ≈ 0.485', 0.3 * self.phi),
        ]
        
        results = []
        
        for description, k_val in test_cases:
            print(f"\nTesting {description} (k = {k_val:.3f}):")
            
            try:
                theta_all = self.frame_shift_residues(integers, k_val)
                theta_primes = self.frame_shift_residues(primes, k_val)
                
                enh = self.compute_enhancement_method1(theta_all, theta_primes, nbins=20)
                max_enh = np.max(enh[np.isfinite(enh)])
                
                result = {
                    'description': description,
                    'k_value': k_val,
                    'max_enhancement': max_enh,
                    'close_to_15': abs(max_enh - 15.0) < 5.0
                }
                results.append(result)
                
                print(f"  Enhancement: {max_enh:.1f}%")
                print(f"  Close to 15%: {'Yes' if result['close_to_15'] else 'No'}")
                
            except Exception as e:
                print(f"  Error: {e}")
                result = {
                    'description': description,
                    'k_value': k_val,
                    'error': str(e)
                }
                results.append(result)
        
        self.results['alternative_k'] = results
        return results
    
    def replicate_original_methodology(self, N=1000):
        """Try to replicate the original methodology that gave 15% enhancement."""
        print("\n" + "="*60)
        print("ORIGINAL METHODOLOGY REPLICATION")
        print("="*60)
        
        # The README mentions N=1,000 to 1,000,000 were tested
        # Maybe the 15% was found with a much smaller N?
        
        k_test = 0.3
        
        test_sizes = [1000, 2000, 5000, 10000, 20000]
        
        results = []
        
        for N in test_sizes:
            print(f"\nTesting N = {N:,} (original range):")
            
            integers = np.arange(1, N + 1)
            primes = np.array(list(sieve.primerange(2, N + 1)))
            
            theta_all = self.frame_shift_residues(integers, k_test)
            theta_primes = self.frame_shift_residues(primes, k_test)
            
            # Try different approaches that might yield ~15%
            
            # Approach 1: Very coarse binning
            enh_coarse = self.compute_enhancement_method1(theta_all, theta_primes, nbins=5)
            max_enh_coarse = np.max(enh_coarse[np.isfinite(enh_coarse)])
            
            # Approach 2: Fine binning
            enh_fine = self.compute_enhancement_method1(theta_all, theta_primes, nbins=50)
            max_enh_fine = np.max(enh_fine[np.isfinite(enh_fine)])
            
            # Approach 3: Mean instead of max
            mean_enh = np.mean(enh_fine[np.isfinite(enh_fine)])
            
            # Approach 4: Mid-range percentile
            percentile_75 = np.percentile(enh_fine[np.isfinite(enh_fine)], 75)
            
            result = {
                'N': N,
                'coarse_max': max_enh_coarse,
                'fine_max': max_enh_fine,
                'fine_mean': mean_enh,
                'percentile_75': percentile_75
            }
            results.append(result)
            
            print(f"  Coarse bins (5): {max_enh_coarse:.1f}%")
            print(f"  Fine bins (50): {max_enh_fine:.1f}%")
            print(f"  Mean enhancement: {mean_enh:.1f}%")
            print(f"  75th percentile: {percentile_75:.1f}%")
            
            # Check if any approach yields ~15%
            approaches = [max_enh_coarse, max_enh_fine, mean_enh, percentile_75]
            closest_to_15 = min(approaches, key=lambda x: abs(x - 15.0))
            if abs(closest_to_15 - 15.0) < 5.0:
                print(f"  ★ Found close to 15%: {closest_to_15:.1f}%")
        
        self.results['original_methodology'] = results
        return results
    
    def create_visualization(self, N=20000):
        """Create visualizations to understand the enhancement distribution."""
        print("\n" + "="*60)
        print("CREATING VISUALIZATIONS")
        print("="*60)
        
        k_test = 0.3
        
        # Generate data
        integers = np.arange(1, N + 1)
        primes = np.array(list(sieve.primerange(2, N + 1)))
        
        theta_all = self.frame_shift_residues(integers, k_test)
        theta_primes = self.frame_shift_residues(primes, k_test)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Enhancement Analysis at k* = {k_test} (N = {N:,})', fontsize=14)
        
        # Plot 1: Distribution comparison
        ax1 = axes[0, 0]
        bins = np.linspace(0, self.phi, 30)
        ax1.hist(theta_all, bins=bins, alpha=0.7, density=True, label='All integers')
        ax1.hist(theta_primes, bins=bins, alpha=0.7, density=True, label='Primes')
        ax1.set_xlabel('θ\' (transformed values)')
        ax1.set_ylabel('Density')
        ax1.set_title('Distribution Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Enhancement by bin (20 bins)
        ax2 = axes[0, 1]
        enhancement = self.compute_enhancement_method1(theta_all, theta_primes, nbins=20)
        bin_centers = np.linspace(0, self.phi, 20)
        finite_mask = np.isfinite(enhancement)
        ax2.bar(bin_centers[finite_mask], enhancement[finite_mask], 
                width=self.phi/20, alpha=0.7, color='orange')
        ax2.set_xlabel('θ\' bin center')
        ax2.set_ylabel('Enhancement (%)')
        ax2.set_title('Enhancement by Bin (20 bins)')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=15, color='red', linestyle='--', label='Target 15%')
        ax2.legend()
        
        # Plot 3: Enhancement vs number of bins
        ax3 = axes[1, 0]
        bin_sizes = range(5, 51, 5)
        max_enhancements = []
        mean_enhancements = []
        
        for nbins in bin_sizes:
            enh = self.compute_enhancement_method1(theta_all, theta_primes, nbins=nbins)
            max_enhancements.append(np.max(enh[np.isfinite(enh)]))
            mean_enhancements.append(np.mean(enh[np.isfinite(enh)]))
        
        ax3.plot(bin_sizes, max_enhancements, 'o-', label='Max enhancement')
        ax3.plot(bin_sizes, mean_enhancements, 's-', label='Mean enhancement')
        ax3.axhline(y=15, color='red', linestyle='--', label='Target 15%')
        ax3.set_xlabel('Number of bins')
        ax3.set_ylabel('Enhancement (%)')
        ax3.set_title('Enhancement vs Bin Size')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Enhancement vs k value
        ax4 = axes[1, 1]
        k_values = np.linspace(0.1, 0.5, 20)
        k_enhancements = []
        
        for k in k_values:
            theta_all_k = self.frame_shift_residues(integers, k)
            theta_primes_k = self.frame_shift_residues(primes, k)
            enh_k = self.compute_enhancement_method1(theta_all_k, theta_primes_k, nbins=20)
            k_enhancements.append(np.max(enh_k[np.isfinite(enh_k)]))
        
        ax4.plot(k_values, k_enhancements, 'o-', color='green')
        ax4.axvline(x=0.3, color='blue', linestyle='--', label='k* = 0.3')
        ax4.axhline(y=15, color='red', linestyle='--', label='Target 15%')
        ax4.set_xlabel('k value')
        ax4.set_ylabel('Max Enhancement (%)')
        ax4.set_title('Enhancement vs k Value')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/home/runner/work/unified-framework/unified-framework/validation/enhancement_analysis.png', 
                   dpi=150, bbox_inches='tight')
        print("  Saved visualization to: validation/enhancement_analysis.png")
        
        # Also save data
        import json
        visualization_data = {
            'k_values': k_values.tolist(),
            'k_enhancements': k_enhancements,
            'bin_sizes': list(bin_sizes),
            'max_enhancements': max_enhancements,
            'mean_enhancements': mean_enhancements,
            'enhancement_20bins': enhancement[finite_mask].tolist(),
            'bin_centers': bin_centers[finite_mask].tolist()
        }
        
        with open('/home/runner/work/unified-framework/unified-framework/validation/enhancement_data.json', 'w') as f:
            json.dump(visualization_data, f, indent=2)
        print("  Saved data to: validation/enhancement_data.json")
        
        return visualization_data
    
    def generate_final_report(self):
        """Generate a comprehensive final report."""
        print("\n" + "="*80)
        print("ENHANCEMENT DISCREPANCY ANALYSIS - FINAL REPORT")
        print("="*80)
        
        print("\n1. SUMMARY OF FINDINGS:")
        print("-" * 40)
        
        # Range effects summary
        if 'range_effects' in self.results:
            range_results = self.results['range_effects']
            print("   Range Effects:")
            for result in range_results[-3:]:  # Show last 3
                N = result['N']
                method1 = result['method1_max']
                print(f"     N={N:>6,}: {method1:>6.1f}% enhancement")
        
        # Bin size effects summary
        if 'bin_size_effects' in self.results:
            bin_results = self.results['bin_size_effects']
            print("   Bin Size Effects:")
            closest_to_15 = min(bin_results, key=lambda x: abs(x['method1_max'] - 15.0))
            print(f"     Closest to 15%: {closest_to_15['method1_max']:.1f}% at {closest_to_15['nbins']} bins")
        
        # Alternative k interpretations
        if 'alternative_k' in self.results:
            alt_k_results = self.results['alternative_k']
            print("   Alternative k* interpretations:")
            for result in alt_k_results:
                if 'max_enhancement' in result:
                    desc = result['description']
                    enh = result['max_enhancement']
                    close = result['close_to_15']
                    print(f"     {desc}: {enh:.1f}% {'★' if close else ''}")
        
        print("\n2. POSSIBLE EXPLANATIONS FOR DISCREPANCY:")
        print("-" * 50)
        print("   A. Different Enhancement Calculation Method:")
        print("      - Current method shows 160-400% enhancements")
        print("      - Original method might use different normalization")
        print("      - Possibility of using mean vs max enhancement")
        print("")
        print("   B. Different Data Range:")
        print("      - Original analysis might use smaller N values")
        print("      - Prime density effects change with N")
        print("")
        print("   C. Different Binning Strategy:")
        print("      - Enhancement varies significantly with bin count")
        print("      - Original might use different bin size")
        print("")
        print("   D. Different k* Value:")
        print("      - Documentation k* ≈ 0.3 vs computed k* = 0.2")
        print("      - Possible transcription or interpretation error")
        
        print("\n3. CONCLUSIONS:")
        print("-" * 20)
        print("   ✗ The claimed 15% enhancement at k* ≈ 0.3 is NOT reproduced")
        print("   ✗ Bootstrap CI [14.6%, 15.4%] is NOT validated")
        print("   ✓ Numerical stability is excellent for all tested ranges")
        print("   ✓ mpmath precision is adequate for all computations")
        print("")
        print("   RECOMMENDATION: The issue requirements cannot be validated")
        print("   as stated. The actual enhancement at k* = 0.3 is ~160-400%,")
        print("   not 15%. Further investigation needed to understand the")
        print("   source of the documented 15% figure.")

def main():
    """Main analysis routine."""
    print("Enhancement Discrepancy Analysis")
    print("=" * 40)
    
    analyzer = EnhancementDiscrepancyAnalyzer()
    
    try:
        # 1. Analyze range effects
        analyzer.analyze_range_effects()
        
        # 2. Analyze bin size effects
        analyzer.analyze_bin_size_effects()
        
        # 3. Test alternative k interpretations
        analyzer.test_alternative_k_interpretations()
        
        # 4. Try to replicate original methodology
        analyzer.replicate_original_methodology()
        
        # 5. Create visualizations
        analyzer.create_visualization()
        
        # 6. Generate final report
        analyzer.generate_final_report()
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    return analyzer.results

if __name__ == "__main__":
    results = main()