# Hybrid Scaling Architecture in Extreme Prime Prediction

## Experiment Overview

This experiment tests the hypothesis regarding a dual-adapter hybrid scaling architecture for extreme prime prediction, specifically examining:

1. **Dual Adapter System**: C adapter (GMP/MPFR, fixed precision, scales ≤50) and Python adapter (gmpy2/mpmath, dynamic precision, arbitrary scales)
2. **Convergent Accuracy**: Emergent asymptotic convergence across 1200+ orders of magnitude (10^20 to 10^1233) with <0.0001% deviation
3. **Resonance Asymmetry**: Non-obvious asymmetry in signal enrichment favoring larger semiprime factor (q) over smaller (p) by ~5x
4. **Statistical Significance**: Non-randomness in predictions with p < 1e-300

## Directory Structure

```
hybrid-scaling-extreme-prime/
├── src/
│   └── z5d_adapter.c          # C adapter with GMP/MPFR (scales ≤50)
├── tools/
│   └── run_geofac_peaks_mod.py # Geometric resonance detection
├── data/                       # Test data (generated)
├── results/                    # Experiment results
├── z5d_adapter.py             # Python adapter with gmpy2/mpmath (arbitrary precision)
├── z5d_validation_n127.py     # Validation experiments
├── run_experiment.py          # Main experiment runner
├── reproduce_scaling.sh       # Automated scaling benchmark
├── requirements.txt           # Python dependencies
├── FINDINGS.md               # Experimental findings and conclusions
└── README.md                 # This file
```

## Installation

### Prerequisites

For C adapter (optional, scales ≤50):
```bash
# Ubuntu/Debian
sudo apt-get install libgmp-dev libmpfr-dev gcc

# macOS
brew install gmp mpfr
```

For Python adapter (required):
```bash
pip install -r requirements.txt
```

Note: gmpy2 may require additional setup on some systems.

## Usage

### Run Complete Experiment

```bash
python3 run_experiment.py
```

This runs all validation tests and saves results to `results/experiment_results.json`.

### Run Individual Components

**Test Python adapter convergence:**
```bash
python3 z5d_adapter.py --test-convergence --start 20 --end 127 --step 10
```

**Test single scale:**
```bash
python3 z5d_adapter.py --scale 100
```

**Run scaling benchmark:**
```bash
chmod +x reproduce_scaling.sh
./reproduce_scaling.sh --scale-min 20 --scale-max 100 --step 10
```

**Test resonance asymmetry:**
```bash
python3 tools/run_geofac_peaks_mod.py --test-suite
```

**Test specific semiprime:**
```bash
python3 tools/run_geofac_peaks_mod.py --p 11 --q 13 --window 1000
```

**Run validation tests:**
```bash
python3 z5d_validation_n127.py --test all
```

## Hypothesis Details

### Claim 1: Dual Adapter System
- **C adapter** (src/z5d_adapter.c:47-60): Uses GMP/MPFR with fixed 256-bit precision for scales ≤50
- **Python adapter** (z5d_adapter.py:20-40): Uses gmpy2/mpmath with dynamic `dps = max(100, int(bits * 0.4) + 200)`
- **Automatic switching** (reproduce_scaling.sh:51-60): Based on scale_max >50

### Claim 2: Convergent Accuracy
- **Z5D scoring** (z5d_adapter.py:90-120): log10-relative error from PNT-based prediction
- **PNT approximation** (z5d_adapter.py:60-85): `p_n ≈ n * (ln(n) + ln(ln(n)) - 1 + (ln(ln(n)) - 2)/ln(n))`
- **Expected performance**: 10^20 in ~75ms, 10^1233 in ~115ms
- **Target accuracy**: <0.0001% deviation at 10^1233 scales

### Claim 3: Resonance Asymmetry
- **Geometric amplitude** (tools/run_geofac_peaks_mod.py:220-250): `A(k) = cos(ln(k)*φ) × cos(ln(k)*e)`
- **Expected enrichment**: 5x signal strength near q vs p
- **Application**: Targeted factorization in 256-426 bit semiprimes

### Claim 4: Statistical Significance
- **Non-randomness**: p < 1e-300 (experiments/z5d_validation_n127.py:200-250)
- **Tests**: Runs test, autocorrelation, Anderson-Darling

## Results

After running the experiment, results are saved to:
- `results/experiment_results.json`: Raw test results
- `FINDINGS.md`: Detailed analysis and conclusions

## Technical References

- Prime Number Theorem: https://mathworld.wolfram.com/PrimeNumberTheorem.html
- GNFS (comparison): https://en.wikipedia.org/wiki/General_number_field_sieve

## License

Part of the playground repository experimental suite.
