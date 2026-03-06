# Z-Sandbox Gists

This directory contains self-contained, educational code demonstrations ("gists") showcasing key algorithms and techniques from the z-sandbox geometric factorization framework.

## Available Gists

### `ulam_spiral/`

**Ulam Spiral with Z-Framework Geometric Embeddings**

A comprehensive exploration of the Ulam spiral's prime distribution patterns using Z-Framework's 5-dimensional geodesic space mapping, Quasi-Monte Carlo (QMC) methods, and statistical analysis. Bridges classical number theory visualization with modern geometric factorization techniques.

**Features:**
- **Standard Ulam spiral generation** with prime marking (201×201 default grid)
- **Z-Framework integration:**
  - Discrete curvature κ(n) = d(n) * ln(n+1) / e²
  - Geometric resolution θ'(n,k) = φ * ((n mod φ) / φ)^k
  - Combined Z-weight for unified prime probability weighting
- **Multi-panel visualization:**
  - Standard prime marking (black on white)
  - Local prime density heatmap
  - Curvature κ(n) overlay at prime positions
  - Geometric resolution θ'(n,k) overlay
- **Statistical analysis:**
  - Correlations between Z-metrics and prime positions
  - Diagonal pattern detection via angular binning
  - Quadratic polynomial identification (e.g., n² + n + 41)
  - Chi-square tests for pattern significance
- **QMC-enhanced large-scale analysis:**
  - Sobol sequences with Owen scrambling
  - Analyzes spirals up to 10,000,000+ positions
  - Bootstrap confidence intervals (95% CI)
  - O(N^(-1-ε)) convergence vs. O(N^(-1/2)) for Monte Carlo
- **Self-contained:** Two main scripts with comprehensive documentation
- **Educational:** Clear mathematical foundations and inline documentation
- **Reproducible:** Fixed seeds (seed=42) ensure deterministic results

**Mathematical Foundation:**
- Ulam spiral coordinate mapping (2D spiral from origin)
- Z-Framework axioms (κ, θ', z_weight)
- Prime Number Theorem for density baseline
- Pearson correlation for Z-metric validation
- Chi-square test for diagonal pattern detection
- Bootstrap resampling for confidence intervals

**Usage:**

```bash
# Install dependencies
pip install numpy scipy matplotlib sympy

# Standard visualization (201×201 grid)
python3 gists/ulam_spiral/ulam_spiral_z_framework.py

# QMC-enhanced large-scale analysis (up to 10^7)
python3 gists/ulam_spiral/ulam_spiral_qmc_analysis.py
```

Or import as a module:

```python
from ulam_spiral_z_framework import generate_ulam_spiral, visualize_ulam_spiral

# Generate custom spiral
spiral_data = generate_ulam_spiral(size=401, seed=42)  # 401×401 grid

# Create visualization
visualize_ulam_spiral(spiral_data, output_path='custom_spiral.png')

# QMC analysis
from ulam_spiral_qmc_analysis import UlamSpiralQMC, bootstrap_ci

sampler = UlamSpiralQMC(max_n=1_000_000, seed=42)
result = sampler.analyze_sample(n_samples=10000, bias_mode='uniform')
print(f"κ(n) correlation: {result['kappa_correlation']:.6f}")
```

**Performance:**
- Standard spiral (201×201): ~10-15 seconds on modern hardware
- QMC analysis (10^7 range, 50k samples): ~30-60 seconds
- Bootstrap CI (100 iterations): ~30 seconds
- Visualization generation: ~5 seconds

**Key Results (201×201 grid, n ≤ 40,401):**
- Total primes: 4,236 (10.5% density vs. 10.1% expected from PNT)
- Z-Framework correlations:
  - κ(n) with primes: +0.015 (weak positive)
  - θ'(n,k=0.3) with primes: +0.0005 (minimal)
- Diagonal patterns: 142 detected (χ² confirms non-uniformity, p < 0.05)
- Euler's polynomial (n² + n + 41): 92% prime density for n ∈ [0, 49]

**Note:** This gist demonstrates novel integration of classical number theory visualization (Ulam spiral) with modern geometric techniques (Z-Framework). Results show weak but positive correlations between Z-metrics and prime positions, suggesting potential for deeper investigation at larger scales. For full documentation including mathematical foundations, limitations, and Mission Charter compliance, see:
- `gists/ulam_spiral/README.md` (comprehensive guide)
- `gists/ulam_spiral/ulam_spiral_z_framework.py` (standard visualization)
- `gists/ulam_spiral/ulam_spiral_qmc_analysis.py` (QMC-enhanced analysis)
- `gists/ulam_spiral/MISSION_CHARTER_MANIFEST.md` (compliance documentation)

---

### `pollard_rho_gaussian_lattice_monte_carlo.py`

**Enhanced Pollard's Rho with Gaussian Integer Lattice and Monte Carlo Integration**

A self-contained demonstration of Pollard's Rho enhanced with Gaussian Integer Lattice theory and Monte Carlo variance reduction, featuring three sampling strategies for improved factorization efficiency.

**Features:**
- **Three sampling modes:**
  - `uniform`: Standard random sampling (baseline)
  - `stratified`: Partitioned parameter space for better coverage
  - `sobol`: Low-discrepancy quasi-random sequence
- **Self-contained:** Uses only Python standard library (no external dependencies)
- **Educational:** Comprehensive inline documentation explaining the mathematics
- **Validated:** Successfully factors test cases including 899, 1003, and 10403
- **Reproducible:** Seed-based randomization ensures consistent results

**Mathematical Foundation:**
- Gaussian Integer Lattice ℤ[i]
- Epstein Zeta closed form E_2(9/4) ≈ 3.7246
- O(N^{1/4}) targeting via lattice theory
- Variance-reduced Monte Carlo sampling

**Usage:**

```bash
# Run the demonstration
python3 gists/pollard_rho_gaussian_lattice_monte_carlo.py
```

Or import and use as a module:

```python
from pollard_rho_gaussian_lattice_monte_carlo import GaussianLatticePollard

# Initialize factorizer
factorizer = GaussianLatticePollard(seed=42)

# Factor a semiprime
N = 899  # 29 × 31
factor = factorizer.monte_carlo_lattice_pollard(
    N=N,
    max_iterations=10000,
    num_trials=10,
    sampling_mode='sobol'
)

print(f"Found factor: {factor}")
```

**Performance:**
Based on benchmarks from the full z-sandbox implementation:
- N = 899: ~0.12s
- N = 1003: ~0.45s
- N = 10403: ~1.16s

**Note:** This gist is a simplified, standalone version for educational purposes. For the full implementation with high-precision arithmetic (mpmath), integration with the GVA framework, and comprehensive test suite, see:
- `python/pollard_gaussian_monte_carlo.py`
- `tests/test_pollard_gaussian_monte_carlo.py`
- `python/examples/pollard_gaussian_demo.py`

---

### `rqmc_control_knob_demo.py`

**RQMC Control Knob: Adjustable Coherence in Randomized Quasi-Monte Carlo Sampling**

A standalone demonstration of the RQMC Control Knob feature, showcasing the ScrambledSobolSampler with adjustable coherence parameter α for variance-reduced Monte Carlo integration. This implements established scrambled net theory (Owen 1997, Dick 2010) with a user-friendly control knob that maps the coherence parameter to scrambling depth, enabling advanced RQMC modes with O(N^(-3/2+ε)) convergence for smooth integrands.

**Features:**
- **Four RQMC modes:**
  - `rqmc_sobol`: Scrambled Sobol' with α-controlled randomization
  - `rqmc_halton`: Scrambled Halton with α-controlled randomization
  - `rqmc_adaptive`: Adaptive RQMC with target ~10% variance
  - `rqmc_split_step`: Split-step RQMC evolution with re-scrambling
- **Tunable α parameter:** Control knob from 0.0 (max scrambling) to 1.0 (minimal scrambling)
- **Performance benchmarks:** Demonstrates sample sizes 100, 500, 1000
- **Convergence rates:** O(N^(-3/2+ε)) for smooth integrands (Owen 1997, Dick 2010)
- **Variance estimation:** Unbiased via M independent scrambled replications
- **Optics connection:** Reduced source coherence analogy from nonlinear optics

**Mathematical Framework:**
- Scrambling depth: d(α) = ⌈32 × (1 - α²)⌉
- Ensemble size: M(α) = max(1, ⌈10 × (1 - α²)⌉)
- Target variance: ~10% normalized (adaptive mode)
- Convergence: O(N^(-3/2+ε)) for scrambled nets (Owen 1997, Dick 2010)

**Usage:**

```bash
# Run the full demonstration
python3 gists/rqmc_control_knob_demo.py

# Quick start example only
python3 gists/rqmc_control_knob_demo.py --quick-start-only

# Custom parameters
python3 gists/rqmc_control_knob_demo.py --samples 1000 --alpha 0.5
```

Or import and use as a module:

```python
from rqmc_control_knob_demo import ScrambledSobolSampler

# Initialize sampler with tunable α
sampler = ScrambledSobolSampler(dimension=2, alpha=0.5, seed=42)

# Generate samples
samples = sampler.generate(1000)

# Generate replications for variance estimation
replications = sampler.generate_replications(1000)
```

**Performance:**
Based on benchmarks (seed=42):
- Sample generation: ~0.2-0.4 ms for 500 samples
- Variance stability: ~0.083 ± 0.000008 across replications
- 30-40× better candidate diversity than uniform MC
- 12/12 test passing rate

**Theoretical Background:**
- **Owen Scrambling (1997)**: Nested random digit scrambling for (t,m,s)-nets
- **L'Ecuyer (2020)**: Randomized Quasi-Monte Carlo overview
- **Dick (2010)**: Higher order scrambled digital nets achieve optimal rate
- **arXiv:2503.02629**: Partially coherent pulses in nonlinear dispersive media

**Connection to Optics:**
The implementation draws inspiration from reduced source coherence in nonlinear optics:
- Coherence parameter α ↔ Scrambling strength
- Complex screen ensemble ↔ M independent scrambles
- Split-step Fourier ↔ Split-step RQMC evolution
- Partial coherence robustness ↔ Variance stabilization

**Note:** This gist is a simplified, standalone version for educational purposes. For the full implementation with all optimizations, integration with the factorization framework, and comprehensive test suite, see:
- `python/rqmc_control.py`
- `tests/test_rqmc_control.py`
- `docs/RQMC_CONTROL_KNOB.md`
- `python/monte_carlo.py` (integration with four RQMC modes)

---

### `transec_udp_zerortt.py`

**Zero-RTT Encrypted UDP Messaging with TRANSEC Protocol**

A self-contained implementation of zero-RTT encrypted UDP messaging using time-slot key rotation with HKDF-SHA256 and ChaCha20-Poly1305 AEAD, featuring integrated benchmarking with bootstrap confidence intervals.

**Features:**
- **Zero round-trip encryption:** No handshake needed after bootstrap
- **Time-sliced key rotation:** Configurable slot duration (default: 5 seconds)
- **Replay protection:** Per-slot sequence tracking
- **Clock drift tolerance:** Configurable window (default: ±2 slots)
- **Integrated benchmarking:** Bootstrap CI for throughput measurement
- **Standalone UDP server/client:** Ready-to-use implementations

**Mathematical Foundation:**
- Key Derivation: HKDF-SHA256(shared_secret, slot_index)
- Encryption: ChaCha20-Poly1305 AEAD
- Replay Protection: Per-slot sequence tracking
- Drift Tolerance: ±N slots around current time

**Usage:**

```bash
# Run demonstration
python3 gists/transec_udp_zerortt.py --demo

# Run benchmark (1000 messages)
python3 gists/transec_udp_zerortt.py --benchmark --count 1000

# Start UDP server
python3 gists/transec_udp_zerortt.py --server --port 5000

# Send message
python3 gists/transec_udp_zerortt.py --send "Hello, TRANSEC!" --port 5000
```

Or import and use as a module:

```python
import secrets
from transec_udp_zerortt import TransecCipher, benchmark

# Initialize cipher
shared_secret = secrets.token_bytes(32)
sender = TransecCipher(shared_secret)
receiver = TransecCipher(shared_secret)

# Encrypt/decrypt
plaintext = b"Hello, TRANSEC!"
packet = sender.seal(plaintext, sequence=1)
decrypted = receiver.open(packet)

# Run benchmark
results = benchmark(count=1000)
print(f"Throughput: {results['throughput']:.0f} msg/sec")
print(f"95% CI: [{results['ci_lower']:.0f}, {results['ci_upper']:.0f}]")
```

**Performance:**
Based on localhost benchmarks (empirically validated):
- Throughput: 30,000+ msg/sec on modern hardware
- 95% bootstrap CI: [30,000, 36,000] msg/sec (typical range)
- Encryption overhead: <0.05 ms per packet
- Key derivation: <0.1 ms per slot

**Packet Format:**
```
[slot_index: 8 bytes] [sequence: 8 bytes] [nonce: 12 bytes] [ciphertext+tag: variable]
```

**Dependencies:**
```bash
pip install cryptography numpy
```

**Inspiration:**
Inspired by military frequency-hopping COMSEC (Communications Security), enabling secure, low-latency messaging for tactical communications, IoT networks, and distributed systems.

**Note:** This gist is a simplified, standalone version for educational purposes and quick prototyping. For the full implementation with advanced features (prime-based slot normalization, extended configuration options, comprehensive test suite), see:
- `python/transec.py`
- `python/transec_prime_optimization.py`
- `tests/test_transec.py`
- `docs/TRANSEC.md`

---

### `wide_scan_geores_factor.py`

**Wide-Scan Geometric Resonance Factorization (N-only, 127-bit demo)**

A self-contained demonstration of N-only factorization using geometric resonance with wide integer m-scan and Dirichlet kernel filtering. Successfully factors a 127-bit semiprime in 2-5 minutes using only the target number N as input.

**Features:**
- **N-only input:** No prior knowledge of factors required
- **Geometric resonance:** Comb formula with Dirichlet kernel sharpening
- **Wide-scan coverage:** Integer m-scan ±180 around m₀=0
- **Deterministic:** Golden-ratio low-discrepancy k-sampling with fixed seed
- **Self-contained:** Uses only mpmath (no NumPy/SymPy/ECM/NFS)
- **Primality checking:** Deterministic Miller-Rabin for 64-bit integers
- **CLI support:** Configurable parameters via command-line arguments

**Mathematical Foundation:**
- Golden-ratio LD sampling on k ∈ [0.25, 0.45]
- Dirichlet kernel D_J(θ) with J=6, threshold=0.92
- Comb formula: p̂ = exp((ln N - 2πm/k) / 2)
- Wide integer m-scan exploits coverage + filtering strategy

**Usage:**

```bash
# Install dependency
pip install mpmath

# Run demo (127-bit semiprime)
python3 gists/wide_scan_geores_factor.py

# Custom parameters
python3 gists/wide_scan_geores_factor.py --N 899 --m-span 200
```

**Expected Output:**

For N = 137524771864208156028430259349934309717:
- p = 10508623501177419659 (64-bit prime)
- q = 13086849276577416863 (64-bit prime)
- Runtime: 2-5 minutes on modern laptop
- Positions tested: ~289,000
- Candidates: ~73,000 (25% keep ratio)

**Key Insight:**

Success comes from **wide-scan coverage** (±180 integer m values) combined with **Dirichlet filtering** (~75% rejection), not from precise N-derived m₀ targeting (which simplifies to 0 for semiprimes). The method generates geometric candidates via the comb formula and validates them through divisibility testing—geometry guides candidate generation, but classical divisibility (N % p_candidate == 0) is the final arbiter. This demonstrates geometric resonance as a candidate generation strategy for appropriately-sized semiprimes.

**Validation:**
- ✅ 100% success rate on demo 127-bit target
- ✅ Deterministic and reproducible (fixed seed=42)
- ✅ No classical factoring methods (no ECM/NFS/Pollard/GCD)
- ✅ Validated against results/geometric_resonance_127bit/method.py

**Note:** This gist is based on the validated method from `results/geometric_resonance_127bit/`. For detailed analysis, see:
- `results/geometric_resonance_127bit/README.md`
- `results/geometric_resonance_127bit/metrics.json`
- Documentation in `gists/wide_scan_geores_factor_README.md`

---

## About Gists

Gists in this directory are designed to be:
1. **Self-contained:** Minimal or no external dependencies
2. **Educational:** Clear documentation and examples
3. **Runnable:** Can be executed directly or imported
4. **Demonstrative:** Showcase key concepts from the framework

For the full z-sandbox framework with all features, see the main repository documentation.
