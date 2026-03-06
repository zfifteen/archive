#!/bin/bash

# Shell script to run the complete logband test from 1e2 through 1e18
# Run this script in the project directory: ./run_full_logband.sh
# Note: Large scales (1e14+) may take hours or days; run in background if needed.
# Ensure python and dependencies are available.

# Scales to test: 10^2 to 10^18
SCALES=(100 1000 10000 100000 1000000 10000000 100000000 1000000000 10000000000 100000000000 1000000000000 10000000000000 100000000000000 1000000000000000 10000000000000000 100000000000000000 1000000000000000000)

# Output base directory
OUTPUT_BASE="results_full_logband"

# Create output directory if not exists
mkdir -p "$OUTPUT_BASE"

# Loop through scales
for scale in "${SCALES[@]}"; do
    echo "Starting run for scale $scale..."
    python run_experiment.py --mode logband --scales "$scale" --alphas "2.0" --output "$OUTPUT_BASE/scale_${scale}" --free-loc
    if [ $? -eq 0 ]; then
        echo "Completed run for scale $scale."
    else
        echo "Error in run for scale $scale. Check logs."
        exit 1
    fi
done

echo "All runs completed. Results in $OUTPUT_BASE/"