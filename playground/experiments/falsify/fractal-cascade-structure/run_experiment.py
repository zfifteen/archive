#!/usr/bin/env python3
"""
Falsification Experiment: Fractal Cascade Structure in Prime Gaps

This script tests whether prime gaps exhibit recursive log-normal structure
within magnitude strata and power-law variance scaling (Hurst exponent).

Key concepts:
- gaps[i] = prime[i+1] - prime[i]  (actual gap sizes)
- If gaps follow lognormal: log(gaps) ~ Normal(μ, σ²)
- Stratify by magnitude, test lognormality within each stratum
- Test variance scaling: Var(stratum) ~ Mean(stratum)^(2H)
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.optimize import curve_fit
import seaborn as sns
from tqdm import tqdm
from sklearn.linear_model import LinearRegression

# Configuration constants
MIN_STRATUM_SIZE = 100
KS_STAT_THRESHOLD = 0.10
KS_P_THRESHOLD = 0.01
BOOTSTRAP_ITERS = 1000
SEED = 42

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@dataclass
class StratumResult:
    """Results for analyzing a single magnitude stratum."""
    range_id: str
    stratum_id: int
    gap_min: float
    gap_max: float
    n_gaps: int
    # Statistics of actual gaps in stratum
    mean_gap: float
    std_gap: float
    # Lognormal fit parameters (fit to log(gap))
    mu_lognormal: float
    sigma_lognormal: float
    # KS test results
    ks_stat: float
    ks_p: float
    pass_ks: bool


@dataclass
class RangeResult:
    """Results for a prime range analysis."""
    range_id: str
    n_gaps: int
    h_estimate: float
    h_95ci_lower: float
    h_95ci_upper: float
    r_squared: float
    n_strata_used: int
    pct_strata_pass_ks: float
    strata_results: List[StratumResult]


@dataclass
class NullModelResult:
    """Results from null model comparison."""
    model_type: str
    range_id: str
    h_estimate: float
    r_squared: float
    pct_strata_pass_ks: float
    delta_h: float


class PrimeGenerator:
    """Generates primes using segmented sieve for memory efficiency."""
    
    def generate_range(self, start: int, end: int) -> np.ndarray:
        """Generate all primes in [start, end] using segmented sieve."""
        if start < 2:
            start = 2
        
        if start > end:
            return np.array([], dtype=np.int64)
        
        chunk_size = 10**6
        primes = []
        
        # Generate small primes for sieving
        limit = int(np.sqrt(end)) + 1
        small_primes = self._simple_sieve(limit)
        
        # Process in chunks
        current_start = start
        with tqdm(total=end-start, desc=f"Generating primes [{start:.1e}, {end:.1e}]", unit="num") as pbar:
            while current_start < end:
                current_end = min(current_start + chunk_size, end)
                chunk_primes = self._segmented_sieve_chunk(current_start, current_end, small_primes)
                if len(chunk_primes) > 0:
                    primes.append(chunk_primes)
                pbar.update(current_end - current_start)
                current_start = current_end
        
        if not primes:
            return np.array([], dtype=np.int64)
        
        return np.concatenate(primes)
    
    def _simple_sieve(self, limit: int) -> np.ndarray:
        """Standard Sieve of Eratosthenes."""
        if limit < 2:
            return np.array([], dtype=np.int64)
        
        is_prime = np.ones(limit + 1, dtype=bool)
        is_prime[0:2] = False
        for i in range(2, int(np.sqrt(limit)) + 1):
            if is_prime[i]:
                is_prime[i*i : limit+1 : i] = False
        return np.nonzero(is_prime)[0]
    
    def _segmented_sieve_chunk(self, start: int, end: int, small_primes: np.ndarray) -> np.ndarray:
        """Sieve a specific chunk using precomputed small primes."""
        length = end - start
        if length <= 0:
            return np.array([], dtype=np.int64)
        
        is_prime = np.ones(length, dtype=bool)
        
        # Mark 0 and 1 as non-prime if in range
        if start <= 0 < end:
            is_prime[0 - start] = False
        if start <= 1 < end:
            is_prime[1 - start] = False
        
        # Sieve using small primes
        limit = int(np.sqrt(end))
        for p in small_primes:
            if p > limit:
                break
            # Find first multiple of p in [start, end)
            first_multiple = ((start + p - 1) // p) * p
            if first_multiple < p * p:
                first_multiple = p * p
            # Mark multiples
            idx = first_multiple - start
            if idx < length:
                is_prime[idx::p] = False
        
        numbers = np.arange(start, end, dtype=np.int64)
        return numbers[is_prime]


class FractalAnalyzer:
    """Analyzes fractal cascade structure in gap sequences."""
    
    def __init__(self, seed: int = SEED):
        self.rng = np.random.default_rng(seed)
    
    def analyze_range(self, range_id: str, gaps: np.ndarray, n_strata: int) -> Optional[RangeResult]:
        """Perform full fractal analysis on gap sequence."""
        
        # Filter out any invalid gaps
        valid_gaps = gaps[gaps > 0]
        if len(valid_gaps) < n_strata * MIN_STRATUM_SIZE:
            logger.warning(f"Not enough valid gaps for range {range_id}")
            return None
        
        logger.info(f"Analyzing {len(valid_gaps)} gaps with {n_strata} strata")
        
        # Stratify by quantiles (equal number per stratum)
        try:
            quantiles = np.linspace(0, 100, n_strata + 1)
            bin_edges = np.percentile(valid_gaps, quantiles)
        except Exception as e:
            logger.error(f"Error computing quantiles: {e}")
            return None
        
        strata_results = []
        stratum_means = []
        stratum_stds = []
        
        for i in range(n_strata):
            lower = bin_edges[i]
            upper = bin_edges[i+1]
            
            # Extract gaps in this stratum
            if i == n_strata - 1:
                mask = (valid_gaps >= lower) & (valid_gaps <= upper)
            else:
                mask = (valid_gaps >= lower) & (valid_gaps < upper)
            
            stratum_gaps = valid_gaps[mask]
            n_gaps = len(stratum_gaps)
            
            if n_gaps < MIN_STRATUM_SIZE:
                logger.debug(f"Stratum {i} has only {n_gaps} gaps, skipping")
                continue
            
            # Compute statistics of actual gaps
            mean_gap = float(np.mean(stratum_gaps))
            std_gap = float(np.std(stratum_gaps, ddof=1))
            
            # Test lognormality: log(gaps) should be normal
            log_gaps = np.log(stratum_gaps)
            mu_ln = float(np.mean(log_gaps))
            sigma_ln = float(np.std(log_gaps, ddof=1))
            
            if sigma_ln < 1e-10:
                logger.debug(f"Stratum {i} has zero variance, skipping")
                continue
            
            # KS test: are log_gaps normally distributed?
            ks_stat, ks_p = stats.kstest(log_gaps, 'norm', args=(mu_ln, sigma_ln))
            pass_ks = (ks_stat < KS_STAT_THRESHOLD) or (ks_p > KS_P_THRESHOLD)
            
            strata_results.append(StratumResult(
                range_id=range_id,
                stratum_id=i,
                gap_min=float(lower),
                gap_max=float(upper),
                n_gaps=n_gaps,
                mean_gap=mean_gap,
                std_gap=std_gap,
                mu_lognormal=mu_ln,
                sigma_lognormal=sigma_ln,
                ks_stat=float(ks_stat),
                ks_p=float(ks_p),
                pass_ks=bool(pass_ks)
            ))
            
            # For scaling law: use actual gap statistics
            if mean_gap > 0 and std_gap > 0:
                stratum_means.append(mean_gap)
                stratum_stds.append(std_gap)
        
        if len(stratum_means) < 3:
            logger.warning(f"Not enough valid strata ({len(stratum_means)}) for scaling analysis")
            return None
        
        # Estimate Hurst exponent: log(σ) ~ H * log(μ)
        log_means = np.log(stratum_means)
        log_stds = np.log(stratum_stds)
        
        # Bootstrap for confidence intervals
        h_estimates = []
        for _ in range(BOOTSTRAP_ITERS):
            indices = self.rng.choice(len(stratum_means), size=len(stratum_means), replace=True)
            if len(np.unique(indices)) < 3:
                continue
            
            X_boot = log_means[indices].reshape(-1, 1)
            y_boot = log_stds[indices]
            
            try:
                reg = LinearRegression().fit(X_boot, y_boot)
                h_estimates.append(reg.coef_[0])
            except:
                continue
        
        if len(h_estimates) < 100:
            logger.warning(f"Bootstrap failed to produce enough estimates")
            return None
        
        h_estimates = np.array(h_estimates)
        h_est = float(np.median(h_estimates))
        h_lower = float(np.percentile(h_estimates, 2.5))
        h_upper = float(np.percentile(h_estimates, 97.5))
        
        # Main regression for R²
        reg_main = LinearRegression().fit(log_means.reshape(-1, 1), log_stds)
        r2 = float(reg_main.score(log_means.reshape(-1, 1), log_stds))
        
        pct_pass = 100.0 * sum(s.pass_ks for s in strata_results) / len(strata_results)
        
        return RangeResult(
            range_id=range_id,
            n_gaps=len(valid_gaps),
            h_estimate=h_est,
            h_95ci_lower=h_lower,
            h_95ci_upper=h_upper,
            r_squared=r2,
            n_strata_used=len(strata_results),
            pct_strata_pass_ks=pct_pass,
            strata_results=strata_results
        )
    
    def generate_null_model(self, model_type: str, target_gaps: np.ndarray, n_samples: int = None) -> np.ndarray:
        """Generate synthetic gaps from null models.
        
        Args:
            model_type: 'cramer' (independent) or 'cascade' (multiplicative)
            target_gaps: Real gaps to match statistics
            n_samples: Number of synthetic gaps (default: len(target_gaps))
        """
        if n_samples is None:
            n_samples = len(target_gaps)
        
        if model_type == 'cramer':
            # Cramér model: independent samples from empirical distribution
            return self.rng.choice(target_gaps, size=n_samples, replace=True)
        
        elif model_type == 'cascade':
            # Multiplicative cascade model
            return self._generate_cascade(target_gaps, n_samples)
        
        else:
            raise ValueError(f"Unknown null model: {model_type}")
    
    def _generate_cascade(self, target_gaps: np.ndarray, n_samples: int) -> np.ndarray:
        """Generate gaps using multiplicative cascade."""
        # Match target log-gap statistics
        log_target = np.log(target_gaps[target_gaps > 0])
        target_mu = np.mean(log_target)
        target_sigma = np.std(log_target, ddof=1)
        
        # Determine cascade depth
        k = int(np.ceil(np.log2(n_samples)))
        size = 2**k
        
        # At each level, multiply by lognormal weights
        # Want final log-gap ~ N(target_mu, target_sigma^2)
        # After k steps: log(gap) = sum of k log(weights)
        # Need: k * mu_w = target_mu, k * sigma_w^2 = target_sigma^2
        mu_w = target_mu / k
        sigma_w = target_sigma / np.sqrt(k)
        
        # Build cascade
        measure = np.ones(1)
        for _ in range(k):
            # Split each bin into 2
            measure = np.repeat(measure, 2)
            # Multiply by lognormal weights (correctly parameterized)
            log_weights = self.rng.normal(mu_w, sigma_w, size=len(measure))
            weights = np.exp(log_weights)
            measure = measure * weights
        
        # Take first n_samples
        return measure[:n_samples]


class ExperimentRunner:
    """Orchestrates the full experiment."""
    
    def __init__(self, output_dir: str, seed: int = SEED):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.seed = seed
        self.prime_gen = PrimeGenerator()
        self.analyzer = FractalAnalyzer(seed)
    
    def run(self, ranges: List[str], n_strata: int = 10, null_models: List[str] = None):
        """Run experiment on specified prime ranges."""
        if null_models is None:
            null_models = ['cramer', 'cascade']
        
        all_results = []
        null_results = []
        
        for range_str in ranges:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing range: {range_str}")
            logger.info(f"{'='*60}")
            
            try:
                parts = range_str.split(':')
                start = int(float(parts[0]))
                end = int(float(parts[1]))
            except (ValueError, IndexError) as e:
                logger.error(f"Invalid range format '{range_str}': {e}")
                continue
            
            # Generate primes and compute gaps
            logger.info("Generating primes...")
            primes = self.prime_gen.generate_range(start, end)
            if len(primes) < 2:
                logger.warning(f"Not enough primes in range {range_str}")
                continue
            
            gaps = np.diff(primes)
            logger.info(f"Got {len(primes)} primes, {len(gaps)} gaps")
            
            # Analyze real data
            logger.info("Analyzing real gaps...")
            result = self.analyzer.analyze_range(range_str, gaps, n_strata)
            
            if result is None:
                logger.warning(f"Analysis failed for range {range_str}")
                continue
            
            all_results.append(result)
            logger.info(f"H = {result.h_estimate:.3f} [{result.h_95ci_lower:.3f}, {result.h_95ci_upper:.3f}]")
            logger.info(f"R² = {result.r_squared:.3f}")
            logger.info(f"KS pass rate = {result.pct_strata_pass_ks:.1f}%")
            
            # Plot results
            self._plot_range_results(result)
            
            # Null models
            for model_type in null_models:
                logger.info(f"\nRunning null model: {model_type}")
                syn_gaps = self.analyzer.generate_null_model(model_type, gaps)
                
                null_result = self.analyzer.analyze_range(f"{range_str}_{model_type}", syn_gaps, n_strata)
                
                if null_result:
                    delta_h = null_result.h_estimate - result.h_estimate
                    null_results.append(NullModelResult(
                        model_type=model_type,
                        range_id=range_str,
                        h_estimate=null_result.h_estimate,
                        r_squared=null_result.r_squared,
                        pct_strata_pass_ks=null_result.pct_strata_pass_ks,
                        delta_h=delta_h
                    ))
                    logger.info(f"  H = {null_result.h_estimate:.3f}, ΔH = {delta_h:+.3f}")
                    logger.info(f"  KS pass = {null_result.pct_strata_pass_ks:.1f}%")
        
        # Save and report
        self._save_results(all_results, null_results)
        self._generate_report(all_results, null_results)
        
        logger.info(f"\nResults saved to {self.output_dir}")
    
    def _plot_range_results(self, result: RangeResult):
        """Generate plots for a range analysis."""
        # Extract data for plotting
        means = np.array([s.mean_gap for s in result.strata_results])
        stds = np.array([s.std_gap for s in result.strata_results])
        
        valid = (means > 0) & (stds > 0)
        means = means[valid]
        stds = stds[valid]
        
        if len(means) < 2:
            return
        
        log_means = np.log(means)
        log_stds = np.log(stds)
        
        # Variance scaling plot
        plt.figure(figsize=(10, 6))
        plt.scatter(log_means, log_stds, s=50, alpha=0.7, label='Observed strata')
        
        # Fit line
        reg = LinearRegression().fit(log_means.reshape(-1, 1), log_stds)
        x_line = np.array([log_means.min(), log_means.max()])
        y_line = reg.predict(x_line.reshape(-1, 1))
        plt.plot(x_line, y_line, 'r--', linewidth=2,
                label=f'Fit: H = {result.h_estimate:.3f} (R² = {result.r_squared:.3f})')
        
        plt.xlabel('log(Mean gap)')
        plt.ylabel('log(Std gap)')
        plt.title(f'Variance Scaling Law: {result.range_id}')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        filename = f"scaling_{result.range_id.replace(':', '_')}.png"
        plt.savefig(self.output_dir / filename, dpi=150)
        plt.close()
        logger.info(f"Saved plot: {filename}")
    
    def _save_results(self, results: List[RangeResult], null_results: List[NullModelResult]):
        """Save results to JSON."""
        data = {
            'observed': [asdict(r) for r in results],
            'null_models': [asdict(r) for r in null_results]
        }
        
        output_file = self.output_dir / 'results.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved results: {output_file}")
    
    def _generate_report(self, results: List[RangeResult], null_results: List[NullModelResult]):
        """Generate markdown report."""
        lines = []
        lines.append("# Fractal Cascade Structure Falsification Test\n")
        lines.append(f"Date: {pd.Timestamp.now()}\n")
        
        # Summary
        lines.append("## Summary\n")
        lines.append(f"Analyzed {len(results)} prime ranges\n")
        
        # Falsification criteria
        lines.append("## Falsification Criteria\n")
        lines.append("The hypothesis is FALSIFIED if:\n")
        lines.append("1. H not in [0.6, 1.0] OR highly variable across ranges\n")
        lines.append("2. Within-stratum KS pass rate < 80%\n")
        lines.append("3. Null models (Cramér) successfully replicate structure\n")
        
        # Check criteria
        h_in_range = all(0.6 <= r.h_estimate <= 1.0 for r in results)
        ks_pass = all(r.pct_strata_pass_ks >= 80.0 for r in results)
        
        # Null model check
        null_fail = True
        for nr in null_results:
            if nr.model_type == 'cramer':
                # Cramér should fail to replicate: low KS or wrong H
                if nr.pct_strata_pass_ks >= 70.0 and abs(nr.delta_h) < 0.15:
                    null_fail = False
                    break
        
        falsified = not (h_in_range and ks_pass and null_fail)
        
        lines.append("\n## Verdict\n")
        if falsified:
            lines.append("**FALSIFIED**\n")
            if not h_in_range:
                lines.append("- Hurst exponent outside valid range or inconsistent\n")
            if not ks_pass:
                lines.append("- Within-stratum lognormality not supported (<80% pass)\n")
            if not null_fail:
                lines.append("- Null models successfully replicated the structure\n")
        else:
            lines.append("**NOT FALSIFIED**\n")
            lines.append("Data consistent with fractal cascade hypothesis.\n")
        
        # Detailed results
        lines.append("\n## Observed Results\n")
        for r in results:
            lines.append(f"\n### Range {r.range_id}\n")
            lines.append(f"- N gaps: {r.n_gaps}\n")
            lines.append(f"- H estimate: {r.h_estimate:.3f} [{r.h_95ci_lower:.3f}, {r.h_95ci_upper:.3f}]\n")
            lines.append(f"- R²: {r.r_squared:.3f}\n")
            lines.append(f"- Strata used: {r.n_strata_used}\n")
            lines.append(f"- KS pass rate: {r.pct_strata_pass_ks:.1f}%\n")
        
        lines.append("\n## Null Model Comparison\n")
        for nr in null_results:
            lines.append(f"- {nr.model_type} ({nr.range_id}): H={nr.h_estimate:.3f} (ΔH={nr.delta_h:+.3f}), KS={nr.pct_strata_pass_ks:.1f}%\n")
        
        report_file = self.output_dir / 'report.md'
        with open(report_file, 'w') as f:
            f.writelines(lines)
        logger.info(f"Saved report: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Falsification test for fractal cascade structure in prime gaps'
    )
    parser.add_argument(
        '--ranges',
        default='1e6:1e7',
        help='Comma-separated prime ranges (e.g., "1e6:1e7,1e9:1e10")'
    )
    parser.add_argument(
        '--output',
        default='results',
        help='Output directory for results'
    )
    parser.add_argument(
        '--strata',
        type=int,
        default=10,
        help='Number of magnitude strata'
    )
    parser.add_argument(
        '--null-models',
        default='cramer,cascade',
        help='Comma-separated null models to test'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=SEED,
        help='Random seed'
    )
    
    args = parser.parse_args()
    
    # Parse arguments
    ranges = [r.strip() for r in args.ranges.split(',')]
    null_models = [m.strip() for m in args.null_models.split(',')]
    
    # Run experiment
    runner = ExperimentRunner(args.output, args.seed)
    runner.run(ranges, args.strata, null_models)


if __name__ == '__main__':
    main()
