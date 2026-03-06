"""
CLI for RSA Keygen A/B Test

Command-line interface for running keygen experiments with simplex-anchor.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.experiments.keygen_ab import run_keygen_experiment, save_results
from src.z5d.simplex_anchor import ConditionType


def main():
    parser = argparse.ArgumentParser(
        description="RSA Keygen A/B Test with Simplex-Anchor Enhancement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test (baseline)
  python -m cli.keygen_ab --bits 1024 --condition baseline --trials 500 --seed 1337 \\
      --out-dir results/keygen_simplex_anchor/baseline_1024

  # Simplex-anchor test
  python -m cli.keygen_ab --bits 1024 --condition simplex --trials 500 --seed 1337 \\
      --out-dir results/keygen_simplex_anchor/simplex_1024

  # Full suite
  python -m cli.keygen_ab --bits 2048 --condition simplex --trials 10000 --seed 1337 \\
      --out-dir results/keygen_simplex_anchor/simplex_2048
        """,
    )
    
    parser.add_argument(
        "--bits",
        type=int,
        required=True,
        choices=[1024, 2048],
        help="RSA bit length (1024 or 2048)",
    )
    
    parser.add_argument(
        "--condition",
        type=str,
        required=True,
        choices=["baseline", "simplex", "A4", "euler", "self_dual"],
        help="Simplex-anchor condition",
    )
    
    parser.add_argument(
        "--trials",
        type=int,
        required=True,
        help="Number of trials to run",
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        required=True,
        help="Random seed for reproducibility",
    )
    
    parser.add_argument(
        "--out-dir",
        type=str,
        required=True,
        help="Output directory for results",
    )
    
    parser.add_argument(
        "--mr-rounds",
        type=int,
        default=20,
        help="Miller-Rabin rounds (default: 20)",
    )
    
    parser.add_argument(
        "--td-limit",
        type=int,
        default=1000,
        help="Trial division limit (default: 1000)",
    )
    
    args = parser.parse_args()
    
    # Validate condition type
    condition: ConditionType = args.condition
    
    print("=" * 70)
    print("RSA Keygen A/B Test - Simplex-Anchor Enhancement")
    print("=" * 70)
    print(f"Bit length:      {args.bits}")
    print(f"Condition:       {condition}")
    print(f"Trials:          {args.trials}")
    print(f"Seed:            {args.seed}")
    print(f"MR rounds:       {args.mr_rounds}")
    print(f"TD limit:        {args.td_limit}")
    print(f"Output dir:      {args.out_dir}")
    print("=" * 70)
    print()
    
    # Run experiment
    trials, summary = run_keygen_experiment(
        bit_length=args.bits,
        condition=condition,
        n_trials=args.trials,
        seed=args.seed,
        mr_rounds=args.mr_rounds,
        td_limit=args.td_limit,
    )
    
    # Save results
    save_results(trials, summary, Path(args.out_dir))
    
    print()
    print("=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    print(f"Condition:              {summary.condition}")
    print(f"Bit length:             {summary.bit_length}")
    print(f"Trials:                 {summary.n_trials}")
    print(f"Mean candidates:        {summary.mean_candidates:.2f}")
    print(f"Median candidates:      {summary.median_candidates:.2f}")
    print(f"Mean MR calls:          {summary.mean_mr_calls:.2f}")
    print(f"Median MR calls:        {summary.median_mr_calls:.2f}")
    print(f"Mean total time (ms):   {summary.mean_total_time_ms:.2f}")
    print(f"Median total time (ms): {summary.median_total_time_ms:.2f}")
    print(f"Mean MR time (ms):      {summary.mean_mr_time_ms:.2f}")
    print(f"Median MR time (ms):    {summary.median_mr_time_ms:.2f}")
    print("=" * 70)
    print()
    print(f"✓ Results saved to: {args.out_dir}")


if __name__ == "__main__":
    main()
