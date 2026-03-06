#!/bin/bash
# run_benchmark.sh - Standard benchmark suite for LogLog MPFR library
# This script builds and runs the benchmark suite without requiring arguments

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  LogLog MPFR Benchmark Runner${NC}"
echo -e "${BLUE}=====================================${NC}"
echo

# Check if benchmark binary exists
if [ ! -f "benchmark_loglog" ]; then
    echo -e "${YELLOW}Benchmark binary not found. Building...${NC}"
    make benchmark_loglog
    echo
fi

# Run the benchmark
echo -e "${GREEN}Starting benchmark suite...${NC}"
echo
./benchmark_loglog

# Save results to file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="benchmark_results_${TIMESTAMP}.txt"

echo
echo -e "${GREEN}Saving results to ${RESULTS_FILE}...${NC}"
./benchmark_loglog > "${RESULTS_FILE}" 2>&1

echo -e "${GREEN}Benchmark complete!${NC}"
echo -e "${GREEN}Results saved to: ${RESULTS_FILE}${NC}"
echo
