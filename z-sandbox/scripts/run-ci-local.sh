#!/bin/bash
#
# Local CI Runner for z-sandbox
# Runs all CI checks locally before pushing to GitHub
#
# Usage: ./run-ci-local.sh [--workflow NAME] [--verbose]
#

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
WORKFLOW=""
VERBOSE=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --workflow)
      WORKFLOW="$2"
      shift 2
      ;;
    -w)
      WORKFLOW="$2"
      shift 2
      ;;
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--workflow NAME] [--verbose]"
      echo ""
      echo "Options:"
      echo "  --workflow, -w NAME   Run specific workflow (charter, gradle, geometric, wiener, ingest)"
      echo "  --verbose, -v         Show detailed output"
      echo "  --help, -h            Show this help"
      echo ""
      echo "Available workflows:"
      echo "  charter     - Mission Charter compliance validation"
      echo "  gradle      - Build and test Java components"
      echo "  geometric   - Verify geometric resonance artifacts"
      echo "  wiener      - Run Wiener attack tests"
      echo "  ingest      - Ingest loose markdown (dry-run)"
      echo "  all         - Run all workflows (default)"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Default to all if no workflow specified
if [[ -z "$WORKFLOW" ]]; then
  WORKFLOW="all"
fi

echo -e "${BLUE}=================================================="
echo "Local CI Runner for z-sandbox"
echo "==================================================${NC}"
echo ""

FAILED_WORKFLOWS=()
PASSED_WORKFLOWS=()

# Function to run a workflow job
run_workflow() {
  local name=$1
  local description=$2
  shift 2

  echo -e "${BLUE}Running: $description${NC}"
  echo "---"

  if $VERBOSE; then
    if "$@"; then
      echo -e "${GREEN}✓ PASSED: $name${NC}"
      PASSED_WORKFLOWS+=("$name")
      return 0
    else
      echo -e "${RED}✗ FAILED: $name${NC}"
      FAILED_WORKFLOWS+=("$name")
      return 1
    fi
  else
    if OUTPUT=$("$@" 2>&1); then
      echo -e "${GREEN}✓ PASSED: $name${NC}"
      PASSED_WORKFLOWS+=("$name")
      return 0
    else
      echo -e "${RED}✗ FAILED: $name${NC}"
      echo "$OUTPUT"
      FAILED_WORKFLOWS+=("$name")
      return 1
    fi
  fi
}

# Charter Compliance Workflow
run_charter() {
  echo -e "\n${YELLOW}[1/5] Charter Compliance Validation${NC}"
  echo "=================================================="

  # Get changed markdown files (compared to main or last commit)
  if git rev-parse --verify main >/dev/null 2>&1; then
    CHANGED_FILES=$(git diff --name-only main...HEAD | grep '\.md$' || true)
  else
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD | grep '\.md$' || true)
  fi

  if [[ -z "$CHANGED_FILES" ]]; then
    echo "No markdown files changed. Skipping validation."
    PASSED_WORKFLOWS+=("charter")
    return 0
  fi

  ALL_PASSED=true
  CHECKED_COUNT=0

  for file in $CHANGED_FILES; do
    # Skip non-deliverables
    if [[ ! "$file" =~ (_SUMMARY|_REPORT|_IMPLEMENTATION|_GUIDE|PLAN) ]] && \
       [[ "$file" != "MISSION_CHARTER.md" ]]; then
      continue
    fi

    # Skip templates
    if [[ "$file" =~ docs/templates/ ]]; then
      continue
    fi

    echo ""
    echo "Validating: $file"
    if python3 tools/validate_charter.py "$file" --author="Local CI" 2>&1; then
      echo -e "${GREEN}✓ $file is compliant${NC}"
    else
      echo -e "${RED}✗ $file is NOT compliant${NC}"
      ALL_PASSED=false
    fi
    CHECKED_COUNT=$((CHECKED_COUNT + 1))
  done

  echo ""
  echo "Files checked: $CHECKED_COUNT"

  if [[ "$CHECKED_COUNT" -eq 0 ]]; then
    echo "No deliverables to validate"
    PASSED_WORKFLOWS+=("charter")
    return 0
  fi

  if $ALL_PASSED; then
    PASSED_WORKFLOWS+=("charter")
    return 0
  else
    FAILED_WORKFLOWS+=("charter")
    return 1
  fi
}

# Gradle Build Workflow
run_gradle() {
  echo -e "\n${YELLOW}[2/5] Gradle Build & Test${NC}"
  echo "=================================================="

  run_workflow "gradle" "Build and test Java components" \
    ./gradlew -q test jacocoTestReport
}

# Geometric Resonance Workflow
run_geometric() {
  echo -e "\n${YELLOW}[3/5] Geometric Resonance Artifact Verification${NC}"
  echo "=================================================="

  # Check if artifacts exist
  if [[ ! -d "results/geometric_resonance_127bit" ]]; then
    echo "No geometric resonance artifacts found. Skipping."
    PASSED_WORKFLOWS+=("geometric")
    return 0
  fi

  # Run all verification steps
  local all_passed=true

  echo "Checking checksums..."
  if (cd results/geometric_resonance_127bit && sha256sum -c checksums.txt 2>&1); then
    echo -e "${GREEN}✓ Checksums verified${NC}"
  else
    echo -e "${RED}✗ Checksum verification failed${NC}"
    all_passed=false
  fi

  echo ""
  echo "Verifying factors..."
  if python3 python/verify_factors_127bit.py 2>&1; then
    echo -e "${GREEN}✓ Factor verification passed${NC}"
  else
    echo -e "${RED}✗ Factor verification failed${NC}"
    all_passed=false
  fi

  echo ""
  echo "Checking candidates file..."
  if grep -q "10508623501177419659" results/geometric_resonance_127bit/candidates.txt && \
     grep -q "13086849276577416863" results/geometric_resonance_127bit/candidates.txt; then
    echo -e "${GREEN}✓ Both factors found in candidates${NC}"
  else
    echo -e "${RED}✗ Factors missing from candidates${NC}"
    all_passed=false
  fi

  echo ""
  echo "Verifying metrics..."
  if python3 -c "
import json
with open('results/geometric_resonance_127bit/metrics.json') as f:
    m = json.load(f)
assert m['run_info']['success'] == True
assert m['run_info']['factors_found']['p'] == '10508623501177419659'
assert m['run_info']['factors_found']['q'] == '13086849276577416863'
print('✓ Metrics validation passed')
" 2>&1; then
    echo -e "${GREEN}✓ Metrics verified${NC}"
  else
    echo -e "${RED}✗ Metrics verification failed${NC}"
    all_passed=false
  fi

  echo ""
  echo "Running test suite..."
  if python3 tests/test_geometric_resonance_127bit.py 2>&1; then
    echo -e "${GREEN}✓ Tests passed${NC}"
  else
    echo -e "${RED}✗ Tests failed${NC}"
    all_passed=false
  fi

  if $all_passed; then
    PASSED_WORKFLOWS+=("geometric")
    return 0
  else
    FAILED_WORKFLOWS+=("geometric")
    return 1
  fi
}

# Wiener Attack Workflow
run_wiener() {
  echo -e "\n${YELLOW}[4/5] Wiener Attack Tests${NC}"
  echo "=================================================="

  # Check if files exist
  if [[ ! -f "python/wiener_attack.py" ]] || [[ ! -f "tests/test_wiener_attack.py" ]]; then
    echo "Wiener attack files not found. Skipping."
    PASSED_WORKFLOWS+=("wiener")
    return 0
  fi

  run_workflow "wiener" "Run Wiener attack tests" \
    env PYTHONPATH=python python -m pytest -q tests/test_wiener_attack.py
}

# Ingest Workflow (dry-run)
run_ingest() {
  echo -e "\n${YELLOW}[5/5] Markdown Ingest (dry-run)${NC}"
  echo "=================================================="

  # Detect new root-level markdown files
  if git rev-parse --verify main >/dev/null 2>&1; then
    NEW_FILES=$(git diff --name-status main...HEAD | awk '$1 ~ /^A/ && $2 !~ /\// && $2 ~ /\.md$/ {print $2}' | tr '\n' ' ')
  else
    NEW_FILES=$(git diff --name-status HEAD~1 HEAD | awk '$1 ~ /^A/ && $2 !~ /\// && $2 ~ /\.md$/ {print $2}' | tr '\n' ' ')
  fi

  if [[ -z "${NEW_FILES// }" ]]; then
    echo "No new root-level markdown files. Skipping."
    PASSED_WORKFLOWS+=("ingest")
    return 0
  fi

  echo "Files to ingest: $NEW_FILES"
  run_workflow "ingest" "Ingest loose markdown (dry-run)" \
    python src/python/docs_ingest.py --dry-run $NEW_FILES
}

# Run workflows based on selection
case $WORKFLOW in
  charter)
    run_charter
    ;;
  gradle)
    run_gradle
    ;;
  geometric)
    run_geometric
    ;;
  wiener)
    run_wiener
    ;;
  ingest)
    run_ingest
    ;;
  all)
    run_charter || true
    run_gradle || true
    run_geometric || true
    run_wiener || true
    run_ingest || true
    ;;
  *)
    echo -e "${RED}Unknown workflow: $WORKFLOW${NC}"
    echo "Use --help to see available workflows"
    exit 1
    ;;
esac

# Summary
echo ""
echo -e "${BLUE}=================================================="
echo "CI Summary"
echo "==================================================${NC}"
echo ""
echo -e "${GREEN}Passed: ${#PASSED_WORKFLOWS[@]}${NC}"
for workflow in "${PASSED_WORKFLOWS[@]}"; do
  echo -e "  ${GREEN}✓${NC} $workflow"
done

if [[ ${#FAILED_WORKFLOWS[@]} -gt 0 ]]; then
  echo ""
  echo -e "${RED}Failed: ${#FAILED_WORKFLOWS[@]}${NC}"
  for workflow in "${FAILED_WORKFLOWS[@]}"; do
    echo -e "  ${RED}✗${NC} $workflow"
  done
  echo ""
  echo -e "${RED}Some CI checks failed. Please fix before pushing.${NC}"
  exit 1
else
  echo ""
  echo -e "${GREEN}All CI checks passed! ✓${NC}"
  echo "Safe to push to GitHub."
  exit 0
fi

