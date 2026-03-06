
# TECH-SPEC: Falsifying Golden Ratio (φ) "Harmonic Spectrum" in Prime Gaps

## 1. Objective

Test whether prime gap sequences exhibit a **special harmonic relationship with the golden ratio φ = 1.618...**, specifically whether the power spectrum of prime gaps shows anomalous peaks at φ-related frequencies.

The experiment should answer:

- Do prime gap Fourier transforms show significant peaks at frequencies f = k·φ (k = 1, 2, 3, ...)?
- Are these peaks **statistically distinguishable** from noise and spurious peaks in random sequences?
- Can synthetic sequences with **no φ-structure** replicate any observed peaks through random chance?
- Is the claim of φ-harmonic structure robust across different prime ranges?

---

## 2. High-level design

### Core methodology:

- Extract **prime log-gaps** Δ_n = ln(p_{n+1} / p_n) over multiple disjoint prime ranges.
- Compute **Discrete Fourier Transform (DFT)** or **Welch periodogram** to estimate power spectral density (PSD).
- Identify peaks in the power spectrum and test for clustering around **φ-harmonic frequencies**: f_k = k·φ/N for k = 1, 2, 3, ...
- Compare observed peak structure against:
  - **Null model**: White noise, shuffled gaps, Poisson-simulated gaps.
  - **Alternative periodicities**: Test whether peaks align better with π, e, √2, etc.
- Apply **rigorous significance testing** (Monte Carlo permutation tests, Bonferroni correction).

### Null hypothesis:

If prime gaps exhibit **no special φ-structure**:
- Power spectrum should be approximately **flat** (white noise) or show only logarithmic-scale trends.
- Any peaks near φ-related frequencies are indistinguishable from peaks in shuffled/synthetic data.
- Peak detection rate should match **false discovery rate** from multiple testing.

### Falsification criteria:

- **Falsified** if peaks at φ-harmonics significantly exceed null expectations across multiple tests.
- **Supported** if peak distribution is statistically indistinguishable from random noise.

---

## 3. Data and inputs

### Prime gap datasets:

- **Prime log-gaps** Δ_n = ln(p_{n+1} / p_n) from ranges:
  1. [10^6, 10^7] (N ≈ 500k gaps)
  2. [10^9, 10^10] (N ≈ 400k gaps)
  3. [10^12, 10^13] (N ≈ 300k gaps)
  4. [10^15, 10^16] (if available, N ≈ 250k gaps)

### Preprocessing:

- **Detrending**: Remove linear or polynomial trend (to eliminate non-stationarity).
- **Windowing**: Apply Hamming or Hann window to reduce spectral leakage.
- **Normalization**: Z-normalize (μ=0, σ=1) before computing FFT.

### Golden ratio harmonics:

Define target frequencies:
```
f_k = k * φ / N, k = 1, 2, 3, ..., 10
```
where φ = (1 + √5)/2 ≈ 1.618033988749895.

---

## 4. Models and null hypotheses

### Model A: φ-harmonic structure hypothesis

**Claim**: Prime gaps encode harmonic structure at golden ratio frequencies.

**Prediction**:
- Power spectrum should show **statistically significant peaks** at f_k = k·φ/N.
- Peak amplitudes at φ-frequencies should exceed 95th or 99th percentile of shuffled data.
- Multiple harmonics (k=1,2,3,...) should be detectable.

**Test**:
For each range, compute:
```
PSD(f) = |FFT(Δ_n)|²
Peak score at f_k: S_k = PSD(f_k) / median(PSD)
```

### Model B: No special φ-structure (null)

**Claim**: Any observed peaks are random fluctuations or artifacts.

**Prediction**:
- Power spectrum is approximately flat or shows only scale-dependent trends.
- Peak distribution at φ-frequencies matches peak distribution at random frequencies.
- Permutation tests show no significant excess at φ-harmonics.

### Alternative hypotheses:

Test whether peaks align better with:
- **π-harmonics**: f_k = k·π/N
- **e-harmonics**: f_k = k·e/N
- **√2-harmonics**: f_k = k·√2/N

---

## 5. Metrics and analysis

### Primary metrics:

1. **Power spectral density (PSD)**:
   ```
   PSD(f) = |FFT(Δ_n)|² / N
   ```

2. **Peak prominence**:
   - Identify local maxima in PSD(f).
   - Measure prominence: height above surrounding baseline.

3. **φ-alignment score**:
   - For each detected peak at f_peak, compute distance to nearest φ-harmonic:
     ```
     d_φ = min_k |f_peak - k·φ/N|
     ```
   - Count peaks with d_φ < ε (e.g., ε = 0.01).

4. **Z-score for φ-peaks**:
   ```
   Z_k = (PSD(f_k) - μ_PSD) / σ_PSD
   ```
   where μ_PSD, σ_PSD estimated from full spectrum.

### Statistical tests:

1. **Permutation test**:
   - Shuffle gap sequence M=10,000 times.
   - For each shuffle, compute PSD and measure peak amplitude at φ-frequencies.
   - p-value = fraction of shuffles with higher φ-peak than observed.

2. **Multiple testing correction**:
   - Test K=10 harmonics → apply Bonferroni correction: α_corrected = 0.05 / K.

3. **Spectral concentration test**:
   - Compare peak density near φ-frequencies vs. random frequency bands.

### Visualizations:

- **Power spectrum plot**: PSD(f) with φ-harmonic markers
- **Peak histogram**: Distribution of detected peaks across frequency axis
- **φ-alignment plot**: Distance of all peaks to nearest φ-harmonic
- **Null comparison**: Observed vs. shuffled PSD overlays

---

## 6. Falsification criteria

### Evidence SUPPORTING φ-harmonic hypothesis:

✓ Multiple peaks (k ≥ 3) align with φ-harmonics within ε-tolerance  
✓ Peak amplitudes at φ-frequencies exceed 99th percentile of shuffled data  
✓ Permutation test p-value < 0.001 (after Bonferroni correction)  
✓ Effect robust across multiple prime ranges  
✓ φ-alignment significantly better than π, e, or √2 alignment

### Evidence REFUTING φ-harmonic hypothesis:

✗ No consistent peaks at φ-frequencies across ranges  
✗ Peak distribution at φ-frequencies indistinguishable from random  
✗ Permutation test p-value > 0.05  
✗ Peaks align equally well (or better) with other constants  
✗ Effect disappears after correcting for multiple testing

**Decision rule**:
- If ≥ 3 φ-harmonics show Z > 3.5 and p < 0.001 across all ranges → **Hypothesis supported**
- If p > 0.05 or peak distribution matches null → **Hypothesis rejected**

---

## 7. Expected outputs

### Quantitative results:

1. **Table**: Peak amplitudes at f_k = k·φ/N for k=1...10 across all ranges
2. **p-values**: Permutation test results for each (φ-harmonic, range) pair
3. **Peak counts**: Number of detected peaks within ε-distance of φ-frequencies
4. **Comparison table**: φ vs π vs e alignment scores

### Plots:

1. `power_spectrum.png`: PSD with φ-harmonic vertical lines
2. `peak_alignment.png`: Histogram of peak distances to φ-harmonics
3. `permutation_null.png`: Observed vs shuffled PSD distributions
4. `multi_range_comparison.png`: Spectral peaks across different prime ranges

### Report:

- `phi_harmonic_report.md`: Statistical tests, peak analysis, conclusions

---

## 8. Implementation notes

### Python libraries:

```python
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import welch, find_peaks, detrend
import matplotlib.pyplot as plt
```

### Algorithm outline:

```python
phi = (1 + np.sqrt(5)) / 2

for prime_range in ranges:
    gaps = load_prime_gaps(prime_range)
    log_gaps = np.log(gaps)
    
    # Preprocessing
    log_gaps_detrended = detrend(log_gaps)
    window = np.hanning(len(log_gaps_detrended))
    log_gaps_windowed = log_gaps_detrended * window
    
    # Compute power spectrum
    freqs, psd = welch(log_gaps_windowed, nperseg=1024)
    
    # Identify φ-harmonic frequencies
    phi_freqs = [k * phi / len(log_gaps) for k in range(1, 11)]
    
    # Measure peak amplitudes at φ-frequencies
    phi_peaks = [psd[np.argmin(np.abs(freqs - f))] for f in phi_freqs]
    
    # Permutation test
    null_distribution = []
    for _ in range(10000):
        shuffled = np.random.permutation(log_gaps_windowed)
        _, psd_null = welch(shuffled, nperseg=1024)
        phi_peaks_null = [psd_null[np.argmin(np.abs(freqs - f))] for f in phi_freqs]
        null_distribution.append(max(phi_peaks_null))
    
    # Compute p-value
    p_value = np.mean([x >= max(phi_peaks) for x in null_distribution])
    
    # Store results
    results[prime_range] = {
        'phi_peaks': phi_peaks,
        'p_value': p_value
    }
```

### Validation checks:

- Verify FFT implementation on synthetic sinusoid: peak at known frequency
- Confirm detrending removes linear drift without affecting high-frequency content
- Check that windowing reduces spectral leakage

---

## 9. Timeline

- **Day 1**: Load prime gap data, implement preprocessing pipeline
- **Day 2**: Compute power spectra, identify peaks
- **Day 3**: Implement φ-alignment scoring and permutation tests
- **Day 4**: Run statistical tests, compare against alternative constants
- **Day 5**: Create visualizations, write report

---

## 10. Potential pitfalls

1. **Spectral leakage**: FFT of finite sequence creates side-lobes → use proper windowing (Hann, Hamming)
2. **Multiple testing**: Testing many harmonics inflates false positive rate → apply Bonferroni or FDR correction
3. **Edge effects**: FFT boundary assumptions → apply zero-padding or tapering
4. **Trend contamination**: Low-frequency trend can dominate spectrum → always detrend
5. **Frequency resolution**: Δf = 1/N limits ability to resolve closely spaced peaks

---

## 11. References

- **Bracewell (1999)**: *The Fourier Transform and Its Applications*. (FFT theory, spectral analysis)
- **Percival & Walden (1993)**: *Spectral Analysis for Physical Applications*. (Welch method, windowing)
- **Stoica & Moses (2005)**: *Spectral Analysis of Signals*. (Peak detection, significance testing)
