#!/bin/bash

# Script to run PR-0003 experiments across all scales from 10^5 to 10^10
# Configured with appropriate flags: backend auto/z5d, plots enabled for small scales only, autocorr none, no-cache

cd /Users/velocityworks/IdeaProjects/playground/experiments/PR-0003_prime_log_gap_optimized || exit

echo "Starting runs from 10^5 to 10^10..."

# 10^5: segmented (auto), plots enabled
echo "Running 10^5..."
python run_experiment.py --max-prime 1e5 --prime-backend auto --autocorr none --plots --no-cache

# 10^6: segmented (auto), plots enabled
echo "Running 10^6..."
python run_experiment.py --max-prime 1e6 --prime-backend auto --autocorr none --plots --no-cache

# 10^7: segmented (auto), plots enabled
echo "Running 10^7..."
python run_experiment.py --max-prime 1e7 --prime-backend auto --autocorr none --plots --no-cache

# 10^8: segmented (auto), plots disabled
echo "Running 10^8..."
python run_experiment.py --max-prime 1e8 --prime-backend auto --autocorr none --no-cache

# 10^9: z5d, plots disabled
echo "Running 10^9..."
python run_experiment.py --max-prime 1e9 --prime-backend z5d --autocorr none --no-cache

# 10^10: z5d, plots disabled
echo "Running 10^10..."
python run_experiment.py --max-prime 1e10 --prime-backend z5d --autocorr none --no-cache

echo "All runs completed."