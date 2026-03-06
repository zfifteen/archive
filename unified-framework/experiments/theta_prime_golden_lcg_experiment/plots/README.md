# Plots Directory

This directory contains visualizations generated from experiment results.

## Generated Plots

When matplotlib is available, the following plots are generated:

### rsa_variance.png
- Left panel: Variance comparison (baseline vs θ′-biased) for each RSA test case
- Right panel: Variance reduction percentage for each test case
- Shows whether θ′-biased ordering reduces variance in RSA QMC sampling

### crispr_resonance.png
- Left panel: Entropy and resonance score comparison (baseline vs θ′-biased)
- Right panel: Improvement percentages with 95% confidence intervals
- Demonstrates impact of θ′-biased ordering on CRISPR guide scoring

### crypto_fails.png
- Left panel: Failure rate comparison across different drift sigma values
- Right panel: Relative improvement percentages with 95% CI
- Shows rekey tolerance under varying network drift conditions

### cross_lift.png
- Cross-domain lift comparison with 95% confidence intervals
- Visualizes hypothesis testing results across all three domains (RSA, CRISPR, Crypto)
- Color-coded bars with error bars for statistical significance

## Generating Plots

```bash
# After running the experiment
python generate_plots.py

# Or specify a custom results file
python generate_plots.py results/experiment_results.json
```

## Requirements

Plots require matplotlib:

```bash
pip install matplotlib
```

If matplotlib is not available, the experiment still runs successfully and generates text-based reports instead.

## Alternative: Text Reports

Without matplotlib, use the text-based summary:

```bash
python generate_summary.py
```

This creates `results/experiment_summary.txt` with all the same information in text format.

## Notes

- Plots use non-interactive 'Agg' backend for server/headless environments
- All plots are saved as PNG files at 150 DPI
- Plot generation is optional - experiment results are complete without them
- Plots directory is gitignored by default (regenerated on each run)
