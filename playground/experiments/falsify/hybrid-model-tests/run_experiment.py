#!/usr/bin/env python3
"""
Hybrid Model Comparison Experiment
Falsifying claims about prime gap statistical properties
"""

import numpy as np
import pandas as pd
import os
import sys
from tqdm import tqdm

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models import (
    LognormalARMA, ExponentialDrift, FractionalGNLognormal,
    GARCHLognormal, CorrelatedCramer, AdditiveDecomposition
)
from analysis import (
    compute_target_stats, analyze_model, rank_models, check_falsification_criteria
)
from visualization import create_all_plots

def load_prime_gaps(data_path, n_samples=None):
    """Load prime log gaps from CSV file"""
    print(f"Loading data from {data_path}")
    data = pd.read_csv(data_path, header=None).values.flatten()

    if n_samples and len(data) > n_samples:
        data = data[:n_samples]

    print(f"Loaded {len(data)} log gap samples")
    return data

def main():
    # Configuration
    DATA_PATH = "/Users/velocityworks/IdeaProjects/playground/experiments/PR-0002_prime_log_gap_falsification/data/log_gaps_1000000.csv"
    N_SAMPLES = 50000  # Use subset for faster computation
    OUTPUT_DIR = "/Users/velocityworks/IdeaProjects/playground/experiments/falsify/hybrid-model-tests/results"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Load real prime gap data
    print("Step 1: Loading prime gap data...")
    real_gaps = load_prime_gaps(DATA_PATH, N_SAMPLES)

    # Step 2: Compute target statistics
    print("Step 2: Computing target statistics...")
    target_stats = compute_target_stats(real_gaps)
    print(f"Target stats: mean={target_stats['mean']:.4f}, std={target_stats['std']:.4f}")
    print(f"ACF(1)={target_stats['acf1']:.4f}, P95={target_stats['p95']:.4f}")

    # Step 3: Initialize models
    print("Step 3: Initializing hybrid models...")
    models = [
        LognormalARMA(),
        ExponentialDrift(),
        FractionalGNLognormal(),
        GARCHLognormal(),
        CorrelatedCramer(),
        AdditiveDecomposition()
    ]

    # Step 4: Fit models and generate synthetic data
    print("Step 4: Fitting models and generating synthetic data...")
    synthetic_data = {}
    results = []

    for model in tqdm(models, desc="Processing models"):
        print(f"\nFitting {model.name}...")

        # Fit parameters
        params = model.fit(target_stats)
        print(f"Best params: {params}")

        # Generate synthetic data
        synth_gaps = model.simulate(params, len(real_gaps))
        synthetic_data[model.name] = synth_gaps

        # Analyze performance
        result = analyze_model(real_gaps, synth_gaps, model.name, params)
        results.append(result)

        print(f"KS distance: {result['d_ks']:.4f}, p-value: {result['p_value_ks']:.4f}")
        print(f"ACF error: {result['acf_error']:.4f}")

    # Step 5: Rank models
    print("\nStep 5: Ranking models...")
    ranked_results = rank_models(results)

    # Step 6: Check falsification criteria
    print("Step 6: Checking falsification criteria...")
    conclusion = check_falsification_criteria(results)
    print(f"Conclusion: {conclusion}")

    # Step 7: Create visualizations
    print("Step 7: Creating visualizations...")
    create_all_plots(real_gaps, synthetic_data, ranked_results, OUTPUT_DIR)

    # Step 8: Generate report
    print("Step 8: Generating report...")
    generate_report(results, ranked_results, conclusion, target_stats, OUTPUT_DIR)

    print(f"\nExperiment completed! Results saved to {OUTPUT_DIR}")

def generate_report(results, ranked_results, conclusion, target_stats, output_dir):
    """Generate markdown report"""
    report_path = os.path.join(output_dir, 'hybrid_model_report.md')

    with open(report_path, 'w') as f:
        f.write("# Hybrid Model Comparison Report\n\n")
        f.write("## Objective\n")
        f.write("Test whether hybrid stochastic models can replicate the statistical properties ")
        f.write("claimed for prime gaps, thereby falsifying claims of uniqueness.\n\n")

        f.write("## Target Statistics\n")
        f.write(f"- **Mean**: {target_stats['mean']:.4f}\n")
        f.write(f"- **Std Dev**: {target_stats['std']:.4f}\n")
        f.write(f"- **Skewness**: {target_stats['skewness']:.4f}\n")
        f.write(f"- **Kurtosis**: {target_stats['kurtosis']:.4f}\n")
        f.write(f"- **95th percentile**: {target_stats['p95']:.4f}\n")
        f.write(f"- **99th percentile**: {target_stats['p99']:.4f}\n")
        f.write(f"- **ACF(1)**: {target_stats['acf1']:.4f}\n\n")

        f.write("## Model Results\n\n")
        f.write("| Model | KS Distance | p-value | ACF Error | Tail Disc. | AIC |\n")
        f.write("|-------|------------|---------|-----------|------------|-----|\n")

        for result in ranked_results:
            f.write(f"| {result['model']} | {result['d_ks']:.4f} | {result['p_value_ks']:.4f} | ")
            f.write(f"{result['acf_error']:.4f} | {result['tail_discrepancy']:.4f} | {result['aic']:.1f} |\n")

        f.write("\n## Best Parameters\n\n")
        for result in ranked_results:
            f.write(f"### {result['model']}\n")
            f.write(f"Parameters: {result['params']}\n\n")

        f.write("## Conclusion\n\n")
        f.write(f"**{conclusion}**\n\n")

        f.write("## Interpretation\n\n")
        if "FALSIFIED" in conclusion:
            f.write("The results suggest that prime gap statistical properties are not unique ")
            f.write("and can be replicated by tuned synthetic models. This challenges claims ")
            f.write("of special structure in prime gaps.\n\n")
        elif "SUPPORTED" in conclusion:
            f.write("No hybrid model could adequately match prime gap statistics, ")
            f.write("providing support for the uniqueness of prime gap properties.\n\n")
        else:
            f.write("Mixed results require further investigation.\n\n")

        f.write("## Visualizations\n\n")
        f.write("- `distribution_comparison.png`: Histogram overlays\n")
        f.write("- `acf_comparison.png`: Autocorrelation function comparisons\n")
        f.write("- `qq_plots.png`: Quantile-quantile plots\n")
        f.write("- `model_ranking.png`: Performance comparison\n")
        f.write("- `parameter_sensitivity.png`: Parameter sensitivity analysis\n")

if __name__ == "__main__":
    main()
