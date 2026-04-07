#!/usr/bin/env python3
"""
Generate an exploratory markdown summary for the Z5D-Geofac alignment experiment.

The summary is intentionally descriptive. It reports overlap metrics from the
experiment pipeline without presenting them as validation of the active
nth-prime predictor.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


def format_percent(value: float, precision: int = 2) -> str:
    """Format a number as percentage."""
    return f"{value * 100:.{precision}f}%"


def generate_executive_summary(report: Dict[str, Any]) -> str:
    """Generate the executive summary section."""
    jaccard = report["jaccard_bins"]
    ci_lower, ci_upper = report["jaccard_ci_95"]
    topk_rate = report["topk_hit_rate"]
    spearman = report["spearman_rho"]
    passes_gate = report["gate_decision"]["passes_z5d_gate"]

    headline = (
        "one exploratory run exceeded the legacy overlap threshold"
        if passes_gate
        else "the recorded run stayed below the legacy overlap threshold"
    )

    return f"""# Z5D-Geofac Exploratory Alignment Report

## Executive Summary

**Result: {headline}**

This experiment compares a Z5D-derived peak pipeline with Geofac under a shared
QMC seed stream. The result is descriptive for this pipeline, dataset, and
binning setup. It does not validate the active nth-prime predictor.

### Recorded metrics

| Metric | Value | Reading |
|--------|-------|---------|
| **Jaccard Index** | **{jaccard:.4f}** | Descriptive overlap for this run |
| **95% Confidence Interval** | [{ci_lower:.4f}, {ci_upper:.4f}] | {'Above' if ci_lower > 0.10 else 'Below'} the legacy lower-bound threshold |
| **Top-K Hit Rate** | {format_percent(topk_rate)} | Shared-bin fraction for this run |
| **Spearman ρ** | {spearman:.4f} | {'Moderate positive' if spearman >= 0.3 else 'Weak positive' if spearman >= 0.1 else 'Weak / no'} rank agreement |

## Interpretation

The overlap metrics indicate that this experiment produced a measurable signal,
but they do not establish that Geofac validates the active predictor or that the
two systems encode the same structure in general. The rank-correlation result
should be read alongside the overlap metrics before drawing broader conclusions.

### Legacy threshold check

Historical threshold retained in this experiment:
- `Jaccard >= 0.20`
- `CI lower bound > 0.10`

Recorded run:
- `Jaccard = {jaccard:.4f}`
- `CI lower bound = {ci_lower:.4f}`

In this repository, exceeding that threshold means "worth further study under
this pipeline," not "predictor validated."
"""


def generate_methodology(report: Dict[str, Any]) -> str:
    """Generate the methodology section."""
    return f"""## Methodology

This experiment compares two exploratory pipelines:

1. **Z5D-derived peak pipeline**: maps QMC samples to `k` values, then derives
   peak bins using the repo CLI when available or a documented surrogate path
   when it is not.
2. **Geofac pipeline**: computes candidate amplitudes and bins them under the
   same broad scale range.

### Reproducibility configuration

```json
{json.dumps({
    "seed_set_id": report["seed_set_id"],
    "qmc_type": report["qmc_type"],
    "scale_range": report["scale_gate"],
    "top_k": report["K"],
    "num_bins": report["num_bins"],
    "bootstrap_samples": report["bootstrap_samples"],
    "confidence_level": report["confidence_level"],
    "git_sha": report["git"]["sha"],
}, indent=2)}
```

### Procedure

- Generate a shared QMC seed set
- Produce Z5D-derived peak bins
- Produce Geofac peak bins
- Compute overlap, hit-rate, and rank-correlation statistics
- Report the result as an exploratory artifact

### Important limit

This experiment measures overlap between experiment pipelines. It does not
directly test nth-prime correctness.
"""


def generate_results(report: Dict[str, Any]) -> str:
    """Generate detailed results section."""
    return f"""## Detailed Results

### Binning statistics

| System | Top rows kept | Unique bins |
|--------|---------------|-------------|
| Z5D-derived pipeline | {report['K']} | {report['z5d_unique_bins']} |
| Geofac | {report['K']} | {report['geofac_unique_bins']} |

### Overlap statistics

- **Intersection:** {report['intersection_bins']} bins
- **Union:** {report['union_bins']} bins
- **Z5D-only bins:** {report['z5d_unique_bins'] - report['intersection_bins']}
- **Geofac-only bins:** {report['geofac_unique_bins'] - report['intersection_bins']}

### Bootstrap summary

- **Point estimate:** {report['jaccard_bins']:.4f}
- **Bootstrap mean:** {report['jaccard_bootstrap_mean']:.4f}
- **95% CI:** [{report['jaccard_ci_95'][0]:.4f}, {report['jaccard_ci_95'][1]:.4f}]
- **Top-K hit rate:** {format_percent(report['topk_hit_rate'])}
- **Spearman ρ:** {report['spearman_rho']:.4f}
- **p-value:** {report['spearman_pval']:.4e}
"""


def generate_reproduction(report: Dict[str, Any]) -> str:
    """Generate reproduction instructions."""
    return f"""## Reproduction

```bash
cd experiments/z5d_geofac_alignment_001/tools

# Run the experiment shell
python run_experiment.py --samples 1000 --max-process 100 --test
```

If `z5d_cli` is unavailable, the Z5D-derived side of the pipeline may fall back
to a documented surrogate mock path. Results from that path remain exploratory
and should not be treated as equivalent evidence for the active predictor.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate exploratory summary for the alignment experiment"
    )
    parser.add_argument("--report", type=Path, required=True, help="Input report JSON")
    parser.add_argument("--output", type=Path, required=True, help="Output markdown path")
    args = parser.parse_args()

    with args.report.open("r") as f:
        report = json.load(f)

    sections = [
        generate_executive_summary(report),
        generate_methodology(report),
        generate_results(report),
        generate_reproduction(report),
    ]
    content = "\n\n".join(sections) + "\n"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        f.write(content)

    print(f"Wrote exploratory summary to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
