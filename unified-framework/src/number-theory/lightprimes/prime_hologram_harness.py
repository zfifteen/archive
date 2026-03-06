#!/usr/bin/env python3
"""
prime_hologram_harness.py

Batch “harness” database for prime embeddings.
Features:
 1. bootstrap → use Miller–Rabin to generate first N primes,
    compute (stub) embeddings, and save to .npy
 2. query     → load a .npy coords file and radius‐search it

Usage:
  # 1. Bootstrap your harness with the first 360 primes,
  #    each embedded in D dims (replace embed_z with your real embedding!):
  ./prime_hologram_harness.py bootstrap \
    --count 360 \
    --dims 16 \
    --output harness_coords.npy

  # 2. Query:
  ./prime_hologram_harness.py query \
    --coords harness_coords.npy \
    --point 0.1 0.2 … 0.16 \
    --radius 0.05
"""

import sys
import argparse
import logging
import random

from typing import Sequence

import numpy as np
from scipy.spatial import cKDTree

# Configure root logger
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.ERROR,
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# By convention: row i of coords ↦ integer n = i-th prime
# We no longer use a fixed OFFSET, since we store only primes here.


def is_prime(n: int, k: int = 5) -> bool:
    """
    Miller–Rabin primality test (probabilistic).
    Returns True if n is probably prime, False if composite.
    k = number of bases to test.
    """
    if n < 2:
        return False
    # small-primes filter
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    if n in small_primes:
        return True
    for p in small_primes:
        if n % p == 0:
            return False

    # write n-1 = 2^s * d
    d = n - 1
    s = 0
    while d & 1 == 0:
        d >>= 1
        s += 1

    def trial(a: int) -> bool:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                return True
        return False

    for _ in range(k):
        a = random.randrange(2, n - 1)
        if not trial(a):
            return False
    return True


def generate_primes(count: int) -> Sequence[int]:
    """
    Generate first `count` primes using is_prime().
    """
    primes = []
    candidate = 2
    while len(primes) < count:
        if is_prime(candidate):
            primes.append(candidate)
            logger.debug(f"Found prime #{len(primes)} → {candidate}")
        candidate += 1
    logger.info(f"Generated {count} primes (last = {primes[-1]})")
    return primes


def embed_z(n: int, dims: int) -> np.ndarray:
    """
    Stub embedding for integer n into R^dims.
    Replace this with your actual Z-metric embeddings!
    """
    # Example: random unit-vector embedding (for demo only)
    vec = np.random.normal(size=(dims,))
    return vec / np.linalg.norm(vec)


class HarnessDatabase:
    """
    Immutable batch database for Z-embeddings of primes.
    Implicit mapping: row i → i-th prime in the bootstrap list.
    """

    def __init__(self, coords: np.ndarray, primes: Sequence[int]):
        if coords.dtype != np.float64:
            raise ValueError("coords must be float64")
        if coords.ndim != 2:
            raise ValueError("coords must be 2D")
        if coords.shape[0] != len(primes):
            raise ValueError("coords rows must match number of primes")

        self.coords = coords
        self.primes = np.array(primes, dtype=np.int32)
        self.tree = cKDTree(self.coords)
        logger.info(
            f"HarnessDB initialized with {len(primes)} primes, dim={coords.shape[1]}"
        )

    @classmethod
    def load(cls, coords_path: str, primes_path: str):
        """
        Load embeddings (.npy) and prime list (.txt or .npy).
        """
        logger.info(f"Loading coords from '{coords_path}'")
        coords = np.load(coords_path)

        logger.info(f"Loading primes from '{primes_path}'")
        # primes can be stored as .npy or newline-delimited .txt
        if primes_path.endswith(".npy"):
            primes = np.load(primes_path).tolist()
        else:
            with open(primes_path, "r") as f:
                primes = [int(line.strip()) for line in f if line.strip()]

        return cls(coords, primes)

    def save(self, coords_path: str, primes_path: str) -> None:
        """
        Persist coords (.npy) and primes (.txt).
        """
        logger.info(f"Saving coords to '{coords_path}'")
        np.save(coords_path, self.coords)

        logger.info(f"Saving primes list to '{primes_path}'")
        with open(primes_path, "w") as f:
            for p in self.primes:
                f.write(f"{p}\n")

    def query_radius(self, point: Sequence[float], radius: float) -> Sequence[int]:
        """
        Return all primes whose embeddings lie within `radius` of `point`.
        """
        pt = np.asarray(point, dtype=np.float64)
        logger.info(f"Querying radius={radius} around point={pt.tolist()}")
        idxs = self.tree.query_ball_point(pt, radius)
        result = self.primes[idxs]
        logger.info(f"Found {len(result)} hits: {result.tolist()}")
        return result


def main():
    p = argparse.ArgumentParser(
        description="Harness DB: bootstrap first-N primes or query a saved DB"
    )
    sub = p.add_subparsers(dest="cmd")

    # bootstrap
    bs = sub.add_parser("bootstrap", help="Generate N primes & embeddings → save")
    bs.add_argument(
        "--count", type=int, default=360, help="Number of primes to generate"
    )
    bs.add_argument(
        "--dims", type=int, required=True, help="Dimensionality of embeddings"
    )
    bs.add_argument(
        "--output", required=True, help="Output prefix (e.g. 'harness')"
    )
    bs.add_argument(
        "--seed", type=int, default=None, help="Random seed for embeddings"
    )

    # query
    qr = sub.add_parser("query", help="Load a harness DB and radius-query it")
    qr.add_argument(
        "--coords", required=True, help="Path to .npy coords file"
    )
    qr.add_argument(
        "--primes", required=True, help="Path to primes list (.txt or .npy)"
    )
    qr.add_argument(
        "--point", required=True, nargs="+", type=float, help="Embedding to query"
    )
    qr.add_argument(
        "--radius", required=True, type=float, help="Search radius"
    )

    args = p.parse_args()

    if args.cmd == "bootstrap":
        if args.seed is not None:
            random.seed(args.seed)
            np.random.seed(args.seed)

        primes = generate_primes(args.count)
        coords = np.vstack([embed_z(n, args.dims) for n in primes])

        coords_path = f"{args.output}_coords.npy"
        primes_path = f"{args.output}_primes.txt"
        db = HarnessDatabase(coords, primes)
        db.save(coords_path, primes_path)
        logger.info(
            f"Bootstrap complete → '{coords_path}', '{primes_path}'"
        )

    elif args.cmd == "query":
        db = HarnessDatabase.load(args.coords, args.primes)
        db.query_radius(args.point, args.radius)

    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
