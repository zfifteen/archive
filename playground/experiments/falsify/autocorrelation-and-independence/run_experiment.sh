#!/bin/bash

# Run the ACF falsification experiment with standard parameters
# This script assumes you have the necessary dependencies installed (numpy, scipy, statsmodels, matplotlib, seaborn)

echo "Starting ACF Falsification Experiment..."

# Using parameters from TECH-SPEC.md
# - 10,000 permutations for p-value < 0.01 precision
# - 1,000 bootstrap iterations for robust CIs
# - Ranges covering 10^8 to 10^11

python3 run_acf_falsification.py \
  --ranges "1e8:1e9,1e9:1e10,1e10:1e11" \
  --window-size 100000 \
  --max-lag 100 \
  --permutations 10000 \
  --bootstrap-iterations 1000 \
  --output results/ \
  --detrend

echo "Experiment complete. Check results/report.md for the summary."
