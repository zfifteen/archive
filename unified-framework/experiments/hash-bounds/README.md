# SHA-256 Constant Predictability Experiments

This directory contains educational demonstrations showing that SHA-256's "nothing-up-my-sleeve" constants are mathematically predictable and verifiable.

## Overview

**Important**: This is **not a security vulnerability**. SHA-256's security does not depend on the secrecy of its constants - they are public and verifiable by design. These experiments demonstrate the transparency that makes SHA-256 trustworthy.

## What This Demonstrates

SHA-256's initial vector (IV) constants are derived from:
```
frac = {sqrt(p_m)}          # fractional part of sqrt(m-th prime)
word = floor(frac * 2^32)   # → 32-bit hex word (SHA-256 IV)
```

This proof-of-concept shows:
1. **Predictability**: Fractional parts can be predicted using smooth approximations (`m log m`) or advanced models (Z5D)
2. **Geometric Bounds**: These fractional parts can be bounded using golden ratio-based formulas
3. **Reconstruction**: The 32-bit constants can be reconstructed without knowing the primes
4. **Transparency**: Math is not magic - it's verifiable, predictable transparency

## Quick Start

### Basic Demo

Run the main demonstration script:
```bash
python hash_bounds_demo.py 10
```

### SHA-256 IV Reconstruction

Show how the official SHA-256 IV can be perfectly reconstructed:
```bash
python hash_bounds_demo.py --show-sha256-iv
```

### Visualization

Generate a plot showing the fractional part distribution:
```bash
python hash_bounds_demo.py --plot
```

Save the plot to a file:
```bash
python hash_bounds_demo.py --plot --plot-max 200 --plot-output fracparts.png
```

## Files in This Directory

- **`hash_bounds_demo.py`** - Main demonstration script with plotting support (recommended)
- **`poc.py`** - Original proof-of-concept demonstrating predictability
- **`bounds.py`** - Alternative implementation with high-precision calculations
- **`README_POC.md`** - Detailed documentation about the proof-of-concept
- **`sha256.py`** - SHA-256 implementation utilities
- **`lis.py`**, **`lis_wrapper.py`**, **`lis_corrector.py`** - Supporting analysis tools

## Usage Examples

```bash
# Basic demonstration for prime index 10
python hash_bounds_demo.py 10

# Show SHA-256 IV reconstruction
python hash_bounds_demo.py --show-sha256-iv

# Plot fractional parts for m=1 to m=100
python hash_bounds_demo.py --plot

# Plot with custom range and save to file
python hash_bounds_demo.py --plot --plot-max 200 --plot-output fracparts.png

# Use smooth approximation instead of Z5D
python hash_bounds_demo.py 10 --no-z5d

# Adjust width factor for bounds
python hash_bounds_demo.py 10 --width-factor 0.3

# Combined: show IV and generate plot
python hash_bounds_demo.py --show-sha256-iv --plot --plot-output sha256_demo.png
```

## Dependencies

**Required**:
- Python 3.8+
- numpy, matplotlib (for plotting)

**Optional** (enhances precision):
- `mpmath`: High-precision arithmetic
- `sympy`: Accurate prime computation
- Repository's `Z5DEnhancedPredictor`: Advanced prime prediction

The scripts will fall back gracefully if optional dependencies are missing.

## Mathematical Background

### SHA-256 Constants

SHA-256 uses "nothing-up-my-sleeve" numbers:
- **IV (8 words)**: First 32 bits of fractional parts of square roots of first 8 primes
- **Round constants (64 words)**: First 32 bits of fractional parts of cube roots of first 64 primes

### Fractional Part Prediction

For the m-th prime p_m:
1. **Smooth approximation**: p_m ≈ m ln m (basic, less accurate)
2. **Z5D prediction**: More accurate asymptotic estimate using the Z Framework
3. **Fractional part**: frac(sqrt(p_m)) = sqrt(p_m) - floor(sqrt(p_m))

### Geometric Bounds

Using golden ratio φ = (1 + √5) / 2:
```
width = φ * ((m % φ) / φ)^k_star * width_factor
bound = [frac_pred - width, frac_pred + width]
```

With `width_factor = 0.155`, we achieve ~50% coverage over large ranges.

## Bitcoin Mining Connection

In Bitcoin mining:
- Miners perform brute-force search over 32-bit nonce space
- SHA-256 constants are fixed and known
- **This PoC shows**: Predictability in hash constants enables understanding of statistical distributions

**Important**: This does **not** break Bitcoin or enable practical attacks. It demonstrates transparency, not weakness.

## Educational Purpose

These experiments serve to:
1. **Educate**: Show how cryptographic constants are derived
2. **Verify**: Demonstrate that constants are mathematically verifiable
3. **Demystify**: Prove that "nothing-up-my-sleeve" means transparency, not randomness

## Security Note

**This is not a security issue.** SHA-256's security does not depend on the secrecy of its constants - they are public and verifiable by design. These demonstrations prove the transparency that makes SHA-256 trustworthy, not vulnerable.

The predictability shown here:
- ✓ Proves mathematical transparency
- ✓ Enables independent verification
- ✗ Does NOT break SHA-256
- ✗ Does NOT compromise Bitcoin
- ✗ Does NOT enable practical attacks

## References

- [SHA-256 Specification (FIPS 180-4)](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)
- [Nothing-up-my-sleeve numbers](https://en.wikipedia.org/wiki/Nothing-up-my-sleeve_number)
- Z Framework documentation in `docs/`
- See also: `README_POC.md` for detailed technical explanation

## Contributing

When adding new experiments or improvements:
1. Follow the repository's coding style (Black, Flake8)
2. Add appropriate documentation
3. Ensure educational value is clear
4. Include security disclaimers

## License

Part of the unified-framework repository. See repository LICENSE for details.
