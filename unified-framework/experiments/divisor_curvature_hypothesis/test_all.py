#!/usr/bin/env python3
"""
Quick test runner to verify all experiment components.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"{'='*70}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0


def main():
    """Run all tests."""
    exp_dir = Path(__file__).parent
    
    tests = [
        (f"cd {exp_dir} && python run_experiment.py --seed 42",
         "Main experiment (n=2-49) - Hypothesis target range"),
        
        (f"cd {exp_dir} && python extended_analysis.py",
         "Extended analysis across multiple ranges"),
        
        (f"cd {exp_dir} && python visualize.py --output-dir test_plots",
         "Visualization generation"),
    ]
    
    results = []
    for cmd, desc in tests:
        success = run_command(cmd, desc)
        results.append((desc, success))
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    for desc, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {desc}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print(f"\n{'='*70}")
        print("ALL TESTS PASSED ✓")
        print(f"{'='*70}")
        return 0
    else:
        print(f"\n{'='*70}")
        print("SOME TESTS FAILED ✗")
        print(f"{'='*70}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
