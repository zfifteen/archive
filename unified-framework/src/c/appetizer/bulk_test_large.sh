#!/bin/bash

# Script to run bulk analysis with 5000 inputs for SHA-256 Classifier

# Read inputs from file into an array using a while loop to avoid mapfile dependency
INPUTS=()
while IFS= read -r line; do
    INPUTS+=("$line")
done < large_input_set.txt

# Run the analyzer with all inputs
./bin/sha256_bulk_analyzer "${INPUTS[@]}" > bulk_analysis_results_5000.csv

echo "Bulk analysis completed. Results saved to bulk_analysis_results_5000.csv"
echo "Total inputs processed: ${#INPUTS[@]}"
