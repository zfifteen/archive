#!/bin/bash

# Record start time in nanoseconds
start=$(date +%s%N)

# Configuration: find 10 primes at this digit scale
max_digits=617
num_primes=100

# Generate the base number (10^(max_digits-1))
n="1"
for ((i=1; i<max_digits; i++)); do
    n="${n}0"
done

echo "========================================"
echo "Finding ${num_primes} primes at scale 10^$((max_digits-1)) (${max_digits} digits)"
echo "Base number: ${n}"
echo "========================================"

# Find the specified number of primes at this scale
for ((prime_count=1; prime_count<=num_primes; prime_count++)); do
    # Record start time in milliseconds
    t_start=$(($(date +%s%N) / 1000000))

    echo "----------------------------------------"
    echo "Prime ${prime_count}/${num_primes} at scale 10^$((max_digits-1))"

    ./bin/z5d_prime_gen "$n" --stats

    # Record end time in milliseconds
    t_end=$(($(date +%s%N) / 1000000))

    # Calculate elapsed time in milliseconds
    elapsed_ms=$((t_end - t_start))

    echo "Prime ${prime_count} generation time: ${elapsed_ms} ms"

    # Increment the base number slightly for the next search
    # This ensures we find different primes in the same scale
    n="${n}1"
done

# Record end time in nanoseconds
end=$(date +%s%N)

# Compute elapsed nanoseconds
elapsed_ns=$((end - start))

# Convert to milliseconds
elapsed_ms_total=$((elapsed_ns / 1000000))

echo "========================================"
echo "Found ${num_primes} primes at ${max_digits}-digit scale"
echo "Total elapsed time: ${elapsed_ms_total} ms"
echo "Average time per prime: $((elapsed_ms_total / num_primes)) ms"