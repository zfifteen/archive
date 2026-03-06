# Z5D Secure RSA Key Generator

*A high-performance RSA-4096 key generator using mathematical prediction and hardware acceleration*

Generate cryptographically secure RSA keys in under a second on Apple hardware with the Z5D Prime Predictor—an advanced mathematical framework that optimizes prime number selection.

## Features

- **Fast Generation**: Under 1 second on Apple Silicon hardware
- **Mathematically Optimized**: Z5D predictor reduces brute-force searching
- **Cryptographically Secure**: Non-reproducible keys from high-entropy system sources
- **Hardware-Accelerated**: Apple AMX instructions + OpenMP parallelization
- **Production Ready**: Self-signed certificates with proper X.509 extensions

## Quick Start

### Installation (macOS)

```bash
# Install dependencies via Homebrew
brew install openssl gmp mpfr libomp

# Build the generator
make

# Generate a secure key pair
./bin/z5d_secure_key_gen
```

Keys and certificates are created in the `generated/` directory.

## Usage

### Basic Generation
```bash
./bin/z5d_secure_key_gen
```

### Command Options
```
--bits INT             Key size (default: 4096)
--e INT                Public exponent (default: 65537)
--validity-days INT    Certificate validity in days (default: 30)
--kappa-geo FLOAT      Z5D geodesic parameter (default: 0.300)
--kappa-star FLOAT     Z5D calibration factor (default: 0.04449)  
--phi FLOAT            Golden ratio integration (default: 1.618...)
--bump-p INT           Bump value for p (default: 0)
--bump-q INT           Bump value for q (default: 1)
--debug                Enable verbose diagnostic logging
--quiet                Suppress non-essential output
--show-hardware        Display hardware information (macOS only)
```

### Examples
```bash
# Generate with custom validity period
./bin/z5d_secure_key_gen --validity-days 365

# Generate with debug output
./bin/z5d_secure_key_gen --debug

# Generate quietly for scripting
./bin/z5d_secure_key_gen --quiet
```

## Output

Each run creates uniquely named files:

- `z5d_key_gen-<unique-tag>.key` - Private key (PEM format, 0600 permissions)
- `z5d_key_gen-<unique-tag>.crt` - Self-signed certificate (PEM format)

The unique tag is derived from high-entropy seeds, ensuring different keys each run.

## Security

- **High-Entropy Seeds**: Uses `/dev/urandom` with additional entropy mixing
- **Cryptographic Mixing**: SHA-256 based seed derivation with domain separation
- **Memory Hygiene**: Sensitive data cleansed using `OPENSSL_cleanse`
- **Secure File Permissions**: Private keys created with 0600 permissions
- **Non-Deterministic**: Each run generates unique keys

## Technical Details

### Z5D Framework

The generator uses the Z5D prime predictor with calibrated parameters:
- **kappa_geo**: 0.3 (geodesic mapping exponent)
- **kappa_star**: 0.04449 (Z5D calibration factor)
- **phi**: 1.61803398874989 (golden ratio)

### Performance

- **Apple Silicon**: Less than 1 second generation time
- **Parallel Acceleration**: OpenMP scales with CPU cores
- **Memory Usage**: ~50MB peak during prime generation

## Verification

```bash
# Build and test
make test

# Verify generated key
openssl rsa -in generated/z5d_key_gen-*.key -check

# Inspect certificate
openssl x509 -in generated/z5d_key_gen-*.crt -text -noout
```

## Dependencies

### Required
- **OpenSSL** (>= 1.1.1): Cryptographic functions
- **GMP** (>= 6.0): Arbitrary precision arithmetic
- **MPFR** (>= 4.0): Multiple precision floating-point

### Optional
- **libomp** (>= 12.0): OpenMP support for parallel generation

## Troubleshooting

### Common Issues

**Missing OpenSSL:**
```bash
brew install openssl
```

**Missing GMP:**
```bash
brew install gmp
```

**OpenMP Not Found:**
```bash
brew install libomp  # Optional, for parallel acceleration
```

**Permission Denied:**
- Private keys are intentionally created with 0600 permissions

Use `--debug` for detailed logging during generation.

## Architecture

### Source Files
- `src/z5d_key_gen.c`: Main program and RSA key generation
- `src/z5d_predictor.c`: Z5D prime prediction implementation
- `include/z5d_predictor.h`: Z5D predictor interface
- `include/z_framework_params.h`: Framework parameter definitions
- `include/z_seed_generator.h`: High-entropy seed generation

### Build
- **Compiler**: Clang with Apple Silicon optimizations
- **Optimizations**: -O3, -ffast-math, -funroll-loops
- **Frameworks**: Metal, Foundation (macOS)

## License

This implementation is part of the unified-framework project portfolio.

## Contributing

This is a standalone repository extracted from the unified-framework. For contributions or issues, please refer to the main project repository.
