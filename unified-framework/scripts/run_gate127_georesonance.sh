#!/bin/bash
# Run Gate-127 geometric resonance factorization
# Implements PR-123 + PR-969 scaling integration
# Uses curvature drift & scaling laws for 127-bit challenge

set -e

echo "=========================================="
echo "  Gate-127 Geometric Resonance Factorization"
echo "  PR-123 Scaling Integration"
echo "=========================================="
echo ""

# Gate-127 challenge number
GATE_127="137524771864208156028430259349934309717"

# Expected factors (for validation)
EXPECTED_P="10508623501177419659"
EXPECTED_Q="13086849276577416863"

echo "Challenge number: $GATE_127"
echo "Bit length: 127"
echo ""
echo "Expected factors:"
echo "  p = $EXPECTED_P"
echo "  q = $EXPECTED_Q"
echo ""

# Build the project if needed
if [ ! -d "build/classes" ]; then
    echo "Building project..."
    gradle build -q
    echo ""
fi

echo "=========================================="
echo "Starting Factorization..."
echo "=========================================="
echo ""

# Run the factorization
gradle run --args="--factor $GATE_127" --console=plain

RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
    echo "=========================================="
    echo "  ✓ GATE-127 FACTORIZATION COMPLETE"
    echo "=========================================="
else
    echo "=========================================="
    echo "  ✗ FACTORIZATION FAILED"
    echo "=========================================="
fi

exit $RESULT
