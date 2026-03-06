#!/usr/bin/env bash
#
# Run the Official 127-bit Geofac Challenge
#
# This script runs the 127-bit factorization challenge with optimized
# shell-exclusion pruning configuration.
#
# Expected runtime on 64-core AMD EPYC 7J13: 4.8-6.2 minutes
# (Previous best without shell pruning: ~19 minutes)
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  127-bit Geofac Challenge Runner${NC}"
echo -e "${BLUE}  Shell-Exclusion Pruning Enabled${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
    echo -e "${YELLOW}⚠️  Python 3.8+ required. Found: Python $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Check if dependencies are installed
if ! python3 -c "import numpy" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pip install -e . || {
        echo -e "${YELLOW}⚠️  Failed to install dependencies${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Run the challenge
echo -e "${BLUE}Starting 127-bit challenge...${NC}"
echo ""

python3 cli/challenge_127.py "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Challenge completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}  Challenge failed or interrupted${NC}"
    echo -e "${YELLOW}  Exit code: $EXIT_CODE${NC}"
    echo -e "${YELLOW}========================================${NC}"
fi

exit $EXIT_CODE
