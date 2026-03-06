# Z-Curvature Genomic Features Smoke Test

This directory contains a complete implementation of a "smoke test" for Z-curvature features applied to genomic tasks. The smoke test evaluates whether simple Z-curvature features derived from θ'(i,k) = φ·{i/φ}^k can capture "prime-like" sparsity/structure that adds predictive signal for genomic tasks such as mutation hotspots and CRISPR off-targets.

## Quick Start

```bash
# Run quick smoke test
python genomic_smoke_test.py --quick

# Run full smoke test with challenging dataset
python genomic_smoke_test.py --dataset challenging

# Run complete comprehensive test suite
python complete_smoke_test.py
```

## Files

- **`src/applications/z_curvature_genomic.py`** - Core Z-curvature feature extraction for genomic sequences
- **`genomic_smoke_test.py`** - Main smoke test framework with multiple dataset types
- **`complete_smoke_test.py`** - Comprehensive test suite that answers all three key questions
- **`z_curvature_smoke_test_results.json`** - Detailed results from the last complete test run

## Smoke Test Questions

The smoke test is designed to answer three critical questions:

1. **Q1: Measurable lift over baseline?** - Do Z-curvature features provide any measurable improvement over naive sequence features?
2. **Q2: Robust to parameter changes?** - Is any lift robust to trivial changes in window size and k values?
3. **Q3: Negligible compute cost?** - Can the analysis run in <5 minutes for practical use?

## Results Summary

Based on the comprehensive smoke test:

- **Q1**: ❌ **NO** - Average -7.2% change across test conditions
- **Q2**: ✅ **YES** - Multiple k values and window sizes tested successfully 
- **Q3**: ✅ **YES** - Maximum time 1.3s, well under 5 minutes

**Overall Verdict**: ❌ **FAIL** - No significant advantage over baseline features

**Recommendation**: Explore alternative approaches or feature engineering methods.

## Implementation Details

### Z-Curvature Features

The implementation extracts features based on the θ'(i,k) = φ·{i/φ}^k transformation:

- **Statistical features**: Mean, std deviation, skewness of θ' values
- **Position-weighted features**: Nucleotide-weighted θ' statistics  
- **Prime-like patterns**: Positions where θ' aligns with golden ratio multiples

### Baseline Features

Simple sequence-based features for comparison:

- **Nucleotide composition**: A, T, C, G frequencies
- **GC content**: Overall and local variability
- **Position statistics**: Numeric sequence properties

### Datasets

1. **Simple**: Basic synthetic data with obvious patterns
2. **Challenging**: Realistic synthetic data with subtle θ'-aligned patterns
3. **Real**: Actual genomic sequences from BRCA1, TP53, CFTR genes

## Usage Examples

```bash
# Quick test with different datasets
python genomic_smoke_test.py --quick --dataset simple
python genomic_smoke_test.py --quick --dataset challenging  
python genomic_smoke_test.py --quick --dataset real

# Full test with robustness analysis
python genomic_smoke_test.py --dataset challenging --robustness

# Custom parameters
python genomic_smoke_test.py --samples 200 --length 300
```

## Technical Notes

- **Compute optimization**: Z-curvature computation optimized from 220s to <1s
- **Feature engineering**: Multiple k values (0.2, 0.3, 0.4) and window sizes (10, 20, 50)
- **Evaluation**: Random Forest classifier with cross-validation and AUC metrics
- **Reproducibility**: Fixed random seeds ensure consistent results

## Conclusion

While the Z-curvature features are computationally efficient and the framework is robust to parameter changes, they do not provide a measurable improvement over simple baseline features for the genomic pattern detection tasks tested. This suggests that either:

1. The specific θ'(i,k) transformation may not be optimal for genomic sequence analysis
2. Different feature engineering approaches may be needed
3. The genomic patterns being tested may not align with the "prime-like" sparsity that Z-curvature features are designed to capture

The smoke test successfully fulfilled its purpose as a "cheap, same-day check" to evaluate the approach before investing in a larger study.