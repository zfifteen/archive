#!/bin/bash

# Prime Grid Plot - Demonstration Script
# =====================================
# 
# Demonstrates the C implementation of prime_grid_plot.py
# Shows various features and scales of the prime grid plotting tool.
#
# @file demo.sh
# @version 1.0

set -e

echo "Prime Grid Plot - C Implementation Demonstration"
echo "=============================================="
echo ""

# Check if executable exists
EXECUTABLE="./bin/prime_grid_plot"
if [ ! -x "$EXECUTABLE" ]; then
    echo "Building prime_grid_plot executable..."
    make
    echo ""
fi

# Create output directory
mkdir -p demo_output

echo "Demo 1: Small scale grid (10^3) - Dense sampling"
echo "------------------------------------------------"
$EXECUTABLE --scale "10^3" \
    --x-start 1 --x-end 3 \
    --y-start 0 --y-end 1000 \
    --y-step 1 \
    --out-csv demo_output/small_grid.csv \
    --verbose

echo ""
echo "Demo 2: Medium scale grid (10^6) - Random probes"
echo "------------------------------------------------"
$EXECUTABLE --scale "10^6" \
    --x-start 1 --x-end 5 \
    --y-start 0 --y-end 100000 \
    --probes 200 \
    --seed 12345 \
    --mr-rounds 20 \
    --out-csv demo_output/medium_grid.csv \
    --verbose

echo ""
echo "Demo 3: Large scale grid (10^9) - Sparse sampling"
echo "-------------------------------------------------"
$EXECUTABLE --scale "10^9" \
    --x-start 1 --x-end 2 \
    --y-start 0 --y-end 10000000 \
    --probes 100 \
    --seed 54321 \
    --mr-rounds 24 \
    --out-csv demo_output/large_grid.csv \
    --verbose

echo ""
echo "Demo 4: Ultra scale (10^12) - Very sparse sampling"
echo "-------------------------------------------------"
$EXECUTABLE --scale "10^12" \
    --x-start 1 --x-end 2 \
    --y-start 0 --y-end 1000000000000 \
    --probes 50 \
    --seed 98765 \
    --mr-rounds 30 \
    --out-csv demo_output/ultra_grid.csv \
    --verbose

echo ""
echo "Demonstration complete!"
echo "======================"
echo ""
echo "Generated CSV files:"
ls -la demo_output/*.csv

echo ""
echo "CSV file statistics:"
for csv_file in demo_output/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "$(basename $csv_file): $(wc -l < $csv_file) lines"
    fi
done

echo ""
echo "Sample data from small_grid.csv:"
echo "x,y,N,is_prime"
head -10 demo_output/small_grid.csv | tail -9

echo ""
echo "Note: For visualization, process the CSV files with external plotting tools."
echo "The C implementation focuses on computation and data generation."
echo ""
echo "Example Python visualization command:"
echo "  import pandas as pd; import matplotlib.pyplot as plt"
echo "  df = pd.read_csv('demo_output/small_grid.csv')"
echo "  primes = df[df['is_prime'] == 1]"
echo "  plt.scatter(primes['x'], primes['y']); plt.show()"