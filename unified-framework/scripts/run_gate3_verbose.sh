#!/bin/bash
# Run Gate-127 factorization with verbose logging
# Note: "gate3" is a legacy naming convention; this runs Gate-127
# Uses PR-123 scaling integration

set -e

echo "========================================="
echo "  Gate-127 Factorization (Verbose Mode)"
echo "  PR-123 Scaling Integration"
echo "========================================="
echo ""

GATE_127="137524771864208156028430259349934309717"

# Build the project
echo "Building project..."
./gradlew build -q

echo ""
echo "Starting factorization attempt..."
echo ""

# Run the factorization
./gradlew run --args="--factor $GATE_127" --quiet

echo ""
echo "Factorization complete."
