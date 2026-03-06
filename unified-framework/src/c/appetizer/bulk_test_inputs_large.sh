#!/bin/bash

# Script to run bulk analysis with a large, diverse set of inputs for SHA-256 Classifier

# Array of diverse inputs (expanded to 500+ through loops and patterns)
INPUTS=()

# Incremental digit strings (1 to 50 repetitions)
for i in {1..50}; do
    INPUTS+=("$(printf '1%.0s' {1..$i})")
done

# Incremental alphabetical strings (a to z, repeated 1 to 20 times)
for i in {1..20}; do
    INPUTS+=("$(printf 'a%.0s' {1..$i})")
done

# Mixed digit strings (various patterns)
for i in {1..10}; do
    INPUTS+=("$(printf '%d' $i)$(printf '%d%.0s' $i {1..7})")
    INPUTS+=("$(printf '%d' $i)$(printf '%d%.0s' $((10-$i)) {1..7})")
done

# Mixed alphabetical strings (various patterns)
for char in {a..z}; do
    INPUTS+=("$char")
    INPUTS+=("$char$char")
    INPUTS+=("$char$(echo $char | tr '[:lower:]' '[:upper:]')")
done

# Random-like strings (simulated by fixed diverse inputs with symbols)
for i in {1..50}; do
    INPUTS+=("rand$i!@#")
    INPUTS+=("rand$i#$%")
done

# Textual excerpts and variations (short phrases with repetition)
TEXTS=("Call me Ishmael." "Some years ago" "Never mind how long" "I thought I would sail" "Watery part of world")
for text in "${TEXTS[@]}"; do
    INPUTS+=("$text")
    INPUTS+=("$text $text")
done

# Empty and single char variations (including special chars)
INPUTS+=("")
for char in ' ' '!' '@' '#' '$' '%' '^' '&' '*' '(' ')' '-' '=' '+' '[' ']' '{' '}' ';' ':' ',' '.' '/'; do
    INPUTS+=("$char")
    INPUTS+=("$char$char")
done

# Mixed alphanumeric (various combinations)
for i in {1..20}; do
    INPUTS+=("abc$i")
    INPUTS+=("ABC$i")
    INPUTS+=("$i xyz")
    INPUTS+=("$i XYZ")
done

# Longer numerical sequences and patterns
for i in {1..10}; do
    INPUTS+=("1234567890123456$i")
    INPUTS+=("9876543210987654$i")
    INPUTS+=("1111222233334444$i")
done

# Additional filler to reach 500+ if needed (repeating patterns)
for i in {1..50}; do
    INPUTS+=("test$i")
    INPUTS+=("input$i")
done

# Run the analyzer with all inputs
./bin/sha256_bulk_analyzer "${INPUTS[@]}" > bulk_analysis_results_large.csv

echo "Bulk analysis completed. Results saved to bulk_analysis_results_large.csv"
echo "Total inputs processed: ${#INPUTS[@]}"
