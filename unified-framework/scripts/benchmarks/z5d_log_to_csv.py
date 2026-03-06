#!/usr/bin/env python3
"""
z5d_log_to_csv.py — Minimal streaming parser from Z5D logs -> CSV

Usage:
  python z5d_log_to_csv.py /path/to/bench_z5d_phase2.out.txt out.csv [--sci-threshold 15]

Notes:
- Parses semi-structured blocks like:
    Test for k = 10^N
    Input k: ...
    Z5D prediction: ...
    Found prime at prediction: ...
    Found prime: ... (diff +X)
    Raw Z5D prediction (rounded): ...
    Refined p_...: ...
    -- MR rounds (enhanced, deterministic bases): ...
    time: ... ms
- Handles very large logs by streaming (no full-file loads).
- Converts integers with >= sci-threshold digits to scientific notation.
"""

import argparse, csv, re, sys
from typing import Dict, Optional

# --- regex (compiled once) ---
RX_TEST      = re.compile(r'^Test for k = 10\^(\d+)\s*$')
RX_INPUT_K   = re.compile(r'^Input k:\s*([0-9]+)\s*$')
RX_PRED      = re.compile(r'^Z5D prediction:\s*([0-9]+)\s*$')
RX_FOUND_AT  = re.compile(r'^Found prime at prediction:\s*([0-9]+)\s*$')
RX_FOUND     = re.compile(r'^Found prime:\s*([0-9]+)\s*\(diff\s*([+-]?[0-9]+)\)\s*$')
RX_RAW       = re.compile(r'^Raw Z5D prediction \(rounded\):\s*([0-9]+)\s*$')
RX_REFINED   = re.compile(r'^Refined p_[0-9]+:\s*([0-9]+)\s*$')
RX_MR        = re.compile(r'^-- MR rounds.*:\s*([0-9]+)\s*$')
RX_TIME      = re.compile(r'^time:\s*([0-9]+)\s*ms\s*$')
RX_SEP       = re.compile(r'^-+\s*$')  # row separator (optional)

FIELDS = [
    "test_k_power",
    "input_k",
    "z5d_prediction",
    "found_prime",
    "found_at_prediction",
    "diff",
    "raw_prediction",
    "refined_pk",
    "mr_rounds",
    "time_ms",
]

def fmt_sci(num_str: str, threshold: int) -> str:
    """Format an integer string as scientific notation if its length >= threshold.
       Avoids int/float conversion (works for 10^1234)."""
    s = num_str.strip()
    if not s or not s.isdigit():
        return s
    if len(s) < threshold:
        return s
    # scientific:  d.dddd…e+exp  (keep 6 significant digits total)
    exp = len(s) - 1
    mant = s[0:6]  # first digit + next 5
    if len(mant) < 6:
        mant = mant.ljust(6, '0')
    mantissa = f"{mant[0]}.{mant[1:]}"
    return f"{mantissa}e+{exp}"

def write_row(writer: csv.DictWriter, row: Dict[str, Optional[str]], sci_threshold: int):
    # apply sci formatting to numeric-like fields
    for k in ("input_k","z5d_prediction","found_prime","raw_prediction","refined_pk"):
        if row.get(k):
            row[k] = fmt_sci(row[k], sci_threshold)
    writer.writerow(row)

def parse_file(in_path: str, out_path: str, sci_threshold: int):
    current: Dict[str, Optional[str]] = {k: "" for k in FIELDS}

    with open(in_path, "r", encoding="utf-8", errors="replace") as fin, \
            open(out_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=FIELDS)
        writer.writeheader()

        for line in fin:
            line = line.rstrip("\n")

            m = RX_TEST.match(line)
            if m:
                # If a previous block wasn't flushed (missing time/sep), flush it.
                if any(current.values()):
                    write_row(writer, current, sci_threshold)
                current = {k: "" for k in FIELDS}
                current["test_k_power"] = m.group(1)
                continue

            m = RX_INPUT_K.match(line)
            if m:
                current["input_k"] = m.group(1)
                continue

            m = RX_PRED.match(line)
            if m:
                current["z5d_prediction"] = m.group(1)
                continue

            m = RX_FOUND_AT.match(line)
            if m:
                current["found_prime"] = m.group(1)
                current["found_at_prediction"] = "1"
                current["diff"] = current.get("diff","") or "0"
                continue

            m = RX_FOUND.match(line)
            if m:
                current["found_prime"] = m.group(1)
                current["diff"] = m.group(2)
                # If we later see explicit "at prediction", leave found_at_prediction=1; else 0
                if not current.get("found_at_prediction"):
                    current["found_at_prediction"] = "0"
                continue

            m = RX_RAW.match(line)
            if m:
                current["raw_prediction"] = m.group(1)
                continue

            m = RX_REFINED.match(line)
            if m:
                current["refined_pk"] = m.group(1)
                continue

            m = RX_MR.match(line)
            if m:
                current["mr_rounds"] = m.group(1)
                continue

            m = RX_TIME.match(line)
            if m:
                current["time_ms"] = m.group(1)
                # time typically marks end of a block; write row
                write_row(writer, current, sci_threshold)
                current = {k: "" for k in FIELDS}
                continue

            if RX_SEP.match(line):
                # Separator — if we have a partially filled block, flush it.
                if any(current.values()):
                    write_row(writer, current, sci_threshold)
                    current = {k: "" for k in FIELDS}
                continue

        # End-of-file: flush any trailing data
        if any(current.values()):
            write_row(writer, current, sci_threshold)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Parse Z5D log into CSV.")
    ap.add_argument("input", help="Path to Z5D log file")
    ap.add_argument("output", help="Path to output CSV")
    ap.add_argument("--sci-threshold", type=int, default=15,
                    help="Convert integers with >= this many digits to scientific notation (default: 15)")
    args = ap.parse_args(argv)
    parse_file(args.input, args.output, args.sci_threshold)

if __name__ == "__main__":
    sys.exit(main())
