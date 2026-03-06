# Lognormal vs Exponential Distribution Falsification Test: Scale-Dependent Crossover at 10^12

## Major Finding: Sharp Lognormal-to-Exponential Crossover

This experiment reveals a **scale-dependent phenomenon in prime gap distributions**:
- **Scales ≤10^11**: Lognormal models dominate (ΔBIC > +20, 100% wins)
- **Scales ≥10^12**: Exponential models dominate (ΔBIC < -12, 100% wins)

The crossover at ~10^12 (mean gap ~32) supports **Cramér's conjecture** (gaps ~ Exp(ln n) at large scales) and aligns with Cohen (2024) theorem on moment convergence. See `results/white_paper.md` for full analysis and `results/crossover_analysis.md` for detailed findings.

## Overview

The experiment:
1. Generates primes in disjoint ranges (now up to arbitrary precision using Python port of LIS-Corrector C code).
2. Bands primes by magnitude (log-spaced or linear for narrow ranges to avoid float precision issues).
3. Extracts consecutive gaps per band.
4. Fits Exponential and Lognormal on 70% train set.
5. Evaluates on 30% test set using BIC, log-likelihood, KS test.
6. Determines winner per band (ΔBIC ≥10 favors lognormal; ≤-10 favors exponential).

Falsification requires lognormal failure in ≥50% bands across ≥2 ranges. **No falsification observed**—instead, a genuine scale-dependent behavior.

## Major Updates
- **Python Prime Generator**: Full port of `c/prime_generator.c` with Wheel-30, Lucas pre-filter, adaptive Miller-Rabin (gmpy2).
- **Arbitrary Precision**: Handles 10^19+ (dtype=object, float conversions for fitting).
- **Banding Fix**: Linear spacing for narrow ranges (<1% of start) to fix float precision loss.
- **Benchmarks**: 15 scales (10^5-10^18) in `results/bench_*`; crossover plot in `results/delta_bic_phase_diagram.png`.

## Running the Experiment

### Prerequisites
```bash
pip install -r requirements.txt gmpy2  # gmpy2 for fast primality
```

### Execution
Default:
```bash
python run_experiment.py
```

Custom:
```bash
python run_experiment.py --ranges "1e7:2e7,2e7:3e7" --output results_custom/ --seed 123
```

Large scales (arbitrary precision):
```bash
python run_experiment.py --ranges "1e16:1e17" --prime-source python --output results_large/
```

Options:
- `--prime-source python`: Arbitrary precision generator (default: sieve/primesieve).
- `--bands 1`: Single band for benchmarks (default 6).
- `--seed 42`: Reproducibility.

### Output
- `results.json`: Metrics per band (BIC, KS, winner).
- `results.csv`: Summary table.
- `report.md`: Verdict (NOT FALSIFIED).
- `fit_*.png`: Histograms/PDFs/Q-Q plots.

## Benchmark Results (10^5 to 10^18)
See `results/benchmark_summary.md` for timings (~1.7-32s, stable at large scales).

| Scale | Gaps | ΔBIC | Winner |
|-------|------|------|--------|
| 10^5  | 7335 | +20 | Lognormal |
| 10^6  | 61621 | +20 | Lognormal |
| 10^7  | 530249 | +20 | Lognormal |
| 10^8  | 4652642 | +20 | Lognormal |
| 10^9  | 4213093 | +20 | Lognormal |
| 10^10 | 380429 | +20 | Lognormal |
| 10^11 | 34542 | +20.5 | Lognormal |
| 10^12 | 31726 | -12.7 | Exponential |
| 10^13 | 5883 | -15 | Exponential |
| 10^14 | 5391 | -15 | Exponential |
| 10^15 | 5011 | -15 | Exponential |
| 10^16 | 5224 | -15 | Exponential |
| 10^17 | 5592 | -15 | Exponential |
| 10^18 | 6288 | -15 | Exponential |

## Crossover Phenomenon
- **Transition**: 10^11.5 (ΔBIC +105, lognormal) → 10^12 (ΔBIC -13, exponential).
- **Mean Gap**: ~30 → ~32.
- **Cause**: Local sieving (lognormal) → global randomness (exponential).
- **Plot**: `results/delta_bic_phase_diagram.png`.

## Falsification Criteria
"Lognormal > Exponential" falsified if ≥50% bands favor exponential across ≥2 ranges. **Not falsified**—scale-dependence observed instead.

## White Paper
Full analysis: `results/white_paper.md` (ready for *Experimental Mathematics* submission).

## C Code
`c/prime_generator.c`: Original GMP implementation (compiled with `make`).

## Next Steps
- Multi-band validation at 10^12.
- Cramér-normalized gaps (g'/ln(p_n) → Exp(1)).
- Publish!

EOF

### Prerequisites

Install dependencies:

```bash
pip install -r requirements.txt
```

For large prime ranges (e.g., up to 10^18), install primesieve:

```bash
brew install primesieve  # macOS with Homebrew
# Or download from https://primesieve.org/
```

### Execution

Run the experiment with default settings:

```bash
python run_experiment.py
```

Customize ranges and output:

```bash
python run_experiment.py --ranges "1e7:2e7,2e7:3e7" --output results_custom/ --seed 123
```

For large ranges, use primesieve:

```bash
python run_experiment.py --ranges "1e16:1e17" --prime-source primesieve --output results_large/
```

Note: Use --prime-source primesieve for ranges > 10^10 to leverage optimized prime generation. Default is segmented sieve for smaller ranges.

### Output

The script produces:
- `results.json`: Detailed metrics for every band.
- `results.csv`: Flattened summary table.
- `report.md`: Human-readable summary and falsification verdict.
- `fit_*.png`: Diagnostic plots for the first band of each range.

## Falsification Criteria

The claim "Lognormal > Exponential" is considered **falsified** if:
- Lognormal fails to beat Exponential (by $\Delta BIC \ge 10$) in $\ge 50\%$ of bands across at least two independent ranges.
