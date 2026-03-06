#!/usr/bin/env python3
"""
Dataset Preparation for ML Cross-Validation
===========================================

Prepares three key datasets for cross-domain machine learning validation:
1. Zeta Zeros Dataset: Riemann zeta zero spacings and quantum chaos metrics
2. GUE Metrics Dataset: Gaussian Unitary Ensemble statistics for random matrix theory
3. CRISPR Metrics Dataset: Spectral analysis features from biological sequences

Uses existing Z Framework components to ensure consistency with established methodology.
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path
import time
import warnings
warnings.filterwarnings('ignore')

# Add framework path
sys.path.append('/home/runner/work/unified-framework/unified-framework')

# Import Z Framework components
from src.core.domain import DiscreteZetaShift, E_SQUARED
from src.core.axioms import universal_invariance, curvature, theta_prime
import mpmath as mp

# Set high precision
mp.mp.dps = 50

# Constants
PHI = float((1 + mp.sqrt(5)) / 2)  # Golden ratio
PI = float(mp.pi)
E = float(mp.e)

class DatasetPreparator:
    """
    Comprehensive dataset preparation for cross-domain ML validation
    """
    
    def __init__(self, output_dir="datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize storage for datasets
        self.zeta_dataset = None
        self.gue_dataset = None
        self.crispr_dataset = None
        self.combined_dataset = None
        
        print(f"DatasetPreparator initialized - output directory: {self.output_dir}")
        
    def prepare_zeta_zeros_dataset(self, n_zeros=100, n_points=200):
        """
        Prepare dataset from Riemann zeta zeros and quantum chaos metrics
        """
        print(f"\nPreparing zeta zeros dataset ({n_zeros} zeros, {n_points} points)...")
        
        data = []
        
        # Generate zeta zeros
        print("Computing Riemann zeta zeros...")
        zeta_zeros = []
        for k in range(1, n_zeros + 1):
            zero = mp.zetazero(k)
            zeta_zeros.append(float(zero.imag))
        
        # Compute spacings
        spacings = np.array([zeta_zeros[i+1] - zeta_zeros[i] 
                           for i in range(len(zeta_zeros)-1)])
        
        # Generate DiscreteZetaShift embeddings for quantum analysis
        print("Computing DiscreteZetaShift 5D embeddings...")
        for n in range(2, n_points + 2):
            try:
                # Create DiscreteZetaShift instance
                dz = DiscreteZetaShift(n)
                attrs = dz.attributes
                
                # Extract quantum chaos metrics
                D, E, F, I, O = attrs['D'], attrs['E'], attrs['F'], attrs['I'], attrs['O']
                
                # Compute 5D helical embedding coordinates
                a = np.sqrt(float(D)**2 + float(E)**2)  # Amplitude
                x = a * np.cos(float(D)) if a > 0 else 0
                y = a * np.sin(float(E)) if a > 0 else 0
                z = float(F) / E_SQUARED
                w = float(I)
                u = float(O)
                
                # Compute frame-corrected curvature using divisor count
                import sympy
                d_n = sympy.divisor_count(n)
                kappa = curvature(n, d_n)
                
                # Compute theta-prime transformation (golden ratio modular)
                theta_transformed = theta_prime(n, 0.3, PHI)
                
                # Universal invariance measure
                invariance = universal_invariance(n, 3e8)
                
                # Quantum chaos indicators
                level_spacing = spacings[min(n-2, len(spacings)-1)] if n-2 < len(spacings) else spacings[-1]
                goe_indicator = level_spacing / np.mean(spacings[:10]) if len(spacings) > 10 else 1.0
                
                # Spectral rigidity (simplified)
                spectral_rigidity = np.var(spacings[:min(20, len(spacings))])
                
                data.append({
                    'n': n,
                    'D': D, 'E': E, 'F': F, 'I': I, 'O': O,
                    'x_coord': x, 'y_coord': y, 'z_coord': z, 'w_coord': w, 'u_coord': u,
                    'amplitude': a,
                    'curvature': kappa,
                    'theta_transformed': theta_transformed,
                    'universal_invariance': invariance,
                    'zeta_spacing': level_spacing,
                    'goe_indicator': goe_indicator,
                    'spectral_rigidity': spectral_rigidity,
                    'log_n': np.log(n),
                    'sqrt_n': np.sqrt(n),
                    'domain': 'quantum_chaos'
                })
                
            except Exception as e:
                print(f"Warning: Failed to compute for n={n}: {e}")
                continue
        
        self.zeta_dataset = pd.DataFrame(data)
        
        # Save dataset
        output_path = self.output_dir / "zeta_zeros_dataset.csv"
        self.zeta_dataset.to_csv(output_path, index=False)
        
        print(f"✓ Zeta zeros dataset created: {len(self.zeta_dataset)} samples")
        print(f"  Features: {list(self.zeta_dataset.columns)}")
        print(f"  Saved to: {output_path}")
        
        return self.zeta_dataset
    
    def prepare_gue_metrics_dataset(self, n_matrices=150, matrix_size=20):
        """
        Prepare Gaussian Unitary Ensemble (GUE) metrics dataset
        """
        print(f"\nPreparing GUE metrics dataset ({n_matrices} matrices, size {matrix_size}x{matrix_size})...")
        
        data = []
        
        for i in range(n_matrices):
            try:
                # Generate random Hermitian matrix (GUE)
                # Real part: Gaussian with variance 1/2 for off-diagonal, 1 for diagonal
                real_part = np.random.normal(0, 1/np.sqrt(2), (matrix_size, matrix_size))
                real_part = (real_part + real_part.T) / 2  # Make symmetric
                np.fill_diagonal(real_part, np.random.normal(0, 1, matrix_size))
                
                # Imaginary part: Gaussian with variance 1/2 for off-diagonal, 0 for diagonal
                imag_part = np.random.normal(0, 1/np.sqrt(2), (matrix_size, matrix_size))
                imag_part = (imag_part - imag_part.T) / 2  # Make antisymmetric
                np.fill_diagonal(imag_part, 0)
                
                # Construct Hermitian matrix
                matrix = real_part + 1j * imag_part
                
                # Compute eigenvalues
                eigenvals = np.linalg.eigvals(matrix)
                eigenvals = np.sort(eigenvals.real)  # Sort real parts
                
                # Compute level spacings
                spacings = np.diff(eigenvals)
                
                # GUE statistical measures
                mean_spacing = np.mean(spacings)
                spacing_variance = np.var(spacings)
                spacing_ratio = np.mean(spacings[1:] / spacings[:-1]) if len(spacings) > 1 else 1.0
                
                # Spectral properties
                spectral_norm = np.linalg.norm(matrix)
                trace = np.trace(matrix).real
                determinant = np.linalg.det(matrix).real if np.linalg.det(matrix).real > 0 else 1e-10
                log_determinant = np.log(abs(determinant))
                
                # Level repulsion (Wigner surmise)
                s_min = np.min(spacings) if len(spacings) > 0 else 0
                level_repulsion = s_min / mean_spacing if mean_spacing > 0 else 0
                
                # Correlation measures
                autocorr = np.corrcoef(spacings[:-1], spacings[1:])[0, 1] if len(spacings) > 2 else 0
                
                # Relate to Z framework through DiscreteZetaShift
                # Use matrix properties as input for discrete transformations
                n_equiv = max(2, int(abs(trace)) % 1000 + 2)  # Map trace to integer for DZ analysis
                
                try:
                    dz = DiscreteZetaShift(n_equiv)
                    attrs = dz.attributes
                    z_correlation = attrs['O']  # Use O value as quantum-discrete bridge
                except:
                    z_correlation = 0.0
                
                # Curvature based on spectral properties
                import sympy
                d_n_equiv = sympy.divisor_count(n_equiv)
                spectral_curvature = curvature(n_equiv, d_n_equiv)
                
                data.append({
                    'matrix_id': i,
                    'matrix_size': matrix_size,
                    'mean_spacing': mean_spacing,
                    'spacing_variance': spacing_variance,
                    'spacing_ratio': spacing_ratio,
                    'spectral_norm': spectral_norm,
                    'trace': trace,
                    'log_determinant': log_determinant,
                    'level_repulsion': level_repulsion,
                    'autocorrelation': autocorr,
                    'min_eigenval': np.min(eigenvals),
                    'max_eigenval': np.max(eigenvals),
                    'eigenval_range': np.max(eigenvals) - np.min(eigenvals),
                    'z_correlation': z_correlation,
                    'spectral_curvature': spectral_curvature,
                    'n_equivalent': n_equiv,
                    'domain': 'random_matrix'
                })
                
            except Exception as e:
                print(f"Warning: Failed to compute GUE matrix {i}: {e}")
                continue
        
        self.gue_dataset = pd.DataFrame(data)
        
        # Save dataset
        output_path = self.output_dir / "gue_metrics_dataset.csv"
        self.gue_dataset.to_csv(output_path, index=False)
        
        print(f"✓ GUE metrics dataset created: {len(self.gue_dataset)} samples")
        print(f"  Features: {list(self.gue_dataset.columns)}")
        print(f"  Saved to: {output_path}")
        
        return self.gue_dataset
    
    def prepare_crispr_metrics_dataset(self, n_sequences=100):
        """
        Prepare CRISPR sequence metrics dataset using wave-crispr methodology
        """
        print(f"\nPreparing CRISPR metrics dataset ({n_sequences} sequences)...")
        
        # Real biological sequences (subset from comprehensive_cross_validation.py)
        sequences = {
            'PCSK9_exon1': "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG",
            'CCR5_delta32': "ATGGATTATCAAGTGTCAAGTCCAATCTATGACATCAATTATTACCTGTACGAGTTCCTCCACCAGGAAATACTGAGGACCAGCTGTCTTTGCCCGCCCTGCTGTTGGTGGTGCTCTTTTCTCTCCTCGTGATTCTCCCAGAAGGCTGAGGAACATCCAG",
            'BRCA1_exon11': "GAGATCAAAGGGCAGTGAGTTCTCCAAGCCTTATCTGGGAACTCAGGGTCTGCAGTGACTTCCCCAATGTGTCAGCCTCCACTGGTGGTCAGTGAAATCTCTGTGGCCTGAGGATCTCCAGTGCTGATACTCTGCCTAATCTGTCTCATCTCTCTCTC",
            'TP53_exon4': "CCCTTCCCAGAAAACCTACCAGGGCAGCTACGGTTTCCGTCTGGGCTTCTTGCATTCTGGGACAGCCAAGTCTGTGACTTGCACGTACTCCCCTGCCCTCAACAAGATGTTTTGCCAACTGGCCAAGACCTGCCCTGTGCAGCTGTGGGTTGATTCCAC",
            'CFTR_delta_F508': "CATAGCCGACCTGGAGATCACCAACCAGAAGGAAGGACTCGTGGAAGTCCAGATACCTGGAAGGCCACAGAGGAAACTGTCTTCAACTGGACTTCATCGGGCTCCTGTTCTTGGTGATCTCATTGGTCTGGGTGACATCCGATTTGCTTTGCCAGTGGCT"
        }
        
        # Generate additional synthetic sequences for larger dataset
        bases = ['A', 'T', 'G', 'C']
        base_weights = {'A': 1+0j, 'T': -1+0j, 'C': 0+1j, 'G': 0-1j}
        
        all_sequences = list(sequences.values())
        sequence_names = list(sequences.keys())
        
        # Add synthetic sequences
        for i in range(n_sequences - len(sequences)):
            # Generate synthetic sequence with realistic base composition
            length = np.random.randint(100, 200)
            # Realistic GC content (40-60%)
            gc_content = np.random.uniform(0.4, 0.6)
            n_gc = int(length * gc_content)
            n_at = length - n_gc
            
            synthetic_seq = (['G', 'C'] * (n_gc // 2) + ['G'] * (n_gc % 2) + 
                           ['A', 'T'] * (n_at // 2) + ['A'] * (n_at % 2))
            np.random.shuffle(synthetic_seq)
            all_sequences.append(''.join(synthetic_seq))
            sequence_names.append(f'synthetic_{i+1}')
        
        data = []
        
        for idx, sequence in enumerate(all_sequences[:n_sequences]):
            try:
                seq_name = sequence_names[idx] if idx < len(sequence_names) else f'seq_{idx}'
                
                # Basic sequence properties
                length = len(sequence)
                gc_content = (sequence.count('G') + sequence.count('C')) / length
                
                # Build waveform using wave-crispr methodology
                d = 0.34  # Standard DNA spacing
                spacings = [d] * length
                s = np.cumsum(spacings)
                waveform = np.array([base_weights[base] * np.exp(2j * np.pi * s[i]) 
                                   for i, base in enumerate(sequence)])
                
                # Spectral analysis
                spectrum = np.abs(np.fft.fft(waveform))
                spectrum_power = spectrum ** 2
                
                # Spectral features
                spectral_mean = np.mean(spectrum)
                spectral_std = np.std(spectrum)
                spectral_max = np.max(spectrum)
                spectral_entropy = -np.sum((spectrum_power / np.sum(spectrum_power)) * 
                                         np.log(spectrum_power / np.sum(spectrum_power) + 1e-10))
                
                # Frequency domain features
                freqs = np.fft.fftfreq(len(waveform))
                dominant_freq = freqs[np.argmax(spectrum)]
                bandwidth = np.sum(spectrum > spectral_mean) / len(spectrum)
                
                # Phase information
                phase = np.angle(waveform)
                phase_variance = np.var(phase)
                
                # Complexity measures
                complexity_lz = self._lempel_ziv_complexity(sequence)
                
                # Map to Z framework through sequence-derived integer
                n_seq = max(2, (length + int(gc_content * 1000)) % 1000 + 2)
                
                try:
                    dz = DiscreteZetaShift(n_seq)
                    attrs = dz.attributes
                    quantum_bridge = attrs['O']
                    discrete_F = attrs['F']
                except:
                    quantum_bridge = 0.0
                    discrete_F = 0.0
                
                # Frame transformations
                import sympy
                d_n_seq = sympy.divisor_count(n_seq)
                seq_curvature = curvature(n_seq, d_n_seq)
                theta_transform = theta_prime(n_seq, 0.3, PHI)
                
                # CRISPR efficiency proxies (based on known correlations)
                efficiency_proxy = gc_content * spectral_entropy  # Simple efficiency model
                
                data.append({
                    'sequence_id': idx,
                    'sequence_name': seq_name,
                    'length': length,
                    'gc_content': gc_content,
                    'spectral_mean': spectral_mean,
                    'spectral_std': spectral_std,
                    'spectral_max': spectral_max,
                    'spectral_entropy': spectral_entropy,
                    'dominant_frequency': dominant_freq,
                    'bandwidth': bandwidth,
                    'phase_variance': phase_variance,
                    'complexity_lz': complexity_lz,
                    'quantum_bridge': quantum_bridge,
                    'discrete_F': discrete_F,
                    'sequence_curvature': seq_curvature,
                    'theta_transform': theta_transform,
                    'efficiency_proxy': efficiency_proxy,
                    'n_sequence': n_seq,
                    'domain': 'biological'
                })
                
            except Exception as e:
                print(f"Warning: Failed to process sequence {idx}: {e}")
                continue
        
        self.crispr_dataset = pd.DataFrame(data)
        
        # Save dataset
        output_path = self.output_dir / "crispr_metrics_dataset.csv"
        self.crispr_dataset.to_csv(output_path, index=False)
        
        print(f"✓ CRISPR metrics dataset created: {len(self.crispr_dataset)} samples")
        print(f"  Features: {list(self.crispr_dataset.columns)}")
        print(f"  Saved to: {output_path}")
        
        return self.crispr_dataset
    
    def _lempel_ziv_complexity(self, sequence):
        """
        Compute Lempel-Ziv complexity of a sequence
        """
        if len(sequence) < 2:
            return 1
        
        n = len(sequence)
        complexity = 1
        i = 0
        
        while i < n - 1:
            j = i + 1
            while j <= n:
                substring = sequence[i:j]
                if substring not in sequence[:i]:
                    complexity += 1
                    i = j - 1
                    break
                j += 1
            else:
                break
            i += 1
        
        return complexity
    
    def combine_datasets(self):
        """
        Combine all datasets with common features for cross-domain analysis
        """
        print("\nCombining datasets for cross-domain analysis...")
        
        if any(ds is None or len(ds) == 0 for ds in [self.zeta_dataset, self.gue_dataset, self.crispr_dataset]):
            print("Error: Not all datasets prepared successfully. Check individual dataset preparation.")
            # Create minimal combined dataset if some data exists
            if self.zeta_dataset is not None and len(self.zeta_dataset) > 0:
                print(f"Only zeta dataset available with {len(self.zeta_dataset)} samples")
                # Create a minimal combined dataset with just zeta data
                combined_data = []
                for idx, row in self.zeta_dataset.iterrows():
                    combined_data.append({
                        'sample_id': f'zeta_{idx}',
                        'domain': 'quantum_chaos',
                        'curvature': row['curvature'],
                        'theta_transformed': row['theta_transformed'],
                        'universal_invariance': row['universal_invariance'],
                        'amplitude': row['amplitude'],
                        'spectral_measure': row['spectral_rigidity'],
                        'correlation_measure': row['goe_indicator'],
                        'complexity_measure': row['O'],
                        'log_scale': row['log_n'],
                        'n_value': row['n']
                    })
                
                self.combined_dataset = pd.DataFrame(combined_data)
                
                # Save minimal combined dataset
                output_path = self.output_dir / "combined_features.csv"
                self.combined_dataset.to_csv(output_path, index=False)
                
                print(f"✓ Minimal combined dataset created: {len(self.combined_dataset)} samples")
                print(f"  Domains: {self.combined_dataset['domain'].value_counts().to_dict()}")
                print(f"  Common features: {list(self.combined_dataset.columns)}")
                print(f"  Saved to: {output_path}")
                
                return self.combined_dataset
            else:
                return None
        
        # Identify common features across domains
        common_features = []
        
        # Add identifier and domain
        combined_data = []
        
        # Process zeta dataset
        for idx, row in self.zeta_dataset.iterrows():
            combined_data.append({
                'sample_id': f'zeta_{idx}',
                'domain': 'quantum_chaos',
                'curvature': row['curvature'],
                'theta_transformed': row['theta_transformed'],
                'universal_invariance': row['universal_invariance'],
                'amplitude': row['amplitude'],
                'spectral_measure': row['spectral_rigidity'],
                'correlation_measure': row['goe_indicator'],
                'complexity_measure': row['O'],
                'log_scale': row['log_n'],
                'n_value': row['n']
            })
        
        # Process GUE dataset
        for idx, row in self.gue_dataset.iterrows():
            combined_data.append({
                'sample_id': f'gue_{idx}',
                'domain': 'random_matrix',
                'curvature': row['spectral_curvature'],
                'theta_transformed': row['z_correlation'],  # Proxy mapping
                'universal_invariance': row['spectral_norm'] / 1000,  # Normalized
                'amplitude': row['eigenval_range'],
                'spectral_measure': row['spacing_variance'],
                'correlation_measure': row['autocorrelation'],
                'complexity_measure': row['level_repulsion'],
                'log_scale': np.log(row['matrix_size']),
                'n_value': row['n_equivalent']
            })
        
        # Process CRISPR dataset
        for idx, row in self.crispr_dataset.iterrows():
            combined_data.append({
                'sample_id': f'crispr_{idx}',
                'domain': 'biological',
                'curvature': row['sequence_curvature'],
                'theta_transformed': row['theta_transform'],
                'universal_invariance': row['quantum_bridge'] / 100,  # Normalized
                'amplitude': row['spectral_max'],
                'spectral_measure': row['spectral_entropy'],
                'correlation_measure': row['gc_content'],
                'complexity_measure': row['complexity_lz'],
                'log_scale': np.log(row['length']),
                'n_value': row['n_sequence']
            })
        
        self.combined_dataset = pd.DataFrame(combined_data)
        
        # Save combined dataset
        output_path = self.output_dir / "combined_features.csv"
        self.combined_dataset.to_csv(output_path, index=False)
        
        print(f"✓ Combined dataset created: {len(self.combined_dataset)} samples")
        print(f"  Domains: {self.combined_dataset['domain'].value_counts().to_dict()}")
        print(f"  Common features: {list(self.combined_dataset.columns)}")
        print(f"  Saved to: {output_path}")
        
        return self.combined_dataset
    
    def generate_summary_report(self):
        """
        Generate comprehensive summary of prepared datasets
        """
        print("\nGenerating dataset summary report...")
        
        summary = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'datasets': {},
            'statistics': {},
            'cross_domain_analysis': {}
        }
        
        # Individual dataset summaries
        for name, dataset in [('zeta_zeros', self.zeta_dataset), 
                             ('gue_metrics', self.gue_dataset),
                             ('crispr_metrics', self.crispr_dataset)]:
            if dataset is not None:
                summary['datasets'][name] = {
                    'n_samples': len(dataset),
                    'n_features': len(dataset.columns),
                    'features': list(dataset.columns),
                    'memory_usage_mb': dataset.memory_usage(deep=True).sum() / 1024**2
                }
        
        # Combined dataset summary
        if self.combined_dataset is not None:
            summary['datasets']['combined'] = {
                'n_samples': len(self.combined_dataset),
                'n_features': len(self.combined_dataset.columns),
                'domain_distribution': self.combined_dataset['domain'].value_counts().to_dict()
            }
            
            # Cross-domain statistics
            for feature in ['curvature', 'theta_transformed', 'spectral_measure']:
                if feature in self.combined_dataset.columns:
                    by_domain = self.combined_dataset.groupby('domain')[feature].describe()
                    summary['cross_domain_analysis'][feature] = by_domain.to_dict()
        
        # Save summary
        output_path = self.output_dir / "dataset_summary.json"
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"✓ Summary report saved to: {output_path}")
        
        # Create visualization
        self._create_dataset_visualizations()
        
        return summary
    
    def _create_dataset_visualizations(self):
        """
        Create visualization plots for the prepared datasets
        """
        if self.combined_dataset is None:
            return
        
        print("Creating dataset visualizations...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Cross-Domain ML Dataset Overview', fontsize=16)
        
        # Domain distribution
        domain_counts = self.combined_dataset['domain'].value_counts()
        axes[0,0].pie(domain_counts.values, labels=domain_counts.index, autopct='%1.1f%%')
        axes[0,0].set_title('Sample Distribution by Domain')
        
        # Feature distributions by domain
        key_features = ['curvature', 'theta_transformed', 'spectral_measure']
        
        for i, feature in enumerate(key_features):
            if feature in self.combined_dataset.columns:
                for domain in self.combined_dataset['domain'].unique():
                    data = self.combined_dataset[self.combined_dataset['domain'] == domain][feature]
                    axes[0,i+1].hist(data, alpha=0.7, label=domain, bins=20)
                axes[0,i+1].set_title(f'{feature.replace("_", " ").title()} Distribution')
                axes[0,i+1].legend()
        
        # Cross-domain correlations
        numeric_features = self.combined_dataset.select_dtypes(include=[np.number]).columns
        corr_matrix = self.combined_dataset[numeric_features].corr()
        
        im = axes[1,0].imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        axes[1,0].set_title('Feature Correlation Matrix')
        axes[1,0].set_xticks(range(len(numeric_features)))
        axes[1,0].set_yticks(range(len(numeric_features)))
        axes[1,0].set_xticklabels(numeric_features, rotation=45, ha='right')
        axes[1,0].set_yticklabels(numeric_features)
        plt.colorbar(im, ax=axes[1,0])
        
        # Feature importance via variance
        feature_vars = self.combined_dataset[numeric_features].var().sort_values(ascending=False)
        axes[1,1].bar(range(len(feature_vars)), feature_vars.values)
        axes[1,1].set_title('Feature Variance (Importance Proxy)')
        axes[1,1].set_xticks(range(len(feature_vars)))
        axes[1,1].set_xticklabels(feature_vars.index, rotation=45, ha='right')
        
        # Cross-domain scatter plot
        if 'curvature' in self.combined_dataset.columns and 'theta_transformed' in self.combined_dataset.columns:
            for domain in self.combined_dataset['domain'].unique():
                mask = self.combined_dataset['domain'] == domain
                x = self.combined_dataset.loc[mask, 'curvature']
                y = self.combined_dataset.loc[mask, 'theta_transformed']
                axes[1,2].scatter(x, y, alpha=0.7, label=domain)
            
            axes[1,2].set_xlabel('Curvature')
            axes[1,2].set_ylabel('Theta Transformed')
            axes[1,2].set_title('Cross-Domain Feature Space')
            axes[1,2].legend()
        
        plt.tight_layout()
        
        # Save visualization
        output_path = self.output_dir / "dataset_overview.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Visualizations saved to: {output_path}")

def main():
    """
    Main execution function for dataset preparation
    """
    print("ML Cross-Validation Dataset Preparation")
    print("=" * 50)
    
    # Initialize preparator
    preparator = DatasetPreparator("datasets")
    
    # Prepare individual datasets
    start_time = time.time()
    
    # 1. Zeta zeros dataset
    zeta_data = preparator.prepare_zeta_zeros_dataset(n_zeros=100, n_points=150)
    
    # 2. GUE metrics dataset  
    gue_data = preparator.prepare_gue_metrics_dataset(n_matrices=150, matrix_size=15)
    
    # 3. CRISPR metrics dataset
    crispr_data = preparator.prepare_crispr_metrics_dataset(n_sequences=100)
    
    # 4. Combine datasets
    combined_data = preparator.combine_datasets()
    
    # 5. Generate summary report
    summary = preparator.generate_summary_report()
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*50}")
    print("DATASET PREPARATION COMPLETED")
    print(f"{'='*50}")
    print(f"Total time: {elapsed_time:.2f} seconds")
    print(f"Datasets created: {len([d for d in [zeta_data, gue_data, crispr_data, combined_data] if d is not None])}")
    print(f"Total samples: {len(combined_data) if combined_data is not None else 0}")
    print(f"Output directory: datasets/")
    
    print("\nDataset files created:")
    for file_path in Path("datasets").glob("*.csv"):
        size_mb = file_path.stat().st_size / 1024**2
        print(f"  {file_path.name}: {size_mb:.2f} MB")
    
    print("\nNext steps:")
    print("1. Run train_models.py to train ML models")
    print("2. Run run_cross_validation.py for validation")
    print("3. Run generate_report.py for final analysis")

if __name__ == "__main__":
    main()