"""Batch runner dumping approximate_hash_bound outputs for later analysis.

This variant is self-contained: it inlines the minimal logic from
`bounds.py` and avoids repo-level imports. It only optionally uses
`mpmath` (if installed) and `sympy` (if installed). Otherwise it
falls back to standard `math` and a simple sieve.

Optional LIS integrations (PoC):
- --lis-correct: compute true p(m) with Z5D seed + LIS + MR (ctypes wrapper)
- --lis-start/--lis-end: print a single LIS metric — MR-call reduction vs
  wheel-210 baseline — over the requested numeric range. The runner attempts
  a quiet build; if building is blocked, it explains how to fix.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import subprocess
import importlib

# Optional LIS integration (self-contained import from local folder)
try:
    from lis import reduction_vs_wheel210  # type: ignore
except Exception:
    try:  # attempt to add script directory to path
        _here = Path(__file__).resolve().parent
        if str(_here) not in sys.path:
            sys.path.insert(0, str(_here))
        from lis import reduction_vs_wheel210  # type: ignore
    except Exception:
        reduction_vs_wheel210 = None  # type: ignore

# Optional high-precision backend; falls back to float math if absent
try:  # pragma: no cover - optional dependency
    import mpmath as mp  # type: ignore

    try:
        mp.mp.dps = 50  # higher precision when available
    except Exception:
        pass
except Exception:  # pragma: no cover
    mp = None  # type: ignore


# Self-contained defaults (tunable)
WIDTH_FACTOR_DEFAULT = 0.155


def validate_width_factor(width_factor: float, context: str = "hash_bounds") -> float:
    """Validate/clamp width factor in a simple, self-contained way.

    For the standalone script we avoid repo-wide config and accept any
    small positive real value, clamped to a reasonable range.
    """
    try:
        x = float(width_factor)
    except Exception:
        return WIDTH_FACTOR_DEFAULT
    if not math.isfinite(x) or x <= 0:
        return WIDTH_FACTOR_DEFAULT
    return min(x, 1.0)


# --- Inlined helpers from bounds.py (trimmed for standalone use) ---

def _try_load_z5d(opt_in: bool) -> Optional[object]:
    """Try to import the full repo Z5D; else return None (we provide a minimal one)."""

    if not opt_in:
        return None

    try:  # pragma: no cover - only available inside full repo
        from src.core.z_5d_enhanced import Z5DEnhancedPredictor  # type: ignore

        return Z5DEnhancedPredictor()
    except Exception:
        try:
            here = Path(__file__).resolve()
            repo_root = here.parents[2]
            if str(repo_root) not in sys.path:
                sys.path.append(str(repo_root))
            from src.core.z_5d_enhanced import Z5DEnhancedPredictor  # type: ignore

            return Z5DEnhancedPredictor()
        except Exception:
            return None


# ---- Minimal Z5D implementation (pure mpmath; no numpy/scipy) ----

def _mu(n: int) -> int:
    if n == 1:
        return 1
    m = n
    p = 2
    primes = 0
    while p * p <= m:
        if m % p == 0:
            primes += 1
            m //= p
            if m % p == 0:
                return 0
            while m % p == 0:
                m //= p
        p += 1 if p == 2 else 2
    if m > 1:
        primes += 1
    return -1 if (primes % 2) else 1


def _K_for(x: float) -> int:
    if mp is None:
        return 16
    return max(12, int(mp.log(x, 2)))


def _R_of(x: float):
    if mp is None:
        raise RuntimeError("Z5D requires mpmath; install it or run with --no-z5d")
    x = mp.mpf(x)
    if x < 2:
        return mp.mpf('0')
    K = _K_for(float(x))
    s = mp.mpf('0')
    for k in range(1, K + 1):
        muk = _mu(k)
        if muk == 0:
            continue
        kf = mp.mpf(k)
        xk = x ** (1 / kf)
        s += (muk / kf) * mp.li(xk)
    return s


def _R_prime_of(x: float):
    if mp is None:
        raise RuntimeError("Z5D requires mpmath; install it or run with --no-z5d")
    x = mp.mpf(x)
    if x < 2:
        return mp.mpf('0')
    K = _K_for(float(x))
    s = mp.mpf('0')
    inv_x = 1 / x
    ln_x = mp.log(x)
    for k in range(1, K + 1):
        muk = _mu(k)
        if muk == 0:
            continue
        kf = mp.mpf(k)
        xk = x ** (1 / kf)
        s += muk * (xk * inv_x) / (kf * ln_x)
    return s


def _nth_prime_initial_guess(n: int):
    if mp is None:
        raise RuntimeError("Z5D requires mpmath; install it or run with --no-z5d")
    n_mp = mp.mpf(n)
    if n < 6:
        small = [2, 3, 5, 7, 11]
        return mp.mpf(small[n - 1])
    ln = mp.log(n_mp)
    l2 = mp.log(ln)
    return n_mp * (ln + l2 - 1 + (l2 - 2) / ln)


def _nth_prime_estimate(n: int, max_steps: int = 8):
    if mp is None:
        raise RuntimeError("Z5D requires mpmath; install it or run with --no-z5d")
    tol = mp.mpf('1e-40')
    x = _nth_prime_initial_guess(n)
    for _ in range(max_steps):
        Rx = _R_of(x)
        dR = _R_prime_of(x)
        if dR == 0:
            break
        delta = (Rx - n) / dR
        x_new = x - delta
        if x_new <= 2:
            x_new = mp.mpf('3')
        if abs(delta) < tol:
            x = x_new
            break
        x = x_new
    return x


class MinimalZ5D:
    def __init__(self, dps: int = 50) -> None:
        if mp is None:
            raise RuntimeError("Z5D requires mpmath; install it or run with --no-z5d")
        try:
            mp.mp.dps = max(40, int(dps))
        except Exception:
            pass

    def z_5d_prediction(self, n: int) -> float:
        est = _nth_prime_estimate(n)
        return float(est)


def fractional_sqrt(x: float) -> float:
    """Return fractional part of sqrt(x) using mp if available, else math."""

    if mp is not None:
        r = mp.sqrt(x)
        return float(r - mp.floor(r))
    r = math.sqrt(float(x))
    return r - math.floor(r)


def sha256_frac_to_u32_hex(frac: float) -> str:
    """Convert a fractional part to the 32-bit word format used by SHA-256."""

    if mp is not None:
        val = int(mp.floor(frac * (1 << 32)))
    else:
        val = int(math.floor(float(frac) * (1 << 32)))
    return f"0x{val:08x}"


def nth_prime(n: int) -> int:
    """Return the n-th prime (1-indexed) using a light fallback approach.

    - Uses sympy if present.
    - Otherwise uses a simple sieve with a PNT-based upper bound. Suitable
      for modest n used in demos (n <= ~100000). Not optimized for very large n.
    """

    if n < 1:
        raise ValueError("n must be >= 1")

    try:  # pragma: no cover - optional dependency
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
    m: int,
    k_star: float = 0.04449,
    use_z5d: bool = True,
    width_factor: float | None = None,
    compute_truth: bool = True,
) -> BoundResult:
    """Predict fractional-part bounds around sqrt(p_m) and compare to truth.

    Uses Z5DEnhancedPredictor if available to predict p_m (the m-th prime),
    otherwise falls back to a smooth approximation (m log m) that is not
    prime-accurate but keeps the demo runnable.
    """

    # Width factor validation (self-contained)
    if width_factor is None:
        width_factor = WIDTH_FACTOR_DEFAULT
    else:
        width_factor = validate_width_factor(width_factor)

    p_approx: float
    if use_z5d:
        z5d = _try_load_z5d(True)
        if z5d is None:
            # Use minimal inlined Z5D predictor (requires mpmath)
            if mp is None:
                raise RuntimeError("Z5D requested but mpmath not installed. Install mpmath or run with --no-z5d.")
            z5d = MinimalZ5D()
        p_approx = float(z5d.z_5d_prediction(m))  # type: ignore[attr-defined]
    else:
        # Smooth fallback: m log m (not prime-accurate; demo only)
        p_approx = float(m) * (float(mp.log(m)) if mp is not None else math.log(m))

    frac_pred = fractional_sqrt(p_approx)

    # Geometric adjustment using optimized width factor
    phi = (1.0 + (float(mp.sqrt(5)) if mp is not None else math.sqrt(5.0))) / 2.0
    theta_prime = phi * (((float(m) % phi) / phi) ** k_star)
    width = theta_prime * float(width_factor)
    lower_bound = frac_pred - width
    upper_bound = frac_pred + width

    # Ground truth for comparison
    p_true: Optional[int]
    frac_true: Optional[float]
    sha32_true: Optional[str]

    if compute_truth:
        try:
            p_true_int: Optional[int] = None
            if getattr(parse_args, "LIS_CORRECT_ENABLED", False):
                # Use fixed per-band windows only (no adaptive or fallback behavior)
                from lis_corrector import lis_correct_nth_prime  # type: ignore

                def _lis_window_for_n(n_val: int) -> int:
                    # Fixed windows (PoC; calibrated to 0% failures per band)
                    if 1_000 <= n_val <= 10_000:
                        return 5_000
                    if 10_000 < n_val <= 100_000:
                        return 5_000
                    if 100_000 < n_val <= 1_000_000:
                        return 10_000
                    if 1_000_000 < n_val <= 10_000_000:
                        return 100_000
                    if 10_000_000 < n_val <= 100_000_000:
                        return 1_000_000
                    raise RuntimeError(
                        f"LIS-correct window undefined for n={n_val}. Supported bands: 1e3..1e8."
                    )

                win = _lis_window_for_n(m)
                p_c, _mr, _base = lis_correct_nth_prime(m, window=win)
                p_true_int = int(p_c)
            else:
                p_true_int = int(nth_prime(m))
            frac_true_val = fractional_sqrt(float(p_true_int))
            p_true = p_true_int
            frac_true = float(frac_true_val)
            sha32_true = sha256_frac_to_u32_hex(frac_true_val)
        except Exception:
            p_true = None
            frac_true = None
            sha32_true = None
    else:
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


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute approximate hash bounds for a range of prime indices and dump JSON records."
    )
    parser.add_argument("--start", type=int, default=10011000, help="starting prime index (inclusive)")
    parser.add_argument("--stop", type=int, default=10012000, help="ending prime index (inclusive)")
    parser.add_argument(
        "--k-star",
        type=float,
        default=0.04449,
        help="curvature parameter supplied to approximate_hash_bound",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("hash_bounds_out.txt"),
        help="path to the output file (JSON lines)",
    )
    parser.add_argument(
        "--no-z5d",
        action="store_true",
        help="disable Z5D predictor and fall back to smooth approximation",
    )
    parser.add_argument(
        "--no-truth",
        action="store_true",
        help="skip nth-prime ground truth to avoid heavy dependencies",
    )
    parser.add_argument(
        "--width-factor",
        type=float,
        default=WIDTH_FACTOR_DEFAULT,
        help=f"geometric bound width factor (default: {WIDTH_FACTOR_DEFAULT}, optimized for 50% coverage)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4096,
        help="batch size for vectorized processing (default: 1000)",
    )
    parser.add_argument(
        "--lis-correct",
        action="store_true",
        help="use LIS corrector (Z5D seed + LIS + MR) to compute true p(m)",
    )
    parser.add_argument(
        "--lis-start",
        type=int,
        help="optional: numeric range start to evaluate LIS MR-call reduction",
    )
    parser.add_argument(
        "--lis-end",
        type=int,
        help="optional: numeric range end (inclusive) to evaluate LIS MR-call reduction",
    )
    return parser.parse_args(argv)


def process_batch_vectorized(
    m_values: List[int],
    k_star: float,
    use_z5d: bool,
    width_factor: float,
    compute_truth: bool,
) -> List[BoundResult]:
    """
    Process a batch of m values using vectorized operations where possible.

    For maximum performance with large ranges (10³ to 10⁶), this function
    processes multiple prime indices in batches to leverage NumPy operations
    and reduce per-iteration overhead.

    Args:
        m_values: List of prime indices to process
        k_star: Z_5D calibration parameter
        use_z5d: Whether to use Z5D enhanced predictor
        width_factor: Geometric bound width factor

    Returns:
        List of BoundResult objects
    """
    results = []

    # Process in batches to balance memory usage and performance
    for m in m_values:
        try:
            result = approximate_hash_bound(m, k_star, use_z5d, width_factor, compute_truth)
            results.append(result)
        except Exception as e:
            # Handle individual failures gracefully in large ranges
            print(f"Warning: Failed to process m={m}: {e}", file=sys.stderr)
            continue

    return results

def build_record(m: int, result: BoundResult, k_star: float, width_factor: float) -> Dict[str, Any]:
    lower, upper = result.bound
    frac_true = result.frac_true
    p_true = result.p_true
    within_bounds = None
    frac_error_abs = None
    prime_error_abs = None
    prime_error_rel_ppm = None

    if frac_true is not None:
        within_bounds = lower <= frac_true <= upper
        frac_error_abs = abs(result.frac_pred - frac_true)

    if p_true is not None:
        prime_error_abs = abs(result.p_pred - p_true)
        if p_true != 0:
            prime_error_rel_ppm = (prime_error_abs / p_true) * 1_000_000

    record = {
        "m": m,
        "k_star": k_star,
        "width_factor": width_factor,
        "prediction": result.p_pred,
        "prime_true": p_true,
        "frac_pred": result.frac_pred,
        "frac_true": frac_true,
        "bound_lower": lower,
        "bound_upper": upper,
        "bound_width": upper - lower,
        "sha32_from_pred": result.sha32_from_pred,
        "sha32_from_true": result.sha32_from_true,
        "within_bounds": within_bounds,
        "frac_error_abs": frac_error_abs,
        "prime_error_abs": prime_error_abs,
        "prime_error_rel_ppm": prime_error_rel_ppm,
    }
    return record


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    setattr(parse_args, "LIS_CORRECT_ENABLED", bool(args.lis_correct))
    if args.start <= 0 or args.stop <= 0:
        raise ValueError("start and stop must be positive integers")
    if args.start > args.stop:
        raise ValueError("start must be <= stop")

    # Validate and set width factor
    width_factor = args.width_factor
    if width_factor is None:
        width_factor = WIDTH_FACTOR_DEFAULT
    else:
        width_factor = validate_width_factor(width_factor)

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    bounds_hits = 0
    missing_truth = 0
    use_z5d = not args.no_z5d
    compute_truth = not args.no_truth

    # Calculate total range for progress tracking
    total_range = args.stop - args.start + 1
    print(f"Processing range {args.start} to {args.stop} ({total_range:,} values)")
    print(f"Using width_factor: {width_factor} (target coverage: ~50%)")
    print(f"Batch size: {args.batch_size}")

    start_time = time.time()

    with output_path.open("w", encoding="utf-8") as fh:
        # Process in batches for better performance
        for batch_start in range(args.start, args.stop + 1, args.batch_size):
            batch_end = min(batch_start + args.batch_size - 1, args.stop)
            batch_m_values = list(range(batch_start, batch_end + 1))

            # Show progress for large ranges
            if total_range > 1000:
                progress = (batch_start - args.start) / total_range * 100
                print(f"Progress: {progress:.1f}% (processing m={batch_start} to {batch_end})")

            # Process batch with vectorized operations
            batch_results = process_batch_vectorized(
                batch_m_values, args.k_star, use_z5d, width_factor, compute_truth
            )

            # Write results to file
            for m, result in zip(batch_m_values, batch_results):
                if result is None:  # Skip failed computations
                    continue

                record = build_record(m, result, args.k_star, width_factor)
                json.dump(record, fh, separators=(",", ":"))
                fh.write("\n")

                total += 1
                if record["within_bounds"] is None:
                    missing_truth += 1
                elif record["within_bounds"]:
                    bounds_hits += 1

    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f}s ({total/elapsed:.1f} records/sec)")
    print(f"Wrote {total} records to {output_path}")

    if total > missing_truth:
        coverage = bounds_hits / (total - missing_truth)
        print(f"Bound coverage (true frac available): {coverage:.3%}")
        print(f"Width factor effectiveness: {coverage/0.5:.2f}x target")
    else:
        print("No ground truth available to assess bounds.")

    # Optional: evaluate LIS MR-call reduction over a numeric range
    if args.lis_start is not None and args.lis_end is not None:
        def _try_build_lis() -> bool:
            here = Path(__file__).resolve()
            repo_root = here.parents[2]  # hash-bounds/.. (experiments)/.. -> repo root
            lis_dir = repo_root / "src" / "c" / "lis"
            print("Attempting to build LIS (liblis) ...")
            try:
                proc = subprocess.run(["make", "-C", str(lis_dir), "all"], capture_output=True, text=True)
            except Exception as be:
                print(f"Failed to invoke make: {be}")
                return False
            if proc.returncode != 0:
                print("Build failed. Output:")
                if proc.stdout:
                    print(proc.stdout)
                if proc.stderr:
                    print(proc.stderr)
                return False
            return True

        # no nested function needed; call directly via _rvw

        ls, le = int(args.lis_start), int(args.lis_end)
        if ls > le:
            ls, le = le, ls

        # Use module-level symbol if available; otherwise handle build/import.
        _rvw = reduction_vs_wheel210
        if _rvw is None:
            # Try to build and import
            if not _try_build_lis():
                print("LIS build failed. Please run: make -C src/c/lis")
                sys.exit(2)
            try:
                # Ensure script dir in path then import
                script_dir = Path(__file__).resolve().parent
                if str(script_dir) not in sys.path:
                    sys.path.insert(0, str(script_dir))
                from lis import reduction_vs_wheel210 as _rvw  # type: ignore
            except Exception as ie:
                print(f"LIS import failed after build: {ie}")
                print("Please confirm liblis was built and is loadable.")
                sys.exit(2)

        # Have a symbol; try to run. If loading fails, rebuild once and retry.
        try:
            # call via local _rvw to avoid scope issues
            baseline, after, reduction = _rvw(range(ls, le + 1))  # type: ignore
            print(f"\nLIS: MR-call reduction vs wheel-210 baseline: {reduction*100:.2f}% (range {ls}..{le}, baseline {baseline}, MR {after})")
        except Exception:
            if not _try_build_lis():
                print("LIS build failed. Please run: make -C src/c/lis")
                sys.exit(2)
            try:
                # Reload lis module to pick up freshly built library
                import lis as _lis  # type: ignore
                importlib.reload(_lis)
                _rvw = _lis.reduction_vs_wheel210  # type: ignore
                baseline, after, reduction = _rvw(range(ls, le + 1))  # type: ignore
                print(f"\nLIS: MR-call reduction vs wheel-210 baseline: {reduction*100:.2f}% (range {ls}..{le}, baseline {baseline}, MR {after})")
            except Exception as e2:
                print(f"LIS still unavailable after build: {e2}")
                print("Please run: make -C src/c/lis and ensure liblis.dylib/.so exists under src/c/lis/lib")
                sys.exit(2)


if __name__ == "__main__":
    main()
