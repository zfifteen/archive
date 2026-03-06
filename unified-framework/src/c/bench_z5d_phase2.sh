#!/bin/bash

# Record start time in nanoseconds
start=$(date +%s%N)

n=10
# Use string length comparison instead of integer comparison for large numbers
max_digits=1233
while [ ${#n} -le $max_digits ]; do
    # Record start time in milliseconds
    t_start=$(($(date +%s%N) / 1000000))

    # --- SCRIPT UPDATE ---
    # Calculate the correct exponent for the label.
    power=$((${#n} - 1))

    # Use a clear label that includes the power of 10.
    echo "----------------------------------------"
    echo "Test for k = 10^${power}"

    ./bin/z5d_prime_gen "$n" --stats

    # Record end time in milliseconds
    t_end=$(($(date +%s%N) / 1000000))

    # Calculate elapsed time in milliseconds
    elapsed_ms=$((t_end - t_start))

    echo "time: ${elapsed_ms} ms"

    n="${n}0"
done

# Record end time in nanoseconds
end=$(date +%s%N)

# Compute elapsed nanoseconds
elapsed_ns=$((end - start))

# Convert to milliseconds
elapsed_ms_total=$((elapsed_ns / 1000000))

echo "========================================"
echo "Total elapsed time: ${elapsed_ms_total} ms"