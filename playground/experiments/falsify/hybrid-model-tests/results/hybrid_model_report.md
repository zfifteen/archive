# Hybrid Model Comparison Report

## Objective
Test whether hybrid stochastic models can replicate the statistical properties claimed for prime gaps, thereby falsifying claims of uniqueness.

## Target Statistics
- **Mean**: 0.0003
- **Std Dev**: 0.0048
- **Skewness**: 71.7218
- **Kurtosis**: 6194.1061
- **95th percentile**: 0.0005
- **99th percentile**: 0.0024
- **ACF(1)**: 0.7956

## Model Results

| Model | KS Distance | p-value | ACF Error | Tail Disc. | AIC |
|-------|------------|---------|-----------|------------|-----|
| Additive Decomposition | 0.5199 | 0.0000 | 0.4173 | 0.0019 | -799254.5 |
| Fractional GN + Lognormal | 0.5686 | 0.0000 | 0.4230 | 0.0025 | -713003.0 |
| Correlated Cramér | 0.7931 | 0.0000 | 0.1686 | 0.0019 | -937745.5 |
| GARCH(1,1) + Lognormal | 0.9073 | 0.0000 | 0.4984 | 0.0023 | -541004.3 |
| Lognormal ARMA(1,1) | 1.0000 | 0.0000 | 0.2439 | 2.8175 | -173488.9 |
| Exponential + Drift | 1.0000 | 0.0000 | 0.4986 | 2.0167 | -534332.1 |

## Best Parameters

### Additive Decomposition
Parameters: (0.0001263127011702816, 0.0, 0.00047789582162492596, 100, -8.283614208823037, 0.00477895821624926)

### Fractional GN + Lognormal
Parameters: (-8.283614208823037, 0.7)

### Correlated Cramér
Parameters: (3958.430113262737, 0.7956408252654454)

### GARCH(1,1) + Lognormal
Parameters: (-8.283614208823037, 2.2838441632656307e-06, 0.1, 0.8)

### Lognormal ARMA(1,1)
Parameters: (0.7000000000000001, 0.30000000000000016, 0.1)

### Exponential + Drift
Parameters: (0.00024120618152423504, 0.0, 0.00477895821624926)

## Conclusion

**INCONCLUSIVE: Mixed results, further investigation needed**

## Interpretation

Mixed results require further investigation.

## Visualizations

- `distribution_comparison.png`: Histogram overlays
- `acf_comparison.png`: Autocorrelation function comparisons
- `qq_plots.png`: Quantile-quantile plots
- `model_ranking.png`: Performance comparison
- `parameter_sensitivity.png`: Parameter sensitivity analysis
