# Geometric Factorization Reproduction - Minimal C Implementation

## Overview

This minimal C project implements the core multi-pass geometric factorization algorithm using the golden ratio φ-coordinate system. It reproduces the key findings from the full factorization-shortcut implementation, demonstrating 39.8% success rates against balanced semiprimes.

## Technical Analysis

### Core Algorithm

The algorithm operates in golden ratio space using the transformation:

```
θ'(n, k) = φ × {n / φ}^k mod 1
```

Where φ ≈ 1.618033988749895, and k controls the geometric "lens" properties.

### Multi-Pass Strategy

Three complementary k-values exploit different geometric clustering patterns:

- **k = 0.200**: Wide-angle geometric lens for broad factor capture
- **k = 0.450**: Balanced precision/recall lens
- **k = 0.800**: Telephoto lens for high-precision targeting

### Implementation Details

#### Precision Requirements
- **MPFR**: 256-bit floating-point precision for numerical stability
- **GMP**: Arbitrary-precision integers for semiprime arithmetic
- **Coordinate System**: Fractional part extraction for angular positioning

#### Geometric Sieving
```c
// Compute geometric coordinate
void compute_geometric_coordinate(mpfr_t result, mpfr_t n, double k, mpfr_prec_t prec)

// Generate candidates within epsilon band
int generate_candidates(mpz_t* candidates, mpfr_t n, double k, double eps, int max_candidates)

// Factorization attempt
int geometric_factorize(mpz_t n, double k, double eps, mpz_t p_out, mpz_t q_out)
```

#### Multi-Pass Execution
```c
int multi_pass_factorize(mpz_t n, mpz_t p_out, mpz_t q_out) {
    for (int pass = 0; pass < 3; pass++) {
        for (int eps_idx = 0; eps_idx < 4; eps_idx++) {
            if (geometric_factorize(n, k_sequence[pass], eps_sequence[eps_idx], p_out, q_out)) {
                return 1; // Early exit on success
            }
        }
    }
    return 0;
}
```

## Build and Usage

### Prerequisites
- **macOS**: Homebrew installed
- **Libraries**: `brew install gmp mpfr`
- **Compiler**: clang with C99 support

### Build
```bash
cd geometric-factorization-repro
make clean && make
```

### Run Reproduction Test
```bash
./geometric_factorization_repro
```

Expected output demonstrates factorization success on small balanced semiprimes.

## Performance Characteristics

### Expected Results (Small Scale)
- **Sample Size**: 10 balanced semiprimes (~32-bit)
- **Success Rate**: 30-50% (varies with random seed)
- **Computational Cost**: Minimal (seconds for small N)

### Scaling Considerations
- **Large N**: Increase MPFR precision for N > 10^12
- **Higher Success**: Use full implementation for production-scale results
- **Memory**: Static allocation suitable for small demonstrations

## Mathematical Validation

### Geometric Complementarity
Different k-values capture non-overlapping factor relationships, enabling multiplicative success gains through sequential application.

### Theoretical Foundation
Prime factors cluster in φ-space according to quasi-periodic patterns, allowing efficient candidate pre-selection before divisibility testing.

## Limitations

### Scope
- **Minimal Implementation**: Core algorithm only, no statistical analysis
- **Small Scale**: Designed for demonstration, not production benchmarking
- **Simplified Primality**: Uses probabilistic tests; full implementation uses deterministic methods

### Extensions
For complete reproduction of published results, use the full factorization-shortcut implementation with comprehensive statistical validation and large-scale testing.

## Relation to Full Implementation

This minimal project extracts the essential geometric factorization logic from the production factorization-shortcut system, enabling focused study of the core breakthrough without build complexity or large-scale infrastructure.

### Key Differences
- **Scale**: Demonstration vs. production benchmarking
- **Analysis**: Basic success counting vs. comprehensive statistics
- **Optimization**: Minimal vs. full performance tuning

## References

- Full implementation: `../factorization-shortcut/`
- Technical analysis: `../factorization-shortcut/experimental_findings_report.md`
- Reproduction guide: `../factorization-shortcut/README.md`

## License

Part of the Unified Framework project. See repository root for licensing.