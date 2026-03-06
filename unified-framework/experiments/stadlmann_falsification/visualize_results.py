#!/usr/bin/env python3
"""
Visualization of Falsification Results
======================================

Creates comparison charts showing claimed vs measured enhancements.
"""

import json
import matplotlib.pyplot as plt
import numpy as np

# Load results
with open('results.json', 'r') as f:
    results = json.load(f)

# Create figure with subplots
fig = plt.figure(figsize=(14, 10))

# 1. Claimed vs Measured Enhancement
ax1 = plt.subplot(2, 2, 1)
categories = ['Claimed\nMinimum', 'Claimed\nCI Lower', 'Measured', 'Claimed\nCI Upper', 'Claimed\nMaximum']
values = [1.0, 0.8, 0.20, 2.2, 2.0]
colors = ['red', 'orange', 'green', 'orange', 'red']

bars = ax1.bar(categories, values, color=colors, alpha=0.6, edgecolor='black')
ax1.axhline(y=0.20, color='green', linestyle='--', linewidth=2, label='Measured (0.20%)')
ax1.axhspan(0.8, 2.2, alpha=0.2, color='red', label='Claimed CI')
ax1.set_ylabel('Enhancement (%)', fontsize=12, fontweight='bold')
ax1.set_title('Claimed vs Measured Density Boost', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.2f}%', ha='center', va='bottom', fontweight='bold')

# 2. Monotonicity Test Results
ax2 = plt.subplot(2, 2, 2)
mono_data = results['tests']['monotonicity']
theta_vals = mono_data['theta_values']
predictions = mono_data['predictions']

ax2.plot(theta_vals, predictions, 'o-', linewidth=2, markersize=8, color='blue')
ax2.axvline(x=0.525, color='red', linestyle='--', linewidth=2, label='Stadlmann θ=0.525')
ax2.set_xlabel('Distribution Level (θ)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Prediction (nth prime)', fontsize=12, fontweight='bold')
ax2.set_title('Monotonicity: θ as "Dial"', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Scale Invariance
ax3 = plt.subplot(2, 2, 3)
scale_data = results['tests']['scale_invariance']
scales = scale_data['scales']
rel_diffs = [scale_data['rel_diffs_by_scale'][str(s)] * 100 for s in scales]

scale_labels = [f"10^{int(np.log10(s))}" for s in scales]
ax3.plot(scale_labels, rel_diffs, 's-', linewidth=2, markersize=10, color='purple')
ax3.set_xlabel('Scale (k)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Relative Difference (%)', fontsize=12, fontweight='bold')
ax3.set_title('Scale Invariance Test', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)

# Add CV annotation
cv = scale_data['coefficient_of_variation']
ax3.text(0.5, 0.95, f'CV = {cv:.3f}', transform=ax3.transAxes,
         fontsize=11, fontweight='bold', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
         verticalalignment='top', horizontalalignment='center')

# 4. Test Summary
ax4 = plt.subplot(2, 2, 4)
test_names = ['Independence', 'Monotonicity', 'Claimed\nBoost', 'Scale\nInvariance', 'Randomness']
test_status = [
    'SUPPORTED' if not results['tests']['independence']['falsified'] else 'FALSIFIED',
    'SUPPORTED' if not results['tests']['monotonicity']['falsified'] else 'FALSIFIED',
    'FALSIFIED' if results['tests']['claimed_boost']['falsified'] else 'SUPPORTED',
    'SUPPORTED' if not results['tests']['scale_invariance']['falsified'] else 'FALSIFIED',
    'SUPPORTED' if not results['tests']['randomness']['falsified'] else 'FALSIFIED',
]
colors_status = ['green' if s == 'SUPPORTED' else 'red' for s in test_status]

y_pos = np.arange(len(test_names))
ax4.barh(y_pos, [1 if s == 'SUPPORTED' else -1 for s in test_status], color=colors_status, alpha=0.6)
ax4.set_yticks(y_pos)
ax4.set_yticklabels(test_names, fontsize=11, fontweight='bold')
ax4.set_xlabel('Test Result', fontsize=12, fontweight='bold')
ax4.set_title('Test Summary', fontsize=14, fontweight='bold')
ax4.set_xlim([-1.5, 1.5])
ax4.set_xticks([-1, 1])
ax4.set_xticklabels(['FALSIFIED', 'SUPPORTED'], fontweight='bold')
ax4.axvline(x=0, color='black', linewidth=2)
ax4.grid(axis='x', alpha=0.3)

# Overall title
fig.suptitle('Stadlmann Distribution Level Falsification: Visual Summary', 
             fontsize=16, fontweight='bold', y=0.995)

# Add text annotation with key finding
fig.text(0.5, 0.01, 
         '⚠️  KEY FINDING: Claimed 1-2% boost is FALSIFIED - Actual: ~0.20% (5-10× smaller)',
         ha='center', fontsize=12, fontweight='bold', 
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

plt.tight_layout(rect=[0, 0.03, 1, 0.99])
plt.savefig('falsification_visualization.png', dpi=150, bbox_inches='tight')
print("✅ Visualization saved to falsification_visualization.png")

# Create second figure: Enhancement comparison
fig2, ax = plt.subplots(figsize=(10, 6))

# Data
methods = ['Claimed\n(Min)', 'Claimed\n(Max)', 'Measured\n(Bootstrap)', 'Scale 10^4', 'Scale 10^5', 'Scale 10^6']
enhancements = [1.0, 2.0, 0.20, 0.179, 0.223, 0.268]
colors2 = ['red', 'red', 'green', 'blue', 'blue', 'blue']

bars = ax.bar(methods, enhancements, color=colors2, alpha=0.6, edgecolor='black', linewidth=2)

# Add horizontal line at measured value
ax.axhline(y=0.20, color='green', linestyle='--', linewidth=2, label='Measured Bootstrap Mean')
ax.axhspan(0.8, 2.2, alpha=0.15, color='red', label='Claimed CI Range')

ax.set_ylabel('Enhancement (%)', fontsize=14, fontweight='bold')
ax.set_title('Stadlmann Density Enhancement: Claimed vs Measured', fontsize=16, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar, val in zip(bars, enhancements):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.2f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add annotation
ax.text(0.5, 0.95, 
        'FALSIFIED: 5-10× discrepancy between claimed and measured',
        transform=ax.transAxes, ha='center', va='top',
        fontsize=12, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

plt.tight_layout()
plt.savefig('enhancement_comparison.png', dpi=150, bbox_inches='tight')
print("✅ Enhancement comparison saved to enhancement_comparison.png")

print("\nVisualization complete!")
print(f"Status: {results['status']}")
print(f"Falsification rate: {results['summary']['falsification_rate']*100:.1f}%")
