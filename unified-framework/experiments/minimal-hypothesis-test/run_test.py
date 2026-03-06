from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable, List, Tuple


def normal_one_sided_p_value(z: float) -> float:
    # p = 1 - Phi(z) = 0.5 * erfc(z / sqrt(2))
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Minimal test: does observed coverage exceed the random-baseline "
            "expectation given the same widths? (Poisson-binomial normal approx)"
        )
    )
    default_path = Path(__file__).resolve().parents[2] / "hash_bounds_results.txt"
    parser.add_argument("--input", type=Path, default=default_path, help="path to JSONL results")
    parser.add_argument("--alpha", type=float, default=0.01, help="one-sided significance level")
    return parser.parse_args(argv)


def load_hits_and_widths(path: Path) -> Tuple[int, List[float]]:
    hits = 0
    widths: List[float] = []
    total = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            # Require fractional truth and a width
            if rec.get("frac_true") is None:
                continue
            w = float(rec.get("bound_width", 0.0))
            if w <= 0.0:
                continue
            widths.append(w)
            total += 1
            if rec.get("within_bounds") is True:
                hits += 1
    if total == 0:
        raise RuntimeError("No valid records found in input file.")
    return hits, widths


def run_test(input_path: Path, alpha: float) -> None:
    hits, widths = load_hits_and_widths(input_path)
    mu = sum(widths)
    var = sum(w * (1.0 - w) for w in widths)
    n = len(widths)

    if var <= 0.0:
        raise RuntimeError("Degenerate variance; widths must be in (0,1).")

    z = (hits - mu) / math.sqrt(var)
    p = normal_one_sided_p_value(z)

    print(f"Input: {input_path}")
    print(f"Samples: {n}")
    print(f"Hits: {hits}")
    print(f"Sum widths (μ): {mu:.6f}")
    print(f"Var (σ²): {var:.6f}")
    print(f"z-score: {z:.3f}")
    print(f"one-sided p-value: {p:.6g}")

    if p < alpha:
        print(f"Reject H0 at α={alpha}: coverage exceeds random baseline (evidence of structure).")
    else:
        print(f"Fail to reject H0 at α={alpha}: no lift over random baseline detected.")


if __name__ == "__main__":
    args = parse_args()
    run_test(args.input.resolve(), args.alpha)

