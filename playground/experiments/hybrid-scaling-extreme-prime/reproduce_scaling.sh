#!/bin/bash
# reproduce_scaling.sh
# Automated scaling benchmark script
# Switches between C and Python adapters based on scale_max

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPERIMENT_DIR="$SCRIPT_DIR"
SRC_DIR="$EXPERIMENT_DIR/src"
RESULTS_DIR="$EXPERIMENT_DIR/results"

# Default parameters
SCALE_MIN=20
SCALE_MAX=100
STEP=10
ADAPTER="auto"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --scale-min)
            SCALE_MIN="$2"
            shift 2
            ;;
        --scale-max)
            SCALE_MAX="$2"
            shift 2
            ;;
        --step)
            STEP="$2"
            shift 2
            ;;
        --adapter)
            ADAPTER="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --scale-min NUM    Minimum scale (default: 20)"
            echo "  --scale-max NUM    Maximum scale (default: 100)"
            echo "  --step NUM         Step size (default: 10)"
            echo "  --adapter TYPE     Adapter type: auto, c, python (default: auto)"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --scale-min 20 --scale-max 50"
            echo "  $0 --scale-max 1233 --adapter python"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "=========================================="
echo "Hybrid Scaling Architecture Benchmark"
echo "=========================================="
echo "Scale range: 10^$SCALE_MIN to 10^$SCALE_MAX"
echo "Step size: $STEP"
echo ""

# Automatic adapter selection based on scale_max
if [ "$ADAPTER" == "auto" ]; then
    if [ "$SCALE_MAX" -le 50 ]; then
        ADAPTER="c"
        echo "Auto-selected: C adapter (scale_max <= 50)"
    else
        ADAPTER="python"
        echo "Auto-selected: Python adapter (scale_max > 50)"
    fi
else
    echo "Using specified adapter: $ADAPTER"
fi

echo ""

# Run benchmark with selected adapter
if [ "$ADAPTER" == "c" ]; then
    # C adapter - compile first if needed
    C_ADAPTER="$SRC_DIR/z5d_adapter"
    C_SOURCE="$SRC_DIR/z5d_adapter.c"
    
    echo "Checking C adapter compilation..."
    if [ ! -f "$C_ADAPTER" ] || [ "$C_SOURCE" -nt "$C_ADAPTER" ]; then
        echo "Compiling C adapter..."
        # Check for GMP and MPFR
        if ! pkg-config --exists gmp mpfr 2>/dev/null; then
            echo "WARNING: GMP/MPFR not found via pkg-config"
            echo "Attempting compilation anyway..."
            gcc -O3 -o "$C_ADAPTER" "$C_SOURCE" -lgmp -lmpfr 2>/dev/null || {
                echo "ERROR: Failed to compile C adapter"
                echo "Please install GMP and MPFR libraries"
                echo "  Ubuntu/Debian: sudo apt-get install libgmp-dev libmpfr-dev"
                echo "  macOS: brew install gmp mpfr"
                exit 1
            }
        else
            gcc -O3 $(pkg-config --cflags --libs gmp mpfr) -o "$C_ADAPTER" "$C_SOURCE"
        fi
        echo "Compilation successful!"
    fi
    
    echo ""
    echo "Running C adapter benchmark..."
    echo "Scale,Time(ms),Predicted,RelError,Log10Error" > "$RESULTS_DIR/scaling_benchmark.csv"
    
    for scale in $(seq $SCALE_MIN $STEP $SCALE_MAX); do
        echo -n "Testing scale 10^$scale... "
        start_time=$(date +%s%3N)
        output=$("$C_ADAPTER" "$scale" 2>&1)
        end_time=$(date +%s%3N)
        elapsed=$((end_time - start_time))
        
        # Extract predicted value from output
        predicted=$(echo "$output" | grep "Predicted nth prime" | awk '{print $NF}')
        
        echo "$scale,$elapsed,$predicted,0.0,-inf" >> "$RESULTS_DIR/scaling_benchmark.csv"
        echo "${elapsed}ms"
    done
    
elif [ "$ADAPTER" == "python" ]; then
    # Python adapter
    PYTHON_ADAPTER="$EXPERIMENT_DIR/z5d_adapter.py"
    
    echo "Running Python adapter benchmark..."
    echo "This may take some time for extreme scales..."
    echo ""
    
    start_time=$(date +%s%3N)
    python3 "$PYTHON_ADAPTER" --test-convergence \
        --start "$SCALE_MIN" \
        --end "$SCALE_MAX" \
        --step "$STEP" \
        > "$RESULTS_DIR/scaling_output.txt"
    end_time=$(date +%s%3N)
    total_time=$((end_time - start_time))
    
    echo "Benchmark completed in ${total_time}ms"
    
    # Parse results
    echo "Parsing results..."
    grep "^10\^" "$RESULTS_DIR/scaling_output.txt" > "$RESULTS_DIR/scaling_benchmark.txt" || true
    
else
    echo "ERROR: Unknown adapter type: $ADAPTER"
    exit 1
fi

echo ""
echo "=========================================="
echo "Benchmark Complete!"
echo "=========================================="
echo "Results saved to: $RESULTS_DIR/"
echo ""

# Show summary if available
if [ -f "$RESULTS_DIR/scaling_benchmark.csv" ]; then
    echo "Summary (CSV format):"
    head -n 1 "$RESULTS_DIR/scaling_benchmark.csv"
    tail -n 5 "$RESULTS_DIR/scaling_benchmark.csv"
elif [ -f "$RESULTS_DIR/scaling_benchmark.txt" ]; then
    echo "Summary:"
    head -n 5 "$RESULTS_DIR/scaling_benchmark.txt"
fi

echo ""
echo "Expected performance (from hypothesis):"
echo "  10^20:   ~75ms"
echo "  10^1233: ~115ms"
echo ""
