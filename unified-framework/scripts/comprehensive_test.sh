#!/bin/bash

# Comprehensive test script for precision bug fix
# Tests geodesic_z5d_search.c across multiple scales

echo "Comprehensive Precision Bug Fix Verification"
echo "=========================================="
echo

cd src/c

# Build the program
echo "Building geodesic_z5d_search with MPFR..."
gcc -I/opt/homebrew/include -o geodesic_z5d_search geodesic_z5d_search.c -L/opt/homebrew/lib -lgmp -lmpfr -lm -Xpreprocessor -fopenmp /opt/homebrew/Cellar/libomp/21.1.2/lib/libomp.dylib
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✅ Build successful"
echo

# Test 1: Small scale (baseline test)
echo "Test 1: Small scale (k ≈ 8686)"
echo "Expected: Distinct primes (baseline case)"
./geodesic_z5d_search 8686 3 | grep "Prime:"
echo

# Test 2: Medium scale 
echo "Test 2: Medium scale (k ≈ 10^6)"
echo "Expected: Distinct primes"
./geodesic_z5d_search 1000000 3 | grep "Prime:"
echo

# Test 3: Large scale
echo "Test 3: Large scale (k ≈ 10^12)"
echo "Expected: Distinct primes"
./geodesic_z5d_search 1000000000000 3 | grep "Prime:"
echo

# Test 4: Very large scale (precision threshold)
echo "Test 4: Very large scale (k ≈ 10^15)"
echo "Expected: Distinct primes (near original bug threshold)"
./geodesic_z5d_search 1000000000000000 3 | grep "Prime:"
echo

# Test 5: Extreme scale (original bug case)
echo "Test 5: Extreme scale (k = 37124508045065437) - ORIGINAL BUG CASE"
echo "Expected: Distinct primes (this was failing before fix)"
./geodesic_z5d_search 37124508045065437 3 | grep "Prime:"
echo

# Test 6: Ultra extreme scale
echo "Test 6: Ultra extreme scale (k ≈ 10^17)"
echo "Expected: Distinct primes (beyond original requirements)"
./geodesic_z5d_search 100000000000000000 3 | grep "Prime:"
echo

echo "Verification Complete!"
echo "If all tests show distinct prime values for consecutive k,"
echo "then the precision bug has been successfully fixed."