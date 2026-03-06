# Methods: Spectral Resonance Optimization for CRISPR gRNA Prediction

## Overview

This document describes the mathematical formulation, implementation details, and validation methodology for the φ-phase transform with arcsin bridge compression applied to CRISPR gRNA prediction.

## 1. Complex DNA Encoding

DNA sequences are encoded as complex-valued waveforms using the following mapping:

```
A (Adenine)  → +1 + 0i  (positive real axis)
T (Thymine)  → -1 + 0i  (negative real axis)
C (Cytosine) → 0 + 1i   (positive imaginary axis)
G (Guanine)  → 0 - 1i   (negative imaginary axis)
```

**Rationale:** This encoding preserves the natural Watson-Crick base pairing structure (A-T, C-G) through complex conjugate relationships and purine-pyrimidine distinctions through real-imaginary separation.

For a DNA sequence S = s₁s₂...sₙ, the complex waveform is:
```
x[n] = w(sₙ) ∈ ℂ,  n = 1, 2, ..., N
```

where w(·) is the encoding function above.

## 2. Golden Ratio (φ) Phase Transform

### 2.1 Mathematical Formulation

The φ-phase transform applies position-dependent phase modulation based on the golden ratio:

```
θ'(n, k) = φ · ((n mod φ) / φ)^k
```

where:
- φ = (1 + √5)/2 ≈ 1.618033988749895 (golden ratio)
- n ∈ {0, 1, ..., N-1} is the sequence position (0-indexed)
- k ∈ [0.20, 0.40] is the phase power parameter

The transformed waveform is:
```
y[n; k] = x[n] · exp(i·θ'(n, k))
```

### 2.2 Parameter Selection

**Optimal k value (k*):** Empirically determined as k* = 0.300 through systematic sweep analysis across the range [0.20, 0.40] with step size Δk = 0.005.

**φ-phase properties:**
1. **Quasi-periodicity:** The modulo operation with φ creates a quasi-periodic structure that avoids exact repetition
2. **Golden ratio scaling:** φ provides optimal irrational spacing, minimizing resonant interference
3. **Power law modulation:** The power exponent k allows tuning between uniform (k→0) and sharply peaked (k→1) phase distributions

### 2.3 Physical Interpretation

The φ-phase transform models position-dependent structural variations in DNA, analogous to:
- Helical pitch variations
- Base stacking energies
- Local conformational flexibility

## 3. Arcsin Bridge Compression

### 3.1 Mathematical Formulation

The arcsin bridge applies phase compression to sharpen spectral peaks:

```
z̃ = arcsin(α · sin(z))
```

where:
- z = Arg(y[n; k]) + θ'(n, k) is the total phase
- α ∈ [0.85, 0.98] is the compression factor
- Default: α = 0.95

The compressed waveform is:
```
ỹ[n] = |y[n; k]| · exp(i·z̃)
```

### 3.2 Compression Mechanism

The arcsin function has the Taylor expansion:
```
arcsin(x) ≈ x + x³/6 + 3x⁵/40 + ... for |x| ≤ 1
```

For α < 1:
- **Small phases (|sin(z)| << 1):** Nearly linear, minimal compression
- **Large phases (|sin(z)| ≈ 1):** Strong compression toward ±π/2, reducing sidelobes

**Effect:** Sharpens fundamental frequency peaks while suppressing high-frequency sidelobes.

### 3.3 Parameter Range Justification

- **α < 0.85:** Excessive compression, loss of discriminative information
- **α > 0.98:** Insufficient compression, minimal benefit
- **Recommended range:** [0.85, 0.98]
- **Default α = 0.95:** Balanced compression

## 4. Spectral Feature Extraction

### 4.1 Fourier Transform

Apply windowed FFT to the compressed waveform:
```
Y[m] = FFT(ỹ[n] · w[n])
```

where w[n] is the window function (default: Hann window).

**FFT parameters:**
- Size N: 256 (or 512 for longer sequences)
- Zero-padding: To next power of 2
- Window: Hann (default), Hamming, or Blackman

**Hann window:**
```
w[n] = 0.5 · (1 - cos(2πn/(N-1)))
```

Magnitude spectrum:
```
S[m] = |Y[m]|,  m = 0, 1, ..., N/2-1 (positive frequencies only)
```

### 4.2 Feature Definitions

#### ΔEntropy (Spectral Entropy Change)

Shannon entropy of the magnitude spectrum:
```
H(S) = -Σₘ p[m] · log₂(p[m])
```

where p[m] = S[m] / Σₘ S[m] is the normalized spectrum.

Change in entropy:
```
ΔEntropy = H(S_transformed) - H(S_baseline)
```

**Interpretation:** Measures information content redistribution. Positive ΔEntropy indicates spectral broadening; negative indicates concentration.

#### Δf₁ (Fundamental Frequency Change)

Peak magnitude at fundamental frequency f₁:
```
f₁ ≈ N / L (normalized frequency)
```

where L is the sequence length.

Change in fundamental peak:
```
Δf₁ = 100 · (S_transformed[f₁] - S_baseline[f₁]) / S_baseline[f₁]  (percent)
```

**Interpretation:** Positive Δf₁ indicates enhanced fundamental resonance, correlated with target disruption potential.

#### Sidelobe Ratio

Main lobe energy:
```
E_main = Σₘ∈ML S[m]²
```

where ML is the main lobe region (width W = 10 bins centered on f₁).

Sidelobe energy:
```
E_side = Σₘ∉ML S[m]²,  S[m] > θ·max(S)
```

where θ = 0.25 is the threshold ratio.

Sidelobe ratio:
```
R_sidelobe = E_side / E_main
```

Change in sidelobe ratio:
```
Δsidelobe = R_sidelobe(transformed) - R_sidelobe(baseline)
```

**Interpretation:** Negative Δsidelobe indicates sidelobe suppression, improving spectral purity.

#### Magnitude-Squared Coherence (MSC)

Frequency-domain correlation between two spectra:
```
MSC(S₁, S₂) = (Σₘ S₁[m]·S₂[m])² / (Σₘ S₁[m]² · Σₘ S₂[m]²)
```

Range: [0, 1], where 1 indicates identical spectra.

**Application:** Off-target similarity measure. Low MSC suggests reduced off-target binding.

#### Wasserstein-1 Distance (W₁)

Earth Mover's Distance between normalized spectra:
```
W₁(p, q) = inf_{γ∈Γ(p,q)} 𝔼_{(x,y)~γ}[|x - y|]
```

where p, q are probability distributions (normalized spectra) and Γ(p,q) is the set of all couplings.

**Interpretation:** Measures the "work" required to transform one distribution into another. Lower W₁ indicates greater similarity.

#### Sidelobe Asymmetry Score (SAS)

Balance between left and right sidelobes:
```
SAS = (E_right - E_left) / (E_right + E_left)
```

Range: [-1, 1], where 0 is symmetric, >0 is right-skewed, <0 is left-skewed.

**Interpretation:** May correlate with directional binding preferences or structural asymmetries.

### 4.3 Composite Disruption Score

Weighted combination of features:
```
D = w_entropy · ΔEntropy + w_f1 · |Δf₁| + w_sidelobe · Δsidelobe
```

**Default weights:** w_entropy = w_f1 = w_sidelobe = 1.0 (equal weighting)

**Optimization:** Weights can be calibrated on training data to maximize predictive performance.

## 5. GC Content Analysis

### 5.1 GC Percentage

```
GC% = 100 · (n_G + n_C) / N
```

where n_G, n_C are counts of G and C bases.

### 5.2 GC Quartiles

Sequences are assigned to quartiles based on GC%:
- Q1: GC% ∈ [0, 25)
- Q2: GC% ∈ [25, 50)
- Q3: GC% ∈ [50, 75)
- Q4: GC% ∈ [75, 100]

### 5.3 Correlation Analysis

Pearson and Spearman correlations between composite disruption score D and GC quartile:
```
r_Pearson = cov(D, Q) / (σ_D · σ_Q)
r_Spearman = correlation of rank(D) and rank(Q)
```

**Hypothesis:** Spectral features show quartile-dependent trends due to GC-dependent structural properties.

**Multiple testing correction:** False Discovery Rate (FDR) adjustment using Benjamini-Hochberg procedure.

## 6. Validation Methodology

### 6.1 Baseline Comparison

**RuleSet3 (RS3):** Current state-of-the-art on-target predictor (DeWeirdt et al., Nature Communications 2022).

**Comparison metric:** Area Under ROC Curve (AUC)
```
AUC = P(score(positive) > score(negative))
```

### 6.2 Bootstrap Confidence Intervals

Stratified bootstrap with n_draws = 10,000:

1. **Stratification:** Sample with replacement within each locus group to maintain structure
2. **AUC calculation:** Compute AUC for each bootstrap sample
3. **Confidence interval:** 95% CI from 2.5th and 97.5th percentiles

**ΔAUC:**
```
ΔAUC = AUC_method - AUC_baseline
```

with conservative CI:
```
CI_low = AUC_method_low - AUC_baseline_high
CI_high = AUC_method_high - AUC_baseline_low
```

### 6.3 Reproducibility

**Random seeds:** All random operations (bootstrap, data splitting) use fixed seeds:
- Python: 1337
- NumPy: 1337
- PyTorch: 1337 (if applicable)

**Environment logging:** Record versions of:
- Python
- NumPy
- SciPy
- scikit-learn
- pandas

## 7. Ablation Studies

To isolate contributions, compare:

1. **Baseline:** No transforms (k = 0, α = 1)
2. **φ-phase only:** k = 0.300, α = 1 (no arcsin)
3. **Arcsin only:** k = 0, α = 0.95 (no φ-phase)
4. **Full method:** k = 0.300, α = 0.95

**Expected result:** Main gain from φ-phase + arcsin interaction.

### 7.1 Alternate Encodings

Test alternate complex encodings:
- Real-only: A=1, T=-1, C=0.5, G=-0.5
- Purine-pyrimidine: Purines (A,G) → real axis, Pyrimidines (C,T) → imaginary axis
- Keto-amino: Chemical group-based encoding

### 7.2 Window Functions

Compare Hann, Hamming, Blackman, and rectangular (no window).

**Metrics:** Spectral leakage, sidelobe levels, feature sensitivity.

### 7.3 FFT Sizes

Test N ∈ {128, 256, 512, 1024} to assess length sensitivity.

**Trade-off:** Frequency resolution vs. computational cost.

## 8. Implementation Notes

### 8.1 Numerical Stability

- Add small epsilon (1e-12) to avoid log(0) in entropy calculations
- Normalize spectra before distance metrics
- Use double-precision (float64) for phase calculations

### 8.2 Edge Cases

- **Short sequences (L < 20):** Zero-pad to minimum FFT size
- **Long sequences (L > 512):** Segment and average, or increase FFT size
- **Invalid bases:** Raise ValueError with clear message

### 8.3 Performance

- Vectorize operations using NumPy
- Pre-compute phase arrays for batch processing
- Use FFT size as power of 2 for efficiency (FFTW optimization)

**Typical runtime:** ~1-2 ms per sequence on modern CPU

## 9. Statistical Reporting

All reported metrics must include:
1. Point estimate
2. 95% confidence interval (bootstrap or analytical)
3. Sample size
4. Random seed
5. Software versions

**Example:**
```
ΔAUC = 0.032 [0.018, 0.047], n=1000, seed=1337
```

## 10. Data Requirements

### 10.1 Input Format

TSV or CSV with columns:
- `sequence`: gRNA sequence (20-30 bp, A/T/C/G)
- `activity`: On-target activity score (0-1 scale)
- `locus`: Target locus identifier (for stratification)
- `rs3_score`: (Optional) RuleSet3 baseline score

### 10.2 Validation Sets

**Recommended:** Public datasets with experimentally validated activities:
- DeWeirdt et al. (2022) validation set
- Doench et al. (2016) pooled screen data
- Hart et al. (2015) essential gene screens

## 11. Failure Modes and Diagnostics

### 11.1 Over-compression (α → 1)

**Symptom:** Loss of discriminative power, all spectra become similar
**Diagnostic:** Monitor Δsidelobe; positive values indicate over-compression
**Mitigation:** Reduce α or add early stopping

### 11.2 GC Extremes

**Symptom:** Entropy metrics saturate at very high or low GC%
**Diagnostic:** Stratify by GC quartile and check for non-linearity
**Mitigation:** Include GC% as covariate; report partial correlations

### 11.3 Window/Length Sensitivity

**Symptom:** Feature values vary significantly with FFT size or window
**Diagnostic:** Run ablations across {128, 256, 512} and window types
**Mitigation:** Report stability ranges; use consistent parameters

## 12. Future Extensions

### 12.1 Off-Target Scoring

Use MSC and W₁ distances between on-target and off-target spectra as penalty terms in composite score.

### 12.2 Machine Learning Integration

Use spectral features as invariant inputs to:
- Logistic regression (interpretable baseline)
- Gradient boosted trees (XGBoost)
- Neural networks (deep learning)

**Advantage:** Physics-informed features reduce overfitting risk.

### 12.3 Repair Pathway Prediction

Entropy gradients may correlate with NHEJ vs. HDR pathway preferences (hypothesis for future work).

## References

1. DeWeirdt PC, et al. (2022). Accounting for small variations in the tracrRNA sequence improves sgRNA activity predictions for CRISPR screening. *Nature Communications* 13:5255.

2. Doench JG, et al. (2016). Optimized sgRNA design to maximize activity and minimize off-target effects of CRISPR-Cas9. *Nature Biotechnology* 34:184-191.

3. Golden ratio and Fibonacci sequences in biological systems: Livio M. (2002). *The Golden Ratio: The Story of Phi*. Broadway Books.

4. Wasserstein distances: Villani C. (2008). *Optimal Transport: Old and New*. Springer.

5. Shannon entropy in spectral analysis: Cover TM, Thomas JA. (2006). *Elements of Information Theory*. Wiley.

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-10  
**Authors:** Z Framework Team
