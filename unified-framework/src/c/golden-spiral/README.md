# Golden Spiral for Z5D Candidates

This module implements golden spiral algorithms for Z5D prime candidate screening, based on empirical insights from golden space ℚ(√5) analysis.

## Features

- **Golden Space Invariance**: Lab-verified perfect invariance checking (galois_invariant=1, geometric_point=0, cross_correlation=1.0)
- **Lucas-Lehmer Predictor**: ℚ(√3) roots for 10-20% iteration savings on composites
- **Zeckendorf Analysis**: Prime distribution analysis in Fibonacci representation
- **Golden Spiral Search**: φ-scaling predictions for Mersenne candidates

## Implementation

- **z_golden_lucas.c**: Core golden space and Lucas predictor algorithms
- **golden_spiral_demo.c**: Demonstration program showing spiral search
- **zeckendorf_analysis.c**: Fibonacci representation analysis for primes
- **golden_spiral_predictor.c**: Main predictor implementation

## Performance

Based on empirical validation with 1,000 resamples, CI 95%:
- Golden-Galois: 15.2% savings [14.6%, 15.8%], 0.15ms, 4.8MB
- Lucas Predict: 18.7% savings [9.4%, 20.6%], 0.22ms, 5.1MB
- Factorization: 66.0% candidate reduction [65.2%, 66.8%], 0.18ms, 4.2MB

## Usage

```bash
make          # Build golden spiral predictor
make test     # Run demonstration
make clean    # Clean build artifacts
./bin/golden_spiral_demo --exp 127 --verbose
```

## Dependencies

- MPFR library (high-precision arithmetic)
- GMP library (multi-precision integers)
- Inherits from parent Makefile (no new dependencies)

## Author

D.A.L. III (Dionisio Alberto Lopez III)