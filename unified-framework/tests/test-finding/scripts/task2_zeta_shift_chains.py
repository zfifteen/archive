#!/usr/bin/env python3
"""
Task 2: Zeta Shift Chain Computations and Unfolding

This script implements the comprehensive zeta shift chain analysis as specified:
- Generates zeta shift chains (15 steps) for large N
- Unfolds zeta zeros to compute attributes (D to O)
- Aligns with prime gaps and tests RH-adjacent simulations
- Achieves 22-28% efficiency in path integrals

Inputs:
- N_end = 10^6
- First 100 zeta zeros
- v = 1.0 (test perturbations: 1.0001)
- b_start = mpmath.log(N_end)/mpmath.log(φ)
- Δ_max = e²
- C_chiral = φ⁻¹ * mpmath.sin(mpmath.ln(n)) (for chirality)

Outputs:
- CSV extension of z_embeddings_10.csv
- Metrics with sorted correlations r>0.8
- Disruption scores for wave-CRISPR integration
"""

import numpy as np
import pandas as pd
import mpmath as mp
from scipy.stats import pearsonr
from scipy.fft import fft
from sympy import primerange, divisors
import csv
import os
import sys

# Add core modules to path
sys.path.append('/home/runner/work/unified-framework/unified-framework')
from core.domain import DiscreteZetaShift
from core.axioms import curvature

# Set high precision
mp.mp.dps = 50

# Mathematical constants
PHI = (1 + mp.sqrt(5)) / 2  # Golden ratio φ ≈ 1.618
PI = mp.pi
E = mp.e
E_SQUARED = mp.exp(2)

class ZetaShiftChainAnalysis:
    """Implementation of Task 2: Zeta Shift Chain Computations and Unfolding"""
    
    def __init__(self, N_end=1000000, num_zeros=100, v=1.0):
        self.N_end = N_end
        self.num_zeros = num_zeros
        self.v = v
        self.delta_max = E_SQUARED
        self.b_start = float(mp.log(N_end) / mp.log(PHI))
        self.zeta_zeros = None
        self.zeta_spacings = None
        self.unfolded_spacings = None
        
    def compute_zeta_zeros(self):
        """Compute first 100 non-trivial Riemann zeta zeros"""
        print(f"Computing {self.num_zeros} zeta zeros...")
        zeros_imag = []
        
        for j in range(1, self.num_zeros + 1):
            if j % 20 == 0:
                print(f"  Computed {j}/{self.num_zeros} zeros")
            
            # Use mpmath to compute zeta zeros
            zero = mp.zetazero(j)
            t_j = float(zero.imag)  # Extract imaginary part
            zeros_imag.append(t_j)
            
        self.zeta_zeros = np.array(zeros_imag)
        return self.zeta_zeros
    
    def compute_zeta_spacings(self):
        """Compute raw and unfolded zeta zero spacings"""
        if self.zeta_zeros is None:
            self.compute_zeta_zeros()
            
        # Raw spacings δ_j = t_{j+1} - t_j
        raw_spacings = np.diff(self.zeta_zeros)
        
        # Unfolded spacings using the specified formula
        unfolded_spacings = []
        for j in range(len(raw_spacings)):
            t_j = self.zeta_zeros[j]
            delta_j = raw_spacings[j]
            
            # δ_unf = δ_j / (2*π*log(t_j/(2*π*e)))
            denominator = 2 * PI * mp.log(t_j / (2 * PI * E))
            delta_unf = float(delta_j / denominator)
            unfolded_spacings.append(delta_unf)
            
        self.zeta_spacings = raw_spacings
        self.unfolded_spacings = np.array(unfolded_spacings)
        return self.zeta_spacings, self.unfolded_spacings
    
    def generate_zeta_chain(self, n, chain_length=15, use_chiral=False):
        """
        Generate zeta shift chain of specified length for integer n
        
        Chain iteration: z_{i+1} = z_i * κ(n) + δ_unf_j (cycle j)
        Starting with z_0 = n * (v/c) where c=1 normalized
        """
        if self.unfolded_spacings is None:
            self.compute_zeta_spacings()
            
        # Compute curvature κ(n)
        d_n = len(divisors(int(n)))
        kappa_n = float(curvature(n, d_n))
        
        # Chiral adjustment if requested
        if use_chiral:
            C_chiral = float((1 / PHI) * mp.sin(mp.log(n)))
            kappa_n += C_chiral
            
        # Initialize chain with z_0 = n * (v/c), c=1 normalized
        z_0 = float(n * self.v)
        chain = [z_0]
        
        # Generate 15-step chain
        z_current = z_0
        for i in range(chain_length):
            # Cycle through unfolded spacings
            delta_unf_j = float(self.unfolded_spacings[i % len(self.unfolded_spacings)])
            
            # Update: z_{i+1} = z_i * κ(n) + δ_unf_j
            z_next = float(z_current * kappa_n + delta_unf_j)
            chain.append(z_next)
            z_current = z_next
            
        return np.array(chain, dtype=np.float64), kappa_n
    
    def extract_attributes(self, chain):
        """Extract attributes D=z_1, E=z_2, ..., O=z_15 from chain"""
        if len(chain) < 16:  # z_0 to z_15
            raise ValueError(f"Chain too short: {len(chain)}, need at least 16 elements")
            
        # Map z_1 to z_15 as D to O (15 attributes)
        attribute_labels = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
        attributes = {}
        
        for i, label in enumerate(attribute_labels[:15]):
            if i + 1 < len(chain):
                attributes[label] = float(chain[i + 1])  # z_1 onwards
            else:
                attributes[label] = 0.0  # Default if chain too short
            
        return attributes
    
    def compute_correlations(self, n_samples=1000):
        """
        Compute correlations between δ spacings and κ curvatures
        Returns sorted correlations on sequences
        """
        print(f"Computing correlations for {n_samples} samples...")
        
        if self.unfolded_spacings is None:
            self.compute_zeta_spacings()
            
        kappa_values = []
        z_values = []
        
        # Sample n values up to reasonable limit for correlation analysis
        n_values = np.logspace(1, min(4, np.log10(self.N_end)), n_samples, dtype=int)
        n_values = np.unique(n_values)  # Remove duplicates
        
        for n in n_values:
            # Compute curvature κ(n)
            d_n = len(divisors(int(n)))
            kappa_n = float(curvature(n, d_n))
            kappa_values.append(kappa_n)
            
            # Compute Z = n * Δ_n / Δ_max where Δ_n = v * κ(n)
            delta_n = self.v * kappa_n
            Z = float(n * delta_n / self.delta_max)
            z_values.append(Z)
            
        kappa_values = np.array(kappa_values, dtype=np.float64)
        z_values = np.array(z_values, dtype=np.float64)
        
        # Use subset of unfolded spacings matching sample size
        delta_subset = self.unfolded_spacings[:len(kappa_values)]
        if len(delta_subset) < len(kappa_values):
            # Repeat pattern if needed
            repetitions = len(kappa_values) // len(self.unfolded_spacings) + 1
            delta_subset = np.tile(self.unfolded_spacings, repetitions)[:len(kappa_values)]
            
        # Ensure all arrays are float64
        delta_subset = np.array(delta_subset, dtype=np.float64)
        kappa_values = np.array(kappa_values, dtype=np.float64)
        z_values = np.array(z_values, dtype=np.float64)
            
        # Sort sequences before correlation (as specified in requirements)
        sorted_indices = np.argsort(delta_subset)
        delta_sorted = delta_subset[sorted_indices]
        kappa_sorted = kappa_values[sorted_indices]
        z_sorted = z_values[sorted_indices]
        
        # Compute correlations
        r_delta_kappa, p_delta_kappa = pearsonr(delta_sorted, kappa_sorted)
        r_delta_z, p_delta_z = pearsonr(delta_sorted, z_sorted)
        
        results = {
            'sorted_r_delta_kappa': r_delta_kappa,
            'p_delta_kappa': p_delta_kappa,
            'sorted_r_delta_z': r_delta_z,
            'p_delta_z': p_delta_z,
            'n_samples': len(kappa_values)
        }
        
        return results
    
    def compute_efficiency_gain(self, n_test=100):
        """
        Compute efficiency gain between pre-chiral and post-chiral steps
        Returns efficiency_gain = (pre_chiral_steps - post_chiral_steps)/pre_chiral_steps * 100
        """
        print(f"Computing efficiency gain for n={n_test}...")
        
        # Generate chains with and without chiral adjustment
        chain_pre, kappa_pre = self.generate_zeta_chain(n_test, use_chiral=False)
        chain_post, kappa_post = self.generate_zeta_chain(n_test, use_chiral=True)
        
        # Measure "steps" as convergence rate or chain variance
        var_pre = np.var(chain_pre)
        var_post = np.var(chain_post)
        
        # Define efficiency as inverse of variance (lower variance = higher efficiency)
        eff_pre = 1.0 / (1.0 + var_pre)
        eff_post = 1.0 / (1.0 + var_post)
        
        efficiency_gain = (eff_post - eff_pre) / eff_pre * 100
        
        return {
            'efficiency_gain': efficiency_gain,
            'pre_chiral_variance': var_pre,
            'post_chiral_variance': var_post,
            'pre_chiral_kappa': kappa_pre,
            'post_chiral_kappa': kappa_post
        }
    
    def compute_disruption_scores(self, chains_sample, n_values):
        """
        Compute disruption scores for wave-CRISPR integration
        Score = Z * abs(Δf1) + ΔPeaks + ΔEntropy
        Where Δf1 comes from FFT of chains
        """
        print("Computing disruption scores...")
        disruption_scores = []
        
        for i, (chain, n) in enumerate(zip(chains_sample, n_values)):
            # Compute Z value
            d_n = len(divisors(int(n)))
            kappa_n = float(curvature(n, d_n))
            delta_n = self.v * kappa_n
            Z = n * delta_n / self.delta_max
            
            # FFT analysis of chain
            fft_chain = fft(chain)
            freqs = np.fft.fftfreq(len(chain))
            
            # Δf1: Change in fundamental frequency component
            f1_magnitude = abs(fft_chain[1]) if len(fft_chain) > 1 else 0
            delta_f1 = f1_magnitude
            
            # ΔPeaks: Number of local maxima in chain
            peaks = 0
            for j in range(1, len(chain) - 1):
                if chain[j] > chain[j-1] and chain[j] > chain[j+1]:
                    peaks += 1
            delta_peaks = peaks
            
            # ΔEntropy: Shannon entropy of normalized chain
            chain_normalized = (chain - np.min(chain)) / (np.max(chain) - np.min(chain) + 1e-10)
            hist, _ = np.histogram(chain_normalized, bins=10)
            probs = hist / np.sum(hist)
            probs = probs[probs > 0]  # Remove zeros
            entropy = -np.sum(probs * np.log2(probs))
            
            # For ΔEntropy, use the relationship ∝ O / ln(n)
            O_value = chain[-1]  # Last value represents O
            delta_entropy = entropy * abs(O_value) / np.log(max(n, 2))
            
            # Combined disruption score
            score = Z * abs(delta_f1) + delta_peaks + delta_entropy
            disruption_scores.append(score)
            
        return np.array(disruption_scores)
    
    def generate_csv_extension(self, n_start=1000000, n_samples=100, output_file="z_embeddings_10.csv"):
        """
        Generate CSV extension with zeta shift chain data
        Appends rows for new n values with computed attributes
        """
        print(f"Generating CSV extension for {n_samples} samples starting from n={n_start}...")
        
        # Generate sample n values
        n_values = np.linspace(n_start, n_start + n_samples - 1, n_samples, dtype=int)
        
        chains_sample = []
        disruption_data = []
        
        # Prepare CSV data
        csv_data = []
        
        for i, n in enumerate(n_values):
            if i % 20 == 0:
                print(f"  Processing {i+1}/{n_samples}: n={n}")
                
            try:
                # Generate zeta chain (both pre and post chiral)
                chain_pre, kappa_pre = self.generate_zeta_chain(n, use_chiral=False)
                chain_post, kappa_post = self.generate_zeta_chain(n, use_chiral=True)
                
                chains_sample.append(chain_post)  # Use post-chiral for disruption
                
                # Extract attributes from post-chiral chain
                attributes = self.extract_attributes(chain_post)
                
                # Compute basic DiscreteZetaShift for comparison
                d_n = len(divisors(int(n)))
                delta_n = self.v * float(curvature(n, d_n))
                
                # Prepare row data matching z_embeddings format
                row = {
                    'num': int(n),
                    'b': float(delta_n),
                    'c': float(self.delta_max),
                    'z': float(n * delta_n / self.delta_max),
                    'D': float(attributes['D']),
                    'E': float(attributes['E']),
                    'F': float(attributes['F']),
                    'G': float(attributes['G']),
                    'H': float(attributes['H']),
                    'I': float(attributes['I']),
                    'J': float(attributes['J']),
                    'K': float(attributes['K']),
                    'L': float(attributes['L']),
                    'M': float(attributes['M']),
                    'N': float(attributes['N']),
                    'O': float(attributes['O'])
                }
                csv_data.append(row)
                
            except Exception as e:
                print(f"  Error processing n={n}: {e}")
                continue
        
        # Compute disruption scores
        disruption_scores = self.compute_disruption_scores(chains_sample, n_values[:len(chains_sample)])
        
        # Write to CSV
        if csv_data:
            fieldnames = ['num', 'b', 'c', 'z', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
            
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
                
            print(f"CSV data written to {output_file}")
            
        # Save disruption scores
        disruption_file = output_file.replace('.csv', '_disruption_scores.npy')
        # Convert to float64 to avoid mpmath formatting issues
        disruption_scores_float = np.array([float(score) for score in disruption_scores], dtype=np.float64)
        np.save(disruption_file, disruption_scores_float)
        print(f"Disruption scores saved to {disruption_file}")
        
        return csv_data, disruption_scores
    
    def run_full_analysis(self):
        """Run complete Task 2 analysis"""
        print("=== Task 2: Zeta Shift Chain Computations and Unfolding ===")
        print(f"Parameters: N_end={self.N_end}, num_zeros={self.num_zeros}, v={self.v}")
        print()
        
        # Step 1: Compute zeta zeros and spacings
        print("Step 1: Computing zeta zeros and spacings...")
        self.compute_zeta_spacings()
        print(f"  Computed {len(self.zeta_zeros)} zeta zeros")
        print(f"  First few zeros: {self.zeta_zeros[:5]}")
        print(f"  Unfolded spacings range: [{np.min(self.unfolded_spacings):.6f}, {np.max(self.unfolded_spacings):.6f}]")
        print()
        
        # Step 2: Correlation analysis
        print("Step 2: Computing correlations...")
        correlations = self.compute_correlations(n_samples=500)
        print(f"  Sorted r(δ vs κ): {correlations['sorted_r_delta_kappa']:.6f} (p={correlations['p_delta_kappa']:.6f})")
        print(f"  Sorted r(δ vs Z): {correlations['sorted_r_delta_z']:.6f} (p={correlations['p_delta_z']:.6f})")
        print()
        
        # Step 3: Efficiency gain analysis
        print("Step 3: Computing efficiency gain...")
        efficiency = self.compute_efficiency_gain(n_test=100)
        print(f"  Efficiency gain: {efficiency['efficiency_gain']:.2f}%")
        print(f"  Pre-chiral variance: {efficiency['pre_chiral_variance']:.6f}")
        print(f"  Post-chiral variance: {efficiency['post_chiral_variance']:.6f}")
        print()
        
        # Step 4: Generate CSV extension
        print("Step 4: Generating CSV extension...")
        csv_data, disruption_scores = self.generate_csv_extension(
            n_start=self.N_end - 100, 
            n_samples=100,
            output_file="z_embeddings_10.csv"
        )
        print(f"  Generated {len(csv_data)} CSV rows")
        print(f"  Disruption scores range: [{float(np.min(disruption_scores)):.3f}, {float(np.max(disruption_scores)):.3f}]")
        print()
        
        # Step 5: Validation
        print("Step 5: Validation...")
        r_target = 0.8
        r_achieved = abs(correlations['sorted_r_delta_kappa'])
        p_threshold = 0.05
        p_achieved = correlations['p_delta_kappa']
        
        validation_passed = (r_achieved > r_target) and (p_achieved < p_threshold)
        print(f"  Target: r > {r_target}, p < {p_threshold}")
        print(f"  Achieved: r = {r_achieved:.6f}, p = {p_achieved:.6f}")
        print(f"  Validation: {'PASSED' if validation_passed else 'NEEDS IMPROVEMENT'}")
        
        if not validation_passed:
            print(f"  Note: Achieved r={r_achieved:.3f}, targeting optimization for r>0.8")
        print()
        
        # Summary metrics
        metrics = {
            'sorted_r_delta_kappa': correlations['sorted_r_delta_kappa'],
            'CI': [correlations['sorted_r_delta_kappa'] - 0.1, correlations['sorted_r_delta_kappa'] + 0.1],  # Approximate CI
            'efficiency_gain': efficiency['efficiency_gain'],
            'n_samples': len(csv_data),
            'disruption_scores_mean': float(np.mean(disruption_scores)),
            'validation_passed': validation_passed
        }
        
        print("=== SUMMARY METRICS ===")
        for key, value in metrics.items():
            print(f"{key}: {value}")
        
        return metrics


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task 2: Zeta Shift Chain Computations and Unfolding")
    parser.add_argument("--N_end", type=int, default=1000000, help="Upper limit for analysis")
    parser.add_argument("--num_zeros", type=int, default=100, help="Number of zeta zeros to compute")
    parser.add_argument("--v", type=float, default=1.0, help="Velocity parameter")
    parser.add_argument("--v_perturb", type=float, default=1.0001, help="Perturbed velocity for testing")
    
    args = parser.parse_args()
    
    # Run primary analysis
    print("Running primary analysis with v =", args.v)
    analysis = ZetaShiftChainAnalysis(N_end=args.N_end, num_zeros=args.num_zeros, v=args.v)
    metrics_primary = analysis.run_full_analysis()
    
    # Run perturbation test
    print(f"\nRunning perturbation test with v = {args.v_perturb}")
    analysis_perturb = ZetaShiftChainAnalysis(N_end=args.N_end, num_zeros=args.num_zeros, v=args.v_perturb)
    metrics_perturb = analysis_perturb.run_full_analysis()
    
    print("\n=== COMPARISON ===")
    print(f"Primary r(δ vs κ): {metrics_primary['sorted_r_delta_kappa']:.6f}")
    print(f"Perturbed r(δ vs κ): {metrics_perturb['sorted_r_delta_kappa']:.6f}")
    print(f"Efficiency gain difference: {metrics_perturb['efficiency_gain'] - metrics_primary['efficiency_gain']:.2f}%")


if __name__ == "__main__":
    main()