# Lucas Index System (LIS) — Proof of Concept

This directory contains the Lucas Index System (LIS), a Proof of Concept addressing approach for nth‑prime search that layers a Lucas/Fibonacci probable‑prime pre‑filter before Miller–Rabin verification.

## Overview

LIS improves prime‑search efficiency by leveraging Lucas sequence congruences (notably Fibonacci/Lucas properties) to prune many composites before Miller–Rabin (MR) is invoked.

## Files

- `lucas_index.c` - Core Lucas-index implementation
- `lucas_index.h` - Header file with function declarations and constants
- `lucas_demo.c` - Demonstration program showing Lucas-index capabilities
- `Makefile` - Self-contained build system (no parent linkage)
- `demo_lucas.sh` - Shell script demonstrating the functionality
- `README.md` - This documentation file

## Building

```bash
make              # Build the demonstration executable
make test         # Build and run the demonstration
make clean        # Clean build artifacts
make help         # Show available targets
```

## Dependencies

Dependencies detected locally:
- GMP (GNU Multiple Precision Arithmetic Library)
- MPFR (Multiple Precision Floating-Point Reliable Library)
- OpenMP (optional, for parallel processing)

## Method (Proof of Concept)

This PoC uses a Lucas/Fibonacci probable‑prime filter (Selfridge/Kronecker‑5 variant) to prune composite candidates prior to MR checks. We compare MR‑call counts against a single, realistic presieve baseline: wheel‑210 (coprime to 2·3·5·7). The single metric reported is MR‑call reduction vs baseline: 1 − (MR_calls / wheel‑210_candidates).
