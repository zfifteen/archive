# SHA-256 Constant Predictability PoC

## Overview

This proof-of-concept demonstrates that SHA-256's "nothing-up-my-sleeve" constants can be predicted and reconstructed through mathematical analysis. This is **not a security vulnerability** - it's educational transparency showing that cryptographic constants are publicly verifiable by design.

## What This PoC Demonstrates

1. **SHA-256 IV Derivation**: The initial vector (IV) constants in SHA-256 are derived from the fractional parts of square roots of the first 8 primes:
   ```
   frac = {sqrt(p_m)}          # fractional part of sqrt(m-th prime)
   word = floor(frac * 2^32)   # → 32-bit hex word (SHA-256 IV)
   ```

2. **Predictability**: These fractional parts can be approximated using smooth functions like `m log m` or advanced models like Z5DEnhancedPredictor.

3. **Geometric Bounds**: We can bound these fractional parts geometrically using golden ratio-based formulas.

4. **Transparency**: The constants are not secret - they're mathematically verifiable and transparent.

## Usage

### Basic Demo

Demonstrate predictability for a specific prime index:
```bash
python poc.py 10
```

### SHA-256 IV Reconstruction

Show how the official SHA-256 IV can be perfectly reconstructed:
```bash
python poc.py --show-sha256-iv
```

Output:
```
SHA-256 Initial Vector (IV) — Recreated
============================================================
SHA-256 IV words (from frac(sqrt(prime))):

  p_1 =   2  →  sqrt = 1.414214  →  {frac} = 0.41421356  →  0x6a09e667  ✓
  p_2 =   3  →  sqrt = 1.732051  →  {frac} = 0.73205081  →  0xbb67ae85  ✓
  ...
  
✓ Perfect match! SHA-256 IV successfully reconstructed.
```

### Options

- `--no-z5d`: Use smooth approximation (`m log m`) instead of Z5D predictor
- `--width-factor <float>`: Adjust geometric bound width (default: 0.155)
- `--no-bounds`: Don't show geometric bounds
- `--help`: Show full help message

## Examples

```bash
# Basic demonstration
python poc.py 10

# Show SHA-256 IV
python poc.py --show-sha256-iv

# Use smooth approximation
python poc.py 10 --no-z5d

# Wider bounds
python poc.py 10 --width-factor 0.3
```

## Bitcoin Mining Connection

In Bitcoin mining:
- Miners perform brute-force search over 32-bit nonce space
- SHA-256 constants are fixed and known
- **This PoC shows**: Predictability in hash constants → potential for understanding statistical distributions in hash chains

**Important**: This is not a vulnerability. The constants are public by design. This demonstrates transparency, not weakness.

## Dependencies

**Required**:
- Python 3.8+

**Optional** (enhances precision):
- `mpmath`: High-precision arithmetic
- `sympy`: Accurate prime computation
- Repository's `Z5DEnhancedPredictor`: Advanced prime prediction

The script will fall back gracefully if optional dependencies are missing.

## Mathematical Background

### SHA-256 Constants

SHA-256 uses "nothing-up-my-sleeve" numbers derived from:
- **IV (8 words)**: First 32 bits of fractional parts of square roots of first 8 primes
- **Round constants (64 words)**: First 32 bits of fractional parts of cube roots of first 64 primes

### Fractional Part Prediction

For the m-th prime p_m, we predict:
1. **Smooth approximation**: p_m ≈ m ln m  (where ln denotes the natural logarithm)
2. **Z5D prediction**: More accurate asymptotic estimate
3. **Fractional part**: frac(sqrt(p_m)) = sqrt(p_m) - floor(sqrt(p_m))

### Geometric Bounds

Using golden ratio φ = (1 + √5) / 2:
```
width = φ * ((m % φ) / φ)^k_star * width_factor
bound = [frac_pred - width, frac_pred + width]
```

With `width_factor = 0.155`, we achieve ~50% coverage over large ranges.

## Educational Purpose

This PoC serves to:
1. **Educate**: Show how cryptographic constants are derived
2. **Verify**: Demonstrate that constants are mathematically verifiable
3. **Demystify**: Prove that "nothing-up-my-sleeve" means transparency, not randomness

## References

- [SHA-256 Specification (FIPS 180-4)](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)
- [Nothing-up-my-sleeve numbers](https://en.wikipedia.org/wiki/Nothing-up-my-sleeve_number)
- Z Framework documentation in `docs/`

## Security Note

**This is not a security issue.** SHA-256's security does not depend on the secrecy of its constants - they are public and verifiable by design. This PoC demonstrates the transparency that makes SHA-256 trustworthy, not vulnerable.

The predictability shown here:
- ✓ Proves mathematical transparency
- ✓ Enables independent verification
- ✗ Does NOT break SHA-256
- ✗ Does NOT compromise Bitcoin
- ✗ Does NOT enable practical attacks

## License

This PoC is part of the unified-framework repository and follows the same MIT license.
