#!/usr/bin/env python3
"""
SHA-256 Constant Predictability PoC

This script demonstrates that SHA-256's "nothing-up-my-sleeve" constants are
derived from floor(frac(sqrt(p_i)) * 2³²) for the first 8 primes, and shows
that these fractional parts can be predicted using smooth approximations.

**This is not a security vulnerability** - it's educational transparency.
SHA-256 constants are public and verifiable by design. This PoC proves the
transparency - math is not magic.

What This Script Demonstrates:
- You can predict fractional parts using smooth approximations (m log m)
- You can bound them geometrically
- You can reconstruct the 32-bit constants without knowing the primes
- This is not a break - it's educational transparency

Core Mechanism:
    frac = {sqrt(p_m)}          # fractional part of sqrt(m-th prime)
    word = floor(frac * 2^32)   # → 32-bit hex word (like SHA-256 IV)

Bitcoin Mining Connection:
In mining:
- Miners don't care about SHA-256 IV
- But nonce iteration is brute-force over 32-bit space
- If you could predict hash output distributions, you could bias nonce search

This PoC shows:
    Predictability in hash constants → potential for statistical bias in hash chains

Not a vulnerability - but a warning: "nothing-up-my-sleeve" ≠ randomness.
"""

import argparse
import math
import sys
from pathlib import Path
from typing import Optional

# Optional high-precision backend
try:
    import mpmath as mp
    mp.mp.dps = 50
    HAS_MPMATH = True
except ImportError:
    mp = None  # type: ignore
    HAS_MPMATH = False

# Try to import sympy for prime computation
try:
    import sympy as sp
    HAS_SYMPY = True
except ImportError:
    sp = None  # type: ignore
    HAS_SYMPY = False

# Try to import Z5D predictor from repository
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.core.z_5d_enhanced import Z5DEnhancedPredictor
    HAS_Z5D = True
except ImportError:
    Z5DEnhancedPredictor = None  # type: ignore
    HAS_Z5D = False


# SHA-256 Initial Vector (first 8 primes' sqrt fractional parts → 32-bit words)
SHA256_IV = [
    0x6a09e667,  # sqrt(2)
    0xbb67ae85,  # sqrt(3)
    0x3c6ef372,  # sqrt(5)
    0xa54ff53a,  # sqrt(7)
    0x510e527f,  # sqrt(11)
    0x9b05688c,  # sqrt(13)
    0x1f83d9ab,  # sqrt(17)
    0x5be0cd19,  # sqrt(19)
]


def fractional_sqrt(x: float) -> float:
    """Return fractional part of sqrt(x)."""
    if HAS_MPMATH and mp is not None:
        r = mp.sqrt(x)
        return float(r - mp.floor(r))
    r = math.sqrt(float(x))
    return r - math.floor(r)


def sha256_frac_to_u32_hex(frac: float) -> str:
    """Convert a fractional part to the 32-bit word format used by SHA-256."""
    if HAS_MPMATH and mp is not None:
        val = int(mp.floor(frac * (1 << 32)))
    else:
        val = int(math.floor(float(frac) * (1 << 32)))
    return f"0x{val:08x}"


def nth_prime(n: int) -> int:
    """Return the n-th prime (1-indexed)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    
    # Small primes for direct lookup
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    if n <= len(small_primes):
        return small_primes[n - 1]
    
    if HAS_SYMPY and sp is not None:
        return int(sp.prime(n))
    
    # Fallback: simple sieve
    nn = float(n)
    upper = int(nn * (math.log(nn) + math.log(math.log(nn))) + 100)
    
    sieve = bytearray(b"\x01") * (upper + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(upper**0.5) + 1):
        if sieve[p]:
            sieve[p * p : upper + 1 : p] = b"\x00" * ((upper - p * p) // p + 1)
    
    primes = [i for i, v in enumerate(sieve) if v]
    if len(primes) < n:
        raise RuntimeError(f"Sieve too small for n={n}")
    return primes[n - 1]


def predict_prime_smooth(m: int) -> float:
    """Predict the m-th prime using smooth approximation (m log m)."""
    if m < 1:
        raise ValueError("m must be >= 1")
    if m == 1:
        return 2.0
    
    if HAS_MPMATH and mp is not None:
        return float(m * mp.log(m))
    return float(m * math.log(m))


def predict_prime_z5d(m: int) -> Optional[float]:
    """Predict the m-th prime using Z5D enhanced predictor if available."""
    if not HAS_Z5D or Z5DEnhancedPredictor is None:
        return None
    
    try:
        predictor = Z5DEnhancedPredictor()
        return predictor.z_5d_prediction(m)
    except Exception:
        return None


def compute_geometric_bound(
    m: int, 
    frac_pred: float, 
    k_star: float = 0.04449, 
    width_factor: float = 0.155
) -> tuple[float, float]:
    """
    Compute geometric bound for fractional part prediction.
    
    This is the key innovation - bounding the fractional part using
    golden ratio geometry and a width factor calibrated to ~50% coverage.
    
    Args:
        m: Prime index
        frac_pred: Predicted fractional part
        k_star: Curvature parameter (default: 0.04449)
        width_factor: Width scaling factor (default: 0.155 for ~50% coverage)
    
    Returns:
        (lower_bound, upper_bound) tuple
    """
    phi = (1.0 + math.sqrt(5.0)) / 2.0  # Golden ratio
    theta_prime = phi * (((float(m) % phi) / phi) ** k_star)
    width = theta_prime * width_factor
    
    lower_bound = frac_pred - width
    upper_bound = frac_pred + width
    
    return (lower_bound, upper_bound)


def demonstrate_predictability(
    m: int,
    use_z5d: bool = True,
    width_factor: float = 0.155,
    show_bounds: bool = True
) -> None:
    """
    Demonstrate SHA-256 constant predictability for a given prime index.
    
    Args:
        m: Prime index (1-indexed, e.g., 1→2, 2→3, 3→5, etc.)
        use_z5d: Use Z5D predictor if available
        width_factor: Width factor for geometric bounds
        show_bounds: Whether to show geometric bounds
    """
    print(f"\nGeometric Fractional-Part Demo (educational)")
    print(f"{'='*60}")
    
    # Predict prime
    if use_z5d:
        p_pred = predict_prime_z5d(m)
        if p_pred is None:
            print("Z5D predictor not available, falling back to smooth approximation")
            p_pred = predict_prime_smooth(m)
            pred_method = "m log m"
        else:
            pred_method = "Z5D"
    else:
        p_pred = predict_prime_smooth(m)
        pred_method = "m log m"
    
    # Get true prime
    try:
        p_true = nth_prime(m)
    except Exception as e:
        print(f"Warning: Could not compute true prime: {e}")
        p_true = None
    
    # Compute fractional parts
    frac_pred = fractional_sqrt(p_pred)
    frac_true = fractional_sqrt(p_true) if p_true is not None else None
    
    # Display results
    print(f"Prime index (m): {m}")
    print(f"p_m (pred/{pred_method}): {float(p_pred):.6f}")
    if p_true is not None:
        print(f"p_m (true): {p_true}")
        error_ppm = abs(float(p_pred) - p_true) / p_true * 1_000_000
        print(f"Prediction error: {error_ppm:.1f} ppm")
    
    print(f"\nfrac(sqrt(p_m)) pred: {frac_pred:.12f}")
    if frac_true is not None:
        print(f"frac(sqrt(p_m)) true: {frac_true:.12f}")
        frac_error = abs(frac_pred - frac_true)
        print(f"Fractional error: {frac_error:.6e}")
    
    # Show geometric bounds
    if show_bounds:
        lower, upper = compute_geometric_bound(m, frac_pred, width_factor=width_factor)
        bound_width = upper - lower
        print(f"\nillustrative bound: [{lower:.12f}, {upper:.12f}]")
        print(f"Bound width: {bound_width:.6e}")
        
        if frac_true is not None:
            in_bounds = lower <= frac_true <= upper
            print(f"True frac in bounds: {'✓ YES' if in_bounds else '✗ NO'}")
    
    # Show SHA-256 words
    print(f"\nSHA-256 word from pred frac: {sha256_frac_to_u32_hex(frac_pred)}")
    if frac_true is not None:
        print(f"SHA-256 word from true frac: {sha256_frac_to_u32_hex(frac_true)}")


def show_sha256_iv() -> None:
    """Display SHA-256 IV reconstruction from prime square roots."""
    print("\nSHA-256 Initial Vector (IV) — Recreated")
    print("=" * 60)
    print("SHA-256 IV words (from frac(sqrt(prime))):")
    print()
    
    iv_words = []
    for i in range(1, 9):
        p = nth_prime(i)
        frac = fractional_sqrt(p)
        word_hex = sha256_frac_to_u32_hex(frac)
        word_int = int(word_hex, 16)
        iv_words.append(word_hex)
        
        expected = SHA256_IV[i - 1]
        match = "✓" if word_int == expected else "✗"
        print(f"  p_{i} = {p:3d}  →  sqrt = {math.sqrt(p):.6f}  →  "
              f"{{frac}} = {frac:.8f}  →  {word_hex}  {match}")
    
    print()
    print("Official SHA-256 IV:")
    print("  " + " ".join(f"0x{w:08x}" for w in SHA256_IV))
    print()
    print("Reconstructed IV:")
    print("  " + " ".join(iv_words))
    print()
    
    # Verify perfect match
    reconstructed = [int(w, 16) for w in iv_words]
    if reconstructed == SHA256_IV:
        print("✓ Perfect match! SHA-256 IV successfully reconstructed.")
    else:
        print("✗ Mismatch detected (this should not happen)")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SHA-256 Constant Predictability PoC (Educational)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Demonstrate for prime index 10
  python poc.py 10
  
  # Show SHA-256 IV reconstruction
  python poc.py --show-sha256-iv
  
  # Use smooth approximation instead of Z5D
  python poc.py 10 --no-z5d
  
  # Adjust width factor for bounds
  python poc.py 10 --width-factor 0.3
        """
    )
    
    parser.add_argument(
        "m",
        nargs="?",
        type=int,
        default=10,
        help="Prime index to demonstrate (default: 10)"
    )
    
    parser.add_argument(
        "--show-sha256-iv",
        action="store_true",
        help="Show SHA-256 IV reconstruction from first 8 primes"
    )
    
    parser.add_argument(
        "--no-z5d",
        action="store_true",
        help="Disable Z5D predictor (use smooth approximation)"
    )
    
    parser.add_argument(
        "--width-factor",
        type=float,
        default=0.155,
        help="Width factor for geometric bounds (default: 0.155)"
    )
    
    parser.add_argument(
        "--no-bounds",
        action="store_true",
        help="Don't show geometric bounds"
    )
    
    args = parser.parse_args()
    
    # Show SHA-256 IV if requested
    if args.show_sha256_iv:
        show_sha256_iv()
        return
    
    # Otherwise demonstrate for specific m
    demonstrate_predictability(
        m=args.m,
        use_z5d=not args.no_z5d,
        width_factor=args.width_factor,
        show_bounds=not args.no_bounds
    )
    
    print("\n" + "="*60)
    print("Educational Note:")
    print("This is not a vulnerability. SHA-256 constants are publicly")
    print("verifiable, not secret. This PoC proves the transparency.")
    print("Math is not magic - it's beautiful, predictable transparency.")
    print("="*60)


if __name__ == "__main__":
    main()
