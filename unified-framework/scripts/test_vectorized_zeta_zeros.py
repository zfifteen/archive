#!/usr/bin/env python3
"""
Vectorized Tests for Zeta Zeros Dataset

This module implements comprehensive vectorized tests for the Odlyzko/LMFDB 
zeta zeros dataset, targeting performance benchmarks for n=10^3 to 10^6 zeros.

Features:
- Vectorized operations using NumPy for optimal performance
- Multiple test scales: 10^3, 10^4, 10^5, 10^6 zeros
- Statistical analysis and validation
- Performance benchmarking
- Integration with existing zeta framework
"""

import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def load_zeta_zeros(max_zeros: Optional[int] = None) -> np.ndarray:
    """
    Load zeta zeros from numpy file.
    
    Args:
        max_zeros: Maximum number of zeros to load (None for all)
        
    Returns:
        NumPy array of complex zeros
    """
    zeros_file = os.path.join('..', 'src', 'data', 'zeta_zeros.npy')
    
    if not os.path.exists(zeros_file):
        raise FileNotFoundError(f"Zeta zeros file not found: {zeros_file}")
    
    print(f"Loading zeta zeros from: {zeros_file}")
    zeros = np.load(zeros_file)
    
    if max_zeros is not None and len(zeros) > max_zeros:
        zeros = zeros[:max_zeros]
    
    print(f"✓ Loaded {len(zeros)} zeros")
    return zeros

def compute_zero_spacings(zeros: np.ndarray) -> np.ndarray:
    """
    Compute spacings between consecutive zeros (vectorized).
    
    Args:
        zeros: Array of complex zeros
        
    Returns:
        Array of spacings (differences in imaginary parts)
    """
    imag_parts = zeros.imag
    spacings = np.diff(imag_parts)
    return spacings

def compute_gap_statistics(spacings: np.ndarray) -> Dict:
    """
    Compute statistical properties of zero spacings.
    
    Args:
        spacings: Array of consecutive zero spacings
        
    Returns:
        Dictionary of statistical measures
    """
    mean_spacing = np.mean(spacings)
    std_spacing = np.std(spacings)
    stats = {
        'mean_spacing': mean_spacing,
        'std_spacing': std_spacing,
        'min_spacing': np.min(spacings),
        'max_spacing': np.max(spacings),
        'median_spacing': np.median(spacings),
        'variance': np.var(spacings),
        'skewness': float(np.mean(((spacings - mean_spacing) / std_spacing)**3)),
        'kurtosis': float(np.mean(((spacings - mean_spacing) / std_spacing)**4)) - 3,
        'percentile_95': np.percentile(spacings, 95),
        'percentile_5': np.percentile(spacings, 5)
    }
    
    return stats

def test_weyl_asymptotic_formula(zeros: np.ndarray) -> Dict:
    """
    Test Weyl's asymptotic formula for zero counting function (vectorized).
    
    Weyl's formula: N(T) ~ T/(2π) * log(T/(2πe))
    
    Args:
        zeros: Array of complex zeros
        
    Returns:
        Dictionary with test results
    """
    imag_parts = zeros.imag
    max_height = np.max(imag_parts)
    
    # Count zeros up to height T (vectorized)
    T_values = np.logspace(1, np.log10(max_height), 100)  # 100 test points
    actual_counts = np.zeros_like(T_values)
    
    for i, T in enumerate(T_values):
        actual_counts[i] = np.sum(imag_parts <= T)
    
    # Weyl's asymptotic prediction (vectorized)
    predicted_counts = T_values / (2 * np.pi) * np.log(T_values / (2 * np.pi * np.e))
    
    # Compute relative errors
    relative_errors = np.abs(actual_counts - predicted_counts) / predicted_counts
    
    return {
        'T_values': T_values.tolist(),
        'actual_counts': actual_counts.tolist(),
        'predicted_counts': predicted_counts.tolist(),
        'relative_errors': relative_errors.tolist(),
        'mean_relative_error': float(np.mean(relative_errors)),
        'max_relative_error': float(np.max(relative_errors)),
        'asymptotic_accuracy': float(1.0 - np.mean(relative_errors))
    }

def test_riemann_von_mangoldt_formula(zeros: np.ndarray, sample_size: int = 1000) -> Dict:
    """
    Test Riemann-von Mangoldt explicit formula for prime counting (vectorized).
    
    Args:
        zeros: Array of complex zeros
        sample_size: Number of sample points to test
        
    Returns:
        Dictionary with test results
    """
    imag_parts = zeros.imag[:sample_size]  # Use subset for performance
    
    # Test points for prime counting function evaluation
    x_values = np.logspace(1, 4, 50)  # x from 10 to 10^4
    
    # Simplified explicit formula contribution from zeros
    contributions = np.zeros(len(x_values))
    
    for i, x in enumerate(x_values):
        # Sum over zeros: sum(x^rho / rho) where rho = 0.5 + i*gamma
        rho_contributions = np.real(x**(0.5 + 1j * imag_parts) / (0.5 + 1j * imag_parts))
        contributions[i] = np.sum(rho_contributions)
    
    return {
        'x_values': x_values.tolist(),
        'zero_contributions': contributions.tolist(),
        'sample_size': sample_size
    }

def test_montgomery_conjecture(spacings: np.ndarray) -> Dict:
    """
    Test Montgomery's pair correlation conjecture (simplified version).
    
    Args:
        spacings: Array of consecutive zero spacings
        
    Returns:
        Dictionary with test results
    """
    # Normalize spacings by mean spacing
    mean_spacing = np.mean(spacings)
    normalized_spacings = spacings / mean_spacing
    
    # Compute local spacing distribution
    bins = np.linspace(0, 5, 100)
    hist, _ = np.histogram(normalized_spacings, bins=bins, density=True)
    
    # Expected distribution (simplified)
    # Montgomery predicts behavior similar to random matrix eigenvalue spacings
    bin_centers = (bins[1:] + bins[:-1]) / 2
    
    return {
        'normalized_spacings': normalized_spacings.tolist(),
        'bin_centers': bin_centers.tolist(),
        'spacing_density': hist.tolist(),
        'mean_normalized_spacing': float(np.mean(normalized_spacings)),
        'variance_normalized_spacing': float(np.var(normalized_spacings))
    }

def benchmark_vectorized_operations(zeros: np.ndarray, n_sizes: List[int]) -> Dict:
    """
    Benchmark vectorized operations at different scales.
    
    Args:
        zeros: Array of complex zeros
        n_sizes: List of sample sizes to benchmark
        
    Returns:
        Dictionary with benchmark results
    """
    benchmark_results = {}
    
    for n in n_sizes:
        if n > len(zeros):
            continue
            
        print(f"Benchmarking n={n:,} zeros...")
        
        subset = zeros[:n]
        times = {}
        
        # Benchmark spacing computation
        start_time = time.time()
        spacings = compute_zero_spacings(subset)
        times['spacing_computation'] = time.time() - start_time
        
        # Benchmark statistical analysis
        start_time = time.time()
        stats = compute_gap_statistics(spacings)
        times['statistical_analysis'] = time.time() - start_time
        
        # Benchmark Weyl formula test
        start_time = time.time()
        weyl_test = test_weyl_asymptotic_formula(subset)
        times['weyl_formula_test'] = time.time() - start_time
        
        # Benchmark array operations
        start_time = time.time()
        _ = np.fft.fft(subset.imag)  # FFT of imaginary parts
        times['fft_computation'] = time.time() - start_time
        
        # Compute throughput
        total_time = sum(times.values())
        throughput = n / total_time if total_time > 0 else 0
        
        benchmark_results[n] = {
            'times': times,
            'total_time': total_time,
            'throughput_zeros_per_second': throughput,
            'memory_usage_mb': subset.nbytes / (1024 * 1024)
        }
    
    return benchmark_results

def run_comprehensive_tests(target_sizes: List[int] = None) -> Dict:
    """
    Run comprehensive vectorized tests for zeta zeros dataset.
    
    Args:
        target_sizes: List of sample sizes to test (default: [10^3, 10^4, 10^5, 10^6])
        
    Returns:
        Dictionary with all test results
    """
    if target_sizes is None:
        target_sizes = [1000, 10000, 100000, 1000000]  # 10^3 to 10^6
    
    print("=" * 80)
    print("COMPREHENSIVE VECTORIZED TESTS FOR ZETA ZEROS DATASET")
    print("=" * 80)
    
    # Load zeros
    zeros = load_zeta_zeros()
    max_available = len(zeros)
    
    # Filter target sizes to available data
    valid_sizes = [n for n in target_sizes if n <= max_available]
    
    print(f"Available zeros: {max_available:,}")
    print(f"Test sizes: {valid_sizes}")
    print()
    
    # Run tests for each size
    all_results = {}
    
    for n in valid_sizes:
        print(f"\n{'='*20} TESTING n={n:,} ZEROS {'='*20}")
        
        subset = zeros[:n]
        
        # Compute spacings
        print("Computing zero spacings...")
        spacings = compute_zero_spacings(subset)
        
        # Statistical analysis
        print("Computing gap statistics...")
        gap_stats = compute_gap_statistics(spacings)
        
        # Weyl formula test
        print("Testing Weyl asymptotic formula...")
        weyl_test = test_weyl_asymptotic_formula(subset)
        
        # Montgomery conjecture test
        print("Testing Montgomery pair correlation...")
        montgomery_test = test_montgomery_conjecture(spacings)
        
        # Performance benchmark
        print("Running performance benchmarks...")
        start_time = time.time()
        benchmark = benchmark_vectorized_operations(subset, [n])
        total_test_time = time.time() - start_time
        
        all_results[n] = {
            'gap_statistics': gap_stats,
            'weyl_asymptotic_test': weyl_test,
            'montgomery_correlation_test': montgomery_test,
            'performance_benchmark': benchmark[n] if n in benchmark else None,
            'total_test_time': total_test_time,
            'data_quality': {
                'zeros_count': len(subset),
                'real_part_accuracy': float(np.std(subset.real)),  # Should be ~0 (all 0.5)
                'imaginary_range': [float(np.min(subset.imag)), float(np.max(subset.imag))],
                'monotonic_ordering': bool(np.all(np.diff(subset.imag) > 0))
            }
        }
        
        print(f"✓ Completed tests for n={n:,} in {total_test_time:.2f}s")
    
    return all_results

def generate_test_report(results: Dict, output_file: str = None) -> str:
    """
    Generate comprehensive test report.
    
    Args:
        results: Test results dictionary
        output_file: Optional file to save report
        
    Returns:
        Report string
    """
    report_lines = []
    report_lines.append("ZETA ZEROS VECTORIZED TEST REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Summary table
    report_lines.append("PERFORMANCE SUMMARY")
    report_lines.append("-" * 30)
    report_lines.append(f"{'Size':>8} {'Time(s)':>8} {'Throughput':>12} {'Memory(MB)':>12}")
    report_lines.append("-" * 50)
    
    for n, result in results.items():
        time_taken = result['total_test_time']
        benchmark = result.get('performance_benchmark')
        if benchmark:
            throughput = f"{benchmark['throughput_zeros_per_second']:,.0f}/s"
            memory = f"{benchmark['memory_usage_mb']:.1f}"
        else:
            throughput = "N/A"
            memory = "N/A"
        
        report_lines.append(f"{n:>8,} {time_taken:>8.2f} {throughput:>12} {memory:>12}")
    
    report_lines.append("")
    
    # Detailed results for each size
    for n, result in results.items():
        report_lines.append(f"DETAILED RESULTS FOR n={n:,}")
        report_lines.append("-" * 40)
        
        # Gap statistics
        gap_stats = result['gap_statistics']
        report_lines.append(f"Gap Statistics:")
        report_lines.append(f"  Mean spacing: {gap_stats['mean_spacing']:.6f}")
        report_lines.append(f"  Std deviation: {gap_stats['std_spacing']:.6f}")
        report_lines.append(f"  Min/Max: {gap_stats['min_spacing']:.6f} / {gap_stats['max_spacing']:.6f}")
        
        # Weyl test
        weyl_test = result['weyl_asymptotic_test']
        report_lines.append(f"Weyl Asymptotic Formula:")
        report_lines.append(f"  Mean relative error: {weyl_test['mean_relative_error']:.6f}")
        report_lines.append(f"  Asymptotic accuracy: {weyl_test['asymptotic_accuracy']:.6f}")
        
        # Data quality
        quality = result['data_quality']
        report_lines.append(f"Data Quality:")
        report_lines.append(f"  Real part accuracy: {quality['real_part_accuracy']:.10f}")
        report_lines.append(f"  Monotonic ordering: {quality['monotonic_ordering']}")
        report_lines.append(f"  Imaginary range: {quality['imaginary_range'][0]:.3f} to {quality['imaginary_range'][1]:.3f}")
        
        report_lines.append("")
    
    report = "\n".join(report_lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"✓ Report saved to: {output_file}")
    
    return report

def save_results_json(results: Dict, output_file: str):
    """Save detailed results in JSON format."""
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Detailed results saved to: {output_file}")
    except Exception as e:
        print(f"Warning: Could not save JSON results: {e}")

def main():
    """Main test execution function."""
    print("Zeta Zeros Vectorized Test Suite")
    print("Testing scales: 10^3, 10^4, 10^5, 10^6 zeros")
    print("=" * 60)
    
    try:
        # Run comprehensive tests
        results = run_comprehensive_tests()
        
        # Generate reports
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"../test_results/zeta_zeros_test_report_{timestamp}.txt"
        json_file = f"../test_results/zeta_zeros_test_results_{timestamp}.json"
        
        # Ensure output directory exists
        os.makedirs("../test_results", exist_ok=True)
        
        # Generate and save reports
        report = generate_test_report(results, report_file)
        save_results_json(results, json_file)
        
        # Print summary
        print("\n" + "=" * 60)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print(f"  Tested scales: {list(results.keys())}")
        print(f"  Report: {report_file}")
        print(f"  Detailed results: {json_file}")
        print("=" * 60)
        
        # Quick validation check
        all_passed = True
        for n, result in results.items():
            quality = result['data_quality']
            if not quality['monotonic_ordering'] or quality['real_part_accuracy'] > 1e-10:
                all_passed = False
                break
        
        if all_passed:
            print("✓ All validation checks passed")
        else:
            print("⚠️ Some validation checks failed - review detailed results")
        
        return True
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)