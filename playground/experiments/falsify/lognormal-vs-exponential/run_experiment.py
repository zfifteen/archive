#!/usr/bin/env python3
"""
Falsification Experiment: Lognormal vs Exponential Distribution for Prime Gaps

This script implements the falsification test described in TECH-SPEC.md.
It tests whether prime gaps in log-space are better modeled by lognormal distributions
than by exponential distributions across multiple disjoint ranges and bands.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.optimize import minimize
import seaborn as sns
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Metrics for a fitted model on test data."""

    name: str
    params: Dict[str, float]
    log_likelihood: float
    aic: float
    bic: float
    ks_stat: float
    ks_pvalue: float
    ad_stat: Optional[float] = None
    ad_pvalue: Optional[float] = None


@dataclass
class BandResult:
    """Results for a single band."""

    range_id: str
    band_id: int
    p_min: float
    p_max: float
    n_train: int
    n_test: int
    exp_metrics: ModelMetrics
    ln_metrics: ModelMetrics
    winner: str  # "lognormal", "exponential", or "ambiguous"
    delta_bic: float  # BIC_exp - BIC_ln (positive favors lognormal)
    delta_logl: float  # logL_ln - logL_exp (positive favors lognormal)


class PrimeGenerator:
    """Generates primes using Python port (z5d)."""

    def __init__(self):
        from python_prime_generator import PythonPrimeGenerator

        self.py_gen = PythonPrimeGenerator()

    def generate_range(self, start: int, end: int) -> np.ndarray:
        """
        Generate primes in [start, end] using z5d/python generator (sequential).
        Estimates count via PNT approximation; generates until end.
        """
        import math

        if start < 2:
            start = 2

        log_start = math.log(start) if start > 1 else 1
        estimated_count = int((end - start) / log_start) + 1000  # Buffer for accuracy

        all_primes = []
        current = start
        for _ in range(estimated_count + 1000):  # Extra buffer
            if current > end:
                break
            prime, _ = self.py_gen.next_prime_from(current)
            if prime > end:
                break
            all_primes.append(prime)
            current = prime + 2  # Next odd candidate

        return np.array(all_primes, dtype=object)


class DistributionFitter:
    """Fits and evaluates distributions."""

    def fit_exponential(self, data: np.ndarray) -> Tuple[float]:
        """
        Fit exponential distribution.
        Returns (scale,) where scale = 1/lambda.
        Standard exponential has loc=0 fixed.
        """
        # MLE for exponential: scale = mean
        scale = np.mean(data)
        return (scale,)

    def fit_lognormal(self, data: np.ndarray) -> Tuple[float, float]:
        """
        Fit lognormal distribution.
        Returns (s, scale) where loc=0 is fixed.
        s=sigma, scale=exp(mu).
        """
        # Check for positive data
        if np.any(data <= 0):
            raise ValueError("Lognormal requires positive data")

        # Convert to float for log (handles large ints)
        data_float = np.array(data, dtype=float)

        # MLE for lognormal: fit normal to log(data)
        log_data = np.log(data_float)
        mu = np.mean(log_data)
        # CRITICAL FIX: Use ddof=1 for unbiased estimator (MLE with sample correction)
        sigma = np.std(log_data, ddof=1)

        # Scipy parameterization: s=sigma, scale=exp(mu), loc=0
        return (sigma, np.exp(mu))

    def evaluate_exponential(
        self, data: np.ndarray, params: Tuple[float]
    ) -> ModelMetrics:
        """Evaluate exponential fit on data."""
        (scale,) = params
        n = len(data)
        data_float = np.array(data, dtype=float)

        # Log likelihood
        log_l = np.sum(stats.expon.logpdf(data_float, loc=0, scale=scale))

        # CRITICAL FIX: k=1 parameter (scale only, loc=0 fixed)
        k = 1
        aic = 2 * k - 2 * log_l
        bic = k * np.log(n) - 2 * log_l

        # KS Test
        ks_stat, ks_p = stats.kstest(data_float, "expon", args=(0, scale))

        return ModelMetrics(
            name="exponential",
            params={"scale": scale, "lambda": 1.0 / scale},
            log_likelihood=log_l,
            aic=aic,
            bic=bic,
            ks_stat=ks_stat,
            ks_pvalue=ks_p,
        )

    def evaluate_lognormal(
        self, data: np.ndarray, params: Tuple[float, float]
    ) -> ModelMetrics:
        """Evaluate lognormal fit on data."""
        s, scale = params
        n = len(data)
        data_float = np.array(data, dtype=float)

        # Log likelihood
        log_l = np.sum(stats.lognorm.logpdf(data_float, s=s, loc=0, scale=scale))

        # CRITICAL FIX: k=2 parameters (s, scale; loc=0 fixed)
        k = 2
        aic = 2 * k - 2 * log_l
        bic = k * np.log(n) - 2 * log_l

        # KS Test
        ks_stat, ks_p = stats.kstest(data_float, "lognorm", args=(s, 0, scale))

        return ModelMetrics(
            name="lognormal",
            params={"s": s, "scale": scale, "mu": np.log(scale), "sigma": s},
            log_likelihood=log_l,
            aic=aic,
            bic=bic,
            ks_stat=ks_stat,
            ks_pvalue=ks_p,
        )


class FalsificationExperiment:
    """Main experiment controller."""

    def __init__(self, output_dir: str, seed: int = 42):
        self.output_dir = output_dir
        self.seed = seed
        self.prime_source = "python"  # Always z5d/python
        self.rng = np.random.default_rng(seed)
        self.prime_gen = PrimeGenerator()
        self.fitter = DistributionFitter()

        os.makedirs(output_dir, exist_ok=True)

    def collect_gaps_logband(self, n0, alpha=2.0, max_gaps=10**6, tail_bias=False):
        """
        Collect gaps from the log-band window [n0/alpha, alpha*n0].
        If window too large, use random start within window and generate consecutive gaps.
        """
        low = int(n0 / alpha)
        high = int(alpha * n0)
        window_size = high - low

        import math

        log_low = math.log(low) if low > 1 else 1
        estimated_primes = int(window_size / log_low) + 10000

        MAX_PRIMES_TO_GENERATE = (
            2_000_000  # Cap to prevent long runtime; use random start if exceeded
        )
        MAX_GAPS_FOR_FITTING = max_gaps  # 50k

        all_primes = []
        sampling_method = "full_window"

        if estimated_primes > MAX_PRIMES_TO_GENERATE:
            # Too large: Use random starting point within window, generate consecutive
            mean_gap = int(math.log(n0) * 2)  # Rough estimate for gap size
            max_start_offset = max(1, window_size - MAX_PRIMES_TO_GENERATE * mean_gap)
            start_offset = np.random.randint(0, max_start_offset)
            start = low + start_offset
            logger.info(
                f"n0={n0}: Window too large ({estimated_primes} primes); using random start at {start} within [{low}, {high}]"
            )

            current = start if start >= 2 else 2
            while len(all_primes) < MAX_PRIMES_TO_GENERATE and current < high * 1.1:
                prime, _ = self.prime_gen.py_gen.next_prime_from(current)
                if prime > high:
                    break
                all_primes.append(prime)
                current = prime + 2
            sampling_method = "random_start"
        else:
            # Full window: Sequential from low
            current = low if low >= 2 else 2
            while len(all_primes) < estimated_primes and current < high * 1.1:
                prime, _ = self.prime_gen.py_gen.next_prime_from(current)
                if prime > high:
                    break
                all_primes.append(prime)
                current = prime + 2
            sampling_method = "full_window"

        if len(all_primes) < 2:
            logger.warning(f"Insufficient primes for n0={n0}")
            return np.array([]), {}

        gaps = np.diff(all_primes).astype(float)
        gaps = gaps[gaps > 0]
        original_n = len(gaps)
        subsampled = False
        if original_n > MAX_GAPS_FOR_FITTING:
            selected_indices = np.sort(
                np.random.choice(original_n, MAX_GAPS_FOR_FITTING, replace=False)
            )
            gaps = gaps[selected_indices]
            subsampled = True
            logger.info(f"n0={n0}: Subsampled from {original_n} to {len(gaps)} gaps")

        meta = {
            "n0": n0,
            "alpha": alpha,
            "low": low,
            "high": high,
            "log_width": 2 * np.log10(alpha),
            "realized_N": len(gaps),
            "original_N": original_n,
            "subsampled": subsampled,
            "tail_bias": tail_bias,
            "sampling_method": sampling_method,
            "mean_gap": np.mean(gaps) if len(gaps) > 0 else 0,
            "generated_primes": len(all_primes),
        }
        return gaps, meta

    def run(
        self,
        ranges=None,
        n_bands=6,
        min_gaps=5000,
        alpha=2.0,
        max_gaps=10**6,
        shuffle=False,
        free_loc=True,
        tail_bias=False,
        alphas=None,
        mode="logband",
    ):
        """
        Run the full experiment.
        mode: 'legacy' for original, 'logband' for fixed log-band.
        If alphas is list, run for each and aggregate.
        """
        from scipy.stats import expon, lognorm
        import warnings

        if mode == "legacy":
            all_results = []

            for range_str in ranges:
                logger.info(f"Processing legacy range: {range_str}")
                try:
                    start_str, end_str = range_str.split(":")
                    start, end = int(float(start_str)), int(float(end_str))
                except ValueError:
                    logger.error(
                        f"Invalid range format: {range_str}. Expected start:end (e.g. 1e8:1e9)"
                    )
                    continue

                primes = self.prime_gen.generate_range(start, end)
                if len(primes) < 2:
                    logger.warning(f"Not enough primes in range {range_str}")
                    continue

                gaps = np.diff(primes)
                gap_primes = primes[:-1]

                if end - start < start * 0.01:
                    band_edges = np.linspace(start, end, num=n_bands + 1)
                else:
                    log_min = np.log10(float(start))
                    log_max = np.log10(float(end))
                    band_edges = np.logspace(log_min, log_max, n_bands + 1)

                for i in range(n_bands):
                    band_min = band_edges[i]
                    band_max = band_edges[i + 1]
                    mask = (gap_primes >= band_min) & (gap_primes < band_max)
                    band_gaps = gaps[mask]

                    if len(band_gaps) < min_gaps:
                        logger.warning(
                            f"Band {i} ({band_min:.1e}-{band_max:.1e}) has insufficient gaps: {len(band_gaps)}"
                        )
                        continue

                    logger.info(f"  Band {i}: {len(band_gaps)} gaps")

                    indices = np.arange(len(band_gaps))
                    self.rng.shuffle(indices)
                    shuffled_gaps = band_gaps[indices]

                    split_idx = int(0.7 * len(shuffled_gaps))
                    train_gaps = shuffled_gaps[:split_idx]
                    test_gaps = shuffled_gaps[split_idx:]

                    exp_params = self.fitter.fit_exponential(train_gaps)
                    ln_params = self.fitter.fit_lognormal(train_gaps)

                    exp_metrics = self.fitter.evaluate_exponential(
                        test_gaps, exp_params
                    )
                    ln_metrics = self.fitter.evaluate_lognormal(test_gaps, ln_params)

                    delta_bic = exp_metrics.bic - ln_metrics.bic
                    delta_logl = ln_metrics.log_likelihood - exp_metrics.log_likelihood

                    winner = "ambiguous"
                    if delta_bic >= 10:
                        winner = "lognormal"
                    elif delta_bic <= -10:
                        winner = "exponential"

                    result = BandResult(
                        range_id=range_str,
                        band_id=i,
                        p_min=band_min,
                        p_max=band_max,
                        n_train=len(train_gaps),
                        n_test=len(test_gaps),
                        exp_metrics=exp_metrics,
                        ln_metrics=ln_metrics,
                        winner=winner,
                        delta_bic=delta_bic,
                        delta_logl=delta_logl,
                    )
                    all_results.append(result)

                    if i == 0:
                        self._plot_band_fit(
                            test_gaps, exp_params, ln_params, result, range_str, i
                        )

            self._save_results(all_results)
            self._generate_report(all_results)
            return all_results

        elif mode == "logband":
            SCALES = [10**k for k in range(2, 19)]  # 1e2 to 1e18
            all_results = {}
            if alphas is None:
                alphas = [alpha]

            for a in alphas:
                logger.info(f"Running logband with alpha={a}")
                res = []
                for n0 in SCALES:
                    gaps, meta = self.collect_gaps_logband(
                        n0, alpha=a, max_gaps=max_gaps, tail_bias=tail_bias
                    )
                    if len(gaps) < 1000:
                        logger.warning(f"n0={n0}: Only {len(gaps)} gaps; skipping")
                        continue

                    N = len(gaps)
                    consecutive_gaps_used = (
                        meta["generated_primes"] - 1
                    )  # Gaps from consecutive primes
                    if shuffle:
                        indices = np.arange(N)
                        self.rng.shuffle(indices)
                        gaps = gaps[indices]
                        logger.info(f"n0={n0}: Shuffled gaps")

                    split_idx = int(0.7 * N)
                    train_gaps = gaps[:split_idx]
                    test_gaps = gaps[split_idx:]

                    # Fit exponential
                    if free_loc:
                        exp_params = expon.fit(train_gaps, floc=None)
                    else:
                        exp_params = expon.fit(train_gaps, floc=0)
                    exp_loc, exp_scale = exp_params
                    exp_loglik = stats.expon.logpdf(test_gaps, *exp_params).sum()
                    exp_bic = -2 * exp_loglik + 1 * np.log(N)
                    exp_ks = stats.kstest(test_gaps, "expon", args=exp_params).statistic

                    # Fit lognormal
                    positive_train = train_gaps[train_gaps > 0]
                    if len(positive_train) < 2:
                        logger.warning(
                            f"n0={n0}: Insufficient positive gaps for lognormal"
                        )
                        continue
                    log_train = np.log(positive_train)
                    ln_mu = np.mean(log_train)
                    ln_sigma = np.std(log_train, ddof=0)
                    if free_loc:
                        with warnings.catch_warnings(record=True) as w:
                            warnings.simplefilter("always")
                            ln_params = lognorm.fit(train_gaps, floc=None)
                            if len(w) > 0:
                                ln_params = lognorm.fit(train_gaps, floc=0)
                                logger.warning(f"n0={n0}: Lognormal fallback to loc=0")
                    else:
                        ln_params = lognorm.fit(train_gaps, floc=0)
                    ln_shape, ln_loc, ln_scale = ln_params
                    ln_loglik = stats.lognorm.logpdf(
                        test_gaps[test_gaps > 0], *ln_params
                    ).sum()
                    k_ln = 3 if free_loc and ln_loc > 0 else 2
                    ln_bic = -2 * ln_loglik + k_ln * np.log(N)
                    ln_ks = stats.kstest(test_gaps, "lognorm", args=ln_params).statistic

                    delta_bic = exp_bic - ln_bic
                    winner = (
                        "lognormal"
                        if delta_bic > 10
                        else ("exponential" if delta_bic < -10 else "ambiguous")
                    )

                    r = {
                        "scale": n0,
                        "log10_scale": np.log10(n0),
                        "consecutive_gaps_used": consecutive_gaps_used,
                        "realized_N": N,
                        "mean_gap": np.mean(gaps),
                        "expected_mean": np.log(n0),
                        "exp_bic": exp_bic,
                        "ln_bic": ln_bic,
                        "delta_bic": delta_bic,
                        "exp_ks": exp_ks,
                        "ln_ks": ln_ks,
                        "winner": winner,
                        "alpha": a,
                        "shuffle": shuffle,
                        "free_loc": free_loc,
                        "ln_loc": ln_loc,
                        **meta,
                    }
                    res.append(r)
                    logger.info(
                        f"n0=10^{int(np.log10(n0)):2d}: consecutive_gaps_used={consecutive_gaps_used}, N={N:>8,}, mean={np.mean(gaps):6.2f}, ΔBIC={delta_bic:+8.1f}, winner={winner}"
                    )

                all_results[a] = res

            # Save
            self._save_logband_results(
                all_results, alphas, max_gaps, shuffle, free_loc, tail_bias
            )
            self._generate_logband_report(all_results)
            return all_results

        else:
            raise ValueError(f"Unknown mode: {mode}")

    def _plot_band_fit(
        self,
        data: np.ndarray,
        exp_params: Tuple,
        ln_params: Tuple,
        result: BandResult,
        range_id: str,
        band_id: int,
    ):
        """Generate diagnostic plots for the fit."""
        if len(data) == 0:
            logger.warning(f"No data to plot for {range_id} band {band_id}")
            return

        plt.figure(figsize=(12, 5))

        # Histogram and PDFs
        plt.subplot(1, 2, 1)
        sns.histplot(data, stat="density", alpha=0.3, label="Data")

        x = np.linspace(max(1, min(data)), max(data), 1000)

        # Exp PDF
        (scale_exp,) = exp_params
        y_exp = stats.expon.pdf(x, loc=0, scale=scale_exp)
        plt.plot(x, y_exp, "r-", label=f"Exp (BIC={result.exp_metrics.bic:.0f})")

        # Lognormal PDF
        s_ln, scale_ln = ln_params
        y_ln = stats.lognorm.pdf(x, s=s_ln, loc=0, scale=scale_ln)
        plt.plot(x, y_ln, "g-", label=f"Lognorm (BIC={result.ln_metrics.bic:.0f})")

        plt.title(f"Range {range_id} Band {band_id}\nWinner: {result.winner}")
        plt.xlabel("Gap Size")
        plt.ylabel("Density")
        plt.legend()

        # Q-Q Plot (Log-space for Lognormal)
        plt.subplot(1, 2, 2)
        data_float = np.array(data, dtype=float)
        stats.probplot(np.log(data_float), dist="norm", plot=plt)
        plt.title("Q-Q Plot (Log-Data vs Normal)")

        plt.tight_layout()
        filename = f"fit_{range_id.replace(':', '_')}_band{band_id}.png"
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        logger.info(f"Saved plot: {filename}")

    def _save_results(self, results: List[BandResult]):
        """Save results to JSON and CSV."""
        # JSON
        json_data = [asdict(r) for r in results]
        with open(os.path.join(self.output_dir, "results.json"), "w") as f:
            json.dump(json_data, f, indent=2)

        # CSV
        flat_data = []
        for r in results:
            item = {
                "range_id": r.range_id,
                "band_id": r.band_id,
                "p_min": r.p_min,
                "p_max": r.p_max,
                "n_train": r.n_train,
                "n_test": r.n_test,
                "winner": r.winner,
                "delta_bic": r.delta_bic,
                "delta_logl": r.delta_logl,
                "exp_bic": r.exp_metrics.bic,
                "ln_bic": r.ln_metrics.bic,
                "exp_ks": r.exp_metrics.ks_stat,
                "ln_ks": r.ln_metrics.ks_stat,
                "exp_ks_p": r.exp_metrics.ks_pvalue,
                "ln_ks_p": r.ln_metrics.ks_pvalue,
            }
            flat_data.append(item)

        pd.DataFrame(flat_data).to_csv(
            os.path.join(self.output_dir, "results.csv"), index=False
        )
        logger.info("Results saved to results.json and results.csv")

    def _generate_report(self, results: List[BandResult]):
        """Generate a summary report."""
        if not results:
            logger.warning("No results to report.")
            return

        report = []
        report.append("# Falsification Test Report: Lognormal vs Exponential\n")

        # Overall stats
        n_total = len(results)
        n_ln_wins = sum(1 for r in results if r.winner == "lognormal")
        n_exp_wins = sum(1 for r in results if r.winner == "exponential")
        n_ambiguous = sum(1 for r in results if r.winner == "ambiguous")

        report.append("## Summary\n")
        report.append(f"- Total Bands Tested: {n_total}")
        report.append(
            f"- Lognormal Wins: {n_ln_wins} ({n_ln_wins / n_total * 100:.1f}%)"
        )
        report.append(
            f"- Exponential Wins: {n_exp_wins} ({n_exp_wins / n_total * 100:.1f}%)"
        )
        report.append(
            f"- Ambiguous: {n_ambiguous} ({n_ambiguous / n_total * 100:.1f}%)"
        )

        # Per Range
        report.append("\n## Per-Range Breakdown\n")
        ranges = sorted(list(set(r.range_id for r in results)))

        falsified = False
        falsification_reasons = []

        for rid in ranges:
            range_results = [r for r in results if r.range_id == rid]
            n_range = len(range_results)
            n_r_ln = sum(1 for r in range_results if r.winner == "lognormal")

            report.append(f"### Range {rid}")
            report.append(f"- Bands: {n_range}")
            report.append(f"- Lognormal Wins: {n_r_ln} ({n_r_ln / n_range * 100:.1f}%)")

            # Check falsification criteria per range
            if n_r_ln / n_range < 0.5:
                report.append(f"  - **WARNING**: Lognormal win rate < 50%")

        # Global Falsification Check
        # Criterion: Lognormal fails if it doesn't beat exponential by ΔBIC ≥ 10 in ≥50% of bands
        # across two independent ranges
        ranges_below_50pct = []
        for rid in ranges:
            range_results = [r for r in results if r.range_id == rid]
            if not range_results:
                continue
            n_r_ln = sum(1 for r in range_results if r.winner == "lognormal")
            if n_r_ln / len(range_results) < 0.5:
                ranges_below_50pct.append(rid)

        if len(ranges_below_50pct) >= 2:
            falsified = True
            falsification_reasons.append(
                f"Lognormal win rate < 50% in {len(ranges_below_50pct)} ranges: {ranges_below_50pct}"
            )

        report.append("\n## Conclusion\n")
        if falsified:
            report.append("**RESULT: FALSIFIED**")
            report.append(
                "The claim that lognormal distributions better model prime gaps has been falsified "
                "under the current protocol."
            )
            for reason in falsification_reasons:
                report.append(f"- {reason}")
        else:
            report.append("**RESULT: NOT FALSIFIED**")
            report.append(
                "The data supports the claim that lognormal distributions provide a better fit "
                "than exponential distributions."
            )

        report_text = "\n".join(report)
        with open(os.path.join(self.output_dir, "report.md"), "w") as f:
            f.write(report_text)

        logger.info(f"Report generated at {os.path.join(self.output_dir, 'report.md')}")
        print("\n" + "=" * 80)
        print(report_text)
        print("=" * 80)

    def _save_logband_results(
        self,
        all_results: Dict[float, List[Dict]],
        alphas: List[float],
        max_gaps: int,
        shuffle: bool,
        free_loc: bool,
        tail_bias: bool,
    ):
        """
        Save logband results to JSON and CSV.
        """
        output_dir = self.output_dir + "_logband"
        os.makedirs(output_dir, exist_ok=True)

        output = {
            "experiment": "lognormal_vs_exponential_logband",
            "protocol": {
                "method": "fixed_log_band_width",
                "alphas": alphas,
                "log10_width_per_alpha": {a: 2 * np.log10(a) for a in alphas},
                "max_gaps": max_gaps,
                "subsampling": "tail_biased" if tail_bias else "uniform_random",
                "shuffle": shuffle,
                "free_loc": free_loc,
                "scales": [10**k for k in range(2, 19)],
            },
            "results": {str(a): res for a, res in all_results.items()},
        }

        with open(os.path.join(output_dir, "results_logband.json"), "w") as f:
            json.dump(output, f, indent=2, default=str)

        # CSV
        flat_data = []
        for a, res in all_results.items():
            for r in res:
                r_copy = r.copy()
                r_copy["alpha"] = a
                flat_data.append(r_copy)
        pd.DataFrame(flat_data).to_csv(
            os.path.join(output_dir, "results_logband.csv"), index=False
        )

        logger.info(f"Logband results saved to {output_dir}")

    def _generate_logband_report(self, all_results: Dict[float, List[Dict]]):
        """
        Generate report for logband results.
        """
        report = []
        report.append("# Logband Falsification Test Report")

        # Per alpha summary
        for a, res in all_results.items():
            n_total = len(res)
            n_ln_wins = sum(1 for r in res if r["winner"] == "lognormal")
            n_exp_wins = sum(1 for r in res if r["winner"] == "exponential")
            n_amb = sum(1 for r in res if r["winner"] == "ambiguous")

            report.append(f"## Alpha = {a}")
            report.append(f"- Total Scales: {n_total}")
            report.append(
                f"- Lognormal Wins: {n_ln_wins} ({n_ln_wins / n_total * 100:.1f}%)"
            )
            report.append(
                f"- Exponential Wins: {n_exp_wins} ({n_exp_wins / n_total * 100:.1f}%)"
            )
            report.append(f"- Ambiguous: {n_amb} ({n_amb / n_total * 100:.1f}%)")

            # Crossover approximation
            prev_delta = None
            crossovers = []
            for r in res:
                if prev_delta is not None and prev_delta * r["delta_bic"] < 0:
                    crossovers.append(r["scale"])
                prev_delta = r["delta_bic"]
            if crossovers:
                report.append(f"- Approximate Crossover Scales: {crossovers}")

        # Stability check
        report.append("\n## Stability Across Alphas")
        crossovers_per_alpha = {}
        for a, res in all_results.items():
            prev_delta = None
            crossovers = []
            for r in res:
                if prev_delta is not None and prev_delta * r["delta_bic"] < 0:
                    crossovers.append(r["scale"])
                prev_delta = r["delta_bic"]
            crossovers_per_alpha[a] = crossovers
        report.append(f"Crossover scales per alpha: {crossovers_per_alpha}")
        if (
            all(len(c) > 0 for c in crossovers_per_alpha.values())
            and max(len(c) for c in crossovers_per_alpha.values()) == 1
        ):
            report.append("Stable crossover across alphas (real transition likely).")
        else:
            report.append("Crossover varies or absent (possible artifact).")

        # Overall
        overall_ln_win_rate = sum(
            1 for res in all_results.values() for r in res if r["winner"] == "lognormal"
        ) / sum(len(res) for res in all_results.values() or [1])
        report.append("\n## Conclusion")
        if overall_ln_win_rate < 0.5:
            report.append(
                "**FALSIFIED**: Lognormal does not outperform exponential overall."
            )
        else:
            report.append(
                "**NOT FALSIFIED**: Lognormal provides better fit in most scales."
            )

        report_text = "\n".join(report)
        with open(
            os.path.join(self.output_dir + "_logband", "report_logband.md"), "w"
        ) as f:
            f.write(report_text)

        logger.info("Logband report generated.")
        print(report_text)


def main():
    parser = argparse.ArgumentParser(
        description="Run Lognormal vs Exponential Falsification Test"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="logband",
        choices=["legacy", "logband"],
        help="Mode: 'legacy' for original, 'logband' for fixed log-band sampling",
    )
    parser.add_argument(
        "--ranges",
        type=str,
        default="1e6:1e7,1e7:1e8",
        help="For legacy mode: Comma-separated ranges (e.g. '1e6:1e7,1e7:1e8')",
    )
    parser.add_argument(
        "--scales",
        type=str,
        default="1e2,1e3,1e4,1e5,1e6,1e7,1e8,1e9,1e10,1e11,1e12,1e13,1e14,1e15,1e16,1e17,1e18",
        help="For logband mode: Comma-separated scales (e.g. '1e5,1e6,...')",
    )
    parser.add_argument(
        "--alphas",
        type=str,
        default="2.0",
        help="For logband: Comma-separated alphas (e.g. '1.5,2.0,3.0')",
    )
    parser.add_argument(
        "--max-gaps",
        type=int,
        default=50000,
        help="Max gaps per scale in logband (subsample if exceeded)",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        default=False,
        help="Enable shuffling in logband (default off)",
    )
    parser.add_argument(
        "--free-loc",
        action="store_true",
        default=True,
        help="Allow free loc in fits (default on)",
    )
    parser.add_argument(
        "--tail-bias",
        action="store_true",
        default=False,
        help="Tail-biased subsampling in logband (default uniform)",
    )
    parser.add_argument(
        "--output", type=str, default="results", help="Output directory"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--bands", type=int, default=6, help="For legacy: Number of bands per range"
    )
    parser.add_argument(
        "--min-gaps", type=int, default=5000, help="For legacy: Min gaps per band"
    )

    args = parser.parse_args()

    if args.mode == "legacy":
        ranges = args.ranges.split(",")
        experiment = FalsificationExperiment(args.output, args.seed)
        experiment.run(ranges, n_bands=args.bands, min_gaps=args.min_gaps)
    else:  # logband
        scales = [float(s) for s in args.scales.split(",")]
        alphas_list = [float(a) for a in args.alphas.split(",")]
        experiment = FalsificationExperiment(args.output, args.seed)
        experiment.run(
            ranges=None,
            n_bands=args.bands,
            min_gaps=args.min_gaps,
            alpha=alphas_list[0] if len(alphas_list) == 1 else None,
            max_gaps=args.max_gaps,
            shuffle=args.shuffle,
            free_loc=args.free_loc,
            tail_bias=args.tail_bias,
            alphas=alphas_list,
            mode="logband",
        )


if __name__ == "__main__":
    main()
