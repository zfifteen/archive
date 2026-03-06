#!/bin/bash
# Factor Recovery Demonstration Runner
# =====================================
# This script runs the verified factor recovery demonstration
# and saves the output to a timestamped log file.

set -e

echo "=========================================="
echo "  Factor Recovery Demonstration"
echo "=========================================="
echo ""
echo "Repository: zfifteen/z-sandbox"
echo "Method: Geodesic Validation Assault (GVA)"
echo ""

# Check for required dependencies
echo "Checking dependencies..."
if ! python3 -c "import mpmath, sympy" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip3 install mpmath sympy
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies found"
fi

echo ""
echo "Running factor recovery demonstration..."
echo ""

# Run the demo and save output
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOGFILE="factor_recovery_${TIMESTAMP}.log"

python3 python/demo_factor_recovery_verified.py 2>&1 | tee "$LOGFILE"

echo ""
echo "=========================================="
echo "  Demonstration Complete"
echo "=========================================="
echo ""
echo "Log saved to: $LOGFILE"
echo ""
echo "Summary:"
grep -E "(SUCCESS|FAILED)" "$LOGFILE" || echo "  Check log for details"
echo ""
