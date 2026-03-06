#!/usr/bin/env python3
"""
Visualization of Categorical Biproducts Experiment Results

Generates plots comparing baseline and categorical GVA performance.
"""

import json
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Load results
results_dir = Path(__file__).parent.parent / "results"

with open(results_dir / "baseline_profile.json") as f:
    baseline = json.load(f)

with open(results_dir / "categorical_profile.json") as f:
    categorical = json.load(f)

# Extract metrics
baseline_vars = [r['variance']['total'] for r in baseline]
categorical_vars = [r['variance']['total'] for r in categorical]

baseline_embed_times = [r['timing']['embed_per_candidate_sec'] * 1e6 for r in baseline]
categorical_embed_times = [r['timing']['embed_per_candidate_sec'] * 1e6 for r in categorical]

baseline_dist_times = [r['timing']['distance_per_candidate_sec'] * 1e6 for r in baseline]
categorical_dist_times = [r['timing']['distance_per_candidate_sec'] * 1e6 for r in categorical]

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Categorical Biproducts vs Baseline GVA\nVERDICT: FALSIFIED', 
             fontsize=16, fontweight='bold', color='red')

# 1. Variance Comparison
ax = axes[0, 0]
positions = [1, 2]
bp = ax.boxplot([baseline_vars, categorical_vars], positions=positions, 
                 widths=0.6, patch_artist=True, 
                 labels=['Baseline\n(n=8)', 'Categorical\n(n=3)'])
for patch, color in zip(bp['boxes'], ['lightblue', 'lightcoral']):
    patch.set_facecolor(color)
ax.set_ylabel('Total Variance', fontsize=12)
ax.set_title('Variance: No Significant Difference\np=0.46, ratio=0.993', fontsize=11)
ax.axhline(np.mean(baseline_vars), color='blue', linestyle='--', alpha=0.5, label='Baseline mean')
ax.axhline(np.mean(categorical_vars), color='red', linestyle='--', alpha=0.5, label='Categorical mean')
ax.grid(axis='y', alpha=0.3)
ax.legend(fontsize=9)

# Add falsification criterion box
ax.text(0.98, 0.02, '✗ Variance ratio > 0.95\n(0.993 > 0.95)', 
        transform=ax.transAxes, fontsize=9, verticalalignment='bottom',
        horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 2. Embedding Time Comparison
ax = axes[0, 1]
positions = [1, 2]
bp = ax.boxplot([baseline_embed_times, categorical_embed_times], positions=positions,
                 widths=0.6, patch_artist=True,
                 labels=['Baseline\n(n=8)', 'Categorical\n(n=3)'])
for patch, color in zip(bp['boxes'], ['lightblue', 'lightcoral']):
    patch.set_facecolor(color)
ax.set_ylabel('Embedding Time (µs/candidate)', fontsize=12)
ax.set_title('Embedding: 2.52× Overhead', fontsize=11, color='red')
ax.grid(axis='y', alpha=0.3)

# Add threshold line
threshold = np.mean(baseline_embed_times) * 2.0
ax.axhline(threshold, color='orange', linestyle='--', linewidth=2, 
           label='2× Threshold', alpha=0.7)
ax.legend(fontsize=9)

# Add falsification criterion box
ax.text(0.98, 0.98, '✗ Overhead > 2.0×\n(2.52× > 2.0×)', 
        transform=ax.transAxes, fontsize=9, verticalalignment='top',
        horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 3. Distance Time Comparison
ax = axes[1, 0]
positions = [1, 2]
bp = ax.boxplot([baseline_dist_times, categorical_dist_times], positions=positions,
                 widths=0.6, patch_artist=True,
                 labels=['Baseline\n(n=8)', 'Categorical\n(n=3)'])
for patch, color in zip(bp['boxes'], ['lightblue', 'lightcoral']):
    patch.set_facecolor(color)
ax.set_ylabel('Distance Time (µs/candidate)', fontsize=12)
ax.set_title('Distance: 1.19× Overhead', fontsize=11)
ax.grid(axis='y', alpha=0.3)

# 4. Summary Verdict
ax = axes[1, 1]
ax.axis('off')

verdict_text = """
HYPOTHESIS FALSIFIED
(High Confidence)

Falsification Criteria:
━━━━━━━━━━━━━━━━━━━━━━━━━
✗ Variance ratio 0.993 > 0.95
  (Only 0.73% reduction)

✗ p-value 0.4591 > 0.05
  (Not statistically significant)

✗ Overhead 2.52× > 2.0×
  (Exceeds acceptable threshold)

━━━━━━━━━━━━━━━━━━━━━━━━━

Conclusion:
Category-theoretic biproduct
decomposition does NOT enhance
GVA. The baseline method is
already near-optimal.

Root Cause:
GVA dimensions are already
independent. Categorical
abstraction is a mathematical
restatement, not an algorithmic
improvement.
"""

ax.text(0.5, 0.5, verdict_text, transform=ax.transAxes,
        fontsize=10, verticalalignment='center', horizontalalignment='center',
        family='monospace',
        bbox=dict(boxstyle='round', facecolor='mistyrose', alpha=0.9, pad=1))

plt.tight_layout()

# Save figure
output_file = results_dir / "comparison_plot.png"
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"Plot saved to: {output_file}")

# Also save as PDF for high quality
output_pdf = results_dir / "comparison_plot.pdf"
plt.savefig(output_pdf, bbox_inches='tight')
print(f"PDF saved to: {output_pdf}")

print("\nVisualization complete.")
