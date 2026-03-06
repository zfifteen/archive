#!/bin/bash

#
# TG-SHA: Vulnerability Demonstration Script
# ==========================================
#
# Demonstrates TG-SHA vulnerability when k* parameter is exposed
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Change to the TG-SHA directory
cd "$(dirname "$0")"

echo -e "${CYAN}TG-SHA: Vulnerability Demonstration${NC}"
echo "======================================"
echo ""

# Build if needed
if [ ! -f "bin/tg_sha_demo" ]; then
    echo "Building TG-SHA..."
    make clean && make
    echo ""
fi

echo -e "${GREEN}SECURE MODE (k* hidden):${NC}"
echo "------------------------"
./bin/tg_sha_demo --secure --message "Test Message"
echo ""

echo -e "${RED}BROKEN MODE (k* exposed):${NC}"
echo "-------------------------"
./bin/tg_sha_demo --broken --message "Test Message"
echo ""

echo -e "${YELLOW}SIDE-BY-SIDE COMPARISON:${NC}"
echo "------------------------"
./bin/tg_sha_demo --both --predict 8
echo ""

echo -e "${CYAN}Summary:${NC}"
echo "• Secure mode: Random-like, unpredictable"
echo "• Broken mode: Geometric patterns when k* exposed"
echo "• Vulnerability: k* acts like Dual_EC_DRBG 'd' parameter"