"""
Obfuscation is Not Security

This PoC relates prime-derived fractional parts to the way SHA-256
builds its "nothing up my sleeve" constants (fractional parts of square
and cube roots of small primes). It shows predictions alongside
ground truth, then maps a fractional part to a 32-bit word as SHA-256 does.

Caveats
- This is for educational purposes only.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from typing import Optional, Tuple

import mpmath as mp

# Try to import centralized parameters
try:
    from pathlib import Path
    # Add repo root to path for imports
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    if str(repo_root) not in sys.path:
        sys.path.append(str(repo_root))
    from src.core.params import WIDTH_FACTOR_DEFAULT, validate_width_factor
except ImportError:
    # Fallback for when params are not available
    WIDTH_FACTOR_DEFAULT = 0.155
    def validate_width_factor(width_factor, context="hash_bounds"):
        return width_factor

# Ultra-high precision to preserve tiny fractional differences
mp.mp.dps = 50


def _try_load_z5d(opt_in: bool) -> Optional[object]:
    """Optionally import Z5DEnhancedPredictor without hard failure.

    By default, avoids importing to keep the demo fast and dependency-light.
    Only attempts import when `opt_in` is True.
    """

    if not opt_in:
        return None

    try:
        from src.core.z_5d_enhanced import Z5DEnhancedPredictor  # type: ignore

        return Z5DEnhancedPredictor()
    except Exception:
        # Try adding repo root (two levels up from experiments/hash-bounds)
        # so `src/` becomes importable when running this file directly.
        try:
            from pathlib import Path

            here = Path(__file__).resolve()
            repo_root = here.parents[2]
            if str(repo_root) not in sys.path:
                sys.path.append(str(repo_root))
            from src.core.z_5d_enhanced import (  # type: ignore
                Z5DEnhancedPredictor,
            )

            return Z5DEnhancedPredictor()
        except Exception:
            return None


def fractional_sqrt(x: mp.mpf) -> mp.mpf:
    """Return fractional part of sqrt(x) with high precision."""

    r = mp.sqrt(x)
    return r - mp.floor(r)


def sha256_frac_to_u32_hex(frac: mp.mpf) -> str:
    """Convert a fractional part to the 32-bit word format used by SHA-256.

    SHA-256 constants take floor(frac * 2^32) and render as 8-hex digits.
    """

    val = int(mp.floor(frac * (1 << 32)))
    return f"0x{val:08x}"


def nth_prime(n: int) -> int:
    """Return the n-th prime (1-indexed) using a light fallback approach.

    - Uses sympy if present.
    - Otherwise uses a simple sieve with a PNT-based upper bound. Suitable
      for modest n used in demos (n <= ~100000). Not optimized for very large n.
    """

    if n < 1:
        raise ValueError("n must be >= 1")

    try:
        import sympy as sp  # type: ignore

        return int(sp.prime(n))
    except Exception:
        pass

    if n == 1:
        return 2

    # Rosser Schoenfeld upper bound for n >= 6: n(log n + log log n)
    # Add a small safety margin and handle small n directly.
    if n < 6:
        # Primes: 2, 3, 5, 7, 11
        small = [2, 3, 5, 7, 11]
        return small[n - 1]

    nn = float(n)
    upper = int(nn * (math.log(nn) + math.log(math.log(nn))) + 10)

    # Simple sieve up to `upper`
    sieve = bytearray(b"\x01") * (upper + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(upper**0.5) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : upper + 1 : step] = b"\x00" * ((upper - start) // step + 1)

    primes = [i for i, v in enumerate(sieve) if v]
    if len(primes) < n:
        # Very unlikely for demo ranges; fall back to a naive extension
        candidate = upper + 1
        while len(primes) < n:
            is_prime = True
            r = int(candidate**0.5)
            for p in primes:
                if p > r:
                    break
                if candidate % p == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(candidate)
            candidate += 1
    return primes[n - 1]


@dataclass
class BoundResult:
    p_pred: float
    p_true: Optional[int]
    frac_pred: float
    frac_true: Optional[float]
    bound: Tuple[float, float]
    sha32_from_pred: str
    sha32_from_true: Optional[str]


def approximate_hash_bound(
    m: int, k_star: float = 0.04449, use_z5d: bool = False, width_factor: float = None
) -> BoundResult:
    """Predict fractional-part bounds around sqrt(p_m) and compare to truth.

    Uses Z5DEnhancedPredictor if available to predict p_m (the m-th prime),
    otherwise falls back to a smooth approximation (m log m) that is not
    prime-accurate but keeps the demo runnable.

    Args:
        m: Prime index
        k_star: Z_5D calibration parameter
        use_z5d: Whether to use Z5D enhanced predictor
        width_factor: Geometric bound width factor (uses optimized default if None)
    """

    # Use centralized width factor with validation
    if width_factor is None:
        width_factor = WIDTH_FACTOR_DEFAULT
    else:
        width_factor = validate_width_factor(width_factor)

    z5d = _try_load_z5d(use_z5d)

    if z5d is not None:
        p_approx = mp.mpf(z5d.z_5d_prediction(m))  # type: ignore[attr-defined]
    else:
        # Smooth fallback: m log m (not prime-accurate; demo only)
        p_approx = mp.mpf(m) * mp.log(m)

    frac_pred = fractional_sqrt(p_approx)

    # Geometric adjustment using optimized width factor
    phi = (1 + mp.sqrt(5)) / 2
    theta_prime = phi * ((mp.mpf(m) % phi / phi) ** k_star)
    width = theta_prime * mp.mpf(width_factor)
    lower_bound = frac_pred - width
    upper_bound = frac_pred + width

    # Ground truth for comparison
    p_true: Optional[int]
    frac_true: Optional[float]
    sha32_true: Optional[str]

    try:
        p_true = int(nth_prime(m))
        frac_true_mp = fractional_sqrt(mp.mpf(p_true))
        frac_true = float(frac_true_mp)
        sha32_true = sha256_frac_to_u32_hex(frac_true_mp)
    except Exception:
        p_true = None
        frac_true = None
        sha32_true = None

    return BoundResult(
        p_pred=float(p_approx),
        p_true=p_true,
        frac_pred=float(frac_pred),
        frac_true=frac_true,
        bound=(float(lower_bound), float(upper_bound)),
        sha32_from_pred=sha256_frac_to_u32_hex(frac_pred),
        sha32_from_true=sha32_true,
    )


def _demo_sha256_iv() -> None:
    """Show how SHA-256 initial hash words derive from sqrt(primes).

    H0..H7 come from fractional parts of sqrt of the first 8 primes.
    Prints the computed 32-bit words to illustrate the linkage.
    """

    first_8_primes = [nth_prime(i) for i in range(1, 9)]
    words = []
    for p in first_8_primes:
        frac = fractional_sqrt(mp.mpf(p))
        words.append(sha256_frac_to_u32_hex(frac))
    print("SHA-256 IV words (from frac(sqrt(prime))):")
    print(" ".join(words))


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Geometric demo around fractional parts of sqrt(p_m) with a "
            "SHA-256 constants linkage."
        )
    )
    parser.add_argument("m", type=int, nargs="?", default=10, help="prime index m")
    parser.add_argument(
        "--k-star",
        type=float,
        default=0.04449,
        help="curvature parameter for illustrative bound width",
    )
    parser.add_argument(
        "--use-z5d",
        action="store_true",
        help="use Z5DEnhancedPredictor (slower, requires project deps)",
    )
    parser.add_argument(
        "--width-factor",
        type=float,
        default=None,
        help=f"geometric bound width factor (default: {WIDTH_FACTOR_DEFAULT}, optimized for 50%% coverage)",
    )
    parser.add_argument(
        "--show-sha256-iv",
        action="store_true",
        help="also print the 8 IV words from sqrt(primes)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    res = approximate_hash_bound(args.m, args.k_star, use_z5d=args.use_z5d, width_factor=args.width_factor)

    print("Geometric Fractional-Part Demo (educational)")
    if res.p_true is not None:
        print(
            f"p_m (pred/true): {res.p_pred:.6f} / {res.p_true}"
        )
    else:
        print(f"p_m (pred): {res.p_pred:.6f} (true unavailable)")

    print(f"frac(sqrt(p_m)) pred: {res.frac_pred:.12f}")
    if res.frac_true is not None:
        print(f"frac(sqrt(p_m)) true: {res.frac_true:.12f}")

    lb, ub = res.bound
    print(f"illustrative bound: [{lb:.12f}, {ub:.12f}] (width={ub - lb:.12e})")

    print(f"SHA-256 word from pred frac: {res.sha32_from_pred}")
    if res.sha32_from_true is not None:
        print(f"SHA-256 word from true frac: {res.sha32_from_true}")

    if args.show_sha256_iv:
        print()
        _demo_sha256_iv()


if __name__ == "__main__":
    main()
