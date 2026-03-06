# Simplex-Anchor Experiment CLI

Command-line interface for running simplex-anchor A/B experiments.

## Keygen A/B Test

Run RSA keygen experiments to validate simplex-anchor enhancement.

### Quick Test (5 trials)

```bash
# Baseline
python -m cli.keygen_ab --bits 1024 --condition baseline --trials 5 --seed 1337 \
    --out-dir results/keygen_simplex_anchor/baseline_1024

# Simplex
python -m cli.keygen_ab --bits 1024 --condition simplex --trials 5 --seed 1337 \
    --out-dir results/keygen_simplex_anchor/simplex_1024
```

### CI/PR Shard (500 trials)

```bash
python -m cli.keygen_ab --bits 1024 --condition baseline --trials 500 --seed 1337 \
    --out-dir results/keygen_simplex_anchor/baseline_1024
```

### Full Suite (10,000 trials)

```bash
for bits in 1024 2048; do
  for cond in baseline simplex A4 euler self_dual; do
    python -m cli.keygen_ab \
      --bits $bits \
      --condition $cond \
      --trials 10000 \
      --seed 1337 \
      --out-dir results/keygen_simplex_anchor/${cond}_${bits}
  done
done
```

## Options

- `--bits`: RSA bit length (1024 or 2048)
- `--condition`: Simplex-anchor condition (baseline, simplex, A4, euler, self_dual)
- `--trials`: Number of trials to run
- `--seed`: Random seed for reproducibility
- `--out-dir`: Output directory for results
- `--mr-rounds`: Miller-Rabin rounds (default: 20)
- `--td-limit`: Trial division limit (default: 1000)

## Output Files

Each run produces:
- `metrics.csv`: Per-trial detailed metrics
- `summary.json`: Aggregate statistics

## Analysis

After collecting results, use the analysis scripts:

```bash
# Generate report
python scripts/analyze_keygen_results.py \
  --results-dir results/keygen_simplex_anchor \
  --output experiments/reports/simplex_anchor_summary.md

# Check acceptance criteria
python scripts/check_acceptance_criteria.py \
  --config configs/simplex_anchor_experiment.json \
  --results-dir results/keygen_simplex_anchor
```
