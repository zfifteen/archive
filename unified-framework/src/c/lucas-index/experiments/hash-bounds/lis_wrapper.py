#!/usr/bin/env python3
"""
LIS Wrapper (Python) — Proof of Concept

Invokes the LIS (Lucas/Fibonacci pre-filter) from Python. Two modes:
  1) Metrics (default): compute MR-call reduction vs wheel-210 baseline
  2) Filter (--filter): emit only LIS survivors

Usage:
  python3 lis_wrapper.py --start 1 --end 200000
  python3 lis_wrapper.py --input candidates.txt
  python3 lis_wrapper.py --filter --start 1 --end 10000
  python3 lis_wrapper.py --filter --input candidates.txt --output survivors.txt
"""
from __future__ import annotations

import argparse
import sys
from typing import Iterable, List

# Local wrapper imports liblis and builds if needed
from lis import prune_with_lis, reduction_vs_wheel210


def iter_range(start: int, end: int) -> Iterable[int]:
    step = 1 if end >= start else -1
    for n in range(start, end + step, step):
        yield n


def iter_file(path: str | None) -> Iterable[int]:
    fh = sys.stdin if not path or path == "-" else open(path, "r")
    try:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            try:
                yield int(s)
            except ValueError:
                continue
    finally:
        if fh is not sys.stdin:
            fh.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="LIS (Lucas Index System) Python wrapper — PoC")
    ap.add_argument("--start", type=int, help="start of numeric range")
    ap.add_argument("--end", type=int, help="end of numeric range (inclusive)")
    ap.add_argument("--input", type=str, help="newline-separated integers file (or '-' for stdin)")
    ap.add_argument("--output", type=str, help="write survivors to this file in filter mode")
    ap.add_argument("--batch", type=int, default=8192, help="batch size for LIS calls (default: 8192)")
    ap.add_argument("--filter", action="store_true", help="emit only LIS survivors instead of metrics")
    args = ap.parse_args()

    # Source selection
    sources: List[Iterable[int]] = []
    if args.start is not None and args.end is not None:
        sources.append(iter_range(args.start, args.end))
    if args.input:
        sources.append(iter_file(args.input))
    if not sources:
        ap.error("provide --start/--end or --input")
        return 2

    # Chain sources into one iterator
    def chained() -> Iterable[int]:
        for it in sources:
            for n in it:
                yield n

    if args.filter:
        # Filter mode: print or write survivors
        survivors = prune_with_lis(chained(), batch_size=args.batch)
        if args.output:
            with open(args.output, "w") as fh:
                for n in survivors:
                    fh.write(f"{n}\n")
        else:
            for n in survivors:
                print(n)
        return 0

    # Metrics mode (default)
    baseline, after, reduction = reduction_vs_wheel210(chained(), batch_size=args.batch)
    print("LIS Phase 1 — Proof of Concept")
    if args.start is not None and args.end is not None:
        print(f"Range: [{args.start}, {args.end}]")
    if args.input:
        print(f"Input: {args.input}")
    print(f"Baseline (wheel-210) candidates: {baseline}")
    print(f"After LIS filter (MR calls):     {after}")
    print(f"MR-call reduction vs baseline:   {reduction*100:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
