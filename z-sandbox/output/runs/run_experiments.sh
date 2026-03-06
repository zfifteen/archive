#!/bin/bash
# Script to execute and log geometric resonance factorization runs

RUNS_DIR="/home/runner/work/z-sandbox/z-sandbox/runs"
N="137524771864208156028430259349934309717"

# Function to execute a run and log results
run_experiment() {
    local run_id="$1"
    local description="$2"
    local args="$3"
    
    echo "========================================"
    echo "Run $run_id: $description"
    echo "========================================"
    echo "Arguments: $args"
    echo ""
    
    local start_time=$(date +%s)
    local log_file="${RUNS_DIR}/run_${run_id}.log"
    
    # Execute the factorization
    cd /home/runner/work/z-sandbox/z-sandbox
    ./gradlew run --args="$N $args" > "$log_file" 2>&1
    local exit_code=$?
    
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    
    echo "Exit code: $exit_code"
    echo "Runtime: ${elapsed}s"
    echo ""
    
    # Check for factors in output
    if grep -q "FOUND:" "$log_file"; then
        echo "✓ FACTORS FOUND!"
        grep -A 2 "FOUND:" "$log_file"
        result="SUCCESS"
    else
        echo "✗ No factors found"
        result="No factors"
    fi
    
    echo ""
    echo "Log saved to: $log_file"
    echo ""
    
    # Return elapsed time and result
    echo "${elapsed}s|${result}"
}

# Export function for use in subshells
export -f run_experiment
export RUNS_DIR
export N
