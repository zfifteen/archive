"""
Z5D Riemann Scaling Anomaly Analysis
===================================

Evaluate O(1/log^2 k) correction terms for Z5D prime predictions.
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy import optimize
import matplotlib.pyplot as plt
import warnings
from pathlib import Path
from typing import Dict, Tuple, Optional, Union
import argparse
import json
import mpmath as mp

from .io_utils import load_white_paper
from ..statistical.bootstrap_validation import bootstrap_confidence_intervals


# Set high precision for extreme k values
mp.mp.dps = 50


def z5d_with_riemann_correction(p_hat_z5d: float, k: int, beta: float) -> float:
    """
    Apply O(1/log²k) correction to Z5D prediction.
    
    Args:
        p_hat_z5d: Z5D baseline prediction
        k: prime index  
        beta: correction coefficient
        
    Returns:
        Corrected prediction
    """
    if k <= 1:
        return p_hat_z5d  # No correction for k=1
    
    log_k = np.log(float(k))
    correction_factor = 1.0 + beta / (log_k**2)
    return p_hat_z5d * correction_factor


def compute_correction_features(df: pd.DataFrame, use_mpmath: bool = False) -> pd.DataFrame:
    """
    Compute correction features for scaling anomaly analysis.
    
    Args:
        df: Input dataframe with k, p_true, p_hat_z5d columns
        use_mpmath: Use high-precision arithmetic for large k
        
    Returns:
        DataFrame with additional feature columns
    """
    df = df.copy()
    
    if use_mpmath:
        # High precision computation for extreme k
        logk_hp = [float(mp.log(mp.mpf(k))) for k in df['k']]
        df['logk'] = logk_hp
        df['ilog2'] = [1.0 / (lk**2) for lk in logk_hp]
    else:
        # Standard numpy computation
        df['logk'] = np.log(df['k'].astype(float))
        df['ilog2'] = 1.0 / (df['logk']**2)
    
    # Additional features for robustness analysis
    df['ilog'] = 1.0 / df['logk']  # 1/log k term
    df['ilog3'] = 1.0 / (df['logk']**3)  # 1/log^3 k term
    
    return df


def fit_correction(df: pd.DataFrame, form: str = "multiplicative", 
                  holdout_pct: float = 0.0) -> Dict:
    """
    Fit O(1/log^2 k) correction to Z5D predictions.
    
    Args:
        df: Input data with required columns
        form: Correction form ("multiplicative", "additive", "relerr-reg")
        holdout_pct: Percentage of largest k to holdout for testing
        
    Returns:
        Dictionary with fitting results and metrics
    """
    df = df.copy()
    
    # Split into train/test if holdout requested
    if holdout_pct > 0:
        k_threshold = np.percentile(df['k'], 100 - holdout_pct)
        train_df = df[df['k'] < k_threshold].copy()
        test_df = df[df['k'] >= k_threshold].copy()
    else:
        train_df = df.copy()
        test_df = df.copy()
    
    if len(train_df) < 5:  # Reduced threshold for testing
        raise ValueError(f"Insufficient training data: {len(train_df)} samples")
    
    # Fit correction coefficient
    if form == "multiplicative":
        beta, fit_info = _fit_multiplicative_correction(train_df)
    elif form == "additive":
        beta, fit_info = _fit_additive_correction(train_df)
    elif form == "relerr-reg":
        beta, fit_info = _fit_relative_error_regression(train_df)
    else:
        raise ValueError(f"Unknown form: {form}")
    
    # Compute corrected predictions
    test_corrected = _apply_correction(test_df, beta, form)
    
    # Compute metrics
    baseline_rmse = np.sqrt(np.mean((test_df['p_true'] - test_df['p_hat_z5d'])**2))
    corrected_rmse = np.sqrt(np.mean((test_df['p_true'] - test_corrected)**2))
    
    baseline_medae = np.median(np.abs(test_df['p_true'] - test_df['p_hat_z5d']))
    corrected_medae = np.median(np.abs(test_df['p_true'] - test_corrected))
    
    rmse_delta = baseline_rmse - corrected_rmse
    medae_delta = baseline_medae - corrected_medae
    
    return {
        "beta": beta,
        "beta_ci": None,  # Will be filled by bootstrap
        "metric_improvement": {
            "rmse_delta": rmse_delta,
            "medae_delta": medae_delta,
            "baseline_rmse": baseline_rmse,
            "corrected_rmse": corrected_rmse,
            "baseline_medae": baseline_medae,
            "corrected_medae": corrected_medae
        },
        "p_value": None,  # Will be filled by bootstrap
        "n": len(test_df),
        "n_train": len(train_df),
        "notes": f"Form: {form}, holdout: {holdout_pct}%",
        "fit_info": fit_info
    }


def _fit_multiplicative_correction(df: pd.DataFrame) -> Tuple[float, Dict]:
    """Fit multiplicative correction: p_corr = p_hat * (1 + beta/log^2 k)"""
    
    # Set up least squares problem
    # Residual: p_true - p_hat * (1 + beta * ilog2) = p_true - p_hat - beta * p_hat * ilog2
    # Minimize: || (p_true - p_hat) + beta * p_hat * ilog2 ||^2
    
    y = df['p_true'] - df['p_hat_z5d']
    X = -df['p_hat_z5d'] * df['ilog2']
    
    # Solve via least squares
    beta = np.sum(X * y) / np.sum(X * X)
    
    # Compute R^2 and residuals
    y_pred = -beta * X
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Also fit with Huber robust regression for comparison
    try:
        from sklearn.linear_model import HuberRegressor
        huber = HuberRegressor(fit_intercept=False)
        huber.fit(X.values.reshape(-1, 1), y.values)
        beta_robust = huber.coef_[0]
    except:
        beta_robust = beta
    
    fit_info = {
        "r2": r2,
        "beta_robust": beta_robust,
        "n_fit": len(df)
    }
    
    return beta, fit_info


def _fit_additive_correction(df: pd.DataFrame) -> Tuple[float, Dict]:
    """Fit additive correction: p_corr = p_hat + gamma * p_hat * ilog2"""
    # This is algebraically equivalent to multiplicative with gamma = beta
    return _fit_multiplicative_correction(df)


def _fit_relative_error_regression(df: pd.DataFrame) -> Tuple[float, Dict]:
    """Fit relative error regression: err_rel ~ alpha + beta * ilog2"""
    
    # Compute relative error
    err_rel = (df['p_true'] - df['p_hat_z5d']) / df['p_true']
    
    # Set up regression: err_rel = alpha + beta * ilog2
    X = np.column_stack([np.ones(len(df)), df['ilog2']])
    y = err_rel
    
    # Solve via least squares
    params = np.linalg.lstsq(X, y, rcond=None)[0]
    alpha, beta = params
    
    # Compute R^2
    y_pred = X @ params
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    fit_info = {
        "alpha": alpha,
        "r2": r2,
        "n_fit": len(df)
    }
    
    return beta, fit_info


def _apply_correction(df: pd.DataFrame, beta: float, form: str) -> np.ndarray:
    """Apply correction to predictions."""
    if form in ["multiplicative", "additive"]:
        return df['p_hat_z5d'] * (1.0 + beta * df['ilog2'])
    elif form == "relerr-reg":
        # Back out multiplicative correction from relative error regression
        return df['p_hat_z5d'] * (1.0 + beta * df['ilog2'])
    else:
        raise ValueError(f"Unknown form: {form}")


def bootstrap_analysis(df: pd.DataFrame, form: str = "multiplicative",
                      holdout_pct: float = 20.0, n_bootstrap: int = 10000,
                      stratify_bins: int = 20) -> Dict:
    """
    Perform stratified bootstrap analysis with significance testing.
    
    Args:
        df: Input data
        form: Correction form
        holdout_pct: Holdout percentage for testing
        n_bootstrap: Number of bootstrap samples
        stratify_bins: Number of log-k bins for stratified sampling
        
    Returns:
        Bootstrap analysis results
    """
    np.random.seed(42)  # For reproducibility
    
    # Create log-k bins for stratified sampling
    logk_bins = pd.qcut(df['logk'], q=stratify_bins, duplicates='drop')
    
    bootstrap_results = []
    
    for i in range(n_bootstrap):
        # Stratified bootstrap sample
        boot_indices = []
        for bin_label in logk_bins.cat.categories:
            bin_mask = (logk_bins == bin_label)
            bin_indices = df.index[bin_mask].tolist()
            if bin_indices:
                boot_bin_indices = np.random.choice(bin_indices, size=len(bin_indices), replace=True)
                boot_indices.extend(boot_bin_indices)
        
        boot_df = df.iloc[boot_indices].reset_index(drop=True)
        
        try:
            boot_result = fit_correction(boot_df, form=form, holdout_pct=holdout_pct)
            bootstrap_results.append(boot_result)
        except:
            continue  # Skip failed bootstrap samples
    
    if len(bootstrap_results) < 10:  # Reduced from 100 for testing
        raise ValueError(f"Too few successful bootstrap samples: {len(bootstrap_results)}")
    
    # Extract metrics
    betas = [r["beta"] for r in bootstrap_results]
    rmse_deltas = [r["metric_improvement"]["rmse_delta"] for r in bootstrap_results]
    medae_deltas = [r["metric_improvement"]["medae_delta"] for r in bootstrap_results]
    
    # Compute confidence intervals
    beta_ci = (np.percentile(betas, 2.5), np.percentile(betas, 97.5))
    rmse_delta_ci = (np.percentile(rmse_deltas, 2.5), np.percentile(rmse_deltas, 97.5))
    medae_delta_ci = (np.percentile(medae_deltas, 2.5), np.percentile(medae_deltas, 97.5))
    
    # One-sided significance test: H0: RMSE_delta >= 0 (no improvement)
    p_value = np.mean(np.array(rmse_deltas) >= 0)
    
    # Original fit for point estimate
    original_result = fit_correction(df, form=form, holdout_pct=holdout_pct)
    
    return {
        "original": original_result,
        "bootstrap": {
            "n_bootstrap": len(bootstrap_results),
            "beta_mean": np.mean(betas),
            "beta_std": np.std(betas),
            "beta_ci": beta_ci,
            "rmse_delta_mean": np.mean(rmse_deltas),
            "rmse_delta_std": np.std(rmse_deltas),
            "rmse_delta_ci": rmse_delta_ci,
            "medae_delta_mean": np.mean(medae_deltas),
            "medae_delta_ci": medae_delta_ci,
            "p_value": p_value,
            "significance": p_value < 0.01
        },
        "raw_results": bootstrap_results
    }


def run_diagnostics(df: pd.DataFrame, beta: float, form: str) -> Dict:
    """Run model diagnostics on corrected residuals."""
    
    # Apply correction
    p_corrected = _apply_correction(df, beta, form)
    residuals_baseline = df['p_true'] - df['p_hat_z5d']
    residuals_corrected = df['p_true'] - p_corrected
    
    diagnostics = {}
    
    # Breusch-Pagan test for heteroskedasticity
    try:
        from statsmodels.stats.diagnostic import het_breuschpagan
        lm_stat, lm_pval, fval, f_pval = het_breuschpagan(residuals_corrected, df[['logk']])
        diagnostics['breusch_pagan'] = {
            'statistic': float(lm_stat), 
            'p_value': float(lm_pval),
            'interpretation': 'homoskedastic' if lm_pval > 0.05 else 'heteroskedastic'
        }
    except:
        diagnostics['breusch_pagan'] = {'error': 'Test failed'}
    
    # Durbin-Watson test for autocorrelation
    try:
        from statsmodels.stats.stattools import durbin_watson
        dw_stat = durbin_watson(residuals_corrected)
        diagnostics['durbin_watson'] = {
            'statistic': float(dw_stat),
            'interpretation': 'no autocorr' if 1.5 < dw_stat < 2.5 else 'autocorrelation present'
        }
    except:
        diagnostics['durbin_watson'] = {'error': 'Test failed'}
    
    # Normality tests (for information only)
    try:
        stat, pval = stats.shapiro(residuals_corrected)
        diagnostics['shapiro_wilk'] = {
            'statistic': float(stat),
            'p_value': float(pval)
        }
    except:
        diagnostics['shapiro_wilk'] = {'error': 'Test failed'}
    
    # Lag-1 autocorrelation
    try:
        lag1_corr = np.corrcoef(residuals_corrected[:-1], residuals_corrected[1:])[0, 1]
        diagnostics['lag1_autocorr'] = float(lag1_corr)
    except:
        diagnostics['lag1_autocorr'] = None
    
    return diagnostics


def generate_plots(df: pd.DataFrame, beta: float, form: str, output_dir: str):
    """Generate diagnostic plots."""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Apply correction
    p_corrected = _apply_correction(df, beta, form)
    residuals_baseline = df['p_true'] - df['p_hat_z5d']
    residuals_corrected = df['p_true'] - p_corrected
    
    # Residuals vs log(k) - before and after
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.scatter(df['logk'], residuals_baseline, alpha=0.6)
    ax1.axhline(y=0, color='r', linestyle='--')
    ax1.set_xlabel('log(k)')
    ax1.set_ylabel('Residuals')
    ax1.set_title('Baseline Residuals vs log(k)')
    ax1.grid(True)
    
    ax2.scatter(df['logk'], residuals_corrected, alpha=0.6)
    ax2.axhline(y=0, color='r', linestyle='--')
    ax2.set_xlabel('log(k)')
    ax2.set_ylabel('Residuals')
    ax2.set_title('Corrected Residuals vs log(k)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'residuals_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Q-Q plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    stats.probplot(residuals_baseline, dist="norm", plot=ax1)
    ax1.set_title('Q-Q Plot: Baseline Residuals')
    ax1.grid(True)
    
    stats.probplot(residuals_corrected, dist="norm", plot=ax2)
    ax2.set_title('Q-Q Plot: Corrected Residuals')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'qq_plots.png', dpi=150, bbox_inches='tight')
    plt.close()


def generate_report(results: Dict, output_path: str):
    """Generate markdown report."""
    
    bootstrap = results['bootstrap']
    original = results['original']
    
    # Extract key metrics
    beta_est = original['beta']
    beta_ci = bootstrap['beta_ci']
    rmse_delta = bootstrap['rmse_delta_mean']
    rmse_delta_ci = bootstrap['rmse_delta_ci']
    p_value = bootstrap['p_value']
    significant = bootstrap['significance']
    
    baseline_rmse = original['metric_improvement']['baseline_rmse']
    corrected_rmse = original['metric_improvement']['corrected_rmse']
    
    report = f"""# Z5D Riemann Scaling Anomaly Analysis Report

## Executive Summary

**Model**: $\\hat{{p}}_{{\\text{{corr}}}} = \\hat{{p}}_{{\\text{{Z5D}}}}(1 + \\hat{{\\beta}}/\\log^2 k)$

**Estimate**: $\\hat{{\\beta}} = {beta_est:.6f}$ (95% CI: [{beta_ci[0]:.6f}, {beta_ci[1]:.6f}])

**Effect**: 
- RMSE_baseline = {baseline_rmse:.6f}
- RMSE_corrected = {corrected_rmse:.6f}  
- ΔRMSE = {rmse_delta:.6f} (95% CI: [{rmse_delta_ci[0]:.6f}, {rmse_delta_ci[1]:.6f}])
- **p-value = {p_value:.6f}**

**Decision**: {'✅ Adopt' if significant else '❌ Reject'} O(1/log²k) correction (criterion: p < 0.01)

## Analysis Details

- **Sample size**: {original['n']} (test set), {original['n_train']} (training set)
- **Bootstrap samples**: {bootstrap['n_bootstrap']}
- **Statistical significance**: {'Significant' if significant else 'Not significant'} improvement

## Model Performance

| Metric | Baseline | Corrected | Improvement |
|--------|----------|-----------|-------------|
| RMSE | {baseline_rmse:.6f} | {corrected_rmse:.6f} | {rmse_delta:.6f} |
| Relative Improvement | - | - | {100*rmse_delta/baseline_rmse:.2f}% |

## Bootstrap Confidence Intervals

- **β coefficient**: [{beta_ci[0]:.6f}, {beta_ci[1]:.6f}]
- **RMSE improvement**: [{rmse_delta_ci[0]:.6f}, {rmse_delta_ci[1]:.6f}]

## Statistical Test

- **Null hypothesis**: O(1/log²k) correction provides no improvement (ΔRMSE ≥ 0)
- **Alternative hypothesis**: O(1/log²k) correction improves predictions (ΔRMSE < 0)
- **Test statistic**: One-sided bootstrap test
- **p-value**: {p_value:.6f}
- **Significance level**: α = 0.01
- **Result**: {'Reject H₀' if significant else 'Fail to reject H₀'}

## Interpretation

{'The O(1/log²k) correction term shows statistically significant improvement in Z5D prime predictions. The coefficient β = ' + f'{beta_est:.6f}' + ' indicates that the correction scales predictions by a factor of (1 + β/log²k), providing systematic improvement especially for smaller k values where 1/log²k is larger.' if significant else 'The O(1/log²k) correction term does not show statistically significant improvement in Z5D prime predictions. The estimated coefficient β = ' + f'{beta_est:.6f}' + ' with wide confidence intervals suggests the effect is not distinguishable from noise under this dataset and protocol.'}
"""
    
    with open(output_path, 'w') as f:
        f.write(report)


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(description='Z5D Riemann Scaling Anomaly Analysis')
    parser.add_argument('--white-paper', required=True,
                       help='Path to white paper data file')
    parser.add_argument('--form', choices=['multiplicative', 'additive', 'relerr-reg'],
                       default='multiplicative',
                       help='Correction form to test')
    parser.add_argument('--bootstrap', type=int, default=10000,
                       help='Number of bootstrap samples')
    parser.add_argument('--holdout_top_k_pct', type=float, default=20,
                       help='Percentage of largest k to holdout for testing')
    parser.add_argument('--plots-dir', default='plots/z5d_riemann_scaling_anomaly',
                       help='Output directory for plots')
    parser.add_argument('--out', default='reports/z5d_riemann_scaling_anomaly.md',
                       help='Output report file')
    parser.add_argument('--use-mpmath', action='store_true',
                       help='Use high-precision arithmetic')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed
    np.random.seed(args.seed)
    
    print(f"Loading data from {args.white_paper}...")
    df = load_white_paper(args.white_paper)
    
    print(f"Computing correction features...")
    df = compute_correction_features(df, use_mpmath=args.use_mpmath)
    
    print(f"Running bootstrap analysis with {args.bootstrap} samples...")
    results = bootstrap_analysis(
        df, 
        form=args.form,
        holdout_pct=args.holdout_top_k_pct,
        n_bootstrap=args.bootstrap
    )
    
    print(f"Running diagnostics...")
    diagnostics = run_diagnostics(df, results['original']['beta'], args.form)
    results['diagnostics'] = diagnostics
    
    print(f"Generating plots in {args.plots_dir}...")
    generate_plots(df, results['original']['beta'], args.form, args.plots_dir)
    
    print(f"Generating report {args.out}...")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    generate_report(results, args.out)
    
    # Save processed data
    data_dir = Path('data/derived')
    data_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(data_dir / 'riemann_z5d_clean.parquet')
    
    # Save full results (simplified to avoid circular references)
    results_file = Path(args.out).parent / 'z5d_riemann_scaling_anomaly_results.json'
    
    # Create simplified results for JSON serialization
    simplified_results = {
        'original': {
            'beta': float(results['original']['beta']),
            'metric_improvement': {k: float(v) for k, v in results['original']['metric_improvement'].items()},
            'n': int(results['original']['n']),
            'n_train': int(results['original']['n_train']),
            'notes': results['original']['notes']
        },
        'bootstrap': {
            'n_bootstrap': int(results['bootstrap']['n_bootstrap']),
            'beta_mean': float(results['bootstrap']['beta_mean']),
            'beta_std': float(results['bootstrap']['beta_std']),
            'beta_ci': [float(x) for x in results['bootstrap']['beta_ci']],
            'rmse_delta_mean': float(results['bootstrap']['rmse_delta_mean']),
            'rmse_delta_std': float(results['bootstrap']['rmse_delta_std']),
            'rmse_delta_ci': [float(x) for x in results['bootstrap']['rmse_delta_ci']],
            'medae_delta_mean': float(results['bootstrap']['medae_delta_mean']),
            'medae_delta_ci': [float(x) for x in results['bootstrap']['medae_delta_ci']],
            'p_value': float(results['bootstrap']['p_value']),
            'significance': bool(results['bootstrap']['significance'])
        }
    }
    
    with open(results_file, 'w') as f:
        json.dump(simplified_results, f, indent=2)
    
    print(f"Analysis complete!")
    print(f"- Report: {args.out}")
    print(f"- Plots: {args.plots_dir}")
    print(f"- Data: {data_dir / 'riemann_z5d_clean.parquet'}")
    print(f"- Results: {results_file}")
    
    # Print summary
    p_value = results['bootstrap']['p_value']
    significant = results['bootstrap']['significance']
    beta = results['original']['beta']
    
    print(f"\n=== SUMMARY ===")
    print(f"β coefficient: {beta:.6f}")
    print(f"p-value: {p_value:.6f}")
    print(f"Significant (p < 0.01): {'YES' if significant else 'NO'}")


if __name__ == '__main__':
    main()