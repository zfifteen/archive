#!/usr/bin/env python3
"""
Experiment Setup for Discrete Riemannian Embeddings on High-Dimensional Tori
for QMC-Accelerated Geodesic Factorization

This script sets up and runs an experiment to test factorization using geodesic
distances on high-dimensional tori, augmented by QMC (Quasi-Monte Carlo) sampling
with Sobol sequences and Owen scrambling, as described in the GVA (Geodesic
Validation Assault) method.

Key components:
- Embedding integers into high-dimensional torus
- Riemannian geometry analogs for discrete sets
- QMC variance-reduced sampling
- Geodesic distance anomaly detection for factor identification

Usage:
    python experiment_setup.py --target <semiprime> --dims <dimensions> --samples <num_samples>
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gva_factorize import gva_factorize_64bit
from targets import load_256bit_targets
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ExperimentSetup:
    """Setup and configuration for geodesic factorization experiments."""

    def __init__(self, target: int, range_radius: int = 10000000):
        """
        Initialize experiment setup.

        Args:
            target: Semiprime target for factorization
            range_radius: Search range around sqrt(N) for factors
        """
        self.target = target
        self.range_radius = range_radius

        # Validate target
        if target <= 1:
            raise ValueError("Target must be a positive integer > 1")
        if target >= 2**64:
            raise ValueError("Target must be < 2^64 for this implementation")

        logger.info(f"Experiment setup: target={target}, range_radius={range_radius}")

    def run_experiment(self):
        """Execute the factorization experiment using GVA."""
        logger.info("Starting geodesic factorization experiment...")

        import time
        start_time = time.time()

        try:
            p, q, dist = gva_factorize_64bit(self.target, self.range_radius)

            execution_time = time.time() - start_time

            results = {
                'success': p is not None,
                'factors': (p, q) if p else None,
                'geodesic_distance': float(dist) if dist else None,
                'execution_time': execution_time,
                'target': self.target,
                'range_radius': self.range_radius
            }

            # Log results
            if results['success']:
                logger.info(f"Factorization successful! Factors: {p} × {q}")
                logger.info(f"Geodesic distance: {float(dist):.6f}")
            else:
                logger.warning("Factorization did not succeed within parameters")

            # Save detailed results
            self.save_results(results)

            return results

        except Exception as e:
            logger.error(f"Experiment failed: {e}")
            raise

    def save_results(self, results: dict):
        """Save experiment results to JSON file."""
        output_file = Path(f"experiment_results_{self.target}_{self.range_radius}r.json")
        with open(output_file, 'w') as f:
            json.dump({
                'experiment_config': {
                    'target': self.target,
                    'range_radius': self.range_radius
                },
                'results': results,
                'timestamp': str(Path(__file__).stat().st_mtime)
            }, f, indent=2)

        logger.info(f"Results saved to {output_file}")


def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(description="Run geodesic factorization experiment")
    parser.add_argument('--target', type=int,
                       help='Semiprime target for factorization')
    parser.add_argument('--range-radius', type=int, default=10000000,
                       help='Search range radius around sqrt(N) (default: 10M)')
    parser.add_argument('--list-targets', action='store_true',
                       help='List available test targets')

    args = parser.parse_args()

    if args.list_targets:
        print("Available test targets (first 10 from 256bit targets):")
        targets = load_256bit_targets(10)
        for i, value in enumerate(targets):
            print(f"  target_{i}: {value}")
        return

    if not args.target:
        parser.error("--target is required unless --list-targets is specified")

    # Setup and run experiment
    experiment = ExperimentSetup(
        target=args.target,
        range_radius=args.range_radius
    )

    results = experiment.run_experiment()

    # Print summary
    print("\nExperiment Summary:")
    print(f"Target: {args.target}")
    print(f"Success: {results.get('success', False)}")
    if results.get('success'):
        print(f"Factors found: {results['factors']}")
        print(f"Geodesic distance: {results.get('geodesic_distance', 'N/A')}")
    print(f"Execution time: {results.get('execution_time', 'N/A'):.2f} seconds")


if __name__ == "__main__":
    main()
