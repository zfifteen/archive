## 9. Falsifiable Predictions

### 9.1 Enrichment Scaling Law

**Prediction:** For semiprimes with controlled factor ratios \(q/p \in \{1.5, 2, 3, 5, 10, 50\}\) and fixed bit-size, the Z5D enrichment ratio (near-\(q\) enrichment divided by near-\(p\) enrichment) should scale as either:

- \(q/p\) (arc-density model, from Theorem 1), or
- \((q/p)^2\) (dwell-time model, from Equation 19)

**Disconfirmation:** If the enrichment ratio does not increase monotonically with \(q/p\), or if it saturates below the linear prediction, the conformal anisotropy explanation is falsified.

### 9.2 Regime Transition

**Prediction:** Below \(q/p \approx 2.4\) (the transition at \(p/q = \tan(\pi/8)\)), the enrichment asymmetry should collapse toward 1x for both factors.

**Disconfirmation:** If strong asymmetry persists for highly balanced semiprimes (\(q/p < 1.5\)), the geometric explanation is insufficient and another mechanism is at work.

### 9.3 Arc-Length-Weighted Sampling

**Prediction:** A modified Fermat search using arc-length-uniform sampling (\(\Delta\theta \propto 1/|dz/d\theta|\)) should outperform standard uniform-\(\theta\) sampling by a factor approaching \(q/p\) for unbalanced semiprimes.

**Protocol:** Implement both sampling modes. For each, count samples required to find the correct \(m^2 = n^2 - N\). Run on semiprimes with \(q/p \in \{1.5, 2, 3, 5, 10\}\) and fixed 64-bit size. Compare sample counts.

**Disconfirmation:** If arc-length-weighted sampling shows no statistically significant improvement for any tested ratio, the anisotropy does not translate to algorithmic advantage.

### 9.4 Fourier Structure of the Resonance Sum

**Prediction:** Fourier analysis of the Z5D amplitude sum over the parametric angle \(\theta\) should reveal a dominant peak at frequency 2 (corresponding to the \(\cos(2\theta)\) term in \(|z|^2 = (n^2 + m^2) + 2nm\cos(2\theta)\)), with possible sub-harmonics at golden-ratio-related frequencies.

### 9.5 Window Optimization

**Prediction:** The optimal \(k\)-window width in the resonance sum (Equation 24) should relate to the Joukowski radius \(\mathcal{R} = \sqrt{n/m}\) or to \(\varphi \cdot \sqrt{N}\), since these are the characteristic geometric scales of the factoring ellipse.