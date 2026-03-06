#!/bin/bash
# RSA-260 Geometric Factorization Wrapper Script
#
# This script provides a convenient interface to run RSA-260 factorization
# with proper logging and parameter management.
#
# Usage:
#   ./scripts/run_rsa260.sh [options]
#
# Examples:
#   ./scripts/run_rsa260.sh --dps 1000 --k 0.3 --window 0.05
#   ./scripts/run_rsa260.sh --dps 2000 --k 0.29 --step 0.00001 --m0 0.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DPS=1000
K=0.3
M0="auto"
WINDOW=0.05
STEP=0.0001
NEIGHBOR_RADIUS=2
PRP_ROUNDS=32
LOGDIR="logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOGFILE="${LOGDIR}/rsa260_run_${TIMESTAMP}.log"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dps)
            DPS="$2"
            shift 2
            ;;
        --k)
            K="$2"
            shift 2
            ;;
        --m0)
            M0="$2"
            shift 2
            ;;
        --window)
            WINDOW="$2"
            shift 2
            ;;
        --step)
            STEP="$2"
            shift 2
            ;;
        --neighbor-radius|--neighbor_radius)
            NEIGHBOR_RADIUS="$2"
            shift 2
            ;;
        --prp-rounds|--prp_rounds)
            PRP_ROUNDS="$2"
            shift 2
            ;;
        --logdir)
            LOGDIR="$2"
            shift 2
            ;;
        --help|-h)
            echo "RSA-260 Geometric Factorization"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --dps <int>              Decimal precision (≥1000, default: 1000)"
            echo "  --k <float>              Wave number parameter (default: 0.3)"
            echo "  --m0 <float>             Center m value (default: auto)"
            echo "  --window <float>         Window width for m sampling (default: 0.05)"
            echo "  --step <float>           Step size for fractional m (default: 0.0001)"
            echo "  --neighbor-radius <int>  Check ±radius around candidates (default: 2)"
            echo "  --prp-rounds <int>       Miller-Rabin rounds (default: 32)"
            echo "  --logdir <path>          Log directory (default: logs)"
            echo "  --help, -h               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --dps 1000 --k 0.3 --window 0.05"
            echo "  $0 --dps 2000 --k 0.29 --step 0.00001 --m0 0.0"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create log directory
mkdir -p "$LOGDIR"

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         RSA-260 Geometric Factorization Runner                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  DPS:             $DPS"
echo "  k:               $K"
echo "  m0:              $M0"
echo "  Window:          ±$WINDOW"
echo "  Step:            $STEP"
echo "  Neighbor radius: ±$NEIGHBOR_RADIUS"
echo "  PRP rounds:      $PRP_ROUNDS"
echo "  Log file:        $LOGFILE"
echo ""

# Build command
CMD="python3 python/rsa260_repro.py --dps $DPS --k $K --window $WINDOW --step $STEP --neighbor_radius $NEIGHBOR_RADIUS --prp_rounds $PRP_ROUNDS"

if [ "$M0" != "auto" ]; then
    CMD="$CMD --m0 $M0"
fi

# Run and capture output
echo -e "${YELLOW}Starting factorization...${NC}"
echo ""

# Use tee to write to both stdout and log file
if eval "$CMD" 2>&1 | tee "$LOGFILE"; then
    EXIT_CODE=${PIPESTATUS[0]}
else
    EXIT_CODE=$?
fi

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                       SUCCESS!                                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    No factor found                             ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo -e "${BLUE}Log saved to: ${LOGFILE}${NC}"
echo ""

exit $EXIT_CODE
