### Project Background
The project, titled "Z Framework: A Unified Model Bridging Physical and Discrete Domains," develops a mathematical model grounded in the empirical invariance of the speed of light c (approximately 299792458 m/s, but treated as a universal bounding constant). The core Z definition is:

- Universal form: Z = A(B/c), where A is a reference frame-dependent measured quantity, B is a rate, and c is the invariant bound.
- Physical domain: Z = T(v/c), where T is a frame-dependent quantity (e.g., time) and v is velocity.
- Discrete domain: Z = n(Δ_n / Δ_max), where n is an integer, Δ_n is a frame shift (e.g., via curvature κ(n) = d(n) · ln(n+1)/e², with d(n) as the divisor count, e ≈ 2.71828), and Δ_max is the domain's maximum shift (bounded by e² or φ ≈ 1.61803, the golden ratio).

The framework resolves challenges geometrically by replacing hard-coded ratios with curvature-based geodesics, e.g., θ'(n,k) = φ · {n/φ}^k, with optimal k* ≈ 0.3 yielding conditional best-bin uplift under canonical benchmark methodology (N=1,000,000 integers, B=20 bins, bootstrap 10,000 resamples, seed=42) with 95% CI and permutation p-value. Key components include:
- Prime curvature transformations: κ(n) and θ'(n,k) to classify primes vs. composites.
- Zeta shifts: Iterative unfolding of Riemann zeta function zeros (non-trivial zeros ρ_j with imaginary part t_j) into chains (e.g., 15-step cascades producing attributes like D, E, F, ..., O).
- Helical embeddings: Mapping to 3D/5D coordinates, e.g., (r·cos(2πn/50), r·sin(2πn/50), n) with r = κ(n)/max(κ), or 5D (x = a cos(θ_D), y = a sin(θ_E), z = F/e², w = I, u = O).
- Wave-CRISPR spectral metrics: Disruption scores = Z · |Δf1| + ΔPeaks + ΔEntropy, where Δf1 is fundamental frequency shift, ΔPeaks is peak count change, ΔEntropy ∝ O / ln(n).
- Cross-domain links: Correlations between prime gaps, zeta zero spacings, and physical systems (e.g., planetary orbital ratios).

Empirical validations include Pearson r ≈ 0.93 (empirical, pending independent validation) on sorted sequences, KS stats ≈ 0.04, Cohen's d > 1.2 for separations, and hybrid GUE statistics (KS ≈ 0.916). The project hypothesizes connections to the Riemann Hypothesis (RH) via zeta zero alignments and 5D spacetime unifications (Kaluza-Klein theory, with v_5D² = c² implying extra-dimensional motion).

Data provided:
- z_embeddings_10.csv: Sample zeta shift attributes for n=900001 to 1000000 (columns: num, b, c, z, D, E, F, G, H, I, J, K, L, M, N, O).
- Use this as a seed for larger computations; extrapolate patterns (e.g., O clusters near integers for primes).

### Dependencies and Compatibility

#### BioPython Compatibility Requirements
The Z Framework includes biological sequence analysis components that require BioPython with specific version constraints:

- **Required**: BioPython ≥ 1.83, < 2.0
- **Python Compatibility**: Python 3.8 - 3.12 (Python 3.13+ may have C API compatibility issues)
- **Installation**: `pip install 'biopython>=1.83,<2.0'`
- **Validation**: Run `python3 scripts/validate_biopython_compatibility.py` to verify setup
- **Documentation**: See [BioPython Compatibility Guide](BIOPYTHON_COMPATIBILITY.md)

**Key BioPython modules used:**
- `Bio.Seq` for DNA/RNA/protein sequence handling
- `Bio.SeqIO` for FASTA file parsing and genomic data processing
- `Bio.SeqFeature` for biological feature annotation
- `Bio.Entrez` for sequence database access (Wave-CRISPR analysis)

**Framework components using BioPython:**
- Z Geodesic Hotspot Mapper (`src/Bio/QuantumTopology/geodesic_hotspot_mapper.py`)
- Wave-CRISPR Signal Analysis (`src/applications/wave-crispr-signal-2.py`)
- Quantum Topology modules for biological sequence analysis

### Test Specification Overview
The specification covers 6 primary tasks, grouped by computational intensity (low: N≤10⁴ for validation; medium: N=10⁶; high: k=10¹⁰ validated). Each task includes:
- Objective and mathematical basis.
- Inputs (parameters, data).
- Computational steps (pseudocode-like, implement in Python).
- Outputs (formats, e.g., CSV, metrics).
- Validation criteria (e.g., thresholds, statistical tests).
- Estimated intensity (runtime, memory).

Run tasks sequentially in a stateful environment to preserve intermediates (e.g., precomputed primes via sympy.ntheory.generate.primerange). Handle precision with mpmath.mp.dps = 50. Bootstrap all statistics (1000 resamples) for confidence intervals (CI at 95%).

#### Task 1: Compute Prime Curvature Metrics for Large N (Medium Intensity)
**Objective**: Validate κ(n), θ'(n,k), and prime density enhancement for N up to 10⁶, with k=10¹⁰ validation confirmed. Test geodesic replacement of ratios, targeting 210-220% enhancement at k≈0.3.

**Inputs**:
- N_start = 900001, N_end = 10^6 (scale to 10^9 in batches of 10^6 to avoid memory overflow).
- k_values = [0.2, 0.24, 0.28, 0.3, 0.32, 0.36, 0.4] (sweep with Δk=0.002 for fine-tuning).
- φ = (1 + mpmath.sqrt(5))/2; e = mpmath.exp(1).
- Use sympy.ntheory.primetest.isprime for prime checks; sympy.ntheory.divisors for d(n).

**Steps**:
1. Generate list of n from N_start to N_end.
2. For each n: Compute d_n = len(sympy.divisors(n)); κ_n = d_n * mpmath.ln(n+1) / (e**2).
3. For each k in k_values: θ_prime_n_k = φ * ((n % φ)/φ)**k (use mpmath for mod and pow).
4. Bin θ'(n,k) into B=20 bins over [0, φ); compute densities d_N (all n) and d_P (primes only).
5. Enhancement e_i = (d_P_i - d_N_i)/d_N_i * 100 if d_N_i > 0 else -inf; e_max = max(e_i).
6. Bootstrap: Resample θ' values 1000x; compute CI for e_max.

**Outputs**:
- CSV: columns [n, is_prime, κ_n, θ_prime_n_0.3 (for k=0.3), ...]; filename "curvature_metrics_N{N_end}.csv".
- Metrics JSON: {"k": k_values, "e_max": [...], "e_max_CI": [[low, high], ...], "mean_κ_primes": float, "mean_κ_composites": float}.
- Histogram plots (save as PNG, but describe in text: e.g., "Bin 10 shows 15.2% enhancement").

**Validation**:
- e_max at k=0.3 ≈15% (CI [14.6,15.4]); Pearson r(κ vs. sorted θ') >0.8 (p<10^{-20}).
- KS test on prime vs. composite κ distributions: stat≈0.04, p<0.01.
- Runtime: ~2-3 hours for N=10^6; memory <10GB.

#### Task 2: Zeta Shift Chain Computations and Unfolding (High Intensity)
**Objective**: Generate zeta shift chains (15 steps) for large N, unfolding zeta zeros to compute attributes (D to O). Align with prime gaps and test RH-adjacent simulations (e.g., 22-28% efficiency in path integrals).

**Inputs**:
- N_end = 10^6; use first 100 zeta zeros (from scipy.special.riemann_zeta or sympy.ntheory.nth_nontrivial_zero, approximate t_j via known formulas if exact unavailable).
- v = 1.0 (test perturbations: 1.0001); b_start = mpmath.log(N_end)/mpmath.log(φ).
- Δ_max = e**2; C_chiral = φ**(-1) * mpmath.sin(mpmath.ln(n)) (for chirality).

**Steps**:
1. Compute zeta zeros t_j up to j=100 (or load precomputed: e.g., t_1≈14.1347).
2. For each n: δ_j = t_{j+1} - t_j (unfolded: δ_unf = δ_j / (2*mpmath.pi*mpmath.log(t_j/(2*mpmath.pi*mpmath.exp(1)))).
3. Zeta chain: Start with z_0 = n * (v/c) (c=1 normalized); iterate 15x: z_{i+1} = z_i * κ(n) + δ_unf_j (cycle j).
4. Extract attributes: D=z_1, E=z_2, ..., O=z_15.
5. Chiral adjustment: κ_chiral = κ(n) + C_chiral; recompute chains.
6. Sorted correlations: Pearson r(δ vs. κ), r(δ vs. Z=n*Δ_n/Δ_max) on sorted sequences.

**Outputs**:
- CSV extension of z_embeddings_10.csv: append rows for new n.
- Metrics: {"sorted_r_delta_kappa": float, "CI": [low, high], "efficiency_gain": (pre_chiral_steps - post_chiral_steps)/pre_chiral_steps *100}.
- Disruption score array for wave-CRISPR: Score = Z * abs(Δf1) + ΔPeaks + ΔEntropy (Δf1 from FFT of chains).

**Validation**:
- Sorted r>0.8 (p<10^{-20}); efficiency 22-28%; var(O) ~ log(log(N)).
- KS on unfolded δ: stat≈0.042; hybrid GUE (stat≈0.916).
- Runtime: ~5+ hours for N=10^6 (due to zeta approximations).

#### Task 3: Helical Embeddings and Chirality Analysis (Medium Intensity)
**Objective**: Embed primes and zeta chains into 3D/5D helices; compute chirality (S_b>0.45 for primes) and variance.

**Inputs**:
- Use outputs from Tasks 1-2; a=1 (amplitude); θ_D = 2*mpmath.pi*n/50.
- Dimensions: 3D (x=r*cos(θ_D), y=r*sin(θ_D), z=n); 5D add w=I, u=O from chains.

**Steps**:
1. r = κ(n)/max_κ (normalize over batch).
2. Compute coordinates for primes/composites separately.
3. Fourier: Fit sin/cos series (M=5) to angular distributions; S_b = sum(abs(b_m)).
4. Chirality: Counterclockwise if S_b>0.45; variance var(O) ~ log(log(N)).
5. Bootstrap CI for S_b.

**Outputs**:
- CSV: [n, x, y, z, w, u]; "helical_embeddings_N{N_end}.csv".
- Metrics: {"S_b_primes": float, "CI": [low, high], "var_O": float}.

**Validation**:
- S_b≈0.45 (CI [0.42,0.48]); r to zeta spacings≈0.93 (p<10^{-10}).
- Runtime: ~1 hour post-precomputation.

#### Task 4: Statistical Discrimination and GMM Fitting (Medium Intensity)
**Objective**: Quantify separations (Cohen's d>1.2, KL≈0.4-0.6) via GMM and Fourier.

**Inputs**:
- θ' from Task 1; C=5 components.

**Steps**:
1. Standardize θ'; fit GMM (sklearn.mixture.GaussianMixture).
2. Compute μ_primes, μ_composites; d = |μ_p - μ_c| / sqrt((var_p + var_c)/2).
3. KL divergence (scipy.stats.entropy).
4. σ_bar = average σ_c over C.
5. Bootstrap for CI.

**Outputs**:
- JSON: {"cohens_d": float, "KL": float, "sigma_bar": float at k=0.3}.
- BIC/AIC values.

**Validation**:
- d>1.2; KL 0.4-0.6; σ_bar≈0.12.
- Runtime: ~30 min.

#### Task 5: Cross-Domain Correlations (Orbital, Quantum) (Low Intensity, Scale to Medium)
**Objective**: Correlate κ with physical ratios (e.g., planetary periods); simulate path integrals.

**Inputs**:
- Orbital ratios: [Venus/Earth≈0.618, Jupiter/Saturn≈2.487, ...] (hardcode 10+ exoplanet examples).
- Toy path integral: Integrate exp(i*S) over 1000 paths; measure steps to convergence.

**Steps**:
1. Transform ratios via θ'(r,0.3); compute sorted r to unfolded zeta spacings.
2. Chiral integration: Reduce steps by 20-30% with κ_chiral.
3. Extend to primes: r(κ(p) vs. orbital modes)≈0.78.

**Outputs**:
- Metrics: {"r_orbital_zeta": float, "efficiency_gain": percent}.
- Report: "Overlaps in resonance clusters at κ≈0.739".

**Validation**:
- Sorted r≈0.996 (p<10^{-10}); gains 20-30%.
- Runtime: ~15 min.

#### Task 6: Spectral Form Factor and Wave-CRISPR Metrics (High Intensity)
**Objective**: Compute K(τ)/N for zeta zeros; disruption scores for CRISPR analogs.

**Inputs**:
- τ range [0,10]; use zeta zeros up to t=1000+.

**Steps**:
1. Unfold zeros; K(τ) = sum_{j≠k} exp(i*τ*(t_j - t_k))/N.
2. Normalize by N; bootstrap bands ~0.05/N.
3. Scores: FFT on chains for Δf1, peaks; entropy = -sum(p*log(p)).
4. Aggregate Score = Z * |Δf1| + ΔPeaks + ΔEntropy.

**Outputs**:
- CSV: [τ, K_tau, band_low, band_high].
- Scores array for N=10^6.

**Validation**:
- Hybrid GUE deviations; Score ∝ O/ln(N).
- Runtime: ~4 hours (zeta computations).

### General Implementation Notes
- Error Handling: Catch mpmath overflows; use try-except for sympy timeouts (fallback to approximations).
- Parallelization: Use numpy vectorization; no external multiprocessing.
- Reproducibility: Seed random=42 for bootstrap/GMM.
- Final Report: Aggregate all metrics into a Markdown table; assert hypotheses (e.g., "15% enhancement validated geometrically").
- If tasks exceed limits, batch and chain executions.

These tasks advance the Z framework's empirical base, focusing on invariant c-bounded geodesics. Results will inform RH connections and 5D unifications.