"""
Title: Irreducibility Analysis of Golden-Ratio-Curved Prime Transition Matrices

Author: Big D
Date: 2025-08-01

Description:
This executable scientific white paper tests the hypothesis that the transition matrix T(k),
constructed from a golden-ratio-based curvature transformation of prime numbers, remains irreducible
across a wide range of curvature exponents k.

Irreducibility of T(k) implies the graph formed by curved prime transitions is strongly connected—
i.e., every prime state can be reached from any other. This ensures ergodicity and a unique
stationary distribution, analogous to stability and causality in dynamical systems.

The transformation:
    theta(p, k) = φ * {p/φ}^k
maps each prime p into a curved value using the golden ratio φ ≈ 1.618.
This represents a nonlinear, frame-dependent reshaping of prime "space," inspired by relativistic
geometry, where k acts as a curvature exponent. The hypothesis is falsified if, for any k tested,
T(k) becomes reducible (i.e., the graph breaks into disconnected components).

This provides a falsifiable test for structural invariance in the distribution of primes under
nonlinear transformations, potentially linking number theory with spectral graph theory and
dynamical systems.
"""

import numpy as np
from scipy.sparse.csgraph import connected_components
from sympy import isprime

# Constants
phi = (1 + 5 ** 0.5) / 2  # Golden ratio φ = (1 + √5) / 2
K_RANGE = np.arange(0.1, 3.0, 0.1)  # Range of curvature exponents k to test

# Curvature Transformation & Matrix Builder
def curvature_transform(n, k):
    """Apply golden-ratio-based curvature transformation to an integer n."""
    # Maps n to a curved value in [0, φ] using exponent k to control curvature strength
    return phi * ((n % phi) / phi) ** k

def build_transition_matrix(primes, k):
    """
    Construct a stochastic (row-normalized) transition matrix T(k)
    where entries represent transition likelihoods between curved prime states.
    """
    theta = np.array([curvature_transform(p, k) for p in primes])  # Apply transformation to all primes
    T = np.exp(-np.abs(theta[:, None] - theta[None, :]))  # Gaussian-like kernel on distance between curved values
    return T / T.sum(axis=1, keepdims=True)  # Normalize rows to make it a stochastic matrix

# Irreducibility Test
def test_irreducibility(primes, k_vals):
    """
    For each k in k_vals, test whether the transition matrix T(k) is irreducible.
    A matrix is irreducible if the corresponding directed graph has one strongly connected component.
    """
    irreducible_status = []
    for k in k_vals:
        T = build_transition_matrix(primes, k)
        n_components, _ = connected_components(csgraph=T, directed=True, connection='strong')
        irreducible = n_components == 1  # True if the graph is strongly connected
        irreducible_status.append((k, irreducible))
    return irreducible_status

# Main Execution Loop
# Main Execution Loop
if __name__ == "__main__":
    # Generate a list of prime numbers in a specified range
    primes = [p for p in range(5, 50001) if isprime(p)]  # Extended range to 50,000 for enhanced analysis

    # Run irreducibility test for all k values
    results = test_irreducibility(primes, K_RANGE)

    # Falsification check: hypothesis fails if any matrix is reducible (graph has >1 component)
    is_falsified = any(not status[1] for status in results)
    print("\nIrreducibility Falsification Test:", "FAIL" if is_falsified else "PASS")

    # Print irreducibility status for each tested k
    for k, irreducible in results:
        print(f"k = {k:.1f}: Irreducible = {irreducible}")

    # Final hypothesis conclusion
    if is_falsified:
        print("\nHypothesis falsified: Transition matrix becomes reducible at some k, indicating frame-dependent disconnection.")
    else:
        print("\nHypothesis passes: Transition matrix remains irreducible across all tested k, supporting invariant connectivity.")

    # Summary section displaying meaningful statistics and parameters
    print("\n--- Summary of Execution ---")
    print(f"Total number of primes tested: {len(primes)}")
    print(f"Range of primes: {primes[0]} to {primes[-1]}")
    print(f"Curvature exponent range (k): {K_RANGE[0]} to {K_RANGE[-1]:.1f} in steps of {K_RANGE[1] - K_RANGE[0]:.1f}")
    print(f"Irreducibility observed for all tested k-values: {all(status[1] for status in results)}")
    print(f"Golden ratio (φ): {phi:.6f}")
    print("\nExecution completed successfully.")