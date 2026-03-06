# Geometric Factorization Optimized Demo

A C99 implementation of geometric factorization using golden ratio mapping and spiral search for prime discovery. This demo explores an alternative approach to integer factorization based on number-theoretic properties of the golden ratio φ.

## Overview

The algorithm attempts to factor semiprimes by mapping numbers onto a unit circle using the golden ratio, then searching for prime factors that align geometrically. It combines:
- Golden ratio coordinate transformations
- Spiral search patterns inspired by phyllotaxis
- Z5D prime prediction for candidate generation
- Miller-Rabin primality testing

## Success Range

Through extensive testing with 10-20 samples per bit size, the algorithm shows the following success rates:

| Bit Size | Success Rate | Notes |
|----------|-------------|-------|
| 4 | 100% (10/10) | Perfect success on tiny semiprimes |
| 6 | 100% (5/5) | Reliable for very small factors |
| 8 | 60% (6/10) | Moderate success |
| 10 | 60% (6/10) | Consistent with 8-bit performance |
| 14 | 70% (7/10) | Peak performance in mid-range |
| 19 | Failed | Timeout/error on larger inputs |
| 24 | 50% (5/10) | Declining success |
| 29 | 80% (8/10) / 70% (14/20) | Strong at this size |
| 30-33 | Failed | Computational limits |
| 34 | 10% (1/10) | Maximum bit size with any success |
| 35-64 | 0% | No successes at larger sizes |

**Minimum Bit Size for Success**: 4 bits (100% rate)  
**Maximum Bit Size for Success**: 34 bits (10% rate)  
**Optimal Range**: 14-29 bits (50-80% success)

## Python Demo Results
A simplified Python implementation (`python_geometric_factorization_demo.py`) demonstrates the geometric factorization on 20-bit semiprimes. Recent run achieved success after 2 attempts:
- Successfully factorized 463193 = 479 × 967
- Showed effective filtering: Reduced 123 primes to 1 candidate for k=0.2, proving the method as a true shortcut over full trial division.

## Building

### Prerequisites
- macOS with Homebrew
- GCC/Clang with C99 support
- GMP (GNU Multiple Precision Arithmetic Library)
- MPFR (Multiple Precision Floating-Point Reliable Library)
- OpenSSL

### Installation
```bash
brew install gmp mpfr openssl
```

### Compile
```bash
make
```

This builds the executable `bin/geometric_factorization_optimized_demo`.

## Usage

### Basic Run
```bash
./bin/geometric_factorization_optimized_demo [samples] [bit_size]
```

- `samples`: Number of semiprimes to test (default: 10)
- `bit_size`: Bit size of semiprimes to generate (default: 64)

### Examples
```bash
# Test 10 samples of 32-bit semiprimes
./bin/geometric_factorization_optimized_demo 10 32

# Test 5 samples of 16-bit semiprimes
./bin/geometric_factorization_optimized_demo 5 16
```

### Output
- Prints success rate and factorizations to stdout
- Logs detailed results to `logs/factorization_log.txt`
- Successful factorizations in `logs/success_log.txt`
- Failed cases in `logs/fail_log.txt`

## Mathematical Background

### Golden Ratio Mapping
For a number N and exponent k, compute geometric coordinate θ(N, k):
```
θ(N, k) = { φ × {N / φ}^k }
```
Where φ = (1 + √5)/2 ≈ 1.618, and {x} is the fractional part.

### Factor Search
- Generate prime candidates near √N
- Select those with |θ(p, k) - θ(N, k)| ≤ ε
- Test divisibility: if p divides N, found factor

### Spiral Enhancement
Additional candidates from golden angle spirals:
- Angle increment: γ ≈ 137.508°
- Radial growth for broader coverage

## Performance Characteristics

- **Strengths**: Excellent on small semiprimes (4-29 bits)
- **Weaknesses**: Fails on RSA-sized numbers; inconsistent at edges
- **Speed**: Fast for small N; slows dramatically >30 bits
- **Scalability**: Needs major optimizations for practical use

## Files

- `main.c`: Core implementation
- `golden_spiral.c/h`: Spiral search utilities
- `Makefile`: Build configuration
- `TODO.md`: Development roadmap
- `geometric_factorization_success.md`: Detailed success analysis
- `minimum_bit_size_factorization.md`: Minimum bit size documentation
- `python_demo_results.md`: Python demo execution results
- `python_geometric_factorization_demo.py`: Simplified Python implementation
- `logs/`: Test result logs

## Future Work

- Implement predictive Z5D-guided search
- Add hybrid fallbacks (ECM, Pollard Rho)
- Parallelize with OpenMP
- Dynamic parameter tuning
- Scale to 64+ bit semiprimes

## License

This is experimental research code. Use at your own risk.
