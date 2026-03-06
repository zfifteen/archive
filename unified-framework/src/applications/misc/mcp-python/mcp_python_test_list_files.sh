#!/bin/bash

BASE_URL="http://127.0.0.1:8000"
TARGET_DIR="/Users/velocityworks/IdeaProjects/unified-framework/results"

echo "Listing files in: $TARGET_DIR"
echo "================================"
echo ""

START_TIME=$(date +%s%N)

curl -s -X POST "$BASE_URL/tools/call" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"list_dir\",\"arguments\":{\"path\":\"$TARGET_DIR\"}}" | jq -r '.content[0].text'

END_TIME=$(date +%s%N)
ELAPSED=$((($END_TIME - $START_TIME) / 1000000))

echo ""
echo "================================"
echo "Runtime: ${ELAPSED}ms"