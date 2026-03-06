#!/bin/bash

# Script to run PR-0003 experiment at 10^9 scale with Z5D backend
# Preconfigured: max_prime=1e9, backend=z5d, autocorr=none, no-cache, plots disabled

cd /Users/velocityworks/IdeaProjects/playground/experiments/PR-0003_prime_log_gap_optimized

python run_experiment.py --max-prime 1e9 --prime-backend z5d --autocorr none --no-cache