#!/bin/bash
# Script to sweep width_factor values for Appetizer Demo
# ===================================================
# This script tests various width_factor values to observe impact on coverage.

echo "Starting width_factor sweep for Appetizer Demo..."
echo "Results will be logged to width_factor_sweep_results.txt"

# List of width_factor values to test
WIDTH_FACTORS=(0.1 0.125 0.15 0.175 0.2 0.25 0.3)

# Clear previous results
echo "width_factor,Hash_Coverage (%),Round_Coverage (%)" > width_factor_sweep_results.txt

for wf in "${WIDTH_FACTORS[@]}"; do
    echo "Testing width_factor = $wf"
    # Update width_factor in the source code
    sed -i.bak "s/double width_factor = [0-9.]*;/double width_factor = $wf;/" sha256_appetizer.c
    # Force rebuild by cleaning first
    make clean
    make
    # Run the demo and capture output
    OUTPUT=$(./sha256_appetizer)
    # Extract coverage percentages from output
    HASH_COVERAGE=$(echo "$OUTPUT" | grep "Summary for Initial Hash Values" | grep -o "[0-9.]*%" | tr -d "%")
    ROUND_COVERAGE=$(echo "$OUTPUT" | grep "Summary for Round Constants" | grep -o "[0-9.]*%" | tr -d "%")
    # Log results
    echo "$wf,$HASH_COVERAGE,$ROUND_COVERAGE" >> width_factor_sweep_results.txt
    echo "  Hash Coverage: $HASH_COVERAGE%, Round Coverage: $ROUND_COVERAGE%"
done

echo "Sweep complete. Results saved to width_factor_sweep_results.txt"
# Display final results
cat width_factor_sweep_results.txt

