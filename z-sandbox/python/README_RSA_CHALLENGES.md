# RSA Challenge Benchmark

## Overview

This benchmark validates the Geometric-Monte Carlo factorization efficiency claims on production-grade test cases rather than toy factors. It addresses the verification gates:

1. **Real RSA challenge semiprimes** (RSA-100, RSA-129)
2. **Opt-in execution** (manual, not in default CI)
3. **Machine-readable logs** (JSON/CSV output)
4. **Distant-factor evidence** (skewed semiprimes)

## Quick Start

```bash
# Run the benchmark with default settings
PYTHONPATH=python python3 python/benchmark_rsa_challenges.py

# Specify output directory
PYTHONPATH=python python3 python/benchmark_rsa_challenges.py --output-dir my_results

# Test specific strategies
PYTHONPATH=python python3 python/benchmark_rsa_challenges.py --strategies sobol golden-angle

# Skip skewed semiprime tests
PYTHONPATH=python python3 python/benchmark_rsa_challenges.py --skip-skewed
```

## Output Files

Results are saved to `bench_out/` (or custom directory):

- `rsa_bench_YYYYMMDD_HHMMSS.json` - Machine-readable JSON
- `rsa_bench_YYYYMMDD_HHMMSS.csv` - Spreadsheet-compatible CSV

### JSON Format

```json
{
  "challenge": "10e15-primary",
  "N": "1000001970000133",
  "N_bits": 50,
  "balance": "near-balanced",
  "strategy": "sobol",
  "seed": 42,
  "num_trials": 5,
  "max_iterations": 100000,
  "factor_found": "10000019",
  "expected_factors": ["10000019", "100000007"],
  "success": true,
  "time_ms": 2.28,
  "error": null,
  "timestamp": "2025-10-27T20:07:12.086351"
}
```

### CSV Format

Columns: `challenge`, `N`, `N_bits`, `balance`, `strategy`, `seed`, `num_trials`, `max_iterations`, `factor_found`, `expected_factors`, `success`, `time_ms`, `error`, `timestamp`

## Test Cases

### Primary Test: 10^15 Scale

- **N**: 1000001970000133 (~10^15)
- **Factors**: 10000019 × 100000007
- **Balance**: Near-balanced (ratio ~10:1)
- **Expected**: Fast factorization, validates speedup claims

### Skewed Semiprimes

1. **skewed-10e15-small-p**
   - Factor ratio: ~1,000,000:1
   - Tests algorithm on highly unbalanced factors

2. **skewed-10e15-moderate**
   - Factor ratio: ~10:1
   - Validates speedup on moderately skewed cases

### RSA Challenges (Validation Gates)

- **RSA-100**: 330-bit, too large for Pollard's rho in reasonable time
- **RSA-129**: 426-bit, demonstrates algorithm behavior on real challenges

**Note**: RSA-100 and RSA-129 are included as validation targets but will timeout with Pollard's rho. They demonstrate the need for advanced factorization methods.

## Typical Results

```
Primary Test: 10^15 Scale Semiprime
  ✓ standard: 14.0ms
  ✓ sobol: 2.3ms (+84% speedup)
  ✓ golden-angle: 4.2ms (+70% speedup)

Skewed Semiprime Tests
  skewed-10e15-moderate (10:1 ratio):
    ✓ standard: 14.0ms
    ✓ sobol: 2.2ms (+84% speedup)
    ✓ golden-angle: 4.1ms (+71% speedup)
```

## Integration with CI

This benchmark is **opt-in** and not part of default CI:

- Too time-consuming for every commit
- Results are variance-sensitive
- Machine-readable logs enable offline analysis

For CI, use the lightweight tests:
```bash
pytest tests/test_large_scale_benchmarks.py -m "not slow"
```

## Auditable Results

Machine-readable logs enable:

1. **Time-series analysis**: Compare runs across commits
2. **Reproducibility**: Documented seeds for deterministic results
3. **Statistical validation**: Multiple trials with aggregated metrics
4. **Speedup tracking**: Monitor performance over time

Example diff workflow:
```bash
# Run benchmark on commit A
git checkout commit-A
python3 python/benchmark_rsa_challenges.py --output-dir bench_A

# Run benchmark on commit B
git checkout commit-B
python3 python/benchmark_rsa_challenges.py --output-dir bench_B

# Compare results
diff bench_A/*.csv bench_B/*.csv
```

## Related Files

- `python/benchmark_large_scale_factorization.py` - Statistical analysis benchmark
- `python/demo_geometric_monte_carlo_10e15.py` - Interactive demonstration
- `docs/GEOMETRIC_MONTE_CARLO_10E15_EFFICIENCY.md` - Complete documentation
- `tests/test_large_scale_benchmarks.py` - Unit tests (opt-in slow tests)

## References

- RSA Challenges: src/test/resources/rsa_challenges.csv
- Pollard's Rho: python/pollard_gaussian_monte_carlo.py
- Low-discrepancy sampling: python/low_discrepancy.py
