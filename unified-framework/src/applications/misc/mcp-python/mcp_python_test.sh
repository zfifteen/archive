#!/bin/bash

BASE_URL="http://127.0.0.1:8000"
START_TIME=$(date +%s%N)

echo "Testing MCP Python Server"
echo "========================="
echo ""

# Test 1: Initialize
echo "Test 1: Initialize"
curl -s -X POST "$BASE_URL/initialize" | jq .
echo ""

# Test 2: List Tools
echo "Test 2: List Tools"
curl -s -X GET "$BASE_URL/tools/list" | jq '.tools[].name'
echo ""

# Test 3: Bash Tool
echo "Test 3: Bash Tool - echo test"
curl -s -X POST "$BASE_URL/tools/call" \
  -H "Content-Type: application/json" \
  -d '{"name":"bash","arguments":{"command":"echo Hello from bash"}}' | jq .
echo ""

# Test 4: Python Tool
echo "Test 4: Python Tool - simple calculation"
curl -s -X POST "$BASE_URL/tools/call" \
  -H "Content-Type: application/json" \
  -d '{"name":"python","arguments":{"code":"print(2 + 2)"}}' | jq .
echo ""

# Test 5: Write File
echo "Test 5: Write File"
curl -s -X POST "$BASE_URL/tools/call" \
  -H "Content-Type: application/json" \
  -d '{"name":"write_file","arguments":{"path":"/tmp/test_mcp.txt","content":"Test content from MCP"}}' | jq .
echo ""

# Test 6: Read File
echo "Test 6: Read File"
curl -s -X POST "$BASE_URL/tools/call" \
  -H "Content-Type: application/json" \
  -d '{"name":"read_file","arguments":{"path":"/tmp/test_mcp.txt"}}' | jq .
echo ""

# Test 7: List Directory
echo "Test 7: List Directory"
curl -s -X POST "$BASE_URL/tools/call" \
  -H "Content-Type: application/json" \
  -d '{"name":"list_dir","arguments":{"path":"/tmp"}}' | jq -r '.content[0].text' | head -10
echo "..."
echo ""

# Test 8: GitHub CLI (may fail if not authenticated)
echo "Test 8: GitHub CLI - version"
curl -s -X POST "$BASE_URL/tools/call" \
  -H "Content-Type: application/json" \
  -d '{"name":"gh","arguments":{"args":"--version"}}' | jq .
echo ""

# Cleanup
rm -f /tmp/test_mcp.txt

END_TIME=$(date +%s%N)
ELAPSED=$((($END_TIME - $START_TIME) / 1000000))

echo "========================="
echo "All tests completed"
echo "Total runtime: ${ELAPSED}ms"