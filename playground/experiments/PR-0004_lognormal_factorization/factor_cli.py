#!/usr/bin/env python3
import argparse
from src.pipeline import factor_with_lognormal_prefilter
from src.model import ModelStore
from src.config import SearchPolicyConfig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("N", type=int, help="Semiprime to factor")
    parser.add_argument("--max-steps", type=int, default=10000)
    parser.add_argument("--radius-scale", type=float, default=1.0)
    parser.add_argument(
        "--direction-mode", choices=["ALTERNATE", "RANDOM"], default="ALTERNATE"
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    model = ModelStore()
    cfg = SearchPolicyConfig(
        max_steps=args.max_steps,
        radius_scale=args.radius_scale,
        direction_mode=args.direction_mode,
        seed=args.seed,
    )
    factor = factor_with_lognormal_prefilter(args.N, model, cfg)
    if factor is None:
        print("NONE")
    else:
        print(f"{factor} {args.N // factor}")


if __name__ == "__main__":
    main()
