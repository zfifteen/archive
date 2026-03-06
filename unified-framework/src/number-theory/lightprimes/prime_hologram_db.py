#!/usr/bin/env python3
"""
prime_hologram_db.py

Contains both the immutable batch “harness” DB and
the streaming-window DB, each instrumented with logging.
Includes a minimal CLI for quick sanity checks.
"""

import sys
import logging
import argparse
from typing import Optional, Sequence, Union

import numpy as np
from scipy.spatial import cKDTree

# Configure root logger
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.ERROR,
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

OFFSET = 2  # row i ↦ n = i + OFFSET


class HarnessDatabase:
    """
    Immutable batch database. Embeddings never change order or size.
    Implicit mapping: row i ↦ integer n = i + OFFSET
    """

    def __init__(self, coords: np.ndarray, offset: int = OFFSET):
        if coords.dtype != np.float64:
            raise ValueError("coords must be float64")
        if coords.ndim != 2:
            raise ValueError("coords must be 2D")

        self.coords = coords
        self.offset = offset
        self.tree = cKDTree(coords)
        logger.info(
            f"HarnessDatabase initialized with {coords.shape[0]} points, "
            f"dimension {coords.shape[1]}, offset={self.offset}"
        )

    @classmethod
    def load(cls, coords_path: str, offset: int = OFFSET) -> "HarnessDatabase":
        logger.info(f"Loading harness coords from '{coords_path}'")
        coords = np.load(coords_path)
        return cls(coords, offset)

    def save(self, coords_path: str) -> None:
        logger.info(f"Saving harness coords to '{coords_path}'")
        np.save(coords_path, self.coords)

    def query_radius(
        self, point: Union[Sequence[float], np.ndarray], radius: float
    ) -> np.ndarray:
        pt = np.asarray(point, dtype=np.float64)
        logger.info(f"Querying harness radius={radius} around point={pt.tolist()}")
        idxs = self.tree.query_ball_point(pt, radius)
        result = np.array(idxs, dtype=np.int32) + self.offset
        logger.info(f"Found {len(result)} hits: {result.tolist()}")
        return result


class StreamingDatabase:
    """
    Sliding-window in-memory database. Window size capped at `window_size`.
    Explicit `indices` array so insert/delete never breaks n ↦ embedding mapping.
    """

    def __init__(self, window_size: int = 360, dims: Optional[int] = None):
        self.window_size = window_size
        self.indices = np.empty((0,), dtype=np.int32)
        self.coords = np.empty((0, dims), dtype=np.float64) if dims else None
        self.tree: Optional[cKDTree] = None
        logger.info(f"StreamingDatabase initialized (window_size={window_size}, dims={dims})")

    def add_point(self, n: int, coord: Union[Sequence[float], np.ndarray]) -> None:
        c = np.asarray(coord, dtype=np.float64).reshape(1, -1)
        if self.coords is None:
            self.coords = c
            logger.debug("Inferred embedding dimension from first point.")
        else:
            self.coords = np.vstack([self.coords, c])

        self.indices = np.append(self.indices, np.int32(n))
        logger.info(f"Added point n={n}, coord={c.flatten().tolist()}")

        # Evict oldest if needed
        if len(self.indices) > self.window_size:
            evicted = len(self.indices) - self.window_size
            self.coords = self.coords[-self.window_size :]
            self.indices = self.indices[-self.window_size :]
            logger.info(f"Evicted {evicted} oldest point(s) to maintain window_size")

        # Rebuild tree
        self.tree = cKDTree(self.coords)
        logger.info(f"KD-tree rebuilt; now contains {len(self.indices)} points")

    def query_radius(
        self, point: Union[Sequence[float], np.ndarray], radius: float
    ) -> np.ndarray:
        if self.tree is None or self.tree.n == 0:
            logger.warning("Query on empty StreamingDatabase → returning []")
            return np.empty((0,), dtype=np.int32)

        pt = np.asarray(point, dtype=np.float64)
        logger.info(f"Querying stream radius={radius} around point={pt.tolist()}")
        idxs = self.tree.query_ball_point(pt, radius)
        result = self.indices[idxs]
        logger.info(f"Found {len(result)} hits: {result.tolist()}")
        return result


def main():
    p = argparse.ArgumentParser(
        description="Prime Hologram DB CLI: harness-query or stream-add/stream-query"
    )
    sub = p.add_subparsers(dest="command")

    # harness-query
    hq = sub.add_parser("harness-query", help="Query the static harness DB")
    hq.add_argument("--coords", required=True, help="Path to .npy coords file")
    hq.add_argument(
        "--point", required=True, nargs="+", type=float, help="Embedding to query"
    )
    hq.add_argument("--radius", required=True, type=float, help="Search radius")

    # stream-add
    sa = sub.add_parser("stream-add", help="Add a point to the streaming DB")
    sa.add_argument("--n", required=True, type=int, help="Integer label")
    sa.add_argument(
        "--coord",
        required=True,
        nargs="+",
        type=float,
        help="Embedding to add (space-separated)",
    )
    sa.add_argument(
        "--window-size",
        type=int,
        default=360,
        help="Max window size (default: 360)",
    )

    # stream-query
    sq = sub.add_parser("stream-query", help="Query the streaming DB")
    sq.add_argument(
        "--point", required=True, nargs="+", type=float, help="Embedding to query"
    )
    sq.add_argument("--radius", required=True, type=float, help="Search radius")
    sq.add_argument(
        "--window-size",
        type=int,
        default=360,
        help="Max window size (default: 360)",
    )

    args = p.parse_args()

    if args.command == "harness-query":
        db = HarnessDatabase.load(args.coords)
        db.query_radius(args.point, args.radius)

    elif args.command == "stream-add":
        # For simplicity, keep a single DB instance per execution
        db = StreamingDatabase(window_size=args.window_size, dims=len(args.coord))
        db.add_point(args.n, args.coord)

    elif args.command == "stream-query":
        # You’d normally persist `db` across calls; here we just demo
        db = StreamingDatabase(window_size=args.window_size, dims=len(args.point))
        logger.warning("No points added yet—stream-query will be empty")
        db.query_radius(args.point, args.radius)

    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
