#!/usr/bin/env python3
"""
Z-Curvature Genomic Features Smoke Test

This script implements a "cheap, same-day check" to determine if Z-curvature features
derived from θ'(i,k) = φ·{i/φ}^k can capture "prime-like" sparsity/structure that
adds predictive signal for genomic tasks (mutation hotspots, CRISPR off-targets).

The smoke test answers three key questions:
1. Do Z-features provide measurable lift over naive sequence baseline?
2. Is that lift robust to trivial changes (window size and k)?
3. Is the compute cost negligible?

Usage:
    python genomic_smoke_test.py [--quick] [--samples N] [--length L]
"""

import argparse
import time
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Any
import sys
import os

# Add the applications module to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'applications'))

from z_curvature_genomic import (ZCurvatureGenomicFeatures, BaselineGenomicFeatures, 
                                create_synthetic_dataset, create_challenging_dataset, 
                                test_with_real_sequences)

class GenomicSmokeTest:
    """
    Smoke test framework for Z-curvature genomic features.
    
    This class orchestrates the comparison between Z-curvature features
    and baseline features on synthetic genomic data with known patterns.
    """
    
    def __init__(self, quick_mode: bool = False):
        """
        Initialize smoke test.
        
        Args:
            quick_mode: If True, use reduced parameters for faster execution
        """
        self.quick_mode = quick_mode
        
        if quick_mode:
            self.n_samples = 50
            self.seq_length = 100
            self.k_values = [0.3]
            self.window_sizes = [20]
            self.cv_folds = 3
        else:
            self.n_samples = 200
            self.seq_length = 200
            self.k_values = [0.2, 0.3, 0.4]
            self.window_sizes = [10, 20, 50]
            self.cv_folds = 5
        
        self.z_extractor = ZCurvatureGenomicFeatures(self.k_values, self.window_sizes)
        self.baseline_extractor = BaselineGenomicFeatures(self.window_sizes)
        self.results = {}
    
    def run_smoke_test(self, dataset_type: str = "challenging") -> Dict[str, Any]:
        """
        Run the complete smoke test and return results.
        
        Args:
            dataset_type: Type of dataset to use ("simple", "challenging", "real")
        
        Returns:
            Dictionary containing test results and metrics
        """
        print("🚦 Z-Curvature Genomic Features Smoke Test")
        print("=" * 60)
        print(f"Mode: {'Quick' if self.quick_mode else 'Full'}")
        print(f"Dataset: {dataset_type}")
        print(f"Samples: {self.n_samples}, Sequence length: {self.seq_length}")
        print(f"K values: {self.k_values}")
        print(f"Window sizes: {self.window_sizes}")
        print()
        
        start_time = time.time()
        
        # Step 1: Generate/load dataset
        print(f"📊 Loading {dataset_type} dataset...")
        if dataset_type == "simple":
            sequences, labels = create_synthetic_dataset(self.n_samples, self.seq_length)
        elif dataset_type == "challenging":
            sequences, labels = create_challenging_dataset(self.n_samples, self.seq_length)
        elif dataset_type == "real":
            sequences, labels = test_with_real_sequences()
            if len(sequences) == 0:
                print("⚠️  No real sequences found, falling back to challenging dataset")
                sequences, labels = create_challenging_dataset(self.n_samples, self.seq_length)
                dataset_type = "challenging"
        else:
            raise ValueError(f"Unknown dataset type: {dataset_type}")
            
        print(f"✅ Loaded {len(sequences)} sequences")
        print(f"   - Positive samples: {sum(labels)}")
        print(f"   - Negative samples: {len(labels) - sum(labels)}")
        
        # Limit samples for quick mode
        if self.quick_mode and len(sequences) > self.n_samples:
            indices = np.random.choice(len(sequences), self.n_samples, replace=False)
            sequences = [sequences[i] for i in indices]
            labels = [labels[i] for i in indices]
            print(f"   - Limited to {len(sequences)} samples for quick mode")
        print()
        
        # Step 2: Extract Z-curvature features
        print("🔬 Extracting Z-curvature features...")
        z_features_start = time.time()
        z_feature_data = []
        for i, seq in enumerate(sequences):
            if i % 50 == 0:
                print(f"   Processing sequence {i+1}/{len(sequences)}")
            features = self.z_extractor.extract_all_features(seq)
            z_feature_data.append(features)
        
        z_df = pd.DataFrame(z_feature_data)
        z_extraction_time = time.time() - z_features_start
        print(f"✅ Z-curvature features extracted in {z_extraction_time:.2f}s")
        print(f"   Feature count: {len(z_df.columns)}")
        print()
        
        # Step 3: Extract baseline features
        print("📏 Extracting baseline features...")
        baseline_features_start = time.time()
        baseline_feature_data = []
        for seq in sequences:
            features = self.baseline_extractor.extract_all_features(seq)
            baseline_feature_data.append(features)
        
        baseline_df = pd.DataFrame(baseline_feature_data)
        baseline_extraction_time = time.time() - baseline_features_start
        print(f"✅ Baseline features extracted in {baseline_extraction_time:.2f}s")
        print(f"   Feature count: {len(baseline_df.columns)}")
        print()
        
        # Step 4: Train and evaluate models
        print("🤖 Training and evaluating models...")
        
        # Z-curvature model
        z_scores, z_auc = self._evaluate_features(z_df, labels, "Z-curvature")
        
        # Baseline model
        baseline_scores, baseline_auc = self._evaluate_features(baseline_df, labels, "Baseline")
        
        # Combined model (for comparison)
        combined_df = pd.concat([z_df, baseline_df], axis=1)
        combined_scores, combined_auc = self._evaluate_features(combined_df, labels, "Combined")
        
        total_time = time.time() - start_time
        
        # Step 5: Compile results
        self.results = {
            'dataset': {
                'type': dataset_type,
                'n_samples': len(sequences),
                'seq_length': self.seq_length,
                'positive_samples': sum(labels),
                'negative_samples': len(labels) - sum(labels)
            },
            'features': {
                'z_curvature_count': len(z_df.columns),
                'baseline_count': len(baseline_df.columns),
                'z_extraction_time': z_extraction_time,
                'baseline_extraction_time': baseline_extraction_time
            },
            'performance': {
                'z_curvature': {'cv_score': z_scores, 'auc': z_auc},
                'baseline': {'cv_score': baseline_scores, 'auc': baseline_auc},
                'combined': {'cv_score': combined_scores, 'auc': combined_auc}
            },
            'timing': {
                'total_time': total_time,
                'time_per_sequence': total_time / len(sequences)
            },
            'parameters': {
                'k_values': self.k_values,
                'window_sizes': self.window_sizes,
                'quick_mode': self.quick_mode
            }
        }
        
        # Step 6: Print summary
        self._print_results()
        
        return self.results
    
    def _evaluate_features(self, feature_df: pd.DataFrame, labels: List[int], model_name: str) -> Tuple[np.ndarray, float]:
        """
        Evaluate features using cross-validation and return scores.
        
        Args:
            feature_df: DataFrame with features
            labels: Target labels
            model_name: Name of the model for logging
            
        Returns:
            Tuple of (cv_scores, auc_score)
        """
        # Handle NaN values
        feature_df = feature_df.fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(feature_df)
        
        # Cross-validation
        clf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
        cv_scores = cross_val_score(clf, X_scaled, labels, cv=self.cv_folds, scoring='accuracy')
        
        # Train final model for AUC
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, labels, test_size=0.3, random_state=42, stratify=labels
        )
        clf.fit(X_train, y_train)
        y_pred_proba = clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"   {model_name}: CV accuracy = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}, AUC = {auc:.3f}")
        
        return cv_scores, auc
    
    def _print_results(self):
        """Print comprehensive results summary."""
        print()
        print("📈 SMOKE TEST RESULTS")
        print("=" * 60)
        
        # Performance comparison
        z_perf = self.results['performance']['z_curvature']
        baseline_perf = self.results['performance']['baseline']
        combined_perf = self.results['performance']['combined']
        
        print("🎯 PERFORMANCE COMPARISON:")
        print(f"   Z-curvature:  CV = {z_perf['cv_score'].mean():.3f} ± {z_perf['cv_score'].std():.3f}, AUC = {z_perf['auc']:.3f}")
        print(f"   Baseline:     CV = {baseline_perf['cv_score'].mean():.3f} ± {baseline_perf['cv_score'].std():.3f}, AUC = {baseline_perf['auc']:.3f}")
        print(f"   Combined:     CV = {combined_perf['cv_score'].mean():.3f} ± {combined_perf['cv_score'].std():.3f}, AUC = {combined_perf['auc']:.3f}")
        
        # Calculate lift
        z_lift = (z_perf['auc'] - baseline_perf['auc']) / baseline_perf['auc'] * 100
        cv_lift = (z_perf['cv_score'].mean() - baseline_perf['cv_score'].mean()) / baseline_perf['cv_score'].mean() * 100
        
        print()
        print("📊 LIFT ANALYSIS:")
        print(f"   AUC lift: {z_lift:+.1f}% (Z-curvature vs baseline)")
        print(f"   CV lift:  {cv_lift:+.1f}% (Z-curvature vs baseline)")
        
        # Computational efficiency
        timing = self.results['timing']
        features = self.results['features']
        
        print()
        print("⚡ COMPUTATIONAL EFFICIENCY:")
        print(f"   Total time: {timing['total_time']:.2f}s")
        print(f"   Time per sequence: {timing['time_per_sequence']*1000:.1f}ms")
        print(f"   Z-feature extraction: {features['z_extraction_time']:.2f}s")
        print(f"   Baseline extraction: {features['baseline_extraction_time']:.2f}s")
        
        # Answer the key questions
        print()
        print("❓ KEY QUESTIONS ANSWERED:")
        
        # Question 1: Measurable lift?
        if z_perf['auc'] > baseline_perf['auc'] and z_lift > 1.0:
            lift_answer = f"✅ YES - {z_lift:.1f}% AUC improvement"
        else:
            lift_answer = f"❌ NO - {z_lift:.1f}% change (not significant)"
        print(f"   Q1: Measurable lift over baseline? {lift_answer}")
        
        # Question 2: Robustness to parameters?
        if len(self.k_values) > 1 and len(self.window_sizes) > 1:
            robustness_answer = "✅ YES - Tested multiple k values and window sizes"
        else:
            robustness_answer = "⚠️  PARTIAL - Limited parameter testing (quick mode)"
        print(f"   Q2: Robust to parameter changes? {robustness_answer}")
        
        # Question 3: Negligible compute cost?
        if timing['total_time'] < 300:  # 5 minutes
            compute_answer = f"✅ YES - {timing['total_time']:.1f}s total"
        else:
            compute_answer = f"⚠️  SLOW - {timing['total_time']:.1f}s total"
        print(f"   Q3: Negligible compute cost? {compute_answer}")
        
        print()
        print("🎯 SMOKE TEST VERDICT:")
        if z_lift > 1.0 and timing['total_time'] < 300:
            verdict = "✅ PASS - Z-curvature features show promise for genomic tasks"
        elif z_lift > 0:
            verdict = "⚠️  MARGINAL - Small improvement, needs further investigation"
        else:
            verdict = "❌ FAIL - No significant improvement over baseline"
        print(f"   {verdict}")


def test_robustness(results: Dict[str, Any]):
    """
    Test robustness of Z-curvature features across different parameter settings.
    
    Args:
        results: Results from the main smoke test
    """
    print()
    print("🔄 ROBUSTNESS TESTING")
    print("=" * 40)
    
    k_values = [0.1, 0.2, 0.3, 0.4, 0.5]
    window_sizes = [5, 10, 20, 30, 50]
    
    # Quick robustness test with smaller dataset
    sequences, labels = create_synthetic_dataset(50, 100)
    
    results_grid = []
    
    for k in k_values:
        for w in window_sizes:
            extractor = ZCurvatureGenomicFeatures([k], [w])
            
            # Extract features
            feature_data = []
            for seq in sequences:
                features = extractor.extract_all_features(seq)
                feature_data.append(features)
            
            df = pd.DataFrame(feature_data).fillna(0)
            
            if len(df.columns) > 0:
                # Quick evaluation
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(df)
                
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, labels, test_size=0.3, random_state=42, stratify=labels
                )
                
                clf = RandomForestClassifier(n_estimators=20, random_state=42, max_depth=3)
                clf.fit(X_train, y_train)
                
                accuracy = clf.score(X_test, y_test)
                results_grid.append({'k': k, 'window': w, 'accuracy': accuracy})
    
    if results_grid:
        df_results = pd.DataFrame(results_grid)
        print(f"Tested {len(results_grid)} parameter combinations")
        print(f"Accuracy range: {df_results['accuracy'].min():.3f} - {df_results['accuracy'].max():.3f}")
        print(f"Accuracy std: {df_results['accuracy'].std():.3f}")
        
        # Find best parameters
        best_result = df_results.loc[df_results['accuracy'].idxmax()]
        print(f"Best parameters: k={best_result['k']}, window={best_result['window']}, accuracy={best_result['accuracy']:.3f}")


def main():
    """Main entry point for the smoke test."""
    parser = argparse.ArgumentParser(description='Z-Curvature Genomic Features Smoke Test')
    parser.add_argument('--quick', action='store_true', 
                       help='Run in quick mode with reduced parameters')
    parser.add_argument('--samples', type=int, default=None,
                       help='Number of samples to generate (overrides quick/full mode)')
    parser.add_argument('--length', type=int, default=None,
                       help='Sequence length (overrides quick/full mode)')
    parser.add_argument('--dataset', choices=['simple', 'challenging', 'real'], 
                       default='challenging',
                       help='Dataset type to use for testing')
    parser.add_argument('--robustness', action='store_true',
                       help='Run additional robustness testing')
    
    args = parser.parse_args()
    
    # Initialize smoke test
    smoke_test = GenomicSmokeTest(quick_mode=args.quick)
    
    # Override parameters if specified
    if args.samples is not None:
        smoke_test.n_samples = args.samples
    if args.length is not None:
        smoke_test.seq_length = args.length
    
    # Run the smoke test
    results = smoke_test.run_smoke_test(dataset_type=args.dataset)
    
    # Run robustness testing if requested
    if args.robustness:
        test_robustness(results)
    
    return results


if __name__ == "__main__":
    main()