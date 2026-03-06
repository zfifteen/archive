#!/usr/bin/env python3
"""
Linear Scaling Hypothesis Validation for Prime-Driven Sieve in Compression Contexts

This script implements comprehensive validation of the linear scaling hypothesis
for the prime-driven compression algorithm as specified in Issue #195.

MATHEMATICAL FOUNDATION:
- Universal Z form: Z = A(B/c) with normalization to invariant c = e²
- Discrete domain: Z = n(Δₙ / Δₘₐₓ) where Δₙ = κ(n) = d(n)·ln(n+1)/e²
- Golden ratio modular mapping: θ'(n,k) = φ·{n/φ}^k with k*=0.200
- Expected 495.2% prime density enhancement at optimal k*

SCALING HYPOTHESIS:
- Algorithm components should demonstrate O(n) time complexity
- O(n) transformations, O(n) histogram binning, constant GMM fitting
- Linear regression validation with R² ≥ 0.998 required

BENCHMARK METHODOLOGY:
- Test sizes: 100KB, 1MB, 10MB  
- Data types: structured text (repetitive), binary (random incompressible)
- Algorithms: prime-driven, gzip, bzip2, LZMA
- Statistical analysis: least squares fitting t = a·n + b

Author: DAL
License: MIT
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import time
import gzip
import bz2
import lzma
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings("ignore")

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from applications.prime_compression_fixed import (
        PrimeDrivenCompressor, 
        CompressionBenchmark,
        PrimeGeodesicTransform,
        K_OPTIMAL, PHI
    )
    PRIME_COMPRESSION_AVAILABLE = True
except ImportError as e:
    try:
        from applications.prime_compression import (
            PrimeDrivenCompressor, 
            CompressionBenchmark,
            PrimeGeodesicTransform,
            K_OPTIMAL, PHI
        )
        PRIME_COMPRESSION_AVAILABLE = True
    except ImportError as e2:
        print(f"Warning: Prime compression not available: {e2}")
        PRIME_COMPRESSION_AVAILABLE = False


@dataclass
class ScalingResult:
    """Results from linear scaling analysis."""
    algorithm: str
    data_type: str
    sizes: List[int]
    times: List[float]
    ratios: List[float]
    linear_coeff: float
    intercept: float
    r_squared: float
    time_per_byte: List[float]
    passes_validation: bool


class DataGenerator:
    """Generate test datasets for scaling validation."""
    
    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducibility."""
        np.random.seed(seed)
        
    def generate_structured_text(self, size_bytes: int) -> bytes:
        """
        Generate structured text with repetitive patterns for compressibility.
        
        Args:
            size_bytes: Target size in bytes
            
        Returns:
            Structured text data as bytes
        """
        # Create base pattern that tiles well
        base_pattern = (
            "The Z Framework leverages the universal form Z = A(B/c) where c bounds all measurable rates. "
            "Prime density enhancement of 495.2% is achieved at optimal curvature k*=0.200 through "
            "golden ratio modular transformation θ'(n,k) = φ·{n/φ}^k. "
            "This demonstrates linear scaling O(n) with discrete domain normalization to e². "
        )
        
        # Calculate repetitions needed
        pattern_size = len(base_pattern.encode('utf-8'))
        repetitions = (size_bytes // pattern_size) + 1
        
        # Generate data and trim to exact size
        data = (base_pattern * repetitions).encode('utf-8')
        return data[:size_bytes]
    
    def generate_binary_data(self, size_bytes: int) -> bytes:
        """
        Generate random binary data (incompressible).
        
        Args:
            size_bytes: Target size in bytes
            
        Returns:
            Random binary data
        """
        return np.random.randint(0, 256, size_bytes, dtype=np.uint8).tobytes()


class CompressionTimer:
    """Time compression operations with high precision."""
    
    @staticmethod
    def time_compression(algorithm: str, data: bytes) -> Tuple[float, float, int]:
        """
        Time compression operation and measure results.
        
        Args:
            algorithm: Algorithm name ('gzip', 'bzip2', 'lzma', 'prime_driven')
            data: Input data to compress
            
        Returns:
            (compression_time, compression_ratio, compressed_size)
        """
        original_size = len(data)
        
        start_time = time.perf_counter()
        
        if algorithm == 'gzip':
            compressed = gzip.compress(data)
            
        elif algorithm == 'bzip2':
            compressed = bz2.compress(data)
            
        elif algorithm == 'lzma':
            compressed = lzma.compress(data)
            
        elif algorithm == 'prime_driven':
            if not PRIME_COMPRESSION_AVAILABLE:
                return 0.0, 0.0, original_size
            
            compressor = PrimeDrivenCompressor()
            compressed_data, metrics = compressor.compress(data)
            compressed_size = metrics.compressed_size
            compression_time = time.perf_counter() - start_time
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 0.0
            return compression_time, compression_ratio, compressed_size
            
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        compression_time = time.perf_counter() - start_time
        compressed_size = len(compressed)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0.0
        
        return compression_time, compression_ratio, compressed_size


class LinearScalingValidator:
    """Validate linear scaling hypothesis with statistical analysis."""
    
    def __init__(self):
        """Initialize validator."""
        self.data_generator = DataGenerator()
        self.timer = CompressionTimer()
        
    def run_scaling_test(
        self, 
        algorithm: str, 
        data_type: str, 
        test_sizes: List[int],
        num_trials: int = 3
    ) -> ScalingResult:
        """
        Run scaling test for a specific algorithm and data type.
        
        Args:
            algorithm: Compression algorithm to test
            data_type: 'structured' or 'binary'
            test_sizes: List of data sizes to test
            num_trials: Number of trials to average
            
        Returns:
            ScalingResult with analysis
        """
        print(f"Testing {algorithm} on {data_type} data...")
        
        avg_times = []
        avg_ratios = []
        
        for size in test_sizes:
            print(f"  Size: {size:,} bytes...", end=' ')
            
            trial_times = []
            trial_ratios = []
            
            for trial in range(num_trials):
                # Generate fresh data for each trial
                if data_type == 'structured':
                    data = self.data_generator.generate_structured_text(size)
                else:  # binary
                    data = self.data_generator.generate_binary_data(size)
                
                compression_time, compression_ratio, _ = self.timer.time_compression(algorithm, data)
                
                trial_times.append(compression_time)
                trial_ratios.append(compression_ratio)
            
            # Average across trials
            avg_time = np.mean(trial_times)
            avg_ratio = np.mean(trial_ratios)
            
            avg_times.append(avg_time)
            avg_ratios.append(avg_ratio)
            
            print(f"avg_time={avg_time:.4f}s, ratio={avg_ratio:.2f}x")
        
        # Perform linear regression analysis
        sizes_array = np.array(test_sizes).reshape(-1, 1)
        times_array = np.array(avg_times)
        
        # Fit linear model: t = a*n + b
        reg = LinearRegression()
        reg.fit(sizes_array, times_array)
        
        linear_coeff = reg.coef_[0]
        intercept = reg.intercept_
        r_squared = r2_score(times_array, reg.predict(sizes_array))
        
        # Calculate time per byte
        time_per_byte = [t/s for t, s in zip(avg_times, test_sizes)]
        
        # Validation: R² ≥ 0.998 for linear scaling
        passes_validation = r_squared >= 0.998
        
        return ScalingResult(
            algorithm=algorithm,
            data_type=data_type,
            sizes=test_sizes,
            times=avg_times,
            ratios=avg_ratios,
            linear_coeff=linear_coeff,
            intercept=intercept,
            r_squared=r_squared,
            time_per_byte=time_per_byte,
            passes_validation=passes_validation
        )
    
    def generate_scaling_report(self, results: List[ScalingResult]) -> str:
        """
        Generate comprehensive scaling analysis report.
        
        Args:
            results: List of ScalingResult objects
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("="*80)
        report.append("LINEAR SCALING HYPOTHESIS VALIDATION REPORT")
        report.append("="*80)
        report.append("")
        
        # Mathematical foundation
        report.append("MATHEMATICAL FOUNDATION:")
        report.append(f"- Universal Z form: Z = A(B/c) with c = e² normalization")
        report.append(f"- Golden ratio φ = {float(PHI):.10f}")
        report.append(f"- Optimal curvature k* = {float(K_OPTIMAL):.3f}")
        report.append(f"- Transformation: θ'(n,k) = φ * {n/φ}^k")
        report.append(f"- Expected prime density enhancement: 495.2%")
        report.append("")
        
        # Validation criteria
        report.append("VALIDATION CRITERIA:")
        report.append("- Linear scaling hypothesis: O(n) time complexity")
        report.append("- Statistical requirement: R² ≥ 0.998")
        report.append("- Test data sizes: 100KB, 1MB, 10MB")
        report.append("- Data types: structured (repetitive), binary (incompressible)")
        report.append("")
        
        # Results summary
        report.append("RESULTS SUMMARY:")
        report.append("")
        
        # Group results by data type
        structured_results = [r for r in results if r.data_type == 'structured']
        binary_results = [r for r in results if r.data_type == 'binary']
        
        for data_type, type_results in [('Structured Text', structured_results), 
                                       ('Binary Data', binary_results)]:
            if not type_results:
                continue
                
            report.append(f"{data_type}:")
            report.append("-" * 50)
            report.append(f"{'Algorithm':<15} | {'Linear Coeff':<12} | {'R²':<8} | {'Validation'}")
            report.append("-" * 50)
            
            for result in type_results:
                validation_status = "PASS" if result.passes_validation else "FAIL"
                report.append(f"{result.algorithm:<15} | {result.linear_coeff:<12.2e} | "
                            f"{result.r_squared:<8.6f} | {validation_status}")
            
            report.append("")
        
        # Detailed analysis
        report.append("DETAILED ANALYSIS:")
        report.append("")
        
        for result in results:
            report.append(f"{result.algorithm.upper()} - {result.data_type.title()}:")
            report.append(f"  Linear Model: t = {result.linear_coeff:.2e} * n + {result.intercept:.6f}")
            report.append(f"  R² Score: {result.r_squared:.6f}")
            report.append(f"  Validation: {'PASS' if result.passes_validation else 'FAIL'}")
            
            # Time per byte analysis
            min_tpb = min(result.time_per_byte)
            max_tpb = max(result.time_per_byte)
            avg_tpb = np.mean(result.time_per_byte)
            
            report.append(f"  Time/byte: min={min_tpb:.2e}, max={max_tpb:.2e}, avg={avg_tpb:.2e}")
            
            # Size-specific timings
            report.append("  Size-specific results:")
            for size, time_val, ratio in zip(result.sizes, result.times, result.ratios):
                size_str = f"{size//1000}KB" if size < 1000000 else f"{size//1000000}MB"
                report.append(f"    {size_str:>6}: {time_val:.4f}s, ratio={ratio:.2f}x")
            
            report.append("")
        
        # Conclusion
        all_pass = all(r.passes_validation for r in results)
        report.append("CONCLUSION:")
        report.append(f"- Overall validation: {'PASS' if all_pass else 'FAIL'}")
        report.append(f"- Algorithms tested: {len(set(r.algorithm for r in results))}")
        report.append(f"- All show linear scaling: {'Yes' if all_pass else 'No'}")
        
        if PRIME_COMPRESSION_AVAILABLE:
            prime_results = [r for r in results if r.algorithm == 'prime_driven']
            if prime_results:
                avg_r2 = np.mean([r.r_squared for r in prime_results])
                report.append(f"- Prime-driven avg R²: {avg_r2:.6f}")
        
        report.append("")
        report.append("Linear scaling hypothesis validation complete.")
        report.append("="*80)
        
        return "\n".join(report)
    
    def create_scaling_plots(self, results: List[ScalingResult], output_dir: str = "."):
        """
        Create visualization plots for scaling analysis.
        
        Args:
            results: List of ScalingResult objects
            output_dir: Directory to save plots
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Plot 1: Time vs Size (linear scaling)
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Linear Scaling Hypothesis Validation', fontsize=16)
        
        # Structured data - Time vs Size
        ax = axes[0, 0]
        structured_results = [r for r in results if r.data_type == 'structured']
        for result in structured_results:
            ax.plot(result.sizes, result.times, 'o-', label=f'{result.algorithm} (R²={result.r_squared:.4f})')
        ax.set_xlabel('Data Size (bytes)')
        ax.set_ylabel('Compression Time (seconds)')
        ax.set_title('Structured Text: Time vs Size')
        ax.legend()
        ax.grid(True)
        
        # Binary data - Time vs Size  
        ax = axes[0, 1]
        binary_results = [r for r in results if r.data_type == 'binary']
        for result in binary_results:
            ax.plot(result.sizes, result.times, 'o-', label=f'{result.algorithm} (R²={result.r_squared:.4f})')
        ax.set_xlabel('Data Size (bytes)')
        ax.set_ylabel('Compression Time (seconds)')
        ax.set_title('Binary Data: Time vs Size')
        ax.legend()
        ax.grid(True)
        
        # Structured data - Time per Byte
        ax = axes[1, 0]
        for result in structured_results:
            ax.plot(result.sizes, result.time_per_byte, 'o-', label=result.algorithm)
        ax.set_xlabel('Data Size (bytes)')
        ax.set_ylabel('Time per Byte (s/byte)')
        ax.set_title('Structured Text: Time per Byte')
        ax.legend()
        ax.grid(True)
        ax.set_yscale('log')
        
        # Binary data - Time per Byte
        ax = axes[1, 1]
        for result in binary_results:
            ax.plot(result.sizes, result.time_per_byte, 'o-', label=result.algorithm)
        ax.set_xlabel('Data Size (bytes)')
        ax.set_ylabel('Time per Byte (s/byte)')
        ax.set_title('Binary Data: Time per Byte')
        ax.legend()
        ax.grid(True)
        ax.set_yscale('log')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'linear_scaling_validation.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: R² validation summary
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        algorithms = list(set(r.algorithm for r in results))
        structured_r2 = []
        binary_r2 = []
        
        for algo in algorithms:
            struct_result = next((r for r in results if r.algorithm == algo and r.data_type == 'structured'), None)
            binary_result = next((r for r in results if r.algorithm == algo and r.data_type == 'binary'), None)
            
            structured_r2.append(struct_result.r_squared if struct_result else 0)
            binary_r2.append(binary_result.r_squared if binary_result else 0)
        
        x = np.arange(len(algorithms))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, structured_r2, width, label='Structured Text', alpha=0.8)
        bars2 = ax.bar(x + width/2, binary_r2, width, label='Binary Data', alpha=0.8)
        
        # Add validation line
        ax.axhline(y=0.998, color='red', linestyle='--', linewidth=2, label='Validation Threshold (R²=0.998)')
        
        ax.set_xlabel('Compression Algorithm')
        ax.set_ylabel('R² Score')
        ax.set_title('Linear Scaling Validation: R² Scores by Algorithm')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0.99, 1.001)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.0001,
                       f'{height:.4f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'r_squared_validation.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Plots saved to {output_dir}/")


def main():
    """Run comprehensive linear scaling validation."""
    print("Linear Scaling Hypothesis Validation for Prime-Driven Sieve")
    print("=" * 60)
    print()
    
    # Initialize validator
    validator = LinearScalingValidator()
    
    # Define test parameters as per issue requirements
    test_sizes = [
        100_000,    # 100KB
        1_000_000,  # 1MB  
        10_000_000  # 10MB
    ]
    
    algorithms = ['gzip', 'bzip2', 'lzma']
    if PRIME_COMPRESSION_AVAILABLE:
        algorithms.append('prime_driven')
    
    data_types = ['structured', 'binary']
    
    # Run comprehensive testing
    all_results = []
    
    for algorithm in algorithms:
        for data_type in data_types:
            try:
                result = validator.run_scaling_test(algorithm, data_type, test_sizes)
                all_results.append(result)
            except Exception as e:
                print(f"Error testing {algorithm} on {data_type}: {e}")
                continue
    
    # Generate analysis
    report = validator.generate_scaling_report(all_results)
    
    # Save report
    with open('linear_scaling_validation_report.txt', 'w') as f:
        f.write(report)
    
    # Create visualizations
    validator.create_scaling_plots(all_results)
    
    # Print report
    print(report)
    
    # Summary validation
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r.passes_validation)
    
    print(f"\nVALIDATION SUMMARY:")
    print(f"Total tests: {total_tests}")
    print(f"Passed tests: {passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("✓ LINEAR SCALING HYPOTHESIS VALIDATED")
    else:
        print("✗ Linear scaling hypothesis validation failed")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)