#!/usr/bin/env python3
"""
Z-normalization Artifacts Experiment

Tests whether observed prime gap autocorrelation (ACF(1) ≈ 0.8) is a mathematical
artifact caused by Z-normalization of finite datasets.
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings("ignore")

# Set random seed for reproducibility
np.random.seed(42)

# Constants
M = 50  # Number of Monte Carlo replicates (testing with smaller M first)
SAMPLE_SIZES = [100, 500, 1000, 5000, 10000]
DISTRIBUTIONS = ["gaussian", "uniform", "poisson", "lognormal", "pareto", "geometric"]
MAX_LAGS = 20


class ZNormalizationExperiment:
    """Main class for running Z-normalization artifact experiments."""

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Results storage
        self.results = {}
        self.acf_decay_data = {}

    def generate_iid_data(self, distribution: str, n: int) -> np.ndarray:
        """Generate i.i.d. data from specified distribution."""
        if distribution == "gaussian":
            return np.random.normal(0, 1, n)
        elif distribution == "uniform":
            return np.random.uniform(0, 1, n)
        elif distribution == "poisson":
            return np.random.poisson(5, n).astype(float)
        elif distribution == "lognormal":
            return np.random.lognormal(0, 1, n)
        elif distribution == "pareto":
            # Pareto distribution with shape parameter α=2 (heavy-tailed)
            return np.random.pareto(2, n)
        elif distribution == "geometric":
            # Geometric distribution (discrete, gap-like)
            return np.random.geometric(0.1, n).astype(float)
        else:
            raise ValueError(f"Unknown distribution: {distribution}")

    def z_normalize(self, data: np.ndarray) -> np.ndarray:
        """Apply Z-normalization (standardization)."""
        return (data - np.mean(data)) / np.std(data)

    def compute_acf(self, data: np.ndarray, nlags: int = MAX_LAGS) -> np.ndarray:
        """Compute sample autocorrelation function."""
        # Use statsmodels acf with fft=False for consistency
        acf_vals = acf(data, nlags=nlags, fft=False)
        return np.array(acf_vals)

    def compute_bias_corrected_acf(
        self, data: np.ndarray, nlags: int = MAX_LAGS
    ) -> np.ndarray:
        """Compute bias-corrected autocorrelation function.

        Uses the Bartlett correction: divide by (N - k) instead of N for lag k.
        This reduces finite-sample bias, especially for small N.
        """
        n = len(data)
        acf_vals = np.zeros(nlags + 1)

        # Compute mean and variance
        mean = np.mean(data)
        var = np.var(data, ddof=0)  # Population variance

        # Compute ACF with bias correction
        for k in range(nlags + 1):
            if k == 0:
                acf_vals[k] = 1.0
            else:
                # Bias-corrected estimator: divide by (n - k)
                numerator = np.sum((data[:-k] - mean) * (data[k:] - mean))
                denominator = (n - k) * var
                acf_vals[k] = numerator / denominator if denominator != 0 else 0

        return acf_vals

    def run_single_replicate(self, distribution: str, n: int) -> Dict[str, float]:
        """Run a single Monte Carlo replicate."""
        # Generate i.i.d. data
        X = self.generate_iid_data(distribution, n)

        # Z-normalize
        Z = self.z_normalize(X)

        # Compute both standard and bias-corrected ACF
        acf_standard = self.compute_acf(Z, nlags=MAX_LAGS)
        acf_corrected = self.compute_bias_corrected_acf(Z, nlags=MAX_LAGS)

        # Return results (using standard ACF for main analysis, corrected for comparison)
        result = {"acf1_standard": acf_standard[1], "acf1_corrected": acf_corrected[1]}
        for k in range(2, MAX_LAGS + 1):
            result[f"acf{k}_standard"] = acf_standard[k]
            result[f"acf{k}_corrected"] = acf_corrected[k]

        return result

    def run_monte_carlo(
        self, distribution: str, n: int, m: int = M
    ) -> Dict[str, np.ndarray]:
        """Run Monte Carlo simulation for given distribution and sample size."""
        print(f"Running {m} replicates for {distribution}, N={n}")

        # Storage for results (both standard and bias-corrected ACF)
        acf_lists: Dict[str, List[float]] = {}
        for k in range(1, MAX_LAGS + 1):
            acf_lists[f"acf{k}_standard"] = []
            acf_lists[f"acf{k}_corrected"] = []

        for replicate in range(m):
            if replicate % 100 == 0:
                print(f"  Replicate {replicate + 1}/{m}")

            result = self.run_single_replicate(distribution, n)

            for key, value in result.items():
                acf_lists[key].append(float(value))

        # Convert to numpy arrays
        acf_arrays: Dict[str, np.ndarray] = {}
        for key in acf_lists:
            acf_arrays[key] = np.array(acf_lists[key])

        return acf_arrays

    def compute_statistics(self, acf_values: np.ndarray) -> Dict[str, float]:
        """Compute statistical measures for ACF values."""
        mean_val = np.mean(acf_values)
        std_val = np.std(acf_values, ddof=1)
        se = std_val / np.sqrt(len(acf_values))

        # One-sample t-test against 0
        t_test_result = stats.ttest_1samp(acf_values, 0)
        t_stat = float(t_test_result[0])
        p_value = float(t_test_result[1])

        # Effect size (Cohen's d)
        cohens_d = float(mean_val / std_val if std_val > 0 else 0)

        return {
            "mean": float(mean_val),
            "std": float(std_val),
            "se": float(se),
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "cohens_d": float(cohens_d),
        }

    def run_experiment(self):
        """Run the complete experiment."""
        print("Starting Z-normalization artifact experiment...")

        for distribution in DISTRIBUTIONS:
            print(f"\nProcessing distribution: {distribution}")

            for n in SAMPLE_SIZES:
                print(f"  Sample size N={n}")

                # Run Monte Carlo
                acf_data = self.run_monte_carlo(distribution, n)

                # Compute statistics for each lag (both standard and corrected)
                stats_results = {}
                for lag in range(1, MAX_LAGS + 1):
                    key_standard = f"acf{lag}_standard"
                    key_corrected = f"acf{lag}_corrected"
                    stats_results[key_standard] = self.compute_statistics(
                        acf_data[key_standard]
                    )
                    stats_results[key_corrected] = self.compute_statistics(
                        acf_data[key_corrected]
                    )

                # Store results
                key = (distribution, n)
                self.results[key] = {"acf_data": acf_data, "statistics": stats_results}

                # Store ACF decay data for plotting (using standard ACF for main plots)
                self.acf_decay_data[key] = {
                    "lags": list(range(1, MAX_LAGS + 1)),
                    "mean_acf": [
                        stats_results[f"acf{k}_standard"]["mean"]
                        for k in range(1, MAX_LAGS + 1)
                    ],
                    "se_acf": [
                        stats_results[f"acf{k}_standard"]["se"]
                        for k in range(1, MAX_LAGS + 1)
                    ],
                }

        print("\nExperiment completed!")
        self.save_results()

    def save_results(self):
        """Save results to files."""
        # Save raw results as JSON
        results_serializable = {}
        for key, value in self.results.items():
            dist, n = key
            results_serializable[f"{dist}_{n}"] = {"statistics": value["statistics"]}

        with open(self.output_dir / "experiment_results.json", "w") as f:
            json.dump(results_serializable, f, indent=2)

        # Create summary table
        self.create_summary_table()

        print(f"Results saved to {self.output_dir}")

    def create_summary_table(self):
        """Create a summary table of ACF(1) results for both standard and bias-corrected estimators."""
        rows = []
        for distribution in DISTRIBUTIONS:
            for n in SAMPLE_SIZES:
                key = (distribution, n)
                stats_standard = self.results[key]["statistics"]["acf1_standard"]
                stats_corrected = self.results[key]["statistics"]["acf1_corrected"]

                row = {
                    "Distribution": distribution.capitalize(),
                    "N": n,
                    "Mean_ACF1_Standard": round(stats_standard["mean"], 4),
                    "SE_Standard": round(stats_standard["se"], 4),
                    "Mean_ACF1_Corrected": round(stats_corrected["mean"], 4),
                    "SE_Corrected": round(stats_corrected["se"], 4),
                    "t_stat_standard": round(stats_standard["t_stat"], 4),
                    "p_value_standard": round(stats_standard["p_value"], 6),
                    "t_stat_corrected": round(stats_corrected["t_stat"], 4),
                    "p_value_corrected": round(stats_corrected["p_value"], 6),
                }
                rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(self.output_dir / "acf1_summary.csv", index=False)

    def create_plots(self):
        """Create all required visualizations."""
        print("Creating plots...")

        # Set style
        plt.style.use("default")
        sns.set_palette("husl")

        # Plot 1: ACF(1) vs sample size
        self.plot_acf1_vs_sample_size()

        # Plot 2: ACF decay for different distributions
        self.plot_acf_decay()

        # Plot 3: Distribution of ACF(1) values
        self.plot_acf1_distribution()

        # Plot 4: ACF comparison across distributions
        self.plot_acf_comparison()

        print("Plots created!")

    def plot_acf1_vs_sample_size(self):
        """Plot ACF(1) vs sample size on log-log scale."""
        fig, ax = plt.subplots(figsize=(10, 6))

        for distribution in DISTRIBUTIONS:
            n_values = []
            mean_acf1 = []
            se_values = []

            for n in SAMPLE_SIZES:
                key = (distribution, n)
                stats_acf1 = self.results[key]["statistics"]["acf1_standard"]
                n_values.append(n)
                mean_acf1.append(stats_acf1["mean"])
                se_values.append(stats_acf1["se"])

            # Plot with error bars
            ax.errorbar(
                n_values,
                mean_acf1,
                yerr=se_values,
                label=distribution.capitalize(),
                marker="o",
                capsize=3,
            )

        ax.set_xscale("log")
        ax.set_xlabel("Sample Size (N)")
        ax.set_ylabel("Mean ACF(1)")
        ax.set_title("ACF(1) vs Sample Size (Z-normalized i.i.d. data)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.axhline(y=0, color="black", linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig(
            self.output_dir / "acf1_vs_sample_size.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def plot_acf_decay(self):
        """Plot ACF decay for different lags and distributions."""
        fig, axes = plt.subplots(3, 2, figsize=(12, 12))
        axes = axes.flatten()

        for idx, distribution in enumerate(DISTRIBUTIONS):
            ax = axes[idx]

            for n in SAMPLE_SIZES[::2]:  # Plot every other N for clarity
                key = (distribution, n)
                decay_data = self.acf_decay_data[key]

                lags = decay_data["lags"]
                mean_acf = decay_data["mean_acf"]
                se_acf = decay_data["se_acf"]

                ax.errorbar(
                    lags,
                    mean_acf,
                    yerr=se_acf,
                    label=f"N={n}",
                    marker="o",
                    markersize=3,
                    capsize=2,
                )

            ax.set_xlabel("Lag (k)")
            ax.set_ylabel("ACF(k)")
            ax.set_title(f"{distribution.capitalize()} Distribution")
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.axhline(y=0, color="black", linestyle="--", alpha=0.5)
            ax.set_ylim(-0.5, 0.5)

        plt.tight_layout()
        plt.savefig(self.output_dir / "acf_decay.png", dpi=300, bbox_inches="tight")
        plt.close()

    def plot_acf1_distribution(self):
        """Plot histogram of ACF(1) values across replicates."""
        fig, axes = plt.subplots(3, 2, figsize=(12, 12))
        axes = axes.flatten()

        for idx, distribution in enumerate(DISTRIBUTIONS):
            ax = axes[idx]

            # Use N=1000 for the histogram
            key = (distribution, 1000)
            acf1_values = self.results[key]["acf_data"]["acf1_standard"]

            ax.hist(acf1_values, bins=30, alpha=0.7, edgecolor="black")
            ax.axvline(
                np.mean(acf1_values),
                color="red",
                linestyle="--",
                label=f"Mean = {np.mean(acf1_values):.3f}",
            )
            ax.set_xlabel("ACF(1)")
            ax.set_ylabel("Frequency")
            ax.set_title(f"{distribution.capitalize()} (N=1000)")
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(
            self.output_dir / "acf1_distribution.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def plot_acf_comparison(self):
        """Plot ACF comparison across distributions for N=1000."""
        fig, ax = plt.subplots(figsize=(10, 6))

        n = 1000  # Use N=1000 for comparison

        for distribution in DISTRIBUTIONS:
            key = (distribution, n)
            decay_data = self.acf_decay_data[key]

            lags = decay_data["lags"]
            mean_acf = decay_data["mean_acf"]
            se_acf = decay_data["se_acf"]

            ax.errorbar(
                lags,
                mean_acf,
                yerr=se_acf,
                label=distribution.capitalize(),
                marker="o",
                capsize=3,
            )

        ax.set_xlabel("Lag (k)")
        ax.set_ylabel("ACF(k)")
        ax.set_title(f"ACF Comparison Across Distributions (N={n})")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.axhline(y=0, color="black", linestyle="--", alpha=0.5)
        ax.set_ylim(-0.3, 0.3)

        plt.tight_layout()
        plt.savefig(
            self.output_dir / "synthetic_comparison.png", dpi=300, bbox_inches="tight"
        )
        plt.close()


def main():
    """Main function to run the experiment."""
    # Create experiment instance
    experiment = ZNormalizationExperiment()

    # Run the experiment
    experiment.run_experiment()

    # Create plots
    experiment.create_plots()

    print("\nExperiment complete! Check the 'results' directory for outputs.")


if __name__ == "__main__":
    main()
