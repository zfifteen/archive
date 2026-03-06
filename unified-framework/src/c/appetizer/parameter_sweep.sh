#!/bin/bash
# Script to sweep width_factor and k_star values for Appetizer Demo
# ===================================================
# This script tests various combinations of width_factor and k_star values
# by passing them as command-line arguments to the sha256_appetizer program.
# Results are logged for analysis.

echo "Starting parameter sweep for Appetizer Demo..."
echo "Results will be logged to parameter_sweep_results.txt"

# Compile the program once
make clean
make

# Lists of values to test
WIDTH_FACTORS=(0.25 0.3 0.35 0.4 0.45 0.5)
K_STARS=(0.02 0.03 0.04 0.05 0.06)

# Clear previous results
echo "width_factor,k_star,Hash_Coverage (%),Round_Coverage (%)" > parameter_sweep_results.txt

for wf in "${WIDTH_FACTORS[@]}"; do
    for ks in "${K_STARS[@]}"; do
        echo "Testing width_factor = $wf, k_star = $ks"
        # Run the demo with the specified parameters and capture output
        OUTPUT=$(./sha256_appetizer $wf $ks)
        # Extract coverage percentages from output
        HASH_COVERAGE=$(echo "$OUTPUT" | grep "Summary for Initial Hash Values" | grep -o "[0-9.]*%" | tr -d "%")
        ROUND_COVERAGE=$(echo "$OUTPUT" | grep "Summary for Round Constants" | grep -o "[0-9.]*%" | tr -d "%")
        # Log results
        echo "$wf,$ks,$HASH_COVERAGE,$ROUND_COVERAGE" >> parameter_sweep_results.txt
        echo "  Hash Coverage: $HASH_COVERAGE%, Round Coverage: $ROUND_COVERAGE%"
    done
done

echo "Parameter sweep complete. Results saved to parameter_sweep_results.txt"
# Display final results
cat parameter_sweep_results.txt

