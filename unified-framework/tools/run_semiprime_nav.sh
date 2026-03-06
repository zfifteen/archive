#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}
OUT="artifacts/semiprime_nav"
mkdir -p "$OUT"

echo "Running Semiprime Navigation Evaluation..."
echo "=========================================="

# Balanced (default) evaluation
echo "Running balanced evaluation..."
$PY tools/semiprime_balanced_eval.py
mv balanced_eval.csv "$OUT/balanced_eval.csv"
mv balanced_eval.md  "$OUT/balanced_eval.md"

# Balanced (default) done. Now unbalanced comparison: narrow p-band
echo "Running unbalanced evaluation..."
$PY tools/semiprime_balanced_eval.py --unbalanced 2>/dev/null || true
[ -f balanced_eval_unbal.csv ] && mv balanced_eval_unbal.csv "$OUT/balanced_eval_unbal.csv" || true
[ -f balanced_eval_unbal.md ]  && mv balanced_eval_unbal.md  "$OUT/balanced_eval_unbal.md"  || true

echo "Wrote artifacts to $OUT"
echo ""
echo "Generated files:"
ls -la "$OUT"