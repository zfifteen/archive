#!/usr/bin/env python3
"""
ML Model Training Script for Cross-Domain Validation
==================================================

Trains and saves ML models for quantum chaos and biological sequence analysis.
Supports multiple algorithms and hyperparameter optimization.
"""

import sys
import os
import numpy as np
import pandas as pd
import pickle
import json
from pathlib import Path
import time
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error

# Add framework path
sys.path.append('/home/runner/work/unified-framework/unified-framework')
from run_cross_validation import SimplifiedCrossValidator

class MLModelTrainer:
    """
    Comprehensive ML model trainer for cross-domain validation
    """
    
    def __init__(self, output_dir="../models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.models = {}
        self.scalers = {}
        self.training_results = {}
        
        print(f"MLModelTrainer initialized - output: {self.output_dir}")
    
    def train_all_models(self):
        """
        Train comprehensive suite of ML models
        """
        print("Training comprehensive ML model suite...")
        
        # Get data from cross-validator
        validator = SimplifiedCrossValidator()
        quantum_features, quantum_labels, quantum_names = validator.create_quantum_chaos_features(150)
        bio_features, bio_labels, bio_names = validator.create_biological_features(150)
        
        # Train quantum chaos models
        print("\n1. Training quantum chaos models...")
        self._train_domain_models(
            quantum_features, quantum_labels, quantum_names, 
            domain_name="quantum_chaos", task_type="classification"
        )
        
        # Train biological models
        print("\n2. Training biological models...")
        self._train_domain_models(
            bio_features, bio_labels, bio_names,
            domain_name="biological", task_type="classification"
        )
        
        # Train cross-domain models
        print("\n3. Training cross-domain models...")
        self._train_cross_domain_models(quantum_features, bio_features, quantum_labels, bio_labels)
        
        # Save training results
        self._save_training_summary()
        
        return self.training_results
    
    def _train_domain_models(self, features, labels, feature_names, domain_name, task_type="classification"):
        """
        Train models for a specific domain
        """
        # Prepare data
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Store scaler
        self.scalers[domain_name] = scaler
        
        # Define models to train
        if task_type == "classification":
            models_config = {
                'random_forest': (RandomForestClassifier(n_estimators=100, random_state=42), {}),
                'logistic_regression': (LogisticRegression(random_state=42), {'C': [0.1, 1, 10]}),
                'svm': (SVC(random_state=42), {'C': [0.1, 1, 10], 'kernel': ['rbf', 'linear']}),
                'neural_network': (MLPClassifier(random_state=42, max_iter=1000), 
                                 {'hidden_layer_sizes': [(50,), (100,), (50, 25)]})
            }
        else:  # regression
            models_config = {
                'random_forest': (RandomForestRegressor(n_estimators=100, random_state=42), {}),
                'linear_regression': (LinearRegression(), {}),
                'svm': (SVR(), {'C': [0.1, 1, 10], 'kernel': ['rbf', 'linear']}),
                'neural_network': (MLPRegressor(random_state=42, max_iter=1000),
                                 {'hidden_layer_sizes': [(50,), (100,), (50, 25)]})
        }
        
        domain_results = {}
        
        for model_name, (model, param_grid) in models_config.items():
            print(f"  Training {model_name}...")
            
            try:
                if param_grid:
                    # Hyperparameter optimization
                    grid_search = GridSearchCV(model, param_grid, cv=3, scoring='accuracy' if task_type == 'classification' else 'r2')
                    grid_search.fit(features_scaled, labels)
                    best_model = grid_search.best_estimator_
                    best_params = grid_search.best_params_
                else:
                    # No hyperparameter tuning
                    best_model = model
                    best_model.fit(features_scaled, labels)
                    best_params = {}
                
                # Cross-validation evaluation
                cv_scores = cross_val_score(best_model, features_scaled, labels, cv=5)
                
                # Store model and results
                model_key = f"{domain_name}_{model_name}"
                self.models[model_key] = best_model
                
                domain_results[model_name] = {
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'best_params': best_params,
                    'n_features': features.shape[1],
                    'n_samples': len(features)
                }
                
                # Save model
                model_path = self.output_dir / f"{model_key}.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(best_model, f)
                
                print(f"    {model_name}: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
                
            except Exception as e:
                print(f"    Warning: {model_name} training failed: {e}")
                continue
        
        self.training_results[domain_name] = domain_results
        
        # Save scaler
        scaler_path = self.output_dir / f"{domain_name}_scaler.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
    
    def _train_cross_domain_models(self, quantum_features, bio_features, quantum_labels, bio_labels):
        """
        Train models for cross-domain transfer
        """
        # Align feature dimensions
        min_features = min(quantum_features.shape[1], bio_features.shape[1])
        quantum_subset = quantum_features[:, :min_features]
        bio_subset = bio_features[:, :min_features]
        
        cross_results = {}
        
        # Quantum -> Biological transfer
        print("  Training Quantum → Biological transfer...")
        scaler_qb = StandardScaler()
        quantum_scaled = scaler_qb.fit_transform(quantum_subset)
        bio_scaled = scaler_qb.transform(bio_subset)
        
        rf_qb = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_qb.fit(quantum_scaled, quantum_labels)
        
        bio_pred = rf_qb.predict(bio_scaled)
        qb_accuracy = accuracy_score(bio_labels, bio_pred)
        
        # Store cross-domain model
        self.models['quantum_to_biological'] = rf_qb
        self.scalers['quantum_to_biological'] = scaler_qb
        
        model_path = self.output_dir / "quantum_to_biological.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(rf_qb, f)
        
        cross_results['quantum_to_biological'] = {
            'accuracy': qb_accuracy,
            'n_features': min_features
        }
        
        # Biological -> Quantum transfer
        print("  Training Biological → Quantum transfer...")
        scaler_bq = StandardScaler()
        bio_scaled2 = scaler_bq.fit_transform(bio_subset)
        quantum_scaled2 = scaler_bq.transform(quantum_subset)
        
        rf_bq = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_bq.fit(bio_scaled2, bio_labels)
        
        quantum_pred = rf_bq.predict(quantum_scaled2)
        bq_accuracy = accuracy_score(quantum_labels, quantum_pred)
        
        # Store cross-domain model
        self.models['biological_to_quantum'] = rf_bq
        self.scalers['biological_to_quantum'] = scaler_bq
        
        model_path = self.output_dir / "biological_to_quantum.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(rf_bq, f)
        
        cross_results['biological_to_quantum'] = {
            'accuracy': bq_accuracy,
            'n_features': min_features
        }
        
        self.training_results['cross_domain'] = cross_results
        
        print(f"    Quantum → Biological: {qb_accuracy:.3f}")
        print(f"    Biological → Quantum: {bq_accuracy:.3f}")
    
    def _save_training_summary(self):
        """
        Save comprehensive training summary
        """
        summary = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'models_trained': list(self.models.keys()),
            'training_results': self.training_results,
            'model_files': [f.name for f in self.output_dir.glob('*.pkl')],
            'summary_statistics': self._compute_summary_stats()
        }
        
        output_path = self.output_dir / "training_summary.json"
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✓ Training summary saved to: {output_path}")
    
    def _compute_summary_stats(self):
        """
        Compute summary statistics across all models
        """
        all_scores = []
        
        for domain, results in self.training_results.items():
            if domain != 'cross_domain':
                for model, metrics in results.items():
                    all_scores.append(metrics.get('cv_mean', 0))
        
        return {
            'mean_performance': np.mean(all_scores) if all_scores else 0,
            'std_performance': np.std(all_scores) if all_scores else 0,
            'n_models': len(self.models),
            'best_model': max(self.models.keys(), 
                            key=lambda k: self._get_model_score(k)) if self.models else None
        }
    
    def _get_model_score(self, model_key):
        """
        Get performance score for a model
        """
        parts = model_key.split('_')
        if len(parts) >= 2:
            domain = '_'.join(parts[:-1])
            model_name = parts[-1]
            
            if domain in self.training_results and model_name in self.training_results[domain]:
                return self.training_results[domain][model_name].get('cv_mean', 0)
        
        return 0

def main():
    """
    Main training execution
    """
    print("ML Model Training for Cross-Domain Validation")
    print("=" * 50)
    
    trainer = MLModelTrainer()
    
    start_time = time.time()
    
    # Train all models
    results = trainer.train_all_models()
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*50}")
    print("MODEL TRAINING COMPLETED")
    print(f"{'='*50}")
    print(f"Total time: {elapsed_time:.2f} seconds")
    print(f"Models trained: {len(trainer.models)}")
    
    # Summary statistics
    if 'summary_statistics' in results:
        stats = results['summary_statistics']
        print(f"Mean performance: {stats['mean_performance']:.3f} ± {stats['std_performance']:.3f}")
        print(f"Best model: {stats['best_model']}")
    
    print(f"\nModel files saved to: ../models/")
    print("Available for inference and further analysis")

if __name__ == "__main__":
    main()