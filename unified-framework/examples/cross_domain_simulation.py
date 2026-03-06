"""
Cross-Domain Simulation: Orbital Resonances vs. Primes
------------------------------------------------------

Validates analogies by correlating orbital ratios with prime gaps/zeta spacings.

Inputs:
- Solar ratios (10 hardcoded pairs)
- Primes to N=10^6; zeta zeros M=100

Methods:
1. Transform ratios r via θ'(r,0.3)
2. Compute sorted r with unfolded zeta δ_j and prime gaps g_i = p_{i+1}-p_i
3. Pearson r (sorted/unsorted); multimodal matches via GMM

Outputs:
- Table: Pair (orbital vs. zeta/prime) | Sorted r | p-value | κ_mean
- Overlap clusters

Success Criteria: Sorted r>0.78; κ_modes ≈0.3-1.5
"""

import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import sympy
import mpmath as mp
from core.axioms import theta_prime, curvature
from core.orbital import pairwise_ratios

# Set high precision
mp.mp.dps = 50

# Constants
PHI = float((1 + mp.sqrt(5)) / 2)
E_SQUARED = float(mp.e ** 2)

class CrossDomainSimulation:
    def __init__(self):
        """Initialize the cross-domain simulation with hardcoded solar ratios."""
        # Hardcoded 10 solar orbital ratio pairs (in days)
        self.orbital_periods = {
            "Mercury": 87.97,
            "Venus": 224.7, 
            "Earth": 365.26,
            "Mars": 686.98,
            "Jupiter": 4332.59,
            "Saturn": 10759.22,
            "Uranus": 30685.4,
            "Neptune": 60190.03,
            "Pluto": 90560.0,  # Added for more pairs
            "Ceres": 1681.6    # Added for more pairs
        }
        
        # Get the first 10 pairwise ratios
        self.ratio_pairs = pairwise_ratios(self.orbital_periods)[:10]
        self.ratio_labels = [pair[0] for pair in self.ratio_pairs]
        self.ratios = np.array([pair[1] for pair in self.ratio_pairs])
        
        print(f"Using {len(self.ratios)} orbital ratio pairs:")
        for i, (label, ratio) in enumerate(self.ratio_pairs):
            print(f"  {i+1}. {label}: {ratio:.3f}")
    
    def generate_primes(self, N=1000000):
        """Generate primes up to N and compute prime gaps."""
        print(f"\nGenerating primes up to N={N:,}...")
        self.primes = list(sympy.primerange(2, N))
        self.prime_gaps = np.array([self.primes[i+1] - self.primes[i] 
                                   for i in range(len(self.primes)-1)])
        print(f"Generated {len(self.primes):,} primes with {len(self.prime_gaps):,} gaps")
        return self.primes, self.prime_gaps
    
    def generate_zeta_zeros(self, M=100):
        """Generate M Riemann zeta zeros and compute spacings."""
        print(f"\nGenerating M={M} Riemann zeta zeros...")
        self.zeta_zeros = []
        for k in range(1, M+1):
            zero = mp.zetazero(k)
            self.zeta_zeros.append(float(zero.imag))
        
        # Compute unfolded zeta spacings δ_j
        self.zeta_spacings = np.array([self.zeta_zeros[i+1] - self.zeta_zeros[i] 
                                      for i in range(len(self.zeta_zeros)-1)])
        print(f"Generated {len(self.zeta_zeros)} zeta zeros with {len(self.zeta_spacings)} spacings")
        return self.zeta_zeros, self.zeta_spacings
    
    def transform_ratios(self, k=0.3):
        """Apply θ'(r,k) transformation to orbital ratios."""
        print(f"\nApplying θ'(r,{k}) transformation...")
        self.theta_transformed = np.array([theta_prime(r, k, PHI) for r in self.ratios])
        print(f"Transformed {len(self.theta_transformed)} ratios")
        return self.theta_transformed
    
    def compute_curvatures(self):
        """Compute curvature κ for transformed ratios."""
        print("\nComputing curvatures...")
        # Use the curvature function from core/orbital.py which takes just n
        from core.orbital import curvature as orbital_curvature
        
        # Scale the theta_transformed values to get meaningful integer inputs for curvature
        # Since theta values are often < 2, multiply by a scaling factor to get larger integers
        scale_factor = 100
        scaled_values = self.theta_transformed * scale_factor
        
        # Compute curvatures using the orbital curvature function
        self.curvatures = np.array([orbital_curvature(max(2, int(round(t)))) 
                                   for t in scaled_values])
        
        # Also compute curvatures for the original ratios for comparison
        self.ratio_curvatures = np.array([orbital_curvature(max(2, int(round(r * 10)))) 
                                         for r in self.ratios])
        
        print(f"Theta-based curvatures: mean={np.mean(self.curvatures):.3f}, range=[{np.min(self.curvatures):.3f}, {np.max(self.curvatures):.3f}]")
        print(f"Ratio-based curvatures: mean={np.mean(self.ratio_curvatures):.3f}, range=[{np.min(self.ratio_curvatures):.3f}, {np.max(self.ratio_curvatures):.3f}]")
        
        return self.curvatures
    
    def correlation_analysis(self):
        """Perform Pearson correlation analysis (sorted and unsorted)."""
        print("\nPerforming correlation analysis...")
        
        # Ensure equal lengths for comparison
        min_len = min(len(self.theta_transformed), len(self.prime_gaps), len(self.zeta_spacings))
        
        theta_subset = self.theta_transformed[:min_len]
        gaps_subset = self.prime_gaps[:min_len] 
        zeta_subset = self.zeta_spacings[:min_len]
        
        # Unsorted correlations
        r_theta_gaps_unsorted, p_theta_gaps_unsorted = pearsonr(theta_subset, gaps_subset)
        r_theta_zeta_unsorted, p_theta_zeta_unsorted = pearsonr(theta_subset, zeta_subset)
        
        # Sorted correlations (by magnitude)
        theta_sorted = np.sort(theta_subset)
        gaps_sorted = np.sort(gaps_subset)
        zeta_sorted = np.sort(zeta_subset)
        
        r_theta_gaps_sorted, p_theta_gaps_sorted = pearsonr(theta_sorted, gaps_sorted)
        r_theta_zeta_sorted, p_theta_zeta_sorted = pearsonr(theta_sorted, zeta_sorted)
        
        self.correlations = {
            'prime_gaps': {
                'unsorted_r': r_theta_gaps_unsorted,
                'unsorted_p': p_theta_gaps_unsorted,
                'sorted_r': r_theta_gaps_sorted,
                'sorted_p': p_theta_gaps_sorted
            },
            'zeta_spacings': {
                'unsorted_r': r_theta_zeta_unsorted,
                'unsorted_p': p_theta_zeta_unsorted,
                'sorted_r': r_theta_zeta_sorted,
                'sorted_p': p_theta_zeta_sorted
            }
        }
        
        return self.correlations
    
    def gmm_analysis(self, n_components=5):
        """Perform Gaussian Mixture Model analysis for multimodal matching."""
        print(f"\nPerforming GMM analysis with {n_components} components...")
        
        # Prepare data for GMM
        min_len = min(len(self.theta_transformed), len(self.prime_gaps), len(self.zeta_spacings))
        
        data_combined = np.column_stack([
            self.theta_transformed[:min_len],
            self.prime_gaps[:min_len],
            self.zeta_spacings[:min_len]
        ])
        
        # Standardize data
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_combined)
        
        # Fit GMM
        self.gmm = GaussianMixture(n_components=n_components, random_state=42)
        self.gmm.fit(data_scaled)
        
        # Get cluster assignments
        self.cluster_labels = self.gmm.predict(data_scaled)
        
        # Compute cluster statistics using both curvature types
        self.cluster_stats = {}
        for i in range(n_components):
            mask = self.cluster_labels == i
            if np.sum(mask) > 0:
                theta_curvs = self.curvatures[:min_len][mask] if len(self.curvatures) >= min_len else []
                ratio_curvs = self.ratio_curvatures[:min_len][mask] if len(self.ratio_curvatures) >= min_len else []
                
                self.cluster_stats[i] = {
                    'count': np.sum(mask),
                    'mean_kappa_theta': np.mean(theta_curvs) if len(theta_curvs) > 0 else 0,
                    'std_kappa_theta': np.std(theta_curvs) if len(theta_curvs) > 0 else 0,
                    'mean_kappa_ratio': np.mean(ratio_curvs) if len(ratio_curvs) > 0 else 0,
                    'std_kappa_ratio': np.std(ratio_curvs) if len(ratio_curvs) > 0 else 0,
                }
        
        print(f"GMM converged with {len(self.cluster_stats)} active clusters")
    def overlap_analysis(self):
        """Analyze overlap clusters between orbital, prime, and zeta domains."""
        print("\nPerforming overlap cluster analysis...")
        
        # Create feature vectors for each domain
        min_len = min(len(self.theta_transformed), len(self.prime_gaps), len(self.zeta_spacings))
        
        # Normalize features for fair comparison
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        
        # Orbital features (theta-transformed ratios)
        orbital_features = self.theta_transformed[:min_len].reshape(-1, 1)
        orbital_norm = scaler.fit_transform(orbital_features).flatten()
        
        # Prime gap features
        prime_features = self.prime_gaps[:min_len].reshape(-1, 1)
        prime_norm = scaler.fit_transform(prime_features).flatten()
        
        # Zeta spacing features  
        zeta_features = self.zeta_spacings[:min_len].reshape(-1, 1)
        zeta_norm = scaler.fit_transform(zeta_features).flatten()
        
        # Compute pairwise overlaps (correlation-based similarity)
        orbital_prime_overlap = np.corrcoef(orbital_norm, prime_norm)[0, 1]
        orbital_zeta_overlap = np.corrcoef(orbital_norm, zeta_norm)[0, 1]
        prime_zeta_overlap = np.corrcoef(prime_norm, zeta_norm)[0, 1]
        
        # Find common high-value regions (top quartile overlap)
        orbital_q75 = np.percentile(orbital_norm, 75)
        prime_q75 = np.percentile(prime_norm, 75)
        zeta_q75 = np.percentile(zeta_norm, 75)
        
        # Identify overlap regions
        orbital_high = orbital_norm >= orbital_q75
        prime_high = prime_norm >= prime_q75
        zeta_high = zeta_norm >= zeta_q75
        
        orbital_prime_common = np.sum(orbital_high & prime_high)
        orbital_zeta_common = np.sum(orbital_high & zeta_high)
        prime_zeta_common = np.sum(prime_high & zeta_high)
        all_three_common = np.sum(orbital_high & prime_high & zeta_high)
        
        self.overlap_results = {
            'correlations': {
                'orbital_prime': orbital_prime_overlap,
                'orbital_zeta': orbital_zeta_overlap,
                'prime_zeta': prime_zeta_overlap
            },
            'high_value_overlaps': {
                'orbital_prime': orbital_prime_common,
                'orbital_zeta': orbital_zeta_common,
                'prime_zeta': prime_zeta_common,
                'all_three': all_three_common,
                'total_points': min_len
            }
        }
        
        print(f"Overlap correlations:")
        print(f"  Orbital-Prime: {orbital_prime_overlap:.3f}")
        print(f"  Orbital-Zeta: {orbital_zeta_overlap:.3f}")
        print(f"  Prime-Zeta: {prime_zeta_overlap:.3f}")
        
        print(f"High-value region overlaps (top quartile):")
        print(f"  Orbital-Prime: {orbital_prime_common}/{min_len} points ({100*orbital_prime_common/min_len:.1f}%)")
        print(f"  Orbital-Zeta: {orbital_zeta_common}/{min_len} points ({100*orbital_zeta_common/min_len:.1f}%)")
        print(f"  Prime-Zeta: {prime_zeta_common}/{min_len} points ({100*prime_zeta_common/min_len:.1f}%)")
        print(f"  All three domains: {all_three_common}/{min_len} points ({100*all_three_common/min_len:.1f}%)")
        
        return self.overlap_results
    
    def generate_results_table(self):
        """Generate the required output table."""
        print("\nGenerating results table...")
        
        results = []
        
        # For each orbital pair, create entries for prime gaps and zeta spacings
        for i, (label, ratio) in enumerate(self.ratio_pairs):
            # Prime gaps entry
            prime_entry = {
                'Pair': f"{label} vs Prime Gaps",
                'Orbital_Ratio': ratio,
                'Theta_Transformed': self.theta_transformed[i] if i < len(self.theta_transformed) else np.nan,
                'Sorted_r': self.correlations['prime_gaps']['sorted_r'],
                'P_value': self.correlations['prime_gaps']['sorted_p'],
                'Kappa_mean': self.cluster_stats[0]['mean_kappa_ratio'] if 0 in self.cluster_stats else np.mean(self.ratio_curvatures),
                'Domain': 'Prime'
            }
            results.append(prime_entry)
            
            # Zeta spacings entry
            zeta_entry = {
                'Pair': f"{label} vs Zeta Spacings", 
                'Orbital_Ratio': ratio,
                'Theta_Transformed': self.theta_transformed[i] if i < len(self.theta_transformed) else np.nan,
                'Sorted_r': self.correlations['zeta_spacings']['sorted_r'],
                'P_value': self.correlations['zeta_spacings']['sorted_p'],
                'Kappa_mean': self.cluster_stats[0]['mean_kappa_ratio'] if 0 in self.cluster_stats else np.mean(self.ratio_curvatures),
                'Domain': 'Zeta'
            }
            results.append(zeta_entry)
        
        self.results_df = pd.DataFrame(results)
        return self.results_df
    
    def print_summary(self):
        """Print comprehensive simulation summary."""
        print("\n" + "="*80)
        print("CROSS-DOMAIN SIMULATION RESULTS")
        print("="*80)
        
        print(f"\nOrbital Ratios ({len(self.ratios)} pairs):")
        print(f"  Range: [{np.min(self.ratios):.3f}, {np.max(self.ratios):.3f}]")
        print(f"  Mean: {np.mean(self.ratios):.3f}")
        
        print(f"\nPrime Data:")
        print(f"  Primes generated: {len(self.primes):,}")
        print(f"  Prime gaps: {len(self.prime_gaps):,}")
        print(f"  Gap range: [{np.min(self.prime_gaps)}, {np.max(self.prime_gaps)}]")
        
        print(f"\nZeta Data:")
        print(f"  Zeta zeros: {len(self.zeta_zeros)}")
        print(f"  Spacings: {len(self.zeta_spacings)}")
        print(f"  Spacing range: [{np.min(self.zeta_spacings):.3f}, {np.max(self.zeta_spacings):.3f}]")
        
        print(f"\nCorrelation Results:")
        print(f"  Prime Gaps - Sorted r: {self.correlations['prime_gaps']['sorted_r']:.3f} (p={self.correlations['prime_gaps']['sorted_p']:.2e})")
        print(f"  Prime Gaps - Unsorted r: {self.correlations['prime_gaps']['unsorted_r']:.3f} (p={self.correlations['prime_gaps']['unsorted_p']:.2e})")
        print(f"  Zeta Spacings - Sorted r: {self.correlations['zeta_spacings']['sorted_r']:.3f} (p={self.correlations['zeta_spacings']['sorted_p']:.2e})")
        print(f"  Zeta Spacings - Unsorted r: {self.correlations['zeta_spacings']['unsorted_r']:.3f} (p={self.correlations['zeta_spacings']['unsorted_p']:.2e})")
        
        print(f"\nOverlap Cluster Analysis:")
        if hasattr(self, 'overlap_results'):
            overlaps = self.overlap_results['correlations']
            high_overlaps = self.overlap_results['high_value_overlaps']
            total = high_overlaps['total_points']
            
            print(f"  Cross-domain correlations:")
            print(f"    Orbital-Prime: {overlaps['orbital_prime']:.3f}")
            print(f"    Orbital-Zeta: {overlaps['orbital_zeta']:.3f}")
            print(f"    Prime-Zeta: {overlaps['prime_zeta']:.3f}")
            
            print(f"  High-value region overlaps:")
            print(f"    Orbital-Prime: {high_overlaps['orbital_prime']}/{total} ({100*high_overlaps['orbital_prime']/total:.1f}%)")
            print(f"    Orbital-Zeta: {high_overlaps['orbital_zeta']}/{total} ({100*high_overlaps['orbital_zeta']/total:.1f}%)")
            print(f"    Prime-Zeta: {high_overlaps['prime_zeta']}/{total} ({100*high_overlaps['prime_zeta']/total:.1f}%)")
            print(f"    All three: {high_overlaps['all_three']}/{total} ({100*high_overlaps['all_three']/total:.1f}%)")
        
        print(f"\nGMM Cluster Analysis:")
        for cluster_id, stats in self.cluster_stats.items():
            print(f"  Cluster {cluster_id}: {stats['count']} points")
            print(f"    κ_theta_mean={stats['mean_kappa_theta']:.3f}±{stats['std_kappa_theta']:.3f}")
            print(f"    κ_ratio_mean={stats['mean_kappa_ratio']:.3f}±{stats['std_kappa_ratio']:.3f}")
        
        print(f"\nCurvature Statistics:")
        print(f"  θ-based κ range: [{np.min(self.curvatures):.3f}, {np.max(self.curvatures):.3f}], mean: {np.mean(self.curvatures):.3f}")
        print(f"  Ratio-based κ range: [{np.min(self.ratio_curvatures):.3f}, {np.max(self.ratio_curvatures):.3f}], mean: {np.mean(self.ratio_curvatures):.3f}")
        
        # Success criteria evaluation using ratio-based curvatures
        print(f"\nSUCCESS CRITERIA EVALUATION:")
        sorted_r_prime = self.correlations['prime_gaps']['sorted_r']
        sorted_r_zeta = self.correlations['zeta_spacings']['sorted_r']
        max_sorted_r = max(sorted_r_prime, sorted_r_zeta)
        
        print(f"  1. Sorted r > 0.78: {max_sorted_r:.3f} > 0.78 → {'✓ PASS' if max_sorted_r > 0.78 else '✗ FAIL'}")
        
        # Use ratio-based curvatures for success criteria
        kappa_modes = [stats['mean_kappa_ratio'] for stats in self.cluster_stats.values() if stats['mean_kappa_ratio'] > 0]
        in_range = [0.3 <= k <= 1.5 for k in kappa_modes]
        print(f"  2. κ_modes ≈ 0.3-1.5: {np.sum(in_range)}/{len(kappa_modes)} modes in range → {'✓ PASS' if len(kappa_modes) > 0 and np.mean(in_range) >= 0.5 else '✗ FAIL'}")
        print(f"     Active κ_modes: {[f'{k:.3f}' for k in kappa_modes]}")
        
        print("\n" + "="*80)
    
    def create_visualizations(self):
        """Create comprehensive visualization plots."""
        plt.style.use('default')
        fig, axes = plt.subplots(3, 2, figsize=(15, 18))
        fig.suptitle('Cross-Domain Simulation: Orbital Resonances vs. Primes', fontsize=16)
        
        # Plot 1: Orbital ratios
        axes[0,0].bar(range(len(self.ratios)), self.ratios, color='skyblue')
        axes[0,0].set_title('Orbital Period Ratios')
        axes[0,0].set_xlabel('Pair Index')
        axes[0,0].set_ylabel('Ratio')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Plot 2: θ' transformed ratios
        axes[0,1].bar(range(len(self.theta_transformed)), self.theta_transformed, color='orange')
        axes[0,1].set_title('θ\'(r,0.3) Transformed Ratios')
        axes[0,1].set_xlabel('Pair Index')
        axes[0,1].set_ylabel('θ\' Value')
        
        # Plot 3: Correlation comparison
        correlations_to_plot = [
            self.correlations['prime_gaps']['sorted_r'],
            self.correlations['prime_gaps']['unsorted_r'],
            self.correlations['zeta_spacings']['sorted_r'],
            self.correlations['zeta_spacings']['unsorted_r']
        ]
        labels = ['Prime (Sorted)', 'Prime (Unsorted)', 'Zeta (Sorted)', 'Zeta (Unsorted)']
        colors = ['green', 'lightgreen', 'blue', 'lightblue']
        
        bars = axes[1,0].bar(labels, correlations_to_plot, color=colors)
        axes[1,0].set_title('Pearson Correlations')
        axes[1,0].set_ylabel('Correlation Coefficient')
        axes[1,0].axhline(y=0.78, color='red', linestyle='--', label='Success Threshold')
        axes[1,0].legend()
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Plot 4: Curvature distribution (both types)
        axes[1,1].hist(self.curvatures, bins=15, alpha=0.7, color='purple', label='θ-based κ')
        axes[1,1].hist(self.ratio_curvatures, bins=15, alpha=0.7, color='orange', label='Ratio-based κ')
        axes[1,1].axvline(x=0.3, color='red', linestyle='--', label='κ=0.3')
        axes[1,1].axvline(x=1.5, color='red', linestyle='--', label='κ=1.5')
        axes[1,1].set_title('Curvature Distribution')
        axes[1,1].set_xlabel('κ (Curvature)')
        axes[1,1].set_ylabel('Frequency')
        axes[1,1].legend()
        
        # Plot 5: Overlap analysis heatmap
        if hasattr(self, 'overlap_results'):
            overlaps = self.overlap_results['correlations']
            overlap_matrix = np.array([
                [1.0, overlaps['orbital_prime'], overlaps['orbital_zeta']],
                [overlaps['orbital_prime'], 1.0, overlaps['prime_zeta']],
                [overlaps['orbital_zeta'], overlaps['prime_zeta'], 1.0]
            ])
            
            im = axes[2,0].imshow(overlap_matrix, cmap='coolwarm', vmin=-1, vmax=1)
            axes[2,0].set_title('Cross-Domain Overlap Correlations')
            axes[2,0].set_xticks([0, 1, 2])
            axes[2,0].set_yticks([0, 1, 2])
            axes[2,0].set_xticklabels(['Orbital', 'Prime', 'Zeta'])
            axes[2,0].set_yticklabels(['Orbital', 'Prime', 'Zeta'])
            
            # Add correlation values as text
            for i in range(3):
                for j in range(3):
                    text = axes[2,0].text(j, i, f'{overlap_matrix[i, j]:.3f}',
                                        ha="center", va="center", color="black" if abs(overlap_matrix[i, j]) < 0.5 else "white")
            
            plt.colorbar(im, ax=axes[2,0])
        
        # Plot 6: Domain comparison scatter plot
        min_len = min(len(self.theta_transformed), len(self.prime_gaps), len(self.zeta_spacings))
        scatter_data = {
            'orbital': self.theta_transformed[:min_len],
            'prime': self.prime_gaps[:min_len],
            'zeta': self.zeta_spacings[:min_len]
        }
        
        # Normalize for comparison
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        orbital_norm = scaler.fit_transform(scatter_data['orbital'].reshape(-1, 1)).flatten()
        prime_norm = scaler.fit_transform(scatter_data['prime'].reshape(-1, 1)).flatten()
        
        axes[2,1].scatter(orbital_norm, prime_norm, alpha=0.7, color='red', label='Orbital vs Prime')
        axes[2,1].plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Perfect correlation')
        axes[2,1].set_title('Normalized Domain Comparison')
        axes[2,1].set_xlabel('Orbital (normalized)')
        axes[2,1].set_ylabel('Prime Gaps (normalized)')
        axes[2,1].legend()
        
        plt.tight_layout()
        
        # Save plot
        output_path = '/home/runner/work/unified-framework/unified-framework/experiments/cross_domain_simulation_results.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nVisualization saved to: {output_path}")
        
        return fig
    
    def run_simulation(self):
        """Run the complete cross-domain simulation."""
        print("Starting Cross-Domain Simulation: Orbital Resonances vs. Primes")
        print("="*70)
        
        # Step 1: Generate data
        self.generate_primes(N=1000000)
        self.generate_zeta_zeros(M=100)
        
        # Step 2: Transform ratios
        self.transform_ratios(k=0.3)
        self.compute_curvatures()
        
        # Step 3: Analysis
        self.correlation_analysis()
        self.gmm_analysis()
        self.overlap_analysis()
        
        # Step 4: Results
        self.generate_results_table()
        self.print_summary()
        
        # Step 5: Visualizations
        self.create_visualizations()
        
        return self.results_df

def main():
    """Main execution function."""
    simulation = CrossDomainSimulation()
    results_df = simulation.run_simulation()
    
    # Display results table
    print("\nDETAILED RESULTS TABLE:")
    print("-" * 120)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(results_df.to_string(index=False, float_format='%.6f'))
    
    # Save results
    output_csv = '/home/runner/work/unified-framework/unified-framework/experiments/cross_domain_results.csv'
    results_df.to_csv(output_csv, index=False)
    print(f"\nResults saved to: {output_csv}")

if __name__ == "__main__":
    main()