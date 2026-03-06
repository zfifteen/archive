#!/bin/bash
# Script to sweep combined width_factor and k_star values for Appetizer Demo
# ===================================================
# This script tests combinations of width_factor and k_star values to observe impact on coverage.

echo "Starting combined width_factor and k_star sweep for Appetizer Demo..."
echo "Results will be logged to combined_sweep_results.txt"

# Lists of values to test
WIDTH_FACTORS=(0.2 0.25 0.3)
K_STARS=(0.03 0.05 0.07)

# Clear previous results
echo "width_factor,k_star,Hash_Coverage (%),Round_Coverage (%)" > combined_sweep_results.txt

for wf in "${WIDTH_FACTORS[@]}"; do
    for ks in "${K_STARS[@]}"; do
        echo "Testing width_factor = $wf, k_star = $ks"
        # Update width_factor and k_star in the source code
        sed -i.bak "s/double width_factor = [0-9.]*;/double width_factor = $wf;/" sha256_appetizer.c
        sed -i.bak "s/double k_star = [0-9.]*;/double k_star = $ks;/" sha256_appetizer.c
        # Force rebuild by cleaning first
        make clean
        make
        # Run the demo and capture output
        OUTPUT=$(./bin/sha256_appetizer)
        # Extract coverage percentages from output
        HASH_COVERAGE=$(echo "$OUTPUT" | grep "Summary for Initial Hash Values" | grep -o "[0-9.]*%" | tr -d "%")
        ROUND_COVERAGE=$(echo "$OUTPUT" | grep "Summary for Round Constants" | grep -o "[0-9.]*%" | tr -d "%")
        # Log results
        echo "$wf,$ks,$HASH_COVERAGE,$ROUND_COVERAGE" >> combined_sweep_results.txt
        echo "  Hash Coverage: $HASH_COVERAGE%, Round Coverage: $ROUND_COVERAGE%"
    done
done

echo "Combined sweep complete. Results saved to combined_sweep_results.txt"
# Display final results
cat combined_sweep_results.txt

