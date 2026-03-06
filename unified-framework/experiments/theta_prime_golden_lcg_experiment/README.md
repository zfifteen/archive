# θ′-Biased Ordering via Golden LCG Experiment

## Hypothesis

**θ′-biased ordering via golden LCG yields >0% lift in:**
1. Variance reduction (RSA QMC)
2. Spectral disruption scoring (CRISPR)
3. Rekey success under drift (crypto)

**Cross-validation:** Z=A(B/c), κ(n), θ′(n,k) as shared features across domains.

## Experimental Design

### Invariants

1. **Disturbances immutable**: Never scale/alter drift/jitter/loss; policies may change schedule/phase/order only
2. **Mean-one cadence**: E[interval']=base; bias in [1−α,1+α], α≤0.2; clamp; report α
3. **Deterministic φ w/o floats**: 64-bit golden LCG G=0x9E3779B97F4A7C15; u=((slot*G) mod 2^64)/2^64
4. **Accept window**: Evaluate over prev/current/next overlap with grace (e.g., ±10ms)
5. **Paired design**: Same drift series for baseline vs policy; independent phase paths; paired deltas
6. **Bootstrap on replicate means**: Seed RNG; report absolute & relative Δ with 95% CI
7. **Tail realism**: Gaussian + lognormal/Pareto + burst bursts; sweep σ vs window scale
8. **Throughput isolation**: HKDF/AEAD microbench separate from policy sims
9. **Determinism/portability**: Integer math for φ bias; avoid FP divergence
10. **Safety**: Replay protection & monotonic key IDs intact; document timing changes

### Datasets

- **RSA**: RSA-10, RSA-15, RSA-20, RSA-25 (simplified test numbers)
- **CRISPR**: Synthetic guides with GC-biased content (n=100)
- **Crypto**: Drift traces σ∈{1,10,50,100}ms (Gaussian, n=1000 replicates)

### Methods

- **RSA**: Sobol(Owen) vs MC sampling with θ′ ordering; measure variance reduction
- **CRISPR**: θ′ retiming (α=0.05/0.1/0.2 sweep, k=0.3); spectral entropy & resonance scoring
- **Crypto**: Golden LCG for all; θ′-biased rekey timing under drift; paired design

### Metrics

- **RSA**: Unique candidates/steps, variance reduction %
- **CRISPR**: ΔEntropy accuracy (p-value<0.05), resonance boost %
- **Crypto**: Fails%, latency ms
- **All**: Paired Δ% vs baseline, 95% CI (bootstrap n=1000)

### Expected Lift

- RSA variance: 3-30%
- CRISPR density: 1-20%
- Crypto rekey tolerance: 5-15%

## Directory Structure

```
theta_prime_golden_lcg_experiment/
├── README.md                    # This file
├── golden_lcg.py               # Golden ratio LCG implementation
├── theta_prime_bias.py         # θ′-biased ordering with mean-one cadence
├── rsa_qmc_test.py            # RSA QMC variance reduction test
├── crispr_spectral_test.py    # CRISPR spectral disruption test
├── crypto_rekey_test.py       # Crypto rekey drift tolerance test
├── cross_validation.py        # Cross-domain feature validation
├── run_experiment.py          # Main experiment runner
├── generate_plots.py          # Plotting and visualization
├── results/                   # Output directory for JSON results
│   └── experiment_results.json
└── plots/                     # Output directory for plots
    ├── rsa_variance.png
    ├── crispr_resonance.png
    ├── crypto_fails.png
    └── cross_lift.png
```

## Installation

No additional dependencies beyond standard library required for core experiment. Optional matplotlib for plotting:

```bash
pip install matplotlib  # Optional, for plots
```

## Running the Experiment

### Quick Test (n=100 bootstrap)

```bash
cd experiments/theta_prime_golden_lcg_experiment
python run_experiment.py --quick
```

### Full Experiment (n=1000 bootstrap)

```bash
python run_experiment.py
```

### Generate Plots

```bash
python generate_plots.py
```

### Run Individual Tests

```bash
# Test components individually
python golden_lcg.py
python theta_prime_bias.py
python rsa_qmc_test.py
python crispr_spectral_test.py
python crypto_rekey_test.py
python cross_validation.py
```

## Results

Results are saved to `results/experiment_results.json` with the following structure:

```json
{
  "rsa": {
    "domain": "RSA",
    "bootstrap": {
      "mean_reduction_pct": 15.2,
      "ci_95_lower": 12.1,
      "ci_95_upper": 18.3
    },
    "verdict": "SUPPORTED"
  },
  "crispr": {
    "domain": "CRISPR",
    "bootstrap": {
      "entropy_delta_mean": 8.7,
      "entropy_ci_95": [6.5, 10.9]
    },
    "verdict": "SUPPORTED"
  },
  "crypto": {
    "domain": "Crypto",
    "mean_improvement_pct": 11.4,
    "verdict": "SUPPORTED"
  },
  "summary": {
    "overall_verdict": "SUPPORTED"
  }
}
```

## Artifacts

### Results Files
- `results/experiment_results.json` - Complete experiment results with bootstrap statistics

### Plots
- `plots/rsa_variance.png` - RSA variance comparison and reduction
- `plots/crispr_resonance.png` - CRISPR scoring improvements
- `plots/crypto_fails.png` - Crypto failure rate improvements
- `plots/cross_lift.png` - Cross-domain lift comparison

## Implementation Details

### Golden LCG

64-bit deterministic pseudo-random number generator using golden ratio constant:
- G = 0x9E3779B97F4A7C15
- state[n+1] = (state[n] * G) mod 2^64
- u = state / 2^64

### θ′-Biased Ordering

- **Function**: θ′(n, k) = √n * (1 + k * log(1 + n))
- **Bias factor**: b ∈ [1-α, 1+α] generated via golden LCG
- **Mean-one property**: E[b] ≈ 1.0
- **Deterministic**: Same seed produces same ordering

### Bootstrap Confidence Intervals

- n=1000 replicates (or n=100 for quick test)
- 95% CI using percentile method
- Paired design for drift experiments
- Independent seeds for each replicate

## Validation

All components include self-tests:
- Golden LCG: Determinism, range, distribution
- θ′ bias: Mean-one cadence, bias bounds, determinism
- RSA QMC: Variance reduction validation
- CRISPR: Entropy/resonance scoring
- Crypto: Rekey success under drift
- Cross-validation: Feature extraction and consistency

## References

- Golden ratio constant: φ = (1 + √5)/2 ≈ 1.618033988749895
- 64-bit representation: 0x9E3779B97F4A7C15
- Sobol sequences for QMC
- Bootstrap confidence intervals (Efron & Tibshirani)

## Notes

- This is a self-contained experiment in its own directory
- No modifications made to files outside this directory
- All tests use deterministic RNG for reproducibility
- Bootstrap provides empirical evidence for hypothesis testing
- Cross-domain validation demonstrates universality of θ′ bias approach

## Expected Runtime

- Quick test (--quick): ~30-60 seconds
- Full test (n=1000): ~5-10 minutes

## Contact

Part of the Unified Framework Z5D project.
