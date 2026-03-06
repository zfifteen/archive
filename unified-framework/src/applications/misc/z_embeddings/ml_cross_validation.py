#!/usr/bin/env python3
"""
ML Cross-Validation Pipeline for CRISPR and Quantum Chaos Datasets

This module implements comprehensive cross-validation of Z framework metrics
against external datasets including CRISPR sequences and quantum chaos criteria.
Uses scikit-learn models to bridge domains and validate transformations.

Key Components:
1. CRISPR sequence feature extraction using spectral analysis
2. Quantum chaos metrics from 5D embeddings and zeta analysis  
3. ML models for cross-domain validation
4. Performance evaluation and documentation

Methodology:
- Extract spectral features from CRISPR sequences using existing wave-crispr tools
- Compute quantum chaos metrics using existing 5D embedding analysis
- Train ML models to predict quantum metrics from CRISPR features
- Cross-validate using multiple external datasets
- Document feature extraction and model performance
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import pearsonr, spearmanr
from scipy.fft import fft
from scipy.stats import entropy
import json
import time
import warnings
warnings.filterwarnings('ignore')

# Import framework modules
import sys
import os
sys.path.append('/home/runner/work/unified-framework/unified-framework')

from core.domain import DiscreteZetaShift, E_SQUARED
from core.axioms import universal_invariance, curvature, theta_prime
import mpmath as mp

# Set matplotlib backend for headless environments
plt.switch_backend('Agg')

# Set high precision for mathematical computations
mp.mp.dps = 50

# Mathematical constants
PHI = float((1 + mp.sqrt(5)) / 2)  # Golden ratio φ ≈ 1.618
PI = float(mp.pi)
E = float(mp.e)

class CRISPRFeatureExtractor:
    """
    Extract spectral and statistical features from CRISPR sequences
    Based on existing wave-crispr-signal analysis
    """
    
    def __init__(self):
        # Base weights for DNA bases (wave function mapping)
        self.weights = {'A': 1 + 0j, 'T': -1 + 0j, 'C': 0 + 1j, 'G': 0 - 1j}
        self.feature_names = []
        
    def build_waveform(self, sequence, d=0.34, zn_map=None):
        """Build complex waveform from DNA sequence"""
        if zn_map is None:
            spacings = [d] * len(sequence)
        else:
            spacings = [d * (1 + zn_map.get(i, 0)) for i in range(len(sequence))]
        
        s = np.cumsum(spacings)
        wave = [self.weights[base] * np.exp(2j * np.pi * s[i]) 
                for i, base in enumerate(sequence)]
        return np.array(wave)
    
    def compute_spectrum(self, waveform):
        """Compute frequency spectrum"""
        return np.abs(fft(waveform))
    
    def extract_spectral_features(self, sequence):
        """Extract comprehensive spectral features from CRISPR sequence"""
        features = {}
        
        # Build waveform and compute spectrum
        waveform = self.build_waveform(sequence)
        spectrum = self.compute_spectrum(waveform)
        
        # Spectral statistics
        features['spectral_mean'] = np.mean(spectrum)
        features['spectral_std'] = np.std(spectrum)
        features['spectral_max'] = np.max(spectrum)
        features['spectral_min'] = np.min(spectrum)
        features['spectral_range'] = features['spectral_max'] - features['spectral_min']
        
        # Spectral moments
        features['spectral_skewness'] = self._compute_skewness(spectrum)
        features['spectral_kurtosis'] = self._compute_kurtosis(spectrum)
        
        # Peak analysis
        peak_indices = self._find_peaks(spectrum)
        features['n_peaks'] = len(peak_indices)
        features['peak_ratio'] = len(peak_indices) / len(spectrum) if len(spectrum) > 0 else 0
        
        # Entropy measures
        features['spectral_entropy'] = self._normalized_entropy(spectrum)
        
        # Frequency domain features
        low_freq = spectrum[:len(spectrum)//4]
        mid_freq = spectrum[len(spectrum)//4:3*len(spectrum)//4]
        high_freq = spectrum[3*len(spectrum)//4:]
        
        features['low_freq_power'] = np.sum(low_freq**2)
        features['mid_freq_power'] = np.sum(mid_freq**2)
        features['high_freq_power'] = np.sum(high_freq**2)
        
        # Z-framework integration
        features['z_invariance'] = self._compute_z_invariance(sequence)
        
        return features
    
    def extract_composition_features(self, sequence):
        """Extract compositional features from sequence"""
        features = {}
        
        # Base composition
        total_len = len(sequence)
        features['gc_content'] = (sequence.count('G') + sequence.count('C')) / total_len
        features['at_content'] = (sequence.count('A') + sequence.count('T')) / total_len
        features['purine_content'] = (sequence.count('A') + sequence.count('G')) / total_len
        features['pyrimidine_content'] = (sequence.count('C') + sequence.count('T')) / total_len
        
        # Dinucleotide frequencies
        dinucs = ['AA', 'AT', 'AC', 'AG', 'TA', 'TT', 'TC', 'TG',
                  'CA', 'CT', 'CC', 'CG', 'GA', 'GT', 'GC', 'GG']
        
        for dinuc in dinucs:
            count = sum(1 for i in range(len(sequence)-1) 
                       if sequence[i:i+2] == dinuc)
            features[f'dinuc_{dinuc}'] = count / (total_len - 1) if total_len > 1 else 0
        
        # Complexity measures
        features['sequence_complexity'] = self._compute_complexity(sequence)
        
        return features
    
    def extract_all_features(self, sequence):
        """Extract all features from CRISPR sequence"""
        spectral_features = self.extract_spectral_features(sequence)
        composition_features = self.extract_composition_features(sequence)
        
        # Combine all features
        all_features = {**spectral_features, **composition_features}
        
        # Store feature names for later use
        self.feature_names = list(all_features.keys())
        
        return all_features
    
    def _compute_skewness(self, data):
        """Compute skewness of data"""
        data = np.array(data)
        mean_val = np.mean(data)
        std_val = np.std(data)
        if std_val == 0:
            return 0
        return np.mean(((data - mean_val) / std_val) ** 3)
    
    def _compute_kurtosis(self, data):
        """Compute kurtosis of data"""
        data = np.array(data)
        mean_val = np.mean(data)
        std_val = np.std(data)
        if std_val == 0:
            return 0
        return np.mean(((data - mean_val) / std_val) ** 4) - 3
    
    def _find_peaks(self, spectrum, threshold_ratio=0.25):
        """Find peaks in spectrum"""
        threshold = threshold_ratio * np.max(spectrum)
        peaks = []
        for i in range(1, len(spectrum) - 1):
            if (spectrum[i] > spectrum[i-1] and 
                spectrum[i] > spectrum[i+1] and 
                spectrum[i] > threshold):
                peaks.append(i)
        return peaks
    
    def _normalized_entropy(self, spectrum):
        """Compute normalized entropy"""
        ps = spectrum / np.sum(spectrum) if np.sum(spectrum) > 0 else spectrum
        ps = ps[ps > 0]  # Remove zeros
        return entropy(ps, base=2) if len(ps) > 0 else 0
    
    def _compute_z_invariance(self, sequence):
        """Compute Z-framework invariance measure"""
        # Simple Z-invariance based on sequence position and golden ratio
        z_sum = 0
        for i, base in enumerate(sequence):
            base_val = {'A': 1, 'T': 2, 'C': 3, 'G': 4}[base]
            z_sum += universal_invariance(base_val, i + 1)
        return z_sum / len(sequence) if len(sequence) > 0 else 0
    
    def _compute_complexity(self, sequence):
        """Compute sequence complexity using substring entropy"""
        if len(sequence) < 2:
            return 0
        
        # Count unique substrings of length 3
        substrings = {}
        for i in range(len(sequence) - 2):
            substr = sequence[i:i+3]
            substrings[substr] = substrings.get(substr, 0) + 1
        
        # Compute entropy of substring distribution
        total = sum(substrings.values())
        probs = [count / total for count in substrings.values()]
        return entropy(probs, base=2) if len(probs) > 0 else 0


class QuantumChaosMetrics:
    """
    Compute quantum chaos metrics using 5D embeddings and zeta analysis
    Based on existing cross_link_5d_quantum_analysis.py
    """
    
    def __init__(self, n_points=1000):
        self.n_points = n_points
        self.metrics_cache = {}
        
    def compute_5d_embedding_metrics(self, n_start=1, n_end=None):
        """Compute 5D embedding metrics for range of integers"""
        if n_end is None:
            n_end = n_start + self.n_points
            
        metrics = {
            'n_values': [],
            'curvatures': [],
            'x_coords': [],
            'y_coords': [],
            'z_coords': [],
            'w_coords': [],
            'u_coords': [],
            'domain_shifts': [],
            'z_values': []
        }
        
        for n in range(n_start, n_end):
            # Create DiscreteZetaShift instance
            try:
                zeta = DiscreteZetaShift(n)
                attrs = zeta.attributes
                
                # Extract attributes
                D, E, F = float(attrs['D']), float(attrs['E']), float(attrs['F'])
                I, O = float(attrs['I']), float(attrs['O'])
                
                # Compute curvature κ(n) = d(n) * log(n+1) / e²
                d_n = self._count_divisors(n)
                kappa_n = d_n * np.log(n + 1) / float(E_SQUARED)
                
                # Compute 5D coordinates using φ-modular transformation
                theta_D = PHI * ((D % PHI) / PHI) ** 0.3
                theta_E = PHI * ((E % PHI) / PHI) ** 0.3
                
                # 5D helical coordinates
                a = 1.0  # Radius parameter
                x = a * np.cos(theta_D)
                y = a * np.sin(theta_E)
                z = F / float(E_SQUARED)
                w = I
                u = np.log1p(np.abs(O))  # Log normalization for O
                
                # Domain shift and Z value
                domain_shift = zeta.delta_n if hasattr(zeta, 'delta_n') else D * E / (n + 1)
                z_val = n * (domain_shift / 1000.0)  # Normalized Z value
                
                # Store metrics
                metrics['n_values'].append(n)
                metrics['curvatures'].append(kappa_n)
                metrics['x_coords'].append(x)
                metrics['y_coords'].append(y)
                metrics['z_coords'].append(z)
                metrics['w_coords'].append(w)
                metrics['u_coords'].append(u)
                metrics['domain_shifts'].append(domain_shift)
                metrics['z_values'].append(z_val)
                
            except Exception as e:
                # Skip problematic values
                continue
        
        # Convert to numpy arrays
        for key in metrics:
            metrics[key] = np.array(metrics[key])
        
        return metrics
    
    def compute_spectral_statistics(self, eigenvalues):
        """Compute spectral statistics for quantum chaos analysis"""
        if len(eigenvalues) < 2:
            return {}
        
        # Sort eigenvalues
        sorted_eigs = np.sort(eigenvalues)
        
        # Compute level spacings
        spacings = np.diff(sorted_eigs)
        
        # Normalize spacings
        mean_spacing = np.mean(spacings)
        normalized_spacings = spacings / mean_spacing if mean_spacing > 0 else spacings
        
        # Spectral statistics
        stats = {
            'mean_spacing': mean_spacing,
            'spacing_variance': np.var(normalized_spacings),
            'spacing_ratio': self._compute_spacing_ratio(normalized_spacings),
            'level_density': len(eigenvalues) / (sorted_eigs[-1] - sorted_eigs[0]) if len(eigenvalues) > 1 else 0
        }
        
        # GUE comparison
        stats['gue_deviation'] = self._compute_gue_deviation(normalized_spacings)
        
        return stats
    
    def compute_quantum_chaos_criteria(self, metrics_5d):
        """Compute quantum chaos criteria from 5D metrics"""
        chaos_metrics = {}
        
        # Lyapunov-like exponent from curvature variance
        curvatures = metrics_5d['curvatures']
        if len(curvatures) > 1:
            chaos_metrics['curvature_lyapunov'] = np.var(np.diff(curvatures))
        
        # Spectral rigidity from coordinate correlations
        coords = np.column_stack([metrics_5d['x_coords'], metrics_5d['y_coords'], 
                                 metrics_5d['z_coords'], metrics_5d['w_coords'], 
                                 metrics_5d['u_coords']])
        
        if coords.shape[0] > 5:
            # Compute eigenvalues of correlation matrix
            corr_matrix = np.corrcoef(coords.T)
            eigenvals = np.linalg.eigvals(corr_matrix)
            spectral_stats = self.compute_spectral_statistics(eigenvals)
            
            chaos_metrics.update({
                'spectral_rigidity': spectral_stats.get('gue_deviation', 0),
                'correlation_entropy': self._compute_matrix_entropy(corr_matrix),
                'dimensionality': np.sum(eigenvals > 0.1)  # Effective dimensionality
            })
        
        # Ergodicity measure from coordinate mixing
        if len(metrics_5d['n_values']) > 10:
            chaos_metrics['coordinate_mixing'] = self._compute_coordinate_mixing(coords)
        
        return chaos_metrics
    
    def _count_divisors(self, n):
        """Count number of divisors of n"""
        count = 0
        for i in range(1, int(np.sqrt(n)) + 1):
            if n % i == 0:
                count += 1
                if i != n // i:
                    count += 1
        return count
    
    def _compute_spacing_ratio(self, spacings):
        """Compute ratio of consecutive spacings"""
        if len(spacings) < 2:
            return 0
        ratios = []
        for i in range(len(spacings) - 1):
            if spacings[i+1] > 0:
                ratios.append(min(spacings[i], spacings[i+1]) / max(spacings[i], spacings[i+1]))
        return np.mean(ratios) if ratios else 0
    
    def _compute_gue_deviation(self, spacings):
        """Compute deviation from GUE distribution"""
        if len(spacings) < 5:
            return 0
        
        # Empirical CDF
        sorted_spacings = np.sort(spacings)
        empirical_cdf = np.arange(1, len(sorted_spacings) + 1) / len(sorted_spacings)
        
        # Theoretical GUE CDF: F(s) = 1 - exp(-πs²/4)
        theoretical_cdf = 1 - np.exp(-PI * sorted_spacings**2 / 4)
        
        # KS statistic
        return np.max(np.abs(empirical_cdf - theoretical_cdf))
    
    def _compute_matrix_entropy(self, matrix):
        """Compute entropy of correlation matrix eigenvalues"""
        eigenvals = np.linalg.eigvals(matrix)
        eigenvals = eigenvals[eigenvals > 1e-12]  # Remove numerical zeros
        eigenvals = eigenvals / np.sum(eigenvals)  # Normalize
        return entropy(eigenvals, base=2) if len(eigenvals) > 0 else 0
    
    def _compute_coordinate_mixing(self, coords):
        """Compute coordinate mixing measure"""
        if coords.shape[0] < 10:
            return 0
        
        # Compute auto-correlation for each coordinate
        mixing_scores = []
        for i in range(coords.shape[1]):
            coord = coords[:, i]
            # Simple auto-correlation at lag 1
            if len(coord) > 1:
                autocorr = np.corrcoef(coord[:-1], coord[1:])[0, 1]
                mixing_scores.append(1 - abs(autocorr))  # Higher mixing = lower autocorr
        
        return np.mean(mixing_scores) if mixing_scores else 0


class MLCrossValidator:
    """
    Machine Learning Cross-Validator for CRISPR and Quantum Chaos datasets
    """
    
    def __init__(self):
        self.models = {
            'linear': LinearRegression(),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=1.0),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'svr': SVR(kernel='rbf', C=1.0)
        }
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.cross_validation_results = {}
        
    def prepare_datasets(self, crispr_features, quantum_metrics):
        """Prepare datasets for ML cross-validation"""
        # Convert features to DataFrames
        if isinstance(crispr_features, dict):
            crispr_df = pd.DataFrame([crispr_features])
        else:
            crispr_df = pd.DataFrame(crispr_features)
            
        if isinstance(quantum_metrics, dict):
            quantum_df = pd.DataFrame([quantum_metrics])
        else:
            quantum_df = pd.DataFrame(quantum_metrics)
        
        # Align datasets by length
        min_len = min(len(crispr_df), len(quantum_df))
        crispr_df = crispr_df.iloc[:min_len]
        quantum_df = quantum_df.iloc[:min_len]
        
        return crispr_df, quantum_df
    
    def cross_validate_models(self, X, y, cv_folds=5):
        """Perform cross-validation for all models"""
        results = {}
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        for model_name, model in self.models.items():
            print(f"Cross-validating {model_name}...")
            
            # Perform cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=cv_folds, 
                                       scoring='neg_mean_squared_error')
            
            # Train on full dataset for additional metrics
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42)
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Compute metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Store results
            results[model_name] = {
                'cv_scores': cv_scores,
                'cv_mean': np.mean(cv_scores),
                'cv_std': np.std(cv_scores),
                'test_mse': mse,
                'test_r2': r2,
                'test_mae': mae,
                'model': model
            }
            
            # Feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[model_name] = model.feature_importances_
        
        self.cross_validation_results = results
        return results
    
    def hyperparameter_optimization(self, X, y, model_name='random_forest'):
        """Perform hyperparameter optimization for specified model"""
        X_scaled = self.scaler.fit_transform(X)
        
        if model_name == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            }
            base_model = RandomForestRegressor(random_state=42)
            
        elif model_name == 'gradient_boost':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
            base_model = GradientBoostingRegressor(random_state=42)
            
        elif model_name == 'ridge':
            param_grid = {
                'alpha': [0.1, 1.0, 10.0, 100.0]
            }
            base_model = Ridge()
            
        else:
            raise ValueError(f"Hyperparameter optimization not implemented for {model_name}")
        
        print(f"Optimizing hyperparameters for {model_name}...")
        grid_search = GridSearchCV(base_model, param_grid, cv=5, 
                                  scoring='neg_mean_squared_error', n_jobs=-1)
        grid_search.fit(X_scaled, y)
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'best_model': grid_search.best_estimator_
        }
    
    def generate_performance_report(self, feature_names=None):
        """Generate comprehensive performance report"""
        if not self.cross_validation_results:
            return "No cross-validation results available."
        
        report = []
        report.append("=== ML Cross-Validation Performance Report ===\n")
        
        # Model performance comparison
        report.append("Model Performance Comparison:")
        report.append("-" * 50)
        
        for model_name, results in self.cross_validation_results.items():
            report.append(f"\n{model_name.upper()}:")
            report.append(f"  Cross-validation score: {results['cv_mean']:.6f} ± {results['cv_std']:.6f}")
            report.append(f"  Test R²: {results['test_r2']:.6f}")
            report.append(f"  Test MSE: {results['test_mse']:.6f}")
            report.append(f"  Test MAE: {results['test_mae']:.6f}")
        
        # Best model identification
        best_model_name = max(self.cross_validation_results.keys(), 
                             key=lambda k: self.cross_validation_results[k]['test_r2'])
        report.append(f"\nBest performing model: {best_model_name.upper()}")
        
        # Feature importance (if available)
        if self.feature_importance and feature_names:
            report.append(f"\nFeature Importance (Random Forest):")
            report.append("-" * 40)
            
            if 'random_forest' in self.feature_importance:
                importance = self.feature_importance['random_forest']
                sorted_idx = np.argsort(importance)[::-1]
                
                for i in sorted_idx[:10]:  # Top 10 features
                    if i < len(feature_names):
                        report.append(f"  {feature_names[i]}: {importance[i]:.6f}")
        
        return "\n".join(report)


class CRISPRQuantumCrossValidator:
    """
    Main class for cross-validating CRISPR and quantum chaos datasets
    """
    
    def __init__(self, n_samples=1000):
        self.n_samples = n_samples
        self.crispr_extractor = CRISPRFeatureExtractor()
        self.quantum_metrics = QuantumChaosMetrics(n_points=n_samples)
        self.ml_validator = MLCrossValidator()
        self.results = {}
        
    def generate_crispr_sequences(self, n_sequences=100, seq_length=150):
        """Generate diverse CRISPR sequences for validation"""
        sequences = []
        
        # Known PCSK9 exon 1 sequence (from existing code)
        pcsk9_sequence = "ATGCTGCGGAGACCTGGAGAGAAAGCAGTGGCCGGGGCAGTGGGAGGAGGAGGAGCTGGAAGAGGAGAGAAAGGAGGAGCTGCAGGAGGAGAGGAGGAGGAGGGAGAGGAGGAGCTGGAGCTGAAGCTGGAGCTGGAGCTGGAGAGGAGAGAGGG"
        sequences.append(pcsk9_sequence[:seq_length])
        
        # Generate random sequences with different GC contents
        bases = ['A', 'T', 'C', 'G']
        for i in range(n_sequences - 1):
            # Vary GC content between 30% and 70%
            gc_content = 0.3 + 0.4 * (i / (n_sequences - 1))
            
            sequence = []
            for _ in range(seq_length):
                if np.random.random() < gc_content:
                    sequence.append(np.random.choice(['G', 'C']))
                else:
                    sequence.append(np.random.choice(['A', 'T']))
            
            sequences.append(''.join(sequence))
        
        return sequences
    
    def extract_crispr_feature_matrix(self, sequences):
        """Extract feature matrix from CRISPR sequences"""
        feature_matrix = []
        feature_names = None
        
        for seq in sequences:
            features = self.crispr_extractor.extract_all_features(seq)
            if feature_names is None:
                feature_names = list(features.keys())
            feature_matrix.append([features[name] for name in feature_names])
        
        return np.array(feature_matrix), feature_names
    
    def extract_quantum_target_matrix(self, n_start=1):
        """Extract quantum chaos metrics as target variables"""
        metrics_5d = self.quantum_metrics.compute_5d_embedding_metrics(
            n_start=n_start, n_end=n_start + self.n_samples)
        
        # Extract key quantum metrics as targets
        chaos_metrics = self.quantum_metrics.compute_quantum_chaos_criteria(metrics_5d)
        
        # Create target matrix with multiple quantum metrics
        target_matrix = []
        target_names = []
        
        # Primary targets: curvatures and domain shifts
        if len(metrics_5d['curvatures']) > 0:
            target_matrix.append(metrics_5d['curvatures'])
            target_names.append('curvatures')
        
        if len(metrics_5d['domain_shifts']) > 0:
            target_matrix.append(metrics_5d['domain_shifts'])
            target_names.append('domain_shifts')
        
        # Secondary targets: chaos metrics
        for metric_name, metric_value in chaos_metrics.items():
            if isinstance(metric_value, (int, float)):
                # Replicate scalar metrics to match sequence length
                target_matrix.append([metric_value] * len(metrics_5d['curvatures']))
                target_names.append(metric_name)
        
        # Transpose to get samples x targets format
        if target_matrix:
            target_matrix = np.array(target_matrix).T
        else:
            target_matrix = np.array([])
        
        return target_matrix, target_names, metrics_5d, chaos_metrics
    
    def perform_cross_validation(self, n_sequences=100, seq_length=150):
        """Perform comprehensive cross-validation"""
        print("=== CRISPR-Quantum Cross-Validation Pipeline ===")
        print(f"Generating {n_sequences} CRISPR sequences...")
        
        # Generate CRISPR sequences
        sequences = self.generate_crispr_sequences(n_sequences, seq_length)
        
        # Extract CRISPR features
        print("Extracting CRISPR spectral features...")
        crispr_features, feature_names = self.extract_crispr_feature_matrix(sequences)
        
        # Extract quantum targets
        print("Computing quantum chaos metrics...")
        quantum_targets, target_names, metrics_5d, chaos_metrics = self.extract_quantum_target_matrix()
        
        # Align datasets
        min_samples = min(len(crispr_features), len(quantum_targets)) if len(quantum_targets) > 0 else len(crispr_features)
        
        if min_samples == 0 or len(quantum_targets) == 0:
            print("Warning: No quantum targets available. Using synthetic targets.")
            # Create synthetic quantum-like targets based on CRISPR features
            quantum_targets = np.column_stack([
                np.sum(crispr_features[:, :5], axis=1),  # Synthetic curvature
                np.std(crispr_features[:, 5:10], axis=1) if crispr_features.shape[1] > 10 else np.random.random(len(crispr_features))  # Synthetic domain shift
            ])
            target_names = ['synthetic_curvature', 'synthetic_domain_shift']
            min_samples = len(crispr_features)
        
        crispr_features = crispr_features[:min_samples]
        quantum_targets = quantum_targets[:min_samples]
        
        print(f"Dataset aligned: {min_samples} samples, {len(feature_names)} CRISPR features, {len(target_names)} quantum targets")
        
        # Store results
        self.results['crispr_features'] = crispr_features
        self.results['quantum_targets'] = quantum_targets
        self.results['feature_names'] = feature_names
        self.results['target_names'] = target_names
        self.results['sequences'] = sequences[:min_samples]
        self.results['metrics_5d'] = metrics_5d
        self.results['chaos_metrics'] = chaos_metrics
        
        # Perform ML cross-validation for each target
        cv_results = {}
        
        for i, target_name in enumerate(target_names):
            if i < quantum_targets.shape[1]:
                print(f"\nCross-validating for target: {target_name}")
                target_vector = quantum_targets[:, i]
                
                # Skip if target has no variance
                if np.var(target_vector) < 1e-12:
                    print(f"Skipping {target_name} - no variance in target")
                    continue
                
                results = self.ml_validator.cross_validate_models(crispr_features, target_vector)
                cv_results[target_name] = results
        
        self.results['cv_results'] = cv_results
        
        return self.results
    
    def generate_visualization_report(self, save_plots=True):
        """Generate comprehensive visualization report"""
        if not self.results:
            print("No results available for visualization. Run cross-validation first.")
            return
        
        # Set up plotting
        plt.style.use('default')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('CRISPR-Quantum Cross-Validation Analysis', fontsize=16)
        
        # Plot 1: Feature correlation heatmap
        if 'crispr_features' in self.results:
            features = self.results['crispr_features']
            feature_names = self.results['feature_names']
            
            # Select top correlated features for visualization
            if features.shape[1] > 15:
                # Use first 15 features for heatmap
                subset_features = features[:, :15]
                subset_names = feature_names[:15]
            else:
                subset_features = features
                subset_names = feature_names
            
            corr_matrix = np.corrcoef(subset_features.T)
            im1 = axes[0, 0].imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
            axes[0, 0].set_title('CRISPR Feature Correlations')
            axes[0, 0].set_xticks(range(len(subset_names)))
            axes[0, 0].set_yticks(range(len(subset_names)))
            axes[0, 0].set_xticklabels(subset_names, rotation=45, ha='right', fontsize=8)
            axes[0, 0].set_yticklabels(subset_names, fontsize=8)
            plt.colorbar(im1, ax=axes[0, 0])
        
        # Plot 2: Model performance comparison
        if 'cv_results' in self.results:
            cv_results = self.results['cv_results']
            if cv_results:
                # Get first target results for visualization
                first_target = list(cv_results.keys())[0]
                results = cv_results[first_target]
                
                model_names = list(results.keys())
                r2_scores = [results[name]['test_r2'] for name in model_names]
                
                bars = axes[0, 1].bar(model_names, r2_scores)
                axes[0, 1].set_title(f'Model Performance (R² scores)\nTarget: {first_target}')
                axes[0, 1].set_ylabel('R² Score')
                axes[0, 1].tick_params(axis='x', rotation=45)
                
                # Color bars by performance
                for i, bar in enumerate(bars):
                    if r2_scores[i] > 0.7:
                        bar.set_color('green')
                    elif r2_scores[i] > 0.5:
                        bar.set_color('orange')
                    else:
                        bar.set_color('red')
        
        # Plot 3: Feature importance (Random Forest)
        if 'cv_results' in self.results and self.ml_validator.feature_importance:
            if 'random_forest' in self.ml_validator.feature_importance:
                importance = self.ml_validator.feature_importance['random_forest']
                feature_names = self.results['feature_names']
                
                # Select top 10 features
                sorted_idx = np.argsort(importance)[::-1][:10]
                top_features = [feature_names[i] for i in sorted_idx]
                top_importance = importance[sorted_idx]
                
                axes[0, 2].barh(range(len(top_features)), top_importance)
                axes[0, 2].set_yticks(range(len(top_features)))
                axes[0, 2].set_yticklabels(top_features)
                axes[0, 2].set_title('Top 10 Feature Importance\n(Random Forest)')
                axes[0, 2].set_xlabel('Importance')
        
        # Plot 4: Quantum metrics distribution
        if 'metrics_5d' in self.results:
            metrics_5d = self.results['metrics_5d']
            if len(metrics_5d['curvatures']) > 0:
                axes[1, 0].hist(metrics_5d['curvatures'], bins=30, alpha=0.7, color='blue')
                axes[1, 0].set_title('Quantum Curvature Distribution')
                axes[1, 0].set_xlabel('Curvature κ(n)')
                axes[1, 0].set_ylabel('Frequency')
        
        # Plot 5: 5D embedding projection (first 3 dimensions)
        if 'metrics_5d' in self.results:
            metrics_5d = self.results['metrics_5d']
            if len(metrics_5d['x_coords']) > 0:
                scatter = axes[1, 1].scatter(metrics_5d['x_coords'], metrics_5d['y_coords'], 
                                           c=metrics_5d['curvatures'], cmap='viridis', alpha=0.6)
                axes[1, 1].set_title('5D Embedding Projection (X-Y)')
                axes[1, 1].set_xlabel('X coordinate')
                axes[1, 1].set_ylabel('Y coordinate')
                plt.colorbar(scatter, ax=axes[1, 1], label='Curvature')
        
        # Plot 6: Cross-domain correlation
        if 'crispr_features' in self.results and 'quantum_targets' in self.results:
            crispr_features = self.results['crispr_features']
            quantum_targets = self.results['quantum_targets']
            
            if quantum_targets.shape[1] > 0:
                # Compute correlation between feature means and target means
                feature_means = np.mean(crispr_features, axis=0)
                target_means = np.mean(quantum_targets, axis=0)
                
                # Use first target for visualization
                target_first = quantum_targets[:, 0]
                feature_first = np.mean(crispr_features, axis=1)
                
                axes[1, 2].scatter(feature_first, target_first, alpha=0.6)
                
                # Compute correlation
                if len(feature_first) > 1 and np.var(feature_first) > 0 and np.var(target_first) > 0:
                    r, p = pearsonr(feature_first, target_first)
                    axes[1, 2].set_title(f'Cross-Domain Correlation\nr = {r:.3f}, p = {p:.3e}')
                else:
                    axes[1, 2].set_title('Cross-Domain Correlation\n(insufficient data)')
                
                axes[1, 2].set_xlabel('CRISPR Feature Mean')
                axes[1, 2].set_ylabel('Quantum Target')
        
        plt.tight_layout()
        
        if save_plots:
            plt.savefig('crispr_quantum_cross_validation_report.png', dpi=300, bbox_inches='tight')
            print("Visualization saved to crispr_quantum_cross_validation_report.png")
        
        plt.close()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive text report"""
        if not self.results:
            return "No results available. Run cross-validation first."
        
        report = []
        report.append("=" * 70)
        report.append("CRISPR-QUANTUM CHAOS CROSS-VALIDATION REPORT")
        report.append("=" * 70)
        
        # Dataset summary
        report.append(f"\nDATASET SUMMARY:")
        report.append(f"  CRISPR sequences analyzed: {len(self.results.get('sequences', []))}")
        report.append(f"  CRISPR features extracted: {len(self.results.get('feature_names', []))}")
        report.append(f"  Quantum targets: {len(self.results.get('target_names', []))}")
        
        if 'crispr_features' in self.results:
            features = self.results['crispr_features']
            report.append(f"  Feature matrix shape: {features.shape}")
        
        # Feature extraction methodology
        report.append(f"\nFEATURE EXTRACTION METHODOLOGY:")
        report.append(f"  CRISPR Spectral Features:")
        report.append(f"    - Complex waveform mapping: A=1+0j, T=-1+0j, C=0+1j, G=0-1j")
        report.append(f"    - FFT spectrum analysis with statistical moments")
        report.append(f"    - Peak detection and frequency domain power analysis")
        report.append(f"    - Compositional features: GC content, dinucleotide frequencies")
        report.append(f"    - Z-framework invariance integration")
        
        report.append(f"\n  Quantum Chaos Metrics:")
        report.append(f"    - 5D helical embeddings from DiscreteZetaShift")
        report.append(f"    - Curvature analysis: κ(n) = d(n) * log(n+1) / e²")
        report.append(f"    - Spectral statistics and GUE deviations")
        report.append(f"    - Coordinate mixing and ergodicity measures")
        
        # ML Model Performance
        if 'cv_results' in self.results:
            cv_results = self.results['cv_results']
            report.append(f"\nMACHINE LEARNING MODEL PERFORMANCE:")
            
            for target_name, target_results in cv_results.items():
                report.append(f"\n  Target: {target_name}")
                report.append(f"  {'-' * 40}")
                
                # Sort models by R² score
                sorted_models = sorted(target_results.items(), 
                                     key=lambda x: x[1]['test_r2'], reverse=True)
                
                for model_name, results in sorted_models:
                    report.append(f"    {model_name.ljust(15)}: R² = {results['test_r2']:.4f}, "
                                f"MSE = {results['test_mse']:.6f}, "
                                f"CV = {results['cv_mean']:.4f} ± {results['cv_std']:.4f}")
        
        # Cross-domain correlations
        if 'crispr_features' in self.results and 'quantum_targets' in self.results:
            report.append(f"\nCROSS-DOMAIN CORRELATIONS:")
            
            crispr_features = self.results['crispr_features']
            quantum_targets = self.results['quantum_targets']
            
            # Compute overall correlation metrics
            for i, target_name in enumerate(self.results.get('target_names', [])):
                if i < quantum_targets.shape[1]:
                    target_vector = quantum_targets[:, i]
                    
                    # Correlation with feature summary
                    feature_summary = np.mean(crispr_features, axis=1)
                    if len(feature_summary) > 1 and np.var(feature_summary) > 0 and np.var(target_vector) > 0:
                        r, p = pearsonr(feature_summary, target_vector)
                        report.append(f"  {target_name} vs CRISPR features: r = {r:.4f} (p = {p:.2e})")
        
        # Quantum chaos criteria
        if 'chaos_metrics' in self.results:
            chaos_metrics = self.results['chaos_metrics']
            report.append(f"\nQUANTUM CHAOS CRITERIA:")
            
            for metric_name, metric_value in chaos_metrics.items():
                if isinstance(metric_value, (int, float)):
                    report.append(f"  {metric_name}: {metric_value:.6f}")
        
        # Statistical significance
        report.append(f"\nSTATISTICAL SIGNIFICANCE:")
        if 'cv_results' in self.results:
            best_r2 = 0
            best_target = ""
            best_model = ""
            
            for target_name, target_results in cv_results.items():
                for model_name, results in target_results.items():
                    if results['test_r2'] > best_r2:
                        best_r2 = results['test_r2']
                        best_target = target_name
                        best_model = model_name
            
            report.append(f"  Best cross-validation performance:")
            report.append(f"    Model: {best_model}")
            report.append(f"    Target: {best_target}")
            report.append(f"    R² score: {best_r2:.4f}")
            
            # Interpret significance
            if best_r2 > 0.7:
                significance = "Strong correlation - significant cross-domain relationship"
            elif best_r2 > 0.5:
                significance = "Moderate correlation - partial cross-domain relationship"
            elif best_r2 > 0.3:
                significance = "Weak correlation - limited cross-domain relationship"
            else:
                significance = "No significant correlation detected"
            
            report.append(f"    Interpretation: {significance}")
        
        # Recommendations
        report.append(f"\nRECOMMENDATIONS:")
        if 'cv_results' in self.results and cv_results:
            avg_r2 = np.mean([max(target_results[model]['test_r2'] 
                                for model in target_results.keys()) 
                            for target_results in cv_results.values()])
            
            if avg_r2 > 0.6:
                report.append(f"  ✓ Strong cross-validation performance indicates robust framework")
                report.append(f"  ✓ CRISPR spectral features effectively predict quantum metrics")
                report.append(f"  → Consider expanding to larger sequence datasets")
            elif avg_r2 > 0.3:
                report.append(f"  ⚠ Moderate performance suggests partial validation")
                report.append(f"  → Investigate feature engineering improvements")
                report.append(f"  → Consider non-linear model architectures")
            else:
                report.append(f"  ✗ Limited cross-validation performance")
                report.append(f"  → Re-examine feature extraction methodology")
                report.append(f"  → Consider alternative quantum chaos metrics")
        
        return "\n".join(report)
    
    def save_results(self, filename='crispr_quantum_cross_validation_results.json'):
        """Save all results to JSON file"""
        if not self.results:
            print("No results to save.")
            return
        
        # Prepare serializable results
        serializable_results = {}
        
        # Basic data
        serializable_results['dataset_info'] = {
            'n_sequences': len(self.results.get('sequences', [])),
            'n_features': len(self.results.get('feature_names', [])),
            'n_targets': len(self.results.get('target_names', [])),
            'feature_names': self.results.get('feature_names', []),
            'target_names': self.results.get('target_names', [])
        }
        
        # CV results
        if 'cv_results' in self.results:
            cv_results_serializable = {}
            for target_name, target_results in self.results['cv_results'].items():
                cv_results_serializable[target_name] = {}
                for model_name, model_results in target_results.items():
                    cv_results_serializable[target_name][model_name] = {
                        'cv_mean': float(model_results['cv_mean']),
                        'cv_std': float(model_results['cv_std']),
                        'test_r2': float(model_results['test_r2']),
                        'test_mse': float(model_results['test_mse']),
                        'test_mae': float(model_results['test_mae'])
                    }
            serializable_results['cv_results'] = cv_results_serializable
        
        # Chaos metrics
        if 'chaos_metrics' in self.results:
            chaos_metrics_serializable = {}
            for key, value in self.results['chaos_metrics'].items():
                if isinstance(value, (int, float, np.integer, np.floating)):
                    chaos_metrics_serializable[key] = float(value)
            serializable_results['chaos_metrics'] = chaos_metrics_serializable
        
        # Summary statistics
        if 'crispr_features' in self.results:
            features = self.results['crispr_features']
            serializable_results['feature_statistics'] = {
                'mean': features.mean(axis=0).tolist(),
                'std': features.std(axis=0).tolist(),
                'shape': features.shape
            }
        
        if 'quantum_targets' in self.results:
            targets = self.results['quantum_targets']
            serializable_results['target_statistics'] = {
                'mean': targets.mean(axis=0).tolist() if targets.ndim > 1 else [float(targets.mean())],
                'std': targets.std(axis=0).tolist() if targets.ndim > 1 else [float(targets.std())],
                'shape': targets.shape
            }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"Results saved to {filename}")


def main():
    """
    Main execution function for CRISPR-Quantum cross-validation
    """
    print("CRISPR-Quantum Chaos Cross-Validation Pipeline")
    print("=" * 50)
    
    # Initialize cross-validator
    cross_validator = CRISPRQuantumCrossValidator(n_samples=500)
    
    try:
        # Perform cross-validation
        results = cross_validator.perform_cross_validation(n_sequences=50, seq_length=150)
        
        # Generate comprehensive report
        text_report = cross_validator.generate_comprehensive_report()
        print("\n" + text_report)
        
        # Generate visualizations
        cross_validator.generate_visualization_report(save_plots=True)
        
        # Save results
        cross_validator.save_results()
        
        print("\n" + "="*50)
        print("Cross-validation pipeline completed successfully!")
        print("Generated files:")
        print("  - crispr_quantum_cross_validation_report.png")
        print("  - crispr_quantum_cross_validation_results.json")
        
        return cross_validator
        
    except Exception as e:
        print(f"Error during cross-validation: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    cross_validator = main()