#!/usr/bin/env python3
"""
CLI Command: Run the Official 127-bit Geofac Challenge

This script provides a one-command interface to run the 127-bit factorization
challenge with optimized shell-exclusion pruning.

Usage:
    python cli/challenge_127.py [--config CONFIG_PATH]
    
Example:
    python cli/challenge_127.py
    python cli/challenge_127.py --config configs/challenge-127.yml
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from z5d.challenge_factorizer import (
    factor_challenge_127bit,
    FactorizationConfig,
    FactorizationResult,
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Factor the official 127-bit geofac challenge with shell-exclusion pruning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use default optimized config
  %(prog)s --no-shell-exclusion     # Baseline (no pruning)
  %(prog)s --max-iterations 1000000 # Override iteration limit
  
Expected Runtime:
  With shell exclusion:    4.8-6.2 minutes (64-core AMD EPYC 7J13)
  Without shell exclusion: ~19 minutes (baseline)
  Speedup:                 3-4x
        """
    )
    
    parser.add_argument(
        "--no-shell-exclusion",
        action="store_true",
        help="Disable shell-exclusion pruning (baseline mode)",
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        help="Override maximum iterations",
    )
    
    parser.add_argument(
        "--shell-delta",
        type=int,
        help="Override shell delta (width)",
    )
    
    parser.add_argument(
        "--shell-count",
        type=int,
        help="Override shell count",
    )
    
    return parser.parse_args()


def main():
    """Main entry point for 127-bit challenge CLI."""
    args = parse_args()
    
    # Create default configuration
    config = FactorizationConfig.challenge_127bit()
    
    # Apply command-line overrides
    if args.no_shell_exclusion:
        config.use_shell_exclusion = False
        print("⚠️  Shell exclusion disabled (baseline mode)")
    
    if args.max_iterations:
        config.max_iters = args.max_iterations
        print(f"🔧 Max iterations override: {args.max_iterations:,}")
    
    if args.shell_delta:
        config.shell_delta = args.shell_delta
        print(f"🔧 Shell delta override: {args.shell_delta}")
    
    if args.shell_count:
        config.shell_count = args.shell_count
        print(f"🔧 Shell count override: {args.shell_count}")
    
    print()
    
    # Run the challenge
    try:
        result = factor_challenge_127bit(config)
        
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
