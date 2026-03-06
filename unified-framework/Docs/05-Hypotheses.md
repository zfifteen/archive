# Hypotheses

## Theoretical Claims (Not Yet Fully Validated)

### Cross-Domain Biological Applications (PR #249, #251)
- **Claim**: Geometric resonance principles used for wide-scan factorization also apply to DNA sequence analysis
- **DNA Breathing**: Wave-based modeling shows 18% higher variability in AT-rich regions
- **CRISPR Efficiency**: 25% computational efficiency gain claimed in target site identification workflow (not laboratory sequencing)
- **Method**: Transform DNA sequences into 5D geodesic space, apply QMC sampling
- **Validation**: Correlates with 2010 DNA flexibility studies, integrated with BioGRID-ORCS datasets
- **Status**: Preliminary correlations observed, requires independent clinical validation

### Wide-Scan Factorization Success (PR #249, #251)
- **Claim**: Comprehensive m-value scanning with Dirichlet filtering enables semiprime factorization
- **Factorization Achievement**: 100% success on 127-bit semiprimes in 128.1 seconds (optimized to 2.1 minutes)
- **Critical Correction** (PR #251): Success stems from wide-scan coverage (m ∈ [-180, +180]), not from m0 estimation
- **Mathematical Proof**: m0 = nint((k * (ln(N) - 2*ln(√N))) / (2π)) = nint(0) = 0 for balanced semiprimes
- **Key Techniques**: 
  - Dirichlet kernel filtering (|D_J(θ)| ≥ 11.96 threshold)
  - Quasi-Monte Carlo sampling with Sobol sequences (801 k values)
  - High-precision computation (mp.dps=200)
  - 25.24% candidate retention, 0.82% divisibility checks
- **Cross-Domain Bridge**: φ-based phase coherence applicable in multiple domains
- **Status**: Factorization validated; theoretical understanding of why wide-scan works requires further research

### Riemann Zeta Zero Correlations
- **Claim**: Prime geodesic embeddings correlate with unfolded Riemann zeta zeros
- **Reported correlation**: r ≈ 0.93 (p < 10^-10) in 5D helical embeddings
- **Formula**: t_j = Im(ρ_j) / (2π log(Im(ρ_j)/(2π e)))
  - **Where**:
    - `t_j`: Normalized imaginary part of the j-th nontrivial Riemann zeta zero
    - `ρ_j`: The j-th nontrivial zero of the Riemann zeta function (ρ_j = 1/2 + i·Im(ρ_j))
    - `Im(ρ_j)`: Imaginary part of ρ_j
    - `e`: Euler's number (≈ 2.718)
- **Status**: Pending independent validation and full reproduction pack

### Cross-Domain Mathematical Bridge
- **Claim**: Universal equation Z = A(B/c) bridges physical and discrete domains
- **Physical domain**: Z = T(v/c) for relativistic transformations
- **Discrete domain**: Z = n(Δₙ/Δₘₐₓ) for prime prediction
- **Status**: Theoretical framework requiring rigorous proof

### Asymptotic Convergence at Ultra-Large Scales
- **Claim**: Framework maintains accuracy for k > 10^15
- **Current validation**: Only up to k = 10^10
- **Extrapolation**: Based on log-log scaling patterns
- **Status**: Requires empirical confirmation at ultra-extreme scales

### Spectral Chirality in Prime Sequences
- **Claim**: Prime distributions exhibit helical patterns in 5D embeddings
- **Method**: x = cos(θ' · D), y = sin(θ' · E), z = F/e²
- **Evidence**: Preliminary correlation analysis
- **Status**: Needs comprehensive spectral validation

### Efficiency Through Symmetry
- **Claim**: Pre-computed zeta zeros enable 10-100x performance gains
- **Evidence**: Comparative analysis with/without pre-computation
- **Limitation**: Requires validation across diverse computational environments
- **Status**: Hypothesis pending broader empirical confirmation

## Research Directions

These hypotheses guide ongoing research but should not be cited as established facts. Full reproduction packages with data, seeds, transforms, and null hypotheses are required before moving claims to validated results.