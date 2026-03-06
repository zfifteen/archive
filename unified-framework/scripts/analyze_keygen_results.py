"""
Analyze Keygen Results and Generate Summary Report

Processes keygen experiment results and generates comprehensive analysis report.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.bootstrap import compare_conditions
from src.analysis.distributions import compare_distributions


def load_results(results_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load all keygen results from directory."""
    results = {}

    for condition_dir in results_dir.glob("*"):
        if not condition_dir.is_dir():
            continue

        summary_path = condition_dir / "summary.json"
        metrics_path = condition_dir / "metrics.csv"

        if not summary_path.exists():
            continue

        with open(summary_path) as f:
            summary = json.load(f)

        # Extract condition name (format: condition_bitlength)
        parts = condition_dir.name.split("_")
        if len(parts) < 2:
            print(
                f"Warning: Skipping directory with unexpected name format: {condition_dir.name}"
            )
            continue
        condition = parts[0]
        bit_length_str = parts[1].replace("bit", "")
        try:
            bit_length = int(bit_length_str)
        except ValueError:
            print(f"Warning: Could not parse bit length from: {condition_dir.name}")
            continue

        key = f"{condition}_{bit_length}"
        results[key] = {
            "summary": summary,
            "metrics_path": metrics_path,
        }

    return results


def extract_metrics_from_csv(csv_path: Path, metric: str) -> np.ndarray:
    """Extract metric column from CSV."""
    import csv

    values = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            values.append(float(row[metric]))

    return np.array(values)


def analyze_bit_length(
    results: Dict[str, Dict[str, Any]],
    bit_length: int,
) -> Dict[str, Any]:
    """Analyze results for a specific bit length."""
    # Filter for this bit length
    filtered = {k: v for k, v in results.items() if f"_{bit_length}" in k}

    if not filtered:
        return {}

    # Check if we have baseline
    baseline_key = f"baseline_{bit_length}"
    if baseline_key not in filtered:
        print(f"Warning: No baseline for {bit_length}-bit")
        return {}

    baseline_times = extract_metrics_from_csv(
        filtered[baseline_key]["metrics_path"], "total_time_ms"
    )

    analysis = {
        "bit_length": bit_length,
        "baseline": filtered[baseline_key]["summary"],
        "comparisons": {},
    }

    # Compare each condition to baseline
    for key, data in filtered.items():
        if key == baseline_key:
            continue

        condition = key.split("_")[0]
        treatment_times = extract_metrics_from_csv(
            data["metrics_path"], "total_time_ms"
        )

        # Bootstrap comparison
        comparison = compare_conditions(
            baseline_times,
            treatment_times,
            metric_name="total_time_ms",
            n_iterations=1000,
            seed=42,
        )

        # Distribution comparison
        dist_comp = compare_distributions(
            baseline_times,
            treatment_times,
            alpha=0.05,
        )

        analysis["comparisons"][condition] = {
            "summary": data["summary"],
            "bootstrap": comparison,
            "distributions": dist_comp,
        }

    return analysis


def generate_markdown_report(
    analyses: Dict[int, Dict[str, Any]],
    output_path: Path,
) -> None:
    """Generate markdown report from analyses."""
    lines = [
        "# Simplex-Anchor Keygen A/B Test Results",
        "",
        "## Summary",
        "",
        f"Analyzed {len(analyses)} bit lengths with simplex-anchor enhancement.",
        "",
    ]

    for bit_length, analysis in sorted(analyses.items()):
        if not analysis:
            continue

        lines.extend(
            [
                f"## {bit_length}-bit RSA",
                "",
                "### Baseline",
                f"- Median candidates: {analysis['baseline']['median_candidates']:.2f}",
                f"- Median time: {analysis['baseline']['median_total_time_ms']:.2f} ms",
                "",
                "### Comparisons to Baseline",
                "",
            ]
        )

        for condition, comp in analysis["comparisons"].items():
            pct_change = comp["bootstrap"]["percent_change"]

            lines.extend(
                [
                    f"#### {condition.upper()}",
                    f"- Median time: {comp['summary']['median_total_time_ms']:.2f} ms",
                    f"- Percent change: {pct_change['point_estimate']:.2f}% "
                    f"(95% CI: [{pct_change['ci_lower']:.2f}, {pct_change['ci_upper']:.2f}])",
                    f"- Significant: {'✅ Yes' if comp['bootstrap']['significant'] else '❌ No'}",
                    f"- Distributions differ: {'✅ Yes' if comp['distributions']['distributions_differ'] else '❌ No'}",
                    "",
                ]
            )

        lines.append("")

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Report written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze keygen experiment results")
    parser.add_argument(
        "--results-dir", type=str, required=True, help="Directory containing results"
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Output markdown file path"
    )

    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_path = Path(args.output)

    print(f"Loading results from: {results_dir}")
    results = load_results(results_dir)

    if not results:
        print("No results found!")
        return

    print(f"Found {len(results)} result sets")

    # Analyze each bit length
    analyses = {}
    for bit_length in [1024, 2048]:
        print(f"\nAnalyzing {bit_length}-bit...")
        analysis = analyze_bit_length(results, bit_length)
        if analysis:
            analyses[bit_length] = analysis

    # Generate report
    print("\nGenerating report...")
    generate_markdown_report(analyses, output_path)

    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    main()
