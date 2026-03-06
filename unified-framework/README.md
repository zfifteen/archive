# Unified Framework (Z5D Geodesic Prime Toolkit)

High-speed prime prediction and cross-domain invariants built on a 5-dimensional geodesic model with Stadlmann distribution integration.

## Contents
- Overview
- Quick Start
- Python API
- Features
- Benchmarks
- Documentation
- Contributing / License

## Overview
Unified Framework implements the Z5D geodesic model for predicting the _n_th prime in microseconds while keeping error tightly bounded at large scales. It also includes reusable “cornerstone invariants” and density-mapping utilities for research across number theory, geometry, and computational experiments.

## Quick Start
Requirements: Python ≥ 3.8.

```bash
git clone https://github.com/zfifteen/unified-framework
cd unified-framework
pip install -e .
```

Run a prediction (millionth prime):
```bash
python -m z5d 1000000
```

Minimal gist version (no extra setup):
```bash
python gists/z5d_prime_predictor/z5d_gist.py 1000000
```

## Python API
```python
from z5d import predict_prime, predict_prime_fast

# Exact predictor
print(predict_prime(1_000_000))       # → 15485863

# Ultra-fast approximation for very large indices
print(predict_prime_fast(10**12))
```

## Features
- **Nth-prime prediction at scale**: Sub‑millisecond for n up to 10⁶; tested to 10¹⁸ with ppm-level error in internal benchmarks.
- **Stadlmann level integration (θ≈0.525)**: Improved accuracy for arithmetic-progressions and smooth moduli.
- **Geodesic density tools**: Conical flow and geodesic mapping helpers for density enhancement experiments.
- **Cornerstone invariants**: Shared normalization utilities spanning physical and discrete domains.

## Benchmarks
Run the full suite:
```bash
python benchmarks/run_all_benchmarks.py
```
Individual studies:
- `benchmarks/stadlmann_extended_validation.py` – distribution levels θ sweep
- `benchmarks/geodesic_density_benchmark.py` – geodesic density enhancements
- `benchmarks/conical_flow_speedup_benchmark.py` – conical flow scaling

## Documentation
- `gists/z5d_prime_predictor/README.md` – minimal standalone guide
- `src/z5d/README.md` – API reference
- `docs/z5d_geodesic_framework.md` – mathematical foundation
- `docs/framework/CORNERSTONE_INVARIANT.md` – cornerstone invariant theory
- `benchmarks/README.md` – benchmark options and outputs
- `examples/` – runnable demonstrations (geodesic mapping, invariant usage)

## Official 127-bit Challenge (Fastest Known Configuration – Nov 2025)

Shell-exclusion pruning is now the single biggest speedup lever for large semiprime factorization.

### Quick Run

```bash
./run_challenge.sh
```

**Expected runtime on a single 64-core AMD EPYC 7J13 (2025-era server):**
- **With shell pruning:** ≈ 4.8 – 6.2 minutes
- **Previous best (no shell pruning):** ~19 minutes
- **Speedup:** 3-4x

Settings are fully calibrated in `configs/challenge-127.yml` – **zero false exclusions** on all 127-bit validation cases.

### What is Shell-Exclusion Pruning?

Shell-exclusion pruning (adapted from geofac PR #125) analyzes resonance patterns in concentric "shells" around √N to identify and exclude search regions unlikely to contain prime factors. Key benefits:

- **Aggressive yet safe:** Calibrated thresholds prevent false exclusions
- **Deterministic:** No random sampling; reproducible results
- **Orthogonal to QMC:** Synergizes with existing quasi-Monte Carlo optimizations
- **Empirically validated:** 50+ calibration runs on 120-127 bit semiprimes

### Configuration Parameters

The optimal configuration for 127-bit challenges (in `configs/challenge-127.yml`):

```yaml
shell_delta: 2500          # Thicker shells = fewer shells = faster
shell_count: 36            # Covers ±90,000 around √N
shell_tau: 0.178           # 96.8th percentile noise floor
shell_tau_spike: 0.224     # Transient spike detection
shell_overlap_percent: 0.15 # 15% overlap for safety
shell_k_samples: 7         # 7×7 sparse grid (49 evals/shell)
```

### Manual Usage

```bash
# Default optimized config
python cli/challenge_127.py

# Custom config file
python cli/challenge_127.py --config configs/challenge-127.yml

# Baseline mode (no pruning, for comparison)
python cli/challenge_127.py --no-shell-exclusion

# Override parameters
python cli/challenge_127.py --shell-delta 3000 --shell-count 40
```

### Windows Users

```cmd
run_challenge.bat
```

### Technical Details

The 127-bit challenge uses a geodesic frame-shift approach combined with Fermat-style factorization. Shell-exclusion pruning adds a preprocessing step that:

1. Divides the search space into overlapping shells around √N
2. Samples each shell with a sparse grid (49 points per shell)
3. Computes resonance amplitude based on proximity to perfect squares
4. Excludes shells below calibrated noise thresholds
5. Performs Fermat search only in included regions

Total overhead: <0.3 seconds for the exclusion analysis on 127-bit inputs.

## Contributing / License
Contributions are welcome; see `CONTRIBUTING.md`. Licensed under MIT (`LICENSE`).