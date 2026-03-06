#!/bin/bash

# Script to run bulk analysis with diverse inputs for SHA-256 Classifier

# Array of diverse inputs
INPUTS=(
    # Incremental digit strings
    "1" "11" "111" "1111" "11111" "111111" "1111111" "11111111" "111111111"
    # Incremental alphabetical strings
    "a" "aa" "aaa" "aaaa" "aaaaa" "aaaaaa" "aaaaaaa" "aaaaaaaa" "aaaaaaaaa"
    # Mixed digit strings
    "12345678" "98765432" "11223344" "55667788" "12121212" "34343434"
    # Mixed alphabetical strings
    "abc" "ABC" "abcABC" "AbCdEfGh" "xyz" "XYZ"
    # Random strings (simulated by fixed diverse inputs)
    "rand1!@#" "rand2#$%" "rand3%^&" "rand4*()" "rand5-=" "rand6[]{"
    # Textual excerpts (short)
    "Call me Ishmael." "Some years ago" "Never mind how long" "I thought I would sail" "Watery part of world"
    # Empty and single char variations
    "" " " "!" "@" "#" "$" "%"
    # Mixed alphanumeric
    "abc123" "ABC789" "123xyz" "XYZ456" "a1b2c3" "X9Y8Z7"
    # Longer numerical sequences
    "1234567890123456" "9876543210987654" "1111222233334444"
)

# Run the analyzer with all inputs
./bin/sha256_bulk_analyzer "${INPUTS[@]}" > bulk_analysis_results.csv

echo "Bulk analysis completed. Results saved to bulk_analysis_results.csv"
