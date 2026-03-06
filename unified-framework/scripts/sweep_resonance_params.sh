#!/bin/bash
# Parameter sweep script for resonance parameters
# Used when initial factorization attempt is not successful

set -e

# Default values
N=""
K_MIN=""
K_MAX=""
T_MIN=""
T_MAX=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --N)
            N="$2"
            shift 2
            ;;
        --k-min)
            K_MIN="$2"
            shift 2
            ;;
        --k-max)
            K_MAX="$2"
            shift 2
            ;;
        --T-min)
            T_MIN="$2"
            shift 2
            ;;
        --T-max)
            T_MAX="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$N" ]; then
    echo "Error: --N parameter is required"
    exit 1
fi

echo "========================================="
echo "  Resonance Parameter Sweep"
echo "========================================="
echo ""
echo "Target number: $N"
echo "k range: [$K_MIN, $K_MAX]"
echo "T range: [$T_MIN, $T_MAX]"
echo ""

# Build the project
echo "Building project..."
./gradlew build -q

echo ""
echo "Running parameter sweep..."
echo ""

# Note: This is a placeholder implementation
# In production, this would iterate through parameter combinations
# and attempt factorization with each set

echo "Attempting factorization with base parameters..."
./gradlew run --args="--factor $N" --quiet

echo ""
echo "Parameter sweep complete."
echo ""
echo "Note: Full parameter sweep implementation requires"
echo "additional iteration logic over k and T ranges."
