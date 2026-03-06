#!/usr/bin/env python3
"""
Inverse Mersenne Probe RSA Benchmark Harness
=============================================

Benchmark harness for testing Z5D-guided inverse Mersenne probe on RSA Challenge numbers.
Implements bootstrap confidence intervals and comprehensive statistical analysis.

@file scripts/benchmark_inverse_probe_rsa.py
@author Unified Framework Team
@version 1.0
"""

import argparse
import json
import subprocess
import csv
import time
import os
import sys
from pathlib import Path
import numpy as np
from typing import List, Dict, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProbeResult:
    """Container for probe execution results"""
    def __init__(self, json_result: dict, rsa_name: str, window_trials: int):
        self.rsa_name = rsa_name
        self.window_trials = window_trials
        self.n_bits = json_result.get('n_bits', 0)
        self.time_ms = json_result.get('time_ms', 0.0)
        self.found = json_result.get('found', False)
        self.factor_bits = json_result.get('factor_bits', 0)
        self.z5d_preds = json_result.get('z5d_preds', 0)
        self.mr_tests = json_result.get('mr_tests', 0)
        self.factor = json_result.get('factor', None)

class RSABenchmarkHarness:
    """Main benchmark harness for RSA challenge factorization"""
    
    def __init__(self, rsa_data_path: str, probe_executable: str):
        self.rsa_data_path = rsa_data_path
        self.probe_executable = probe_executable
        self.results: List[ProbeResult] = []
        
        # Load RSA challenge data
        with open(rsa_data_path, 'r') as f:
            self.rsa_data = json.load(f)
        
        logger.info(f"Loaded {len(self.rsa_data)} RSA challenge numbers")
    
    def run_probe(self, rsa_number: str, window_trials: int, kappa_geo: float, timeout_ms: int = 600000) -> Dict[str, Any]:
        """Run the C probe executable and return JSON result"""
        cmd = [
            self.probe_executable,
            rsa_number,
            str(window_trials),
            str(kappa_geo)
        ]
        
        try:
            # Run with timeout
            timeout_sec = timeout_ms / 1000.0
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout_sec
            )
            
            if result.returncode != 0:
                logger.error(f"Probe failed: {result.stderr}")
                return {
                    "n_bits": 0,
                    "window_trials": window_trials,
                    "time_ms": timeout_ms,
                    "found": False,
                    "factor_bits": 0,
                    "z5d_preds": 0,
                    "mr_tests": 0,
                    "error": "Process failed"
                }
            
            # Parse JSON output
            return json.loads(result.stdout.strip())
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Probe timed out after {timeout_sec}s")
            return {
                "n_bits": 0,
                "window_trials": window_trials,
                "time_ms": timeout_ms,
                "found": False,
                "factor_bits": 0,
                "z5d_preds": 0,
                "mr_tests": 0,
                "error": "Timeout"
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, output: {result.stdout}")
            return {
                "n_bits": 0,
                "window_trials": window_trials,
                "time_ms": timeout_ms,
                "found": False,
                "factor_bits": 0,
                "z5d_preds": 0,
                "mr_tests": 0,
                "error": "JSON decode error"
            }
    
    def run_benchmark_sweep(self, windows: List[int], kappa_geo: float, reps: int, timeout_ms: int):
        """Run benchmark sweep across RSA numbers and window sizes"""
        total_runs = len(self.rsa_data) * len(windows) * reps
        current_run = 0
        
        logger.info(f"Starting benchmark sweep: {total_runs} total runs")
        
        for rsa_entry in self.rsa_data:
            rsa_name = rsa_entry['name']
            rsa_number = rsa_entry['n']
            
            logger.info(f"Testing {rsa_name} ({len(rsa_number)} digits)")
            
            for window_trials in windows:
                logger.info(f"  Window size: {window_trials}")
                
                for rep in range(reps):
                    current_run += 1
                    logger.info(f"    Rep {rep+1}/{reps} (Run {current_run}/{total_runs})")
                    
                    # Run probe
                    json_result = self.run_probe(rsa_number, window_trials, kappa_geo, timeout_ms)
                    
                    # Store result
                    probe_result = ProbeResult(json_result, rsa_name, window_trials)
                    self.results.append(probe_result)
                    
                    # Log result
                    if probe_result.found:
                        logger.info(f"      SUCCESS: Found factor in {probe_result.time_ms:.1f}ms")
                    else:
                        logger.info(f"      No factor found in {probe_result.time_ms:.1f}ms ({probe_result.z5d_preds} Z5D preds)")
    
    def bootstrap_confidence_intervals(self, data: List[float], n_bootstrap: int = 1000, confidence: float = 0.95) -> Tuple[float, float, float]:
        """Calculate bootstrap confidence intervals"""
        if len(data) == 0:
            return 0.0, 0.0, 0.0
        
        # Bootstrap resampling
        bootstrap_means = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means.append(np.mean(sample))
        
        # Calculate confidence interval
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        mean_estimate = np.mean(data)
        ci_lower = np.percentile(bootstrap_means, lower_percentile)
        ci_upper = np.percentile(bootstrap_means, upper_percentile)
        
        return mean_estimate, ci_lower, ci_upper
    
    def generate_csv_report(self, output_path: str):
        """Generate CSV report of all results"""
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = [
                'rsa_name', 'window_trials', 'n_bits', 'time_ms', 'found',
                'factor_bits', 'z5d_preds', 'mr_tests', 'factor'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow({
                    'rsa_name': result.rsa_name,
                    'window_trials': result.window_trials,
                    'n_bits': result.n_bits,
                    'time_ms': result.time_ms,
                    'found': result.found,
                    'factor_bits': result.factor_bits,
                    'z5d_preds': result.z5d_preds,
                    'mr_tests': result.mr_tests,
                    'factor': result.factor or ""
                })
        
        logger.info(f"CSV report saved to: {output_path}")
    
    def generate_markdown_report(self, output_path: str, kappa_geo: float, reps: int):
        """Generate comprehensive Markdown report with bootstrap analysis"""
        
        # Group results by RSA number and window size
        grouped_results = {}
        for result in self.results:
            key = (result.rsa_name, result.window_trials)
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(result)
        
        with open(output_path, 'w') as f:
            f.write("# Inverse Mersenne Probe RSA Benchmark Report\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Parameters:**\n")
            f.write(f"- κ_geo: {kappa_geo:.5f}\n")
            f.write(f"- Repetitions per test: {reps}\n")
            f.write(f"- Total results: {len(self.results)}\n\n")
            
            f.write("## Executive Summary\n\n")
            
            # Overall statistics
            total_found = sum(1 for r in self.results if r.found)
            success_rate = (total_found / len(self.results)) * 100 if self.results else 0
            
            f.write(f"- **Success Rate:** {success_rate:.1f}% ({total_found}/{len(self.results)} tests)\n")
            
            if self.results:
                all_times = [r.time_ms for r in self.results]
                all_z5d_preds = [r.z5d_preds for r in self.results]
                
                time_mean, time_ci_low, time_ci_high = self.bootstrap_confidence_intervals(all_times)
                preds_mean, preds_ci_low, preds_ci_high = self.bootstrap_confidence_intervals(all_z5d_preds)
                
                f.write(f"- **Mean Time:** {time_mean:.1f}ms (95% CI: [{time_ci_low:.1f}, {time_ci_high:.1f}])\n")
                f.write(f"- **Mean Z5D Predictions:** {preds_mean:.1f} (95% CI: [{preds_ci_low:.1f}, {preds_ci_high:.1f}])\n\n")
            
            f.write("## Detailed Results by RSA Number\n\n")
            
            # Results by RSA number
            rsa_names = sorted(set(r.rsa_name for r in self.results))
            for rsa_name in rsa_names:
                f.write(f"### {rsa_name}\n\n")
                
                rsa_results = [r for r in self.results if r.rsa_name == rsa_name]
                if rsa_results:
                    f.write(f"**Number of bits:** {rsa_results[0].n_bits}\n\n")
                
                # Group by window size
                windows = sorted(set(r.window_trials for r in rsa_results))
                for window in windows:
                    window_results = [r for r in rsa_results if r.window_trials == window]
                    
                    if window_results:
                        times = [r.time_ms for r in window_results]
                        z5d_preds = [r.z5d_preds for r in window_results]
                        found_count = sum(1 for r in window_results if r.found)
                        
                        time_mean, time_ci_low, time_ci_high = self.bootstrap_confidence_intervals(times)
                        preds_mean, preds_ci_low, preds_ci_high = self.bootstrap_confidence_intervals(z5d_preds)
                        
                        f.write(f"**Window Size {window}:**\n")
                        f.write(f"- Successes: {found_count}/{len(window_results)}\n")
                        f.write(f"- Time: {time_mean:.1f}ms (95% CI: [{time_ci_low:.1f}, {time_ci_high:.1f}])\n")
                        f.write(f"- Z5D Predictions: {preds_mean:.1f} (95% CI: [{preds_ci_low:.1f}, {preds_ci_high:.1f}])\n\n")
            
            f.write("## Statistical Analysis\n\n")
            f.write("**Bootstrap Methodology:** 1000 resamples with replacement for 95% confidence intervals.\n\n")
            f.write("**Success Criteria:**\n")
            f.write("- ≥40% median reduction in search space vs uniform scan\n")
            f.write("- Reproducibility across platforms\n")
            f.write("- Statistical significance with p < 0.05\n\n")
            
            # Efficiency analysis
            if grouped_results:
                f.write("### Search Efficiency Analysis\n\n")
                f.write("| RSA Number | Window Size | Mean Time (ms) | 95% CI Lower | 95% CI Upper | Z5D Predictions | Success Rate |\n")
                f.write("|------------|-------------|----------------|--------------|--------------|-----------------|---------------|\n")
                
                for (rsa_name, window_trials), results in sorted(grouped_results.items()):
                    times = [r.time_ms for r in results]
                    z5d_preds = [r.z5d_preds for r in results]
                    found_count = sum(1 for r in results if r.found)
                    
                    time_mean, time_ci_low, time_ci_high = self.bootstrap_confidence_intervals(times)
                    preds_mean, _, _ = self.bootstrap_confidence_intervals(z5d_preds)
                    success_rate = (found_count / len(results)) * 100 if results else 0
                    
                    f.write(f"| {rsa_name} | {window_trials} | {time_mean:.1f} | {time_ci_low:.1f} | {time_ci_high:.1f} | {preds_mean:.1f} | {success_rate:.1f}% |\n")
            
            f.write("\n**Note:** This is a hypothesis test. Crypto relevance claims require p < 10⁻¹⁰ evidence.\n")
        
        logger.info(f"Markdown report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Benchmark Z5D-guided inverse Mersenne probe on RSA Challenge numbers")
    parser.add_argument('--rsa-data', default='data/rsa_challenge.json', help='Path to RSA challenge dataset')
    parser.add_argument('--probe-exe', default='bin/probe', help='Path to inverse Mersenne probe executable')
    parser.add_argument('--windows', nargs='+', type=int, default=[1024, 4096, 16384], help='Window trial sizes to test')
    parser.add_argument('--kappa-geo', type=float, default=0.30769, help='Z5D geometric density parameter')
    parser.add_argument('--reps', type=int, default=5, help='Number of repetitions per test')
    parser.add_argument('--timeout-ms', type=int, default=600000, help='Timeout per test in milliseconds')
    parser.add_argument('--output-dir', default='benchmarks', help='Output directory for results')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check if probe executable exists
    if not os.path.exists(args.probe_exe):
        logger.error(f"Probe executable not found: {args.probe_exe}")
        logger.info("Please build the probe first with: make probe")
        sys.exit(1)
    
    # Check if RSA data exists
    if not os.path.exists(args.rsa_data):
        logger.error(f"RSA challenge data not found: {args.rsa_data}")
        sys.exit(1)
    
    # Initialize harness
    harness = RSABenchmarkHarness(args.rsa_data, args.probe_exe)
    
    # Run benchmark
    logger.info("Starting RSA Challenge benchmark...")
    start_time = time.time()
    
    harness.run_benchmark_sweep(
        windows=args.windows,
        kappa_geo=args.kappa_geo,
        reps=args.reps,
        timeout_ms=args.timeout_ms
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"Benchmark completed in {total_time:.1f} seconds")
    
    # Generate reports
    csv_path = os.path.join(args.output_dir, 'inverse_probe_rsa_results.csv')
    md_path = os.path.join(args.output_dir, 'inverse_probe_rsa_report.md')
    
    harness.generate_csv_report(csv_path)
    harness.generate_markdown_report(md_path, args.kappa_geo, args.reps)
    
    logger.info("Benchmark complete! Check output files:")
    logger.info(f"  CSV: {csv_path}")
    logger.info(f"  Report: {md_path}")

if __name__ == '__main__':
    main()