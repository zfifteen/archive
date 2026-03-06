# Smoke test script for geometric factorization reproduction
# Compiles the C program and runs a small-scale test, logging output to a timestamped file in logs/

set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate timestamp for log file
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
logfile="logs/smoke_test_$timestamp.log"

# Compile the program using Makefile
echo "Compiling the program..." >> "$logfile"
make >> "$logfile" 2>&1

# Run a small-scale test: 1 sample (adjust arguments as needed)
echo "Running smoke test with 1 sample..." >> "$logfile"
./bin/geometric_factorization_repro 1 >> "$logfile" 2>&1

# Check for success (look for "SUCCESS:" in log)
if grep -q "SUCCESS:" "$logfile"; then
    echo "Smoke test PASSED: Factorization completed successfully." >> "$logfile"
    echo "Log saved to $logfile"
else
    echo "Smoke test FAILED: No successful factorization found." >> "$logfile"
    echo "Check log: $logfile"
    exit 1
fi