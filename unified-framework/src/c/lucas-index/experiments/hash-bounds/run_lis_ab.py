#!/usr/bin/env python3
"""
LIS Phase 1 — minimal A/B harness

Compares MR-call baseline (wheel-210) vs wheel-210 + LIS filter over a synthetic
range. Prints a single metric: MR-call reduction vs baseline.
"""
from lis import reduction_vs_wheel210


def main():
    # Synthetic range: choose a moderate interval
    start = 1
    end = 200000  # 2e5
    baseline, mr_calls, reduction = reduction_vs_wheel210(range(start, end + 1))
    print("LIS Phase 1 — Proof of Concept")
    print(f"Range: [{start}, {end}]")
    print(f"Baseline (wheel-210) candidates: {baseline}")
    print(f"After LIS filter (MR calls):     {mr_calls}")
    print(f"MR-call reduction vs baseline:   {reduction*100:.2f}%")


if __name__ == "__main__":
    main()
