# Z5D Simplex-Anchor A/B Validation Experiment

## Overview

This experiment validates the **simplex-anchor enhancement** (E = 1.078437 = A₄ × Euler × self-duality) for prime density improvements in:

1. **RSA Key Generation** - Reducing candidates per prime → fewer Miller-Rabin tests
2. **Geometric-Resonance Factorization** - Better early-rank hits → shorter time-to-first-factor

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Run Quick Test (5 trials)

```bash
# Baseline
python -m cli.keygen_ab --bits 1024 --condition baseline --trials 5 --seed 1337 \
    --out-dir results/keygen_simplex_anchor/baseline_1024

# Simplex-anchor
python -m cli.keygen_ab --bits 1024 --condition simplex --trials 5 --seed 1337 \
    --out-dir results/keygen_simplex_anchor/simplex_1024
```

### 3. View Results

```bash
cat results/keygen_simplex_anchor/baseline_1024/summary.json
cat results/keygen_simplex_anchor/simplex_1024/summary.json
```

## Project Structure

```
.
├── configs/
│   └── simplex_anchor_experiment.json       # All experiment parameters
├── experiments/
│   ├── EXPERIMENT_CARD_simplex_anchor.md    # Design documentation
│   └── reports/                             # Generated analysis reports
├── src/
│   ├── z5d/
│   │   └── simplex_anchor.py                # Core enhancement logic
│   ├── experiments/
│   │   └── keygen_ab.py                     # Keygen A/B harness
│   ├── analysis/
│   │   ├── bootstrap.py                     # Confidence intervals
│   │   └── distributions.py                # KS test, log-rank, tail stats
│   └── plots/
│       ├── keygen.py                        # Keygen visualizations
│       └── resonance.py                     # Resonance visualizations
├── cli/
│   ├── keygen_ab.py                         # Command-line interface
│   └── README.md                            # CLI usage guide
├── tests/
│   ├── test_simplex_anchor.py               # 30 unit tests
│   └── test_keygen_ab.py                    # 15 integration tests
├── scripts/
│   ├── analyze_keygen_results.py            # Generate analysis reports
│   └── check_acceptance_criteria.py         # Validate results
└── .github/workflows/
    └── experiment_simplex_anchor.yml        # CI automation
```

## Experiment Design

### Enhancement Factor

```
E = A₄ × Euler × Self-dual
E = 1.041667 × 1.02 × 1.015
E = 1.078437 (7.84% improvement)
```

### Test Conditions

1. **baseline** - No enhancement (E = 1.0)
2. **simplex** - Full product (E = 1.078437)
3. **A4** - A₄ symmetry only (1.041667)
4. **euler** - Euler factor only (1.02)
5. **self_dual** - Self-duality only (1.015)

### Expected Results

**1024-bit RSA:**
- Baseline: ~354.89 candidates/prime
- Simplex: ~329.09 candidates/prime (7.27% reduction)

**2048-bit RSA:**
- Baseline: ~709.78 candidates/prime
- Simplex: ~658.18 candidates/prime (7.27% reduction)

## Running Experiments

### Quick Shard (CI/PR) - 500 trials

```bash
for cond in baseline simplex A4 euler self_dual; do
  python -m cli.keygen_ab --bits 1024 --condition $cond --trials 500 --seed 1337 \
    --out-dir results/keygen_simplex_anchor/${cond}_1024
done
```

### Full Suite (Production) - 10,000 trials

```bash
for bits in 1024 2048; do
  for cond in baseline simplex A4 euler self_dual; do
    python -m cli.keygen_ab --bits $bits --condition $cond --trials 10000 --seed 1337 \
      --out-dir results/keygen_simplex_anchor/${cond}_${bits}
  done
done
```

## Analysis & Reporting

### Generate Analysis Report

```bash
python scripts/analyze_keygen_results.py \
  --results-dir results/keygen_simplex_anchor \
  --output experiments/reports/simplex_anchor_summary.md
```

### Check Acceptance Criteria

```bash
python scripts/check_acceptance_criteria.py \
  --config configs/simplex_anchor_experiment.json \
  --results-dir results/keygen_simplex_anchor
```

## Acceptance Criteria

### Keygen (Definition of Done)

✅ Median wall-clock ↓ ≥ 5% (95% CI not crossing 0)  
✅ No correctness regressions (all primes validate)  
✅ Ablation: Product > components (statistically significant)

### Resonance (Future Work in z-sandbox)

✅ Median TTF ↓ ≥ 10% (95% CI not crossing 0)  
✅ Top-25 precision ↑ ≥ 5%  
✅ Lighter tail (lower tail index OR higher Q1 hazard)

## CI/CD Integration

### Automated Testing

- **PR/Push**: Quick shard (500 trials)
- **Nightly**: Full suite (10,000 trials)
- **Unit Tests**: 45 tests (100% pass rate)

### Workflow Triggers

```yaml
# Manual trigger
gh workflow run experiment_simplex_anchor.yml -f run_mode=full

# Nightly automatic at 2 AM UTC
# Runs full 10k trial suite
```

## Key Design Principles

1. **No Fallbacks** - Pure simplex-anchor only, no hybrid approaches
2. **Reproducibility** - Fixed seeds (master: 1337) for all RNG
3. **High Precision** - mpmath dps=50 for numerical stability
4. **Determinism** - Same seed → same results always
5. **Security** - GITHUB_TOKEN permissions limited

## Files & Formats

### Output Files

**metrics.csv** - Per-trial detailed data:
```csv
trial_id,bit_length,prime_found,candidates_tested,miller_rabin_calls,mr_time_ms,total_time_ms,condition
0,1024,107095858...,45,6,90.20,91.70,baseline
```

**summary.json** - Aggregate statistics:
```json
{
  "condition": "baseline",
  "bit_length": 1024,
  "n_trials": 5,
  "median_candidates": 230.0,
  "median_total_time_ms": 194.16,
  "seed": 1337
}
```

## Testing

### Run All Tests

```bash
# Unit tests (45 tests)
pytest tests/test_simplex_anchor.py tests/test_keygen_ab.py -v

# With coverage
pytest tests/ --cov=src/z5d/simplex_anchor --cov=src/experiments/keygen_ab \
  --cov-report=html
```

### Test Categories

- **Simplex Anchor**: 30 tests (factors, density, validation)
- **Keygen A/B**: 15 tests (generation, primality, metrics)

## Development

### Code Style

```bash
# Format check
black --check src/z5d/simplex_anchor.py src/experiments/keygen_ab.py

# Lint
flake8 src/z5d/simplex_anchor.py --max-line-length=100
```

### Adding New Conditions

1. Update `configs/simplex_anchor_experiment.json`
2. Add factors to `SimplexAnchorConfig` in `simplex_anchor.py`
3. Update `ConditionType` type hint
4. Add test cases

## Documentation

- **Experiment Card**: [`experiments/EXPERIMENT_CARD_simplex_anchor.md`](experiments/EXPERIMENT_CARD_simplex_anchor.md)
- **CLI Guide**: [`cli/README.md`](cli/README.md)
- **Config Reference**: [`configs/simplex_anchor_experiment.json`](configs/simplex_anchor_experiment.json)

## References

- **Issue**: Z5D Simplex-Anchor A/B Validation for RSA Keygen & Geometric-Resonance
- **A₄ Symmetry**: Alternating group of degree 4
- **Euler Factor**: Prime density related to Euler's totient function
- **Self-Duality**: Geometric duality in 5-dimensional space
- **Miller-Rabin**: Probabilistic primality test (20 rounds, 2⁻⁴⁰ error rate)

## Contributing

See main repository CONTRIBUTING.md for general guidelines.

For this experiment:
1. All changes must pass 45 unit tests
2. Security scan must be clean (CodeQL)
3. Acceptance criteria must be met for production use

## License

MIT License - see repository LICENSE file

## Status

🟢 **Active** - Currently under validation

- ✅ Core implementation complete
- ✅ Unit tests passing (45/45)
- ✅ CLI functional
- ✅ CI workflow ready
- ⏳ Full 10k trial validation pending
- ⏳ Acceptance criteria validation pending

## Contact

For questions or issues, open a GitHub issue in the unified-framework repository.
