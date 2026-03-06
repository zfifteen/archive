# Variance Analysis Reports

This directory contains generated statistical analysis reports examining variance relationships and mathematical properties within the unified framework.

## Report Types

### Basic Variance Analysis (`basic/`)
- Standard variance analysis reports
- Linear model fitting: `var(O) = a·log(log(N)) + b`
- Basic correlation analysis and statistical validation

### Enhanced Variance Analysis (`enhanced/`)
- Comprehensive variance analysis reports
- Power law model fitting: `var(O) = a·(log(log(N)))^b`
- Advanced statistical analysis with multiple model comparisons

## Analysis Focus

These reports examine the mathematical relationship:
```
var(O) ~ log log N
```

Where:
- `var(O)` represents the variance of the observational data
- `N` is the scale parameter
- The relationship is analyzed through both linear and power law models

## Statistical Methods

### Linear Model Analysis
- Slope and intercept estimation with confidence intervals
- R² determination for model fit quality
- Statistical significance testing

### Power Law Model Analysis  
- Coefficient and exponent estimation
- Non-linear regression fitting
- Comparative model performance analysis

### Correlation Analysis
- Pearson correlation coefficients
- Spearman rank correlation (non-parametric)
- P-value significance testing

## Z Framework Integration

All variance analysis reports include interpretations within the context of the Z Framework's mathematical foundations, connecting statistical observations to the underlying theoretical framework.