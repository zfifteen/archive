# Wave-Knob Invariant Self-Tuning Prime Scanner - Reproduction Experiment

## Overview

This experiment reproduces and validates the findings from PR #713 regarding the Wave-Knob Invariant Self-Tuning Prime Scanner system. The key discovery is the emergence of wave-like interference patterns in prime scanning parameters, enabling a self-tuning algorithm to lock onto "resonance valleys" where exactly one prime is detected per scan window.

## Experiment Goals

1. **Reproduce R* Scaling Law**: Validate the predictable bounded growth of R* = window/step ratios:
   - R* = 1.0 at k = 100
   - R* = 1.5 at k = 10^6  
   - R* = 31.5 at k = 10^100

2. **Validate Auto-Tune Convergence**: Confirm convergence in 2-10 iterations across scales

3. **Demonstrate Wave Patterns**: Show fringe-like interference patterns with Pearson r ≥ 0.93

4. **Measure Efficiency Gains**: Validate 25-50% reduction in Miller-Rabin calls via wheel optimization

5. **Cross-Domain Extension**: Test biological scanning with similar wave patterns

## Key Concepts

### Wave-Knob Parameters
- **window**: Search aperture around Z5D prediction (wave envelope)
- **step**: Scanning increment (wavelength/frequency analog)
- **R = window/step**: Wave ratio invariant governing prime-count oscillations

### Resonance Valleys
R* values where `prime_count = 1`, representing optimal scanning parameters for isolating unique primes.

### Mathematical Foundation
- **Core Model**: Z_5D prediction with wave-knob extension
- **Auto-tune**: Minimizes |prime_count - 1| via feedback
- **Unusual Aspect**: Fringe patterns suggest equidistribution under {k/φ}

## File Structure

```
experiments/wave_knob_reproduction/
├── README.md                     # This file
├── wave_knob_scanner.py         # Core Python implementation
├── auto_tune_experiments.py     # Auto-tune scaling studies
├── wave_pattern_analysis.py     # R-sweep and fringe pattern analysis
├── biological_extension.py      # Cross-domain biological scanning
├── visualization.py             # Plotting and heatmap generation
├── data/                        # Experimental data and results
├── plots/                       # Generated visualizations
└── findings_report.md           # Comprehensive findings documentation
```

## Usage

```bash
# Run basic wave-knob scanning
python wave_knob_scanner.py --k 1000 --window 10 --step 2

# Auto-tune experiment
python auto_tune_experiments.py --k-range 100,1000000,10

# Generate wave pattern analysis
python wave_pattern_analysis.py --k 1000 --output data/wave_patterns.json

# Create visualizations
python visualization.py --input data/wave_patterns.json --output plots/

# Run biological extension
python biological_extension.py --sequence-length 10000
```

## Expected Results

Based on PR #713, we expect to validate:

1. **R* Scaling**: Linear relationship between log(k) and R* with bounded growth
2. **Wave Interference**: Oscillating prime counts showing fringe patterns
3. **Auto-Tune Efficiency**: Rapid convergence to resonance valleys
4. **Cross-Domain Universality**: Similar patterns in biological sequence scanning

## References

- PR #713: "Implement Wave-Knob Invariant Self-Tuning Prime Scanner"
- Issue #712: "Wave-Knob Invariant, Self-Tuning Prime Scan"
- Z Framework Core: `src/core/z_5d_enhanced.py`
- Original Implementation: `src/c/z5d_mersenne.c`