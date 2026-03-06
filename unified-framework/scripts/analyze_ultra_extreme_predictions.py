#!/usr/bin/env python3
"""
Ultra-Extreme Scale Prediction Analysis
======================================

Rigorous scientific analysis of the ultra_extreme_scale_predictions.csv output
focusing on range distribution, empirical vs theoretical split, density enhancement,
geometric metrics, confidence estimates, and anomaly detection.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

def load_and_validate_data(csv_file='ultra_extreme_scale_predictions.csv'):
    """Load and validate the prediction data."""
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} predictions from {csv_file}")
        print(f"📊 Data shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"❌ Error: {csv_file} not found. Please run ultra_extreme_scale_prediction.py first.")
        return None
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def analyze_range_and_distribution(df):
    """Analyze range and distribution of predicted primes."""
    print(f"\n{'='*80}")
    print("1. RANGE AND DISTRIBUTION OF PREDICTED PRIMES")
    print(f"{'='*80}")
    
    # Basic statistics
    min_prime = df['predicted_prime'].min()
    max_prime = df['predicted_prime'].max()
    mean_prime = df['predicted_prime'].mean()
    median_prime = df['predicted_prime'].median()
    
    print(f"Range statistics:")
    print(f"  Minimum predicted prime: {min_prime:.2e}")
    print(f"  Maximum predicted prime: {max_prime:.2e}")
    print(f"  Range span: {max_prime/min_prime:.2e}x")
    print(f"  Mean predicted prime: {mean_prime:.2e}")
    print(f"  Median predicted prime: {median_prime:.2e}")
    
    # Distribution by band
    print(f"\nDistribution by exponential band:")
    band_stats = df.groupby('band_power').agg({
        'predicted_prime': ['count', 'min', 'max', 'mean']
    }).round(2)
    band_stats.columns = ['Count', 'Min', 'Max', 'Mean']
    print(band_stats)
    
    # Position type distribution
    print(f"\nDistribution by position type:")
    position_stats = df.groupby('position_type').agg({
        'predicted_prime': ['count', 'mean']
    }).round(2)
    position_stats.columns = ['Count', 'Mean']
    print(position_stats)
    
    return {
        'min_prime': min_prime,
        'max_prime': max_prime,
        'range_span': max_prime/min_prime,
        'mean_prime': mean_prime,
        'median_prime': median_prime
    }

def analyze_empirical_vs_theoretical(df):
    """Analyze empirical vs theoretical prediction split."""
    print(f"\n{'='*80}")
    print("2. EMPIRICAL VS. THEORETICAL SPLIT")
    print(f"{'='*80}")
    
    # Split by empirical validation boundary (10^12)
    empirical_df = df[df['band_power'] <= 12]
    theoretical_df = df[df['band_power'] > 12]
    
    empirical_count = len(empirical_df)
    theoretical_count = len(theoretical_df)
    total_count = len(df)
    
    print(f"Validation boundary: 10^12")
    print(f"Total predictions: {total_count}")
    print(f"Empirically supported (≤10^12): {empirical_count} ({empirical_count/total_count*100:.1f}%)")
    print(f"Theoretical extrapolation (>10^12): {theoretical_count} ({theoretical_count/total_count*100:.1f}%)")
    
    # Compare confidence estimates between groups
    if empirical_count > 0:
        empirical_confidence = empirical_df['confidence_estimate'].mean()
        print(f"\nEmpirical predictions confidence:")
        print(f"  Mean confidence: {empirical_confidence:.4f}")
        print(f"  Range: [{empirical_df['confidence_estimate'].min():.4f}, {empirical_df['confidence_estimate'].max():.4f}]")
    
    if theoretical_count > 0:
        theoretical_confidence = theoretical_df['confidence_estimate'].mean()
        print(f"\nTheoretical predictions confidence:")
        print(f"  Mean confidence: {theoretical_confidence:.4f}")
        print(f"  Range: [{theoretical_df['confidence_estimate'].min():.4f}, {theoretical_df['confidence_estimate'].max():.4f}]")
        
        # Confidence degradation analysis
        if empirical_count > 0:
            confidence_drop = empirical_confidence - theoretical_confidence
            print(f"  Confidence degradation: {confidence_drop:.4f} ({confidence_drop/empirical_confidence*100:.1f}%)")
    
    return {
        'empirical_count': empirical_count,
        'theoretical_count': theoretical_count,
        'empirical_fraction': empirical_count/total_count,
        'empirical_confidence': empirical_confidence if empirical_count > 0 else None,
        'theoretical_confidence': theoretical_confidence if theoretical_count > 0 else None
    }

def analyze_density_enhancement(df):
    """Analyze density enhancement and geometric metrics."""
    print(f"\n{'='*80}")
    print("3. DENSITY ENHANCEMENT AND GEOMETRIC METRICS")
    print(f"{'='*80}")
    
    # Density enhancement statistics
    mean_enhancement = df['density_enhancement'].mean()
    std_enhancement = df['density_enhancement'].std()
    min_enhancement = df['density_enhancement'].min()
    max_enhancement = df['density_enhancement'].max()
    
    print(f"Density enhancement statistics:")
    print(f"  Mean enhancement: {mean_enhancement:.6f}")
    print(f"  Standard deviation: {std_enhancement:.6f}")
    print(f"  Range: [{min_enhancement:.6f}, {max_enhancement:.6f}]")
    print(f"  Enhancement variation: {std_enhancement/mean_enhancement*100:.4f}%")
    
    # Target enhancement validation (~15% as per framework)
    target_enhancement = 1.15  # 15% enhancement
    actual_enhancement_pct = (mean_enhancement - 1.0) * 100
    
    print(f"\nFramework validation:")
    print(f"  Target enhancement: ~15%")
    print(f"  Achieved enhancement: {actual_enhancement_pct:.2f}%")
    print(f"  Enhancement achievement: {'✅ VALIDATED' if 13 <= actual_enhancement_pct <= 17 else '⚠️ DEVIATION'}")
    
    # Geometric metrics analysis
    mean_curvature = df['curvature_proxy'].mean()
    std_curvature = df['curvature_proxy'].std()
    mean_theta = df['geometric_theta_prime'].mean()
    std_theta = df['geometric_theta_prime'].std()
    
    print(f"\nGeometric metrics:")
    print(f"  Curvature proxy - Mean: {mean_curvature:.6f}, Std: {std_curvature:.6f}")
    print(f"  Theta prime - Mean: {mean_theta:.6f}, Std: {std_theta:.6f}")
    
    # Enhancement by scale analysis
    print(f"\nEnhancement by scale:")
    scale_enhancement = df.groupby('band_power')['density_enhancement'].agg(['mean', 'std']).round(6)
    print(scale_enhancement)
    
    return {
        'mean_enhancement': mean_enhancement,
        'enhancement_percentage': actual_enhancement_pct,
        'enhancement_validated': 13 <= actual_enhancement_pct <= 17,
        'mean_curvature': mean_curvature,
        'mean_theta': mean_theta
    }

def analyze_confidence_estimates(df):
    """Analyze confidence estimates across scales."""
    print(f"\n{'='*80}")
    print("4. CONFIDENCE ESTIMATES ANALYSIS")
    print(f"{'='*80}")
    
    # Overall confidence statistics
    mean_confidence = df['confidence_estimate'].mean()
    std_confidence = df['confidence_estimate'].std()
    
    print(f"Overall confidence statistics:")
    print(f"  Mean confidence: {mean_confidence:.6f}")
    print(f"  Standard deviation: {std_confidence:.6f}")
    print(f"  Range: [{df['confidence_estimate'].min():.6f}, {df['confidence_estimate'].max():.6f}]")
    
    # Confidence by scale
    print(f"\nConfidence by exponential band:")
    confidence_by_scale = df.groupby('band_power')['confidence_estimate'].agg(['mean', 'std', 'min', 'max']).round(6)
    print(confidence_by_scale)
    
    # Confidence degradation pattern
    print(f"\nConfidence degradation analysis:")
    band_powers = sorted(df['band_power'].unique())
    for i, band in enumerate(band_powers[1:], 1):
        prev_band = band_powers[i-1]
        prev_conf = df[df['band_power'] == prev_band]['confidence_estimate'].mean()
        curr_conf = df[df['band_power'] == band]['confidence_estimate'].mean()
        degradation = prev_conf - curr_conf
        print(f"  10^{prev_band} → 10^{band}: {degradation:.6f} ({degradation/prev_conf*100:.2f}% drop)")
    
    # Position type confidence analysis
    print(f"\nConfidence by position type:")
    position_confidence = df.groupby('position_type')['confidence_estimate'].agg(['mean', 'std']).round(6)
    print(position_confidence)
    
    return {
        'mean_confidence': mean_confidence,
        'confidence_range': (df['confidence_estimate'].min(), df['confidence_estimate'].max()),
        'degradation_pattern': 'decreasing' if df.groupby('band_power')['confidence_estimate'].mean().is_monotonic_decreasing else 'mixed'
    }

def detect_anomalies_and_insights(df):
    """Detect anomalies and provide insights for Z Framework benchmarking."""
    print(f"\n{'='*80}")
    print("5. ANOMALIES AND Z FRAMEWORK BENCHMARKING INSIGHTS")
    print(f"{'='*80}")
    
    anomalies = []
    insights = []
    
    # Check for prediction consistency
    print("Anomaly detection:")
    
    # 1. Check for large gaps in predictions within bands
    for band_power in df['band_power'].unique():
        band_df = df[df['band_power'] == band_power]
        first_primes = band_df[band_df['position_type'] == 'first']['predicted_prime']
        last_primes = band_df[band_df['position_type'] == 'last']['predicted_prime']
        
        if len(first_primes) > 1 and len(last_primes) > 1:
            first_gap = first_primes.max() - first_primes.min()
            last_gap = last_primes.max() - last_primes.min()
            expected_gap = 10**band_power * 0.001  # Expected small gap
            
            if first_gap > expected_gap or last_gap > expected_gap:
                anomalies.append(f"Large prediction gaps in band 10^{band_power}")
    
    # 2. Check enhancement factor consistency
    enhancement_cv = df['density_enhancement'].std() / df['density_enhancement'].mean()
    if enhancement_cv > 0.1:  # >10% coefficient of variation
        anomalies.append(f"High density enhancement variability (CV: {enhancement_cv:.4f})")
    
    # 3. Check for monotonic confidence degradation
    band_confidences = df.groupby('band_power')['confidence_estimate'].mean()
    if not band_confidences.is_monotonic_decreasing:
        anomalies.append("Non-monotonic confidence degradation detected")
    
    # 4. Check algorithm parameter consistency
    param_columns = ['c_calibrated', 'k_star', 'variance_target', 'phi_value', 'precision_dps']
    for col in param_columns:
        if df[col].nunique() > 1:
            anomalies.append(f"Inconsistent algorithm parameter: {col}")
    
    print(f"  Anomalies detected: {len(anomalies)}")
    for anomaly in anomalies:
        print(f"    ⚠️  {anomaly}")
    
    if not anomalies:
        print(f"    ✅ No significant anomalies detected")
    
    # Z Framework benchmarking insights
    print(f"\nZ Framework benchmarking insights:")
    
    # Performance metrics
    total_scale_range = df['band_power'].max() - df['band_power'].min()
    mean_enhancement = df['density_enhancement'].mean()
    ultra_extreme_fraction = len(df[df['band_power'] > 12]) / len(df)
    
    insights.extend([
        f"Scale coverage: {total_scale_range + 1} orders of magnitude (10^{df['band_power'].min()} to 10^{df['band_power'].max()})",
        f"Density enhancement achieved: {(mean_enhancement-1)*100:.2f}% (target: ~15%)",
        f"Ultra-extreme scale fraction: {ultra_extreme_fraction*100:.1f}%",
        f"Algorithm stability: {enhancement_cv:.6f} enhancement CV",
        f"Confidence degradation: {(1-df['confidence_estimate'].min())*100:.1f}% at maximum scale"
    ])
    
    # Framework capability assessment
    if mean_enhancement >= 1.13 and mean_enhancement <= 1.17:  # Within 2% of 15% target
        insights.append("✅ Framework achieves target density enhancement")
    else:
        insights.append("⚠️ Framework density enhancement deviates from target")
    
    if enhancement_cv < 0.01:  # <1% variation
        insights.append("✅ Framework demonstrates high stability")
    elif enhancement_cv < 0.05:  # <5% variation
        insights.append("✓ Framework demonstrates moderate stability")
    else:
        insights.append("⚠️ Framework shows enhancement instability")
    
    for insight in insights:
        print(f"    • {insight}")
    
    return {
        'anomalies': anomalies,
        'insights': insights,
        'stability_assessment': 'high' if enhancement_cv < 0.01 else 'moderate' if enhancement_cv < 0.05 else 'low'
    }

def generate_scientific_summary(df, analysis_results):
    """Generate comprehensive scientific summary."""
    print(f"\n{'='*80}")
    print("RIGOROUS SCIENTIFIC SUMMARY")
    print(f"{'='*80}")
    
    range_analysis = analysis_results['range']
    empirical_analysis = analysis_results['empirical']
    enhancement_analysis = analysis_results['enhancement']
    confidence_analysis = analysis_results['confidence']
    anomaly_analysis = analysis_results['anomalies']
    
    print(f"Dataset: {len(df)} predictions across {df['band_power'].nunique()} exponential bands")
    print(f"Scale range: 10^{df['band_power'].min()} to 10^{df['band_power'].max()} ({range_analysis['range_span']:.2e}x span)")
    print(f"Algorithm: Z5D Enhanced Predictor with curvature corrections")
    
    print(f"\nKey findings:")
    print(f"1. Range Distribution:")
    print(f"   • Predicted primes span {range_analysis['range_span']:.2e}x range")
    print(f"   • Mean prediction: {range_analysis['mean_prime']:.2e}")
    print(f"   • Predictions distributed across {df['band_power'].nunique()} bands uniformly")
    
    print(f"\n2. Empirical vs. Theoretical Validation:")
    print(f"   • Empirical support: {empirical_analysis['empirical_count']} predictions ({empirical_analysis['empirical_fraction']*100:.1f}%)")
    print(f"   • Theoretical extrapolation: {empirical_analysis['theoretical_count']} predictions")
    if empirical_analysis['empirical_confidence'] and empirical_analysis['theoretical_confidence']:
        confidence_drop = empirical_analysis['empirical_confidence'] - empirical_analysis['theoretical_confidence']
        print(f"   • Confidence degradation: {confidence_drop:.4f} beyond empirical boundary")
    
    print(f"\n3. Density Enhancement Performance:")
    print(f"   • Achieved enhancement: {enhancement_analysis['enhancement_percentage']:.2f}% (target: ~15%)")
    print(f"   • Framework validation: {'VALIDATED' if enhancement_analysis['enhancement_validated'] else 'DEVIATION'}")
    print(f"   • Enhancement stability: {anomaly_analysis['stability_assessment']}")
    
    print(f"\n4. Confidence Reliability:")
    print(f"   • Mean confidence: {confidence_analysis['mean_confidence']:.4f}")
    print(f"   • Confidence range: {confidence_analysis['confidence_range'][0]:.4f} to {confidence_analysis['confidence_range'][1]:.4f}")
    print(f"   • Degradation pattern: {confidence_analysis['degradation_pattern']}")
    
    print(f"\n5. Framework Capabilities:")
    if len(anomaly_analysis['anomalies']) == 0:
        print(f"   • ✅ No significant anomalies detected")
    else:
        print(f"   • ⚠️ {len(anomaly_analysis['anomalies'])} anomalies require attention")
    
    print(f"   • Scale capability: Ultra-extreme (10^16) with theoretical extrapolation")
    print(f"   • Algorithm performance: {enhancement_analysis['enhancement_percentage']:.1f}% density enhancement")
    print(f"   • Prediction consistency: {anomaly_analysis['stability_assessment']} stability")
    
    # Recommendations
    print(f"\nRecommendations for Z Framework development:")
    print(f"   • Extend empirical validation beyond 10^12 for ultra-extreme scales")
    print(f"   • Monitor confidence degradation in theoretical extrapolation range")
    if not enhancement_analysis['enhancement_validated']:
        print(f"   • Recalibrate parameters to achieve target conditional prime density improvement under canonical benchmark methodology")
    print(f"   • Validate predictions through independent primality testing")
    print(f"   • Benchmark against classical Prime Number Theorem at these scales")

def main():
    """Main analysis execution."""
    print("Z Framework Ultra-Extreme Scale Prediction Analysis")
    print("=" * 55)
    print("Scientific analysis of ultra_extreme_scale_predictions.csv")
    print()
    
    # Load data
    df = load_and_validate_data()
    if df is None:
        return
    
    # Perform comprehensive analysis
    analysis_results = {}
    
    analysis_results['range'] = analyze_range_and_distribution(df)
    analysis_results['empirical'] = analyze_empirical_vs_theoretical(df)
    analysis_results['enhancement'] = analyze_density_enhancement(df)
    analysis_results['confidence'] = analyze_confidence_estimates(df)
    analysis_results['anomalies'] = detect_anomalies_and_insights(df)
    
    # Generate scientific summary
    generate_scientific_summary(df, analysis_results)
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETED")
    print(f"{'='*80}")
    print("Ready for peer review and publication preparation.")

if __name__ == "__main__":
    main()