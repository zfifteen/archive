# SHA-256 Constants Are Predictable

## Overview

SHA-256, the cryptographic hash function used in Bitcoin and countless other applications, uses "nothing-up-my-sleeve" numbers as constants. These constants are derived from the fractional parts of square and cube roots of prime numbers, making them **mathematically predictable and verifiable**.

**Important**: This is **not a security vulnerability**. SHA-256's security does not depend on the secrecy of its constants. They are public and verifiable by design.

## What Are Nothing-Up-My-Sleeve Numbers?

Nothing-up-my-sleeve numbers are constants in cryptographic algorithms chosen in a way that makes it unlikely they contain hidden backdoors. For SHA-256, these constants are derived from mathematical constants (prime numbers) using a transparent, verifiable process.

## SHA-256 Initial Vector Derivation

SHA-256's initial hash values (IV) are derived from the first 8 primes:

```
For the m-th prime p_m:
1. Calculate sqrt(p_m)
2. Take the fractional part: frac = sqrt(p_m) - floor(sqrt(p_m))
3. Scale to 32 bits: word = floor(frac * 2^32)
4. Represent as hex: 0xXXXXXXXX
```

### Example: The First SHA-256 IV Word

```
p_1 = 2
sqrt(2) = 1.41421356...
frac = 0.41421356...
word = floor(0.41421356... * 2^32) = 0x6a09e667
```

This is exactly the first word in SHA-256's IV!

## Demonstration

The repository includes a proof-of-concept in `experiments/hash-bounds/` that demonstrates this predictability:

```bash
# Show SHA-256 IV reconstruction
cd experiments/hash-bounds
python hash_bounds_demo.py --show-sha256-iv
```

Output:
```
SHA-256 IV words (from frac(sqrt(prime))):

  p_1 =   2  →  sqrt = 1.414214  →  {frac} = 0.41421356  →  0x6a09e667  ✓
  p_2 =   3  →  sqrt = 1.732051  →  {frac} = 0.73205081  →  0xbb67ae85  ✓
  p_3 =   5  →  sqrt = 2.236068  →  {frac} = 0.23606798  →  0x3c6ef372  ✓
  ...
  
✓ Perfect match! SHA-256 IV successfully reconstructed.
```

## Predictability via Z Framework

The unified-framework's Z5D predictor can predict prime numbers, which in turn allows prediction of the fractional parts used in SHA-256 constants:

```bash
# Demonstrate predictability for the 10th prime
python hash_bounds_demo.py 10
```

The demonstration shows:
- **Predicted prime**: Using Z5D or smooth approximation (m log m)
- **True prime**: The actual m-th prime
- **Fractional parts**: Both predicted and true
- **Geometric bounds**: Confidence intervals for predictions
- **SHA-256 words**: Both predicted and true 32-bit constants

## Visualization

Generate a plot showing the distribution of fractional parts:

```bash
python hash_bounds_demo.py --plot --plot-max 100 --plot-output fracparts.png
```

This creates a visualization showing:
- True fractional parts (blue dots)
- Predicted fractional parts (red x's)
- Geometric bounds (green shaded region)

## Why This Matters

### 1. Transparency

SHA-256's constants are **not secret**. They are derived from public mathematical constants in a verifiable way. Anyone can reconstruct them independently.

### 2. No Backdoors

The transparent derivation makes it extremely unlikely that the constants contain hidden backdoors. If someone had chosen constants arbitrarily, they might have selected values with special mathematical properties that weaken the algorithm.

### 3. Educational Value

Understanding how cryptographic constants are derived demystifies cryptography and helps build trust in the algorithms we depend on daily.

## Security Implications

### What This DOES Mean

- ✓ SHA-256 constants are **transparent and verifiable**
- ✓ Anyone can **independently verify** the constants
- ✓ The derivation method is **mathematically sound**
- ✓ This proves **there are no hidden backdoors** in the constants

### What This DOES NOT Mean

- ✗ This is **not a vulnerability** in SHA-256
- ✗ This does **not break** SHA-256's security properties
- ✗ This does **not compromise** Bitcoin or other SHA-256 applications
- ✗ This does **not enable** practical attacks

### Why SHA-256 Remains Secure

SHA-256's security comes from:
1. **One-way property**: Hard to find input given output
2. **Collision resistance**: Hard to find two inputs with same output
3. **Avalanche effect**: Small input changes cause large output changes

The **constants are irrelevant to security** - they could even be all zeros and SHA-256 would still be secure (though less trusted due to lack of transparency).

## Bitcoin Mining Context

In Bitcoin mining:
- Miners search for nonces that produce hashes meeting difficulty criteria
- This is a **brute-force search** over the nonce space
- SHA-256 constants are **fixed and known** to all miners
- Predictability of constants does **not help** find valid nonces faster

## Mathematical Background: Geometric Bounds

The Z Framework provides geometric bounds for fractional parts:

```python
phi = (1 + sqrt(5)) / 2  # Golden ratio
width = phi * ((m % phi) / phi)^k_star * width_factor
bound = [frac_pred - width, frac_pred + width]
```

With `width_factor = 0.155`, these bounds contain the true fractional part approximately 50% of the time, demonstrating the predictability of these mathematical constants.

## References

- **Demonstration**: `experiments/hash-bounds/hash_bounds_demo.py`
- **Documentation**: `experiments/hash-bounds/README.md`
- **FIPS 180-4**: [SHA-256 Specification](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)
- **Wikipedia**: [Nothing-up-my-sleeve numbers](https://en.wikipedia.org/wiki/Nothing-up-my-sleeve_number)

## Try It Yourself

```bash
# Clone the repository
git clone https://github.com/zfifteen/unified-framework
cd unified-framework

# Install dependencies
pip install -e .[dev]

# Run the demonstration
cd experiments/hash-bounds
python hash_bounds_demo.py --show-sha256-iv

# Generate visualization
python hash_bounds_demo.py --plot --plot-output my_plot.png
```

## Conclusion

The predictability of SHA-256 constants is **a feature, not a bug**. It demonstrates:
- **Mathematical transparency**: Anyone can verify the constants
- **No hidden backdoors**: The derivation method is open and verifiable
- **Educational value**: Understanding builds trust in cryptographic systems

This is not about breaking SHA-256 - it's about understanding and trusting it.

**Math is not magic - it's beautiful, predictable transparency.**
