# ML Cross-Validation Methodology Report

## Overview
This report documents the cross-domain machine learning validation between quantum chaos metrics and biological sequence features using the Z Framework.

## Datasets

### Quantum Chaos Features
- **Source**: DiscreteZetaShift 5D embeddings and Riemann zeta zero analysis
- **Features**: D, E, F, I, O (from DiscreteZetaShift), amplitude, curvature, theta transformations
- **Target**: Quantum chaos classification based on O value threshold
- **Samples**: ~100 integer sequences (n = 2 to 101)

### Biological Features
- **Source**: Real CRISPR target sequences and synthetic DNA sequences
- **Features**: Length, GC content, dimer/trimer complexity, base frequencies, quantum bridge
- **Target**: CRISPR efficiency classification based on GC content and complexity
- **Samples**: ~100 DNA sequences (50-150 bp)

## Machine Learning Models

### Within-Domain Validation
- **Algorithm**: Random Forest Classifier (100 estimators)
- **Preprocessing**: StandardScaler normalization
- **Validation**: 5-fold cross-validation with 70/30 train-test split
- **Metrics**: Accuracy, cross-validation mean ± std

### Cross-Domain Validation
- **Approach**: Train on one domain, test on another
- **Feature Alignment**: Use minimum common feature count
- **Directions**: Quantum→Biological and Biological→Quantum
- **Hypothesis**: Z Framework enables cross-domain pattern recognition

## Key Results

1. **Within-Domain Performance**: Demonstrates ML models can classify quantum chaos and biological efficiency
2. **Cross-Domain Transfer**: Tests whether quantum mathematical patterns predict biological behavior
3. **Feature Importance**: Identifies which Z Framework components are most predictive
4. **Statistical Significance**: Cross-validation provides confidence intervals

## Z Framework Integration

- **Universal Invariance**: c normalization ensures frame-independent analysis
- **Curvature Transformations**: κ(n) = d(n)·ln(n+1)/e² bridges domains
- **Golden Ratio Modular**: θ'(n,k) = φ·{n/φ}^k reveals hidden patterns
- **5D Embeddings**: (x,y,z,w,u) coordinates provide geometric feature space

## Validation Criteria

- **Success Threshold**: >60% accuracy for within-domain classification
- **Cross-Domain Significance**: >50% accuracy (better than random)
- **Reproducibility**: Results stable across multiple runs
- **Statistical Rigor**: Cross-validation confidence intervals reported

## Limitations

- **Sample Size**: Limited to ~100 samples per domain for computational efficiency
- **Feature Engineering**: Simplified spectral analysis for biological sequences
- **Domain Gap**: Quantum and biological systems have different scales and physics
- **Validation Scope**: Proof-of-concept rather than comprehensive validation

## Future Work

- **Larger Datasets**: Scale to 1000+ samples per domain
- **Advanced Features**: Include full wave-CRISPR spectral analysis
- **Deep Learning**: Neural networks for complex pattern detection
- **Physical Validation**: Test predictions against experimental CRISPR data

## Reproducibility

All code, data, and results are available in the test-finding/ml-cross-validation/ directory:
- `scripts/prepare_datasets.py`: Data generation
- `scripts/train_models.py`: ML model training  
- `scripts/run_cross_validation.py`: Validation pipeline
- `results/`: Output files and visualizations

Execute scripts in order to reproduce all results with identical random seeds.
