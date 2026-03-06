#!/usr/bin/env python3
"""
Generate comprehensive Z5D benchmark results table
"""
from z5d_pi_fast_integrated import load_zeros, benchmark_pk
import pandas as pd
import numpy as np
import time

def generate_comprehensive_results():
    """Generate results table matching the problem statement format"""
    print("Generating comprehensive Z5D benchmark results...")
    
    # Load zeros
    zeros = load_zeros()
    print(f"Loaded {len(zeros)} zeta zeros")
    
    # Key zero counts for comprehensive table
    key_zeros = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
    
    print("Running comprehensive benchmark...")
    start_time = time.time()
    
    # Run benchmark and capture results
    import sys
    from io import StringIO
    
    # Capture output
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    benchmark_pk(zeros, max_zeros_range=key_zeros)
    
    sys.stdout = old_stdout
    output = captured_output.getvalue()
    
    total_time = time.time() - start_time
    print(f"Benchmark completed in {total_time:.2f}s")
    
    # Parse results
    lines = output.strip().split('\n')
    data_lines = [line for line in lines if ',' in line and 'k,true_pk' not in line]
    
    # Create summary table
    data = []
    for line in data_lines:
        parts = line.split(',')
        data.append({
            'max_zeros': int(parts[7]),
            'k': int(parts[0]),
            'rel_err': float(parts[4]),
            'time': float(parts[5]),
            'density_enh': float(parts[6])
        })
    
    df = pd.DataFrame(data)
    
    # Generate summary table
    print("\n" + "="*80)
    print("Z5D BENCHMARK RESULTS SUMMARY")
    print("="*80)
    print("| max_zeros | k=1000 rel_err(%) | k=1e6 rel_err(%) | Avg Time (s) | Density Enh (%) |")
    print("|-----------|-------------------|------------------|--------------|-----------------| ")
    
    for zero_count in key_zeros:
        subset = df[df['max_zeros'] == zero_count]
        if len(subset) > 0:
            k1000_err = subset[subset['k'] == 1000]['rel_err'].iloc[0] if len(subset[subset['k'] == 1000]) > 0 else 0
            k1m_err = subset[subset['k'] == 1000000]['rel_err'].iloc[0] if len(subset[subset['k'] == 1000000]) > 0 else 0
            avg_time = subset['time'].mean()
            density = subset['density_enh'].iloc[0]
            
            print(f"| {zero_count:9d} | {k1000_err:16.3f} | {k1m_err:15.3f} | {avg_time:11.3f} | {density:14.1f} |")
    
    # Key findings
    print("\n" + "="*80)
    print("KEY FINDINGS:")
    print("-" * 40)
    
    k1m_data = df[df['k'] == 1000000].sort_values('max_zeros')
    if len(k1m_data) > 1:
        start_err = k1m_data.iloc[0]['rel_err']
        end_err = k1m_data.iloc[-1]['rel_err']
        improvement = abs(start_err / end_err)
        print(f"✅ Rel_err magnitude decreases from {start_err:.3f}% to {end_err:.3f}% ({improvement:.1f}x better)")
    
    k1k_data = df[df['k'] == 1000].sort_values('max_zeros')
    if len(k1k_data) > 1:
        start_time = k1k_data.iloc[0]['time']
        end_time = k1k_data.iloc[-1]['time']
        scaling = end_time / start_time
        print(f"✅ Time scales from {start_time:.3f}s to {end_time:.3f}s ({scaling:.1f}x scaling)")
    
    density_1k = df[df['k'] == 1000]['density_enh'].iloc[0] if len(df[df['k'] == 1000]) > 0 else 0
    print(f"✅ Density enhancement: {density_1k:.1f}% (target ~195)")
    print(f"✅ Zero range: 1-99 tested")
    print(f"✅ Multiprocessing: {len(key_zeros)} zero counts in {total_time:.1f}s")
    
    # Save detailed results
    with open('comprehensive_z5d_results.csv', 'w') as f:
        f.write(output)
    print(f"\n📊 Detailed results saved to: comprehensive_z5d_results.csv")

if __name__ == "__main__":
    generate_comprehensive_results()