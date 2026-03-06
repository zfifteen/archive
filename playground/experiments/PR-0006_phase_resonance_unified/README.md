# PR-0006: Unified Phase-Resonance Methods Across Number Theory and Molecular Biology

## Overview

This experiment tests the hypothesis that phase-resonance methods using irrational constants can unify pattern detection across discrete mathematical structures (prime factorization) and dynamic biological systems (DNA helical dynamics).

## Hypothesis

**Claim:** Irrational or non-integer phase alignments in resonance frameworks can bridge number theory (primes/semiprimes) and molecular biology (DNA helical twisting), indicating a broader class of unified analytic tools for detecting irregularity in natural sequences.

## Experimental Design

### Number Theory Domain
- **Method:** Geometric resonance using φ (golden ratio) and e (Euler's number)
- **Formula:** `R(k) = cos(θ + ln(k)·φ) / ln(k) + cos(ln(k)·e) · 0.5`
- **Test data:** Synthetic semiprimes with known factors
- **Metrics:** Factor detection accuracy, SNR at true factors, peak sharpness

### Molecular Biology Domain
- **Method:** Helical phase modulation with Chirp Z-Transform
- **Formula:** `H(k) = exp(i * 2π * k / 10.5)`
- **Test data:** Synthetic DNA sequences with known structural properties
- **Metrics:** Phase coherence, spectral peak at helical frequency, mutation sensitivity

### Cross-Domain Analysis
- **Unified metrics:** Phase coherence, SNR, peak sharpness, spectral purity
- **Statistical tests:** Correlation analysis, effect sizes, ANOVA
- **Controls:** Random phases, integer periods, non-resonant sequences

## Running the Experiment

### Installation

```bash
cd experiments/PR-0006_phase_resonance_unified
pip install -r requirements.txt
```

### Execution

```bash
python run_experiment.py
```

This will:
1. Generate test datasets (semiprimes and DNA sequences)
2. Run phase-resonance analysis on both domains
3. Extract and compare unified metrics
4. Run control experiments
5. Generate visualizations
6. Update FINDINGS.md with results and verdict

### Output Files

```
experiments/PR-0006_phase_resonance_unified/
├── FINDINGS.md              # Detailed findings (conclusion-first format)
├── results/
│   ├── summary_dashboard.png
│   ├── nt_resonance_scan.png
│   ├── dna_spectrum.png
│   ├── cross_domain_comparison.png
│   └── results.json
└── data/
    ├── semiprimes.json
    └── dna_sequences.json
```

## File Structure

```
PR-0006_phase_resonance_unified/
├── README.md (this file)
├── FINDINGS.md (experimental results, conclusion-first)
├── run_experiment.py (main execution script)
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── number_theory.py      # Semiprime factorization resonance
│   ├── molecular_biology.py  # DNA phase encoding and CZT
│   ├── unified_metrics.py    # Cross-domain comparison
│   └── visualization.py      # Plotting functions
├── data/ (generated datasets)
└── results/ (plots and JSON output)
```

## Implementation Status

This experiment follows the **Incremental Coder** protocol:

- [x] Complete structure with all files and functions
- [x] `number_theory.generate_semiprimes()` - IMPLEMENTED
- [ ] Other functions - Detailed specifications in comments (TO BE IMPLEMENTED)

### Next Steps

To continue implementation, run:
```
continue
```

This will implement the next function according to the incremental protocol.

## Key References

1. **geofac_validation** - Geometric factorization validation  
   https://github.com/zfifteen/geofac_validation

2. **dna-breathing-dynamics-encoding** - DNA biophysical encoding  
   https://github.com/zfifteen/dna-breathing-dynamics-encoding

## Dependencies

- Python 3.7+
- NumPy (numerical computation)
- SciPy (signal processing, FFT, CZT)
- Matplotlib (visualization)

## Expected Runtime

- Number theory analysis: ~1 minute (50 semiprimes)
- DNA analysis: ~30 seconds (10 sequences, 1000bp each)
- Cross-domain statistics: ~10 seconds
- Total: ~2 minutes

## Validation Criteria

The hypothesis will be considered **CONFIRMED** if:
1. Both domains show SNR improvement > 3.0 vs random baseline
2. Cross-domain correlation coefficient > 0.7
3. Controls show degraded performance (effect size > 1.0)
4. Phase coherence metrics are statistically similar

Otherwise: **PARTIALLY CONFIRMED** or **FALSIFIED** with detailed reasoning.

## Author

GitHub Copilot (Incremental Coder Agent)

## License

Same as parent repository
