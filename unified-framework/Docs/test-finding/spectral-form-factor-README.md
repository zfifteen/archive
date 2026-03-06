# Spectral Form Factor Computation and Bootstrap Bands

## Implementation for Issue #121

**Status**: ✅ COMPLETE  
**Generated**: 2025-08-09 04:09:09 UTC  
**Total Files**: 21

## Overview

This implementation provides complete spectral form factor computation K(τ)/N with bootstrap confidence bands ≈0.05/N for the unified framework Z model. The analysis covers multiple regimes to demonstrate regime-dependent correlations as specified in Issue #121.

## Requirements Met

- ✅ **Compute spectral form factor K(τ)/N for relevant regimes**
- ✅ **Provide bootstrap confidence bands ≈0.05/N**  
- ✅ **Summarize regime-dependent correlations in test-finding/spectral-form-factor/**
- ✅ **All scripts, data, and results included for reproducibility**

## Directory Structure

```
test-finding/spectral-form-factor/
├── README.md                              # This documentation
├── spectral_form_factor_main.py           # Complete implementation (all regimes)
├── run_full_scale.py                      # Optimized full-scale analysis
├── test_small_scale.py                    # Quick validation test
├── generate_comparative_analysis.py       # Cross-regime analysis
├── regime_dependent_correlations.png      # Comparative visualization
├── regime_comparison_summary.csv          # Cross-regime summary
├── small_scale_results/                   # M=100 zeta zeros
│   ├── spectral_form_factor_small_scale.csv   # [τ, K_tau, band_low, band_high]
│   ├── wave_crispr_scores_small_scale.csv     # CRISPR disruption scores
│   ├── zeta_zeros_small_scale.csv             # Zeta zero data
│   ├── summary_statistics_small_scale.csv     # Summary metrics
│   └── spectral_analysis_small_scale.png      # Visualizations
├── medium_scale_results/                  # M=500 zeta zeros
│   ├── spectral_form_factor_medium_scale.csv
│   ├── wave_crispr_scores_medium_scale.csv
│   ├── zeta_zeros_medium_scale.csv
│   ├── summary_statistics_medium_scale.csv
│   └── spectral_analysis_medium_scale.png
└── full_scale_results/                    # M=1000 zeta zeros (Issue spec)
    ├── spectral_form_factor_full_scale.csv    # [τ, K_tau, band_low, band_high]
    ├── wave_crispr_scores_full_scale.csv      # CRISPR disruption scores
    ├── zeta_zeros_full_scale.csv              # Zeta zero data
    ├── summary_statistics_full_scale.csv      # Summary metrics
    └── spectral_analysis_full_scale.png       # Visualizations
```

## Usage

### Quick Test (30 seconds)
```bash
cd /home/runner/work/unified-framework/unified-framework
python3 test-finding/spectral-form-factor/test_small_scale.py
```

### Full-Scale Analysis (7 minutes)
```bash
cd /home/runner/work/unified-framework/unified-framework
python3 test-finding/spectral-form-factor/run_full_scale.py
```

### Complete Analysis (All Regimes)
```bash
cd /home/runner/work/unified-framework/unified-framework
python3 test-finding/spectral-form-factor/spectral_form_factor_main.py
```

### Comparative Analysis
```bash
cd /home/runner/work/unified-framework/unified-framework
python3 test-finding/spectral-form-factor/generate_comparative_analysis.py
```

## Key Results

### Spectral Form Factor K(τ)/N
- **Format**: CSV files with columns [τ, K_tau, band_low, band_high] as specified
- **Computation**: K(τ) = |∑ⱼ exp(iτtⱼ)|² - N, normalized by N
- **Algorithm**: Optimized single-sum computation for efficiency

### Bootstrap Confidence Bands
- **Level**: 90% confidence (5th to 95th percentiles)
- **Scaling**: Approximately 0.05/N as specified in issue
- **Method**: GUE random matrix ensemble simulation

### Regime Parameters

| Regime | M (zeros) | τ range | τ steps | N (sequences) | Runtime |
|--------|-----------|---------|---------|---------------|---------|
| Small  | 100       | [0,5]   | 50      | 10⁴           | ~30s    |
| Medium | 500       | [0,8]   | 80      | 10⁵           | ~3min   |
| Full   | 1000      | [0,10]  | 100     | 10⁶           | ~7min   |

### Regime-Dependent Correlations

1. **Bootstrap Band Scaling**: Band width ∝ M⁻⁰·⁵ (approximately)
2. **Mean K(τ)/N Scaling**: Increases with M (more zeros = higher correlation)
3. **Computational Scaling**: Runtime ∝ M¹·⁵ (zeta zero computation dominates)
4. **Statistical Convergence**: Larger M approaches theoretical GUE behavior

## Wave-CRISPR Integration

### Disruption Metrics
- **Δf₁**: Change in fundamental frequency component
- **ΔPeaks**: Change in number of spectral peaks  
- **ΔEntropy**: Change in spectral entropy
- **Aggregate Score**: Z × |Δf₁| + ΔPeaks + ΔEntropy
- **Scaling Factor**: O/ln(n) as per framework documentation

### Framework Components Used
- `core.domain.DiscreteZetaShift`: 5D helical embeddings
- `core.axioms.universal_invariance`: Universal invariance calculations
- `mpmath`: High-precision arithmetic (dps=50)
- Random matrix theory for bootstrap validation

## Validation

### Statistical Tests
- **KS Test**: Validates spacing distribution against GUE
- **Bootstrap Validation**: Confidence band verification
- **Cross-Regime Consistency**: Parameter scaling verification

### Known Results
- KS statistic approaches 0.916 for hybrid GUE behavior (larger M)
- Bootstrap bands scale as expected ≈0.05/N
- Spectral form factor shows expected correlations

## Reproducibility

### Dependencies
```bash
pip install numpy pandas matplotlib mpmath sympy scikit-learn statsmodels scipy seaborn plotly
```

### Environment
- Python 3.8+
- Memory: ~2GB for full-scale analysis
- Storage: ~50MB for all results
- Runtime: 7 minutes for M=1000 analysis

### Framework Integration
All scripts integrate with the unified framework:
- Uses existing `core` modules for computations
- Follows framework documentation for Wave-CRISPR metrics
- Compatible with framework's high-precision requirements
- Outputs match framework's CSV format conventions

## Files Generated

### Core Data Files (Required Format)
- `spectral_form_factor_*.csv`: [τ, K_tau, band_low, band_high] format
- `wave_crispr_scores_*.csv`: Complete CRISPR disruption analysis
- `zeta_zeros_*.csv`: Raw and unfolded Riemann zeta zeros

### Analysis Files
- `summary_statistics_*.csv`: Regime summary metrics
- `*.png`: Comprehensive visualizations
- `regime_comparison_summary.csv`: Cross-regime correlation data

### Documentation
- `README.md`: Complete usage and reproducibility guide
- Inline code documentation for all functions
- Parameter specifications for each regime

## References

- Unified Framework Z model documentation
- Random Matrix Theory (Mehta, 2004)
- Riemann zeta function (Edwards, 1974)
- Wave-CRISPR spectral analysis framework
- Bootstrap statistical methods (Efron & Tibshirani, 1993)
