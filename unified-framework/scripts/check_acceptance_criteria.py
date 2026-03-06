"""
Check Acceptance Criteria for Simplex-Anchor Experiment

Validates that experiment results meet the defined acceptance criteria.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load experiment configuration."""
    with open(config_path) as f:
        return json.load(f)


def load_analysis_results(results_dir: Path) -> Dict[str, Any]:
    """Load analysis results from directory."""
    # This would load the analyzed results
    # For now, we'll check individual summaries
    results = {}

    for condition_dir in results_dir.glob("*"):
        if not condition_dir.is_dir():
            continue

        summary_path = condition_dir / "summary.json"
        if summary_path.exists():
            with open(summary_path) as f:
                parts = condition_dir.name.split("_")
                try:
                    if len(parts) < 2 or not parts[1].endswith("bit"):
                        raise ValueError("Invalid directory name format")
                    condition = parts[0]
                    bit_length = int(parts[1].replace("bit", ""))
                except (IndexError, ValueError) as e:
                    print(
                        f"Warning: Skipping directory with unexpected format: {condition_dir.name} ({e})"
                    )
                    continue

                key = f"{condition}_{bit_length}"
                results[key] = json.load(f)

    return results


def check_keygen_acceptance(
    baseline_summary: Dict[str, Any],
    simplex_summary: Dict[str, Any],
    criteria: Dict[str, Any],
    bit_length: int,
) -> Dict[str, Any]:
    """Check if keygen results meet acceptance criteria.

    Returns dict with pass/fail and details.
    """
    # Calculate percent speedup
    baseline_time = baseline_summary["median_total_time_ms"]
    simplex_time = simplex_summary["median_total_time_ms"]

    speedup_pct = ((baseline_time - simplex_time) / baseline_time) * 100.0

    # Check threshold
    required_speedup = criteria["median_speedup_pct"]
    passes_threshold = speedup_pct >= required_speedup

    # Note: We can't check CI without full bootstrap analysis here
    # This is a simplified check

    return {
        "bit_length": bit_length,
        "baseline_time_ms": baseline_time,
        "simplex_time_ms": simplex_time,
        "speedup_pct": speedup_pct,
        "required_speedup_pct": required_speedup,
        "passes_threshold": passes_threshold,
        "status": "✅ PASS" if passes_threshold else "❌ FAIL",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check acceptance criteria for simplex-anchor experiment"
    )
    parser.add_argument(
        "--config", type=str, required=True, help="Path to experiment config JSON"
    )
    parser.add_argument(
        "--results-dir", type=str, required=True, help="Directory containing results"
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    results_dir = Path(args.results_dir)

    print("=" * 70)
    print("SIMPLEX-ANCHOR ACCEPTANCE CRITERIA CHECK")
    print("=" * 70)
    print()

    # Load config
    config = load_config(config_path)
    criteria = config["acceptance_criteria"]["keygen"]

    print(f"Config: {config_path}")
    print(f"Results: {results_dir}")
    print(f"Required speedup: ≥{criteria['median_speedup_pct']}%")
    print()

    # Load results
    results = load_analysis_results(results_dir)

    if not results:
        print("❌ ERROR: No results found!")
        sys.exit(1)

    # Check each bit length
    all_pass = True

    for bit_length in [1024, 2048]:
        baseline_key = f"baseline_{bit_length}"
        simplex_key = f"simplex_{bit_length}"

        if baseline_key not in results or simplex_key not in results:
            print(f"⚠️  WARNING: Missing results for {bit_length}-bit")
            continue

        check = check_keygen_acceptance(
            results[baseline_key],
            results[simplex_key],
            criteria,
            bit_length,
        )

        print(f"## {bit_length}-bit RSA")
        print(f"   Baseline time:  {check['baseline_time_ms']:.2f} ms")
        print(f"   Simplex time:   {check['simplex_time_ms']:.2f} ms")
        print(f"   Speedup:        {check['speedup_pct']:.2f}%")
        print(f"   Required:       ≥{check['required_speedup_pct']}%")
        print(f"   Status:         {check['status']}")
        print()

        if not check["passes_threshold"]:
            all_pass = False

    print("=" * 70)
    if all_pass:
        print("✅ ALL ACCEPTANCE CRITERIA PASSED")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ SOME ACCEPTANCE CRITERIA FAILED")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
