#!/bin/bash
# benchmark_big_n_python.sh
# Sweep large n values up to 10^1233 using the Python predictor.

set -euo pipefail

if [ "$(uname -s)" != "Darwin" ]; then
  echo "❌ macOS only: this script supports Darwin exclusively."
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY_SRC_DIR="$REPO_ROOT/src/python"
OUTPUT_DIR="$REPO_ROOT/scripts/output"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_CSV="$OUTPUT_DIR/z5d_big_n_timings_python_${TIMESTAMP}.csv"
LATEST_CSV="$OUTPUT_DIR/z5d_big_n_timings_python.csv"
ENVMETA="$OUTPUT_DIR/z5d_big_n_timings_python_${TIMESTAMP}.envmeta"
PYTHON_BIN="${PYTHON_BIN:-python3}"

: "${Z5D_SEED:=1337}"
: "${CFLAGS:=}"
: "${MPFR_VERSION:=unknown}"
: "${GMP_VERSION:=unknown}"
: "${PYTHONHASHSEED:=0}"

mkdir -p "$OUTPUT_DIR"
export Z5D_SEED PYTHONHASHSEED

# Verify gmpy2 is available in the chosen interpreter (no fallbacks)
if ! "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1; then
import gmpy2
PY
  echo "❌ gmpy2 not found in $PYTHON_BIN. Install with:"
  echo "   $PYTHON_BIN -m pip install gmpy2"
  exit 1
fi

if [ -n "${EXPS_OVERRIDE:-}" ]; then
  IFS=',' read -r -a EXPS <<< "$EXPS_OVERRIDE"
else
  EXPS=(20)
  for e in $(seq 50 50 1200); do EXPS+=("$e"); done
  EXPS+=("1230" "1233")
fi

echo "=== Z5D big-n benchmark (Python) ==="
echo "Provenance: seed=$Z5D_SEED cflags='${CFLAGS}' gmp=$GMP_VERSION mpfr=$MPFR_VERSION pythonhashseed=$PYTHONHASHSEED"

{
  echo "timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "command=$0 $*"
  echo "os=$(uname -a)"
  echo "cpu_brand=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo unknown)"
  echo "cpu_model=$(sysctl -n hw.model 2>/dev/null || echo unknown)"
  echo "cpu_physical=$(sysctl -n hw.physicalcpu 2>/dev/null || echo unknown)"
  echo "cpu_logical=$(sysctl -n hw.logicalcpu 2>/dev/null || echo unknown)"
  echo "compiler_cc=$(cc --version 2>/dev/null | head -n1)"
  echo "java=$(java -version 2>&1 | tr '\n' ';')"
  echo "python=$($PYTHON_BIN -V 2>&1)"
  echo "gmp=${GMP_VERSION}"
  echo "mpfr=${MPFR_VERSION}"
  echo "cflags=${CFLAGS:-unset}"
  echo "seed=${Z5D_SEED}"
  echo "pythonhashseed=${PYTHONHASHSEED}"
} > "$ENVMETA"

print_hardware_overview() {
  echo "Hardware Overview:"
  if command -v sysctl >/dev/null 2>&1; then
    model=$(sysctl -n hw.model 2>/dev/null || true)
    chip=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || true)
    pcores=$(sysctl -n hw.physicalcpu 2>/dev/null || true)
    lcores=$(sysctl -n hw.logicalcpu 2>/dev/null || true)
    mem_bytes=$(sysctl -n hw.memsize 2>/dev/null || true)
    os_ver=$(sw_vers -productVersion 2>/dev/null || true)

    if [ -n "${mem_bytes:-}" ]; then
      mem_gb=$(( (mem_bytes + 1024*1024*512) / 1024 / 1024 / 1024 ))
      mem_str="${mem_gb} GB"
    else
      mem_str="unknown"
    fi

    [ -n "${model:-}" ] && echo "  Model: $model"
    [ -n "${chip:-}" ] && echo "  Chip: $chip"
    [ -n "${pcores:-}" ] && echo "  Physical Cores: $pcores"
    [ -n "${lcores:-}" ] && echo "  Logical Cores: $lcores"
    echo "  Memory: ${mem_str}"
    [ -n "${os_ver:-}" ] && echo "  macOS: $os_ver"
  else
    echo "  (hardware details unavailable: sysctl not found)"
  fi
  echo
}

print_hardware_overview

# Warm-up sweep (not logged)
echo "Warm-up sweep (not logged)..."
for EXP in "${EXPS[@]}"; do
  n_str=$("$PYTHON_BIN" - <<PY
exp = int("${EXP}")
print(10**exp)
PY
)
  "$PYTHON_BIN" - <<PY
import sys, os
sys.path.append("$PY_SRC_DIR")
from z5d_predictor import predict_nth_prime
predict_nth_prime(int("${n_str}"))
PY
done
echo "Warm-up done. Running measured sweep..."

echo "n,elapsed_ms,prime_digits,seed,mpfr,gmp,cflags,pythonhashseed" > "$OUT_CSV"

for EXP in "${EXPS[@]}"; do
  n_str=$("$PYTHON_BIN" - <<PY
exp = int("${EXP}")
print(10**exp)
PY
)

  start_s=$(python3 - <<'PY'
import time
print(f"{time.time():.9f}")
PY
)
  prime=$("$PYTHON_BIN" - <<PY
import sys, os, random
try:
    import numpy as np
except Exception:
    np = None
seed = int(os.getenv("Z5D_SEED", "1337"))
random.seed(seed)
if np is not None:
    np.random.seed(seed)
sys.path.append("$PY_SRC_DIR")
from z5d_predictor import predict_nth_prime
print(predict_nth_prime(int("${n_str}" )).prime)
PY
)
  end_s=$(python3 - <<'PY'
import time
print(f"{time.time():.9f}")
PY
)
  elapsed_ms=$(python3 - <<PY
start=float("$start_s")
end=float("$end_s")
print(f"{(end-start)*1000:.3f}")
PY
)
  digits=${#prime}

  echo "10^$EXP: ${elapsed_ms} ms, digits=$digits"
  echo "$n_str,$elapsed_ms,$digits,$Z5D_SEED,$MPFR_VERSION,$GMP_VERSION,\"$CFLAGS\",$PYTHONHASHSEED" >> "$OUT_CSV"
done

cp "$OUT_CSV" "$LATEST_CSV"
echo "Results written to $OUT_CSV"
echo "Latest symlink copy: $LATEST_CSV"
echo "Environment metadata: $ENVMETA"
