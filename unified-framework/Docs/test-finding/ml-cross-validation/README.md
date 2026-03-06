# ML Cross-Validation: Quantum Chaos & CRISPR Metrics

This directory contains cross-domain machine learning validation bridging quantum chaos phenomena and CRISPR sequence metrics using the Z Framework.

## Directory Structure

```
ml-cross-validation/
├── README.md                 # This documentation
├── datasets/                 # Generated datasets for ML validation
│   ├── zeta_zeros_dataset.csv
│   ├── gue_metrics_dataset.csv
│   ├── crispr_metrics_dataset.csv
│   └── combined_features.csv
├── models/                   # Trained ML models and configurations
│   ├── quantum_chaos_classifier.pkl
│   ├── crispr_regressor.pkl
│   └── cross_domain_ensemble.pkl
├── notebooks/               # Jupyter notebooks demonstrating analysis
│   ├── 01_data_preparation.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_cross_validation_results.ipynb
├── results/                 # Analysis results and summaries
│   ├── cross_validation_summary.json
│   ├── model_performance_report.md
│   └── validation_plots/
├── scripts/                 # Executable Python scripts
│   ├── prepare_datasets.py
│   ├── train_models.py
│   ├── run_cross_validation.py
│   └── generate_report.py
└── requirements.txt         # Specific dependencies for this module
```

## Overview

This cross-validation implementation validates the Z Framework's capability to bridge:

1. **Quantum Chaos Metrics**: Derived from DiscreteZetaShift 5D embeddings and Riemann zeta zero analysis
2. **CRISPR Sequence Metrics**: Spectral analysis of biological sequences using wave-crispr methodology
3. **GUE Statistics**: Gaussian Unitary Ensemble metrics for random matrix theory validation

## Key Features

- **Cross-Domain ML Models**: Classification and regression models bridging quantum and biological domains
- **Reproducible Workflows**: Automated scripts and detailed notebooks for reproducibility
- **Statistical Validation**: Bootstrap confidence intervals and cross-validation metrics
- **Comprehensive Analysis**: Feature importance, model interpretability, and domain correlation analysis

## Quick Start

1. **Prepare Datasets**:
   ```bash
   cd tests/test-finding/ml-cross-validation/scripts
   python prepare_datasets.py
   ```

2. **Train Models**:
   ```bash
   python train_models.py
   ```

3. **Run Cross-Validation**:
   ```bash
   python run_cross_validation.py
   ```

4. **View Results**:
   ```bash
   python generate_report.py
   ```

## Methodology

The cross-validation approach uses:

- **Z Framework Components**: Universal invariance, curvature transformations, golden ratio modular arithmetic
- **Feature Engineering**: Spectral features from CRISPR sequences, quantum chaos metrics from 5D embeddings
- **ML Models**: Random Forest, Gradient Boosting, SVM, Neural Networks via scikit-learn
- **Validation**: K-fold cross-validation, bootstrap sampling, domain-specific performance metrics

## Expected Results

The validation demonstrates:
- Cross-domain correlation between quantum chaos and biological sequence complexity
- ML model ability to predict quantum metrics from CRISPR features
- Statistical significance of Z Framework transformations across domains
- Reproducible evidence of universal mathematical patterns

## Dependencies

See `requirements.txt` for specific versions. Main dependencies:
- numpy, pandas, scikit-learn
- matplotlib, seaborn (visualization)
- mpmath, sympy (high-precision mathematics)
- scipy, statsmodels (statistical analysis)

## References

- Z Framework documentation: `../../README.md`
- Core mathematical functions: `src/core/`
- Existing ML validation: `src/applications/ml_cross_validation.py`