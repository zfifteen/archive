#!/bin/bash
# Script to sweep k_star values for Appetizer Demo
# ===================================================
# This script tests various k_star values to observe impact on coverage.

echo "Starting k_star sweep for Appetizer Demo..."
echo "Results will be logged to k_star_sweep_results.txt"

# List of k_star values to test
K_STARS=(0.02 0.03 0.04 0.05 0.06 0.07 0.08)

# Clear previous results
echo "k_star,Hash_Coverage (%),Round_Coverage (%)" > k_star_sweep_results.txt

# Reset width_factor to original value
sed -i.bak "s/double width_factor = [0-9.]*;/double width_factor = 0.155;/" sha256_appetizer.c

for ks in "${K_STARS[@]}"; do
    echo "Testing k_star = $ks"
    # Update k_star in the source code
    sed -i.bak "s/double k_star = [0-9.]*;/double k_star = $ks;/" sha256_appetizer.c
    # Force rebuild by cleaning first
    make clean
    make
    # Run the demo and capture output
    OUTPUT=$(./sha256_appetizer)
    # Extract coverage percentages from output
    HASH_COVERAGE=$(echo "$OUTPUT" | grep "Summary for Initial Hash Values" | grep -o "[0-9.]*%" | tr -d "%")
    ROUND_COVERAGE=$(echo "$OUTPUT" | grep "Summary for Round Constants" | grep -o "[0-9.]*%" | tr -d "%")
    # Log results
    echo "$ks,$HASH_COVERAGE,$ROUND_COVERAGE" >> k_star_sweep_results.txt
    echo "  Hash Coverage: $HASH_COVERAGE%, Round Coverage: $ROUND_COVERAGE%"
done

echo "Sweep complete. Results saved to k_star_sweep_results.txt"
# Display final results
cat k_star_sweep_results.txt

