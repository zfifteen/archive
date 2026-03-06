# CRISPR Spectral Resonance Optimization

Optimize CRISPR gRNA prediction using golden-ratio (φ) phase transforms with arcsin phase compression applied to complex DNA waveforms.

## Overview

This application implements a novel approach to CRISPR gRNA on-target activity prediction by:

1. **Complex DNA encoding**: Maps A/T/C/G to complex values (A=1, T=-1, C=+i, G=-i)
2. **φ-phase transform**: Applies position-dependent phase modulation based on golden ratio
3. **Arcsin bridge**: Compresses phases to sharpen spectral peaks
4. **Spectral features**: Extracts ΔEntropy, Δf₁, sidelobe ratios, and more
5. **ML-ready**: Provides invariant features for downstream model training

## Quick Start

### Installation

```bash
# From repository root
pip install -e .
```

### Single Sequence Analysis

```bash
cd src/applications/crispr/applications
python cli.py --sequence ATCGATCGATCGATCGATCG --k 0.300 --alpha 0.95
```

### K-Parameter Sweep

```bash
python cli.py \
  --sequence ATCGATCGATCGATCGATCG \
  --k-sweep \
  --k-min 0.20 \
  --k-max 0.40 \
  --k-step 0.01 \
  --output k_sweep_results.csv
```

### Batch Processing

```bash
# Create sequences.txt with one sequence per line
python cli.py --input sequences.txt --output batch_results.csv
```

### Full Validation Pipeline

```bash
cd src/applications/crispr/proof_pack
python run_validation.py \
  --dataset ../data/sample_guides.tsv \
  --kstar 0.300 \
  --alpha 0.95 \
  --N 256 \
  --window hann \
  --bootstrap 10000 \
  --compare rs3 \
  --out results/validation.json
```

## Python API

```python
from modules.phi_phase import encode_dna_complex, combined_transform
from modules.spectral_features import SpectralFeatureExtractor

# Encode DNA sequence
sequence = "ATCGATCGATCGATCGATCG"
waveform = encode_dna_complex(sequence)

# Apply transforms
phi_transformed, arcsin_compressed, phi_phases = combined_transform(
    waveform, 
    k=0.300,      # φ-phase power parameter
    alpha=0.95    # Arcsin compression factor
)

# Extract spectral features
extractor = SpectralFeatureExtractor(fft_size=256, window_type='hann')
spectrum_base = extractor.compute_spectrum(waveform)
spectrum_final = extractor.compute_spectrum(arcsin_compressed)

features = extractor.extract_all_features(spectrum_base, spectrum_final)

print(f"ΔEntropy: {features['delta_entropy']:.4f}")
print(f"Δf₁: {features['delta_f1']:.2f}%")
print(f"Composite disruption score: {features['composite_disruption_score']:.2f}")
```

## Directory Structure

```
src/applications/crispr/
├── modules/
│   ├── phi_phase.py           # φ-phase and arcsin transforms
│   └── spectral_features.py   # Feature extraction
├── applications/
│   └── cli.py                 # Command-line interface
├── proof_pack/
│   └── run_validation.py      # Validation and benchmarking
├── configs/
│   └── k300.yaml              # Default configuration
├── data/
│   └── sample_guides.tsv      # Sample dataset
├── tests/
│   ├── test_phi_phase.py
│   └── test_spectral_features.py
├── METHODS.md                 # Detailed methodology
└── README.md                  # This file
```

## Configuration

Configuration files use YAML format. Example (`configs/k300.yaml`):

```yaml
encoding:
  A: "1+0j"
  T: "-1+0j"
  C: "0+1j"
  G: "0-1j"

window: hann
N: 256

phi_phase:
  enabled: true
  k: 0.300

arcsin_bridge:
  enabled: true
  alpha: 0.95

bootstrap:
  n_draws: 10000
  stratify_by: locus

random_seeds:
  python: 1337
  numpy: 1337
  torch: 1337

baseline:
  ruleset3:
    provider: rs3
    version: pinned
```

## Features

### Spectral Features

- **ΔEntropy**: Change in spectral entropy (information redistribution)
- **Δf₁**: Change in fundamental frequency peak (%)
- **Δsidelobe**: Change in sidelobe-to-mainlobe ratio
- **MSC**: Magnitude-squared coherence (similarity measure)
- **W₁**: Wasserstein-1 distance (Earth Mover's Distance)
- **SAS**: Sidelobe asymmetry score

### GC Content Analysis

- GC percentage computation
- Quartile assignment (Q1-Q4)
- Correlation analysis with spectral features

### Composite Disruption Score

Weighted combination of features:
```
D = w_entropy · ΔEntropy + w_f1 · |Δf₁| + w_sidelobe · Δsidelobe
```

Default: equal weights (w_entropy = w_f1 = w_sidelobe = 1.0)

## Validation

### Dataset Format

Input datasets should be TSV or CSV with columns:
- `sequence`: gRNA sequence (20-30 bp, ATCG only)
- `activity`: On-target activity score (0-1 scale)
- `locus`: Target locus identifier (for stratification)
- `rs3_score`: (Optional) RuleSet3 baseline score

### Metrics

- **AUC**: Area Under ROC Curve with bootstrap confidence intervals
- **ΔAUC**: Improvement over baseline (RuleSet3)
- **GC correlations**: Pearson and Spearman with FDR correction
- **Feature distributions**: Mean, std, min, max for all features

### Reproducibility

All random operations use fixed seeds (default: 1337):
- Python random
- NumPy random
- PyTorch random (if available)

Environment details (Python version, library versions) are logged in output artifacts.

## Performance

Typical performance on modern CPU:
- **Processing time**: ~1-2 ms per sequence
- **Throughput**: ~500-1000 sequences/second
- **Memory**: ~50 MB for 1000 sequences

## Testing

Run all tests:
```bash
# From repository root
pytest src/applications/crispr/tests/ -v
```

Run specific test suites:
```bash
pytest src/applications/crispr/tests/test_phi_phase.py -v
pytest src/applications/crispr/tests/test_spectral_features.py -v
```

## CI/CD

GitHub Actions workflow automatically:
1. Runs all tests on push/PR
2. Validates CLI functionality
3. Executes full validation pipeline
4. Benchmarks performance
5. Verifies reproducibility

See `.github/workflows/crispr-validation.yml`

## Mathematical Details

For complete mathematical formulation, derivations, and implementation details, see [METHODS.md](METHODS.md).

Key equations:

**φ-phase transform:**
```
θ'(n,k) = φ·((n mod φ)/φ)^k
y[n;k] = x[n]·exp(i·θ'(n,k))
```

**Arcsin bridge:**
```
z̃ = arcsin(α·sin(z))
where z = Arg(x) + θ'
```

**Complex encoding:**
```
A → 1+0i, T → -1+0i, C → 0+1i, G → 0-1i
```

## Ablation Studies

Compare contributions of different components:

1. **Baseline**: k=0, α=1 (no transforms)
2. **φ-phase only**: k=0.3, α=1
3. **Arcsin only**: k=0, α=0.95
4. **Full method**: k=0.3, α=0.95

Expected: Main gain from φ-phase + arcsin interaction.

## Failure Modes

### Over-compression (α → 1)
- **Symptom**: Loss of discriminative power
- **Diagnostic**: Monitor Δsidelobe (positive = over-compression)
- **Mitigation**: Reduce α or add early stopping

### GC Extremes
- **Symptom**: Entropy saturation at extreme GC%
- **Diagnostic**: Stratify by GC quartile
- **Mitigation**: Include GC% as covariate

### Window/Length Sensitivity
- **Symptom**: Feature variation with FFT size/window
- **Diagnostic**: Run ablations across {128, 256, 512}
- **Mitigation**: Use consistent parameters, report stability

## References

1. DeWeirdt PC, et al. (2022). Accounting for small variations in the tracrRNA sequence improves sgRNA activity predictions for CRISPR screening. *Nature Communications* 13:5255.

2. Doench JG, et al. (2016). Optimized sgRNA design to maximize activity and minimize off-target effects of CRISPR-Cas9. *Nature Biotechnology* 34:184-191.

3. Golden ratio in biological systems: Livio M. (2002). *The Golden Ratio: The Story of Phi*. Broadway Books.

## License

MIT License (see repository root)

## Citation

If you use this code in your research, please cite:

```bibtex
@software{crispr_spectral_resonance,
  title={CRISPR Spectral Resonance Optimization},
  author={Z Framework Team},
  year={2025},
  url={https://github.com/zfifteen/unified-framework},
  note={Part of the Unified Framework}
}
```

## Support

For issues, questions, or contributions:
- Open an issue: https://github.com/zfifteen/unified-framework/issues
- Refer to METHODS.md for technical details
- Check CI logs for validation failures

---

**Version:** 1.0  
**Last Updated:** 2025-11-10
