"""Analyze JSON-line output produced by hash_1000000.py."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize approximate_hash_bound batch results from a JSON-line text file."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("hash_bounds_results.txt"),
        help="path to the JSON-line results file",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="optional maximum number of records to load (0 = no limit)",
    )
    return parser.parse_args(argv)


def load_records(path: Path, limit: int) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    with path.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh):
            if limit and idx >= limit:
                break
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def summarize(records: List[Dict[str, object]]) -> None:
    total = len(records)
    if total == 0:
        print("No records loaded.")
        return

    with_prime_truth = [r for r in records if r.get("prime_true") is not None]
    with_frac_truth = [r for r in records if r.get("frac_true") is not None]
    bound_checks = [r for r in with_frac_truth if r.get("within_bounds") is not None]
    bound_hits = [r for r in bound_checks if r.get("within_bounds")]

    prime_errors = [float(r["prime_error_abs"]) for r in with_prime_truth if r.get("prime_error_abs") is not None]
    prime_ppm = [float(r["prime_error_rel_ppm"]) for r in with_prime_truth if r.get("prime_error_rel_ppm") is not None]
    frac_errors = [float(r["frac_error_abs"]) for r in with_frac_truth if r.get("frac_error_abs") is not None]
    bound_widths = [float(r["bound_width"]) for r in records if r.get("bound_width") is not None]

    print(f"Records loaded: {total}")
    print(f"Prime ground truth available: {len(with_prime_truth)}")
    print(f"Fractional ground truth available: {len(with_frac_truth)}")

    if bound_checks:
        coverage = len(bound_hits) / len(bound_checks)
        print(f"Bound coverage (available truth): {coverage:.3%}")
    else:
        print("No fractional truth available for bound coverage.")

    if prime_errors:
        print(f"Prime error abs mean/max: {mean(prime_errors):.3f} / {max(prime_errors):.3f}")
    if prime_ppm:
        print(f"Prime error ppm mean/max: {mean(prime_ppm):.3f} / {max(prime_ppm):.3f}")
    if frac_errors:
        print(f"Fractional error mean/max: {mean(frac_errors):.6f} / {max(frac_errors):.6f}")
    if bound_widths:
        print(f"Bound width mean/min/max: {mean(bound_widths):.6f} / {min(bound_widths):.6f} / {max(bound_widths):.6f}")


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    records = load_records(args.input.resolve(), args.limit)
    summarize(records)


if __name__ == "__main__":
    main()

