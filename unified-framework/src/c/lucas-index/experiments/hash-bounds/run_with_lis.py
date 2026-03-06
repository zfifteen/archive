#!/usr/bin/env python3
"""
Run LIS (Lucas Index System) within an existing candidate-generation pipeline.

You can supply candidates via:
  - A Python module & symbol that yields integers (e.g., --module my.mod --symbol gen)
  - A numeric range (--start/--end)
  - A file/stdin of newline-separated integers (--input / '-')

The script prints a single metric:
  MR-call reduction vs wheel-210 baseline: X%

Proof of Concept: minimal integration layer.
"""
from __future__ import annotations

import argparse
import importlib
import sys
from typing import Iterable

from lis import reduction_vs_wheel210


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


def iter_module_symbol(module_path: str, symbol: str) -> Iterable[int]:
    mod = importlib.import_module(module_path)
    gen = getattr(mod, symbol)
    it = gen() if callable(gen) else gen
    for n in it:
        yield int(n)


def main() -> int:
    ap = argparse.ArgumentParser(description="Integrate LIS into an existing pipeline and print a single metric.")
    ap.add_argument("--module", type=str, help="module path that provides candidates (e.g., pkg.mod)")
    ap.add_argument("--symbol", type=str, help="symbol in module (callable or iterable)")
    ap.add_argument("--start", type=int, help="start of numeric range")
    ap.add_argument("--end", type=int, help="end of numeric range (inclusive)")
    ap.add_argument("--input", type=str, help="newline-separated integers file (or '-' for stdin)")
    ap.add_argument("--batch", type=int, default=8192, help="batch size (default: 8192)")
    args = ap.parse_args()

    sources: list[Iterable[int]] = []
    if args.module and args.symbol:
        sources.append(iter_module_symbol(args.module, args.symbol))
    if args.start is not None and args.end is not None:
        sources.append(iter_range(args.start, args.end))
    if args.input:
        sources.append(iter_file(args.input))
    if not sources:
        ap.error("provide --module/--symbol or --start/--end or --input")
        return 2

    def chained() -> Iterable[int]:
        for it in sources:
            for n in it:
                yield n

    baseline, after, reduction = reduction_vs_wheel210(chained(), batch_size=args.batch)
    print("LIS Phase 1 — Proof of Concept")
    if args.module and args.symbol:
        print(f"Pipeline source: {args.module}:{args.symbol}")
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

